import bpy
import cv2
import numpy as np
import math
from mathutils import Matrix
import bmesh
from pyblend.transform import circle2d_coords


class COLOR_CONST:
    colors = [
        [1.0, 0.0, 0.0],
        [0.0, 0.4, 0.0],
        [0.0, 0.6, 0.0],
        [0.0, 0.8, 0.0],
        [0.0, 1.0, 0.0],  # thumb
        [0.0, 0.0, 0.6],
        [0.0, 0.0, 1.0],
        [0.2, 0.2, 1.0],
        [0.4, 0.4, 1.0],  # index
        [0.0, 0.4, 0.4],
        [0.0, 0.6, 0.6],
        [0.0, 0.8, 0.8],
        [0.0, 1.0, 1.0],  # middle
        [0.4, 0.4, 0.0],
        [0.6, 0.6, 0.0],
        [0.8, 0.8, 0.0],
        [1.0, 1.0, 0.0],  # ring
        [0.4, 0.0, 0.4],
        [0.6, 0.0, 0.6],
        [0.8, 0.0, 0.8],
        [1.0, 0.0, 1.0],
    ]  # little


def plot_corner(image, coords_hw, vis=None, linewidth=2):
    """
    Plots a hand stick figure into a matplotlib figure.
    Reference: https://github.com/lixiny/ArtiBoost/blob/main/anakin/viztools/draw.py
    """
    colors = np.array(COLOR_CONST.colors)  # 21 x 3
    colors = colors[:, ::-1]  # BGR
    colors = np.concatenate([colors, np.ones((colors.shape[0], 1))], axis=1)

    # define connections and colors of the links
    links = [
        ((0, 1), colors[1, :]),
        ((1, 2), colors[2, :]),
        ((2, 3), colors[3, :]),
        ((3, 0), colors[4, :]),
        ((4, 5), colors[9, :]),
        ((5, 6), colors[10, :]),
        ((6, 7), colors[11, :]),
        ((7, 4), colors[12, :]),
        ((1, 5), colors[13, :]),
        ((3, 7), colors[14, :]),
        ((2, 6), colors[15, :]),
        ((0, 4), colors[16, :]),
    ]

    return plot_kps(image, coords_hw, links, vis, linewidth)


def plot_kps(image, coords_hw, links, vis=None, linewidth=3):
    """Plots a hand stick figure into a matplotlib figure."""

    colors = np.array(COLOR_CONST.colors)
    colors = colors[:, ::-1]
    colors = np.concatenate([colors, np.ones((colors.shape[0], 1))], axis=1)

    if vis is None:
        vis = np.ones_like(coords_hw[:, 0]) == 1.0

    for connection, color in links:
        if (vis[connection[0]] == False) or (vis[connection[1]] == False):
            continue

        coord1 = coords_hw[connection[0], :]
        coord2 = coords_hw[connection[1], :]
        c1x = int(coord1[0])
        c1y = int(coord1[1])
        c2x = int(coord2[0])
        c2y = int(coord2[1])
        cv2.line(image, (c1x, c1y), (c2x, c2y), color=color * 255, thickness=linewidth)

    for i in range(coords_hw.shape[0]):
        cx = int(coords_hw[i, 0])
        cy = int(coords_hw[i, 1])
        cv2.circle(image, (cx, cy), radius=2 * linewidth, thickness=-1, color=colors[i, :] * 255)

    return image


def generate(mesh_type="VERTEX", length=1.0, subdivision=2):
    """
    Generates vertex and face data for a variety of geometric shapes.

    Args:
        mesh_type (str): Type of the mesh. One of "VERTEX", "TRIANGLE", "TETRAHEDRON", "CUBE", "ICOSPHERE".
        length (float): Length / radius of the mesh.
        subdivision (int): Subdivision level of the mesh, only used for "ICOSPHERE".

    Returns:
        tuple: A tuple containing:
            - list: List of vertices.
            - list: List of edges.
            - list: List of faces.

    Reference: https://github.com/uhlik/bpy/blob/6fa219343cd3f9e230500ebb63f805c0648de8ab/space_view3d_point_cloud_visualizer.py
    """
    if mesh_type == "VERTEX":
        return (
            [
                (0, 0, 0),
            ],
            [],
            [],
        )

    elif mesh_type == "TRIANGLE":
        offset = 0.0
        r = math.sqrt(3) / 3 * length
        c = circle2d_coords(r, 3, offset, 0, 0)
        dv = []
        for i in c:
            dv.append(
                (
                    i[0],
                    i[1],
                    0,
                )
            )
        df = [
            (
                0,
                2,
                1,
            ),
        ]
        return dv, [], df
    elif mesh_type == "TETRAHEDRON":
        l = length
        excircle_radius = math.sqrt(3) / 3 * l
        c = circle2d_coords(excircle_radius, 3, 0, 0, 0)
        h = l / 3 * math.sqrt(6)
        dv = [
            (
                c[0][0],
                c[0][1],
                0,
            ),
            (
                c[1][0],
                c[1][1],
                0,
            ),
            (
                c[2][0],
                c[2][1],
                0,
            ),
            (
                0,
                0,
                h,
            ),
        ]
        df = [
            (0, 1, 2),
            (3, 2, 1),
            (3, 1, 0),
            (3, 0, 2),
        ]
        return dv, [], df
    elif mesh_type == "CUBE":
        l = length / 2
        dv = [
            (+l, +l, -l),
            (+l, -l, -l),
            (-l, -l, -l),
            (-l, +l, -l),
            (+l, +l, +l),
            (+l, -l, +l),
            (-l, -l, +l),
            (-l, +l, +l),
        ]
        df = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (4, 0, 3, 7),
        ]
        return dv, [], df
    elif mesh_type == "ICOSPHERE":
        if subdivision == 1:
            dv = [
                (0.0, 0.0, -0.5),
                (0.3617999851703644, -0.2628600001335144, -0.22360749542713165),
                (-0.13819250464439392, -0.42531999945640564, -0.22360749542713165),
                (-0.44721248745918274, 0.0, -0.22360749542713165),
                (-0.13819250464439392, 0.42531999945640564, -0.22360749542713165),
                (0.3617999851703644, 0.2628600001335144, -0.22360749542713165),
                (0.13819250464439392, -0.42531999945640564, 0.22360749542713165),
                (-0.3617999851703644, -0.2628600001335144, 0.22360749542713165),
                (-0.3617999851703644, 0.2628600001335144, 0.22360749542713165),
                (0.13819250464439392, 0.42531999945640564, 0.22360749542713165),
                (0.44721248745918274, 0.0, 0.22360749542713165),
                (0.0, 0.0, 0.5),
            ]
            df = [
                (0, 1, 2),
                (1, 0, 5),
                (0, 2, 3),
                (0, 3, 4),
                (0, 4, 5),
                (1, 5, 10),
                (2, 1, 6),
                (3, 2, 7),
                (4, 3, 8),
                (5, 4, 9),
                (1, 10, 6),
                (2, 6, 7),
                (3, 7, 8),
                (4, 8, 9),
                (5, 9, 10),
                (6, 10, 11),
                (7, 6, 11),
                (8, 7, 11),
                (9, 8, 11),
                (10, 9, 11),
            ]
        elif subdivision == 2:
            dv = [
                (0.0, 0.0, -0.5),
                (0.36180365085601807, -0.2628626525402069, -0.22360976040363312),
                (-0.1381940096616745, -0.42532461881637573, -0.22360992431640625),
                (-0.4472131133079529, 0.0, -0.22360780835151672),
                (-0.1381940096616745, 0.42532461881637573, -0.22360992431640625),
                (0.36180365085601807, 0.2628626525402069, -0.22360976040363312),
                (0.1381940096616745, -0.42532461881637573, 0.22360992431640625),
                (-0.36180365085601807, -0.2628626525402069, 0.22360976040363312),
                (-0.36180365085601807, 0.2628626525402069, 0.22360976040363312),
                (0.1381940096616745, 0.42532461881637573, 0.22360992431640625),
                (0.4472131133079529, 0.0, 0.22360780835151672),
                (0.0, 0.0, 0.5),
                (-0.08122777938842773, -0.24999763071537018, -0.42532721161842346),
                (0.21266134083271027, -0.15450569987297058, -0.4253270924091339),
                (0.13143441081047058, -0.40450581908226013, -0.26286882162094116),
                (0.4253239333629608, 0.0, -0.2628679573535919),
                (0.21266134083271027, 0.15450569987297058, -0.4253270924091339),
                (-0.262864887714386, 0.0, -0.42532584071159363),
                (-0.3440946936607361, -0.24999846518039703, -0.26286810636520386),
                (-0.08122777938842773, 0.24999763071537018, -0.42532721161842346),
                (-0.3440946936607361, 0.24999846518039703, -0.26286810636520386),
                (0.13143441081047058, 0.40450581908226013, -0.26286882162094116),
                (0.47552892565727234, -0.15450631082057953, 0.0),
                (0.47552892565727234, 0.15450631082057953, 0.0),
                (0.0, -0.4999999701976776, 0.0),
                (0.2938928008079529, -0.4045083522796631, 0.0),
                (-0.47552892565727234, -0.15450631082057953, 0.0),
                (-0.2938928008079529, -0.4045083522796631, 0.0),
                (-0.2938928008079529, 0.4045083522796631, 0.0),
                (-0.47552892565727234, 0.15450631082057953, 0.0),
                (0.2938928008079529, 0.4045083522796631, 0.0),
                (0.0, 0.4999999701976776, 0.0),
                (0.3440946936607361, -0.24999846518039703, 0.26286810636520386),
                (-0.13143441081047058, -0.40450581908226013, 0.26286882162094116),
                (-0.4253239333629608, 0.0, 0.2628679573535919),
                (-0.13143441081047058, 0.40450581908226013, 0.26286882162094116),
                (0.3440946936607361, 0.24999846518039703, 0.26286810636520386),
                (0.08122777938842773, -0.24999763071537018, 0.4253271818161011),
                (0.262864887714386, 0.0, 0.42532584071159363),
                (-0.21266134083271027, -0.15450569987297058, 0.4253270924091339),
                (-0.21266134083271027, 0.15450569987297058, 0.4253270924091339),
                (0.08122777938842773, 0.24999763071537018, 0.4253271818161011),
            ]
            df = [
                (0, 13, 12),
                (1, 13, 15),
                (0, 12, 17),
                (0, 17, 19),
                (0, 19, 16),
                (1, 15, 22),
                (2, 14, 24),
                (3, 18, 26),
                (4, 20, 28),
                (5, 21, 30),
                (1, 22, 25),
                (2, 24, 27),
                (3, 26, 29),
                (4, 28, 31),
                (5, 30, 23),
                (6, 32, 37),
                (7, 33, 39),
                (8, 34, 40),
                (9, 35, 41),
                (10, 36, 38),
                (38, 41, 11),
                (38, 36, 41),
                (36, 9, 41),
                (41, 40, 11),
                (41, 35, 40),
                (35, 8, 40),
                (40, 39, 11),
                (40, 34, 39),
                (34, 7, 39),
                (39, 37, 11),
                (39, 33, 37),
                (33, 6, 37),
                (37, 38, 11),
                (37, 32, 38),
                (32, 10, 38),
                (23, 36, 10),
                (23, 30, 36),
                (30, 9, 36),
                (31, 35, 9),
                (31, 28, 35),
                (28, 8, 35),
                (29, 34, 8),
                (29, 26, 34),
                (26, 7, 34),
                (27, 33, 7),
                (27, 24, 33),
                (24, 6, 33),
                (25, 32, 6),
                (25, 22, 32),
                (22, 10, 32),
                (30, 31, 9),
                (30, 21, 31),
                (21, 4, 31),
                (28, 29, 8),
                (28, 20, 29),
                (20, 3, 29),
                (26, 27, 7),
                (26, 18, 27),
                (18, 2, 27),
                (24, 25, 6),
                (24, 14, 25),
                (14, 1, 25),
                (22, 23, 10),
                (22, 15, 23),
                (15, 5, 23),
                (16, 21, 5),
                (16, 19, 21),
                (19, 4, 21),
                (19, 20, 4),
                (19, 17, 20),
                (17, 3, 20),
                (17, 18, 3),
                (17, 12, 18),
                (12, 2, 18),
                (15, 16, 5),
                (15, 13, 16),
                (13, 0, 16),
                (12, 14, 2),
                (12, 13, 14),
                (13, 1, 14),
            ]
        else:
            raise ValueError("unsupported subdivision: {}".format(subdivision))
        return dv, [], df
    else:
        return (
            [
                (
                    0,
                    0,
                    0,
                ),
            ],
            [],
            [],
        )


def calc_mesh(pc_np, name="PointCloud", colors=None, mesh_type="TETRAHEDRON", length=1.0, subdivision=2):
    """
    Creates a mesh object in Blender based on input point cloud data and optional color information.

    Args:
        pc_np (ndarray): Input point cloud data.
        name (str): Name of the mesh object.
        colors (ndarray): Optional color information.
        mesh_type (str): Type of the mesh. One of "VERTEX", "TRIANGLE", "TETRAHEDRON", "CUBE", "ICOSPHERE".
        length (float): Length / radius of the mesh.
        subdivision (int): Subdivision level of the mesh, only used for "ICOSPHERE".

    Reference: https://github.com/uhlik/bpy/blob/6fa219343cd3f9e230500ebb63f805c0648de8ab/space_view3d_point_cloud_visualizer.py
    """
    # ======== Preparing Translation Matrices from Point Cloud ========
    matrices = [Matrix.Translation(point) for point in pc_np[:, :3]]

    # ======== Triangulating Mesh Faces ========
    gv, _, gf = generate(mesh_type=mesh_type, length=length, subdivision=subdivision)
    me = bpy.data.meshes.new("mesh")
    me.from_pydata(gv, [], gf)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

    # ======== Preparing Vertex and Face Arrays ========
    gv = np.zeros((len(me.vertices) * 3), dtype=np.float32)
    me.vertices.foreach_get("co", gv)
    gv.shape = (len(me.vertices), 3)
    gf = np.zeros((len(me.polygons) * 3), dtype=np.int32)
    me.polygons.foreach_get("vertices", gf)
    gf.shape = (len(me.polygons), 3)
    zgv = gv.reshape(-1)

    # ======== Applying Transformations to Mesh Geometry ========
    vs = np.zeros((len(matrices) * len(gv) * 3), dtype=np.float32)
    fs = np.zeros((len(matrices) * len(gf) * 3), dtype=np.int32)
    cos = np.zeros((len(me.vertices) * 3), dtype=np.float32)
    fis = np.zeros((len(me.polygons) * 3), dtype=np.int32)
    for i, m in enumerate(matrices):
        # doesn't work when passing ndarray directly
        me.transform(Matrix(m))
        me.vertices.foreach_get("co", cos)
        vs[i * len(cos) : (i * len(cos)) + len(cos)] = cos
        me.polygons.foreach_get("vertices", fis)
        fis += (i * len(me.vertices),)
        fs[i * len(fis) : (i * len(fis)) + len(fis)] = fis
        me.vertices.foreach_set("co", zgv)
    bpy.data.meshes.remove(me)

    # ======== Creating Final Mesh Object ========
    me = bpy.data.meshes.new(name)
    vl = int(len(vs) / 3)
    fl = int(len(fs) / 3)
    me.vertices.add(vl)
    me.loops.add(fl * 3)
    me.polygons.add(fl)
    face_lengths = np.full(fl, 3, dtype=np.int32)
    loop_starts = np.arange(0, fl * 3, 3, dtype=np.int32)
    me.vertices.foreach_set("co", vs)
    me.polygons.foreach_set("loop_total", face_lengths)
    me.polygons.foreach_set("loop_start", loop_starts)
    me.polygons.foreach_set("vertices", fs)
    me.validate()  # avoid crash
    so = bpy.context.scene.objects
    for i in so:
        i.select_set(False)
    o = bpy.data.objects.new(name, me)

    # Add object to scene
    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(o)
    o.select_set(True)
    view_layer.objects.active = o

    # ======== Applying Colors to Mesh ========
    if colors is not None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for n in nodes:
            nodes.remove(n)
        attr = nodes.new("ShaderNodeAttribute")
        diff = nodes.new("ShaderNodeBsdfDiffuse")
        attr.attribute_name = "Col"
        out = nodes.new("ShaderNodeOutputMaterial")
        links.new(attr.outputs[0], diff.inputs[0])
        links.new(diff.outputs[0], out.inputs[0])
        o.data.materials.append(mat)
        colors = np.repeat(colors, len(gf) * 3, axis=0)
        colors = colors.reshape(-1)
        vc = o.data.vertex_colors.new()
        vc.data.foreach_set("color", colors)
