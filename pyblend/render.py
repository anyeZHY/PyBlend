import bpy
import math
from pyblend.find import find_all_pass_index


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


def config_cycles(pre_sample=1024, sample=4096):
    """
    Config cycles render engine for preview_samples and samples
    """
    bpy.data.scenes["Scene"].cycles.preview_samples = pre_sample
    bpy.data.scenes["Scene"].cycles.samples = sample


def config_render(
    path="tmp/output.png", engine="CYCLES", res_x=640, res_y=480, file_format="PNG", transparent=True, enable_gpu=True
):
    """
    Config render engine for path, engine, res_x, res_y, file_format, transparent
    """

    bpy.context.preferences.edit.undo_steps = 0  # disable undo

    render = bpy.context.scene.render
    render.filepath = path
    render.image_settings.file_format = file_format
    render.film_transparent = transparent
    render.resolution_x = res_x
    render.resolution_y = res_y
    if engine.startswith("C"):
        render.engine = "CYCLES"
        config_cycles()
        bpy.data.scenes["Scene"].cycles.use_denoising = True
        if enable_gpu:
            config_cycle_gpu()
    else:
        render.engine = "BLENDER_EEVEE"


def enable_depth_render(base_path="output", reverse=False):
    """
    Enable depth render and output exr and png. The png is normalized to [0, 1]
    and saved in base_path. The exr is the raw depth value. The png is useful for
    visualization.

    Args:
        base_path (str, optional): base path to save the exr and png. Defaults to "output".
        reverse (bool, optional): whether to reverse the depth value. Defaults to False.
    """
    bpy.context.scene.use_nodes = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].use_pass_z = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].pass_alpha_threshold = 0

    nodes = bpy.context.scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links
    if "Render Layers" not in nodes:
        render_node = nodes.new("CompositorNodeRLayers")
    else:
        render_node = nodes["Render Layers"]
    if "Composite" not in nodes:
        output_node = nodes.new("CompositorNodeComposite")
    else:
        output_node = nodes["Composite"]

    link1 = links.new(render_node.outputs[0], output_node.inputs[0])
    exr_output_node = nodes.new("CompositorNodeOutputFile")
    exr_output_node.format.file_format = "OPEN_EXR"
    # read exr with:
    # 1. OPENCV_IO_ENABLE_OPENEXR=1
    # 2. cv2.imread(PATH_TO_EXR_FILE, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    exr_output_node.base_path = base_path
    link2 = links.new(render_node.outputs[2], exr_output_node.inputs[0])

    # add normalized png depth
    output_node2 = nodes.new("CompositorNodeNormalize")
    png_output_node = nodes.new("CompositorNodeOutputFile")
    png_output_node.format.file_format = "PNG"
    png_output_node.base_path = base_path
    link3 = links.new(render_node.outputs[2], output_node2.inputs[0])
    if reverse:
        output_node3 = nodes.new("CompositorNodeMath")
        # x = 1 - x
        output_node3.operation = "MULTIPLY"
        output_node3.inputs[1].default_value = -1
        link4 = links.new(output_node2.outputs[0], output_node3.inputs[0])
        output_node4 = nodes.new("CompositorNodeMath")
        output_node4.operation = "ADD"
        output_node4.inputs[1].default_value = 1
        link5 = links.new(output_node3.outputs[0], output_node4.inputs[0])
        link6 = links.new(output_node4.outputs[0], png_output_node.inputs[0])
    else:
        link4 = links.new(output_node2.outputs[0], png_output_node.inputs[0])
    return exr_output_node, png_output_node


def enable_normal_render(base_path="output"):
    """
    Enable normal render and output png. The png is normalized to [0, 1].
    """
    bpy.context.scene.use_nodes = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].use_pass_normal = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].pass_alpha_threshold = 0

    nodes = bpy.context.scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links
    if "Render Layers" not in nodes:
        render_node = nodes.new("CompositorNodeRLayers")
    else:
        render_node = nodes["Render Layers"]

    # Seperate RGBA
    output_node1 = nodes.new("CompositorNodeSepRGBA")
    link1 = links.new(render_node.outputs[3], output_node1.inputs[0])
    # map RGB from [-1, 1] to [0, 1] separately (MapRange)
    output_nodeR = nodes.new("CompositorNodeMapRange")
    output_nodeR.inputs[1].default_value = -1
    output_nodeR.inputs[2].default_value = 1
    output_nodeR.inputs[3].default_value = 0
    output_nodeR.inputs[4].default_value = 1
    output_nodeR.use_clamp = True
    link2 = links.new(output_node1.outputs[0], output_nodeR.inputs[0])
    output_nodeG = nodes.new("CompositorNodeMapRange")
    output_nodeG.inputs[1].default_value = -1
    output_nodeG.inputs[2].default_value = 1
    output_nodeG.inputs[3].default_value = 0
    output_nodeG.inputs[4].default_value = 1
    output_nodeG.use_clamp = True
    link3 = links.new(output_node1.outputs[1], output_nodeG.inputs[0])
    output_nodeB = nodes.new("CompositorNodeMapRange")
    output_nodeB.inputs[1].default_value = -1
    output_nodeB.inputs[2].default_value = 1
    output_nodeB.inputs[3].default_value = 0
    output_nodeB.inputs[4].default_value = 1

    link4 = links.new(output_node1.outputs[2], output_nodeB.inputs[0])
    # combine RGB
    output_node2 = nodes.new("CompositorNodeCombRGBA")
    link5 = links.new(output_nodeR.outputs[0], output_node2.inputs[0])
    link6 = links.new(output_nodeG.outputs[0], output_node2.inputs[1])
    link7 = links.new(output_nodeB.outputs[0], output_node2.inputs[2])
    # output
    png_output_node = nodes.new("CompositorNodeOutputFile")
    png_output_node.format.file_format = "PNG"
    png_output_node.base_path = base_path
    link8 = links.new(output_node2.outputs[0], png_output_node.inputs[0])
    return png_output_node


def enable_segmentation_render(base_path="output", max_value=None):
    """
    In the segmentation render, each object is assigned a unique color.
    Each objects has the attribute pass_index, which is used to assign the color.

    Args:
        base_path (str, optional): base path to save the png. Defaults to "output".


    Returns:
        png_output_node, exr_output_node
    """
    bpy.context.scene.use_nodes = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].use_pass_object_index = True
    nodes = bpy.context.scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links
    if "Render Layers" not in nodes:
        render_node = nodes.new("CompositorNodeRLayers")
    else:
        render_node = nodes["Render Layers"]
    if max_value is None:
        max_value = max(find_all_pass_index())
    print(f"max_value: {max_value}")

    png_output_node = nodes.new("CompositorNodeOutputFile")
    png_output_node.format.file_format = "PNG"
    output_node1 = nodes.new("CompositorNodeSetAlpha")
    rainbow_link(render_node.outputs["IndexOB"], output_node1.inputs[0], max_value=max_value)
    output_node2 = nodes.new("CompositorNodeMath")
    output_node2.operation = "CEIL"
    link1 = links.new(render_node.outputs["IndexOB"], output_node2.inputs[0])
    link2 = links.new(output_node2.outputs[0], output_node1.inputs[1])
    link3 = links.new(output_node1.outputs[0], png_output_node.inputs[0])
    png_output_node.base_path = base_path

    exr_output_node = nodes.new("CompositorNodeOutputFile")
    exr_output_node.format.file_format = "OPEN_EXR"
    exr_output_node.base_path = base_path
    link3 = links.new(render_node.outputs["IndexOB"], exr_output_node.inputs[0])
    return exr_output_node, png_output_node


def rainbow_link(input_node, output_node, max_value=2):
    """
    Link input_node to output_node with rainbow colors.
    The color is computed by sin function by following the formula:
    >>> i = input_value / max_value
    >>> r = sin(2 * math.pi * i + 2) * 0.5 + 0.5
    >>> g = sin(2 * math.pi * i + 4) * 0.5 + 0.5
    >>> b = sin(2 * math.pi * i + 6) * 0.5 + 0.5
    >>> output_value = (r, g, b)
    where input_value is in [0, max_value] and output_value is in [0, 1]^3.
    """
    # normalize
    normalize_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    normalize_node.operation = "DIVIDE"
    normalize_node.inputs[1].default_value = max_value
    link1 = bpy.context.scene.node_tree.links.new(input_node, normalize_node.inputs[0])
    # multiply 0.024
    multiply_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    multiply_node.operation = "MULTIPLY"
    multiply_node.inputs[1].default_value = math.pi * 2
    link2 = bpy.context.scene.node_tree.links.new(normalize_node.outputs[0], multiply_node.inputs[0])
    # add 2
    add2_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    add2_node.operation = "ADD"
    add2_node.inputs[1].default_value = 2
    link3 = bpy.context.scene.node_tree.links.new(multiply_node.outputs[0], add2_node.inputs[0])
    # add 4
    add4_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    add4_node.operation = "ADD"
    add4_node.inputs[1].default_value = 4
    link4 = bpy.context.scene.node_tree.links.new(multiply_node.outputs[0], add4_node.inputs[0])
    # sin
    sin_node1 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    sin_node1.operation = "SINE"
    link5 = bpy.context.scene.node_tree.links.new(multiply_node.outputs[0], sin_node1.inputs[0])
    sin_node2 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    sin_node2.operation = "SINE"
    link6 = bpy.context.scene.node_tree.links.new(add2_node.outputs[0], sin_node2.inputs[0])
    sin_node3 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    sin_node3.operation = "SINE"
    link7 = bpy.context.scene.node_tree.links.new(add4_node.outputs[0], sin_node3.inputs[0])
    # multiply 0.5
    multiply_node1 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    multiply_node1.operation = "MULTIPLY"
    multiply_node1.inputs[1].default_value = 0.5
    link8 = bpy.context.scene.node_tree.links.new(sin_node1.outputs[0], multiply_node1.inputs[0])
    multiply_node2 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    multiply_node2.operation = "MULTIPLY"
    multiply_node2.inputs[1].default_value = 0.5
    link9 = bpy.context.scene.node_tree.links.new(sin_node2.outputs[0], multiply_node2.inputs[0])
    multiply_node3 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    multiply_node3.operation = "MULTIPLY"
    multiply_node3.inputs[1].default_value = 0.5
    link10 = bpy.context.scene.node_tree.links.new(sin_node3.outputs[0], multiply_node3.inputs[0])
    # add 0.5
    add_node1 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    add_node1.operation = "ADD"
    add_node1.inputs[1].default_value = 0.5
    link11 = bpy.context.scene.node_tree.links.new(multiply_node1.outputs[0], add_node1.inputs[0])
    add_node2 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    add_node2.operation = "ADD"
    add_node2.inputs[1].default_value = 0.5
    link12 = bpy.context.scene.node_tree.links.new(multiply_node2.outputs[0], add_node2.inputs[0])
    add_node3 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMath")
    add_node3.operation = "ADD"
    add_node3.inputs[1].default_value = 0.5
    link13 = bpy.context.scene.node_tree.links.new(multiply_node3.outputs[0], add_node3.inputs[0])
    # combine
    combine_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeCombRGBA")
    link14 = bpy.context.scene.node_tree.links.new(add_node1.outputs[0], combine_node.inputs[0])
    link15 = bpy.context.scene.node_tree.links.new(add_node2.outputs[0], combine_node.inputs[1])
    link16 = bpy.context.scene.node_tree.links.new(add_node3.outputs[0], combine_node.inputs[2])
    # output
    link17 = bpy.context.scene.node_tree.links.new(combine_node.outputs[0], output_node)


def render_image(path=None):
    if path is not None:
        bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
