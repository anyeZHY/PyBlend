import bpy
import numpy as np
from numpy.random import rand
from pyblend.transform import random_loc


def create_light(type="POINT", location=(0, 0, 2), rotation=(0, 0, 0), energy=2, color=(1, 1, 1), size=1, name=None):
    """
    Create a light with given parameters.

    Args:
        type: "area", "spot" or "point"
        name: name of the light
    """
    bpy.ops.object.light_add(type=type.upper(), location=location)
    light = bpy.context.object
    light.rotation_euler = rotation
    if name is not None:
        light.name = name
        light.data.name = name
    light.data.energy = energy
    light.data.color = color
    if type == "area":
        light.data.size = size
    elif type == "spot":
        light.data.spot_size = size
    return light


def config_world(strength: float = None, color=None):
    world_node_tree = bpy.data.worlds["World"].node_tree
    if strength is None:
        world_node_tree.nodes["Background"].inputs[1].default_value = rand() * 0.05  # strength
    else:
        world_node_tree.nodes["Background"].inputs[1].default_value = strength
    if color is None:
        world_node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 0.8 + rand() * 0.2)  # color
    else:
        world_node_tree.nodes["Background"].inputs[0].default_value = color


def config_light_random(light: bpy.types.Object, loc, radius, energy, delta_energy):
    loc = np.array(loc)
    radius = np.array([0, radius])
    light.location = random_loc(loc, radius)
    light.data.energy = energy + (rand() - 0.5) * delta_energy


def config_point_light():
    point = bpy.data.objects["Point"]
    # position
    radius = rand() * 0.4 + 0.2
    theta = (rand() - 0.5) * np.pi
    phi = (rand() - 0.5) * np.pi
    point.location = [
        radius * np.sin(theta),
        0.8 + radius * np.cos(theta) * np.cos(phi),
        radius * np.cos(theta) * np.sin(phi),
    ]
    # power
    bpy.data.lights["Point"].energy = 15 + (rand() - 0.5) * 15
