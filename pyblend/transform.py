import bpy
import numpy as np
from mathutils import Matrix
from numpy.random import rand, uniform


def random_loc(loc, radius=[0, 1], theta=[-0.5, 0.5], phi=[-1, 1]):
    radius = uniform(radius[0], radius[1])
    theta = uniform(theta[0], theta[1]) * np.pi
    phi = uniform(phi[0], phi[1]) * np.pi
    loc = np.array([np.sin(theta), np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi)]) * radius + loc
    return loc


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
