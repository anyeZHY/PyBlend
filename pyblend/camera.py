import bpy
import numpy as np
from mathutils import Matrix


def get_K_intr_from_blender(camera: bpy.types.Camera = None, width=None, height=None):
    """
    Get the intrinsic matrix from Blender.
    """
    if width is None:
        width = bpy.context.scene.render.resolution_x
    if height is None:
        height = bpy.context.scene.render.resolution_y
    if camera is None:
        angle = bpy.data.cameras["Camera"].angle
    else:
        angle = camera.angle

    aspect_ratio = width / height
    K = np.zeros((3, 3), dtype=np.float32)
    K[0][0] = width / 2 / np.tan(angle / 2)
    K[1][1] = height / 2.0 / np.tan(angle / 2) * aspect_ratio
    K[0][2] = width / 2.0
    K[1][2] = height / 2.0
    K[2][2] = 1.0
    K.transpose()
    return K.astype(np.float32)


def get_3x4_RT_matrix_from_blender(camera: bpy.types.Camera = None):
    if camera is None:
        camera = bpy.data.objects["Camera"]
    R_bcam2cv = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))

    location, rotation = camera.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    T_world2bcam = -1 * R_world2bcam @ location

    R_world2cv = R_bcam2cv @ R_world2bcam
    T_world2cv = R_bcam2cv @ T_world2bcam

    RT = Matrix(
        (
            R_world2cv[0][:] + (T_world2cv[0],),
            R_world2cv[1][:] + (T_world2cv[1],),
            R_world2cv[2][:] + (T_world2cv[2],),
            [0, 0, 0, 1],
        )
    )
    return np.array(RT).astype(np.float32)


def get_camera_para(camera=None):
    """
    Get the camera parameters from Blender.
    Reference: https://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera

    Args:
        camera (bpy.types.Object, optional): camera object. Defaults to None.

    Returns:
        dict: camera parameters, including intrinsic and extrinsic matrices
    """
    if camera is None:
        camera = bpy.data.objects["Camera"]
    K = get_K_intr_from_blender(camera)
    T = get_3x4_RT_matrix_from_blender(camera)

    meta = {
        "intrinsic": K,
        "extrinsic": np.array(T),
    }
    return meta
