import bpy
import numpy as np
from mathutils import Matrix

from pyblend.mesh import get_meshes
from pyblend.transform import transform, center_vert_bbox, get_vertices


def create_plane(location, rotation, scale, name=None) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(location=location, rotation=rotation)
    plane = bpy.context.object
    if name is not None:
        plane.name = name
    plane.scale = scale
    return plane


def create_monkey(location, rotation, scale, name=None) -> bpy.types.Object:
    bpy.ops.mesh.primitive_monkey_add(location=location, rotation=rotation)
    monkey = bpy.context.object
    if name is not None:
        monkey.name = name
    monkey.scale = scale
    return monkey


def load_obj(obj_root, obj_name, center=True, join=False, smart_uv=False):
    """
    Load obj/ply/glb file to Blender

    Args:
        obj_root (str): path to obj/ply/glb file
        obj_name (str): name of the object, used as the name of the mesh and material
        center (bool, optional): whether to center the object. Defaults to True.
    """
    if obj_root.endswith(".obj"):
        bpy.ops.import_scene.obj(filepath=obj_root)
    elif obj_root.endswith(".ply"):
        bpy.ops.import_mesh.ply(filepath=obj_root)
    elif obj_root.endswith(".glb"):
        bpy.ops.import_scene.gltf(filepath=obj_root)
    else:
        raise NotImplementedError
    bpy.context.selected_objects[0].name = obj_name
    if bpy.context.selected_objects[0].type == "MESH":
        bpy.context.selected_objects[0].data.name = obj_name
    obj = bpy.data.objects[obj_name]

    if join:
        join_objects([obj])
    if center:
        mesh = get_meshes(obj)[0]
        vertices = get_vertices(mesh)
        _, offset, _ = center_vert_bbox(vertices, scale=False)
        matrix = np.eye(4)
        matrix[:3, 3] = -offset
        transform(mesh, Matrix(matrix))
        obj.location = (0, 0, 0)

    if obj.active_material is not None:
        obj.active_material.name = f"mat_{obj_name}"
    bpy.context.view_layer.objects.active = obj
    if smart_uv:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def join_objects(objs):
    """
    Join multiple objects into one

    Args:
        objs (list): list of objects to join
    """
    bpy.ops.object.select_all(action="DESELECT")
    # select all meshes of the objects
    meshes = []
    for obj in objs:
        meshes.extend(get_meshes(obj))
    if len(meshes) == 0:
        print("No mesh to join")
        return
    if len(meshes) == 1:
        print("Only one mesh, no need to join")
        return
    for m in meshes:
        # Select all mesh objects
        m.select_set(state=True)
        # Makes one active
        bpy.context.view_layer.objects.active = m

    bpy.ops.object.join()
    # get the joined mesh
    obj = bpy.context.object
    return obj


def enable_shaow_catcher(obj):
    assert bpy.context.scene.render.engine == "CYCLES", "Only support Cycles"
    obj.is_shadow_catcher = True
