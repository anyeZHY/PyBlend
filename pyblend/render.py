import bpy


def config_cycle_gpu(verbose=False):
    devices = []
    bpy.data.scenes[0].render.engine = "CYCLES"
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    if verbose:
        print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)

    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        if d["name"][0] == "N":  # enable NVIDIA devices
            d["use"] = 1
            devices.append(d["name"])

    return devices


def config_cycles(pre_sample=4, sample=16):
    """
    Config cycles render engine for preview_samples and samples
    """
    bpy.data.scenes["Scene"].cycles.preview_samples = pre_sample
    bpy.data.scenes["Scene"].cycles.samples = sample


def config_render(scene: bpy.types.Scene, res_x=640, res_y=480, file_format="PNG"):
    bpy.context.preferences.edit.undo_steps = 0
    scene.render.image_settings.file_format = file_format
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
