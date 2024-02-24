import bpy
import math
import numpy as np
from mathutils import Matrix, Vector
from numpy.random import rand, uniform
from pyblend.find import find_all_meshes, scene_meshes, scene_root_objects


def get_vertices(obj_or_mesh: bpy.types.Object or bpy.types.Mesh, mode="obj"):
    """
    Get the vertices of the given object or mesh.

    Args:
        obj_or_mesh (bpy.types.Object or bpy.types.Mesh): The object or mesh.
        mode (str, optional): "obj" or "world". Object space or world space. Defaults to "obj".
    """
    mesh = obj_or_mesh.data if isinstance(obj_or_mesh, bpy.types.Object) else obj_or_mesh
    assert mesh is not None, "mesh is None"
    vertices = np.ones(len(mesh.vertices) * 3)
    obj_or_mesh.data.vertices.foreach_get("co", vertices)
    vertices = vertices.reshape(-1, 3)  # (N, 3)
    if mode == "world":
        # vertices = np.array([obj_or_mesh.matrix_world @ Vector(v) for v in vertices])
        matrix_world = np.array(obj_or_mesh.matrix_world)  # (4, 4)
        vertices = np.concatenate([vertices, np.ones((len(vertices), 1))], axis=1)  # (N, 4)
        vertices = vertices @ matrix_world.T  # (N, 4) @ (4, 4) -> (N, 4)
        vertices = vertices[:, :3]
    return vertices


def set_vertices(obj_or_mesh: bpy.types.Object or bpy.types.Mesh, vertices):
    """
    Set the vertices of the given object or mesh.
    Not suggested to use this function for complex meshes or objects.
    """
    mesh: bpy.types.Mesh = obj_or_mesh.data if isinstance(obj_or_mesh, bpy.types.Object) else obj_or_mesh
    assert mesh is not None, "mesh is None"
    mesh.vertices.foreach_set("co", vertices.reshape(-1))
    mesh.update()


def get_faces(obj_or_mesh: bpy.types.Object or bpy.types.Mesh):
    """
    Get the faces of the given object or mesh.
    """
    mesh = obj_or_mesh.data if isinstance(obj_or_mesh, bpy.types.Object) else obj_or_mesh
    assert mesh is not None, "mesh is None"
    faces = np.ones(len(mesh.polygons) * 3)
    mesh.polygons.foreach_get("vertices", faces)
    faces = faces.reshape(-1, 3)  # (N, 3)
    return faces


def random_loc(loc, radius=[0, 1], theta=[-0.5, 0.5], phi=[-1, 1]):
    radius = uniform(radius[0], radius[1])
    theta = uniform(theta[0], theta[1]) * np.pi
    phi = uniform(phi[0], phi[1]) * np.pi
    loc += (
        np.array(
            [
                np.cos(phi) * np.cos(theta),
                np.cos(phi) * np.sin(theta),
                np.sin(phi),
            ]
        )
        * radius
    )
    return loc


def againts_wall(obj: bpy.types.Object, z=0):
    """
    Move the object to the wall. The wall is defined as the z coordinate of the lowest vertex.

    Args:
        obj (bpy.types.Object): The object.
        z (float, optional): The z coordinate of the wall. Defaults to 0.
    """
    vertices = get_vertices(obj, mode="world")
    obj.location[2] = -vertices[:, 2].min() + z


def set_origin(obj: bpy.types.Object, loc=(0, 0, 0)):
    """
    Select the given object and set its center to the world origin.
    """
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
    obj.location = loc


def look_at(obj: bpy.types.Object, target):
    """
    Point the given object at the target.
    """
    loc = np.array(obj.location)
    target = np.array(target)
    direction = target - loc
    direction = Vector(direction)
    rot_quat = direction.to_track_quat("-Z", "Y")
    obj.rotation_euler = rot_quat.to_euler()


def _normalize_obj(obj_or_mesh: bpy.types.Object or bpy.types.Mesh):
    """
    Normalize the object to have unit bounding box and center at the world origin.
    Note: This function will change the mesh data of the object in-place.
    Not suggested to use this function for complex meshes or objects.
    """
    vertices = get_vertices(obj_or_mesh)
    vertices, center, scale = center_vert_bbox(vertices, scale=True)
    set_vertices(obj_or_mesh, vertices)
    return scale


def scene_bbox(single_obj=None, ignore_matrix=False):
    """
    Compute the bounding box of the scene.
    Refers to https://github.com/cvlab-columbia/zero123/blob/main/objaverse-rendering/scripts/blender_script.py

    Args:
        single_obj (bpy.types.Object, optional): If not None, only compute the bounding box of this object. Defaults to None.
        ignore_matrix (bool, optional): If True, ignore the matrix_world of the object. Defaults to False.

    Returns:
        Tuple[Vector, Vector]: The minimum and maximum coordinates of the bounding box.
    """
    bbox_min = (math.inf,) * 3
    bbox_max = (-math.inf,) * 3
    found = False
    for obj in scene_meshes() if single_obj is None else [single_obj]:
        found = True
        for coord in obj.bound_box:
            coord = Vector(coord)
            if not ignore_matrix:
                coord = obj.matrix_world @ coord
            bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
            bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
    if not found:
        raise RuntimeError("no objects in scene to compute bounding box for")
    return Vector(bbox_min), Vector(bbox_max)


def obj_bbox(obj: bpy.types.Object, ignore_matrix=False, mode="minmax"):
    """
    Compute the bounding box of the given object.

    Args:
        obj (bpy.types.Object): The object
        ignore_matrix (bool, optional): If True, ignore the matrix_world of the object. Defaults to False.
        mode (str, optional): "minmax" or "box". Defaults to "minmax".

    Returns:
        Tuple[Vector, Vector]: The minimum and maximum coordinates of the bounding box.
    """
    if mode == "minmax":
        bbox_min = (math.inf,) * 3
        bbox_max = (-math.inf,) * 3
        for obj in find_all_meshes(obj):
            for coord in obj.bound_box:
                coord = Vector(coord)
                if not ignore_matrix:
                    coord = obj.matrix_world @ coord
                bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
                bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
        return Vector(bbox_min), Vector(bbox_max)
    elif mode == "box":
        # return a 8 * 3 array
        bbox_min = (math.inf,) * 3
        bbox_max = (-math.inf,) * 3
        for obj in find_all_meshes(obj):
            for coord in obj.bound_box:
                coord = Vector(coord)
                bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
                bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
        # canonical box
        box = np.array(
            [
                [bbox_min[0], bbox_min[1], bbox_min[2]],
                [bbox_min[0], bbox_min[1], bbox_max[2]],
                [bbox_min[0], bbox_max[1], bbox_max[2]],
                [bbox_min[0], bbox_max[1], bbox_min[2]],
                [bbox_max[0], bbox_min[1], bbox_min[2]],
                [bbox_max[0], bbox_min[1], bbox_max[2]],
                [bbox_max[0], bbox_max[1], bbox_max[2]],
                [bbox_max[0], bbox_max[1], bbox_min[2]],
            ]
        )
        if not ignore_matrix:
            box = np.concatenate([box, np.ones((8, 1))], axis=1)
            box = box @ np.array(obj.matrix_world).T
            box = box[:, :3]
        return box
    else:
        raise ValueError(f"Unknown mode {mode}")


def normalize_scene():
    """
    Normalize the scene to have unit bounding box and center at the world origin.
    """
    bbox_min, bbox_max = scene_bbox()
    scale = 1 / max(bbox_max - bbox_min)
    for obj in scene_root_objects():
        obj.scale = obj.scale * scale
    # Apply scale to matrix_world.
    bpy.context.view_layer.update()
    bbox_min, bbox_max = scene_bbox()
    offset = -(bbox_min + bbox_max) / 2
    for obj in scene_root_objects():
        obj.matrix_world.translation += offset
    bpy.ops.object.select_all(action="DESELECT")


def normalize_obj(obj: bpy.types.Object):
    """
    Normalize the object to have unit bounding box and center at the world origin.
    """
    bbox_min, bbox_max = obj_bbox(obj)
    scale = 1 / max(bbox_max - bbox_min)
    obj.scale = obj.scale * scale
    # Apply scale to matrix_world.
    bpy.context.view_layer.update()
    bbox_min, bbox_max = obj_bbox(obj)
    offset = -(bbox_min + bbox_max) / 2
    obj.matrix_world = Matrix.Translation(offset) @ obj.matrix_world
    bpy.context.view_layer.update()


def transform(obj_or_mesh: bpy.types.Object or bpy.types.Mesh, matrix: Matrix or np.ndarray):
    mesh = obj_or_mesh.data if isinstance(obj_or_mesh, bpy.types.Object) else obj_or_mesh
    mesh.transform(Matrix(matrix))
    mesh.update()


def random_transform(obj: bpy.types.Object, offset_scale=1):
    """
    Randomly transform the object.
    """
    matrix = Matrix.Rotation(uniform(0, 2 * np.pi), 4, "Z")
    matrix = matrix @ Matrix.Rotation(uniform(0, 2 * np.pi), 4, "Y")
    matrix = matrix @ Matrix.Rotation(uniform(0, 2 * np.pi), 4, "X")
    matrix = matrix @ Matrix.Translation(uniform(-1, 1, 3) * offset_scale)

    obj.matrix_world = Matrix(matrix) @ obj.matrix_world
    bpy.context.view_layer.update()
    return obj


def center_vert_bbox(vertices, bbox_center=None, bbox_scale=None, scale=False):
    if bbox_center is None:
        bbox_center = (vertices.min(0) + vertices.max(0)) / 2
    vertices = vertices - bbox_center
    if scale:
        if bbox_scale is None:
            bbox_scale = np.linalg.norm(vertices, 2, 1).max()
        vertices = vertices / bbox_scale
    else:
        bbox_scale = 1
    return vertices, bbox_center, bbox_scale


def persp_project(points3d, cam_intr):
    hom_2d = np.array(cam_intr).dot(points3d.transpose()).transpose()
    points2d = (hom_2d / (hom_2d[:, 2:] + 1e-6))[:, :2]
    return points2d.astype(np.float32)


def circle2d_coords(radius, steps, offset, ox, oy):
    """
    Generates 2D coordinates of a circle.

    Args:
        radius (float): Radius of the circle.
        steps (int): Number of steps.
        offset (float): Offset angle.
        ox (float): X coordinate of the center.
        oy (float): Y coordinate of the center.
    """
    r = []
    angstep = 2 * math.pi / steps
    for i in range(steps):
        x = math.sin(i * angstep + offset) * radius + ox
        y = math.cos(i * angstep + offset) * radius + oy
        r.append((x, y))
    return r
