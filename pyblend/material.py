import bpy
from numpy.random import rand


def reset_mat(mat):
    """Reset material to default"""
    mats = bpy.data.materials
    name = mat.name
    mats.remove(mat)
    mat = mats.new(name)
    mat.use_nodes = True
    return mat


def create_texture_node(nodes: bpy.types.NodeGroup, path: str = None, img: bpy.types.Image = None) -> bpy.types.Node:
    """Create a texture node and load image from path or img"""
    tex_node = nodes.new("ShaderNodeTexImage")
    if img is not None:
        tex_node.image = img
    elif path is not None:
        tex_node.image = bpy.data.images.load(filepath=path)
    return tex_node


def load_mat_library(lib_root):
    """Load material library from .blend file"""
    assert lib_root.endswith(".blend"), "Only support .blend file"
    with bpy.data.libraries.load(lib_root, link=True) as (data_from, data_to):
        data_to.materials = data_from.materials


def random_transparent_mat(nodes):
    prin_node = nodes["Principled BSDF"]
    prin_node.inputs[9].default_value = rand() * 0.1  # Roughness
    prin_node.inputs[16].default_value = 1.4 + rand() * 0.2  # IOR
    prin_node.inputs[17].default_value = 0.8 + rand() * 0.2  # Transmission


def random_metallic_mat(nodes):
    prin_node = nodes["Principled BSDF"]
    for i in range(6, 16):
        prin_node.inputs[i].default_value = rand()


def random_mat(mat):
    nodes = mat.node_tree.nodes
    prin_node = nodes["Principled BSDF"]
    prob = rand()
    if prob <= 0.2:
        random_transparent_mat(nodes)
    elif 0.2 < prob <= 0.4:
        random_metallic_mat(nodes)
    elif 0.4 < prob <= 0.6:
        prin_node.inputs[9].default_value = rand()  # Roughness
