def get_meshes(obj):
    """
    Get all the meshes of an object recursively.
    """
    meshes = []
    if obj.type == "MESH":
        meshes.append(obj)
    for child in obj.children:
        meshes.extend(get_meshes(child))
    return meshes
