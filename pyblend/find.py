import bpy


def find_all_meshes(obj: bpy.types.Object):
    """
    Find all meshes in the given object and its children.

    Args:
        obj (bpy.types.Object): The object.

    Returns:
        List[bpy.types.Object]: The list of meshes.
    """
    meshes = []
    if isinstance(obj.data, bpy.types.Mesh):
        meshes.append(obj)
    for child in obj.children:
        meshes.extend(find_all_meshes(child))
    return meshes


def scene_root_objects(objs=None):
    """
    Iterate over all root objects in the scene.
    """
    for obj in bpy.context.scene.objects.values():
        if not obj.parent:
            yield obj


def scene_meshes():
    """
    Iterate over all meshes in the scene.
    """
    for obj in bpy.context.scene.objects.values():
        if isinstance(obj.data, (bpy.types.Mesh)):
            yield obj
