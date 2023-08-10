import bpy


def find_parent(obj: bpy.types.Object):
    while obj.parent:
        obj = obj.parent
    return obj


def find_all_meshes(obj: bpy.types.Object, parent=True):
    """
    Find all meshes in the given object and its children.

    Args:
        obj (bpy.types.Object): The object.

    Returns:
        List[bpy.types.Object]: The list of meshes.
    """
    if parent:
        obj = find_parent(obj)
    meshes = []
    if isinstance(obj.data, bpy.types.Mesh):
        meshes.append(obj)
    for child in obj.children:
        meshes.extend(find_all_meshes(child, parent=False))
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


def find_all_objects(obj: bpy.types.Object):
    """
    Find all objects in the given object and its children.

    Args:
        obj (bpy.types.Object): The object.

    Returns:
        List[bpy.types.Object]: The list of objects.
    """
    objs = []
    objs.append(obj)
    for child in obj.children:
        objs.extend(find_all_objects(child))
    return objs


def find_all_pass_index():
    indexes = []
    for obj in bpy.context.scene.objects.values():
        idx = obj.pass_index
        if idx not in indexes:
            indexes.append(idx)
    return indexes
