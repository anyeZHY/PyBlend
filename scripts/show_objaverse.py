import cv2
import bpy
import random
import objaverse
import numpy as np
from pyblend.object import load_obj
from pyblend.viztools import plot_corner
from pyblend.find import find_all_objects
from pyblend.lighting import config_world
from pyblend.camera import get_camera_para
from pyblend.utils import BlenderRemover, ArgumentParserForBlender
from pyblend.transform import look_at, normalize_obj, random_loc, obj_bbox, random_transform, persp_project
from pyblend.render import (
    config_render,
    render_image,
    enable_segmentation_render,
    enable_depth_render,
    enable_normal_render,
)


def load_objaverse(uids, download_processes=1):
    objects = objaverse.load_objects(
        uids=uids,
        download_processes=download_processes,
    )
    return objects


def main(args):
    random.seed(42)
    np.random.seed(42)

    uids = objaverse.load_lvis_annotations()  # dict of class -> list of uids
    uids = [uid for uid_list in uids.values() for uid in uid_list]
    uids = random.sample(uids, 100)

    # ======== Config ========
    config_render(res_x=640, res_y=640, transparent=False)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)
    camera = bpy.data.objects["Camera"]
    exr_seg_node, png_seg_node = enable_segmentation_render("tmp/objaverse", max_value=args.num_obj)
    exr_depth_node, png_depth_node = enable_depth_render("tmp/objaverse", reverse=True)
    png_normal_node = enable_normal_render("tmp/objaverse")
    png_seg_node.file_slots[0].path = f"seg_"
    exr_seg_node.file_slots[0].path = f"seg_"
    png_depth_node.file_slots[0].path = f"depth_"
    exr_depth_node.file_slots[0].path = f"depth_"
    png_normal_node.file_slots[0].path = f"normal_"

    # ======== Set up scene ========
    for scene_idx in range(args.num_scene):
        objects = load_objaverse(random.sample(uids, args.num_obj))
        bbox_list = []
        for ii, (uid, path) in enumerate(objects.items()):
            # load object
            obj = load_obj(path, "object", center=False, join=True)
            obj.location = (0, 0, 0)
            normalize_obj(obj)
            for obj in find_all_objects(obj):
                obj.pass_index = ii + 1
            random_transform(obj, offset_scale=2)
            bbox = obj_bbox(obj, mode="box")  # (8, 3)
            bbox_list.append(bbox)

        # ======== Render ========
        for camera_idx in range(args.num_views):
            camera.location = random_loc((0, 0, 0), (8, 8), theta=(-1, 1), phi=(0, 1))
            look_at(camera, (0, 0, 0))
            bpy.context.view_layer.update()
            camera_para = get_camera_para(camera)
            intr = camera_para["intrinsic"]  # (3, 3)
            extr = camera_para["extrinsic"]  # (4, 4)
            bbox2d_list = []
            for bbox in bbox_list:
                bbox2cam = extr.dot(np.concatenate([bbox, np.ones((8, 1))], axis=1).transpose()).transpose()[
                    :, :3
                ]  # (8, 3)
                bbox2d = persp_project(bbox2cam, intr)  # (8, 2)
                bbox2d_list.append(bbox2d)
            bpy.context.scene.frame_current = scene_idx * args.num_views + camera_idx
            render_image(f"tmp/objaverse/out_{scene_idx * args.num_views + camera_idx:04d}.png")
            image = cv2.imread(
                f"tmp/objaverse/out_{scene_idx * args.num_views + camera_idx:04d}.png", cv2.IMREAD_UNCHANGED
            )
            for bbox2d in bbox2d_list:
                image = plot_corner(image, bbox2d, linewidth=1)
            cv2.imwrite(f"tmp/objaverse/out_bbox_{scene_idx * args.num_views + camera_idx:04d}.png", image)
        remover.clear_all()


if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    args = parser.add_argument("--num_scene", type=int, default=10)
    args = parser.add_argument("--num_obj", type=int, default=10)
    args = parser.add_argument("--num_views", type=int, default=2)
    args = parser.parse_args()
    main(args)
