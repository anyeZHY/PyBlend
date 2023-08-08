import bpy
import random
import objaverse
import numpy as np
from pyblend.object import load_obj
from pyblend.lighting import config_world, create_light
from pyblend.utils import BlenderRemover, ArgumentParserForBlender
from pyblend.render import config_render, render_image
from pyblend.transform import look_at, normalize_obj, againts_wall, random_loc
from pyblend.mesh import get_meshes


def load_objaverse(uids, download_processes=1):
    objects = objaverse.load_objects(
        uids=uids,
        download_processes=download_processes,
    )
    return objects


if __name__ == "__main__":
    uids = objaverse.load_uids()
    uids = uids[:10]
    objects = load_objaverse(uids)  # dict: uid -> object

    # ======== Config ========
    config_render(res_x=320, res_y=240, transparent=True)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)
    camera = bpy.data.objects["Camera"]

    uid, path = random.choice(list(objects.items()))
    # ======== Set up scene ========
    obj = load_obj(path, "object", center=True, join=True)
    obj.location = (0, 0, 0)
    normalize_obj(obj)
    camera.location = random_loc((0, 0, 0), (3, 3), theta=(-1, 1), phi=(0, 1))
    look_at(camera, (0, 0, 0))
    # ======== Render ========
    render_image(f"tmp/objaverse/out.png")
