import bpy
import numpy as np
from pyblend.lighting import config_world
from pyblend.object import load_obj, create_plane
from pyblend.material import random_mat, set_voronoi_texture
from pyblend.utils import BlenderRemover, ArgumentParserForBlender, debug
from pyblend.render import config_render, render_image, enable_depth_render, enable_normal_render


def render_teaser(args):
    # ======== Config ========
    config_render(res_x=320, res_y=240)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.5)
    camera = bpy.data.objects["Camera"]
    camera.location = (0, -10, 3)
    camera.rotation_euler = (np.pi / 2.5, 0, 0)

    exr_depth_node, png_depth_node = enable_depth_render("tmp/teaser", reverse=True)
    png_normal_node = enable_normal_render("tmp/teaser")

    # ======== Set up scene ========
    plane = create_plane((0, 1, 0), (np.pi / 2, 0, 0), (10, 10, 10), name="plane")
    plane.active_material = set_voronoi_texture(plane.active_material)
    plane = create_plane((0, 0, -1.2), (0, 0, 0), (10, 10, 10), name="plane")

    bunny = load_obj("docs/bunny.obj", "bunny", center=True)
    bunny.scale = (15, 15, 15)
    bunny.location = (0, -0.5, 0)

    # ======== Render ========
    for i in range(args.begin, args.end):
        # change linearly (color)
        color = np.array([0.5, 0.5, 0.5, 1.0]) + np.array([0.5, 0.5, 0.5, 1.0]) * np.sin(
            np.deg2rad(np.array([1, 2, 3, 4]) * i)
        )
        bunny.active_material = random_mat(bunny.active_material, color)
        bunny.rotation_euler[2] = np.deg2rad(i)
        bpy.context.scene.frame_current = i
        exr_depth_node.file_slots[0].path = f"depth_"
        png_depth_node.file_slots[0].path = f"depth_"
        png_normal_node.file_slots[0].path = f"normal_"
        render_image(f"tmp/teaser/out_{i:04d}.png")

    # ======== Save blend file ========
    debug("tmp/teaser/debug.blend")


if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    parser.add_argument("--begin", type=int, default=0)
    parser.add_argument("--end", type=int, default=360)
    args = parser.parse_args()
    render_teaser(args)
