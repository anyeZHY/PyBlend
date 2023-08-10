import cv2
import numpy as np


class COLOR_CONST:
    colors = [
        [1.0, 0.0, 0.0],
        [0.0, 0.4, 0.0],
        [0.0, 0.6, 0.0],
        [0.0, 0.8, 0.0],
        [0.0, 1.0, 0.0],  # thumb
        [0.0, 0.0, 0.6],
        [0.0, 0.0, 1.0],
        [0.2, 0.2, 1.0],
        [0.4, 0.4, 1.0],  # index
        [0.0, 0.4, 0.4],
        [0.0, 0.6, 0.6],
        [0.0, 0.8, 0.8],
        [0.0, 1.0, 1.0],  # middle
        [0.4, 0.4, 0.0],
        [0.6, 0.6, 0.0],
        [0.8, 0.8, 0.0],
        [1.0, 1.0, 0.0],  # ring
        [0.4, 0.0, 0.4],
        [0.6, 0.0, 0.6],
        [0.8, 0.0, 0.8],
        [1.0, 0.0, 1.0],
    ]  # little


def plot_corner(image, coords_hw, vis=None, linewidth=2):
    """
    Plots a hand stick figure into a matplotlib figure.
    Reference: https://github.com/lixiny/ArtiBoost/blob/main/anakin/viztools/draw.py
    """
    colors = np.array(COLOR_CONST.colors)  # 21 x 3
    colors = colors[:, ::-1]  # BGR
    colors = np.concatenate([colors, np.ones((colors.shape[0], 1))], axis=1)

    # define connections and colors of the links
    links = [
        ((0, 1), colors[1, :]),
        ((1, 2), colors[2, :]),
        ((2, 3), colors[3, :]),
        ((3, 0), colors[4, :]),
        ((4, 5), colors[9, :]),
        ((5, 6), colors[10, :]),
        ((6, 7), colors[11, :]),
        ((7, 4), colors[12, :]),
        ((1, 5), colors[13, :]),
        ((3, 7), colors[14, :]),
        ((2, 6), colors[15, :]),
        ((0, 4), colors[16, :]),
    ]

    return plot_kps(image, coords_hw, links, vis, linewidth)


def plot_kps(image, coords_hw, links, vis=None, linewidth=3):
    """Plots a hand stick figure into a matplotlib figure."""

    colors = np.array(COLOR_CONST.colors)
    colors = colors[:, ::-1]
    colors = np.concatenate([colors, np.ones((colors.shape[0], 1))], axis=1)

    if vis is None:
        vis = np.ones_like(coords_hw[:, 0]) == 1.0

    for connection, color in links:
        if (vis[connection[0]] == False) or (vis[connection[1]] == False):
            continue

        coord1 = coords_hw[connection[0], :]
        coord2 = coords_hw[connection[1], :]
        c1x = int(coord1[0])
        c1y = int(coord1[1])
        c2x = int(coord2[0])
        c2y = int(coord2[1])
        cv2.line(image, (c1x, c1y), (c2x, c2y), color=color * 255, thickness=linewidth)

    for i in range(coords_hw.shape[0]):
        cx = int(coords_hw[i, 0])
        cy = int(coords_hw[i, 1])
        cv2.circle(image, (cx, cy), radius=2 * linewidth, thickness=-1, color=colors[i, :] * 255)

    return image
