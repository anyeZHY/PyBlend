import bpy
import numpy as np
from mathutils import Matrix, Vector
from numpy.random import rand, uniform


def get_vertices(obj: bpy.types.Object, mode="obj"):
    """
    Get the vertices of the given object.

    Args:
        obj (bpy.types.Object): the object
        mode (str, optional): "obj" or "world". Object space or world space. Defaults to "obj".
    """
    vertices = np.ones(len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", vertices)
    vertices = vertices.reshape(-1, 3)
    if mode == "world":
        vertices = np.array([obj.matrix_world @ Vector(v) for v in vertices])
    return vertices


def set_vertices(obj: bpy.types.Object, vertices):
    obj.data.vertices.foreach_set("co", vertices.reshape(-1))


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


def normalize_obj(obj: bpy.types.Object):
    """
    Normalize the object to have unit bounding box and center at the world origin.
    """
    vertices = get_vertices(obj)
    vertices, _, _ = center_vert_bbox(vertices, scale=True)
    set_vertices(obj, vertices)


def transform(obj: bpy.types.Object, matrix: Matrix or np.ndarray):
    obj.data.transform(Matrix(matrix))
    obj.data.update()


def random_transform(obj, matrix, scale):
    camera_free = rand() * (2 * np.pi)
    camera_free_rotmat = np.array(
        [
            [np.cos(camera_free), -np.sin(camera_free), 0],
            [np.sin(camera_free), np.cos(camera_free), 0],
            [0, 0, 1],
        ]
    )
    matrix_tmp = np.concatenate(
        [np.concatenate([camera_free_rotmat, np.zeros((3, 1))], axis=1), [[0, 0, 0, 1]]], axis=0
    )

    theta = uniform(-0.5, 0.5) * np.pi
    phi = uniform(-1 / 6, 1 + 1 / 6) * np.pi
    offset = (
        np.array(
            [
                np.cos(theta) * np.cos(phi),
                np.cos(theta) * np.sin(phi),
                np.sin(theta),
            ]
        )
        * scale
    )

    transform(obj, matrix @ matrix_tmp)
    obj.location = offset
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
