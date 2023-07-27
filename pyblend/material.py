import bpy
import numpy as np
from numpy.random import rand


def reset_mat(mat):
    """Reset material to default"""
    mats = bpy.data.materials
    name = mat.name
    mats.remove(mat)
    mat = mats.new(name)
    mat.use_nodes = True
    return mat


def create_mat(name: str, nodes: bpy.types.NodeGroup = None) -> bpy.types.Material:
    """
    Create material with name and nodes
    """
    mats = bpy.data.materials
    mat = mats.new(name)
    mat.use_nodes = True
    if nodes is not None:
        mat.node_tree.nodes.clear()
        mat.node_tree.nodes.new("ShaderNodeGroup").node_tree = nodes
    return mat


def create_texture_node(nodes: bpy.types.NodeGroup, path: str = None, img: bpy.types.Image = None) -> bpy.types.Node:
    """
    Create a texture node and load image from path or img
    """
    tex_node = nodes.new("ShaderNodeTexImage")
    if img is not None:
        tex_node.image = img
    elif path is not None:
        tex_node.image = bpy.data.images.load(filepath=path)
    return tex_node


def load_mat_library(lib_root):
    """
    Load material library from .blend file
    """
    assert lib_root.endswith(".blend"), "Only support .blend file"
    with bpy.data.libraries.load(lib_root, link=True) as (data_from, data_to):
        data_to.materials = data_from.materials


def set_voronoi_texture(mat):
    if mat is None:
        mat = bpy.data.materials.new(name="Material")
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    tex_node = nodes.new("ShaderNodeTexVoronoi")

    links = mat.node_tree.links
    links.new(tex_node.outputs[1], nodes["Principled BSDF"].inputs[0])
    return mat


def random_transparent_mat(nodes, color=None):
    prin_node = nodes["Principled BSDF"]
    if color is None:
        prin_node.inputs[0].default_value = np.random.uniform(0.3, 0.9, 4)  # Base Color
    else:
        prin_node.inputs[0].default_value = color
    for i in range(4, 13):
        prin_node.inputs[i].default_value = 0
    prin_node.inputs[14].default_value = 1.45
    prin_node.inputs[15].default_value = 0  # Roughness
    prin_node.inputs[17].default_value = 0.9 + rand() * 0.1  # Transmission


def random_metallic_mat(nodes, color=None):
    prin_node = nodes["Principled BSDF"]
    if color is None:
        prin_node.inputs[0].default_value = np.random.uniform(0.3, 0.9, 4)  # Base Color
    else:
        prin_node.inputs[0].default_value = color
    for i in range(6, 16):
        prin_node.inputs[i].default_value = rand() / 5


def random_mat(mat, color=None):
    if mat is None:
        mat = bpy.data.materials.new(name="Material")
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    prob = rand()
    if prob <= 0.5:
        random_transparent_mat(nodes, color)
    elif 0.5 < prob <= 1.0:
        random_metallic_mat(nodes, color)
    return mat
