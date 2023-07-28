import bpy
import numpy as np
from pyblend.object import load_obj, create_plane, enable_shaow_catcher
from pyblend.lighting import config_world, create_light
from pyblend.material import random_mat, set_voronoi_texture, load_mat_library
from pyblend.utils import BlenderRemover, ArgumentParserForBlender, debug
from pyblend.render import config_render, render_image
from pyblend.transform import look_at, normalize_obj, againts_wall, random_loc


def render_teaser(args):
    # ======== Config ========
    config_render(res_x=320, res_y=240, transparent=False)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)
    if args.color is not None:
        load_mat_library("docs/materials.blend")
        mat = bpy.data.materials["cbrewer medium blue"]
        hex_color = args.color
        color = np.array([int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]) / 255
        mat.node_tree.nodes["Hue Saturation Value"].inputs[4].default_value = np.append(color, 1)
    else:
        mat = None
    # ======== Set up scene ========
    plane = create_plane((0, 0, -1), (0, 0, 0), (20, 20, 20), name="plane")
    enable_shaow_catcher(plane)
    obj = load_obj(args.input, "object", center=True)
    normalize_obj(obj)
    againts_wall(obj, z=-1)
    spot_light = create_light("SPOT", (3, 3, 10), (np.pi / 2, 0, 0), 400, (1, 1, 1), 5, name="light")
    look_at(spot_light, obj.location)
    camera = bpy.data.objects["Camera"]
    # ======== Render ========
    for i in range(args.num):
        camera.location = random_loc((0, 0, 0), (6, 6), theta=(-1, 1), phi=(0, 1))
        look_at(camera, obj.location)
        if args.color is None:
            obj.active_material = random_mat(obj.active_material)
        else:
            obj.active_material = mat
        render_image(f"tmp/multiview/{args.name}_{i:04d}.png")


if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    parser.add_argument("-i", "--input", type=str, default="docs/bunny.obj")
    parser.add_argument("-n", "--num", type=int, default=12)
    parser.add_argument("-c", "--color", type=str, default=None)
    parser.add_argument("--name", type=str, default="out")
    args = parser.parse_args()
    render_teaser(args)
