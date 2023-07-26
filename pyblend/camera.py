import numpy as np


def get_K_intr_from_blender(focal_length, width=640, height=480):
    aspect_ratio = width / height
    angle = 2 * np.arctan(18 / focal_length)
    K = np.zeros((3, 3), dtype=np.float32)
    K[0][0] = width / 2 / np.tan(angle / 2)
    K[1][1] = height / 2.0 / np.tan(angle / 2) * aspect_ratio
    K[0][2] = width / 2.0
    K[1][2] = height / 2.0
    K[2][2] = 1.0
    K.transpose()
    return K
