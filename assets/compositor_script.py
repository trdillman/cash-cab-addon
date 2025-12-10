import bpy
import mathutils


# Generate unique scene name
base_name = "Scene"
end_name = base_name
if bpy.data.scenes.get(end_name) is not None:
    i = 1
    end_name = base_name + f".{i:03d}"
    while bpy.data.scenes.get(end_name) is not None:
        end_name = base_name + f".{i:03d}"
        i += 1

scene = bpy.context.window.scene.copy()

scene.name = end_name
scene.use_fake_user = True
bpy.context.window.scene = scene


def _rr_yuv_adjustments_node_group():
    """Initialize .RR_YUV_adjustments node group"""
    _rr_yuv_adjustments = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_YUV_adjustments")

    _rr_yuv_adjustments.color_tag = 'NONE'
    _rr_yuv_adjustments.description = ""
    _rr_yuv_adjustments.default_group_node_width = 140
    # _rr_yuv_adjustments interface

    # Socket U
    u_socket = _rr_yuv_adjustments.interface.new_socket(name="U", in_out='OUTPUT', socket_type='NodeSocketFloat')
    u_socket.default_value = 0.0
    u_socket.min_value = -3.4028234663852886e+38
    u_socket.max_value = 3.4028234663852886e+38
    u_socket.subtype = 'NONE'
    u_socket.attribute_domain = 'POINT'
    u_socket.default_input = 'VALUE'
    u_socket.structure_type = 'AUTO'

    # Socket V
    v_socket = _rr_yuv_adjustments.interface.new_socket(name="V", in_out='OUTPUT', socket_type='NodeSocketFloat')
    v_socket.default_value = 0.0
    v_socket.min_value = -3.4028234663852886e+38
    v_socket.max_value = 3.4028234663852886e+38
    v_socket.subtype = 'NONE'
    v_socket.attribute_domain = 'POINT'
    v_socket.default_input = 'VALUE'
    v_socket.structure_type = 'AUTO'

    # Socket Factor
    factor_socket = _rr_yuv_adjustments.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket.default_value = 1.0
    factor_socket.min_value = 0.0
    factor_socket.max_value = 1.0
    factor_socket.subtype = 'FACTOR'
    factor_socket.attribute_domain = 'POINT'
    factor_socket.default_input = 'VALUE'
    factor_socket.structure_type = 'AUTO'

    # Socket U
    u_socket_1 = _rr_yuv_adjustments.interface.new_socket(name="U", in_out='INPUT', socket_type='NodeSocketFloat')
    u_socket_1.default_value = 0.5
    u_socket_1.min_value = -10000.0
    u_socket_1.max_value = 10000.0
    u_socket_1.subtype = 'NONE'
    u_socket_1.attribute_domain = 'POINT'
    u_socket_1.hide_value = True
    u_socket_1.default_input = 'VALUE'
    u_socket_1.structure_type = 'AUTO'

    # Socket V
    v_socket_1 = _rr_yuv_adjustments.interface.new_socket(name="V", in_out='INPUT', socket_type='NodeSocketFloat')
    v_socket_1.default_value = 0.5
    v_socket_1.min_value = -10000.0
    v_socket_1.max_value = 10000.0
    v_socket_1.subtype = 'NONE'
    v_socket_1.attribute_domain = 'POINT'
    v_socket_1.hide_value = True
    v_socket_1.default_input = 'VALUE'
    v_socket_1.structure_type = 'AUTO'

    # Socket Hue
    hue_socket = _rr_yuv_adjustments.interface.new_socket(name="Hue", in_out='INPUT', socket_type='NodeSocketFloat')
    hue_socket.default_value = 0.0
    hue_socket.min_value = -10000.0
    hue_socket.max_value = 10000.0
    hue_socket.subtype = 'NONE'
    hue_socket.attribute_domain = 'POINT'
    hue_socket.default_input = 'VALUE'
    hue_socket.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket = _rr_yuv_adjustments.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket.default_value = 1.0
    saturation_socket.min_value = -10000.0
    saturation_socket.max_value = 10000.0
    saturation_socket.subtype = 'NONE'
    saturation_socket.attribute_domain = 'POINT'
    saturation_socket.default_input = 'VALUE'
    saturation_socket.structure_type = 'AUTO'

    # Initialize _rr_yuv_adjustments nodes

    # Node Frame.001
    frame_001 = _rr_yuv_adjustments.nodes.new("NodeFrame")
    frame_001.label = "Hue"
    frame_001.name = "Frame.001"
    frame_001.label_size = 20
    frame_001.shrink = True

    # Node Frame
    frame = _rr_yuv_adjustments.nodes.new("NodeFrame")
    frame.label = "Chroma"
    frame.name = "Frame"
    frame.label_size = 20
    frame.shrink = True

    # Node Group Input
    group_input = _rr_yuv_adjustments.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"

    # Node Reroute.003
    reroute_003 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_003.name = "Reroute.003"
    reroute_003.socket_idname = "NodeSocketFloat"
    # Node Reroute.004
    reroute_004 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_004.name = "Reroute.004"
    reroute_004.socket_idname = "NodeSocketFloat"
    # Node Math.002
    math_002 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.hide = True
    math_002.operation = 'COSINE'
    math_002.use_clamp = False

    # Node Math.001
    math_001 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.hide = True
    math_001.operation = 'MULTIPLY'
    math_001.use_clamp = False

    # Node Math.006
    math_006 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_006.name = "Math.006"
    math_006.hide = True
    math_006.operation = 'SINE'
    math_006.use_clamp = False

    # Node Math.005
    math_005 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_005.name = "Math.005"
    math_005.hide = True
    math_005.operation = 'MULTIPLY'
    math_005.use_clamp = False

    # Node Math.004
    math_004 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_004.name = "Math.004"
    math_004.hide = True
    math_004.operation = 'ADD'
    math_004.use_clamp = False

    # Node Math.007
    math_007 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_007.name = "Math.007"
    math_007.hide = True
    math_007.operation = 'COSINE'
    math_007.use_clamp = False

    # Node Math.008
    math_008 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_008.name = "Math.008"
    math_008.hide = True
    math_008.operation = 'MULTIPLY'
    math_008.use_clamp = False

    # Node Math.009
    math_009 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_009.name = "Math.009"
    math_009.hide = True
    math_009.operation = 'SINE'
    math_009.use_clamp = False

    # Node Math.010
    math_010 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_010.name = "Math.010"
    math_010.hide = True
    math_010.operation = 'MULTIPLY'
    math_010.use_clamp = False

    # Node Math.011
    math_011 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_011.name = "Math.011"
    math_011.hide = True
    math_011.operation = 'ADD'
    math_011.use_clamp = False

    # Node Reroute.002
    reroute_002 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_002.name = "Reroute.002"
    reroute_002.socket_idname = "NodeSocketFloat"
    # Node Reroute.001
    reroute_001 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_001.name = "Reroute.001"
    reroute_001.socket_idname = "NodeSocketFloat"
    # Node Reroute
    reroute = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute.name = "Reroute"
    reroute.socket_idname = "NodeSocketFloat"
    # Node Math
    math = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'MULTIPLY'
    math.use_clamp = False

    # Node Math.003
    math_003 = _rr_yuv_adjustments.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'MULTIPLY'
    math_003.use_clamp = False

    # Node Group Output
    group_output = _rr_yuv_adjustments.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # Node Mix
    mix = _rr_yuv_adjustments.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = 'FLOAT'
    mix.factor_mode = 'UNIFORM'

    # Node Mix.001
    mix_001 = _rr_yuv_adjustments.nodes.new("ShaderNodeMix")
    mix_001.name = "Mix.001"
    mix_001.blend_type = 'MIX'
    mix_001.clamp_factor = True
    mix_001.clamp_result = False
    mix_001.data_type = 'FLOAT'
    mix_001.factor_mode = 'UNIFORM'

    # Node Reroute.005
    reroute_005 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_005.name = "Reroute.005"
    reroute_005.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.006
    reroute_006 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_006.name = "Reroute.006"
    reroute_006.socket_idname = "NodeSocketFloat"
    # Node Reroute.007
    reroute_007 = _rr_yuv_adjustments.nodes.new("NodeReroute")
    reroute_007.name = "Reroute.007"
    reroute_007.socket_idname = "NodeSocketFloat"
    # Set parents
    math_002.parent = frame_001
    math_001.parent = frame_001
    math_006.parent = frame_001
    math_005.parent = frame_001
    math_004.parent = frame_001
    math_007.parent = frame_001
    math_008.parent = frame_001
    math_009.parent = frame_001
    math_010.parent = frame_001
    math_011.parent = frame_001
    reroute_002.parent = frame_001
    reroute_001.parent = frame_001
    reroute.parent = frame_001
    math.parent = frame
    math_003.parent = frame

    # Set locations
    frame_001.location = (-812.6248168945312, 201.2519989013672)
    frame.location = (151.5600128173828, 179.83200073242188)
    group_input.location = (-1296.9588623046875, 27.893131256103516)
    reroute_003.location = (-33.80141067504883, -275.7003173828125)
    reroute_004.location = (-810.5643310546875, -271.6595153808594)
    math_002.location = (184.15673828125, -94.94267272949219)
    math_001.location = (404.2100830078125, -40.43861389160156)
    math_006.location = (186.31982421875, -166.45095825195312)
    math_005.location = (402.09912109375, -116.27684020996094)
    math_004.location = (618.9151611328125, -45.77891540527344)
    math_007.location = (184.15673828125, -310.9474792480469)
    math_008.location = (404.2100830078125, -256.4434509277344)
    math_009.location = (186.31982421875, -382.45574951171875)
    math_010.location = (402.09912109375, -332.2816467285156)
    math_011.location = (618.9151611328125, -261.78375244140625)
    reroute_002.location = (34.02001953125, -89.28944396972656)
    reroute_001.location = (34.02001953125, -46.26676940917969)
    reroute.location = (34.02001953125, -397.4166259765625)
    math.location = (29.162338256835938, -35.5465087890625)
    math_003.location = (29.402603149414062, -194.0684814453125)
    group_output.location = (713.3328857421875, 463.1195373535156)
    mix.location = (486.8363342285156, 576.2271118164062)
    mix_001.location = (487.88323974609375, 395.04052734375)
    reroute_005.location = (-791.6239624023438, 377.03094482421875)
    reroute_006.location = (-793.6707153320312, 448.7335510253906)
    reroute_007.location = (-789.2373657226562, 269.1168212890625)

    # Set dimensions
    frame_001.width, frame_001.height = 788.1047973632812, 436.1520080566406
    frame.width, frame.height = 198.3200225830078, 364.51202392578125
    group_input.width, group_input.height = 140.0, 100.0
    reroute_003.width, reroute_003.height = 13.5, 100.0
    reroute_004.width, reroute_004.height = 13.5, 100.0
    math_002.width, math_002.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    math_006.width, math_006.height = 140.0, 100.0
    math_005.width, math_005.height = 140.0, 100.0
    math_004.width, math_004.height = 140.0, 100.0
    math_007.width, math_007.height = 140.0, 100.0
    math_008.width, math_008.height = 140.0, 100.0
    math_009.width, math_009.height = 140.0, 100.0
    math_010.width, math_010.height = 140.0, 100.0
    math_011.width, math_011.height = 140.0, 100.0
    reroute_002.width, reroute_002.height = 13.5, 100.0
    reroute_001.width, reroute_001.height = 13.5, 100.0
    reroute.width, reroute.height = 13.5, 100.0
    math.width, math.height = 140.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    group_output.width, group_output.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    mix_001.width, mix_001.height = 140.0, 100.0
    reroute_005.width, reroute_005.height = 13.5, 100.0
    reroute_006.width, reroute_006.height = 13.5, 100.0
    reroute_007.width, reroute_007.height = 13.5, 100.0

    # Initialize _rr_yuv_adjustments links

    # reroute_003.Output -> math.Value
    _rr_yuv_adjustments.links.new(reroute_003.outputs[0], math.inputs[1])
    # reroute_003.Output -> math_003.Value
    _rr_yuv_adjustments.links.new(reroute_003.outputs[0], math_003.inputs[1])
    # mix.Result -> group_output.U
    _rr_yuv_adjustments.links.new(mix.outputs[0], group_output.inputs[0])
    # mix_001.Result -> group_output.V
    _rr_yuv_adjustments.links.new(mix_001.outputs[0], group_output.inputs[1])
    # math_002.Value -> math_001.Value
    _rr_yuv_adjustments.links.new(math_002.outputs[0], math_001.inputs[1])
    # reroute.Output -> math_002.Value
    _rr_yuv_adjustments.links.new(reroute.outputs[0], math_002.inputs[0])
    # math_001.Value -> math_004.Value
    _rr_yuv_adjustments.links.new(math_001.outputs[0], math_004.inputs[0])
    # math_006.Value -> math_005.Value
    _rr_yuv_adjustments.links.new(math_006.outputs[0], math_005.inputs[1])
    # reroute.Output -> math_006.Value
    _rr_yuv_adjustments.links.new(reroute.outputs[0], math_006.inputs[0])
    # math_005.Value -> math_004.Value
    _rr_yuv_adjustments.links.new(math_005.outputs[0], math_004.inputs[1])
    # reroute_001.Output -> math_001.Value
    _rr_yuv_adjustments.links.new(reroute_001.outputs[0], math_001.inputs[0])
    # reroute_002.Output -> math_005.Value
    _rr_yuv_adjustments.links.new(reroute_002.outputs[0], math_005.inputs[0])
    # math_004.Value -> math.Value
    _rr_yuv_adjustments.links.new(math_004.outputs[0], math.inputs[0])
    # math_007.Value -> math_008.Value
    _rr_yuv_adjustments.links.new(math_007.outputs[0], math_008.inputs[1])
    # reroute.Output -> math_007.Value
    _rr_yuv_adjustments.links.new(reroute.outputs[0], math_007.inputs[0])
    # math_008.Value -> math_011.Value
    _rr_yuv_adjustments.links.new(math_008.outputs[0], math_011.inputs[0])
    # math_009.Value -> math_010.Value
    _rr_yuv_adjustments.links.new(math_009.outputs[0], math_010.inputs[1])
    # reroute.Output -> math_009.Value
    _rr_yuv_adjustments.links.new(reroute.outputs[0], math_009.inputs[0])
    # math_010.Value -> math_011.Value
    _rr_yuv_adjustments.links.new(math_010.outputs[0], math_011.inputs[1])
    # group_input.Hue -> reroute.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[3], reroute.inputs[0])
    # reroute_002.Output -> math_008.Value
    _rr_yuv_adjustments.links.new(reroute_002.outputs[0], math_008.inputs[0])
    # reroute_001.Output -> math_010.Value
    _rr_yuv_adjustments.links.new(reroute_001.outputs[0], math_010.inputs[0])
    # group_input.U -> reroute_001.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[1], reroute_001.inputs[0])
    # group_input.V -> reroute_002.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[2], reroute_002.inputs[0])
    # math_011.Value -> math_003.Value
    _rr_yuv_adjustments.links.new(math_011.outputs[0], math_003.inputs[0])
    # reroute_004.Output -> reroute_003.Input
    _rr_yuv_adjustments.links.new(reroute_004.outputs[0], reroute_003.inputs[0])
    # group_input.Saturation -> reroute_004.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[4], reroute_004.inputs[0])
    # reroute_006.Output -> mix.A
    _rr_yuv_adjustments.links.new(reroute_006.outputs[0], mix.inputs[2])
    # math.Value -> mix.B
    _rr_yuv_adjustments.links.new(math.outputs[0], mix.inputs[3])
    # math_003.Value -> mix_001.B
    _rr_yuv_adjustments.links.new(math_003.outputs[0], mix_001.inputs[3])
    # reroute_007.Output -> mix_001.A
    _rr_yuv_adjustments.links.new(reroute_007.outputs[0], mix_001.inputs[2])
    # reroute_005.Output -> mix_001.Factor
    _rr_yuv_adjustments.links.new(reroute_005.outputs[0], mix_001.inputs[0])
    # reroute_005.Output -> mix.Factor
    _rr_yuv_adjustments.links.new(reroute_005.outputs[0], mix.inputs[0])
    # group_input.Factor -> reroute_005.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[0], reroute_005.inputs[0])
    # group_input.U -> reroute_006.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[1], reroute_006.inputs[0])
    # group_input.V -> reroute_007.Input
    _rr_yuv_adjustments.links.new(group_input.outputs[2], reroute_007.inputs[0])

    return _rr_yuv_adjustments


_rr_yuv_adjustments = _rr_yuv_adjustments_node_group()

def _rr_saturation_node_group():
    """Initialize .RR_saturation node group"""
    _rr_saturation = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_saturation")

    _rr_saturation.color_tag = 'NONE'
    _rr_saturation.description = ""
    _rr_saturation.default_group_node_width = 140
    # _rr_saturation interface

    # Socket Image
    image_socket = _rr_saturation.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket.attribute_domain = 'POINT'
    image_socket.default_input = 'VALUE'
    image_socket.structure_type = 'AUTO'

    # Socket Fac
    fac_socket = _rr_saturation.interface.new_socket(name="Fac", in_out='INPUT', socket_type='NodeSocketFloat')
    fac_socket.default_value = 1.0
    fac_socket.min_value = 0.0
    fac_socket.max_value = 1.0
    fac_socket.subtype = 'FACTOR'
    fac_socket.attribute_domain = 'POINT'
    fac_socket.default_input = 'VALUE'
    fac_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_1 = _rr_saturation.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_1.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_1.attribute_domain = 'POINT'
    image_socket_1.default_input = 'VALUE'
    image_socket_1.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_1 = _rr_saturation.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_1.default_value = 1.0
    saturation_socket_1.min_value = 0.0
    saturation_socket_1.max_value = 2.0
    saturation_socket_1.subtype = 'FACTOR'
    saturation_socket_1.attribute_domain = 'POINT'
    saturation_socket_1.default_input = 'VALUE'
    saturation_socket_1.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket = _rr_saturation.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket.default_value = 0.5
    perceptual_socket.min_value = 0.0
    perceptual_socket.max_value = 1.0
    perceptual_socket.subtype = 'FACTOR'
    perceptual_socket.attribute_domain = 'POINT'
    perceptual_socket.default_input = 'VALUE'
    perceptual_socket.structure_type = 'AUTO'

    # Initialize _rr_saturation nodes

    # Node Separate Color.002
    separate_color_002 = _rr_saturation.nodes.new("CompositorNodeSeparateColor")
    separate_color_002.name = "Separate Color.002"
    separate_color_002.mode = 'HSV'
    separate_color_002.ycc_mode = 'ITUBT709'

    # Node Group Input
    group_input_1 = _rr_saturation.nodes.new("NodeGroupInput")
    group_input_1.name = "Group Input"

    # Node Combine Color.001
    combine_color_001 = _rr_saturation.nodes.new("CompositorNodeCombineColor")
    combine_color_001.name = "Combine Color.001"
    combine_color_001.mode = 'HSV'
    combine_color_001.ycc_mode = 'ITUBT709'

    # Node Math.001
    math_001_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_001_1.name = "Math.001"
    math_001_1.hide = True
    math_001_1.operation = 'MULTIPLY'
    math_001_1.use_clamp = True

    # Node Separate Color.001
    separate_color_001 = _rr_saturation.nodes.new("CompositorNodeSeparateColor")
    separate_color_001.name = "Separate Color.001"
    separate_color_001.mode = 'YUV'
    separate_color_001.ycc_mode = 'ITUBT709'

    # Node YUV
    yuv = _rr_saturation.nodes.new("CompositorNodeGroup")
    yuv.label = "YUV"
    yuv.name = "YUV"
    yuv.node_tree = _rr_yuv_adjustments
    # Socket_6
    yuv.inputs[0].default_value = 1.0
    # Socket_5
    yuv.inputs[3].default_value = 0.0

    # Node Reroute
    reroute_1 = _rr_saturation.nodes.new("NodeReroute")
    reroute_1.name = "Reroute"
    reroute_1.socket_idname = "NodeSocketFloatFactor"
    # Node Combine Color
    combine_color = _rr_saturation.nodes.new("CompositorNodeCombineColor")
    combine_color.name = "Combine Color"
    combine_color.mode = 'YUV'
    combine_color.ycc_mode = 'ITUBT709'

    # Node Group Output
    group_output_1 = _rr_saturation.nodes.new("NodeGroupOutput")
    group_output_1.name = "Group Output"
    group_output_1.is_active_output = True

    # Node Mix.001
    mix_001_1 = _rr_saturation.nodes.new("ShaderNodeMix")
    mix_001_1.name = "Mix.001"
    mix_001_1.blend_type = 'MIX'
    mix_001_1.clamp_factor = False
    mix_001_1.clamp_result = False
    mix_001_1.data_type = 'RGBA'
    mix_001_1.factor_mode = 'UNIFORM'

    # Node Mix
    mix_1 = _rr_saturation.nodes.new("ShaderNodeMix")
    mix_1.name = "Mix"
    mix_1.blend_type = 'MIX'
    mix_1.clamp_factor = False
    mix_1.clamp_result = False
    mix_1.data_type = 'RGBA'
    mix_1.factor_mode = 'UNIFORM'

    # Node Separate Color.003
    separate_color_003 = _rr_saturation.nodes.new("CompositorNodeSeparateColor")
    separate_color_003.name = "Separate Color.003"
    separate_color_003.mode = 'HSV'
    separate_color_003.ycc_mode = 'ITUBT709'

    # Node Combine Color.002
    combine_color_002 = _rr_saturation.nodes.new("CompositorNodeCombineColor")
    combine_color_002.name = "Combine Color.002"
    combine_color_002.mode = 'HSV'
    combine_color_002.ycc_mode = 'ITUBT709'

    # Node Map Range
    map_range = _rr_saturation.nodes.new("ShaderNodeMapRange")
    map_range.name = "Map Range"
    map_range.clamp = True
    map_range.data_type = 'FLOAT'
    map_range.interpolation_type = 'LINEAR'
    # From Min
    map_range.inputs[1].default_value = 0.0
    # From Max
    map_range.inputs[2].default_value = 1.0
    # To Min
    map_range.inputs[3].default_value = 0.0
    # To Max
    map_range.inputs[4].default_value = 1.0

    # Node Separate Color.004
    separate_color_004 = _rr_saturation.nodes.new("CompositorNodeSeparateColor")
    separate_color_004.name = "Separate Color.004"
    separate_color_004.mode = 'HSV'
    separate_color_004.ycc_mode = 'ITUBT709'

    # Node Combine Color.003
    combine_color_003 = _rr_saturation.nodes.new("CompositorNodeCombineColor")
    combine_color_003.name = "Combine Color.003"
    combine_color_003.mode = 'HSV'
    combine_color_003.ycc_mode = 'ITUBT709'

    # Node Math
    math_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_1.name = "Math"
    math_1.hide = True
    math_1.operation = 'MINIMUM'
    math_1.use_clamp = False

    # Node Reroute.005
    reroute_005_1 = _rr_saturation.nodes.new("NodeReroute")
    reroute_005_1.name = "Reroute.005"
    reroute_005_1.socket_idname = "NodeSocketFloat"
    # Node Mix.002
    mix_002 = _rr_saturation.nodes.new("ShaderNodeMix")
    mix_002.name = "Mix.002"
    mix_002.blend_type = 'MIX'
    mix_002.clamp_factor = False
    mix_002.clamp_result = False
    mix_002.data_type = 'RGBA'
    mix_002.factor_mode = 'UNIFORM'

    # Node Math.002
    math_002_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_002_1.name = "Math.002"
    math_002_1.operation = 'MULTIPLY'
    math_002_1.use_clamp = True

    # Node Map Range.001
    map_range_001 = _rr_saturation.nodes.new("ShaderNodeMapRange")
    map_range_001.name = "Map Range.001"
    map_range_001.clamp = True
    map_range_001.data_type = 'FLOAT'
    map_range_001.interpolation_type = 'LINEAR'
    # From Min
    map_range_001.inputs[1].default_value = 0.5
    # From Max
    map_range_001.inputs[2].default_value = 1.0
    # To Min
    map_range_001.inputs[3].default_value = 1.0
    # To Max
    map_range_001.inputs[4].default_value = 0.0

    # Node Map Range.002
    map_range_002 = _rr_saturation.nodes.new("ShaderNodeMapRange")
    map_range_002.name = "Map Range.002"
    map_range_002.clamp = True
    map_range_002.data_type = 'FLOAT'
    map_range_002.interpolation_type = 'LINEAR'
    # From Min
    map_range_002.inputs[1].default_value = 0.0
    # From Max
    map_range_002.inputs[2].default_value = 0.5
    # To Min
    map_range_002.inputs[3].default_value = 0.0
    # To Max
    map_range_002.inputs[4].default_value = 1.0

    # Node Switch
    switch = _rr_saturation.nodes.new("CompositorNodeSwitch")
    switch.name = "Switch"

    # Node Group Input.001
    group_input_001 = _rr_saturation.nodes.new("NodeGroupInput")
    group_input_001.name = "Group Input.001"

    # Node Math.003
    math_003_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_003_1.name = "Math.003"
    math_003_1.hide = True
    math_003_1.operation = 'ADD'
    math_003_1.use_clamp = False

    # Node Math.004
    math_004_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_004_1.name = "Math.004"
    math_004_1.operation = 'SUBTRACT'
    math_004_1.use_clamp = False
    # Value_001
    math_004_1.inputs[1].default_value = 1.0

    # Node Math.005
    math_005_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_005_1.name = "Math.005"
    math_005_1.hide = True
    math_005_1.operation = 'ABSOLUTE'
    math_005_1.use_clamp = False

    # Node Math.006
    math_006_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_006_1.name = "Math.006"
    math_006_1.operation = 'SUBTRACT'
    math_006_1.use_clamp = False
    # Value_001
    math_006_1.inputs[1].default_value = 1.0

    # Node Math.007
    math_007_1 = _rr_saturation.nodes.new("ShaderNodeMath")
    math_007_1.name = "Math.007"
    math_007_1.hide = True
    math_007_1.operation = 'ABSOLUTE'
    math_007_1.use_clamp = False

    # Node Frame
    frame_1 = _rr_saturation.nodes.new("NodeFrame")
    frame_1.label = "Does not work when Sat is not a single value"
    frame_1.name = "Frame"
    frame_1.label_size = 20
    frame_1.shrink = True

    # Set parents
    switch.parent = frame_1
    math_003_1.parent = frame_1
    math_004_1.parent = frame_1
    math_005_1.parent = frame_1
    math_006_1.parent = frame_1
    math_007_1.parent = frame_1

    # Set locations
    separate_color_002.location = (-1246.8607177734375, 223.02792358398438)
    group_input_1.location = (-1869.4866943359375, -40.0)
    combine_color_001.location = (-358.6033020019531, 264.7619934082031)
    math_001_1.location = (-774.5558471679688, 66.31111907958984)
    separate_color_001.location = (-1385.9456787109375, -604.56787109375)
    yuv.location = (-1157.904052734375, -646.5054931640625)
    reroute_1.location = (-1385.9456787109375, -834.9468994140625)
    combine_color.location = (-885.945556640625, -584.56787109375)
    group_output_1.location = (1689.539306640625, 258.4005432128906)
    mix_001_1.location = (1245.783447265625, 303.24847412109375)
    mix_1.location = (291.661376953125, 75.9622573852539)
    separate_color_003.location = (486.8824462890625, 64.26908111572266)
    combine_color_002.location = (886.8824462890625, 64.26908111572266)
    map_range.location = (684.8823852539062, 84.26908111572266)
    separate_color_004.location = (-640.9152221679688, -808.2415161132812)
    combine_color_003.location = (-244.4824981689453, -771.9412841796875)
    math_1.location = (-434.6631164550781, -793.5341796875)
    reroute_005_1.location = (-748.3933715820312, -293.2272644042969)
    mix_002.location = (2.5975937843322754, -467.9107971191406)
    math_002_1.location = (-449.0088806152344, -425.15350341796875)
    map_range_001.location = (-890.8894653320312, -332.3018798828125)
    map_range_002.location = (-359.2393493652344, 62.30069351196289)
    switch.location = (595.3917236328125, -317.9326171875)
    group_input_001.location = (710.4332885742188, 576.3576049804688)
    math_003_1.location = (414.886962890625, -273.75836181640625)
    math_004_1.location = (29.43701171875, -193.4512939453125)
    math_005_1.location = (224.0989990234375, -295.52435302734375)
    math_006_1.location = (35.1094970703125, -35.689697265625)
    math_007_1.location = (229.771484375, -137.76275634765625)
    frame_1.location = (1181.1600341796875, 896.9519653320312)

    # Set dimensions
    separate_color_002.width, separate_color_002.height = 140.0, 100.0
    group_input_1.width, group_input_1.height = 140.0, 100.0
    combine_color_001.width, combine_color_001.height = 140.0, 100.0
    math_001_1.width, math_001_1.height = 140.0, 100.0
    separate_color_001.width, separate_color_001.height = 140.0, 100.0
    yuv.width, yuv.height = 187.7114715576172, 100.0
    reroute_1.width, reroute_1.height = 13.5, 100.0
    combine_color.width, combine_color.height = 140.0, 100.0
    group_output_1.width, group_output_1.height = 140.0, 100.0
    mix_001_1.width, mix_001_1.height = 140.0, 100.0
    mix_1.width, mix_1.height = 140.0, 100.0
    separate_color_003.width, separate_color_003.height = 140.0, 100.0
    combine_color_002.width, combine_color_002.height = 140.0, 100.0
    map_range.width, map_range.height = 140.0, 100.0
    separate_color_004.width, separate_color_004.height = 140.0, 100.0
    combine_color_003.width, combine_color_003.height = 140.0, 100.0
    math_1.width, math_1.height = 130.14614868164062, 100.0
    reroute_005_1.width, reroute_005_1.height = 13.5, 100.0
    mix_002.width, mix_002.height = 140.0, 100.0
    math_002_1.width, math_002_1.height = 140.0, 100.0
    map_range_001.width, map_range_001.height = 140.0, 100.0
    map_range_002.width, map_range_002.height = 140.0, 100.0
    switch.width, switch.height = 140.0, 100.0
    group_input_001.width, group_input_001.height = 140.0, 100.0
    math_003_1.width, math_003_1.height = 140.0, 100.0
    math_004_1.width, math_004_1.height = 140.0, 100.0
    math_005_1.width, math_005_1.height = 140.0, 100.0
    math_006_1.width, math_006_1.height = 140.0, 100.0
    math_007_1.width, math_007_1.height = 140.0, 100.0
    frame_1.width, frame_1.height = 764.239990234375, 461.7119445800781

    # Initialize _rr_saturation links

    # separate_color_001.Alpha -> combine_color.Alpha
    _rr_saturation.links.new(separate_color_001.outputs[3], combine_color.inputs[3])
    # group_input_1.Image -> separate_color_001.Image
    _rr_saturation.links.new(group_input_1.outputs[1], separate_color_001.inputs[0])
    # separate_color_002.Alpha -> combine_color_001.Alpha
    _rr_saturation.links.new(separate_color_002.outputs[3], combine_color_001.inputs[3])
    # separate_color_002.Blue -> combine_color_001.Blue
    _rr_saturation.links.new(separate_color_002.outputs[2], combine_color_001.inputs[2])
    # separate_color_002.Green -> math_001_1.Value
    _rr_saturation.links.new(separate_color_002.outputs[1], math_001_1.inputs[0])
    # separate_color_002.Red -> combine_color_001.Red
    _rr_saturation.links.new(separate_color_002.outputs[0], combine_color_001.inputs[0])
    # math_001_1.Value -> combine_color_001.Green
    _rr_saturation.links.new(math_001_1.outputs[0], combine_color_001.inputs[1])
    # group_input_1.Image -> separate_color_002.Image
    _rr_saturation.links.new(group_input_1.outputs[1], separate_color_002.inputs[0])
    # group_input_1.Saturation -> math_001_1.Value
    _rr_saturation.links.new(group_input_1.outputs[2], math_001_1.inputs[1])
    # combine_color_001.Image -> mix_1.A
    _rr_saturation.links.new(combine_color_001.outputs[0], mix_1.inputs[6])
    # separate_color_001.Green -> yuv.U
    _rr_saturation.links.new(separate_color_001.outputs[1], yuv.inputs[1])
    # separate_color_001.Blue -> yuv.V
    _rr_saturation.links.new(separate_color_001.outputs[2], yuv.inputs[2])
    # yuv.U -> combine_color.Green
    _rr_saturation.links.new(yuv.outputs[0], combine_color.inputs[1])
    # yuv.V -> combine_color.Blue
    _rr_saturation.links.new(yuv.outputs[1], combine_color.inputs[2])
    # separate_color_001.Red -> combine_color.Red
    _rr_saturation.links.new(separate_color_001.outputs[0], combine_color.inputs[0])
    # reroute_1.Output -> yuv.Saturation
    _rr_saturation.links.new(reroute_1.outputs[0], yuv.inputs[4])
    # group_input_1.Saturation -> reroute_1.Input
    _rr_saturation.links.new(group_input_1.outputs[2], reroute_1.inputs[0])
    # separate_color_003.Alpha -> combine_color_002.Alpha
    _rr_saturation.links.new(separate_color_003.outputs[3], combine_color_002.inputs[3])
    # separate_color_003.Blue -> combine_color_002.Blue
    _rr_saturation.links.new(separate_color_003.outputs[2], combine_color_002.inputs[2])
    # separate_color_003.Red -> combine_color_002.Red
    _rr_saturation.links.new(separate_color_003.outputs[0], combine_color_002.inputs[0])
    # mix_1.Result -> separate_color_003.Image
    _rr_saturation.links.new(mix_1.outputs[2], separate_color_003.inputs[0])
    # combine_color_002.Image -> mix_001_1.B
    _rr_saturation.links.new(combine_color_002.outputs[0], mix_001_1.inputs[7])
    # separate_color_003.Green -> map_range.Value
    _rr_saturation.links.new(separate_color_003.outputs[1], map_range.inputs[0])
    # map_range.Result -> combine_color_002.Green
    _rr_saturation.links.new(map_range.outputs[0], combine_color_002.inputs[1])
    # separate_color_004.Alpha -> combine_color_003.Alpha
    _rr_saturation.links.new(separate_color_004.outputs[3], combine_color_003.inputs[3])
    # separate_color_004.Red -> combine_color_003.Red
    _rr_saturation.links.new(separate_color_004.outputs[0], combine_color_003.inputs[0])
    # combine_color.Image -> separate_color_004.Image
    _rr_saturation.links.new(combine_color.outputs[0], separate_color_004.inputs[0])
    # separate_color_004.Green -> combine_color_003.Green
    _rr_saturation.links.new(separate_color_004.outputs[1], combine_color_003.inputs[1])
    # separate_color_004.Blue -> math_1.Value
    _rr_saturation.links.new(separate_color_004.outputs[2], math_1.inputs[1])
    # reroute_005_1.Output -> math_1.Value
    _rr_saturation.links.new(reroute_005_1.outputs[0], math_1.inputs[0])
    # separate_color_002.Blue -> reroute_005_1.Input
    _rr_saturation.links.new(separate_color_002.outputs[2], reroute_005_1.inputs[0])
    # math_1.Value -> combine_color_003.Blue
    _rr_saturation.links.new(math_1.outputs[0], combine_color_003.inputs[2])
    # combine_color.Image -> mix_002.A
    _rr_saturation.links.new(combine_color.outputs[0], mix_002.inputs[6])
    # combine_color_003.Image -> mix_002.B
    _rr_saturation.links.new(combine_color_003.outputs[0], mix_002.inputs[7])
    # reroute_005_1.Output -> math_002_1.Value
    _rr_saturation.links.new(reroute_005_1.outputs[0], math_002_1.inputs[0])
    # group_input_1.Perceptual -> map_range_001.Value
    _rr_saturation.links.new(group_input_1.outputs[3], map_range_001.inputs[0])
    # map_range_001.Result -> math_002_1.Value
    _rr_saturation.links.new(map_range_001.outputs[0], math_002_1.inputs[1])
    # group_input_1.Perceptual -> map_range_002.Value
    _rr_saturation.links.new(group_input_1.outputs[3], map_range_002.inputs[0])
    # map_range_002.Result -> mix_1.Factor
    _rr_saturation.links.new(map_range_002.outputs[0], mix_1.inputs[0])
    # math_002_1.Value -> mix_002.Factor
    _rr_saturation.links.new(math_002_1.outputs[0], mix_002.inputs[0])
    # mix_002.Result -> mix_1.B
    _rr_saturation.links.new(mix_002.outputs[2], mix_1.inputs[7])
    # group_input_001.Fac -> mix_001_1.Factor
    _rr_saturation.links.new(group_input_001.outputs[0], mix_001_1.inputs[0])
    # group_input_001.Image -> mix_001_1.A
    _rr_saturation.links.new(group_input_001.outputs[1], mix_001_1.inputs[6])
    # group_input_001.Image -> switch.Off
    _rr_saturation.links.new(group_input_001.outputs[1], switch.inputs[1])
    # group_input_001.Saturation -> math_004_1.Value
    _rr_saturation.links.new(group_input_001.outputs[2], math_004_1.inputs[0])
    # math_004_1.Value -> math_005_1.Value
    _rr_saturation.links.new(math_004_1.outputs[0], math_005_1.inputs[0])
    # math_005_1.Value -> math_003_1.Value
    _rr_saturation.links.new(math_005_1.outputs[0], math_003_1.inputs[1])
    # math_003_1.Value -> switch.Switch
    _rr_saturation.links.new(math_003_1.outputs[0], switch.inputs[0])
    # math_006_1.Value -> math_007_1.Value
    _rr_saturation.links.new(math_006_1.outputs[0], math_007_1.inputs[0])
    # group_input_001.Fac -> math_006_1.Value
    _rr_saturation.links.new(group_input_001.outputs[0], math_006_1.inputs[0])
    # math_007_1.Value -> math_003_1.Value
    _rr_saturation.links.new(math_007_1.outputs[0], math_003_1.inputs[0])
    # mix_001_1.Result -> switch.On
    _rr_saturation.links.new(mix_001_1.outputs[2], switch.inputs[2])
    # mix_001_1.Result -> group_output_1.Image
    _rr_saturation.links.new(mix_001_1.outputs[2], group_output_1.inputs[0])

    return _rr_saturation


_rr_saturation = _rr_saturation_node_group()

def _rr_color_boost_node_group():
    """Initialize .RR_color_boost node group"""
    _rr_color_boost = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_color_boost")

    _rr_color_boost.color_tag = 'NONE'
    _rr_color_boost.description = ""
    _rr_color_boost.default_group_node_width = 140
    # _rr_color_boost interface

    # Socket Image
    image_socket_2 = _rr_color_boost.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_2.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_2.attribute_domain = 'POINT'
    image_socket_2.default_input = 'VALUE'
    image_socket_2.structure_type = 'AUTO'

    # Socket Image
    image_socket_3 = _rr_color_boost.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_3.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_3.attribute_domain = 'POINT'
    image_socket_3.default_input = 'VALUE'
    image_socket_3.structure_type = 'AUTO'

    # Socket Strength
    strength_socket = _rr_color_boost.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket.default_value = 0.0
    strength_socket.min_value = -1.0
    strength_socket.max_value = 1.0
    strength_socket.subtype = 'FACTOR'
    strength_socket.attribute_domain = 'POINT'
    strength_socket.description = "Adjusts the saturation of lower saturated areas without changing highly saturated areas, pre-transform"
    strength_socket.default_input = 'VALUE'
    strength_socket.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket_1 = _rr_color_boost.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket_1.default_value = 1.0
    perceptual_socket_1.min_value = 0.0
    perceptual_socket_1.max_value = 1.0
    perceptual_socket_1.subtype = 'FACTOR'
    perceptual_socket_1.attribute_domain = 'POINT'
    perceptual_socket_1.default_input = 'VALUE'
    perceptual_socket_1.structure_type = 'AUTO'

    # Initialize _rr_color_boost nodes

    # Node Map Range
    map_range_1 = _rr_color_boost.nodes.new("ShaderNodeMapRange")
    map_range_1.name = "Map Range"
    map_range_1.clamp = False
    map_range_1.data_type = 'FLOAT'
    map_range_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_1.inputs[1].default_value = 0.0
    # From Max
    map_range_1.inputs[2].default_value = 1.0
    # To Min
    map_range_1.inputs[3].default_value = 1.0
    # To Max
    map_range_1.inputs[4].default_value = 4.0

    # Node Map Range.001
    map_range_001_1 = _rr_color_boost.nodes.new("ShaderNodeMapRange")
    map_range_001_1.name = "Map Range.001"
    map_range_001_1.clamp = False
    map_range_001_1.data_type = 'FLOAT'
    map_range_001_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_1.inputs[1].default_value = 0.0
    # From Max
    map_range_001_1.inputs[2].default_value = 1.0
    # To Min
    map_range_001_1.inputs[3].default_value = 1.0
    # To Max
    map_range_001_1.inputs[4].default_value = 0.0

    # Node Separate Color.001
    separate_color_001_1 = _rr_color_boost.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_1.name = "Separate Color.001"
    separate_color_001_1.mode = 'HSV'
    separate_color_001_1.ycc_mode = 'ITUBT709'
    separate_color_001_1.outputs[0].hide = True
    separate_color_001_1.outputs[2].hide = True
    separate_color_001_1.outputs[3].hide = True

    # Node Math
    math_2 = _rr_color_boost.nodes.new("ShaderNodeMath")
    math_2.name = "Math"
    math_2.hide = True
    math_2.operation = 'MULTIPLY'
    math_2.use_clamp = False

    # Node Group Output
    group_output_2 = _rr_color_boost.nodes.new("NodeGroupOutput")
    group_output_2.name = "Group Output"
    group_output_2.is_active_output = True

    # Node Group Input
    group_input_2 = _rr_color_boost.nodes.new("NodeGroupInput")
    group_input_2.name = "Group Input"

    # Node Saturation
    saturation = _rr_color_boost.nodes.new("CompositorNodeGroup")
    saturation.label = "Saturation"
    saturation.name = "Saturation"
    saturation.node_tree = _rr_saturation
    # Socket_4
    saturation.inputs[0].default_value = 1.0

    # Node Math.001
    math_001_2 = _rr_color_boost.nodes.new("ShaderNodeMath")
    math_001_2.name = "Math.001"
    math_001_2.operation = 'ABSOLUTE'
    math_001_2.use_clamp = False

    # Node Switch
    switch_1 = _rr_color_boost.nodes.new("CompositorNodeSwitch")
    switch_1.name = "Switch"

    # Node Math.002
    math_002_2 = _rr_color_boost.nodes.new("ShaderNodeMath")
    math_002_2.name = "Math.002"
    math_002_2.operation = 'LESS_THAN'
    math_002_2.use_clamp = False
    # Value_001
    math_002_2.inputs[1].default_value = 0.0

    # Node Math.003
    math_003_2 = _rr_color_boost.nodes.new("ShaderNodeMath")
    math_003_2.name = "Math.003"
    math_003_2.operation = 'ADD'
    math_003_2.use_clamp = True

    # Set locations
    map_range_1.location = (-141.8714141845703, -64.75092315673828)
    map_range_001_1.location = (-541.8714599609375, -104.75093078613281)
    separate_color_001_1.location = (-721.8714599609375, -184.7509307861328)
    math_2.location = (-341.8714294433594, -64.75092315673828)
    group_output_2.location = (1098.199951171875, 144.76531982421875)
    group_input_2.location = (-1136.5186767578125, 98.28276062011719)
    saturation.location = (590.58935546875, 144.76531982421875)
    math_001_2.location = (-327.9425048828125, 314.1860656738281)
    switch_1.location = (865.4786376953125, 275.9734191894531)
    math_002_2.location = (-154.54383850097656, 101.55369567871094)
    math_003_2.location = (23.522119522094727, 102.47196197509766)

    # Set dimensions
    map_range_1.width, map_range_1.height = 140.0, 100.0
    map_range_001_1.width, map_range_001_1.height = 140.0, 100.0
    separate_color_001_1.width, separate_color_001_1.height = 140.0, 100.0
    math_2.width, math_2.height = 140.0, 100.0
    group_output_2.width, group_output_2.height = 140.0, 100.0
    group_input_2.width, group_input_2.height = 140.0, 100.0
    saturation.width, saturation.height = 169.08709716796875, 100.0
    math_001_2.width, math_001_2.height = 140.0, 100.0
    switch_1.width, switch_1.height = 140.0, 100.0
    math_002_2.width, math_002_2.height = 140.0, 100.0
    math_003_2.width, math_003_2.height = 140.0, 100.0

    # Initialize _rr_color_boost links

    # group_input_2.Image -> separate_color_001_1.Image
    _rr_color_boost.links.new(group_input_2.outputs[0], separate_color_001_1.inputs[0])
    # group_input_2.Image -> saturation.Image
    _rr_color_boost.links.new(group_input_2.outputs[0], saturation.inputs[1])
    # group_input_2.Strength -> math_2.Value
    _rr_color_boost.links.new(group_input_2.outputs[1], math_2.inputs[0])
    # math_2.Value -> map_range_1.Value
    _rr_color_boost.links.new(math_2.outputs[0], map_range_1.inputs[0])
    # separate_color_001_1.Green -> map_range_001_1.Value
    _rr_color_boost.links.new(separate_color_001_1.outputs[1], map_range_001_1.inputs[0])
    # map_range_001_1.Result -> math_2.Value
    _rr_color_boost.links.new(map_range_001_1.outputs[0], math_2.inputs[1])
    # group_input_2.Strength -> math_001_2.Value
    _rr_color_boost.links.new(group_input_2.outputs[1], math_001_2.inputs[0])
    # saturation.Image -> switch_1.On
    _rr_color_boost.links.new(saturation.outputs[0], switch_1.inputs[2])
    # switch_1.Image -> group_output_2.Image
    _rr_color_boost.links.new(switch_1.outputs[0], group_output_2.inputs[0])
    # math_001_2.Value -> switch_1.Switch
    _rr_color_boost.links.new(math_001_2.outputs[0], switch_1.inputs[0])
    # group_input_2.Image -> switch_1.Off
    _rr_color_boost.links.new(group_input_2.outputs[0], switch_1.inputs[1])
    # map_range_1.Result -> saturation.Saturation
    _rr_color_boost.links.new(map_range_1.outputs[0], saturation.inputs[2])
    # group_input_2.Strength -> math_002_2.Value
    _rr_color_boost.links.new(group_input_2.outputs[1], math_002_2.inputs[0])
    # math_002_2.Value -> math_003_2.Value
    _rr_color_boost.links.new(math_002_2.outputs[0], math_003_2.inputs[0])
    # group_input_2.Perceptual -> math_003_2.Value
    _rr_color_boost.links.new(group_input_2.outputs[2], math_003_2.inputs[1])
    # math_003_2.Value -> saturation.Perceptual
    _rr_color_boost.links.new(math_003_2.outputs[0], saturation.inputs[3])

    return _rr_color_boost


_rr_color_boost = _rr_color_boost_node_group()

def _rr_white_balance_node_group():
    """Initialize .RR_white_balance node group"""
    _rr_white_balance = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_white_balance")

    _rr_white_balance.color_tag = 'NONE'
    _rr_white_balance.description = ""
    _rr_white_balance.default_group_node_width = 140
    # _rr_white_balance interface

    # Socket Image
    image_socket_4 = _rr_white_balance.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_4.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_4.attribute_domain = 'POINT'
    image_socket_4.default_input = 'VALUE'
    image_socket_4.structure_type = 'AUTO'

    # Socket Image
    image_socket_5 = _rr_white_balance.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_5.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_5.attribute_domain = 'POINT'
    image_socket_5.default_input = 'VALUE'
    image_socket_5.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_1 = _rr_white_balance.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_1.default_value = 1.0
    factor_socket_1.min_value = 0.0
    factor_socket_1.max_value = 1.0
    factor_socket_1.subtype = 'FACTOR'
    factor_socket_1.attribute_domain = 'POINT'
    factor_socket_1.default_input = 'VALUE'
    factor_socket_1.structure_type = 'AUTO'

    # Socket Temperature
    temperature_socket = _rr_white_balance.interface.new_socket(name="Temperature", in_out='INPUT', socket_type='NodeSocketFloat')
    temperature_socket.default_value = 0.5
    temperature_socket.min_value = 0.0
    temperature_socket.max_value = 1.0
    temperature_socket.subtype = 'FACTOR'
    temperature_socket.attribute_domain = 'POINT'
    temperature_socket.description = "Adjusts the prominence of the red and blue channels for a warmer or cooler look, pre-transform"
    temperature_socket.default_input = 'VALUE'
    temperature_socket.structure_type = 'AUTO'

    # Socket Tint
    tint_socket = _rr_white_balance.interface.new_socket(name="Tint", in_out='INPUT', socket_type='NodeSocketFloat')
    tint_socket.default_value = 0.5
    tint_socket.min_value = 0.0
    tint_socket.max_value = 1.0
    tint_socket.subtype = 'FACTOR'
    tint_socket.attribute_domain = 'POINT'
    tint_socket.description = "Adjusts the prominence of the green channel for a green or purple look, pre-transform"
    tint_socket.default_input = 'VALUE'
    tint_socket.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket_2 = _rr_white_balance.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket_2.default_value = 0.0
    perceptual_socket_2.min_value = 0.0
    perceptual_socket_2.max_value = 1.0
    perceptual_socket_2.subtype = 'FACTOR'
    perceptual_socket_2.attribute_domain = 'POINT'
    perceptual_socket_2.default_input = 'VALUE'
    perceptual_socket_2.structure_type = 'AUTO'

    # Initialize _rr_white_balance nodes

    # Node Group Output
    group_output_3 = _rr_white_balance.nodes.new("NodeGroupOutput")
    group_output_3.name = "Group Output"
    group_output_3.is_active_output = True

    # Node Math.002
    math_002_3 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_002_3.name = "Math.002"
    math_002_3.hide = True
    math_002_3.operation = 'MULTIPLY'
    math_002_3.use_clamp = False

    # Node Reroute.001
    reroute_001_1 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_001_1.name = "Reroute.001"
    reroute_001_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_1 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_002_1.name = "Reroute.002"
    reroute_002_1.socket_idname = "NodeSocketFloat"
    # Node Math.001
    math_001_3 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_001_3.name = "Math.001"
    math_001_3.hide = True
    math_001_3.operation = 'MULTIPLY'
    math_001_3.use_clamp = False

    # Node Math.003
    math_003_3 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_003_3.name = "Math.003"
    math_003_3.hide = True
    math_003_3.operation = 'MULTIPLY'
    math_003_3.use_clamp = False

    # Node Map Range.001
    map_range_001_2 = _rr_white_balance.nodes.new("ShaderNodeMapRange")
    map_range_001_2.name = "Map Range.001"
    map_range_001_2.hide = True
    map_range_001_2.clamp = False
    map_range_001_2.data_type = 'FLOAT'
    map_range_001_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_2.inputs[1].default_value = 0.0
    # From Max
    map_range_001_2.inputs[2].default_value = 1.0
    # To Min
    map_range_001_2.inputs[3].default_value = 0.0
    # To Max
    map_range_001_2.inputs[4].default_value = 2.0

    # Node Map Range.002
    map_range_002_1 = _rr_white_balance.nodes.new("ShaderNodeMapRange")
    map_range_002_1.name = "Map Range.002"
    map_range_002_1.hide = True
    map_range_002_1.clamp = False
    map_range_002_1.data_type = 'FLOAT'
    map_range_002_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_1.inputs[1].default_value = 0.0
    # From Max
    map_range_002_1.inputs[2].default_value = 1.0
    # To Min
    map_range_002_1.inputs[3].default_value = 2.0
    # To Max
    map_range_002_1.inputs[4].default_value = 0.0

    # Node Map Range.003
    map_range_003 = _rr_white_balance.nodes.new("ShaderNodeMapRange")
    map_range_003.name = "Map Range.003"
    map_range_003.hide = True
    map_range_003.clamp = False
    map_range_003.data_type = 'FLOAT'
    map_range_003.interpolation_type = 'LINEAR'
    # From Min
    map_range_003.inputs[1].default_value = 0.0
    # From Max
    map_range_003.inputs[2].default_value = 1.0
    # To Min
    map_range_003.inputs[3].default_value = 2.0
    # To Max
    map_range_003.inputs[4].default_value = 0.0

    # Node Combine Color
    combine_color_1 = _rr_white_balance.nodes.new("CompositorNodeCombineColor")
    combine_color_1.name = "Combine Color"
    combine_color_1.hide = True
    combine_color_1.mode = 'RGB'
    combine_color_1.ycc_mode = 'ITUBT709'

    # Node Separate Color
    separate_color = _rr_white_balance.nodes.new("CompositorNodeSeparateColor")
    separate_color.name = "Separate Color"
    separate_color.hide = True
    separate_color.mode = 'RGB'
    separate_color.ycc_mode = 'ITUBT709'

    # Node Group Input
    group_input_3 = _rr_white_balance.nodes.new("NodeGroupInput")
    group_input_3.name = "Group Input"

    # Node White Balance
    white_balance = _rr_white_balance.nodes.new("CompositorNodeColorBalance")
    white_balance.label = "White Balance"
    white_balance.name = "White Balance"
    white_balance.correction_method = 'WHITEPOINT'
    white_balance.input_whitepoint = mathutils.Color((1.0845540761947632, 0.9678249955177307, 1.0696442127227783))
    white_balance.output_whitepoint = mathutils.Color((1.0035851001739502, 0.9986798763275146, 1.0025036334991455))
    # Fac
    white_balance.inputs[0].default_value = 1.0
    # Input Temperature
    white_balance.inputs[14].default_value = 6500.0
    # Input Tint
    white_balance.inputs[15].default_value = -9.0
    # Output Temperature
    white_balance.inputs[16].default_value = 6500.0
    # Output Tint
    white_balance.inputs[17].default_value = 9.0

    # Node Frame
    frame_2 = _rr_white_balance.nodes.new("NodeFrame")
    frame_2.label = "Before Blender 4.3"
    frame_2.name = "Frame"
    frame_2.label_size = 20
    frame_2.shrink = True

    # Node Perceptual
    perceptual = _rr_white_balance.nodes.new("ShaderNodeMix")
    perceptual.label = "Perceptual"
    perceptual.name = "Perceptual"
    perceptual.blend_type = 'MIX'
    perceptual.clamp_factor = False
    perceptual.clamp_result = False
    perceptual.data_type = 'RGBA'
    perceptual.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_2 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_2.name = "Reroute"
    reroute_2.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.003
    reroute_003_1 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_003_1.name = "Reroute.003"
    reroute_003_1.socket_idname = "NodeSocketFloatFactor"
    # Node Mix
    mix_2 = _rr_white_balance.nodes.new("ShaderNodeMix")
    mix_2.name = "Mix"
    mix_2.blend_type = 'MIX'
    mix_2.clamp_factor = True
    mix_2.clamp_result = False
    mix_2.data_type = 'RGBA'
    mix_2.factor_mode = 'UNIFORM'

    # Node Reroute.004
    reroute_004_1 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_004_1.name = "Reroute.004"
    reroute_004_1.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.005
    reroute_005_2 = _rr_white_balance.nodes.new("NodeReroute")
    reroute_005_2.name = "Reroute.005"
    reroute_005_2.socket_idname = "NodeSocketColor"
    # Node Math
    math_3 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_3.name = "Math"
    math_3.hide = True
    math_3.operation = 'ADD'
    math_3.use_clamp = False

    # Node Switch
    switch_2 = _rr_white_balance.nodes.new("CompositorNodeSwitch")
    switch_2.name = "Switch"

    # Node Math.004
    math_004_2 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_004_2.name = "Math.004"
    math_004_2.hide = True
    math_004_2.operation = 'ABSOLUTE'
    math_004_2.use_clamp = False

    # Node Math.005
    math_005_2 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_005_2.name = "Math.005"
    math_005_2.hide = True
    math_005_2.operation = 'ABSOLUTE'
    math_005_2.use_clamp = False

    # Node Math.006
    math_006_2 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_006_2.name = "Math.006"
    math_006_2.hide = True
    math_006_2.operation = 'ABSOLUTE'
    math_006_2.use_clamp = False

    # Node Math.007
    math_007_2 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_007_2.name = "Math.007"
    math_007_2.hide = True
    math_007_2.operation = 'ADD'
    math_007_2.use_clamp = False

    # Node Math.008
    math_008_1 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_008_1.name = "Math.008"
    math_008_1.operation = 'SUBTRACT'
    math_008_1.use_clamp = False
    # Value_001
    math_008_1.inputs[1].default_value = 0.5

    # Node Math.009
    math_009_1 = _rr_white_balance.nodes.new("ShaderNodeMath")
    math_009_1.name = "Math.009"
    math_009_1.operation = 'SUBTRACT'
    math_009_1.use_clamp = False
    # Value_001
    math_009_1.inputs[1].default_value = 0.5

    # Set parents
    math_002_3.parent = frame_2
    reroute_001_1.parent = frame_2
    reroute_002_1.parent = frame_2
    math_001_3.parent = frame_2
    math_003_3.parent = frame_2
    map_range_001_2.parent = frame_2
    map_range_002_1.parent = frame_2
    map_range_003.parent = frame_2
    combine_color_1.parent = frame_2
    separate_color.parent = frame_2
    reroute_2.parent = frame_2
    reroute_003_1.parent = frame_2

    # Set locations
    group_output_3.location = (1874.5135498046875, 141.7371368408203)
    math_002_3.location = (629.0, -224.13201904296875)
    reroute_001_1.location = (769.0, -304.13201904296875)
    reroute_002_1.location = (409.0, -304.13201904296875)
    math_001_3.location = (609.0, -84.13201904296875)
    math_003_3.location = (629.0, -144.13201904296875)
    map_range_001_2.location = (429.0, -44.13201904296875)
    map_range_002_1.location = (429.0, -244.13201904296875)
    map_range_003.location = (429.0, -164.13201904296875)
    combine_color_1.location = (829.0, -144.13201904296875)
    separate_color.location = (29.0, -104.13201904296875)
    group_input_3.location = (-1021.186279296875, 160.0)
    white_balance.location = (300.0, -139.13714599609375)
    frame_2.location = (-369.0, 564.1320190429688)
    perceptual.location = (880.0, 60.0)
    reroute_2.location = (169.0, -184.13201904296875)
    reroute_003_1.location = (169.0, -244.13201904296875)
    mix_2.location = (1240.0, 260.0)
    reroute_004_1.location = (1020.0, 100.0)
    reroute_005_2.location = (1020.0, 120.0)
    math_3.location = (-170.21914672851562, 681.0372314453125)
    switch_2.location = (1465.386962890625, 418.54632568359375)
    math_004_2.location = (-347.3252258300781, 701.0155639648438)
    math_005_2.location = (-348.373779296875, 660.1082763671875)
    math_006_2.location = (-345.22808837890625, 619.2010498046875)
    math_007_2.location = (21.914188385009766, 634.3096313476562)
    math_008_1.location = (-568.6477661132812, 750.2905883789062)
    math_009_1.location = (-572.575439453125, 596.5552368164062)

    # Set dimensions
    group_output_3.width, group_output_3.height = 140.0, 100.0
    math_002_3.width, math_002_3.height = 140.0, 100.0
    reroute_001_1.width, reroute_001_1.height = 13.5, 100.0
    reroute_002_1.width, reroute_002_1.height = 13.5, 100.0
    math_001_3.width, math_001_3.height = 140.0, 100.0
    math_003_3.width, math_003_3.height = 140.0, 100.0
    map_range_001_2.width, map_range_001_2.height = 140.0, 100.0
    map_range_002_1.width, map_range_002_1.height = 140.0, 100.0
    map_range_003.width, map_range_003.height = 140.0, 100.0
    combine_color_1.width, combine_color_1.height = 123.65950012207031, 100.0
    separate_color.width, separate_color.height = 140.0, 100.0
    group_input_3.width, group_input_3.height = 140.0, 100.0
    white_balance.width, white_balance.height = 240.0, 100.0
    frame_2.width, frame_2.height = 981.8994750976562, 338.15203857421875
    perceptual.width, perceptual.height = 140.0, 100.0
    reroute_2.width, reroute_2.height = 13.5, 100.0
    reroute_003_1.width, reroute_003_1.height = 13.5, 100.0
    mix_2.width, mix_2.height = 140.0, 100.0
    reroute_004_1.width, reroute_004_1.height = 13.5, 100.0
    reroute_005_2.width, reroute_005_2.height = 13.5, 100.0
    math_3.width, math_3.height = 140.0, 100.0
    switch_2.width, switch_2.height = 140.0, 100.0
    math_004_2.width, math_004_2.height = 140.0, 100.0
    math_005_2.width, math_005_2.height = 140.0, 100.0
    math_006_2.width, math_006_2.height = 140.0, 100.0
    math_007_2.width, math_007_2.height = 140.0, 100.0
    math_008_1.width, math_008_1.height = 140.0, 100.0
    math_009_1.width, math_009_1.height = 140.0, 100.0

    # Initialize _rr_white_balance links

    # math_002_3.Value -> combine_color_1.Blue
    _rr_white_balance.links.new(math_002_3.outputs[0], combine_color_1.inputs[2])
    # reroute_2.Output -> map_range_002_1.Value
    _rr_white_balance.links.new(reroute_2.outputs[0], map_range_002_1.inputs[0])
    # math_003_3.Value -> combine_color_1.Green
    _rr_white_balance.links.new(math_003_3.outputs[0], combine_color_1.inputs[1])
    # separate_color.Red -> math_001_3.Value
    _rr_white_balance.links.new(separate_color.outputs[0], math_001_3.inputs[0])
    # separate_color.Green -> math_003_3.Value
    _rr_white_balance.links.new(separate_color.outputs[1], math_003_3.inputs[0])
    # reroute_2.Output -> map_range_001_2.Value
    _rr_white_balance.links.new(reroute_2.outputs[0], map_range_001_2.inputs[0])
    # map_range_001_2.Result -> math_001_3.Value
    _rr_white_balance.links.new(map_range_001_2.outputs[0], math_001_3.inputs[1])
    # map_range_002_1.Result -> math_002_3.Value
    _rr_white_balance.links.new(map_range_002_1.outputs[0], math_002_3.inputs[1])
    # map_range_003.Result -> math_003_3.Value
    _rr_white_balance.links.new(map_range_003.outputs[0], math_003_3.inputs[1])
    # math_001_3.Value -> combine_color_1.Red
    _rr_white_balance.links.new(math_001_3.outputs[0], combine_color_1.inputs[0])
    # reroute_002_1.Output -> reroute_001_1.Input
    _rr_white_balance.links.new(reroute_002_1.outputs[0], reroute_001_1.inputs[0])
    # reroute_003_1.Output -> map_range_003.Value
    _rr_white_balance.links.new(reroute_003_1.outputs[0], map_range_003.inputs[0])
    # reroute_001_1.Output -> combine_color_1.Alpha
    _rr_white_balance.links.new(reroute_001_1.outputs[0], combine_color_1.inputs[3])
    # separate_color.Blue -> math_002_3.Value
    _rr_white_balance.links.new(separate_color.outputs[2], math_002_3.inputs[0])
    # separate_color.Alpha -> reroute_002_1.Input
    _rr_white_balance.links.new(separate_color.outputs[3], reroute_002_1.inputs[0])
    # group_input_3.Image -> separate_color.Image
    _rr_white_balance.links.new(group_input_3.outputs[0], separate_color.inputs[0])
    # group_input_3.Image -> white_balance.Image
    _rr_white_balance.links.new(group_input_3.outputs[0], white_balance.inputs[1])
    # combine_color_1.Image -> perceptual.A
    _rr_white_balance.links.new(combine_color_1.outputs[0], perceptual.inputs[6])
    # white_balance.Image -> perceptual.B
    _rr_white_balance.links.new(white_balance.outputs[0], perceptual.inputs[7])
    # group_input_3.Temperature -> reroute_2.Input
    _rr_white_balance.links.new(group_input_3.outputs[2], reroute_2.inputs[0])
    # group_input_3.Tint -> reroute_003_1.Input
    _rr_white_balance.links.new(group_input_3.outputs[3], reroute_003_1.inputs[0])
    # group_input_3.Perceptual -> perceptual.Factor
    _rr_white_balance.links.new(group_input_3.outputs[4], perceptual.inputs[0])
    # perceptual.Result -> mix_2.B
    _rr_white_balance.links.new(perceptual.outputs[2], mix_2.inputs[7])
    # reroute_005_2.Output -> mix_2.A
    _rr_white_balance.links.new(reroute_005_2.outputs[0], mix_2.inputs[6])
    # reroute_004_1.Output -> mix_2.Factor
    _rr_white_balance.links.new(reroute_004_1.outputs[0], mix_2.inputs[0])
    # group_input_3.Factor -> reroute_004_1.Input
    _rr_white_balance.links.new(group_input_3.outputs[1], reroute_004_1.inputs[0])
    # group_input_3.Image -> reroute_005_2.Input
    _rr_white_balance.links.new(group_input_3.outputs[0], reroute_005_2.inputs[0])
    # switch_2.Image -> group_output_3.Image
    _rr_white_balance.links.new(switch_2.outputs[0], group_output_3.inputs[0])
    # group_input_3.Factor -> math_004_2.Value
    _rr_white_balance.links.new(group_input_3.outputs[1], math_004_2.inputs[0])
    # math_009_1.Value -> math_006_2.Value
    _rr_white_balance.links.new(math_009_1.outputs[0], math_006_2.inputs[0])
    # math_004_2.Value -> math_3.Value
    _rr_white_balance.links.new(math_004_2.outputs[0], math_3.inputs[0])
    # math_005_2.Value -> math_3.Value
    _rr_white_balance.links.new(math_005_2.outputs[0], math_3.inputs[1])
    # math_3.Value -> math_007_2.Value
    _rr_white_balance.links.new(math_3.outputs[0], math_007_2.inputs[0])
    # math_006_2.Value -> math_007_2.Value
    _rr_white_balance.links.new(math_006_2.outputs[0], math_007_2.inputs[1])
    # mix_2.Result -> switch_2.On
    _rr_white_balance.links.new(mix_2.outputs[2], switch_2.inputs[2])
    # reroute_005_2.Output -> switch_2.Off
    _rr_white_balance.links.new(reroute_005_2.outputs[0], switch_2.inputs[1])
    # math_007_2.Value -> switch_2.Switch
    _rr_white_balance.links.new(math_007_2.outputs[0], switch_2.inputs[0])
    # group_input_3.Temperature -> math_008_1.Value
    _rr_white_balance.links.new(group_input_3.outputs[2], math_008_1.inputs[0])
    # math_008_1.Value -> math_005_2.Value
    _rr_white_balance.links.new(math_008_1.outputs[0], math_005_2.inputs[0])
    # group_input_3.Tint -> math_009_1.Value
    _rr_white_balance.links.new(group_input_3.outputs[3], math_009_1.inputs[0])

    return _rr_white_balance


_rr_white_balance = _rr_white_balance_node_group()

def _rr_contrast_node_group():
    """Initialize .RR_contrast node group"""
    _rr_contrast = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_contrast")

    _rr_contrast.color_tag = 'NONE'
    _rr_contrast.description = ""
    _rr_contrast.default_group_node_width = 140
    # _rr_contrast interface

    # Socket Image
    image_socket_6 = _rr_contrast.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_6.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_6.attribute_domain = 'POINT'
    image_socket_6.default_input = 'VALUE'
    image_socket_6.structure_type = 'AUTO'

    # Socket Image
    image_socket_7 = _rr_contrast.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_7.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_7.attribute_domain = 'POINT'
    image_socket_7.default_input = 'VALUE'
    image_socket_7.structure_type = 'AUTO'

    # Socket Total
    total_socket = _rr_contrast.interface.new_socket(name="Total", in_out='INPUT', socket_type='NodeSocketFloat')
    total_socket.default_value = 0.0
    total_socket.min_value = -1.0
    total_socket.max_value = 1.0
    total_socket.subtype = 'FACTOR'
    total_socket.attribute_domain = 'POINT'
    total_socket.description = "Adjusts the exposure and gamma at the same time pre-transform to increase contrast, similar to Blender's high or low contrast looks but with more control"
    total_socket.default_input = 'VALUE'
    total_socket.structure_type = 'AUTO'

    # Socket Highlights
    highlights_socket = _rr_contrast.interface.new_socket(name="Highlights", in_out='INPUT', socket_type='NodeSocketFloat')
    highlights_socket.default_value = 0.0
    highlights_socket.min_value = -1.0
    highlights_socket.max_value = 1.0
    highlights_socket.subtype = 'FACTOR'
    highlights_socket.attribute_domain = 'POINT'
    highlights_socket.default_input = 'VALUE'
    highlights_socket.structure_type = 'AUTO'

    # Socket Shadows
    shadows_socket = _rr_contrast.interface.new_socket(name="Shadows", in_out='INPUT', socket_type='NodeSocketFloat')
    shadows_socket.default_value = 0.0
    shadows_socket.min_value = -1.0
    shadows_socket.max_value = 1.0
    shadows_socket.subtype = 'FACTOR'
    shadows_socket.attribute_domain = 'POINT'
    shadows_socket.default_input = 'VALUE'
    shadows_socket.structure_type = 'AUTO'

    # Initialize _rr_contrast nodes

    # Node Group Output
    group_output_4 = _rr_contrast.nodes.new("NodeGroupOutput")
    group_output_4.name = "Group Output"
    group_output_4.is_active_output = True

    # Node Exposure.003
    exposure_003 = _rr_contrast.nodes.new("CompositorNodeExposure")
    exposure_003.name = "Exposure.003"

    # Node Gamma
    gamma = _rr_contrast.nodes.new("CompositorNodeGamma")
    gamma.name = "Gamma"

    # Node Map Range
    map_range_2 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_2.name = "Map Range"
    map_range_2.clamp = False
    map_range_2.data_type = 'FLOAT'
    map_range_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_2.inputs[1].default_value = -1.0
    # From Max
    map_range_2.inputs[2].default_value = 1.0
    # To Min
    map_range_2.inputs[3].default_value = -1.0
    # To Max
    map_range_2.inputs[4].default_value = 1.0

    # Node Map Range.003
    map_range_003_1 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_003_1.name = "Map Range.003"
    map_range_003_1.clamp = False
    map_range_003_1.data_type = 'FLOAT'
    map_range_003_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_1.inputs[1].default_value = -1.0
    # From Max
    map_range_003_1.inputs[2].default_value = 1.0
    # To Min
    map_range_003_1.inputs[3].default_value = 0.5
    # To Max
    map_range_003_1.inputs[4].default_value = 1.5

    # Node Group Input.003
    group_input_003 = _rr_contrast.nodes.new("NodeGroupInput")
    group_input_003.name = "Group Input.003"

    # Node Mix.003
    mix_003 = _rr_contrast.nodes.new("ShaderNodeMix")
    mix_003.name = "Mix.003"
    mix_003.blend_type = 'MIX'
    mix_003.clamp_factor = True
    mix_003.clamp_result = False
    mix_003.data_type = 'RGBA'
    mix_003.factor_mode = 'UNIFORM'

    # Node Exposure.004
    exposure_004 = _rr_contrast.nodes.new("CompositorNodeExposure")
    exposure_004.name = "Exposure.004"

    # Node Gamma.001
    gamma_001 = _rr_contrast.nodes.new("CompositorNodeGamma")
    gamma_001.name = "Gamma.001"

    # Node Map Range.001
    map_range_001_3 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_001_3.name = "Map Range.001"
    map_range_001_3.clamp = False
    map_range_001_3.data_type = 'FLOAT'
    map_range_001_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_3.inputs[1].default_value = -1.0
    # From Max
    map_range_001_3.inputs[2].default_value = 1.0
    # To Min
    map_range_001_3.inputs[3].default_value = -1.0
    # To Max
    map_range_001_3.inputs[4].default_value = 1.0

    # Node Map Range.004
    map_range_004 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_004.name = "Map Range.004"
    map_range_004.clamp = False
    map_range_004.data_type = 'FLOAT'
    map_range_004.interpolation_type = 'LINEAR'
    # From Min
    map_range_004.inputs[1].default_value = -1.0
    # From Max
    map_range_004.inputs[2].default_value = 1.0
    # To Min
    map_range_004.inputs[3].default_value = 0.5
    # To Max
    map_range_004.inputs[4].default_value = 1.5

    # Node Group Input.004
    group_input_004 = _rr_contrast.nodes.new("NodeGroupInput")
    group_input_004.name = "Group Input.004"

    # Node Mix.004
    mix_004 = _rr_contrast.nodes.new("ShaderNodeMix")
    mix_004.name = "Mix.004"
    mix_004.blend_type = 'MIX'
    mix_004.clamp_factor = True
    mix_004.clamp_result = False
    mix_004.data_type = 'RGBA'
    mix_004.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_3 = _rr_contrast.nodes.new("NodeReroute")
    reroute_3.name = "Reroute"
    reroute_3.socket_idname = "NodeSocketColor"
    # Node Frame
    frame_3 = _rr_contrast.nodes.new("NodeFrame")
    frame_3.label = "Highlights"
    frame_3.name = "Frame"
    frame_3.label_size = 20
    frame_3.shrink = True

    # Node Frame.001
    frame_001_1 = _rr_contrast.nodes.new("NodeFrame")
    frame_001_1.label = "Shadows"
    frame_001_1.name = "Frame.001"
    frame_001_1.label_size = 20
    frame_001_1.shrink = True

    # Node Math
    math_4 = _rr_contrast.nodes.new("ShaderNodeMath")
    math_4.name = "Math"
    math_4.operation = 'LOGARITHM'
    math_4.use_clamp = False
    # Value_001
    math_4.inputs[1].default_value = 0.0010000000474974513

    # Node Exposure.005
    exposure_005 = _rr_contrast.nodes.new("CompositorNodeExposure")
    exposure_005.name = "Exposure.005"

    # Node Gamma.002
    gamma_002 = _rr_contrast.nodes.new("CompositorNodeGamma")
    gamma_002.name = "Gamma.002"

    # Node Map Range.002
    map_range_002_2 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_002_2.name = "Map Range.002"
    map_range_002_2.clamp = False
    map_range_002_2.data_type = 'FLOAT'
    map_range_002_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_2.inputs[1].default_value = -1.0
    # From Max
    map_range_002_2.inputs[2].default_value = 1.0
    # To Min
    map_range_002_2.inputs[3].default_value = -1.0
    # To Max
    map_range_002_2.inputs[4].default_value = 1.0

    # Node Map Range.005
    map_range_005 = _rr_contrast.nodes.new("ShaderNodeMapRange")
    map_range_005.name = "Map Range.005"
    map_range_005.clamp = False
    map_range_005.data_type = 'FLOAT'
    map_range_005.interpolation_type = 'LINEAR'
    # From Min
    map_range_005.inputs[1].default_value = -1.0
    # From Max
    map_range_005.inputs[2].default_value = 1.0
    # To Min
    map_range_005.inputs[3].default_value = 0.5
    # To Max
    map_range_005.inputs[4].default_value = 1.5

    # Node Group Input.005
    group_input_005 = _rr_contrast.nodes.new("NodeGroupInput")
    group_input_005.name = "Group Input.005"

    # Node Frame.002
    frame_002 = _rr_contrast.nodes.new("NodeFrame")
    frame_002.label = "All"
    frame_002.name = "Frame.002"
    frame_002.label_size = 20
    frame_002.shrink = True

    # Set parents
    exposure_003.parent = frame_3
    gamma.parent = frame_3
    map_range_2.parent = frame_3
    map_range_003_1.parent = frame_3
    group_input_003.parent = frame_3
    mix_003.parent = frame_3
    exposure_004.parent = frame_001_1
    gamma_001.parent = frame_001_1
    map_range_001_3.parent = frame_001_1
    map_range_004.parent = frame_001_1
    group_input_004.parent = frame_001_1
    mix_004.parent = frame_001_1
    reroute_3.parent = frame_001_1
    math_4.parent = frame_001_1
    exposure_005.parent = frame_002
    gamma_002.parent = frame_002
    map_range_002_2.parent = frame_002
    map_range_005.parent = frame_002
    group_input_005.parent = frame_002

    # Set locations
    group_output_4.location = (1189.9320068359375, 410.9642639160156)
    exposure_003.location = (623.442138671875, -229.70346069335938)
    gamma.location = (924.304443359375, -279.60504150390625)
    map_range_2.location = (396.5458984375, -296.18658447265625)
    map_range_003_1.location = (396.5458984375, -547.246337890625)
    group_input_003.location = (29.406494140625, -158.86871337890625)
    mix_003.location = (1165.873046875, -35.538818359375)
    exposure_004.location = (640.0799560546875, -238.4630126953125)
    gamma_001.location = (940.9420776367188, -288.36456298828125)
    map_range_001_3.location = (413.18341064453125, -304.9461669921875)
    map_range_004.location = (413.18341064453125, -556.005859375)
    group_input_004.location = (28.9844970703125, -258.91217041015625)
    mix_004.location = (1182.5107421875, -44.29833984375)
    reroute_3.location = (542.974609375, -221.64816284179688)
    frame_3.location = (-2826.360107421875, 527.592041015625)
    frame_001_1.location = (-1408.6800537109375, 541.2720336914062)
    math_4.location = (635.5045166015625, -35.94671630859375)
    exposure_005.location = (570.9684448242188, -35.97186279296875)
    gamma_002.location = (871.8307495117188, -85.87344360351562)
    map_range_002_2.location = (342.32940673828125, -160.0255126953125)
    map_range_005.location = (342.32940673828125, -411.08526611328125)
    group_input_005.location = (29.279539108276367, -351.546875)
    frame_002.location = (14.760000228881836, 554.9520263671875)

    # Set dimensions
    group_output_4.width, group_output_4.height = 140.0, 100.0
    exposure_003.width, exposure_003.height = 140.0, 100.0
    gamma.width, gamma.height = 140.0, 100.0
    map_range_2.width, map_range_2.height = 140.0, 100.0
    map_range_003_1.width, map_range_003_1.height = 140.0, 100.0
    group_input_003.width, group_input_003.height = 140.0, 100.0
    mix_003.width, mix_003.height = 140.0, 100.0
    exposure_004.width, exposure_004.height = 140.0, 100.0
    gamma_001.width, gamma_001.height = 140.0, 100.0
    map_range_001_3.width, map_range_001_3.height = 140.0, 100.0
    map_range_004.width, map_range_004.height = 140.0, 100.0
    group_input_004.width, group_input_004.height = 140.0, 100.0
    mix_004.width, mix_004.height = 140.0, 100.0
    reroute_3.width, reroute_3.height = 13.5, 100.0
    frame_3.width, frame_3.height = 1335.199951171875, 805.1520385742188
    frame_001_1.width, frame_001_1.height = 1351.760009765625, 813.7920532226562
    math_4.width, math_4.height = 140.0, 100.0
    exposure_005.width, exposure_005.height = 140.0, 100.0
    gamma_002.width, gamma_002.height = 140.0, 100.0
    map_range_002_2.width, map_range_002_2.height = 140.0, 100.0
    map_range_005.width, map_range_005.height = 140.0, 100.0
    group_input_005.width, group_input_005.height = 140.0, 100.0
    frame_002.width, frame_002.height = 1040.7200927734375, 670.5120239257812

    # Initialize _rr_contrast links

    # exposure_003.Image -> gamma.Image
    _rr_contrast.links.new(exposure_003.outputs[0], gamma.inputs[0])
    # map_range_2.Result -> exposure_003.Exposure
    _rr_contrast.links.new(map_range_2.outputs[0], exposure_003.inputs[1])
    # map_range_003_1.Result -> gamma.Gamma
    _rr_contrast.links.new(map_range_003_1.outputs[0], gamma.inputs[1])
    # group_input_003.Image -> exposure_003.Image
    _rr_contrast.links.new(group_input_003.outputs[0], exposure_003.inputs[0])
    # group_input_003.Highlights -> map_range_2.Value
    _rr_contrast.links.new(group_input_003.outputs[2], map_range_2.inputs[0])
    # group_input_003.Highlights -> map_range_003_1.Value
    _rr_contrast.links.new(group_input_003.outputs[2], map_range_003_1.inputs[0])
    # gamma.Image -> mix_003.B
    _rr_contrast.links.new(gamma.outputs[0], mix_003.inputs[7])
    # group_input_003.Image -> mix_003.A
    _rr_contrast.links.new(group_input_003.outputs[0], mix_003.inputs[6])
    # group_input_003.Image -> mix_003.Factor
    _rr_contrast.links.new(group_input_003.outputs[0], mix_003.inputs[0])
    # exposure_004.Image -> gamma_001.Image
    _rr_contrast.links.new(exposure_004.outputs[0], gamma_001.inputs[0])
    # map_range_001_3.Result -> exposure_004.Exposure
    _rr_contrast.links.new(map_range_001_3.outputs[0], exposure_004.inputs[1])
    # map_range_004.Result -> gamma_001.Gamma
    _rr_contrast.links.new(map_range_004.outputs[0], gamma_001.inputs[1])
    # reroute_3.Output -> exposure_004.Image
    _rr_contrast.links.new(reroute_3.outputs[0], exposure_004.inputs[0])
    # gamma_001.Image -> mix_004.B
    _rr_contrast.links.new(gamma_001.outputs[0], mix_004.inputs[7])
    # reroute_3.Output -> mix_004.A
    _rr_contrast.links.new(reroute_3.outputs[0], mix_004.inputs[6])
    # mix_003.Result -> reroute_3.Input
    _rr_contrast.links.new(mix_003.outputs[2], reroute_3.inputs[0])
    # group_input_004.Shadows -> map_range_001_3.Value
    _rr_contrast.links.new(group_input_004.outputs[3], map_range_001_3.inputs[0])
    # group_input_004.Shadows -> map_range_004.Value
    _rr_contrast.links.new(group_input_004.outputs[3], map_range_004.inputs[0])
    # group_input_004.Image -> math_4.Value
    _rr_contrast.links.new(group_input_004.outputs[0], math_4.inputs[0])
    # math_4.Value -> mix_004.Factor
    _rr_contrast.links.new(math_4.outputs[0], mix_004.inputs[0])
    # exposure_005.Image -> gamma_002.Image
    _rr_contrast.links.new(exposure_005.outputs[0], gamma_002.inputs[0])
    # map_range_002_2.Result -> exposure_005.Exposure
    _rr_contrast.links.new(map_range_002_2.outputs[0], exposure_005.inputs[1])
    # map_range_005.Result -> gamma_002.Gamma
    _rr_contrast.links.new(map_range_005.outputs[0], gamma_002.inputs[1])
    # gamma_002.Image -> group_output_4.Image
    _rr_contrast.links.new(gamma_002.outputs[0], group_output_4.inputs[0])
    # mix_004.Result -> exposure_005.Image
    _rr_contrast.links.new(mix_004.outputs[2], exposure_005.inputs[0])
    # group_input_005.Total -> map_range_002_2.Value
    _rr_contrast.links.new(group_input_005.outputs[1], map_range_002_2.inputs[0])
    # group_input_005.Total -> map_range_005.Value
    _rr_contrast.links.new(group_input_005.outputs[1], map_range_005.inputs[0])

    return _rr_contrast


_rr_contrast = _rr_contrast_node_group()

def _rr_halation_node_group():
    """Initialize .RR_halation node group"""
    _rr_halation = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_halation")

    _rr_halation.color_tag = 'NONE'
    _rr_halation.description = ""
    _rr_halation.default_group_node_width = 140
    # _rr_halation interface

    # Socket Image
    image_socket_8 = _rr_halation.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_8.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_8.attribute_domain = 'POINT'
    image_socket_8.default_input = 'VALUE'
    image_socket_8.structure_type = 'AUTO'

    # Socket Glare
    glare_socket = _rr_halation.interface.new_socket(name="Glare", in_out='OUTPUT', socket_type='NodeSocketColor')
    glare_socket.default_value = (0.0, 0.0, 0.0, 1.0)
    glare_socket.attribute_domain = 'POINT'
    glare_socket.default_input = 'VALUE'
    glare_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_9 = _rr_halation.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_9.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_9.attribute_domain = 'POINT'
    image_socket_9.default_input = 'VALUE'
    image_socket_9.structure_type = 'AUTO'

    # Socket Threshold
    threshold_socket = _rr_halation.interface.new_socket(name="Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    threshold_socket.default_value = 0.0
    threshold_socket.min_value = -3.4028234663852886e+38
    threshold_socket.max_value = 3.4028234663852886e+38
    threshold_socket.subtype = 'NONE'
    threshold_socket.attribute_domain = 'POINT'
    threshold_socket.default_input = 'VALUE'
    threshold_socket.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_1 = _rr_halation.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_1.default_value = 0.0
    strength_socket_1.min_value = -3.4028234663852886e+38
    strength_socket_1.max_value = 3.4028234663852886e+38
    strength_socket_1.subtype = 'FACTOR'
    strength_socket_1.attribute_domain = 'POINT'
    strength_socket_1.default_input = 'VALUE'
    strength_socket_1.structure_type = 'AUTO'

    # Socket Size
    size_socket = _rr_halation.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketFloat')
    size_socket.default_value = 1.0
    size_socket.min_value = 0.0
    size_socket.max_value = 1.0
    size_socket.subtype = 'FACTOR'
    size_socket.attribute_domain = 'POINT'
    size_socket.default_input = 'VALUE'
    size_socket.structure_type = 'AUTO'

    # Initialize _rr_halation nodes

    # Node Group Output
    group_output_5 = _rr_halation.nodes.new("NodeGroupOutput")
    group_output_5.name = "Group Output"
    group_output_5.is_active_output = True

    # Node Group Input
    group_input_4 = _rr_halation.nodes.new("NodeGroupInput")
    group_input_4.name = "Group Input"

    # Node Glare.001
    glare_001 = _rr_halation.nodes.new("CompositorNodeGlare")
    glare_001.name = "Glare.001"
    glare_001.glare_type = 'BLOOM'
    glare_001.quality = 'HIGH'
    # Highlights Smoothness
    glare_001.inputs[2].default_value = 0.8999999761581421
    # Clamp Highlights
    glare_001.inputs[3].default_value = False
    # Maximum Highlights
    glare_001.inputs[4].default_value = 10.0
    # Saturation
    glare_001.inputs[6].default_value = 0.0
    # Tint
    glare_001.inputs[7].default_value = (1.0, 1.0, 0.9967055320739746, 1.0)

    # Node Map Range.001
    map_range_001_4 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_001_4.name = "Map Range.001"
    map_range_001_4.clamp = True
    map_range_001_4.data_type = 'FLOAT'
    map_range_001_4.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_4.inputs[1].default_value = 0.0
    # From Max
    map_range_001_4.inputs[2].default_value = 1.0
    # To Min
    map_range_001_4.inputs[3].default_value = 0.009999999776482582
    # To Max
    map_range_001_4.inputs[4].default_value = 0.07500000298023224

    # Node Mix.001
    mix_001_2 = _rr_halation.nodes.new("ShaderNodeMix")
    mix_001_2.name = "Mix.001"
    mix_001_2.blend_type = 'ADD'
    mix_001_2.clamp_factor = True
    mix_001_2.clamp_result = False
    mix_001_2.data_type = 'RGBA'
    mix_001_2.factor_mode = 'UNIFORM'

    # Node Map Range.003
    map_range_003_2 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_003_2.name = "Map Range.003"
    map_range_003_2.clamp = True
    map_range_003_2.data_type = 'FLOAT'
    map_range_003_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_2.inputs[1].default_value = 0.0
    # From Max
    map_range_003_2.inputs[2].default_value = 1.0
    # To Min
    map_range_003_2.inputs[3].default_value = 0.0
    # To Max
    map_range_003_2.inputs[4].default_value = 10.0

    # Node Vector Math
    vector_math = _rr_halation.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'SUBTRACT'

    # Node Color Ramp
    color_ramp = _rr_halation.nodes.new("CompositorNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    # Initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.0
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (1.0, 0.0, 0.0, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(1.0)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (1.0, 0.5, 0.0, 1.0)


    # Node Mix
    mix_3 = _rr_halation.nodes.new("ShaderNodeMix")
    mix_3.name = "Mix"
    mix_3.blend_type = 'COLOR'
    mix_3.clamp_factor = True
    mix_3.clamp_result = False
    mix_3.data_type = 'RGBA'
    mix_3.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_3.inputs[0].default_value = 1.0

    # Node Map Range.002
    map_range_002_3 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_002_3.name = "Map Range.002"
    map_range_002_3.clamp = True
    map_range_002_3.data_type = 'FLOAT'
    map_range_002_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_3.inputs[1].default_value = 0.0
    # From Max
    map_range_002_3.inputs[2].default_value = 20.0
    # To Min
    map_range_002_3.inputs[3].default_value = 0.0
    # To Max
    map_range_002_3.inputs[4].default_value = 1.0

    # Node Blur
    blur = _rr_halation.nodes.new("CompositorNodeBlur")
    blur.name = "Blur"
    blur.filter_type = 'FAST_GAUSS'
    # Extend Bounds
    blur.inputs[2].default_value = False
    # Separable
    blur.inputs[3].default_value = True

    # Node Separate Color
    separate_color_1 = _rr_halation.nodes.new("CompositorNodeSeparateColor")
    separate_color_1.name = "Separate Color"
    separate_color_1.mode = 'YUV'
    separate_color_1.ycc_mode = 'ITUBT709'

    # Node Map Range.005
    map_range_005_1 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_005_1.name = "Map Range.005"
    map_range_005_1.clamp = True
    map_range_005_1.data_type = 'FLOAT'
    map_range_005_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_1.inputs[1].default_value = 0.0
    # From Max
    map_range_005_1.inputs[2].default_value = 1.0
    # To Min
    map_range_005_1.inputs[3].default_value = 1.0
    # To Max
    map_range_005_1.inputs[4].default_value = 0.0

    # Node Math.007
    math_007_3 = _rr_halation.nodes.new("ShaderNodeMath")
    math_007_3.name = "Math.007"
    math_007_3.hide = True
    math_007_3.operation = 'MULTIPLY'
    math_007_3.use_clamp = False

    # Node Convert Colorspace
    convert_colorspace = _rr_halation.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace.name = "Convert Colorspace"
    convert_colorspace.from_color_space = 'Linear Rec.709'
    convert_colorspace.to_color_space = 'AgX Base sRGB'

    # Node Dilate/Erode
    dilate_erode = _rr_halation.nodes.new("CompositorNodeDilateErode")
    dilate_erode.name = "Dilate/Erode"
    dilate_erode.falloff = 'SMOOTH'
    dilate_erode.mode = 'FEATHER'
    # Size
    dilate_erode.inputs[1].default_value = 3

    # Node Math.008
    math_008_2 = _rr_halation.nodes.new("ShaderNodeMath")
    math_008_2.name = "Math.008"
    math_008_2.hide = True
    math_008_2.operation = 'SUBTRACT'
    math_008_2.use_clamp = False

    # Node Map Range.006
    map_range_006 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_006.name = "Map Range.006"
    map_range_006.clamp = True
    map_range_006.data_type = 'FLOAT'
    map_range_006.interpolation_type = 'LINEAR'
    # Value
    map_range_006.inputs[0].default_value = 1.0
    # From Min
    map_range_006.inputs[1].default_value = 0.0
    # From Max
    map_range_006.inputs[2].default_value = 1.0
    # To Min
    map_range_006.inputs[3].default_value = 5.0

    # Node Float Curve.002
    float_curve_002 = _rr_halation.nodes.new("ShaderNodeFloatCurve")
    float_curve_002.name = "Float Curve.002"
    # Mapping settings
    float_curve_002.mapping.extend = 'EXTRAPOLATED'
    float_curve_002.mapping.tone = 'STANDARD'
    float_curve_002.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_002.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_002.mapping.clip_min_x = 0.0
    float_curve_002.mapping.clip_min_y = 0.0
    float_curve_002.mapping.clip_max_x = 1.0
    float_curve_002.mapping.clip_max_y = 1.0
    float_curve_002.mapping.use_clip = True
    # Curve 0
    float_curve_002_curve_0 = float_curve_002.mapping.curves[0]
    float_curve_002_curve_0_point_0 = float_curve_002_curve_0.points[0]
    float_curve_002_curve_0_point_0.location = (0.0, 0.0)
    float_curve_002_curve_0_point_0.handle_type = 'AUTO'
    float_curve_002_curve_0_point_1 = float_curve_002_curve_0.points[1]
    float_curve_002_curve_0_point_1.location = (0.6499999761581421, 0.25)
    float_curve_002_curve_0_point_1.handle_type = 'AUTO'
    float_curve_002_curve_0_point_2 = float_curve_002_curve_0.points.new(1.0, 1.0)
    float_curve_002_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_002.mapping.update()
    # Factor
    float_curve_002.inputs[0].default_value = 1.0

    # Node Relative To Pixel.001
    relative_to_pixel_001 = _rr_halation.nodes.new("CompositorNodeRelativeToPixel")
    relative_to_pixel_001.name = "Relative To Pixel.001"
    relative_to_pixel_001.data_type = 'FLOAT'
    relative_to_pixel_001.reference_dimension = 'Diagonal'

    # Node Float Curve.003
    float_curve_003 = _rr_halation.nodes.new("ShaderNodeFloatCurve")
    float_curve_003.name = "Float Curve.003"
    # Mapping settings
    float_curve_003.mapping.extend = 'EXTRAPOLATED'
    float_curve_003.mapping.tone = 'STANDARD'
    float_curve_003.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_003.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_003.mapping.clip_min_x = 0.0
    float_curve_003.mapping.clip_min_y = 0.0
    float_curve_003.mapping.clip_max_x = 1.0
    float_curve_003.mapping.clip_max_y = 1.0
    float_curve_003.mapping.use_clip = True
    # Curve 0
    float_curve_003_curve_0 = float_curve_003.mapping.curves[0]
    float_curve_003_curve_0_point_0 = float_curve_003_curve_0.points[0]
    float_curve_003_curve_0_point_0.location = (0.0, 0.0)
    float_curve_003_curve_0_point_0.handle_type = 'AUTO'
    float_curve_003_curve_0_point_1 = float_curve_003_curve_0.points[1]
    float_curve_003_curve_0_point_1.location = (0.25, 0.7500000596046448)
    float_curve_003_curve_0_point_1.handle_type = 'AUTO'
    float_curve_003_curve_0_point_2 = float_curve_003_curve_0.points.new(1.0, 1.0)
    float_curve_003_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_003.mapping.update()
    # Factor
    float_curve_003.inputs[0].default_value = 1.0

    # Node Map Range
    map_range_3 = _rr_halation.nodes.new("ShaderNodeMapRange")
    map_range_3.name = "Map Range"
    map_range_3.clamp = True
    map_range_3.data_type = 'FLOAT'
    map_range_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_3.inputs[1].default_value = 0.0
    # From Max
    map_range_3.inputs[2].default_value = 1.0
    # To Min
    map_range_3.inputs[3].default_value = 0.0
    # To Max
    map_range_3.inputs[4].default_value = 0.05000000074505806

    # Node Float Curve.004
    float_curve_004 = _rr_halation.nodes.new("ShaderNodeFloatCurve")
    float_curve_004.name = "Float Curve.004"
    # Mapping settings
    float_curve_004.mapping.extend = 'EXTRAPOLATED'
    float_curve_004.mapping.tone = 'STANDARD'
    float_curve_004.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_004.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_004.mapping.clip_min_x = 0.0
    float_curve_004.mapping.clip_min_y = 0.0
    float_curve_004.mapping.clip_max_x = 1.0
    float_curve_004.mapping.clip_max_y = 1.0
    float_curve_004.mapping.use_clip = True
    # Curve 0
    float_curve_004_curve_0 = float_curve_004.mapping.curves[0]
    float_curve_004_curve_0_point_0 = float_curve_004_curve_0.points[0]
    float_curve_004_curve_0_point_0.location = (0.0, 0.0)
    float_curve_004_curve_0_point_0.handle_type = 'AUTO'
    float_curve_004_curve_0_point_1 = float_curve_004_curve_0.points[1]
    float_curve_004_curve_0_point_1.location = (0.6499999761581421, 0.25)
    float_curve_004_curve_0_point_1.handle_type = 'AUTO'
    float_curve_004_curve_0_point_2 = float_curve_004_curve_0.points.new(1.0, 1.0)
    float_curve_004_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_004.mapping.update()
    # Factor
    float_curve_004.inputs[0].default_value = 1.0

    # Node Group Input.001
    group_input_001_1 = _rr_halation.nodes.new("NodeGroupInput")
    group_input_001_1.name = "Group Input.001"
    group_input_001_1.outputs[1].hide = True
    group_input_001_1.outputs[2].hide = True
    group_input_001_1.outputs[3].hide = True
    group_input_001_1.outputs[4].hide = True

    # Node Frame
    frame_4 = _rr_halation.nodes.new("NodeFrame")
    frame_4.label = "Mask"
    frame_4.name = "Frame"
    frame_4.label_size = 20
    frame_4.shrink = True

    # Set parents
    blur.parent = frame_4
    separate_color_1.parent = frame_4
    map_range_005_1.parent = frame_4
    math_007_3.parent = frame_4
    convert_colorspace.parent = frame_4
    dilate_erode.parent = frame_4
    math_008_2.parent = frame_4
    map_range_006.parent = frame_4
    relative_to_pixel_001.parent = frame_4
    float_curve_003.parent = frame_4
    map_range_3.parent = frame_4

    # Set locations
    group_output_5.location = (1823.085205078125, 322.71490478515625)
    group_input_4.location = (-2094.37841796875, -35.065372467041016)
    glare_001.location = (134.02569580078125, 73.7452392578125)
    map_range_001_4.location = (-124.89546966552734, -449.0188293457031)
    mix_001_2.location = (1313.1995849609375, 324.7460632324219)
    map_range_003_2.location = (-122.36175537109375, -169.96702575683594)
    vector_math.location = (1594.227783203125, 474.8631591796875)
    color_ramp.location = (693.1517333984375, -129.1175537109375)
    mix_3.location = (1040.21240234375, 107.08480072021484)
    map_range_002_3.location = (469.2263488769531, -111.58677673339844)
    blur.location = (943.1319580078125, -364.201171875)
    separate_color_1.location = (248.21240234375, -131.8060302734375)
    map_range_005_1.location = (1271.73681640625, -35.8187255859375)
    math_007_3.location = (1530.744384765625, -211.6317138671875)
    convert_colorspace.location = (58.0419921875, -152.30908203125)
    dilate_erode.location = (1740.9364013671875, -114.874755859375)
    math_008_2.location = (1274.6531982421875, -318.905029296875)
    map_range_006.location = (735.8295288085938, -473.2266540527344)
    float_curve_002.location = (-463.0643310546875, -185.07119750976562)
    relative_to_pixel_001.location = (529.3966064453125, -545.0770263671875)
    float_curve_003.location = (30.0579833984375, -376.237548828125)
    map_range_3.location = (319.9769287109375, -388.9493408203125)
    float_curve_004.location = (-460.0843505859375, -506.9332580566406)
    group_input_001_1.location = (1006.3281860351562, 399.3986511230469)
    frame_4.location = (-1621.5, 917.5)

    # Set dimensions
    group_output_5.width, group_output_5.height = 140.0, 100.0
    group_input_4.width, group_input_4.height = 140.0, 100.0
    glare_001.width, glare_001.height = 219.2844696044922, 100.0
    map_range_001_4.width, map_range_001_4.height = 140.0, 100.0
    mix_001_2.width, mix_001_2.height = 140.0, 100.0
    map_range_003_2.width, map_range_003_2.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    mix_3.width, mix_3.height = 140.0, 100.0
    map_range_002_3.width, map_range_002_3.height = 140.0, 100.0
    blur.width, blur.height = 140.0, 100.0
    separate_color_1.width, separate_color_1.height = 140.0, 100.0
    map_range_005_1.width, map_range_005_1.height = 140.0, 100.0
    math_007_3.width, math_007_3.height = 113.86624908447266, 100.0
    convert_colorspace.width, convert_colorspace.height = 150.0, 100.0
    dilate_erode.width, dilate_erode.height = 140.0, 100.0
    math_008_2.width, math_008_2.height = 140.0, 100.0
    map_range_006.width, map_range_006.height = 140.0, 100.0
    float_curve_002.width, float_curve_002.height = 240.0, 100.0
    relative_to_pixel_001.width, relative_to_pixel_001.height = 140.0, 100.0
    float_curve_003.width, float_curve_003.height = 240.0, 100.0
    map_range_3.width, map_range_3.height = 140.0, 100.0
    float_curve_004.width, float_curve_004.height = 240.0, 100.0
    group_input_001_1.width, group_input_001_1.height = 140.0, 100.0
    frame_4.width, frame_4.height = 1911.0, 745.0

    # Initialize _rr_halation links

    # map_range_002_3.Result -> color_ramp.Fac
    _rr_halation.links.new(map_range_002_3.outputs[0], color_ramp.inputs[0])
    # glare_001.Glare -> map_range_002_3.Value
    _rr_halation.links.new(glare_001.outputs[1], map_range_002_3.inputs[0])
    # group_input_4.Strength -> float_curve_002.Value
    _rr_halation.links.new(group_input_4.outputs[2], float_curve_002.inputs[1])
    # glare_001.Glare -> mix_3.A
    _rr_halation.links.new(glare_001.outputs[1], mix_3.inputs[6])
    # group_input_4.Image -> relative_to_pixel_001.Image
    _rr_halation.links.new(group_input_4.outputs[0], relative_to_pixel_001.inputs[2])
    # map_range_005_1.Result -> math_007_3.Value
    _rr_halation.links.new(map_range_005_1.outputs[0], math_007_3.inputs[0])
    # float_curve_002.Value -> map_range_003_2.Value
    _rr_halation.links.new(float_curve_002.outputs[0], map_range_003_2.inputs[0])
    # mix_001_2.Result -> vector_math.Vector
    _rr_halation.links.new(mix_001_2.outputs[2], vector_math.inputs[0])
    # separate_color_1.Red -> math_008_2.Value
    _rr_halation.links.new(separate_color_1.outputs[0], math_008_2.inputs[1])
    # relative_to_pixel_001.Value -> map_range_006.To Max
    _rr_halation.links.new(relative_to_pixel_001.outputs[0], map_range_006.inputs[4])
    # mix_3.Result -> mix_001_2.B
    _rr_halation.links.new(mix_3.outputs[2], mix_001_2.inputs[7])
    # blur.Image -> math_008_2.Value
    _rr_halation.links.new(blur.outputs[0], math_008_2.inputs[0])
    # convert_colorspace.Image -> separate_color_1.Image
    _rr_halation.links.new(convert_colorspace.outputs[0], separate_color_1.inputs[0])
    # map_range_003_2.Result -> glare_001.Strength
    _rr_halation.links.new(map_range_003_2.outputs[0], glare_001.inputs[5])
    # group_input_4.Image -> glare_001.Image
    _rr_halation.links.new(group_input_4.outputs[0], glare_001.inputs[0])
    # group_input_4.Image -> convert_colorspace.Image
    _rr_halation.links.new(group_input_4.outputs[0], convert_colorspace.inputs[0])
    # math_008_2.Value -> math_007_3.Value
    _rr_halation.links.new(math_008_2.outputs[0], math_007_3.inputs[1])
    # separate_color_1.Red -> map_range_005_1.Value
    _rr_halation.links.new(separate_color_1.outputs[0], map_range_005_1.inputs[0])
    # group_input_4.Threshold -> glare_001.Threshold
    _rr_halation.links.new(group_input_4.outputs[1], glare_001.inputs[1])
    # separate_color_1.Red -> blur.Image
    _rr_halation.links.new(separate_color_1.outputs[0], blur.inputs[0])
    # mix_001_2.Result -> group_output_5.Image
    _rr_halation.links.new(mix_001_2.outputs[2], group_output_5.inputs[0])
    # vector_math.Vector -> group_output_5.Glare
    _rr_halation.links.new(vector_math.outputs[0], group_output_5.inputs[1])
    # math_007_3.Value -> dilate_erode.Mask
    _rr_halation.links.new(math_007_3.outputs[0], dilate_erode.inputs[0])
    # group_input_4.Size -> float_curve_003.Value
    _rr_halation.links.new(group_input_4.outputs[3], float_curve_003.inputs[1])
    # float_curve_003.Value -> map_range_3.Value
    _rr_halation.links.new(float_curve_003.outputs[0], map_range_3.inputs[0])
    # map_range_3.Result -> relative_to_pixel_001.Value
    _rr_halation.links.new(map_range_3.outputs[0], relative_to_pixel_001.inputs[1])
    # dilate_erode.Mask -> mix_001_2.Factor
    _rr_halation.links.new(dilate_erode.outputs[0], mix_001_2.inputs[0])
    # map_range_006.Result -> blur.Size
    _rr_halation.links.new(map_range_006.outputs[0], blur.inputs[1])
    # map_range_001_4.Result -> glare_001.Size
    _rr_halation.links.new(map_range_001_4.outputs[0], glare_001.inputs[8])
    # group_input_4.Size -> float_curve_004.Value
    _rr_halation.links.new(group_input_4.outputs[3], float_curve_004.inputs[1])
    # float_curve_004.Value -> map_range_001_4.Value
    _rr_halation.links.new(float_curve_004.outputs[0], map_range_001_4.inputs[0])
    # color_ramp.Image -> mix_3.B
    _rr_halation.links.new(color_ramp.outputs[0], mix_3.inputs[7])
    # group_input_001_1.Image -> mix_001_2.A
    _rr_halation.links.new(group_input_001_1.outputs[0], mix_001_2.inputs[6])
    # group_input_001_1.Image -> vector_math.Vector
    _rr_halation.links.new(group_input_001_1.outputs[0], vector_math.inputs[1])

    return _rr_halation


_rr_halation = _rr_halation_node_group()

def _rr_glare_node_group():
    """Initialize .RR_glare node group"""
    _rr_glare = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_glare")

    _rr_glare.color_tag = 'NONE'
    _rr_glare.description = ""
    _rr_glare.default_group_node_width = 140
    # _rr_glare interface

    # Socket Image
    image_socket_10 = _rr_glare.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_10.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_10.attribute_domain = 'POINT'
    image_socket_10.default_input = 'VALUE'
    image_socket_10.structure_type = 'AUTO'

    # Socket Glare
    glare_socket_1 = _rr_glare.interface.new_socket(name="Glare", in_out='OUTPUT', socket_type='NodeSocketColor')
    glare_socket_1.default_value = (0.0, 0.0, 0.0, 1.0)
    glare_socket_1.attribute_domain = 'POINT'
    glare_socket_1.default_input = 'VALUE'
    glare_socket_1.structure_type = 'AUTO'

    # Socket Image
    image_socket_11 = _rr_glare.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_11.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_11.attribute_domain = 'POINT'
    image_socket_11.default_input = 'VALUE'
    image_socket_11.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_2 = _rr_glare.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_2.default_value = 0.0
    factor_socket_2.min_value = 0.0
    factor_socket_2.max_value = 1.0
    factor_socket_2.subtype = 'FACTOR'
    factor_socket_2.attribute_domain = 'POINT'
    factor_socket_2.description = "Adjusts how much total glare is applied, pre-transform"
    factor_socket_2.default_input = 'VALUE'
    factor_socket_2.structure_type = 'AUTO'

    # Socket Threshold
    threshold_socket_1 = _rr_glare.interface.new_socket(name="Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    threshold_socket_1.default_value = 1.0
    threshold_socket_1.min_value = 0.0
    threshold_socket_1.max_value = 100.0
    threshold_socket_1.subtype = 'NONE'
    threshold_socket_1.attribute_domain = 'POINT'
    threshold_socket_1.description = "Adjusts how bright a pixel needs to be in order to cause glare"
    threshold_socket_1.default_input = 'VALUE'
    threshold_socket_1.structure_type = 'AUTO'

    # Socket Smoothness
    smoothness_socket = _rr_glare.interface.new_socket(name="Smoothness", in_out='INPUT', socket_type='NodeSocketFloat')
    smoothness_socket.default_value = 1.0
    smoothness_socket.min_value = 0.0
    smoothness_socket.max_value = 1.0
    smoothness_socket.subtype = 'FACTOR'
    smoothness_socket.attribute_domain = 'POINT'
    smoothness_socket.default_input = 'VALUE'
    smoothness_socket.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_2 = _rr_glare.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_2.default_value = 1.0
    saturation_socket_2.min_value = 0.0
    saturation_socket_2.max_value = 1.0
    saturation_socket_2.subtype = 'FACTOR'
    saturation_socket_2.attribute_domain = 'POINT'
    saturation_socket_2.description = "Adjusts how much color the bloom picks up from the scene before the tint"
    saturation_socket_2.default_input = 'VALUE'
    saturation_socket_2.structure_type = 'AUTO'

    # Socket Tint
    tint_socket_1 = _rr_glare.interface.new_socket(name="Tint", in_out='INPUT', socket_type='NodeSocketColor')
    tint_socket_1.default_value = (1.0, 1.0, 1.0, 1.0)
    tint_socket_1.attribute_domain = 'POINT'
    tint_socket_1.description = "Color to multiply the bloom with. To fully use this color, set the Saturation above to 0"
    tint_socket_1.default_input = 'VALUE'
    tint_socket_1.structure_type = 'AUTO'

    # Panel Bloom
    bloom_panel = _rr_glare.interface.new_panel("Bloom")
    # Socket Bloom Strength
    bloom_strength_socket = _rr_glare.interface.new_socket(name="Bloom Strength", in_out='INPUT', socket_type='NodeSocketFloat', parent = bloom_panel)
    bloom_strength_socket.default_value = 1.0
    bloom_strength_socket.min_value = 0.0
    bloom_strength_socket.max_value = 1.0
    bloom_strength_socket.subtype = 'FACTOR'
    bloom_strength_socket.attribute_domain = 'POINT'
    bloom_strength_socket.description = "Adjusts how much glow is applied around bright areas"
    bloom_strength_socket.default_input = 'VALUE'
    bloom_strength_socket.structure_type = 'AUTO'

    # Socket Size
    size_socket_1 = _rr_glare.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketFloat', parent = bloom_panel)
    size_socket_1.default_value = 9.0
    size_socket_1.min_value = 1.0
    size_socket_1.max_value = 9.0
    size_socket_1.subtype = 'NONE'
    size_socket_1.attribute_domain = 'POINT'
    size_socket_1.description = "Adjusts the size of the glow around bright areas"
    size_socket_1.default_input = 'VALUE'
    size_socket_1.structure_type = 'AUTO'


    # Panel Streaks
    streaks_panel = _rr_glare.interface.new_panel("Streaks")
    # Socket Streaks Strength
    streaks_strength_socket = _rr_glare.interface.new_socket(name="Streaks Strength", in_out='INPUT', socket_type='NodeSocketFloat', parent = streaks_panel)
    streaks_strength_socket.default_value = 0.5
    streaks_strength_socket.min_value = 0.0
    streaks_strength_socket.max_value = 1.0
    streaks_strength_socket.subtype = 'FACTOR'
    streaks_strength_socket.attribute_domain = 'POINT'
    streaks_strength_socket.description = "Adjusts how much the streaks are mixed in with the origional image"
    streaks_strength_socket.default_input = 'VALUE'
    streaks_strength_socket.structure_type = 'AUTO'

    # Socket Length
    length_socket = _rr_glare.interface.new_socket(name="Length", in_out='INPUT', socket_type='NodeSocketFloat', parent = streaks_panel)
    length_socket.default_value = 0.25
    length_socket.min_value = 0.0
    length_socket.max_value = 1.0
    length_socket.subtype = 'FACTOR'
    length_socket.attribute_domain = 'POINT'
    length_socket.description = "Adjusts the size of the streaks"
    length_socket.default_input = 'VALUE'
    length_socket.structure_type = 'AUTO'

    # Socket Count
    count_socket = _rr_glare.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt', parent = streaks_panel)
    count_socket.default_value = 16
    count_socket.min_value = 2
    count_socket.max_value = 16
    count_socket.subtype = 'NONE'
    count_socket.attribute_domain = 'POINT'
    count_socket.description = "Adjusts how many streaks are created around bright areas"
    count_socket.default_input = 'VALUE'
    count_socket.structure_type = 'AUTO'

    # Socket Angle
    angle_socket = _rr_glare.interface.new_socket(name="Angle", in_out='INPUT', socket_type='NodeSocketFloat', parent = streaks_panel)
    angle_socket.default_value = 0.0
    angle_socket.min_value = -3.4028234663852886e+38
    angle_socket.max_value = 3.4028234663852886e+38
    angle_socket.subtype = 'ANGLE'
    angle_socket.attribute_domain = 'POINT'
    angle_socket.description = "Adjusts the rotation of the streaks"
    angle_socket.default_input = 'VALUE'
    angle_socket.structure_type = 'AUTO'


    # Panel Ghosting
    ghosting_panel = _rr_glare.interface.new_panel("Ghosting")
    # Socket Ghosting Strength
    ghosting_strength_socket = _rr_glare.interface.new_socket(name="Ghosting Strength", in_out='INPUT', socket_type='NodeSocketFloat', parent = ghosting_panel)
    ghosting_strength_socket.default_value = 0.0
    ghosting_strength_socket.min_value = 0.0
    ghosting_strength_socket.max_value = 1.0
    ghosting_strength_socket.subtype = 'FACTOR'
    ghosting_strength_socket.attribute_domain = 'POINT'
    ghosting_strength_socket.description = "Adjusts how much camera artifacting is applied on top of the image"
    ghosting_strength_socket.default_input = 'VALUE'
    ghosting_strength_socket.structure_type = 'AUTO'

    # Socket Color Modulation
    color_modulation_socket = _rr_glare.interface.new_socket(name="Color Modulation", in_out='INPUT', socket_type='NodeSocketFloat', parent = ghosting_panel)
    color_modulation_socket.default_value = 1.0
    color_modulation_socket.min_value = 0.0
    color_modulation_socket.max_value = 1.0
    color_modulation_socket.subtype = 'FACTOR'
    color_modulation_socket.attribute_domain = 'POINT'
    color_modulation_socket.default_input = 'VALUE'
    color_modulation_socket.structure_type = 'AUTO'

    # Socket Steps
    steps_socket = _rr_glare.interface.new_socket(name="Steps", in_out='INPUT', socket_type='NodeSocketInt', parent = ghosting_panel)
    steps_socket.default_value = 5
    steps_socket.min_value = 2
    steps_socket.max_value = 5
    steps_socket.subtype = 'NONE'
    steps_socket.attribute_domain = 'POINT'
    steps_socket.default_input = 'VALUE'
    steps_socket.structure_type = 'AUTO'


    # Panel Halation
    halation_panel = _rr_glare.interface.new_panel("Halation")
    # Socket Halation Strength
    halation_strength_socket = _rr_glare.interface.new_socket(name="Halation Strength", in_out='INPUT', socket_type='NodeSocketFloat', parent = halation_panel)
    halation_strength_socket.default_value = 0.0
    halation_strength_socket.min_value = 0.0
    halation_strength_socket.max_value = 1.0
    halation_strength_socket.subtype = 'FACTOR'
    halation_strength_socket.attribute_domain = 'POINT'
    halation_strength_socket.description = "Adjusts how much camera artifacting is applied on top of the image"
    halation_strength_socket.default_input = 'VALUE'
    halation_strength_socket.structure_type = 'AUTO'

    # Socket Halation Size
    halation_size_socket = _rr_glare.interface.new_socket(name="Halation Size", in_out='INPUT', socket_type='NodeSocketFloat', parent = halation_panel)
    halation_size_socket.default_value = 1.0
    halation_size_socket.min_value = 0.0
    halation_size_socket.max_value = 1.0
    halation_size_socket.subtype = 'FACTOR'
    halation_size_socket.attribute_domain = 'POINT'
    halation_size_socket.default_input = 'VALUE'
    halation_size_socket.structure_type = 'AUTO'


    # Initialize _rr_glare nodes

    # Node Mix.005
    mix_005 = _rr_glare.nodes.new("ShaderNodeMix")
    mix_005.name = "Mix.005"
    mix_005.hide = True
    mix_005.blend_type = 'DIFFERENCE'
    mix_005.clamp_factor = False
    mix_005.clamp_result = False
    mix_005.data_type = 'RGBA'
    mix_005.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_005.inputs[0].default_value = 1.0

    # Node Separate Color.003
    separate_color_003_1 = _rr_glare.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_1.name = "Separate Color.003"
    separate_color_003_1.hide = True
    separate_color_003_1.mode = 'RGB'
    separate_color_003_1.ycc_mode = 'ITUBT709'
    separate_color_003_1.outputs[0].hide = True
    separate_color_003_1.outputs[1].hide = True
    separate_color_003_1.outputs[2].hide = True

    # Node Reroute.005
    reroute_005_3 = _rr_glare.nodes.new("NodeReroute")
    reroute_005_3.name = "Reroute.005"
    reroute_005_3.socket_idname = "NodeSocketColor"
    # Node Streaks
    streaks = _rr_glare.nodes.new("CompositorNodeGlare")
    streaks.label = "Streaks"
    streaks.name = "Streaks"
    streaks.glare_type = 'STREAKS'
    streaks.quality = 'HIGH'
    # Clamp Highlights
    streaks.inputs[3].default_value = False
    # Maximum Highlights
    streaks.inputs[4].default_value = 0.0
    # Iterations
    streaks.inputs[11].default_value = 5
    # Color Modulation
    streaks.inputs[13].default_value = 0.0

    # Node Glare Alpha
    glare_alpha = _rr_glare.nodes.new("CompositorNodeSetAlpha")
    glare_alpha.label = "Glare Alpha"
    glare_alpha.name = "Glare Alpha"
    glare_alpha.mode = 'REPLACE_ALPHA'

    # Node Group Input
    group_input_5 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_5.name = "Group Input"
    group_input_5.outputs[1].hide = True
    group_input_5.outputs[6].hide = True
    group_input_5.outputs[7].hide = True
    group_input_5.outputs[12].hide = True
    group_input_5.outputs[13].hide = True
    group_input_5.outputs[14].hide = True
    group_input_5.outputs[15].hide = True
    group_input_5.outputs[16].hide = True
    group_input_5.outputs[17].hide = True

    # Node Mix.006
    mix_006 = _rr_glare.nodes.new("ShaderNodeMix")
    mix_006.name = "Mix.006"
    mix_006.hide = True
    mix_006.blend_type = 'ADD'
    mix_006.clamp_factor = False
    mix_006.clamp_result = True
    mix_006.data_type = 'RGBA'
    mix_006.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_006.inputs[0].default_value = 1.0

    # Node Group Output
    group_output_6 = _rr_glare.nodes.new("NodeGroupOutput")
    group_output_6.name = "Group Output"
    group_output_6.is_active_output = True

    # Node Ghosting
    ghosting = _rr_glare.nodes.new("CompositorNodeGlare")
    ghosting.label = "Ghosting"
    ghosting.name = "Ghosting"
    ghosting.glare_type = 'GHOSTS'
    ghosting.quality = 'HIGH'
    # Clamp Highlights
    ghosting.inputs[3].default_value = False
    # Maximum Highlights
    ghosting.inputs[4].default_value = 0.0

    # Node Glare
    glare = _rr_glare.nodes.new("CompositorNodeGlare")
    glare.name = "Glare"
    glare.glare_type = 'BLOOM'
    glare.quality = 'HIGH'
    # Clamp Highlights
    glare.inputs[3].default_value = False
    # Maximum Highlights
    glare.inputs[4].default_value = 0.0

    # Node Add Bloom
    add_bloom = _rr_glare.nodes.new("ShaderNodeMix")
    add_bloom.name = "Add Bloom"
    add_bloom.blend_type = 'ADD'
    add_bloom.clamp_factor = False
    add_bloom.clamp_result = False
    add_bloom.data_type = 'RGBA'
    add_bloom.factor_mode = 'UNIFORM'
    # Factor_Float
    add_bloom.inputs[0].default_value = 1.0

    # Node Add Streaks
    add_streaks = _rr_glare.nodes.new("ShaderNodeMix")
    add_streaks.name = "Add Streaks"
    add_streaks.blend_type = 'ADD'
    add_streaks.clamp_factor = False
    add_streaks.clamp_result = False
    add_streaks.data_type = 'RGBA'
    add_streaks.factor_mode = 'UNIFORM'
    # Factor_Float
    add_streaks.inputs[0].default_value = 1.0

    # Node Add Ghosting
    add_ghosting = _rr_glare.nodes.new("ShaderNodeMix")
    add_ghosting.name = "Add Ghosting"
    add_ghosting.mute = True
    add_ghosting.blend_type = 'ADD'
    add_ghosting.clamp_factor = False
    add_ghosting.clamp_result = False
    add_ghosting.data_type = 'RGBA'
    add_ghosting.factor_mode = 'UNIFORM'
    # Factor_Float
    add_ghosting.inputs[0].default_value = 1.0

    # Node RGB
    rgb = _rr_glare.nodes.new("CompositorNodeRGB")
    rgb.name = "RGB"

    rgb.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
    # Node Map Range
    map_range_4 = _rr_glare.nodes.new("ShaderNodeMapRange")
    map_range_4.name = "Map Range"
    map_range_4.clamp = True
    map_range_4.data_type = 'FLOAT'
    map_range_4.interpolation_type = 'LINEAR'
    # From Min
    map_range_4.inputs[1].default_value = 0.0
    # From Max
    map_range_4.inputs[2].default_value = 1.0
    # To Min
    map_range_4.inputs[3].default_value = 0.8999999761581421
    # To Max
    map_range_4.inputs[4].default_value = 1.0

    # Node Math
    math_5 = _rr_glare.nodes.new("ShaderNodeMath")
    math_5.name = "Math"
    math_5.operation = 'MULTIPLY'
    math_5.use_clamp = False
    # Value_001
    math_5.inputs[1].default_value = 0.5

    # Node Float Curve
    float_curve = _rr_glare.nodes.new("ShaderNodeFloatCurve")
    float_curve.name = "Float Curve"
    # Mapping settings
    float_curve.mapping.extend = 'EXTRAPOLATED'
    float_curve.mapping.tone = 'STANDARD'
    float_curve.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve.mapping.clip_min_x = 0.0
    float_curve.mapping.clip_min_y = 0.0
    float_curve.mapping.clip_max_x = 1.0
    float_curve.mapping.clip_max_y = 1.0
    float_curve.mapping.use_clip = True
    # Curve 0
    float_curve_curve_0 = float_curve.mapping.curves[0]
    float_curve_curve_0_point_0 = float_curve_curve_0.points[0]
    float_curve_curve_0_point_0.location = (0.0, 0.0)
    float_curve_curve_0_point_0.handle_type = 'AUTO'
    float_curve_curve_0_point_1 = float_curve_curve_0.points[1]
    float_curve_curve_0_point_1.location = (0.75, 0.25)
    float_curve_curve_0_point_1.handle_type = 'AUTO'
    float_curve_curve_0_point_2 = float_curve_curve_0.points.new(1.0, 1.0)
    float_curve_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve.mapping.update()
    # Factor
    float_curve.inputs[0].default_value = 1.0

    # Node Group Input.001
    group_input_001_2 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_001_2.name = "Group Input.001"
    group_input_001_2.outputs[2].hide = True
    group_input_001_2.outputs[3].hide = True
    group_input_001_2.outputs[4].hide = True
    group_input_001_2.outputs[5].hide = True
    group_input_001_2.outputs[6].hide = True
    group_input_001_2.outputs[7].hide = True
    group_input_001_2.outputs[8].hide = True
    group_input_001_2.outputs[9].hide = True
    group_input_001_2.outputs[10].hide = True
    group_input_001_2.outputs[11].hide = True
    group_input_001_2.outputs[12].hide = True
    group_input_001_2.outputs[13].hide = True
    group_input_001_2.outputs[14].hide = True
    group_input_001_2.outputs[15].hide = True
    group_input_001_2.outputs[16].hide = True
    group_input_001_2.outputs[17].hide = True

    # Node Group Input.002
    group_input_002 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_002.name = "Group Input.002"
    group_input_002.outputs[2].hide = True
    group_input_002.outputs[3].hide = True
    group_input_002.outputs[4].hide = True
    group_input_002.outputs[5].hide = True
    group_input_002.outputs[7].hide = True
    group_input_002.outputs[9].hide = True
    group_input_002.outputs[10].hide = True
    group_input_002.outputs[11].hide = True
    group_input_002.outputs[13].hide = True
    group_input_002.outputs[14].hide = True
    group_input_002.outputs[15].hide = True
    group_input_002.outputs[16].hide = True
    group_input_002.outputs[17].hide = True

    # Node Frame
    frame_5 = _rr_glare.nodes.new("NodeFrame")
    frame_5.label = "Streaks"
    frame_5.name = "Frame"
    frame_5.label_size = 20
    frame_5.shrink = True

    # Node Group Input.003
    group_input_003_1 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_003_1.name = "Group Input.003"
    group_input_003_1.outputs[1].hide = True
    group_input_003_1.outputs[8].hide = True
    group_input_003_1.outputs[9].hide = True
    group_input_003_1.outputs[10].hide = True
    group_input_003_1.outputs[11].hide = True
    group_input_003_1.outputs[12].hide = True
    group_input_003_1.outputs[13].hide = True
    group_input_003_1.outputs[14].hide = True
    group_input_003_1.outputs[15].hide = True
    group_input_003_1.outputs[16].hide = True
    group_input_003_1.outputs[17].hide = True

    # Node Frame.001
    frame_001_2 = _rr_glare.nodes.new("NodeFrame")
    frame_001_2.label = "Bloom"
    frame_001_2.name = "Frame.001"
    frame_001_2.label_size = 20
    frame_001_2.shrink = True

    # Node Group Input.004
    group_input_004_1 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_004_1.name = "Group Input.004"
    group_input_004_1.outputs[1].hide = True
    group_input_004_1.outputs[6].hide = True
    group_input_004_1.outputs[7].hide = True
    group_input_004_1.outputs[8].hide = True
    group_input_004_1.outputs[9].hide = True
    group_input_004_1.outputs[10].hide = True
    group_input_004_1.outputs[11].hide = True
    group_input_004_1.outputs[15].hide = True
    group_input_004_1.outputs[16].hide = True
    group_input_004_1.outputs[17].hide = True

    # Node Frame.002
    frame_002_1 = _rr_glare.nodes.new("NodeFrame")
    frame_002_1.label = "Ghosting"
    frame_002_1.name = "Frame.002"
    frame_002_1.label_size = 20
    frame_002_1.shrink = True

    # Node Switch
    switch_3 = _rr_glare.nodes.new("CompositorNodeSwitch")
    switch_3.name = "Switch"

    # Node Math.004
    math_004_3 = _rr_glare.nodes.new("ShaderNodeMath")
    math_004_3.name = "Math.004"
    math_004_3.hide = True
    math_004_3.operation = 'ADD'
    math_004_3.use_clamp = False

    # Node Math.005
    math_005_3 = _rr_glare.nodes.new("ShaderNodeMath")
    math_005_3.name = "Math.005"
    math_005_3.hide = True
    math_005_3.operation = 'ADD'
    math_005_3.use_clamp = False

    # Node Math.006
    math_006_3 = _rr_glare.nodes.new("ShaderNodeMath")
    math_006_3.name = "Math.006"
    math_006_3.hide = True
    math_006_3.operation = 'ADD'
    math_006_3.use_clamp = False

    # Node Reroute.002
    reroute_002_2 = _rr_glare.nodes.new("NodeReroute")
    reroute_002_2.name = "Reroute.002"
    reroute_002_2.socket_idname = "NodeSocketColor"
    # Node Frame.003
    frame_003 = _rr_glare.nodes.new("NodeFrame")
    frame_003.label = "Alpha"
    frame_003.name = "Frame.003"
    frame_003.label_size = 20
    frame_003.shrink = True

    # Node Frame.004
    frame_004 = _rr_glare.nodes.new("NodeFrame")
    frame_004.label = "Mix"
    frame_004.name = "Frame.004"
    frame_004.label_size = 20
    frame_004.shrink = True

    # Node Reroute.003
    reroute_003_2 = _rr_glare.nodes.new("NodeReroute")
    reroute_003_2.name = "Reroute.003"
    reroute_003_2.socket_idname = "NodeSocketColor"
    # Node Group Input.005
    group_input_005_1 = _rr_glare.nodes.new("NodeGroupInput")
    group_input_005_1.name = "Group Input.005"
    group_input_005_1.outputs[1].hide = True
    group_input_005_1.outputs[3].hide = True
    group_input_005_1.outputs[4].hide = True
    group_input_005_1.outputs[5].hide = True
    group_input_005_1.outputs[6].hide = True
    group_input_005_1.outputs[7].hide = True
    group_input_005_1.outputs[8].hide = True
    group_input_005_1.outputs[9].hide = True
    group_input_005_1.outputs[10].hide = True
    group_input_005_1.outputs[11].hide = True
    group_input_005_1.outputs[12].hide = True
    group_input_005_1.outputs[13].hide = True
    group_input_005_1.outputs[14].hide = True
    group_input_005_1.outputs[17].hide = True

    # Node Frame.005
    frame_005 = _rr_glare.nodes.new("NodeFrame")
    frame_005.label = "Halation"
    frame_005.name = "Frame.005"
    frame_005.label_size = 20
    frame_005.shrink = True

    # Node Add Halation
    add_halation = _rr_glare.nodes.new("ShaderNodeMix")
    add_halation.name = "Add Halation"
    add_halation.blend_type = 'ADD'
    add_halation.clamp_factor = False
    add_halation.clamp_result = False
    add_halation.data_type = 'RGBA'
    add_halation.factor_mode = 'UNIFORM'
    # Factor_Float
    add_halation.inputs[0].default_value = 1.0

    # Node Halation
    halation = _rr_glare.nodes.new("CompositorNodeGroup")
    halation.label = "Halation"
    halation.name = "Halation"
    halation.node_tree = _rr_halation

    # Node Add Glare
    add_glare = _rr_glare.nodes.new("ShaderNodeMix")
    add_glare.name = "Add Glare"
    add_glare.blend_type = 'ADD'
    add_glare.clamp_factor = False
    add_glare.clamp_result = False
    add_glare.data_type = 'RGBA'
    add_glare.factor_mode = 'UNIFORM'

    # Set parents
    mix_005.parent = frame_003
    separate_color_003_1.parent = frame_003
    reroute_005_3.parent = frame_003
    streaks.parent = frame_5
    glare_alpha.parent = frame_003
    group_input_5.parent = frame_5
    mix_006.parent = frame_003
    ghosting.parent = frame_002_1
    glare.parent = frame_001_2
    add_bloom.parent = frame_004
    add_streaks.parent = frame_004
    add_ghosting.parent = frame_004
    rgb.parent = frame_004
    map_range_4.parent = frame_5
    math_5.parent = frame_5
    float_curve.parent = frame_5
    group_input_001_2.parent = frame_004
    group_input_002.parent = frame_003
    group_input_003_1.parent = frame_001_2
    group_input_004_1.parent = frame_002_1
    switch_3.parent = frame_003
    math_004_3.parent = frame_003
    math_005_3.parent = frame_003
    math_006_3.parent = frame_003
    reroute_002_2.parent = frame_003
    reroute_003_2.parent = frame_003
    group_input_005_1.parent = frame_005
    add_halation.parent = frame_004
    halation.parent = frame_005
    add_glare.parent = frame_004

    # Set locations
    mix_005.location = (572.3328247070312, -173.404541015625)
    separate_color_003_1.location = (423.59942626953125, -254.4901123046875)
    reroute_005_3.location = (310.26300048828125, -264.758056640625)
    streaks.location = (856.9351196289062, -68.55044555664062)
    glare_alpha.location = (980.1426391601562, -35.5015869140625)
    group_input_5.location = (29.478271484375, -419.84991455078125)
    mix_006.location = (772.3557739257812, -210.859619140625)
    group_output_6.location = (2033.40380859375, -409.1210632324219)
    ghosting.location = (319.43878173828125, -35.998779296875)
    glare.location = (324.6446533203125, -36.18170166015625)
    add_bloom.location = (304.2311706542969, -337.0522155761719)
    add_streaks.location = (318.52020263671875, -83.44326782226562)
    add_ghosting.location = (302.7416076660156, -604.080078125)
    rgb.location = (29.112030029296875, -35.95599365234375)
    map_range_4.location = (598.793701171875, -567.5029907226562)
    math_5.location = (587.74462890625, -35.839508056640625)
    float_curve.location = (285.759765625, -38.824920654296875)
    group_input_001_2.location = (297.63543701171875, -1121.7041015625)
    group_input_002.location = (29.11822509765625, -235.273681640625)
    frame_5.location = (-1815.4801025390625, 449.8320007324219)
    group_input_003_1.location = (29.2261962890625, -196.28863525390625)
    frame_001_2.location = (-1277.6400146484375, -417.76800537109375)
    group_input_004_1.location = (28.953857421875, -187.03143310546875)
    frame_002_1.location = (-1271.1600341796875, -914.5680541992188)
    switch_3.location = (1269.748779296875, -237.6817626953125)
    math_004_3.location = (298.38433837890625, -336.973388671875)
    math_005_3.location = (300.04034423828125, -394.1260986328125)
    math_006_3.location = (295.90069580078125, -454.591796875)
    reroute_002_2.location = (309.86846923828125, -310.4219970703125)
    frame_003.location = (558.3600463867188, -601.3680419921875)
    frame_004.location = (-284.0400085449219, 442.63201904296875)
    reroute_003_2.location = (235.51055908203125, -106.6229248046875)
    group_input_005_1.location = (29.19677734375, -106.869384765625)
    frame_005.location = (-1250.280029296875, -1458.8880615234375)
    add_halation.location = (294.0220031738281, -854.92529296875)
    halation.location = (295.255126953125, -35.74462890625)
    add_glare.location = (606.1504516601562, -968.1110229492188)

    # Set dimensions
    mix_005.width, mix_005.height = 140.0, 100.0
    separate_color_003_1.width, separate_color_003_1.height = 140.0, 100.0
    reroute_005_3.width, reroute_005_3.height = 13.5, 100.0
    streaks.width, streaks.height = 190.12863159179688, 100.0
    glare_alpha.width, glare_alpha.height = 174.52017211914062, 100.0
    group_input_5.width, group_input_5.height = 140.0, 100.0
    mix_006.width, mix_006.height = 140.0, 100.0
    group_output_6.width, group_output_6.height = 140.0, 100.0
    ghosting.width, ghosting.height = 190.12863159179688, 100.0
    glare.width, glare.height = 185.4783935546875, 100.0
    add_bloom.width, add_bloom.height = 140.0, 100.0
    add_streaks.width, add_streaks.height = 140.0, 100.0
    add_ghosting.width, add_ghosting.height = 140.0, 100.0
    rgb.width, rgb.height = 140.0, 100.0
    map_range_4.width, map_range_4.height = 140.0, 100.0
    math_5.width, math_5.height = 140.0, 100.0
    float_curve.width, float_curve.height = 240.0, 100.0
    group_input_001_2.width, group_input_001_2.height = 140.0, 100.0
    group_input_002.width, group_input_002.height = 140.0, 100.0
    frame_5.width, frame_5.height = 1076.44873046875, 825.31201171875
    group_input_003_1.width, group_input_003_1.height = 140.0, 100.0
    frame_001_2.width, frame_001_2.height = 538.9984130859375, 440.11199951171875
    group_input_004_1.width, group_input_004_1.height = 140.0, 100.0
    frame_002_1.width, frame_002_1.height = 538.6085815429688, 460.99200439453125
    switch_3.width, switch_3.height = 140.0, 100.0
    math_004_3.width, math_004_3.height = 140.0, 100.0
    math_005_3.width, math_005_3.height = 140.0, 100.0
    math_006_3.width, math_006_3.height = 140.0, 100.0
    reroute_002_2.width, reroute_002_2.height = 13.5, 100.0
    frame_003.width, frame_003.height = 1438.8798828125, 508.33203125
    frame_004.width, frame_004.height = 775.0400390625, 1220.592041015625
    reroute_003_2.width, reroute_003_2.height = 13.5, 100.0
    group_input_005_1.width, group_input_005_1.height = 140.0, 100.0
    frame_005.width, frame_005.height = 503.98944091796875, 247.8719482421875
    add_halation.width, add_halation.height = 140.0, 100.0
    halation.width, halation.height = 179.26943969726562, 100.0
    add_glare.width, add_glare.height = 140.0, 100.0

    # Initialize _rr_glare links

    # reroute_003_2.Output -> mix_005.A
    _rr_glare.links.new(reroute_003_2.outputs[0], mix_005.inputs[6])
    # group_input_5.Image -> streaks.Image
    _rr_glare.links.new(group_input_5.outputs[0], streaks.inputs[0])
    # separate_color_003_1.Alpha -> mix_006.B
    _rr_glare.links.new(separate_color_003_1.outputs[3], mix_006.inputs[7])
    # mix_005.Result -> mix_006.A
    _rr_glare.links.new(mix_005.outputs[2], mix_006.inputs[6])
    # reroute_005_3.Output -> mix_005.B
    _rr_glare.links.new(reroute_005_3.outputs[0], mix_005.inputs[7])
    # reroute_003_2.Output -> glare_alpha.Image
    _rr_glare.links.new(reroute_003_2.outputs[0], glare_alpha.inputs[0])
    # reroute_005_3.Output -> separate_color_003_1.Image
    _rr_glare.links.new(reroute_005_3.outputs[0], separate_color_003_1.inputs[0])
    # add_bloom.Result -> add_ghosting.A
    _rr_glare.links.new(add_bloom.outputs[2], add_ghosting.inputs[6])
    # add_streaks.Result -> add_bloom.A
    _rr_glare.links.new(add_streaks.outputs[2], add_bloom.inputs[6])
    # rgb.RGBA -> add_streaks.A
    _rr_glare.links.new(rgb.outputs[0], add_streaks.inputs[6])
    # mix_006.Result -> glare_alpha.Alpha
    _rr_glare.links.new(mix_006.outputs[2], glare_alpha.inputs[1])
    # streaks.Glare -> add_streaks.B
    _rr_glare.links.new(streaks.outputs[1], add_streaks.inputs[7])
    # glare.Glare -> add_bloom.B
    _rr_glare.links.new(glare.outputs[1], add_bloom.inputs[7])
    # ghosting.Glare -> add_ghosting.B
    _rr_glare.links.new(ghosting.outputs[1], add_ghosting.inputs[7])
    # group_input_5.Saturation -> streaks.Saturation
    _rr_glare.links.new(group_input_5.outputs[4], streaks.inputs[6])
    # group_input_5.Tint -> streaks.Tint
    _rr_glare.links.new(group_input_5.outputs[5], streaks.inputs[7])
    # group_input_5.Threshold -> streaks.Threshold
    _rr_glare.links.new(group_input_5.outputs[2], streaks.inputs[1])
    # group_input_5.Length -> map_range_4.Value
    _rr_glare.links.new(group_input_5.outputs[9], map_range_4.inputs[0])
    # map_range_4.Result -> streaks.Fade
    _rr_glare.links.new(map_range_4.outputs[0], streaks.inputs[12])
    # group_input_5.Streaks Strength -> float_curve.Value
    _rr_glare.links.new(group_input_5.outputs[8], float_curve.inputs[1])
    # float_curve.Value -> math_5.Value
    _rr_glare.links.new(float_curve.outputs[0], math_5.inputs[0])
    # math_5.Value -> streaks.Strength
    _rr_glare.links.new(math_5.outputs[0], streaks.inputs[5])
    # group_input_5.Count -> streaks.Streaks
    _rr_glare.links.new(group_input_5.outputs[10], streaks.inputs[9])
    # group_input_5.Angle -> streaks.Streaks Angle
    _rr_glare.links.new(group_input_5.outputs[11], streaks.inputs[10])
    # group_input_002.Image -> reroute_005_3.Input
    _rr_glare.links.new(group_input_002.outputs[0], reroute_005_3.inputs[0])
    # group_input_003_1.Tint -> glare.Tint
    _rr_glare.links.new(group_input_003_1.outputs[5], glare.inputs[7])
    # group_input_003_1.Saturation -> glare.Saturation
    _rr_glare.links.new(group_input_003_1.outputs[4], glare.inputs[6])
    # group_input_003_1.Threshold -> glare.Threshold
    _rr_glare.links.new(group_input_003_1.outputs[2], glare.inputs[1])
    # group_input_004_1.Threshold -> ghosting.Threshold
    _rr_glare.links.new(group_input_004_1.outputs[2], ghosting.inputs[1])
    # group_input_004_1.Saturation -> ghosting.Saturation
    _rr_glare.links.new(group_input_004_1.outputs[4], ghosting.inputs[6])
    # group_input_004_1.Tint -> ghosting.Tint
    _rr_glare.links.new(group_input_004_1.outputs[5], ghosting.inputs[7])
    # group_input_5.Smoothness -> streaks.Smoothness
    _rr_glare.links.new(group_input_5.outputs[3], streaks.inputs[2])
    # group_input_003_1.Smoothness -> glare.Smoothness
    _rr_glare.links.new(group_input_003_1.outputs[3], glare.inputs[2])
    # group_input_004_1.Smoothness -> ghosting.Smoothness
    _rr_glare.links.new(group_input_004_1.outputs[3], ghosting.inputs[2])
    # glare_alpha.Image -> switch_3.On
    _rr_glare.links.new(glare_alpha.outputs[0], switch_3.inputs[2])
    # group_input_002.Factor -> math_004_3.Value
    _rr_glare.links.new(group_input_002.outputs[1], math_004_3.inputs[0])
    # group_input_002.Bloom Strength -> math_004_3.Value
    _rr_glare.links.new(group_input_002.outputs[6], math_004_3.inputs[1])
    # math_004_3.Value -> math_005_3.Value
    _rr_glare.links.new(math_004_3.outputs[0], math_005_3.inputs[0])
    # group_input_002.Streaks Strength -> math_005_3.Value
    _rr_glare.links.new(group_input_002.outputs[8], math_005_3.inputs[1])
    # math_005_3.Value -> math_006_3.Value
    _rr_glare.links.new(math_005_3.outputs[0], math_006_3.inputs[0])
    # group_input_002.Ghosting Strength -> math_006_3.Value
    _rr_glare.links.new(group_input_002.outputs[12], math_006_3.inputs[1])
    # math_006_3.Value -> switch_3.Switch
    _rr_glare.links.new(math_006_3.outputs[0], switch_3.inputs[0])
    # reroute_002_2.Output -> switch_3.Off
    _rr_glare.links.new(reroute_002_2.outputs[0], switch_3.inputs[1])
    # group_input_002.Image -> reroute_002_2.Input
    _rr_glare.links.new(group_input_002.outputs[0], reroute_002_2.inputs[0])
    # group_input_003_1.Size -> glare.Size
    _rr_glare.links.new(group_input_003_1.outputs[7], glare.inputs[8])
    # group_input_004_1.Color Modulation -> ghosting.Color Modulation
    _rr_glare.links.new(group_input_004_1.outputs[13], ghosting.inputs[13])
    # group_input_004_1.Steps -> ghosting.Iterations
    _rr_glare.links.new(group_input_004_1.outputs[14], ghosting.inputs[11])
    # glare_alpha.Image -> group_output_6.Image
    _rr_glare.links.new(glare_alpha.outputs[0], group_output_6.inputs[0])
    # add_ghosting.Result -> add_halation.A
    _rr_glare.links.new(add_ghosting.outputs[2], add_halation.inputs[6])
    # halation.Glare -> add_halation.B
    _rr_glare.links.new(halation.outputs[1], add_halation.inputs[7])
    # add_halation.Result -> group_output_6.Glare
    _rr_glare.links.new(add_halation.outputs[2], group_output_6.inputs[1])
    # group_input_005_1.Halation Strength -> halation.Strength
    _rr_glare.links.new(group_input_005_1.outputs[15], halation.inputs[2])
    # group_input_005_1.Threshold -> halation.Threshold
    _rr_glare.links.new(group_input_005_1.outputs[2], halation.inputs[1])
    # group_input_005_1.Halation Size -> halation.Size
    _rr_glare.links.new(group_input_005_1.outputs[16], halation.inputs[3])
    # group_input_003_1.Bloom Strength -> glare.Strength
    _rr_glare.links.new(group_input_003_1.outputs[6], glare.inputs[5])
    # group_input_003_1.Image -> glare.Image
    _rr_glare.links.new(group_input_003_1.outputs[0], glare.inputs[0])
    # group_input_004_1.Ghosting Strength -> ghosting.Strength
    _rr_glare.links.new(group_input_004_1.outputs[12], ghosting.inputs[5])
    # group_input_004_1.Image -> ghosting.Image
    _rr_glare.links.new(group_input_004_1.outputs[0], ghosting.inputs[0])
    # group_input_005_1.Image -> halation.Image
    _rr_glare.links.new(group_input_005_1.outputs[0], halation.inputs[0])
    # add_halation.Result -> add_glare.B
    _rr_glare.links.new(add_halation.outputs[2], add_glare.inputs[7])
    # group_input_001_2.Image -> add_glare.A
    _rr_glare.links.new(group_input_001_2.outputs[0], add_glare.inputs[6])
    # add_glare.Result -> reroute_003_2.Input
    _rr_glare.links.new(add_glare.outputs[2], reroute_003_2.inputs[0])
    # group_input_001_2.Factor -> add_glare.Factor
    _rr_glare.links.new(group_input_001_2.outputs[1], add_glare.inputs[0])

    return _rr_glare


_rr_glare = _rr_glare_node_group()

def _rr_vignette_node_group():
    """Initialize .RR_vignette node group"""
    _rr_vignette = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_vignette")

    _rr_vignette.color_tag = 'NONE'
    _rr_vignette.description = ""
    _rr_vignette.default_group_node_width = 200
    # _rr_vignette interface

    # Socket Image
    image_socket_12 = _rr_vignette.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_12.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_12.attribute_domain = 'POINT'
    image_socket_12.default_input = 'VALUE'
    image_socket_12.structure_type = 'AUTO'

    # Socket Mask
    mask_socket = _rr_vignette.interface.new_socket(name="Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    mask_socket.default_value = 0.0
    mask_socket.min_value = -3.4028234663852886e+38
    mask_socket.max_value = 3.4028234663852886e+38
    mask_socket.subtype = 'NONE'
    mask_socket.attribute_domain = 'POINT'
    mask_socket.default_input = 'VALUE'
    mask_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_13 = _rr_vignette.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_13.default_value = (0.5, 0.5, 0.5, 1.0)
    image_socket_13.attribute_domain = 'POINT'
    image_socket_13.default_input = 'VALUE'
    image_socket_13.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_3 = _rr_vignette.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_3.default_value = 1.0
    factor_socket_3.min_value = 0.0
    factor_socket_3.max_value = 1.0
    factor_socket_3.subtype = 'FACTOR'
    factor_socket_3.attribute_domain = 'POINT'
    factor_socket_3.default_input = 'VALUE'
    factor_socket_3.structure_type = 'AUTO'

    # Socket Color
    color_socket = _rr_vignette.interface.new_socket(name="Color", in_out='INPUT', socket_type='NodeSocketColor')
    color_socket.default_value = (0.0, 0.0, 0.0, 1.0)
    color_socket.attribute_domain = 'POINT'
    color_socket.default_input = 'VALUE'
    color_socket.structure_type = 'AUTO'

    # Socket Highlights
    highlights_socket_1 = _rr_vignette.interface.new_socket(name="Highlights", in_out='INPUT', socket_type='NodeSocketFloat')
    highlights_socket_1.default_value = 0.0
    highlights_socket_1.min_value = 0.0
    highlights_socket_1.max_value = 1.0
    highlights_socket_1.subtype = 'FACTOR'
    highlights_socket_1.attribute_domain = 'POINT'
    highlights_socket_1.default_input = 'VALUE'
    highlights_socket_1.structure_type = 'AUTO'

    # Socket Linear Blending
    linear_blending_socket = _rr_vignette.interface.new_socket(name="Linear Blending", in_out='INPUT', socket_type='NodeSocketFloat')
    linear_blending_socket.default_value = 0.0
    linear_blending_socket.min_value = 0.0
    linear_blending_socket.max_value = 1.0
    linear_blending_socket.subtype = 'FACTOR'
    linear_blending_socket.attribute_domain = 'POINT'
    linear_blending_socket.default_input = 'VALUE'
    linear_blending_socket.structure_type = 'AUTO'

    # Socket Roundness
    roundness_socket = _rr_vignette.interface.new_socket(name="Roundness", in_out='INPUT', socket_type='NodeSocketFloat')
    roundness_socket.default_value = 1.0
    roundness_socket.min_value = 0.0
    roundness_socket.max_value = 1.0
    roundness_socket.subtype = 'FACTOR'
    roundness_socket.attribute_domain = 'POINT'
    roundness_socket.default_input = 'VALUE'
    roundness_socket.structure_type = 'AUTO'

    # Socket Feathering
    feathering_socket = _rr_vignette.interface.new_socket(name="Feathering", in_out='INPUT', socket_type='NodeSocketFloat')
    feathering_socket.default_value = 0.5
    feathering_socket.min_value = 0.0
    feathering_socket.max_value = 1.0
    feathering_socket.subtype = 'FACTOR'
    feathering_socket.attribute_domain = 'POINT'
    feathering_socket.default_input = 'VALUE'
    feathering_socket.structure_type = 'AUTO'

    # Panel Transform
    transform_panel = _rr_vignette.interface.new_panel("Transform")
    # Socket Scale X
    scale_x_socket = _rr_vignette.interface.new_socket(name="Scale X", in_out='INPUT', socket_type='NodeSocketFloat', parent = transform_panel)
    scale_x_socket.default_value = 1.0
    scale_x_socket.min_value = 0.0
    scale_x_socket.max_value = 2.0
    scale_x_socket.subtype = 'FACTOR'
    scale_x_socket.attribute_domain = 'POINT'
    scale_x_socket.default_input = 'VALUE'
    scale_x_socket.structure_type = 'AUTO'

    # Socket Scale Y
    scale_y_socket = _rr_vignette.interface.new_socket(name="Scale Y", in_out='INPUT', socket_type='NodeSocketFloat', parent = transform_panel)
    scale_y_socket.default_value = 1.0
    scale_y_socket.min_value = 0.0
    scale_y_socket.max_value = 2.0
    scale_y_socket.subtype = 'FACTOR'
    scale_y_socket.attribute_domain = 'POINT'
    scale_y_socket.default_input = 'VALUE'
    scale_y_socket.structure_type = 'AUTO'

    # Socket Rotation
    rotation_socket = _rr_vignette.interface.new_socket(name="Rotation", in_out='INPUT', socket_type='NodeSocketFloat', parent = transform_panel)
    rotation_socket.default_value = 0.0
    rotation_socket.min_value = -10000.0
    rotation_socket.max_value = 10000.0
    rotation_socket.subtype = 'ANGLE'
    rotation_socket.attribute_domain = 'POINT'
    rotation_socket.default_input = 'VALUE'
    rotation_socket.structure_type = 'AUTO'

    # Socket Shift X
    shift_x_socket = _rr_vignette.interface.new_socket(name="Shift X", in_out='INPUT', socket_type='NodeSocketFloat', parent = transform_panel)
    shift_x_socket.default_value = 0.0
    shift_x_socket.min_value = -1.0
    shift_x_socket.max_value = 1.0
    shift_x_socket.subtype = 'FACTOR'
    shift_x_socket.attribute_domain = 'POINT'
    shift_x_socket.default_input = 'VALUE'
    shift_x_socket.structure_type = 'AUTO'

    # Socket Shift Y
    shift_y_socket = _rr_vignette.interface.new_socket(name="Shift Y", in_out='INPUT', socket_type='NodeSocketFloat', parent = transform_panel)
    shift_y_socket.default_value = 0.0
    shift_y_socket.min_value = -1.0
    shift_y_socket.max_value = 1.0
    shift_y_socket.subtype = 'FACTOR'
    shift_y_socket.attribute_domain = 'POINT'
    shift_y_socket.default_input = 'VALUE'
    shift_y_socket.structure_type = 'AUTO'


    # Initialize _rr_vignette nodes

    # Node Group Output
    group_output_7 = _rr_vignette.nodes.new("NodeGroupOutput")
    group_output_7.name = "Group Output"
    group_output_7.is_active_output = True

    # Node Group Input
    group_input_6 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_6.name = "Group Input"

    # Node Frame
    frame_6 = _rr_vignette.nodes.new("NodeFrame")
    frame_6.label = "Mask"
    frame_6.name = "Frame"
    frame_6.label_size = 20
    frame_6.shrink = True

    # Node Blur
    blur_1 = _rr_vignette.nodes.new("CompositorNodeBlur")
    blur_1.name = "Blur"
    blur_1.filter_type = 'FAST_GAUSS'
    # Extend Bounds
    blur_1.inputs[2].default_value = True
    # Separable
    blur_1.inputs[3].default_value = True

    # Node Image Info
    image_info = _rr_vignette.nodes.new("CompositorNodeImageInfo")
    image_info.name = "Image Info"
    image_info.outputs[1].hide = True
    image_info.outputs[2].hide = True
    image_info.outputs[3].hide = True
    image_info.outputs[4].hide = True

    # Node Separate XYZ
    separate_xyz = _rr_vignette.nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.name = "Separate XYZ"

    # Node Math
    math_6 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_6.name = "Math"
    math_6.operation = 'MAXIMUM'
    math_6.use_clamp = False

    # Node Map Range
    map_range_5 = _rr_vignette.nodes.new("ShaderNodeMapRange")
    map_range_5.name = "Map Range"
    map_range_5.clamp = True
    map_range_5.data_type = 'FLOAT'
    map_range_5.interpolation_type = 'LINEAR'
    # From Min
    map_range_5.inputs[1].default_value = 0.0
    # From Max
    map_range_5.inputs[2].default_value = 1.0
    # To Min
    map_range_5.inputs[3].default_value = 0.0

    # Node Math.001
    math_001_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_001_4.name = "Math.001"
    math_001_4.operation = 'DIVIDE'
    math_001_4.use_clamp = False
    # Value_001
    math_001_4.inputs[1].default_value = 2.0

    # Node Math.002
    math_002_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_002_4.name = "Math.002"
    math_002_4.hide = True
    math_002_4.operation = 'MULTIPLY'
    math_002_4.use_clamp = False

    # Node Math.003
    math_003_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_003_4.label = "Halve"
    math_003_4.name = "Math.003"
    math_003_4.hide = True
    math_003_4.operation = 'DIVIDE'
    math_003_4.use_clamp = False
    math_003_4.inputs[1].hide = True
    math_003_4.inputs[2].hide = True
    # Value_001
    math_003_4.inputs[1].default_value = 2.0

    # Node Math.004
    math_004_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_004_4.label = "Halve"
    math_004_4.name = "Math.004"
    math_004_4.hide = True
    math_004_4.operation = 'DIVIDE'
    math_004_4.use_clamp = False
    math_004_4.inputs[1].hide = True
    math_004_4.inputs[2].hide = True
    # Value_001
    math_004_4.inputs[1].default_value = 2.0

    # Node Math.005
    math_005_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_005_4.name = "Math.005"
    math_005_4.hide = True
    math_005_4.operation = 'MULTIPLY'
    math_005_4.use_clamp = False

    # Node Group Input.001
    group_input_001_3 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_001_3.name = "Group Input.001"
    group_input_001_3.outputs[1].hide = True
    group_input_001_3.outputs[3].hide = True
    group_input_001_3.outputs[4].hide = True
    group_input_001_3.outputs[5].hide = True
    group_input_001_3.outputs[6].hide = True
    group_input_001_3.outputs[7].hide = True
    group_input_001_3.outputs[8].hide = True
    group_input_001_3.outputs[9].hide = True
    group_input_001_3.outputs[10].hide = True
    group_input_001_3.outputs[11].hide = True
    group_input_001_3.outputs[12].hide = True

    # Node Mix
    mix_4 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_4.name = "Mix"
    mix_4.blend_type = 'MIX'
    mix_4.clamp_factor = True
    mix_4.clamp_result = False
    mix_4.data_type = 'RGBA'
    mix_4.factor_mode = 'UNIFORM'

    # Node Frame.001
    frame_001_3 = _rr_vignette.nodes.new("NodeFrame")
    frame_001_3.label = "Simple Blending"
    frame_001_3.name = "Frame.001"
    frame_001_3.label_size = 20
    frame_001_3.shrink = True

    # Node Group Input.002
    group_input_002_1 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_002_1.name = "Group Input.002"
    group_input_002_1.outputs[1].hide = True
    group_input_002_1.outputs[3].hide = True
    group_input_002_1.outputs[4].hide = True
    group_input_002_1.outputs[5].hide = True
    group_input_002_1.outputs[6].hide = True
    group_input_002_1.outputs[7].hide = True
    group_input_002_1.outputs[8].hide = True
    group_input_002_1.outputs[9].hide = True
    group_input_002_1.outputs[10].hide = True
    group_input_002_1.outputs[11].hide = True
    group_input_002_1.outputs[12].hide = True

    # Node Frame.002
    frame_002_2 = _rr_vignette.nodes.new("NodeFrame")
    frame_002_2.label = "Linear Blending"
    frame_002_2.name = "Frame.002"
    frame_002_2.label_size = 20
    frame_002_2.shrink = True

    # Node Mix.004
    mix_004_1 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_004_1.name = "Mix.004"
    mix_004_1.blend_type = 'MIX'
    mix_004_1.clamp_factor = True
    mix_004_1.clamp_result = False
    mix_004_1.data_type = 'RGBA'
    mix_004_1.factor_mode = 'UNIFORM'

    # Node Group Input.003
    group_input_003_2 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_003_2.name = "Group Input.003"
    group_input_003_2.outputs[5].hide = True
    group_input_003_2.outputs[6].hide = True
    group_input_003_2.outputs[7].hide = True
    group_input_003_2.outputs[8].hide = True
    group_input_003_2.outputs[9].hide = True
    group_input_003_2.outputs[10].hide = True
    group_input_003_2.outputs[11].hide = True
    group_input_003_2.outputs[12].hide = True

    # Node Mix.005
    mix_005_1 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_005_1.name = "Mix.005"
    mix_005_1.blend_type = 'MIX'
    mix_005_1.clamp_factor = True
    mix_005_1.clamp_result = False
    mix_005_1.data_type = 'RGBA'
    mix_005_1.factor_mode = 'UNIFORM'

    # Node Separate Color
    separate_color_2 = _rr_vignette.nodes.new("CompositorNodeSeparateColor")
    separate_color_2.name = "Separate Color"
    separate_color_2.mode = 'HSV'
    separate_color_2.ycc_mode = 'ITUBT709'

    # Node Combine Color
    combine_color_2 = _rr_vignette.nodes.new("CompositorNodeCombineColor")
    combine_color_2.name = "Combine Color"
    combine_color_2.mode = 'HSV'
    combine_color_2.ycc_mode = 'ITUBT709'

    # Node Math.007
    math_007_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_007_4.name = "Math.007"
    math_007_4.hide = True
    math_007_4.operation = 'MULTIPLY'
    math_007_4.use_clamp = False

    # Node Math.008
    math_008_3 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_008_3.name = "Math.008"
    math_008_3.operation = 'MINIMUM'
    math_008_3.use_clamp = False
    # Value_001
    math_008_3.inputs[1].default_value = 1.0

    # Node Mix.006
    mix_006_1 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_006_1.name = "Mix.006"
    mix_006_1.blend_type = 'ADD'
    mix_006_1.clamp_factor = True
    mix_006_1.clamp_result = False
    mix_006_1.data_type = 'RGBA'
    mix_006_1.factor_mode = 'UNIFORM'

    # Node Mix.007
    mix_007 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_007.name = "Mix.007"
    mix_007.blend_type = 'MULTIPLY'
    mix_007.clamp_factor = True
    mix_007.clamp_result = False
    mix_007.data_type = 'RGBA'
    mix_007.factor_mode = 'UNIFORM'

    # Node Mix.008
    mix_008 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_008.name = "Mix.008"
    mix_008.blend_type = 'MIX'
    mix_008.clamp_factor = True
    mix_008.clamp_result = False
    mix_008.data_type = 'RGBA'
    mix_008.factor_mode = 'UNIFORM'

    # Node Math.006
    math_006_4 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_006_4.name = "Math.006"
    math_006_4.operation = 'SUBTRACT'
    math_006_4.use_clamp = True

    # Node Mix.009
    mix_009 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_009.name = "Mix.009"
    mix_009.blend_type = 'MIX'
    mix_009.clamp_factor = True
    mix_009.clamp_result = False
    mix_009.data_type = 'FLOAT'
    mix_009.factor_mode = 'UNIFORM'

    # Node Map Range.002
    map_range_002_4 = _rr_vignette.nodes.new("ShaderNodeMapRange")
    map_range_002_4.name = "Map Range.002"
    map_range_002_4.clamp = True
    map_range_002_4.data_type = 'FLOAT'
    map_range_002_4.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_4.inputs[1].default_value = 0.0
    # From Max
    map_range_002_4.inputs[2].default_value = 1.0
    # To Min
    map_range_002_4.inputs[3].default_value = 1.0

    # Node Frame.003
    frame_003_1 = _rr_vignette.nodes.new("NodeFrame")
    frame_003_1.label = "Safety"
    frame_003_1.name = "Frame.003"
    frame_003_1.label_size = 20
    frame_003_1.shrink = True

    # Node Frame.004
    frame_004_1 = _rr_vignette.nodes.new("NodeFrame")
    frame_004_1.label = "Mix"
    frame_004_1.name = "Frame.004"
    frame_004_1.label_size = 20
    frame_004_1.shrink = True

    # Node Reroute.010
    reroute_010 = _rr_vignette.nodes.new("NodeReroute")
    reroute_010.name = "Reroute.010"
    reroute_010.socket_idname = "NodeSocketColor"
    # Node Reroute.011
    reroute_011 = _rr_vignette.nodes.new("NodeReroute")
    reroute_011.name = "Reroute.011"
    reroute_011.socket_idname = "NodeSocketColor"
    # Node Reroute.012
    reroute_012 = _rr_vignette.nodes.new("NodeReroute")
    reroute_012.name = "Reroute.012"
    reroute_012.socket_idname = "NodeSocketColor"
    # Node Reroute.013
    reroute_013 = _rr_vignette.nodes.new("NodeReroute")
    reroute_013.name = "Reroute.013"
    reroute_013.socket_idname = "NodeSocketColor"
    # Node Image Coordinates
    image_coordinates = _rr_vignette.nodes.new("CompositorNodeImageCoordinates")
    image_coordinates.name = "Image Coordinates"

    # Node Separate XYZ.004
    separate_xyz_004 = _rr_vignette.nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz_004.name = "Separate XYZ.004"

    # Node Math.022
    math_022 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_022.name = "Math.022"
    math_022.hide = True
    math_022.operation = 'POWER'
    math_022.use_clamp = False

    # Node Math.023
    math_023 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_023.name = "Math.023"
    math_023.hide = True
    math_023.operation = 'ADD'
    math_023.use_clamp = False

    # Node Math.024
    math_024 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_024.name = "Math.024"
    math_024.hide = True
    math_024.operation = 'POWER'
    math_024.use_clamp = False

    # Node Math.025
    math_025 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_025.name = "Math.025"
    math_025.operation = 'GREATER_THAN'
    math_025.use_clamp = False
    # Value_001
    math_025.inputs[1].default_value = 0.10000000149011612

    # Node Math.026
    math_026 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_026.name = "Math.026"
    math_026.hide = True
    math_026.operation = 'POWER'
    math_026.use_clamp = False

    # Node Vector Math.006
    vector_math_006 = _rr_vignette.nodes.new("ShaderNodeVectorMath")
    vector_math_006.name = "Vector Math.006"
    vector_math_006.hide = True
    vector_math_006.operation = 'SCALE'

    # Node Vector Math.007
    vector_math_007 = _rr_vignette.nodes.new("ShaderNodeVectorMath")
    vector_math_007.name = "Vector Math.007"
    vector_math_007.operation = 'SUBTRACT'
    # Vector_001
    vector_math_007.inputs[1].default_value = (0.5, 0.49999991059303284, 0.5)

    # Node Vector Math.008
    vector_math_008 = _rr_vignette.nodes.new("ShaderNodeVectorMath")
    vector_math_008.name = "Vector Math.008"
    vector_math_008.hide = True
    vector_math_008.operation = 'ABSOLUTE'

    # Node Math.027
    math_027 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_027.name = "Math.027"
    math_027.operation = 'POWER'
    math_027.use_clamp = False
    # Value_001
    math_027.inputs[1].default_value = 0.5

    # Node Math.028
    math_028 = _rr_vignette.nodes.new("ShaderNodeMath")
    math_028.name = "Math.028"
    math_028.operation = 'POWER'
    math_028.use_clamp = False
    # Value_001
    math_028.inputs[1].default_value = 4.0

    # Node Map Range.003
    map_range_003_3 = _rr_vignette.nodes.new("ShaderNodeMapRange")
    map_range_003_3.name = "Map Range.003"
    map_range_003_3.clamp = True
    map_range_003_3.data_type = 'FLOAT'
    map_range_003_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_3.inputs[1].default_value = 0.0
    # From Max
    map_range_003_3.inputs[2].default_value = 1.0
    # To Min
    map_range_003_3.inputs[3].default_value = 1.2000000476837158
    # To Max
    map_range_003_3.inputs[4].default_value = 5.0

    # Node Float Curve
    float_curve_1 = _rr_vignette.nodes.new("ShaderNodeFloatCurve")
    float_curve_1.name = "Float Curve"
    # Mapping settings
    float_curve_1.mapping.extend = 'EXTRAPOLATED'
    float_curve_1.mapping.tone = 'STANDARD'
    float_curve_1.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_1.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_1.mapping.clip_min_x = 0.0
    float_curve_1.mapping.clip_min_y = 0.0
    float_curve_1.mapping.clip_max_x = 1.0
    float_curve_1.mapping.clip_max_y = 1.0
    float_curve_1.mapping.use_clip = True
    # Curve 0
    float_curve_1_curve_0 = float_curve_1.mapping.curves[0]
    float_curve_1_curve_0_point_0 = float_curve_1_curve_0.points[0]
    float_curve_1_curve_0_point_0.location = (0.0, 0.0)
    float_curve_1_curve_0_point_0.handle_type = 'AUTO'
    float_curve_1_curve_0_point_1 = float_curve_1_curve_0.points[1]
    float_curve_1_curve_0_point_1.location = (0.75, 0.25)
    float_curve_1_curve_0_point_1.handle_type = 'AUTO'
    float_curve_1_curve_0_point_2 = float_curve_1_curve_0.points.new(1.0, 1.0)
    float_curve_1_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_1.mapping.update()
    # Factor
    float_curve_1.inputs[0].default_value = 1.0

    # Node Map Range.004
    map_range_004_1 = _rr_vignette.nodes.new("ShaderNodeMapRange")
    map_range_004_1.name = "Map Range.004"
    map_range_004_1.clamp = True
    map_range_004_1.data_type = 'FLOAT'
    map_range_004_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_004_1.inputs[1].default_value = 0.0
    # From Max
    map_range_004_1.inputs[2].default_value = 1.0
    # To Min
    map_range_004_1.inputs[3].default_value = 0.949999988079071
    # To Max
    map_range_004_1.inputs[4].default_value = 2.049999952316284

    # Node Float Curve.001
    float_curve_001 = _rr_vignette.nodes.new("ShaderNodeFloatCurve")
    float_curve_001.name = "Float Curve.001"
    # Mapping settings
    float_curve_001.mapping.extend = 'EXTRAPOLATED'
    float_curve_001.mapping.tone = 'STANDARD'
    float_curve_001.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_001.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_001.mapping.clip_min_x = 0.0
    float_curve_001.mapping.clip_min_y = 0.0
    float_curve_001.mapping.clip_max_x = 1.0
    float_curve_001.mapping.clip_max_y = 1.0
    float_curve_001.mapping.use_clip = True
    # Curve 0
    float_curve_001_curve_0 = float_curve_001.mapping.curves[0]
    float_curve_001_curve_0_point_0 = float_curve_001_curve_0.points[0]
    float_curve_001_curve_0_point_0.location = (0.0, 0.0)
    float_curve_001_curve_0_point_0.handle_type = 'AUTO'
    float_curve_001_curve_0_point_1 = float_curve_001_curve_0.points[1]
    float_curve_001_curve_0_point_1.location = (0.25, 0.23000001907348633)
    float_curve_001_curve_0_point_1.handle_type = 'AUTO'
    float_curve_001_curve_0_point_2 = float_curve_001_curve_0.points.new(0.4000000059604645, 0.4699999988079071)
    float_curve_001_curve_0_point_2.handle_type = 'AUTO'
    float_curve_001_curve_0_point_3 = float_curve_001_curve_0.points.new(0.5, 0.6599997282028198)
    float_curve_001_curve_0_point_3.handle_type = 'AUTO'
    float_curve_001_curve_0_point_4 = float_curve_001_curve_0.points.new(0.75, 0.9550001621246338)
    float_curve_001_curve_0_point_4.handle_type = 'AUTO'
    float_curve_001_curve_0_point_5 = float_curve_001_curve_0.points.new(0.8999999761581421, 0.9900000095367432)
    float_curve_001_curve_0_point_5.handle_type = 'AUTO'
    float_curve_001_curve_0_point_6 = float_curve_001_curve_0.points.new(1.0, 1.0)
    float_curve_001_curve_0_point_6.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_001.mapping.update()
    # Factor
    float_curve_001.inputs[0].default_value = 1.0

    # Node Map Range.005
    map_range_005_2 = _rr_vignette.nodes.new("ShaderNodeMapRange")
    map_range_005_2.name = "Map Range.005"
    map_range_005_2.clamp = True
    map_range_005_2.data_type = 'FLOAT'
    map_range_005_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_2.inputs[1].default_value = 0.0
    # From Max
    map_range_005_2.inputs[2].default_value = 1.0
    # To Min
    map_range_005_2.inputs[3].default_value = 1.0
    # To Max
    map_range_005_2.inputs[4].default_value = 0.0

    # Node Rotate.001
    rotate_001 = _rr_vignette.nodes.new("CompositorNodeRotate")
    rotate_001.name = "Rotate.001"
    rotate_001.filter_type = 'BILINEAR'

    # Node Alpha Over.001
    alpha_over_001 = _rr_vignette.nodes.new("CompositorNodeAlphaOver")
    alpha_over_001.name = "Alpha Over.001"
    # Fac
    alpha_over_001.inputs[0].default_value = 1.0
    # Straight Alpha
    alpha_over_001.inputs[3].default_value = False

    # Node Scale.001
    scale_001 = _rr_vignette.nodes.new("CompositorNodeScale")
    scale_001.name = "Scale.001"
    scale_001.frame_method = 'STRETCH'
    scale_001.interpolation = 'BILINEAR'
    scale_001.space = 'RELATIVE'

    # Node Mix.003
    mix_003_1 = _rr_vignette.nodes.new("ShaderNodeMix")
    mix_003_1.name = "Mix.003"
    mix_003_1.blend_type = 'ADD'
    mix_003_1.clamp_factor = True
    mix_003_1.clamp_result = True
    mix_003_1.data_type = 'RGBA'
    mix_003_1.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_003_1.inputs[0].default_value = 1.0
    # B_Color
    mix_003_1.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Translate.001
    translate_001 = _rr_vignette.nodes.new("CompositorNodeTranslate")
    translate_001.name = "Translate.001"
    translate_001.interpolation = 'NEAREST'
    translate_001.wrap_axis = 'NONE'

    # Node Group Input.004
    group_input_004_2 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_004_2.name = "Group Input.004"
    group_input_004_2.outputs[0].hide = True
    group_input_004_2.outputs[1].hide = True
    group_input_004_2.outputs[2].hide = True
    group_input_004_2.outputs[3].hide = True
    group_input_004_2.outputs[4].hide = True
    group_input_004_2.outputs[5].hide = True
    group_input_004_2.outputs[12].hide = True

    # Node Group Input.005
    group_input_005_2 = _rr_vignette.nodes.new("NodeGroupInput")
    group_input_005_2.name = "Group Input.005"
    group_input_005_2.outputs[1].hide = True
    group_input_005_2.outputs[2].hide = True
    group_input_005_2.outputs[3].hide = True
    group_input_005_2.outputs[4].hide = True
    group_input_005_2.outputs[5].hide = True
    group_input_005_2.outputs[6].hide = True
    group_input_005_2.outputs[7].hide = True
    group_input_005_2.outputs[8].hide = True
    group_input_005_2.outputs[9].hide = True
    group_input_005_2.outputs[10].hide = True
    group_input_005_2.outputs[11].hide = True
    group_input_005_2.outputs[12].hide = True

    # Node Reroute
    reroute_4 = _rr_vignette.nodes.new("NodeReroute")
    reroute_4.name = "Reroute"
    reroute_4.socket_idname = "NodeSocketColor"
    # Node Reroute.001
    reroute_001_2 = _rr_vignette.nodes.new("NodeReroute")
    reroute_001_2.name = "Reroute.001"
    reroute_001_2.socket_idname = "NodeSocketColor"
    # Set parents
    group_input_6.parent = frame_6
    blur_1.parent = frame_6
    image_info.parent = frame_6
    separate_xyz.parent = frame_6
    math_6.parent = frame_6
    map_range_5.parent = frame_6
    math_001_4.parent = frame_6
    math_002_4.parent = frame_6
    math_003_4.parent = frame_6
    math_004_4.parent = frame_6
    math_005_4.parent = frame_6
    group_input_001_3.parent = frame_001_3
    mix_4.parent = frame_001_3
    group_input_002_1.parent = frame_002_2
    mix_004_1.parent = frame_004_1
    group_input_003_2.parent = frame_004_1
    mix_005_1.parent = frame_004_1
    separate_color_2.parent = frame_003_1
    combine_color_2.parent = frame_003_1
    math_007_4.parent = frame_004_1
    math_008_3.parent = frame_003_1
    mix_006_1.parent = frame_002_2
    mix_007.parent = frame_002_2
    mix_008.parent = frame_002_2
    math_006_4.parent = frame_004_1
    mix_009.parent = frame_004_1
    map_range_002_4.parent = frame_004_1
    reroute_010.parent = frame_004_1
    reroute_011.parent = frame_004_1
    reroute_012.parent = frame_004_1
    reroute_013.parent = frame_002_2
    image_coordinates.parent = frame_6
    separate_xyz_004.parent = frame_6
    math_022.parent = frame_6
    math_023.parent = frame_6
    math_024.parent = frame_6
    math_025.parent = frame_6
    math_026.parent = frame_6
    vector_math_006.parent = frame_6
    vector_math_007.parent = frame_6
    vector_math_008.parent = frame_6
    math_027.parent = frame_6
    math_028.parent = frame_6
    map_range_003_3.parent = frame_6
    float_curve_1.parent = frame_6
    map_range_004_1.parent = frame_6
    float_curve_001.parent = frame_6
    map_range_005_2.parent = frame_6
    rotate_001.parent = frame_6
    alpha_over_001.parent = frame_6
    scale_001.parent = frame_6
    mix_003_1.parent = frame_6
    translate_001.parent = frame_6
    group_input_004_2.parent = frame_6
    group_input_005_2.parent = frame_6
    reroute_4.parent = frame_004_1

    # Set locations
    group_output_7.location = (3245.559326171875, 68.33099365234375)
    group_input_6.location = (29.246826171875, -358.1910095214844)
    frame_6.location = (-3790.440185546875, 372.072021484375)
    blur_1.location = (3596.069091796875, -390.4656066894531)
    image_info.location = (362.9892578125, -809.0462646484375)
    separate_xyz.location = (2312.99658203125, -744.2481079101562)
    math_6.location = (2576.37548828125, -719.06591796875)
    map_range_5.location = (2982.8486328125, -558.747314453125)
    math_001_4.location = (2744.67138671875, -721.32763671875)
    math_002_4.location = (2785.24560546875, -475.89288330078125)
    math_003_4.location = (2576.5048828125, -626.151611328125)
    math_004_4.location = (2574.5595703125, -674.7127075195312)
    math_005_4.location = (2780.86328125, -520.166748046875)
    group_input_001_3.location = (28.83990478515625, -178.19583129882812)
    mix_4.location = (549.2394409179688, -36.040016174316406)
    frame_001_3.location = (289.08001708984375, -54.168006896972656)
    group_input_002_1.location = (29.113372802734375, -323.6173400878906)
    frame_002_2.location = (174.60000610351562, -388.2480163574219)
    mix_004_1.location = (845.140625, -665.0350341796875)
    group_input_003_2.location = (29.2939453125, -425.71014404296875)
    mix_005_1.location = (1109.406005859375, -350.8150939941406)
    separate_color_2.location = (29.07958984375, -86.57177734375)
    combine_color_2.location = (404.986083984375, -40.616943359375)
    math_007_4.location = (1106.17236328125, -605.486572265625)
    math_008_3.location = (221.014404296875, -35.63916015625)
    mix_006_1.location = (600.7291259765625, -274.8187561035156)
    mix_007.location = (600.44140625, -36.113067626953125)
    mix_008.location = (853.8782958984375, -55.414825439453125)
    math_006_4.location = (426.988525390625, -300.0814208984375)
    mix_009.location = (766.59033203125, -302.32403564453125)
    map_range_002_4.location = (426.64111328125, -36.09075927734375)
    frame_003_1.location = (2479.320068359375, 327.4320068359375)
    frame_004_1.location = (1088.280029296875, 619.7520141601562)
    reroute_010.location = (172.7838134765625, -616.7404174804688)
    reroute_011.location = (165.163330078125, -841.761962890625)
    reroute_012.location = (441.37646484375, -872.9256591796875)
    reroute_013.location = (163.970703125, -299.4451599121094)
    image_coordinates.location = (661.090087890625, -71.76858520507812)
    separate_xyz_004.location = (1460.496337890625, -224.3851318359375)
    math_022.location = (1726.755126953125, -254.1330108642578)
    math_023.location = (1912.4287109375, -278.81060791015625)
    math_024.location = (1725.87841796875, -305.7757873535156)
    math_025.location = (2301.8427734375, -220.87083435058594)
    math_026.location = (2104.318115234375, -282.7101745605469)
    vector_math_006.location = (1256.874267578125, -248.2681427001953)
    vector_math_007.location = (980.812744140625, -36.1051025390625)
    vector_math_008.location = (1261.727783203125, -297.8320007324219)
    math_027.location = (1717.878173828125, -362.7169494628906)
    math_028.location = (1468.681396484375, -388.4939270019531)
    map_range_003_3.location = (1266.83154296875, -403.9979248046875)
    float_curve_1.location = (958.700439453125, -503.5788879394531)
    map_range_004_1.location = (987.56494140625, -236.9508514404297)
    float_curve_001.location = (662.109619140625, -243.48092651367188)
    map_range_005_2.location = (376.754150390625, -504.92584228515625)
    rotate_001.location = (2785.46337890625, -324.0287780761719)
    alpha_over_001.location = (3388.880859375, -265.3239440917969)
    scale_001.location = (2562.90869140625, -247.8860626220703)
    mix_003_1.location = (3180.00634765625, -121.25469970703125)
    translate_001.location = (2983.476806640625, -369.0198669433594)
    group_input_004_2.location = (2322.541015625, -452.4211120605469)
    group_input_005_2.location = (2984.94091796875, -272.3778076171875)
    reroute_4.location = (380.32861328125, -262.09710693359375)
    reroute_001_2.location = (133.40676879882812, 10.141143798828125)

    # Set dimensions
    group_output_7.width, group_output_7.height = 140.0, 100.0
    group_input_6.width, group_input_6.height = 140.0, 100.0
    frame_6.width, frame_6.height = 3765.2001953125, 910.9920654296875
    blur_1.width, blur_1.height = 140.0, 100.0
    image_info.width, image_info.height = 140.0, 100.0
    separate_xyz.width, separate_xyz.height = 140.0, 100.0
    math_6.width, math_6.height = 140.0, 100.0
    map_range_5.width, map_range_5.height = 140.0, 100.0
    math_001_4.width, math_001_4.height = 140.0, 100.0
    math_002_4.width, math_002_4.height = 140.0, 100.0
    math_003_4.width, math_003_4.height = 140.0, 100.0
    math_004_4.width, math_004_4.height = 140.0, 100.0
    math_005_4.width, math_005_4.height = 140.0, 100.0
    group_input_001_3.width, group_input_001_3.height = 140.0, 100.0
    mix_4.width, mix_4.height = 140.0, 100.0
    frame_001_3.width, frame_001_3.height = 718.1600341796875, 277.3919982910156
    group_input_002_1.width, group_input_002_1.height = 140.0, 100.0
    frame_002_2.width, frame_002_2.height = 1022.7200927734375, 514.9920654296875
    mix_004_1.width, mix_004_1.height = 140.0, 100.0
    group_input_003_2.width, group_input_003_2.height = 140.0, 100.0
    mix_005_1.width, mix_005_1.height = 140.0, 100.0
    separate_color_2.width, separate_color_2.height = 140.0, 100.0
    combine_color_2.width, combine_color_2.height = 140.0, 100.0
    math_007_4.width, math_007_4.height = 140.0, 100.0
    math_008_3.width, math_008_3.height = 140.0, 100.0
    mix_006_1.width, mix_006_1.height = 140.0, 100.0
    mix_007.width, mix_007.height = 140.0, 100.0
    mix_008.width, mix_008.height = 140.0, 100.0
    math_006_4.width, math_006_4.height = 140.0, 100.0
    mix_009.width, mix_009.height = 140.0, 100.0
    map_range_002_4.width, map_range_002_4.height = 140.0, 100.0
    frame_003_1.width, frame_003_1.height = 574.159912109375, 275.23199462890625
    frame_004_1.width, frame_004_1.height = 1278.320068359375, 906.9456787109375
    reroute_010.width, reroute_010.height = 13.5, 100.0
    reroute_011.width, reroute_011.height = 13.5, 100.0
    reroute_012.width, reroute_012.height = 13.5, 100.0
    reroute_013.width, reroute_013.height = 13.5, 100.0
    image_coordinates.width, image_coordinates.height = 140.0, 100.0
    separate_xyz_004.width, separate_xyz_004.height = 140.0, 100.0
    math_022.width, math_022.height = 140.0, 100.0
    math_023.width, math_023.height = 140.0, 100.0
    math_024.width, math_024.height = 140.0, 100.0
    math_025.width, math_025.height = 140.0, 100.0
    math_026.width, math_026.height = 140.0, 100.0
    vector_math_006.width, vector_math_006.height = 140.0, 100.0
    vector_math_007.width, vector_math_007.height = 140.0, 100.0
    vector_math_008.width, vector_math_008.height = 140.0, 100.0
    math_027.width, math_027.height = 140.0, 100.0
    math_028.width, math_028.height = 140.0, 100.0
    map_range_003_3.width, map_range_003_3.height = 140.0, 100.0
    float_curve_1.width, float_curve_1.height = 240.0, 100.0
    map_range_004_1.width, map_range_004_1.height = 140.0, 100.0
    float_curve_001.width, float_curve_001.height = 240.0, 100.0
    map_range_005_2.width, map_range_005_2.height = 140.0, 100.0
    rotate_001.width, rotate_001.height = 140.0, 100.0
    alpha_over_001.width, alpha_over_001.height = 140.0, 100.0
    scale_001.width, scale_001.height = 140.0, 100.0
    mix_003_1.width, mix_003_1.height = 140.0, 100.0
    translate_001.width, translate_001.height = 140.0, 100.0
    group_input_004_2.width, group_input_004_2.height = 140.0, 100.0
    group_input_005_2.width, group_input_005_2.height = 140.0, 100.0
    reroute_4.width, reroute_4.height = 13.5, 100.0
    reroute_001_2.width, reroute_001_2.height = 13.5, 100.0

    # Initialize _rr_vignette links

    # group_input_6.Image -> image_info.Image
    _rr_vignette.links.new(group_input_6.outputs[0], image_info.inputs[0])
    # image_info.Dimensions -> separate_xyz.Vector
    _rr_vignette.links.new(image_info.outputs[0], separate_xyz.inputs[0])
    # separate_xyz.X -> math_6.Value
    _rr_vignette.links.new(separate_xyz.outputs[0], math_6.inputs[0])
    # separate_xyz.Y -> math_6.Value
    _rr_vignette.links.new(separate_xyz.outputs[1], math_6.inputs[1])
    # math_6.Value -> math_001_4.Value
    _rr_vignette.links.new(math_6.outputs[0], math_001_4.inputs[0])
    # math_001_4.Value -> map_range_5.To Max
    _rr_vignette.links.new(math_001_4.outputs[0], map_range_5.inputs[4])
    # map_range_5.Result -> blur_1.Size
    _rr_vignette.links.new(map_range_5.outputs[0], blur_1.inputs[1])
    # group_input_004_2.Shift X -> math_002_4.Value
    _rr_vignette.links.new(group_input_004_2.outputs[10], math_002_4.inputs[0])
    # math_003_4.Value -> math_002_4.Value
    _rr_vignette.links.new(math_003_4.outputs[0], math_002_4.inputs[1])
    # separate_xyz.X -> math_003_4.Value
    _rr_vignette.links.new(separate_xyz.outputs[0], math_003_4.inputs[0])
    # separate_xyz.Y -> math_004_4.Value
    _rr_vignette.links.new(separate_xyz.outputs[1], math_004_4.inputs[0])
    # group_input_004_2.Shift Y -> math_005_4.Value
    _rr_vignette.links.new(group_input_004_2.outputs[11], math_005_4.inputs[0])
    # math_004_4.Value -> math_005_4.Value
    _rr_vignette.links.new(math_004_4.outputs[0], math_005_4.inputs[1])
    # group_input_001_3.Image -> mix_4.A
    _rr_vignette.links.new(group_input_001_3.outputs[0], mix_4.inputs[6])
    # reroute_001_2.Output -> mix_4.Factor
    _rr_vignette.links.new(reroute_001_2.outputs[0], mix_4.inputs[0])
    # group_input_001_3.Color -> mix_4.B
    _rr_vignette.links.new(group_input_001_3.outputs[2], mix_4.inputs[7])
    # reroute_011.Output -> mix_004_1.A
    _rr_vignette.links.new(reroute_011.outputs[0], mix_004_1.inputs[6])
    # group_input_003_2.Image -> mix_005_1.A
    _rr_vignette.links.new(group_input_003_2.outputs[0], mix_005_1.inputs[6])
    # mix_004_1.Result -> mix_005_1.B
    _rr_vignette.links.new(mix_004_1.outputs[2], mix_005_1.inputs[7])
    # separate_color_2.Red -> combine_color_2.Red
    _rr_vignette.links.new(separate_color_2.outputs[0], combine_color_2.inputs[0])
    # separate_color_2.Alpha -> combine_color_2.Alpha
    _rr_vignette.links.new(separate_color_2.outputs[3], combine_color_2.inputs[3])
    # separate_color_2.Blue -> combine_color_2.Blue
    _rr_vignette.links.new(separate_color_2.outputs[2], combine_color_2.inputs[2])
    # reroute_010.Output -> math_007_4.Value
    _rr_vignette.links.new(reroute_010.outputs[0], math_007_4.inputs[1])
    # math_007_4.Value -> group_output_7.Mask
    _rr_vignette.links.new(math_007_4.outputs[0], group_output_7.inputs[1])
    # separate_color_2.Green -> math_008_3.Value
    _rr_vignette.links.new(separate_color_2.outputs[1], math_008_3.inputs[0])
    # math_008_3.Value -> combine_color_2.Green
    _rr_vignette.links.new(math_008_3.outputs[0], combine_color_2.inputs[1])
    # mix_005_1.Result -> separate_color_2.Image
    _rr_vignette.links.new(mix_005_1.outputs[2], separate_color_2.inputs[0])
    # group_input_002_1.Image -> mix_006_1.A
    _rr_vignette.links.new(group_input_002_1.outputs[0], mix_006_1.inputs[6])
    # reroute_013.Output -> mix_006_1.Factor
    _rr_vignette.links.new(reroute_013.outputs[0], mix_006_1.inputs[0])
    # group_input_002_1.Color -> mix_006_1.B
    _rr_vignette.links.new(group_input_002_1.outputs[2], mix_006_1.inputs[7])
    # group_input_002_1.Image -> mix_007.A
    _rr_vignette.links.new(group_input_002_1.outputs[0], mix_007.inputs[6])
    # reroute_013.Output -> mix_007.Factor
    _rr_vignette.links.new(reroute_013.outputs[0], mix_007.inputs[0])
    # group_input_002_1.Color -> mix_007.B
    _rr_vignette.links.new(group_input_002_1.outputs[2], mix_007.inputs[7])
    # reroute_012.Output -> mix_004_1.B
    _rr_vignette.links.new(reroute_012.outputs[0], mix_004_1.inputs[7])
    # mix_006_1.Result -> mix_008.B
    _rr_vignette.links.new(mix_006_1.outputs[2], mix_008.inputs[7])
    # mix_007.Result -> mix_008.A
    _rr_vignette.links.new(mix_007.outputs[2], mix_008.inputs[6])
    # group_input_003_2.Factor -> math_007_4.Value
    _rr_vignette.links.new(group_input_003_2.outputs[1], math_007_4.inputs[0])
    # group_input_003_2.Factor -> mix_009.B
    _rr_vignette.links.new(group_input_003_2.outputs[1], mix_009.inputs[3])
    # mix_009.Result -> mix_005_1.Factor
    _rr_vignette.links.new(mix_009.outputs[0], mix_005_1.inputs[0])
    # group_input_003_2.Factor -> math_006_4.Value
    _rr_vignette.links.new(group_input_003_2.outputs[1], math_006_4.inputs[0])
    # group_input_003_2.Image -> math_006_4.Value
    _rr_vignette.links.new(group_input_003_2.outputs[0], math_006_4.inputs[1])
    # math_006_4.Value -> mix_009.A
    _rr_vignette.links.new(math_006_4.outputs[0], mix_009.inputs[2])
    # reroute_001_2.Output -> reroute_010.Input
    _rr_vignette.links.new(reroute_001_2.outputs[0], reroute_010.inputs[0])
    # mix_4.Result -> reroute_011.Input
    _rr_vignette.links.new(mix_4.outputs[2], reroute_011.inputs[0])
    # mix_008.Result -> reroute_012.Input
    _rr_vignette.links.new(mix_008.outputs[2], reroute_012.inputs[0])
    # reroute_001_2.Output -> reroute_013.Input
    _rr_vignette.links.new(reroute_001_2.outputs[0], reroute_013.inputs[0])
    # group_input_002_1.Color -> mix_008.Factor
    _rr_vignette.links.new(group_input_002_1.outputs[2], mix_008.inputs[0])
    # group_input_6.Image -> image_coordinates.Image
    _rr_vignette.links.new(group_input_6.outputs[0], image_coordinates.inputs[0])
    # separate_xyz_004.X -> math_022.Value
    _rr_vignette.links.new(separate_xyz_004.outputs[0], math_022.inputs[0])
    # math_022.Value -> math_023.Value
    _rr_vignette.links.new(math_022.outputs[0], math_023.inputs[0])
    # math_028.Value -> math_024.Value
    _rr_vignette.links.new(math_028.outputs[0], math_024.inputs[1])
    # separate_xyz_004.Y -> math_024.Value
    _rr_vignette.links.new(separate_xyz_004.outputs[1], math_024.inputs[0])
    # math_024.Value -> math_023.Value
    _rr_vignette.links.new(math_024.outputs[0], math_023.inputs[1])
    # math_026.Value -> math_025.Value
    _rr_vignette.links.new(math_026.outputs[0], math_025.inputs[0])
    # math_023.Value -> math_026.Value
    _rr_vignette.links.new(math_023.outputs[0], math_026.inputs[0])
    # math_028.Value -> math_027.Value
    _rr_vignette.links.new(math_028.outputs[0], math_027.inputs[0])
    # math_027.Value -> math_026.Value
    _rr_vignette.links.new(math_027.outputs[0], math_026.inputs[1])
    # map_range_003_3.Result -> math_028.Value
    _rr_vignette.links.new(map_range_003_3.outputs[0], math_028.inputs[0])
    # math_028.Value -> math_022.Value
    _rr_vignette.links.new(math_028.outputs[0], math_022.inputs[1])
    # map_range_005_2.Result -> float_curve_1.Value
    _rr_vignette.links.new(map_range_005_2.outputs[0], float_curve_1.inputs[1])
    # float_curve_1.Value -> map_range_003_3.Value
    _rr_vignette.links.new(float_curve_1.outputs[0], map_range_003_3.inputs[0])
    # map_range_004_1.Result -> vector_math_006.Scale
    _rr_vignette.links.new(map_range_004_1.outputs[0], vector_math_006.inputs[3])
    # float_curve_001.Value -> map_range_004_1.Value
    _rr_vignette.links.new(float_curve_001.outputs[0], map_range_004_1.inputs[0])
    # map_range_005_2.Result -> float_curve_001.Value
    _rr_vignette.links.new(map_range_005_2.outputs[0], float_curve_001.inputs[1])
    # group_input_6.Roundness -> map_range_005_2.Value
    _rr_vignette.links.new(group_input_6.outputs[5], map_range_005_2.inputs[0])
    # vector_math_006.Vector -> vector_math_008.Vector
    _rr_vignette.links.new(vector_math_006.outputs[0], vector_math_008.inputs[0])
    # vector_math_007.Vector -> vector_math_006.Vector
    _rr_vignette.links.new(vector_math_007.outputs[0], vector_math_006.inputs[0])
    # vector_math_008.Vector -> separate_xyz_004.Vector
    _rr_vignette.links.new(vector_math_008.outputs[0], separate_xyz_004.inputs[0])
    # math_025.Value -> scale_001.Image
    _rr_vignette.links.new(math_025.outputs[0], scale_001.inputs[0])
    # mix_003_1.Result -> alpha_over_001.Image
    _rr_vignette.links.new(mix_003_1.outputs[2], alpha_over_001.inputs[1])
    # image_coordinates.Normalized -> vector_math_007.Vector
    _rr_vignette.links.new(image_coordinates.outputs[1], vector_math_007.inputs[0])
    # scale_001.Image -> rotate_001.Image
    _rr_vignette.links.new(scale_001.outputs[0], rotate_001.inputs[0])
    # rotate_001.Image -> translate_001.Image
    _rr_vignette.links.new(rotate_001.outputs[0], translate_001.inputs[0])
    # math_002_4.Value -> translate_001.X
    _rr_vignette.links.new(math_002_4.outputs[0], translate_001.inputs[1])
    # math_005_4.Value -> translate_001.Y
    _rr_vignette.links.new(math_005_4.outputs[0], translate_001.inputs[2])
    # group_input_003_2.Linear Blending -> mix_004_1.Factor
    _rr_vignette.links.new(group_input_003_2.outputs[4], mix_004_1.inputs[0])
    # combine_color_2.Image -> group_output_7.Image
    _rr_vignette.links.new(combine_color_2.outputs[0], group_output_7.inputs[0])
    # group_input_003_2.Highlights -> map_range_002_4.Value
    _rr_vignette.links.new(group_input_003_2.outputs[3], map_range_002_4.inputs[0])
    # group_input_004_2.Scale X -> scale_001.X
    _rr_vignette.links.new(group_input_004_2.outputs[7], scale_001.inputs[1])
    # group_input_004_2.Scale Y -> scale_001.Y
    _rr_vignette.links.new(group_input_004_2.outputs[8], scale_001.inputs[2])
    # group_input_004_2.Feathering -> map_range_5.Value
    _rr_vignette.links.new(group_input_004_2.outputs[6], map_range_5.inputs[0])
    # group_input_004_2.Rotation -> rotate_001.Degr
    _rr_vignette.links.new(group_input_004_2.outputs[9], rotate_001.inputs[1])
    # group_input_005_2.Image -> mix_003_1.A
    _rr_vignette.links.new(group_input_005_2.outputs[0], mix_003_1.inputs[6])
    # map_range_002_4.Result -> mix_009.Factor
    _rr_vignette.links.new(map_range_002_4.outputs[0], mix_009.inputs[0])
    # group_input_003_2.Color -> reroute_4.Input
    _rr_vignette.links.new(group_input_003_2.outputs[2], reroute_4.inputs[0])
    # reroute_4.Output -> map_range_002_4.To Max
    _rr_vignette.links.new(reroute_4.outputs[0], map_range_002_4.inputs[4])
    # blur_1.Image -> reroute_001_2.Input
    _rr_vignette.links.new(blur_1.outputs[0], reroute_001_2.inputs[0])
    # translate_001.Image -> alpha_over_001.Image
    _rr_vignette.links.new(translate_001.outputs[0], alpha_over_001.inputs[2])
    # alpha_over_001.Image -> blur_1.Image
    _rr_vignette.links.new(alpha_over_001.outputs[0], blur_1.inputs[0])

    return _rr_vignette


_rr_vignette = _rr_vignette_node_group()

def _rr_mask_value_node_group():
    """Initialize .RR_mask_value node group"""
    _rr_mask_value = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_mask_value")

    _rr_mask_value.color_tag = 'NONE'
    _rr_mask_value.description = ""
    _rr_mask_value.default_group_node_width = 140
    # _rr_mask_value interface

    # Socket Mask
    mask_socket_1 = _rr_mask_value.interface.new_socket(name="Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    mask_socket_1.default_value = 0.0
    mask_socket_1.min_value = -3.4028234663852886e+38
    mask_socket_1.max_value = 3.4028234663852886e+38
    mask_socket_1.subtype = 'NONE'
    mask_socket_1.attribute_domain = 'POINT'
    mask_socket_1.default_input = 'VALUE'
    mask_socket_1.structure_type = 'AUTO'

    # Socket Value
    value_socket = _rr_mask_value.interface.new_socket(name="Value", in_out='OUTPUT', socket_type='NodeSocketFloat')
    value_socket.default_value = 0.0
    value_socket.min_value = -3.4028234663852886e+38
    value_socket.max_value = 3.4028234663852886e+38
    value_socket.subtype = 'NONE'
    value_socket.attribute_domain = 'POINT'
    value_socket.default_input = 'VALUE'
    value_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_14 = _rr_mask_value.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketFloat')
    image_socket_14.default_value = 0.5
    image_socket_14.min_value = -10000.0
    image_socket_14.max_value = 10000.0
    image_socket_14.subtype = 'NONE'
    image_socket_14.attribute_domain = 'POINT'
    image_socket_14.default_input = 'VALUE'
    image_socket_14.structure_type = 'AUTO'

    # Socket Mask
    mask_socket_2 = _rr_mask_value.interface.new_socket(name="Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    mask_socket_2.default_value = 1.0
    mask_socket_2.min_value = 0.0
    mask_socket_2.max_value = 1.0
    mask_socket_2.subtype = 'FACTOR'
    mask_socket_2.attribute_domain = 'POINT'
    mask_socket_2.default_input = 'VALUE'
    mask_socket_2.structure_type = 'AUTO'

    # Socket Value
    value_socket_1 = _rr_mask_value.interface.new_socket(name="Value", in_out='INPUT', socket_type='NodeSocketFloat')
    value_socket_1.default_value = 0.5
    value_socket_1.min_value = -10000.0
    value_socket_1.max_value = 10000.0
    value_socket_1.subtype = 'NONE'
    value_socket_1.attribute_domain = 'POINT'
    value_socket_1.default_input = 'VALUE'
    value_socket_1.structure_type = 'AUTO'

    # Socket Range
    range_socket = _rr_mask_value.interface.new_socket(name="Range", in_out='INPUT', socket_type='NodeSocketFloat')
    range_socket.default_value = 0.0
    range_socket.min_value = -3.4028234663852886e+38
    range_socket.max_value = 3.4028234663852886e+38
    range_socket.subtype = 'NONE'
    range_socket.attribute_domain = 'POINT'
    range_socket.default_input = 'VALUE'
    range_socket.structure_type = 'AUTO'

    # Socket Smoothing
    smoothing_socket = _rr_mask_value.interface.new_socket(name="Smoothing", in_out='INPUT', socket_type='NodeSocketFloat')
    smoothing_socket.default_value = 0.0
    smoothing_socket.min_value = 0.0
    smoothing_socket.max_value = 1.0
    smoothing_socket.subtype = 'FACTOR'
    smoothing_socket.attribute_domain = 'POINT'
    smoothing_socket.default_input = 'VALUE'
    smoothing_socket.structure_type = 'AUTO'

    # Initialize _rr_mask_value nodes

    # Node Group Output
    group_output_8 = _rr_mask_value.nodes.new("NodeGroupOutput")
    group_output_8.name = "Group Output"
    group_output_8.is_active_output = True

    # Node Group Input
    group_input_7 = _rr_mask_value.nodes.new("NodeGroupInput")
    group_input_7.name = "Group Input"

    # Node Math
    math_7 = _rr_mask_value.nodes.new("ShaderNodeMath")
    math_7.name = "Math"
    math_7.operation = 'SUBTRACT'
    math_7.use_clamp = False

    # Node Map Range
    map_range_6 = _rr_mask_value.nodes.new("ShaderNodeMapRange")
    map_range_6.name = "Map Range"
    map_range_6.clamp = False
    map_range_6.data_type = 'FLOAT'
    map_range_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_6.inputs[1].default_value = 0.0
    # To Min
    map_range_6.inputs[3].default_value = 1.0
    # To Max
    map_range_6.inputs[4].default_value = 0.0

    # Node Math.002
    math_002_5 = _rr_mask_value.nodes.new("ShaderNodeMath")
    math_002_5.name = "Math.002"
    math_002_5.operation = 'MULTIPLY'
    math_002_5.use_clamp = False

    # Node Map Range.001
    map_range_001_5 = _rr_mask_value.nodes.new("ShaderNodeMapRange")
    map_range_001_5.name = "Map Range.001"
    map_range_001_5.clamp = False
    map_range_001_5.data_type = 'FLOAT'
    map_range_001_5.interpolation_type = 'SMOOTHERSTEP'
    # From Min
    map_range_001_5.inputs[1].default_value = 0.0
    # To Min
    map_range_001_5.inputs[3].default_value = 1.0
    # To Max
    map_range_001_5.inputs[4].default_value = 0.0

    # Node Mix
    mix_5 = _rr_mask_value.nodes.new("ShaderNodeMix")
    mix_5.name = "Mix"
    mix_5.blend_type = 'MIX'
    mix_5.clamp_factor = True
    mix_5.clamp_result = False
    mix_5.data_type = 'FLOAT'
    mix_5.factor_mode = 'UNIFORM'

    # Node Math.003
    math_003_5 = _rr_mask_value.nodes.new("ShaderNodeMath")
    math_003_5.name = "Math.003"
    math_003_5.operation = 'PINGPONG'
    math_003_5.use_clamp = False
    # Value_001
    math_003_5.inputs[1].default_value = 0.5

    # Node Math.004
    math_004_5 = _rr_mask_value.nodes.new("ShaderNodeMath")
    math_004_5.name = "Math.004"
    math_004_5.operation = 'MULTIPLY'
    math_004_5.use_clamp = True

    # Set locations
    group_output_8.location = (768.8401489257812, 150.4246063232422)
    group_input_7.location = (-679.3248901367188, 128.98867797851562)
    math_7.location = (-438.73095703125, 211.4145965576172)
    map_range_6.location = (42.695682525634766, 203.0795440673828)
    math_002_5.location = (468.756591796875, -2.2682812213897705)
    map_range_001_5.location = (42.694541931152344, -37.65199279785156)
    mix_5.location = (266.7018127441406, 93.60157775878906)
    math_003_5.location = (-252.74314880371094, 214.110595703125)
    math_004_5.location = (474.42877197265625, 243.15130615234375)

    # Set dimensions
    group_output_8.width, group_output_8.height = 140.0, 100.0
    group_input_7.width, group_input_7.height = 140.0, 100.0
    math_7.width, math_7.height = 140.0, 100.0
    map_range_6.width, map_range_6.height = 140.0, 100.0
    math_002_5.width, math_002_5.height = 140.0, 100.0
    map_range_001_5.width, map_range_001_5.height = 140.0, 100.0
    mix_5.width, mix_5.height = 140.0, 100.0
    math_003_5.width, math_003_5.height = 140.0, 100.0
    math_004_5.width, math_004_5.height = 140.0, 100.0

    # Initialize _rr_mask_value links

    # math_003_5.Value -> map_range_6.Value
    _rr_mask_value.links.new(math_003_5.outputs[0], map_range_6.inputs[0])
    # group_input_7.Range -> map_range_6.From Max
    _rr_mask_value.links.new(group_input_7.outputs[3], map_range_6.inputs[2])
    # group_input_7.Image -> math_7.Value
    _rr_mask_value.links.new(group_input_7.outputs[0], math_7.inputs[0])
    # group_input_7.Value -> math_7.Value
    _rr_mask_value.links.new(group_input_7.outputs[2], math_7.inputs[1])
    # mix_5.Result -> math_002_5.Value
    _rr_mask_value.links.new(mix_5.outputs[0], math_002_5.inputs[0])
    # group_input_7.Range -> math_002_5.Value
    _rr_mask_value.links.new(group_input_7.outputs[3], math_002_5.inputs[1])
    # math_002_5.Value -> group_output_8.Value
    _rr_mask_value.links.new(math_002_5.outputs[0], group_output_8.inputs[1])
    # math_003_5.Value -> map_range_001_5.Value
    _rr_mask_value.links.new(math_003_5.outputs[0], map_range_001_5.inputs[0])
    # group_input_7.Range -> map_range_001_5.From Max
    _rr_mask_value.links.new(group_input_7.outputs[3], map_range_001_5.inputs[2])
    # map_range_6.Result -> mix_5.A
    _rr_mask_value.links.new(map_range_6.outputs[0], mix_5.inputs[2])
    # map_range_001_5.Result -> mix_5.B
    _rr_mask_value.links.new(map_range_001_5.outputs[0], mix_5.inputs[3])
    # group_input_7.Smoothing -> mix_5.Factor
    _rr_mask_value.links.new(group_input_7.outputs[4], mix_5.inputs[0])
    # math_004_5.Value -> group_output_8.Mask
    _rr_mask_value.links.new(math_004_5.outputs[0], group_output_8.inputs[0])
    # math_7.Value -> math_003_5.Value
    _rr_mask_value.links.new(math_7.outputs[0], math_003_5.inputs[0])
    # mix_5.Result -> math_004_5.Value
    _rr_mask_value.links.new(mix_5.outputs[0], math_004_5.inputs[0])
    # group_input_7.Mask -> math_004_5.Value
    _rr_mask_value.links.new(group_input_7.outputs[1], math_004_5.inputs[1])

    return _rr_mask_value


_rr_mask_value = _rr_mask_value_node_group()

def _rr_srgb_to_lab_node_group():
    """Initialize .RR_sRGB_to_LAB node group"""
    _rr_srgb_to_lab = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_sRGB_to_LAB")

    _rr_srgb_to_lab.color_tag = 'NONE'
    _rr_srgb_to_lab.description = ""
    _rr_srgb_to_lab.default_group_node_width = 140
    # _rr_srgb_to_lab interface

    # Socket L
    l_socket = _rr_srgb_to_lab.interface.new_socket(name="L", in_out='OUTPUT', socket_type='NodeSocketFloat')
    l_socket.default_value = 0.0
    l_socket.min_value = -3.4028234663852886e+38
    l_socket.max_value = 3.4028234663852886e+38
    l_socket.subtype = 'NONE'
    l_socket.attribute_domain = 'POINT'
    l_socket.default_input = 'VALUE'
    l_socket.structure_type = 'AUTO'

    # Socket A
    a_socket = _rr_srgb_to_lab.interface.new_socket(name="A", in_out='OUTPUT', socket_type='NodeSocketFloat')
    a_socket.default_value = 0.0
    a_socket.min_value = -3.4028234663852886e+38
    a_socket.max_value = 3.4028234663852886e+38
    a_socket.subtype = 'NONE'
    a_socket.attribute_domain = 'POINT'
    a_socket.default_input = 'VALUE'
    a_socket.structure_type = 'AUTO'

    # Socket B
    b_socket = _rr_srgb_to_lab.interface.new_socket(name="B", in_out='OUTPUT', socket_type='NodeSocketFloat')
    b_socket.default_value = 0.0
    b_socket.min_value = -3.4028234663852886e+38
    b_socket.max_value = 3.4028234663852886e+38
    b_socket.subtype = 'NONE'
    b_socket.attribute_domain = 'POINT'
    b_socket.default_input = 'VALUE'
    b_socket.structure_type = 'AUTO'

    # Socket Alpha
    alpha_socket = _rr_srgb_to_lab.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
    alpha_socket.default_value = 0.0
    alpha_socket.min_value = -3.4028234663852886e+38
    alpha_socket.max_value = 3.4028234663852886e+38
    alpha_socket.subtype = 'NONE'
    alpha_socket.attribute_domain = 'POINT'
    alpha_socket.default_input = 'VALUE'
    alpha_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_15 = _rr_srgb_to_lab.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_15.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_15.attribute_domain = 'POINT'
    image_socket_15.default_input = 'VALUE'
    image_socket_15.structure_type = 'AUTO'

    # Initialize _rr_srgb_to_lab nodes

    # Node Frame
    frame_7 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_7.label = "l"
    frame_7.name = "Frame"
    frame_7.label_size = 20
    frame_7.shrink = True

    # Node Frame.001
    frame_001_4 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_001_4.label = "m"
    frame_001_4.name = "Frame.001"
    frame_001_4.label_size = 20
    frame_001_4.shrink = True

    # Node Frame.002
    frame_002_3 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_002_3.label = "s"
    frame_002_3.name = "Frame.002"
    frame_002_3.label_size = 20
    frame_002_3.shrink = True

    # Node Frame.003
    frame_003_2 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_003_2.label = "L"
    frame_003_2.name = "Frame.003"
    frame_003_2.label_size = 20
    frame_003_2.shrink = True

    # Node Frame.004
    frame_004_2 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_004_2.label = "A"
    frame_004_2.name = "Frame.004"
    frame_004_2.label_size = 20
    frame_004_2.shrink = True

    # Node Frame.005
    frame_005_1 = _rr_srgb_to_lab.nodes.new("NodeFrame")
    frame_005_1.label = "B"
    frame_005_1.name = "Frame.005"
    frame_005_1.label_size = 20
    frame_005_1.shrink = True

    # Node Group Input
    group_input_8 = _rr_srgb_to_lab.nodes.new("NodeGroupInput")
    group_input_8.name = "Group Input"

    # Node Math
    math_8 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_8.name = "Math"
    math_8.operation = 'MULTIPLY'
    math_8.use_clamp = False
    # Value_001
    math_8.inputs[1].default_value = 0.4122214615345001

    # Node Math.001
    math_001_5 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_001_5.name = "Math.001"
    math_001_5.operation = 'MULTIPLY'
    math_001_5.use_clamp = False
    # Value_001
    math_001_5.inputs[1].default_value = 0.5363325476646423

    # Node Math.003
    math_003_6 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_003_6.name = "Math.003"
    math_003_6.hide = True
    math_003_6.operation = 'ADD'
    math_003_6.use_clamp = False

    # Node Math.002
    math_002_6 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_002_6.name = "Math.002"
    math_002_6.operation = 'MULTIPLY'
    math_002_6.use_clamp = False
    # Value_001
    math_002_6.inputs[1].default_value = 0.05144599452614784

    # Node Math.004
    math_004_6 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_004_6.name = "Math.004"
    math_004_6.hide = True
    math_004_6.operation = 'ADD'
    math_004_6.use_clamp = False

    # Node Math.005
    math_005_5 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_005_5.name = "Math.005"
    math_005_5.operation = 'MULTIPLY'
    math_005_5.use_clamp = False
    # Value_001
    math_005_5.inputs[1].default_value = 0.21190349757671356

    # Node Math.006
    math_006_5 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_006_5.name = "Math.006"
    math_006_5.operation = 'MULTIPLY'
    math_006_5.use_clamp = False
    # Value_001
    math_006_5.inputs[1].default_value = 0.6806995272636414

    # Node Math.007
    math_007_5 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_007_5.name = "Math.007"
    math_007_5.hide = True
    math_007_5.operation = 'ADD'
    math_007_5.use_clamp = False

    # Node Math.008
    math_008_4 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_008_4.name = "Math.008"
    math_008_4.operation = 'MULTIPLY'
    math_008_4.use_clamp = False
    # Value_001
    math_008_4.inputs[1].default_value = 0.10739696025848389

    # Node Math.009
    math_009_2 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_009_2.name = "Math.009"
    math_009_2.hide = True
    math_009_2.operation = 'ADD'
    math_009_2.use_clamp = False

    # Node Math.010
    math_010_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_010_1.name = "Math.010"
    math_010_1.operation = 'MULTIPLY'
    math_010_1.use_clamp = False
    # Value_001
    math_010_1.inputs[1].default_value = 0.08830246329307556

    # Node Math.011
    math_011_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_011_1.name = "Math.011"
    math_011_1.operation = 'MULTIPLY'
    math_011_1.use_clamp = False
    # Value_001
    math_011_1.inputs[1].default_value = 0.2817188501358032

    # Node Math.012
    math_012 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_012.name = "Math.012"
    math_012.hide = True
    math_012.operation = 'ADD'
    math_012.use_clamp = False

    # Node Math.013
    math_013 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_013.name = "Math.013"
    math_013.operation = 'MULTIPLY'
    math_013.use_clamp = False
    # Value_001
    math_013.inputs[1].default_value = 0.6299787163734436

    # Node Math.014
    math_014 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_014.name = "Math.014"
    math_014.hide = True
    math_014.operation = 'ADD'
    math_014.use_clamp = False

    # Node Math.015
    math_015 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_015.label = "CBRT"
    math_015.name = "Math.015"
    math_015.operation = 'POWER'
    math_015.use_clamp = False
    # Value_001
    math_015.inputs[1].default_value = 0.3333333432674408

    # Node Math.017
    math_017 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_017.label = "CBRT"
    math_017.name = "Math.017"
    math_017.operation = 'POWER'
    math_017.use_clamp = False
    # Value_001
    math_017.inputs[1].default_value = 0.3333333432674408

    # Node Math.016
    math_016 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_016.label = "CBRT"
    math_016.name = "Math.016"
    math_016.operation = 'POWER'
    math_016.use_clamp = False
    # Value_001
    math_016.inputs[1].default_value = 0.3333333432674408

    # Node Math.018
    math_018 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_018.name = "Math.018"
    math_018.operation = 'MULTIPLY'
    math_018.use_clamp = False
    # Value_001
    math_018.inputs[1].default_value = 0.21045425534248352

    # Node Math.020
    math_020 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_020.name = "Math.020"
    math_020.operation = 'MULTIPLY'
    math_020.use_clamp = False
    # Value_001
    math_020.inputs[1].default_value = 0.7936177849769592

    # Node Math.022
    math_022_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_022_1.name = "Math.022"
    math_022_1.operation = 'MULTIPLY'
    math_022_1.use_clamp = False
    # Value_001
    math_022_1.inputs[1].default_value = 0.004072046838700771

    # Node Math.021
    math_021 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_021.name = "Math.021"
    math_021.hide = True
    math_021.operation = 'SUBTRACT'
    math_021.use_clamp = False

    # Node Math.019
    math_019 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_019.name = "Math.019"
    math_019.hide = True
    math_019.operation = 'ADD'
    math_019.use_clamp = False

    # Node Math.023
    math_023_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_023_1.name = "Math.023"
    math_023_1.operation = 'MULTIPLY'
    math_023_1.use_clamp = False
    # Value_001
    math_023_1.inputs[1].default_value = 1.9779984951019287

    # Node Math.025
    math_025_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_025_1.name = "Math.025"
    math_025_1.operation = 'MULTIPLY'
    math_025_1.use_clamp = False
    # Value_001
    math_025_1.inputs[1].default_value = 0.4505937099456787

    # Node Math.028
    math_028_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_028_1.name = "Math.028"
    math_028_1.operation = 'MULTIPLY'
    math_028_1.use_clamp = False
    # Value_001
    math_028_1.inputs[1].default_value = 0.025904037058353424

    # Node Math.029
    math_029 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_029.name = "Math.029"
    math_029.operation = 'MULTIPLY'
    math_029.use_clamp = False
    # Value_001
    math_029.inputs[1].default_value = 0.7827717661857605

    # Node Math.030
    math_030 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_030.name = "Math.030"
    math_030.operation = 'MULTIPLY'
    math_030.use_clamp = False
    # Value_001
    math_030.inputs[1].default_value = 0.8086757659912109

    # Node Math.031
    math_031 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_031.name = "Math.031"
    math_031.hide = True
    math_031.operation = 'SUBTRACT'
    math_031.use_clamp = False

    # Node Math.032
    math_032 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_032.name = "Math.032"
    math_032.hide = True
    math_032.operation = 'ADD'
    math_032.use_clamp = False

    # Node Group Output
    group_output_9 = _rr_srgb_to_lab.nodes.new("NodeGroupOutput")
    group_output_9.name = "Group Output"
    group_output_9.is_active_output = True

    # Node Math.027
    math_027_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_027_1.name = "Math.027"
    math_027_1.hide = True
    math_027_1.operation = 'SUBTRACT'
    math_027_1.use_clamp = False

    # Node Math.026
    math_026_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_026_1.name = "Math.026"
    math_026_1.hide = True
    math_026_1.operation = 'ADD'
    math_026_1.use_clamp = False

    # Node Math.024
    math_024_1 = _rr_srgb_to_lab.nodes.new("ShaderNodeMath")
    math_024_1.name = "Math.024"
    math_024_1.operation = 'MULTIPLY'
    math_024_1.use_clamp = False
    # Value_001
    math_024_1.inputs[1].default_value = 2.4285922050476074

    # Node Separate Color.001
    separate_color_001_2 = _rr_srgb_to_lab.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_2.name = "Separate Color.001"
    separate_color_001_2.mode = 'RGB'
    separate_color_001_2.ycc_mode = 'ITUBT709'

    # Node Reroute.001
    reroute_001_3 = _rr_srgb_to_lab.nodes.new("NodeReroute")
    reroute_001_3.name = "Reroute.001"
    reroute_001_3.socket_idname = "NodeSocketFloat"
    # Node Reroute
    reroute_5 = _rr_srgb_to_lab.nodes.new("NodeReroute")
    reroute_5.name = "Reroute"
    reroute_5.socket_idname = "NodeSocketFloat"
    # Set parents
    math_8.parent = frame_7
    math_001_5.parent = frame_7
    math_003_6.parent = frame_7
    math_002_6.parent = frame_7
    math_004_6.parent = frame_7
    math_005_5.parent = frame_001_4
    math_006_5.parent = frame_001_4
    math_007_5.parent = frame_001_4
    math_008_4.parent = frame_001_4
    math_009_2.parent = frame_001_4
    math_010_1.parent = frame_002_3
    math_011_1.parent = frame_002_3
    math_012.parent = frame_002_3
    math_013.parent = frame_002_3
    math_014.parent = frame_002_3
    math_015.parent = frame_7
    math_017.parent = frame_002_3
    math_016.parent = frame_001_4
    math_018.parent = frame_003_2
    math_020.parent = frame_003_2
    math_022_1.parent = frame_003_2
    math_021.parent = frame_003_2
    math_019.parent = frame_003_2
    math_023_1.parent = frame_004_2
    math_025_1.parent = frame_004_2
    math_028_1.parent = frame_005_1
    math_029.parent = frame_005_1
    math_030.parent = frame_005_1
    math_031.parent = frame_005_1
    math_032.parent = frame_005_1
    math_027_1.parent = frame_004_2
    math_026_1.parent = frame_004_2
    math_024_1.parent = frame_004_2

    # Set locations
    frame_7.location = (-606.6000366210938, 742.8720092773438)
    frame_001_4.location = (-603.7200317382812, 182.71200561523438)
    frame_002_3.location = (-604.4400024414062, -376.0080261230469)
    frame_003_2.location = (593.6400146484375, 731.35205078125)
    frame_004_2.location = (587.8800048828125, 174.07200622558594)
    frame_005_1.location = (586.4400024414062, -384.64801025390625)
    group_input_8.location = (-1257.88134765625, 0.0)
    math_8.location = (29.38995361328125, -35.87506103515625)
    math_001_5.location = (30.3779296875, -206.9222412109375)
    math_003_6.location = (316.76531982421875, -147.8509521484375)
    math_002_6.location = (33.34173583984375, -370.05975341796875)
    math_004_6.location = (534.8516845703125, -174.921875)
    math_005_5.location = (29.25299072265625, -35.488494873046875)
    math_006_5.location = (30.240966796875, -206.53567504882812)
    math_007_5.location = (316.62835693359375, -147.46438598632812)
    math_008_4.location = (33.20477294921875, -369.6731872558594)
    math_009_2.location = (534.7147216796875, -174.53530883789062)
    math_010_1.location = (28.97296142578125, -36.170074462890625)
    math_011_1.location = (29.9609375, -207.21725463867188)
    math_012.location = (316.34832763671875, -148.14596557617188)
    math_013.location = (32.92474365234375, -370.3547668457031)
    math_014.location = (534.4346923828125, -175.21688842773438)
    math_015.location = (716.6485595703125, -121.4481201171875)
    math_017.location = (714.3045654296875, -105.29281616210938)
    math_016.location = (712.4110717773438, -111.568603515625)
    math_018.location = (33.6015625, -35.64434814453125)
    math_020.location = (30.34515380859375, -195.2674560546875)
    math_022_1.location = (29.259521484375, -360.6390380859375)
    math_021.location = (548.53759765625, -370.0714416503906)
    math_019.location = (301.19183349609375, -207.4495849609375)
    math_023_1.location = (33.4306640625, -36.06919860839844)
    math_025_1.location = (29.088623046875, -361.06390380859375)
    math_028_1.location = (33.38775634765625, -36.05426025390625)
    math_029.location = (30.13134765625, -195.67742919921875)
    math_030.location = (29.04571533203125, -361.0489501953125)
    math_031.location = (548.3237915039062, -370.48138427734375)
    math_032.location = (300.97802734375, -207.8594970703125)
    group_output_9.location = (1753.110107421875, -150.42881774902344)
    math_027_1.location = (301.02093505859375, -207.8744354248047)
    math_026_1.location = (548.36669921875, -370.49627685546875)
    math_024_1.location = (30.17425537109375, -195.6923370361328)
    separate_color_001_2.location = (-1057.88134765625, 229.4679718017578)
    reroute_001_3.location = (-605.2171020507812, -1088.60498046875)
    reroute_5.location = (1297.698486328125, -1088.60498046875)

    # Set dimensions
    frame_7.width, frame_7.height = 885.9200439453125, 541.6320190429688
    frame_001_4.width, frame_001_4.height = 881.60009765625, 540.1920166015625
    frame_002_3.width, frame_002_3.height = 883.760009765625, 540.9119873046875
    frame_003_2.width, frame_003_2.height = 717.4400634765625, 532.2720336914062
    frame_004_2.width, frame_004_2.height = 717.4400634765625, 531.552001953125
    frame_005_1.width, frame_005_1.height = 717.4400024414062, 531.552001953125
    group_input_8.width, group_input_8.height = 140.0, 100.0
    math_8.width, math_8.height = 145.92752075195312, 100.0
    math_001_5.width, math_001_5.height = 145.92752075195312, 100.0
    math_003_6.width, math_003_6.height = 140.0, 100.0
    math_002_6.width, math_002_6.height = 145.92752075195312, 100.0
    math_004_6.width, math_004_6.height = 140.0, 100.0
    math_005_5.width, math_005_5.height = 145.92752075195312, 100.0
    math_006_5.width, math_006_5.height = 145.92752075195312, 100.0
    math_007_5.width, math_007_5.height = 140.0, 100.0
    math_008_4.width, math_008_4.height = 145.92752075195312, 100.0
    math_009_2.width, math_009_2.height = 140.0, 100.0
    math_010_1.width, math_010_1.height = 145.92752075195312, 100.0
    math_011_1.width, math_011_1.height = 145.92752075195312, 100.0
    math_012.width, math_012.height = 140.0, 100.0
    math_013.width, math_013.height = 145.92752075195312, 100.0
    math_014.width, math_014.height = 140.0, 100.0
    math_015.width, math_015.height = 140.0, 100.0
    math_017.width, math_017.height = 140.0, 100.0
    math_016.width, math_016.height = 140.0, 100.0
    math_018.width, math_018.height = 140.0, 100.0
    math_020.width, math_020.height = 140.0, 100.0
    math_022_1.width, math_022_1.height = 140.0, 100.0
    math_021.width, math_021.height = 140.0, 100.0
    math_019.width, math_019.height = 140.0, 100.0
    math_023_1.width, math_023_1.height = 140.0, 100.0
    math_025_1.width, math_025_1.height = 140.0, 100.0
    math_028_1.width, math_028_1.height = 140.0, 100.0
    math_029.width, math_029.height = 140.0, 100.0
    math_030.width, math_030.height = 140.0, 100.0
    math_031.width, math_031.height = 140.0, 100.0
    math_032.width, math_032.height = 140.0, 100.0
    group_output_9.width, group_output_9.height = 140.0, 100.0
    math_027_1.width, math_027_1.height = 140.0, 100.0
    math_026_1.width, math_026_1.height = 140.0, 100.0
    math_024_1.width, math_024_1.height = 140.0, 100.0
    separate_color_001_2.width, separate_color_001_2.height = 140.0, 100.0
    reroute_001_3.width, reroute_001_3.height = 13.5, 100.0
    reroute_5.width, reroute_5.height = 13.5, 100.0

    # Initialize _rr_srgb_to_lab links

    # math_014.Value -> math_017.Value
    _rr_srgb_to_lab.links.new(math_014.outputs[0], math_017.inputs[0])
    # math_010_1.Value -> math_012.Value
    _rr_srgb_to_lab.links.new(math_010_1.outputs[0], math_012.inputs[0])
    # math_005_5.Value -> math_007_5.Value
    _rr_srgb_to_lab.links.new(math_005_5.outputs[0], math_007_5.inputs[0])
    # separate_color_001_2.Red -> math_005_5.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[0], math_005_5.inputs[0])
    # math_018.Value -> math_019.Value
    _rr_srgb_to_lab.links.new(math_018.outputs[0], math_019.inputs[0])
    # separate_color_001_2.Green -> math_006_5.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[1], math_006_5.inputs[0])
    # math_004_6.Value -> math_015.Value
    _rr_srgb_to_lab.links.new(math_004_6.outputs[0], math_015.inputs[0])
    # math_011_1.Value -> math_012.Value
    _rr_srgb_to_lab.links.new(math_011_1.outputs[0], math_012.inputs[1])
    # math_006_5.Value -> math_007_5.Value
    _rr_srgb_to_lab.links.new(math_006_5.outputs[0], math_007_5.inputs[1])
    # math_012.Value -> math_014.Value
    _rr_srgb_to_lab.links.new(math_012.outputs[0], math_014.inputs[0])
    # math_020.Value -> math_019.Value
    _rr_srgb_to_lab.links.new(math_020.outputs[0], math_019.inputs[1])
    # math_008_4.Value -> math_009_2.Value
    _rr_srgb_to_lab.links.new(math_008_4.outputs[0], math_009_2.inputs[1])
    # separate_color_001_2.Red -> math_8.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[0], math_8.inputs[0])
    # math_007_5.Value -> math_009_2.Value
    _rr_srgb_to_lab.links.new(math_007_5.outputs[0], math_009_2.inputs[0])
    # math_009_2.Value -> math_016.Value
    _rr_srgb_to_lab.links.new(math_009_2.outputs[0], math_016.inputs[0])
    # math_001_5.Value -> math_003_6.Value
    _rr_srgb_to_lab.links.new(math_001_5.outputs[0], math_003_6.inputs[1])
    # separate_color_001_2.Blue -> math_002_6.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[2], math_002_6.inputs[0])
    # separate_color_001_2.Green -> math_001_5.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[1], math_001_5.inputs[0])
    # math_016.Value -> math_020.Value
    _rr_srgb_to_lab.links.new(math_016.outputs[0], math_020.inputs[0])
    # math_022_1.Value -> math_021.Value
    _rr_srgb_to_lab.links.new(math_022_1.outputs[0], math_021.inputs[1])
    # math_8.Value -> math_003_6.Value
    _rr_srgb_to_lab.links.new(math_8.outputs[0], math_003_6.inputs[0])
    # separate_color_001_2.Red -> math_010_1.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[0], math_010_1.inputs[0])
    # math_003_6.Value -> math_004_6.Value
    _rr_srgb_to_lab.links.new(math_003_6.outputs[0], math_004_6.inputs[0])
    # math_017.Value -> math_022_1.Value
    _rr_srgb_to_lab.links.new(math_017.outputs[0], math_022_1.inputs[0])
    # separate_color_001_2.Blue -> math_008_4.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[2], math_008_4.inputs[0])
    # math_013.Value -> math_014.Value
    _rr_srgb_to_lab.links.new(math_013.outputs[0], math_014.inputs[1])
    # math_019.Value -> math_021.Value
    _rr_srgb_to_lab.links.new(math_019.outputs[0], math_021.inputs[0])
    # math_015.Value -> math_018.Value
    _rr_srgb_to_lab.links.new(math_015.outputs[0], math_018.inputs[0])
    # math_002_6.Value -> math_004_6.Value
    _rr_srgb_to_lab.links.new(math_002_6.outputs[0], math_004_6.inputs[1])
    # separate_color_001_2.Green -> math_011_1.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[1], math_011_1.inputs[0])
    # separate_color_001_2.Blue -> math_013.Value
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[2], math_013.inputs[0])
    # group_input_8.Image -> separate_color_001_2.Image
    _rr_srgb_to_lab.links.new(group_input_8.outputs[0], separate_color_001_2.inputs[0])
    # math_021.Value -> group_output_9.L
    _rr_srgb_to_lab.links.new(math_021.outputs[0], group_output_9.inputs[0])
    # math_023_1.Value -> math_027_1.Value
    _rr_srgb_to_lab.links.new(math_023_1.outputs[0], math_027_1.inputs[0])
    # math_024_1.Value -> math_027_1.Value
    _rr_srgb_to_lab.links.new(math_024_1.outputs[0], math_027_1.inputs[1])
    # math_016.Value -> math_024_1.Value
    _rr_srgb_to_lab.links.new(math_016.outputs[0], math_024_1.inputs[0])
    # math_025_1.Value -> math_026_1.Value
    _rr_srgb_to_lab.links.new(math_025_1.outputs[0], math_026_1.inputs[1])
    # math_017.Value -> math_025_1.Value
    _rr_srgb_to_lab.links.new(math_017.outputs[0], math_025_1.inputs[0])
    # math_027_1.Value -> math_026_1.Value
    _rr_srgb_to_lab.links.new(math_027_1.outputs[0], math_026_1.inputs[0])
    # math_015.Value -> math_023_1.Value
    _rr_srgb_to_lab.links.new(math_015.outputs[0], math_023_1.inputs[0])
    # math_028_1.Value -> math_032.Value
    _rr_srgb_to_lab.links.new(math_028_1.outputs[0], math_032.inputs[0])
    # math_029.Value -> math_032.Value
    _rr_srgb_to_lab.links.new(math_029.outputs[0], math_032.inputs[1])
    # math_016.Value -> math_029.Value
    _rr_srgb_to_lab.links.new(math_016.outputs[0], math_029.inputs[0])
    # math_030.Value -> math_031.Value
    _rr_srgb_to_lab.links.new(math_030.outputs[0], math_031.inputs[1])
    # math_017.Value -> math_030.Value
    _rr_srgb_to_lab.links.new(math_017.outputs[0], math_030.inputs[0])
    # math_032.Value -> math_031.Value
    _rr_srgb_to_lab.links.new(math_032.outputs[0], math_031.inputs[0])
    # math_015.Value -> math_028_1.Value
    _rr_srgb_to_lab.links.new(math_015.outputs[0], math_028_1.inputs[0])
    # math_026_1.Value -> group_output_9.A
    _rr_srgb_to_lab.links.new(math_026_1.outputs[0], group_output_9.inputs[1])
    # math_031.Value -> group_output_9.B
    _rr_srgb_to_lab.links.new(math_031.outputs[0], group_output_9.inputs[2])
    # reroute_5.Output -> group_output_9.Alpha
    _rr_srgb_to_lab.links.new(reroute_5.outputs[0], group_output_9.inputs[3])
    # reroute_001_3.Output -> reroute_5.Input
    _rr_srgb_to_lab.links.new(reroute_001_3.outputs[0], reroute_5.inputs[0])
    # separate_color_001_2.Alpha -> reroute_001_3.Input
    _rr_srgb_to_lab.links.new(separate_color_001_2.outputs[3], reroute_001_3.inputs[0])

    return _rr_srgb_to_lab


_rr_srgb_to_lab = _rr_srgb_to_lab_node_group()

def _rr_lab_to_srgb_node_group():
    """Initialize .RR_LAB_to_sRGB node group"""
    _rr_lab_to_srgb = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_LAB_to_sRGB")

    _rr_lab_to_srgb.color_tag = 'NONE'
    _rr_lab_to_srgb.description = ""
    _rr_lab_to_srgb.default_group_node_width = 140
    # _rr_lab_to_srgb interface

    # Socket Image
    image_socket_16 = _rr_lab_to_srgb.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_16.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_16.attribute_domain = 'POINT'
    image_socket_16.default_input = 'VALUE'
    image_socket_16.structure_type = 'AUTO'

    # Socket L
    l_socket_1 = _rr_lab_to_srgb.interface.new_socket(name="L", in_out='INPUT', socket_type='NodeSocketFloat')
    l_socket_1.default_value = 0.5
    l_socket_1.min_value = -10000.0
    l_socket_1.max_value = 10000.0
    l_socket_1.subtype = 'NONE'
    l_socket_1.attribute_domain = 'POINT'
    l_socket_1.hide_value = True
    l_socket_1.default_input = 'VALUE'
    l_socket_1.structure_type = 'AUTO'

    # Socket A
    a_socket_1 = _rr_lab_to_srgb.interface.new_socket(name="A", in_out='INPUT', socket_type='NodeSocketFloat')
    a_socket_1.default_value = 0.5
    a_socket_1.min_value = -10000.0
    a_socket_1.max_value = 10000.0
    a_socket_1.subtype = 'NONE'
    a_socket_1.attribute_domain = 'POINT'
    a_socket_1.hide_value = True
    a_socket_1.default_input = 'VALUE'
    a_socket_1.structure_type = 'AUTO'

    # Socket B
    b_socket_1 = _rr_lab_to_srgb.interface.new_socket(name="B", in_out='INPUT', socket_type='NodeSocketFloat')
    b_socket_1.default_value = 0.5
    b_socket_1.min_value = -10000.0
    b_socket_1.max_value = 10000.0
    b_socket_1.subtype = 'NONE'
    b_socket_1.attribute_domain = 'POINT'
    b_socket_1.hide_value = True
    b_socket_1.default_input = 'VALUE'
    b_socket_1.structure_type = 'AUTO'

    # Socket Alpha
    alpha_socket_1 = _rr_lab_to_srgb.interface.new_socket(name="Alpha", in_out='INPUT', socket_type='NodeSocketFloat')
    alpha_socket_1.default_value = 1.0
    alpha_socket_1.min_value = 0.0
    alpha_socket_1.max_value = 1.0
    alpha_socket_1.subtype = 'FACTOR'
    alpha_socket_1.attribute_domain = 'POINT'
    alpha_socket_1.default_input = 'VALUE'
    alpha_socket_1.structure_type = 'AUTO'

    # Initialize _rr_lab_to_srgb nodes

    # Node Frame
    frame_8 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_8.label = "l"
    frame_8.name = "Frame"
    frame_8.label_size = 20
    frame_8.shrink = True

    # Node Frame.001
    frame_001_5 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_001_5.label = "m"
    frame_001_5.name = "Frame.001"
    frame_001_5.label_size = 20
    frame_001_5.shrink = True

    # Node Frame.002
    frame_002_4 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_002_4.label = "s"
    frame_002_4.name = "Frame.002"
    frame_002_4.label_size = 20
    frame_002_4.shrink = True

    # Node Frame.003
    frame_003_3 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_003_3.label = "R"
    frame_003_3.name = "Frame.003"
    frame_003_3.label_size = 20
    frame_003_3.shrink = True

    # Node Frame.004
    frame_004_3 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_004_3.label = "G"
    frame_004_3.name = "Frame.004"
    frame_004_3.label_size = 20
    frame_004_3.shrink = True

    # Node Frame.005
    frame_005_2 = _rr_lab_to_srgb.nodes.new("NodeFrame")
    frame_005_2.label = "B"
    frame_005_2.name = "Frame.005"
    frame_005_2.label_size = 20
    frame_005_2.shrink = True

    # Node Math.001
    math_001_6 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_001_6.name = "Math.001"
    math_001_6.operation = 'MULTIPLY'
    math_001_6.use_clamp = False
    # Value_001
    math_001_6.inputs[1].default_value = 0.3963377773761749

    # Node Math.003
    math_003_7 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_003_7.name = "Math.003"
    math_003_7.operation = 'MULTIPLY'
    math_003_7.use_clamp = False
    # Value_001
    math_003_7.inputs[1].default_value = 0.21580375730991364

    # Node Math.002
    math_002_7 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_002_7.name = "Math.002"
    math_002_7.hide = True
    math_002_7.operation = 'ADD'
    math_002_7.use_clamp = False

    # Node Math.004
    math_004_7 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_004_7.name = "Math.004"
    math_004_7.operation = 'POWER'
    math_004_7.use_clamp = False
    # Value_001
    math_004_7.inputs[1].default_value = 3.0

    # Node Math.005
    math_005_6 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_005_6.name = "Math.005"
    math_005_6.operation = 'MULTIPLY'
    math_005_6.use_clamp = False
    # Value_001
    math_005_6.inputs[1].default_value = 0.10556134581565857

    # Node Math.006
    math_006_6 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_006_6.name = "Math.006"
    math_006_6.operation = 'MULTIPLY'
    math_006_6.use_clamp = False
    # Value_001
    math_006_6.inputs[1].default_value = 0.0638541728258133

    # Node Math.009
    math_009_3 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_009_3.name = "Math.009"
    math_009_3.operation = 'POWER'
    math_009_3.use_clamp = False
    # Value_001
    math_009_3.inputs[1].default_value = 3.0

    # Node Math.008
    math_008_5 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_008_5.name = "Math.008"
    math_008_5.hide = True
    math_008_5.operation = 'SUBTRACT'
    math_008_5.use_clamp = False

    # Node Math.010
    math_010_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_010_2.name = "Math.010"
    math_010_2.operation = 'MULTIPLY'
    math_010_2.use_clamp = False
    # Value_001
    math_010_2.inputs[1].default_value = 0.08948417752981186

    # Node Math.011
    math_011_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_011_2.name = "Math.011"
    math_011_2.operation = 'MULTIPLY'
    math_011_2.use_clamp = False
    # Value_001
    math_011_2.inputs[1].default_value = 1.2914855480194092

    # Node Math.014
    math_014_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_014_1.name = "Math.014"
    math_014_1.hide = True
    math_014_1.operation = 'SUBTRACT'
    math_014_1.use_clamp = False

    # Node Group Input
    group_input_9 = _rr_lab_to_srgb.nodes.new("NodeGroupInput")
    group_input_9.name = "Group Input"

    # Node Math.013
    math_013_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_013_1.name = "Math.013"
    math_013_1.hide = True
    math_013_1.operation = 'SUBTRACT'
    math_013_1.use_clamp = False

    # Node Math.007
    math_007_6 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_007_6.name = "Math.007"
    math_007_6.hide = True
    math_007_6.operation = 'SUBTRACT'
    math_007_6.use_clamp = False

    # Node Reroute
    reroute_6 = _rr_lab_to_srgb.nodes.new("NodeReroute")
    reroute_6.name = "Reroute"
    reroute_6.socket_idname = "NodeSocketFloat"
    # Node Reroute.001
    reroute_001_4 = _rr_lab_to_srgb.nodes.new("NodeReroute")
    reroute_001_4.name = "Reroute.001"
    reroute_001_4.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_3 = _rr_lab_to_srgb.nodes.new("NodeReroute")
    reroute_002_3.name = "Reroute.002"
    reroute_002_3.socket_idname = "NodeSocketFloat"
    # Node Math
    math_9 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_9.name = "Math"
    math_9.hide = True
    math_9.operation = 'ADD'
    math_9.use_clamp = False

    # Node Math.012
    math_012_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_012_1.name = "Math.012"
    math_012_1.operation = 'POWER'
    math_012_1.use_clamp = False
    # Value_001
    math_012_1.inputs[1].default_value = 3.0

    # Node Math.015
    math_015_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_015_1.name = "Math.015"
    math_015_1.operation = 'MULTIPLY'
    math_015_1.use_clamp = False
    # Value_001
    math_015_1.inputs[1].default_value = 4.076741695404053

    # Node Math.016
    math_016_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_016_1.name = "Math.016"
    math_016_1.hide = True
    math_016_1.operation = 'SUBTRACT'
    math_016_1.use_clamp = False

    # Node Math.017
    math_017_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_017_1.name = "Math.017"
    math_017_1.operation = 'MULTIPLY'
    math_017_1.use_clamp = False
    # Value_001
    math_017_1.inputs[1].default_value = 3.307711601257324

    # Node Math.019
    math_019_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_019_1.name = "Math.019"
    math_019_1.operation = 'MULTIPLY'
    math_019_1.use_clamp = False
    # Value_001
    math_019_1.inputs[1].default_value = 0.23096993565559387

    # Node Math.020
    math_020_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_020_1.name = "Math.020"
    math_020_1.operation = 'MULTIPLY'
    math_020_1.use_clamp = False
    # Value_001
    math_020_1.inputs[1].default_value = -1.2684379816055298

    # Node Math.023
    math_023_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_023_2.name = "Math.023"
    math_023_2.operation = 'MULTIPLY'
    math_023_2.use_clamp = False
    # Value_001
    math_023_2.inputs[1].default_value = 2.609757423400879

    # Node Math.024
    math_024_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_024_2.name = "Math.024"
    math_024_2.operation = 'MULTIPLY'
    math_024_2.use_clamp = False
    # Value_001
    math_024_2.inputs[1].default_value = 0.34131938219070435

    # Node Math.021
    math_021_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_021_1.name = "Math.021"
    math_021_1.hide = True
    math_021_1.operation = 'ADD'
    math_021_1.use_clamp = False

    # Node Math.022
    math_022_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_022_2.name = "Math.022"
    math_022_2.hide = True
    math_022_2.operation = 'SUBTRACT'
    math_022_2.use_clamp = False

    # Node Math.025
    math_025_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_025_2.name = "Math.025"
    math_025_2.operation = 'MULTIPLY'
    math_025_2.use_clamp = False
    # Value_001
    math_025_2.inputs[1].default_value = -0.004196086432784796

    # Node Math.026
    math_026_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_026_2.name = "Math.026"
    math_026_2.hide = True
    math_026_2.operation = 'SUBTRACT'
    math_026_2.use_clamp = False

    # Node Math.028
    math_028_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_028_2.name = "Math.028"
    math_028_2.operation = 'MULTIPLY'
    math_028_2.use_clamp = False
    # Value_001
    math_028_2.inputs[1].default_value = 0.7034186124801636

    # Node Math.029
    math_029_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_029_1.name = "Math.029"
    math_029_1.operation = 'MULTIPLY'
    math_029_1.use_clamp = False
    # Value_001
    math_029_1.inputs[1].default_value = 1.7076146602630615

    # Node Math.018
    math_018_1 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_018_1.name = "Math.018"
    math_018_1.hide = True
    math_018_1.operation = 'ADD'
    math_018_1.use_clamp = False

    # Node Math.027
    math_027_2 = _rr_lab_to_srgb.nodes.new("ShaderNodeMath")
    math_027_2.name = "Math.027"
    math_027_2.hide = True
    math_027_2.operation = 'ADD'
    math_027_2.use_clamp = False

    # Node Reroute.004
    reroute_004_2 = _rr_lab_to_srgb.nodes.new("NodeReroute")
    reroute_004_2.name = "Reroute.004"
    reroute_004_2.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.003
    reroute_003_3 = _rr_lab_to_srgb.nodes.new("NodeReroute")
    reroute_003_3.name = "Reroute.003"
    reroute_003_3.socket_idname = "NodeSocketFloatFactor"
    # Node Combine Color
    combine_color_3 = _rr_lab_to_srgb.nodes.new("CompositorNodeCombineColor")
    combine_color_3.name = "Combine Color"
    combine_color_3.mode = 'RGB'
    combine_color_3.ycc_mode = 'ITUBT709'

    # Node Group Output
    group_output_10 = _rr_lab_to_srgb.nodes.new("NodeGroupOutput")
    group_output_10.name = "Group Output"
    group_output_10.is_active_output = True

    # Set parents
    math_001_6.parent = frame_8
    math_003_7.parent = frame_8
    math_002_7.parent = frame_8
    math_004_7.parent = frame_8
    math_005_6.parent = frame_001_5
    math_006_6.parent = frame_001_5
    math_009_3.parent = frame_001_5
    math_008_5.parent = frame_001_5
    math_010_2.parent = frame_002_4
    math_011_2.parent = frame_002_4
    math_014_1.parent = frame_002_4
    math_013_1.parent = frame_002_4
    math_007_6.parent = frame_001_5
    reroute_6.parent = frame_002_4
    reroute_001_4.parent = frame_8
    reroute_002_3.parent = frame_001_5
    math_9.parent = frame_8
    math_012_1.parent = frame_002_4
    math_015_1.parent = frame_003_3
    math_016_1.parent = frame_003_3
    math_017_1.parent = frame_003_3
    math_019_1.parent = frame_003_3
    math_020_1.parent = frame_004_3
    math_023_2.parent = frame_004_3
    math_024_2.parent = frame_004_3
    math_021_1.parent = frame_004_3
    math_022_2.parent = frame_004_3
    math_025_2.parent = frame_005_2
    math_026_2.parent = frame_005_2
    math_028_2.parent = frame_005_2
    math_029_1.parent = frame_005_2
    math_018_1.parent = frame_003_3
    math_027_2.parent = frame_005_2

    # Set locations
    frame_8.location = (-448.20001220703125, 186.8520050048828)
    frame_001_5.location = (-453.2400207519531, -322.1880187988281)
    frame_002_4.location = (-453.2400207519531, -824.028076171875)
    frame_003_3.location = (585.7200317382812, 287.11199951171875)
    frame_004_3.location = (585.7200317382812, -270.1679992675781)
    frame_005_2.location = (585.7200317382812, -826.7280883789062)
    math_001_6.location = (30.4813232421875, -148.60289001464844)
    math_003_7.location = (29.4132080078125, -310.0068359375)
    math_002_7.location = (444.392333984375, -197.37184143066406)
    math_004_7.location = (638.4321899414062, -106.75553894042969)
    math_005_6.location = (30.406097412109375, -148.07794189453125)
    math_006_6.location = (29.337982177734375, -309.4819030761719)
    math_009_3.location = (638.35693359375, -106.2305908203125)
    math_008_5.location = (444.3171081542969, -196.84689331054688)
    math_010_2.location = (30.406097412109375, -148.4639892578125)
    math_011_2.location = (29.337982177734375, -309.867919921875)
    math_014_1.location = (444.3171081542969, -197.23291015625)
    group_input_9.location = (-1044.4654541015625, -560.0506591796875)
    math_013_1.location = (267.8774719238281, -40.87353515625)
    math_007_6.location = (267.8774719238281, -40.487518310546875)
    reroute_6.location = (43.680145263671875, -45.2542724609375)
    reroute_001_4.location = (41.6463623046875, -40.73890686035156)
    reroute_002_3.location = (40.127532958984375, -43.086578369140625)
    math_9.location = (267.95269775390625, -41.01246643066406)
    math_012_1.location = (638.35693359375, -106.6165771484375)
    math_015_1.location = (30.87939453125, -36.0831298828125)
    math_016_1.location = (282.37548828125, -144.75802612304688)
    math_017_1.location = (28.8912353515625, -199.9332275390625)
    math_019_1.location = (28.8912353515625, -363.1110534667969)
    math_020_1.location = (30.87939453125, -35.835296630859375)
    math_023_2.location = (28.8912353515625, -199.68539428710938)
    math_024_2.location = (28.8912353515625, -362.8632507324219)
    math_021_1.location = (282.37548828125, -144.51019287109375)
    math_022_2.location = (501.82720947265625, -203.20724487304688)
    math_025_2.location = (30.87939453125, -36.189208984375)
    math_026_2.location = (282.37548828125, -144.86407470703125)
    math_028_2.location = (28.8912353515625, -200.03924560546875)
    math_029_1.location = (28.8912353515625, -363.21710205078125)
    math_018_1.location = (501.82720947265625, -203.455078125)
    math_027_2.location = (501.82720947265625, -203.56121826171875)
    reroute_004_2.location = (-512.4686279296875, -1427.89208984375)
    reroute_003_3.location = (1319.47998046875, -1427.89208984375)
    combine_color_3.location = (1519.4661865234375, -482.8539123535156)
    group_output_10.location = (1761.5096435546875, -512.4573364257812)

    # Set dimensions
    frame_8.width, frame_8.height = 807.4400634765625, 480.25201416015625
    frame_001_5.width, frame_001_5.height = 807.4400634765625, 479.5320129394531
    frame_002_4.width, frame_002_4.height = 807.4400634765625, 480.251953125
    frame_003_3.width, frame_003_3.height = 670.6400756835938, 533.7120361328125
    frame_004_3.width, frame_004_3.height = 670.6400756835938, 532.9920654296875
    frame_005_2.width, frame_005_2.height = 670.6400756835938, 533.7119750976562
    math_001_6.width, math_001_6.height = 140.0, 100.0
    math_003_7.width, math_003_7.height = 140.0, 100.0
    math_002_7.width, math_002_7.height = 140.0, 100.0
    math_004_7.width, math_004_7.height = 140.0, 100.0
    math_005_6.width, math_005_6.height = 140.0, 100.0
    math_006_6.width, math_006_6.height = 140.0, 100.0
    math_009_3.width, math_009_3.height = 140.0, 100.0
    math_008_5.width, math_008_5.height = 140.0, 100.0
    math_010_2.width, math_010_2.height = 140.0, 100.0
    math_011_2.width, math_011_2.height = 140.0, 100.0
    math_014_1.width, math_014_1.height = 140.0, 100.0
    group_input_9.width, group_input_9.height = 140.0, 100.0
    math_013_1.width, math_013_1.height = 140.0, 100.0
    math_007_6.width, math_007_6.height = 140.0, 100.0
    reroute_6.width, reroute_6.height = 13.5, 100.0
    reroute_001_4.width, reroute_001_4.height = 13.5, 100.0
    reroute_002_3.width, reroute_002_3.height = 13.5, 100.0
    math_9.width, math_9.height = 140.0, 100.0
    math_012_1.width, math_012_1.height = 140.0, 100.0
    math_015_1.width, math_015_1.height = 140.0, 100.0
    math_016_1.width, math_016_1.height = 140.0, 100.0
    math_017_1.width, math_017_1.height = 140.0, 100.0
    math_019_1.width, math_019_1.height = 140.0, 100.0
    math_020_1.width, math_020_1.height = 140.0, 100.0
    math_023_2.width, math_023_2.height = 140.0, 100.0
    math_024_2.width, math_024_2.height = 140.0, 100.0
    math_021_1.width, math_021_1.height = 140.0, 100.0
    math_022_2.width, math_022_2.height = 140.0, 100.0
    math_025_2.width, math_025_2.height = 140.0, 100.0
    math_026_2.width, math_026_2.height = 140.0, 100.0
    math_028_2.width, math_028_2.height = 140.0, 100.0
    math_029_1.width, math_029_1.height = 140.0, 100.0
    math_018_1.width, math_018_1.height = 140.0, 100.0
    math_027_2.width, math_027_2.height = 140.0, 100.0
    reroute_004_2.width, reroute_004_2.height = 13.5, 100.0
    reroute_003_3.width, reroute_003_3.height = 13.5, 100.0
    combine_color_3.width, combine_color_3.height = 140.0, 100.0
    group_output_10.width, group_output_10.height = 140.0, 100.0

    # Initialize _rr_lab_to_srgb links

    # math_001_6.Value -> math_9.Value
    _rr_lab_to_srgb.links.new(math_001_6.outputs[0], math_9.inputs[1])
    # math_002_7.Value -> math_004_7.Value
    _rr_lab_to_srgb.links.new(math_002_7.outputs[0], math_004_7.inputs[0])
    # math_9.Value -> math_002_7.Value
    _rr_lab_to_srgb.links.new(math_9.outputs[0], math_002_7.inputs[0])
    # math_003_7.Value -> math_002_7.Value
    _rr_lab_to_srgb.links.new(math_003_7.outputs[0], math_002_7.inputs[1])
    # group_input_9.A -> math_001_6.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[1], math_001_6.inputs[0])
    # group_input_9.B -> math_003_7.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[2], math_003_7.inputs[0])
    # reroute_001_4.Output -> math_9.Value
    _rr_lab_to_srgb.links.new(reroute_001_4.outputs[0], math_9.inputs[0])
    # math_005_6.Value -> math_007_6.Value
    _rr_lab_to_srgb.links.new(math_005_6.outputs[0], math_007_6.inputs[1])
    # math_008_5.Value -> math_009_3.Value
    _rr_lab_to_srgb.links.new(math_008_5.outputs[0], math_009_3.inputs[0])
    # math_007_6.Value -> math_008_5.Value
    _rr_lab_to_srgb.links.new(math_007_6.outputs[0], math_008_5.inputs[0])
    # math_006_6.Value -> math_008_5.Value
    _rr_lab_to_srgb.links.new(math_006_6.outputs[0], math_008_5.inputs[1])
    # group_input_9.A -> math_005_6.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[1], math_005_6.inputs[0])
    # group_input_9.B -> math_006_6.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[2], math_006_6.inputs[0])
    # reroute_002_3.Output -> math_007_6.Value
    _rr_lab_to_srgb.links.new(reroute_002_3.outputs[0], math_007_6.inputs[0])
    # math_010_2.Value -> math_013_1.Value
    _rr_lab_to_srgb.links.new(math_010_2.outputs[0], math_013_1.inputs[1])
    # math_014_1.Value -> math_012_1.Value
    _rr_lab_to_srgb.links.new(math_014_1.outputs[0], math_012_1.inputs[0])
    # math_013_1.Value -> math_014_1.Value
    _rr_lab_to_srgb.links.new(math_013_1.outputs[0], math_014_1.inputs[0])
    # math_011_2.Value -> math_014_1.Value
    _rr_lab_to_srgb.links.new(math_011_2.outputs[0], math_014_1.inputs[1])
    # group_input_9.A -> math_010_2.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[1], math_010_2.inputs[0])
    # group_input_9.B -> math_011_2.Value
    _rr_lab_to_srgb.links.new(group_input_9.outputs[2], math_011_2.inputs[0])
    # reroute_6.Output -> math_013_1.Value
    _rr_lab_to_srgb.links.new(reroute_6.outputs[0], math_013_1.inputs[0])
    # group_input_9.L -> reroute_6.Input
    _rr_lab_to_srgb.links.new(group_input_9.outputs[0], reroute_6.inputs[0])
    # group_input_9.L -> reroute_001_4.Input
    _rr_lab_to_srgb.links.new(group_input_9.outputs[0], reroute_001_4.inputs[0])
    # group_input_9.L -> reroute_002_3.Input
    _rr_lab_to_srgb.links.new(group_input_9.outputs[0], reroute_002_3.inputs[0])
    # math_004_7.Value -> math_015_1.Value
    _rr_lab_to_srgb.links.new(math_004_7.outputs[0], math_015_1.inputs[0])
    # math_015_1.Value -> math_016_1.Value
    _rr_lab_to_srgb.links.new(math_015_1.outputs[0], math_016_1.inputs[0])
    # math_009_3.Value -> math_017_1.Value
    _rr_lab_to_srgb.links.new(math_009_3.outputs[0], math_017_1.inputs[0])
    # math_017_1.Value -> math_016_1.Value
    _rr_lab_to_srgb.links.new(math_017_1.outputs[0], math_016_1.inputs[1])
    # math_016_1.Value -> math_018_1.Value
    _rr_lab_to_srgb.links.new(math_016_1.outputs[0], math_018_1.inputs[0])
    # math_012_1.Value -> math_019_1.Value
    _rr_lab_to_srgb.links.new(math_012_1.outputs[0], math_019_1.inputs[0])
    # math_019_1.Value -> math_018_1.Value
    _rr_lab_to_srgb.links.new(math_019_1.outputs[0], math_018_1.inputs[1])
    # math_004_7.Value -> math_020_1.Value
    _rr_lab_to_srgb.links.new(math_004_7.outputs[0], math_020_1.inputs[0])
    # math_020_1.Value -> math_021_1.Value
    _rr_lab_to_srgb.links.new(math_020_1.outputs[0], math_021_1.inputs[0])
    # math_009_3.Value -> math_023_2.Value
    _rr_lab_to_srgb.links.new(math_009_3.outputs[0], math_023_2.inputs[0])
    # math_023_2.Value -> math_021_1.Value
    _rr_lab_to_srgb.links.new(math_023_2.outputs[0], math_021_1.inputs[1])
    # math_021_1.Value -> math_022_2.Value
    _rr_lab_to_srgb.links.new(math_021_1.outputs[0], math_022_2.inputs[0])
    # math_012_1.Value -> math_024_2.Value
    _rr_lab_to_srgb.links.new(math_012_1.outputs[0], math_024_2.inputs[0])
    # math_024_2.Value -> math_022_2.Value
    _rr_lab_to_srgb.links.new(math_024_2.outputs[0], math_022_2.inputs[1])
    # math_004_7.Value -> math_025_2.Value
    _rr_lab_to_srgb.links.new(math_004_7.outputs[0], math_025_2.inputs[0])
    # math_025_2.Value -> math_026_2.Value
    _rr_lab_to_srgb.links.new(math_025_2.outputs[0], math_026_2.inputs[0])
    # math_009_3.Value -> math_028_2.Value
    _rr_lab_to_srgb.links.new(math_009_3.outputs[0], math_028_2.inputs[0])
    # math_028_2.Value -> math_026_2.Value
    _rr_lab_to_srgb.links.new(math_028_2.outputs[0], math_026_2.inputs[1])
    # math_026_2.Value -> math_027_2.Value
    _rr_lab_to_srgb.links.new(math_026_2.outputs[0], math_027_2.inputs[0])
    # math_012_1.Value -> math_029_1.Value
    _rr_lab_to_srgb.links.new(math_012_1.outputs[0], math_029_1.inputs[0])
    # math_029_1.Value -> math_027_2.Value
    _rr_lab_to_srgb.links.new(math_029_1.outputs[0], math_027_2.inputs[1])
    # math_018_1.Value -> combine_color_3.Red
    _rr_lab_to_srgb.links.new(math_018_1.outputs[0], combine_color_3.inputs[0])
    # math_022_2.Value -> combine_color_3.Green
    _rr_lab_to_srgb.links.new(math_022_2.outputs[0], combine_color_3.inputs[1])
    # math_027_2.Value -> combine_color_3.Blue
    _rr_lab_to_srgb.links.new(math_027_2.outputs[0], combine_color_3.inputs[2])
    # reroute_003_3.Output -> combine_color_3.Alpha
    _rr_lab_to_srgb.links.new(reroute_003_3.outputs[0], combine_color_3.inputs[3])
    # reroute_004_2.Output -> reroute_003_3.Input
    _rr_lab_to_srgb.links.new(reroute_004_2.outputs[0], reroute_003_3.inputs[0])
    # group_input_9.Alpha -> reroute_004_2.Input
    _rr_lab_to_srgb.links.new(group_input_9.outputs[3], reroute_004_2.inputs[0])
    # combine_color_3.Image -> group_output_10.Image
    _rr_lab_to_srgb.links.new(combine_color_3.outputs[0], group_output_10.inputs[0])

    return _rr_lab_to_srgb


_rr_lab_to_srgb = _rr_lab_to_srgb_node_group()

def _rr_lab_adjustments_node_group():
    """Initialize .RR_LAB_adjustments node group"""
    _rr_lab_adjustments = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_LAB_adjustments")

    _rr_lab_adjustments.color_tag = 'NONE'
    _rr_lab_adjustments.description = ""
    _rr_lab_adjustments.default_group_node_width = 140
    # _rr_lab_adjustments interface

    # Socket A
    a_socket_2 = _rr_lab_adjustments.interface.new_socket(name="A", in_out='OUTPUT', socket_type='NodeSocketFloat')
    a_socket_2.default_value = 0.0
    a_socket_2.min_value = -3.4028234663852886e+38
    a_socket_2.max_value = 3.4028234663852886e+38
    a_socket_2.subtype = 'NONE'
    a_socket_2.attribute_domain = 'POINT'
    a_socket_2.default_input = 'VALUE'
    a_socket_2.structure_type = 'AUTO'

    # Socket B
    b_socket_2 = _rr_lab_adjustments.interface.new_socket(name="B", in_out='OUTPUT', socket_type='NodeSocketFloat')
    b_socket_2.default_value = 0.0
    b_socket_2.min_value = -3.4028234663852886e+38
    b_socket_2.max_value = 3.4028234663852886e+38
    b_socket_2.subtype = 'NONE'
    b_socket_2.attribute_domain = 'POINT'
    b_socket_2.default_input = 'VALUE'
    b_socket_2.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_4 = _rr_lab_adjustments.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_4.default_value = 1.0
    factor_socket_4.min_value = 0.0
    factor_socket_4.max_value = 1.0
    factor_socket_4.subtype = 'FACTOR'
    factor_socket_4.attribute_domain = 'POINT'
    factor_socket_4.default_input = 'VALUE'
    factor_socket_4.structure_type = 'AUTO'

    # Socket A
    a_socket_3 = _rr_lab_adjustments.interface.new_socket(name="A", in_out='INPUT', socket_type='NodeSocketFloat')
    a_socket_3.default_value = 0.5
    a_socket_3.min_value = -10000.0
    a_socket_3.max_value = 10000.0
    a_socket_3.subtype = 'NONE'
    a_socket_3.attribute_domain = 'POINT'
    a_socket_3.hide_value = True
    a_socket_3.default_input = 'VALUE'
    a_socket_3.structure_type = 'AUTO'

    # Socket B
    b_socket_3 = _rr_lab_adjustments.interface.new_socket(name="B", in_out='INPUT', socket_type='NodeSocketFloat')
    b_socket_3.default_value = 0.5
    b_socket_3.min_value = -10000.0
    b_socket_3.max_value = 10000.0
    b_socket_3.subtype = 'NONE'
    b_socket_3.attribute_domain = 'POINT'
    b_socket_3.hide_value = True
    b_socket_3.default_input = 'VALUE'
    b_socket_3.structure_type = 'AUTO'

    # Socket Hue
    hue_socket_1 = _rr_lab_adjustments.interface.new_socket(name="Hue", in_out='INPUT', socket_type='NodeSocketFloat')
    hue_socket_1.default_value = 0.0
    hue_socket_1.min_value = -10000.0
    hue_socket_1.max_value = 10000.0
    hue_socket_1.subtype = 'NONE'
    hue_socket_1.attribute_domain = 'POINT'
    hue_socket_1.default_input = 'VALUE'
    hue_socket_1.structure_type = 'AUTO'

    # Socket Chroma
    chroma_socket = _rr_lab_adjustments.interface.new_socket(name="Chroma", in_out='INPUT', socket_type='NodeSocketFloat')
    chroma_socket.default_value = 0.3400000333786011
    chroma_socket.min_value = -10000.0
    chroma_socket.max_value = 10000.0
    chroma_socket.subtype = 'NONE'
    chroma_socket.attribute_domain = 'POINT'
    chroma_socket.default_input = 'VALUE'
    chroma_socket.structure_type = 'AUTO'

    # Initialize _rr_lab_adjustments nodes

    # Node Frame
    frame_9 = _rr_lab_adjustments.nodes.new("NodeFrame")
    frame_9.label = "Chroma"
    frame_9.name = "Frame"
    frame_9.label_size = 20
    frame_9.shrink = True

    # Node Frame.001
    frame_001_6 = _rr_lab_adjustments.nodes.new("NodeFrame")
    frame_001_6.label = "Hue (degrees)"
    frame_001_6.name = "Frame.001"
    frame_001_6.label_size = 20
    frame_001_6.shrink = True

    # Node Frame.002
    frame_002_5 = _rr_lab_adjustments.nodes.new("NodeFrame")
    frame_002_5.label = " "
    frame_002_5.name = "Frame.002"
    frame_002_5.label_size = 20
    frame_002_5.shrink = True

    # Node Math.003
    math_003_8 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_003_8.name = "Math.003"
    math_003_8.hide = True
    math_003_8.operation = 'ADD'
    math_003_8.use_clamp = False

    # Node Math.002
    math_002_8 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_002_8.name = "Math.002"
    math_002_8.hide = True
    math_002_8.operation = 'SQRT'
    math_002_8.use_clamp = False

    # Node Math
    math_10 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_10.label = "Square"
    math_10.name = "Math"
    math_10.hide = True
    math_10.operation = 'POWER'
    math_10.use_clamp = False
    # Value_001
    math_10.inputs[1].default_value = 2.0

    # Node Math.001
    math_001_7 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_001_7.label = "Square"
    math_001_7.name = "Math.001"
    math_001_7.hide = True
    math_001_7.operation = 'POWER'
    math_001_7.use_clamp = False
    # Value_001
    math_001_7.inputs[1].default_value = 2.0

    # Node Group Output
    group_output_11 = _rr_lab_adjustments.nodes.new("NodeGroupOutput")
    group_output_11.name = "Group Output"
    group_output_11.is_active_output = True

    # Node Math.006
    math_006_7 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_006_7.name = "Math.006"
    math_006_7.operation = 'ARCTAN2'
    math_006_7.use_clamp = False

    # Node Group Input
    group_input_10 = _rr_lab_adjustments.nodes.new("NodeGroupInput")
    group_input_10.name = "Group Input"

    # Node Reroute
    reroute_7 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_7.name = "Reroute"
    reroute_7.socket_idname = "NodeSocketFloat"
    # Node Reroute.001
    reroute_001_5 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_001_5.name = "Reroute.001"
    reroute_001_5.socket_idname = "NodeSocketFloat"
    # Node Math.004
    math_004_8 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_004_8.name = "Math.004"
    math_004_8.hide = True
    math_004_8.operation = 'MULTIPLY'
    math_004_8.use_clamp = False

    # Node Math.005
    math_005_7 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_005_7.name = "Math.005"
    math_005_7.hide = True
    math_005_7.operation = 'COSINE'
    math_005_7.use_clamp = False

    # Node Math.007
    math_007_7 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_007_7.name = "Math.007"
    math_007_7.hide = True
    math_007_7.operation = 'SINE'
    math_007_7.use_clamp = False

    # Node Math.008
    math_008_6 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_008_6.name = "Math.008"
    math_008_6.hide = True
    math_008_6.operation = 'MULTIPLY'
    math_008_6.use_clamp = False

    # Node Math.009
    math_009_4 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_009_4.name = "Math.009"
    math_009_4.operation = 'MULTIPLY'
    math_009_4.use_clamp = False

    # Node Math.010
    math_010_3 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_010_3.name = "Math.010"
    math_010_3.hide = True
    math_010_3.operation = 'MULTIPLY'
    math_010_3.use_clamp = False

    # Node Math.011
    math_011_3 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_011_3.name = "Math.011"
    math_011_3.hide = True
    math_011_3.operation = 'COSINE'
    math_011_3.use_clamp = False

    # Node Math.012
    math_012_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_012_2.name = "Math.012"
    math_012_2.hide = True
    math_012_2.operation = 'SUBTRACT'
    math_012_2.use_clamp = False

    # Node Math.013
    math_013_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_013_2.name = "Math.013"
    math_013_2.hide = True
    math_013_2.operation = 'MULTIPLY'
    math_013_2.use_clamp = False

    # Node Math.014
    math_014_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_014_2.name = "Math.014"
    math_014_2.hide = True
    math_014_2.operation = 'SINE'
    math_014_2.use_clamp = False

    # Node Math.015
    math_015_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_015_2.name = "Math.015"
    math_015_2.hide = True
    math_015_2.operation = 'MULTIPLY'
    math_015_2.use_clamp = False

    # Node Math.016
    math_016_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_016_2.name = "Math.016"
    math_016_2.hide = True
    math_016_2.operation = 'ADD'
    math_016_2.use_clamp = False

    # Node Math.017
    math_017_2 = _rr_lab_adjustments.nodes.new("ShaderNodeMath")
    math_017_2.name = "Math.017"
    math_017_2.hide = True
    math_017_2.operation = 'MULTIPLY'
    math_017_2.use_clamp = False

    # Node Reroute.002
    reroute_002_4 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_002_4.name = "Reroute.002"
    reroute_002_4.socket_idname = "NodeSocketFloat"
    # Node Reroute.003
    reroute_003_4 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_003_4.name = "Reroute.003"
    reroute_003_4.socket_idname = "NodeSocketFloat"
    # Node Frame.003
    frame_003_4 = _rr_lab_adjustments.nodes.new("NodeFrame")
    frame_003_4.label = "Rotate Hue"
    frame_003_4.name = "Frame.003"
    frame_003_4.label_size = 20
    frame_003_4.shrink = True

    # Node Mix
    mix_6 = _rr_lab_adjustments.nodes.new("ShaderNodeMix")
    mix_6.name = "Mix"
    mix_6.blend_type = 'MIX'
    mix_6.clamp_factor = True
    mix_6.clamp_result = False
    mix_6.data_type = 'FLOAT'
    mix_6.factor_mode = 'UNIFORM'

    # Node Reroute.004
    reroute_004_3 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_004_3.name = "Reroute.004"
    reroute_004_3.socket_idname = "NodeSocketFloat"
    # Node Reroute.005
    reroute_005_4 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_005_4.name = "Reroute.005"
    reroute_005_4.socket_idname = "NodeSocketFloat"
    # Node Mix.001
    mix_001_3 = _rr_lab_adjustments.nodes.new("ShaderNodeMix")
    mix_001_3.name = "Mix.001"
    mix_001_3.blend_type = 'MIX'
    mix_001_3.clamp_factor = True
    mix_001_3.clamp_result = False
    mix_001_3.data_type = 'FLOAT'
    mix_001_3.factor_mode = 'UNIFORM'

    # Node Reroute.006
    reroute_006_1 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_006_1.name = "Reroute.006"
    reroute_006_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.007
    reroute_007_1 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_007_1.name = "Reroute.007"
    reroute_007_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.008
    reroute_008 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_008.name = "Reroute.008"
    reroute_008.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.009
    reroute_009 = _rr_lab_adjustments.nodes.new("NodeReroute")
    reroute_009.name = "Reroute.009"
    reroute_009.socket_idname = "NodeSocketFloatFactor"
    # Set parents
    math_003_8.parent = frame_9
    math_002_8.parent = frame_9
    math_10.parent = frame_9
    math_001_7.parent = frame_9
    math_006_7.parent = frame_001_6
    reroute_7.parent = frame_002_5
    reroute_001_5.parent = frame_002_5
    math_004_8.parent = frame_002_5
    math_005_7.parent = frame_002_5
    math_007_7.parent = frame_002_5
    math_008_6.parent = frame_002_5
    math_010_3.parent = frame_003_4
    math_011_3.parent = frame_003_4
    math_012_2.parent = frame_003_4
    math_013_2.parent = frame_003_4
    math_014_2.parent = frame_003_4
    math_015_2.parent = frame_003_4
    math_016_2.parent = frame_003_4
    math_017_2.parent = frame_003_4
    reroute_002_4.parent = frame_003_4
    reroute_003_4.parent = frame_003_4

    # Set locations
    frame_9.location = (-220.6800079345703, 66.61199951171875)
    frame_001_6.location = (457.5600280761719, -294.64801025390625)
    frame_002_5.location = (765.9625244140625, 37.09199905395508)
    math_003_8.location = (223.88294982910156, -63.618499755859375)
    math_002_8.location = (412.1392822265625, -63.61848449707031)
    math_10.location = (29.220748901367188, -41.00346374511719)
    math_001_7.location = (29.220748901367188, -92.22053527832031)
    group_output_11.location = (1955.6053466796875, 16.430662155151367)
    math_006_7.location = (29.22265625, -35.855010986328125)
    group_input_10.location = (-1029.1424560546875, -95.63964080810547)
    reroute_7.location = (35.56158447265625, -221.5614013671875)
    reroute_001_5.location = (34.02001953125, -45.79140090942383)
    math_004_8.location = (362.376953125, -40.5706672668457)
    math_005_7.location = (196.1395263671875, -72.24894714355469)
    math_007_7.location = (196.13946533203125, -211.33984375)
    math_008_6.location = (363.2362060546875, -170.20765686035156)
    math_009_4.location = (561.8677978515625, 100.21451568603516)
    math_010_3.location = (368.0252380371094, -164.50880432128906)
    math_011_3.location = (29.365753173828125, -160.16209411621094)
    math_012_2.location = (555.4493408203125, -196.75355529785156)
    math_013_2.location = (365.1285095214844, -234.64527893066406)
    math_014_2.location = (29.378753662109375, -232.1868438720703)
    math_015_2.location = (370.1569519042969, -40.56343078613281)
    math_016_2.location = (552.4456787109375, -62.48207092285156)
    math_017_2.location = (375.4714660644531, -96.29624938964844)
    reroute_002_4.location = (168.88873291015625, -108.50080871582031)
    reroute_003_4.location = (168.99867248535156, -45.22593688964844)
    frame_003_4.location = (-345.96002197265625, -251.6280059814453)
    mix_6.location = (1580.2659912109375, 158.045166015625)
    reroute_004_3.location = (1328.477294921875, 187.41981506347656)
    reroute_005_4.location = (-310.5168762207031, 189.6441650390625)
    mix_001_3.location = (1580.6181640625, -29.750816345214844)
    reroute_006_1.location = (1328.25927734375, 146.64907836914062)
    reroute_007_1.location = (-305.55035400390625, 150.51336669921875)
    reroute_008.location = (-312.366455078125, 230.40139770507812)
    reroute_009.location = (1328.0594482421875, 232.66372680664062)

    # Set dimensions
    frame_9.width, frame_9.height = 581.3600463867188, 145.99200439453125
    frame_001_6.width, frame_001_6.height = 198.31997680664062, 206.11199951171875
    frame_002_5.width, frame_002_5.height = 532.1575927734375, 264.7920227050781
    math_003_8.width, math_003_8.height = 140.0, 100.0
    math_002_8.width, math_002_8.height = 140.0, 100.0
    math_10.width, math_10.height = 140.0, 100.0
    math_001_7.width, math_001_7.height = 140.0, 100.0
    group_output_11.width, group_output_11.height = 140.0, 100.0
    math_006_7.width, math_006_7.height = 140.0, 100.0
    group_input_10.width, group_input_10.height = 140.0, 100.0
    reroute_7.width, reroute_7.height = 13.5, 100.0
    reroute_001_5.width, reroute_001_5.height = 13.5, 100.0
    math_004_8.width, math_004_8.height = 140.0, 100.0
    math_005_7.width, math_005_7.height = 140.0, 100.0
    math_007_7.width, math_007_7.height = 140.0, 100.0
    math_008_6.width, math_008_6.height = 140.0, 100.0
    math_009_4.width, math_009_4.height = 140.0, 100.0
    math_010_3.width, math_010_3.height = 140.0, 100.0
    math_011_3.width, math_011_3.height = 140.0, 100.0
    math_012_2.width, math_012_2.height = 140.0, 100.0
    math_013_2.width, math_013_2.height = 140.0, 100.0
    math_014_2.width, math_014_2.height = 140.0, 100.0
    math_015_2.width, math_015_2.height = 140.0, 100.0
    math_016_2.width, math_016_2.height = 140.0, 100.0
    math_017_2.width, math_017_2.height = 140.0, 100.0
    reroute_002_4.width, reroute_002_4.height = 13.5, 100.0
    reroute_003_4.width, reroute_003_4.height = 13.5, 100.0
    frame_003_4.width, frame_003_4.height = 724.6400146484375, 287.83203125
    mix_6.width, mix_6.height = 140.0, 100.0
    reroute_004_3.width, reroute_004_3.height = 13.5, 100.0
    reroute_005_4.width, reroute_005_4.height = 13.5, 100.0
    mix_001_3.width, mix_001_3.height = 140.0, 100.0
    reroute_006_1.width, reroute_006_1.height = 13.5, 100.0
    reroute_007_1.width, reroute_007_1.height = 13.5, 100.0
    reroute_008.width, reroute_008.height = 13.5, 100.0
    reroute_009.width, reroute_009.height = 13.5, 100.0

    # Initialize _rr_lab_adjustments links

    # math_001_7.Value -> math_003_8.Value
    _rr_lab_adjustments.links.new(math_001_7.outputs[0], math_003_8.inputs[1])
    # math_003_8.Value -> math_002_8.Value
    _rr_lab_adjustments.links.new(math_003_8.outputs[0], math_002_8.inputs[0])
    # math_10.Value -> math_003_8.Value
    _rr_lab_adjustments.links.new(math_10.outputs[0], math_003_8.inputs[0])
    # group_input_10.A -> math_10.Value
    _rr_lab_adjustments.links.new(group_input_10.outputs[1], math_10.inputs[0])
    # group_input_10.B -> math_001_7.Value
    _rr_lab_adjustments.links.new(group_input_10.outputs[2], math_001_7.inputs[0])
    # reroute_001_5.Output -> math_004_8.Value
    _rr_lab_adjustments.links.new(reroute_001_5.outputs[0], math_004_8.inputs[0])
    # math_005_7.Value -> math_004_8.Value
    _rr_lab_adjustments.links.new(math_005_7.outputs[0], math_004_8.inputs[1])
    # reroute_7.Output -> math_005_7.Value
    _rr_lab_adjustments.links.new(reroute_7.outputs[0], math_005_7.inputs[0])
    # reroute_001_5.Output -> math_008_6.Value
    _rr_lab_adjustments.links.new(reroute_001_5.outputs[0], math_008_6.inputs[0])
    # math_007_7.Value -> math_008_6.Value
    _rr_lab_adjustments.links.new(math_007_7.outputs[0], math_008_6.inputs[1])
    # reroute_7.Output -> math_007_7.Value
    _rr_lab_adjustments.links.new(reroute_7.outputs[0], math_007_7.inputs[0])
    # math_006_7.Value -> reroute_7.Input
    _rr_lab_adjustments.links.new(math_006_7.outputs[0], reroute_7.inputs[0])
    # mix_001_3.Result -> group_output_11.B
    _rr_lab_adjustments.links.new(mix_001_3.outputs[0], group_output_11.inputs[1])
    # math_002_8.Value -> math_009_4.Value
    _rr_lab_adjustments.links.new(math_002_8.outputs[0], math_009_4.inputs[0])
    # math_009_4.Value -> reroute_001_5.Input
    _rr_lab_adjustments.links.new(math_009_4.outputs[0], reroute_001_5.inputs[0])
    # group_input_10.Chroma -> math_009_4.Value
    _rr_lab_adjustments.links.new(group_input_10.outputs[4], math_009_4.inputs[1])
    # reroute_003_4.Output -> math_010_3.Value
    _rr_lab_adjustments.links.new(reroute_003_4.outputs[0], math_010_3.inputs[0])
    # math_011_3.Value -> math_010_3.Value
    _rr_lab_adjustments.links.new(math_011_3.outputs[0], math_010_3.inputs[1])
    # math_010_3.Value -> math_012_2.Value
    _rr_lab_adjustments.links.new(math_010_3.outputs[0], math_012_2.inputs[0])
    # math_014_2.Value -> math_013_2.Value
    _rr_lab_adjustments.links.new(math_014_2.outputs[0], math_013_2.inputs[1])
    # reroute_002_4.Output -> math_013_2.Value
    _rr_lab_adjustments.links.new(reroute_002_4.outputs[0], math_013_2.inputs[0])
    # math_013_2.Value -> math_012_2.Value
    _rr_lab_adjustments.links.new(math_013_2.outputs[0], math_012_2.inputs[1])
    # group_input_10.Hue -> math_011_3.Value
    _rr_lab_adjustments.links.new(group_input_10.outputs[3], math_011_3.inputs[0])
    # group_input_10.Hue -> math_014_2.Value
    _rr_lab_adjustments.links.new(group_input_10.outputs[3], math_014_2.inputs[0])
    # math_012_2.Value -> math_006_7.Value
    _rr_lab_adjustments.links.new(math_012_2.outputs[0], math_006_7.inputs[1])
    # reroute_003_4.Output -> math_015_2.Value
    _rr_lab_adjustments.links.new(reroute_003_4.outputs[0], math_015_2.inputs[0])
    # math_014_2.Value -> math_015_2.Value
    _rr_lab_adjustments.links.new(math_014_2.outputs[0], math_015_2.inputs[1])
    # math_015_2.Value -> math_016_2.Value
    _rr_lab_adjustments.links.new(math_015_2.outputs[0], math_016_2.inputs[0])
    # reroute_002_4.Output -> math_017_2.Value
    _rr_lab_adjustments.links.new(reroute_002_4.outputs[0], math_017_2.inputs[0])
    # math_011_3.Value -> math_017_2.Value
    _rr_lab_adjustments.links.new(math_011_3.outputs[0], math_017_2.inputs[1])
    # math_017_2.Value -> math_016_2.Value
    _rr_lab_adjustments.links.new(math_017_2.outputs[0], math_016_2.inputs[1])
    # math_016_2.Value -> math_006_7.Value
    _rr_lab_adjustments.links.new(math_016_2.outputs[0], math_006_7.inputs[0])
    # group_input_10.B -> reroute_002_4.Input
    _rr_lab_adjustments.links.new(group_input_10.outputs[2], reroute_002_4.inputs[0])
    # group_input_10.A -> reroute_003_4.Input
    _rr_lab_adjustments.links.new(group_input_10.outputs[1], reroute_003_4.inputs[0])
    # math_004_8.Value -> mix_6.B
    _rr_lab_adjustments.links.new(math_004_8.outputs[0], mix_6.inputs[3])
    # reroute_004_3.Output -> mix_6.A
    _rr_lab_adjustments.links.new(reroute_004_3.outputs[0], mix_6.inputs[2])
    # reroute_005_4.Output -> reroute_004_3.Input
    _rr_lab_adjustments.links.new(reroute_005_4.outputs[0], reroute_004_3.inputs[0])
    # group_input_10.A -> reroute_005_4.Input
    _rr_lab_adjustments.links.new(group_input_10.outputs[1], reroute_005_4.inputs[0])
    # math_008_6.Value -> mix_001_3.B
    _rr_lab_adjustments.links.new(math_008_6.outputs[0], mix_001_3.inputs[3])
    # reroute_006_1.Output -> mix_001_3.A
    _rr_lab_adjustments.links.new(reroute_006_1.outputs[0], mix_001_3.inputs[2])
    # reroute_007_1.Output -> reroute_006_1.Input
    _rr_lab_adjustments.links.new(reroute_007_1.outputs[0], reroute_006_1.inputs[0])
    # group_input_10.B -> reroute_007_1.Input
    _rr_lab_adjustments.links.new(group_input_10.outputs[2], reroute_007_1.inputs[0])
    # mix_6.Result -> group_output_11.A
    _rr_lab_adjustments.links.new(mix_6.outputs[0], group_output_11.inputs[0])
    # reroute_009.Output -> mix_6.Factor
    _rr_lab_adjustments.links.new(reroute_009.outputs[0], mix_6.inputs[0])
    # reroute_009.Output -> mix_001_3.Factor
    _rr_lab_adjustments.links.new(reroute_009.outputs[0], mix_001_3.inputs[0])
    # group_input_10.Factor -> reroute_008.Input
    _rr_lab_adjustments.links.new(group_input_10.outputs[0], reroute_008.inputs[0])
    # reroute_008.Output -> reroute_009.Input
    _rr_lab_adjustments.links.new(reroute_008.outputs[0], reroute_009.inputs[0])

    return _rr_lab_adjustments


_rr_lab_adjustments = _rr_lab_adjustments_node_group()

def _rr_adjust_mask_node_group():
    """Initialize .RR_adjust_mask node group"""
    _rr_adjust_mask = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_adjust_mask")

    _rr_adjust_mask.color_tag = 'NONE'
    _rr_adjust_mask.description = ""
    _rr_adjust_mask.default_group_node_width = 140
    # _rr_adjust_mask interface

    # Socket Result
    result_socket = _rr_adjust_mask.interface.new_socket(name="Result", in_out='OUTPUT', socket_type='NodeSocketFloat')
    result_socket.default_value = 0.0
    result_socket.min_value = -3.4028234663852886e+38
    result_socket.max_value = 3.4028234663852886e+38
    result_socket.subtype = 'NONE'
    result_socket.attribute_domain = 'POINT'
    result_socket.default_input = 'VALUE'
    result_socket.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_5 = _rr_adjust_mask.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_5.default_value = 0.5
    factor_socket_5.min_value = 0.0
    factor_socket_5.max_value = 1.0
    factor_socket_5.subtype = 'FACTOR'
    factor_socket_5.attribute_domain = 'POINT'
    factor_socket_5.default_input = 'VALUE'
    factor_socket_5.structure_type = 'AUTO'

    # Socket Image
    image_socket_17 = _rr_adjust_mask.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketFloat')
    image_socket_17.default_value = 0.0
    image_socket_17.min_value = -3.4028234663852886e+38
    image_socket_17.max_value = 3.4028234663852886e+38
    image_socket_17.subtype = 'NONE'
    image_socket_17.attribute_domain = 'POINT'
    image_socket_17.default_input = 'VALUE'
    image_socket_17.structure_type = 'AUTO'

    # Socket Multiply
    multiply_socket = _rr_adjust_mask.interface.new_socket(name="Multiply", in_out='INPUT', socket_type='NodeSocketFloat')
    multiply_socket.default_value = 1.0
    multiply_socket.min_value = -10000.0
    multiply_socket.max_value = 10000.0
    multiply_socket.subtype = 'NONE'
    multiply_socket.attribute_domain = 'POINT'
    multiply_socket.default_input = 'VALUE'
    multiply_socket.structure_type = 'AUTO'

    # Socket Add
    add_socket = _rr_adjust_mask.interface.new_socket(name="Add", in_out='INPUT', socket_type='NodeSocketFloat')
    add_socket.default_value = 0.0
    add_socket.min_value = -10000.0
    add_socket.max_value = 10000.0
    add_socket.subtype = 'NONE'
    add_socket.attribute_domain = 'POINT'
    add_socket.default_input = 'VALUE'
    add_socket.structure_type = 'AUTO'

    # Initialize _rr_adjust_mask nodes

    # Node Group Output
    group_output_12 = _rr_adjust_mask.nodes.new("NodeGroupOutput")
    group_output_12.name = "Group Output"
    group_output_12.is_active_output = True

    # Node Group Input
    group_input_11 = _rr_adjust_mask.nodes.new("NodeGroupInput")
    group_input_11.name = "Group Input"

    # Node Math.003
    math_003_9 = _rr_adjust_mask.nodes.new("ShaderNodeMath")
    math_003_9.name = "Math.003"
    math_003_9.hide = True
    math_003_9.operation = 'MULTIPLY'
    math_003_9.use_clamp = False

    # Node Mix
    mix_7 = _rr_adjust_mask.nodes.new("ShaderNodeMix")
    mix_7.name = "Mix"
    mix_7.blend_type = 'MIX'
    mix_7.clamp_factor = True
    mix_7.clamp_result = False
    mix_7.data_type = 'FLOAT'
    mix_7.factor_mode = 'UNIFORM'

    # Node Math
    math_11 = _rr_adjust_mask.nodes.new("ShaderNodeMath")
    math_11.name = "Math"
    math_11.hide = True
    math_11.operation = 'ADD'
    math_11.use_clamp = False

    # Set locations
    group_output_12.location = (280.62774658203125, 25.7557315826416)
    group_input_11.location = (-747.2412109375, 19.83364486694336)
    math_003_9.location = (-385.5726318359375, -65.1778793334961)
    mix_7.location = (69.57425689697266, 92.1557388305664)
    math_11.location = (-189.77902221679688, -94.39694213867188)

    # Set dimensions
    group_output_12.width, group_output_12.height = 140.0, 100.0
    group_input_11.width, group_input_11.height = 140.0, 100.0
    math_003_9.width, math_003_9.height = 140.0, 100.0
    mix_7.width, mix_7.height = 140.0, 100.0
    math_11.width, math_11.height = 140.0, 100.0

    # Initialize _rr_adjust_mask links

    # group_input_11.Image -> math_003_9.Value
    _rr_adjust_mask.links.new(group_input_11.outputs[1], math_003_9.inputs[0])
    # group_input_11.Multiply -> math_003_9.Value
    _rr_adjust_mask.links.new(group_input_11.outputs[2], math_003_9.inputs[1])
    # group_input_11.Factor -> mix_7.Factor
    _rr_adjust_mask.links.new(group_input_11.outputs[0], mix_7.inputs[0])
    # mix_7.Result -> group_output_12.Result
    _rr_adjust_mask.links.new(mix_7.outputs[0], group_output_12.inputs[0])
    # group_input_11.Image -> mix_7.A
    _rr_adjust_mask.links.new(group_input_11.outputs[1], mix_7.inputs[2])
    # math_003_9.Value -> math_11.Value
    _rr_adjust_mask.links.new(math_003_9.outputs[0], math_11.inputs[0])
    # math_11.Value -> mix_7.B
    _rr_adjust_mask.links.new(math_11.outputs[0], mix_7.inputs[3])
    # group_input_11.Add -> math_11.Value
    _rr_adjust_mask.links.new(group_input_11.outputs[3], math_11.inputs[1])

    return _rr_adjust_mask


_rr_adjust_mask = _rr_adjust_mask_node_group()

def _rr_flip_mask_node_group():
    """Initialize .RR_flip_mask node group"""
    _rr_flip_mask = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_flip_mask")

    _rr_flip_mask.color_tag = 'NONE'
    _rr_flip_mask.description = ""
    _rr_flip_mask.default_group_node_width = 140
    # _rr_flip_mask interface

    # Socket Result
    result_socket_1 = _rr_flip_mask.interface.new_socket(name="Result", in_out='OUTPUT', socket_type='NodeSocketFloat')
    result_socket_1.default_value = 0.0
    result_socket_1.min_value = -3.4028234663852886e+38
    result_socket_1.max_value = 3.4028234663852886e+38
    result_socket_1.subtype = 'NONE'
    result_socket_1.attribute_domain = 'POINT'
    result_socket_1.default_input = 'VALUE'
    result_socket_1.structure_type = 'AUTO'

    # Socket Value
    value_socket_2 = _rr_flip_mask.interface.new_socket(name="Value", in_out='INPUT', socket_type='NodeSocketFloat')
    value_socket_2.default_value = 0.0
    value_socket_2.min_value = -1.0
    value_socket_2.max_value = 1.0
    value_socket_2.subtype = 'FACTOR'
    value_socket_2.attribute_domain = 'POINT'
    value_socket_2.default_input = 'VALUE'
    value_socket_2.structure_type = 'AUTO'

    # Socket Mask
    mask_socket_3 = _rr_flip_mask.interface.new_socket(name="Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    mask_socket_3.default_value = 0.0
    mask_socket_3.min_value = 0.0
    mask_socket_3.max_value = 1.0
    mask_socket_3.subtype = 'NONE'
    mask_socket_3.attribute_domain = 'POINT'
    mask_socket_3.default_input = 'VALUE'
    mask_socket_3.structure_type = 'AUTO'

    # Initialize _rr_flip_mask nodes

    # Node Group Output
    group_output_13 = _rr_flip_mask.nodes.new("NodeGroupOutput")
    group_output_13.name = "Group Output"
    group_output_13.is_active_output = True

    # Node Group Input
    group_input_12 = _rr_flip_mask.nodes.new("NodeGroupInput")
    group_input_12.name = "Group Input"

    # Node Map Range.008
    map_range_008 = _rr_flip_mask.nodes.new("ShaderNodeMapRange")
    map_range_008.label = "Flip"
    map_range_008.name = "Map Range.008"
    map_range_008.hide = True
    map_range_008.clamp = False
    map_range_008.data_type = 'FLOAT'
    map_range_008.interpolation_type = 'LINEAR'
    # From Min
    map_range_008.inputs[1].default_value = 0.0
    # From Max
    map_range_008.inputs[2].default_value = 1.0
    # To Min
    map_range_008.inputs[3].default_value = 1.0
    # To Max
    map_range_008.inputs[4].default_value = 0.0

    # Node Map Range.009
    map_range_009 = _rr_flip_mask.nodes.new("ShaderNodeMapRange")
    map_range_009.name = "Map Range.009"
    map_range_009.clamp = True
    map_range_009.data_type = 'FLOAT'
    map_range_009.interpolation_type = 'LINEAR'
    # From Min
    map_range_009.inputs[1].default_value = 0.0
    # From Max
    map_range_009.inputs[2].default_value = 1.0
    # To Min
    map_range_009.inputs[3].default_value = 1.0

    # Node Mix.002
    mix_002_1 = _rr_flip_mask.nodes.new("ShaderNodeMix")
    mix_002_1.name = "Mix.002"
    mix_002_1.blend_type = 'MIX'
    mix_002_1.clamp_factor = True
    mix_002_1.clamp_result = False
    mix_002_1.data_type = 'FLOAT'
    mix_002_1.factor_mode = 'UNIFORM'

    # Node Map Range.013
    map_range_013 = _rr_flip_mask.nodes.new("ShaderNodeMapRange")
    map_range_013.name = "Map Range.013"
    map_range_013.clamp = True
    map_range_013.data_type = 'FLOAT'
    map_range_013.interpolation_type = 'LINEAR'
    # From Min
    map_range_013.inputs[1].default_value = 0.0
    # From Max
    map_range_013.inputs[2].default_value = -1.0
    # To Min
    map_range_013.inputs[3].default_value = 1.0

    # Node Math.005
    math_005_8 = _rr_flip_mask.nodes.new("ShaderNodeMath")
    math_005_8.name = "Math.005"
    math_005_8.operation = 'GREATER_THAN'
    math_005_8.use_clamp = False
    # Value_001
    math_005_8.inputs[1].default_value = 0.0

    # Set locations
    group_output_13.location = (564.521728515625, 157.97665405273438)
    group_input_12.location = (-540.087646484375, -24.414573669433594)
    map_range_008.location = (-97.82568359375, -95.760986328125)
    map_range_009.location = (77.8681640625, -146.4075927734375)
    mix_002_1.location = (357.3046875, 205.1519775390625)
    map_range_013.location = (81.49267578125, 110.5740966796875)
    math_005_8.location = (78.77099609375, 264.67822265625)

    # Set dimensions
    group_output_13.width, group_output_13.height = 140.0, 100.0
    group_input_12.width, group_input_12.height = 140.0, 100.0
    map_range_008.width, map_range_008.height = 140.0, 100.0
    map_range_009.width, map_range_009.height = 140.0, 100.0
    mix_002_1.width, mix_002_1.height = 140.0, 100.0
    map_range_013.width, map_range_013.height = 140.0, 100.0
    math_005_8.width, math_005_8.height = 140.0, 100.0

    # Initialize _rr_flip_mask links

    # group_input_12.Mask -> map_range_008.Value
    _rr_flip_mask.links.new(group_input_12.outputs[1], map_range_008.inputs[0])
    # group_input_12.Value -> map_range_009.Value
    _rr_flip_mask.links.new(group_input_12.outputs[0], map_range_009.inputs[0])
    # map_range_013.Result -> mix_002_1.A
    _rr_flip_mask.links.new(map_range_013.outputs[0], mix_002_1.inputs[2])
    # map_range_008.Result -> map_range_013.To Max
    _rr_flip_mask.links.new(map_range_008.outputs[0], map_range_013.inputs[4])
    # map_range_009.Result -> mix_002_1.B
    _rr_flip_mask.links.new(map_range_009.outputs[0], mix_002_1.inputs[3])
    # group_input_12.Value -> map_range_013.Value
    _rr_flip_mask.links.new(group_input_12.outputs[0], map_range_013.inputs[0])
    # math_005_8.Value -> mix_002_1.Factor
    _rr_flip_mask.links.new(math_005_8.outputs[0], mix_002_1.inputs[0])
    # group_input_12.Mask -> map_range_009.To Max
    _rr_flip_mask.links.new(group_input_12.outputs[1], map_range_009.inputs[4])
    # group_input_12.Value -> math_005_8.Value
    _rr_flip_mask.links.new(group_input_12.outputs[0], math_005_8.inputs[0])
    # mix_002_1.Result -> group_output_13.Result
    _rr_flip_mask.links.new(mix_002_1.outputs[0], group_output_13.inputs[0])

    return _rr_flip_mask


_rr_flip_mask = _rr_flip_mask_node_group()

def _rr_hue_correct_pre_node_group():
    """Initialize .RR_hue_correct_pre node group"""
    _rr_hue_correct_pre = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_hue_correct_pre")

    _rr_hue_correct_pre.color_tag = 'NONE'
    _rr_hue_correct_pre.description = ""
    _rr_hue_correct_pre.default_group_node_width = 140
    # _rr_hue_correct_pre interface

    # Socket Image
    image_socket_18 = _rr_hue_correct_pre.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_18.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_18.attribute_domain = 'POINT'
    image_socket_18.default_input = 'VALUE'
    image_socket_18.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_6 = _rr_hue_correct_pre.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_6.default_value = 1.0
    factor_socket_6.min_value = 0.0
    factor_socket_6.max_value = 1.0
    factor_socket_6.subtype = 'FACTOR'
    factor_socket_6.attribute_domain = 'POINT'
    factor_socket_6.default_input = 'VALUE'
    factor_socket_6.structure_type = 'AUTO'

    # Socket Input
    input_socket = _rr_hue_correct_pre.interface.new_socket(name="Input", in_out='INPUT', socket_type='NodeSocketColor')
    input_socket.default_value = (0.0, 0.0, 0.0, 1.0)
    input_socket.attribute_domain = 'POINT'
    input_socket.default_input = 'VALUE'
    input_socket.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket_3 = _rr_hue_correct_pre.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket_3.default_value = 1.0
    perceptual_socket_3.min_value = 0.0
    perceptual_socket_3.max_value = 1.0
    perceptual_socket_3.subtype = 'FACTOR'
    perceptual_socket_3.attribute_domain = 'POINT'
    perceptual_socket_3.default_input = 'VALUE'
    perceptual_socket_3.structure_type = 'AUTO'

    # Socket Range
    range_socket_1 = _rr_hue_correct_pre.interface.new_socket(name="Range", in_out='INPUT', socket_type='NodeSocketFloat')
    range_socket_1.default_value = 0.20000000298023224
    range_socket_1.min_value = 0.0
    range_socket_1.max_value = 1.0
    range_socket_1.subtype = 'FACTOR'
    range_socket_1.attribute_domain = 'POINT'
    range_socket_1.default_input = 'VALUE'
    range_socket_1.structure_type = 'AUTO'

    # Socket Smoothing
    smoothing_socket_1 = _rr_hue_correct_pre.interface.new_socket(name="Smoothing", in_out='INPUT', socket_type='NodeSocketFloat')
    smoothing_socket_1.default_value = 0.0
    smoothing_socket_1.min_value = 0.0
    smoothing_socket_1.max_value = 1.0
    smoothing_socket_1.subtype = 'FACTOR'
    smoothing_socket_1.attribute_domain = 'POINT'
    smoothing_socket_1.default_input = 'VALUE'
    smoothing_socket_1.structure_type = 'AUTO'

    # Socket Saturation Mask
    saturation_mask_socket = _rr_hue_correct_pre.interface.new_socket(name="Saturation Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_mask_socket.default_value = 1.0
    saturation_mask_socket.min_value = -1.0
    saturation_mask_socket.max_value = 1.0
    saturation_mask_socket.subtype = 'FACTOR'
    saturation_mask_socket.attribute_domain = 'POINT'
    saturation_mask_socket.default_input = 'VALUE'
    saturation_mask_socket.structure_type = 'AUTO'

    # Socket Value Mask
    value_mask_socket = _rr_hue_correct_pre.interface.new_socket(name="Value Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    value_mask_socket.default_value = 0.0
    value_mask_socket.min_value = -1.0
    value_mask_socket.max_value = 1.0
    value_mask_socket.subtype = 'FACTOR'
    value_mask_socket.attribute_domain = 'POINT'
    value_mask_socket.default_input = 'VALUE'
    value_mask_socket.structure_type = 'AUTO'

    # Panel Hue
    hue_panel = _rr_hue_correct_pre.interface.new_panel("Hue")
    # Socket Red Hue
    red_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Red Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    red_hue_socket.default_value = 0.5
    red_hue_socket.min_value = 0.0
    red_hue_socket.max_value = 1.0
    red_hue_socket.subtype = 'FACTOR'
    red_hue_socket.attribute_domain = 'POINT'
    red_hue_socket.default_input = 'VALUE'
    red_hue_socket.structure_type = 'AUTO'

    # Socket Orange Hue
    orange_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Orange Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    orange_hue_socket.default_value = 0.5
    orange_hue_socket.min_value = 0.0
    orange_hue_socket.max_value = 1.0
    orange_hue_socket.subtype = 'FACTOR'
    orange_hue_socket.attribute_domain = 'POINT'
    orange_hue_socket.default_input = 'VALUE'
    orange_hue_socket.structure_type = 'AUTO'

    # Socket Yellow Hue
    yellow_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Yellow Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    yellow_hue_socket.default_value = 0.5
    yellow_hue_socket.min_value = 0.0
    yellow_hue_socket.max_value = 1.0
    yellow_hue_socket.subtype = 'FACTOR'
    yellow_hue_socket.attribute_domain = 'POINT'
    yellow_hue_socket.default_input = 'VALUE'
    yellow_hue_socket.structure_type = 'AUTO'

    # Socket Green Hue
    green_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Green Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    green_hue_socket.default_value = 0.5
    green_hue_socket.min_value = 0.0
    green_hue_socket.max_value = 1.0
    green_hue_socket.subtype = 'FACTOR'
    green_hue_socket.attribute_domain = 'POINT'
    green_hue_socket.default_input = 'VALUE'
    green_hue_socket.structure_type = 'AUTO'

    # Socket Teal Hue
    teal_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Teal Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    teal_hue_socket.default_value = 0.5
    teal_hue_socket.min_value = 0.0
    teal_hue_socket.max_value = 1.0
    teal_hue_socket.subtype = 'FACTOR'
    teal_hue_socket.attribute_domain = 'POINT'
    teal_hue_socket.default_input = 'VALUE'
    teal_hue_socket.structure_type = 'AUTO'

    # Socket Blue Hue
    blue_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Blue Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    blue_hue_socket.default_value = 0.5
    blue_hue_socket.min_value = 0.0
    blue_hue_socket.max_value = 1.0
    blue_hue_socket.subtype = 'FACTOR'
    blue_hue_socket.attribute_domain = 'POINT'
    blue_hue_socket.default_input = 'VALUE'
    blue_hue_socket.structure_type = 'AUTO'

    # Socket Pink Hue
    pink_hue_socket = _rr_hue_correct_pre.interface.new_socket(name="Pink Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel)
    pink_hue_socket.default_value = 0.5
    pink_hue_socket.min_value = 0.0
    pink_hue_socket.max_value = 1.0
    pink_hue_socket.subtype = 'FACTOR'
    pink_hue_socket.attribute_domain = 'POINT'
    pink_hue_socket.default_input = 'VALUE'
    pink_hue_socket.structure_type = 'AUTO'


    # Panel Saturation
    saturation_panel = _rr_hue_correct_pre.interface.new_panel("Saturation")
    # Socket Red Saturation
    red_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Red Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    red_saturation_socket.default_value = 1.0
    red_saturation_socket.min_value = 0.0
    red_saturation_socket.max_value = 2.0
    red_saturation_socket.subtype = 'FACTOR'
    red_saturation_socket.attribute_domain = 'POINT'
    red_saturation_socket.default_input = 'VALUE'
    red_saturation_socket.structure_type = 'AUTO'

    # Socket Orange Saturation
    orange_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Orange Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    orange_saturation_socket.default_value = 1.0
    orange_saturation_socket.min_value = 0.0
    orange_saturation_socket.max_value = 2.0
    orange_saturation_socket.subtype = 'FACTOR'
    orange_saturation_socket.attribute_domain = 'POINT'
    orange_saturation_socket.default_input = 'VALUE'
    orange_saturation_socket.structure_type = 'AUTO'

    # Socket Yellow Saturation
    yellow_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Yellow Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    yellow_saturation_socket.default_value = 1.0
    yellow_saturation_socket.min_value = 0.0
    yellow_saturation_socket.max_value = 2.0
    yellow_saturation_socket.subtype = 'FACTOR'
    yellow_saturation_socket.attribute_domain = 'POINT'
    yellow_saturation_socket.default_input = 'VALUE'
    yellow_saturation_socket.structure_type = 'AUTO'

    # Socket Green Saturation
    green_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Green Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    green_saturation_socket.default_value = 1.0
    green_saturation_socket.min_value = 0.0
    green_saturation_socket.max_value = 2.0
    green_saturation_socket.subtype = 'FACTOR'
    green_saturation_socket.attribute_domain = 'POINT'
    green_saturation_socket.default_input = 'VALUE'
    green_saturation_socket.structure_type = 'AUTO'

    # Socket Teal Saturation
    teal_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Teal Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    teal_saturation_socket.default_value = 1.0
    teal_saturation_socket.min_value = 0.0
    teal_saturation_socket.max_value = 2.0
    teal_saturation_socket.subtype = 'FACTOR'
    teal_saturation_socket.attribute_domain = 'POINT'
    teal_saturation_socket.default_input = 'VALUE'
    teal_saturation_socket.structure_type = 'AUTO'

    # Socket Blue Saturation
    blue_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Blue Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    blue_saturation_socket.default_value = 1.0
    blue_saturation_socket.min_value = 0.0
    blue_saturation_socket.max_value = 2.0
    blue_saturation_socket.subtype = 'FACTOR'
    blue_saturation_socket.attribute_domain = 'POINT'
    blue_saturation_socket.default_input = 'VALUE'
    blue_saturation_socket.structure_type = 'AUTO'

    # Socket Pink Saturation
    pink_saturation_socket = _rr_hue_correct_pre.interface.new_socket(name="Pink Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel)
    pink_saturation_socket.default_value = 1.0
    pink_saturation_socket.min_value = 0.0
    pink_saturation_socket.max_value = 2.0
    pink_saturation_socket.subtype = 'FACTOR'
    pink_saturation_socket.attribute_domain = 'POINT'
    pink_saturation_socket.default_input = 'VALUE'
    pink_saturation_socket.structure_type = 'AUTO'


    # Panel Value
    value_panel = _rr_hue_correct_pre.interface.new_panel("Value")
    # Socket Red Value
    red_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Red Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    red_value_socket.default_value = 1.0
    red_value_socket.min_value = 0.0
    red_value_socket.max_value = 2.0
    red_value_socket.subtype = 'FACTOR'
    red_value_socket.attribute_domain = 'POINT'
    red_value_socket.default_input = 'VALUE'
    red_value_socket.structure_type = 'AUTO'

    # Socket Orange Value
    orange_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Orange Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    orange_value_socket.default_value = 1.0
    orange_value_socket.min_value = 0.0
    orange_value_socket.max_value = 2.0
    orange_value_socket.subtype = 'FACTOR'
    orange_value_socket.attribute_domain = 'POINT'
    orange_value_socket.default_input = 'VALUE'
    orange_value_socket.structure_type = 'AUTO'

    # Socket Yellow Value
    yellow_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Yellow Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    yellow_value_socket.default_value = 1.0
    yellow_value_socket.min_value = 0.0
    yellow_value_socket.max_value = 2.0
    yellow_value_socket.subtype = 'FACTOR'
    yellow_value_socket.attribute_domain = 'POINT'
    yellow_value_socket.default_input = 'VALUE'
    yellow_value_socket.structure_type = 'AUTO'

    # Socket Green Value
    green_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Green Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    green_value_socket.default_value = 1.0
    green_value_socket.min_value = 0.0
    green_value_socket.max_value = 2.0
    green_value_socket.subtype = 'FACTOR'
    green_value_socket.attribute_domain = 'POINT'
    green_value_socket.default_input = 'VALUE'
    green_value_socket.structure_type = 'AUTO'

    # Socket Teal Value
    teal_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Teal Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    teal_value_socket.default_value = 1.0
    teal_value_socket.min_value = 0.0
    teal_value_socket.max_value = 2.0
    teal_value_socket.subtype = 'FACTOR'
    teal_value_socket.attribute_domain = 'POINT'
    teal_value_socket.default_input = 'VALUE'
    teal_value_socket.structure_type = 'AUTO'

    # Socket Blue Value
    blue_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Blue Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    blue_value_socket.default_value = 1.0
    blue_value_socket.min_value = 0.0
    blue_value_socket.max_value = 2.0
    blue_value_socket.subtype = 'FACTOR'
    blue_value_socket.attribute_domain = 'POINT'
    blue_value_socket.default_input = 'VALUE'
    blue_value_socket.structure_type = 'AUTO'

    # Socket Pink Value
    pink_value_socket = _rr_hue_correct_pre.interface.new_socket(name="Pink Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel)
    pink_value_socket.default_value = 1.0
    pink_value_socket.min_value = 0.0
    pink_value_socket.max_value = 2.0
    pink_value_socket.subtype = 'FACTOR'
    pink_value_socket.attribute_domain = 'POINT'
    pink_value_socket.default_input = 'VALUE'
    pink_value_socket.structure_type = 'AUTO'


    # Initialize _rr_hue_correct_pre nodes

    # Node Group Output
    group_output_14 = _rr_hue_correct_pre.nodes.new("NodeGroupOutput")
    group_output_14.name = "Group Output"
    group_output_14.is_active_output = True

    # Node Separate Color
    separate_color_3 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_3.name = "Separate Color"
    separate_color_3.mode = 'HSV'
    separate_color_3.ycc_mode = 'ITUBT709'
    separate_color_3.outputs[0].hide = True
    separate_color_3.outputs[2].hide = True
    separate_color_3.outputs[3].hide = True

    # Node Group Input
    group_input_13 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_13.name = "Group Input"

    # Node Hue Correct
    hue_correct = _rr_hue_correct_pre.nodes.new("CompositorNodeHueCorrect")
    hue_correct.name = "Hue Correct"
    # Mapping settings
    hue_correct.mapping.extend = 'EXTRAPOLATED'
    hue_correct.mapping.tone = 'STANDARD'
    hue_correct.mapping.black_level = (0.0, 0.0, 0.0)
    hue_correct.mapping.white_level = (1.0, 1.0, 1.0)
    hue_correct.mapping.clip_min_x = 0.0
    hue_correct.mapping.clip_min_y = 0.0
    hue_correct.mapping.clip_max_x = 1.0
    hue_correct.mapping.clip_max_y = 1.0
    hue_correct.mapping.use_clip = True
    # Curve 0
    hue_correct_curve_0 = hue_correct.mapping.curves[0]
    for i in range(len(hue_correct_curve_0.points.values()) - 1, 1, -1):
        hue_correct_curve_0.points.remove(hue_correct_curve_0.points[i])
    hue_correct_curve_0_point_0 = hue_correct_curve_0.points[0]
    hue_correct_curve_0_point_0.location = (0.0, 0.5)
    hue_correct_curve_0_point_0.handle_type = 'AUTO'
    hue_correct_curve_0_point_1 = hue_correct_curve_0.points[1]
    hue_correct_curve_0_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_curve_0_point_1.handle_type = 'AUTO'
    hue_correct_curve_0_point_2 = hue_correct_curve_0.points.new(0.16700001060962677, 0.5)
    hue_correct_curve_0_point_2.handle_type = 'AUTO'
    hue_correct_curve_0_point_3 = hue_correct_curve_0.points.new(0.33000001311302185, 0.5)
    hue_correct_curve_0_point_3.handle_type = 'AUTO'
    hue_correct_curve_0_point_4 = hue_correct_curve_0.points.new(0.5, 0.5)
    hue_correct_curve_0_point_4.handle_type = 'AUTO'
    hue_correct_curve_0_point_5 = hue_correct_curve_0.points.new(0.6700000166893005, 0.5)
    hue_correct_curve_0_point_5.handle_type = 'AUTO'
    hue_correct_curve_0_point_6 = hue_correct_curve_0.points.new(0.8399999737739563, 0.5)
    hue_correct_curve_0_point_6.handle_type = 'AUTO'
    hue_correct_curve_0_point_7 = hue_correct_curve_0.points.new(1.0, 0.5)
    hue_correct_curve_0_point_7.handle_type = 'AUTO'
    # Curve 1
    hue_correct_curve_1 = hue_correct.mapping.curves[1]
    for i in range(len(hue_correct_curve_1.points.values()) - 1, 1, -1):
        hue_correct_curve_1.points.remove(hue_correct_curve_1.points[i])
    hue_correct_curve_1_point_0 = hue_correct_curve_1.points[0]
    hue_correct_curve_1_point_0.location = (0.0, 0.5)
    hue_correct_curve_1_point_0.handle_type = 'AUTO'
    hue_correct_curve_1_point_1 = hue_correct_curve_1.points[1]
    hue_correct_curve_1_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_curve_1_point_1.handle_type = 'AUTO'
    hue_correct_curve_1_point_2 = hue_correct_curve_1.points.new(0.16699999570846558, 0.5)
    hue_correct_curve_1_point_2.handle_type = 'AUTO'
    hue_correct_curve_1_point_3 = hue_correct_curve_1.points.new(0.335999995470047, 0.5)
    hue_correct_curve_1_point_3.handle_type = 'AUTO'
    hue_correct_curve_1_point_4 = hue_correct_curve_1.points.new(0.5, 0.5)
    hue_correct_curve_1_point_4.handle_type = 'AUTO'
    hue_correct_curve_1_point_5 = hue_correct_curve_1.points.new(0.6700000166893005, 0.5)
    hue_correct_curve_1_point_5.handle_type = 'AUTO'
    hue_correct_curve_1_point_6 = hue_correct_curve_1.points.new(0.8339999914169312, 0.5)
    hue_correct_curve_1_point_6.handle_type = 'AUTO'
    hue_correct_curve_1_point_7 = hue_correct_curve_1.points.new(1.0, 0.5)
    hue_correct_curve_1_point_7.handle_type = 'AUTO'
    # Curve 2
    hue_correct_curve_2 = hue_correct.mapping.curves[2]
    for i in range(len(hue_correct_curve_2.points.values()) - 1, 1, -1):
        hue_correct_curve_2.points.remove(hue_correct_curve_2.points[i])
    hue_correct_curve_2_point_0 = hue_correct_curve_2.points[0]
    hue_correct_curve_2_point_0.location = (0.0, 0.5)
    hue_correct_curve_2_point_0.handle_type = 'AUTO'
    hue_correct_curve_2_point_1 = hue_correct_curve_2.points[1]
    hue_correct_curve_2_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_curve_2_point_1.handle_type = 'AUTO'
    hue_correct_curve_2_point_2 = hue_correct_curve_2.points.new(0.1679999977350235, 0.5)
    hue_correct_curve_2_point_2.handle_type = 'AUTO'
    hue_correct_curve_2_point_3 = hue_correct_curve_2.points.new(0.335999995470047, 0.5)
    hue_correct_curve_2_point_3.handle_type = 'AUTO'
    hue_correct_curve_2_point_4 = hue_correct_curve_2.points.new(0.5, 0.5)
    hue_correct_curve_2_point_4.handle_type = 'AUTO'
    hue_correct_curve_2_point_5 = hue_correct_curve_2.points.new(0.6690000295639038, 0.5)
    hue_correct_curve_2_point_5.handle_type = 'AUTO'
    hue_correct_curve_2_point_6 = hue_correct_curve_2.points.new(0.8330000042915344, 0.5)
    hue_correct_curve_2_point_6.handle_type = 'AUTO'
    hue_correct_curve_2_point_7 = hue_correct_curve_2.points.new(1.0, 0.5)
    hue_correct_curve_2_point_7.handle_type = 'AUTO'
    # Update curve after changes
    hue_correct.mapping.update()

    # Node Separate Color.001
    separate_color_001_3 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_3.name = "Separate Color.001"
    separate_color_001_3.mode = 'HSV'
    separate_color_001_3.ycc_mode = 'ITUBT709'
    separate_color_001_3.outputs[0].hide = True
    separate_color_001_3.outputs[1].hide = True

    # Node Group Input.001
    group_input_001_4 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_001_4.name = "Group Input.001"
    group_input_001_4.outputs[0].hide = True
    group_input_001_4.outputs[2].hide = True
    group_input_001_4.outputs[3].hide = True
    group_input_001_4.outputs[4].hide = True
    group_input_001_4.outputs[5].hide = True
    group_input_001_4.outputs[6].hide = True
    group_input_001_4.outputs[14].hide = True
    group_input_001_4.outputs[15].hide = True
    group_input_001_4.outputs[16].hide = True
    group_input_001_4.outputs[17].hide = True
    group_input_001_4.outputs[18].hide = True
    group_input_001_4.outputs[19].hide = True
    group_input_001_4.outputs[20].hide = True
    group_input_001_4.outputs[21].hide = True
    group_input_001_4.outputs[22].hide = True
    group_input_001_4.outputs[23].hide = True
    group_input_001_4.outputs[24].hide = True
    group_input_001_4.outputs[25].hide = True
    group_input_001_4.outputs[26].hide = True
    group_input_001_4.outputs[27].hide = True
    group_input_001_4.outputs[28].hide = True

    # Node Combine Color
    combine_color_4 = _rr_hue_correct_pre.nodes.new("CompositorNodeCombineColor")
    combine_color_4.name = "Combine Color"
    combine_color_4.mode = 'HSV'
    combine_color_4.ycc_mode = 'ITUBT709'

    # Node Group
    group = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group.label = "Teal"
    group.name = "Group"
    group.node_tree = _rr_mask_value
    # Socket_4
    group.inputs[2].default_value = 0.5

    # Node Group.001
    group_001 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_001.label = "Blue"
    group_001.name = "Group.001"
    group_001.node_tree = _rr_mask_value
    # Socket_4
    group_001.inputs[2].default_value = 0.6700000166893005

    # Node Group.002
    group_002 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_002.label = "Pink"
    group_002.name = "Group.002"
    group_002.node_tree = _rr_mask_value
    # Socket_4
    group_002.inputs[2].default_value = 0.8399999737739563

    # Node Group.004
    group_004 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_004.label = "Red"
    group_004.name = "Group.004"
    group_004.node_tree = _rr_mask_value
    # Socket_4
    group_004.inputs[2].default_value = 0.0

    # Node Group.005
    group_005 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_005.label = "Orange"
    group_005.name = "Group.005"
    group_005.node_tree = _rr_mask_value
    # Socket_4
    group_005.inputs[2].default_value = 0.0949999988079071

    # Node Group.006
    group_006 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_006.label = "Yellow"
    group_006.name = "Group.006"
    group_006.node_tree = _rr_mask_value
    # Socket_4
    group_006.inputs[2].default_value = 0.16699999570846558

    # Node Group.007
    group_007 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_007.label = "Green"
    group_007.name = "Group.007"
    group_007.node_tree = _rr_mask_value
    # Socket_4
    group_007.inputs[2].default_value = 0.33000001311302185

    # Node Math.001
    math_001_8 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_001_8.name = "Math.001"
    math_001_8.operation = 'WRAP'
    math_001_8.use_clamp = False
    # Value_001
    math_001_8.inputs[1].default_value = 1.0
    # Value_002
    math_001_8.inputs[2].default_value = 0.0

    # Node Reroute.001
    reroute_001_6 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_001_6.name = "Reroute.001"
    reroute_001_6.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_5 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_002_5.name = "Reroute.002"
    reroute_002_5.socket_idname = "NodeSocketFloat"
    # Node Frame
    frame_10 = _rr_hue_correct_pre.nodes.new("NodeFrame")
    frame_10.label = "Hue"
    frame_10.name = "Frame"
    frame_10.label_size = 20
    frame_10.shrink = True

    # Node Group Input.002
    group_input_002_2 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_002_2.name = "Group Input.002"
    group_input_002_2.outputs[0].hide = True
    group_input_002_2.outputs[2].hide = True
    group_input_002_2.outputs[3].hide = True
    group_input_002_2.outputs[4].hide = True
    group_input_002_2.outputs[5].hide = True
    group_input_002_2.outputs[6].hide = True
    group_input_002_2.outputs[7].hide = True
    group_input_002_2.outputs[8].hide = True
    group_input_002_2.outputs[9].hide = True
    group_input_002_2.outputs[10].hide = True
    group_input_002_2.outputs[11].hide = True
    group_input_002_2.outputs[12].hide = True
    group_input_002_2.outputs[13].hide = True
    group_input_002_2.outputs[21].hide = True
    group_input_002_2.outputs[22].hide = True
    group_input_002_2.outputs[23].hide = True
    group_input_002_2.outputs[24].hide = True
    group_input_002_2.outputs[25].hide = True
    group_input_002_2.outputs[26].hide = True
    group_input_002_2.outputs[27].hide = True
    group_input_002_2.outputs[28].hide = True

    # Node Reroute.004
    reroute_004_4 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_004_4.name = "Reroute.004"
    reroute_004_4.socket_idname = "NodeSocketFloat"
    # Node Frame.001
    frame_001_7 = _rr_hue_correct_pre.nodes.new("NodeFrame")
    frame_001_7.label = "Saturation"
    frame_001_7.name = "Frame.001"
    frame_001_7.label_size = 20
    frame_001_7.shrink = True

    # Node Reroute
    reroute_8 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_8.name = "Reroute"
    reroute_8.socket_idname = "NodeSocketFloat"
    # Node Clamp
    clamp = _rr_hue_correct_pre.nodes.new("ShaderNodeClamp")
    clamp.name = "Clamp"
    clamp.clamp_type = 'MINMAX'
    # Min
    clamp.inputs[1].default_value = 0.0
    # Max
    clamp.inputs[2].default_value = 1.0

    # Node Group Input.003
    group_input_003_3 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_003_3.name = "Group Input.003"

    # Node Mix.001
    mix_001_4 = _rr_hue_correct_pre.nodes.new("ShaderNodeMix")
    mix_001_4.name = "Mix.001"
    mix_001_4.blend_type = 'MIX'
    mix_001_4.clamp_factor = True
    mix_001_4.clamp_result = False
    mix_001_4.data_type = 'RGBA'
    mix_001_4.factor_mode = 'UNIFORM'

    # Node Group Input.004
    group_input_004_3 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_004_3.name = "Group Input.004"
    group_input_004_3.outputs[3].hide = True
    group_input_004_3.outputs[4].hide = True
    group_input_004_3.outputs[7].hide = True
    group_input_004_3.outputs[8].hide = True
    group_input_004_3.outputs[9].hide = True
    group_input_004_3.outputs[10].hide = True
    group_input_004_3.outputs[11].hide = True
    group_input_004_3.outputs[12].hide = True
    group_input_004_3.outputs[13].hide = True
    group_input_004_3.outputs[14].hide = True
    group_input_004_3.outputs[15].hide = True
    group_input_004_3.outputs[16].hide = True
    group_input_004_3.outputs[17].hide = True
    group_input_004_3.outputs[18].hide = True
    group_input_004_3.outputs[19].hide = True
    group_input_004_3.outputs[20].hide = True
    group_input_004_3.outputs[21].hide = True
    group_input_004_3.outputs[22].hide = True
    group_input_004_3.outputs[23].hide = True
    group_input_004_3.outputs[24].hide = True
    group_input_004_3.outputs[25].hide = True
    group_input_004_3.outputs[26].hide = True
    group_input_004_3.outputs[27].hide = True
    group_input_004_3.outputs[28].hide = True

    # Node Reroute.008
    reroute_008_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_008_1.name = "Reroute.008"
    reroute_008_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.009
    reroute_009_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_009_1.name = "Reroute.009"
    reroute_009_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.010
    reroute_010_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_010_1.name = "Reroute.010"
    reroute_010_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.011
    reroute_011_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_011_1.name = "Reroute.011"
    reroute_011_1.socket_idname = "NodeSocketFloat"
    # Node Frame.002
    frame_002_6 = _rr_hue_correct_pre.nodes.new("NodeFrame")
    frame_002_6.label = "Perceptual"
    frame_002_6.name = "Frame.002"
    frame_002_6.label_size = 20
    frame_002_6.shrink = True

    # Node .sRGB_to_LAB
    _srgb_to_lab = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _srgb_to_lab.name = ".sRGB_to_LAB"
    _srgb_to_lab.node_tree = _rr_srgb_to_lab

    # Node .LAB_to_sRGB
    _lab_to_srgb = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_to_srgb.name = ".LAB_to_sRGB"
    _lab_to_srgb.node_tree = _rr_lab_to_srgb

    # Node Reroute.013
    reroute_013_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_013_1.name = "Reroute.013"
    reroute_013_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.014
    reroute_014 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_014.name = "Reroute.014"
    reroute_014.socket_idname = "NodeSocketFloat"
    # Node .LAB_adjustments.001
    _lab_adjustments_001 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_001.name = ".LAB_adjustments.001"
    _lab_adjustments_001.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.002
    _lab_adjustments_002 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_002.name = ".LAB_adjustments.002"
    _lab_adjustments_002.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.003
    _lab_adjustments_003 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_003.name = ".LAB_adjustments.003"
    _lab_adjustments_003.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.004
    _lab_adjustments_004 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_004.name = ".LAB_adjustments.004"
    _lab_adjustments_004.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.005
    _lab_adjustments_005 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_005.name = ".LAB_adjustments.005"
    _lab_adjustments_005.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.006
    _lab_adjustments_006 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_006.name = ".LAB_adjustments.006"
    _lab_adjustments_006.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.007
    _lab_adjustments_007 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    _lab_adjustments_007.name = ".LAB_adjustments.007"
    _lab_adjustments_007.node_tree = _rr_lab_adjustments

    # Node Switch
    switch_4 = _rr_hue_correct_pre.nodes.new("CompositorNodeSwitch")
    switch_4.name = "Switch"

    # Node Reroute.015
    reroute_015 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_015.name = "Reroute.015"
    reroute_015.socket_idname = "NodeSocketColor"
    # Node Math
    math_12 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_12.name = "Math"
    math_12.operation = 'COMPARE'
    math_12.use_clamp = False
    # Value_001
    math_12.inputs[1].default_value = 1.0
    # Value_002
    math_12.inputs[2].default_value = 0.0010000000474974513

    # Node Math.002
    math_002_9 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_002_9.name = "Math.002"
    math_002_9.operation = 'COMPARE'
    math_002_9.use_clamp = False
    # Value_001
    math_002_9.inputs[1].default_value = 0.0
    # Value_002
    math_002_9.inputs[2].default_value = 0.0010000000474974513

    # Node Switch.001
    switch_001 = _rr_hue_correct_pre.nodes.new("CompositorNodeSwitch")
    switch_001.name = "Switch.001"

    # Node Reroute.016
    reroute_016 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_016.name = "Reroute.016"
    reroute_016.socket_idname = "NodeSocketColor"
    # Node Frame.003
    frame_003_5 = _rr_hue_correct_pre.nodes.new("NodeFrame")
    frame_003_5.label = "Combine"
    frame_003_5.name = "Frame.003"
    frame_003_5.label_size = 20
    frame_003_5.shrink = True

    # Node Group.009
    group_009 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_009.name = "Group.009"
    group_009.node_tree = _rr_adjust_mask
    # Socket_4
    group_009.inputs[3].default_value = 0.0

    # Node Group.010
    group_010 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_010.name = "Group.010"
    group_010.node_tree = _rr_adjust_mask
    # Socket_4
    group_010.inputs[3].default_value = 0.0

    # Node Group.011
    group_011 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_011.name = "Group.011"
    group_011.node_tree = _rr_adjust_mask
    # Socket_4
    group_011.inputs[3].default_value = 0.0

    # Node Group.012
    group_012 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_012.name = "Group.012"
    group_012.node_tree = _rr_adjust_mask
    # Socket_4
    group_012.inputs[3].default_value = 0.0

    # Node Group.013
    group_013 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_013.name = "Group.013"
    group_013.node_tree = _rr_adjust_mask
    # Socket_4
    group_013.inputs[3].default_value = 0.0

    # Node Group.014
    group_014 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_014.name = "Group.014"
    group_014.node_tree = _rr_adjust_mask
    # Socket_4
    group_014.inputs[3].default_value = 0.0

    # Node Group.015
    group_015 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_015.name = "Group.015"
    group_015.node_tree = _rr_adjust_mask
    # Socket_4
    group_015.inputs[3].default_value = 0.0

    # Node Reroute.005
    reroute_005_5 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_005_5.name = "Reroute.005"
    reroute_005_5.socket_idname = "NodeSocketFloat"
    # Node Group.025
    group_025 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_025.name = "Group.025"
    group_025.node_tree = _rr_adjust_mask
    # Socket_0
    group_025.inputs[2].default_value = 1.0

    # Node Group.026
    group_026 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_026.name = "Group.026"
    group_026.node_tree = _rr_adjust_mask
    # Socket_0
    group_026.inputs[2].default_value = 1.0

    # Node Group.027
    group_027 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_027.name = "Group.027"
    group_027.node_tree = _rr_adjust_mask
    # Socket_0
    group_027.inputs[2].default_value = 1.0

    # Node Group.028
    group_028 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_028.name = "Group.028"
    group_028.node_tree = _rr_adjust_mask
    # Socket_0
    group_028.inputs[2].default_value = 1.0

    # Node Group.029
    group_029 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_029.name = "Group.029"
    group_029.node_tree = _rr_adjust_mask
    # Socket_0
    group_029.inputs[2].default_value = 1.0

    # Node Group.030
    group_030 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_030.name = "Group.030"
    group_030.node_tree = _rr_adjust_mask
    # Socket_0
    group_030.inputs[2].default_value = 1.0

    # Node Group.031
    group_031 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_031.name = "Group.031"
    group_031.node_tree = _rr_adjust_mask
    # Socket_0
    group_031.inputs[2].default_value = 1.0

    # Node Reroute.003
    reroute_003_5 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_003_5.name = "Reroute.003"
    reroute_003_5.socket_idname = "NodeSocketColor"
    # Node Map Range
    map_range_7 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_7.name = "Map Range"
    map_range_7.clamp = True
    map_range_7.data_type = 'FLOAT'
    map_range_7.interpolation_type = 'LINEAR'
    # From Min
    map_range_7.inputs[1].default_value = 0.0
    # From Max
    map_range_7.inputs[2].default_value = 1.0
    # To Min
    map_range_7.inputs[3].default_value = -0.5235999822616577
    # To Max
    map_range_7.inputs[4].default_value = 0.5235999822616577

    # Node Map Range.001
    map_range_001_6 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_001_6.label = "To Rad"
    map_range_001_6.name = "Map Range.001"
    map_range_001_6.hide = True
    map_range_001_6.clamp = True
    map_range_001_6.data_type = 'FLOAT'
    map_range_001_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_6.inputs[1].default_value = 0.0
    # From Max
    map_range_001_6.inputs[2].default_value = 1.0
    # To Min
    map_range_001_6.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_001_6.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.002
    map_range_002_5 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_002_5.label = "To Rad"
    map_range_002_5.name = "Map Range.002"
    map_range_002_5.hide = True
    map_range_002_5.clamp = True
    map_range_002_5.data_type = 'FLOAT'
    map_range_002_5.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_5.inputs[1].default_value = 0.0
    # From Max
    map_range_002_5.inputs[2].default_value = 1.0
    # To Min
    map_range_002_5.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_002_5.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.003
    map_range_003_4 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_003_4.label = "To Rad"
    map_range_003_4.name = "Map Range.003"
    map_range_003_4.hide = True
    map_range_003_4.clamp = True
    map_range_003_4.data_type = 'FLOAT'
    map_range_003_4.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_4.inputs[1].default_value = 0.0
    # From Max
    map_range_003_4.inputs[2].default_value = 1.0
    # To Min
    map_range_003_4.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_003_4.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.004
    map_range_004_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_004_2.label = "To Rad"
    map_range_004_2.name = "Map Range.004"
    map_range_004_2.hide = True
    map_range_004_2.clamp = True
    map_range_004_2.data_type = 'FLOAT'
    map_range_004_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_004_2.inputs[1].default_value = 0.0
    # From Max
    map_range_004_2.inputs[2].default_value = 1.0
    # To Min
    map_range_004_2.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_004_2.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.005
    map_range_005_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_005_3.label = "To Rad"
    map_range_005_3.name = "Map Range.005"
    map_range_005_3.hide = True
    map_range_005_3.clamp = True
    map_range_005_3.data_type = 'FLOAT'
    map_range_005_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_3.inputs[1].default_value = 0.0
    # From Max
    map_range_005_3.inputs[2].default_value = 1.0
    # To Min
    map_range_005_3.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_005_3.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.006
    map_range_006_1 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_006_1.label = "To Rad"
    map_range_006_1.name = "Map Range.006"
    map_range_006_1.hide = True
    map_range_006_1.clamp = True
    map_range_006_1.data_type = 'FLOAT'
    map_range_006_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_006_1.inputs[1].default_value = 0.0
    # From Max
    map_range_006_1.inputs[2].default_value = 1.0
    # To Min
    map_range_006_1.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_006_1.inputs[4].default_value = 1.0471975803375244

    # Node Separate Color.004
    separate_color_004_1 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_004_1.name = "Separate Color.004"
    separate_color_004_1.mode = 'HSV'
    separate_color_004_1.ycc_mode = 'ITUBT709'

    # Node Combine Color.001
    combine_color_001_1 = _rr_hue_correct_pre.nodes.new("CompositorNodeCombineColor")
    combine_color_001_1.name = "Combine Color.001"
    combine_color_001_1.mode = 'HSV'
    combine_color_001_1.ycc_mode = 'ITUBT709'

    # Node Clamp.001
    clamp_001 = _rr_hue_correct_pre.nodes.new("ShaderNodeClamp")
    clamp_001.name = "Clamp.001"
    clamp_001.clamp_type = 'MINMAX'
    # Min
    clamp_001.inputs[1].default_value = 0.0
    # Max
    clamp_001.inputs[2].default_value = 1.0

    # Node Reroute.019
    reroute_019 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_019.name = "Reroute.019"
    reroute_019.socket_idname = "NodeSocketFloat"
    # Node Reroute.020
    reroute_020 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_020.name = "Reroute.020"
    reroute_020.socket_idname = "NodeSocketFloat"
    # Node Reroute.021
    reroute_021 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_021.name = "Reroute.021"
    reroute_021.socket_idname = "NodeSocketFloat"
    # Node Reroute.022
    reroute_022 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_022.name = "Reroute.022"
    reroute_022.socket_idname = "NodeSocketFloat"
    # Node Reroute.023
    reroute_023 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_023.name = "Reroute.023"
    reroute_023.socket_idname = "NodeSocketFloat"
    # Node Reroute.024
    reroute_024 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_024.name = "Reroute.024"
    reroute_024.socket_idname = "NodeSocketFloat"
    # Node Reroute.025
    reroute_025 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_025.name = "Reroute.025"
    reroute_025.socket_idname = "NodeSocketFloat"
    # Node Reroute.028
    reroute_028 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_028.name = "Reroute.028"
    reroute_028.socket_idname = "NodeSocketFloat"
    # Node Reroute.029
    reroute_029 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_029.name = "Reroute.029"
    reroute_029.socket_idname = "NodeSocketFloat"
    # Node Reroute.030
    reroute_030 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_030.name = "Reroute.030"
    reroute_030.socket_idname = "NodeSocketFloat"
    # Node Reroute.031
    reroute_031 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_031.name = "Reroute.031"
    reroute_031.socket_idname = "NodeSocketFloat"
    # Node Reroute.032
    reroute_032 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_032.name = "Reroute.032"
    reroute_032.socket_idname = "NodeSocketFloat"
    # Node Reroute.033
    reroute_033 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_033.name = "Reroute.033"
    reroute_033.socket_idname = "NodeSocketFloat"
    # Node Reroute.034
    reroute_034 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_034.name = "Reroute.034"
    reroute_034.socket_idname = "NodeSocketFloat"
    # Node Group Input.005
    group_input_005_3 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_005_3.name = "Group Input.005"
    group_input_005_3.outputs[0].hide = True
    group_input_005_3.outputs[1].hide = True
    group_input_005_3.outputs[2].hide = True
    group_input_005_3.outputs[3].hide = True
    group_input_005_3.outputs[5].hide = True
    group_input_005_3.outputs[6].hide = True
    group_input_005_3.outputs[7].hide = True
    group_input_005_3.outputs[8].hide = True
    group_input_005_3.outputs[9].hide = True
    group_input_005_3.outputs[10].hide = True
    group_input_005_3.outputs[11].hide = True
    group_input_005_3.outputs[12].hide = True
    group_input_005_3.outputs[13].hide = True
    group_input_005_3.outputs[14].hide = True
    group_input_005_3.outputs[15].hide = True
    group_input_005_3.outputs[16].hide = True
    group_input_005_3.outputs[17].hide = True
    group_input_005_3.outputs[18].hide = True
    group_input_005_3.outputs[19].hide = True
    group_input_005_3.outputs[20].hide = True
    group_input_005_3.outputs[21].hide = True
    group_input_005_3.outputs[22].hide = True
    group_input_005_3.outputs[23].hide = True
    group_input_005_3.outputs[24].hide = True
    group_input_005_3.outputs[25].hide = True
    group_input_005_3.outputs[26].hide = True
    group_input_005_3.outputs[27].hide = True
    group_input_005_3.outputs[28].hide = True

    # Node Separate Color.002
    separate_color_002_1 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_1.name = "Separate Color.002"
    separate_color_002_1.mode = 'HSV'
    separate_color_002_1.ycc_mode = 'ITUBT709'
    separate_color_002_1.outputs[1].hide = True
    separate_color_002_1.outputs[2].hide = True
    separate_color_002_1.outputs[3].hide = True

    # Node Separate Color.003
    separate_color_003_2 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_2.name = "Separate Color.003"
    separate_color_003_2.mode = 'HSV'
    separate_color_003_2.ycc_mode = 'ITUBT709'
    separate_color_003_2.outputs[0].hide = True
    separate_color_003_2.outputs[2].hide = True
    separate_color_003_2.outputs[3].hide = True

    # Node Reroute.006
    reroute_006_2 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_006_2.name = "Reroute.006"
    reroute_006_2.socket_idname = "NodeSocketColor"
    # Node Separate Color.005
    separate_color_005 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_005.name = "Separate Color.005"
    separate_color_005.mode = 'HSV'
    separate_color_005.ycc_mode = 'ITUBT709'

    # Node Reroute.012
    reroute_012_1 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_012_1.name = "Reroute.012"
    reroute_012_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.035
    reroute_035 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_035.name = "Reroute.035"
    reroute_035.socket_idname = "NodeSocketFloat"
    # Node Reroute.036
    reroute_036 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_036.name = "Reroute.036"
    reroute_036.socket_idname = "NodeSocketFloat"
    # Node Reroute.037
    reroute_037 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_037.name = "Reroute.037"
    reroute_037.socket_idname = "NodeSocketFloat"
    # Node Reroute.038
    reroute_038 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_038.name = "Reroute.038"
    reroute_038.socket_idname = "NodeSocketFloat"
    # Node Reroute.039
    reroute_039 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_039.name = "Reroute.039"
    reroute_039.socket_idname = "NodeSocketFloat"
    # Node Reroute.040
    reroute_040 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_040.name = "Reroute.040"
    reroute_040.socket_idname = "NodeSocketFloat"
    # Node Reroute.041
    reroute_041 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_041.name = "Reroute.041"
    reroute_041.socket_idname = "NodeSocketFloat"
    # Node Reroute.042
    reroute_042 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_042.name = "Reroute.042"
    reroute_042.socket_idname = "NodeSocketFloat"
    # Node Reroute.043
    reroute_043 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_043.name = "Reroute.043"
    reroute_043.socket_idname = "NodeSocketFloat"
    # Node Reroute.044
    reroute_044 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_044.name = "Reroute.044"
    reroute_044.socket_idname = "NodeSocketFloat"
    # Node Reroute.045
    reroute_045 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_045.name = "Reroute.045"
    reroute_045.socket_idname = "NodeSocketFloat"
    # Node Reroute.046
    reroute_046 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_046.name = "Reroute.046"
    reroute_046.socket_idname = "NodeSocketFloat"
    # Node Reroute.047
    reroute_047 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_047.name = "Reroute.047"
    reroute_047.socket_idname = "NodeSocketFloat"
    # Node Reroute.017
    reroute_017 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_017.name = "Reroute.017"
    reroute_017.socket_idname = "NodeSocketColor"
    # Node Reroute.048
    reroute_048 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_048.name = "Reroute.048"
    reroute_048.socket_idname = "NodeSocketColor"
    # Node Separate Color.006
    separate_color_006 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_006.name = "Separate Color.006"
    separate_color_006.mode = 'HSV'
    separate_color_006.ycc_mode = 'ITUBT709'

    # Node Combine Color.002
    combine_color_002_1 = _rr_hue_correct_pre.nodes.new("CompositorNodeCombineColor")
    combine_color_002_1.name = "Combine Color.002"
    combine_color_002_1.mode = 'HSV'
    combine_color_002_1.ycc_mode = 'ITUBT709'

    # Node Group Input.006
    group_input_006 = _rr_hue_correct_pre.nodes.new("NodeGroupInput")
    group_input_006.name = "Group Input.006"
    group_input_006.outputs[0].hide = True
    group_input_006.outputs[1].hide = True
    group_input_006.outputs[2].hide = True
    group_input_006.outputs[3].hide = True
    group_input_006.outputs[4].hide = True
    group_input_006.outputs[5].hide = True
    group_input_006.outputs[6].hide = True
    group_input_006.outputs[7].hide = True
    group_input_006.outputs[8].hide = True
    group_input_006.outputs[9].hide = True
    group_input_006.outputs[10].hide = True
    group_input_006.outputs[11].hide = True
    group_input_006.outputs[12].hide = True
    group_input_006.outputs[13].hide = True
    group_input_006.outputs[14].hide = True
    group_input_006.outputs[15].hide = True
    group_input_006.outputs[16].hide = True
    group_input_006.outputs[17].hide = True
    group_input_006.outputs[18].hide = True
    group_input_006.outputs[19].hide = True
    group_input_006.outputs[20].hide = True
    group_input_006.outputs[28].hide = True

    # Node Group.033
    group_033 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_033.name = "Group.033"
    group_033.node_tree = _rr_adjust_mask
    # Socket_4
    group_033.inputs[3].default_value = 0.0

    # Node Group.034
    group_034 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_034.name = "Group.034"
    group_034.node_tree = _rr_adjust_mask
    # Socket_4
    group_034.inputs[3].default_value = 0.0

    # Node Group.035
    group_035 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_035.name = "Group.035"
    group_035.node_tree = _rr_adjust_mask
    # Socket_4
    group_035.inputs[3].default_value = 0.0

    # Node Group.036
    group_036 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_036.name = "Group.036"
    group_036.node_tree = _rr_adjust_mask
    # Socket_4
    group_036.inputs[3].default_value = 0.0

    # Node Group.037
    group_037 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_037.name = "Group.037"
    group_037.node_tree = _rr_adjust_mask
    # Socket_4
    group_037.inputs[3].default_value = 0.0

    # Node Group.038
    group_038 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_038.name = "Group.038"
    group_038.node_tree = _rr_adjust_mask
    # Socket_4
    group_038.inputs[3].default_value = 0.0

    # Node Group.039
    group_039 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_039.name = "Group.039"
    group_039.node_tree = _rr_adjust_mask
    # Socket_4
    group_039.inputs[3].default_value = 0.0

    # Node Frame.004
    frame_004_4 = _rr_hue_correct_pre.nodes.new("NodeFrame")
    frame_004_4.label = "Value"
    frame_004_4.name = "Frame.004"
    frame_004_4.label_size = 20
    frame_004_4.shrink = True

    # Node Reroute.049
    reroute_049 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_049.name = "Reroute.049"
    reroute_049.socket_idname = "NodeSocketFloat"
    # Node Reroute.050
    reroute_050 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_050.name = "Reroute.050"
    reroute_050.socket_idname = "NodeSocketFloat"
    # Node Mix
    mix_8 = _rr_hue_correct_pre.nodes.new("ShaderNodeMix")
    mix_8.name = "Mix"
    mix_8.blend_type = 'MIX'
    mix_8.clamp_factor = True
    mix_8.clamp_result = False
    mix_8.data_type = 'RGBA'
    mix_8.factor_mode = 'UNIFORM'

    # Node Reroute.051
    reroute_051 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_051.name = "Reroute.051"
    reroute_051.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.052
    reroute_052 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_052.name = "Reroute.052"
    reroute_052.socket_idname = "NodeSocketColor"
    # Node Reroute.053
    reroute_053 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_053.label = "Factor"
    reroute_053.name = "Reroute.053"
    reroute_053.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.054
    reroute_054 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_054.label = "Input"
    reroute_054.name = "Reroute.054"
    reroute_054.socket_idname = "NodeSocketColor"
    # Node Value
    value = _rr_hue_correct_pre.nodes.new("ShaderNodeValue")
    value.label = "Range"
    value.name = "Value"

    value.outputs[0].default_value = 0.16660000383853912
    # Node Math.003
    math_003_10 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_003_10.label = "Halve"
    math_003_10.name = "Math.003"
    math_003_10.hide = True
    math_003_10.operation = 'DIVIDE'
    math_003_10.use_clamp = False
    # Value_001
    math_003_10.inputs[1].default_value = 2.0

    # Node Math.004
    math_004_9 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_004_9.name = "Math.004"
    math_004_9.operation = 'MULTIPLY'
    math_004_9.use_clamp = False

    # Node Reroute.055
    reroute_055 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_055.name = "Reroute.055"
    reroute_055.socket_idname = "NodeSocketFloat"
    # Node Map Range.007
    map_range_007 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_007.name = "Map Range.007"
    map_range_007.clamp = True
    map_range_007.data_type = 'FLOAT'
    map_range_007.interpolation_type = 'LINEAR'
    # From Min
    map_range_007.inputs[1].default_value = 0.0
    # From Max
    map_range_007.inputs[2].default_value = 1.0
    # To Min
    map_range_007.inputs[3].default_value = 0.0
    # To Max
    map_range_007.inputs[4].default_value = 6.0

    # Node Math.013
    math_013_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_013_3.label = "*2"
    math_013_3.name = "Math.013"
    math_013_3.hide = True
    math_013_3.operation = 'MULTIPLY'
    math_013_3.use_clamp = False
    # Value_001
    math_013_3.inputs[1].default_value = 2.0

    # Node Math.014
    math_014_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_014_3.label = "-1"
    math_014_3.name = "Math.014"
    math_014_3.hide = True
    math_014_3.operation = 'SUBTRACT'
    math_014_3.use_clamp = False
    # Value_001
    math_014_3.inputs[1].default_value = 1.0

    # Node Math.015
    math_015_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_015_3.label = "*2"
    math_015_3.name = "Math.015"
    math_015_3.hide = True
    math_015_3.operation = 'MULTIPLY'
    math_015_3.use_clamp = False
    # Value_001
    math_015_3.inputs[1].default_value = 2.0

    # Node Math.016
    math_016_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_016_3.label = "-1"
    math_016_3.name = "Math.016"
    math_016_3.hide = True
    math_016_3.operation = 'SUBTRACT'
    math_016_3.use_clamp = False
    # Value_001
    math_016_3.inputs[1].default_value = 1.0

    # Node Reroute.057
    reroute_057 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_057.label = "Sat Mask"
    reroute_057.name = "Reroute.057"
    reroute_057.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.058
    reroute_058 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_058.label = "Value Mask"
    reroute_058.name = "Reroute.058"
    reroute_058.socket_idname = "NodeSocketFloatFactor"
    # Node Separate Color.007
    separate_color_007 = _rr_hue_correct_pre.nodes.new("CompositorNodeSeparateColor")
    separate_color_007.name = "Separate Color.007"
    separate_color_007.mode = 'HSV'
    separate_color_007.ycc_mode = 'ITUBT709'

    # Node Math.029
    math_029_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_029_2.name = "Math.029"
    math_029_2.hide = True
    math_029_2.operation = 'MULTIPLY'
    math_029_2.use_clamp = False

    # Node Reroute.061
    reroute_061 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_061.name = "Reroute.061"
    reroute_061.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.062
    reroute_062 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_062.name = "Reroute.062"
    reroute_062.socket_idname = "NodeSocketFloatFactor"
    # Node Math.032
    math_032_1 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_032_1.name = "Math.032"
    math_032_1.hide = True
    math_032_1.operation = 'MULTIPLY'
    math_032_1.use_clamp = False

    # Node Math.012
    math_012_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_012_3.label = "/ 6"
    math_012_3.name = "Math.012"
    math_012_3.hide = True
    math_012_3.operation = 'DIVIDE'
    math_012_3.use_clamp = False
    # Value_001
    math_012_3.inputs[1].default_value = 6.0

    # Node Math.027
    math_027_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_027_3.label = "/ 6"
    math_027_3.name = "Math.027"
    math_027_3.hide = True
    math_027_3.operation = 'DIVIDE'
    math_027_3.use_clamp = False
    # Value_001
    math_027_3.inputs[1].default_value = 6.0

    # Node Math.017
    math_017_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_017_3.label = "*2"
    math_017_3.name = "Math.017"
    math_017_3.hide = True
    math_017_3.operation = 'MULTIPLY'
    math_017_3.use_clamp = False
    # Value_001
    math_017_3.inputs[1].default_value = 2.0

    # Node Math.018
    math_018_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_018_2.label = "-1"
    math_018_2.name = "Math.018"
    math_018_2.hide = True
    math_018_2.operation = 'SUBTRACT'
    math_018_2.use_clamp = False
    # Value_001
    math_018_2.inputs[1].default_value = 1.0

    # Node Math.028
    math_028_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_028_3.label = "/ 6"
    math_028_3.name = "Math.028"
    math_028_3.hide = True
    math_028_3.operation = 'DIVIDE'
    math_028_3.use_clamp = False
    # Value_001
    math_028_3.inputs[1].default_value = 6.0

    # Node Math.019
    math_019_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_019_2.label = "*2"
    math_019_2.name = "Math.019"
    math_019_2.hide = True
    math_019_2.operation = 'MULTIPLY'
    math_019_2.use_clamp = False
    # Value_001
    math_019_2.inputs[1].default_value = 2.0

    # Node Math.020
    math_020_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_020_2.label = "-1"
    math_020_2.name = "Math.020"
    math_020_2.hide = True
    math_020_2.operation = 'SUBTRACT'
    math_020_2.use_clamp = False
    # Value_001
    math_020_2.inputs[1].default_value = 1.0

    # Node Math.033
    math_033 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_033.label = "/ 6"
    math_033.name = "Math.033"
    math_033.hide = True
    math_033.operation = 'DIVIDE'
    math_033.use_clamp = False
    # Value_001
    math_033.inputs[1].default_value = 6.0

    # Node Math.021
    math_021_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_021_2.label = "*2"
    math_021_2.name = "Math.021"
    math_021_2.hide = True
    math_021_2.operation = 'MULTIPLY'
    math_021_2.use_clamp = False
    # Value_001
    math_021_2.inputs[1].default_value = 2.0

    # Node Math.022
    math_022_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_022_3.label = "-1"
    math_022_3.name = "Math.022"
    math_022_3.hide = True
    math_022_3.operation = 'SUBTRACT'
    math_022_3.use_clamp = False
    # Value_001
    math_022_3.inputs[1].default_value = 1.0

    # Node Math.034
    math_034 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_034.label = "/ 6"
    math_034.name = "Math.034"
    math_034.hide = True
    math_034.operation = 'DIVIDE'
    math_034.use_clamp = False
    # Value_001
    math_034.inputs[1].default_value = 6.0

    # Node Math.023
    math_023_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_023_3.label = "*2"
    math_023_3.name = "Math.023"
    math_023_3.hide = True
    math_023_3.operation = 'MULTIPLY'
    math_023_3.use_clamp = False
    # Value_001
    math_023_3.inputs[1].default_value = 2.0

    # Node Math.024
    math_024_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_024_3.label = "-1"
    math_024_3.name = "Math.024"
    math_024_3.hide = True
    math_024_3.operation = 'SUBTRACT'
    math_024_3.use_clamp = False
    # Value_001
    math_024_3.inputs[1].default_value = 1.0

    # Node Math.035
    math_035 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_035.label = "/ 6"
    math_035.name = "Math.035"
    math_035.hide = True
    math_035.operation = 'DIVIDE'
    math_035.use_clamp = False
    # Value_001
    math_035.inputs[1].default_value = 6.0

    # Node Math.025
    math_025_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_025_3.label = "*2"
    math_025_3.name = "Math.025"
    math_025_3.hide = True
    math_025_3.operation = 'MULTIPLY'
    math_025_3.use_clamp = False
    # Value_001
    math_025_3.inputs[1].default_value = 2.0

    # Node Math.026
    math_026_3 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_026_3.label = "-1"
    math_026_3.name = "Math.026"
    math_026_3.hide = True
    math_026_3.operation = 'SUBTRACT'
    math_026_3.use_clamp = False
    # Value_001
    math_026_3.inputs[1].default_value = 1.0

    # Node Math.036
    math_036 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_036.label = "/ 6"
    math_036.name = "Math.036"
    math_036.hide = True
    math_036.operation = 'DIVIDE'
    math_036.use_clamp = False
    # Value_001
    math_036.inputs[1].default_value = 6.0

    # Node Reroute.007
    reroute_007_2 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_007_2.name = "Reroute.007"
    reroute_007_2.socket_idname = "NodeSocketFloat"
    # Node Map Range.012
    map_range_012 = _rr_hue_correct_pre.nodes.new("ShaderNodeMapRange")
    map_range_012.name = "Map Range.012"
    map_range_012.clamp = True
    map_range_012.data_type = 'FLOAT'
    map_range_012.interpolation_type = 'SMOOTHERSTEP'
    # From Min
    map_range_012.inputs[1].default_value = 0.0
    # From Max
    map_range_012.inputs[2].default_value = 0.10000000149011612
    # To Min
    map_range_012.inputs[3].default_value = 0.0
    # To Max
    map_range_012.inputs[4].default_value = 1.0

    # Node Reroute.018
    reroute_018 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_018.name = "Reroute.018"
    reroute_018.socket_idname = "NodeSocketFloat"
    # Node Reroute.026
    reroute_026 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_026.name = "Reroute.026"
    reroute_026.socket_idname = "NodeSocketFloat"
    # Node Reroute.027
    reroute_027 = _rr_hue_correct_pre.nodes.new("NodeReroute")
    reroute_027.name = "Reroute.027"
    reroute_027.socket_idname = "NodeSocketFloat"
    # Node Group.016
    group_016 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_016.name = "Group.016"
    group_016.node_tree = _rr_flip_mask

    # Node Group.017
    group_017 = _rr_hue_correct_pre.nodes.new("CompositorNodeGroup")
    group_017.name = "Group.017"
    group_017.node_tree = _rr_flip_mask

    # Node Float Curve
    float_curve_2 = _rr_hue_correct_pre.nodes.new("ShaderNodeFloatCurve")
    float_curve_2.name = "Float Curve"
    # Mapping settings
    float_curve_2.mapping.extend = 'EXTRAPOLATED'
    float_curve_2.mapping.tone = 'STANDARD'
    float_curve_2.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_2.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_2.mapping.clip_min_x = 0.0
    float_curve_2.mapping.clip_min_y = 0.0
    float_curve_2.mapping.clip_max_x = 1.0
    float_curve_2.mapping.clip_max_y = 1.0
    float_curve_2.mapping.use_clip = True
    # Curve 0
    float_curve_2_curve_0 = float_curve_2.mapping.curves[0]
    float_curve_2_curve_0_point_0 = float_curve_2_curve_0.points[0]
    float_curve_2_curve_0_point_0.location = (0.0, 0.0)
    float_curve_2_curve_0_point_0.handle_type = 'AUTO'
    float_curve_2_curve_0_point_1 = float_curve_2_curve_0.points[1]
    float_curve_2_curve_0_point_1.location = (0.25, 0.75)
    float_curve_2_curve_0_point_1.handle_type = 'AUTO'
    float_curve_2_curve_0_point_2 = float_curve_2_curve_0.points.new(1.0, 1.0)
    float_curve_2_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_2.mapping.update()

    # Node Math.005
    math_005_9 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_005_9.name = "Math.005"
    math_005_9.operation = 'GREATER_THAN'
    math_005_9.use_clamp = False
    # Value_001
    math_005_9.inputs[1].default_value = 0.0

    # Node Math.006
    math_006_8 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_006_8.name = "Math.006"
    math_006_8.operation = 'DIVIDE'
    math_006_8.use_clamp = False
    # Value_001
    math_006_8.inputs[1].default_value = 1.5

    # Node Math.007
    math_007_8 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_007_8.name = "Math.007"
    math_007_8.operation = 'DIVIDE'
    math_007_8.use_clamp = False
    # Value_001
    math_007_8.inputs[1].default_value = 1.5

    # Node Math.008
    math_008_7 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_008_7.name = "Math.008"
    math_008_7.operation = 'DIVIDE'
    math_008_7.use_clamp = False
    # Value_001
    math_008_7.inputs[1].default_value = 1.5

    # Node Math.009
    math_009_5 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_009_5.name = "Math.009"
    math_009_5.operation = 'DIVIDE'
    math_009_5.use_clamp = False
    # Value_001
    math_009_5.inputs[1].default_value = 1.5

    # Node Math.010
    math_010_4 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_010_4.name = "Math.010"
    math_010_4.operation = 'DIVIDE'
    math_010_4.use_clamp = False
    # Value_001
    math_010_4.inputs[1].default_value = 1.5

    # Node Math.011
    math_011_4 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_011_4.name = "Math.011"
    math_011_4.operation = 'DIVIDE'
    math_011_4.use_clamp = False
    # Value_001
    math_011_4.inputs[1].default_value = 1.5

    # Node Math.030
    math_030_1 = _rr_hue_correct_pre.nodes.new("ShaderNodeMath")
    math_030_1.name = "Math.030"
    math_030_1.operation = 'DIVIDE'
    math_030_1.use_clamp = False
    # Value_001
    math_030_1.inputs[1].default_value = 1.5

    # Set parents
    group_input_001_4.parent = frame_10
    math_001_8.parent = frame_10
    reroute_001_6.parent = frame_10
    reroute_002_5.parent = frame_10
    group_input_002_2.parent = frame_001_7
    reroute_004_4.parent = frame_001_7
    clamp.parent = frame_001_7
    group_input_003_3.parent = frame_002_6
    mix_001_4.parent = frame_003_5
    group_input_004_3.parent = frame_003_5
    reroute_008_1.parent = frame_002_6
    reroute_009_1.parent = frame_002_6
    reroute_010_1.parent = frame_002_6
    reroute_011_1.parent = frame_002_6
    _srgb_to_lab.parent = frame_002_6
    _lab_to_srgb.parent = frame_002_6
    reroute_013_1.parent = frame_002_6
    reroute_014.parent = frame_002_6
    _lab_adjustments_001.parent = frame_002_6
    _lab_adjustments_002.parent = frame_002_6
    _lab_adjustments_003.parent = frame_002_6
    _lab_adjustments_004.parent = frame_002_6
    _lab_adjustments_005.parent = frame_002_6
    _lab_adjustments_006.parent = frame_002_6
    _lab_adjustments_007.parent = frame_002_6
    switch_4.parent = frame_003_5
    reroute_015.parent = frame_003_5
    math_12.parent = frame_003_5
    math_002_9.parent = frame_003_5
    switch_001.parent = frame_003_5
    reroute_016.parent = frame_003_5
    group_009.parent = frame_001_7
    group_010.parent = frame_001_7
    group_011.parent = frame_001_7
    group_012.parent = frame_001_7
    group_013.parent = frame_001_7
    group_014.parent = frame_001_7
    group_015.parent = frame_001_7
    reroute_005_5.parent = frame_001_7
    group_025.parent = frame_10
    group_026.parent = frame_10
    group_027.parent = frame_10
    group_028.parent = frame_10
    group_029.parent = frame_10
    group_030.parent = frame_10
    group_031.parent = frame_10
    map_range_7.parent = frame_002_6
    map_range_001_6.parent = frame_002_6
    map_range_002_5.parent = frame_002_6
    map_range_003_4.parent = frame_002_6
    map_range_004_2.parent = frame_002_6
    map_range_005_3.parent = frame_002_6
    map_range_006_1.parent = frame_002_6
    separate_color_004_1.parent = frame_002_6
    combine_color_001_1.parent = frame_002_6
    clamp_001.parent = frame_002_6
    reroute_028.parent = frame_002_6
    reroute_029.parent = frame_002_6
    reroute_030.parent = frame_002_6
    reroute_031.parent = frame_002_6
    reroute_032.parent = frame_002_6
    reroute_034.parent = frame_002_6
    separate_color_002_1.parent = frame_10
    separate_color_003_2.parent = frame_001_7
    reroute_012_1.parent = frame_10
    reroute_035.parent = frame_10
    reroute_036.parent = frame_10
    reroute_037.parent = frame_10
    reroute_038.parent = frame_10
    reroute_039.parent = frame_10
    reroute_040.parent = frame_10
    reroute_041.parent = frame_10
    reroute_042.parent = frame_10
    reroute_043.parent = frame_10
    reroute_044.parent = frame_10
    reroute_045.parent = frame_10
    reroute_046.parent = frame_10
    reroute_047.parent = frame_10
    reroute_017.parent = frame_002_6
    reroute_048.parent = frame_002_6
    separate_color_006.parent = frame_004_4
    combine_color_002_1.parent = frame_004_4
    group_input_006.parent = frame_004_4
    group_033.parent = frame_004_4
    group_034.parent = frame_004_4
    group_035.parent = frame_004_4
    group_036.parent = frame_004_4
    group_037.parent = frame_004_4
    group_038.parent = frame_004_4
    group_039.parent = frame_004_4
    reroute_049.parent = frame_004_4
    reroute_050.parent = frame_004_4
    mix_8.parent = frame_003_5
    reroute_051.parent = frame_003_5
    reroute_052.parent = frame_003_5
    reroute_053.parent = frame_003_5
    reroute_054.parent = frame_003_5
    math_013_3.parent = frame_10
    math_014_3.parent = frame_10
    math_015_3.parent = frame_10
    math_016_3.parent = frame_10
    reroute_057.parent = frame_003_5
    reroute_058.parent = frame_003_5
    separate_color_007.parent = frame_003_5
    math_029_2.parent = frame_003_5
    reroute_061.parent = frame_003_5
    reroute_062.parent = frame_003_5
    math_032_1.parent = frame_003_5
    math_012_3.parent = frame_10
    math_027_3.parent = frame_10
    math_017_3.parent = frame_10
    math_018_2.parent = frame_10
    math_028_3.parent = frame_10
    math_019_2.parent = frame_10
    math_020_2.parent = frame_10
    math_033.parent = frame_10
    math_021_2.parent = frame_10
    math_022_3.parent = frame_10
    math_034.parent = frame_10
    math_023_3.parent = frame_10
    math_024_3.parent = frame_10
    math_035.parent = frame_10
    math_025_3.parent = frame_10
    math_026_3.parent = frame_10
    math_036.parent = frame_10
    reroute_026.parent = frame_10
    reroute_027.parent = frame_10
    group_016.parent = frame_003_5
    group_017.parent = frame_003_5
    float_curve_2.parent = frame_003_5
    math_005_9.parent = frame_003_5
    math_006_8.parent = frame_004_4
    math_007_8.parent = frame_004_4
    math_008_7.parent = frame_004_4
    math_009_5.parent = frame_004_4
    math_010_4.parent = frame_004_4
    math_011_4.parent = frame_004_4
    math_030_1.parent = frame_004_4

    # Set locations
    group_output_14.location = (6327.2216796875, -90.70211029052734)
    separate_color_3.location = (-1467.9178466796875, 21.059410095214844)
    group_input_13.location = (-2649.806396484375, -625.0185546875)
    hue_correct.location = (-1121.0526123046875, 147.24240112304688)
    separate_color_001_3.location = (2469.36865234375, -666.8716430664062)
    group_input_001_4.location = (29.217697143554688, -653.3338623046875)
    combine_color_4.location = (2797.526611328125, -578.9133911132812)
    group.location = (-1596.087646484375, -1818.707763671875)
    group_001.location = (-1595.2578125, -2030.882568359375)
    group_002.location = (-1597.0523681640625, -2241.424072265625)
    group_004.location = (-1593.0517578125, -974.7217407226562)
    group_005.location = (-1594.8626708984375, -1183.8515625)
    group_006.location = (-1594.8626708984375, -1393.431884765625)
    group_007.location = (-1594.8626708984375, -1606.4842529296875)
    math_001_8.location = (1029.7850341796875, -35.6751708984375)
    reroute_001_6.location = (966.153076171875, -141.487548828125)
    reroute_002_5.location = (966.153076171875, -1565.58740234375)
    frame_10.location = (-105.4800033569336, -777.76806640625)
    group_input_002_2.location = (29.26708984375, -601.2550048828125)
    reroute_004_4.location = (888.6751708984375, -117.60260009765625)
    frame_001_7.location = (1523.8800048828125, -807.2880859375)
    reroute_8.location = (1555.673828125, -647.1904296875)
    clamp.location = (934.9837646484375, -35.77325439453125)
    group_input_003_3.location = (334.887939453125, -558.880859375)
    mix_001_4.location = (452.5791015625, -642.6529541015625)
    group_input_004_3.location = (28.89892578125, -548.4332885742188)
    reroute_008_1.location = (1210.2086181640625, -1598.7896728515625)
    reroute_009_1.location = (1236.9703369140625, -1621.34033203125)
    reroute_010_1.location = (1209.5509033203125, -144.183349609375)
    reroute_011_1.location = (1237.5985107421875, -159.55419921875)
    frame_002_6.location = (1126.4400634765625, 1508.9520263671875)
    _srgb_to_lab.location = (29.1453857421875, -85.7353515625)
    _lab_to_srgb.location = (1380.5804443359375, -35.6275634765625)
    reroute_013_1.location = (677.4808349609375, -158.562255859375)
    reroute_014.location = (680.9002685546875, -137.6533203125)
    _lab_adjustments_001.location = (983.9708251953125, -228.5155029296875)
    _lab_adjustments_002.location = (981.8160400390625, -456.5684814453125)
    _lab_adjustments_003.location = (980.0245361328125, -684.2100219726562)
    _lab_adjustments_004.location = (977.3367919921875, -906.4742431640625)
    _lab_adjustments_005.location = (973.7530517578125, -1133.2197265625)
    _lab_adjustments_006.location = (971.9613037109375, -1353.691650390625)
    _lab_adjustments_007.location = (964.7943115234375, -1563.4090576171875)
    switch_4.location = (715.1494140625, -772.0282592773438)
    reroute_015.location = (240.16943359375, -869.3853759765625)
    math_12.location = (453.3759765625, -461.8907470703125)
    math_002_9.location = (719.40234375, -493.8368225097656)
    switch_001.location = (975.02001953125, -818.563720703125)
    reroute_016.location = (242.82861328125, -925.281982421875)
    frame_003_5.location = (3656.52001953125, 562.1520385742188)
    group_009.location = (675.1837158203125, -134.75494384765625)
    group_010.location = (672.0421142578125, -339.0260009765625)
    group_011.location = (669.7574462890625, -545.4688720703125)
    group_012.location = (671.5494384765625, -755.2056884765625)
    group_013.location = (667.0692138671875, -973.9056396484375)
    group_014.location = (666.1734619140625, -1189.020263671875)
    group_015.location = (665.2774658203125, -1393.379638671875)
    reroute_005_5.location = (871.5428466796875, -1425.788818359375)
    group_025.location = (717.7479248046875, -256.726806640625)
    group_026.location = (717.7479248046875, -463.5909423828125)
    group_027.location = (717.7479248046875, -677.281005859375)
    group_028.location = (717.7479248046875, -888.0574951171875)
    group_029.location = (717.7479248046875, -1101.74853515625)
    group_030.location = (717.7479248046875, -1313.497314453125)
    group_031.location = (717.7479248046875, -1533.016357421875)
    reroute_003_5.location = (-1542.1016845703125, -124.68637084960938)
    map_range_7.location = (769.447998046875, -454.578369140625)
    map_range_001_6.location = (774.07275390625, -382.04296875)
    map_range_002_5.location = (802.2659912109375, -838.1699829101562)
    map_range_003_4.location = (798.3795166015625, -1063.5697021484375)
    map_range_004_2.location = (801.4525146484375, -1291.884521484375)
    map_range_005_3.location = (791.2677001953125, -1508.5406494140625)
    map_range_006_1.location = (794.756103515625, -1716.4530029296875)
    separate_color_004_1.location = (1704.2757568359375, -1565.1275634765625)
    combine_color_001_1.location = (2080.54248046875, -1556.6385498046875)
    clamp_001.location = (1901.0123291015625, -1570.9063720703125)
    reroute_019.location = (1205.2760009765625, -1014.9318237304688)
    reroute_020.location = (1388.5252685546875, -2069.8154296875)
    reroute_021.location = (1437.930419921875, -2276.517822265625)
    reroute_022.location = (1343.8963623046875, -1855.9095458984375)
    reroute_023.location = (1249.104736328125, -1221.211181640625)
    reroute_024.location = (1285.391357421875, -1429.0186767578125)
    reroute_025.location = (1313.8907470703125, -1639.9617919921875)
    reroute_028.location = (78.8359375, -338.501220703125)
    reroute_029.location = (126.1531982421875, -557.9124145507812)
    reroute_030.location = (158.9512939453125, -788.8140258789062)
    reroute_031.location = (187.45068359375, -1012.3154907226562)
    reroute_032.location = (217.456298828125, -1231.4945068359375)
    reroute_033.location = (1388.5252685546875, 51.66729736328125)
    reroute_034.location = (311.4903564453125, -1664.05712890625)
    group_input_005_3.location = (-2121.70166015625, -1473.614501953125)
    separate_color_002_1.location = (257.1065673828125, -291.7899169921875)
    separate_color_003_2.location = (293.6646728515625, -247.0855712890625)
    reroute_006_2.location = (-21.84799575805664, -748.2371826171875)
    separate_color_005.location = (-2349.432861328125, -744.0811767578125)
    reroute_012_1.location = (630.1240844726562, -251.7523193359375)
    reroute_035.location = (630.1240844726562, -647.9146728515625)
    reroute_036.location = (630.1240844726562, -883.6785888671875)
    reroute_037.location = (630.1240844726562, -1285.90185546875)
    reroute_038.location = (630.1240844726562, -461.0186767578125)
    reroute_039.location = (630.1240844726562, -860.9820556640625)
    reroute_040.location = (630.1240844726562, -1519.01806640625)
    reroute_041.location = (630.1240844726562, -438.4371337890625)
    reroute_042.location = (630.1240844726562, -229.64593505859375)
    reroute_043.location = (630.1240844726562, -1496.059814453125)
    reroute_044.location = (630.1240844726562, -1308.59375)
    reroute_045.location = (630.1240844726562, -1096.369384765625)
    reroute_046.location = (630.1240844726562, -670.5770263671875)
    reroute_047.location = (630.1240844726562, -1073.47607421875)
    reroute_017.location = (1587.5445556640625, -1704.732177734375)
    reroute_048.location = (1586.8851318359375, -70.3468017578125)
    separate_color_006.location = (137.758056640625, -71.7537841796875)
    combine_color_002_1.location = (886.786865234375, -35.9990234375)
    group_input_006.location = (28.863525390625, -773.0697021484375)
    group_033.location = (564.9618530273438, -357.52685546875)
    group_034.location = (564.9618530273438, -564.3909912109375)
    group_035.location = (564.9618530273438, -778.0810546875)
    group_036.location = (564.9618530273438, -988.8575439453125)
    group_037.location = (564.9618530273438, -1202.548583984375)
    group_038.location = (564.9618530273438, -1414.29736328125)
    group_039.location = (564.9618530273438, -1633.81640625)
    frame_004_4.location = (-1245.239990234375, -676.968017578125)
    reroute_049.location = (843.0610961914062, -155.87921142578125)
    reroute_050.location = (841.079345703125, -1665.718505859375)
    mix_8.location = (2264.98291015625, -684.4335327148438)
    reroute_051.location = (904.46337890625, -380.69927978515625)
    reroute_052.location = (904.46337890625, -422.1624755859375)
    reroute_053.location = (455.93896484375, -382.381103515625)
    reroute_054.location = (455.93896484375, -418.9241027832031)
    value.location = (-2116.966796875, -1393.484130859375)
    math_003_10.location = (-2111.7099609375, -1157.021728515625)
    math_004_9.location = (-2116.9482421875, -1219.907958984375)
    reroute_055.location = (-1923.2305908203125, -1390.0787353515625)
    map_range_007.location = (-2352.68701171875, -1220.70947265625)
    math_013_3.location = (483.56195068359375, -1565.682373046875)
    math_014_3.location = (486.46234130859375, -1607.145751953125)
    math_015_3.location = (481.4731750488281, -1343.464599609375)
    math_016_3.location = (484.3736572265625, -1384.927734375)
    reroute_057.location = (455.93896484375, -316.962158203125)
    reroute_058.location = (455.93896484375, -349.7470703125)
    separate_color_007.location = (1364.7822265625, -114.92364501953125)
    math_029_2.location = (2246.05615234375, -373.823486328125)
    reroute_061.location = (1559.54736328125, -89.43466186523438)
    reroute_062.location = (1361.6357421875, -306.09429931640625)
    math_032_1.location = (2240.0615234375, -215.01583862304688)
    math_012_3.location = (484.5810241699219, -1648.578369140625)
    math_027_3.location = (484.5810241699219, -1430.96142578125)
    math_017_3.location = (481.4731750488281, -1134.9580078125)
    math_018_2.location = (484.3736572265625, -1176.42138671875)
    math_028_3.location = (484.5810241699219, -1222.4549560546875)
    math_019_2.location = (481.4731750488281, -931.2813720703125)
    math_020_2.location = (484.3736572265625, -972.74462890625)
    math_033.location = (484.5810241699219, -1018.7781982421875)
    math_021_2.location = (481.4731750488281, -719.291259765625)
    math_022_3.location = (484.3736572265625, -760.7545166015625)
    math_034.location = (484.5810241699219, -806.7882080078125)
    math_023_3.location = (481.4731750488281, -503.9752197265625)
    math_024_3.location = (484.3736572265625, -545.4384765625)
    math_035.location = (484.5810241699219, -591.47216796875)
    math_025_3.location = (489.2469787597656, -311.936279296875)
    math_026_3.location = (492.1474914550781, -353.3995361328125)
    math_036.location = (492.3548583984375, -399.433349609375)
    reroute_007_2.location = (-1968.4185791015625, -1069.8162841796875)
    map_range_012.location = (-2350.541015625, -926.8952026367188)
    reroute_018.location = (-1968.4185791015625, -1093.6214599609375)
    reroute_026.location = (631.3870239257812, -282.42919921875)
    reroute_027.location = (489.4726867675781, -280.1646728515625)
    group_016.location = (1948.85205078125, -35.86907958984375)
    group_017.location = (1944.896484375, -217.75332641601562)
    float_curve_2.location = (1644.09765625, -197.183349609375)
    math_005_9.location = (1424.203125, -430.21466064453125)
    math_006_8.location = (398.25909423828125, -368.255615234375)
    math_007_8.location = (393.64617919921875, -573.6142578125)
    math_008_7.location = (390.18634033203125, -793.3656005859375)
    math_009_5.location = (392.3072509765625, -1003.5989990234375)
    math_010_4.location = (398.707763671875, -1217.0340576171875)
    math_011_4.location = (396.57421875, -1421.931640625)
    math_030_1.location = (395.5074462890625, -1641.769775390625)

    # Set dimensions
    group_output_14.width, group_output_14.height = 150.67941284179688, 100.0
    separate_color_3.width, separate_color_3.height = 140.0, 100.0
    group_input_13.width, group_input_13.height = 140.0, 100.0
    hue_correct.width, hue_correct.height = 360.844970703125, 100.0
    separate_color_001_3.width, separate_color_001_3.height = 140.0, 100.0
    group_input_001_4.width, group_input_001_4.height = 140.0, 100.0
    combine_color_4.width, combine_color_4.height = 140.0, 100.0
    group.width, group.height = 175.66017150878906, 100.0
    group_001.width, group_001.height = 175.66017150878906, 100.0
    group_002.width, group_002.height = 175.66017150878906, 100.0
    group_004.width, group_004.height = 175.66017150878906, 100.0
    group_005.width, group_005.height = 175.66017150878906, 100.0
    group_006.width, group_006.height = 175.66017150878906, 100.0
    group_007.width, group_007.height = 175.66017150878906, 100.0
    math_001_8.width, math_001_8.height = 140.0, 100.0
    reroute_001_6.width, reroute_001_6.height = 13.5, 100.0
    reroute_002_5.width, reroute_002_5.height = 13.5, 100.0
    frame_10.width, frame_10.height = 1199.1199951171875, 1716.672119140625
    group_input_002_2.width, group_input_002_2.height = 140.0, 100.0
    reroute_004_4.width, reroute_004_4.height = 13.5, 100.0
    frame_001_7.width, frame_001_7.height = 1104.0799560546875, 1576.991943359375
    reroute_8.width, reroute_8.height = 13.5, 100.0
    clamp.width, clamp.height = 140.0, 100.0
    group_input_003_3.width, group_input_003_3.height = 140.0, 100.0
    mix_001_4.width, mix_001_4.height = 140.0, 100.0
    group_input_004_3.width, group_input_004_3.height = 140.0, 100.0
    reroute_008_1.width, reroute_008_1.height = 13.5, 100.0
    reroute_009_1.width, reroute_009_1.height = 13.5, 100.0
    reroute_010_1.width, reroute_010_1.height = 13.5, 100.0
    reroute_011_1.width, reroute_011_1.height = 13.5, 100.0
    frame_002_6.width, frame_002_6.height = 2249.60009765625, 1789.39208984375
    _srgb_to_lab.width, _srgb_to_lab.height = 140.0, 100.0
    _lab_to_srgb.width, _lab_to_srgb.height = 140.0, 100.0
    reroute_013_1.width, reroute_013_1.height = 13.5, 100.0
    reroute_014.width, reroute_014.height = 13.5, 100.0
    _lab_adjustments_001.width, _lab_adjustments_001.height = 140.0, 100.0
    _lab_adjustments_002.width, _lab_adjustments_002.height = 140.0, 100.0
    _lab_adjustments_003.width, _lab_adjustments_003.height = 140.0, 100.0
    _lab_adjustments_004.width, _lab_adjustments_004.height = 140.0, 100.0
    _lab_adjustments_005.width, _lab_adjustments_005.height = 140.0, 100.0
    _lab_adjustments_006.width, _lab_adjustments_006.height = 140.0, 100.0
    _lab_adjustments_007.width, _lab_adjustments_007.height = 140.0, 100.0
    switch_4.width, switch_4.height = 140.0, 100.0
    reroute_015.width, reroute_015.height = 13.5, 100.0
    math_12.width, math_12.height = 140.0, 100.0
    math_002_9.width, math_002_9.height = 140.0, 100.0
    switch_001.width, switch_001.height = 140.0, 100.0
    reroute_016.width, reroute_016.height = 13.5, 100.0
    frame_003_5.width, frame_003_5.height = 2433.919921875, 960.6720581054688
    group_009.width, group_009.height = 159.940185546875, 100.0
    group_010.width, group_010.height = 159.940185546875, 100.0
    group_011.width, group_011.height = 159.940185546875, 100.0
    group_012.width, group_012.height = 159.940185546875, 100.0
    group_013.width, group_013.height = 159.940185546875, 100.0
    group_014.width, group_014.height = 159.940185546875, 100.0
    group_015.width, group_015.height = 159.940185546875, 100.0
    reroute_005_5.width, reroute_005_5.height = 13.5, 100.0
    group_025.width, group_025.height = 159.940185546875, 100.0
    group_026.width, group_026.height = 159.940185546875, 100.0
    group_027.width, group_027.height = 159.940185546875, 100.0
    group_028.width, group_028.height = 159.940185546875, 100.0
    group_029.width, group_029.height = 159.940185546875, 100.0
    group_030.width, group_030.height = 159.940185546875, 100.0
    group_031.width, group_031.height = 159.940185546875, 100.0
    reroute_003_5.width, reroute_003_5.height = 13.5, 100.0
    map_range_7.width, map_range_7.height = 140.0, 100.0
    map_range_001_6.width, map_range_001_6.height = 140.0, 100.0
    map_range_002_5.width, map_range_002_5.height = 140.0, 100.0
    map_range_003_4.width, map_range_003_4.height = 140.0, 100.0
    map_range_004_2.width, map_range_004_2.height = 140.0, 100.0
    map_range_005_3.width, map_range_005_3.height = 140.0, 100.0
    map_range_006_1.width, map_range_006_1.height = 140.0, 100.0
    separate_color_004_1.width, separate_color_004_1.height = 140.0, 100.0
    combine_color_001_1.width, combine_color_001_1.height = 140.0, 100.0
    clamp_001.width, clamp_001.height = 140.0, 100.0
    reroute_019.width, reroute_019.height = 13.5, 100.0
    reroute_020.width, reroute_020.height = 13.5, 100.0
    reroute_021.width, reroute_021.height = 13.5, 100.0
    reroute_022.width, reroute_022.height = 13.5, 100.0
    reroute_023.width, reroute_023.height = 13.5, 100.0
    reroute_024.width, reroute_024.height = 13.5, 100.0
    reroute_025.width, reroute_025.height = 13.5, 100.0
    reroute_028.width, reroute_028.height = 13.5, 100.0
    reroute_029.width, reroute_029.height = 13.5, 100.0
    reroute_030.width, reroute_030.height = 13.5, 100.0
    reroute_031.width, reroute_031.height = 13.5, 100.0
    reroute_032.width, reroute_032.height = 13.5, 100.0
    reroute_033.width, reroute_033.height = 13.5, 100.0
    reroute_034.width, reroute_034.height = 13.5, 100.0
    group_input_005_3.width, group_input_005_3.height = 140.0, 100.0
    separate_color_002_1.width, separate_color_002_1.height = 140.0, 100.0
    separate_color_003_2.width, separate_color_003_2.height = 140.0, 100.0
    reroute_006_2.width, reroute_006_2.height = 13.5, 100.0
    separate_color_005.width, separate_color_005.height = 140.0, 100.0
    reroute_012_1.width, reroute_012_1.height = 13.5, 100.0
    reroute_035.width, reroute_035.height = 13.5, 100.0
    reroute_036.width, reroute_036.height = 13.5, 100.0
    reroute_037.width, reroute_037.height = 13.5, 100.0
    reroute_038.width, reroute_038.height = 13.5, 100.0
    reroute_039.width, reroute_039.height = 13.5, 100.0
    reroute_040.width, reroute_040.height = 13.5, 100.0
    reroute_041.width, reroute_041.height = 13.5, 100.0
    reroute_042.width, reroute_042.height = 13.5, 100.0
    reroute_043.width, reroute_043.height = 13.5, 100.0
    reroute_044.width, reroute_044.height = 13.5, 100.0
    reroute_045.width, reroute_045.height = 13.5, 100.0
    reroute_046.width, reroute_046.height = 13.5, 100.0
    reroute_047.width, reroute_047.height = 13.5, 100.0
    reroute_017.width, reroute_017.height = 13.5, 100.0
    reroute_048.width, reroute_048.height = 13.5, 100.0
    separate_color_006.width, separate_color_006.height = 140.0, 100.0
    combine_color_002_1.width, combine_color_002_1.height = 140.0, 100.0
    group_input_006.width, group_input_006.height = 140.0, 100.0
    group_033.width, group_033.height = 159.940185546875, 100.0
    group_034.width, group_034.height = 159.940185546875, 100.0
    group_035.width, group_035.height = 159.940185546875, 100.0
    group_036.width, group_036.height = 159.940185546875, 100.0
    group_037.width, group_037.height = 159.940185546875, 100.0
    group_038.width, group_038.height = 159.940185546875, 100.0
    group_039.width, group_039.height = 159.940185546875, 100.0
    frame_004_4.width, frame_004_4.height = 1055.8399658203125, 1817.47216796875
    reroute_049.width, reroute_049.height = 13.5, 100.0
    reroute_050.width, reroute_050.height = 13.5, 100.0
    mix_8.width, mix_8.height = 140.0, 100.0
    reroute_051.width, reroute_051.height = 13.5, 100.0
    reroute_052.width, reroute_052.height = 13.5, 100.0
    reroute_053.width, reroute_053.height = 13.5, 100.0
    reroute_054.width, reroute_054.height = 13.5, 100.0
    value.width, value.height = 140.0, 100.0
    math_003_10.width, math_003_10.height = 140.0, 100.0
    math_004_9.width, math_004_9.height = 140.0, 100.0
    reroute_055.width, reroute_055.height = 13.5, 100.0
    map_range_007.width, map_range_007.height = 140.0, 100.0
    math_013_3.width, math_013_3.height = 140.0, 100.0
    math_014_3.width, math_014_3.height = 140.0, 100.0
    math_015_3.width, math_015_3.height = 140.0, 100.0
    math_016_3.width, math_016_3.height = 140.0, 100.0
    reroute_057.width, reroute_057.height = 13.5, 100.0
    reroute_058.width, reroute_058.height = 13.5, 100.0
    separate_color_007.width, separate_color_007.height = 140.0, 100.0
    math_029_2.width, math_029_2.height = 140.0, 100.0
    reroute_061.width, reroute_061.height = 13.5, 100.0
    reroute_062.width, reroute_062.height = 13.5, 100.0
    math_032_1.width, math_032_1.height = 140.0, 100.0
    math_012_3.width, math_012_3.height = 140.0, 100.0
    math_027_3.width, math_027_3.height = 140.0, 100.0
    math_017_3.width, math_017_3.height = 140.0, 100.0
    math_018_2.width, math_018_2.height = 140.0, 100.0
    math_028_3.width, math_028_3.height = 140.0, 100.0
    math_019_2.width, math_019_2.height = 140.0, 100.0
    math_020_2.width, math_020_2.height = 140.0, 100.0
    math_033.width, math_033.height = 140.0, 100.0
    math_021_2.width, math_021_2.height = 140.0, 100.0
    math_022_3.width, math_022_3.height = 140.0, 100.0
    math_034.width, math_034.height = 140.0, 100.0
    math_023_3.width, math_023_3.height = 140.0, 100.0
    math_024_3.width, math_024_3.height = 140.0, 100.0
    math_035.width, math_035.height = 140.0, 100.0
    math_025_3.width, math_025_3.height = 140.0, 100.0
    math_026_3.width, math_026_3.height = 140.0, 100.0
    math_036.width, math_036.height = 140.0, 100.0
    reroute_007_2.width, reroute_007_2.height = 13.5, 100.0
    map_range_012.width, map_range_012.height = 140.0, 100.0
    reroute_018.width, reroute_018.height = 13.5, 100.0
    reroute_026.width, reroute_026.height = 13.5, 100.0
    reroute_027.width, reroute_027.height = 13.5, 100.0
    group_016.width, group_016.height = 169.8074951171875, 100.0
    group_017.width, group_017.height = 169.8074951171875, 100.0
    float_curve_2.width, float_curve_2.height = 240.0, 100.0
    math_005_9.width, math_005_9.height = 140.0, 100.0
    math_006_8.width, math_006_8.height = 140.0, 100.0
    math_007_8.width, math_007_8.height = 140.0, 100.0
    math_008_7.width, math_008_7.height = 140.0, 100.0
    math_009_5.width, math_009_5.height = 140.0, 100.0
    math_010_4.width, math_010_4.height = 140.0, 100.0
    math_011_4.width, math_011_4.height = 140.0, 100.0
    math_030_1.width, math_030_1.height = 140.0, 100.0

    # Initialize _rr_hue_correct_pre links

    # separate_color_3.Green -> hue_correct.Fac
    _rr_hue_correct_pre.links.new(separate_color_3.outputs[1], hue_correct.inputs[0])
    # separate_color_001_3.Blue -> combine_color_4.Blue
    _rr_hue_correct_pre.links.new(separate_color_001_3.outputs[2], combine_color_4.inputs[2])
    # separate_color_001_3.Alpha -> combine_color_4.Alpha
    _rr_hue_correct_pre.links.new(separate_color_001_3.outputs[3], combine_color_4.inputs[3])
    # reroute_8.Output -> combine_color_4.Red
    _rr_hue_correct_pre.links.new(reroute_8.outputs[0], combine_color_4.inputs[0])
    # reroute_002_5.Output -> reroute_001_6.Input
    _rr_hue_correct_pre.links.new(reroute_002_5.outputs[0], reroute_001_6.inputs[0])
    # math_001_8.Value -> reroute_8.Input
    _rr_hue_correct_pre.links.new(math_001_8.outputs[0], reroute_8.inputs[0])
    # reroute_004_4.Output -> clamp.Value
    _rr_hue_correct_pre.links.new(reroute_004_4.outputs[0], clamp.inputs[0])
    # reroute_001_6.Output -> math_001_8.Value
    _rr_hue_correct_pre.links.new(reroute_001_6.outputs[0], math_001_8.inputs[0])
    # reroute_016.Output -> mix_001_4.A
    _rr_hue_correct_pre.links.new(reroute_016.outputs[0], mix_001_4.inputs[6])
    # group_input_004_3.Perceptual -> mix_001_4.Factor
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[2], mix_001_4.inputs[0])
    # reroute_008_1.Output -> reroute_010_1.Input
    _rr_hue_correct_pre.links.new(reroute_008_1.outputs[0], reroute_010_1.inputs[0])
    # reroute_009_1.Output -> reroute_011_1.Input
    _rr_hue_correct_pre.links.new(reroute_009_1.outputs[0], reroute_011_1.inputs[0])
    # _srgb_to_lab.L -> _lab_to_srgb.L
    _rr_hue_correct_pre.links.new(_srgb_to_lab.outputs[0], _lab_to_srgb.inputs[0])
    # _srgb_to_lab.Alpha -> _lab_to_srgb.Alpha
    _rr_hue_correct_pre.links.new(_srgb_to_lab.outputs[3], _lab_to_srgb.inputs[3])
    # _srgb_to_lab.B -> reroute_013_1.Input
    _rr_hue_correct_pre.links.new(_srgb_to_lab.outputs[2], reroute_013_1.inputs[0])
    # _srgb_to_lab.A -> reroute_014.Input
    _rr_hue_correct_pre.links.new(_srgb_to_lab.outputs[1], reroute_014.inputs[0])
    # group_input_003_3.Red Saturation -> _lab_adjustments_001.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[14], _lab_adjustments_001.inputs[4])
    # _lab_adjustments_001.A -> _lab_adjustments_002.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_001.outputs[0], _lab_adjustments_002.inputs[1])
    # _lab_adjustments_001.B -> _lab_adjustments_002.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_001.outputs[1], _lab_adjustments_002.inputs[2])
    # map_range_7.Result -> _lab_adjustments_002.Hue
    _rr_hue_correct_pre.links.new(map_range_7.outputs[0], _lab_adjustments_002.inputs[3])
    # group_input_003_3.Orange Saturation -> _lab_adjustments_002.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[15], _lab_adjustments_002.inputs[4])
    # _lab_adjustments_002.A -> _lab_adjustments_003.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_002.outputs[0], _lab_adjustments_003.inputs[1])
    # _lab_adjustments_002.B -> _lab_adjustments_003.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_002.outputs[1], _lab_adjustments_003.inputs[2])
    # map_range_002_5.Result -> _lab_adjustments_003.Hue
    _rr_hue_correct_pre.links.new(map_range_002_5.outputs[0], _lab_adjustments_003.inputs[3])
    # group_input_003_3.Yellow Saturation -> _lab_adjustments_003.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[16], _lab_adjustments_003.inputs[4])
    # _lab_adjustments_003.A -> _lab_adjustments_004.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_003.outputs[0], _lab_adjustments_004.inputs[1])
    # _lab_adjustments_003.B -> _lab_adjustments_004.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_003.outputs[1], _lab_adjustments_004.inputs[2])
    # map_range_003_4.Result -> _lab_adjustments_004.Hue
    _rr_hue_correct_pre.links.new(map_range_003_4.outputs[0], _lab_adjustments_004.inputs[3])
    # group_input_003_3.Green Saturation -> _lab_adjustments_004.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[17], _lab_adjustments_004.inputs[4])
    # _lab_adjustments_004.A -> _lab_adjustments_005.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_004.outputs[0], _lab_adjustments_005.inputs[1])
    # _lab_adjustments_004.B -> _lab_adjustments_005.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_004.outputs[1], _lab_adjustments_005.inputs[2])
    # map_range_004_2.Result -> _lab_adjustments_005.Hue
    _rr_hue_correct_pre.links.new(map_range_004_2.outputs[0], _lab_adjustments_005.inputs[3])
    # group_input_003_3.Teal Saturation -> _lab_adjustments_005.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[18], _lab_adjustments_005.inputs[4])
    # _lab_adjustments_005.A -> _lab_adjustments_006.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_005.outputs[0], _lab_adjustments_006.inputs[1])
    # _lab_adjustments_005.B -> _lab_adjustments_006.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_005.outputs[1], _lab_adjustments_006.inputs[2])
    # map_range_005_3.Result -> _lab_adjustments_006.Hue
    _rr_hue_correct_pre.links.new(map_range_005_3.outputs[0], _lab_adjustments_006.inputs[3])
    # group_input_003_3.Blue Saturation -> _lab_adjustments_006.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[19], _lab_adjustments_006.inputs[4])
    # _lab_adjustments_006.A -> _lab_adjustments_007.A
    _rr_hue_correct_pre.links.new(_lab_adjustments_006.outputs[0], _lab_adjustments_007.inputs[1])
    # _lab_adjustments_006.B -> _lab_adjustments_007.B
    _rr_hue_correct_pre.links.new(_lab_adjustments_006.outputs[1], _lab_adjustments_007.inputs[2])
    # _lab_adjustments_007.A -> reroute_008_1.Input
    _rr_hue_correct_pre.links.new(_lab_adjustments_007.outputs[0], reroute_008_1.inputs[0])
    # _lab_adjustments_007.B -> reroute_009_1.Input
    _rr_hue_correct_pre.links.new(_lab_adjustments_007.outputs[1], reroute_009_1.inputs[0])
    # map_range_006_1.Result -> _lab_adjustments_007.Hue
    _rr_hue_correct_pre.links.new(map_range_006_1.outputs[0], _lab_adjustments_007.inputs[3])
    # group_input_003_3.Pink Saturation -> _lab_adjustments_007.Chroma
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[20], _lab_adjustments_007.inputs[4])
    # reroute_010_1.Output -> _lab_to_srgb.A
    _rr_hue_correct_pre.links.new(reroute_010_1.outputs[0], _lab_to_srgb.inputs[1])
    # reroute_011_1.Output -> _lab_to_srgb.B
    _rr_hue_correct_pre.links.new(reroute_011_1.outputs[0], _lab_to_srgb.inputs[2])
    # reroute_015.Output -> mix_001_4.B
    _rr_hue_correct_pre.links.new(reroute_015.outputs[0], mix_001_4.inputs[7])
    # combine_color_001_1.Image -> reroute_015.Input
    _rr_hue_correct_pre.links.new(combine_color_001_1.outputs[0], reroute_015.inputs[0])
    # group_input_004_3.Perceptual -> math_12.Value
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[2], math_12.inputs[0])
    # math_12.Value -> switch_4.Switch
    _rr_hue_correct_pre.links.new(math_12.outputs[0], switch_4.inputs[0])
    # mix_001_4.Result -> switch_4.Off
    _rr_hue_correct_pre.links.new(mix_001_4.outputs[2], switch_4.inputs[1])
    # reroute_015.Output -> switch_4.On
    _rr_hue_correct_pre.links.new(reroute_015.outputs[0], switch_4.inputs[2])
    # group_input_004_3.Perceptual -> math_002_9.Value
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[2], math_002_9.inputs[0])
    # switch_4.Image -> switch_001.Off
    _rr_hue_correct_pre.links.new(switch_4.outputs[0], switch_001.inputs[1])
    # reroute_016.Output -> switch_001.On
    _rr_hue_correct_pre.links.new(reroute_016.outputs[0], switch_001.inputs[2])
    # math_002_9.Value -> switch_001.Switch
    _rr_hue_correct_pre.links.new(math_002_9.outputs[0], switch_001.inputs[0])
    # combine_color_4.Image -> reroute_016.Input
    _rr_hue_correct_pre.links.new(combine_color_4.outputs[0], reroute_016.inputs[0])
    # reroute_019.Output -> group_009.Factor
    _rr_hue_correct_pre.links.new(reroute_019.outputs[0], group_009.inputs[0])
    # group_input_002_2.Red Saturation -> group_009.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[14], group_009.inputs[2])
    # reroute_023.Output -> group_010.Factor
    _rr_hue_correct_pre.links.new(reroute_023.outputs[0], group_010.inputs[0])
    # group_009.Result -> group_010.Image
    _rr_hue_correct_pre.links.new(group_009.outputs[0], group_010.inputs[1])
    # group_input_002_2.Orange Saturation -> group_010.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[15], group_010.inputs[2])
    # reroute_024.Output -> group_011.Factor
    _rr_hue_correct_pre.links.new(reroute_024.outputs[0], group_011.inputs[0])
    # group_010.Result -> group_011.Image
    _rr_hue_correct_pre.links.new(group_010.outputs[0], group_011.inputs[1])
    # group_input_002_2.Yellow Saturation -> group_011.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[16], group_011.inputs[2])
    # reroute_025.Output -> group_012.Factor
    _rr_hue_correct_pre.links.new(reroute_025.outputs[0], group_012.inputs[0])
    # group_input_002_2.Green Saturation -> group_012.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[17], group_012.inputs[2])
    # group_011.Result -> group_012.Image
    _rr_hue_correct_pre.links.new(group_011.outputs[0], group_012.inputs[1])
    # reroute_022.Output -> group_013.Factor
    _rr_hue_correct_pre.links.new(reroute_022.outputs[0], group_013.inputs[0])
    # group_012.Result -> group_013.Image
    _rr_hue_correct_pre.links.new(group_012.outputs[0], group_013.inputs[1])
    # group_input_002_2.Teal Saturation -> group_013.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[18], group_013.inputs[2])
    # reroute_020.Output -> group_014.Factor
    _rr_hue_correct_pre.links.new(reroute_020.outputs[0], group_014.inputs[0])
    # group_013.Result -> group_014.Image
    _rr_hue_correct_pre.links.new(group_013.outputs[0], group_014.inputs[1])
    # group_input_002_2.Blue Saturation -> group_014.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[19], group_014.inputs[2])
    # reroute_021.Output -> group_015.Factor
    _rr_hue_correct_pre.links.new(reroute_021.outputs[0], group_015.inputs[0])
    # group_014.Result -> group_015.Image
    _rr_hue_correct_pre.links.new(group_014.outputs[0], group_015.inputs[1])
    # group_input_002_2.Pink Saturation -> group_015.Multiply
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[20], group_015.inputs[2])
    # reroute_005_5.Output -> reroute_004_4.Input
    _rr_hue_correct_pre.links.new(reroute_005_5.outputs[0], reroute_004_4.inputs[0])
    # group_015.Result -> reroute_005_5.Input
    _rr_hue_correct_pre.links.new(group_015.outputs[0], reroute_005_5.inputs[0])
    # group_025.Result -> group_026.Image
    _rr_hue_correct_pre.links.new(group_025.outputs[0], group_026.inputs[1])
    # group_026.Result -> group_027.Image
    _rr_hue_correct_pre.links.new(group_026.outputs[0], group_027.inputs[1])
    # group_027.Result -> group_028.Image
    _rr_hue_correct_pre.links.new(group_027.outputs[0], group_028.inputs[1])
    # group_028.Result -> group_029.Image
    _rr_hue_correct_pre.links.new(group_028.outputs[0], group_029.inputs[1])
    # group_029.Result -> group_030.Image
    _rr_hue_correct_pre.links.new(group_029.outputs[0], group_030.inputs[1])
    # group_030.Result -> group_031.Image
    _rr_hue_correct_pre.links.new(group_030.outputs[0], group_031.inputs[1])
    # group_031.Result -> reroute_002_5.Input
    _rr_hue_correct_pre.links.new(group_031.outputs[0], reroute_002_5.inputs[0])
    # reroute_007_2.Output -> group_004.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_004.inputs[0])
    # reroute_007_2.Output -> group_005.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_005.inputs[0])
    # reroute_007_2.Output -> group_006.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_006.inputs[0])
    # reroute_007_2.Output -> group_007.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_007.inputs[0])
    # reroute_007_2.Output -> group.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group.inputs[0])
    # reroute_007_2.Output -> group_001.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_001.inputs[0])
    # reroute_007_2.Output -> group_002.Image
    _rr_hue_correct_pre.links.new(reroute_007_2.outputs[0], group_002.inputs[0])
    # mix_8.Result -> group_output_14.Image
    _rr_hue_correct_pre.links.new(mix_8.outputs[2], group_output_14.inputs[0])
    # reroute_003_5.Output -> separate_color_3.Image
    _rr_hue_correct_pre.links.new(reroute_003_5.outputs[0], separate_color_3.inputs[0])
    # reroute_003_5.Output -> hue_correct.Image
    _rr_hue_correct_pre.links.new(reroute_003_5.outputs[0], hue_correct.inputs[1])
    # group_input_13.Input -> reroute_003_5.Input
    _rr_hue_correct_pre.links.new(group_input_13.outputs[1], reroute_003_5.inputs[0])
    # reroute_006_2.Output -> separate_color_001_3.Image
    _rr_hue_correct_pre.links.new(reroute_006_2.outputs[0], separate_color_001_3.inputs[0])
    # group_input_003_3.Orange Hue -> map_range_7.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[8], map_range_7.inputs[0])
    # group_input_003_3.Red Hue -> map_range_001_6.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[7], map_range_001_6.inputs[0])
    # map_range_001_6.Result -> _lab_adjustments_001.Hue
    _rr_hue_correct_pre.links.new(map_range_001_6.outputs[0], _lab_adjustments_001.inputs[3])
    # group_input_003_3.Yellow Hue -> map_range_002_5.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[9], map_range_002_5.inputs[0])
    # group_input_003_3.Green Hue -> map_range_003_4.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[10], map_range_003_4.inputs[0])
    # group_input_003_3.Teal Hue -> map_range_004_2.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[11], map_range_004_2.inputs[0])
    # group_input_003_3.Blue Hue -> map_range_005_3.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[12], map_range_005_3.inputs[0])
    # group_input_003_3.Pink Hue -> map_range_006_1.Value
    _rr_hue_correct_pre.links.new(group_input_003_3.outputs[13], map_range_006_1.inputs[0])
    # reroute_017.Output -> separate_color_004_1.Image
    _rr_hue_correct_pre.links.new(reroute_017.outputs[0], separate_color_004_1.inputs[0])
    # separate_color_004_1.Red -> combine_color_001_1.Red
    _rr_hue_correct_pre.links.new(separate_color_004_1.outputs[0], combine_color_001_1.inputs[0])
    # separate_color_004_1.Alpha -> combine_color_001_1.Alpha
    _rr_hue_correct_pre.links.new(separate_color_004_1.outputs[3], combine_color_001_1.inputs[3])
    # separate_color_004_1.Green -> clamp_001.Value
    _rr_hue_correct_pre.links.new(separate_color_004_1.outputs[1], clamp_001.inputs[0])
    # clamp_001.Result -> combine_color_001_1.Green
    _rr_hue_correct_pre.links.new(clamp_001.outputs[0], combine_color_001_1.inputs[1])
    # group_input_005_3.Smoothing -> group_004.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_004.inputs[4])
    # group_input_005_3.Smoothing -> group_005.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_005.inputs[4])
    # group_input_005_3.Smoothing -> group_006.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_006.inputs[4])
    # group_input_005_3.Smoothing -> group_007.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_007.inputs[4])
    # group_input_005_3.Smoothing -> group.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group.inputs[4])
    # group_input_005_3.Smoothing -> group_001.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_001.inputs[4])
    # group_input_005_3.Smoothing -> group_002.Smoothing
    _rr_hue_correct_pre.links.new(group_input_005_3.outputs[4], group_002.inputs[4])
    # reroute_042.Output -> reroute_019.Input
    _rr_hue_correct_pre.links.new(reroute_042.outputs[0], reroute_019.inputs[0])
    # reroute_037.Output -> reroute_020.Input
    _rr_hue_correct_pre.links.new(reroute_037.outputs[0], reroute_020.inputs[0])
    # reroute_043.Output -> reroute_021.Input
    _rr_hue_correct_pre.links.new(reroute_043.outputs[0], reroute_021.inputs[0])
    # reroute_047.Output -> reroute_022.Input
    _rr_hue_correct_pre.links.new(reroute_047.outputs[0], reroute_022.inputs[0])
    # reroute_041.Output -> reroute_023.Input
    _rr_hue_correct_pre.links.new(reroute_041.outputs[0], reroute_023.inputs[0])
    # reroute_035.Output -> reroute_024.Input
    _rr_hue_correct_pre.links.new(reroute_035.outputs[0], reroute_024.inputs[0])
    # reroute_039.Output -> reroute_025.Input
    _rr_hue_correct_pre.links.new(reroute_039.outputs[0], reroute_025.inputs[0])
    # reroute_028.Output -> _lab_adjustments_001.Factor
    _rr_hue_correct_pre.links.new(reroute_028.outputs[0], _lab_adjustments_001.inputs[0])
    # reroute_019.Output -> reroute_028.Input
    _rr_hue_correct_pre.links.new(reroute_019.outputs[0], reroute_028.inputs[0])
    # reroute_029.Output -> _lab_adjustments_002.Factor
    _rr_hue_correct_pre.links.new(reroute_029.outputs[0], _lab_adjustments_002.inputs[0])
    # reroute_030.Output -> _lab_adjustments_003.Factor
    _rr_hue_correct_pre.links.new(reroute_030.outputs[0], _lab_adjustments_003.inputs[0])
    # reroute_031.Output -> _lab_adjustments_004.Factor
    _rr_hue_correct_pre.links.new(reroute_031.outputs[0], _lab_adjustments_004.inputs[0])
    # reroute_032.Output -> _lab_adjustments_005.Factor
    _rr_hue_correct_pre.links.new(reroute_032.outputs[0], _lab_adjustments_005.inputs[0])
    # reroute_033.Output -> _lab_adjustments_006.Factor
    _rr_hue_correct_pre.links.new(reroute_033.outputs[0], _lab_adjustments_006.inputs[0])
    # reroute_034.Output -> _lab_adjustments_007.Factor
    _rr_hue_correct_pre.links.new(reroute_034.outputs[0], _lab_adjustments_007.inputs[0])
    # reroute_023.Output -> reroute_029.Input
    _rr_hue_correct_pre.links.new(reroute_023.outputs[0], reroute_029.inputs[0])
    # reroute_024.Output -> reroute_030.Input
    _rr_hue_correct_pre.links.new(reroute_024.outputs[0], reroute_030.inputs[0])
    # reroute_025.Output -> reroute_031.Input
    _rr_hue_correct_pre.links.new(reroute_025.outputs[0], reroute_031.inputs[0])
    # reroute_022.Output -> reroute_032.Input
    _rr_hue_correct_pre.links.new(reroute_022.outputs[0], reroute_032.inputs[0])
    # reroute_020.Output -> reroute_033.Input
    _rr_hue_correct_pre.links.new(reroute_020.outputs[0], reroute_033.inputs[0])
    # reroute_021.Output -> reroute_034.Input
    _rr_hue_correct_pre.links.new(reroute_021.outputs[0], reroute_034.inputs[0])
    # group_input_002_2.Input -> separate_color_003_2.Image
    _rr_hue_correct_pre.links.new(group_input_002_2.outputs[1], separate_color_003_2.inputs[0])
    # group_004.Value -> reroute_012_1.Input
    _rr_hue_correct_pre.links.new(group_004.outputs[1], reroute_012_1.inputs[0])
    # group_006.Mask -> reroute_035.Input
    _rr_hue_correct_pre.links.new(group_006.outputs[0], reroute_035.inputs[0])
    # group_007.Value -> reroute_036.Input
    _rr_hue_correct_pre.links.new(group_007.outputs[1], reroute_036.inputs[0])
    # group_001.Mask -> reroute_037.Input
    _rr_hue_correct_pre.links.new(group_001.outputs[0], reroute_037.inputs[0])
    # group_005.Value -> reroute_038.Input
    _rr_hue_correct_pre.links.new(group_005.outputs[1], reroute_038.inputs[0])
    # group_007.Mask -> reroute_039.Input
    _rr_hue_correct_pre.links.new(group_007.outputs[0], reroute_039.inputs[0])
    # group_002.Value -> reroute_040.Input
    _rr_hue_correct_pre.links.new(group_002.outputs[1], reroute_040.inputs[0])
    # group_005.Mask -> reroute_041.Input
    _rr_hue_correct_pre.links.new(group_005.outputs[0], reroute_041.inputs[0])
    # group_004.Mask -> reroute_042.Input
    _rr_hue_correct_pre.links.new(group_004.outputs[0], reroute_042.inputs[0])
    # group_002.Mask -> reroute_043.Input
    _rr_hue_correct_pre.links.new(group_002.outputs[0], reroute_043.inputs[0])
    # group_001.Value -> reroute_044.Input
    _rr_hue_correct_pre.links.new(group_001.outputs[1], reroute_044.inputs[0])
    # group.Value -> reroute_045.Input
    _rr_hue_correct_pre.links.new(group.outputs[1], reroute_045.inputs[0])
    # group_006.Value -> reroute_046.Input
    _rr_hue_correct_pre.links.new(group_006.outputs[1], reroute_046.inputs[0])
    # group.Mask -> reroute_047.Input
    _rr_hue_correct_pre.links.new(group.outputs[0], reroute_047.inputs[0])
    # reroute_006_2.Output -> _srgb_to_lab.Image
    _rr_hue_correct_pre.links.new(reroute_006_2.outputs[0], _srgb_to_lab.inputs[0])
    # reroute_048.Output -> reroute_017.Input
    _rr_hue_correct_pre.links.new(reroute_048.outputs[0], reroute_017.inputs[0])
    # _lab_to_srgb.Image -> reroute_048.Input
    _rr_hue_correct_pre.links.new(_lab_to_srgb.outputs[0], reroute_048.inputs[0])
    # group_input_13.Input -> separate_color_006.Image
    _rr_hue_correct_pre.links.new(group_input_13.outputs[1], separate_color_006.inputs[0])
    # separate_color_004_1.Blue -> combine_color_001_1.Blue
    _rr_hue_correct_pre.links.new(separate_color_004_1.outputs[2], combine_color_001_1.inputs[2])
    # separate_color_006.Red -> combine_color_002_1.Red
    _rr_hue_correct_pre.links.new(separate_color_006.outputs[0], combine_color_002_1.inputs[0])
    # separate_color_006.Green -> combine_color_002_1.Green
    _rr_hue_correct_pre.links.new(separate_color_006.outputs[1], combine_color_002_1.inputs[1])
    # separate_color_006.Alpha -> combine_color_002_1.Alpha
    _rr_hue_correct_pre.links.new(separate_color_006.outputs[3], combine_color_002_1.inputs[3])
    # combine_color_002_1.Image -> reroute_006_2.Input
    _rr_hue_correct_pre.links.new(combine_color_002_1.outputs[0], reroute_006_2.inputs[0])
    # group_033.Result -> group_034.Image
    _rr_hue_correct_pre.links.new(group_033.outputs[0], group_034.inputs[1])
    # group_034.Result -> group_035.Image
    _rr_hue_correct_pre.links.new(group_034.outputs[0], group_035.inputs[1])
    # group_035.Result -> group_036.Image
    _rr_hue_correct_pre.links.new(group_035.outputs[0], group_036.inputs[1])
    # group_036.Result -> group_037.Image
    _rr_hue_correct_pre.links.new(group_036.outputs[0], group_037.inputs[1])
    # group_037.Result -> group_038.Image
    _rr_hue_correct_pre.links.new(group_037.outputs[0], group_038.inputs[1])
    # group_038.Result -> group_039.Image
    _rr_hue_correct_pre.links.new(group_038.outputs[0], group_039.inputs[1])
    # math_006_8.Value -> group_033.Factor
    _rr_hue_correct_pre.links.new(math_006_8.outputs[0], group_033.inputs[0])
    # math_007_8.Value -> group_034.Factor
    _rr_hue_correct_pre.links.new(math_007_8.outputs[0], group_034.inputs[0])
    # math_008_7.Value -> group_035.Factor
    _rr_hue_correct_pre.links.new(math_008_7.outputs[0], group_035.inputs[0])
    # group_007.Mask -> group_036.Factor
    _rr_hue_correct_pre.links.new(group_007.outputs[0], group_036.inputs[0])
    # math_010_4.Value -> group_037.Factor
    _rr_hue_correct_pre.links.new(math_010_4.outputs[0], group_037.inputs[0])
    # math_011_4.Value -> group_038.Factor
    _rr_hue_correct_pre.links.new(math_011_4.outputs[0], group_038.inputs[0])
    # math_030_1.Value -> group_039.Factor
    _rr_hue_correct_pre.links.new(math_030_1.outputs[0], group_039.inputs[0])
    # reroute_049.Output -> combine_color_002_1.Blue
    _rr_hue_correct_pre.links.new(reroute_049.outputs[0], combine_color_002_1.inputs[2])
    # reroute_050.Output -> reroute_049.Input
    _rr_hue_correct_pre.links.new(reroute_050.outputs[0], reroute_049.inputs[0])
    # group_039.Result -> reroute_050.Input
    _rr_hue_correct_pre.links.new(group_039.outputs[0], reroute_050.inputs[0])
    # switch_001.Image -> mix_8.B
    _rr_hue_correct_pre.links.new(switch_001.outputs[0], mix_8.inputs[7])
    # reroute_052.Output -> mix_8.A
    _rr_hue_correct_pre.links.new(reroute_052.outputs[0], mix_8.inputs[6])
    # reroute_053.Output -> reroute_051.Input
    _rr_hue_correct_pre.links.new(reroute_053.outputs[0], reroute_051.inputs[0])
    # reroute_054.Output -> reroute_052.Input
    _rr_hue_correct_pre.links.new(reroute_054.outputs[0], reroute_052.inputs[0])
    # group_input_004_3.Factor -> reroute_053.Input
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[0], reroute_053.inputs[0])
    # group_input_004_3.Input -> reroute_054.Input
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[1], reroute_054.inputs[0])
    # reroute_055.Output -> group_004.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group_004.inputs[3])
    # reroute_055.Output -> group_006.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group_006.inputs[3])
    # reroute_055.Output -> group_007.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group_007.inputs[3])
    # reroute_055.Output -> group_001.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group_001.inputs[3])
    # reroute_055.Output -> group_002.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group_002.inputs[3])
    # math_004_9.Value -> math_003_10.Value
    _rr_hue_correct_pre.links.new(math_004_9.outputs[0], math_003_10.inputs[0])
    # math_003_10.Value -> group_005.Range
    _rr_hue_correct_pre.links.new(math_003_10.outputs[0], group_005.inputs[3])
    # value.Value -> math_004_9.Value
    _rr_hue_correct_pre.links.new(value.outputs[0], math_004_9.inputs[0])
    # math_004_9.Value -> reroute_055.Input
    _rr_hue_correct_pre.links.new(math_004_9.outputs[0], reroute_055.inputs[0])
    # clamp.Result -> combine_color_4.Green
    _rr_hue_correct_pre.links.new(clamp.outputs[0], combine_color_4.inputs[1])
    # map_range_007.Result -> math_004_9.Value
    _rr_hue_correct_pre.links.new(map_range_007.outputs[0], math_004_9.inputs[1])
    # group_input_13.Range -> map_range_007.Value
    _rr_hue_correct_pre.links.new(group_input_13.outputs[3], map_range_007.inputs[0])
    # math_013_3.Value -> math_014_3.Value
    _rr_hue_correct_pre.links.new(math_013_3.outputs[0], math_014_3.inputs[0])
    # group_input_001_4.Pink Hue -> math_013_3.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[13], math_013_3.inputs[0])
    # math_015_3.Value -> math_016_3.Value
    _rr_hue_correct_pre.links.new(math_015_3.outputs[0], math_016_3.inputs[0])
    # group_input_001_4.Blue Hue -> math_015_3.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[12], math_015_3.inputs[0])
    # math_028_3.Value -> group_029.Add
    _rr_hue_correct_pre.links.new(math_028_3.outputs[0], group_029.inputs[3])
    # group_input_004_3.Saturation Mask -> reroute_057.Input
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[5], reroute_057.inputs[0])
    # group_input_004_3.Value Mask -> reroute_058.Input
    _rr_hue_correct_pre.links.new(group_input_004_3.outputs[6], reroute_058.inputs[0])
    # reroute_052.Output -> separate_color_007.Image
    _rr_hue_correct_pre.links.new(reroute_052.outputs[0], separate_color_007.inputs[0])
    # reroute_051.Output -> math_029_2.Value
    _rr_hue_correct_pre.links.new(reroute_051.outputs[0], math_029_2.inputs[1])
    # math_032_1.Value -> math_029_2.Value
    _rr_hue_correct_pre.links.new(math_032_1.outputs[0], math_029_2.inputs[0])
    # reroute_057.Output -> reroute_061.Input
    _rr_hue_correct_pre.links.new(reroute_057.outputs[0], reroute_061.inputs[0])
    # reroute_058.Output -> reroute_062.Input
    _rr_hue_correct_pre.links.new(reroute_058.outputs[0], reroute_062.inputs[0])
    # math_029_2.Value -> mix_8.Factor
    _rr_hue_correct_pre.links.new(math_029_2.outputs[0], mix_8.inputs[0])
    # reroute_055.Output -> group.Range
    _rr_hue_correct_pre.links.new(reroute_055.outputs[0], group.inputs[3])
    # separate_color_006.Blue -> group_033.Image
    _rr_hue_correct_pre.links.new(separate_color_006.outputs[2], group_033.inputs[1])
    # reroute_026.Output -> group_025.Image
    _rr_hue_correct_pre.links.new(reroute_026.outputs[0], group_025.inputs[1])
    # separate_color_003_2.Green -> group_009.Image
    _rr_hue_correct_pre.links.new(separate_color_003_2.outputs[1], group_009.inputs[1])
    # reroute_014.Output -> _lab_adjustments_001.A
    _rr_hue_correct_pre.links.new(reroute_014.outputs[0], _lab_adjustments_001.inputs[1])
    # reroute_013_1.Output -> _lab_adjustments_001.B
    _rr_hue_correct_pre.links.new(reroute_013_1.outputs[0], _lab_adjustments_001.inputs[2])
    # math_014_3.Value -> math_012_3.Value
    _rr_hue_correct_pre.links.new(math_014_3.outputs[0], math_012_3.inputs[0])
    # math_012_3.Value -> group_031.Add
    _rr_hue_correct_pre.links.new(math_012_3.outputs[0], group_031.inputs[3])
    # math_016_3.Value -> math_027_3.Value
    _rr_hue_correct_pre.links.new(math_016_3.outputs[0], math_027_3.inputs[0])
    # math_027_3.Value -> group_030.Add
    _rr_hue_correct_pre.links.new(math_027_3.outputs[0], group_030.inputs[3])
    # math_017_3.Value -> math_018_2.Value
    _rr_hue_correct_pre.links.new(math_017_3.outputs[0], math_018_2.inputs[0])
    # math_018_2.Value -> math_028_3.Value
    _rr_hue_correct_pre.links.new(math_018_2.outputs[0], math_028_3.inputs[0])
    # group_input_001_4.Teal Hue -> math_017_3.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[11], math_017_3.inputs[0])
    # math_019_2.Value -> math_020_2.Value
    _rr_hue_correct_pre.links.new(math_019_2.outputs[0], math_020_2.inputs[0])
    # math_020_2.Value -> math_033.Value
    _rr_hue_correct_pre.links.new(math_020_2.outputs[0], math_033.inputs[0])
    # group_input_001_4.Green Hue -> math_019_2.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[10], math_019_2.inputs[0])
    # math_033.Value -> group_028.Add
    _rr_hue_correct_pre.links.new(math_033.outputs[0], group_028.inputs[3])
    # math_021_2.Value -> math_022_3.Value
    _rr_hue_correct_pre.links.new(math_021_2.outputs[0], math_022_3.inputs[0])
    # math_022_3.Value -> math_034.Value
    _rr_hue_correct_pre.links.new(math_022_3.outputs[0], math_034.inputs[0])
    # group_input_001_4.Yellow Hue -> math_021_2.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[9], math_021_2.inputs[0])
    # math_034.Value -> group_027.Add
    _rr_hue_correct_pre.links.new(math_034.outputs[0], group_027.inputs[3])
    # math_023_3.Value -> math_024_3.Value
    _rr_hue_correct_pre.links.new(math_023_3.outputs[0], math_024_3.inputs[0])
    # math_024_3.Value -> math_035.Value
    _rr_hue_correct_pre.links.new(math_024_3.outputs[0], math_035.inputs[0])
    # math_035.Value -> group_026.Add
    _rr_hue_correct_pre.links.new(math_035.outputs[0], group_026.inputs[3])
    # group_input_001_4.Orange Hue -> math_023_3.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[8], math_023_3.inputs[0])
    # math_025_3.Value -> math_026_3.Value
    _rr_hue_correct_pre.links.new(math_025_3.outputs[0], math_026_3.inputs[0])
    # math_026_3.Value -> math_036.Value
    _rr_hue_correct_pre.links.new(math_026_3.outputs[0], math_036.inputs[0])
    # group_input_001_4.Red Hue -> math_025_3.Value
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[7], math_025_3.inputs[0])
    # math_036.Value -> group_025.Add
    _rr_hue_correct_pre.links.new(math_036.outputs[0], group_025.inputs[3])
    # reroute_042.Output -> group_025.Factor
    _rr_hue_correct_pre.links.new(reroute_042.outputs[0], group_025.inputs[0])
    # reroute_041.Output -> group_026.Factor
    _rr_hue_correct_pre.links.new(reroute_041.outputs[0], group_026.inputs[0])
    # reroute_035.Output -> group_027.Factor
    _rr_hue_correct_pre.links.new(reroute_035.outputs[0], group_027.inputs[0])
    # reroute_039.Output -> group_028.Factor
    _rr_hue_correct_pre.links.new(reroute_039.outputs[0], group_028.inputs[0])
    # reroute_047.Output -> group_029.Factor
    _rr_hue_correct_pre.links.new(reroute_047.outputs[0], group_029.inputs[0])
    # reroute_037.Output -> group_030.Factor
    _rr_hue_correct_pre.links.new(reroute_037.outputs[0], group_030.inputs[0])
    # reroute_043.Output -> group_031.Factor
    _rr_hue_correct_pre.links.new(reroute_043.outputs[0], group_031.inputs[0])
    # separate_color_005.Red -> reroute_007_2.Input
    _rr_hue_correct_pre.links.new(separate_color_005.outputs[0], reroute_007_2.inputs[0])
    # separate_color_005.Green -> map_range_012.Value
    _rr_hue_correct_pre.links.new(separate_color_005.outputs[1], map_range_012.inputs[0])
    # reroute_018.Output -> group_004.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_004.inputs[1])
    # map_range_012.Result -> reroute_018.Input
    _rr_hue_correct_pre.links.new(map_range_012.outputs[0], reroute_018.inputs[0])
    # reroute_018.Output -> group_005.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_005.inputs[1])
    # reroute_018.Output -> group_006.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_006.inputs[1])
    # reroute_018.Output -> group_007.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_007.inputs[1])
    # reroute_018.Output -> group.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group.inputs[1])
    # reroute_018.Output -> group_001.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_001.inputs[1])
    # reroute_018.Output -> group_002.Mask
    _rr_hue_correct_pre.links.new(reroute_018.outputs[0], group_002.inputs[1])
    # reroute_027.Output -> reroute_026.Input
    _rr_hue_correct_pre.links.new(reroute_027.outputs[0], reroute_026.inputs[0])
    # separate_color_002_1.Red -> reroute_027.Input
    _rr_hue_correct_pre.links.new(separate_color_002_1.outputs[0], reroute_027.inputs[0])
    # group_input_001_4.Input -> separate_color_002_1.Image
    _rr_hue_correct_pre.links.new(group_input_001_4.outputs[1], separate_color_002_1.inputs[0])
    # group_input_13.Input -> separate_color_005.Image
    _rr_hue_correct_pre.links.new(group_input_13.outputs[1], separate_color_005.inputs[0])
    # group_input_006.Red Value -> group_033.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[21], group_033.inputs[2])
    # group_input_006.Orange Value -> group_034.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[22], group_034.inputs[2])
    # group_input_006.Yellow Value -> group_035.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[23], group_035.inputs[2])
    # math_009_5.Value -> group_036.Multiply
    _rr_hue_correct_pre.links.new(math_009_5.outputs[0], group_036.inputs[2])
    # group_input_006.Teal Value -> group_037.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[25], group_037.inputs[2])
    # group_input_006.Blue Value -> group_038.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[26], group_038.inputs[2])
    # group_input_006.Pink Value -> group_039.Multiply
    _rr_hue_correct_pre.links.new(group_input_006.outputs[27], group_039.inputs[2])
    # reroute_061.Output -> group_016.Value
    _rr_hue_correct_pre.links.new(reroute_061.outputs[0], group_016.inputs[0])
    # separate_color_007.Green -> group_016.Mask
    _rr_hue_correct_pre.links.new(separate_color_007.outputs[1], group_016.inputs[1])
    # group_016.Result -> math_032_1.Value
    _rr_hue_correct_pre.links.new(group_016.outputs[0], math_032_1.inputs[0])
    # reroute_062.Output -> group_017.Value
    _rr_hue_correct_pre.links.new(reroute_062.outputs[0], group_017.inputs[0])
    # group_017.Result -> math_032_1.Value
    _rr_hue_correct_pre.links.new(group_017.outputs[0], math_032_1.inputs[1])
    # float_curve_2.Value -> group_017.Mask
    _rr_hue_correct_pre.links.new(float_curve_2.outputs[0], group_017.inputs[1])
    # separate_color_007.Blue -> float_curve_2.Value
    _rr_hue_correct_pre.links.new(separate_color_007.outputs[2], float_curve_2.inputs[1])
    # reroute_062.Output -> math_005_9.Value
    _rr_hue_correct_pre.links.new(reroute_062.outputs[0], math_005_9.inputs[0])
    # math_005_9.Value -> float_curve_2.Factor
    _rr_hue_correct_pre.links.new(math_005_9.outputs[0], float_curve_2.inputs[0])
    # group_004.Mask -> math_006_8.Value
    _rr_hue_correct_pre.links.new(group_004.outputs[0], math_006_8.inputs[0])
    # group_005.Mask -> math_007_8.Value
    _rr_hue_correct_pre.links.new(group_005.outputs[0], math_007_8.inputs[0])
    # group_006.Mask -> math_008_7.Value
    _rr_hue_correct_pre.links.new(group_006.outputs[0], math_008_7.inputs[0])
    # group_input_006.Green Value -> math_009_5.Value
    _rr_hue_correct_pre.links.new(group_input_006.outputs[24], math_009_5.inputs[0])
    # group.Mask -> math_010_4.Value
    _rr_hue_correct_pre.links.new(group.outputs[0], math_010_4.inputs[0])
    # group_001.Mask -> math_011_4.Value
    _rr_hue_correct_pre.links.new(group_001.outputs[0], math_011_4.inputs[0])
    # group_002.Mask -> math_030_1.Value
    _rr_hue_correct_pre.links.new(group_002.outputs[0], math_030_1.inputs[0])

    return _rr_hue_correct_pre


_rr_hue_correct_pre = _rr_hue_correct_pre_node_group()

def _rr_pre_node_group():
    """Initialize .RR_Pre node group"""
    _rr_pre = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_Pre")

    _rr_pre.color_tag = 'NONE'
    _rr_pre.description = ""
    _rr_pre.default_group_node_width = 140
    # _rr_pre interface

    # Socket Image
    image_socket_19 = _rr_pre.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_19.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_19.attribute_domain = 'POINT'
    image_socket_19.default_input = 'VALUE'
    image_socket_19.structure_type = 'AUTO'

    # Socket Glare
    glare_socket_2 = _rr_pre.interface.new_socket(name="Glare", in_out='OUTPUT', socket_type='NodeSocketColor')
    glare_socket_2.default_value = (0.0, 0.0, 0.0, 1.0)
    glare_socket_2.attribute_domain = 'POINT'
    glare_socket_2.default_input = 'VALUE'
    glare_socket_2.structure_type = 'AUTO'

    # Socket Image
    image_socket_20 = _rr_pre.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_20.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_20.attribute_domain = 'POINT'
    image_socket_20.default_input = 'VALUE'
    image_socket_20.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_7 = _rr_pre.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_7.default_value = 1.0
    factor_socket_7.min_value = 0.0
    factor_socket_7.max_value = 1.0
    factor_socket_7.subtype = 'FACTOR'
    factor_socket_7.attribute_domain = 'POINT'
    factor_socket_7.default_input = 'VALUE'
    factor_socket_7.structure_type = 'AUTO'

    # Initialize _rr_pre nodes

    # Node Pre Layer Output
    pre_layer_output = _rr_pre.nodes.new("NodeGroupOutput")
    pre_layer_output.label = "Pre Layer Output"
    pre_layer_output.name = "Pre Layer Output"
    pre_layer_output.is_active_output = True

    # Node Pre Layer Input
    pre_layer_input = _rr_pre.nodes.new("NodeGroupInput")
    pre_layer_input.label = "Pre Layer Input"
    pre_layer_input.name = "Pre Layer Input"

    # Node Frame.002
    frame_002_7 = _rr_pre.nodes.new("NodeFrame")
    frame_002_7.label = "Pre Color"
    frame_002_7.name = "Frame.002"
    frame_002_7.label_size = 20
    frame_002_7.shrink = True

    # Node Frame.003
    frame_003_6 = _rr_pre.nodes.new("NodeFrame")
    frame_003_6.label = "Pre Effects 2"
    frame_003_6.name = "Frame.003"
    frame_003_6.label_size = 20
    frame_003_6.shrink = True

    # Node Frame.004
    frame_004_5 = _rr_pre.nodes.new("NodeFrame")
    frame_004_5.label = "Pre Values"
    frame_004_5.name = "Frame.004"
    frame_004_5.label_size = 20
    frame_004_5.shrink = True

    # Node Color Boost
    color_boost = _rr_pre.nodes.new("CompositorNodeGroup")
    color_boost.label = "Color Boost"
    color_boost.name = "Color Boost"
    color_boost.use_custom_color = True
    color_boost.color = (0.0, 0.0, 0.0)
    color_boost.hide = True
    color_boost.node_tree = _rr_color_boost
    color_boost.inputs[1].hide = True
    color_boost.inputs[2].hide = True
    # Socket_2
    color_boost.inputs[1].default_value = 0.30000001192092896
    # Socket_3
    color_boost.inputs[2].default_value = 1.0

    # Node White Balance
    white_balance_1 = _rr_pre.nodes.new("CompositorNodeGroup")
    white_balance_1.label = "White Balance"
    white_balance_1.name = "White Balance"
    white_balance_1.use_custom_color = True
    white_balance_1.color = (0.0, 0.0, 0.0)
    white_balance_1.mute = True
    white_balance_1.hide = True
    white_balance_1.node_tree = _rr_white_balance
    white_balance_1.inputs[1].hide = True
    white_balance_1.inputs[2].hide = True
    white_balance_1.inputs[3].hide = True
    white_balance_1.inputs[4].hide = True
    # Socket_5
    white_balance_1.inputs[1].default_value = 1.0
    # Socket_1
    white_balance_1.inputs[2].default_value = 0.5
    # Socket_2
    white_balance_1.inputs[3].default_value = 0.4699999988079071
    # Socket_4
    white_balance_1.inputs[4].default_value = 1.0

    # Node Exposure
    exposure = _rr_pre.nodes.new("CompositorNodeExposure")
    exposure.name = "Exposure"
    exposure.use_custom_color = True
    exposure.color = (0.0, 0.0, 0.0)
    exposure.mute = True
    exposure.hide = True
    exposure.inputs[1].hide = True
    # Exposure
    exposure.inputs[1].default_value = 0.0

    # Node Contrast
    contrast = _rr_pre.nodes.new("CompositorNodeGroup")
    contrast.label = "Contrast"
    contrast.name = "Contrast"
    contrast.use_custom_color = True
    contrast.color = (0.0, 0.0, 0.0)
    contrast.hide = True
    contrast.node_tree = _rr_contrast
    contrast.inputs[1].hide = True
    contrast.inputs[2].hide = True
    contrast.inputs[3].hide = True
    # Socket_2
    contrast.inputs[1].default_value = 0.0
    # Socket_4
    contrast.inputs[2].default_value = 0.20000000298023224
    # Socket_5
    contrast.inputs[3].default_value = 0.5

    # Node Offset Power Slope
    offset_power_slope = _rr_pre.nodes.new("CompositorNodeColorBalance")
    offset_power_slope.label = "Offset Power Slope"
    offset_power_slope.name = "Offset Power Slope"
    offset_power_slope.use_custom_color = True
    offset_power_slope.color = (0.0, 0.0, 0.0)
    offset_power_slope.mute = True
    offset_power_slope.hide = True
    offset_power_slope.correction_method = 'OFFSET_POWER_SLOPE'
    offset_power_slope.input_whitepoint = mathutils.Color((0.9991403222084045, 1.0003736019134521, 0.998818039894104))
    offset_power_slope.output_whitepoint = mathutils.Color((0.9991403222084045, 1.0003736019134521, 0.998818039894104))
    offset_power_slope.inputs[0].hide = True
    offset_power_slope.inputs[2].hide = True
    offset_power_slope.inputs[3].hide = True
    offset_power_slope.inputs[4].hide = True
    offset_power_slope.inputs[5].hide = True
    offset_power_slope.inputs[6].hide = True
    offset_power_slope.inputs[7].hide = True
    offset_power_slope.inputs[8].hide = True
    offset_power_slope.inputs[9].hide = True
    offset_power_slope.inputs[10].hide = True
    offset_power_slope.inputs[11].hide = True
    offset_power_slope.inputs[12].hide = True
    offset_power_slope.inputs[13].hide = True
    offset_power_slope.inputs[14].hide = True
    offset_power_slope.inputs[15].hide = True
    offset_power_slope.inputs[16].hide = True
    offset_power_slope.inputs[17].hide = True
    # Fac
    offset_power_slope.inputs[0].default_value = 1.0
    # Base Offset
    offset_power_slope.inputs[8].default_value = 0.0
    # Color Offset
    offset_power_slope.inputs[9].default_value = (0.0, 0.0, 0.0, 1.0)
    # Base Power
    offset_power_slope.inputs[10].default_value = 1.0
    # Color Power
    offset_power_slope.inputs[11].default_value = (1.0, 1.0, 1.0, 1.0)
    # Base Slope
    offset_power_slope.inputs[12].default_value = 1.0
    # Color Slope
    offset_power_slope.inputs[13].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Glare
    glare_1 = _rr_pre.nodes.new("CompositorNodeGroup")
    glare_1.label = "Glare"
    glare_1.name = "Glare"
    glare_1.use_custom_color = True
    glare_1.color = (0.0, 0.0, 0.0)
    glare_1.hide = True
    glare_1.node_tree = _rr_glare
    glare_1.inputs[2].hide = True
    glare_1.inputs[3].hide = True
    glare_1.inputs[4].hide = True
    glare_1.inputs[5].hide = True
    glare_1.inputs[6].hide = True
    glare_1.inputs[7].hide = True
    glare_1.inputs[8].hide = True
    glare_1.inputs[9].hide = True
    glare_1.inputs[10].hide = True
    glare_1.inputs[11].hide = True
    glare_1.inputs[12].hide = True
    glare_1.inputs[13].hide = True
    glare_1.inputs[14].hide = True
    glare_1.inputs[15].hide = True
    glare_1.inputs[16].hide = True
    # Socket_5
    glare_1.inputs[2].default_value = 2.0
    # Socket_20
    glare_1.inputs[3].default_value = 1.0
    # Socket_9
    glare_1.inputs[4].default_value = 1.0
    # Socket_11
    glare_1.inputs[5].default_value = (1.0, 1.0, 1.0, 1.0)
    # Socket_6
    glare_1.inputs[6].default_value = 0.4000000059604645
    # Socket_8
    glare_1.inputs[7].default_value = 0.10000000149011612
    # Socket_3
    glare_1.inputs[8].default_value = 0.1987878829240799
    # Socket_13
    glare_1.inputs[9].default_value = 0.9696969985961914
    # Socket_14
    glare_1.inputs[10].default_value = 2
    # Socket_15
    glare_1.inputs[11].default_value = 1.5707963705062866
    # Socket_17
    glare_1.inputs[12].default_value = 0.0
    # Socket_18
    glare_1.inputs[13].default_value = 1.0
    # Socket_19
    glare_1.inputs[14].default_value = 5
    # Socket_22
    glare_1.inputs[15].default_value = 0.4000000059604645
    # Socket_24
    glare_1.inputs[16].default_value = 1.0

    # Node Mix
    mix_9 = _rr_pre.nodes.new("ShaderNodeMix")
    mix_9.name = "Mix"
    mix_9.hide = True
    mix_9.blend_type = 'MIX'
    mix_9.clamp_factor = False
    mix_9.clamp_result = False
    mix_9.data_type = 'RGBA'
    mix_9.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_9 = _rr_pre.nodes.new("NodeReroute")
    reroute_9.name = "Reroute"
    reroute_9.socket_idname = "NodeSocketColor"
    # Node Reroute.001
    reroute_001_7 = _rr_pre.nodes.new("NodeReroute")
    reroute_001_7.name = "Reroute.001"
    reroute_001_7.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.002
    reroute_002_6 = _rr_pre.nodes.new("NodeReroute")
    reroute_002_6.name = "Reroute.002"
    reroute_002_6.socket_idname = "NodeSocketColor"
    # Node Gamma
    gamma_1 = _rr_pre.nodes.new("CompositorNodeGamma")
    gamma_1.name = "Gamma"
    gamma_1.use_custom_color = True
    gamma_1.color = (0.0, 0.0, 0.0)
    gamma_1.mute = True
    gamma_1.hide = True
    gamma_1.inputs[1].hide = True
    # Gamma
    gamma_1.inputs[1].default_value = 1.0

    # Node Curves
    curves = _rr_pre.nodes.new("CompositorNodeCurveRGB")
    curves.label = "Curves"
    curves.name = "Curves"
    curves.use_custom_color = True
    curves.color = (0.0, 0.0, 0.0)
    curves.hide = True
    # Mapping settings
    curves.mapping.extend = 'EXTRAPOLATED'
    curves.mapping.tone = 'FILMLIKE'
    curves.mapping.black_level = (0.0, 0.0, 0.0)
    curves.mapping.white_level = (1.0, 1.0, 1.0)
    curves.mapping.clip_min_x = 0.0
    curves.mapping.clip_min_y = 0.0
    curves.mapping.clip_max_x = 1.0
    curves.mapping.clip_max_y = 1.0
    curves.mapping.use_clip = False
    # Curve 0
    curves_curve_0 = curves.mapping.curves[0]
    curves_curve_0_point_0 = curves_curve_0.points[0]
    curves_curve_0_point_0.location = (0.0, 0.0)
    curves_curve_0_point_0.handle_type = 'AUTO'
    curves_curve_0_point_1 = curves_curve_0.points[1]
    curves_curve_0_point_1.location = (1.0, 1.0)
    curves_curve_0_point_1.handle_type = 'AUTO'
    # Curve 1
    curves_curve_1 = curves.mapping.curves[1]
    curves_curve_1_point_0 = curves_curve_1.points[0]
    curves_curve_1_point_0.location = (0.0, 0.0)
    curves_curve_1_point_0.handle_type = 'AUTO'
    curves_curve_1_point_1 = curves_curve_1.points[1]
    curves_curve_1_point_1.location = (1.0, 1.0)
    curves_curve_1_point_1.handle_type = 'AUTO'
    # Curve 2
    curves_curve_2 = curves.mapping.curves[2]
    curves_curve_2_point_0 = curves_curve_2.points[0]
    curves_curve_2_point_0.location = (0.0, 0.0)
    curves_curve_2_point_0.handle_type = 'AUTO'
    curves_curve_2_point_1 = curves_curve_2.points[1]
    curves_curve_2_point_1.location = (1.0, 1.0)
    curves_curve_2_point_1.handle_type = 'AUTO'
    # Curve 3
    curves_curve_3 = curves.mapping.curves[3]
    curves_curve_3_point_0 = curves_curve_3.points[0]
    curves_curve_3_point_0.location = (0.0, 0.0)
    curves_curve_3_point_0.handle_type = 'AUTO'
    curves_curve_3_point_1 = curves_curve_3.points[1]
    curves_curve_3_point_1.location = (1.0, 1.0)
    curves_curve_3_point_1.handle_type = 'AUTO'
    # Update curve after changes
    curves.mapping.update()
    curves.inputs[0].hide = True
    curves.inputs[2].hide = True
    curves.inputs[3].hide = True
    # Fac
    curves.inputs[0].default_value = 1.0
    # Black Level
    curves.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # White Level
    curves.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Vignette
    vignette = _rr_pre.nodes.new("CompositorNodeGroup")
    vignette.label = "Vignette"
    vignette.name = "Vignette"
    vignette.use_custom_color = True
    vignette.color = (0.0, 0.0, 0.0)
    vignette.hide = True
    vignette.node_tree = _rr_vignette
    vignette.inputs[1].hide = True
    vignette.inputs[2].hide = True
    vignette.inputs[3].hide = True
    vignette.inputs[4].hide = True
    vignette.inputs[5].hide = True
    vignette.inputs[6].hide = True
    vignette.inputs[7].hide = True
    vignette.inputs[8].hide = True
    vignette.inputs[9].hide = True
    vignette.inputs[10].hide = True
    vignette.inputs[11].hide = True
    vignette.outputs[1].hide = True
    # Socket_12
    vignette.inputs[1].default_value = 0.13076923787593842
    # Socket_9
    vignette.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # Socket_17
    vignette.inputs[3].default_value = 0.0
    # Socket_11
    vignette.inputs[4].default_value = 1.0
    # Socket_2
    vignette.inputs[5].default_value = 1.0
    # Socket_3
    vignette.inputs[6].default_value = 0.5
    # Socket_4
    vignette.inputs[7].default_value = 1.0
    # Socket_5
    vignette.inputs[8].default_value = 1.0
    # Socket_10
    vignette.inputs[9].default_value = 0.0
    # Socket_6
    vignette.inputs[10].default_value = 0.0
    # Socket_7
    vignette.inputs[11].default_value = 0.0

    # Node Frame
    frame_11 = _rr_pre.nodes.new("NodeFrame")
    frame_11.label = "Pre Effects 1"
    frame_11.name = "Frame"
    frame_11.label_size = 20
    frame_11.shrink = True

    # Node Reroute.003
    reroute_003_6 = _rr_pre.nodes.new("NodeReroute")
    reroute_003_6.name = "Reroute.003"
    reroute_003_6.socket_idname = "NodeSocketColor"
    # Node Reroute.004
    reroute_004_5 = _rr_pre.nodes.new("NodeReroute")
    reroute_004_5.name = "Reroute.004"
    reroute_004_5.socket_idname = "NodeSocketColor"
    # Node Reroute.005
    reroute_005_6 = _rr_pre.nodes.new("NodeReroute")
    reroute_005_6.name = "Reroute.005"
    reroute_005_6.socket_idname = "NodeSocketFloatFactor"
    # Node Hue Correct
    hue_correct_1 = _rr_pre.nodes.new("CompositorNodeGroup")
    hue_correct_1.label = "Hue Correct"
    hue_correct_1.name = "Hue Correct"
    hue_correct_1.use_custom_color = True
    hue_correct_1.color = (0.0, 0.0, 0.0)
    hue_correct_1.hide = True
    hue_correct_1.node_tree = _rr_hue_correct_pre
    hue_correct_1.inputs[0].hide = True
    hue_correct_1.inputs[2].hide = True
    hue_correct_1.inputs[3].hide = True
    hue_correct_1.inputs[4].hide = True
    hue_correct_1.inputs[5].hide = True
    hue_correct_1.inputs[6].hide = True
    hue_correct_1.inputs[7].hide = True
    hue_correct_1.inputs[8].hide = True
    hue_correct_1.inputs[9].hide = True
    hue_correct_1.inputs[10].hide = True
    hue_correct_1.inputs[11].hide = True
    hue_correct_1.inputs[12].hide = True
    hue_correct_1.inputs[13].hide = True
    hue_correct_1.inputs[14].hide = True
    hue_correct_1.inputs[15].hide = True
    hue_correct_1.inputs[16].hide = True
    hue_correct_1.inputs[17].hide = True
    hue_correct_1.inputs[18].hide = True
    hue_correct_1.inputs[19].hide = True
    hue_correct_1.inputs[20].hide = True
    hue_correct_1.inputs[21].hide = True
    hue_correct_1.inputs[22].hide = True
    hue_correct_1.inputs[23].hide = True
    hue_correct_1.inputs[24].hide = True
    hue_correct_1.inputs[25].hide = True
    hue_correct_1.inputs[26].hide = True
    hue_correct_1.inputs[27].hide = True
    # Socket_30
    hue_correct_1.inputs[0].default_value = 0.5
    # Socket_18
    hue_correct_1.inputs[2].default_value = 1.0
    # Socket_31
    hue_correct_1.inputs[3].default_value = 0.20000000298023224
    # Socket_22
    hue_correct_1.inputs[4].default_value = 0.0
    # Socket_32
    hue_correct_1.inputs[5].default_value = 1.0
    # Socket_33
    hue_correct_1.inputs[6].default_value = 0.0
    # Socket_6
    hue_correct_1.inputs[7].default_value = 0.5
    # Socket_7
    hue_correct_1.inputs[8].default_value = 1.0
    # Socket_8
    hue_correct_1.inputs[9].default_value = 0.5
    # Socket_9
    hue_correct_1.inputs[10].default_value = 0.5
    # Socket_2
    hue_correct_1.inputs[11].default_value = 0.5
    # Socket_4
    hue_correct_1.inputs[12].default_value = 0.5
    # Socket_5
    hue_correct_1.inputs[13].default_value = 0.5
    # Socket_11
    hue_correct_1.inputs[14].default_value = 1.0
    # Socket_12
    hue_correct_1.inputs[15].default_value = 1.0
    # Socket_13
    hue_correct_1.inputs[16].default_value = 0.8999999761581421
    # Socket_14
    hue_correct_1.inputs[17].default_value = 0.0
    # Socket_15
    hue_correct_1.inputs[18].default_value = 0.0
    # Socket_16
    hue_correct_1.inputs[19].default_value = 0.0
    # Socket_17
    hue_correct_1.inputs[20].default_value = 0.0
    # Socket_23
    hue_correct_1.inputs[21].default_value = 1.0
    # Socket_24
    hue_correct_1.inputs[22].default_value = 1.0
    # Socket_25
    hue_correct_1.inputs[23].default_value = 1.0
    # Socket_26
    hue_correct_1.inputs[24].default_value = 1.0
    # Socket_27
    hue_correct_1.inputs[25].default_value = 1.0
    # Socket_28
    hue_correct_1.inputs[26].default_value = 1.0
    # Socket_29
    hue_correct_1.inputs[27].default_value = 1.0

    # Node Log Curves
    log_curves = _rr_pre.nodes.new("CompositorNodeCurveRGB")
    log_curves.name = "Log Curves"
    log_curves.hide = True
    # Mapping settings
    log_curves.mapping.extend = 'EXTRAPOLATED'
    log_curves.mapping.tone = 'STANDARD'
    log_curves.mapping.black_level = (0.0, 0.0, 0.0)
    log_curves.mapping.white_level = (1.0, 1.0, 1.0)
    log_curves.mapping.clip_min_x = 0.0
    log_curves.mapping.clip_min_y = 0.0
    log_curves.mapping.clip_max_x = 1.0
    log_curves.mapping.clip_max_y = 1.0
    log_curves.mapping.use_clip = True
    # Curve 0
    log_curves_curve_0 = log_curves.mapping.curves[0]
    log_curves_curve_0_point_0 = log_curves_curve_0.points[0]
    log_curves_curve_0_point_0.location = (0.0, 0.0)
    log_curves_curve_0_point_0.handle_type = 'AUTO'
    log_curves_curve_0_point_1 = log_curves_curve_0.points[1]
    log_curves_curve_0_point_1.location = (1.0, 1.0)
    log_curves_curve_0_point_1.handle_type = 'AUTO'
    # Curve 1
    log_curves_curve_1 = log_curves.mapping.curves[1]
    log_curves_curve_1_point_0 = log_curves_curve_1.points[0]
    log_curves_curve_1_point_0.location = (0.0, 0.0)
    log_curves_curve_1_point_0.handle_type = 'AUTO'
    log_curves_curve_1_point_1 = log_curves_curve_1.points[1]
    log_curves_curve_1_point_1.location = (1.0, 1.0)
    log_curves_curve_1_point_1.handle_type = 'AUTO'
    # Curve 2
    log_curves_curve_2 = log_curves.mapping.curves[2]
    log_curves_curve_2_point_0 = log_curves_curve_2.points[0]
    log_curves_curve_2_point_0.location = (0.0, 0.0)
    log_curves_curve_2_point_0.handle_type = 'AUTO'
    log_curves_curve_2_point_1 = log_curves_curve_2.points[1]
    log_curves_curve_2_point_1.location = (1.0, 1.0)
    log_curves_curve_2_point_1.handle_type = 'AUTO'
    # Curve 3
    log_curves_curve_3 = log_curves.mapping.curves[3]
    log_curves_curve_3_point_0 = log_curves_curve_3.points[0]
    log_curves_curve_3_point_0.location = (0.0, 0.0)
    log_curves_curve_3_point_0.handle_type = 'AUTO'
    log_curves_curve_3_point_1 = log_curves_curve_3.points[1]
    log_curves_curve_3_point_1.location = (1.0, 1.0)
    log_curves_curve_3_point_1.handle_type = 'AUTO'
    # Update curve after changes
    log_curves.mapping.update()
    log_curves.inputs[0].hide = True
    log_curves.inputs[2].hide = True
    log_curves.inputs[3].hide = True
    # Fac
    log_curves.inputs[0].default_value = 1.0
    # Black Level
    log_curves.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # White Level
    log_curves.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Convert Colorspace
    convert_colorspace_1 = _rr_pre.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace_1.name = "Convert Colorspace"
    convert_colorspace_1.hide = True
    convert_colorspace_1.from_color_space = 'Linear Rec.709'
    convert_colorspace_1.to_color_space = 'AgX Log'

    # Node Convert Colorspace.001
    convert_colorspace_001 = _rr_pre.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace_001.name = "Convert Colorspace.001"
    convert_colorspace_001.hide = True
    convert_colorspace_001.from_color_space = 'AgX Log'
    convert_colorspace_001.to_color_space = 'Linear Rec.709'

    # Node Frame.001
    frame_001_8 = _rr_pre.nodes.new("NodeFrame")
    frame_001_8.label = "Log Curves"
    frame_001_8.name = "Frame.001"
    frame_001_8.label_size = 20
    frame_001_8.shrink = True

    # Set parents
    color_boost.parent = frame_002_7
    white_balance_1.parent = frame_002_7
    exposure.parent = frame_004_5
    contrast.parent = frame_004_5
    offset_power_slope.parent = frame_002_7
    glare_1.parent = frame_11
    gamma_1.parent = frame_004_5
    curves.parent = frame_004_5
    vignette.parent = frame_003_6
    hue_correct_1.parent = frame_002_7
    log_curves.parent = frame_001_8
    convert_colorspace_1.parent = frame_001_8
    convert_colorspace_001.parent = frame_001_8

    # Set locations
    pre_layer_output.location = (1844.230224609375, -9.238426208496094)
    pre_layer_input.location = (-1645.10546875, -20.0)
    frame_002_7.location = (56.52000045776367, 1.0919971466064453)
    frame_003_6.location = (1080.3599853515625, 1.0919971466064453)
    frame_004_5.location = (-1053.7200927734375, 0.37199708819389343)
    color_boost.location = (29.51095962524414, -41.09199523925781)
    white_balance_1.location = (280.3990173339844, -41.09199523925781)
    exposure.location = (29.029296875, -40.37199783325195)
    contrast.location = (389.02911376953125, -40.37199783325195)
    offset_power_slope.location = (520.3991088867188, -41.09199523925781)
    glare_1.location = (29.462646484375, -40.682464599609375)
    mix_9.location = (1407.7137451171875, -27.939273834228516)
    reroute_9.location = (-958.3750610351562, -120.0)
    reroute_001_7.location = (-1265.293212890625, 53.61821746826172)
    reroute_002_6.location = (1287.710693359375, -120.0)
    gamma_1.location = (209.0291748046875, -40.37199783325195)
    curves.location = (569.0291137695312, -40.37199783325195)
    vignette.location = (29.248046875, -40.72856140136719)
    frame_11.location = (-1292.760009765625, -8.268003463745117)
    reroute_003_6.location = (1553.130615234375, -165.60665893554688)
    reroute_004_5.location = (-958.3750610351562, -165.60665893554688)
    reroute_005_6.location = (1287.710693359375, 53.61821746826172)
    hue_correct_1.location = (758.0184326171875, -40.741600036621094)
    log_curves.location = (29.1724853515625, -81.4576187133789)
    convert_colorspace_1.location = (38.602020263671875, -40.47045135498047)
    convert_colorspace_001.location = (42.974884033203125, -122.80707550048828)
    frame_001_8.location = (-235.0800018310547, 43.571998596191406)

    # Set dimensions
    pre_layer_output.width, pre_layer_output.height = 140.0, 100.0
    pre_layer_input.width, pre_layer_input.height = 140.0, 100.0
    frame_002_7.width, frame_002_7.height = 963.5862426757812, 94.87200164794922
    frame_003_6.width, frame_003_6.height = 198.320068359375, 94.1520004272461
    frame_004_5.width, frame_004_5.height = 793.9650268554688, 94.1520004272461
    color_boost.width, color_boost.height = 191.72219848632812, 100.0
    white_balance_1.width, white_balance_1.height = 197.29344177246094, 100.0
    exposure.width, exposure.height = 140.0, 100.0
    contrast.width, contrast.height = 140.0, 100.0
    offset_power_slope.width, offset_power_slope.height = 200.0, 100.0
    glare_1.width, glare_1.height = 146.86814880371094, 100.0
    mix_9.width, mix_9.height = 140.0, 100.0
    reroute_9.width, reroute_9.height = 13.5, 100.0
    reroute_001_7.width, reroute_001_7.height = 13.5, 100.0
    reroute_002_6.width, reroute_002_6.height = 13.5, 100.0
    gamma_1.width, gamma_1.height = 140.0, 100.0
    curves.width, curves.height = 195.64495849609375, 100.0
    vignette.width, vignette.height = 140.0, 100.0
    frame_11.width, frame_11.height = 205.1881103515625, 94.1520004272461
    reroute_003_6.width, reroute_003_6.height = 13.5, 100.0
    reroute_004_5.width, reroute_004_5.height = 13.5, 100.0
    reroute_005_6.width, reroute_005_6.height = 13.5, 100.0
    hue_correct_1.width, hue_correct_1.height = 176.6262664794922, 100.0
    log_curves.width, log_curves.height = 200.0, 100.0
    convert_colorspace_1.width, convert_colorspace_1.height = 178.1458740234375, 100.0
    convert_colorspace_001.width, convert_colorspace_001.height = 176.06103515625, 100.0
    frame_001_8.width, frame_001_8.height = 258.32000732421875, 176.23199462890625

    # Initialize _rr_pre links

    # white_balance_1.Image -> offset_power_slope.Image
    _rr_pre.links.new(white_balance_1.outputs[0], offset_power_slope.inputs[1])
    # reroute_002_6.Output -> mix_9.A
    _rr_pre.links.new(reroute_002_6.outputs[0], mix_9.inputs[6])
    # reroute_005_6.Output -> mix_9.Factor
    _rr_pre.links.new(reroute_005_6.outputs[0], mix_9.inputs[0])
    # pre_layer_input.Factor -> reroute_001_7.Input
    _rr_pre.links.new(pre_layer_input.outputs[1], reroute_001_7.inputs[0])
    # reroute_9.Output -> reroute_002_6.Input
    _rr_pre.links.new(reroute_9.outputs[0], reroute_002_6.inputs[0])
    # exposure.Image -> gamma_1.Image
    _rr_pre.links.new(exposure.outputs[0], gamma_1.inputs[0])
    # gamma_1.Image -> contrast.Image
    _rr_pre.links.new(gamma_1.outputs[0], contrast.inputs[0])
    # contrast.Image -> curves.Image
    _rr_pre.links.new(contrast.outputs[0], curves.inputs[1])
    # reroute_003_6.Output -> pre_layer_output.Glare
    _rr_pre.links.new(reroute_003_6.outputs[0], pre_layer_output.inputs[1])
    # hue_correct_1.Image -> vignette.Image
    _rr_pre.links.new(hue_correct_1.outputs[0], vignette.inputs[0])
    # pre_layer_input.Image -> glare_1.Image
    _rr_pre.links.new(pre_layer_input.outputs[0], glare_1.inputs[0])
    # glare_1.Image -> exposure.Image
    _rr_pre.links.new(glare_1.outputs[0], exposure.inputs[0])
    # reroute_004_5.Output -> reroute_003_6.Input
    _rr_pre.links.new(reroute_004_5.outputs[0], reroute_003_6.inputs[0])
    # glare_1.Glare -> reroute_004_5.Input
    _rr_pre.links.new(glare_1.outputs[1], reroute_004_5.inputs[0])
    # reroute_001_7.Output -> reroute_005_6.Input
    _rr_pre.links.new(reroute_001_7.outputs[0], reroute_005_6.inputs[0])
    # vignette.Image -> mix_9.B
    _rr_pre.links.new(vignette.outputs[0], mix_9.inputs[7])
    # mix_9.Result -> pre_layer_output.Image
    _rr_pre.links.new(mix_9.outputs[2], pre_layer_output.inputs[0])
    # color_boost.Image -> white_balance_1.Image
    _rr_pre.links.new(color_boost.outputs[0], white_balance_1.inputs[0])
    # pre_layer_input.Factor -> glare_1.Factor
    _rr_pre.links.new(pre_layer_input.outputs[1], glare_1.inputs[1])
    # glare_1.Image -> reroute_9.Input
    _rr_pre.links.new(glare_1.outputs[0], reroute_9.inputs[0])
    # offset_power_slope.Image -> hue_correct_1.Input
    _rr_pre.links.new(offset_power_slope.outputs[0], hue_correct_1.inputs[1])
    # convert_colorspace_1.Image -> log_curves.Image
    _rr_pre.links.new(convert_colorspace_1.outputs[0], log_curves.inputs[1])
    # curves.Image -> convert_colorspace_1.Image
    _rr_pre.links.new(curves.outputs[0], convert_colorspace_1.inputs[0])
    # log_curves.Image -> convert_colorspace_001.Image
    _rr_pre.links.new(log_curves.outputs[0], convert_colorspace_001.inputs[0])
    # convert_colorspace_001.Image -> color_boost.Image
    _rr_pre.links.new(convert_colorspace_001.outputs[0], color_boost.inputs[0])

    return _rr_pre


_rr_pre = _rr_pre_node_group()

def _rr_fix_clipping_node_group():
    """Initialize .RR_fix_clipping node group"""
    _rr_fix_clipping = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_fix_clipping")

    _rr_fix_clipping.color_tag = 'NONE'
    _rr_fix_clipping.description = ""
    _rr_fix_clipping.default_group_node_width = 140
    # _rr_fix_clipping interface

    # Socket Image
    image_socket_21 = _rr_fix_clipping.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_21.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_21.attribute_domain = 'POINT'
    image_socket_21.default_input = 'VALUE'
    image_socket_21.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_8 = _rr_fix_clipping.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_8.default_value = 1.0
    factor_socket_8.min_value = 0.0
    factor_socket_8.max_value = 1.0
    factor_socket_8.subtype = 'FACTOR'
    factor_socket_8.attribute_domain = 'POINT'
    factor_socket_8.default_input = 'VALUE'
    factor_socket_8.structure_type = 'AUTO'

    # Socket Image
    image_socket_22 = _rr_fix_clipping.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_22.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_22.attribute_domain = 'POINT'
    image_socket_22.default_input = 'VALUE'
    image_socket_22.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_2 = _rr_fix_clipping.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_2.default_value = 1.0
    strength_socket_2.min_value = 0.0
    strength_socket_2.max_value = 2.0
    strength_socket_2.subtype = 'FACTOR'
    strength_socket_2.attribute_domain = 'POINT'
    strength_socket_2.default_input = 'VALUE'
    strength_socket_2.structure_type = 'AUTO'

    # Initialize _rr_fix_clipping nodes

    # Node Group Output
    group_output_15 = _rr_fix_clipping.nodes.new("NodeGroupOutput")
    group_output_15.name = "Group Output"
    group_output_15.is_active_output = True

    # Node Group Input
    group_input_14 = _rr_fix_clipping.nodes.new("NodeGroupInput")
    group_input_14.name = "Group Input"

    # Node Separate Color
    separate_color_4 = _rr_fix_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_4.name = "Separate Color"
    separate_color_4.mode = 'HSV'
    separate_color_4.ycc_mode = 'ITUBT709'

    # Node Combine Color
    combine_color_5 = _rr_fix_clipping.nodes.new("CompositorNodeCombineColor")
    combine_color_5.name = "Combine Color"
    combine_color_5.mode = 'HSV'
    combine_color_5.ycc_mode = 'ITUBT709'

    # Node Math.001
    math_001_9 = _rr_fix_clipping.nodes.new("ShaderNodeMath")
    math_001_9.name = "Math.001"
    math_001_9.operation = 'SMOOTH_MIN'
    math_001_9.use_clamp = False
    # Value_001
    math_001_9.inputs[1].default_value = 1.0

    # Node Mix
    mix_10 = _rr_fix_clipping.nodes.new("ShaderNodeMix")
    mix_10.name = "Mix"
    mix_10.blend_type = 'MIX'
    mix_10.clamp_factor = True
    mix_10.clamp_result = False
    mix_10.data_type = 'FLOAT'
    mix_10.factor_mode = 'UNIFORM'

    # Node Mix.001
    mix_001_5 = _rr_fix_clipping.nodes.new("ShaderNodeMix")
    mix_001_5.name = "Mix.001"
    mix_001_5.blend_type = 'MIX'
    mix_001_5.clamp_factor = True
    mix_001_5.clamp_result = False
    mix_001_5.data_type = 'FLOAT'
    mix_001_5.factor_mode = 'UNIFORM'
    # B_Float
    mix_001_5.inputs[3].default_value = 0.0

    # Node Map Range
    map_range_8 = _rr_fix_clipping.nodes.new("ShaderNodeMapRange")
    map_range_8.name = "Map Range"
    map_range_8.clamp = True
    map_range_8.data_type = 'FLOAT'
    map_range_8.interpolation_type = 'LINEAR'
    # From Min
    map_range_8.inputs[1].default_value = 1.0
    # To Min
    map_range_8.inputs[3].default_value = 0.0
    # To Max
    map_range_8.inputs[4].default_value = 1.0

    # Node Mix.002
    mix_002_2 = _rr_fix_clipping.nodes.new("ShaderNodeMix")
    mix_002_2.name = "Mix.002"
    mix_002_2.blend_type = 'MIX'
    mix_002_2.clamp_factor = True
    mix_002_2.clamp_result = False
    mix_002_2.data_type = 'FLOAT'
    mix_002_2.factor_mode = 'UNIFORM'

    # Node Map Range.001
    map_range_001_7 = _rr_fix_clipping.nodes.new("ShaderNodeMapRange")
    map_range_001_7.name = "Map Range.001"
    map_range_001_7.clamp = True
    map_range_001_7.data_type = 'FLOAT'
    map_range_001_7.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_7.inputs[1].default_value = 0.0
    # From Max
    map_range_001_7.inputs[2].default_value = 1.0
    # To Min
    map_range_001_7.inputs[3].default_value = 500.0
    # To Max
    map_range_001_7.inputs[4].default_value = 50.0

    # Node Math
    math_13 = _rr_fix_clipping.nodes.new("ShaderNodeMath")
    math_13.name = "Math"
    math_13.operation = 'MULTIPLY'
    math_13.use_clamp = False

    # Node Float Curve
    float_curve_3 = _rr_fix_clipping.nodes.new("ShaderNodeFloatCurve")
    float_curve_3.name = "Float Curve"
    # Mapping settings
    float_curve_3.mapping.extend = 'EXTRAPOLATED'
    float_curve_3.mapping.tone = 'STANDARD'
    float_curve_3.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_3.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_3.mapping.clip_min_x = 0.0
    float_curve_3.mapping.clip_min_y = 0.0
    float_curve_3.mapping.clip_max_x = 1.0
    float_curve_3.mapping.clip_max_y = 1.0
    float_curve_3.mapping.use_clip = True
    # Curve 0
    float_curve_3_curve_0 = float_curve_3.mapping.curves[0]
    float_curve_3_curve_0_point_0 = float_curve_3_curve_0.points[0]
    float_curve_3_curve_0_point_0.location = (0.0, 0.0)
    float_curve_3_curve_0_point_0.handle_type = 'AUTO'
    float_curve_3_curve_0_point_1 = float_curve_3_curve_0.points[1]
    float_curve_3_curve_0_point_1.location = (0.25, 0.75)
    float_curve_3_curve_0_point_1.handle_type = 'AUTO'
    float_curve_3_curve_0_point_2 = float_curve_3_curve_0.points.new(1.0, 1.0)
    float_curve_3_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_3.mapping.update()
    # Factor
    float_curve_3.inputs[0].default_value = 1.0

    # Node Float Curve.001
    float_curve_001_1 = _rr_fix_clipping.nodes.new("ShaderNodeFloatCurve")
    float_curve_001_1.name = "Float Curve.001"
    # Mapping settings
    float_curve_001_1.mapping.extend = 'EXTRAPOLATED'
    float_curve_001_1.mapping.tone = 'STANDARD'
    float_curve_001_1.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_001_1.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_001_1.mapping.clip_min_x = 0.0
    float_curve_001_1.mapping.clip_min_y = 0.0
    float_curve_001_1.mapping.clip_max_x = 1.0
    float_curve_001_1.mapping.clip_max_y = 1.0
    float_curve_001_1.mapping.use_clip = True
    # Curve 0
    float_curve_001_1_curve_0 = float_curve_001_1.mapping.curves[0]
    float_curve_001_1_curve_0_point_0 = float_curve_001_1_curve_0.points[0]
    float_curve_001_1_curve_0_point_0.location = (0.0, 0.0)
    float_curve_001_1_curve_0_point_0.handle_type = 'AUTO'
    float_curve_001_1_curve_0_point_1 = float_curve_001_1_curve_0.points[1]
    float_curve_001_1_curve_0_point_1.location = (0.75, 0.25)
    float_curve_001_1_curve_0_point_1.handle_type = 'AUTO'
    float_curve_001_1_curve_0_point_2 = float_curve_001_1_curve_0.points.new(1.0, 1.0)
    float_curve_001_1_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_001_1.mapping.update()
    # Factor
    float_curve_001_1.inputs[0].default_value = 1.0

    # Node Reroute
    reroute_10 = _rr_fix_clipping.nodes.new("NodeReroute")
    reroute_10.label = "Value"
    reroute_10.name = "Reroute"
    reroute_10.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_7 = _rr_fix_clipping.nodes.new("NodeReroute")
    reroute_002_7.name = "Reroute.002"
    reroute_002_7.socket_idname = "NodeSocketFloat"
    # Node Reroute.003
    reroute_003_7 = _rr_fix_clipping.nodes.new("NodeReroute")
    reroute_003_7.name = "Reroute.003"
    reroute_003_7.socket_idname = "NodeSocketFloat"
    # Node Reroute.005
    reroute_005_7 = _rr_fix_clipping.nodes.new("NodeReroute")
    reroute_005_7.label = "Desaturate"
    reroute_005_7.name = "Reroute.005"
    reroute_005_7.socket_idname = "NodeSocketFloat"
    # Node Map Range.002
    map_range_002_6 = _rr_fix_clipping.nodes.new("ShaderNodeMapRange")
    map_range_002_6.name = "Map Range.002"
    map_range_002_6.clamp = True
    map_range_002_6.data_type = 'FLOAT'
    map_range_002_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_6.inputs[1].default_value = 0.0
    # From Max
    map_range_002_6.inputs[2].default_value = 1.0
    # To Min
    map_range_002_6.inputs[3].default_value = 0.0
    # To Max
    map_range_002_6.inputs[4].default_value = 1.0

    # Node Map Range.003
    map_range_003_5 = _rr_fix_clipping.nodes.new("ShaderNodeMapRange")
    map_range_003_5.name = "Map Range.003"
    map_range_003_5.clamp = True
    map_range_003_5.data_type = 'FLOAT'
    map_range_003_5.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_5.inputs[1].default_value = 1.0
    # From Max
    map_range_003_5.inputs[2].default_value = 2.0
    # To Min
    map_range_003_5.inputs[3].default_value = 0.10000000149011612
    # To Max
    map_range_003_5.inputs[4].default_value = 1.0

    # Node Switch
    switch_5 = _rr_fix_clipping.nodes.new("CompositorNodeSwitch")
    switch_5.name = "Switch"

    # Node Group Input.001
    group_input_001_5 = _rr_fix_clipping.nodes.new("NodeGroupInput")
    group_input_001_5.name = "Group Input.001"

    # Node Map Range.004
    map_range_004_3 = _rr_fix_clipping.nodes.new("ShaderNodeMapRange")
    map_range_004_3.name = "Map Range.004"
    map_range_004_3.clamp = True
    map_range_004_3.data_type = 'FLOAT'
    map_range_004_3.interpolation_type = 'LINEAR'
    # From Min
    map_range_004_3.inputs[1].default_value = 0.0
    # From Max
    map_range_004_3.inputs[2].default_value = 1.0
    # To Min
    map_range_004_3.inputs[3].default_value = 0.0
    # To Max
    map_range_004_3.inputs[4].default_value = 1.0

    # Node Math.002
    math_002_10 = _rr_fix_clipping.nodes.new("ShaderNodeMath")
    math_002_10.name = "Math.002"
    math_002_10.hide = True
    math_002_10.operation = 'MULTIPLY'
    math_002_10.use_clamp = False

    # Set locations
    group_output_15.location = (1173.9783935546875, 86.77745819091797)
    group_input_14.location = (-1549.8076171875, -70.30512237548828)
    separate_color_4.location = (-919.7051391601562, 102.26093292236328)
    combine_color_5.location = (655.7327270507812, 162.07054138183594)
    math_001_9.location = (-117.7879867553711, -294.3639831542969)
    mix_10.location = (223.04244995117188, -146.70860290527344)
    mix_001_5.location = (212.91482543945312, 706.8451538085938)
    map_range_8.location = (17.571918487548828, 665.1180419921875)
    mix_002_2.location = (396.21478271484375, 848.4559326171875)
    map_range_001_7.location = (-160.54148864746094, 517.7476806640625)
    math_13.location = (-691.2012329101562, 630.8530883789062)
    float_curve_3.location = (-439.88934326171875, 556.4215087890625)
    float_curve_001_1.location = (-995.3359375, 716.8094482421875)
    reroute_10.location = (-233.3874053955078, -272.57476806640625)
    reroute_002_7.location = (20.631303787231445, 742.3732299804688)
    reroute_003_7.location = (23.662893295288086, 718.7258911132812)
    reroute_005_7.location = (-1183.5435791015625, 506.4384460449219)
    map_range_002_6.location = (-120.99342346191406, -17.20541000366211)
    map_range_003_5.location = (-381.97760009765625, -312.4131164550781)
    switch_5.location = (974.7593383789062, 126.60952758789062)
    group_input_001_5.location = (648.990234375, 267.8216552734375)
    map_range_004_3.location = (225.97250366210938, 176.5897216796875)
    math_002_10.location = (-1316.4228515625, -130.69830322265625)

    # Set dimensions
    group_output_15.width, group_output_15.height = 140.0, 100.0
    group_input_14.width, group_input_14.height = 140.0, 100.0
    separate_color_4.width, separate_color_4.height = 140.0, 100.0
    combine_color_5.width, combine_color_5.height = 140.0, 100.0
    math_001_9.width, math_001_9.height = 140.0, 100.0
    mix_10.width, mix_10.height = 140.0, 100.0
    mix_001_5.width, mix_001_5.height = 140.0, 100.0
    map_range_8.width, map_range_8.height = 140.0, 100.0
    mix_002_2.width, mix_002_2.height = 140.0, 100.0
    map_range_001_7.width, map_range_001_7.height = 140.0, 100.0
    math_13.width, math_13.height = 140.0, 100.0
    float_curve_3.width, float_curve_3.height = 240.0, 100.0
    float_curve_001_1.width, float_curve_001_1.height = 240.0, 100.0
    reroute_10.width, reroute_10.height = 20.0, 100.0
    reroute_002_7.width, reroute_002_7.height = 20.0, 100.0
    reroute_003_7.width, reroute_003_7.height = 20.0, 100.0
    reroute_005_7.width, reroute_005_7.height = 20.0, 100.0
    map_range_002_6.width, map_range_002_6.height = 140.0, 100.0
    map_range_003_5.width, map_range_003_5.height = 140.0, 100.0
    switch_5.width, switch_5.height = 140.0, 100.0
    group_input_001_5.width, group_input_001_5.height = 140.0, 100.0
    map_range_004_3.width, map_range_004_3.height = 140.0, 100.0
    math_002_10.width, math_002_10.height = 140.0, 100.0

    # Initialize _rr_fix_clipping links

    # reroute_003_7.Output -> mix_002_2.A
    _rr_fix_clipping.links.new(reroute_003_7.outputs[0], mix_002_2.inputs[2])
    # map_range_8.Result -> mix_001_5.Factor
    _rr_fix_clipping.links.new(map_range_8.outputs[0], mix_001_5.inputs[0])
    # reroute_003_7.Output -> mix_001_5.A
    _rr_fix_clipping.links.new(reroute_003_7.outputs[0], mix_001_5.inputs[2])
    # mix_10.Result -> combine_color_5.Blue
    _rr_fix_clipping.links.new(mix_10.outputs[0], combine_color_5.inputs[2])
    # reroute_10.Output -> mix_10.A
    _rr_fix_clipping.links.new(reroute_10.outputs[0], mix_10.inputs[2])
    # mix_001_5.Result -> mix_002_2.B
    _rr_fix_clipping.links.new(mix_001_5.outputs[0], mix_002_2.inputs[3])
    # reroute_10.Output -> math_001_9.Value
    _rr_fix_clipping.links.new(reroute_10.outputs[0], math_001_9.inputs[0])
    # separate_color_4.Red -> combine_color_5.Red
    _rr_fix_clipping.links.new(separate_color_4.outputs[0], combine_color_5.inputs[0])
    # math_001_9.Value -> mix_10.B
    _rr_fix_clipping.links.new(math_001_9.outputs[0], mix_10.inputs[3])
    # separate_color_4.Blue -> map_range_8.Value
    _rr_fix_clipping.links.new(separate_color_4.outputs[2], map_range_8.inputs[0])
    # group_input_14.Image -> separate_color_4.Image
    _rr_fix_clipping.links.new(group_input_14.outputs[1], separate_color_4.inputs[0])
    # switch_5.Image -> group_output_15.Image
    _rr_fix_clipping.links.new(switch_5.outputs[0], group_output_15.inputs[0])
    # map_range_002_6.Result -> mix_10.Factor
    _rr_fix_clipping.links.new(map_range_002_6.outputs[0], mix_10.inputs[0])
    # float_curve_3.Value -> map_range_001_7.Value
    _rr_fix_clipping.links.new(float_curve_3.outputs[0], map_range_001_7.inputs[0])
    # map_range_001_7.Result -> map_range_8.From Max
    _rr_fix_clipping.links.new(map_range_001_7.outputs[0], map_range_8.inputs[2])
    # reroute_005_7.Output -> math_13.Value
    _rr_fix_clipping.links.new(reroute_005_7.outputs[0], math_13.inputs[1])
    # float_curve_001_1.Value -> math_13.Value
    _rr_fix_clipping.links.new(float_curve_001_1.outputs[0], math_13.inputs[0])
    # reroute_002_7.Output -> mix_002_2.Factor
    _rr_fix_clipping.links.new(reroute_002_7.outputs[0], mix_002_2.inputs[0])
    # math_13.Value -> float_curve_3.Value
    _rr_fix_clipping.links.new(math_13.outputs[0], float_curve_3.inputs[1])
    # math_002_10.Value -> float_curve_001_1.Value
    _rr_fix_clipping.links.new(math_002_10.outputs[0], float_curve_001_1.inputs[1])
    # separate_color_4.Blue -> reroute_10.Input
    _rr_fix_clipping.links.new(separate_color_4.outputs[2], reroute_10.inputs[0])
    # math_13.Value -> reroute_002_7.Input
    _rr_fix_clipping.links.new(math_13.outputs[0], reroute_002_7.inputs[0])
    # separate_color_4.Green -> reroute_003_7.Input
    _rr_fix_clipping.links.new(separate_color_4.outputs[1], reroute_003_7.inputs[0])
    # separate_color_4.Alpha -> combine_color_5.Alpha
    _rr_fix_clipping.links.new(separate_color_4.outputs[3], combine_color_5.inputs[3])
    # map_range_003_5.Result -> math_001_9.Value
    _rr_fix_clipping.links.new(map_range_003_5.outputs[0], math_001_9.inputs[2])
    # math_002_10.Value -> map_range_002_6.Value
    _rr_fix_clipping.links.new(math_002_10.outputs[0], map_range_002_6.inputs[0])
    # math_002_10.Value -> map_range_003_5.Value
    _rr_fix_clipping.links.new(math_002_10.outputs[0], map_range_003_5.inputs[0])
    # combine_color_5.Image -> switch_5.On
    _rr_fix_clipping.links.new(combine_color_5.outputs[0], switch_5.inputs[2])
    # group_input_001_5.Image -> switch_5.Off
    _rr_fix_clipping.links.new(group_input_001_5.outputs[1], switch_5.inputs[1])
    # group_input_001_5.Strength -> switch_5.Switch
    _rr_fix_clipping.links.new(group_input_001_5.outputs[2], switch_5.inputs[0])
    # separate_color_4.Green -> map_range_004_3.Value
    _rr_fix_clipping.links.new(separate_color_4.outputs[1], map_range_004_3.inputs[0])
    # map_range_004_3.Result -> combine_color_5.Green
    _rr_fix_clipping.links.new(map_range_004_3.outputs[0], combine_color_5.inputs[1])
    # group_input_14.Strength -> math_002_10.Value
    _rr_fix_clipping.links.new(group_input_14.outputs[2], math_002_10.inputs[1])
    # group_input_14.Factor -> math_002_10.Value
    _rr_fix_clipping.links.new(group_input_14.outputs[0], math_002_10.inputs[0])

    return _rr_fix_clipping


_rr_fix_clipping = _rr_fix_clipping_node_group()

def _rr_texture_node_group():
    """Initialize .RR_texture node group"""
    _rr_texture = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_texture")

    _rr_texture.color_tag = 'NONE'
    _rr_texture.description = ""
    _rr_texture.default_group_node_width = 140
    # _rr_texture interface

    # Socket Image
    image_socket_23 = _rr_texture.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_23.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_23.attribute_domain = 'POINT'
    image_socket_23.default_input = 'VALUE'
    image_socket_23.structure_type = 'AUTO'

    # Socket Image
    image_socket_24 = _rr_texture.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_24.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_24.attribute_domain = 'POINT'
    image_socket_24.default_input = 'VALUE'
    image_socket_24.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_3 = _rr_texture.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_3.default_value = 0.0
    strength_socket_3.min_value = -1.0
    strength_socket_3.max_value = 1.0
    strength_socket_3.subtype = 'FACTOR'
    strength_socket_3.attribute_domain = 'POINT'
    strength_socket_3.default_input = 'VALUE'
    strength_socket_3.structure_type = 'AUTO'

    # Socket Keep Color
    keep_color_socket = _rr_texture.interface.new_socket(name="Keep Color", in_out='INPUT', socket_type='NodeSocketFloat')
    keep_color_socket.default_value = 1.0
    keep_color_socket.min_value = 0.0
    keep_color_socket.max_value = 1.0
    keep_color_socket.subtype = 'FACTOR'
    keep_color_socket.attribute_domain = 'POINT'
    keep_color_socket.default_input = 'VALUE'
    keep_color_socket.structure_type = 'AUTO'

    # Initialize _rr_texture nodes

    # Node Group Output
    group_output_16 = _rr_texture.nodes.new("NodeGroupOutput")
    group_output_16.name = "Group Output"
    group_output_16.is_active_output = True

    # Node Group Input
    group_input_15 = _rr_texture.nodes.new("NodeGroupInput")
    group_input_15.name = "Group Input"

    # Node Math
    math_14 = _rr_texture.nodes.new("ShaderNodeMath")
    math_14.name = "Math"
    math_14.hide = True
    math_14.operation = 'MULTIPLY'
    math_14.use_clamp = False

    # Node Map Range
    map_range_9 = _rr_texture.nodes.new("ShaderNodeMapRange")
    map_range_9.name = "Map Range"
    map_range_9.clamp = False
    map_range_9.data_type = 'FLOAT'
    map_range_9.interpolation_type = 'LINEAR'
    # From Min
    map_range_9.inputs[1].default_value = -1.0
    # From Max
    map_range_9.inputs[2].default_value = 1.0
    # To Min
    map_range_9.inputs[3].default_value = -50.0
    # To Max
    map_range_9.inputs[4].default_value = 50.0

    # Node Brightness/Contrast
    brightness_contrast = _rr_texture.nodes.new("CompositorNodeBrightContrast")
    brightness_contrast.name = "Brightness/Contrast"
    # Bright
    brightness_contrast.inputs[1].default_value = 0.0

    # Node Mix
    mix_11 = _rr_texture.nodes.new("ShaderNodeMix")
    mix_11.name = "Mix"
    mix_11.blend_type = 'COLOR'
    mix_11.clamp_factor = True
    mix_11.clamp_result = False
    mix_11.data_type = 'RGBA'
    mix_11.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_11 = _rr_texture.nodes.new("NodeReroute")
    reroute_11.name = "Reroute"
    reroute_11.socket_idname = "NodeSocketColor"
    # Node Fix Clipping
    fix_clipping = _rr_texture.nodes.new("CompositorNodeGroup")
    fix_clipping.label = "Fix Clipping"
    fix_clipping.name = "Fix Clipping"
    fix_clipping.node_tree = _rr_fix_clipping
    # Socket_6
    fix_clipping.inputs[0].default_value = 1.0
    # Socket_3
    fix_clipping.inputs[2].default_value = 0.5

    # Node Math.001
    math_001_10 = _rr_texture.nodes.new("ShaderNodeMath")
    math_001_10.name = "Math.001"
    math_001_10.operation = 'SUBTRACT'
    math_001_10.use_clamp = False
    # Value_001
    math_001_10.inputs[1].default_value = 0.5

    # Node Math.002
    math_002_11 = _rr_texture.nodes.new("ShaderNodeMath")
    math_002_11.name = "Math.002"
    math_002_11.hide = True
    math_002_11.operation = 'ABSOLUTE'
    math_002_11.use_clamp = False

    # Node Map Range.001
    map_range_001_8 = _rr_texture.nodes.new("ShaderNodeMapRange")
    map_range_001_8.name = "Map Range.001"
    map_range_001_8.clamp = True
    map_range_001_8.data_type = 'FLOAT'
    map_range_001_8.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_8.inputs[1].default_value = 0.0
    # From Max
    map_range_001_8.inputs[2].default_value = 0.5
    # To Min
    map_range_001_8.inputs[3].default_value = 1.0
    # To Max
    map_range_001_8.inputs[4].default_value = 0.0

    # Node Math.003
    math_003_11 = _rr_texture.nodes.new("ShaderNodeMath")
    math_003_11.name = "Math.003"
    math_003_11.operation = 'MULTIPLY'
    math_003_11.use_clamp = False

    # Node Mix.001
    mix_001_6 = _rr_texture.nodes.new("ShaderNodeMix")
    mix_001_6.name = "Mix.001"
    mix_001_6.blend_type = 'MIX'
    mix_001_6.clamp_factor = True
    mix_001_6.clamp_result = False
    mix_001_6.data_type = 'RGBA'
    mix_001_6.factor_mode = 'UNIFORM'

    # Node Math.004
    math_004_10 = _rr_texture.nodes.new("ShaderNodeMath")
    math_004_10.name = "Math.004"
    math_004_10.hide = True
    math_004_10.operation = 'ABSOLUTE'
    math_004_10.use_clamp = False

    # Node Switch
    switch_6 = _rr_texture.nodes.new("CompositorNodeSwitch")
    switch_6.name = "Switch"

    # Set locations
    group_output_16.location = (663.0430908203125, 239.75357055664062)
    group_input_15.location = (-1722.554931640625, 22.046470642089844)
    math_14.location = (-918.31591796875, -264.8763122558594)
    map_range_9.location = (-707.7189331054688, -222.40826416015625)
    brightness_contrast.location = (-466.4172058105469, -160.6040496826172)
    mix_11.location = (-31.9829158782959, 50.42103576660156)
    reroute_11.location = (-562.3643798828125, -18.474075317382812)
    fix_clipping.location = (-283.64752197265625, -161.5338134765625)
    math_001_10.location = (-1355.9735107421875, -316.1934814453125)
    math_002_11.location = (-1354.74658203125, -481.3642578125)
    map_range_001_8.location = (-1175.826171875, -317.0362243652344)
    math_003_11.location = (-704.6264038085938, -62.946624755859375)
    mix_001_6.location = (261.9417724609375, 289.3966979980469)
    math_004_10.location = (-21.4372501373291, 211.15061950683594)
    switch_6.location = (435.47296142578125, 269.8943176269531)

    # Set dimensions
    group_output_16.width, group_output_16.height = 140.0, 100.0
    group_input_15.width, group_input_15.height = 163.06765747070312, 100.0
    math_14.width, math_14.height = 140.0, 100.0
    map_range_9.width, map_range_9.height = 140.0, 100.0
    brightness_contrast.width, brightness_contrast.height = 140.0, 100.0
    mix_11.width, mix_11.height = 140.0, 100.0
    reroute_11.width, reroute_11.height = 13.5, 100.0
    fix_clipping.width, fix_clipping.height = 162.7245635986328, 100.0
    math_001_10.width, math_001_10.height = 140.0, 100.0
    math_002_11.width, math_002_11.height = 140.0, 100.0
    map_range_001_8.width, map_range_001_8.height = 140.0, 100.0
    math_003_11.width, math_003_11.height = 140.0, 100.0
    mix_001_6.width, mix_001_6.height = 140.0, 100.0
    math_004_10.width, math_004_10.height = 140.0, 100.0
    switch_6.width, switch_6.height = 140.0, 100.0

    # Initialize _rr_texture links

    # map_range_9.Result -> brightness_contrast.Contrast
    _rr_texture.links.new(map_range_9.outputs[0], brightness_contrast.inputs[2])
    # reroute_11.Output -> brightness_contrast.Image
    _rr_texture.links.new(reroute_11.outputs[0], brightness_contrast.inputs[0])
    # group_input_15.Strength -> math_14.Value
    _rr_texture.links.new(group_input_15.outputs[1], math_14.inputs[0])
    # math_14.Value -> map_range_9.Value
    _rr_texture.links.new(math_14.outputs[0], map_range_9.inputs[0])
    # reroute_11.Output -> mix_11.B
    _rr_texture.links.new(reroute_11.outputs[0], mix_11.inputs[7])
    # group_input_15.Image -> reroute_11.Input
    _rr_texture.links.new(group_input_15.outputs[0], reroute_11.inputs[0])
    # brightness_contrast.Image -> fix_clipping.Image
    _rr_texture.links.new(brightness_contrast.outputs[0], fix_clipping.inputs[1])
    # fix_clipping.Image -> mix_11.A
    _rr_texture.links.new(fix_clipping.outputs[0], mix_11.inputs[6])
    # group_input_15.Image -> math_001_10.Value
    _rr_texture.links.new(group_input_15.outputs[0], math_001_10.inputs[0])
    # math_001_10.Value -> math_002_11.Value
    _rr_texture.links.new(math_001_10.outputs[0], math_002_11.inputs[0])
    # math_002_11.Value -> map_range_001_8.Value
    _rr_texture.links.new(math_002_11.outputs[0], map_range_001_8.inputs[0])
    # map_range_001_8.Result -> math_14.Value
    _rr_texture.links.new(map_range_001_8.outputs[0], math_14.inputs[1])
    # group_input_15.Strength -> math_003_11.Value
    _rr_texture.links.new(group_input_15.outputs[1], math_003_11.inputs[0])
    # group_input_15.Keep Color -> math_003_11.Value
    _rr_texture.links.new(group_input_15.outputs[2], math_003_11.inputs[1])
    # math_003_11.Value -> mix_11.Factor
    _rr_texture.links.new(math_003_11.outputs[0], mix_11.inputs[0])
    # mix_11.Result -> mix_001_6.B
    _rr_texture.links.new(mix_11.outputs[2], mix_001_6.inputs[7])
    # reroute_11.Output -> mix_001_6.A
    _rr_texture.links.new(reroute_11.outputs[0], mix_001_6.inputs[6])
    # math_004_10.Value -> mix_001_6.Factor
    _rr_texture.links.new(math_004_10.outputs[0], mix_001_6.inputs[0])
    # mix_001_6.Result -> switch_6.On
    _rr_texture.links.new(mix_001_6.outputs[2], switch_6.inputs[2])
    # reroute_11.Output -> switch_6.Off
    _rr_texture.links.new(reroute_11.outputs[0], switch_6.inputs[1])
    # math_004_10.Value -> switch_6.Switch
    _rr_texture.links.new(math_004_10.outputs[0], switch_6.inputs[0])
    # switch_6.Image -> group_output_16.Image
    _rr_texture.links.new(switch_6.outputs[0], group_output_16.inputs[0])
    # group_input_15.Strength -> math_004_10.Value
    _rr_texture.links.new(group_input_15.outputs[1], math_004_10.inputs[0])

    return _rr_texture


_rr_texture = _rr_texture_node_group()

def _rr_difference_mask_node_group():
    """Initialize .RR_difference_mask node group"""
    _rr_difference_mask = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_difference_mask")

    _rr_difference_mask.color_tag = 'NONE'
    _rr_difference_mask.description = ""
    _rr_difference_mask.default_group_node_width = 140
    # _rr_difference_mask interface

    # Socket Image
    image_socket_25 = _rr_difference_mask.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_25.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_25.attribute_domain = 'POINT'
    image_socket_25.default_input = 'VALUE'
    image_socket_25.structure_type = 'AUTO'

    # Socket Mask
    mask_socket_4 = _rr_difference_mask.interface.new_socket(name="Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    mask_socket_4.default_value = 0.0
    mask_socket_4.min_value = -3.4028234663852886e+38
    mask_socket_4.max_value = 3.4028234663852886e+38
    mask_socket_4.subtype = 'NONE'
    mask_socket_4.attribute_domain = 'POINT'
    mask_socket_4.default_input = 'VALUE'
    mask_socket_4.structure_type = 'AUTO'

    # Socket Image
    image_socket_26 = _rr_difference_mask.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_26.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_26.attribute_domain = 'POINT'
    image_socket_26.default_input = 'VALUE'
    image_socket_26.structure_type = 'AUTO'

    # Socket Image
    image_socket_27 = _rr_difference_mask.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_27.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_27.attribute_domain = 'POINT'
    image_socket_27.default_input = 'VALUE'
    image_socket_27.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_4 = _rr_difference_mask.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_4.default_value = 1.0
    strength_socket_4.min_value = 0.0
    strength_socket_4.max_value = 1.0
    strength_socket_4.subtype = 'FACTOR'
    strength_socket_4.attribute_domain = 'POINT'
    strength_socket_4.default_input = 'VALUE'
    strength_socket_4.structure_type = 'AUTO'

    # Initialize _rr_difference_mask nodes

    # Node Math.001
    math_001_11 = _rr_difference_mask.nodes.new("ShaderNodeMath")
    math_001_11.name = "Math.001"
    math_001_11.operation = 'ADD'
    math_001_11.use_clamp = True

    # Node Map Range.001
    map_range_001_9 = _rr_difference_mask.nodes.new("ShaderNodeMapRange")
    map_range_001_9.name = "Map Range.001"
    map_range_001_9.clamp = False
    map_range_001_9.data_type = 'FLOAT'
    map_range_001_9.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_9.inputs[1].default_value = 0.0
    # From Max
    map_range_001_9.inputs[2].default_value = 1.0
    # To Min
    map_range_001_9.inputs[3].default_value = 1.0
    # To Max
    map_range_001_9.inputs[4].default_value = 0.0

    # Node Group Output
    group_output_17 = _rr_difference_mask.nodes.new("NodeGroupOutput")
    group_output_17.name = "Group Output"
    group_output_17.is_active_output = True

    # Node Group Input
    group_input_16 = _rr_difference_mask.nodes.new("NodeGroupInput")
    group_input_16.name = "Group Input"

    # Node Mix.001
    mix_001_7 = _rr_difference_mask.nodes.new("ShaderNodeMix")
    mix_001_7.name = "Mix.001"
    mix_001_7.blend_type = 'SUBTRACT'
    mix_001_7.clamp_factor = False
    mix_001_7.clamp_result = True
    mix_001_7.data_type = 'RGBA'
    mix_001_7.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_001_7.inputs[0].default_value = 1.0

    # Node Map Range
    map_range_10 = _rr_difference_mask.nodes.new("ShaderNodeMapRange")
    map_range_10.name = "Map Range"
    map_range_10.clamp = False
    map_range_10.data_type = 'FLOAT'
    map_range_10.interpolation_type = 'LINEAR'
    # From Min
    map_range_10.inputs[1].default_value = -9.999999747378752e-06
    # To Min
    map_range_10.inputs[3].default_value = 0.0
    # To Max
    map_range_10.inputs[4].default_value = 1.0

    # Node Mix
    mix_12 = _rr_difference_mask.nodes.new("ShaderNodeMix")
    mix_12.name = "Mix"
    mix_12.hide = True
    mix_12.blend_type = 'MIX'
    mix_12.clamp_factor = False
    mix_12.clamp_result = False
    mix_12.data_type = 'RGBA'
    mix_12.factor_mode = 'UNIFORM'

    # Node Math
    math_15 = _rr_difference_mask.nodes.new("ShaderNodeMath")
    math_15.name = "Math"
    math_15.operation = 'MULTIPLY'
    math_15.use_clamp = True

    # Set locations
    math_001_11.location = (-320.0, 340.0)
    map_range_001_9.location = (-820.0, 180.0)
    group_output_17.location = (500.0, -60.0)
    group_input_16.location = (-1320.0, -80.0)
    mix_001_7.location = (-820.0, 420.0)
    map_range_10.location = (-320.0, 160.0)
    mix_12.location = (200.0, -80.0)
    math_15.location = (-60.0, 240.0)

    # Set dimensions
    math_001_11.width, math_001_11.height = 140.0, 100.0
    map_range_001_9.width, map_range_001_9.height = 140.0, 100.0
    group_output_17.width, group_output_17.height = 140.0, 100.0
    group_input_16.width, group_input_16.height = 140.0, 100.0
    mix_001_7.width, mix_001_7.height = 140.0, 100.0
    map_range_10.width, map_range_10.height = 140.0, 100.0
    mix_12.width, mix_12.height = 140.0, 100.0
    math_15.width, math_15.height = 140.0, 100.0

    # Initialize _rr_difference_mask links

    # mix_001_7.Result -> map_range_10.Value
    _rr_difference_mask.links.new(mix_001_7.outputs[2], map_range_10.inputs[0])
    # map_range_10.Result -> math_15.Value
    _rr_difference_mask.links.new(map_range_10.outputs[0], math_15.inputs[1])
    # math_15.Value -> group_output_17.Mask
    _rr_difference_mask.links.new(math_15.outputs[0], group_output_17.inputs[1])
    # group_input_16.Strength -> map_range_10.From Max
    _rr_difference_mask.links.new(group_input_16.outputs[2], map_range_10.inputs[2])
    # group_input_16.Image -> mix_001_7.B
    _rr_difference_mask.links.new(group_input_16.outputs[0], mix_001_7.inputs[7])
    # math_001_11.Value -> math_15.Value
    _rr_difference_mask.links.new(math_001_11.outputs[0], math_15.inputs[0])
    # group_input_16.Strength -> map_range_001_9.Value
    _rr_difference_mask.links.new(group_input_16.outputs[2], map_range_001_9.inputs[0])
    # map_range_001_9.Result -> math_001_11.Value
    _rr_difference_mask.links.new(map_range_001_9.outputs[0], math_001_11.inputs[1])
    # group_input_16.Image -> mix_001_7.A
    _rr_difference_mask.links.new(group_input_16.outputs[1], mix_001_7.inputs[6])
    # math_15.Value -> mix_12.Factor
    _rr_difference_mask.links.new(math_15.outputs[0], mix_12.inputs[0])
    # group_input_16.Image -> mix_12.B
    _rr_difference_mask.links.new(group_input_16.outputs[1], mix_12.inputs[7])
    # group_input_16.Image -> mix_12.A
    _rr_difference_mask.links.new(group_input_16.outputs[0], mix_12.inputs[6])
    # mix_12.Result -> group_output_17.Image
    _rr_difference_mask.links.new(mix_12.outputs[2], group_output_17.inputs[0])
    # mix_001_7.Result -> math_001_11.Value
    _rr_difference_mask.links.new(mix_001_7.outputs[2], math_001_11.inputs[0])

    return _rr_difference_mask


_rr_difference_mask = _rr_difference_mask_node_group()

def _rr_sharpness_node_group():
    """Initialize .RR_sharpness node group"""
    _rr_sharpness = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_sharpness")

    _rr_sharpness.color_tag = 'NONE'
    _rr_sharpness.description = ""
    _rr_sharpness.default_group_node_width = 140
    # _rr_sharpness interface

    # Socket Image
    image_socket_28 = _rr_sharpness.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_28.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_28.attribute_domain = 'POINT'
    image_socket_28.default_input = 'VALUE'
    image_socket_28.structure_type = 'AUTO'

    # Socket Mask
    mask_socket_5 = _rr_sharpness.interface.new_socket(name="Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    mask_socket_5.default_value = 0.0
    mask_socket_5.min_value = -3.4028234663852886e+38
    mask_socket_5.max_value = 3.4028234663852886e+38
    mask_socket_5.subtype = 'NONE'
    mask_socket_5.attribute_domain = 'POINT'
    mask_socket_5.default_input = 'VALUE'
    mask_socket_5.structure_type = 'AUTO'

    # Socket Image
    image_socket_29 = _rr_sharpness.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_29.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_29.attribute_domain = 'POINT'
    image_socket_29.default_input = 'VALUE'
    image_socket_29.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_5 = _rr_sharpness.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_5.default_value = 1.0
    strength_socket_5.min_value = 0.0
    strength_socket_5.max_value = 1.0
    strength_socket_5.subtype = 'FACTOR'
    strength_socket_5.attribute_domain = 'POINT'
    strength_socket_5.default_input = 'VALUE'
    strength_socket_5.structure_type = 'AUTO'

    # Socket Masking
    masking_socket = _rr_sharpness.interface.new_socket(name="Masking", in_out='INPUT', socket_type='NodeSocketFloat')
    masking_socket.default_value = 0.0
    masking_socket.min_value = 0.0
    masking_socket.max_value = 1.0
    masking_socket.subtype = 'FACTOR'
    masking_socket.attribute_domain = 'POINT'
    masking_socket.default_input = 'VALUE'
    masking_socket.structure_type = 'AUTO'

    # Initialize _rr_sharpness nodes

    # Node Group Output
    group_output_18 = _rr_sharpness.nodes.new("NodeGroupOutput")
    group_output_18.name = "Group Output"
    group_output_18.is_active_output = True

    # Node Group Input
    group_input_17 = _rr_sharpness.nodes.new("NodeGroupInput")
    group_input_17.name = "Group Input"

    # Node Mix.001
    mix_001_8 = _rr_sharpness.nodes.new("ShaderNodeMix")
    mix_001_8.name = "Mix.001"
    mix_001_8.blend_type = 'MIX'
    mix_001_8.clamp_factor = False
    mix_001_8.clamp_result = False
    mix_001_8.data_type = 'RGBA'
    mix_001_8.factor_mode = 'UNIFORM'

    # Node Difference Mask
    difference_mask = _rr_sharpness.nodes.new("CompositorNodeGroup")
    difference_mask.label = "Difference Mask"
    difference_mask.name = "Difference Mask"
    difference_mask.node_tree = _rr_difference_mask

    # Node Filter.001
    filter_001 = _rr_sharpness.nodes.new("CompositorNodeFilter")
    filter_001.name = "Filter.001"
    filter_001.filter_type = 'SHARPEN_DIAMOND'

    # Set locations
    group_output_18.location = (654.5111694335938, 102.5179443359375)
    group_input_17.location = (-640.0, 40.0)
    mix_001_8.location = (420.0, 0.0)
    difference_mask.location = (100.0, 100.0)
    filter_001.location = (-180.0, -160.0)

    # Set dimensions
    group_output_18.width, group_output_18.height = 140.0, 100.0
    group_input_17.width, group_input_17.height = 140.0, 100.0
    mix_001_8.width, mix_001_8.height = 140.0, 100.0
    difference_mask.width, difference_mask.height = 193.1370849609375, 100.0
    filter_001.width, filter_001.height = 171.18359375, 100.0

    # Initialize _rr_sharpness links

    # filter_001.Image -> mix_001_8.B
    _rr_sharpness.links.new(filter_001.outputs[0], mix_001_8.inputs[7])
    # filter_001.Image -> difference_mask.Image
    _rr_sharpness.links.new(filter_001.outputs[0], difference_mask.inputs[1])
    # group_input_17.Image -> difference_mask.Image
    _rr_sharpness.links.new(group_input_17.outputs[0], difference_mask.inputs[0])
    # group_input_17.Image -> mix_001_8.A
    _rr_sharpness.links.new(group_input_17.outputs[0], mix_001_8.inputs[6])
    # group_input_17.Image -> filter_001.Image
    _rr_sharpness.links.new(group_input_17.outputs[0], filter_001.inputs[1])
    # mix_001_8.Result -> group_output_18.Image
    _rr_sharpness.links.new(mix_001_8.outputs[2], group_output_18.inputs[0])
    # group_input_17.Strength -> filter_001.Fac
    _rr_sharpness.links.new(group_input_17.outputs[1], filter_001.inputs[0])
    # group_input_17.Masking -> difference_mask.Strength
    _rr_sharpness.links.new(group_input_17.outputs[2], difference_mask.inputs[2])
    # difference_mask.Mask -> group_output_18.Mask
    _rr_sharpness.links.new(difference_mask.outputs[1], group_output_18.inputs[1])
    # difference_mask.Mask -> mix_001_8.Factor
    _rr_sharpness.links.new(difference_mask.outputs[1], mix_001_8.inputs[0])

    return _rr_sharpness


_rr_sharpness = _rr_sharpness_node_group()

def _rr_clarity_node_group():
    """Initialize .RR_clarity node group"""
    _rr_clarity = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_clarity")

    _rr_clarity.color_tag = 'NONE'
    _rr_clarity.description = ""
    _rr_clarity.default_group_node_width = 140
    # _rr_clarity interface

    # Socket Image
    image_socket_30 = _rr_clarity.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_30.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_30.attribute_domain = 'POINT'
    image_socket_30.default_input = 'VALUE'
    image_socket_30.structure_type = 'AUTO'

    # Socket Image
    image_socket_31 = _rr_clarity.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_31.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_31.attribute_domain = 'POINT'
    image_socket_31.default_input = 'VALUE'
    image_socket_31.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_6 = _rr_clarity.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_6.default_value = 0.0
    strength_socket_6.min_value = -1.0
    strength_socket_6.max_value = 1.0
    strength_socket_6.subtype = 'FACTOR'
    strength_socket_6.attribute_domain = 'POINT'
    strength_socket_6.default_input = 'VALUE'
    strength_socket_6.structure_type = 'AUTO'

    # Socket Size
    size_socket_2 = _rr_clarity.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketFloat')
    size_socket_2.default_value = 0.5
    size_socket_2.min_value = 0.0
    size_socket_2.max_value = 1.0
    size_socket_2.subtype = 'FACTOR'
    size_socket_2.attribute_domain = 'POINT'
    size_socket_2.default_input = 'VALUE'
    size_socket_2.structure_type = 'AUTO'

    # Initialize _rr_clarity nodes

    # Node Input.001
    input_001 = _rr_clarity.nodes.new("NodeGroupInput")
    input_001.name = "Input.001"

    # Node Blur
    blur_2 = _rr_clarity.nodes.new("CompositorNodeBlur")
    blur_2.name = "Blur"
    blur_2.filter_type = 'FAST_GAUSS'
    # Extend Bounds
    blur_2.inputs[2].default_value = False
    # Separable
    blur_2.inputs[3].default_value = True

    # Node Map Range
    map_range_11 = _rr_clarity.nodes.new("ShaderNodeMapRange")
    map_range_11.name = "Map Range"
    map_range_11.clamp = False
    map_range_11.data_type = 'FLOAT'
    map_range_11.interpolation_type = 'LINEAR'
    # From Min
    map_range_11.inputs[1].default_value = -1.0
    # From Max
    map_range_11.inputs[2].default_value = 1.0
    # To Min
    map_range_11.inputs[3].default_value = 0.5
    # To Max
    map_range_11.inputs[4].default_value = -0.5

    # Node Separate Color
    separate_color_5 = _rr_clarity.nodes.new("CompositorNodeSeparateColor")
    separate_color_5.name = "Separate Color"
    separate_color_5.mode = 'HSV'
    separate_color_5.ycc_mode = 'ITUBT709'

    # Node Combine Color
    combine_color_6 = _rr_clarity.nodes.new("CompositorNodeCombineColor")
    combine_color_6.name = "Combine Color"
    combine_color_6.mode = 'HSV'
    combine_color_6.ycc_mode = 'ITUBT709'

    # Node Group Output
    group_output_19 = _rr_clarity.nodes.new("NodeGroupOutput")
    group_output_19.name = "Group Output"
    group_output_19.is_active_output = True

    # Node Map Range.002
    map_range_002_7 = _rr_clarity.nodes.new("ShaderNodeMapRange")
    map_range_002_7.name = "Map Range.002"
    map_range_002_7.clamp = False
    map_range_002_7.data_type = 'FLOAT'
    map_range_002_7.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_7.inputs[1].default_value = 0.0
    # From Max
    map_range_002_7.inputs[2].default_value = 1.0
    # To Min
    map_range_002_7.inputs[3].default_value = 0.05000000074505806
    # To Max
    map_range_002_7.inputs[4].default_value = 500.0

    # Node Math
    math_16 = _rr_clarity.nodes.new("ShaderNodeMath")
    math_16.name = "Math"
    math_16.operation = 'SMOOTH_MIN'
    math_16.use_clamp = False
    # Value_001
    math_16.inputs[1].default_value = 1.0
    # Value_002
    math_16.inputs[2].default_value = 0.10000000149011612

    # Node Mix.001
    mix_001_9 = _rr_clarity.nodes.new("ShaderNodeMix")
    mix_001_9.name = "Mix.001"
    mix_001_9.blend_type = 'MIX'
    mix_001_9.clamp_factor = False
    mix_001_9.clamp_result = False
    mix_001_9.data_type = 'FLOAT'
    mix_001_9.factor_mode = 'UNIFORM'

    # Node Mix.002
    mix_002_3 = _rr_clarity.nodes.new("ShaderNodeMix")
    mix_002_3.name = "Mix.002"
    mix_002_3.blend_type = 'MIX'
    mix_002_3.clamp_factor = True
    mix_002_3.clamp_result = False
    mix_002_3.data_type = 'FLOAT'
    mix_002_3.factor_mode = 'UNIFORM'

    # Node Switch
    switch_7 = _rr_clarity.nodes.new("CompositorNodeSwitch")
    switch_7.name = "Switch"

    # Node Input.002
    input_002 = _rr_clarity.nodes.new("NodeGroupInput")
    input_002.name = "Input.002"

    # Node Math.001
    math_001_12 = _rr_clarity.nodes.new("ShaderNodeMath")
    math_001_12.name = "Math.001"
    math_001_12.operation = 'ABSOLUTE'
    math_001_12.use_clamp = False

    # Node Math.002
    math_002_12 = _rr_clarity.nodes.new("ShaderNodeMath")
    math_002_12.name = "Math.002"
    math_002_12.operation = 'SMOOTH_MAX'
    math_002_12.use_clamp = False
    # Value_001
    math_002_12.inputs[1].default_value = 0.0
    # Value_002
    math_002_12.inputs[2].default_value = 0.10000000149011612

    # Node Map Range.001
    map_range_001_10 = _rr_clarity.nodes.new("ShaderNodeMapRange")
    map_range_001_10.name = "Map Range.001"
    map_range_001_10.clamp = True
    map_range_001_10.data_type = 'FLOAT'
    map_range_001_10.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_10.inputs[1].default_value = 0.0
    # From Max
    map_range_001_10.inputs[2].default_value = 1.0
    # To Min
    map_range_001_10.inputs[3].default_value = 0.0
    # To Max
    map_range_001_10.inputs[4].default_value = 1.0

    # Node Reroute
    reroute_12 = _rr_clarity.nodes.new("NodeReroute")
    reroute_12.name = "Reroute"
    reroute_12.socket_idname = "NodeSocketFloatFactor"
    # Set locations
    input_001.location = (-103.90840911865234, 40.0)
    blur_2.location = (704.9039916992188, -104.07454681396484)
    map_range_11.location = (642.8991088867188, 365.8083190917969)
    separate_color_5.location = (300.0, 40.0)
    combine_color_6.location = (2032.87255859375, 103.94535827636719)
    group_output_19.location = (2730.864990234375, 47.11818313598633)
    map_range_002_7.location = (302.1554260253906, -147.77835083007812)
    math_16.location = (1258.300537109375, 211.4564971923828)
    mix_001_9.location = (956.3479614257812, 267.9299621582031)
    mix_002_3.location = (1672.6099853515625, 366.3753356933594)
    switch_7.location = (2477.081298828125, 168.9549102783203)
    input_002.location = (2040.8189697265625, 249.90689086914062)
    math_001_12.location = (2236.98583984375, 229.1326904296875)
    math_002_12.location = (1428.70703125, 192.54881286621094)
    map_range_001_10.location = (954.3351440429688, 521.0219116210938)
    reroute_12.location = (456.6950988769531, 392.4225158691406)

    # Set dimensions
    input_001.width, input_001.height = 140.0, 100.0
    blur_2.width, blur_2.height = 140.0, 100.0
    map_range_11.width, map_range_11.height = 140.0, 100.0
    separate_color_5.width, separate_color_5.height = 140.0, 100.0
    combine_color_6.width, combine_color_6.height = 140.0, 100.0
    group_output_19.width, group_output_19.height = 140.0, 100.0
    map_range_002_7.width, map_range_002_7.height = 140.0, 100.0
    math_16.width, math_16.height = 140.0, 100.0
    mix_001_9.width, mix_001_9.height = 140.0, 100.0
    mix_002_3.width, mix_002_3.height = 140.0, 100.0
    switch_7.width, switch_7.height = 140.0, 100.0
    input_002.width, input_002.height = 140.0, 100.0
    math_001_12.width, math_001_12.height = 140.0, 100.0
    math_002_12.width, math_002_12.height = 140.0, 100.0
    map_range_001_10.width, map_range_001_10.height = 140.0, 100.0
    reroute_12.width, reroute_12.height = 13.5, 100.0

    # Initialize _rr_clarity links

    # reroute_12.Output -> map_range_11.Value
    _rr_clarity.links.new(reroute_12.outputs[0], map_range_11.inputs[0])
    # input_001.Size -> map_range_002_7.Value
    _rr_clarity.links.new(input_001.outputs[2], map_range_002_7.inputs[0])
    # separate_color_5.Blue -> blur_2.Image
    _rr_clarity.links.new(separate_color_5.outputs[2], blur_2.inputs[0])
    # input_001.Image -> separate_color_5.Image
    _rr_clarity.links.new(input_001.outputs[0], separate_color_5.inputs[0])
    # separate_color_5.Red -> combine_color_6.Red
    _rr_clarity.links.new(separate_color_5.outputs[0], combine_color_6.inputs[0])
    # separate_color_5.Green -> combine_color_6.Green
    _rr_clarity.links.new(separate_color_5.outputs[1], combine_color_6.inputs[1])
    # separate_color_5.Alpha -> combine_color_6.Alpha
    _rr_clarity.links.new(separate_color_5.outputs[3], combine_color_6.inputs[3])
    # map_range_002_7.Result -> blur_2.Size
    _rr_clarity.links.new(map_range_002_7.outputs[0], blur_2.inputs[1])
    # map_range_11.Result -> mix_001_9.Factor
    _rr_clarity.links.new(map_range_11.outputs[0], mix_001_9.inputs[0])
    # separate_color_5.Blue -> mix_001_9.A
    _rr_clarity.links.new(separate_color_5.outputs[2], mix_001_9.inputs[2])
    # blur_2.Image -> mix_001_9.B
    _rr_clarity.links.new(blur_2.outputs[0], mix_001_9.inputs[3])
    # mix_001_9.Result -> math_16.Value
    _rr_clarity.links.new(mix_001_9.outputs[0], math_16.inputs[0])
    # combine_color_6.Image -> switch_7.On
    _rr_clarity.links.new(combine_color_6.outputs[0], switch_7.inputs[2])
    # input_002.Image -> switch_7.Off
    _rr_clarity.links.new(input_002.outputs[0], switch_7.inputs[1])
    # math_001_12.Value -> switch_7.Switch
    _rr_clarity.links.new(math_001_12.outputs[0], switch_7.inputs[0])
    # input_002.Strength -> math_001_12.Value
    _rr_clarity.links.new(input_002.outputs[1], math_001_12.inputs[0])
    # switch_7.Image -> group_output_19.Image
    _rr_clarity.links.new(switch_7.outputs[0], group_output_19.inputs[0])
    # math_16.Value -> math_002_12.Value
    _rr_clarity.links.new(math_16.outputs[0], math_002_12.inputs[0])
    # math_002_12.Value -> mix_002_3.B
    _rr_clarity.links.new(math_002_12.outputs[0], mix_002_3.inputs[3])
    # mix_001_9.Result -> mix_002_3.A
    _rr_clarity.links.new(mix_001_9.outputs[0], mix_002_3.inputs[2])
    # mix_002_3.Result -> combine_color_6.Blue
    _rr_clarity.links.new(mix_002_3.outputs[0], combine_color_6.inputs[2])
    # reroute_12.Output -> map_range_001_10.Value
    _rr_clarity.links.new(reroute_12.outputs[0], map_range_001_10.inputs[0])
    # map_range_001_10.Result -> mix_002_3.Factor
    _rr_clarity.links.new(map_range_001_10.outputs[0], mix_002_3.inputs[0])
    # input_001.Strength -> reroute_12.Input
    _rr_clarity.links.new(input_001.outputs[1], reroute_12.inputs[0])

    return _rr_clarity


_rr_clarity = _rr_clarity_node_group()

def _rr_mask_value_001_node_group():
    """Initialize .RR_mask_value.001 node group"""
    _rr_mask_value_001 = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_mask_value.001")

    _rr_mask_value_001.color_tag = 'NONE'
    _rr_mask_value_001.description = ""
    _rr_mask_value_001.default_group_node_width = 140
    # _rr_mask_value_001 interface

    # Socket Shadow Mask
    shadow_mask_socket = _rr_mask_value_001.interface.new_socket(name="Shadow Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    shadow_mask_socket.default_value = 0.0
    shadow_mask_socket.min_value = -3.4028234663852886e+38
    shadow_mask_socket.max_value = 3.4028234663852886e+38
    shadow_mask_socket.subtype = 'NONE'
    shadow_mask_socket.attribute_domain = 'POINT'
    shadow_mask_socket.default_input = 'VALUE'
    shadow_mask_socket.structure_type = 'AUTO'

    # Socket Midtone Mask
    midtone_mask_socket = _rr_mask_value_001.interface.new_socket(name="Midtone Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    midtone_mask_socket.default_value = 0.0
    midtone_mask_socket.min_value = -3.4028234663852886e+38
    midtone_mask_socket.max_value = 3.4028234663852886e+38
    midtone_mask_socket.subtype = 'NONE'
    midtone_mask_socket.attribute_domain = 'POINT'
    midtone_mask_socket.default_input = 'VALUE'
    midtone_mask_socket.structure_type = 'AUTO'

    # Socket Highlight Mask
    highlight_mask_socket = _rr_mask_value_001.interface.new_socket(name="Highlight Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
    highlight_mask_socket.default_value = 0.0
    highlight_mask_socket.min_value = -3.4028234663852886e+38
    highlight_mask_socket.max_value = 3.4028234663852886e+38
    highlight_mask_socket.subtype = 'NONE'
    highlight_mask_socket.attribute_domain = 'POINT'
    highlight_mask_socket.default_input = 'VALUE'
    highlight_mask_socket.structure_type = 'AUTO'

    # Socket Image
    image_socket_32 = _rr_mask_value_001.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_32.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_32.attribute_domain = 'POINT'
    image_socket_32.default_input = 'VALUE'
    image_socket_32.structure_type = 'AUTO'

    # Socket Shadow Range
    shadow_range_socket = _rr_mask_value_001.interface.new_socket(name="Shadow Range", in_out='INPUT', socket_type='NodeSocketFloat')
    shadow_range_socket.default_value = 0.5
    shadow_range_socket.min_value = 0.0
    shadow_range_socket.max_value = 1.0
    shadow_range_socket.subtype = 'FACTOR'
    shadow_range_socket.attribute_domain = 'POINT'
    shadow_range_socket.default_input = 'VALUE'
    shadow_range_socket.structure_type = 'AUTO'

    # Socket Midtone Range
    midtone_range_socket = _rr_mask_value_001.interface.new_socket(name="Midtone Range", in_out='INPUT', socket_type='NodeSocketFloat')
    midtone_range_socket.default_value = 0.5
    midtone_range_socket.min_value = 0.0
    midtone_range_socket.max_value = 1.0
    midtone_range_socket.subtype = 'FACTOR'
    midtone_range_socket.attribute_domain = 'POINT'
    midtone_range_socket.default_input = 'VALUE'
    midtone_range_socket.structure_type = 'AUTO'

    # Socket Highlight Range
    highlight_range_socket = _rr_mask_value_001.interface.new_socket(name="Highlight Range", in_out='INPUT', socket_type='NodeSocketFloat')
    highlight_range_socket.default_value = 0.5
    highlight_range_socket.min_value = 0.0
    highlight_range_socket.max_value = 1.0
    highlight_range_socket.subtype = 'FACTOR'
    highlight_range_socket.attribute_domain = 'POINT'
    highlight_range_socket.default_input = 'VALUE'
    highlight_range_socket.structure_type = 'AUTO'

    # Initialize _rr_mask_value_001 nodes

    # Node Group Output
    group_output_20 = _rr_mask_value_001.nodes.new("NodeGroupOutput")
    group_output_20.name = "Group Output"
    group_output_20.is_active_output = True

    # Node Group Input
    group_input_18 = _rr_mask_value_001.nodes.new("NodeGroupInput")
    group_input_18.name = "Group Input"

    # Node Map Range
    map_range_12 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_12.name = "Map Range"
    map_range_12.clamp = True
    map_range_12.data_type = 'FLOAT'
    map_range_12.interpolation_type = 'SMOOTHERSTEP'
    # From Min
    map_range_12.inputs[1].default_value = 0.0
    # To Min
    map_range_12.inputs[3].default_value = 1.0
    # To Max
    map_range_12.inputs[4].default_value = 0.0

    # Node Map Range.001
    map_range_001_11 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_001_11.name = "Map Range.001"
    map_range_001_11.clamp = True
    map_range_001_11.data_type = 'FLOAT'
    map_range_001_11.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_11.inputs[1].default_value = 0.0
    # From Max
    map_range_001_11.inputs[2].default_value = 1.0
    # To Min
    map_range_001_11.inputs[3].default_value = 0.0010000000474974513
    # To Max
    map_range_001_11.inputs[4].default_value = 1.0

    # Node Map Range.002
    map_range_002_8 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_002_8.name = "Map Range.002"
    map_range_002_8.clamp = True
    map_range_002_8.data_type = 'FLOAT'
    map_range_002_8.interpolation_type = 'SMOOTHERSTEP'
    # From Min
    map_range_002_8.inputs[1].default_value = 0.0
    # To Min
    map_range_002_8.inputs[3].default_value = 1.0
    # To Max
    map_range_002_8.inputs[4].default_value = 0.0

    # Node Map Range.003
    map_range_003_6 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_003_6.name = "Map Range.003"
    map_range_003_6.clamp = True
    map_range_003_6.data_type = 'FLOAT'
    map_range_003_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_6.inputs[1].default_value = 0.0
    # From Max
    map_range_003_6.inputs[2].default_value = 1.0
    # To Min
    map_range_003_6.inputs[3].default_value = 0.0010000000474974513
    # To Max
    map_range_003_6.inputs[4].default_value = 1.0

    # Node Map Range.004
    map_range_004_4 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_004_4.name = "Map Range.004"
    map_range_004_4.clamp = True
    map_range_004_4.data_type = 'FLOAT'
    map_range_004_4.interpolation_type = 'SMOOTHERSTEP'
    # From Max
    map_range_004_4.inputs[2].default_value = 1.0
    # To Min
    map_range_004_4.inputs[3].default_value = 0.0
    # To Max
    map_range_004_4.inputs[4].default_value = 1.0

    # Node Map Range.005
    map_range_005_4 = _rr_mask_value_001.nodes.new("ShaderNodeMapRange")
    map_range_005_4.name = "Map Range.005"
    map_range_005_4.clamp = True
    map_range_005_4.data_type = 'FLOAT'
    map_range_005_4.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_4.inputs[1].default_value = 0.0
    # From Max
    map_range_005_4.inputs[2].default_value = 1.0
    # To Min
    map_range_005_4.inputs[3].default_value = 1.0
    # To Max
    map_range_005_4.inputs[4].default_value = 0.0010000000474974513

    # Node Math
    math_17 = _rr_mask_value_001.nodes.new("ShaderNodeMath")
    math_17.name = "Math"
    math_17.operation = 'SUBTRACT'
    math_17.use_clamp = False
    # Value_001
    math_17.inputs[1].default_value = 0.5

    # Node Math.001
    math_001_13 = _rr_mask_value_001.nodes.new("ShaderNodeMath")
    math_001_13.name = "Math.001"
    math_001_13.operation = 'ABSOLUTE'
    math_001_13.use_clamp = False

    # Set locations
    group_output_20.location = (654.7741088867188, 33.92732238769531)
    group_input_18.location = (-772.3325805664062, 0.9693519473075867)
    map_range_12.location = (247.71951293945312, 186.70474243164062)
    map_range_001_11.location = (-114.77481079101562, 79.75371551513672)
    map_range_002_8.location = (184.83786010742188, 577.924072265625)
    map_range_003_6.location = (-118.23011016845703, 584.8287963867188)
    map_range_004_4.location = (189.2615509033203, -220.51669311523438)
    map_range_005_4.location = (-49.04458999633789, -346.97967529296875)
    math_17.location = (-175.32998657226562, 247.6080780029297)
    math_001_13.location = (-8.963539123535156, 226.8741912841797)

    # Set dimensions
    group_output_20.width, group_output_20.height = 140.0, 100.0
    group_input_18.width, group_input_18.height = 140.0, 100.0
    map_range_12.width, map_range_12.height = 140.0, 100.0
    map_range_001_11.width, map_range_001_11.height = 140.0, 100.0
    map_range_002_8.width, map_range_002_8.height = 140.0, 100.0
    map_range_003_6.width, map_range_003_6.height = 140.0, 100.0
    map_range_004_4.width, map_range_004_4.height = 140.0, 100.0
    map_range_005_4.width, map_range_005_4.height = 140.0, 100.0
    math_17.width, math_17.height = 140.0, 100.0
    math_001_13.width, math_001_13.height = 140.0, 100.0

    # Initialize _rr_mask_value_001 links

    # group_input_18.Image -> map_range_004_4.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[0], map_range_004_4.inputs[0])
    # math_17.Value -> math_001_13.Value
    _rr_mask_value_001.links.new(math_17.outputs[0], math_001_13.inputs[0])
    # group_input_18.Image -> math_17.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[0], math_17.inputs[0])
    # map_range_005_4.Result -> map_range_004_4.From Min
    _rr_mask_value_001.links.new(map_range_005_4.outputs[0], map_range_004_4.inputs[1])
    # group_input_18.Image -> map_range_002_8.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[0], map_range_002_8.inputs[0])
    # math_001_13.Value -> map_range_12.Value
    _rr_mask_value_001.links.new(math_001_13.outputs[0], map_range_12.inputs[0])
    # map_range_003_6.Result -> map_range_002_8.From Max
    _rr_mask_value_001.links.new(map_range_003_6.outputs[0], map_range_002_8.inputs[2])
    # map_range_001_11.Result -> map_range_12.From Max
    _rr_mask_value_001.links.new(map_range_001_11.outputs[0], map_range_12.inputs[2])
    # group_input_18.Highlight Range -> map_range_005_4.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[3], map_range_005_4.inputs[0])
    # group_input_18.Midtone Range -> map_range_001_11.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[2], map_range_001_11.inputs[0])
    # group_input_18.Shadow Range -> map_range_003_6.Value
    _rr_mask_value_001.links.new(group_input_18.outputs[1], map_range_003_6.inputs[0])
    # map_range_12.Result -> group_output_20.Midtone Mask
    _rr_mask_value_001.links.new(map_range_12.outputs[0], group_output_20.inputs[1])
    # map_range_002_8.Result -> group_output_20.Shadow Mask
    _rr_mask_value_001.links.new(map_range_002_8.outputs[0], group_output_20.inputs[0])
    # map_range_004_4.Result -> group_output_20.Highlight Mask
    _rr_mask_value_001.links.new(map_range_004_4.outputs[0], group_output_20.inputs[2])

    return _rr_mask_value_001


_rr_mask_value_001 = _rr_mask_value_001_node_group()

def _rr_color_blending_node_group():
    """Initialize .RR_color_blending node group"""
    _rr_color_blending = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_color_blending")

    _rr_color_blending.color_tag = 'NONE'
    _rr_color_blending.description = ""
    _rr_color_blending.default_group_node_width = 140
    # _rr_color_blending interface

    # Socket Image
    image_socket_33 = _rr_color_blending.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_33.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_33.attribute_domain = 'POINT'
    image_socket_33.default_input = 'VALUE'
    image_socket_33.structure_type = 'AUTO'

    # Socket Input
    input_socket_1 = _rr_color_blending.interface.new_socket(name="Input", in_out='INPUT', socket_type='NodeSocketColor')
    input_socket_1.default_value = (0.0, 0.0, 0.0, 1.0)
    input_socket_1.attribute_domain = 'POINT'
    input_socket_1.default_input = 'VALUE'
    input_socket_1.structure_type = 'AUTO'

    # Panel Shadows
    shadows_panel = _rr_color_blending.interface.new_panel("Shadows")
    # Socket Shadow Color
    shadow_color_socket = _rr_color_blending.interface.new_socket(name="Shadow Color", in_out='INPUT', socket_type='NodeSocketColor', parent = shadows_panel)
    shadow_color_socket.default_value = (0.5, 0.5, 0.5, 1.0)
    shadow_color_socket.attribute_domain = 'POINT'
    shadow_color_socket.description = "Value of the second color input"
    shadow_color_socket.default_input = 'VALUE'
    shadow_color_socket.structure_type = 'AUTO'

    # Socket Shadow Range
    shadow_range_socket_1 = _rr_color_blending.interface.new_socket(name="Shadow Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = shadows_panel)
    shadow_range_socket_1.default_value = 0.5
    shadow_range_socket_1.min_value = 0.0
    shadow_range_socket_1.max_value = 1.0
    shadow_range_socket_1.subtype = 'FACTOR'
    shadow_range_socket_1.attribute_domain = 'POINT'
    shadow_range_socket_1.default_input = 'VALUE'
    shadow_range_socket_1.structure_type = 'AUTO'

    # Socket Shadow Factor
    shadow_factor_socket = _rr_color_blending.interface.new_socket(name="Shadow Factor", in_out='INPUT', socket_type='NodeSocketFloat', parent = shadows_panel)
    shadow_factor_socket.default_value = 1.0
    shadow_factor_socket.min_value = 0.0
    shadow_factor_socket.max_value = 1.0
    shadow_factor_socket.subtype = 'FACTOR'
    shadow_factor_socket.attribute_domain = 'POINT'
    shadow_factor_socket.default_input = 'VALUE'
    shadow_factor_socket.structure_type = 'AUTO'


    # Panel Midtones
    midtones_panel = _rr_color_blending.interface.new_panel("Midtones")
    # Socket Midtone Color
    midtone_color_socket = _rr_color_blending.interface.new_socket(name="Midtone Color", in_out='INPUT', socket_type='NodeSocketColor', parent = midtones_panel)
    midtone_color_socket.default_value = (0.5, 0.5, 0.5, 1.0)
    midtone_color_socket.attribute_domain = 'POINT'
    midtone_color_socket.description = "Value of the second color input"
    midtone_color_socket.default_input = 'VALUE'
    midtone_color_socket.structure_type = 'AUTO'

    # Socket Midtone Range
    midtone_range_socket_1 = _rr_color_blending.interface.new_socket(name="Midtone Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = midtones_panel)
    midtone_range_socket_1.default_value = 0.5
    midtone_range_socket_1.min_value = 0.0
    midtone_range_socket_1.max_value = 1.0
    midtone_range_socket_1.subtype = 'FACTOR'
    midtone_range_socket_1.attribute_domain = 'POINT'
    midtone_range_socket_1.default_input = 'VALUE'
    midtone_range_socket_1.structure_type = 'AUTO'

    # Socket Midtone Factor
    midtone_factor_socket = _rr_color_blending.interface.new_socket(name="Midtone Factor", in_out='INPUT', socket_type='NodeSocketFloat', parent = midtones_panel)
    midtone_factor_socket.default_value = 1.0
    midtone_factor_socket.min_value = 0.0
    midtone_factor_socket.max_value = 1.0
    midtone_factor_socket.subtype = 'FACTOR'
    midtone_factor_socket.attribute_domain = 'POINT'
    midtone_factor_socket.default_input = 'VALUE'
    midtone_factor_socket.structure_type = 'AUTO'


    # Panel Highlights
    highlights_panel = _rr_color_blending.interface.new_panel("Highlights")
    # Socket Highlight Color
    highlight_color_socket = _rr_color_blending.interface.new_socket(name="Highlight Color", in_out='INPUT', socket_type='NodeSocketColor', parent = highlights_panel)
    highlight_color_socket.default_value = (0.5, 0.5, 0.5, 1.0)
    highlight_color_socket.attribute_domain = 'POINT'
    highlight_color_socket.description = "Value of the second color input"
    highlight_color_socket.default_input = 'VALUE'
    highlight_color_socket.structure_type = 'AUTO'

    # Socket Highlight Range
    highlight_range_socket_1 = _rr_color_blending.interface.new_socket(name="Highlight Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = highlights_panel)
    highlight_range_socket_1.default_value = 0.5
    highlight_range_socket_1.min_value = 0.0
    highlight_range_socket_1.max_value = 1.0
    highlight_range_socket_1.subtype = 'FACTOR'
    highlight_range_socket_1.attribute_domain = 'POINT'
    highlight_range_socket_1.default_input = 'VALUE'
    highlight_range_socket_1.structure_type = 'AUTO'

    # Socket Highlight Factor
    highlight_factor_socket = _rr_color_blending.interface.new_socket(name="Highlight Factor", in_out='INPUT', socket_type='NodeSocketFloat', parent = highlights_panel)
    highlight_factor_socket.default_value = 1.0
    highlight_factor_socket.min_value = 0.0
    highlight_factor_socket.max_value = 1.0
    highlight_factor_socket.subtype = 'FACTOR'
    highlight_factor_socket.attribute_domain = 'POINT'
    highlight_factor_socket.default_input = 'VALUE'
    highlight_factor_socket.structure_type = 'AUTO'


    # Initialize _rr_color_blending nodes

    # Node Shadow Fac
    shadow_fac = _rr_color_blending.nodes.new("ShaderNodeMath")
    shadow_fac.label = "Shadow Fac"
    shadow_fac.name = "Shadow Fac"
    shadow_fac.hide = True
    shadow_fac.operation = 'MULTIPLY'
    shadow_fac.use_clamp = False

    # Node Highlight Fac
    highlight_fac = _rr_color_blending.nodes.new("ShaderNodeMath")
    highlight_fac.label = "Highlight Fac"
    highlight_fac.name = "Highlight Fac"
    highlight_fac.hide = True
    highlight_fac.operation = 'MULTIPLY'
    highlight_fac.use_clamp = False

    # Node Shadow Color
    shadow_color = _rr_color_blending.nodes.new("ShaderNodeMix")
    shadow_color.label = "Shadow Color"
    shadow_color.name = "Shadow Color"
    shadow_color.blend_type = 'SOFT_LIGHT'
    shadow_color.clamp_factor = False
    shadow_color.clamp_result = False
    shadow_color.data_type = 'RGBA'
    shadow_color.factor_mode = 'UNIFORM'

    # Node Highlight Color
    highlight_color = _rr_color_blending.nodes.new("ShaderNodeMix")
    highlight_color.label = "Highlight Color"
    highlight_color.name = "Highlight Color"
    highlight_color.blend_type = 'SOFT_LIGHT'
    highlight_color.clamp_factor = False
    highlight_color.clamp_result = False
    highlight_color.data_type = 'RGBA'
    highlight_color.factor_mode = 'UNIFORM'

    # Node Group Output
    group_output_21 = _rr_color_blending.nodes.new("NodeGroupOutput")
    group_output_21.name = "Group Output"
    group_output_21.is_active_output = True

    # Node Midtone Color
    midtone_color = _rr_color_blending.nodes.new("ShaderNodeMix")
    midtone_color.label = "Midtone Color"
    midtone_color.name = "Midtone Color"
    midtone_color.blend_type = 'SOFT_LIGHT'
    midtone_color.clamp_factor = False
    midtone_color.clamp_result = False
    midtone_color.data_type = 'RGBA'
    midtone_color.factor_mode = 'UNIFORM'

    # Node Midtone Fac
    midtone_fac = _rr_color_blending.nodes.new("ShaderNodeMath")
    midtone_fac.label = "Midtone Fac"
    midtone_fac.name = "Midtone Fac"
    midtone_fac.hide = True
    midtone_fac.operation = 'MULTIPLY'
    midtone_fac.use_clamp = False

    # Node Group Input
    group_input_19 = _rr_color_blending.nodes.new("NodeGroupInput")
    group_input_19.name = "Group Input"

    # Node Group
    group_1 = _rr_color_blending.nodes.new("CompositorNodeGroup")
    group_1.name = "Group"
    group_1.node_tree = _rr_mask_value_001

    # Node Math
    math_18 = _rr_color_blending.nodes.new("ShaderNodeMath")
    math_18.name = "Math"
    math_18.hide = True
    math_18.operation = 'ADD'
    math_18.use_clamp = False

    # Node Math.001
    math_001_14 = _rr_color_blending.nodes.new("ShaderNodeMath")
    math_001_14.name = "Math.001"
    math_001_14.hide = True
    math_001_14.operation = 'ADD'
    math_001_14.use_clamp = False

    # Node Switch
    switch_8 = _rr_color_blending.nodes.new("CompositorNodeSwitch")
    switch_8.name = "Switch"

    # Node Reroute
    reroute_13 = _rr_color_blending.nodes.new("NodeReroute")
    reroute_13.name = "Reroute"
    reroute_13.socket_idname = "NodeSocketColor"
    # Set locations
    shadow_fac.location = (104.16423797607422, -43.66337203979492)
    highlight_fac.location = (307.00274658203125, -214.58953857421875)
    shadow_color.location = (300.0, 100.0)
    highlight_color.location = (525.7329711914062, -74.11649322509766)
    group_output_21.location = (1057.8507080078125, 146.63607788085938)
    midtone_color.location = (100.0, 240.00001525878906)
    midtone_fac.location = (-86.7425765991211, 99.41006469726562)
    group_input_19.location = (-942.7359008789062, -76.91017150878906)
    group_1.location = (-546.454345703125, 186.17913818359375)
    math_18.location = (100.71022033691406, 396.1310729980469)
    math_001_14.location = (102.03596496582031, 353.6888427734375)
    switch_8.location = (842.2639770507812, 160.0203399658203)
    reroute_13.location = (160.87908935546875, 266.6343994140625)

    # Set dimensions
    shadow_fac.width, shadow_fac.height = 140.0, 100.0
    highlight_fac.width, highlight_fac.height = 140.0, 100.0
    shadow_color.width, shadow_color.height = 140.0, 100.0
    highlight_color.width, highlight_color.height = 140.0, 100.0
    group_output_21.width, group_output_21.height = 140.0, 100.0
    midtone_color.width, midtone_color.height = 140.0, 100.0
    midtone_fac.width, midtone_fac.height = 140.0, 100.0
    group_input_19.width, group_input_19.height = 140.0, 100.0
    group_1.width, group_1.height = 157.44180297851562, 100.0
    math_18.width, math_18.height = 140.0, 100.0
    math_001_14.width, math_001_14.height = 140.0, 100.0
    switch_8.width, switch_8.height = 140.0, 100.0
    reroute_13.width, reroute_13.height = 13.5, 100.0

    # Initialize _rr_color_blending links

    # shadow_fac.Value -> shadow_color.Factor
    _rr_color_blending.links.new(shadow_fac.outputs[0], shadow_color.inputs[0])
    # shadow_color.Result -> highlight_color.A
    _rr_color_blending.links.new(shadow_color.outputs[2], highlight_color.inputs[6])
    # midtone_fac.Value -> midtone_color.Factor
    _rr_color_blending.links.new(midtone_fac.outputs[0], midtone_color.inputs[0])
    # highlight_fac.Value -> highlight_color.Factor
    _rr_color_blending.links.new(highlight_fac.outputs[0], highlight_color.inputs[0])
    # group_input_19.Input -> midtone_color.A
    _rr_color_blending.links.new(group_input_19.outputs[0], midtone_color.inputs[6])
    # midtone_color.Result -> shadow_color.A
    _rr_color_blending.links.new(midtone_color.outputs[2], shadow_color.inputs[6])
    # group_input_19.Input -> group_1.Image
    _rr_color_blending.links.new(group_input_19.outputs[0], group_1.inputs[0])
    # group_input_19.Shadow Range -> group_1.Shadow Range
    _rr_color_blending.links.new(group_input_19.outputs[2], group_1.inputs[1])
    # group_input_19.Midtone Range -> group_1.Midtone Range
    _rr_color_blending.links.new(group_input_19.outputs[5], group_1.inputs[2])
    # group_input_19.Highlight Range -> group_1.Highlight Range
    _rr_color_blending.links.new(group_input_19.outputs[8], group_1.inputs[3])
    # group_input_19.Shadow Color -> shadow_color.B
    _rr_color_blending.links.new(group_input_19.outputs[1], shadow_color.inputs[7])
    # group_input_19.Midtone Color -> midtone_color.B
    _rr_color_blending.links.new(group_input_19.outputs[4], midtone_color.inputs[7])
    # group_input_19.Highlight Color -> highlight_color.B
    _rr_color_blending.links.new(group_input_19.outputs[7], highlight_color.inputs[7])
    # group_1.Shadow Mask -> shadow_fac.Value
    _rr_color_blending.links.new(group_1.outputs[0], shadow_fac.inputs[0])
    # group_1.Midtone Mask -> midtone_fac.Value
    _rr_color_blending.links.new(group_1.outputs[1], midtone_fac.inputs[0])
    # group_1.Highlight Mask -> highlight_fac.Value
    _rr_color_blending.links.new(group_1.outputs[2], highlight_fac.inputs[0])
    # group_input_19.Shadow Factor -> shadow_fac.Value
    _rr_color_blending.links.new(group_input_19.outputs[3], shadow_fac.inputs[1])
    # group_input_19.Midtone Factor -> midtone_fac.Value
    _rr_color_blending.links.new(group_input_19.outputs[6], midtone_fac.inputs[1])
    # group_input_19.Highlight Factor -> highlight_fac.Value
    _rr_color_blending.links.new(group_input_19.outputs[9], highlight_fac.inputs[1])
    # group_input_19.Shadow Factor -> math_18.Value
    _rr_color_blending.links.new(group_input_19.outputs[3], math_18.inputs[0])
    # group_input_19.Midtone Factor -> math_18.Value
    _rr_color_blending.links.new(group_input_19.outputs[6], math_18.inputs[1])
    # math_18.Value -> math_001_14.Value
    _rr_color_blending.links.new(math_18.outputs[0], math_001_14.inputs[0])
    # group_input_19.Highlight Factor -> math_001_14.Value
    _rr_color_blending.links.new(group_input_19.outputs[9], math_001_14.inputs[1])
    # math_001_14.Value -> switch_8.Switch
    _rr_color_blending.links.new(math_001_14.outputs[0], switch_8.inputs[0])
    # switch_8.Image -> group_output_21.Image
    _rr_color_blending.links.new(switch_8.outputs[0], group_output_21.inputs[0])
    # reroute_13.Output -> switch_8.Off
    _rr_color_blending.links.new(reroute_13.outputs[0], switch_8.inputs[1])
    # group_input_19.Input -> reroute_13.Input
    _rr_color_blending.links.new(group_input_19.outputs[0], reroute_13.inputs[0])
    # highlight_color.Result -> switch_8.On
    _rr_color_blending.links.new(highlight_color.outputs[2], switch_8.inputs[2])

    return _rr_color_blending


_rr_color_blending = _rr_color_blending_node_group()

def _rr_value_screen_node_group():
    """Initialize .RR_value_screen node group"""
    _rr_value_screen = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_value_screen")

    _rr_value_screen.color_tag = 'NONE'
    _rr_value_screen.description = ""
    _rr_value_screen.default_group_node_width = 140
    # _rr_value_screen interface

    # Socket Value
    value_socket_3 = _rr_value_screen.interface.new_socket(name="Value", in_out='OUTPUT', socket_type='NodeSocketFloat')
    value_socket_3.default_value = 0.0
    value_socket_3.min_value = -3.4028234663852886e+38
    value_socket_3.max_value = 3.4028234663852886e+38
    value_socket_3.subtype = 'NONE'
    value_socket_3.attribute_domain = 'POINT'
    value_socket_3.default_input = 'VALUE'
    value_socket_3.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_9 = _rr_value_screen.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_9.default_value = 1.0
    factor_socket_9.min_value = 0.0
    factor_socket_9.max_value = 1.0
    factor_socket_9.subtype = 'FACTOR'
    factor_socket_9.attribute_domain = 'POINT'
    factor_socket_9.default_input = 'VALUE'
    factor_socket_9.structure_type = 'AUTO'

    # Socket Value
    value_socket_4 = _rr_value_screen.interface.new_socket(name="Value", in_out='INPUT', socket_type='NodeSocketFloat')
    value_socket_4.default_value = 0.0
    value_socket_4.min_value = 0.0
    value_socket_4.max_value = 1.0
    value_socket_4.subtype = 'NONE'
    value_socket_4.attribute_domain = 'POINT'
    value_socket_4.default_input = 'VALUE'
    value_socket_4.structure_type = 'AUTO'

    # Socket Value
    value_socket_5 = _rr_value_screen.interface.new_socket(name="Value", in_out='INPUT', socket_type='NodeSocketFloat')
    value_socket_5.default_value = 0.0
    value_socket_5.min_value = 0.0
    value_socket_5.max_value = 1.0
    value_socket_5.subtype = 'NONE'
    value_socket_5.attribute_domain = 'POINT'
    value_socket_5.default_input = 'VALUE'
    value_socket_5.structure_type = 'AUTO'

    # Initialize _rr_value_screen nodes

    # Node Group Output
    group_output_22 = _rr_value_screen.nodes.new("NodeGroupOutput")
    group_output_22.name = "Group Output"
    group_output_22.is_active_output = True

    # Node Group Input
    group_input_20 = _rr_value_screen.nodes.new("NodeGroupInput")
    group_input_20.name = "Group Input"

    # Node Math.009
    math_009_6 = _rr_value_screen.nodes.new("ShaderNodeMath")
    math_009_6.name = "Math.009"
    math_009_6.operation = 'SUBTRACT'
    math_009_6.use_clamp = False
    # Value
    math_009_6.inputs[0].default_value = 1.0

    # Node Math.010
    math_010_5 = _rr_value_screen.nodes.new("ShaderNodeMath")
    math_010_5.name = "Math.010"
    math_010_5.operation = 'SUBTRACT'
    math_010_5.use_clamp = False
    # Value
    math_010_5.inputs[0].default_value = 1.0

    # Node Math.011
    math_011_5 = _rr_value_screen.nodes.new("ShaderNodeMath")
    math_011_5.name = "Math.011"
    math_011_5.operation = 'MULTIPLY'
    math_011_5.use_clamp = False

    # Node Math.012
    math_012_4 = _rr_value_screen.nodes.new("ShaderNodeMath")
    math_012_4.name = "Math.012"
    math_012_4.operation = 'SUBTRACT'
    math_012_4.use_clamp = False
    # Value
    math_012_4.inputs[0].default_value = 1.0

    # Node Mix
    mix_13 = _rr_value_screen.nodes.new("ShaderNodeMix")
    mix_13.name = "Mix"
    mix_13.blend_type = 'MIX'
    mix_13.clamp_factor = True
    mix_13.clamp_result = False
    mix_13.data_type = 'FLOAT'
    mix_13.factor_mode = 'UNIFORM'

    # Set locations
    group_output_22.location = (693.5121459960938, 112.50045776367188)
    group_input_20.location = (-448.9206848144531, 76.8016128540039)
    math_009_6.location = (172.7612762451172, -1.543264627456665)
    math_010_5.location = (-216.16978454589844, 28.070009231567383)
    math_011_5.location = (-18.90697479248047, -2.5552353858947754)
    math_012_4.location = (-217.303466796875, -127.32439422607422)
    mix_13.location = (437.3939208984375, 165.99725341796875)

    # Set dimensions
    group_output_22.width, group_output_22.height = 140.0, 100.0
    group_input_20.width, group_input_20.height = 140.0, 100.0
    math_009_6.width, math_009_6.height = 140.0, 100.0
    math_010_5.width, math_010_5.height = 140.0, 100.0
    math_011_5.width, math_011_5.height = 140.0, 100.0
    math_012_4.width, math_012_4.height = 140.0, 100.0
    mix_13.width, mix_13.height = 140.0, 100.0

    # Initialize _rr_value_screen links

    # math_010_5.Value -> math_011_5.Value
    _rr_value_screen.links.new(math_010_5.outputs[0], math_011_5.inputs[0])
    # math_011_5.Value -> math_009_6.Value
    _rr_value_screen.links.new(math_011_5.outputs[0], math_009_6.inputs[1])
    # math_012_4.Value -> math_011_5.Value
    _rr_value_screen.links.new(math_012_4.outputs[0], math_011_5.inputs[1])
    # group_input_20.Value -> math_010_5.Value
    _rr_value_screen.links.new(group_input_20.outputs[1], math_010_5.inputs[1])
    # group_input_20.Value -> math_012_4.Value
    _rr_value_screen.links.new(group_input_20.outputs[2], math_012_4.inputs[1])
    # math_009_6.Value -> mix_13.B
    _rr_value_screen.links.new(math_009_6.outputs[0], mix_13.inputs[3])
    # group_input_20.Value -> mix_13.A
    _rr_value_screen.links.new(group_input_20.outputs[1], mix_13.inputs[2])
    # mix_13.Result -> group_output_22.Value
    _rr_value_screen.links.new(mix_13.outputs[0], group_output_22.inputs[0])
    # group_input_20.Factor -> mix_13.Factor
    _rr_value_screen.links.new(group_input_20.outputs[0], mix_13.inputs[0])

    return _rr_value_screen


_rr_value_screen = _rr_value_screen_node_group()

def _rr_values_node_group():
    """Initialize .RR_values node group"""
    _rr_values = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_values")

    _rr_values.color_tag = 'NONE'
    _rr_values.description = ""
    _rr_values.default_group_node_width = 140
    # _rr_values interface

    # Socket Image
    image_socket_34 = _rr_values.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_34.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_34.attribute_domain = 'POINT'
    image_socket_34.default_input = 'VALUE'
    image_socket_34.structure_type = 'AUTO'

    # Socket Image
    image_socket_35 = _rr_values.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_35.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_35.attribute_domain = 'POINT'
    image_socket_35.default_input = 'VALUE'
    image_socket_35.structure_type = 'AUTO'

    # Socket Blacks
    blacks_socket = _rr_values.interface.new_socket(name="Blacks", in_out='INPUT', socket_type='NodeSocketFloat')
    blacks_socket.default_value = 0.0
    blacks_socket.min_value = -0.5
    blacks_socket.max_value = 0.5
    blacks_socket.subtype = 'FACTOR'
    blacks_socket.attribute_domain = 'POINT'
    blacks_socket.default_input = 'VALUE'
    blacks_socket.structure_type = 'AUTO'

    # Socket Shadows
    shadows_socket_1 = _rr_values.interface.new_socket(name="Shadows", in_out='INPUT', socket_type='NodeSocketFloat')
    shadows_socket_1.default_value = 0.0
    shadows_socket_1.min_value = -0.5
    shadows_socket_1.max_value = 0.5
    shadows_socket_1.subtype = 'FACTOR'
    shadows_socket_1.attribute_domain = 'POINT'
    shadows_socket_1.default_input = 'VALUE'
    shadows_socket_1.structure_type = 'AUTO'

    # Socket Highlights
    highlights_socket_2 = _rr_values.interface.new_socket(name="Highlights", in_out='INPUT', socket_type='NodeSocketFloat')
    highlights_socket_2.default_value = 0.0
    highlights_socket_2.min_value = -0.5
    highlights_socket_2.max_value = 0.5
    highlights_socket_2.subtype = 'FACTOR'
    highlights_socket_2.attribute_domain = 'POINT'
    highlights_socket_2.default_input = 'VALUE'
    highlights_socket_2.structure_type = 'AUTO'

    # Socket Whites
    whites_socket = _rr_values.interface.new_socket(name="Whites", in_out='INPUT', socket_type='NodeSocketFloat')
    whites_socket.default_value = 0.0
    whites_socket.min_value = -0.5
    whites_socket.max_value = 0.5
    whites_socket.subtype = 'FACTOR'
    whites_socket.attribute_domain = 'POINT'
    whites_socket.default_input = 'VALUE'
    whites_socket.structure_type = 'AUTO'

    # Initialize _rr_values nodes

    # Node Group Output
    group_output_23 = _rr_values.nodes.new("NodeGroupOutput")
    group_output_23.name = "Group Output"
    group_output_23.is_active_output = True

    # Node Separate Color
    separate_color_6 = _rr_values.nodes.new("CompositorNodeSeparateColor")
    separate_color_6.name = "Separate Color"
    separate_color_6.mode = 'HSV'
    separate_color_6.ycc_mode = 'ITUBT709'

    # Node Combine Color
    combine_color_7 = _rr_values.nodes.new("CompositorNodeCombineColor")
    combine_color_7.name = "Combine Color"
    combine_color_7.mode = 'HSV'
    combine_color_7.ycc_mode = 'ITUBT709'

    # Node Math
    math_19 = _rr_values.nodes.new("ShaderNodeMath")
    math_19.name = "Math"
    math_19.operation = 'SUBTRACT'
    math_19.use_clamp = False
    # Value_001
    math_19.inputs[1].default_value = 0.25

    # Node Math.001
    math_001_15 = _rr_values.nodes.new("ShaderNodeMath")
    math_001_15.name = "Math.001"
    math_001_15.operation = 'ABSOLUTE'
    math_001_15.use_clamp = False

    # Node Map Range.001
    map_range_001_12 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_001_12.name = "Map Range.001"
    map_range_001_12.clamp = True
    map_range_001_12.data_type = 'FLOAT'
    map_range_001_12.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_12.inputs[1].default_value = 0.0
    # From Max
    map_range_001_12.inputs[2].default_value = 0.5
    # To Min
    map_range_001_12.inputs[3].default_value = 1.0
    # To Max
    map_range_001_12.inputs[4].default_value = 0.0

    # Node Math.002
    math_002_13 = _rr_values.nodes.new("ShaderNodeMath")
    math_002_13.name = "Math.002"
    math_002_13.operation = 'ADD'
    math_002_13.use_clamp = True

    # Node Math.003
    math_003_12 = _rr_values.nodes.new("ShaderNodeMath")
    math_003_12.name = "Math.003"
    math_003_12.operation = 'MULTIPLY'
    math_003_12.use_clamp = False

    # Node Map Range.002
    map_range_002_9 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_002_9.name = "Map Range.002"
    map_range_002_9.clamp = True
    map_range_002_9.data_type = 'FLOAT'
    map_range_002_9.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_9.inputs[1].default_value = -0.5
    # From Max
    map_range_002_9.inputs[2].default_value = 0.5
    # To Min
    map_range_002_9.inputs[3].default_value = -0.25
    # To Max
    map_range_002_9.inputs[4].default_value = 0.25

    # Node Frame
    frame_12 = _rr_values.nodes.new("NodeFrame")
    frame_12.label = "Shadows"
    frame_12.name = "Frame"
    frame_12.label_size = 20
    frame_12.shrink = True

    # Node Group Input.003
    group_input_003_4 = _rr_values.nodes.new("NodeGroupInput")
    group_input_003_4.name = "Group Input.003"
    group_input_003_4.outputs[0].hide = True
    group_input_003_4.outputs[1].hide = True
    group_input_003_4.outputs[3].hide = True
    group_input_003_4.outputs[4].hide = True
    group_input_003_4.outputs[5].hide = True

    # Node Reroute
    reroute_14 = _rr_values.nodes.new("NodeReroute")
    reroute_14.name = "Reroute"
    reroute_14.socket_idname = "NodeSocketFloat"
    # Node Math.004
    math_004_11 = _rr_values.nodes.new("ShaderNodeMath")
    math_004_11.name = "Math.004"
    math_004_11.operation = 'SUBTRACT'
    math_004_11.use_clamp = False
    # Value_001
    math_004_11.inputs[1].default_value = 0.75

    # Node Math.005
    math_005_10 = _rr_values.nodes.new("ShaderNodeMath")
    math_005_10.name = "Math.005"
    math_005_10.operation = 'ABSOLUTE'
    math_005_10.use_clamp = False

    # Node Map Range.003
    map_range_003_7 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_003_7.name = "Map Range.003"
    map_range_003_7.clamp = True
    map_range_003_7.data_type = 'FLOAT'
    map_range_003_7.interpolation_type = 'SMOOTHSTEP'
    # From Min
    map_range_003_7.inputs[1].default_value = 0.0
    # From Max
    map_range_003_7.inputs[2].default_value = 0.5
    # To Min
    map_range_003_7.inputs[3].default_value = 1.0
    # To Max
    map_range_003_7.inputs[4].default_value = 0.0

    # Node Math.006
    math_006_9 = _rr_values.nodes.new("ShaderNodeMath")
    math_006_9.name = "Math.006"
    math_006_9.operation = 'ADD'
    math_006_9.use_clamp = True

    # Node Math.007
    math_007_9 = _rr_values.nodes.new("ShaderNodeMath")
    math_007_9.name = "Math.007"
    math_007_9.operation = 'MULTIPLY'
    math_007_9.use_clamp = False

    # Node Map Range.004
    map_range_004_5 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_004_5.name = "Map Range.004"
    map_range_004_5.clamp = False
    map_range_004_5.data_type = 'FLOAT'
    map_range_004_5.interpolation_type = 'LINEAR'
    # From Min
    map_range_004_5.inputs[1].default_value = -0.5
    # From Max
    map_range_004_5.inputs[2].default_value = 0.5
    # To Min
    map_range_004_5.inputs[3].default_value = -0.25
    # To Max
    map_range_004_5.inputs[4].default_value = 0.25

    # Node Frame.001
    frame_001_9 = _rr_values.nodes.new("NodeFrame")
    frame_001_9.label = "Highlights"
    frame_001_9.name = "Frame.001"
    frame_001_9.label_size = 20
    frame_001_9.shrink = True

    # Node Group Input.004
    group_input_004_4 = _rr_values.nodes.new("NodeGroupInput")
    group_input_004_4.name = "Group Input.004"
    group_input_004_4.outputs[0].hide = True
    group_input_004_4.outputs[1].hide = True
    group_input_004_4.outputs[2].hide = True
    group_input_004_4.outputs[4].hide = True
    group_input_004_4.outputs[5].hide = True

    # Node Reroute.001
    reroute_001_8 = _rr_values.nodes.new("NodeReroute")
    reroute_001_8.name = "Reroute.001"
    reroute_001_8.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_8 = _rr_values.nodes.new("NodeReroute")
    reroute_002_8.name = "Reroute.002"
    reroute_002_8.socket_idname = "NodeSocketFloat"
    # Node Map Range.005
    map_range_005_5 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_005_5.name = "Map Range.005"
    map_range_005_5.clamp = True
    map_range_005_5.data_type = 'FLOAT'
    map_range_005_5.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_5.inputs[1].default_value = 0.0
    # From Max
    map_range_005_5.inputs[2].default_value = 0.5
    # To Min
    map_range_005_5.inputs[3].default_value = 0.0
    # To Max
    map_range_005_5.inputs[4].default_value = 1.0

    # Node Mix.001
    mix_001_10 = _rr_values.nodes.new("ShaderNodeMix")
    mix_001_10.name = "Mix.001"
    mix_001_10.blend_type = 'MIX'
    mix_001_10.clamp_factor = True
    mix_001_10.clamp_result = False
    mix_001_10.data_type = 'FLOAT'
    mix_001_10.factor_mode = 'UNIFORM'

    # Node Math.008
    math_008_8 = _rr_values.nodes.new("ShaderNodeMath")
    math_008_8.name = "Math.008"
    math_008_8.operation = 'GREATER_THAN'
    math_008_8.use_clamp = False
    # Value_001
    math_008_8.inputs[1].default_value = 0.0

    # Node Group
    group_2 = _rr_values.nodes.new("CompositorNodeGroup")
    group_2.name = "Group"
    group_2.node_tree = _rr_value_screen

    # Node Mix
    mix_14 = _rr_values.nodes.new("ShaderNodeMix")
    mix_14.name = "Mix"
    mix_14.blend_type = 'ADD'
    mix_14.clamp_factor = True
    mix_14.clamp_result = True
    mix_14.data_type = 'RGBA'
    mix_14.factor_mode = 'UNIFORM'

    # Node Group Input.002
    group_input_002_3 = _rr_values.nodes.new("NodeGroupInput")
    group_input_002_3.name = "Group Input.002"
    group_input_002_3.outputs[2].hide = True
    group_input_002_3.outputs[3].hide = True
    group_input_002_3.outputs[5].hide = True

    # Node Math.009
    math_009_7 = _rr_values.nodes.new("ShaderNodeMath")
    math_009_7.name = "Math.009"
    math_009_7.operation = 'SUBTRACT'
    math_009_7.use_clamp = True
    # Value
    math_009_7.inputs[0].default_value = 0.75

    # Node Mix.002
    mix_002_4 = _rr_values.nodes.new("ShaderNodeMix")
    mix_002_4.name = "Mix.002"
    mix_002_4.blend_type = 'ADD'
    mix_002_4.clamp_factor = True
    mix_002_4.clamp_result = True
    mix_002_4.data_type = 'RGBA'
    mix_002_4.factor_mode = 'UNIFORM'

    # Node Map Range
    map_range_13 = _rr_values.nodes.new("ShaderNodeMapRange")
    map_range_13.name = "Map Range"
    map_range_13.clamp = True
    map_range_13.data_type = 'FLOAT'
    map_range_13.interpolation_type = 'LINEAR'
    # From Min
    map_range_13.inputs[1].default_value = 0.25
    # From Max
    map_range_13.inputs[2].default_value = 1.0
    # To Min
    map_range_13.inputs[3].default_value = 0.0
    # To Max
    map_range_13.inputs[4].default_value = 1.0

    # Node Frame.002
    frame_002_8 = _rr_values.nodes.new("NodeFrame")
    frame_002_8.label = "Levels"
    frame_002_8.name = "Frame.002"
    frame_002_8.label_size = 20
    frame_002_8.shrink = True

    # Set parents
    math_19.parent = frame_12
    math_001_15.parent = frame_12
    map_range_001_12.parent = frame_12
    math_002_13.parent = frame_12
    math_003_12.parent = frame_12
    map_range_002_9.parent = frame_12
    group_input_003_4.parent = frame_12
    reroute_14.parent = frame_12
    math_004_11.parent = frame_001_9
    math_005_10.parent = frame_001_9
    map_range_003_7.parent = frame_001_9
    math_006_9.parent = frame_001_9
    math_007_9.parent = frame_001_9
    map_range_004_5.parent = frame_001_9
    group_input_004_4.parent = frame_001_9
    reroute_001_8.parent = frame_001_9
    reroute_002_8.parent = frame_001_9
    map_range_005_5.parent = frame_001_9
    mix_001_10.parent = frame_001_9
    math_008_8.parent = frame_001_9
    group_2.parent = frame_001_9
    mix_14.parent = frame_002_8
    group_input_002_3.parent = frame_002_8
    math_009_7.parent = frame_002_8
    mix_002_4.parent = frame_002_8
    map_range_13.parent = frame_002_8

    # Set locations
    group_output_23.location = (1814.7811279296875, -729.8768310546875)
    separate_color_6.location = (-1314.296630859375, -744.1646728515625)
    combine_color_7.location = (1578.1710205078125, -696.1408081054688)
    math_19.location = (132.6434326171875, -182.26629638671875)
    math_001_15.location = (311.13238525390625, -190.91595458984375)
    map_range_001_12.location = (496.85296630859375, -165.59515380859375)
    math_002_13.location = (897.9588623046875, -36.13299560546875)
    math_003_12.location = (693.6583862304688, -205.30242919921875)
    map_range_002_9.location = (498.79278564453125, -405.28326416015625)
    frame_12.location = (-1044.421875, -899.4480590820312)
    group_input_003_4.location = (273.52880859375, -496.79876708984375)
    reroute_14.location = (34.02001953125, -131.60601806640625)
    math_004_11.location = (132.6433868408203, -187.11419677734375)
    math_005_10.location = (314.808837890625, -193.31170654296875)
    map_range_003_7.location = (496.8529052734375, -170.44317626953125)
    math_006_9.location = (896.7333374023438, -36.07623291015625)
    math_007_9.location = (693.6583251953125, -210.15032958984375)
    map_range_004_5.location = (498.792724609375, -410.13116455078125)
    frame_001_9.location = (101.9547119140625, -902.3280639648438)
    group_input_004_4.location = (213.2164306640625, -544.1928100585938)
    reroute_001_8.location = (34.02000427246094, -136.45404052734375)
    reroute_002_8.location = (821.587158203125, -139.90936279296875)
    map_range_005_5.location = (497.2972412109375, -653.3787231445312)
    mix_001_10.location = (1165.6236572265625, -157.99871826171875)
    math_008_8.location = (900.7801513671875, -482.72308349609375)
    group_2.location = (896.0770263671875, -217.14739990234375)
    mix_14.location = (557.4798583984375, -35.70703125)
    group_input_002_3.location = (29.3681640625, -345.6053466796875)
    math_009_7.location = (327.926513671875, -42.23284912109375)
    mix_002_4.location = (905.8486328125, -39.605224609375)
    map_range_13.location = (548.5294189453125, -358.11944580078125)
    frame_002_8.location = (-2449.800048828125, -675.5280151367188)

    # Set dimensions
    group_output_23.width, group_output_23.height = 140.0, 100.0
    separate_color_6.width, separate_color_6.height = 140.0, 100.0
    combine_color_7.width, combine_color_7.height = 140.0, 100.0
    math_19.width, math_19.height = 140.0, 100.0
    math_001_15.width, math_001_15.height = 140.0, 100.0
    map_range_001_12.width, map_range_001_12.height = 140.0, 100.0
    math_002_13.width, math_002_13.height = 140.0, 100.0
    math_003_12.width, math_003_12.height = 140.0, 100.0
    map_range_002_9.width, map_range_002_9.height = 140.0, 100.0
    frame_12.width, frame_12.height = 1067.421875, 663.3119506835938
    group_input_003_4.width, group_input_003_4.height = 140.0, 100.0
    reroute_14.width, reroute_14.height = 13.5, 100.0
    math_004_11.width, math_004_11.height = 140.0, 100.0
    math_005_10.width, math_005_10.height = 140.0, 100.0
    map_range_003_7.width, map_range_003_7.height = 140.0, 100.0
    math_006_9.width, math_006_9.height = 140.0, 100.0
    math_007_9.width, math_007_9.height = 140.0, 100.0
    map_range_004_5.width, map_range_004_5.height = 140.0, 100.0
    frame_001_9.width, frame_001_9.height = 1335.1253662109375, 911.7119750976562
    group_input_004_4.width, group_input_004_4.height = 140.0, 100.0
    reroute_001_8.width, reroute_001_8.height = 13.5, 100.0
    reroute_002_8.width, reroute_002_8.height = 13.5, 100.0
    map_range_005_5.width, map_range_005_5.height = 140.0, 100.0
    mix_001_10.width, mix_001_10.height = 140.0, 100.0
    math_008_8.width, math_008_8.height = 140.0, 100.0
    group_2.width, group_2.height = 176.86212158203125, 100.0
    mix_14.width, mix_14.height = 140.0, 100.0
    group_input_002_3.width, group_input_002_3.height = 140.0, 100.0
    math_009_7.width, math_009_7.height = 140.0, 100.0
    mix_002_4.width, mix_002_4.height = 140.0, 100.0
    map_range_13.width, map_range_13.height = 140.0, 100.0
    frame_002_8.width, frame_002_8.height = 1075.280029296875, 616.5120239257812

    # Initialize _rr_values links

    # separate_color_6.Red -> combine_color_7.Red
    _rr_values.links.new(separate_color_6.outputs[0], combine_color_7.inputs[0])
    # separate_color_6.Green -> combine_color_7.Green
    _rr_values.links.new(separate_color_6.outputs[1], combine_color_7.inputs[1])
    # separate_color_6.Alpha -> combine_color_7.Alpha
    _rr_values.links.new(separate_color_6.outputs[3], combine_color_7.inputs[3])
    # reroute_14.Output -> math_19.Value
    _rr_values.links.new(reroute_14.outputs[0], math_19.inputs[0])
    # math_19.Value -> math_001_15.Value
    _rr_values.links.new(math_19.outputs[0], math_001_15.inputs[0])
    # math_001_15.Value -> map_range_001_12.Value
    _rr_values.links.new(math_001_15.outputs[0], map_range_001_12.inputs[0])
    # reroute_14.Output -> math_002_13.Value
    _rr_values.links.new(reroute_14.outputs[0], math_002_13.inputs[0])
    # map_range_001_12.Result -> math_003_12.Value
    _rr_values.links.new(map_range_001_12.outputs[0], math_003_12.inputs[0])
    # math_003_12.Value -> math_002_13.Value
    _rr_values.links.new(math_003_12.outputs[0], math_002_13.inputs[1])
    # map_range_002_9.Result -> math_003_12.Value
    _rr_values.links.new(map_range_002_9.outputs[0], math_003_12.inputs[1])
    # group_input_003_4.Shadows -> map_range_002_9.Value
    _rr_values.links.new(group_input_003_4.outputs[2], map_range_002_9.inputs[0])
    # separate_color_6.Blue -> reroute_14.Input
    _rr_values.links.new(separate_color_6.outputs[2], reroute_14.inputs[0])
    # reroute_001_8.Output -> math_004_11.Value
    _rr_values.links.new(reroute_001_8.outputs[0], math_004_11.inputs[0])
    # math_004_11.Value -> math_005_10.Value
    _rr_values.links.new(math_004_11.outputs[0], math_005_10.inputs[0])
    # math_005_10.Value -> map_range_003_7.Value
    _rr_values.links.new(math_005_10.outputs[0], map_range_003_7.inputs[0])
    # reroute_002_8.Output -> math_006_9.Value
    _rr_values.links.new(reroute_002_8.outputs[0], math_006_9.inputs[0])
    # map_range_003_7.Result -> math_007_9.Value
    _rr_values.links.new(map_range_003_7.outputs[0], math_007_9.inputs[0])
    # math_007_9.Value -> math_006_9.Value
    _rr_values.links.new(math_007_9.outputs[0], math_006_9.inputs[1])
    # map_range_004_5.Result -> math_007_9.Value
    _rr_values.links.new(map_range_004_5.outputs[0], math_007_9.inputs[1])
    # math_002_13.Value -> reroute_001_8.Input
    _rr_values.links.new(math_002_13.outputs[0], reroute_001_8.inputs[0])
    # reroute_001_8.Output -> reroute_002_8.Input
    _rr_values.links.new(reroute_001_8.outputs[0], reroute_002_8.inputs[0])
    # group_input_004_4.Highlights -> map_range_004_5.Value
    _rr_values.links.new(group_input_004_4.outputs[3], map_range_004_5.inputs[0])
    # group_input_004_4.Highlights -> map_range_005_5.Value
    _rr_values.links.new(group_input_004_4.outputs[3], map_range_005_5.inputs[0])
    # math_006_9.Value -> mix_001_10.A
    _rr_values.links.new(math_006_9.outputs[0], mix_001_10.inputs[2])
    # group_input_004_4.Highlights -> math_008_8.Value
    _rr_values.links.new(group_input_004_4.outputs[3], math_008_8.inputs[0])
    # math_008_8.Value -> mix_001_10.Factor
    _rr_values.links.new(math_008_8.outputs[0], mix_001_10.inputs[0])
    # reroute_002_8.Output -> group_2.Value
    _rr_values.links.new(reroute_002_8.outputs[0], group_2.inputs[1])
    # map_range_003_7.Result -> group_2.Factor
    _rr_values.links.new(map_range_003_7.outputs[0], group_2.inputs[0])
    # map_range_005_5.Result -> group_2.Value
    _rr_values.links.new(map_range_005_5.outputs[0], group_2.inputs[2])
    # group_2.Value -> mix_001_10.B
    _rr_values.links.new(group_2.outputs[0], mix_001_10.inputs[3])
    # mix_001_10.Result -> combine_color_7.Blue
    _rr_values.links.new(mix_001_10.outputs[0], combine_color_7.inputs[2])
    # group_input_002_3.Blacks -> mix_14.B
    _rr_values.links.new(group_input_002_3.outputs[1], mix_14.inputs[7])
    # group_input_002_3.Image -> math_009_7.Value
    _rr_values.links.new(group_input_002_3.outputs[0], math_009_7.inputs[1])
    # math_009_7.Value -> mix_14.Factor
    _rr_values.links.new(math_009_7.outputs[0], mix_14.inputs[0])
    # mix_14.Result -> mix_002_4.A
    _rr_values.links.new(mix_14.outputs[2], mix_002_4.inputs[6])
    # group_input_002_3.Whites -> mix_002_4.B
    _rr_values.links.new(group_input_002_3.outputs[4], mix_002_4.inputs[7])
    # group_input_002_3.Image -> map_range_13.Value
    _rr_values.links.new(group_input_002_3.outputs[0], map_range_13.inputs[0])
    # map_range_13.Result -> mix_002_4.Factor
    _rr_values.links.new(map_range_13.outputs[0], mix_002_4.inputs[0])
    # combine_color_7.Image -> group_output_23.Image
    _rr_values.links.new(combine_color_7.outputs[0], group_output_23.inputs[0])
    # mix_002_4.Result -> separate_color_6.Image
    _rr_values.links.new(mix_002_4.outputs[2], separate_color_6.inputs[0])
    # group_input_002_3.Image -> mix_14.A
    _rr_values.links.new(group_input_002_3.outputs[0], mix_14.inputs[6])

    return _rr_values


_rr_values = _rr_values_node_group()

def _rr_value_saturation_node_group():
    """Initialize .RR_value_saturation node group"""
    _rr_value_saturation = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_value_saturation")

    _rr_value_saturation.color_tag = 'NONE'
    _rr_value_saturation.description = ""
    _rr_value_saturation.default_group_node_width = 140
    # _rr_value_saturation interface

    # Socket Image
    image_socket_36 = _rr_value_saturation.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_36.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_36.attribute_domain = 'POINT'
    image_socket_36.default_input = 'VALUE'
    image_socket_36.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_10 = _rr_value_saturation.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_10.default_value = 1.0
    factor_socket_10.min_value = 0.0
    factor_socket_10.max_value = 1.0
    factor_socket_10.subtype = 'FACTOR'
    factor_socket_10.attribute_domain = 'POINT'
    factor_socket_10.default_input = 'VALUE'
    factor_socket_10.structure_type = 'AUTO'

    # Socket Image
    image_socket_37 = _rr_value_saturation.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_37.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_37.attribute_domain = 'POINT'
    image_socket_37.default_input = 'VALUE'
    image_socket_37.structure_type = 'AUTO'

    # Socket Shadow Saturation
    shadow_saturation_socket = _rr_value_saturation.interface.new_socket(name="Shadow Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    shadow_saturation_socket.default_value = 1.0
    shadow_saturation_socket.min_value = 0.0
    shadow_saturation_socket.max_value = 2.0
    shadow_saturation_socket.subtype = 'FACTOR'
    shadow_saturation_socket.attribute_domain = 'POINT'
    shadow_saturation_socket.default_input = 'VALUE'
    shadow_saturation_socket.structure_type = 'AUTO'

    # Socket Midtone Saturation
    midtone_saturation_socket = _rr_value_saturation.interface.new_socket(name="Midtone Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    midtone_saturation_socket.default_value = 1.0
    midtone_saturation_socket.min_value = 0.0
    midtone_saturation_socket.max_value = 2.0
    midtone_saturation_socket.subtype = 'FACTOR'
    midtone_saturation_socket.attribute_domain = 'POINT'
    midtone_saturation_socket.default_input = 'VALUE'
    midtone_saturation_socket.structure_type = 'AUTO'

    # Socket Highlight Saturation
    highlight_saturation_socket = _rr_value_saturation.interface.new_socket(name="Highlight Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    highlight_saturation_socket.default_value = 1.0
    highlight_saturation_socket.min_value = 0.0
    highlight_saturation_socket.max_value = 2.0
    highlight_saturation_socket.subtype = 'FACTOR'
    highlight_saturation_socket.attribute_domain = 'POINT'
    highlight_saturation_socket.default_input = 'VALUE'
    highlight_saturation_socket.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket_4 = _rr_value_saturation.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket_4.default_value = 1.0
    perceptual_socket_4.min_value = 0.0
    perceptual_socket_4.max_value = 1.0
    perceptual_socket_4.subtype = 'FACTOR'
    perceptual_socket_4.attribute_domain = 'POINT'
    perceptual_socket_4.default_input = 'VALUE'
    perceptual_socket_4.structure_type = 'AUTO'

    # Panel Range
    range_panel = _rr_value_saturation.interface.new_panel("Range")
    # Socket Shadow Range
    shadow_range_socket_2 = _rr_value_saturation.interface.new_socket(name="Shadow Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = range_panel)
    shadow_range_socket_2.default_value = 0.5
    shadow_range_socket_2.min_value = 0.0
    shadow_range_socket_2.max_value = 1.0
    shadow_range_socket_2.subtype = 'FACTOR'
    shadow_range_socket_2.attribute_domain = 'POINT'
    shadow_range_socket_2.default_input = 'VALUE'
    shadow_range_socket_2.structure_type = 'AUTO'

    # Socket Midtone Range
    midtone_range_socket_2 = _rr_value_saturation.interface.new_socket(name="Midtone Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = range_panel)
    midtone_range_socket_2.default_value = 0.5
    midtone_range_socket_2.min_value = 0.0
    midtone_range_socket_2.max_value = 1.0
    midtone_range_socket_2.subtype = 'FACTOR'
    midtone_range_socket_2.attribute_domain = 'POINT'
    midtone_range_socket_2.default_input = 'VALUE'
    midtone_range_socket_2.structure_type = 'AUTO'

    # Socket Highlight Range
    highlight_range_socket_2 = _rr_value_saturation.interface.new_socket(name="Highlight Range", in_out='INPUT', socket_type='NodeSocketFloat', parent = range_panel)
    highlight_range_socket_2.default_value = 0.5
    highlight_range_socket_2.min_value = 0.0
    highlight_range_socket_2.max_value = 1.0
    highlight_range_socket_2.subtype = 'FACTOR'
    highlight_range_socket_2.attribute_domain = 'POINT'
    highlight_range_socket_2.default_input = 'VALUE'
    highlight_range_socket_2.structure_type = 'AUTO'


    # Initialize _rr_value_saturation nodes

    # Node Group Input
    group_input_21 = _rr_value_saturation.nodes.new("NodeGroupInput")
    group_input_21.name = "Group Input"

    # Node Group Output
    group_output_24 = _rr_value_saturation.nodes.new("NodeGroupOutput")
    group_output_24.name = "Group Output"
    group_output_24.is_active_output = True

    # Node Midtone Saturation.001
    midtone_saturation_001 = _rr_value_saturation.nodes.new("CompositorNodeGroup")
    midtone_saturation_001.label = "Midtones"
    midtone_saturation_001.name = "Midtone Saturation.001"
    midtone_saturation_001.node_tree = _rr_saturation

    # Node Midtone Saturation.002
    midtone_saturation_002 = _rr_value_saturation.nodes.new("CompositorNodeGroup")
    midtone_saturation_002.label = "Shadows"
    midtone_saturation_002.name = "Midtone Saturation.002"
    midtone_saturation_002.node_tree = _rr_saturation

    # Node Midtone Saturation.003
    midtone_saturation_003 = _rr_value_saturation.nodes.new("CompositorNodeGroup")
    midtone_saturation_003.label = "Highlights"
    midtone_saturation_003.name = "Midtone Saturation.003"
    midtone_saturation_003.node_tree = _rr_saturation

    # Node Mix
    mix_15 = _rr_value_saturation.nodes.new("ShaderNodeMix")
    mix_15.name = "Mix"
    mix_15.blend_type = 'MIX'
    mix_15.clamp_factor = True
    mix_15.clamp_result = False
    mix_15.data_type = 'RGBA'
    mix_15.factor_mode = 'UNIFORM'

    # Node Group Input.001
    group_input_001_6 = _rr_value_saturation.nodes.new("NodeGroupInput")
    group_input_001_6.name = "Group Input.001"
    group_input_001_6.outputs[2].hide = True
    group_input_001_6.outputs[3].hide = True
    group_input_001_6.outputs[4].hide = True
    group_input_001_6.outputs[5].hide = True
    group_input_001_6.outputs[6].hide = True
    group_input_001_6.outputs[7].hide = True
    group_input_001_6.outputs[8].hide = True
    group_input_001_6.outputs[9].hide = True

    # Node Group
    group_3 = _rr_value_saturation.nodes.new("CompositorNodeGroup")
    group_3.name = "Group"
    group_3.node_tree = _rr_mask_value_001

    # Set locations
    group_input_21.location = (-1219.6827392578125, 337.23809814453125)
    group_output_24.location = (550.9943237304688, 303.1686706542969)
    midtone_saturation_001.location = (-146.41372680664062, 555.7344970703125)
    midtone_saturation_002.location = (-146.43191528320312, 377.04217529296875)
    midtone_saturation_003.location = (-142.2244110107422, 199.37257385253906)
    mix_15.location = (315.1547546386719, 407.3025817871094)
    group_input_001_6.location = (73.96762084960938, 316.9585266113281)
    group_3.location = (-709.407958984375, 613.15576171875)

    # Set dimensions
    group_input_21.width, group_input_21.height = 140.0, 100.0
    group_output_24.width, group_output_24.height = 140.0, 100.0
    midtone_saturation_001.width, midtone_saturation_001.height = 169.08709716796875, 100.0
    midtone_saturation_002.width, midtone_saturation_002.height = 169.08709716796875, 100.0
    midtone_saturation_003.width, midtone_saturation_003.height = 169.08709716796875, 100.0
    mix_15.width, mix_15.height = 140.0, 100.0
    group_input_001_6.width, group_input_001_6.height = 140.0, 100.0
    group_3.width, group_3.height = 157.44180297851562, 100.0

    # Initialize _rr_value_saturation links

    # group_input_21.Midtone Saturation -> midtone_saturation_001.Saturation
    _rr_value_saturation.links.new(group_input_21.outputs[3], midtone_saturation_001.inputs[2])
    # group_input_21.Perceptual -> midtone_saturation_001.Perceptual
    _rr_value_saturation.links.new(group_input_21.outputs[5], midtone_saturation_001.inputs[3])
    # group_3.Shadow Mask -> midtone_saturation_002.Fac
    _rr_value_saturation.links.new(group_3.outputs[0], midtone_saturation_002.inputs[0])
    # group_input_21.Perceptual -> midtone_saturation_002.Perceptual
    _rr_value_saturation.links.new(group_input_21.outputs[5], midtone_saturation_002.inputs[3])
    # group_input_21.Shadow Saturation -> midtone_saturation_002.Saturation
    _rr_value_saturation.links.new(group_input_21.outputs[2], midtone_saturation_002.inputs[2])
    # group_3.Highlight Mask -> midtone_saturation_003.Fac
    _rr_value_saturation.links.new(group_3.outputs[2], midtone_saturation_003.inputs[0])
    # group_input_21.Highlight Saturation -> midtone_saturation_003.Saturation
    _rr_value_saturation.links.new(group_input_21.outputs[4], midtone_saturation_003.inputs[2])
    # group_input_21.Perceptual -> midtone_saturation_003.Perceptual
    _rr_value_saturation.links.new(group_input_21.outputs[5], midtone_saturation_003.inputs[3])
    # midtone_saturation_001.Image -> midtone_saturation_002.Image
    _rr_value_saturation.links.new(midtone_saturation_001.outputs[0], midtone_saturation_002.inputs[1])
    # midtone_saturation_002.Image -> midtone_saturation_003.Image
    _rr_value_saturation.links.new(midtone_saturation_002.outputs[0], midtone_saturation_003.inputs[1])
    # group_input_001_6.Image -> mix_15.A
    _rr_value_saturation.links.new(group_input_001_6.outputs[1], mix_15.inputs[6])
    # midtone_saturation_003.Image -> mix_15.B
    _rr_value_saturation.links.new(midtone_saturation_003.outputs[0], mix_15.inputs[7])
    # group_input_001_6.Factor -> mix_15.Factor
    _rr_value_saturation.links.new(group_input_001_6.outputs[0], mix_15.inputs[0])
    # mix_15.Result -> group_output_24.Image
    _rr_value_saturation.links.new(mix_15.outputs[2], group_output_24.inputs[0])
    # group_3.Midtone Mask -> midtone_saturation_001.Fac
    _rr_value_saturation.links.new(group_3.outputs[1], midtone_saturation_001.inputs[0])
    # group_input_21.Highlight Range -> group_3.Highlight Range
    _rr_value_saturation.links.new(group_input_21.outputs[8], group_3.inputs[3])
    # group_input_21.Midtone Range -> group_3.Midtone Range
    _rr_value_saturation.links.new(group_input_21.outputs[7], group_3.inputs[2])
    # group_input_21.Image -> group_3.Image
    _rr_value_saturation.links.new(group_input_21.outputs[1], group_3.inputs[0])
    # group_input_21.Shadow Range -> group_3.Shadow Range
    _rr_value_saturation.links.new(group_input_21.outputs[6], group_3.inputs[1])
    # group_input_21.Image -> midtone_saturation_001.Image
    _rr_value_saturation.links.new(group_input_21.outputs[1], midtone_saturation_001.inputs[1])

    return _rr_value_saturation


_rr_value_saturation = _rr_value_saturation_node_group()

def _rr_hue_correct_node_group():
    """Initialize .RR_hue_correct node group"""
    _rr_hue_correct = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_hue_correct")

    _rr_hue_correct.color_tag = 'NONE'
    _rr_hue_correct.description = ""
    _rr_hue_correct.default_group_node_width = 140
    # _rr_hue_correct interface

    # Socket Image
    image_socket_38 = _rr_hue_correct.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_38.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_38.attribute_domain = 'POINT'
    image_socket_38.default_input = 'VALUE'
    image_socket_38.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_11 = _rr_hue_correct.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_11.default_value = 1.0
    factor_socket_11.min_value = 0.0
    factor_socket_11.max_value = 1.0
    factor_socket_11.subtype = 'FACTOR'
    factor_socket_11.attribute_domain = 'POINT'
    factor_socket_11.default_input = 'VALUE'
    factor_socket_11.structure_type = 'AUTO'

    # Socket Input
    input_socket_2 = _rr_hue_correct.interface.new_socket(name="Input", in_out='INPUT', socket_type='NodeSocketColor')
    input_socket_2.default_value = (0.0, 0.0, 0.0, 1.0)
    input_socket_2.attribute_domain = 'POINT'
    input_socket_2.default_input = 'VALUE'
    input_socket_2.structure_type = 'AUTO'

    # Socket sRGB
    srgb_socket = _rr_hue_correct.interface.new_socket(name="sRGB", in_out='INPUT', socket_type='NodeSocketColor')
    srgb_socket.default_value = (1.0, 1.0, 1.0, 1.0)
    srgb_socket.attribute_domain = 'POINT'
    srgb_socket.default_input = 'VALUE'
    srgb_socket.structure_type = 'AUTO'

    # Socket Perceptual
    perceptual_socket_5 = _rr_hue_correct.interface.new_socket(name="Perceptual", in_out='INPUT', socket_type='NodeSocketFloat')
    perceptual_socket_5.default_value = 1.0
    perceptual_socket_5.min_value = 0.0
    perceptual_socket_5.max_value = 1.0
    perceptual_socket_5.subtype = 'FACTOR'
    perceptual_socket_5.attribute_domain = 'POINT'
    perceptual_socket_5.default_input = 'VALUE'
    perceptual_socket_5.structure_type = 'AUTO'

    # Socket Range
    range_socket_2 = _rr_hue_correct.interface.new_socket(name="Range", in_out='INPUT', socket_type='NodeSocketFloat')
    range_socket_2.default_value = 0.20000000298023224
    range_socket_2.min_value = 0.0
    range_socket_2.max_value = 1.0
    range_socket_2.subtype = 'FACTOR'
    range_socket_2.attribute_domain = 'POINT'
    range_socket_2.default_input = 'VALUE'
    range_socket_2.structure_type = 'AUTO'

    # Socket Smoothing
    smoothing_socket_2 = _rr_hue_correct.interface.new_socket(name="Smoothing", in_out='INPUT', socket_type='NodeSocketFloat')
    smoothing_socket_2.default_value = 0.0
    smoothing_socket_2.min_value = 0.0
    smoothing_socket_2.max_value = 1.0
    smoothing_socket_2.subtype = 'FACTOR'
    smoothing_socket_2.attribute_domain = 'POINT'
    smoothing_socket_2.default_input = 'VALUE'
    smoothing_socket_2.structure_type = 'AUTO'

    # Socket Saturation Mask
    saturation_mask_socket_1 = _rr_hue_correct.interface.new_socket(name="Saturation Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_mask_socket_1.default_value = 1.0
    saturation_mask_socket_1.min_value = -1.0
    saturation_mask_socket_1.max_value = 1.0
    saturation_mask_socket_1.subtype = 'FACTOR'
    saturation_mask_socket_1.attribute_domain = 'POINT'
    saturation_mask_socket_1.default_input = 'VALUE'
    saturation_mask_socket_1.structure_type = 'AUTO'

    # Socket Value Mask
    value_mask_socket_1 = _rr_hue_correct.interface.new_socket(name="Value Mask", in_out='INPUT', socket_type='NodeSocketFloat')
    value_mask_socket_1.default_value = 0.0
    value_mask_socket_1.min_value = -1.0
    value_mask_socket_1.max_value = 1.0
    value_mask_socket_1.subtype = 'FACTOR'
    value_mask_socket_1.attribute_domain = 'POINT'
    value_mask_socket_1.default_input = 'VALUE'
    value_mask_socket_1.structure_type = 'AUTO'

    # Panel Hue
    hue_panel_1 = _rr_hue_correct.interface.new_panel("Hue")
    # Socket Red Hue
    red_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Red Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    red_hue_socket_1.default_value = 0.5
    red_hue_socket_1.min_value = 0.0
    red_hue_socket_1.max_value = 1.0
    red_hue_socket_1.subtype = 'FACTOR'
    red_hue_socket_1.attribute_domain = 'POINT'
    red_hue_socket_1.default_input = 'VALUE'
    red_hue_socket_1.structure_type = 'AUTO'

    # Socket Orange Hue
    orange_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Orange Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    orange_hue_socket_1.default_value = 0.5
    orange_hue_socket_1.min_value = 0.0
    orange_hue_socket_1.max_value = 1.0
    orange_hue_socket_1.subtype = 'FACTOR'
    orange_hue_socket_1.attribute_domain = 'POINT'
    orange_hue_socket_1.default_input = 'VALUE'
    orange_hue_socket_1.structure_type = 'AUTO'

    # Socket Yellow Hue
    yellow_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Yellow Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    yellow_hue_socket_1.default_value = 0.5
    yellow_hue_socket_1.min_value = 0.0
    yellow_hue_socket_1.max_value = 1.0
    yellow_hue_socket_1.subtype = 'FACTOR'
    yellow_hue_socket_1.attribute_domain = 'POINT'
    yellow_hue_socket_1.default_input = 'VALUE'
    yellow_hue_socket_1.structure_type = 'AUTO'

    # Socket Green Hue
    green_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Green Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    green_hue_socket_1.default_value = 0.5
    green_hue_socket_1.min_value = 0.0
    green_hue_socket_1.max_value = 1.0
    green_hue_socket_1.subtype = 'FACTOR'
    green_hue_socket_1.attribute_domain = 'POINT'
    green_hue_socket_1.default_input = 'VALUE'
    green_hue_socket_1.structure_type = 'AUTO'

    # Socket Teal Hue
    teal_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Teal Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    teal_hue_socket_1.default_value = 0.5
    teal_hue_socket_1.min_value = 0.0
    teal_hue_socket_1.max_value = 1.0
    teal_hue_socket_1.subtype = 'FACTOR'
    teal_hue_socket_1.attribute_domain = 'POINT'
    teal_hue_socket_1.default_input = 'VALUE'
    teal_hue_socket_1.structure_type = 'AUTO'

    # Socket Blue Hue
    blue_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Blue Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    blue_hue_socket_1.default_value = 0.5
    blue_hue_socket_1.min_value = 0.0
    blue_hue_socket_1.max_value = 1.0
    blue_hue_socket_1.subtype = 'FACTOR'
    blue_hue_socket_1.attribute_domain = 'POINT'
    blue_hue_socket_1.default_input = 'VALUE'
    blue_hue_socket_1.structure_type = 'AUTO'

    # Socket Pink Hue
    pink_hue_socket_1 = _rr_hue_correct.interface.new_socket(name="Pink Hue", in_out='INPUT', socket_type='NodeSocketFloat', parent = hue_panel_1)
    pink_hue_socket_1.default_value = 0.5
    pink_hue_socket_1.min_value = 0.0
    pink_hue_socket_1.max_value = 1.0
    pink_hue_socket_1.subtype = 'FACTOR'
    pink_hue_socket_1.attribute_domain = 'POINT'
    pink_hue_socket_1.default_input = 'VALUE'
    pink_hue_socket_1.structure_type = 'AUTO'


    # Panel Saturation
    saturation_panel_1 = _rr_hue_correct.interface.new_panel("Saturation")
    # Socket Red Saturation
    red_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Red Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    red_saturation_socket_1.default_value = 1.0
    red_saturation_socket_1.min_value = 0.0
    red_saturation_socket_1.max_value = 2.0
    red_saturation_socket_1.subtype = 'FACTOR'
    red_saturation_socket_1.attribute_domain = 'POINT'
    red_saturation_socket_1.default_input = 'VALUE'
    red_saturation_socket_1.structure_type = 'AUTO'

    # Socket Orange Saturation
    orange_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Orange Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    orange_saturation_socket_1.default_value = 1.0
    orange_saturation_socket_1.min_value = 0.0
    orange_saturation_socket_1.max_value = 2.0
    orange_saturation_socket_1.subtype = 'FACTOR'
    orange_saturation_socket_1.attribute_domain = 'POINT'
    orange_saturation_socket_1.default_input = 'VALUE'
    orange_saturation_socket_1.structure_type = 'AUTO'

    # Socket Yellow Saturation
    yellow_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Yellow Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    yellow_saturation_socket_1.default_value = 1.0
    yellow_saturation_socket_1.min_value = 0.0
    yellow_saturation_socket_1.max_value = 2.0
    yellow_saturation_socket_1.subtype = 'FACTOR'
    yellow_saturation_socket_1.attribute_domain = 'POINT'
    yellow_saturation_socket_1.default_input = 'VALUE'
    yellow_saturation_socket_1.structure_type = 'AUTO'

    # Socket Green Saturation
    green_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Green Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    green_saturation_socket_1.default_value = 1.0
    green_saturation_socket_1.min_value = 0.0
    green_saturation_socket_1.max_value = 2.0
    green_saturation_socket_1.subtype = 'FACTOR'
    green_saturation_socket_1.attribute_domain = 'POINT'
    green_saturation_socket_1.default_input = 'VALUE'
    green_saturation_socket_1.structure_type = 'AUTO'

    # Socket Teal Saturation
    teal_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Teal Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    teal_saturation_socket_1.default_value = 1.0
    teal_saturation_socket_1.min_value = 0.0
    teal_saturation_socket_1.max_value = 2.0
    teal_saturation_socket_1.subtype = 'FACTOR'
    teal_saturation_socket_1.attribute_domain = 'POINT'
    teal_saturation_socket_1.default_input = 'VALUE'
    teal_saturation_socket_1.structure_type = 'AUTO'

    # Socket Blue Saturation
    blue_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Blue Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    blue_saturation_socket_1.default_value = 1.0
    blue_saturation_socket_1.min_value = 0.0
    blue_saturation_socket_1.max_value = 2.0
    blue_saturation_socket_1.subtype = 'FACTOR'
    blue_saturation_socket_1.attribute_domain = 'POINT'
    blue_saturation_socket_1.default_input = 'VALUE'
    blue_saturation_socket_1.structure_type = 'AUTO'

    # Socket Pink Saturation
    pink_saturation_socket_1 = _rr_hue_correct.interface.new_socket(name="Pink Saturation", in_out='INPUT', socket_type='NodeSocketFloat', parent = saturation_panel_1)
    pink_saturation_socket_1.default_value = 1.0
    pink_saturation_socket_1.min_value = 0.0
    pink_saturation_socket_1.max_value = 2.0
    pink_saturation_socket_1.subtype = 'FACTOR'
    pink_saturation_socket_1.attribute_domain = 'POINT'
    pink_saturation_socket_1.default_input = 'VALUE'
    pink_saturation_socket_1.structure_type = 'AUTO'


    # Panel Value
    value_panel_1 = _rr_hue_correct.interface.new_panel("Value")
    # Socket Red Value
    red_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Red Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    red_value_socket_1.default_value = 1.0
    red_value_socket_1.min_value = 0.0
    red_value_socket_1.max_value = 2.0
    red_value_socket_1.subtype = 'FACTOR'
    red_value_socket_1.attribute_domain = 'POINT'
    red_value_socket_1.default_input = 'VALUE'
    red_value_socket_1.structure_type = 'AUTO'

    # Socket Orange Value
    orange_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Orange Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    orange_value_socket_1.default_value = 1.0
    orange_value_socket_1.min_value = 0.0
    orange_value_socket_1.max_value = 2.0
    orange_value_socket_1.subtype = 'FACTOR'
    orange_value_socket_1.attribute_domain = 'POINT'
    orange_value_socket_1.default_input = 'VALUE'
    orange_value_socket_1.structure_type = 'AUTO'

    # Socket Yellow Value
    yellow_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Yellow Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    yellow_value_socket_1.default_value = 1.0
    yellow_value_socket_1.min_value = 0.0
    yellow_value_socket_1.max_value = 2.0
    yellow_value_socket_1.subtype = 'FACTOR'
    yellow_value_socket_1.attribute_domain = 'POINT'
    yellow_value_socket_1.default_input = 'VALUE'
    yellow_value_socket_1.structure_type = 'AUTO'

    # Socket Green Value
    green_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Green Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    green_value_socket_1.default_value = 1.0
    green_value_socket_1.min_value = 0.0
    green_value_socket_1.max_value = 2.0
    green_value_socket_1.subtype = 'FACTOR'
    green_value_socket_1.attribute_domain = 'POINT'
    green_value_socket_1.default_input = 'VALUE'
    green_value_socket_1.structure_type = 'AUTO'

    # Socket Teal Value
    teal_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Teal Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    teal_value_socket_1.default_value = 1.0
    teal_value_socket_1.min_value = 0.0
    teal_value_socket_1.max_value = 2.0
    teal_value_socket_1.subtype = 'FACTOR'
    teal_value_socket_1.attribute_domain = 'POINT'
    teal_value_socket_1.default_input = 'VALUE'
    teal_value_socket_1.structure_type = 'AUTO'

    # Socket Blue Value
    blue_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Blue Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    blue_value_socket_1.default_value = 1.0
    blue_value_socket_1.min_value = 0.0
    blue_value_socket_1.max_value = 2.0
    blue_value_socket_1.subtype = 'FACTOR'
    blue_value_socket_1.attribute_domain = 'POINT'
    blue_value_socket_1.default_input = 'VALUE'
    blue_value_socket_1.structure_type = 'AUTO'

    # Socket Pink Value
    pink_value_socket_1 = _rr_hue_correct.interface.new_socket(name="Pink Value", in_out='INPUT', socket_type='NodeSocketFloat', parent = value_panel_1)
    pink_value_socket_1.default_value = 1.0
    pink_value_socket_1.min_value = 0.0
    pink_value_socket_1.max_value = 2.0
    pink_value_socket_1.subtype = 'FACTOR'
    pink_value_socket_1.attribute_domain = 'POINT'
    pink_value_socket_1.default_input = 'VALUE'
    pink_value_socket_1.structure_type = 'AUTO'


    # Initialize _rr_hue_correct nodes

    # Node Group Output
    group_output_25 = _rr_hue_correct.nodes.new("NodeGroupOutput")
    group_output_25.name = "Group Output"
    group_output_25.is_active_output = True

    # Node Separate Color
    separate_color_7 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_7.name = "Separate Color"
    separate_color_7.mode = 'HSV'
    separate_color_7.ycc_mode = 'ITUBT709'
    separate_color_7.outputs[0].hide = True
    separate_color_7.outputs[2].hide = True
    separate_color_7.outputs[3].hide = True

    # Node Group Input
    group_input_22 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_22.name = "Group Input"

    # Node Hue Correct
    hue_correct_2 = _rr_hue_correct.nodes.new("CompositorNodeHueCorrect")
    hue_correct_2.name = "Hue Correct"
    # Mapping settings
    hue_correct_2.mapping.extend = 'EXTRAPOLATED'
    hue_correct_2.mapping.tone = 'STANDARD'
    hue_correct_2.mapping.black_level = (0.0, 0.0, 0.0)
    hue_correct_2.mapping.white_level = (1.0, 1.0, 1.0)
    hue_correct_2.mapping.clip_min_x = 0.0
    hue_correct_2.mapping.clip_min_y = 0.0
    hue_correct_2.mapping.clip_max_x = 1.0
    hue_correct_2.mapping.clip_max_y = 1.0
    hue_correct_2.mapping.use_clip = True
    # Curve 0
    hue_correct_2_curve_0 = hue_correct_2.mapping.curves[0]
    for i in range(len(hue_correct_2_curve_0.points.values()) - 1, 1, -1):
        hue_correct_2_curve_0.points.remove(hue_correct_2_curve_0.points[i])
    hue_correct_2_curve_0_point_0 = hue_correct_2_curve_0.points[0]
    hue_correct_2_curve_0_point_0.location = (0.0, 0.5)
    hue_correct_2_curve_0_point_0.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_1 = hue_correct_2_curve_0.points[1]
    hue_correct_2_curve_0_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_2_curve_0_point_1.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_2 = hue_correct_2_curve_0.points.new(0.16700001060962677, 0.5)
    hue_correct_2_curve_0_point_2.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_3 = hue_correct_2_curve_0.points.new(0.33000001311302185, 0.5)
    hue_correct_2_curve_0_point_3.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_4 = hue_correct_2_curve_0.points.new(0.5, 0.5)
    hue_correct_2_curve_0_point_4.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_5 = hue_correct_2_curve_0.points.new(0.6700000166893005, 0.5)
    hue_correct_2_curve_0_point_5.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_6 = hue_correct_2_curve_0.points.new(0.8399999737739563, 0.5)
    hue_correct_2_curve_0_point_6.handle_type = 'AUTO'
    hue_correct_2_curve_0_point_7 = hue_correct_2_curve_0.points.new(1.0, 0.5)
    hue_correct_2_curve_0_point_7.handle_type = 'AUTO'
    # Curve 1
    hue_correct_2_curve_1 = hue_correct_2.mapping.curves[1]
    for i in range(len(hue_correct_2_curve_1.points.values()) - 1, 1, -1):
        hue_correct_2_curve_1.points.remove(hue_correct_2_curve_1.points[i])
    hue_correct_2_curve_1_point_0 = hue_correct_2_curve_1.points[0]
    hue_correct_2_curve_1_point_0.location = (0.0, 0.5)
    hue_correct_2_curve_1_point_0.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_1 = hue_correct_2_curve_1.points[1]
    hue_correct_2_curve_1_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_2_curve_1_point_1.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_2 = hue_correct_2_curve_1.points.new(0.16699999570846558, 0.5)
    hue_correct_2_curve_1_point_2.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_3 = hue_correct_2_curve_1.points.new(0.335999995470047, 0.5)
    hue_correct_2_curve_1_point_3.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_4 = hue_correct_2_curve_1.points.new(0.5, 0.5)
    hue_correct_2_curve_1_point_4.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_5 = hue_correct_2_curve_1.points.new(0.6700000166893005, 0.5)
    hue_correct_2_curve_1_point_5.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_6 = hue_correct_2_curve_1.points.new(0.8339999914169312, 0.5)
    hue_correct_2_curve_1_point_6.handle_type = 'AUTO'
    hue_correct_2_curve_1_point_7 = hue_correct_2_curve_1.points.new(1.0, 0.5)
    hue_correct_2_curve_1_point_7.handle_type = 'AUTO'
    # Curve 2
    hue_correct_2_curve_2 = hue_correct_2.mapping.curves[2]
    for i in range(len(hue_correct_2_curve_2.points.values()) - 1, 1, -1):
        hue_correct_2_curve_2.points.remove(hue_correct_2_curve_2.points[i])
    hue_correct_2_curve_2_point_0 = hue_correct_2_curve_2.points[0]
    hue_correct_2_curve_2_point_0.location = (0.0, 0.5)
    hue_correct_2_curve_2_point_0.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_1 = hue_correct_2_curve_2.points[1]
    hue_correct_2_curve_2_point_1.location = (0.0949999988079071, 0.5)
    hue_correct_2_curve_2_point_1.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_2 = hue_correct_2_curve_2.points.new(0.1679999977350235, 0.5)
    hue_correct_2_curve_2_point_2.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_3 = hue_correct_2_curve_2.points.new(0.335999995470047, 0.5)
    hue_correct_2_curve_2_point_3.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_4 = hue_correct_2_curve_2.points.new(0.5, 0.5)
    hue_correct_2_curve_2_point_4.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_5 = hue_correct_2_curve_2.points.new(0.6690000295639038, 0.5)
    hue_correct_2_curve_2_point_5.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_6 = hue_correct_2_curve_2.points.new(0.8330000042915344, 0.5)
    hue_correct_2_curve_2_point_6.handle_type = 'AUTO'
    hue_correct_2_curve_2_point_7 = hue_correct_2_curve_2.points.new(1.0, 0.5)
    hue_correct_2_curve_2_point_7.handle_type = 'AUTO'
    # Update curve after changes
    hue_correct_2.mapping.update()

    # Node Separate Color.001
    separate_color_001_4 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_4.name = "Separate Color.001"
    separate_color_001_4.mode = 'HSV'
    separate_color_001_4.ycc_mode = 'ITUBT709'
    separate_color_001_4.outputs[0].hide = True
    separate_color_001_4.outputs[1].hide = True

    # Node Group Input.001
    group_input_001_7 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_001_7.name = "Group Input.001"
    group_input_001_7.outputs[0].hide = True
    group_input_001_7.outputs[2].hide = True
    group_input_001_7.outputs[3].hide = True
    group_input_001_7.outputs[4].hide = True
    group_input_001_7.outputs[5].hide = True
    group_input_001_7.outputs[6].hide = True
    group_input_001_7.outputs[7].hide = True
    group_input_001_7.outputs[15].hide = True
    group_input_001_7.outputs[16].hide = True
    group_input_001_7.outputs[17].hide = True
    group_input_001_7.outputs[18].hide = True
    group_input_001_7.outputs[19].hide = True
    group_input_001_7.outputs[20].hide = True
    group_input_001_7.outputs[21].hide = True
    group_input_001_7.outputs[22].hide = True
    group_input_001_7.outputs[23].hide = True
    group_input_001_7.outputs[24].hide = True
    group_input_001_7.outputs[25].hide = True
    group_input_001_7.outputs[26].hide = True
    group_input_001_7.outputs[27].hide = True
    group_input_001_7.outputs[28].hide = True
    group_input_001_7.outputs[29].hide = True

    # Node Combine Color
    combine_color_8 = _rr_hue_correct.nodes.new("CompositorNodeCombineColor")
    combine_color_8.name = "Combine Color"
    combine_color_8.mode = 'HSV'
    combine_color_8.ycc_mode = 'ITUBT709'

    # Node Group
    group_4 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_4.label = "Teal"
    group_4.name = "Group"
    group_4.node_tree = _rr_mask_value
    # Socket_4
    group_4.inputs[2].default_value = 0.5

    # Node Group.001
    group_001_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_001_1.label = "Blue"
    group_001_1.name = "Group.001"
    group_001_1.node_tree = _rr_mask_value
    # Socket_4
    group_001_1.inputs[2].default_value = 0.6700000166893005

    # Node Group.002
    group_002_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_002_1.label = "Pink"
    group_002_1.name = "Group.002"
    group_002_1.node_tree = _rr_mask_value
    # Socket_4
    group_002_1.inputs[2].default_value = 0.8399999737739563

    # Node Group.004
    group_004_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_004_1.label = "Red"
    group_004_1.name = "Group.004"
    group_004_1.node_tree = _rr_mask_value
    # Socket_4
    group_004_1.inputs[2].default_value = 0.0

    # Node Group.005
    group_005_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_005_1.label = "Orange"
    group_005_1.name = "Group.005"
    group_005_1.node_tree = _rr_mask_value
    # Socket_4
    group_005_1.inputs[2].default_value = 0.0949999988079071

    # Node Group.006
    group_006_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_006_1.label = "Yellow"
    group_006_1.name = "Group.006"
    group_006_1.node_tree = _rr_mask_value
    # Socket_4
    group_006_1.inputs[2].default_value = 0.16699999570846558

    # Node Group.007
    group_007_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_007_1.label = "Green"
    group_007_1.name = "Group.007"
    group_007_1.node_tree = _rr_mask_value
    # Socket_4
    group_007_1.inputs[2].default_value = 0.33000001311302185

    # Node Math.001
    math_001_16 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_001_16.name = "Math.001"
    math_001_16.operation = 'WRAP'
    math_001_16.use_clamp = False
    # Value_001
    math_001_16.inputs[1].default_value = 1.0
    # Value_002
    math_001_16.inputs[2].default_value = 0.0

    # Node Reroute.001
    reroute_001_9 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_001_9.name = "Reroute.001"
    reroute_001_9.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_9 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_002_9.name = "Reroute.002"
    reroute_002_9.socket_idname = "NodeSocketFloat"
    # Node Frame
    frame_13 = _rr_hue_correct.nodes.new("NodeFrame")
    frame_13.label = "Hue"
    frame_13.name = "Frame"
    frame_13.label_size = 20
    frame_13.shrink = True

    # Node Group Input.002
    group_input_002_4 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_002_4.name = "Group Input.002"
    group_input_002_4.outputs[0].hide = True
    group_input_002_4.outputs[2].hide = True
    group_input_002_4.outputs[3].hide = True
    group_input_002_4.outputs[4].hide = True
    group_input_002_4.outputs[5].hide = True
    group_input_002_4.outputs[6].hide = True
    group_input_002_4.outputs[7].hide = True
    group_input_002_4.outputs[8].hide = True
    group_input_002_4.outputs[9].hide = True
    group_input_002_4.outputs[10].hide = True
    group_input_002_4.outputs[11].hide = True
    group_input_002_4.outputs[12].hide = True
    group_input_002_4.outputs[13].hide = True
    group_input_002_4.outputs[14].hide = True
    group_input_002_4.outputs[22].hide = True
    group_input_002_4.outputs[23].hide = True
    group_input_002_4.outputs[24].hide = True
    group_input_002_4.outputs[25].hide = True
    group_input_002_4.outputs[26].hide = True
    group_input_002_4.outputs[27].hide = True
    group_input_002_4.outputs[28].hide = True
    group_input_002_4.outputs[29].hide = True

    # Node Reroute.004
    reroute_004_6 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_004_6.name = "Reroute.004"
    reroute_004_6.socket_idname = "NodeSocketFloat"
    # Node Frame.001
    frame_001_10 = _rr_hue_correct.nodes.new("NodeFrame")
    frame_001_10.label = "Saturation"
    frame_001_10.name = "Frame.001"
    frame_001_10.label_size = 20
    frame_001_10.shrink = True

    # Node Reroute
    reroute_15 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_15.name = "Reroute"
    reroute_15.socket_idname = "NodeSocketFloat"
    # Node Clamp
    clamp_1 = _rr_hue_correct.nodes.new("ShaderNodeClamp")
    clamp_1.name = "Clamp"
    clamp_1.clamp_type = 'MINMAX'
    # Min
    clamp_1.inputs[1].default_value = 0.0
    # Max
    clamp_1.inputs[2].default_value = 1.0

    # Node Group Input.003
    group_input_003_5 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_003_5.name = "Group Input.003"

    # Node Mix.001
    mix_001_11 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_001_11.name = "Mix.001"
    mix_001_11.blend_type = 'MIX'
    mix_001_11.clamp_factor = True
    mix_001_11.clamp_result = False
    mix_001_11.data_type = 'RGBA'
    mix_001_11.factor_mode = 'UNIFORM'

    # Node Group Input.004
    group_input_004_5 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_004_5.name = "Group Input.004"
    group_input_004_5.outputs[2].hide = True
    group_input_004_5.outputs[4].hide = True
    group_input_004_5.outputs[5].hide = True
    group_input_004_5.outputs[8].hide = True
    group_input_004_5.outputs[9].hide = True
    group_input_004_5.outputs[10].hide = True
    group_input_004_5.outputs[11].hide = True
    group_input_004_5.outputs[12].hide = True
    group_input_004_5.outputs[13].hide = True
    group_input_004_5.outputs[14].hide = True
    group_input_004_5.outputs[15].hide = True
    group_input_004_5.outputs[16].hide = True
    group_input_004_5.outputs[17].hide = True
    group_input_004_5.outputs[18].hide = True
    group_input_004_5.outputs[19].hide = True
    group_input_004_5.outputs[20].hide = True
    group_input_004_5.outputs[21].hide = True
    group_input_004_5.outputs[22].hide = True
    group_input_004_5.outputs[23].hide = True
    group_input_004_5.outputs[24].hide = True
    group_input_004_5.outputs[25].hide = True
    group_input_004_5.outputs[26].hide = True
    group_input_004_5.outputs[27].hide = True
    group_input_004_5.outputs[28].hide = True
    group_input_004_5.outputs[29].hide = True

    # Node Reroute.008
    reroute_008_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_008_2.name = "Reroute.008"
    reroute_008_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.009
    reroute_009_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_009_2.name = "Reroute.009"
    reroute_009_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.010
    reroute_010_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_010_2.name = "Reroute.010"
    reroute_010_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.011
    reroute_011_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_011_2.name = "Reroute.011"
    reroute_011_2.socket_idname = "NodeSocketFloat"
    # Node Frame.002
    frame_002_9 = _rr_hue_correct.nodes.new("NodeFrame")
    frame_002_9.label = "Perceptual"
    frame_002_9.name = "Frame.002"
    frame_002_9.label_size = 20
    frame_002_9.shrink = True

    # Node .sRGB_to_LAB
    _srgb_to_lab_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _srgb_to_lab_1.name = ".sRGB_to_LAB"
    _srgb_to_lab_1.node_tree = _rr_srgb_to_lab

    # Node .LAB_to_sRGB
    _lab_to_srgb_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_to_srgb_1.name = ".LAB_to_sRGB"
    _lab_to_srgb_1.node_tree = _rr_lab_to_srgb

    # Node Reroute.013
    reroute_013_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_013_2.name = "Reroute.013"
    reroute_013_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.014
    reroute_014_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_014_1.name = "Reroute.014"
    reroute_014_1.socket_idname = "NodeSocketFloat"
    # Node .LAB_adjustments.001
    _lab_adjustments_001_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_001_1.name = ".LAB_adjustments.001"
    _lab_adjustments_001_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.002
    _lab_adjustments_002_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_002_1.name = ".LAB_adjustments.002"
    _lab_adjustments_002_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.003
    _lab_adjustments_003_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_003_1.name = ".LAB_adjustments.003"
    _lab_adjustments_003_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.004
    _lab_adjustments_004_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_004_1.name = ".LAB_adjustments.004"
    _lab_adjustments_004_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.005
    _lab_adjustments_005_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_005_1.name = ".LAB_adjustments.005"
    _lab_adjustments_005_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.006
    _lab_adjustments_006_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_006_1.name = ".LAB_adjustments.006"
    _lab_adjustments_006_1.node_tree = _rr_lab_adjustments

    # Node .LAB_adjustments.007
    _lab_adjustments_007_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    _lab_adjustments_007_1.name = ".LAB_adjustments.007"
    _lab_adjustments_007_1.node_tree = _rr_lab_adjustments

    # Node Switch
    switch_9 = _rr_hue_correct.nodes.new("CompositorNodeSwitch")
    switch_9.name = "Switch"

    # Node Reroute.015
    reroute_015_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_015_1.name = "Reroute.015"
    reroute_015_1.socket_idname = "NodeSocketColor"
    # Node Math
    math_20 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_20.name = "Math"
    math_20.operation = 'COMPARE'
    math_20.use_clamp = False
    # Value_001
    math_20.inputs[1].default_value = 1.0
    # Value_002
    math_20.inputs[2].default_value = 0.0010000000474974513

    # Node Math.002
    math_002_14 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_002_14.name = "Math.002"
    math_002_14.operation = 'COMPARE'
    math_002_14.use_clamp = False
    # Value_001
    math_002_14.inputs[1].default_value = 0.0
    # Value_002
    math_002_14.inputs[2].default_value = 0.0010000000474974513

    # Node Switch.001
    switch_001_1 = _rr_hue_correct.nodes.new("CompositorNodeSwitch")
    switch_001_1.name = "Switch.001"

    # Node Reroute.016
    reroute_016_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_016_1.name = "Reroute.016"
    reroute_016_1.socket_idname = "NodeSocketColor"
    # Node Frame.003
    frame_003_7 = _rr_hue_correct.nodes.new("NodeFrame")
    frame_003_7.label = "Combine"
    frame_003_7.name = "Frame.003"
    frame_003_7.label_size = 20
    frame_003_7.shrink = True

    # Node Group.009
    group_009_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_009_1.name = "Group.009"
    group_009_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_009_1.inputs[3].default_value = 0.0

    # Node Group.010
    group_010_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_010_1.name = "Group.010"
    group_010_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_010_1.inputs[3].default_value = 0.0

    # Node Group.011
    group_011_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_011_1.name = "Group.011"
    group_011_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_011_1.inputs[3].default_value = 0.0

    # Node Group.012
    group_012_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_012_1.name = "Group.012"
    group_012_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_012_1.inputs[3].default_value = 0.0

    # Node Group.013
    group_013_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_013_1.name = "Group.013"
    group_013_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_013_1.inputs[3].default_value = 0.0

    # Node Group.014
    group_014_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_014_1.name = "Group.014"
    group_014_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_014_1.inputs[3].default_value = 0.0

    # Node Group.015
    group_015_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_015_1.name = "Group.015"
    group_015_1.node_tree = _rr_adjust_mask
    # Socket_4
    group_015_1.inputs[3].default_value = 0.0

    # Node Reroute.005
    reroute_005_8 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_005_8.name = "Reroute.005"
    reroute_005_8.socket_idname = "NodeSocketFloat"
    # Node Group.025
    group_025_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_025_1.name = "Group.025"
    group_025_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_025_1.inputs[2].default_value = 1.0

    # Node Group.026
    group_026_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_026_1.name = "Group.026"
    group_026_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_026_1.inputs[2].default_value = 1.0

    # Node Group.027
    group_027_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_027_1.name = "Group.027"
    group_027_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_027_1.inputs[2].default_value = 1.0

    # Node Group.028
    group_028_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_028_1.name = "Group.028"
    group_028_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_028_1.inputs[2].default_value = 1.0

    # Node Group.029
    group_029_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_029_1.name = "Group.029"
    group_029_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_029_1.inputs[2].default_value = 1.0

    # Node Group.030
    group_030_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_030_1.name = "Group.030"
    group_030_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_030_1.inputs[2].default_value = 1.0

    # Node Group.031
    group_031_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_031_1.name = "Group.031"
    group_031_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_031_1.inputs[2].default_value = 1.0

    # Node Reroute.003
    reroute_003_8 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_003_8.name = "Reroute.003"
    reroute_003_8.socket_idname = "NodeSocketColor"
    # Node Map Range
    map_range_14 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_14.name = "Map Range"
    map_range_14.clamp = True
    map_range_14.data_type = 'FLOAT'
    map_range_14.interpolation_type = 'LINEAR'
    # From Min
    map_range_14.inputs[1].default_value = 0.0
    # From Max
    map_range_14.inputs[2].default_value = 1.0
    # To Min
    map_range_14.inputs[3].default_value = -0.5235999822616577
    # To Max
    map_range_14.inputs[4].default_value = 0.5235999822616577

    # Node Map Range.001
    map_range_001_13 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_001_13.label = "To Rad"
    map_range_001_13.name = "Map Range.001"
    map_range_001_13.hide = True
    map_range_001_13.clamp = True
    map_range_001_13.data_type = 'FLOAT'
    map_range_001_13.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_13.inputs[1].default_value = 0.0
    # From Max
    map_range_001_13.inputs[2].default_value = 1.0
    # To Min
    map_range_001_13.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_001_13.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.002
    map_range_002_10 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_002_10.label = "To Rad"
    map_range_002_10.name = "Map Range.002"
    map_range_002_10.hide = True
    map_range_002_10.clamp = True
    map_range_002_10.data_type = 'FLOAT'
    map_range_002_10.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_10.inputs[1].default_value = 0.0
    # From Max
    map_range_002_10.inputs[2].default_value = 1.0
    # To Min
    map_range_002_10.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_002_10.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.003
    map_range_003_8 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_003_8.label = "To Rad"
    map_range_003_8.name = "Map Range.003"
    map_range_003_8.hide = True
    map_range_003_8.clamp = True
    map_range_003_8.data_type = 'FLOAT'
    map_range_003_8.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_8.inputs[1].default_value = 0.0
    # From Max
    map_range_003_8.inputs[2].default_value = 1.0
    # To Min
    map_range_003_8.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_003_8.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.004
    map_range_004_6 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_004_6.label = "To Rad"
    map_range_004_6.name = "Map Range.004"
    map_range_004_6.hide = True
    map_range_004_6.clamp = True
    map_range_004_6.data_type = 'FLOAT'
    map_range_004_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_004_6.inputs[1].default_value = 0.0
    # From Max
    map_range_004_6.inputs[2].default_value = 1.0
    # To Min
    map_range_004_6.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_004_6.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.005
    map_range_005_6 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_005_6.label = "To Rad"
    map_range_005_6.name = "Map Range.005"
    map_range_005_6.hide = True
    map_range_005_6.clamp = True
    map_range_005_6.data_type = 'FLOAT'
    map_range_005_6.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_6.inputs[1].default_value = 0.0
    # From Max
    map_range_005_6.inputs[2].default_value = 1.0
    # To Min
    map_range_005_6.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_005_6.inputs[4].default_value = 1.0471975803375244

    # Node Map Range.006
    map_range_006_2 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_006_2.label = "To Rad"
    map_range_006_2.name = "Map Range.006"
    map_range_006_2.hide = True
    map_range_006_2.clamp = True
    map_range_006_2.data_type = 'FLOAT'
    map_range_006_2.interpolation_type = 'LINEAR'
    # From Min
    map_range_006_2.inputs[1].default_value = 0.0
    # From Max
    map_range_006_2.inputs[2].default_value = 1.0
    # To Min
    map_range_006_2.inputs[3].default_value = -1.0471999645233154
    # To Max
    map_range_006_2.inputs[4].default_value = 1.0471975803375244

    # Node Separate Color.004
    separate_color_004_2 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_004_2.name = "Separate Color.004"
    separate_color_004_2.mode = 'HSV'
    separate_color_004_2.ycc_mode = 'ITUBT709'

    # Node Combine Color.001
    combine_color_001_2 = _rr_hue_correct.nodes.new("CompositorNodeCombineColor")
    combine_color_001_2.name = "Combine Color.001"
    combine_color_001_2.mode = 'HSV'
    combine_color_001_2.ycc_mode = 'ITUBT709'

    # Node Clamp.001
    clamp_001_1 = _rr_hue_correct.nodes.new("ShaderNodeClamp")
    clamp_001_1.name = "Clamp.001"
    clamp_001_1.clamp_type = 'MINMAX'
    # Min
    clamp_001_1.inputs[1].default_value = 0.0
    # Max
    clamp_001_1.inputs[2].default_value = 1.0

    # Node Reroute.019
    reroute_019_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_019_1.name = "Reroute.019"
    reroute_019_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.020
    reroute_020_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_020_1.name = "Reroute.020"
    reroute_020_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.021
    reroute_021_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_021_1.name = "Reroute.021"
    reroute_021_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.022
    reroute_022_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_022_1.name = "Reroute.022"
    reroute_022_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.023
    reroute_023_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_023_1.name = "Reroute.023"
    reroute_023_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.024
    reroute_024_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_024_1.name = "Reroute.024"
    reroute_024_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.025
    reroute_025_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_025_1.name = "Reroute.025"
    reroute_025_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.028
    reroute_028_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_028_1.name = "Reroute.028"
    reroute_028_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.029
    reroute_029_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_029_1.name = "Reroute.029"
    reroute_029_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.030
    reroute_030_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_030_1.name = "Reroute.030"
    reroute_030_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.031
    reroute_031_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_031_1.name = "Reroute.031"
    reroute_031_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.032
    reroute_032_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_032_1.name = "Reroute.032"
    reroute_032_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.033
    reroute_033_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_033_1.name = "Reroute.033"
    reroute_033_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.034
    reroute_034_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_034_1.name = "Reroute.034"
    reroute_034_1.socket_idname = "NodeSocketFloat"
    # Node Group Input.005
    group_input_005_4 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_005_4.name = "Group Input.005"
    group_input_005_4.outputs[0].hide = True
    group_input_005_4.outputs[1].hide = True
    group_input_005_4.outputs[2].hide = True
    group_input_005_4.outputs[3].hide = True
    group_input_005_4.outputs[4].hide = True
    group_input_005_4.outputs[6].hide = True
    group_input_005_4.outputs[7].hide = True
    group_input_005_4.outputs[8].hide = True
    group_input_005_4.outputs[9].hide = True
    group_input_005_4.outputs[10].hide = True
    group_input_005_4.outputs[11].hide = True
    group_input_005_4.outputs[12].hide = True
    group_input_005_4.outputs[13].hide = True
    group_input_005_4.outputs[14].hide = True
    group_input_005_4.outputs[15].hide = True
    group_input_005_4.outputs[16].hide = True
    group_input_005_4.outputs[17].hide = True
    group_input_005_4.outputs[18].hide = True
    group_input_005_4.outputs[19].hide = True
    group_input_005_4.outputs[20].hide = True
    group_input_005_4.outputs[21].hide = True
    group_input_005_4.outputs[22].hide = True
    group_input_005_4.outputs[23].hide = True
    group_input_005_4.outputs[24].hide = True
    group_input_005_4.outputs[25].hide = True
    group_input_005_4.outputs[26].hide = True
    group_input_005_4.outputs[27].hide = True
    group_input_005_4.outputs[28].hide = True
    group_input_005_4.outputs[29].hide = True

    # Node Separate Color.002
    separate_color_002_2 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_2.name = "Separate Color.002"
    separate_color_002_2.mode = 'HSV'
    separate_color_002_2.ycc_mode = 'ITUBT709'
    separate_color_002_2.outputs[1].hide = True
    separate_color_002_2.outputs[2].hide = True
    separate_color_002_2.outputs[3].hide = True

    # Node Separate Color.003
    separate_color_003_3 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_3.name = "Separate Color.003"
    separate_color_003_3.mode = 'HSV'
    separate_color_003_3.ycc_mode = 'ITUBT709'
    separate_color_003_3.outputs[0].hide = True
    separate_color_003_3.outputs[2].hide = True
    separate_color_003_3.outputs[3].hide = True

    # Node Reroute.006
    reroute_006_3 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_006_3.name = "Reroute.006"
    reroute_006_3.socket_idname = "NodeSocketColor"
    # Node Separate Color.005
    separate_color_005_1 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_005_1.name = "Separate Color.005"
    separate_color_005_1.mode = 'HSV'
    separate_color_005_1.ycc_mode = 'ITUBT709'

    # Node Reroute.012
    reroute_012_2 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_012_2.name = "Reroute.012"
    reroute_012_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.035
    reroute_035_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_035_1.name = "Reroute.035"
    reroute_035_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.036
    reroute_036_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_036_1.name = "Reroute.036"
    reroute_036_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.037
    reroute_037_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_037_1.name = "Reroute.037"
    reroute_037_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.038
    reroute_038_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_038_1.name = "Reroute.038"
    reroute_038_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.039
    reroute_039_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_039_1.name = "Reroute.039"
    reroute_039_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.040
    reroute_040_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_040_1.name = "Reroute.040"
    reroute_040_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.041
    reroute_041_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_041_1.name = "Reroute.041"
    reroute_041_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.042
    reroute_042_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_042_1.name = "Reroute.042"
    reroute_042_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.043
    reroute_043_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_043_1.name = "Reroute.043"
    reroute_043_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.044
    reroute_044_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_044_1.name = "Reroute.044"
    reroute_044_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.045
    reroute_045_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_045_1.name = "Reroute.045"
    reroute_045_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.046
    reroute_046_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_046_1.name = "Reroute.046"
    reroute_046_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.047
    reroute_047_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_047_1.name = "Reroute.047"
    reroute_047_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.017
    reroute_017_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_017_1.name = "Reroute.017"
    reroute_017_1.socket_idname = "NodeSocketColor"
    # Node Reroute.048
    reroute_048_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_048_1.name = "Reroute.048"
    reroute_048_1.socket_idname = "NodeSocketColor"
    # Node Separate Color.006
    separate_color_006_1 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_006_1.name = "Separate Color.006"
    separate_color_006_1.mode = 'HSV'
    separate_color_006_1.ycc_mode = 'ITUBT709'

    # Node Combine Color.002
    combine_color_002_2 = _rr_hue_correct.nodes.new("CompositorNodeCombineColor")
    combine_color_002_2.name = "Combine Color.002"
    combine_color_002_2.mode = 'HSV'
    combine_color_002_2.ycc_mode = 'ITUBT709'

    # Node Group Input.006
    group_input_006_1 = _rr_hue_correct.nodes.new("NodeGroupInput")
    group_input_006_1.name = "Group Input.006"
    group_input_006_1.outputs[0].hide = True
    group_input_006_1.outputs[1].hide = True
    group_input_006_1.outputs[2].hide = True
    group_input_006_1.outputs[3].hide = True
    group_input_006_1.outputs[4].hide = True
    group_input_006_1.outputs[5].hide = True
    group_input_006_1.outputs[6].hide = True
    group_input_006_1.outputs[7].hide = True
    group_input_006_1.outputs[8].hide = True
    group_input_006_1.outputs[9].hide = True
    group_input_006_1.outputs[10].hide = True
    group_input_006_1.outputs[11].hide = True
    group_input_006_1.outputs[12].hide = True
    group_input_006_1.outputs[13].hide = True
    group_input_006_1.outputs[14].hide = True
    group_input_006_1.outputs[15].hide = True
    group_input_006_1.outputs[16].hide = True
    group_input_006_1.outputs[17].hide = True
    group_input_006_1.outputs[18].hide = True
    group_input_006_1.outputs[19].hide = True
    group_input_006_1.outputs[20].hide = True
    group_input_006_1.outputs[21].hide = True
    group_input_006_1.outputs[29].hide = True

    # Node Group.033
    group_033_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_033_1.name = "Group.033"
    group_033_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_033_1.inputs[2].default_value = 1.0

    # Node Group.034
    group_034_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_034_1.name = "Group.034"
    group_034_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_034_1.inputs[2].default_value = 1.0

    # Node Group.035
    group_035_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_035_1.name = "Group.035"
    group_035_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_035_1.inputs[2].default_value = 1.0

    # Node Group.036
    group_036_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_036_1.name = "Group.036"
    group_036_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_036_1.inputs[2].default_value = 1.0

    # Node Group.037
    group_037_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_037_1.name = "Group.037"
    group_037_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_037_1.inputs[2].default_value = 1.0

    # Node Group.038
    group_038_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_038_1.name = "Group.038"
    group_038_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_038_1.inputs[2].default_value = 1.0

    # Node Group.039
    group_039_1 = _rr_hue_correct.nodes.new("CompositorNodeGroup")
    group_039_1.name = "Group.039"
    group_039_1.node_tree = _rr_adjust_mask
    # Socket_0
    group_039_1.inputs[2].default_value = 1.0

    # Node Frame.004
    frame_004_6 = _rr_hue_correct.nodes.new("NodeFrame")
    frame_004_6.label = "Value"
    frame_004_6.name = "Frame.004"
    frame_004_6.label_size = 20
    frame_004_6.shrink = True

    # Node Reroute.049
    reroute_049_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_049_1.name = "Reroute.049"
    reroute_049_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.050
    reroute_050_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_050_1.name = "Reroute.050"
    reroute_050_1.socket_idname = "NodeSocketFloat"
    # Node Mix
    mix_16 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_16.name = "Mix"
    mix_16.blend_type = 'MIX'
    mix_16.clamp_factor = True
    mix_16.clamp_result = False
    mix_16.data_type = 'RGBA'
    mix_16.factor_mode = 'UNIFORM'

    # Node Reroute.051
    reroute_051_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_051_1.name = "Reroute.051"
    reroute_051_1.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.052
    reroute_052_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_052_1.name = "Reroute.052"
    reroute_052_1.socket_idname = "NodeSocketColor"
    # Node Reroute.053
    reroute_053_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_053_1.label = "Factor"
    reroute_053_1.name = "Reroute.053"
    reroute_053_1.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.054
    reroute_054_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_054_1.label = "Input"
    reroute_054_1.name = "Reroute.054"
    reroute_054_1.socket_idname = "NodeSocketColor"
    # Node Value
    value_1 = _rr_hue_correct.nodes.new("ShaderNodeValue")
    value_1.label = "Range"
    value_1.name = "Value"

    value_1.outputs[0].default_value = 0.16660000383853912
    # Node Math.003
    math_003_13 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_003_13.label = "Halve"
    math_003_13.name = "Math.003"
    math_003_13.hide = True
    math_003_13.operation = 'DIVIDE'
    math_003_13.use_clamp = False
    # Value_001
    math_003_13.inputs[1].default_value = 2.0

    # Node Math.004
    math_004_12 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_004_12.name = "Math.004"
    math_004_12.operation = 'MULTIPLY'
    math_004_12.use_clamp = False

    # Node Reroute.055
    reroute_055_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_055_1.name = "Reroute.055"
    reroute_055_1.socket_idname = "NodeSocketFloat"
    # Node Map Range.007
    map_range_007_1 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_007_1.name = "Map Range.007"
    map_range_007_1.clamp = True
    map_range_007_1.data_type = 'FLOAT'
    map_range_007_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_007_1.inputs[1].default_value = 0.0
    # From Max
    map_range_007_1.inputs[2].default_value = 1.0
    # To Min
    map_range_007_1.inputs[3].default_value = 0.0
    # To Max
    map_range_007_1.inputs[4].default_value = 6.0

    # Node Math.005
    math_005_11 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_005_11.label = "-1"
    math_005_11.name = "Math.005"
    math_005_11.hide = True
    math_005_11.operation = 'SUBTRACT'
    math_005_11.use_clamp = False
    # Value_001
    math_005_11.inputs[1].default_value = 1.0

    # Node Math.006
    math_006_10 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_006_10.label = "-1"
    math_006_10.name = "Math.006"
    math_006_10.hide = True
    math_006_10.operation = 'SUBTRACT'
    math_006_10.use_clamp = False
    # Value_001
    math_006_10.inputs[1].default_value = 1.0

    # Node Math.007
    math_007_10 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_007_10.label = "-1"
    math_007_10.name = "Math.007"
    math_007_10.hide = True
    math_007_10.operation = 'SUBTRACT'
    math_007_10.use_clamp = False
    # Value_001
    math_007_10.inputs[1].default_value = 1.0

    # Node Math.008
    math_008_9 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_008_9.label = "-1"
    math_008_9.name = "Math.008"
    math_008_9.hide = True
    math_008_9.operation = 'SUBTRACT'
    math_008_9.use_clamp = False
    # Value_001
    math_008_9.inputs[1].default_value = 1.0

    # Node Math.009
    math_009_8 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_009_8.label = "-1"
    math_009_8.name = "Math.009"
    math_009_8.hide = True
    math_009_8.operation = 'SUBTRACT'
    math_009_8.use_clamp = False
    # Value_001
    math_009_8.inputs[1].default_value = 1.0

    # Node Math.010
    math_010_6 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_010_6.label = "-1"
    math_010_6.name = "Math.010"
    math_010_6.hide = True
    math_010_6.operation = 'SUBTRACT'
    math_010_6.use_clamp = False
    # Value_001
    math_010_6.inputs[1].default_value = 1.0

    # Node Math.011
    math_011_6 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_011_6.label = "-1"
    math_011_6.name = "Math.011"
    math_011_6.hide = True
    math_011_6.operation = 'SUBTRACT'
    math_011_6.use_clamp = False
    # Value_001
    math_011_6.inputs[1].default_value = 1.0

    # Node Math.013
    math_013_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_013_4.label = "*2"
    math_013_4.name = "Math.013"
    math_013_4.hide = True
    math_013_4.operation = 'MULTIPLY'
    math_013_4.use_clamp = False
    # Value_001
    math_013_4.inputs[1].default_value = 2.0

    # Node Math.014
    math_014_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_014_4.label = "-1"
    math_014_4.name = "Math.014"
    math_014_4.hide = True
    math_014_4.operation = 'SUBTRACT'
    math_014_4.use_clamp = False
    # Value_001
    math_014_4.inputs[1].default_value = 1.0

    # Node Math.015
    math_015_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_015_4.label = "*2"
    math_015_4.name = "Math.015"
    math_015_4.hide = True
    math_015_4.operation = 'MULTIPLY'
    math_015_4.use_clamp = False
    # Value_001
    math_015_4.inputs[1].default_value = 2.0

    # Node Math.016
    math_016_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_016_4.label = "-1"
    math_016_4.name = "Math.016"
    math_016_4.hide = True
    math_016_4.operation = 'SUBTRACT'
    math_016_4.use_clamp = False
    # Value_001
    math_016_4.inputs[1].default_value = 1.0

    # Node Reroute.057
    reroute_057_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_057_1.label = "Sat Mask"
    reroute_057_1.name = "Reroute.057"
    reroute_057_1.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.058
    reroute_058_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_058_1.label = "Value Mask"
    reroute_058_1.name = "Reroute.058"
    reroute_058_1.socket_idname = "NodeSocketFloatFactor"
    # Node Separate Color.007
    separate_color_007_1 = _rr_hue_correct.nodes.new("CompositorNodeSeparateColor")
    separate_color_007_1.name = "Separate Color.007"
    separate_color_007_1.mode = 'HSV'
    separate_color_007_1.ycc_mode = 'ITUBT709'

    # Node Math.029
    math_029_3 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_029_3.name = "Math.029"
    math_029_3.hide = True
    math_029_3.operation = 'MULTIPLY'
    math_029_3.use_clamp = False

    # Node Map Range.008
    map_range_008_1 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_008_1.label = "Flip"
    map_range_008_1.name = "Map Range.008"
    map_range_008_1.hide = True
    map_range_008_1.clamp = True
    map_range_008_1.data_type = 'FLOAT'
    map_range_008_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_008_1.inputs[1].default_value = 0.0
    # From Max
    map_range_008_1.inputs[2].default_value = 1.0
    # To Min
    map_range_008_1.inputs[3].default_value = 1.0
    # To Max
    map_range_008_1.inputs[4].default_value = 0.0

    # Node Mix.002
    mix_002_5 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_002_5.name = "Mix.002"
    mix_002_5.blend_type = 'MIX'
    mix_002_5.clamp_factor = True
    mix_002_5.clamp_result = False
    mix_002_5.data_type = 'FLOAT'
    mix_002_5.factor_mode = 'UNIFORM'

    # Node Map Range.009
    map_range_009_1 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_009_1.name = "Map Range.009"
    map_range_009_1.clamp = False
    map_range_009_1.data_type = 'FLOAT'
    map_range_009_1.interpolation_type = 'LINEAR'
    # From Min
    map_range_009_1.inputs[1].default_value = -1.0
    # From Max
    map_range_009_1.inputs[2].default_value = 1.0
    # To Min
    map_range_009_1.inputs[3].default_value = 0.0
    # To Max
    map_range_009_1.inputs[4].default_value = 1.0

    # Node Mix.003
    mix_003_2 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_003_2.name = "Mix.003"
    mix_003_2.blend_type = 'MIX'
    mix_003_2.clamp_factor = True
    mix_003_2.clamp_result = False
    mix_003_2.data_type = 'FLOAT'
    mix_003_2.factor_mode = 'UNIFORM'
    # A_Float
    mix_003_2.inputs[2].default_value = 1.0

    # Node Math.030
    math_030_2 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_030_2.name = "Math.030"
    math_030_2.hide = True
    math_030_2.operation = 'ABSOLUTE'
    math_030_2.use_clamp = False

    # Node Reroute.061
    reroute_061_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_061_1.name = "Reroute.061"
    reroute_061_1.socket_idname = "NodeSocketFloatFactor"
    # Node Map Range.010
    map_range_010 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_010.label = "Flip"
    map_range_010.name = "Map Range.010"
    map_range_010.hide = True
    map_range_010.clamp = True
    map_range_010.data_type = 'FLOAT'
    map_range_010.interpolation_type = 'LINEAR'
    # From Min
    map_range_010.inputs[1].default_value = 0.0
    # From Max
    map_range_010.inputs[2].default_value = 1.0
    # To Min
    map_range_010.inputs[3].default_value = 1.0
    # To Max
    map_range_010.inputs[4].default_value = 0.0

    # Node Mix.004
    mix_004_2 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_004_2.name = "Mix.004"
    mix_004_2.blend_type = 'MIX'
    mix_004_2.clamp_factor = True
    mix_004_2.clamp_result = False
    mix_004_2.data_type = 'FLOAT'
    mix_004_2.factor_mode = 'UNIFORM'

    # Node Map Range.011
    map_range_011 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_011.name = "Map Range.011"
    map_range_011.clamp = False
    map_range_011.data_type = 'FLOAT'
    map_range_011.interpolation_type = 'LINEAR'
    # From Min
    map_range_011.inputs[1].default_value = -1.0
    # From Max
    map_range_011.inputs[2].default_value = 1.0
    # To Min
    map_range_011.inputs[3].default_value = 0.0
    # To Max
    map_range_011.inputs[4].default_value = 1.0

    # Node Mix.005
    mix_005_2 = _rr_hue_correct.nodes.new("ShaderNodeMix")
    mix_005_2.name = "Mix.005"
    mix_005_2.blend_type = 'MIX'
    mix_005_2.clamp_factor = True
    mix_005_2.clamp_result = False
    mix_005_2.data_type = 'FLOAT'
    mix_005_2.factor_mode = 'UNIFORM'
    # A_Float
    mix_005_2.inputs[2].default_value = 1.0

    # Node Math.031
    math_031_1 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_031_1.name = "Math.031"
    math_031_1.hide = True
    math_031_1.operation = 'ABSOLUTE'
    math_031_1.use_clamp = False

    # Node Reroute.062
    reroute_062_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_062_1.name = "Reroute.062"
    reroute_062_1.socket_idname = "NodeSocketFloatFactor"
    # Node Math.032
    math_032_2 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_032_2.name = "Math.032"
    math_032_2.hide = True
    math_032_2.operation = 'MULTIPLY'
    math_032_2.use_clamp = False

    # Node Math.012
    math_012_5 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_012_5.label = "/ 6"
    math_012_5.name = "Math.012"
    math_012_5.hide = True
    math_012_5.operation = 'DIVIDE'
    math_012_5.use_clamp = False
    # Value_001
    math_012_5.inputs[1].default_value = 6.0

    # Node Math.027
    math_027_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_027_4.label = "/ 6"
    math_027_4.name = "Math.027"
    math_027_4.hide = True
    math_027_4.operation = 'DIVIDE'
    math_027_4.use_clamp = False
    # Value_001
    math_027_4.inputs[1].default_value = 6.0

    # Node Math.017
    math_017_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_017_4.label = "*2"
    math_017_4.name = "Math.017"
    math_017_4.hide = True
    math_017_4.operation = 'MULTIPLY'
    math_017_4.use_clamp = False
    # Value_001
    math_017_4.inputs[1].default_value = 2.0

    # Node Math.018
    math_018_3 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_018_3.label = "-1"
    math_018_3.name = "Math.018"
    math_018_3.hide = True
    math_018_3.operation = 'SUBTRACT'
    math_018_3.use_clamp = False
    # Value_001
    math_018_3.inputs[1].default_value = 1.0

    # Node Math.028
    math_028_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_028_4.label = "/ 6"
    math_028_4.name = "Math.028"
    math_028_4.hide = True
    math_028_4.operation = 'DIVIDE'
    math_028_4.use_clamp = False
    # Value_001
    math_028_4.inputs[1].default_value = 6.0

    # Node Math.019
    math_019_3 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_019_3.label = "*2"
    math_019_3.name = "Math.019"
    math_019_3.hide = True
    math_019_3.operation = 'MULTIPLY'
    math_019_3.use_clamp = False
    # Value_001
    math_019_3.inputs[1].default_value = 2.0

    # Node Math.020
    math_020_3 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_020_3.label = "-1"
    math_020_3.name = "Math.020"
    math_020_3.hide = True
    math_020_3.operation = 'SUBTRACT'
    math_020_3.use_clamp = False
    # Value_001
    math_020_3.inputs[1].default_value = 1.0

    # Node Math.033
    math_033_1 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_033_1.label = "/ 6"
    math_033_1.name = "Math.033"
    math_033_1.hide = True
    math_033_1.operation = 'DIVIDE'
    math_033_1.use_clamp = False
    # Value_001
    math_033_1.inputs[1].default_value = 6.0

    # Node Math.021
    math_021_3 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_021_3.label = "*2"
    math_021_3.name = "Math.021"
    math_021_3.hide = True
    math_021_3.operation = 'MULTIPLY'
    math_021_3.use_clamp = False
    # Value_001
    math_021_3.inputs[1].default_value = 2.0

    # Node Math.022
    math_022_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_022_4.label = "-1"
    math_022_4.name = "Math.022"
    math_022_4.hide = True
    math_022_4.operation = 'SUBTRACT'
    math_022_4.use_clamp = False
    # Value_001
    math_022_4.inputs[1].default_value = 1.0

    # Node Math.034
    math_034_1 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_034_1.label = "/ 6"
    math_034_1.name = "Math.034"
    math_034_1.hide = True
    math_034_1.operation = 'DIVIDE'
    math_034_1.use_clamp = False
    # Value_001
    math_034_1.inputs[1].default_value = 6.0

    # Node Math.023
    math_023_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_023_4.label = "*2"
    math_023_4.name = "Math.023"
    math_023_4.hide = True
    math_023_4.operation = 'MULTIPLY'
    math_023_4.use_clamp = False
    # Value_001
    math_023_4.inputs[1].default_value = 2.0

    # Node Math.024
    math_024_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_024_4.label = "-1"
    math_024_4.name = "Math.024"
    math_024_4.hide = True
    math_024_4.operation = 'SUBTRACT'
    math_024_4.use_clamp = False
    # Value_001
    math_024_4.inputs[1].default_value = 1.0

    # Node Math.035
    math_035_1 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_035_1.label = "/ 6"
    math_035_1.name = "Math.035"
    math_035_1.hide = True
    math_035_1.operation = 'DIVIDE'
    math_035_1.use_clamp = False
    # Value_001
    math_035_1.inputs[1].default_value = 6.0

    # Node Math.025
    math_025_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_025_4.label = "*2"
    math_025_4.name = "Math.025"
    math_025_4.hide = True
    math_025_4.operation = 'MULTIPLY'
    math_025_4.use_clamp = False
    # Value_001
    math_025_4.inputs[1].default_value = 2.0

    # Node Math.026
    math_026_4 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_026_4.label = "-1"
    math_026_4.name = "Math.026"
    math_026_4.hide = True
    math_026_4.operation = 'SUBTRACT'
    math_026_4.use_clamp = False
    # Value_001
    math_026_4.inputs[1].default_value = 1.0

    # Node Math.036
    math_036_1 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_036_1.label = "/ 6"
    math_036_1.name = "Math.036"
    math_036_1.hide = True
    math_036_1.operation = 'DIVIDE'
    math_036_1.use_clamp = False
    # Value_001
    math_036_1.inputs[1].default_value = 6.0

    # Node Math.037
    math_037 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_037.label = "Halve"
    math_037.name = "Math.037"
    math_037.hide = True
    math_037.operation = 'MULTIPLY'
    math_037.use_clamp = False
    # Value_001
    math_037.inputs[1].default_value = 0.5

    # Node Math.038
    math_038 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_038.label = "Halve"
    math_038.name = "Math.038"
    math_038.hide = True
    math_038.operation = 'MULTIPLY'
    math_038.use_clamp = False
    # Value_001
    math_038.inputs[1].default_value = 0.5

    # Node Math.039
    math_039 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_039.label = "Halve"
    math_039.name = "Math.039"
    math_039.hide = True
    math_039.operation = 'MULTIPLY'
    math_039.use_clamp = False
    # Value_001
    math_039.inputs[1].default_value = 0.5

    # Node Math.040
    math_040 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_040.label = "Halve"
    math_040.name = "Math.040"
    math_040.hide = True
    math_040.operation = 'MULTIPLY'
    math_040.use_clamp = False
    # Value_001
    math_040.inputs[1].default_value = 0.5

    # Node Math.041
    math_041 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_041.label = "Halve"
    math_041.name = "Math.041"
    math_041.hide = True
    math_041.operation = 'MULTIPLY'
    math_041.use_clamp = False
    # Value_001
    math_041.inputs[1].default_value = 0.5

    # Node Math.042
    math_042 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_042.label = "Halve"
    math_042.name = "Math.042"
    math_042.hide = True
    math_042.operation = 'MULTIPLY'
    math_042.use_clamp = False
    # Value_001
    math_042.inputs[1].default_value = 0.5

    # Node Math.043
    math_043 = _rr_hue_correct.nodes.new("ShaderNodeMath")
    math_043.label = "Halve"
    math_043.name = "Math.043"
    math_043.hide = True
    math_043.operation = 'MULTIPLY'
    math_043.use_clamp = False
    # Value_001
    math_043.inputs[1].default_value = 0.5

    # Node Reroute.007
    reroute_007_3 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_007_3.name = "Reroute.007"
    reroute_007_3.socket_idname = "NodeSocketFloat"
    # Node Map Range.012
    map_range_012_1 = _rr_hue_correct.nodes.new("ShaderNodeMapRange")
    map_range_012_1.name = "Map Range.012"
    map_range_012_1.clamp = True
    map_range_012_1.data_type = 'FLOAT'
    map_range_012_1.interpolation_type = 'SMOOTHERSTEP'
    # From Min
    map_range_012_1.inputs[1].default_value = 0.0
    # From Max
    map_range_012_1.inputs[2].default_value = 0.10000000149011612
    # To Min
    map_range_012_1.inputs[3].default_value = 0.0
    # To Max
    map_range_012_1.inputs[4].default_value = 1.0

    # Node Reroute.018
    reroute_018_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_018_1.name = "Reroute.018"
    reroute_018_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.026
    reroute_026_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_026_1.name = "Reroute.026"
    reroute_026_1.socket_idname = "NodeSocketFloat"
    # Node Reroute.027
    reroute_027_1 = _rr_hue_correct.nodes.new("NodeReroute")
    reroute_027_1.name = "Reroute.027"
    reroute_027_1.socket_idname = "NodeSocketFloat"
    # Set parents
    group_input_001_7.parent = frame_13
    math_001_16.parent = frame_13
    reroute_001_9.parent = frame_13
    reroute_002_9.parent = frame_13
    group_input_002_4.parent = frame_001_10
    reroute_004_6.parent = frame_001_10
    clamp_1.parent = frame_001_10
    group_input_003_5.parent = frame_002_9
    mix_001_11.parent = frame_003_7
    group_input_004_5.parent = frame_003_7
    reroute_008_2.parent = frame_002_9
    reroute_009_2.parent = frame_002_9
    reroute_010_2.parent = frame_002_9
    reroute_011_2.parent = frame_002_9
    _srgb_to_lab_1.parent = frame_002_9
    _lab_to_srgb_1.parent = frame_002_9
    reroute_013_2.parent = frame_002_9
    reroute_014_1.parent = frame_002_9
    _lab_adjustments_001_1.parent = frame_002_9
    _lab_adjustments_002_1.parent = frame_002_9
    _lab_adjustments_003_1.parent = frame_002_9
    _lab_adjustments_004_1.parent = frame_002_9
    _lab_adjustments_005_1.parent = frame_002_9
    _lab_adjustments_006_1.parent = frame_002_9
    _lab_adjustments_007_1.parent = frame_002_9
    switch_9.parent = frame_003_7
    reroute_015_1.parent = frame_003_7
    math_20.parent = frame_003_7
    math_002_14.parent = frame_003_7
    switch_001_1.parent = frame_003_7
    reroute_016_1.parent = frame_003_7
    group_009_1.parent = frame_001_10
    group_010_1.parent = frame_001_10
    group_011_1.parent = frame_001_10
    group_012_1.parent = frame_001_10
    group_013_1.parent = frame_001_10
    group_014_1.parent = frame_001_10
    group_015_1.parent = frame_001_10
    reroute_005_8.parent = frame_001_10
    group_025_1.parent = frame_13
    group_026_1.parent = frame_13
    group_027_1.parent = frame_13
    group_028_1.parent = frame_13
    group_029_1.parent = frame_13
    group_030_1.parent = frame_13
    group_031_1.parent = frame_13
    map_range_14.parent = frame_002_9
    map_range_001_13.parent = frame_002_9
    map_range_002_10.parent = frame_002_9
    map_range_003_8.parent = frame_002_9
    map_range_004_6.parent = frame_002_9
    map_range_005_6.parent = frame_002_9
    map_range_006_2.parent = frame_002_9
    separate_color_004_2.parent = frame_002_9
    combine_color_001_2.parent = frame_002_9
    clamp_001_1.parent = frame_002_9
    reroute_028_1.parent = frame_002_9
    reroute_029_1.parent = frame_002_9
    reroute_030_1.parent = frame_002_9
    reroute_031_1.parent = frame_002_9
    reroute_032_1.parent = frame_002_9
    reroute_034_1.parent = frame_002_9
    separate_color_002_2.parent = frame_13
    separate_color_003_3.parent = frame_001_10
    reroute_012_2.parent = frame_13
    reroute_035_1.parent = frame_13
    reroute_036_1.parent = frame_13
    reroute_037_1.parent = frame_13
    reroute_038_1.parent = frame_13
    reroute_039_1.parent = frame_13
    reroute_040_1.parent = frame_13
    reroute_041_1.parent = frame_13
    reroute_042_1.parent = frame_13
    reroute_043_1.parent = frame_13
    reroute_044_1.parent = frame_13
    reroute_045_1.parent = frame_13
    reroute_046_1.parent = frame_13
    reroute_047_1.parent = frame_13
    reroute_017_1.parent = frame_002_9
    reroute_048_1.parent = frame_002_9
    separate_color_006_1.parent = frame_004_6
    combine_color_002_2.parent = frame_004_6
    group_input_006_1.parent = frame_004_6
    group_033_1.parent = frame_004_6
    group_034_1.parent = frame_004_6
    group_035_1.parent = frame_004_6
    group_036_1.parent = frame_004_6
    group_037_1.parent = frame_004_6
    group_038_1.parent = frame_004_6
    group_039_1.parent = frame_004_6
    reroute_049_1.parent = frame_004_6
    reroute_050_1.parent = frame_004_6
    mix_16.parent = frame_003_7
    reroute_051_1.parent = frame_003_7
    reroute_052_1.parent = frame_003_7
    reroute_053_1.parent = frame_003_7
    reroute_054_1.parent = frame_003_7
    math_005_11.parent = frame_004_6
    math_006_10.parent = frame_004_6
    math_007_10.parent = frame_004_6
    math_008_9.parent = frame_004_6
    math_009_8.parent = frame_004_6
    math_010_6.parent = frame_004_6
    math_011_6.parent = frame_004_6
    math_013_4.parent = frame_13
    math_014_4.parent = frame_13
    math_015_4.parent = frame_13
    math_016_4.parent = frame_13
    reroute_057_1.parent = frame_003_7
    reroute_058_1.parent = frame_003_7
    separate_color_007_1.parent = frame_003_7
    math_029_3.parent = frame_003_7
    map_range_008_1.parent = frame_003_7
    mix_002_5.parent = frame_003_7
    map_range_009_1.parent = frame_003_7
    mix_003_2.parent = frame_003_7
    math_030_2.parent = frame_003_7
    reroute_061_1.parent = frame_003_7
    map_range_010.parent = frame_003_7
    mix_004_2.parent = frame_003_7
    map_range_011.parent = frame_003_7
    mix_005_2.parent = frame_003_7
    math_031_1.parent = frame_003_7
    reroute_062_1.parent = frame_003_7
    math_032_2.parent = frame_003_7
    math_012_5.parent = frame_13
    math_027_4.parent = frame_13
    math_017_4.parent = frame_13
    math_018_3.parent = frame_13
    math_028_4.parent = frame_13
    math_019_3.parent = frame_13
    math_020_3.parent = frame_13
    math_033_1.parent = frame_13
    math_021_3.parent = frame_13
    math_022_4.parent = frame_13
    math_034_1.parent = frame_13
    math_023_4.parent = frame_13
    math_024_4.parent = frame_13
    math_035_1.parent = frame_13
    math_025_4.parent = frame_13
    math_026_4.parent = frame_13
    math_036_1.parent = frame_13
    math_037.parent = frame_004_6
    math_038.parent = frame_004_6
    math_039.parent = frame_004_6
    math_040.parent = frame_004_6
    math_041.parent = frame_004_6
    math_042.parent = frame_004_6
    math_043.parent = frame_004_6
    reroute_026_1.parent = frame_13
    reroute_027_1.parent = frame_13

    # Set locations
    group_output_25.location = (6077.283203125, 4.011042594909668)
    separate_color_7.location = (-1467.9178466796875, 21.059410095214844)
    group_input_22.location = (-2649.806396484375, -625.0185546875)
    hue_correct_2.location = (-1121.0526123046875, 147.24240112304688)
    separate_color_001_4.location = (2469.36865234375, -666.8716430664062)
    group_input_001_7.location = (29.217697143554688, -653.3338623046875)
    combine_color_8.location = (2797.526611328125, -578.9133911132812)
    group_4.location = (-1596.087646484375, -1818.707763671875)
    group_001_1.location = (-1595.2578125, -2030.882568359375)
    group_002_1.location = (-1597.0523681640625, -2241.424072265625)
    group_004_1.location = (-1593.0517578125, -974.7217407226562)
    group_005_1.location = (-1594.8626708984375, -1183.8515625)
    group_006_1.location = (-1594.8626708984375, -1393.431884765625)
    group_007_1.location = (-1594.8626708984375, -1606.4842529296875)
    math_001_16.location = (1029.7850341796875, -35.6751708984375)
    reroute_001_9.location = (966.153076171875, -141.487548828125)
    reroute_002_9.location = (966.153076171875, -1565.58740234375)
    frame_13.location = (-105.4800033569336, -777.76806640625)
    group_input_002_4.location = (29.26708984375, -601.2550048828125)
    reroute_004_6.location = (888.6751708984375, -117.60260009765625)
    frame_001_10.location = (1523.8800048828125, -807.2880859375)
    reroute_15.location = (1555.673828125, -647.1904296875)
    clamp_1.location = (934.9837646484375, -35.77325439453125)
    group_input_003_5.location = (334.887939453125, -558.880859375)
    mix_001_11.location = (452.5791015625, -1089.77294921875)
    group_input_004_5.location = (28.89892578125, -995.55322265625)
    reroute_008_2.location = (1210.2086181640625, -1598.7896728515625)
    reroute_009_2.location = (1236.9703369140625, -1621.34033203125)
    reroute_010_2.location = (1209.5509033203125, -144.183349609375)
    reroute_011_2.location = (1237.5985107421875, -159.55419921875)
    frame_002_9.location = (1126.4400634765625, 1508.9520263671875)
    _srgb_to_lab_1.location = (29.1453857421875, -85.7353515625)
    _lab_to_srgb_1.location = (1380.5804443359375, -35.6275634765625)
    reroute_013_2.location = (677.4808349609375, -158.562255859375)
    reroute_014_1.location = (680.9002685546875, -137.6533203125)
    _lab_adjustments_001_1.location = (983.9708251953125, -228.5155029296875)
    _lab_adjustments_002_1.location = (981.8160400390625, -456.5684814453125)
    _lab_adjustments_003_1.location = (980.0245361328125, -684.2100219726562)
    _lab_adjustments_004_1.location = (977.3367919921875, -906.4742431640625)
    _lab_adjustments_005_1.location = (973.7530517578125, -1133.2197265625)
    _lab_adjustments_006_1.location = (971.9613037109375, -1353.691650390625)
    _lab_adjustments_007_1.location = (964.7943115234375, -1563.4090576171875)
    switch_9.location = (715.1494140625, -1219.148193359375)
    reroute_015_1.location = (240.16943359375, -1316.50537109375)
    math_20.location = (453.3759765625, -909.0106811523438)
    math_002_14.location = (719.40234375, -940.956787109375)
    switch_001_1.location = (975.02001953125, -1265.68359375)
    reroute_016_1.location = (242.82861328125, -1372.40185546875)
    frame_003_7.location = (3656.52001953125, 1009.27197265625)
    group_009_1.location = (675.1837158203125, -134.75494384765625)
    group_010_1.location = (672.0421142578125, -339.0260009765625)
    group_011_1.location = (669.7574462890625, -545.4688720703125)
    group_012_1.location = (671.5494384765625, -755.2056884765625)
    group_013_1.location = (667.0692138671875, -973.9056396484375)
    group_014_1.location = (666.1734619140625, -1189.020263671875)
    group_015_1.location = (665.2774658203125, -1393.379638671875)
    reroute_005_8.location = (871.5428466796875, -1425.788818359375)
    group_025_1.location = (717.7479248046875, -256.726806640625)
    group_026_1.location = (717.7479248046875, -463.5909423828125)
    group_027_1.location = (717.7479248046875, -677.281005859375)
    group_028_1.location = (717.7479248046875, -888.0574951171875)
    group_029_1.location = (717.7479248046875, -1101.74853515625)
    group_030_1.location = (717.7479248046875, -1313.497314453125)
    group_031_1.location = (717.7479248046875, -1533.016357421875)
    reroute_003_8.location = (-1542.1016845703125, -124.68637084960938)
    map_range_14.location = (769.447998046875, -454.578369140625)
    map_range_001_13.location = (774.07275390625, -382.04296875)
    map_range_002_10.location = (802.2659912109375, -838.1699829101562)
    map_range_003_8.location = (798.3795166015625, -1063.5697021484375)
    map_range_004_6.location = (801.4525146484375, -1291.884521484375)
    map_range_005_6.location = (791.2677001953125, -1508.5406494140625)
    map_range_006_2.location = (794.756103515625, -1716.4530029296875)
    separate_color_004_2.location = (1704.2757568359375, -1565.1275634765625)
    combine_color_001_2.location = (2080.54248046875, -1556.6385498046875)
    clamp_001_1.location = (1901.0123291015625, -1570.9063720703125)
    reroute_019_1.location = (1205.2760009765625, -1014.9318237304688)
    reroute_020_1.location = (1388.5252685546875, -2069.8154296875)
    reroute_021_1.location = (1437.930419921875, -2276.517822265625)
    reroute_022_1.location = (1343.8963623046875, -1855.9095458984375)
    reroute_023_1.location = (1249.104736328125, -1221.211181640625)
    reroute_024_1.location = (1285.391357421875, -1429.0186767578125)
    reroute_025_1.location = (1313.8907470703125, -1639.9617919921875)
    reroute_028_1.location = (78.8359375, -338.501220703125)
    reroute_029_1.location = (126.1531982421875, -557.9124145507812)
    reroute_030_1.location = (158.9512939453125, -788.8140258789062)
    reroute_031_1.location = (187.45068359375, -1012.3154907226562)
    reroute_032_1.location = (217.456298828125, -1231.4945068359375)
    reroute_033_1.location = (1388.5252685546875, 51.66729736328125)
    reroute_034_1.location = (311.4903564453125, -1664.05712890625)
    group_input_005_4.location = (-2121.70166015625, -1473.614501953125)
    separate_color_002_2.location = (257.1065673828125, -291.7899169921875)
    separate_color_003_3.location = (293.6646728515625, -247.0855712890625)
    reroute_006_3.location = (-21.84799575805664, -748.2371826171875)
    separate_color_005_1.location = (-2349.432861328125, -744.0811767578125)
    reroute_012_2.location = (630.1240844726562, -251.7523193359375)
    reroute_035_1.location = (630.1240844726562, -647.9146728515625)
    reroute_036_1.location = (630.1240844726562, -883.6785888671875)
    reroute_037_1.location = (630.1240844726562, -1285.90185546875)
    reroute_038_1.location = (630.1240844726562, -461.0186767578125)
    reroute_039_1.location = (630.1240844726562, -860.9820556640625)
    reroute_040_1.location = (630.1240844726562, -1519.01806640625)
    reroute_041_1.location = (630.1240844726562, -438.4371337890625)
    reroute_042_1.location = (630.1240844726562, -229.64593505859375)
    reroute_043_1.location = (630.1240844726562, -1496.059814453125)
    reroute_044_1.location = (630.1240844726562, -1308.59375)
    reroute_045_1.location = (630.1240844726562, -1096.369384765625)
    reroute_046_1.location = (630.1240844726562, -670.5770263671875)
    reroute_047_1.location = (630.1240844726562, -1073.47607421875)
    reroute_017_1.location = (1587.5445556640625, -1704.732177734375)
    reroute_048_1.location = (1586.8851318359375, -70.3468017578125)
    separate_color_006_1.location = (137.758056640625, -71.7537841796875)
    combine_color_002_2.location = (886.786865234375, -35.9990234375)
    group_input_006_1.location = (28.863525390625, -773.0697021484375)
    group_033_1.location = (564.9618530273438, -357.52685546875)
    group_034_1.location = (564.9618530273438, -564.3909912109375)
    group_035_1.location = (564.9618530273438, -778.0810546875)
    group_036_1.location = (564.9618530273438, -988.8575439453125)
    group_037_1.location = (564.9618530273438, -1202.548583984375)
    group_038_1.location = (564.9618530273438, -1414.29736328125)
    group_039_1.location = (564.9618530273438, -1633.81640625)
    frame_004_6.location = (-1245.239990234375, -676.968017578125)
    reroute_049_1.location = (843.0610961914062, -155.87921142578125)
    reroute_050_1.location = (841.079345703125, -1665.718505859375)
    mix_16.location = (2098.2138671875, -886.1282348632812)
    reroute_051_1.location = (904.46337890625, -827.8192138671875)
    reroute_052_1.location = (904.46337890625, -869.2824096679688)
    reroute_053_1.location = (455.93896484375, -829.5010375976562)
    reroute_054_1.location = (455.93896484375, -866.0440673828125)
    value_1.location = (-2116.966796875, -1393.484130859375)
    math_003_13.location = (-2111.7099609375, -1157.021728515625)
    math_004_12.location = (-2116.9482421875, -1219.907958984375)
    reroute_055_1.location = (-1923.2305908203125, -1390.0787353515625)
    map_range_007_1.location = (-2352.68701171875, -1220.70947265625)
    math_005_11.location = (393.106689453125, -1762.945556640625)
    math_006_10.location = (393.92431640625, -1544.87060546875)
    math_007_10.location = (384.84002685546875, -1332.4747314453125)
    math_008_9.location = (384.8399658203125, -1120.07861328125)
    math_009_8.location = (384.8399658203125, -909.9541015625)
    math_010_6.location = (384.8399658203125, -695.2862548828125)
    math_011_6.location = (384.8399658203125, -489.704833984375)
    math_013_4.location = (483.56195068359375, -1565.682373046875)
    math_014_4.location = (486.46234130859375, -1607.145751953125)
    math_015_4.location = (481.4731750488281, -1343.464599609375)
    math_016_4.location = (484.3736572265625, -1384.927734375)
    reroute_057_1.location = (455.93896484375, -764.0820922851562)
    reroute_058_1.location = (455.93896484375, -796.8670043945312)
    separate_color_007_1.location = (1030.537109375, -369.864990234375)
    math_029_3.location = (1867.4482421875, -820.9434204101562)
    map_range_008_1.location = (1278.36279296875, -294.0582275390625)
    mix_002_5.location = (1473.9560546875, -188.1470947265625)
    map_range_009_1.location = (1281.8779296875, -35.6666259765625)
    mix_003_2.location = (1656.703125, -105.5723876953125)
    math_030_2.location = (1477.25439453125, -109.29046630859375)
    reroute_061_1.location = (1186.6611328125, -121.5078125)
    map_range_010.location = (1278.36279296875, -751.8110961914062)
    mix_004_2.location = (1473.9560546875, -645.9000244140625)
    map_range_011.location = (1281.8779296875, -493.41943359375)
    mix_005_2.location = (1662.9833984375, -563.3251953125)
    math_031_1.location = (1478.1513671875, -563.453125)
    reroute_062_1.location = (1186.6611328125, -579.2606201171875)
    math_032_2.location = (1901.81591796875, -440.62615966796875)
    math_012_5.location = (484.5810241699219, -1648.578369140625)
    math_027_4.location = (484.5810241699219, -1430.96142578125)
    math_017_4.location = (481.4731750488281, -1134.9580078125)
    math_018_3.location = (484.3736572265625, -1176.42138671875)
    math_028_4.location = (484.5810241699219, -1222.4549560546875)
    math_019_3.location = (481.4731750488281, -931.2813720703125)
    math_020_3.location = (484.3736572265625, -972.74462890625)
    math_033_1.location = (484.5810241699219, -1018.7781982421875)
    math_021_3.location = (481.4731750488281, -719.291259765625)
    math_022_4.location = (484.3736572265625, -760.7545166015625)
    math_034_1.location = (484.5810241699219, -806.7882080078125)
    math_023_4.location = (481.4731750488281, -503.9752197265625)
    math_024_4.location = (484.3736572265625, -545.4384765625)
    math_035_1.location = (484.5810241699219, -591.47216796875)
    math_025_4.location = (489.2469787597656, -311.936279296875)
    math_026_4.location = (492.1474914550781, -353.3995361328125)
    math_036_1.location = (492.3548583984375, -399.433349609375)
    math_037.location = (384.8399658203125, -426.6136474609375)
    math_038.location = (384.8399658203125, -630.95556640625)
    math_039.location = (384.8399658203125, -845.4024658203125)
    math_040.location = (384.8399658203125, -1058.1654052734375)
    math_041.location = (384.8399658203125, -1269.2442626953125)
    math_042.location = (384.8399658203125, -1481.44580078125)
    math_043.location = (384.8399658203125, -1700.384033203125)
    reroute_007_3.location = (-1968.4185791015625, -1069.8162841796875)
    map_range_012_1.location = (-2350.541015625, -926.8952026367188)
    reroute_018_1.location = (-1968.4185791015625, -1093.6214599609375)
    reroute_026_1.location = (631.3870239257812, -282.42919921875)
    reroute_027_1.location = (489.4726867675781, -280.1646728515625)

    # Set dimensions
    group_output_25.width, group_output_25.height = 150.67941284179688, 100.0
    separate_color_7.width, separate_color_7.height = 140.0, 100.0
    group_input_22.width, group_input_22.height = 140.0, 100.0
    hue_correct_2.width, hue_correct_2.height = 360.844970703125, 100.0
    separate_color_001_4.width, separate_color_001_4.height = 140.0, 100.0
    group_input_001_7.width, group_input_001_7.height = 140.0, 100.0
    combine_color_8.width, combine_color_8.height = 140.0, 100.0
    group_4.width, group_4.height = 175.66017150878906, 100.0
    group_001_1.width, group_001_1.height = 175.66017150878906, 100.0
    group_002_1.width, group_002_1.height = 175.66017150878906, 100.0
    group_004_1.width, group_004_1.height = 175.66017150878906, 100.0
    group_005_1.width, group_005_1.height = 175.66017150878906, 100.0
    group_006_1.width, group_006_1.height = 175.66017150878906, 100.0
    group_007_1.width, group_007_1.height = 175.66017150878906, 100.0
    math_001_16.width, math_001_16.height = 140.0, 100.0
    reroute_001_9.width, reroute_001_9.height = 13.5, 100.0
    reroute_002_9.width, reroute_002_9.height = 13.5, 100.0
    frame_13.width, frame_13.height = 1199.1199951171875, 1716.672119140625
    group_input_002_4.width, group_input_002_4.height = 140.0, 100.0
    reroute_004_6.width, reroute_004_6.height = 13.5, 100.0
    frame_001_10.width, frame_001_10.height = 1104.0799560546875, 1576.991943359375
    reroute_15.width, reroute_15.height = 13.5, 100.0
    clamp_1.width, clamp_1.height = 140.0, 100.0
    group_input_003_5.width, group_input_003_5.height = 140.0, 100.0
    mix_001_11.width, mix_001_11.height = 140.0, 100.0
    group_input_004_5.width, group_input_004_5.height = 140.0, 100.0
    reroute_008_2.width, reroute_008_2.height = 13.5, 100.0
    reroute_009_2.width, reroute_009_2.height = 13.5, 100.0
    reroute_010_2.width, reroute_010_2.height = 13.5, 100.0
    reroute_011_2.width, reroute_011_2.height = 13.5, 100.0
    frame_002_9.width, frame_002_9.height = 2249.60009765625, 1789.39208984375
    _srgb_to_lab_1.width, _srgb_to_lab_1.height = 140.0, 100.0
    _lab_to_srgb_1.width, _lab_to_srgb_1.height = 140.0, 100.0
    reroute_013_2.width, reroute_013_2.height = 13.5, 100.0
    reroute_014_1.width, reroute_014_1.height = 13.5, 100.0
    _lab_adjustments_001_1.width, _lab_adjustments_001_1.height = 140.0, 100.0
    _lab_adjustments_002_1.width, _lab_adjustments_002_1.height = 140.0, 100.0
    _lab_adjustments_003_1.width, _lab_adjustments_003_1.height = 140.0, 100.0
    _lab_adjustments_004_1.width, _lab_adjustments_004_1.height = 140.0, 100.0
    _lab_adjustments_005_1.width, _lab_adjustments_005_1.height = 140.0, 100.0
    _lab_adjustments_006_1.width, _lab_adjustments_006_1.height = 140.0, 100.0
    _lab_adjustments_007_1.width, _lab_adjustments_007_1.height = 140.0, 100.0
    switch_9.width, switch_9.height = 140.0, 100.0
    reroute_015_1.width, reroute_015_1.height = 13.5, 100.0
    math_20.width, math_20.height = 140.0, 100.0
    math_002_14.width, math_002_14.height = 140.0, 100.0
    switch_001_1.width, switch_001_1.height = 140.0, 100.0
    reroute_016_1.width, reroute_016_1.height = 13.5, 100.0
    frame_003_7.width, frame_003_7.height = 2267.60009765625, 1407.7919921875
    group_009_1.width, group_009_1.height = 159.940185546875, 100.0
    group_010_1.width, group_010_1.height = 159.940185546875, 100.0
    group_011_1.width, group_011_1.height = 159.940185546875, 100.0
    group_012_1.width, group_012_1.height = 159.940185546875, 100.0
    group_013_1.width, group_013_1.height = 159.940185546875, 100.0
    group_014_1.width, group_014_1.height = 159.940185546875, 100.0
    group_015_1.width, group_015_1.height = 159.940185546875, 100.0
    reroute_005_8.width, reroute_005_8.height = 13.5, 100.0
    group_025_1.width, group_025_1.height = 159.940185546875, 100.0
    group_026_1.width, group_026_1.height = 159.940185546875, 100.0
    group_027_1.width, group_027_1.height = 159.940185546875, 100.0
    group_028_1.width, group_028_1.height = 159.940185546875, 100.0
    group_029_1.width, group_029_1.height = 159.940185546875, 100.0
    group_030_1.width, group_030_1.height = 159.940185546875, 100.0
    group_031_1.width, group_031_1.height = 159.940185546875, 100.0
    reroute_003_8.width, reroute_003_8.height = 13.5, 100.0
    map_range_14.width, map_range_14.height = 140.0, 100.0
    map_range_001_13.width, map_range_001_13.height = 140.0, 100.0
    map_range_002_10.width, map_range_002_10.height = 140.0, 100.0
    map_range_003_8.width, map_range_003_8.height = 140.0, 100.0
    map_range_004_6.width, map_range_004_6.height = 140.0, 100.0
    map_range_005_6.width, map_range_005_6.height = 140.0, 100.0
    map_range_006_2.width, map_range_006_2.height = 140.0, 100.0
    separate_color_004_2.width, separate_color_004_2.height = 140.0, 100.0
    combine_color_001_2.width, combine_color_001_2.height = 140.0, 100.0
    clamp_001_1.width, clamp_001_1.height = 140.0, 100.0
    reroute_019_1.width, reroute_019_1.height = 13.5, 100.0
    reroute_020_1.width, reroute_020_1.height = 13.5, 100.0
    reroute_021_1.width, reroute_021_1.height = 13.5, 100.0
    reroute_022_1.width, reroute_022_1.height = 13.5, 100.0
    reroute_023_1.width, reroute_023_1.height = 13.5, 100.0
    reroute_024_1.width, reroute_024_1.height = 13.5, 100.0
    reroute_025_1.width, reroute_025_1.height = 13.5, 100.0
    reroute_028_1.width, reroute_028_1.height = 13.5, 100.0
    reroute_029_1.width, reroute_029_1.height = 13.5, 100.0
    reroute_030_1.width, reroute_030_1.height = 13.5, 100.0
    reroute_031_1.width, reroute_031_1.height = 13.5, 100.0
    reroute_032_1.width, reroute_032_1.height = 13.5, 100.0
    reroute_033_1.width, reroute_033_1.height = 13.5, 100.0
    reroute_034_1.width, reroute_034_1.height = 13.5, 100.0
    group_input_005_4.width, group_input_005_4.height = 140.0, 100.0
    separate_color_002_2.width, separate_color_002_2.height = 140.0, 100.0
    separate_color_003_3.width, separate_color_003_3.height = 140.0, 100.0
    reroute_006_3.width, reroute_006_3.height = 13.5, 100.0
    separate_color_005_1.width, separate_color_005_1.height = 140.0, 100.0
    reroute_012_2.width, reroute_012_2.height = 13.5, 100.0
    reroute_035_1.width, reroute_035_1.height = 13.5, 100.0
    reroute_036_1.width, reroute_036_1.height = 13.5, 100.0
    reroute_037_1.width, reroute_037_1.height = 13.5, 100.0
    reroute_038_1.width, reroute_038_1.height = 13.5, 100.0
    reroute_039_1.width, reroute_039_1.height = 13.5, 100.0
    reroute_040_1.width, reroute_040_1.height = 13.5, 100.0
    reroute_041_1.width, reroute_041_1.height = 13.5, 100.0
    reroute_042_1.width, reroute_042_1.height = 13.5, 100.0
    reroute_043_1.width, reroute_043_1.height = 13.5, 100.0
    reroute_044_1.width, reroute_044_1.height = 13.5, 100.0
    reroute_045_1.width, reroute_045_1.height = 13.5, 100.0
    reroute_046_1.width, reroute_046_1.height = 13.5, 100.0
    reroute_047_1.width, reroute_047_1.height = 13.5, 100.0
    reroute_017_1.width, reroute_017_1.height = 13.5, 100.0
    reroute_048_1.width, reroute_048_1.height = 13.5, 100.0
    separate_color_006_1.width, separate_color_006_1.height = 140.0, 100.0
    combine_color_002_2.width, combine_color_002_2.height = 140.0, 100.0
    group_input_006_1.width, group_input_006_1.height = 140.0, 100.0
    group_033_1.width, group_033_1.height = 159.940185546875, 100.0
    group_034_1.width, group_034_1.height = 159.940185546875, 100.0
    group_035_1.width, group_035_1.height = 159.940185546875, 100.0
    group_036_1.width, group_036_1.height = 159.940185546875, 100.0
    group_037_1.width, group_037_1.height = 159.940185546875, 100.0
    group_038_1.width, group_038_1.height = 159.940185546875, 100.0
    group_039_1.width, group_039_1.height = 159.940185546875, 100.0
    frame_004_6.width, frame_004_6.height = 1055.8399658203125, 1817.47216796875
    reroute_049_1.width, reroute_049_1.height = 13.5, 100.0
    reroute_050_1.width, reroute_050_1.height = 13.5, 100.0
    mix_16.width, mix_16.height = 140.0, 100.0
    reroute_051_1.width, reroute_051_1.height = 13.5, 100.0
    reroute_052_1.width, reroute_052_1.height = 13.5, 100.0
    reroute_053_1.width, reroute_053_1.height = 13.5, 100.0
    reroute_054_1.width, reroute_054_1.height = 13.5, 100.0
    value_1.width, value_1.height = 140.0, 100.0
    math_003_13.width, math_003_13.height = 140.0, 100.0
    math_004_12.width, math_004_12.height = 140.0, 100.0
    reroute_055_1.width, reroute_055_1.height = 13.5, 100.0
    map_range_007_1.width, map_range_007_1.height = 140.0, 100.0
    math_005_11.width, math_005_11.height = 140.0, 100.0
    math_006_10.width, math_006_10.height = 140.0, 100.0
    math_007_10.width, math_007_10.height = 140.0, 100.0
    math_008_9.width, math_008_9.height = 140.0, 100.0
    math_009_8.width, math_009_8.height = 140.0, 100.0
    math_010_6.width, math_010_6.height = 140.0, 100.0
    math_011_6.width, math_011_6.height = 140.0, 100.0
    math_013_4.width, math_013_4.height = 140.0, 100.0
    math_014_4.width, math_014_4.height = 140.0, 100.0
    math_015_4.width, math_015_4.height = 140.0, 100.0
    math_016_4.width, math_016_4.height = 140.0, 100.0
    reroute_057_1.width, reroute_057_1.height = 13.5, 100.0
    reroute_058_1.width, reroute_058_1.height = 13.5, 100.0
    separate_color_007_1.width, separate_color_007_1.height = 140.0, 100.0
    math_029_3.width, math_029_3.height = 140.0, 100.0
    map_range_008_1.width, map_range_008_1.height = 140.0, 100.0
    mix_002_5.width, mix_002_5.height = 140.0, 100.0
    map_range_009_1.width, map_range_009_1.height = 140.0, 100.0
    mix_003_2.width, mix_003_2.height = 140.0, 100.0
    math_030_2.width, math_030_2.height = 140.0, 100.0
    reroute_061_1.width, reroute_061_1.height = 13.5, 100.0
    map_range_010.width, map_range_010.height = 140.0, 100.0
    mix_004_2.width, mix_004_2.height = 140.0, 100.0
    map_range_011.width, map_range_011.height = 140.0, 100.0
    mix_005_2.width, mix_005_2.height = 140.0, 100.0
    math_031_1.width, math_031_1.height = 140.0, 100.0
    reroute_062_1.width, reroute_062_1.height = 13.5, 100.0
    math_032_2.width, math_032_2.height = 140.0, 100.0
    math_012_5.width, math_012_5.height = 140.0, 100.0
    math_027_4.width, math_027_4.height = 140.0, 100.0
    math_017_4.width, math_017_4.height = 140.0, 100.0
    math_018_3.width, math_018_3.height = 140.0, 100.0
    math_028_4.width, math_028_4.height = 140.0, 100.0
    math_019_3.width, math_019_3.height = 140.0, 100.0
    math_020_3.width, math_020_3.height = 140.0, 100.0
    math_033_1.width, math_033_1.height = 140.0, 100.0
    math_021_3.width, math_021_3.height = 140.0, 100.0
    math_022_4.width, math_022_4.height = 140.0, 100.0
    math_034_1.width, math_034_1.height = 140.0, 100.0
    math_023_4.width, math_023_4.height = 140.0, 100.0
    math_024_4.width, math_024_4.height = 140.0, 100.0
    math_035_1.width, math_035_1.height = 140.0, 100.0
    math_025_4.width, math_025_4.height = 140.0, 100.0
    math_026_4.width, math_026_4.height = 140.0, 100.0
    math_036_1.width, math_036_1.height = 140.0, 100.0
    math_037.width, math_037.height = 140.0, 100.0
    math_038.width, math_038.height = 140.0, 100.0
    math_039.width, math_039.height = 140.0, 100.0
    math_040.width, math_040.height = 140.0, 100.0
    math_041.width, math_041.height = 140.0, 100.0
    math_042.width, math_042.height = 140.0, 100.0
    math_043.width, math_043.height = 140.0, 100.0
    reroute_007_3.width, reroute_007_3.height = 13.5, 100.0
    map_range_012_1.width, map_range_012_1.height = 140.0, 100.0
    reroute_018_1.width, reroute_018_1.height = 13.5, 100.0
    reroute_026_1.width, reroute_026_1.height = 13.5, 100.0
    reroute_027_1.width, reroute_027_1.height = 13.5, 100.0

    # Initialize _rr_hue_correct links

    # separate_color_7.Green -> hue_correct_2.Fac
    _rr_hue_correct.links.new(separate_color_7.outputs[1], hue_correct_2.inputs[0])
    # separate_color_001_4.Blue -> combine_color_8.Blue
    _rr_hue_correct.links.new(separate_color_001_4.outputs[2], combine_color_8.inputs[2])
    # separate_color_001_4.Alpha -> combine_color_8.Alpha
    _rr_hue_correct.links.new(separate_color_001_4.outputs[3], combine_color_8.inputs[3])
    # reroute_15.Output -> combine_color_8.Red
    _rr_hue_correct.links.new(reroute_15.outputs[0], combine_color_8.inputs[0])
    # reroute_002_9.Output -> reroute_001_9.Input
    _rr_hue_correct.links.new(reroute_002_9.outputs[0], reroute_001_9.inputs[0])
    # math_001_16.Value -> reroute_15.Input
    _rr_hue_correct.links.new(math_001_16.outputs[0], reroute_15.inputs[0])
    # reroute_004_6.Output -> clamp_1.Value
    _rr_hue_correct.links.new(reroute_004_6.outputs[0], clamp_1.inputs[0])
    # reroute_001_9.Output -> math_001_16.Value
    _rr_hue_correct.links.new(reroute_001_9.outputs[0], math_001_16.inputs[0])
    # reroute_016_1.Output -> mix_001_11.A
    _rr_hue_correct.links.new(reroute_016_1.outputs[0], mix_001_11.inputs[6])
    # group_input_004_5.Perceptual -> mix_001_11.Factor
    _rr_hue_correct.links.new(group_input_004_5.outputs[3], mix_001_11.inputs[0])
    # reroute_008_2.Output -> reroute_010_2.Input
    _rr_hue_correct.links.new(reroute_008_2.outputs[0], reroute_010_2.inputs[0])
    # reroute_009_2.Output -> reroute_011_2.Input
    _rr_hue_correct.links.new(reroute_009_2.outputs[0], reroute_011_2.inputs[0])
    # _srgb_to_lab_1.L -> _lab_to_srgb_1.L
    _rr_hue_correct.links.new(_srgb_to_lab_1.outputs[0], _lab_to_srgb_1.inputs[0])
    # _srgb_to_lab_1.Alpha -> _lab_to_srgb_1.Alpha
    _rr_hue_correct.links.new(_srgb_to_lab_1.outputs[3], _lab_to_srgb_1.inputs[3])
    # _srgb_to_lab_1.B -> reroute_013_2.Input
    _rr_hue_correct.links.new(_srgb_to_lab_1.outputs[2], reroute_013_2.inputs[0])
    # _srgb_to_lab_1.A -> reroute_014_1.Input
    _rr_hue_correct.links.new(_srgb_to_lab_1.outputs[1], reroute_014_1.inputs[0])
    # group_input_003_5.Red Saturation -> _lab_adjustments_001_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[15], _lab_adjustments_001_1.inputs[4])
    # _lab_adjustments_001_1.A -> _lab_adjustments_002_1.A
    _rr_hue_correct.links.new(_lab_adjustments_001_1.outputs[0], _lab_adjustments_002_1.inputs[1])
    # _lab_adjustments_001_1.B -> _lab_adjustments_002_1.B
    _rr_hue_correct.links.new(_lab_adjustments_001_1.outputs[1], _lab_adjustments_002_1.inputs[2])
    # map_range_14.Result -> _lab_adjustments_002_1.Hue
    _rr_hue_correct.links.new(map_range_14.outputs[0], _lab_adjustments_002_1.inputs[3])
    # group_input_003_5.Orange Saturation -> _lab_adjustments_002_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[16], _lab_adjustments_002_1.inputs[4])
    # _lab_adjustments_002_1.A -> _lab_adjustments_003_1.A
    _rr_hue_correct.links.new(_lab_adjustments_002_1.outputs[0], _lab_adjustments_003_1.inputs[1])
    # _lab_adjustments_002_1.B -> _lab_adjustments_003_1.B
    _rr_hue_correct.links.new(_lab_adjustments_002_1.outputs[1], _lab_adjustments_003_1.inputs[2])
    # map_range_002_10.Result -> _lab_adjustments_003_1.Hue
    _rr_hue_correct.links.new(map_range_002_10.outputs[0], _lab_adjustments_003_1.inputs[3])
    # group_input_003_5.Yellow Saturation -> _lab_adjustments_003_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[17], _lab_adjustments_003_1.inputs[4])
    # _lab_adjustments_003_1.A -> _lab_adjustments_004_1.A
    _rr_hue_correct.links.new(_lab_adjustments_003_1.outputs[0], _lab_adjustments_004_1.inputs[1])
    # _lab_adjustments_003_1.B -> _lab_adjustments_004_1.B
    _rr_hue_correct.links.new(_lab_adjustments_003_1.outputs[1], _lab_adjustments_004_1.inputs[2])
    # map_range_003_8.Result -> _lab_adjustments_004_1.Hue
    _rr_hue_correct.links.new(map_range_003_8.outputs[0], _lab_adjustments_004_1.inputs[3])
    # group_input_003_5.Green Saturation -> _lab_adjustments_004_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[18], _lab_adjustments_004_1.inputs[4])
    # _lab_adjustments_004_1.A -> _lab_adjustments_005_1.A
    _rr_hue_correct.links.new(_lab_adjustments_004_1.outputs[0], _lab_adjustments_005_1.inputs[1])
    # _lab_adjustments_004_1.B -> _lab_adjustments_005_1.B
    _rr_hue_correct.links.new(_lab_adjustments_004_1.outputs[1], _lab_adjustments_005_1.inputs[2])
    # map_range_004_6.Result -> _lab_adjustments_005_1.Hue
    _rr_hue_correct.links.new(map_range_004_6.outputs[0], _lab_adjustments_005_1.inputs[3])
    # group_input_003_5.Teal Saturation -> _lab_adjustments_005_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[19], _lab_adjustments_005_1.inputs[4])
    # _lab_adjustments_005_1.A -> _lab_adjustments_006_1.A
    _rr_hue_correct.links.new(_lab_adjustments_005_1.outputs[0], _lab_adjustments_006_1.inputs[1])
    # _lab_adjustments_005_1.B -> _lab_adjustments_006_1.B
    _rr_hue_correct.links.new(_lab_adjustments_005_1.outputs[1], _lab_adjustments_006_1.inputs[2])
    # map_range_005_6.Result -> _lab_adjustments_006_1.Hue
    _rr_hue_correct.links.new(map_range_005_6.outputs[0], _lab_adjustments_006_1.inputs[3])
    # group_input_003_5.Blue Saturation -> _lab_adjustments_006_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[20], _lab_adjustments_006_1.inputs[4])
    # _lab_adjustments_006_1.A -> _lab_adjustments_007_1.A
    _rr_hue_correct.links.new(_lab_adjustments_006_1.outputs[0], _lab_adjustments_007_1.inputs[1])
    # _lab_adjustments_006_1.B -> _lab_adjustments_007_1.B
    _rr_hue_correct.links.new(_lab_adjustments_006_1.outputs[1], _lab_adjustments_007_1.inputs[2])
    # _lab_adjustments_007_1.A -> reroute_008_2.Input
    _rr_hue_correct.links.new(_lab_adjustments_007_1.outputs[0], reroute_008_2.inputs[0])
    # _lab_adjustments_007_1.B -> reroute_009_2.Input
    _rr_hue_correct.links.new(_lab_adjustments_007_1.outputs[1], reroute_009_2.inputs[0])
    # map_range_006_2.Result -> _lab_adjustments_007_1.Hue
    _rr_hue_correct.links.new(map_range_006_2.outputs[0], _lab_adjustments_007_1.inputs[3])
    # group_input_003_5.Pink Saturation -> _lab_adjustments_007_1.Chroma
    _rr_hue_correct.links.new(group_input_003_5.outputs[21], _lab_adjustments_007_1.inputs[4])
    # reroute_010_2.Output -> _lab_to_srgb_1.A
    _rr_hue_correct.links.new(reroute_010_2.outputs[0], _lab_to_srgb_1.inputs[1])
    # reroute_011_2.Output -> _lab_to_srgb_1.B
    _rr_hue_correct.links.new(reroute_011_2.outputs[0], _lab_to_srgb_1.inputs[2])
    # reroute_015_1.Output -> mix_001_11.B
    _rr_hue_correct.links.new(reroute_015_1.outputs[0], mix_001_11.inputs[7])
    # combine_color_001_2.Image -> reroute_015_1.Input
    _rr_hue_correct.links.new(combine_color_001_2.outputs[0], reroute_015_1.inputs[0])
    # group_input_004_5.Perceptual -> math_20.Value
    _rr_hue_correct.links.new(group_input_004_5.outputs[3], math_20.inputs[0])
    # math_20.Value -> switch_9.Switch
    _rr_hue_correct.links.new(math_20.outputs[0], switch_9.inputs[0])
    # mix_001_11.Result -> switch_9.Off
    _rr_hue_correct.links.new(mix_001_11.outputs[2], switch_9.inputs[1])
    # reroute_015_1.Output -> switch_9.On
    _rr_hue_correct.links.new(reroute_015_1.outputs[0], switch_9.inputs[2])
    # group_input_004_5.Perceptual -> math_002_14.Value
    _rr_hue_correct.links.new(group_input_004_5.outputs[3], math_002_14.inputs[0])
    # switch_9.Image -> switch_001_1.Off
    _rr_hue_correct.links.new(switch_9.outputs[0], switch_001_1.inputs[1])
    # reroute_016_1.Output -> switch_001_1.On
    _rr_hue_correct.links.new(reroute_016_1.outputs[0], switch_001_1.inputs[2])
    # math_002_14.Value -> switch_001_1.Switch
    _rr_hue_correct.links.new(math_002_14.outputs[0], switch_001_1.inputs[0])
    # combine_color_8.Image -> reroute_016_1.Input
    _rr_hue_correct.links.new(combine_color_8.outputs[0], reroute_016_1.inputs[0])
    # reroute_019_1.Output -> group_009_1.Factor
    _rr_hue_correct.links.new(reroute_019_1.outputs[0], group_009_1.inputs[0])
    # group_input_002_4.Red Saturation -> group_009_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[15], group_009_1.inputs[2])
    # reroute_023_1.Output -> group_010_1.Factor
    _rr_hue_correct.links.new(reroute_023_1.outputs[0], group_010_1.inputs[0])
    # group_009_1.Result -> group_010_1.Image
    _rr_hue_correct.links.new(group_009_1.outputs[0], group_010_1.inputs[1])
    # group_input_002_4.Orange Saturation -> group_010_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[16], group_010_1.inputs[2])
    # reroute_024_1.Output -> group_011_1.Factor
    _rr_hue_correct.links.new(reroute_024_1.outputs[0], group_011_1.inputs[0])
    # group_010_1.Result -> group_011_1.Image
    _rr_hue_correct.links.new(group_010_1.outputs[0], group_011_1.inputs[1])
    # group_input_002_4.Yellow Saturation -> group_011_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[17], group_011_1.inputs[2])
    # reroute_025_1.Output -> group_012_1.Factor
    _rr_hue_correct.links.new(reroute_025_1.outputs[0], group_012_1.inputs[0])
    # group_input_002_4.Green Saturation -> group_012_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[18], group_012_1.inputs[2])
    # group_011_1.Result -> group_012_1.Image
    _rr_hue_correct.links.new(group_011_1.outputs[0], group_012_1.inputs[1])
    # reroute_022_1.Output -> group_013_1.Factor
    _rr_hue_correct.links.new(reroute_022_1.outputs[0], group_013_1.inputs[0])
    # group_012_1.Result -> group_013_1.Image
    _rr_hue_correct.links.new(group_012_1.outputs[0], group_013_1.inputs[1])
    # group_input_002_4.Teal Saturation -> group_013_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[19], group_013_1.inputs[2])
    # reroute_020_1.Output -> group_014_1.Factor
    _rr_hue_correct.links.new(reroute_020_1.outputs[0], group_014_1.inputs[0])
    # group_013_1.Result -> group_014_1.Image
    _rr_hue_correct.links.new(group_013_1.outputs[0], group_014_1.inputs[1])
    # group_input_002_4.Blue Saturation -> group_014_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[20], group_014_1.inputs[2])
    # reroute_021_1.Output -> group_015_1.Factor
    _rr_hue_correct.links.new(reroute_021_1.outputs[0], group_015_1.inputs[0])
    # group_014_1.Result -> group_015_1.Image
    _rr_hue_correct.links.new(group_014_1.outputs[0], group_015_1.inputs[1])
    # group_input_002_4.Pink Saturation -> group_015_1.Multiply
    _rr_hue_correct.links.new(group_input_002_4.outputs[21], group_015_1.inputs[2])
    # reroute_005_8.Output -> reroute_004_6.Input
    _rr_hue_correct.links.new(reroute_005_8.outputs[0], reroute_004_6.inputs[0])
    # group_015_1.Result -> reroute_005_8.Input
    _rr_hue_correct.links.new(group_015_1.outputs[0], reroute_005_8.inputs[0])
    # group_025_1.Result -> group_026_1.Image
    _rr_hue_correct.links.new(group_025_1.outputs[0], group_026_1.inputs[1])
    # group_026_1.Result -> group_027_1.Image
    _rr_hue_correct.links.new(group_026_1.outputs[0], group_027_1.inputs[1])
    # group_027_1.Result -> group_028_1.Image
    _rr_hue_correct.links.new(group_027_1.outputs[0], group_028_1.inputs[1])
    # group_028_1.Result -> group_029_1.Image
    _rr_hue_correct.links.new(group_028_1.outputs[0], group_029_1.inputs[1])
    # group_029_1.Result -> group_030_1.Image
    _rr_hue_correct.links.new(group_029_1.outputs[0], group_030_1.inputs[1])
    # group_030_1.Result -> group_031_1.Image
    _rr_hue_correct.links.new(group_030_1.outputs[0], group_031_1.inputs[1])
    # group_031_1.Result -> reroute_002_9.Input
    _rr_hue_correct.links.new(group_031_1.outputs[0], reroute_002_9.inputs[0])
    # reroute_007_3.Output -> group_004_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_004_1.inputs[0])
    # reroute_007_3.Output -> group_005_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_005_1.inputs[0])
    # reroute_007_3.Output -> group_006_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_006_1.inputs[0])
    # reroute_007_3.Output -> group_007_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_007_1.inputs[0])
    # reroute_007_3.Output -> group_4.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_4.inputs[0])
    # reroute_007_3.Output -> group_001_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_001_1.inputs[0])
    # reroute_007_3.Output -> group_002_1.Image
    _rr_hue_correct.links.new(reroute_007_3.outputs[0], group_002_1.inputs[0])
    # mix_16.Result -> group_output_25.Image
    _rr_hue_correct.links.new(mix_16.outputs[2], group_output_25.inputs[0])
    # reroute_003_8.Output -> separate_color_7.Image
    _rr_hue_correct.links.new(reroute_003_8.outputs[0], separate_color_7.inputs[0])
    # reroute_003_8.Output -> hue_correct_2.Image
    _rr_hue_correct.links.new(reroute_003_8.outputs[0], hue_correct_2.inputs[1])
    # group_input_22.Input -> reroute_003_8.Input
    _rr_hue_correct.links.new(group_input_22.outputs[1], reroute_003_8.inputs[0])
    # reroute_006_3.Output -> separate_color_001_4.Image
    _rr_hue_correct.links.new(reroute_006_3.outputs[0], separate_color_001_4.inputs[0])
    # group_input_003_5.Orange Hue -> map_range_14.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[9], map_range_14.inputs[0])
    # group_input_003_5.Red Hue -> map_range_001_13.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[8], map_range_001_13.inputs[0])
    # map_range_001_13.Result -> _lab_adjustments_001_1.Hue
    _rr_hue_correct.links.new(map_range_001_13.outputs[0], _lab_adjustments_001_1.inputs[3])
    # group_input_003_5.Yellow Hue -> map_range_002_10.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[10], map_range_002_10.inputs[0])
    # group_input_003_5.Green Hue -> map_range_003_8.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[11], map_range_003_8.inputs[0])
    # group_input_003_5.Teal Hue -> map_range_004_6.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[12], map_range_004_6.inputs[0])
    # group_input_003_5.Blue Hue -> map_range_005_6.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[13], map_range_005_6.inputs[0])
    # group_input_003_5.Pink Hue -> map_range_006_2.Value
    _rr_hue_correct.links.new(group_input_003_5.outputs[14], map_range_006_2.inputs[0])
    # reroute_017_1.Output -> separate_color_004_2.Image
    _rr_hue_correct.links.new(reroute_017_1.outputs[0], separate_color_004_2.inputs[0])
    # separate_color_004_2.Red -> combine_color_001_2.Red
    _rr_hue_correct.links.new(separate_color_004_2.outputs[0], combine_color_001_2.inputs[0])
    # separate_color_004_2.Alpha -> combine_color_001_2.Alpha
    _rr_hue_correct.links.new(separate_color_004_2.outputs[3], combine_color_001_2.inputs[3])
    # separate_color_004_2.Green -> clamp_001_1.Value
    _rr_hue_correct.links.new(separate_color_004_2.outputs[1], clamp_001_1.inputs[0])
    # clamp_001_1.Result -> combine_color_001_2.Green
    _rr_hue_correct.links.new(clamp_001_1.outputs[0], combine_color_001_2.inputs[1])
    # group_input_005_4.Smoothing -> group_004_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_004_1.inputs[4])
    # group_input_005_4.Smoothing -> group_005_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_005_1.inputs[4])
    # group_input_005_4.Smoothing -> group_006_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_006_1.inputs[4])
    # group_input_005_4.Smoothing -> group_007_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_007_1.inputs[4])
    # group_input_005_4.Smoothing -> group_4.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_4.inputs[4])
    # group_input_005_4.Smoothing -> group_001_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_001_1.inputs[4])
    # group_input_005_4.Smoothing -> group_002_1.Smoothing
    _rr_hue_correct.links.new(group_input_005_4.outputs[5], group_002_1.inputs[4])
    # reroute_042_1.Output -> reroute_019_1.Input
    _rr_hue_correct.links.new(reroute_042_1.outputs[0], reroute_019_1.inputs[0])
    # reroute_037_1.Output -> reroute_020_1.Input
    _rr_hue_correct.links.new(reroute_037_1.outputs[0], reroute_020_1.inputs[0])
    # reroute_043_1.Output -> reroute_021_1.Input
    _rr_hue_correct.links.new(reroute_043_1.outputs[0], reroute_021_1.inputs[0])
    # reroute_047_1.Output -> reroute_022_1.Input
    _rr_hue_correct.links.new(reroute_047_1.outputs[0], reroute_022_1.inputs[0])
    # reroute_041_1.Output -> reroute_023_1.Input
    _rr_hue_correct.links.new(reroute_041_1.outputs[0], reroute_023_1.inputs[0])
    # reroute_035_1.Output -> reroute_024_1.Input
    _rr_hue_correct.links.new(reroute_035_1.outputs[0], reroute_024_1.inputs[0])
    # reroute_039_1.Output -> reroute_025_1.Input
    _rr_hue_correct.links.new(reroute_039_1.outputs[0], reroute_025_1.inputs[0])
    # reroute_028_1.Output -> _lab_adjustments_001_1.Factor
    _rr_hue_correct.links.new(reroute_028_1.outputs[0], _lab_adjustments_001_1.inputs[0])
    # reroute_019_1.Output -> reroute_028_1.Input
    _rr_hue_correct.links.new(reroute_019_1.outputs[0], reroute_028_1.inputs[0])
    # reroute_029_1.Output -> _lab_adjustments_002_1.Factor
    _rr_hue_correct.links.new(reroute_029_1.outputs[0], _lab_adjustments_002_1.inputs[0])
    # reroute_030_1.Output -> _lab_adjustments_003_1.Factor
    _rr_hue_correct.links.new(reroute_030_1.outputs[0], _lab_adjustments_003_1.inputs[0])
    # reroute_031_1.Output -> _lab_adjustments_004_1.Factor
    _rr_hue_correct.links.new(reroute_031_1.outputs[0], _lab_adjustments_004_1.inputs[0])
    # reroute_032_1.Output -> _lab_adjustments_005_1.Factor
    _rr_hue_correct.links.new(reroute_032_1.outputs[0], _lab_adjustments_005_1.inputs[0])
    # reroute_033_1.Output -> _lab_adjustments_006_1.Factor
    _rr_hue_correct.links.new(reroute_033_1.outputs[0], _lab_adjustments_006_1.inputs[0])
    # reroute_034_1.Output -> _lab_adjustments_007_1.Factor
    _rr_hue_correct.links.new(reroute_034_1.outputs[0], _lab_adjustments_007_1.inputs[0])
    # reroute_023_1.Output -> reroute_029_1.Input
    _rr_hue_correct.links.new(reroute_023_1.outputs[0], reroute_029_1.inputs[0])
    # reroute_024_1.Output -> reroute_030_1.Input
    _rr_hue_correct.links.new(reroute_024_1.outputs[0], reroute_030_1.inputs[0])
    # reroute_025_1.Output -> reroute_031_1.Input
    _rr_hue_correct.links.new(reroute_025_1.outputs[0], reroute_031_1.inputs[0])
    # reroute_022_1.Output -> reroute_032_1.Input
    _rr_hue_correct.links.new(reroute_022_1.outputs[0], reroute_032_1.inputs[0])
    # reroute_020_1.Output -> reroute_033_1.Input
    _rr_hue_correct.links.new(reroute_020_1.outputs[0], reroute_033_1.inputs[0])
    # reroute_021_1.Output -> reroute_034_1.Input
    _rr_hue_correct.links.new(reroute_021_1.outputs[0], reroute_034_1.inputs[0])
    # group_input_002_4.Input -> separate_color_003_3.Image
    _rr_hue_correct.links.new(group_input_002_4.outputs[1], separate_color_003_3.inputs[0])
    # group_004_1.Value -> reroute_012_2.Input
    _rr_hue_correct.links.new(group_004_1.outputs[1], reroute_012_2.inputs[0])
    # group_006_1.Mask -> reroute_035_1.Input
    _rr_hue_correct.links.new(group_006_1.outputs[0], reroute_035_1.inputs[0])
    # group_007_1.Value -> reroute_036_1.Input
    _rr_hue_correct.links.new(group_007_1.outputs[1], reroute_036_1.inputs[0])
    # group_001_1.Mask -> reroute_037_1.Input
    _rr_hue_correct.links.new(group_001_1.outputs[0], reroute_037_1.inputs[0])
    # group_005_1.Value -> reroute_038_1.Input
    _rr_hue_correct.links.new(group_005_1.outputs[1], reroute_038_1.inputs[0])
    # group_007_1.Mask -> reroute_039_1.Input
    _rr_hue_correct.links.new(group_007_1.outputs[0], reroute_039_1.inputs[0])
    # group_002_1.Value -> reroute_040_1.Input
    _rr_hue_correct.links.new(group_002_1.outputs[1], reroute_040_1.inputs[0])
    # group_005_1.Mask -> reroute_041_1.Input
    _rr_hue_correct.links.new(group_005_1.outputs[0], reroute_041_1.inputs[0])
    # group_004_1.Mask -> reroute_042_1.Input
    _rr_hue_correct.links.new(group_004_1.outputs[0], reroute_042_1.inputs[0])
    # group_002_1.Mask -> reroute_043_1.Input
    _rr_hue_correct.links.new(group_002_1.outputs[0], reroute_043_1.inputs[0])
    # group_001_1.Value -> reroute_044_1.Input
    _rr_hue_correct.links.new(group_001_1.outputs[1], reroute_044_1.inputs[0])
    # group_4.Value -> reroute_045_1.Input
    _rr_hue_correct.links.new(group_4.outputs[1], reroute_045_1.inputs[0])
    # group_006_1.Value -> reroute_046_1.Input
    _rr_hue_correct.links.new(group_006_1.outputs[1], reroute_046_1.inputs[0])
    # group_4.Mask -> reroute_047_1.Input
    _rr_hue_correct.links.new(group_4.outputs[0], reroute_047_1.inputs[0])
    # reroute_006_3.Output -> _srgb_to_lab_1.Image
    _rr_hue_correct.links.new(reroute_006_3.outputs[0], _srgb_to_lab_1.inputs[0])
    # reroute_048_1.Output -> reroute_017_1.Input
    _rr_hue_correct.links.new(reroute_048_1.outputs[0], reroute_017_1.inputs[0])
    # _lab_to_srgb_1.Image -> reroute_048_1.Input
    _rr_hue_correct.links.new(_lab_to_srgb_1.outputs[0], reroute_048_1.inputs[0])
    # group_input_22.Input -> separate_color_006_1.Image
    _rr_hue_correct.links.new(group_input_22.outputs[1], separate_color_006_1.inputs[0])
    # separate_color_004_2.Blue -> combine_color_001_2.Blue
    _rr_hue_correct.links.new(separate_color_004_2.outputs[2], combine_color_001_2.inputs[2])
    # separate_color_006_1.Red -> combine_color_002_2.Red
    _rr_hue_correct.links.new(separate_color_006_1.outputs[0], combine_color_002_2.inputs[0])
    # separate_color_006_1.Green -> combine_color_002_2.Green
    _rr_hue_correct.links.new(separate_color_006_1.outputs[1], combine_color_002_2.inputs[1])
    # separate_color_006_1.Alpha -> combine_color_002_2.Alpha
    _rr_hue_correct.links.new(separate_color_006_1.outputs[3], combine_color_002_2.inputs[3])
    # combine_color_002_2.Image -> reroute_006_3.Input
    _rr_hue_correct.links.new(combine_color_002_2.outputs[0], reroute_006_3.inputs[0])
    # group_033_1.Result -> group_034_1.Image
    _rr_hue_correct.links.new(group_033_1.outputs[0], group_034_1.inputs[1])
    # group_034_1.Result -> group_035_1.Image
    _rr_hue_correct.links.new(group_034_1.outputs[0], group_035_1.inputs[1])
    # group_035_1.Result -> group_036_1.Image
    _rr_hue_correct.links.new(group_035_1.outputs[0], group_036_1.inputs[1])
    # group_036_1.Result -> group_037_1.Image
    _rr_hue_correct.links.new(group_036_1.outputs[0], group_037_1.inputs[1])
    # group_037_1.Result -> group_038_1.Image
    _rr_hue_correct.links.new(group_037_1.outputs[0], group_038_1.inputs[1])
    # group_038_1.Result -> group_039_1.Image
    _rr_hue_correct.links.new(group_038_1.outputs[0], group_039_1.inputs[1])
    # math_037.Value -> group_033_1.Factor
    _rr_hue_correct.links.new(math_037.outputs[0], group_033_1.inputs[0])
    # math_011_6.Value -> group_033_1.Add
    _rr_hue_correct.links.new(math_011_6.outputs[0], group_033_1.inputs[3])
    # math_010_6.Value -> group_034_1.Add
    _rr_hue_correct.links.new(math_010_6.outputs[0], group_034_1.inputs[3])
    # math_038.Value -> group_034_1.Factor
    _rr_hue_correct.links.new(math_038.outputs[0], group_034_1.inputs[0])
    # math_039.Value -> group_035_1.Factor
    _rr_hue_correct.links.new(math_039.outputs[0], group_035_1.inputs[0])
    # math_040.Value -> group_036_1.Factor
    _rr_hue_correct.links.new(math_040.outputs[0], group_036_1.inputs[0])
    # math_041.Value -> group_037_1.Factor
    _rr_hue_correct.links.new(math_041.outputs[0], group_037_1.inputs[0])
    # math_042.Value -> group_038_1.Factor
    _rr_hue_correct.links.new(math_042.outputs[0], group_038_1.inputs[0])
    # math_043.Value -> group_039_1.Factor
    _rr_hue_correct.links.new(math_043.outputs[0], group_039_1.inputs[0])
    # math_009_8.Value -> group_035_1.Add
    _rr_hue_correct.links.new(math_009_8.outputs[0], group_035_1.inputs[3])
    # math_008_9.Value -> group_036_1.Add
    _rr_hue_correct.links.new(math_008_9.outputs[0], group_036_1.inputs[3])
    # math_007_10.Value -> group_037_1.Add
    _rr_hue_correct.links.new(math_007_10.outputs[0], group_037_1.inputs[3])
    # math_006_10.Value -> group_038_1.Add
    _rr_hue_correct.links.new(math_006_10.outputs[0], group_038_1.inputs[3])
    # reroute_049_1.Output -> combine_color_002_2.Blue
    _rr_hue_correct.links.new(reroute_049_1.outputs[0], combine_color_002_2.inputs[2])
    # reroute_050_1.Output -> reroute_049_1.Input
    _rr_hue_correct.links.new(reroute_050_1.outputs[0], reroute_049_1.inputs[0])
    # group_039_1.Result -> reroute_050_1.Input
    _rr_hue_correct.links.new(group_039_1.outputs[0], reroute_050_1.inputs[0])
    # switch_001_1.Image -> mix_16.B
    _rr_hue_correct.links.new(switch_001_1.outputs[0], mix_16.inputs[7])
    # reroute_052_1.Output -> mix_16.A
    _rr_hue_correct.links.new(reroute_052_1.outputs[0], mix_16.inputs[6])
    # reroute_053_1.Output -> reroute_051_1.Input
    _rr_hue_correct.links.new(reroute_053_1.outputs[0], reroute_051_1.inputs[0])
    # reroute_054_1.Output -> reroute_052_1.Input
    _rr_hue_correct.links.new(reroute_054_1.outputs[0], reroute_052_1.inputs[0])
    # group_input_004_5.Factor -> reroute_053_1.Input
    _rr_hue_correct.links.new(group_input_004_5.outputs[0], reroute_053_1.inputs[0])
    # group_input_004_5.Input -> reroute_054_1.Input
    _rr_hue_correct.links.new(group_input_004_5.outputs[1], reroute_054_1.inputs[0])
    # reroute_055_1.Output -> group_004_1.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_004_1.inputs[3])
    # reroute_055_1.Output -> group_006_1.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_006_1.inputs[3])
    # reroute_055_1.Output -> group_007_1.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_007_1.inputs[3])
    # reroute_055_1.Output -> group_001_1.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_001_1.inputs[3])
    # reroute_055_1.Output -> group_002_1.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_002_1.inputs[3])
    # math_004_12.Value -> math_003_13.Value
    _rr_hue_correct.links.new(math_004_12.outputs[0], math_003_13.inputs[0])
    # math_003_13.Value -> group_005_1.Range
    _rr_hue_correct.links.new(math_003_13.outputs[0], group_005_1.inputs[3])
    # value_1.Value -> math_004_12.Value
    _rr_hue_correct.links.new(value_1.outputs[0], math_004_12.inputs[0])
    # math_004_12.Value -> reroute_055_1.Input
    _rr_hue_correct.links.new(math_004_12.outputs[0], reroute_055_1.inputs[0])
    # clamp_1.Result -> combine_color_8.Green
    _rr_hue_correct.links.new(clamp_1.outputs[0], combine_color_8.inputs[1])
    # map_range_007_1.Result -> math_004_12.Value
    _rr_hue_correct.links.new(map_range_007_1.outputs[0], math_004_12.inputs[1])
    # group_input_22.Range -> map_range_007_1.Value
    _rr_hue_correct.links.new(group_input_22.outputs[4], map_range_007_1.inputs[0])
    # math_005_11.Value -> group_039_1.Add
    _rr_hue_correct.links.new(math_005_11.outputs[0], group_039_1.inputs[3])
    # group_input_006_1.Pink Value -> math_005_11.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[28], math_005_11.inputs[0])
    # group_input_006_1.Blue Value -> math_006_10.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[27], math_006_10.inputs[0])
    # group_input_006_1.Teal Value -> math_007_10.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[26], math_007_10.inputs[0])
    # group_input_006_1.Green Value -> math_008_9.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[25], math_008_9.inputs[0])
    # group_input_006_1.Yellow Value -> math_009_8.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[24], math_009_8.inputs[0])
    # group_input_006_1.Orange Value -> math_010_6.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[23], math_010_6.inputs[0])
    # group_input_006_1.Red Value -> math_011_6.Value
    _rr_hue_correct.links.new(group_input_006_1.outputs[22], math_011_6.inputs[0])
    # math_013_4.Value -> math_014_4.Value
    _rr_hue_correct.links.new(math_013_4.outputs[0], math_014_4.inputs[0])
    # group_input_001_7.Pink Hue -> math_013_4.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[14], math_013_4.inputs[0])
    # math_015_4.Value -> math_016_4.Value
    _rr_hue_correct.links.new(math_015_4.outputs[0], math_016_4.inputs[0])
    # group_input_001_7.Blue Hue -> math_015_4.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[13], math_015_4.inputs[0])
    # math_028_4.Value -> group_029_1.Add
    _rr_hue_correct.links.new(math_028_4.outputs[0], group_029_1.inputs[3])
    # group_input_004_5.Saturation Mask -> reroute_057_1.Input
    _rr_hue_correct.links.new(group_input_004_5.outputs[6], reroute_057_1.inputs[0])
    # group_input_004_5.Value Mask -> reroute_058_1.Input
    _rr_hue_correct.links.new(group_input_004_5.outputs[7], reroute_058_1.inputs[0])
    # reroute_052_1.Output -> separate_color_007_1.Image
    _rr_hue_correct.links.new(reroute_052_1.outputs[0], separate_color_007_1.inputs[0])
    # reroute_051_1.Output -> math_029_3.Value
    _rr_hue_correct.links.new(reroute_051_1.outputs[0], math_029_3.inputs[1])
    # math_032_2.Value -> math_029_3.Value
    _rr_hue_correct.links.new(math_032_2.outputs[0], math_029_3.inputs[0])
    # separate_color_007_1.Green -> map_range_008_1.Value
    _rr_hue_correct.links.new(separate_color_007_1.outputs[1], map_range_008_1.inputs[0])
    # map_range_008_1.Result -> mix_002_5.A
    _rr_hue_correct.links.new(map_range_008_1.outputs[0], mix_002_5.inputs[2])
    # separate_color_007_1.Green -> mix_002_5.B
    _rr_hue_correct.links.new(separate_color_007_1.outputs[1], mix_002_5.inputs[3])
    # map_range_009_1.Result -> mix_002_5.Factor
    _rr_hue_correct.links.new(map_range_009_1.outputs[0], mix_002_5.inputs[0])
    # mix_002_5.Result -> mix_003_2.B
    _rr_hue_correct.links.new(mix_002_5.outputs[0], mix_003_2.inputs[3])
    # reroute_061_1.Output -> math_030_2.Value
    _rr_hue_correct.links.new(reroute_061_1.outputs[0], math_030_2.inputs[0])
    # math_030_2.Value -> mix_003_2.Factor
    _rr_hue_correct.links.new(math_030_2.outputs[0], mix_003_2.inputs[0])
    # reroute_057_1.Output -> reroute_061_1.Input
    _rr_hue_correct.links.new(reroute_057_1.outputs[0], reroute_061_1.inputs[0])
    # reroute_061_1.Output -> map_range_009_1.Value
    _rr_hue_correct.links.new(reroute_061_1.outputs[0], map_range_009_1.inputs[0])
    # separate_color_007_1.Blue -> map_range_010.Value
    _rr_hue_correct.links.new(separate_color_007_1.outputs[2], map_range_010.inputs[0])
    # map_range_010.Result -> mix_004_2.A
    _rr_hue_correct.links.new(map_range_010.outputs[0], mix_004_2.inputs[2])
    # separate_color_007_1.Blue -> mix_004_2.B
    _rr_hue_correct.links.new(separate_color_007_1.outputs[2], mix_004_2.inputs[3])
    # map_range_011.Result -> mix_004_2.Factor
    _rr_hue_correct.links.new(map_range_011.outputs[0], mix_004_2.inputs[0])
    # mix_004_2.Result -> mix_005_2.B
    _rr_hue_correct.links.new(mix_004_2.outputs[0], mix_005_2.inputs[3])
    # reroute_062_1.Output -> math_031_1.Value
    _rr_hue_correct.links.new(reroute_062_1.outputs[0], math_031_1.inputs[0])
    # math_031_1.Value -> mix_005_2.Factor
    _rr_hue_correct.links.new(math_031_1.outputs[0], mix_005_2.inputs[0])
    # reroute_062_1.Output -> map_range_011.Value
    _rr_hue_correct.links.new(reroute_062_1.outputs[0], map_range_011.inputs[0])
    # reroute_058_1.Output -> reroute_062_1.Input
    _rr_hue_correct.links.new(reroute_058_1.outputs[0], reroute_062_1.inputs[0])
    # mix_003_2.Result -> math_032_2.Value
    _rr_hue_correct.links.new(mix_003_2.outputs[0], math_032_2.inputs[0])
    # mix_005_2.Result -> math_032_2.Value
    _rr_hue_correct.links.new(mix_005_2.outputs[0], math_032_2.inputs[1])
    # math_029_3.Value -> mix_16.Factor
    _rr_hue_correct.links.new(math_029_3.outputs[0], mix_16.inputs[0])
    # reroute_055_1.Output -> group_4.Range
    _rr_hue_correct.links.new(reroute_055_1.outputs[0], group_4.inputs[3])
    # separate_color_006_1.Blue -> group_033_1.Image
    _rr_hue_correct.links.new(separate_color_006_1.outputs[2], group_033_1.inputs[1])
    # reroute_026_1.Output -> group_025_1.Image
    _rr_hue_correct.links.new(reroute_026_1.outputs[0], group_025_1.inputs[1])
    # separate_color_003_3.Green -> group_009_1.Image
    _rr_hue_correct.links.new(separate_color_003_3.outputs[1], group_009_1.inputs[1])
    # reroute_014_1.Output -> _lab_adjustments_001_1.A
    _rr_hue_correct.links.new(reroute_014_1.outputs[0], _lab_adjustments_001_1.inputs[1])
    # reroute_013_2.Output -> _lab_adjustments_001_1.B
    _rr_hue_correct.links.new(reroute_013_2.outputs[0], _lab_adjustments_001_1.inputs[2])
    # math_014_4.Value -> math_012_5.Value
    _rr_hue_correct.links.new(math_014_4.outputs[0], math_012_5.inputs[0])
    # math_012_5.Value -> group_031_1.Add
    _rr_hue_correct.links.new(math_012_5.outputs[0], group_031_1.inputs[3])
    # math_016_4.Value -> math_027_4.Value
    _rr_hue_correct.links.new(math_016_4.outputs[0], math_027_4.inputs[0])
    # math_027_4.Value -> group_030_1.Add
    _rr_hue_correct.links.new(math_027_4.outputs[0], group_030_1.inputs[3])
    # math_017_4.Value -> math_018_3.Value
    _rr_hue_correct.links.new(math_017_4.outputs[0], math_018_3.inputs[0])
    # math_018_3.Value -> math_028_4.Value
    _rr_hue_correct.links.new(math_018_3.outputs[0], math_028_4.inputs[0])
    # group_input_001_7.Teal Hue -> math_017_4.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[12], math_017_4.inputs[0])
    # math_019_3.Value -> math_020_3.Value
    _rr_hue_correct.links.new(math_019_3.outputs[0], math_020_3.inputs[0])
    # math_020_3.Value -> math_033_1.Value
    _rr_hue_correct.links.new(math_020_3.outputs[0], math_033_1.inputs[0])
    # group_input_001_7.Green Hue -> math_019_3.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[11], math_019_3.inputs[0])
    # math_033_1.Value -> group_028_1.Add
    _rr_hue_correct.links.new(math_033_1.outputs[0], group_028_1.inputs[3])
    # math_021_3.Value -> math_022_4.Value
    _rr_hue_correct.links.new(math_021_3.outputs[0], math_022_4.inputs[0])
    # math_022_4.Value -> math_034_1.Value
    _rr_hue_correct.links.new(math_022_4.outputs[0], math_034_1.inputs[0])
    # group_input_001_7.Yellow Hue -> math_021_3.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[10], math_021_3.inputs[0])
    # math_034_1.Value -> group_027_1.Add
    _rr_hue_correct.links.new(math_034_1.outputs[0], group_027_1.inputs[3])
    # math_023_4.Value -> math_024_4.Value
    _rr_hue_correct.links.new(math_023_4.outputs[0], math_024_4.inputs[0])
    # math_024_4.Value -> math_035_1.Value
    _rr_hue_correct.links.new(math_024_4.outputs[0], math_035_1.inputs[0])
    # math_035_1.Value -> group_026_1.Add
    _rr_hue_correct.links.new(math_035_1.outputs[0], group_026_1.inputs[3])
    # group_input_001_7.Orange Hue -> math_023_4.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[9], math_023_4.inputs[0])
    # math_025_4.Value -> math_026_4.Value
    _rr_hue_correct.links.new(math_025_4.outputs[0], math_026_4.inputs[0])
    # math_026_4.Value -> math_036_1.Value
    _rr_hue_correct.links.new(math_026_4.outputs[0], math_036_1.inputs[0])
    # group_input_001_7.Red Hue -> math_025_4.Value
    _rr_hue_correct.links.new(group_input_001_7.outputs[8], math_025_4.inputs[0])
    # math_036_1.Value -> group_025_1.Add
    _rr_hue_correct.links.new(math_036_1.outputs[0], group_025_1.inputs[3])
    # reroute_042_1.Output -> group_025_1.Factor
    _rr_hue_correct.links.new(reroute_042_1.outputs[0], group_025_1.inputs[0])
    # reroute_041_1.Output -> group_026_1.Factor
    _rr_hue_correct.links.new(reroute_041_1.outputs[0], group_026_1.inputs[0])
    # reroute_035_1.Output -> group_027_1.Factor
    _rr_hue_correct.links.new(reroute_035_1.outputs[0], group_027_1.inputs[0])
    # reroute_039_1.Output -> group_028_1.Factor
    _rr_hue_correct.links.new(reroute_039_1.outputs[0], group_028_1.inputs[0])
    # reroute_047_1.Output -> group_029_1.Factor
    _rr_hue_correct.links.new(reroute_047_1.outputs[0], group_029_1.inputs[0])
    # reroute_037_1.Output -> group_030_1.Factor
    _rr_hue_correct.links.new(reroute_037_1.outputs[0], group_030_1.inputs[0])
    # reroute_043_1.Output -> group_031_1.Factor
    _rr_hue_correct.links.new(reroute_043_1.outputs[0], group_031_1.inputs[0])
    # group_004_1.Mask -> math_037.Value
    _rr_hue_correct.links.new(group_004_1.outputs[0], math_037.inputs[0])
    # group_005_1.Mask -> math_038.Value
    _rr_hue_correct.links.new(group_005_1.outputs[0], math_038.inputs[0])
    # group_006_1.Mask -> math_039.Value
    _rr_hue_correct.links.new(group_006_1.outputs[0], math_039.inputs[0])
    # group_007_1.Mask -> math_040.Value
    _rr_hue_correct.links.new(group_007_1.outputs[0], math_040.inputs[0])
    # group_4.Mask -> math_041.Value
    _rr_hue_correct.links.new(group_4.outputs[0], math_041.inputs[0])
    # group_001_1.Mask -> math_042.Value
    _rr_hue_correct.links.new(group_001_1.outputs[0], math_042.inputs[0])
    # group_002_1.Mask -> math_043.Value
    _rr_hue_correct.links.new(group_002_1.outputs[0], math_043.inputs[0])
    # separate_color_005_1.Red -> reroute_007_3.Input
    _rr_hue_correct.links.new(separate_color_005_1.outputs[0], reroute_007_3.inputs[0])
    # separate_color_005_1.Green -> map_range_012_1.Value
    _rr_hue_correct.links.new(separate_color_005_1.outputs[1], map_range_012_1.inputs[0])
    # reroute_018_1.Output -> group_004_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_004_1.inputs[1])
    # map_range_012_1.Result -> reroute_018_1.Input
    _rr_hue_correct.links.new(map_range_012_1.outputs[0], reroute_018_1.inputs[0])
    # reroute_018_1.Output -> group_005_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_005_1.inputs[1])
    # reroute_018_1.Output -> group_006_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_006_1.inputs[1])
    # reroute_018_1.Output -> group_007_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_007_1.inputs[1])
    # reroute_018_1.Output -> group_4.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_4.inputs[1])
    # reroute_018_1.Output -> group_001_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_001_1.inputs[1])
    # reroute_018_1.Output -> group_002_1.Mask
    _rr_hue_correct.links.new(reroute_018_1.outputs[0], group_002_1.inputs[1])
    # reroute_027_1.Output -> reroute_026_1.Input
    _rr_hue_correct.links.new(reroute_027_1.outputs[0], reroute_026_1.inputs[0])
    # separate_color_002_2.Red -> reroute_027_1.Input
    _rr_hue_correct.links.new(separate_color_002_2.outputs[0], reroute_027_1.inputs[0])
    # group_input_001_7.Input -> separate_color_002_2.Image
    _rr_hue_correct.links.new(group_input_001_7.outputs[1], separate_color_002_2.inputs[0])
    # group_input_22.sRGB -> separate_color_005_1.Image
    _rr_hue_correct.links.new(group_input_22.outputs[2], separate_color_005_1.inputs[0])

    return _rr_hue_correct


_rr_hue_correct = _rr_hue_correct_node_group()

def _rr_preserve_color_node_group():
    """Initialize .RR_preserve_color node group"""
    _rr_preserve_color = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_preserve_color")

    _rr_preserve_color.color_tag = 'NONE'
    _rr_preserve_color.description = ""
    _rr_preserve_color.default_group_node_width = 140
    # _rr_preserve_color interface

    # Socket Image
    image_socket_39 = _rr_preserve_color.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_39.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_39.attribute_domain = 'POINT'
    image_socket_39.default_input = 'VALUE'
    image_socket_39.structure_type = 'AUTO'

    # Socket Image
    image_socket_40 = _rr_preserve_color.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_40.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_40.attribute_domain = 'POINT'
    image_socket_40.default_input = 'VALUE'
    image_socket_40.structure_type = 'AUTO'

    # Socket sRGB Image
    srgb_image_socket = _rr_preserve_color.interface.new_socket(name="sRGB Image", in_out='INPUT', socket_type='NodeSocketColor')
    srgb_image_socket.default_value = (1.0, 1.0, 1.0, 1.0)
    srgb_image_socket.attribute_domain = 'POINT'
    srgb_image_socket.default_input = 'VALUE'
    srgb_image_socket.structure_type = 'AUTO'

    # Socket Filmic
    filmic_socket = _rr_preserve_color.interface.new_socket(name="Filmic", in_out='INPUT', socket_type='NodeSocketFloat')
    filmic_socket.default_value = 0.0
    filmic_socket.min_value = 0.0
    filmic_socket.max_value = 1.0
    filmic_socket.subtype = 'FACTOR'
    filmic_socket.attribute_domain = 'POINT'
    filmic_socket.default_input = 'VALUE'
    filmic_socket.structure_type = 'AUTO'

    # Socket Hue
    hue_socket_2 = _rr_preserve_color.interface.new_socket(name="Hue", in_out='INPUT', socket_type='NodeSocketFloat')
    hue_socket_2.default_value = 0.0
    hue_socket_2.min_value = 0.0
    hue_socket_2.max_value = 1.0
    hue_socket_2.subtype = 'FACTOR'
    hue_socket_2.attribute_domain = 'POINT'
    hue_socket_2.default_input = 'VALUE'
    hue_socket_2.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_3 = _rr_preserve_color.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_3.default_value = 0.0
    saturation_socket_3.min_value = 0.0
    saturation_socket_3.max_value = 1.0
    saturation_socket_3.subtype = 'FACTOR'
    saturation_socket_3.attribute_domain = 'POINT'
    saturation_socket_3.default_input = 'VALUE'
    saturation_socket_3.structure_type = 'AUTO'

    # Socket Cutoff
    cutoff_socket = _rr_preserve_color.interface.new_socket(name="Cutoff", in_out='INPUT', socket_type='NodeSocketFloat')
    cutoff_socket.default_value = 5.0
    cutoff_socket.min_value = 0.0
    cutoff_socket.max_value = 25.0
    cutoff_socket.subtype = 'NONE'
    cutoff_socket.attribute_domain = 'POINT'
    cutoff_socket.default_input = 'VALUE'
    cutoff_socket.structure_type = 'AUTO'

    # Socket Spread
    spread_socket = _rr_preserve_color.interface.new_socket(name="Spread", in_out='INPUT', socket_type='NodeSocketFloat')
    spread_socket.default_value = 0.0
    spread_socket.min_value = 0.0
    spread_socket.max_value = 1.0
    spread_socket.subtype = 'FACTOR'
    spread_socket.attribute_domain = 'POINT'
    spread_socket.default_input = 'VALUE'
    spread_socket.structure_type = 'AUTO'

    # Initialize _rr_preserve_color nodes

    # Node Group Output
    group_output_26 = _rr_preserve_color.nodes.new("NodeGroupOutput")
    group_output_26.name = "Group Output"
    group_output_26.is_active_output = True

    # Node Group Input
    group_input_23 = _rr_preserve_color.nodes.new("NodeGroupInput")
    group_input_23.name = "Group Input"

    # Node Separate Color
    separate_color_8 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_8.name = "Separate Color"
    separate_color_8.mode = 'HSV'
    separate_color_8.ycc_mode = 'ITUBT709'

    # Node Combine Color
    combine_color_9 = _rr_preserve_color.nodes.new("CompositorNodeCombineColor")
    combine_color_9.name = "Combine Color"
    combine_color_9.mode = 'HSV'
    combine_color_9.ycc_mode = 'ITUBT709'

    # Node Separate Color.001
    separate_color_001_5 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_5.name = "Separate Color.001"
    separate_color_001_5.mode = 'HSV'
    separate_color_001_5.ycc_mode = 'ITUBT709'

    # Node Mix
    mix_17 = _rr_preserve_color.nodes.new("ShaderNodeMix")
    mix_17.name = "Mix"
    mix_17.blend_type = 'MIX'
    mix_17.clamp_factor = True
    mix_17.clamp_result = False
    mix_17.data_type = 'RGBA'
    mix_17.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_16 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_16.name = "Reroute"
    reroute_16.socket_idname = "NodeSocketColor"
    # Node Map Range
    map_range_15 = _rr_preserve_color.nodes.new("ShaderNodeMapRange")
    map_range_15.name = "Map Range"
    map_range_15.clamp = True
    map_range_15.data_type = 'FLOAT'
    map_range_15.interpolation_type = 'LINEAR'
    # From Min
    map_range_15.inputs[1].default_value = 0.0
    # From Max
    map_range_15.inputs[2].default_value = 1.0
    # To Min
    map_range_15.inputs[3].default_value = 1.0
    # To Max
    map_range_15.inputs[4].default_value = 0.0

    # Node Math
    math_21 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_21.name = "Math"
    math_21.operation = 'ADD'
    math_21.use_clamp = True

    # Node Map Range.001
    map_range_001_14 = _rr_preserve_color.nodes.new("ShaderNodeMapRange")
    map_range_001_14.name = "Map Range.001"
    map_range_001_14.clamp = True
    map_range_001_14.data_type = 'FLOAT'
    map_range_001_14.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_14.inputs[1].default_value = 0.0
    # From Max
    map_range_001_14.inputs[2].default_value = 1.0
    # To Min
    map_range_001_14.inputs[3].default_value = 0.0

    # Node Separate Color.002
    separate_color_002_3 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_3.name = "Separate Color.002"
    separate_color_002_3.mode = 'HSV'
    separate_color_002_3.ycc_mode = 'ITUBT709'

    # Node Combine Color.001
    combine_color_001_3 = _rr_preserve_color.nodes.new("CompositorNodeCombineColor")
    combine_color_001_3.name = "Combine Color.001"
    combine_color_001_3.mode = 'HSV'
    combine_color_001_3.ycc_mode = 'ITUBT709'

    # Node Math.001
    math_001_17 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_001_17.name = "Math.001"
    math_001_17.operation = 'ADD'
    math_001_17.use_clamp = True

    # Node Group Input.001
    group_input_001_8 = _rr_preserve_color.nodes.new("NodeGroupInput")
    group_input_001_8.name = "Group Input.001"

    # Node Map Range.002
    map_range_002_11 = _rr_preserve_color.nodes.new("ShaderNodeMapRange")
    map_range_002_11.name = "Map Range.002"
    map_range_002_11.clamp = True
    map_range_002_11.data_type = 'FLOAT'
    map_range_002_11.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_11.inputs[1].default_value = 0.0
    # From Max
    map_range_002_11.inputs[2].default_value = 1.0
    # To Min
    map_range_002_11.inputs[3].default_value = 0.0

    # Node Mix.001
    mix_001_12 = _rr_preserve_color.nodes.new("ShaderNodeMix")
    mix_001_12.name = "Mix.001"
    mix_001_12.blend_type = 'MIX'
    mix_001_12.clamp_factor = True
    mix_001_12.clamp_result = False
    mix_001_12.data_type = 'RGBA'
    mix_001_12.factor_mode = 'UNIFORM'

    # Node Math.002
    math_002_15 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_002_15.name = "Math.002"
    math_002_15.operation = 'MULTIPLY'
    math_002_15.use_clamp = False

    # Node Math.003
    math_003_14 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_003_14.name = "Math.003"
    math_003_14.operation = 'MULTIPLY'
    math_003_14.use_clamp = False

    # Node Reroute.001
    reroute_001_10 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_001_10.name = "Reroute.001"
    reroute_001_10.socket_idname = "NodeSocketFloat"
    # Node Reroute.002
    reroute_002_10 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_002_10.name = "Reroute.002"
    reroute_002_10.socket_idname = "NodeSocketFloat"
    # Node Frame
    frame_14 = _rr_preserve_color.nodes.new("NodeFrame")
    frame_14.name = "Frame"
    frame_14.label_size = 20
    frame_14.shrink = True

    # Node Group Input.002
    group_input_002_5 = _rr_preserve_color.nodes.new("NodeGroupInput")
    group_input_002_5.name = "Group Input.002"

    # Node Separate Color.003
    separate_color_003_4 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_4.name = "Separate Color.003"
    separate_color_003_4.mode = 'HSV'
    separate_color_003_4.ycc_mode = 'ITUBT709'

    # Node Map Range.004
    map_range_004_7 = _rr_preserve_color.nodes.new("ShaderNodeMapRange")
    map_range_004_7.name = "Map Range.004"
    map_range_004_7.clamp = True
    map_range_004_7.data_type = 'FLOAT'
    map_range_004_7.interpolation_type = 'SMOOTHERSTEP'
    # To Min
    map_range_004_7.inputs[3].default_value = 0.0
    # To Max
    map_range_004_7.inputs[4].default_value = 1.0

    # Node Convert Colorspace
    convert_colorspace_2 = _rr_preserve_color.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace_2.name = "Convert Colorspace"
    convert_colorspace_2.from_color_space = 'sRGB'
    convert_colorspace_2.to_color_space = 'Filmic sRGB'

    # Node Frame.001
    frame_001_11 = _rr_preserve_color.nodes.new("NodeFrame")
    frame_001_11.name = "Frame.001"
    frame_001_11.label_size = 20
    frame_001_11.shrink = True

    # Node Reroute.004
    reroute_004_7 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_004_7.name = "Reroute.004"
    reroute_004_7.socket_idname = "NodeSocketFloat"
    # Node Reroute.005
    reroute_005_9 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_005_9.name = "Reroute.005"
    reroute_005_9.socket_idname = "NodeSocketFloat"
    # Node Reroute.006
    reroute_006_4 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_006_4.name = "Reroute.006"
    reroute_006_4.socket_idname = "NodeSocketColor"
    # Node Mix.002
    mix_002_6 = _rr_preserve_color.nodes.new("ShaderNodeMix")
    mix_002_6.name = "Mix.002"
    mix_002_6.blend_type = 'MIX'
    mix_002_6.clamp_factor = True
    mix_002_6.clamp_result = False
    mix_002_6.data_type = 'RGBA'
    mix_002_6.factor_mode = 'UNIFORM'

    # Node Math.004
    math_004_13 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_004_13.name = "Math.004"
    math_004_13.operation = 'MULTIPLY'
    math_004_13.use_clamp = False

    # Node Reroute.007
    reroute_007_4 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_007_4.label = "Cutoff"
    reroute_007_4.name = "Reroute.007"
    reroute_007_4.socket_idname = "NodeSocketFloat"
    # Node Reroute.003
    reroute_003_9 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_003_9.name = "Reroute.003"
    reroute_003_9.socket_idname = "NodeSocketFloat"
    # Node Reroute.008
    reroute_008_3 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_008_3.name = "Reroute.008"
    reroute_008_3.socket_idname = "NodeSocketFloat"
    # Node Frame.002
    frame_002_10 = _rr_preserve_color.nodes.new("NodeFrame")
    frame_002_10.label = "Filmic"
    frame_002_10.name = "Frame.002"
    frame_002_10.label_size = 20
    frame_002_10.shrink = True

    # Node Reroute.009
    reroute_009_3 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_009_3.name = "Reroute.009"
    reroute_009_3.socket_idname = "NodeSocketFloat"
    # Node Reroute.010
    reroute_010_3 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_010_3.name = "Reroute.010"
    reroute_010_3.socket_idname = "NodeSocketColor"
    # Node Math.005
    math_005_12 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_005_12.name = "Math.005"
    math_005_12.hide = True
    math_005_12.operation = 'MULTIPLY'
    math_005_12.use_clamp = False

    # Node Math.006
    math_006_11 = _rr_preserve_color.nodes.new("ShaderNodeMath")
    math_006_11.name = "Math.006"
    math_006_11.operation = 'MULTIPLY'
    math_006_11.use_clamp = False
    # Value_001
    math_006_11.inputs[1].default_value = -1.0

    # Node Reroute.011
    reroute_011_3 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_011_3.name = "Reroute.011"
    reroute_011_3.socket_idname = "NodeSocketColor"
    # Node Reroute.012
    reroute_012_3 = _rr_preserve_color.nodes.new("NodeReroute")
    reroute_012_3.name = "Reroute.012"
    reroute_012_3.socket_idname = "NodeSocketFloatFactor"
    # Node Separate Color.004
    separate_color_004_3 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_004_3.name = "Separate Color.004"
    separate_color_004_3.mode = 'HSV'
    separate_color_004_3.ycc_mode = 'ITUBT709'

    # Node Combine Color.002
    combine_color_002_3 = _rr_preserve_color.nodes.new("CompositorNodeCombineColor")
    combine_color_002_3.name = "Combine Color.002"
    combine_color_002_3.mode = 'HSV'
    combine_color_002_3.ycc_mode = 'ITUBT709'

    # Node Separate Color.005
    separate_color_005_2 = _rr_preserve_color.nodes.new("CompositorNodeSeparateColor")
    separate_color_005_2.name = "Separate Color.005"
    separate_color_005_2.mode = 'HSV'
    separate_color_005_2.ycc_mode = 'ITUBT709'
    separate_color_005_2.outputs[0].hide = True
    separate_color_005_2.outputs[1].hide = True
    separate_color_005_2.outputs[3].hide = True

    # Set parents
    group_input_23.parent = frame_14
    separate_color_8.parent = frame_14
    combine_color_9.parent = frame_14
    separate_color_001_5.parent = frame_14
    mix_17.parent = frame_14
    reroute_16.parent = frame_14
    map_range_15.parent = frame_14
    math_21.parent = frame_14
    map_range_001_14.parent = frame_14
    separate_color_002_3.parent = frame_001_11
    combine_color_001_3.parent = frame_001_11
    math_001_17.parent = frame_001_11
    group_input_001_8.parent = frame_001_11
    map_range_002_11.parent = frame_001_11
    mix_001_12.parent = frame_001_11
    math_002_15.parent = frame_001_11
    math_003_14.parent = frame_14
    reroute_001_10.parent = frame_14
    reroute_002_10.parent = frame_14
    group_input_002_5.parent = frame_002_10
    separate_color_003_4.parent = frame_002_10
    map_range_004_7.parent = frame_002_10
    convert_colorspace_2.parent = frame_002_10
    reroute_004_7.parent = frame_001_11
    reroute_005_9.parent = frame_001_11
    reroute_006_4.parent = frame_001_11
    mix_002_6.parent = frame_002_10
    math_004_13.parent = frame_002_10
    reroute_007_4.parent = frame_14
    reroute_003_9.parent = frame_14
    reroute_008_3.parent = frame_001_11
    reroute_009_3.parent = frame_002_10
    reroute_010_3.parent = frame_14
    math_005_12.parent = frame_002_10
    math_006_11.parent = frame_002_10
    reroute_011_3.parent = frame_002_10
    reroute_012_3.parent = frame_002_10
    separate_color_004_3.parent = frame_002_10
    combine_color_002_3.parent = frame_002_10
    separate_color_005_2.parent = frame_002_10

    # Set locations
    group_output_26.location = (3890.70703125, -280.76275634765625)
    group_input_23.location = (29.251007080078125, -568.1797485351562)
    separate_color_8.location = (702.70556640625, -192.51007080078125)
    combine_color_9.location = (1051.73486328125, -330.552490234375)
    separate_color_001_5.location = (700.04443359375, -379.5379333496094)
    mix_17.location = (2200.031982421875, -422.154052734375)
    reroute_16.location = (838.8800048828125, -601.1293334960938)
    map_range_15.location = (980.7530517578125, -628.5833740234375)
    math_21.location = (1220.6873779296875, -864.3560791015625)
    map_range_001_14.location = (1493.94775390625, -677.9837036132812)
    separate_color_002_3.location = (29.499755859375, -502.2367858886719)
    combine_color_001_3.location = (1000.9326171875, -475.3188171386719)
    math_001_17.location = (446.756103515625, -231.004150390625)
    group_input_001_8.location = (128.245849609375, -112.35150146484375)
    map_range_002_11.location = (671.019287109375, -77.75747680664062)
    mix_001_12.location = (1288.0537109375, -268.8945007324219)
    math_002_15.location = (1006.6494140625, -173.0489501953125)
    math_003_14.location = (1981.6224365234375, -406.1400146484375)
    reroute_001_10.location = (2314.795654296875, -252.4044952392578)
    reroute_002_10.location = (2307.906005859375, -36.076263427734375)
    frame_14.location = (-149.40000915527344, 227.67047119140625)
    group_input_002_5.location = (29.3638916015625, -284.7231140136719)
    separate_color_003_4.location = (530.577880859375, -35.8961296081543)
    map_range_004_7.location = (755.9129028320312, -81.12926483154297)
    convert_colorspace_2.location = (666.99267578125, -634.286376953125)
    frame_001_11.location = (2345.400146484375, -27.646085739135742)
    reroute_004_7.location = (80.823974609375, -34.02000427246094)
    reroute_005_9.location = (79.978271484375, -371.2862854003906)
    reroute_006_4.location = (76.474365234375, -448.766845703125)
    mix_002_6.location = (1267.1002197265625, -284.4446105957031)
    math_004_13.location = (1048.6014404296875, -268.9880676269531)
    reroute_007_4.location = (1306.2265625, -34.019989013671875)
    reroute_003_9.location = (114.12793731689453, -45.6151123046875)
    reroute_008_3.location = (808.715576171875, -34.61688232421875)
    frame_002_10.location = (-1716.1201171875, 30.7919979095459)
    reroute_009_3.location = (1405.8004150390625, -107.12149047851562)
    reroute_010_3.location = (543.0761108398438, -526.2076416015625)
    math_005_12.location = (224.7646484375, -453.080810546875)
    math_006_11.location = (519.9434814453125, -230.06150817871094)
    reroute_011_3.location = (667.991943359375, -472.26177978515625)
    reroute_012_3.location = (524.982177734375, -409.0330810546875)
    separate_color_004_3.location = (844.6604614257812, -614.7611083984375)
    combine_color_002_3.location = (1060.981201171875, -521.545654296875)
    separate_color_005_2.location = (841.2093505859375, -494.78924560546875)

    # Set dimensions
    group_output_26.width, group_output_26.height = 140.0, 100.0
    group_input_23.width, group_input_23.height = 140.0, 100.0
    separate_color_8.width, separate_color_8.height = 140.0, 100.0
    combine_color_9.width, combine_color_9.height = 140.0, 100.0
    separate_color_001_5.width, separate_color_001_5.height = 140.0, 100.0
    mix_17.width, mix_17.height = 140.0, 100.0
    reroute_16.width, reroute_16.height = 13.5, 100.0
    map_range_15.width, map_range_15.height = 140.0, 100.0
    math_21.width, math_21.height = 140.0, 100.0
    map_range_001_14.width, map_range_001_14.height = 140.0, 100.0
    separate_color_002_3.width, separate_color_002_3.height = 140.0, 100.0
    combine_color_001_3.width, combine_color_001_3.height = 140.0, 100.0
    math_001_17.width, math_001_17.height = 140.0, 100.0
    group_input_001_8.width, group_input_001_8.height = 140.0, 100.0
    map_range_002_11.width, map_range_002_11.height = 140.0, 100.0
    mix_001_12.width, mix_001_12.height = 140.0, 100.0
    math_002_15.width, math_002_15.height = 140.0, 100.0
    math_003_14.width, math_003_14.height = 140.0, 100.0
    reroute_001_10.width, reroute_001_10.height = 13.5, 100.0
    reroute_002_10.width, reroute_002_10.height = 13.5, 100.0
    frame_14.width, frame_14.height = 2369.119873046875, 1034.430419921875
    group_input_002_5.width, group_input_002_5.height = 140.0, 100.0
    separate_color_003_4.width, separate_color_003_4.height = 140.0, 100.0
    map_range_004_7.width, map_range_004_7.height = 140.0, 100.0
    convert_colorspace_2.width, convert_colorspace_2.height = 150.0, 100.0
    frame_001_11.width, frame_001_11.height = 1456.8798828125, 689.1139526367188
    reroute_004_7.width, reroute_004_7.height = 13.5, 100.0
    reroute_005_9.width, reroute_005_9.height = 13.5, 100.0
    reroute_006_4.width, reroute_006_4.height = 13.5, 100.0
    mix_002_6.width, mix_002_6.height = 140.0, 100.0
    math_004_13.width, math_004_13.height = 140.0, 100.0
    reroute_007_4.width, reroute_007_4.height = 13.5, 100.0
    reroute_003_9.width, reroute_003_9.height = 13.5, 100.0
    reroute_008_3.width, reroute_008_3.height = 13.5, 100.0
    frame_002_10.width, frame_002_10.height = 1439.8204345703125, 801.552001953125
    reroute_009_3.width, reroute_009_3.height = 13.5, 100.0
    reroute_010_3.width, reroute_010_3.height = 13.5, 100.0
    math_005_12.width, math_005_12.height = 140.0, 100.0
    math_006_11.width, math_006_11.height = 140.0, 100.0
    reroute_011_3.width, reroute_011_3.height = 13.5, 100.0
    reroute_012_3.width, reroute_012_3.height = 13.5, 100.0
    separate_color_004_3.width, separate_color_004_3.height = 140.0, 100.0
    combine_color_002_3.width, combine_color_002_3.height = 140.0, 100.0
    separate_color_005_2.width, separate_color_005_2.height = 140.0, 100.0

    # Initialize _rr_preserve_color links

    # separate_color_001_5.Green -> combine_color_9.Green
    _rr_preserve_color.links.new(separate_color_001_5.outputs[1], combine_color_9.inputs[1])
    # separate_color_001_5.Blue -> combine_color_9.Blue
    _rr_preserve_color.links.new(separate_color_001_5.outputs[2], combine_color_9.inputs[2])
    # separate_color_001_5.Alpha -> combine_color_9.Alpha
    _rr_preserve_color.links.new(separate_color_001_5.outputs[3], combine_color_9.inputs[3])
    # mix_001_12.Result -> group_output_26.Image
    _rr_preserve_color.links.new(mix_001_12.outputs[2], group_output_26.inputs[0])
    # separate_color_8.Red -> combine_color_9.Red
    _rr_preserve_color.links.new(separate_color_8.outputs[0], combine_color_9.inputs[0])
    # combine_color_9.Image -> mix_17.B
    _rr_preserve_color.links.new(combine_color_9.outputs[0], mix_17.inputs[7])
    # reroute_16.Output -> mix_17.A
    _rr_preserve_color.links.new(reroute_16.outputs[0], mix_17.inputs[6])
    # separate_color_001_5.Blue -> map_range_15.Value
    _rr_preserve_color.links.new(separate_color_001_5.outputs[2], map_range_15.inputs[0])
    # map_range_15.Result -> math_21.Value
    _rr_preserve_color.links.new(map_range_15.outputs[0], math_21.inputs[0])
    # group_input_23.Hue -> math_21.Value
    _rr_preserve_color.links.new(group_input_23.outputs[3], math_21.inputs[1])
    # group_input_23.Hue -> map_range_001_14.Value
    _rr_preserve_color.links.new(group_input_23.outputs[3], map_range_001_14.inputs[0])
    # math_21.Value -> map_range_001_14.To Max
    _rr_preserve_color.links.new(math_21.outputs[0], map_range_001_14.inputs[4])
    # mix_17.Result -> separate_color_002_3.Image
    _rr_preserve_color.links.new(mix_17.outputs[2], separate_color_002_3.inputs[0])
    # separate_color_002_3.Red -> combine_color_001_3.Red
    _rr_preserve_color.links.new(separate_color_002_3.outputs[0], combine_color_001_3.inputs[0])
    # separate_color_002_3.Blue -> combine_color_001_3.Blue
    _rr_preserve_color.links.new(separate_color_002_3.outputs[2], combine_color_001_3.inputs[2])
    # separate_color_002_3.Alpha -> combine_color_001_3.Alpha
    _rr_preserve_color.links.new(separate_color_002_3.outputs[3], combine_color_001_3.inputs[3])
    # separate_color_002_3.Green -> math_001_17.Value
    _rr_preserve_color.links.new(separate_color_002_3.outputs[1], math_001_17.inputs[1])
    # group_input_001_8.Saturation -> math_001_17.Value
    _rr_preserve_color.links.new(group_input_001_8.outputs[4], math_001_17.inputs[0])
    # group_input_001_8.Saturation -> map_range_002_11.Value
    _rr_preserve_color.links.new(group_input_001_8.outputs[4], map_range_002_11.inputs[0])
    # math_001_17.Value -> map_range_002_11.To Max
    _rr_preserve_color.links.new(math_001_17.outputs[0], map_range_002_11.inputs[4])
    # group_input_23.sRGB Image -> separate_color_8.Image
    _rr_preserve_color.links.new(group_input_23.outputs[1], separate_color_8.inputs[0])
    # combine_color_001_3.Image -> mix_001_12.B
    _rr_preserve_color.links.new(combine_color_001_3.outputs[0], mix_001_12.inputs[7])
    # reroute_006_4.Output -> mix_001_12.A
    _rr_preserve_color.links.new(reroute_006_4.outputs[0], mix_001_12.inputs[6])
    # reroute_005_9.Output -> combine_color_001_3.Green
    _rr_preserve_color.links.new(reroute_005_9.outputs[0], combine_color_001_3.inputs[1])
    # map_range_002_11.Result -> math_002_15.Value
    _rr_preserve_color.links.new(map_range_002_11.outputs[0], math_002_15.inputs[1])
    # math_002_15.Value -> mix_001_12.Factor
    _rr_preserve_color.links.new(math_002_15.outputs[0], mix_001_12.inputs[0])
    # reroute_007_4.Output -> math_003_14.Value
    _rr_preserve_color.links.new(reroute_007_4.outputs[0], math_003_14.inputs[0])
    # map_range_001_14.Result -> math_003_14.Value
    _rr_preserve_color.links.new(map_range_001_14.outputs[0], math_003_14.inputs[1])
    # separate_color_8.Green -> reroute_001_10.Input
    _rr_preserve_color.links.new(separate_color_8.outputs[1], reroute_001_10.inputs[0])
    # reroute_007_4.Output -> reroute_002_10.Input
    _rr_preserve_color.links.new(reroute_007_4.outputs[0], reroute_002_10.inputs[0])
    # math_003_14.Value -> mix_17.Factor
    _rr_preserve_color.links.new(math_003_14.outputs[0], mix_17.inputs[0])
    # group_input_002_5.sRGB Image -> separate_color_003_4.Image
    _rr_preserve_color.links.new(group_input_002_5.outputs[1], separate_color_003_4.inputs[0])
    # separate_color_003_4.Blue -> map_range_004_7.Value
    _rr_preserve_color.links.new(separate_color_003_4.outputs[2], map_range_004_7.inputs[0])
    # group_input_002_5.sRGB Image -> convert_colorspace_2.Image
    _rr_preserve_color.links.new(group_input_002_5.outputs[1], convert_colorspace_2.inputs[0])
    # reroute_002_10.Output -> reroute_004_7.Input
    _rr_preserve_color.links.new(reroute_002_10.outputs[0], reroute_004_7.inputs[0])
    # reroute_001_10.Output -> reroute_005_9.Input
    _rr_preserve_color.links.new(reroute_001_10.outputs[0], reroute_005_9.inputs[0])
    # mix_17.Result -> reroute_006_4.Input
    _rr_preserve_color.links.new(mix_17.outputs[2], reroute_006_4.inputs[0])
    # reroute_011_3.Output -> mix_002_6.A
    _rr_preserve_color.links.new(reroute_011_3.outputs[0], mix_002_6.inputs[6])
    # reroute_012_3.Output -> math_004_13.Value
    _rr_preserve_color.links.new(reroute_012_3.outputs[0], math_004_13.inputs[1])
    # map_range_004_7.Result -> math_004_13.Value
    _rr_preserve_color.links.new(map_range_004_7.outputs[0], math_004_13.inputs[0])
    # math_004_13.Value -> mix_002_6.Factor
    _rr_preserve_color.links.new(math_004_13.outputs[0], mix_002_6.inputs[0])
    # group_input_002_5.Cutoff -> map_range_004_7.From Min
    _rr_preserve_color.links.new(group_input_002_5.outputs[5], map_range_004_7.inputs[1])
    # reroute_003_9.Output -> reroute_007_4.Input
    _rr_preserve_color.links.new(reroute_003_9.outputs[0], reroute_007_4.inputs[0])
    # reroute_009_3.Output -> reroute_003_9.Input
    _rr_preserve_color.links.new(reroute_009_3.outputs[0], reroute_003_9.inputs[0])
    # reroute_008_3.Output -> math_002_15.Value
    _rr_preserve_color.links.new(reroute_008_3.outputs[0], math_002_15.inputs[0])
    # reroute_004_7.Output -> reroute_008_3.Input
    _rr_preserve_color.links.new(reroute_004_7.outputs[0], reroute_008_3.inputs[0])
    # reroute_010_3.Output -> separate_color_001_5.Image
    _rr_preserve_color.links.new(reroute_010_3.outputs[0], separate_color_001_5.inputs[0])
    # map_range_004_7.Result -> reroute_009_3.Input
    _rr_preserve_color.links.new(map_range_004_7.outputs[0], reroute_009_3.inputs[0])
    # mix_002_6.Result -> reroute_010_3.Input
    _rr_preserve_color.links.new(mix_002_6.outputs[2], reroute_010_3.inputs[0])
    # reroute_010_3.Output -> reroute_16.Input
    _rr_preserve_color.links.new(reroute_010_3.outputs[0], reroute_16.inputs[0])
    # group_input_002_5.Cutoff -> math_005_12.Value
    _rr_preserve_color.links.new(group_input_002_5.outputs[5], math_005_12.inputs[0])
    # group_input_002_5.Spread -> math_005_12.Value
    _rr_preserve_color.links.new(group_input_002_5.outputs[6], math_005_12.inputs[1])
    # math_005_12.Value -> math_006_11.Value
    _rr_preserve_color.links.new(math_005_12.outputs[0], math_006_11.inputs[0])
    # math_006_11.Value -> map_range_004_7.From Max
    _rr_preserve_color.links.new(math_006_11.outputs[0], map_range_004_7.inputs[2])
    # group_input_002_5.Image -> reroute_011_3.Input
    _rr_preserve_color.links.new(group_input_002_5.outputs[0], reroute_011_3.inputs[0])
    # group_input_002_5.Filmic -> reroute_012_3.Input
    _rr_preserve_color.links.new(group_input_002_5.outputs[2], reroute_012_3.inputs[0])
    # convert_colorspace_2.Image -> separate_color_004_3.Image
    _rr_preserve_color.links.new(convert_colorspace_2.outputs[0], separate_color_004_3.inputs[0])
    # combine_color_002_3.Image -> mix_002_6.B
    _rr_preserve_color.links.new(combine_color_002_3.outputs[0], mix_002_6.inputs[7])
    # separate_color_004_3.Red -> combine_color_002_3.Red
    _rr_preserve_color.links.new(separate_color_004_3.outputs[0], combine_color_002_3.inputs[0])
    # separate_color_004_3.Green -> combine_color_002_3.Green
    _rr_preserve_color.links.new(separate_color_004_3.outputs[1], combine_color_002_3.inputs[1])
    # separate_color_004_3.Alpha -> combine_color_002_3.Alpha
    _rr_preserve_color.links.new(separate_color_004_3.outputs[3], combine_color_002_3.inputs[3])
    # reroute_011_3.Output -> separate_color_005_2.Image
    _rr_preserve_color.links.new(reroute_011_3.outputs[0], separate_color_005_2.inputs[0])
    # separate_color_005_2.Blue -> combine_color_002_3.Blue
    _rr_preserve_color.links.new(separate_color_005_2.outputs[2], combine_color_002_3.inputs[2])

    return _rr_preserve_color


_rr_preserve_color = _rr_preserve_color_node_group()

def _rr_color_density_node_group():
    """Initialize .RR_color_density node group"""
    _rr_color_density = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_color_density")

    _rr_color_density.color_tag = 'NONE'
    _rr_color_density.description = ""
    _rr_color_density.default_group_node_width = 140
    # _rr_color_density interface

    # Socket Image
    image_socket_41 = _rr_color_density.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_41.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_41.attribute_domain = 'POINT'
    image_socket_41.default_input = 'VALUE'
    image_socket_41.structure_type = 'AUTO'

    # Socket Image
    image_socket_42 = _rr_color_density.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_42.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_42.attribute_domain = 'POINT'
    image_socket_42.default_input = 'VALUE'
    image_socket_42.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_7 = _rr_color_density.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_7.default_value = 0.0
    strength_socket_7.min_value = 0.0
    strength_socket_7.max_value = 1.0
    strength_socket_7.subtype = 'FACTOR'
    strength_socket_7.attribute_domain = 'POINT'
    strength_socket_7.default_input = 'VALUE'
    strength_socket_7.structure_type = 'AUTO'

    # Socket Mask Highlights
    mask_highlights_socket = _rr_color_density.interface.new_socket(name="Mask Highlights", in_out='INPUT', socket_type='NodeSocketFloat')
    mask_highlights_socket.default_value = 0.0
    mask_highlights_socket.min_value = -1.0
    mask_highlights_socket.max_value = 1.0
    mask_highlights_socket.subtype = 'FACTOR'
    mask_highlights_socket.attribute_domain = 'POINT'
    mask_highlights_socket.default_input = 'VALUE'
    mask_highlights_socket.structure_type = 'AUTO'

    # Initialize _rr_color_density nodes

    # Node Separate Color.001
    separate_color_001_6 = _rr_color_density.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_6.name = "Separate Color.001"
    separate_color_001_6.mode = 'HSV'
    separate_color_001_6.ycc_mode = 'ITUBT709'

    # Node Group Output
    group_output_27 = _rr_color_density.nodes.new("NodeGroupOutput")
    group_output_27.name = "Group Output"
    group_output_27.is_active_output = True

    # Node Group Input
    group_input_24 = _rr_color_density.nodes.new("NodeGroupInput")
    group_input_24.name = "Group Input"

    # Node Combine Color
    combine_color_10 = _rr_color_density.nodes.new("CompositorNodeCombineColor")
    combine_color_10.name = "Combine Color"
    combine_color_10.mode = 'HSV'
    combine_color_10.ycc_mode = 'ITUBT709'

    # Node Mix
    mix_18 = _rr_color_density.nodes.new("ShaderNodeMix")
    mix_18.name = "Mix"
    mix_18.blend_type = 'MIX'
    mix_18.clamp_factor = False
    mix_18.clamp_result = False
    mix_18.data_type = 'FLOAT'
    mix_18.factor_mode = 'UNIFORM'

    # Node Map Range
    map_range_16 = _rr_color_density.nodes.new("ShaderNodeMapRange")
    map_range_16.name = "Map Range"
    map_range_16.clamp = False
    map_range_16.data_type = 'FLOAT'
    map_range_16.interpolation_type = 'LINEAR'
    # From Min
    map_range_16.inputs[1].default_value = 0.0
    # From Max
    map_range_16.inputs[2].default_value = 1.0
    # To Min
    map_range_16.inputs[3].default_value = 1.0
    # To Max
    map_range_16.inputs[4].default_value = 0.0

    # Node Map Range.001
    map_range_001_15 = _rr_color_density.nodes.new("ShaderNodeMapRange")
    map_range_001_15.name = "Map Range.001"
    map_range_001_15.clamp = False
    map_range_001_15.data_type = 'FLOAT'
    map_range_001_15.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_15.inputs[1].default_value = -1.0
    # From Max
    map_range_001_15.inputs[2].default_value = 1.0
    # To Min
    map_range_001_15.inputs[3].default_value = 1.0
    # To Max
    map_range_001_15.inputs[4].default_value = 0.0

    # Node Math
    math_22 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_22.name = "Math"
    math_22.hide = True
    math_22.operation = 'MULTIPLY'
    math_22.use_clamp = False

    # Node Math.001
    math_001_18 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_001_18.name = "Math.001"
    math_001_18.hide = True
    math_001_18.operation = 'MULTIPLY'
    math_001_18.use_clamp = False

    # Node Math.002
    math_002_16 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_002_16.name = "Math.002"
    math_002_16.hide = True
    math_002_16.operation = 'MULTIPLY'
    math_002_16.use_clamp = False

    # Node Map Range.002
    map_range_002_12 = _rr_color_density.nodes.new("ShaderNodeMapRange")
    map_range_002_12.name = "Map Range.002"
    map_range_002_12.clamp = False
    map_range_002_12.data_type = 'FLOAT'
    map_range_002_12.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_12.inputs[1].default_value = 0.0
    # From Max
    map_range_002_12.inputs[2].default_value = 1.0
    # To Min
    map_range_002_12.inputs[3].default_value = 1.0
    # To Max
    map_range_002_12.inputs[4].default_value = 2.0

    # Node Math.003
    math_003_15 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_003_15.name = "Math.003"
    math_003_15.hide = True
    math_003_15.operation = 'MULTIPLY'
    math_003_15.use_clamp = False

    # Node Map Range.003
    map_range_003_9 = _rr_color_density.nodes.new("ShaderNodeMapRange")
    map_range_003_9.name = "Map Range.003"
    map_range_003_9.clamp = False
    map_range_003_9.data_type = 'FLOAT'
    map_range_003_9.interpolation_type = 'LINEAR'
    # From Min
    map_range_003_9.inputs[1].default_value = 0.0
    # From Max
    map_range_003_9.inputs[2].default_value = 1.0
    # To Min
    map_range_003_9.inputs[3].default_value = 1.0
    # To Max
    map_range_003_9.inputs[4].default_value = 0.0

    # Node Separate Color.002
    separate_color_002_4 = _rr_color_density.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_4.name = "Separate Color.002"
    separate_color_002_4.mode = 'YUV'
    separate_color_002_4.ycc_mode = 'ITUBT709'

    # Node Math.004
    math_004_14 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_004_14.name = "Math.004"
    math_004_14.hide = True
    math_004_14.operation = 'MULTIPLY'
    math_004_14.use_clamp = False

    # Node Math.005
    math_005_13 = _rr_color_density.nodes.new("ShaderNodeMath")
    math_005_13.name = "Math.005"
    math_005_13.operation = 'GREATER_THAN'
    math_005_13.use_clamp = False
    # Value_001
    math_005_13.inputs[1].default_value = 0.0

    # Set locations
    separate_color_001_6.location = (-704.2545776367188, 362.36834716796875)
    group_output_27.location = (1802.49072265625, 329.1618957519531)
    group_input_24.location = (-1063.1748046875, 90.76285552978516)
    combine_color_10.location = (1388.848876953125, 396.5477600097656)
    mix_18.location = (-150.1317138671875, -135.06956481933594)
    map_range_16.location = (-377.11407470703125, -273.31573486328125)
    map_range_001_15.location = (-699.7435302734375, -201.06756591796875)
    math_22.location = (76.15572357177734, 2.073812246322632)
    math_001_18.location = (326.8385009765625, -62.821533203125)
    math_002_16.location = (838.5537719726562, 184.43255615234375)
    map_range_002_12.location = (532.1033325195312, 30.933029174804688)
    math_003_15.location = (837.6513061523438, 107.44146728515625)
    map_range_003_9.location = (535.493408203125, -216.71392822265625)
    separate_color_002_4.location = (-704.0628051757812, -23.1894474029541)
    math_004_14.location = (-138.46429443359375, 141.04298400878906)
    math_005_13.location = (-437.6619567871094, 168.671630859375)

    # Set dimensions
    separate_color_001_6.width, separate_color_001_6.height = 140.0, 100.0
    group_output_27.width, group_output_27.height = 140.0, 100.0
    group_input_24.width, group_input_24.height = 140.0, 100.0
    combine_color_10.width, combine_color_10.height = 140.0, 100.0
    mix_18.width, mix_18.height = 140.0, 100.0
    map_range_16.width, map_range_16.height = 140.0, 100.0
    map_range_001_15.width, map_range_001_15.height = 140.0, 100.0
    math_22.width, math_22.height = 140.0, 100.0
    math_001_18.width, math_001_18.height = 140.0, 100.0
    math_002_16.width, math_002_16.height = 143.4638671875, 100.0
    map_range_002_12.width, map_range_002_12.height = 140.0, 100.0
    math_003_15.width, math_003_15.height = 140.0, 100.0
    map_range_003_9.width, map_range_003_9.height = 140.0, 100.0
    separate_color_002_4.width, separate_color_002_4.height = 140.0, 100.0
    math_004_14.width, math_004_14.height = 140.0, 100.0
    math_005_13.width, math_005_13.height = 140.0, 100.0

    # Initialize _rr_color_density links

    # separate_color_001_6.Red -> combine_color_10.Red
    _rr_color_density.links.new(separate_color_001_6.outputs[0], combine_color_10.inputs[0])
    # separate_color_001_6.Alpha -> combine_color_10.Alpha
    _rr_color_density.links.new(separate_color_001_6.outputs[3], combine_color_10.inputs[3])
    # group_input_24.Mask Highlights -> map_range_001_15.Value
    _rr_color_density.links.new(group_input_24.outputs[2], map_range_001_15.inputs[0])
    # map_range_001_15.Result -> mix_18.Factor
    _rr_color_density.links.new(map_range_001_15.outputs[0], mix_18.inputs[0])
    # math_22.Value -> math_001_18.Value
    _rr_color_density.links.new(math_22.outputs[0], math_001_18.inputs[0])
    # group_input_24.Strength -> math_001_18.Value
    _rr_color_density.links.new(group_input_24.outputs[1], math_001_18.inputs[1])
    # combine_color_10.Image -> group_output_27.Image
    _rr_color_density.links.new(combine_color_10.outputs[0], group_output_27.inputs[0])
    # separate_color_001_6.Green -> math_002_16.Value
    _rr_color_density.links.new(separate_color_001_6.outputs[1], math_002_16.inputs[0])
    # math_001_18.Value -> map_range_002_12.Value
    _rr_color_density.links.new(math_001_18.outputs[0], map_range_002_12.inputs[0])
    # map_range_002_12.Result -> math_002_16.Value
    _rr_color_density.links.new(map_range_002_12.outputs[0], math_002_16.inputs[1])
    # separate_color_001_6.Blue -> math_003_15.Value
    _rr_color_density.links.new(separate_color_001_6.outputs[2], math_003_15.inputs[0])
    # math_001_18.Value -> map_range_003_9.Value
    _rr_color_density.links.new(math_001_18.outputs[0], map_range_003_9.inputs[0])
    # map_range_003_9.Result -> math_003_15.Value
    _rr_color_density.links.new(map_range_003_9.outputs[0], math_003_15.inputs[1])
    # math_004_14.Value -> math_22.Value
    _rr_color_density.links.new(math_004_14.outputs[0], math_22.inputs[0])
    # group_input_24.Image -> separate_color_001_6.Image
    _rr_color_density.links.new(group_input_24.outputs[0], separate_color_001_6.inputs[0])
    # math_002_16.Value -> combine_color_10.Green
    _rr_color_density.links.new(math_002_16.outputs[0], combine_color_10.inputs[1])
    # map_range_16.Result -> mix_18.B
    _rr_color_density.links.new(map_range_16.outputs[0], mix_18.inputs[3])
    # mix_18.Result -> math_22.Value
    _rr_color_density.links.new(mix_18.outputs[0], math_22.inputs[1])
    # math_003_15.Value -> combine_color_10.Blue
    _rr_color_density.links.new(math_003_15.outputs[0], combine_color_10.inputs[2])
    # group_input_24.Image -> separate_color_002_4.Image
    _rr_color_density.links.new(group_input_24.outputs[0], separate_color_002_4.inputs[0])
    # separate_color_002_4.Red -> map_range_16.Value
    _rr_color_density.links.new(separate_color_002_4.outputs[0], map_range_16.inputs[0])
    # separate_color_002_4.Red -> mix_18.A
    _rr_color_density.links.new(separate_color_002_4.outputs[0], mix_18.inputs[2])
    # separate_color_001_6.Green -> math_004_14.Value
    _rr_color_density.links.new(separate_color_001_6.outputs[1], math_004_14.inputs[0])
    # separate_color_001_6.Blue -> math_005_13.Value
    _rr_color_density.links.new(separate_color_001_6.outputs[2], math_005_13.inputs[0])
    # math_005_13.Value -> math_004_14.Value
    _rr_color_density.links.new(math_005_13.outputs[0], math_004_14.inputs[1])

    return _rr_color_density


_rr_color_density = _rr_color_density_node_group()

def _rr_negative_bleed_node_group():
    """Initialize .RR_negative_bleed node group"""
    _rr_negative_bleed = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_negative_bleed")

    _rr_negative_bleed.color_tag = 'NONE'
    _rr_negative_bleed.description = ""
    _rr_negative_bleed.default_group_node_width = 140
    # _rr_negative_bleed interface

    # Socket Color
    color_socket_1 = _rr_negative_bleed.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
    color_socket_1.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    color_socket_1.attribute_domain = 'POINT'
    color_socket_1.default_input = 'VALUE'
    color_socket_1.structure_type = 'AUTO'

    # Socket Color
    color_socket_2 = _rr_negative_bleed.interface.new_socket(name="Color", in_out='INPUT', socket_type='NodeSocketColor')
    color_socket_2.default_value = (1.0, 1.0, 1.0, 1.0)
    color_socket_2.attribute_domain = 'POINT'
    color_socket_2.default_input = 'VALUE'
    color_socket_2.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_8 = _rr_negative_bleed.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_8.default_value = 1.0
    strength_socket_8.min_value = 0.0
    strength_socket_8.max_value = 1.0
    strength_socket_8.subtype = 'FACTOR'
    strength_socket_8.attribute_domain = 'POINT'
    strength_socket_8.description = "Adjusts the brightness of the glare"
    strength_socket_8.default_input = 'VALUE'
    strength_socket_8.structure_type = 'AUTO'

    # Socket Size
    size_socket_3 = _rr_negative_bleed.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketFloat')
    size_socket_3.default_value = 0.5
    size_socket_3.min_value = 0.0
    size_socket_3.max_value = 1.0
    size_socket_3.subtype = 'FACTOR'
    size_socket_3.attribute_domain = 'POINT'
    size_socket_3.description = "The size of the glare relative to the image. 1 means the glare covers the entire image, 0.5 means the glare covers half the image, and so on"
    size_socket_3.default_input = 'VALUE'
    size_socket_3.structure_type = 'AUTO'

    # Initialize _rr_negative_bleed nodes

    # Node Group Output
    group_output_28 = _rr_negative_bleed.nodes.new("NodeGroupOutput")
    group_output_28.name = "Group Output"
    group_output_28.is_active_output = True

    # Node Group Input
    group_input_25 = _rr_negative_bleed.nodes.new("NodeGroupInput")
    group_input_25.name = "Group Input"

    # Node Invert Color
    invert_color = _rr_negative_bleed.nodes.new("CompositorNodeInvert")
    invert_color.name = "Invert Color"
    invert_color.inputs[0].hide = True
    invert_color.inputs[2].hide = True
    invert_color.inputs[3].hide = True
    # Fac
    invert_color.inputs[0].default_value = 1.0
    # Invert Color
    invert_color.inputs[2].default_value = True
    # Invert Alpha
    invert_color.inputs[3].default_value = False

    # Node Glare
    glare_2 = _rr_negative_bleed.nodes.new("CompositorNodeGlare")
    glare_2.name = "Glare"
    glare_2.glare_type = 'BLOOM'
    glare_2.quality = 'HIGH'
    # Highlights Smoothness
    glare_2.inputs[2].default_value = 1.0
    # Clamp Highlights
    glare_2.inputs[3].default_value = False
    # Maximum Highlights
    glare_2.inputs[4].default_value = 10.0
    # Strength
    glare_2.inputs[5].default_value = 1.0
    # Saturation
    glare_2.inputs[6].default_value = 1.0
    # Tint
    glare_2.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Invert Color.001
    invert_color_001 = _rr_negative_bleed.nodes.new("CompositorNodeInvert")
    invert_color_001.name = "Invert Color.001"
    invert_color_001.inputs[0].hide = True
    invert_color_001.inputs[2].hide = True
    invert_color_001.inputs[3].hide = True
    # Fac
    invert_color_001.inputs[0].default_value = 1.0
    # Invert Color
    invert_color_001.inputs[2].default_value = True
    # Invert Alpha
    invert_color_001.inputs[3].default_value = False

    # Node Map Range
    map_range_17 = _rr_negative_bleed.nodes.new("ShaderNodeMapRange")
    map_range_17.name = "Map Range"
    map_range_17.clamp = True
    map_range_17.data_type = 'FLOAT'
    map_range_17.interpolation_type = 'LINEAR'
    # From Min
    map_range_17.inputs[1].default_value = 0.0
    # From Max
    map_range_17.inputs[2].default_value = 1.0
    # To Min
    map_range_17.inputs[3].default_value = 1.0
    # To Max
    map_range_17.inputs[4].default_value = 0.0

    # Node Separate Color
    separate_color_9 = _rr_negative_bleed.nodes.new("CompositorNodeSeparateColor")
    separate_color_9.name = "Separate Color"
    separate_color_9.mode = 'RGB'
    separate_color_9.ycc_mode = 'ITUBT709'
    separate_color_9.outputs[0].hide = True
    separate_color_9.outputs[1].hide = True
    separate_color_9.outputs[2].hide = True

    # Node Vector Math
    vector_math_1 = _rr_negative_bleed.nodes.new("ShaderNodeVectorMath")
    vector_math_1.name = "Vector Math"
    vector_math_1.operation = 'MULTIPLY'

    # Node Vector Math.001
    vector_math_001 = _rr_negative_bleed.nodes.new("ShaderNodeVectorMath")
    vector_math_001.name = "Vector Math.001"
    vector_math_001.operation = 'ADD'

    # Node Mix
    mix_19 = _rr_negative_bleed.nodes.new("ShaderNodeMix")
    mix_19.name = "Mix"
    mix_19.blend_type = 'SUBTRACT'
    mix_19.clamp_factor = True
    mix_19.clamp_result = True
    mix_19.data_type = 'RGBA'
    mix_19.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_19.inputs[0].default_value = 1.0

    # Node Map Range.001
    map_range_001_16 = _rr_negative_bleed.nodes.new("ShaderNodeMapRange")
    map_range_001_16.name = "Map Range.001"
    map_range_001_16.clamp = True
    map_range_001_16.data_type = 'FLOAT'
    map_range_001_16.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_16.inputs[1].default_value = 0.0
    # From Max
    map_range_001_16.inputs[2].default_value = 1.0
    # To Min
    map_range_001_16.inputs[3].default_value = 0.05000000074505806
    # To Max
    map_range_001_16.inputs[4].default_value = 1.0

    # Node Group Input.001
    group_input_001_9 = _rr_negative_bleed.nodes.new("NodeGroupInput")
    group_input_001_9.name = "Group Input.001"

    # Node Mix.001
    mix_001_13 = _rr_negative_bleed.nodes.new("ShaderNodeMix")
    mix_001_13.name = "Mix.001"
    mix_001_13.blend_type = 'MIX'
    mix_001_13.clamp_factor = True
    mix_001_13.clamp_result = True
    mix_001_13.data_type = 'RGBA'
    mix_001_13.factor_mode = 'UNIFORM'

    # Node Float Curve.001
    float_curve_001_2 = _rr_negative_bleed.nodes.new("ShaderNodeFloatCurve")
    float_curve_001_2.name = "Float Curve.001"
    # Mapping settings
    float_curve_001_2.mapping.extend = 'EXTRAPOLATED'
    float_curve_001_2.mapping.tone = 'STANDARD'
    float_curve_001_2.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_001_2.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_001_2.mapping.clip_min_x = 0.0
    float_curve_001_2.mapping.clip_min_y = 0.0
    float_curve_001_2.mapping.clip_max_x = 1.0
    float_curve_001_2.mapping.clip_max_y = 1.0
    float_curve_001_2.mapping.use_clip = True
    # Curve 0
    float_curve_001_2_curve_0 = float_curve_001_2.mapping.curves[0]
    float_curve_001_2_curve_0_point_0 = float_curve_001_2_curve_0.points[0]
    float_curve_001_2_curve_0_point_0.location = (0.0, 0.0)
    float_curve_001_2_curve_0_point_0.handle_type = 'AUTO'
    float_curve_001_2_curve_0_point_1 = float_curve_001_2_curve_0.points[1]
    float_curve_001_2_curve_0_point_1.location = (0.25, 0.75)
    float_curve_001_2_curve_0_point_1.handle_type = 'AUTO'
    float_curve_001_2_curve_0_point_2 = float_curve_001_2_curve_0.points.new(1.0, 1.0)
    float_curve_001_2_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_001_2.mapping.update()
    # Factor
    float_curve_001_2.inputs[0].default_value = 1.0

    # Set locations
    group_output_28.location = (1230.2132568359375, 140.1040496826172)
    group_input_25.location = (-1379.0806884765625, -289.0778503417969)
    invert_color.location = (-1090.08154296875, 36.039363861083984)
    glare_2.location = (-293.2492370605469, -129.63917541503906)
    invert_color_001.location = (461.1716613769531, 58.10023880004883)
    map_range_17.location = (-551.763916015625, -218.20089721679688)
    separate_color_9.location = (-829.3838500976562, -97.95500946044922)
    vector_math_1.location = (-553.9154663085938, -33.71824645996094)
    vector_math_001.location = (247.30323791503906, 80.67707824707031)
    mix_19.location = (-29.086008071899414, -41.391117095947266)
    map_range_001_16.location = (-551.1838989257812, -521.6072998046875)
    group_input_001_9.location = (251.36241149902344, 255.27149963378906)
    mix_001_13.location = (999.0891723632812, 222.3372802734375)
    float_curve_001_2.location = (556.8165893554688, 571.2718505859375)

    # Set dimensions
    group_output_28.width, group_output_28.height = 140.0, 100.0
    group_input_25.width, group_input_25.height = 140.0, 100.0
    invert_color.width, invert_color.height = 140.0, 100.0
    glare_2.width, glare_2.height = 168.2098388671875, 100.0
    invert_color_001.width, invert_color_001.height = 140.0, 100.0
    map_range_17.width, map_range_17.height = 140.0, 100.0
    separate_color_9.width, separate_color_9.height = 140.0, 100.0
    vector_math_1.width, vector_math_1.height = 140.0, 100.0
    vector_math_001.width, vector_math_001.height = 140.0, 100.0
    mix_19.width, mix_19.height = 140.0, 100.0
    map_range_001_16.width, map_range_001_16.height = 140.0, 100.0
    group_input_001_9.width, group_input_001_9.height = 140.0, 100.0
    mix_001_13.width, mix_001_13.height = 140.0, 100.0
    float_curve_001_2.width, float_curve_001_2.height = 240.0, 100.0

    # Initialize _rr_negative_bleed links

    # group_input_25.Color -> invert_color.Color
    _rr_negative_bleed.links.new(group_input_25.outputs[0], invert_color.inputs[1])
    # mix_001_13.Result -> group_output_28.Color
    _rr_negative_bleed.links.new(mix_001_13.outputs[2], group_output_28.inputs[0])
    # group_input_25.Strength -> map_range_17.Value
    _rr_negative_bleed.links.new(group_input_25.outputs[1], map_range_17.inputs[0])
    # map_range_17.Result -> glare_2.Threshold
    _rr_negative_bleed.links.new(map_range_17.outputs[0], glare_2.inputs[1])
    # map_range_001_16.Result -> glare_2.Size
    _rr_negative_bleed.links.new(map_range_001_16.outputs[0], glare_2.inputs[8])
    # invert_color.Color -> separate_color_9.Image
    _rr_negative_bleed.links.new(invert_color.outputs[0], separate_color_9.inputs[0])
    # separate_color_9.Alpha -> vector_math_1.Vector
    _rr_negative_bleed.links.new(separate_color_9.outputs[3], vector_math_1.inputs[1])
    # vector_math_1.Vector -> glare_2.Image
    _rr_negative_bleed.links.new(vector_math_1.outputs[0], glare_2.inputs[0])
    # invert_color.Color -> vector_math_1.Vector
    _rr_negative_bleed.links.new(invert_color.outputs[0], vector_math_1.inputs[0])
    # glare_2.Glare -> mix_19.A
    _rr_negative_bleed.links.new(glare_2.outputs[1], mix_19.inputs[6])
    # glare_2.Highlights -> mix_19.B
    _rr_negative_bleed.links.new(glare_2.outputs[2], mix_19.inputs[7])
    # mix_19.Result -> vector_math_001.Vector
    _rr_negative_bleed.links.new(mix_19.outputs[2], vector_math_001.inputs[1])
    # invert_color.Color -> vector_math_001.Vector
    _rr_negative_bleed.links.new(invert_color.outputs[0], vector_math_001.inputs[0])
    # vector_math_001.Vector -> invert_color_001.Color
    _rr_negative_bleed.links.new(vector_math_001.outputs[0], invert_color_001.inputs[1])
    # group_input_25.Size -> map_range_001_16.Value
    _rr_negative_bleed.links.new(group_input_25.outputs[2], map_range_001_16.inputs[0])
    # invert_color_001.Color -> mix_001_13.B
    _rr_negative_bleed.links.new(invert_color_001.outputs[0], mix_001_13.inputs[7])
    # group_input_001_9.Color -> mix_001_13.A
    _rr_negative_bleed.links.new(group_input_001_9.outputs[0], mix_001_13.inputs[6])
    # group_input_001_9.Strength -> float_curve_001_2.Value
    _rr_negative_bleed.links.new(group_input_001_9.outputs[1], float_curve_001_2.inputs[1])
    # float_curve_001_2.Value -> mix_001_13.Factor
    _rr_negative_bleed.links.new(float_curve_001_2.outputs[0], mix_001_13.inputs[0])

    return _rr_negative_bleed


_rr_negative_bleed = _rr_negative_bleed_node_group()

def _rr_grain_fast_node_group():
    """Initialize .RR_grain_fast node group"""
    _rr_grain_fast = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_grain_fast")

    _rr_grain_fast.color_tag = 'NONE'
    _rr_grain_fast.description = ""
    _rr_grain_fast.default_group_node_width = 140
    # _rr_grain_fast interface

    # Socket Image
    image_socket_43 = _rr_grain_fast.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_43.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_43.attribute_domain = 'POINT'
    image_socket_43.default_input = 'VALUE'
    image_socket_43.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_12 = _rr_grain_fast.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_12.default_value = 1.0
    factor_socket_12.min_value = 0.0
    factor_socket_12.max_value = 1.0
    factor_socket_12.subtype = 'FACTOR'
    factor_socket_12.attribute_domain = 'POINT'
    factor_socket_12.default_input = 'VALUE'
    factor_socket_12.structure_type = 'AUTO'

    # Socket Image
    image_socket_44 = _rr_grain_fast.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_44.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_44.attribute_domain = 'POINT'
    image_socket_44.default_input = 'VALUE'
    image_socket_44.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_9 = _rr_grain_fast.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_9.default_value = 1.0
    strength_socket_9.min_value = 0.0
    strength_socket_9.max_value = 1.0
    strength_socket_9.subtype = 'FACTOR'
    strength_socket_9.attribute_domain = 'POINT'
    strength_socket_9.default_input = 'VALUE'
    strength_socket_9.structure_type = 'AUTO'

    # Socket Scale
    scale_socket = _rr_grain_fast.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket.default_value = 5.0
    scale_socket.min_value = 1.0
    scale_socket.max_value = 20.0
    scale_socket.subtype = 'FACTOR'
    scale_socket.attribute_domain = 'POINT'
    scale_socket.default_input = 'VALUE'
    scale_socket.structure_type = 'AUTO'

    # Socket Detail
    detail_socket = _rr_grain_fast.interface.new_socket(name="Detail", in_out='INPUT', socket_type='NodeSocketFloat')
    detail_socket.default_value = 0.0
    detail_socket.min_value = 0.0
    detail_socket.max_value = 6.0
    detail_socket.subtype = 'FACTOR'
    detail_socket.attribute_domain = 'POINT'
    detail_socket.default_input = 'VALUE'
    detail_socket.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_4 = _rr_grain_fast.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_4.default_value = 1.0
    saturation_socket_4.min_value = 0.0
    saturation_socket_4.max_value = 1.0
    saturation_socket_4.subtype = 'FACTOR'
    saturation_socket_4.attribute_domain = 'POINT'
    saturation_socket_4.default_input = 'VALUE'
    saturation_socket_4.structure_type = 'AUTO'

    # Socket Animate
    animate_socket = _rr_grain_fast.interface.new_socket(name="Animate", in_out='INPUT', socket_type='NodeSocketBool')
    animate_socket.default_value = False
    animate_socket.attribute_domain = 'POINT'
    animate_socket.default_input = 'VALUE'
    animate_socket.structure_type = 'AUTO'

    # Initialize _rr_grain_fast nodes

    # Node Group Output
    group_output_29 = _rr_grain_fast.nodes.new("NodeGroupOutput")
    group_output_29.name = "Group Output"
    group_output_29.is_active_output = True

    # Node Scene Time
    scene_time = _rr_grain_fast.nodes.new("CompositorNodeSceneTime")
    scene_time.name = "Scene Time"

    # Node Math.002
    math_002_17 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_002_17.name = "Math.002"
    math_002_17.operation = 'MULTIPLY'
    math_002_17.use_clamp = False
    # Value_001
    math_002_17.inputs[1].default_value = 10.0

    # Node Soft Light
    soft_light = _rr_grain_fast.nodes.new("ShaderNodeMix")
    soft_light.name = "Soft Light"
    soft_light.blend_type = 'SOFT_LIGHT'
    soft_light.clamp_factor = False
    soft_light.clamp_result = False
    soft_light.data_type = 'RGBA'
    soft_light.factor_mode = 'UNIFORM'

    # Node Group Input
    group_input_26 = _rr_grain_fast.nodes.new("NodeGroupInput")
    group_input_26.name = "Group Input"

    # Node Voronoi Texture.001
    voronoi_texture_001 = _rr_grain_fast.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture_001.name = "Voronoi Texture.001"
    voronoi_texture_001.distance = 'EUCLIDEAN'
    voronoi_texture_001.feature = 'F1'
    voronoi_texture_001.normalize = True
    voronoi_texture_001.voronoi_dimensions = '4D'
    # Vector
    voronoi_texture_001.inputs[0].default_value = (0.0, 0.0, 0.0)
    # Roughness
    voronoi_texture_001.inputs[4].default_value = 0.75
    # Lacunarity
    voronoi_texture_001.inputs[5].default_value = 0.75
    # Randomness
    voronoi_texture_001.inputs[8].default_value = 1.0

    # Node Math.003
    math_003_16 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_003_16.name = "Math.003"
    math_003_16.operation = 'MULTIPLY'
    math_003_16.use_clamp = False
    # Value_001
    math_003_16.inputs[1].default_value = 50.0

    # Node Reroute.001
    reroute_001_11 = _rr_grain_fast.nodes.new("NodeReroute")
    reroute_001_11.name = "Reroute.001"
    reroute_001_11.socket_idname = "NodeSocketColor"
    # Node Math
    math_23 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_23.name = "Math"
    math_23.hide = True
    math_23.operation = 'MULTIPLY'
    math_23.use_clamp = False

    # Node Separate Color
    separate_color_10 = _rr_grain_fast.nodes.new("CompositorNodeSeparateColor")
    separate_color_10.name = "Separate Color"
    separate_color_10.mode = 'YUV'
    separate_color_10.ycc_mode = 'ITUBT709'
    separate_color_10.outputs[1].hide = True
    separate_color_10.outputs[2].hide = True
    separate_color_10.outputs[3].hide = True

    # Node Mix
    mix_20 = _rr_grain_fast.nodes.new("ShaderNodeMix")
    mix_20.name = "Mix"
    mix_20.blend_type = 'MIX'
    mix_20.clamp_factor = True
    mix_20.clamp_result = False
    mix_20.data_type = 'RGBA'
    mix_20.factor_mode = 'UNIFORM'

    # Node Mix.001
    mix_001_14 = _rr_grain_fast.nodes.new("ShaderNodeMix")
    mix_001_14.name = "Mix.001"
    mix_001_14.blend_type = 'MIX'
    mix_001_14.clamp_factor = True
    mix_001_14.clamp_result = False
    mix_001_14.data_type = 'FLOAT'
    mix_001_14.factor_mode = 'UNIFORM'
    # A_Float
    mix_001_14.inputs[2].default_value = 0.0

    # Node Math.001
    math_001_19 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_001_19.name = "Math.001"
    math_001_19.hide = True
    math_001_19.operation = 'MULTIPLY'
    math_001_19.use_clamp = False

    # Node Math.004
    math_004_15 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_004_15.name = "Math.004"
    math_004_15.operation = 'LESS_THAN'
    math_004_15.use_clamp = False
    # Value_001
    math_004_15.inputs[1].default_value = 0.3499999940395355

    # Node Math.005
    math_005_14 = _rr_grain_fast.nodes.new("ShaderNodeMath")
    math_005_14.name = "Math.005"
    math_005_14.operation = 'SUBTRACT'
    math_005_14.use_clamp = False
    # Value_001
    math_005_14.inputs[1].default_value = 1.0

    # Set locations
    group_output_29.location = (1017.967041015625, -27.382266998291016)
    scene_time.location = (-1389.043701171875, -773.0946044921875)
    math_002_17.location = (-1179.5035400390625, -774.7172241210938)
    soft_light.location = (636.4383544921875, -19.06692886352539)
    group_input_26.location = (-1601.2677001953125, -241.35887145996094)
    voronoi_texture_001.location = (-418.4641418457031, -444.1205749511719)
    math_003_16.location = (-724.0178833007812, -639.5925903320312)
    reroute_001_11.location = (-200.0, -200.0)
    math_23.location = (-333.3213195800781, 1.8867756128311157)
    separate_color_10.location = (-56.9005241394043, -320.6164855957031)
    mix_20.location = (173.951904296875, -228.46580505371094)
    mix_001_14.location = (-725.5336303710938, -449.3686218261719)
    math_001_19.location = (202.2392578125, -5.748194217681885)
    math_004_15.location = (-50.389129638671875, -30.80449867248535)
    math_005_14.location = (-724.0178833007812, -791.909912109375)

    # Set dimensions
    group_output_29.width, group_output_29.height = 140.0, 100.0
    scene_time.width, scene_time.height = 140.0, 100.0
    math_002_17.width, math_002_17.height = 140.0, 100.0
    soft_light.width, soft_light.height = 140.0, 100.0
    group_input_26.width, group_input_26.height = 140.0, 100.0
    voronoi_texture_001.width, voronoi_texture_001.height = 220.0, 100.0
    math_003_16.width, math_003_16.height = 140.0, 100.0
    reroute_001_11.width, reroute_001_11.height = 20.0, 100.0
    math_23.width, math_23.height = 140.0, 100.0
    separate_color_10.width, separate_color_10.height = 140.0, 100.0
    mix_20.width, mix_20.height = 140.0, 100.0
    mix_001_14.width, mix_001_14.height = 140.0, 100.0
    math_001_19.width, math_001_19.height = 140.0, 100.0
    math_004_15.width, math_004_15.height = 140.0, 100.0
    math_005_14.width, math_005_14.height = 140.0, 100.0

    # Initialize _rr_grain_fast links

    # soft_light.Result -> group_output_29.Image
    _rr_grain_fast.links.new(soft_light.outputs[2], group_output_29.inputs[0])
    # scene_time.Frame -> math_002_17.Value
    _rr_grain_fast.links.new(scene_time.outputs[1], math_002_17.inputs[0])
    # reroute_001_11.Output -> soft_light.A
    _rr_grain_fast.links.new(reroute_001_11.outputs[0], soft_light.inputs[6])
    # group_input_26.Scale -> math_003_16.Value
    _rr_grain_fast.links.new(group_input_26.outputs[3], math_003_16.inputs[0])
    # math_003_16.Value -> voronoi_texture_001.Scale
    _rr_grain_fast.links.new(math_003_16.outputs[0], voronoi_texture_001.inputs[2])
    # group_input_26.Image -> reroute_001_11.Input
    _rr_grain_fast.links.new(group_input_26.outputs[1], reroute_001_11.inputs[0])
    # group_input_26.Strength -> math_23.Value
    _rr_grain_fast.links.new(group_input_26.outputs[2], math_23.inputs[1])
    # group_input_26.Factor -> math_23.Value
    _rr_grain_fast.links.new(group_input_26.outputs[0], math_23.inputs[0])
    # voronoi_texture_001.Color -> separate_color_10.Image
    _rr_grain_fast.links.new(voronoi_texture_001.outputs[1], separate_color_10.inputs[0])
    # group_input_26.Saturation -> mix_20.Factor
    _rr_grain_fast.links.new(group_input_26.outputs[5], mix_20.inputs[0])
    # voronoi_texture_001.Color -> mix_20.B
    _rr_grain_fast.links.new(voronoi_texture_001.outputs[1], mix_20.inputs[7])
    # separate_color_10.Red -> mix_20.A
    _rr_grain_fast.links.new(separate_color_10.outputs[0], mix_20.inputs[6])
    # mix_20.Result -> soft_light.B
    _rr_grain_fast.links.new(mix_20.outputs[2], soft_light.inputs[7])
    # mix_001_14.Result -> voronoi_texture_001.W
    _rr_grain_fast.links.new(mix_001_14.outputs[0], voronoi_texture_001.inputs[1])
    # group_input_26.Animate -> mix_001_14.Factor
    _rr_grain_fast.links.new(group_input_26.outputs[6], mix_001_14.inputs[0])
    # math_001_19.Value -> soft_light.Factor
    _rr_grain_fast.links.new(math_001_19.outputs[0], soft_light.inputs[0])
    # math_23.Value -> math_001_19.Value
    _rr_grain_fast.links.new(math_23.outputs[0], math_001_19.inputs[0])
    # voronoi_texture_001.Distance -> math_004_15.Value
    _rr_grain_fast.links.new(voronoi_texture_001.outputs[0], math_004_15.inputs[0])
    # math_004_15.Value -> math_001_19.Value
    _rr_grain_fast.links.new(math_004_15.outputs[0], math_001_19.inputs[1])
    # group_input_26.Detail -> math_005_14.Value
    _rr_grain_fast.links.new(group_input_26.outputs[4], math_005_14.inputs[0])
    # math_005_14.Value -> voronoi_texture_001.Detail
    _rr_grain_fast.links.new(math_005_14.outputs[0], voronoi_texture_001.inputs[3])
    # math_002_17.Value -> mix_001_14.B
    _rr_grain_fast.links.new(math_002_17.outputs[0], mix_001_14.inputs[3])

    return _rr_grain_fast


_rr_grain_fast = _rr_grain_fast_node_group()

def _rr_grain_layer_node_group():
    """Initialize .RR_grain_layer node group"""
    _rr_grain_layer = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_grain_layer")

    _rr_grain_layer.color_tag = 'NONE'
    _rr_grain_layer.description = ""
    _rr_grain_layer.default_group_node_width = 140
    # _rr_grain_layer interface

    # Socket Result
    result_socket_2 = _rr_grain_layer.interface.new_socket(name="Result", in_out='OUTPUT', socket_type='NodeSocketColor')
    result_socket_2.default_value = (0.0, 0.0, 0.0, 0.0)
    result_socket_2.attribute_domain = 'POINT'
    result_socket_2.default_input = 'VALUE'
    result_socket_2.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_13 = _rr_grain_layer.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_13.default_value = 0.5
    factor_socket_13.min_value = -10000.0
    factor_socket_13.max_value = 10000.0
    factor_socket_13.subtype = 'NONE'
    factor_socket_13.attribute_domain = 'POINT'
    factor_socket_13.default_input = 'VALUE'
    factor_socket_13.structure_type = 'AUTO'

    # Socket Image
    image_socket_45 = _rr_grain_layer.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_45.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_45.attribute_domain = 'POINT'
    image_socket_45.hide_value = True
    image_socket_45.default_input = 'VALUE'
    image_socket_45.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_10 = _rr_grain_layer.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_10.default_value = 0.5
    strength_socket_10.min_value = -10000.0
    strength_socket_10.max_value = 10000.0
    strength_socket_10.subtype = 'NONE'
    strength_socket_10.attribute_domain = 'POINT'
    strength_socket_10.default_input = 'VALUE'
    strength_socket_10.structure_type = 'AUTO'

    # Socket Scale
    scale_socket_1 = _rr_grain_layer.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket_1.default_value = 0.5
    scale_socket_1.min_value = -10000.0
    scale_socket_1.max_value = 10000.0
    scale_socket_1.subtype = 'NONE'
    scale_socket_1.attribute_domain = 'POINT'
    scale_socket_1.default_input = 'VALUE'
    scale_socket_1.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_5 = _rr_grain_layer.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_5.default_value = 0.25
    saturation_socket_5.min_value = 0.0
    saturation_socket_5.max_value = 1.0
    saturation_socket_5.subtype = 'FACTOR'
    saturation_socket_5.attribute_domain = 'POINT'
    saturation_socket_5.description = "Amount of mixing between the A and B inputs"
    saturation_socket_5.default_input = 'VALUE'
    saturation_socket_5.structure_type = 'AUTO'

    # Socket Animate
    animate_socket_1 = _rr_grain_layer.interface.new_socket(name="Animate", in_out='INPUT', socket_type='NodeSocketBool')
    animate_socket_1.default_value = False
    animate_socket_1.attribute_domain = 'POINT'
    animate_socket_1.default_input = 'VALUE'
    animate_socket_1.structure_type = 'AUTO'

    # Initialize _rr_grain_layer nodes

    # Node Group Output
    group_output_30 = _rr_grain_layer.nodes.new("NodeGroupOutput")
    group_output_30.name = "Group Output"
    group_output_30.is_active_output = True

    # Node Group Input
    group_input_27 = _rr_grain_layer.nodes.new("NodeGroupInput")
    group_input_27.name = "Group Input"

    # Node Math.008
    math_008_10 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_008_10.name = "Math.008"
    math_008_10.hide = True
    math_008_10.operation = 'MULTIPLY'
    math_008_10.use_clamp = False

    # Node Mix
    mix_21 = _rr_grain_layer.nodes.new("ShaderNodeMix")
    mix_21.name = "Mix"
    mix_21.blend_type = 'SOFT_LIGHT'
    mix_21.clamp_factor = False
    mix_21.clamp_result = False
    mix_21.data_type = 'RGBA'
    mix_21.factor_mode = 'UNIFORM'

    # Node Scene Time.001
    scene_time_001 = _rr_grain_layer.nodes.new("CompositorNodeSceneTime")
    scene_time_001.name = "Scene Time.001"

    # Node Switch
    switch_10 = _rr_grain_layer.nodes.new("CompositorNodeSwitch")
    switch_10.name = "Switch"
    # Off
    switch_10.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Math.007
    math_007_11 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_007_11.name = "Math.007"
    math_007_11.hide = True
    math_007_11.operation = 'ADD'
    math_007_11.use_clamp = False

    # Node Frame
    frame_15 = _rr_grain_layer.nodes.new("NodeFrame")
    frame_15.label = "Noise Base"
    frame_15.name = "Frame"
    frame_15.label_size = 20
    frame_15.shrink = True

    # Node Reroute.007
    reroute_007_5 = _rr_grain_layer.nodes.new("NodeReroute")
    reroute_007_5.name = "Reroute.007"
    reroute_007_5.socket_idname = "NodeSocketColor"
    # Node Frame.002
    frame_002_11 = _rr_grain_layer.nodes.new("NodeFrame")
    frame_002_11.label = "Displacement"
    frame_002_11.name = "Frame.002"
    frame_002_11.label_size = 20
    frame_002_11.shrink = True

    # Node Math.012
    math_012_6 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_012_6.name = "Math.012"
    math_012_6.hide = True
    math_012_6.operation = 'ADD'
    math_012_6.use_clamp = False
    # Value_001
    math_012_6.inputs[1].default_value = 0.5

    # Node Separate Color.001
    separate_color_001_7 = _rr_grain_layer.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_7.name = "Separate Color.001"
    separate_color_001_7.mode = 'YUV'
    separate_color_001_7.ycc_mode = 'ITUBT709'
    separate_color_001_7.outputs[1].hide = True
    separate_color_001_7.outputs[2].hide = True
    separate_color_001_7.outputs[3].hide = True

    # Node Mix.003
    mix_003_3 = _rr_grain_layer.nodes.new("ShaderNodeMix")
    mix_003_3.name = "Mix.003"
    mix_003_3.blend_type = 'MIX'
    mix_003_3.clamp_factor = False
    mix_003_3.clamp_result = False
    mix_003_3.data_type = 'RGBA'
    mix_003_3.factor_mode = 'UNIFORM'

    # Node Frame.001
    frame_001_12 = _rr_grain_layer.nodes.new("NodeFrame")
    frame_001_12.label = "Noise Overlay"
    frame_001_12.name = "Frame.001"
    frame_001_12.label_size = 20
    frame_001_12.shrink = True

    # Node Reroute.003
    reroute_003_10 = _rr_grain_layer.nodes.new("NodeReroute")
    reroute_003_10.name = "Reroute.003"
    reroute_003_10.socket_idname = "NodeSocketColor"
    # Node Group Input.001
    group_input_001_10 = _rr_grain_layer.nodes.new("NodeGroupInput")
    group_input_001_10.name = "Group Input.001"
    group_input_001_10.outputs[0].hide = True
    group_input_001_10.outputs[2].hide = True
    group_input_001_10.outputs[3].hide = True
    group_input_001_10.outputs[4].hide = True
    group_input_001_10.outputs[5].hide = True
    group_input_001_10.outputs[6].hide = True

    # Node Group Input.002
    group_input_002_6 = _rr_grain_layer.nodes.new("NodeGroupInput")
    group_input_002_6.name = "Group Input.002"
    group_input_002_6.outputs[1].hide = True
    group_input_002_6.outputs[3].hide = True
    group_input_002_6.outputs[5].hide = True
    group_input_002_6.outputs[6].hide = True

    # Node Voronoi Texture.003
    voronoi_texture_003 = _rr_grain_layer.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture_003.name = "Voronoi Texture.003"
    voronoi_texture_003.distance = 'EUCLIDEAN'
    voronoi_texture_003.feature = 'F1'
    voronoi_texture_003.normalize = True
    voronoi_texture_003.voronoi_dimensions = '4D'
    # Detail
    voronoi_texture_003.inputs[3].default_value = 0.0
    # Roughness
    voronoi_texture_003.inputs[4].default_value = 1.0
    # Lacunarity
    voronoi_texture_003.inputs[5].default_value = 1.2599999904632568
    # Randomness
    voronoi_texture_003.inputs[8].default_value = 1.0

    # Node Voronoi Texture.004
    voronoi_texture_004 = _rr_grain_layer.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture_004.name = "Voronoi Texture.004"
    voronoi_texture_004.distance = 'EUCLIDEAN'
    voronoi_texture_004.feature = 'F1'
    voronoi_texture_004.normalize = True
    voronoi_texture_004.voronoi_dimensions = '4D'
    # Detail
    voronoi_texture_004.inputs[3].default_value = 0.0
    # Roughness
    voronoi_texture_004.inputs[4].default_value = 0.5
    # Lacunarity
    voronoi_texture_004.inputs[5].default_value = 1.5
    # Randomness
    voronoi_texture_004.inputs[8].default_value = 1.0

    # Node Map Range.005
    map_range_005_7 = _rr_grain_layer.nodes.new("ShaderNodeMapRange")
    map_range_005_7.name = "Map Range.005"
    map_range_005_7.clamp = True
    map_range_005_7.data_type = 'FLOAT'
    map_range_005_7.interpolation_type = 'LINEAR'
    # From Min
    map_range_005_7.inputs[1].default_value = 0.0
    # From Max
    map_range_005_7.inputs[2].default_value = 1.0
    # To Min
    map_range_005_7.inputs[3].default_value = 1.0

    # Node Math.015
    math_015_5 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_015_5.name = "Math.015"
    math_015_5.operation = 'MULTIPLY'
    math_015_5.use_clamp = False
    # Value_001
    math_015_5.inputs[1].default_value = 50.0

    # Node Math.018
    math_018_4 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_018_4.name = "Math.018"
    math_018_4.operation = 'MULTIPLY'
    math_018_4.use_clamp = False
    # Value_001
    math_018_4.inputs[1].default_value = 100.0

    # Node Mix.017
    mix_017 = _rr_grain_layer.nodes.new("ShaderNodeMix")
    mix_017.name = "Mix.017"
    mix_017.blend_type = 'MIX'
    mix_017.clamp_factor = True
    mix_017.clamp_result = False
    mix_017.data_type = 'RGBA'
    mix_017.factor_mode = 'UNIFORM'

    # Node Vector Math.004
    vector_math_004 = _rr_grain_layer.nodes.new("ShaderNodeVectorMath")
    vector_math_004.name = "Vector Math.004"
    vector_math_004.operation = 'ADD'
    # Vector_001
    vector_math_004.inputs[1].default_value = (0.0, 0.0, 1.0)

    # Node Map UV.003
    map_uv_003 = _rr_grain_layer.nodes.new("CompositorNodeMapUV")
    map_uv_003.name = "Map UV.003"
    map_uv_003.filter_type = 'ANISOTROPIC'

    # Node Image Coordinates.002
    image_coordinates_002 = _rr_grain_layer.nodes.new("CompositorNodeImageCoordinates")
    image_coordinates_002.name = "Image Coordinates.002"

    # Node Vector Math.005
    vector_math_005 = _rr_grain_layer.nodes.new("ShaderNodeVectorMath")
    vector_math_005.name = "Vector Math.005"
    vector_math_005.hide = True
    vector_math_005.operation = 'DISTANCE'

    # Node Math.003
    math_003_17 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_003_17.name = "Math.003"
    math_003_17.operation = 'DIVIDE'
    math_003_17.use_clamp = False
    # Value
    math_003_17.inputs[0].default_value = 1.0

    # Node Reroute.004
    reroute_004_8 = _rr_grain_layer.nodes.new("NodeReroute")
    reroute_004_8.name = "Reroute.004"
    reroute_004_8.socket_idname = "NodeSocketFloat"
    # Node Math
    math_24 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_24.name = "Math"
    math_24.hide = True
    math_24.operation = 'MULTIPLY'
    math_24.use_clamp = False

    # Node Math.002
    math_002_18 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_002_18.name = "Math.002"
    math_002_18.hide = True
    math_002_18.operation = 'MULTIPLY'
    math_002_18.use_clamp = False

    # Node Value
    value_2 = _rr_grain_layer.nodes.new("ShaderNodeValue")
    value_2.name = "Value"

    value_2.outputs[0].default_value = 0.7300004959106445
    # Node Mix.011
    mix_011 = _rr_grain_layer.nodes.new("ShaderNodeMix")
    mix_011.name = "Mix.011"
    mix_011.blend_type = 'MIX'
    mix_011.clamp_factor = True
    mix_011.clamp_result = False
    mix_011.data_type = 'RGBA'
    mix_011.factor_mode = 'UNIFORM'
    # A_Color
    mix_011.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)

    # Node Math.004
    math_004_16 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_004_16.name = "Math.004"
    math_004_16.operation = 'MULTIPLY'
    math_004_16.use_clamp = False

    # Node Math.005
    math_005_15 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_005_15.name = "Math.005"
    math_005_15.operation = 'ADD'
    math_005_15.use_clamp = False
    # Value_001
    math_005_15.inputs[1].default_value = 1.0

    # Node Reroute
    reroute_17 = _rr_grain_layer.nodes.new("NodeReroute")
    reroute_17.name = "Reroute"
    reroute_17.socket_idname = "NodeSocketVector2D"
    # Node Reroute.001
    reroute_001_12 = _rr_grain_layer.nodes.new("NodeReroute")
    reroute_001_12.name = "Reroute.001"
    reroute_001_12.socket_idname = "NodeSocketVector2D"
    # Node Map Range.001
    map_range_001_17 = _rr_grain_layer.nodes.new("ShaderNodeMapRange")
    map_range_001_17.name = "Map Range.001"
    map_range_001_17.clamp = True
    map_range_001_17.data_type = 'FLOAT'
    map_range_001_17.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_17.inputs[1].default_value = 0.0
    # To Max
    map_range_001_17.inputs[4].default_value = 0.0

    # Node Math.006
    math_006_12 = _rr_grain_layer.nodes.new("ShaderNodeMath")
    math_006_12.name = "Math.006"
    math_006_12.operation = 'LESS_THAN'
    math_006_12.use_clamp = False
    # Value_001
    math_006_12.inputs[1].default_value = 0.10000000149011612

    # Set parents
    group_input_27.parent = frame_15
    math_008_10.parent = frame_001_12
    mix_21.parent = frame_001_12
    scene_time_001.parent = frame_15
    switch_10.parent = frame_15
    math_007_11.parent = frame_15
    reroute_007_5.parent = frame_001_12
    math_012_6.parent = frame_15
    separate_color_001_7.parent = frame_001_12
    mix_003_3.parent = frame_001_12
    reroute_003_10.parent = frame_001_12
    group_input_001_10.parent = frame_002_11
    group_input_002_6.parent = frame_001_12
    voronoi_texture_003.parent = frame_15
    voronoi_texture_004.parent = frame_15
    map_range_005_7.parent = frame_15
    math_015_5.parent = frame_15
    math_018_4.parent = frame_15
    mix_017.parent = frame_15
    vector_math_004.parent = frame_15
    map_uv_003.parent = frame_002_11
    image_coordinates_002.parent = frame_15
    vector_math_005.parent = frame_15
    math_003_17.parent = frame_15
    reroute_004_8.parent = frame_15
    math_24.parent = frame_15
    math_002_18.parent = frame_15
    value_2.parent = frame_15
    mix_011.parent = frame_15
    math_004_16.parent = frame_15
    math_005_15.parent = frame_15
    reroute_17.parent = frame_15
    reroute_001_12.parent = frame_15
    map_range_001_17.parent = frame_15
    math_006_12.parent = frame_15

    # Set locations
    group_output_30.location = (2254.642578125, 1289.330078125)
    group_input_27.location = (28.81396484375, -639.8718872070312)
    math_008_10.location = (239.183837890625, -67.361083984375)
    mix_21.location = (838.7869873046875, -71.2294921875)
    scene_time_001.location = (417.5400390625, -1092.20703125)
    switch_10.location = (697.5400390625, -972.2069702148438)
    math_007_11.location = (907.07958984375, -997.0889892578125)
    frame_15.location = (-3077.64013671875, 1455.6719970703125)
    reroute_007_5.location = (261.025390625, -593.1083374023438)
    frame_002_11.location = (396.3600158691406, 1501.031982421875)
    math_012_6.location = (697.5400390625, -892.2069702148438)
    separate_color_001_7.location = (341.73388671875, -452.4056396484375)
    mix_003_3.location = (580.3411865234375, -390.1868896484375)
    frame_001_12.location = (1124.280029296875, 1499.592041015625)
    reroute_003_10.location = (138.3203125, -240.460205078125)
    group_input_001_10.location = (29.486602783203125, -57.5699462890625)
    group_input_002_6.location = (29.1146240234375, -36.037841796875)
    voronoi_texture_003.location = (1314.3802490234375, -522.81591796875)
    voronoi_texture_004.location = (1834.5333251953125, -553.4866333007812)
    map_range_005_7.location = (1546.550537109375, -641.611572265625)
    math_015_5.location = (954.5390625, -433.25927734375)
    math_018_4.location = (1307.4371337890625, -922.0155029296875)
    mix_017.location = (3098.88623046875, -159.4573974609375)
    vector_math_004.location = (3277.04833984375, -163.8822021484375)
    map_uv_003.location = (228.23068237304688, -35.9395751953125)
    image_coordinates_002.location = (954.150634765625, -270.76220703125)
    vector_math_005.location = (2111.908935546875, -285.9161376953125)
    math_003_17.location = (1685.519287109375, -49.97216796875)
    reroute_004_8.location = (843.233154296875, -748.4669799804688)
    math_24.location = (951.992431640625, -220.049072265625)
    math_002_18.location = (2796.385986328125, -235.88427734375)
    value_2.location = (30.36376953125, -557.186767578125)
    mix_011.location = (3102.897705078125, -426.189697265625)
    math_004_16.location = (2104.782470703125, -686.4946899414062)
    math_005_15.location = (1302.2388916015625, -1101.1793212890625)
    reroute_17.location = (1685.9124755859375, -329.07958984375)
    reroute_001_12.location = (1995.3211669921875, -330.5531005859375)
    map_range_001_17.location = (2381.5830078125, -35.699462890625)
    math_006_12.location = (2277.249755859375, -684.4495849609375)

    # Set dimensions
    group_output_30.width, group_output_30.height = 140.0, 100.0
    group_input_27.width, group_input_27.height = 140.0, 100.0
    math_008_10.width, math_008_10.height = 140.0, 100.0
    mix_21.width, mix_21.height = 140.0, 100.0
    scene_time_001.width, scene_time_001.height = 140.0, 100.0
    switch_10.width, switch_10.height = 140.0, 100.0
    math_007_11.width, math_007_11.height = 140.0, 100.0
    frame_15.width, frame_15.height = 3446.240234375, 1273.1519775390625
    reroute_007_5.width, reroute_007_5.height = 13.5, 100.0
    frame_002_11.width, frame_002_11.height = 397.0400085449219, 181.6319580078125
    math_012_6.width, math_012_6.height = 140.0, 100.0
    separate_color_001_7.width, separate_color_001_7.height = 140.0, 100.0
    mix_003_3.width, mix_003_3.height = 140.0, 100.0
    frame_001_12.width, frame_001_12.height = 1007.599853515625, 633.072021484375
    reroute_003_10.width, reroute_003_10.height = 13.5, 100.0
    group_input_001_10.width, group_input_001_10.height = 140.0, 100.0
    group_input_002_6.width, group_input_002_6.height = 140.0, 100.0
    voronoi_texture_003.width, voronoi_texture_003.height = 140.0, 100.0
    voronoi_texture_004.width, voronoi_texture_004.height = 140.0, 100.0
    map_range_005_7.width, map_range_005_7.height = 140.0, 100.0
    math_015_5.width, math_015_5.height = 140.0, 100.0
    math_018_4.width, math_018_4.height = 140.0, 100.0
    mix_017.width, mix_017.height = 140.0, 100.0
    vector_math_004.width, vector_math_004.height = 140.0, 100.0
    map_uv_003.width, map_uv_003.height = 140.0, 100.0
    image_coordinates_002.width, image_coordinates_002.height = 140.0, 100.0
    vector_math_005.width, vector_math_005.height = 140.0, 100.0
    math_003_17.width, math_003_17.height = 150.85791015625, 100.0
    reroute_004_8.width, reroute_004_8.height = 13.5, 100.0
    math_24.width, math_24.height = 140.0, 100.0
    math_002_18.width, math_002_18.height = 140.0, 100.0
    value_2.width, value_2.height = 140.0, 100.0
    mix_011.width, mix_011.height = 140.0, 100.0
    math_004_16.width, math_004_16.height = 140.0, 100.0
    math_005_15.width, math_005_15.height = 140.0, 100.0
    reroute_17.width, reroute_17.height = 13.5, 100.0
    reroute_001_12.width, reroute_001_12.height = 13.5, 100.0
    map_range_001_17.width, map_range_001_17.height = 140.0, 100.0
    math_006_12.width, math_006_12.height = 140.0, 100.0

    # Initialize _rr_grain_layer links

    # scene_time_001.Frame -> switch_10.On
    _rr_grain_layer.links.new(scene_time_001.outputs[1], switch_10.inputs[2])
    # reroute_007_5.Output -> mix_003_3.B
    _rr_grain_layer.links.new(reroute_007_5.outputs[0], mix_003_3.inputs[7])
    # reroute_007_5.Output -> separate_color_001_7.Image
    _rr_grain_layer.links.new(reroute_007_5.outputs[0], separate_color_001_7.inputs[0])
    # mix_003_3.Result -> mix_21.B
    _rr_grain_layer.links.new(mix_003_3.outputs[2], mix_21.inputs[7])
    # separate_color_001_7.Red -> mix_003_3.A
    _rr_grain_layer.links.new(separate_color_001_7.outputs[0], mix_003_3.inputs[6])
    # switch_10.Image -> math_007_11.Value
    _rr_grain_layer.links.new(switch_10.outputs[0], math_007_11.inputs[1])
    # math_012_6.Value -> math_007_11.Value
    _rr_grain_layer.links.new(math_012_6.outputs[0], math_007_11.inputs[0])
    # reroute_003_10.Output -> mix_21.A
    _rr_grain_layer.links.new(reroute_003_10.outputs[0], mix_21.inputs[6])
    # group_input_27.Animate -> switch_10.Switch
    _rr_grain_layer.links.new(group_input_27.outputs[5], switch_10.inputs[0])
    # group_input_27.Scale -> math_012_6.Value
    _rr_grain_layer.links.new(group_input_27.outputs[3], math_012_6.inputs[0])
    # group_input_002_6.Factor -> math_008_10.Value
    _rr_grain_layer.links.new(group_input_002_6.outputs[0], math_008_10.inputs[0])
    # group_input_002_6.Strength -> math_008_10.Value
    _rr_grain_layer.links.new(group_input_002_6.outputs[2], math_008_10.inputs[1])
    # math_008_10.Value -> mix_21.Factor
    _rr_grain_layer.links.new(math_008_10.outputs[0], mix_21.inputs[0])
    # voronoi_texture_003.Color -> map_range_005_7.Value
    _rr_grain_layer.links.new(voronoi_texture_003.outputs[1], map_range_005_7.inputs[0])
    # reroute_004_8.Output -> math_015_5.Value
    _rr_grain_layer.links.new(reroute_004_8.outputs[0], math_015_5.inputs[0])
    # reroute_004_8.Output -> math_018_4.Value
    _rr_grain_layer.links.new(reroute_004_8.outputs[0], math_018_4.inputs[0])
    # math_018_4.Value -> map_range_005_7.To Max
    _rr_grain_layer.links.new(math_018_4.outputs[0], map_range_005_7.inputs[4])
    # group_input_001_10.Image -> map_uv_003.Image
    _rr_grain_layer.links.new(group_input_001_10.outputs[1], map_uv_003.inputs[0])
    # vector_math_004.Vector -> map_uv_003.UV
    _rr_grain_layer.links.new(vector_math_004.outputs[0], map_uv_003.inputs[1])
    # mix_011.Result -> reroute_007_5.Input
    _rr_grain_layer.links.new(mix_011.outputs[2], reroute_007_5.inputs[0])
    # map_uv_003.Image -> reroute_003_10.Input
    _rr_grain_layer.links.new(map_uv_003.outputs[0], reroute_003_10.inputs[0])
    # group_input_27.Image -> image_coordinates_002.Image
    _rr_grain_layer.links.new(group_input_27.outputs[1], image_coordinates_002.inputs[0])
    # map_range_005_7.Result -> voronoi_texture_004.Scale
    _rr_grain_layer.links.new(map_range_005_7.outputs[0], voronoi_texture_004.inputs[2])
    # reroute_17.Output -> voronoi_texture_004.Vector
    _rr_grain_layer.links.new(reroute_17.outputs[0], voronoi_texture_004.inputs[0])
    # reroute_001_12.Output -> vector_math_005.Vector
    _rr_grain_layer.links.new(reroute_001_12.outputs[0], vector_math_005.inputs[0])
    # voronoi_texture_004.Position -> mix_017.B
    _rr_grain_layer.links.new(voronoi_texture_004.outputs[2], mix_017.inputs[7])
    # voronoi_texture_004.Position -> vector_math_005.Vector
    _rr_grain_layer.links.new(voronoi_texture_004.outputs[2], vector_math_005.inputs[1])
    # math_015_5.Value -> voronoi_texture_003.Scale
    _rr_grain_layer.links.new(math_015_5.outputs[0], voronoi_texture_003.inputs[2])
    # mix_21.Result -> group_output_30.Result
    _rr_grain_layer.links.new(mix_21.outputs[2], group_output_30.inputs[0])
    # map_range_001_17.Result -> math_002_18.Value
    _rr_grain_layer.links.new(map_range_001_17.outputs[0], math_002_18.inputs[0])
    # math_002_18.Value -> mix_017.Factor
    _rr_grain_layer.links.new(math_002_18.outputs[0], mix_017.inputs[0])
    # voronoi_texture_004.Distance -> math_004_16.Value
    _rr_grain_layer.links.new(voronoi_texture_004.outputs[0], math_004_16.inputs[0])
    # voronoi_texture_003.Distance -> math_004_16.Value
    _rr_grain_layer.links.new(voronoi_texture_003.outputs[0], math_004_16.inputs[1])
    # group_input_002_6.Saturation -> mix_003_3.Factor
    _rr_grain_layer.links.new(group_input_002_6.outputs[4], mix_003_3.inputs[0])
    # math_007_11.Value -> voronoi_texture_003.W
    _rr_grain_layer.links.new(math_007_11.outputs[0], voronoi_texture_003.inputs[1])
    # math_007_11.Value -> math_005_15.Value
    _rr_grain_layer.links.new(math_007_11.outputs[0], math_005_15.inputs[0])
    # math_005_15.Value -> voronoi_texture_004.W
    _rr_grain_layer.links.new(math_005_15.outputs[0], voronoi_texture_004.inputs[1])
    # group_input_27.Scale -> reroute_004_8.Input
    _rr_grain_layer.links.new(group_input_27.outputs[3], reroute_004_8.inputs[0])
    # group_input_27.Strength -> math_24.Value
    _rr_grain_layer.links.new(group_input_27.outputs[2], math_24.inputs[1])
    # group_input_27.Factor -> math_24.Value
    _rr_grain_layer.links.new(group_input_27.outputs[0], math_24.inputs[0])
    # reroute_001_12.Output -> mix_017.A
    _rr_grain_layer.links.new(reroute_001_12.outputs[0], mix_017.inputs[6])
    # reroute_17.Output -> reroute_001_12.Input
    _rr_grain_layer.links.new(reroute_17.outputs[0], reroute_001_12.inputs[0])
    # image_coordinates_002.Uniform -> voronoi_texture_003.Vector
    _rr_grain_layer.links.new(image_coordinates_002.outputs[0], voronoi_texture_003.inputs[0])
    # image_coordinates_002.Normalized -> reroute_17.Input
    _rr_grain_layer.links.new(image_coordinates_002.outputs[1], reroute_17.inputs[0])
    # mix_017.Result -> vector_math_004.Vector
    _rr_grain_layer.links.new(mix_017.outputs[2], vector_math_004.inputs[0])
    # math_003_17.Value -> map_range_001_17.From Max
    _rr_grain_layer.links.new(math_003_17.outputs[0], map_range_001_17.inputs[2])
    # vector_math_005.Value -> map_range_001_17.Value
    _rr_grain_layer.links.new(vector_math_005.outputs[1], map_range_001_17.inputs[0])
    # math_006_12.Value -> math_002_18.Value
    _rr_grain_layer.links.new(math_006_12.outputs[0], math_002_18.inputs[1])
    # math_004_16.Value -> math_006_12.Value
    _rr_grain_layer.links.new(math_004_16.outputs[0], math_006_12.inputs[0])
    # math_006_12.Value -> mix_011.Factor
    _rr_grain_layer.links.new(math_006_12.outputs[0], mix_011.inputs[0])
    # voronoi_texture_004.Color -> mix_011.B
    _rr_grain_layer.links.new(voronoi_texture_004.outputs[1], mix_011.inputs[7])
    # math_015_5.Value -> math_003_17.Value
    _rr_grain_layer.links.new(math_015_5.outputs[0], math_003_17.inputs[1])
    # math_24.Value -> map_range_001_17.To Min
    _rr_grain_layer.links.new(math_24.outputs[0], map_range_001_17.inputs[3])

    return _rr_grain_layer


_rr_grain_layer = _rr_grain_layer_node_group()

def _rr_mix_rgba_node_group():
    """Initialize .RR_mix_RGBA node group"""
    _rr_mix_rgba = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_mix_RGBA")

    _rr_mix_rgba.color_tag = 'NONE'
    _rr_mix_rgba.description = ""
    _rr_mix_rgba.default_group_node_width = 140
    # _rr_mix_rgba interface

    # Socket Result
    result_socket_3 = _rr_mix_rgba.interface.new_socket(name="Result", in_out='OUTPUT', socket_type='NodeSocketColor')
    result_socket_3.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    result_socket_3.attribute_domain = 'POINT'
    result_socket_3.default_input = 'VALUE'
    result_socket_3.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_14 = _rr_mix_rgba.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_14.default_value = 1.0
    factor_socket_14.min_value = 0.0
    factor_socket_14.max_value = 1.0
    factor_socket_14.subtype = 'FACTOR'
    factor_socket_14.attribute_domain = 'POINT'
    factor_socket_14.description = "Amount of mixing between the A and B inputs"
    factor_socket_14.default_input = 'VALUE'
    factor_socket_14.structure_type = 'AUTO'

    # Socket A
    a_socket_4 = _rr_mix_rgba.interface.new_socket(name="A", in_out='INPUT', socket_type='NodeSocketColor')
    a_socket_4.default_value = (1.0, 1.0, 1.0, 1.0)
    a_socket_4.attribute_domain = 'POINT'
    a_socket_4.default_input = 'VALUE'
    a_socket_4.structure_type = 'AUTO'

    # Socket B
    b_socket_4 = _rr_mix_rgba.interface.new_socket(name="B", in_out='INPUT', socket_type='NodeSocketColor')
    b_socket_4.default_value = (1.0, 1.0, 1.0, 1.0)
    b_socket_4.attribute_domain = 'POINT'
    b_socket_4.default_input = 'VALUE'
    b_socket_4.structure_type = 'AUTO'

    # Initialize _rr_mix_rgba nodes

    # Node Group Output
    group_output_31 = _rr_mix_rgba.nodes.new("NodeGroupOutput")
    group_output_31.name = "Group Output"
    group_output_31.is_active_output = True

    # Node Group Input
    group_input_28 = _rr_mix_rgba.nodes.new("NodeGroupInput")
    group_input_28.name = "Group Input"

    # Node Separate Color.001
    separate_color_001_8 = _rr_mix_rgba.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_8.name = "Separate Color.001"
    separate_color_001_8.mode = 'RGB'
    separate_color_001_8.ycc_mode = 'ITUBT709'
    separate_color_001_8.outputs[0].hide = True
    separate_color_001_8.outputs[1].hide = True
    separate_color_001_8.outputs[2].hide = True

    # Node Separate Color.002
    separate_color_002_5 = _rr_mix_rgba.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_5.name = "Separate Color.002"
    separate_color_002_5.mode = 'RGB'
    separate_color_002_5.ycc_mode = 'ITUBT709'
    separate_color_002_5.outputs[0].hide = True
    separate_color_002_5.outputs[1].hide = True
    separate_color_002_5.outputs[2].hide = True

    # Node Step 2.001
    step_2_001 = _rr_mix_rgba.nodes.new("ShaderNodeMix")
    step_2_001.name = "Step 2.001"
    step_2_001.blend_type = 'MIX'
    step_2_001.clamp_factor = True
    step_2_001.clamp_result = False
    step_2_001.data_type = 'RGBA'
    step_2_001.factor_mode = 'UNIFORM'

    # Node Mix
    mix_22 = _rr_mix_rgba.nodes.new("ShaderNodeMix")
    mix_22.name = "Mix"
    mix_22.blend_type = 'MIX'
    mix_22.clamp_factor = True
    mix_22.clamp_result = False
    mix_22.data_type = 'FLOAT'
    mix_22.factor_mode = 'UNIFORM'

    # Node Set Alpha
    set_alpha = _rr_mix_rgba.nodes.new("CompositorNodeSetAlpha")
    set_alpha.name = "Set Alpha"
    set_alpha.mode = 'REPLACE_ALPHA'

    # Set locations
    group_output_31.location = (676.9684448242188, -6.010772228240967)
    group_input_28.location = (-438.9604187011719, -42.23785400390625)
    separate_color_001_8.location = (-132.5958709716797, -104.99211120605469)
    separate_color_002_5.location = (-133.08297729492188, -212.06912231445312)
    step_2_001.location = (118.79283905029297, 158.54074096679688)
    mix_22.location = (123.81440734863281, -105.07279205322266)
    set_alpha.location = (384.5503845214844, 71.45860290527344)

    # Set dimensions
    group_output_31.width, group_output_31.height = 140.0, 100.0
    group_input_28.width, group_input_28.height = 140.0, 100.0
    separate_color_001_8.width, separate_color_001_8.height = 140.0, 100.0
    separate_color_002_5.width, separate_color_002_5.height = 140.0, 100.0
    step_2_001.width, step_2_001.height = 140.0, 100.0
    mix_22.width, mix_22.height = 140.0, 100.0
    set_alpha.width, set_alpha.height = 140.0, 100.0

    # Initialize _rr_mix_rgba links

    # group_input_28.A -> separate_color_001_8.Image
    _rr_mix_rgba.links.new(group_input_28.outputs[1], separate_color_001_8.inputs[0])
    # group_input_28.B -> separate_color_002_5.Image
    _rr_mix_rgba.links.new(group_input_28.outputs[2], separate_color_002_5.inputs[0])
    # group_input_28.Factor -> step_2_001.Factor
    _rr_mix_rgba.links.new(group_input_28.outputs[0], step_2_001.inputs[0])
    # group_input_28.A -> step_2_001.A
    _rr_mix_rgba.links.new(group_input_28.outputs[1], step_2_001.inputs[6])
    # group_input_28.B -> step_2_001.B
    _rr_mix_rgba.links.new(group_input_28.outputs[2], step_2_001.inputs[7])
    # separate_color_001_8.Alpha -> mix_22.A
    _rr_mix_rgba.links.new(separate_color_001_8.outputs[3], mix_22.inputs[2])
    # separate_color_002_5.Alpha -> mix_22.B
    _rr_mix_rgba.links.new(separate_color_002_5.outputs[3], mix_22.inputs[3])
    # group_input_28.Factor -> mix_22.Factor
    _rr_mix_rgba.links.new(group_input_28.outputs[0], mix_22.inputs[0])
    # step_2_001.Result -> set_alpha.Image
    _rr_mix_rgba.links.new(step_2_001.outputs[2], set_alpha.inputs[0])
    # mix_22.Result -> set_alpha.Alpha
    _rr_mix_rgba.links.new(mix_22.outputs[0], set_alpha.inputs[1])
    # set_alpha.Image -> group_output_31.Result
    _rr_mix_rgba.links.new(set_alpha.outputs[0], group_output_31.inputs[0])

    return _rr_mix_rgba


_rr_mix_rgba = _rr_mix_rgba_node_group()

def _rr_grain_accurate_node_group():
    """Initialize .RR_grain_accurate node group"""
    _rr_grain_accurate = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_grain_accurate")

    _rr_grain_accurate.color_tag = 'NONE'
    _rr_grain_accurate.description = ""
    _rr_grain_accurate.default_group_node_width = 140
    # _rr_grain_accurate interface

    # Socket Image
    image_socket_46 = _rr_grain_accurate.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_46.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_46.attribute_domain = 'POINT'
    image_socket_46.default_input = 'VALUE'
    image_socket_46.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_15 = _rr_grain_accurate.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_15.default_value = 1.0
    factor_socket_15.min_value = 0.0
    factor_socket_15.max_value = 1.0
    factor_socket_15.subtype = 'FACTOR'
    factor_socket_15.attribute_domain = 'POINT'
    factor_socket_15.default_input = 'VALUE'
    factor_socket_15.structure_type = 'AUTO'

    # Socket Image
    image_socket_47 = _rr_grain_accurate.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_47.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_47.attribute_domain = 'POINT'
    image_socket_47.default_input = 'VALUE'
    image_socket_47.structure_type = 'AUTO'

    # Socket Strength
    strength_socket_11 = _rr_grain_accurate.interface.new_socket(name="Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    strength_socket_11.default_value = 0.25
    strength_socket_11.min_value = 0.0
    strength_socket_11.max_value = 1.0
    strength_socket_11.subtype = 'FACTOR'
    strength_socket_11.attribute_domain = 'POINT'
    strength_socket_11.default_input = 'VALUE'
    strength_socket_11.structure_type = 'AUTO'

    # Socket Scale
    scale_socket_2 = _rr_grain_accurate.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket_2.default_value = 5.0
    scale_socket_2.min_value = 0.25
    scale_socket_2.max_value = 20.0
    scale_socket_2.subtype = 'FACTOR'
    scale_socket_2.attribute_domain = 'POINT'
    scale_socket_2.default_input = 'VALUE'
    scale_socket_2.structure_type = 'AUTO'

    # Socket Saturation
    saturation_socket_6 = _rr_grain_accurate.interface.new_socket(name="Saturation", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_socket_6.default_value = 1.0
    saturation_socket_6.min_value = 0.0
    saturation_socket_6.max_value = 1.0
    saturation_socket_6.subtype = 'FACTOR'
    saturation_socket_6.attribute_domain = 'POINT'
    saturation_socket_6.default_input = 'VALUE'
    saturation_socket_6.structure_type = 'AUTO'

    # Socket Animate
    animate_socket_2 = _rr_grain_accurate.interface.new_socket(name="Animate", in_out='INPUT', socket_type='NodeSocketBool')
    animate_socket_2.default_value = False
    animate_socket_2.attribute_domain = 'POINT'
    animate_socket_2.default_input = 'VALUE'
    animate_socket_2.structure_type = 'AUTO'

    # Initialize _rr_grain_accurate nodes

    # Node Group Output
    group_output_32 = _rr_grain_accurate.nodes.new("NodeGroupOutput")
    group_output_32.name = "Group Output"
    group_output_32.is_active_output = True

    # Node Alpha Over
    alpha_over = _rr_grain_accurate.nodes.new("CompositorNodeAlphaOver")
    alpha_over.name = "Alpha Over"
    # Straight Alpha
    alpha_over.inputs[3].default_value = False

    # Node Group Input.001
    group_input_001_11 = _rr_grain_accurate.nodes.new("NodeGroupInput")
    group_input_001_11.name = "Group Input.001"

    # Node Group Input.004
    group_input_004_6 = _rr_grain_accurate.nodes.new("NodeGroupInput")
    group_input_004_6.name = "Group Input.004"
    group_input_004_6.outputs[3].hide = True
    group_input_004_6.outputs[4].hide = True
    group_input_004_6.outputs[5].hide = True
    group_input_004_6.outputs[6].hide = True

    # Node Frame.003
    frame_003_8 = _rr_grain_accurate.nodes.new("NodeFrame")
    frame_003_8.name = "Frame.003"
    frame_003_8.label_size = 20
    frame_003_8.shrink = True

    # Node Step 1
    step_1 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    step_1.name = "Step 1"
    step_1.node_tree = _rr_grain_layer

    # Node Group.001
    group_001_2 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    group_001_2.name = "Group.001"
    group_001_2.node_tree = _rr_grain_layer

    # Node Group.002
    group_002_2 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    group_002_2.name = "Group.002"
    group_002_2.node_tree = _rr_grain_layer

    # Node Group.003
    group_003 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    group_003.name = "Group.003"
    group_003.node_tree = _rr_grain_layer

    # Node Group.004
    group_004_2 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    group_004_2.name = "Group.004"
    group_004_2.node_tree = _rr_grain_layer

    # Node Layer Result
    layer_result = _rr_grain_accurate.nodes.new("NodeReroute")
    layer_result.label = "Layer Result"
    layer_result.name = "Layer Result"
    layer_result.socket_idname = "NodeSocketColor"
    # Node Math
    math_25 = _rr_grain_accurate.nodes.new("ShaderNodeMath")
    math_25.name = "Math"
    math_25.operation = 'MULTIPLY'
    math_25.use_clamp = False
    # Value_001
    math_25.inputs[1].default_value = 0.5

    # Node Math.001
    math_001_20 = _rr_grain_accurate.nodes.new("ShaderNodeMath")
    math_001_20.name = "Math.001"
    math_001_20.operation = 'MULTIPLY'
    math_001_20.use_clamp = False
    # Value_001
    math_001_20.inputs[1].default_value = 1.5

    # Node Math.002
    math_002_19 = _rr_grain_accurate.nodes.new("ShaderNodeMath")
    math_002_19.name = "Math.002"
    math_002_19.operation = 'MULTIPLY'
    math_002_19.use_clamp = False
    # Value_001
    math_002_19.inputs[1].default_value = 0.3499999940395355

    # Node Math.003
    math_003_18 = _rr_grain_accurate.nodes.new("ShaderNodeMath")
    math_003_18.name = "Math.003"
    math_003_18.operation = 'MULTIPLY'
    math_003_18.use_clamp = False
    # Value_001
    math_003_18.inputs[1].default_value = 0.75

    # Node Math.004
    math_004_17 = _rr_grain_accurate.nodes.new("ShaderNodeMath")
    math_004_17.name = "Math.004"
    math_004_17.hide = True
    math_004_17.operation = 'MULTIPLY'
    math_004_17.use_clamp = False

    # Node Float Curve
    float_curve_4 = _rr_grain_accurate.nodes.new("ShaderNodeFloatCurve")
    float_curve_4.name = "Float Curve"
    # Mapping settings
    float_curve_4.mapping.extend = 'EXTRAPOLATED'
    float_curve_4.mapping.tone = 'STANDARD'
    float_curve_4.mapping.black_level = (0.0, 0.0, 0.0)
    float_curve_4.mapping.white_level = (1.0, 1.0, 1.0)
    float_curve_4.mapping.clip_min_x = 0.0
    float_curve_4.mapping.clip_min_y = 0.0
    float_curve_4.mapping.clip_max_x = 1.0
    float_curve_4.mapping.clip_max_y = 1.0
    float_curve_4.mapping.use_clip = True
    # Curve 0
    float_curve_4_curve_0 = float_curve_4.mapping.curves[0]
    float_curve_4_curve_0_point_0 = float_curve_4_curve_0.points[0]
    float_curve_4_curve_0_point_0.location = (0.0, 0.0)
    float_curve_4_curve_0_point_0.handle_type = 'AUTO'
    float_curve_4_curve_0_point_1 = float_curve_4_curve_0.points[1]
    float_curve_4_curve_0_point_1.location = (0.25, 0.75)
    float_curve_4_curve_0_point_1.handle_type = 'AUTO'
    float_curve_4_curve_0_point_2 = float_curve_4_curve_0.points.new(1.0, 1.0)
    float_curve_4_curve_0_point_2.handle_type = 'AUTO'
    # Update curve after changes
    float_curve_4.mapping.update()
    # Factor
    float_curve_4.inputs[0].default_value = 1.0

    # Node Step 2
    step_2 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    step_2.name = "Step 2"
    step_2.node_tree = _rr_mix_rgba
    # Socket_2
    step_2.inputs[0].default_value = 0.5

    # Node Step 3
    step_3 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    step_3.name = "Step 3"
    step_3.node_tree = _rr_mix_rgba
    # Socket_2
    step_3.inputs[0].default_value = 0.33000001311302185

    # Node Step 4
    step_4 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    step_4.name = "Step 4"
    step_4.node_tree = _rr_mix_rgba
    # Socket_2
    step_4.inputs[0].default_value = 0.25

    # Node Step 5
    step_5 = _rr_grain_accurate.nodes.new("CompositorNodeGroup")
    step_5.name = "Step 5"
    step_5.node_tree = _rr_mix_rgba
    # Socket_2
    step_5.inputs[0].default_value = 0.20000000298023224

    # Set parents
    group_output_32.parent = frame_003_8
    alpha_over.parent = frame_003_8
    group_input_004_6.parent = frame_003_8
    layer_result.parent = frame_003_8
    math_004_17.parent = frame_003_8
    float_curve_4.parent = frame_003_8

    # Set locations
    group_output_32.location = (1082.185546875, -152.1077880859375)
    alpha_over.location = (817.1421508789062, -139.824951171875)
    group_input_001_11.location = (-630.7741088867188, -753.8955078125)
    group_input_004_6.location = (44.39959716796875, -100.448974609375)
    frame_003_8.location = (1006.4412231445312, -584.280029296875)
    step_1.location = (296.96044921875, -358.31243896484375)
    group_001_2.location = (294.20703125, -585.0982666015625)
    group_002_2.location = (296.0426330566406, -814.6386108398438)
    group_003.location = (293.28924560546875, -1043.2608642578125)
    group_004_2.location = (294.3619079589844, -1273.9749755859375)
    layer_result.location = (34.01995849609375, -239.2069091796875)
    math_25.location = (102.33910369873047, -635.6510620117188)
    math_001_20.location = (105.32262420654297, -864.4855346679688)
    math_002_19.location = (109.18656921386719, -1091.140869140625)
    math_003_18.location = (119.64749908447266, -1309.750732421875)
    math_004_17.location = (295.36981201171875, -294.41656494140625)
    float_curve_4.location = (511.28997802734375, -28.8203125)
    step_2.location = (618.4074096679688, -473.4700622558594)
    step_3.location = (615.6091918945312, -691.0824584960938)
    step_4.location = (615.6091918945312, -902.5474853515625)
    step_5.location = (615.6091918945312, -1121.3892822265625)

    # Set dimensions
    group_output_32.width, group_output_32.height = 140.0, 100.0
    alpha_over.width, alpha_over.height = 140.0, 100.0
    group_input_001_11.width, group_input_001_11.height = 140.0, 100.0
    group_input_004_6.width, group_input_004_6.height = 140.0, 100.0
    frame_003_8.width, frame_003_8.height = 1251.43896484375, 357.84002685546875
    step_1.width, step_1.height = 194.18484497070312, 100.0
    group_001_2.width, group_001_2.height = 194.18484497070312, 100.0
    group_002_2.width, group_002_2.height = 194.18484497070312, 100.0
    group_003.width, group_003.height = 194.18484497070312, 100.0
    group_004_2.width, group_004_2.height = 194.18484497070312, 100.0
    layer_result.width, layer_result.height = 13.5, 100.0
    math_25.width, math_25.height = 140.0, 100.0
    math_001_20.width, math_001_20.height = 140.0, 100.0
    math_002_19.width, math_002_19.height = 140.0, 100.0
    math_003_18.width, math_003_18.height = 140.0, 100.0
    math_004_17.width, math_004_17.height = 140.0, 100.0
    float_curve_4.width, float_curve_4.height = 240.0, 100.0
    step_2.width, step_2.height = 138.2201385498047, 100.0
    step_3.width, step_3.height = 138.2201385498047, 100.0
    step_4.width, step_4.height = 138.2201385498047, 100.0
    step_5.width, step_5.height = 138.2201385498047, 100.0

    # Initialize _rr_grain_accurate links

    # layer_result.Output -> alpha_over.Image
    _rr_grain_accurate.links.new(layer_result.outputs[0], alpha_over.inputs[2])
    # group_input_004_6.Image -> alpha_over.Image
    _rr_grain_accurate.links.new(group_input_004_6.outputs[1], alpha_over.inputs[1])
    # group_input_001_11.Animate -> step_1.Animate
    _rr_grain_accurate.links.new(group_input_001_11.outputs[5], step_1.inputs[5])
    # group_input_001_11.Image -> step_1.Image
    _rr_grain_accurate.links.new(group_input_001_11.outputs[1], step_1.inputs[1])
    # group_input_001_11.Factor -> step_1.Factor
    _rr_grain_accurate.links.new(group_input_001_11.outputs[0], step_1.inputs[0])
    # group_input_001_11.Strength -> step_1.Strength
    _rr_grain_accurate.links.new(group_input_001_11.outputs[2], step_1.inputs[2])
    # group_input_001_11.Saturation -> step_1.Saturation
    _rr_grain_accurate.links.new(group_input_001_11.outputs[4], step_1.inputs[4])
    # group_input_001_11.Animate -> group_001_2.Animate
    _rr_grain_accurate.links.new(group_input_001_11.outputs[5], group_001_2.inputs[5])
    # group_input_001_11.Image -> group_001_2.Image
    _rr_grain_accurate.links.new(group_input_001_11.outputs[1], group_001_2.inputs[1])
    # math_25.Value -> group_001_2.Scale
    _rr_grain_accurate.links.new(math_25.outputs[0], group_001_2.inputs[3])
    # group_input_001_11.Factor -> group_001_2.Factor
    _rr_grain_accurate.links.new(group_input_001_11.outputs[0], group_001_2.inputs[0])
    # group_input_001_11.Strength -> group_001_2.Strength
    _rr_grain_accurate.links.new(group_input_001_11.outputs[2], group_001_2.inputs[2])
    # group_input_001_11.Saturation -> group_001_2.Saturation
    _rr_grain_accurate.links.new(group_input_001_11.outputs[4], group_001_2.inputs[4])
    # group_input_001_11.Animate -> group_002_2.Animate
    _rr_grain_accurate.links.new(group_input_001_11.outputs[5], group_002_2.inputs[5])
    # group_input_001_11.Image -> group_002_2.Image
    _rr_grain_accurate.links.new(group_input_001_11.outputs[1], group_002_2.inputs[1])
    # math_001_20.Value -> group_002_2.Scale
    _rr_grain_accurate.links.new(math_001_20.outputs[0], group_002_2.inputs[3])
    # group_input_001_11.Factor -> group_002_2.Factor
    _rr_grain_accurate.links.new(group_input_001_11.outputs[0], group_002_2.inputs[0])
    # group_input_001_11.Strength -> group_002_2.Strength
    _rr_grain_accurate.links.new(group_input_001_11.outputs[2], group_002_2.inputs[2])
    # group_input_001_11.Saturation -> group_002_2.Saturation
    _rr_grain_accurate.links.new(group_input_001_11.outputs[4], group_002_2.inputs[4])
    # group_input_001_11.Animate -> group_003.Animate
    _rr_grain_accurate.links.new(group_input_001_11.outputs[5], group_003.inputs[5])
    # group_input_001_11.Image -> group_003.Image
    _rr_grain_accurate.links.new(group_input_001_11.outputs[1], group_003.inputs[1])
    # math_002_19.Value -> group_003.Scale
    _rr_grain_accurate.links.new(math_002_19.outputs[0], group_003.inputs[3])
    # group_input_001_11.Factor -> group_003.Factor
    _rr_grain_accurate.links.new(group_input_001_11.outputs[0], group_003.inputs[0])
    # group_input_001_11.Strength -> group_003.Strength
    _rr_grain_accurate.links.new(group_input_001_11.outputs[2], group_003.inputs[2])
    # group_input_001_11.Saturation -> group_003.Saturation
    _rr_grain_accurate.links.new(group_input_001_11.outputs[4], group_003.inputs[4])
    # group_input_001_11.Animate -> group_004_2.Animate
    _rr_grain_accurate.links.new(group_input_001_11.outputs[5], group_004_2.inputs[5])
    # group_input_001_11.Image -> group_004_2.Image
    _rr_grain_accurate.links.new(group_input_001_11.outputs[1], group_004_2.inputs[1])
    # math_003_18.Value -> group_004_2.Scale
    _rr_grain_accurate.links.new(math_003_18.outputs[0], group_004_2.inputs[3])
    # group_input_001_11.Factor -> group_004_2.Factor
    _rr_grain_accurate.links.new(group_input_001_11.outputs[0], group_004_2.inputs[0])
    # group_input_001_11.Strength -> group_004_2.Strength
    _rr_grain_accurate.links.new(group_input_001_11.outputs[2], group_004_2.inputs[2])
    # group_input_001_11.Saturation -> group_004_2.Saturation
    _rr_grain_accurate.links.new(group_input_001_11.outputs[4], group_004_2.inputs[4])
    # group_input_001_11.Scale -> step_1.Scale
    _rr_grain_accurate.links.new(group_input_001_11.outputs[3], step_1.inputs[3])
    # group_input_001_11.Scale -> math_25.Value
    _rr_grain_accurate.links.new(group_input_001_11.outputs[3], math_25.inputs[0])
    # group_input_001_11.Scale -> math_001_20.Value
    _rr_grain_accurate.links.new(group_input_001_11.outputs[3], math_001_20.inputs[0])
    # group_input_001_11.Scale -> math_002_19.Value
    _rr_grain_accurate.links.new(group_input_001_11.outputs[3], math_002_19.inputs[0])
    # group_input_001_11.Scale -> math_003_18.Value
    _rr_grain_accurate.links.new(group_input_001_11.outputs[3], math_003_18.inputs[0])
    # group_input_004_6.Factor -> math_004_17.Value
    _rr_grain_accurate.links.new(group_input_004_6.outputs[0], math_004_17.inputs[0])
    # group_input_004_6.Strength -> math_004_17.Value
    _rr_grain_accurate.links.new(group_input_004_6.outputs[2], math_004_17.inputs[1])
    # math_004_17.Value -> float_curve_4.Value
    _rr_grain_accurate.links.new(math_004_17.outputs[0], float_curve_4.inputs[1])
    # float_curve_4.Value -> alpha_over.Fac
    _rr_grain_accurate.links.new(float_curve_4.outputs[0], alpha_over.inputs[0])
    # alpha_over.Image -> group_output_32.Image
    _rr_grain_accurate.links.new(alpha_over.outputs[0], group_output_32.inputs[0])
    # step_1.Result -> step_2.A
    _rr_grain_accurate.links.new(step_1.outputs[0], step_2.inputs[1])
    # group_001_2.Result -> step_2.B
    _rr_grain_accurate.links.new(group_001_2.outputs[0], step_2.inputs[2])
    # step_2.Result -> step_3.A
    _rr_grain_accurate.links.new(step_2.outputs[0], step_3.inputs[1])
    # group_002_2.Result -> step_3.B
    _rr_grain_accurate.links.new(group_002_2.outputs[0], step_3.inputs[2])
    # step_3.Result -> step_4.A
    _rr_grain_accurate.links.new(step_3.outputs[0], step_4.inputs[1])
    # group_003.Result -> step_4.B
    _rr_grain_accurate.links.new(group_003.outputs[0], step_4.inputs[2])
    # step_4.Result -> step_5.A
    _rr_grain_accurate.links.new(step_4.outputs[0], step_5.inputs[1])
    # group_004_2.Result -> step_5.B
    _rr_grain_accurate.links.new(group_004_2.outputs[0], step_5.inputs[2])
    # step_2.Result -> layer_result.Input
    _rr_grain_accurate.links.new(step_2.outputs[0], layer_result.inputs[0])

    return _rr_grain_accurate


_rr_grain_accurate = _rr_grain_accurate_node_group()

def _rr_split_tone_node_group():
    """Initialize .RR_split_tone node group"""
    _rr_split_tone = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_split_tone")

    _rr_split_tone.color_tag = 'NONE'
    _rr_split_tone.description = ""
    _rr_split_tone.default_group_node_width = 140
    # _rr_split_tone interface

    # Socket Image
    image_socket_48 = _rr_split_tone.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_48.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_48.attribute_domain = 'POINT'
    image_socket_48.default_input = 'VALUE'
    image_socket_48.structure_type = 'AUTO'

    # Socket Image
    image_socket_49 = _rr_split_tone.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_49.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_49.attribute_domain = 'POINT'
    image_socket_49.default_input = 'VALUE'
    image_socket_49.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_16 = _rr_split_tone.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_16.default_value = 0.0
    factor_socket_16.min_value = -1.0
    factor_socket_16.max_value = 1.0
    factor_socket_16.subtype = 'FACTOR'
    factor_socket_16.attribute_domain = 'POINT'
    factor_socket_16.default_input = 'VALUE'
    factor_socket_16.structure_type = 'AUTO'

    # Initialize _rr_split_tone nodes

    # Node Group Output
    group_output_33 = _rr_split_tone.nodes.new("NodeGroupOutput")
    group_output_33.name = "Group Output"
    group_output_33.is_active_output = True

    # Node Group Input
    group_input_29 = _rr_split_tone.nodes.new("NodeGroupInput")
    group_input_29.name = "Group Input"

    # Node RGB Curves
    rgb_curves = _rr_split_tone.nodes.new("CompositorNodeCurveRGB")
    rgb_curves.name = "RGB Curves"
    # Mapping settings
    rgb_curves.mapping.extend = 'EXTRAPOLATED'
    rgb_curves.mapping.tone = 'STANDARD'
    rgb_curves.mapping.black_level = (0.0, 0.0, 0.0)
    rgb_curves.mapping.white_level = (1.0, 1.0, 1.0)
    rgb_curves.mapping.clip_min_x = 0.0
    rgb_curves.mapping.clip_min_y = 0.0
    rgb_curves.mapping.clip_max_x = 1.0
    rgb_curves.mapping.clip_max_y = 1.0
    rgb_curves.mapping.use_clip = True
    # Curve 0
    rgb_curves_curve_0 = rgb_curves.mapping.curves[0]
    rgb_curves_curve_0_point_0 = rgb_curves_curve_0.points[0]
    rgb_curves_curve_0_point_0.location = (0.0, 0.0)
    rgb_curves_curve_0_point_0.handle_type = 'AUTO'
    rgb_curves_curve_0_point_1 = rgb_curves_curve_0.points[1]
    rgb_curves_curve_0_point_1.location = (0.25, 0.10000000149011612)
    rgb_curves_curve_0_point_1.handle_type = 'AUTO'
    rgb_curves_curve_0_point_2 = rgb_curves_curve_0.points.new(0.75, 0.8999999761581421)
    rgb_curves_curve_0_point_2.handle_type = 'AUTO'
    rgb_curves_curve_0_point_3 = rgb_curves_curve_0.points.new(1.0, 1.0)
    rgb_curves_curve_0_point_3.handle_type = 'AUTO'
    # Curve 1
    rgb_curves_curve_1 = rgb_curves.mapping.curves[1]
    rgb_curves_curve_1_point_0 = rgb_curves_curve_1.points[0]
    rgb_curves_curve_1_point_0.location = (0.0, 0.0)
    rgb_curves_curve_1_point_0.handle_type = 'AUTO'
    rgb_curves_curve_1_point_1 = rgb_curves_curve_1.points[1]
    rgb_curves_curve_1_point_1.location = (0.25, 0.30000001192092896)
    rgb_curves_curve_1_point_1.handle_type = 'AUTO'
    rgb_curves_curve_1_point_2 = rgb_curves_curve_1.points.new(0.75, 0.699999988079071)
    rgb_curves_curve_1_point_2.handle_type = 'AUTO'
    rgb_curves_curve_1_point_3 = rgb_curves_curve_1.points.new(1.0, 1.0)
    rgb_curves_curve_1_point_3.handle_type = 'AUTO'
    # Curve 2
    rgb_curves_curve_2 = rgb_curves.mapping.curves[2]
    rgb_curves_curve_2_point_0 = rgb_curves_curve_2.points[0]
    rgb_curves_curve_2_point_0.location = (0.0, 0.0)
    rgb_curves_curve_2_point_0.handle_type = 'AUTO'
    rgb_curves_curve_2_point_1 = rgb_curves_curve_2.points[1]
    rgb_curves_curve_2_point_1.location = (0.25, 0.4000000059604645)
    rgb_curves_curve_2_point_1.handle_type = 'AUTO'
    rgb_curves_curve_2_point_2 = rgb_curves_curve_2.points.new(0.75, 0.6000000238418579)
    rgb_curves_curve_2_point_2.handle_type = 'AUTO'
    rgb_curves_curve_2_point_3 = rgb_curves_curve_2.points.new(1.0, 1.0)
    rgb_curves_curve_2_point_3.handle_type = 'AUTO'
    # Curve 3
    rgb_curves_curve_3 = rgb_curves.mapping.curves[3]
    rgb_curves_curve_3_point_0 = rgb_curves_curve_3.points[0]
    rgb_curves_curve_3_point_0.location = (0.0, 0.0)
    rgb_curves_curve_3_point_0.handle_type = 'AUTO'
    rgb_curves_curve_3_point_1 = rgb_curves_curve_3.points[1]
    rgb_curves_curve_3_point_1.location = (1.0, 1.0)
    rgb_curves_curve_3_point_1.handle_type = 'AUTO'
    # Update curve after changes
    rgb_curves.mapping.update()
    # Fac
    rgb_curves.inputs[0].default_value = 1.0
    # Black Level
    rgb_curves.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # White Level
    rgb_curves.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node RGB Curves.001
    rgb_curves_001 = _rr_split_tone.nodes.new("CompositorNodeCurveRGB")
    rgb_curves_001.name = "RGB Curves.001"
    # Mapping settings
    rgb_curves_001.mapping.extend = 'EXTRAPOLATED'
    rgb_curves_001.mapping.tone = 'STANDARD'
    rgb_curves_001.mapping.black_level = (0.0, 0.0, 0.0)
    rgb_curves_001.mapping.white_level = (1.0, 1.0, 1.0)
    rgb_curves_001.mapping.clip_min_x = 0.0
    rgb_curves_001.mapping.clip_min_y = 0.0
    rgb_curves_001.mapping.clip_max_x = 1.0
    rgb_curves_001.mapping.clip_max_y = 1.0
    rgb_curves_001.mapping.use_clip = True
    # Curve 0
    rgb_curves_001_curve_0 = rgb_curves_001.mapping.curves[0]
    rgb_curves_001_curve_0_point_0 = rgb_curves_001_curve_0.points[0]
    rgb_curves_001_curve_0_point_0.location = (0.0, 0.0)
    rgb_curves_001_curve_0_point_0.handle_type = 'AUTO'
    rgb_curves_001_curve_0_point_1 = rgb_curves_001_curve_0.points[1]
    rgb_curves_001_curve_0_point_1.location = (0.25, 0.4000000059604645)
    rgb_curves_001_curve_0_point_1.handle_type = 'AUTO'
    rgb_curves_001_curve_0_point_2 = rgb_curves_001_curve_0.points.new(0.75, 0.6000000238418579)
    rgb_curves_001_curve_0_point_2.handle_type = 'AUTO'
    rgb_curves_001_curve_0_point_3 = rgb_curves_001_curve_0.points.new(1.0, 1.0)
    rgb_curves_001_curve_0_point_3.handle_type = 'AUTO'
    # Curve 1
    rgb_curves_001_curve_1 = rgb_curves_001.mapping.curves[1]
    rgb_curves_001_curve_1_point_0 = rgb_curves_001_curve_1.points[0]
    rgb_curves_001_curve_1_point_0.location = (0.0, 0.0)
    rgb_curves_001_curve_1_point_0.handle_type = 'AUTO'
    rgb_curves_001_curve_1_point_1 = rgb_curves_001_curve_1.points[1]
    rgb_curves_001_curve_1_point_1.location = (0.25, 0.20000000298023224)
    rgb_curves_001_curve_1_point_1.handle_type = 'AUTO'
    rgb_curves_001_curve_1_point_2 = rgb_curves_001_curve_1.points.new(0.75, 0.7999999523162842)
    rgb_curves_001_curve_1_point_2.handle_type = 'AUTO'
    rgb_curves_001_curve_1_point_3 = rgb_curves_001_curve_1.points.new(1.0, 1.0)
    rgb_curves_001_curve_1_point_3.handle_type = 'AUTO'
    # Curve 2
    rgb_curves_001_curve_2 = rgb_curves_001.mapping.curves[2]
    rgb_curves_001_curve_2_point_0 = rgb_curves_001_curve_2.points[0]
    rgb_curves_001_curve_2_point_0.location = (0.0, 0.0)
    rgb_curves_001_curve_2_point_0.handle_type = 'AUTO'
    rgb_curves_001_curve_2_point_1 = rgb_curves_001_curve_2.points[1]
    rgb_curves_001_curve_2_point_1.location = (0.25, 0.10000000149011612)
    rgb_curves_001_curve_2_point_1.handle_type = 'AUTO'
    rgb_curves_001_curve_2_point_2 = rgb_curves_001_curve_2.points.new(0.75, 0.8999999761581421)
    rgb_curves_001_curve_2_point_2.handle_type = 'AUTO'
    rgb_curves_001_curve_2_point_3 = rgb_curves_001_curve_2.points.new(1.0, 1.0)
    rgb_curves_001_curve_2_point_3.handle_type = 'AUTO'
    # Curve 3
    rgb_curves_001_curve_3 = rgb_curves_001.mapping.curves[3]
    rgb_curves_001_curve_3_point_0 = rgb_curves_001_curve_3.points[0]
    rgb_curves_001_curve_3_point_0.location = (0.0, 0.0)
    rgb_curves_001_curve_3_point_0.handle_type = 'AUTO'
    rgb_curves_001_curve_3_point_1 = rgb_curves_001_curve_3.points[1]
    rgb_curves_001_curve_3_point_1.location = (1.0, 1.0)
    rgb_curves_001_curve_3_point_1.handle_type = 'AUTO'
    # Update curve after changes
    rgb_curves_001.mapping.update()
    # Fac
    rgb_curves_001.inputs[0].default_value = 1.0
    # Black Level
    rgb_curves_001.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # White Level
    rgb_curves_001.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Mix
    mix_23 = _rr_split_tone.nodes.new("ShaderNodeMix")
    mix_23.name = "Mix"
    mix_23.blend_type = 'MIX'
    mix_23.clamp_factor = False
    mix_23.clamp_result = False
    mix_23.data_type = 'RGBA'
    mix_23.factor_mode = 'UNIFORM'

    # Node Mix.001
    mix_001_15 = _rr_split_tone.nodes.new("ShaderNodeMix")
    mix_001_15.name = "Mix.001"
    mix_001_15.blend_type = 'MIX'
    mix_001_15.clamp_factor = False
    mix_001_15.clamp_result = False
    mix_001_15.data_type = 'RGBA'
    mix_001_15.factor_mode = 'UNIFORM'

    # Node Map Range
    map_range_18 = _rr_split_tone.nodes.new("ShaderNodeMapRange")
    map_range_18.name = "Map Range"
    map_range_18.clamp = False
    map_range_18.data_type = 'FLOAT'
    map_range_18.interpolation_type = 'LINEAR'
    # From Min
    map_range_18.inputs[1].default_value = -1.0
    # From Max
    map_range_18.inputs[2].default_value = 1.0
    # To Min
    map_range_18.inputs[3].default_value = 0.0
    # To Max
    map_range_18.inputs[4].default_value = 1.0

    # Node Math
    math_26 = _rr_split_tone.nodes.new("ShaderNodeMath")
    math_26.name = "Math"
    math_26.hide = True
    math_26.operation = 'ABSOLUTE'
    math_26.use_clamp = False

    # Node Map Range.001
    map_range_001_18 = _rr_split_tone.nodes.new("ShaderNodeMapRange")
    map_range_001_18.name = "Map Range.001"
    map_range_001_18.clamp = True
    map_range_001_18.data_type = 'FLOAT'
    map_range_001_18.interpolation_type = 'SMOOTHSTEP'
    # From Min
    map_range_001_18.inputs[1].default_value = 0.0
    # From Max
    map_range_001_18.inputs[2].default_value = 0.5
    # To Min
    map_range_001_18.inputs[3].default_value = 0.0
    # To Max
    map_range_001_18.inputs[4].default_value = 1.0

    # Set locations
    group_output_33.location = (1003.47900390625, -49.283050537109375)
    group_input_29.location = (-760.3927001953125, -106.9295654296875)
    rgb_curves.location = (-0.8886195421218872, -181.72547912597656)
    rgb_curves_001.location = (-1.1708984375, 274.68280029296875)
    mix_23.location = (470.02752685546875, -187.85923767089844)
    mix_001_15.location = (756.513427734375, -3.5158209800720215)
    map_range_18.location = (-199.8279571533203, -173.44273376464844)
    math_26.location = (-43.84900665283203, 412.73052978515625)
    map_range_001_18.location = (162.24368286132812, 509.4166259765625)

    # Set dimensions
    group_output_33.width, group_output_33.height = 140.0, 100.0
    group_input_29.width, group_input_29.height = 140.0, 100.0
    rgb_curves.width, rgb_curves.height = 320.0, 100.0
    rgb_curves_001.width, rgb_curves_001.height = 320.0, 100.0
    mix_23.width, mix_23.height = 140.0, 100.0
    mix_001_15.width, mix_001_15.height = 140.0, 100.0
    map_range_18.width, map_range_18.height = 140.0, 100.0
    math_26.width, math_26.height = 140.0, 100.0
    map_range_001_18.width, map_range_001_18.height = 140.0, 100.0

    # Initialize _rr_split_tone links

    # group_input_29.Image -> rgb_curves.Image
    _rr_split_tone.links.new(group_input_29.outputs[0], rgb_curves.inputs[1])
    # group_input_29.Image -> rgb_curves_001.Image
    _rr_split_tone.links.new(group_input_29.outputs[0], rgb_curves_001.inputs[1])
    # rgb_curves_001.Image -> mix_23.A
    _rr_split_tone.links.new(rgb_curves_001.outputs[0], mix_23.inputs[6])
    # mix_001_15.Result -> group_output_33.Image
    _rr_split_tone.links.new(mix_001_15.outputs[2], group_output_33.inputs[0])
    # mix_23.Result -> mix_001_15.B
    _rr_split_tone.links.new(mix_23.outputs[2], mix_001_15.inputs[7])
    # group_input_29.Image -> mix_001_15.A
    _rr_split_tone.links.new(group_input_29.outputs[0], mix_001_15.inputs[6])
    # group_input_29.Factor -> map_range_18.Value
    _rr_split_tone.links.new(group_input_29.outputs[1], map_range_18.inputs[0])
    # map_range_18.Result -> mix_23.Factor
    _rr_split_tone.links.new(map_range_18.outputs[0], mix_23.inputs[0])
    # group_input_29.Factor -> math_26.Value
    _rr_split_tone.links.new(group_input_29.outputs[1], math_26.inputs[0])
    # rgb_curves.Image -> mix_23.B
    _rr_split_tone.links.new(rgb_curves.outputs[0], mix_23.inputs[7])
    # map_range_001_18.Result -> mix_001_15.Factor
    _rr_split_tone.links.new(map_range_001_18.outputs[0], mix_001_15.inputs[0])
    # math_26.Value -> map_range_001_18.Value
    _rr_split_tone.links.new(math_26.outputs[0], map_range_001_18.inputs[0])

    return _rr_split_tone


_rr_split_tone = _rr_split_tone_node_group()

def _rr_lens_distortion_node_group():
    """Initialize .RR_lens_distortion node group"""
    _rr_lens_distortion = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_lens_distortion")

    _rr_lens_distortion.color_tag = 'NONE'
    _rr_lens_distortion.description = ""
    _rr_lens_distortion.default_group_node_width = 140
    # _rr_lens_distortion interface

    # Socket Image
    image_socket_50 = _rr_lens_distortion.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_50.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_50.attribute_domain = 'POINT'
    image_socket_50.default_input = 'VALUE'
    image_socket_50.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_17 = _rr_lens_distortion.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_17.default_value = 1.0
    factor_socket_17.min_value = 0.0
    factor_socket_17.max_value = 1.0
    factor_socket_17.subtype = 'FACTOR'
    factor_socket_17.attribute_domain = 'POINT'
    factor_socket_17.default_input = 'VALUE'
    factor_socket_17.structure_type = 'AUTO'

    # Socket Image
    image_socket_51 = _rr_lens_distortion.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_51.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_51.attribute_domain = 'POINT'
    image_socket_51.default_input = 'VALUE'
    image_socket_51.structure_type = 'AUTO'

    # Socket Distortion
    distortion_socket = _rr_lens_distortion.interface.new_socket(name="Distortion", in_out='INPUT', socket_type='NodeSocketFloat')
    distortion_socket.default_value = 0.0
    distortion_socket.min_value = -1.0
    distortion_socket.max_value = 1.0
    distortion_socket.subtype = 'FACTOR'
    distortion_socket.attribute_domain = 'POINT'
    distortion_socket.default_input = 'VALUE'
    distortion_socket.structure_type = 'AUTO'

    # Socket Dispersion
    dispersion_socket = _rr_lens_distortion.interface.new_socket(name="Dispersion", in_out='INPUT', socket_type='NodeSocketFloat')
    dispersion_socket.default_value = 0.0
    dispersion_socket.min_value = 0.0
    dispersion_socket.max_value = 1.0
    dispersion_socket.subtype = 'FACTOR'
    dispersion_socket.attribute_domain = 'POINT'
    dispersion_socket.default_input = 'VALUE'
    dispersion_socket.structure_type = 'AUTO'

    # Socket Horizontal Dispersion
    horizontal_dispersion_socket = _rr_lens_distortion.interface.new_socket(name="Horizontal Dispersion", in_out='INPUT', socket_type='NodeSocketBool')
    horizontal_dispersion_socket.default_value = False
    horizontal_dispersion_socket.attribute_domain = 'POINT'
    horizontal_dispersion_socket.default_input = 'VALUE'
    horizontal_dispersion_socket.structure_type = 'AUTO'

    # Initialize _rr_lens_distortion nodes

    # Node Group Output
    group_output_34 = _rr_lens_distortion.nodes.new("NodeGroupOutput")
    group_output_34.name = "Group Output"
    group_output_34.is_active_output = True

    # Node Lens Distortion
    lens_distortion = _rr_lens_distortion.nodes.new("CompositorNodeLensdist")
    lens_distortion.name = "Lens Distortion"
    lens_distortion.distortion_type = 'RADIAL'
    # Jitter
    lens_distortion.inputs[3].default_value = False
    # Fit
    lens_distortion.inputs[4].default_value = True

    # Node Set Alpha
    set_alpha_1 = _rr_lens_distortion.nodes.new("CompositorNodeSetAlpha")
    set_alpha_1.name = "Set Alpha"
    set_alpha_1.mode = 'REPLACE_ALPHA'

    # Node Lens Distortion Alpha
    lens_distortion_alpha = _rr_lens_distortion.nodes.new("CompositorNodeLensdist")
    lens_distortion_alpha.name = "Lens Distortion Alpha"
    lens_distortion_alpha.distortion_type = 'RADIAL'
    # Jitter
    lens_distortion_alpha.inputs[3].default_value = False
    # Fit
    lens_distortion_alpha.inputs[4].default_value = True

    # Node Group Input
    group_input_30 = _rr_lens_distortion.nodes.new("NodeGroupInput")
    group_input_30.name = "Group Input"

    # Node Separate Color.002
    separate_color_002_6 = _rr_lens_distortion.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_6.name = "Separate Color.002"
    separate_color_002_6.mode = 'RGB'
    separate_color_002_6.ycc_mode = 'ITUBT709'
    separate_color_002_6.outputs[0].hide = True
    separate_color_002_6.outputs[1].hide = True
    separate_color_002_6.outputs[2].hide = True

    # Node Lens Distortion.001
    lens_distortion_001 = _rr_lens_distortion.nodes.new("CompositorNodeLensdist")
    lens_distortion_001.name = "Lens Distortion.001"
    lens_distortion_001.distortion_type = 'HORIZONTAL'

    # Node Lens Distortion.002
    lens_distortion_002 = _rr_lens_distortion.nodes.new("CompositorNodeLensdist")
    lens_distortion_002.name = "Lens Distortion.002"
    lens_distortion_002.distortion_type = 'HORIZONTAL'

    # Node Separate Color.003
    separate_color_003_5 = _rr_lens_distortion.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_5.name = "Separate Color.003"
    separate_color_003_5.mode = 'RGB'
    separate_color_003_5.ycc_mode = 'ITUBT709'
    separate_color_003_5.outputs[0].hide = True
    separate_color_003_5.outputs[1].hide = True
    separate_color_003_5.outputs[2].hide = True

    # Node Set Alpha.001
    set_alpha_001 = _rr_lens_distortion.nodes.new("CompositorNodeSetAlpha")
    set_alpha_001.name = "Set Alpha.001"
    set_alpha_001.mode = 'REPLACE_ALPHA'

    # Node Group Input.001
    group_input_001_12 = _rr_lens_distortion.nodes.new("NodeGroupInput")
    group_input_001_12.name = "Group Input.001"

    # Node Math
    math_27 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_27.name = "Math"
    math_27.hide = True
    math_27.operation = 'ADD'
    math_27.use_clamp = False

    # Node Switch
    switch_11 = _rr_lens_distortion.nodes.new("CompositorNodeSwitch")
    switch_11.name = "Switch"

    # Node Math.001
    math_001_21 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_001_21.name = "Math.001"
    math_001_21.hide = True
    math_001_21.operation = 'ABSOLUTE'
    math_001_21.use_clamp = False

    # Node Mix
    mix_24 = _rr_lens_distortion.nodes.new("ShaderNodeMix")
    mix_24.name = "Mix"
    mix_24.blend_type = 'MIX'
    mix_24.clamp_factor = True
    mix_24.clamp_result = False
    mix_24.data_type = 'FLOAT'
    mix_24.factor_mode = 'UNIFORM'
    # B_Float
    mix_24.inputs[3].default_value = 0.0

    # Node Switch.001
    switch_001_2 = _rr_lens_distortion.nodes.new("CompositorNodeSwitch")
    switch_001_2.name = "Switch.001"

    # Node Math.002
    math_002_20 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_002_20.name = "Math.002"
    math_002_20.hide = True
    math_002_20.operation = 'MULTIPLY'
    math_002_20.use_clamp = False

    # Node Math.003
    math_003_19 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_003_19.name = "Math.003"
    math_003_19.hide = True
    math_003_19.operation = 'MULTIPLY'
    math_003_19.use_clamp = False

    # Node Math.004
    math_004_18 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_004_18.name = "Math.004"
    math_004_18.hide = True
    math_004_18.operation = 'MULTIPLY'
    math_004_18.use_clamp = False

    # Node Math.005
    math_005_16 = _rr_lens_distortion.nodes.new("ShaderNodeMath")
    math_005_16.name = "Math.005"
    math_005_16.hide = True
    math_005_16.operation = 'MULTIPLY'
    math_005_16.use_clamp = False

    # Set locations
    group_output_34.location = (1983.554443359375, 196.00830078125)
    lens_distortion.location = (-58.7861328125, 143.5333251953125)
    set_alpha_1.location = (214.980712890625, 55.769203186035156)
    lens_distortion_alpha.location = (-56.42041015625, -60.10271453857422)
    group_input_30.location = (-1036.080078125, 11.373943328857422)
    separate_color_002_6.location = (-372.63641357421875, -157.70399475097656)
    lens_distortion_001.location = (926.1146240234375, -94.6041030883789)
    lens_distortion_002.location = (925.1439208984375, -236.38027954101562)
    separate_color_003_5.location = (700.9571533203125, -258.60888671875)
    set_alpha_001.location = (1216.67529296875, -146.3790740966797)
    group_input_001_12.location = (440.6395568847656, 226.28350830078125)
    math_27.location = (1221.196533203125, 300.2097473144531)
    switch_11.location = (1752.3902587890625, 218.3092498779297)
    math_001_21.location = (915.7676391601562, 307.887451171875)
    mix_24.location = (-712.3638916015625, 230.8922576904297)
    switch_001_2.location = (1477.4842529296875, -21.251853942871094)
    math_002_20.location = (-370.8260498046875, -68.57147216796875)
    math_003_19.location = (-369.88250732421875, -4.3948774337768555)
    math_004_18.location = (658.8317260742188, 142.59939575195312)
    math_005_16.location = (657.88818359375, 216.21383666992188)

    # Set dimensions
    group_output_34.width, group_output_34.height = 140.0, 100.0
    lens_distortion.width, lens_distortion.height = 200.70217895507812, 100.0
    set_alpha_1.width, set_alpha_1.height = 182.19448852539062, 100.0
    lens_distortion_alpha.width, lens_distortion_alpha.height = 200.70217895507812, 100.0
    group_input_30.width, group_input_30.height = 140.0, 100.0
    separate_color_002_6.width, separate_color_002_6.height = 140.0, 100.0
    lens_distortion_001.width, lens_distortion_001.height = 200.70217895507812, 100.0
    lens_distortion_002.width, lens_distortion_002.height = 200.70217895507812, 100.0
    separate_color_003_5.width, separate_color_003_5.height = 140.0, 100.0
    set_alpha_001.width, set_alpha_001.height = 180.39892578125, 100.0
    group_input_001_12.width, group_input_001_12.height = 140.0, 100.0
    math_27.width, math_27.height = 140.0, 100.0
    switch_11.width, switch_11.height = 140.0, 100.0
    math_001_21.width, math_001_21.height = 140.0, 100.0
    mix_24.width, mix_24.height = 140.0, 100.0
    switch_001_2.width, switch_001_2.height = 140.0, 100.0
    math_002_20.width, math_002_20.height = 140.0, 100.0
    math_003_19.width, math_003_19.height = 140.0, 100.0
    math_004_18.width, math_004_18.height = 140.0, 100.0
    math_005_16.width, math_005_16.height = 140.0, 100.0

    # Initialize _rr_lens_distortion links

    # group_input_30.Image -> lens_distortion.Image
    _rr_lens_distortion.links.new(group_input_30.outputs[1], lens_distortion.inputs[0])
    # lens_distortion.Image -> set_alpha_1.Image
    _rr_lens_distortion.links.new(lens_distortion.outputs[0], set_alpha_1.inputs[0])
    # separate_color_002_6.Alpha -> lens_distortion_alpha.Image
    _rr_lens_distortion.links.new(separate_color_002_6.outputs[3], lens_distortion_alpha.inputs[0])
    # group_input_30.Image -> separate_color_002_6.Image
    _rr_lens_distortion.links.new(group_input_30.outputs[1], separate_color_002_6.inputs[0])
    # lens_distortion_alpha.Image -> set_alpha_1.Alpha
    _rr_lens_distortion.links.new(lens_distortion_alpha.outputs[0], set_alpha_1.inputs[1])
    # set_alpha_1.Image -> lens_distortion_001.Image
    _rr_lens_distortion.links.new(set_alpha_1.outputs[0], lens_distortion_001.inputs[0])
    # set_alpha_1.Image -> separate_color_003_5.Image
    _rr_lens_distortion.links.new(set_alpha_1.outputs[0], separate_color_003_5.inputs[0])
    # separate_color_003_5.Alpha -> lens_distortion_002.Image
    _rr_lens_distortion.links.new(separate_color_003_5.outputs[3], lens_distortion_002.inputs[0])
    # lens_distortion_001.Image -> set_alpha_001.Image
    _rr_lens_distortion.links.new(lens_distortion_001.outputs[0], set_alpha_001.inputs[0])
    # lens_distortion_002.Image -> set_alpha_001.Alpha
    _rr_lens_distortion.links.new(lens_distortion_002.outputs[0], set_alpha_001.inputs[1])
    # math_001_21.Value -> math_27.Value
    _rr_lens_distortion.links.new(math_001_21.outputs[0], math_27.inputs[0])
    # group_input_001_12.Image -> switch_11.Off
    _rr_lens_distortion.links.new(group_input_001_12.outputs[1], switch_11.inputs[1])
    # math_27.Value -> switch_11.Switch
    _rr_lens_distortion.links.new(math_27.outputs[0], switch_11.inputs[0])
    # math_003_19.Value -> lens_distortion_alpha.Dispersion
    _rr_lens_distortion.links.new(math_003_19.outputs[0], lens_distortion_alpha.inputs[2])
    # set_alpha_001.Image -> switch_001_2.On
    _rr_lens_distortion.links.new(set_alpha_001.outputs[0], switch_001_2.inputs[2])
    # set_alpha_1.Image -> switch_001_2.Off
    _rr_lens_distortion.links.new(set_alpha_1.outputs[0], switch_001_2.inputs[1])
    # switch_001_2.Image -> switch_11.On
    _rr_lens_distortion.links.new(switch_001_2.outputs[0], switch_11.inputs[2])
    # group_input_001_12.Horizontal Dispersion -> switch_001_2.Switch
    _rr_lens_distortion.links.new(group_input_001_12.outputs[4], switch_001_2.inputs[0])
    # group_input_30.Horizontal Dispersion -> mix_24.Factor
    _rr_lens_distortion.links.new(group_input_30.outputs[4], mix_24.inputs[0])
    # group_input_30.Dispersion -> mix_24.A
    _rr_lens_distortion.links.new(group_input_30.outputs[3], mix_24.inputs[2])
    # switch_11.Image -> group_output_34.Image
    _rr_lens_distortion.links.new(switch_11.outputs[0], group_output_34.inputs[0])
    # group_input_30.Distortion -> math_002_20.Value
    _rr_lens_distortion.links.new(group_input_30.outputs[2], math_002_20.inputs[1])
    # group_input_30.Factor -> math_002_20.Value
    _rr_lens_distortion.links.new(group_input_30.outputs[0], math_002_20.inputs[0])
    # math_002_20.Value -> lens_distortion.Distortion
    _rr_lens_distortion.links.new(math_002_20.outputs[0], lens_distortion.inputs[1])
    # math_002_20.Value -> lens_distortion_alpha.Distortion
    _rr_lens_distortion.links.new(math_002_20.outputs[0], lens_distortion_alpha.inputs[1])
    # mix_24.Result -> math_003_19.Value
    _rr_lens_distortion.links.new(mix_24.outputs[0], math_003_19.inputs[0])
    # group_input_30.Factor -> math_003_19.Value
    _rr_lens_distortion.links.new(group_input_30.outputs[0], math_003_19.inputs[1])
    # math_003_19.Value -> lens_distortion.Dispersion
    _rr_lens_distortion.links.new(math_003_19.outputs[0], lens_distortion.inputs[2])
    # group_input_001_12.Factor -> math_004_18.Value
    _rr_lens_distortion.links.new(group_input_001_12.outputs[0], math_004_18.inputs[0])
    # group_input_001_12.Dispersion -> math_004_18.Value
    _rr_lens_distortion.links.new(group_input_001_12.outputs[3], math_004_18.inputs[1])
    # math_004_18.Value -> math_27.Value
    _rr_lens_distortion.links.new(math_004_18.outputs[0], math_27.inputs[1])
    # math_004_18.Value -> lens_distortion_001.Dispersion
    _rr_lens_distortion.links.new(math_004_18.outputs[0], lens_distortion_001.inputs[2])
    # math_004_18.Value -> lens_distortion_002.Dispersion
    _rr_lens_distortion.links.new(math_004_18.outputs[0], lens_distortion_002.inputs[2])
    # group_input_001_12.Factor -> math_005_16.Value
    _rr_lens_distortion.links.new(group_input_001_12.outputs[0], math_005_16.inputs[0])
    # group_input_001_12.Distortion -> math_005_16.Value
    _rr_lens_distortion.links.new(group_input_001_12.outputs[2], math_005_16.inputs[1])
    # math_005_16.Value -> math_001_21.Value
    _rr_lens_distortion.links.new(math_005_16.outputs[0], math_001_21.inputs[0])

    return _rr_lens_distortion


_rr_lens_distortion = _rr_lens_distortion_node_group()

def _rr_post_node_group():
    """Initialize .RR_Post node group"""
    _rr_post = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_Post")

    _rr_post.color_tag = 'NONE'
    _rr_post.description = ""
    _rr_post.default_group_node_width = 140
    # _rr_post interface

    # Socket Image
    image_socket_52 = _rr_post.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_52.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_52.attribute_domain = 'POINT'
    image_socket_52.default_input = 'VALUE'
    image_socket_52.structure_type = 'AUTO'

    # Socket Image
    image_socket_53 = _rr_post.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_53.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_53.attribute_domain = 'POINT'
    image_socket_53.default_input = 'VALUE'
    image_socket_53.structure_type = 'AUTO'

    # Socket sRGB
    srgb_socket_1 = _rr_post.interface.new_socket(name="sRGB", in_out='INPUT', socket_type='NodeSocketColor')
    srgb_socket_1.default_value = (1.0, 1.0, 1.0, 1.0)
    srgb_socket_1.attribute_domain = 'POINT'
    srgb_socket_1.default_input = 'VALUE'
    srgb_socket_1.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_18 = _rr_post.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_18.default_value = 1.0
    factor_socket_18.min_value = 0.0
    factor_socket_18.max_value = 1.0
    factor_socket_18.subtype = 'FACTOR'
    factor_socket_18.attribute_domain = 'POINT'
    factor_socket_18.default_input = 'VALUE'
    factor_socket_18.structure_type = 'AUTO'

    # Initialize _rr_post nodes

    # Node Post Layer Output
    post_layer_output = _rr_post.nodes.new("NodeGroupOutput")
    post_layer_output.label = "Post Layer Output"
    post_layer_output.name = "Post Layer Output"
    post_layer_output.hide = True
    post_layer_output.is_active_output = True
    post_layer_output.inputs[1].hide = True

    # Node Post Layer Input
    post_layer_input = _rr_post.nodes.new("NodeGroupInput")
    post_layer_input.label = "Post Layer Input"
    post_layer_input.name = "Post Layer Input"

    # Node Frame.001
    frame_001_13 = _rr_post.nodes.new("NodeFrame")
    frame_001_13.label = "Post Color"
    frame_001_13.name = "Frame.001"
    frame_001_13.mute = True
    frame_001_13.label_size = 20
    frame_001_13.shrink = True

    # Node Frame.006
    frame_006 = _rr_post.nodes.new("NodeFrame")
    frame_006.label = "Post Values"
    frame_006.name = "Frame.006"
    frame_006.label_size = 20
    frame_006.shrink = True

    # Node Frame
    frame_16 = _rr_post.nodes.new("NodeFrame")
    frame_16.label = "Detail"
    frame_16.name = "Frame"
    frame_16.label_size = 20
    frame_16.shrink = True

    # Node Frame.007
    frame_007 = _rr_post.nodes.new("NodeFrame")
    frame_007.label = "Post Effects"
    frame_007.name = "Frame.007"
    frame_007.mute = True
    frame_007.label_size = 20
    frame_007.shrink = True

    # Node Reroute.006
    reroute_006_5 = _rr_post.nodes.new("NodeReroute")
    reroute_006_5.name = "Reroute.006"
    reroute_006_5.socket_idname = "NodeSocketColor"
    # Node Reroute.007
    reroute_007_6 = _rr_post.nodes.new("NodeReroute")
    reroute_007_6.name = "Reroute.007"
    reroute_007_6.socket_idname = "NodeSocketColor"
    # Node Reroute.005
    reroute_005_10 = _rr_post.nodes.new("NodeReroute")
    reroute_005_10.name = "Reroute.005"
    reroute_005_10.socket_idname = "NodeSocketColor"
    # Node Texture
    texture = _rr_post.nodes.new("CompositorNodeGroup")
    texture.label = "Texture"
    texture.name = "Texture"
    texture.use_custom_color = True
    texture.color = (0.0, 0.0, 0.0)
    texture.mute = True
    texture.hide = True
    texture.node_tree = _rr_texture
    texture.inputs[1].hide = True
    texture.inputs[2].hide = True
    # Socket_2
    texture.inputs[1].default_value = 0.0
    # Socket_3
    texture.inputs[2].default_value = 1.0

    # Node Reroute.004
    reroute_004_9 = _rr_post.nodes.new("NodeReroute")
    reroute_004_9.name = "Reroute.004"
    reroute_004_9.mute = True
    reroute_004_9.socket_idname = "NodeSocketColor"
    # Node Sharpness
    sharpness = _rr_post.nodes.new("CompositorNodeGroup")
    sharpness.label = "Sharpness"
    sharpness.name = "Sharpness"
    sharpness.use_custom_color = True
    sharpness.color = (0.0, 0.0, 0.0)
    sharpness.hide = True
    sharpness.node_tree = _rr_sharpness
    sharpness.inputs[1].hide = True
    sharpness.inputs[2].hide = True
    sharpness.outputs[1].hide = True
    # Socket_2
    sharpness.inputs[1].default_value = 0.10000000149011612
    # Socket_3
    sharpness.inputs[2].default_value = 0.0

    # Node Clarity
    clarity = _rr_post.nodes.new("CompositorNodeGroup")
    clarity.label = "Clarity"
    clarity.name = "Clarity"
    clarity.use_custom_color = True
    clarity.color = (0.0, 0.0, 0.0)
    clarity.mute = True
    clarity.hide = True
    clarity.node_tree = _rr_clarity
    clarity.inputs[1].hide = True
    clarity.inputs[2].hide = True
    # Socket_3
    clarity.inputs[1].default_value = 0.10000000149011612
    # Socket_2
    clarity.inputs[2].default_value = 0.5

    # Node Curves
    curves_1 = _rr_post.nodes.new("CompositorNodeCurveRGB")
    curves_1.label = "Curves"
    curves_1.name = "Curves"
    curves_1.use_custom_color = True
    curves_1.color = (0.0, 0.0, 0.0)
    curves_1.hide = True
    # Mapping settings
    curves_1.mapping.extend = 'EXTRAPOLATED'
    curves_1.mapping.tone = 'STANDARD'
    curves_1.mapping.black_level = (0.0, 0.0, 0.0)
    curves_1.mapping.white_level = (1.0, 1.0, 1.0)
    curves_1.mapping.clip_min_x = 0.0
    curves_1.mapping.clip_min_y = 0.0
    curves_1.mapping.clip_max_x = 1.0
    curves_1.mapping.clip_max_y = 1.0
    curves_1.mapping.use_clip = True
    # Curve 0
    curves_1_curve_0 = curves_1.mapping.curves[0]
    curves_1_curve_0_point_0 = curves_1_curve_0.points[0]
    curves_1_curve_0_point_0.location = (0.0, 0.0)
    curves_1_curve_0_point_0.handle_type = 'AUTO'
    curves_1_curve_0_point_1 = curves_1_curve_0.points[1]
    curves_1_curve_0_point_1.location = (1.0, 1.0)
    curves_1_curve_0_point_1.handle_type = 'AUTO'
    # Curve 1
    curves_1_curve_1 = curves_1.mapping.curves[1]
    curves_1_curve_1_point_0 = curves_1_curve_1.points[0]
    curves_1_curve_1_point_0.location = (0.0, 0.0)
    curves_1_curve_1_point_0.handle_type = 'AUTO'
    curves_1_curve_1_point_1 = curves_1_curve_1.points[1]
    curves_1_curve_1_point_1.location = (1.0, 1.0)
    curves_1_curve_1_point_1.handle_type = 'AUTO'
    # Curve 2
    curves_1_curve_2 = curves_1.mapping.curves[2]
    curves_1_curve_2_point_0 = curves_1_curve_2.points[0]
    curves_1_curve_2_point_0.location = (0.0, 0.0)
    curves_1_curve_2_point_0.handle_type = 'AUTO'
    curves_1_curve_2_point_1 = curves_1_curve_2.points[1]
    curves_1_curve_2_point_1.location = (1.0, 1.0)
    curves_1_curve_2_point_1.handle_type = 'AUTO'
    # Curve 3
    curves_1_curve_3 = curves_1.mapping.curves[3]
    curves_1_curve_3_point_0 = curves_1_curve_3.points[0]
    curves_1_curve_3_point_0.location = (0.0, 0.0)
    curves_1_curve_3_point_0.handle_type = 'AUTO'
    curves_1_curve_3_point_1 = curves_1_curve_3.points[1]
    curves_1_curve_3_point_1.location = (1.0, 1.0)
    curves_1_curve_3_point_1.handle_type = 'AUTO'
    # Update curve after changes
    curves_1.mapping.update()
    curves_1.inputs[0].hide = True
    curves_1.inputs[2].hide = True
    curves_1.inputs[3].hide = True
    # Fac
    curves_1.inputs[0].default_value = 1.0
    # Black Level
    curves_1.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # White Level
    curves_1.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Color Blending
    color_blending = _rr_post.nodes.new("CompositorNodeGroup")
    color_blending.label = "Color Blending"
    color_blending.name = "Color Blending"
    color_blending.use_custom_color = True
    color_blending.color = (0.0, 0.0, 0.0)
    color_blending.hide = True
    color_blending.node_tree = _rr_color_blending
    color_blending.inputs[1].hide = True
    color_blending.inputs[2].hide = True
    color_blending.inputs[3].hide = True
    color_blending.inputs[4].hide = True
    color_blending.inputs[5].hide = True
    color_blending.inputs[6].hide = True
    color_blending.inputs[7].hide = True
    color_blending.inputs[8].hide = True
    color_blending.inputs[9].hide = True
    # Socket_7
    color_blending.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
    # Socket_2
    color_blending.inputs[2].default_value = 0.5
    # Socket_5
    color_blending.inputs[3].default_value = 1.0
    # Socket_12
    color_blending.inputs[4].default_value = (0.5, 0.5, 0.5, 1.0)
    # Socket_3
    color_blending.inputs[5].default_value = 0.5
    # Socket_11
    color_blending.inputs[6].default_value = 1.0
    # Socket_13
    color_blending.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
    # Socket_4
    color_blending.inputs[8].default_value = 0.5
    # Socket_10
    color_blending.inputs[9].default_value = 1.0

    # Node Values
    values = _rr_post.nodes.new("CompositorNodeGroup")
    values.label = "Values"
    values.name = "Values"
    values.use_custom_color = True
    values.color = (0.0, 0.0, 0.0)
    values.mute = True
    values.hide = True
    values.node_tree = _rr_values
    values.inputs[1].hide = True
    values.inputs[2].hide = True
    values.inputs[3].hide = True
    values.inputs[4].hide = True
    # Socket_2
    values.inputs[1].default_value = 0.0
    # Socket_4
    values.inputs[2].default_value = 0.5
    # Socket_5
    values.inputs[3].default_value = 0.0
    # Socket_3
    values.inputs[4].default_value = 0.0

    # Node Saturation
    saturation_1 = _rr_post.nodes.new("CompositorNodeGroup")
    saturation_1.label = "Saturation"
    saturation_1.name = "Saturation"
    saturation_1.use_custom_color = True
    saturation_1.color = (0.0, 0.0, 0.0)
    saturation_1.hide = True
    saturation_1.node_tree = _rr_saturation
    saturation_1.inputs[0].hide = True
    saturation_1.inputs[2].hide = True
    saturation_1.inputs[3].hide = True
    # Socket_4
    saturation_1.inputs[0].default_value = 1.0
    # Socket_2
    saturation_1.inputs[2].default_value = 0.8999999761581421
    # Socket_3
    saturation_1.inputs[3].default_value = 1.0

    # Node Value Saturation
    value_saturation = _rr_post.nodes.new("CompositorNodeGroup")
    value_saturation.label = "Value Saturation"
    value_saturation.name = "Value Saturation"
    value_saturation.use_custom_color = True
    value_saturation.color = (0.0, 0.0, 0.0)
    value_saturation.mute = True
    value_saturation.hide = True
    value_saturation.node_tree = _rr_value_saturation
    value_saturation.inputs[0].hide = True
    value_saturation.inputs[2].hide = True
    value_saturation.inputs[3].hide = True
    value_saturation.inputs[4].hide = True
    value_saturation.inputs[5].hide = True
    value_saturation.inputs[6].hide = True
    value_saturation.inputs[7].hide = True
    value_saturation.inputs[8].hide = True
    # Socket_9
    value_saturation.inputs[0].default_value = 1.0
    # Socket_3
    value_saturation.inputs[2].default_value = 0.5
    # Socket_5
    value_saturation.inputs[3].default_value = 1.0
    # Socket_6
    value_saturation.inputs[4].default_value = 1.0
    # Socket_4
    value_saturation.inputs[5].default_value = 0.5
    # Socket_2
    value_saturation.inputs[6].default_value = 0.5
    # Socket_7
    value_saturation.inputs[7].default_value = 0.5
    # Socket_8
    value_saturation.inputs[8].default_value = 0.5

    # Node Hue Correct
    hue_correct_3 = _rr_post.nodes.new("CompositorNodeGroup")
    hue_correct_3.label = "Hue Correct"
    hue_correct_3.name = "Hue Correct"
    hue_correct_3.use_custom_color = True
    hue_correct_3.color = (0.0, 0.0, 0.0)
    hue_correct_3.hide = True
    hue_correct_3.node_tree = _rr_hue_correct
    hue_correct_3.inputs[0].hide = True
    hue_correct_3.inputs[3].hide = True
    hue_correct_3.inputs[4].hide = True
    hue_correct_3.inputs[5].hide = True
    hue_correct_3.inputs[6].hide = True
    hue_correct_3.inputs[7].hide = True
    hue_correct_3.inputs[8].hide = True
    hue_correct_3.inputs[9].hide = True
    hue_correct_3.inputs[10].hide = True
    hue_correct_3.inputs[11].hide = True
    hue_correct_3.inputs[12].hide = True
    hue_correct_3.inputs[13].hide = True
    hue_correct_3.inputs[14].hide = True
    hue_correct_3.inputs[15].hide = True
    hue_correct_3.inputs[16].hide = True
    hue_correct_3.inputs[17].hide = True
    hue_correct_3.inputs[18].hide = True
    hue_correct_3.inputs[19].hide = True
    hue_correct_3.inputs[20].hide = True
    hue_correct_3.inputs[21].hide = True
    hue_correct_3.inputs[22].hide = True
    hue_correct_3.inputs[23].hide = True
    hue_correct_3.inputs[24].hide = True
    hue_correct_3.inputs[25].hide = True
    hue_correct_3.inputs[26].hide = True
    hue_correct_3.inputs[27].hide = True
    hue_correct_3.inputs[28].hide = True
    # Socket_30
    hue_correct_3.inputs[0].default_value = 0.5
    # Socket_18
    hue_correct_3.inputs[3].default_value = 1.0
    # Socket_31
    hue_correct_3.inputs[4].default_value = 0.20000000298023224
    # Socket_22
    hue_correct_3.inputs[5].default_value = 0.0
    # Socket_32
    hue_correct_3.inputs[6].default_value = 1.0
    # Socket_33
    hue_correct_3.inputs[7].default_value = 0.0
    # Socket_6
    hue_correct_3.inputs[8].default_value = 0.5
    # Socket_7
    hue_correct_3.inputs[9].default_value = 1.0
    # Socket_8
    hue_correct_3.inputs[10].default_value = 0.5
    # Socket_9
    hue_correct_3.inputs[11].default_value = 0.5
    # Socket_2
    hue_correct_3.inputs[12].default_value = 0.5
    # Socket_4
    hue_correct_3.inputs[13].default_value = 0.5
    # Socket_5
    hue_correct_3.inputs[14].default_value = 0.5
    # Socket_11
    hue_correct_3.inputs[15].default_value = 1.0
    # Socket_12
    hue_correct_3.inputs[16].default_value = 1.0
    # Socket_13
    hue_correct_3.inputs[17].default_value = 0.8999999761581421
    # Socket_14
    hue_correct_3.inputs[18].default_value = 0.0
    # Socket_15
    hue_correct_3.inputs[19].default_value = 0.0
    # Socket_16
    hue_correct_3.inputs[20].default_value = 0.0
    # Socket_17
    hue_correct_3.inputs[21].default_value = 0.0
    # Socket_23
    hue_correct_3.inputs[22].default_value = 1.0
    # Socket_24
    hue_correct_3.inputs[23].default_value = 1.0
    # Socket_25
    hue_correct_3.inputs[24].default_value = 1.0
    # Socket_26
    hue_correct_3.inputs[25].default_value = 1.0
    # Socket_27
    hue_correct_3.inputs[26].default_value = 1.0
    # Socket_28
    hue_correct_3.inputs[27].default_value = 1.0
    # Socket_29
    hue_correct_3.inputs[28].default_value = 1.0

    # Node Lift Gamma Gain
    lift_gamma_gain = _rr_post.nodes.new("CompositorNodeColorBalance")
    lift_gamma_gain.label = "Lift Gamma Gain"
    lift_gamma_gain.name = "Lift Gamma Gain"
    lift_gamma_gain.use_custom_color = True
    lift_gamma_gain.color = (0.0, 0.0, 0.0)
    lift_gamma_gain.mute = True
    lift_gamma_gain.hide = True
    lift_gamma_gain.correction_method = 'LIFT_GAMMA_GAIN'
    lift_gamma_gain.input_whitepoint = mathutils.Color((0.9991403222084045, 1.0003736019134521, 0.998818039894104))
    lift_gamma_gain.output_whitepoint = mathutils.Color((0.9991403222084045, 1.0003736019134521, 0.998818039894104))
    lift_gamma_gain.inputs[0].hide = True
    lift_gamma_gain.inputs[2].hide = True
    lift_gamma_gain.inputs[3].hide = True
    lift_gamma_gain.inputs[4].hide = True
    lift_gamma_gain.inputs[5].hide = True
    lift_gamma_gain.inputs[6].hide = True
    lift_gamma_gain.inputs[7].hide = True
    lift_gamma_gain.inputs[8].hide = True
    lift_gamma_gain.inputs[9].hide = True
    lift_gamma_gain.inputs[10].hide = True
    lift_gamma_gain.inputs[11].hide = True
    lift_gamma_gain.inputs[12].hide = True
    lift_gamma_gain.inputs[13].hide = True
    lift_gamma_gain.inputs[14].hide = True
    lift_gamma_gain.inputs[15].hide = True
    lift_gamma_gain.inputs[16].hide = True
    lift_gamma_gain.inputs[17].hide = True
    # Fac
    lift_gamma_gain.inputs[0].default_value = 1.0
    # Base Lift
    lift_gamma_gain.inputs[2].default_value = 0.0
    # Color Lift
    lift_gamma_gain.inputs[3].default_value = (1.0, 1.0, 1.0, 1.0)
    # Base Gamma
    lift_gamma_gain.inputs[4].default_value = 1.0
    # Color Gamma
    lift_gamma_gain.inputs[5].default_value = (1.0, 1.0, 1.0, 1.0)
    # Base Gain
    lift_gamma_gain.inputs[6].default_value = 1.0
    # Color Gain
    lift_gamma_gain.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)

    # Node Vignette
    vignette_1 = _rr_post.nodes.new("CompositorNodeGroup")
    vignette_1.label = "Vignette"
    vignette_1.name = "Vignette"
    vignette_1.use_custom_color = True
    vignette_1.color = (0.0, 0.0, 0.0)
    vignette_1.hide = True
    vignette_1.node_tree = _rr_vignette
    vignette_1.inputs[1].hide = True
    vignette_1.inputs[2].hide = True
    vignette_1.inputs[3].hide = True
    vignette_1.inputs[4].hide = True
    vignette_1.inputs[5].hide = True
    vignette_1.inputs[6].hide = True
    vignette_1.inputs[7].hide = True
    vignette_1.inputs[8].hide = True
    vignette_1.inputs[9].hide = True
    vignette_1.inputs[10].hide = True
    vignette_1.inputs[11].hide = True
    vignette_1.outputs[1].hide = True
    # Socket_12
    vignette_1.inputs[1].default_value = 0.13076923787593842
    # Socket_9
    vignette_1.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    # Socket_17
    vignette_1.inputs[3].default_value = 0.0
    # Socket_11
    vignette_1.inputs[4].default_value = 0.0
    # Socket_2
    vignette_1.inputs[5].default_value = 1.0
    # Socket_3
    vignette_1.inputs[6].default_value = 0.5
    # Socket_4
    vignette_1.inputs[7].default_value = 1.0
    # Socket_5
    vignette_1.inputs[8].default_value = 1.0
    # Socket_10
    vignette_1.inputs[9].default_value = 0.0
    # Socket_6
    vignette_1.inputs[10].default_value = 0.0
    # Socket_7
    vignette_1.inputs[11].default_value = 0.0

    # Node Preserve Color
    preserve_color = _rr_post.nodes.new("CompositorNodeGroup")
    preserve_color.label = "Preserve Color"
    preserve_color.name = "Preserve Color"
    preserve_color.use_custom_color = True
    preserve_color.color = (0.0, 0.0, 0.0)
    preserve_color.mute = True
    preserve_color.hide = True
    preserve_color.node_tree = _rr_preserve_color
    preserve_color.inputs[2].hide = True
    preserve_color.inputs[3].hide = True
    preserve_color.inputs[4].hide = True
    preserve_color.inputs[5].hide = True
    preserve_color.inputs[6].hide = True
    # Socket_7
    preserve_color.inputs[2].default_value = 0.0
    # Socket_2
    preserve_color.inputs[3].default_value = 1.0
    # Socket_4
    preserve_color.inputs[4].default_value = 0.0
    # Socket_6
    preserve_color.inputs[5].default_value = 4.0
    # Socket_8
    preserve_color.inputs[6].default_value = 0.0

    # Node Fix Clipping
    fix_clipping_1 = _rr_post.nodes.new("CompositorNodeGroup")
    fix_clipping_1.label = "Fix Clipping"
    fix_clipping_1.name = "Fix Clipping"
    fix_clipping_1.use_custom_color = True
    fix_clipping_1.color = (0.0, 0.0, 0.0)
    fix_clipping_1.mute = True
    fix_clipping_1.hide = True
    fix_clipping_1.node_tree = _rr_fix_clipping
    fix_clipping_1.inputs[0].hide = True
    fix_clipping_1.inputs[2].hide = True
    # Socket_6
    fix_clipping_1.inputs[0].default_value = 1.0
    # Socket_3
    fix_clipping_1.inputs[2].default_value = 1.0

    # Node Density
    density = _rr_post.nodes.new("CompositorNodeGroup")
    density.label = "Density"
    density.name = "Density"
    density.use_custom_color = True
    density.color = (0.0, 0.0, 0.0)
    density.hide = True
    density.node_tree = _rr_color_density
    density.inputs[1].hide = True
    density.inputs[2].hide = True
    # Socket_2
    density.inputs[1].default_value = 0.10000000149011612
    # Socket_3
    density.inputs[2].default_value = 0.5

    # Node Mix
    mix_25 = _rr_post.nodes.new("ShaderNodeMix")
    mix_25.name = "Mix"
    mix_25.hide = True
    mix_25.blend_type = 'MIX'
    mix_25.clamp_factor = True
    mix_25.clamp_result = False
    mix_25.data_type = 'RGBA'
    mix_25.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_18 = _rr_post.nodes.new("NodeReroute")
    reroute_18.name = "Reroute"
    reroute_18.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.002
    reroute_002_11 = _rr_post.nodes.new("NodeReroute")
    reroute_002_11.name = "Reroute.002"
    reroute_002_11.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.003
    reroute_003_11 = _rr_post.nodes.new("NodeReroute")
    reroute_003_11.name = "Reroute.003"
    reroute_003_11.socket_idname = "NodeSocketColor"
    # Node Negative Bleed
    negative_bleed = _rr_post.nodes.new("CompositorNodeGroup")
    negative_bleed.label = "Negative Bleed"
    negative_bleed.name = "Negative Bleed"
    negative_bleed.use_custom_color = True
    negative_bleed.color = (0.0, 0.0, 0.0)
    negative_bleed.mute = True
    negative_bleed.hide = True
    negative_bleed.node_tree = _rr_negative_bleed
    negative_bleed.inputs[1].hide = True
    negative_bleed.inputs[2].hide = True
    # Socket_2
    negative_bleed.inputs[1].default_value = 0.0
    # Socket_3
    negative_bleed.inputs[2].default_value = 0.0

    # Node Film Grain Fast
    film_grain_fast = _rr_post.nodes.new("CompositorNodeGroup")
    film_grain_fast.label = "Film Grain Fast"
    film_grain_fast.name = "Film Grain Fast"
    film_grain_fast.use_custom_color = True
    film_grain_fast.color = (0.0, 0.0, 0.0)
    film_grain_fast.mute = True
    film_grain_fast.hide = True
    film_grain_fast.node_tree = _rr_grain_fast
    film_grain_fast.inputs[2].hide = True
    film_grain_fast.inputs[3].hide = True
    film_grain_fast.inputs[4].hide = True
    film_grain_fast.inputs[5].hide = True
    film_grain_fast.inputs[6].hide = True
    # Socket_3
    film_grain_fast.inputs[2].default_value = 0.6615384817123413
    # Socket_2
    film_grain_fast.inputs[3].default_value = 10.0
    # Socket_7
    film_grain_fast.inputs[4].default_value = 2.0
    # Socket_5
    film_grain_fast.inputs[5].default_value = 0.25
    # Socket_6
    film_grain_fast.inputs[6].default_value = False

    # Node Film Grain Accurate
    film_grain_accurate = _rr_post.nodes.new("CompositorNodeGroup")
    film_grain_accurate.label = "Film Grain Accurate"
    film_grain_accurate.name = "Film Grain Accurate"
    film_grain_accurate.use_custom_color = True
    film_grain_accurate.color = (0.0, 0.0, 0.0)
    film_grain_accurate.mute = True
    film_grain_accurate.hide = True
    film_grain_accurate.node_tree = _rr_grain_accurate
    film_grain_accurate.inputs[2].hide = True
    film_grain_accurate.inputs[3].hide = True
    film_grain_accurate.inputs[4].hide = True
    film_grain_accurate.inputs[5].hide = True
    # Input_2
    film_grain_accurate.inputs[2].default_value = 1.0
    # Input_4
    film_grain_accurate.inputs[3].default_value = 10.0
    # Socket_1
    film_grain_accurate.inputs[4].default_value = 0.25
    # Socket_2
    film_grain_accurate.inputs[5].default_value = False

    # Node Reroute.001
    reroute_001_13 = _rr_post.nodes.new("NodeReroute")
    reroute_001_13.name = "Reroute.001"
    reroute_001_13.socket_idname = "NodeSocketFloatFactor"
    # Node Reroute.008
    reroute_008_4 = _rr_post.nodes.new("NodeReroute")
    reroute_008_4.name = "Reroute.008"
    reroute_008_4.socket_idname = "NodeSocketFloatFactor"
    # Node Split Tone
    split_tone = _rr_post.nodes.new("CompositorNodeGroup")
    split_tone.label = "Split Tone"
    split_tone.name = "Split Tone"
    split_tone.use_custom_color = True
    split_tone.color = (0.0, 0.0, 0.0)
    split_tone.mute = True
    split_tone.hide = True
    split_tone.node_tree = _rr_split_tone
    split_tone.inputs[1].hide = True
    # Socket_2
    split_tone.inputs[1].default_value = 0.0

    # Node Lens Distortion
    lens_distortion_1 = _rr_post.nodes.new("CompositorNodeGroup")
    lens_distortion_1.label = "Lens Distortion"
    lens_distortion_1.name = "Lens Distortion"
    lens_distortion_1.use_custom_color = True
    lens_distortion_1.color = (0.0, 0.0, 0.0)
    lens_distortion_1.hide = True
    lens_distortion_1.node_tree = _rr_lens_distortion
    lens_distortion_1.inputs[2].hide = True
    lens_distortion_1.inputs[3].hide = True
    lens_distortion_1.inputs[4].hide = True
    # Socket_2
    lens_distortion_1.inputs[2].default_value = 0.0
    # Socket_3
    lens_distortion_1.inputs[3].default_value = 0.0024999999441206455
    # Socket_4
    lens_distortion_1.inputs[4].default_value = False

    # Node Reroute.009
    reroute_009_4 = _rr_post.nodes.new("NodeReroute")
    reroute_009_4.name = "Reroute.009"
    reroute_009_4.socket_idname = "NodeSocketFloatFactor"
    # Set parents
    texture.parent = frame_16
    sharpness.parent = frame_16
    clarity.parent = frame_16
    curves_1.parent = frame_006
    color_blending.parent = frame_001_13
    values.parent = frame_006
    saturation_1.parent = frame_001_13
    value_saturation.parent = frame_001_13
    hue_correct_3.parent = frame_001_13
    lift_gamma_gain.parent = frame_001_13
    vignette_1.parent = frame_007
    fix_clipping_1.parent = frame_007
    density.parent = frame_001_13
    mix_25.parent = frame_007
    reroute_002_11.parent = frame_007
    negative_bleed.parent = frame_16
    film_grain_fast.parent = frame_007
    film_grain_accurate.parent = frame_007
    reroute_001_13.parent = frame_007
    reroute_008_4.parent = frame_007
    split_tone.parent = frame_001_13
    lens_distortion_1.parent = frame_007
    reroute_009_4.parent = frame_007

    # Set locations
    post_layer_output.location = (919.3887329101562, -180.32693481445312)
    post_layer_input.location = (-997.5892333984375, 82.97206115722656)
    frame_001_13.location = (-548.0, 61.0)
    frame_006.location = (-372.0, 241.0)
    frame_16.location = (128.0, 241.5)
    frame_007.location = (-497.5, -98.71450805664062)
    reroute_006_5.location = (1128.12646484375, -73.5609130859375)
    reroute_007_6.location = (-580.0, -73.5609130859375)
    reroute_005_10.location = (-632.3251953125, 80.0)
    texture.location = (249.99658203125, -41.5)
    reroute_004_9.location = (1112.42724609375, 80.0)
    sharpness.location = (29.99658203125, -41.5)
    clarity.location = (469.99658203125, -41.5)
    curves_1.location = (229.99658203125, -41.0)
    color_blending.location = (1137.009033203125, -41.0)
    values.location = (29.99658203125, -41.0)
    saturation_1.location = (469.6962890625, -41.0)
    value_saturation.location = (677.0089721679688, -41.0)
    hue_correct_3.location = (30.14532470703125, -41.07311248779297)
    lift_gamma_gain.location = (917.0089721679688, -41.0)
    vignette_1.location = (29.96075439453125, -120.47935485839844)
    preserve_color.location = (-591.8577880859375, 199.1927032470703)
    fix_clipping_1.location = (243.5263671875, -120.56977844238281)
    density.location = (256.3444519042969, -41.0)
    mix_25.location = (484.7643127441406, -83.67062377929688)
    reroute_18.location = (-578.428466796875, -136.97686767578125)
    reroute_002_11.location = (400.98388671875, -41.0)
    reroute_003_11.location = (-579.629150390625, -194.0041046142578)
    negative_bleed.location = (681.944091796875, -40.968505859375)
    film_grain_fast.location = (1155.31884765625, -80.86578369140625)
    film_grain_accurate.location = (902.3543701171875, -80.86578369140625)
    reroute_001_13.location = (827.791015625, -41.0)
    reroute_008_4.location = (1052.978515625, -41.0)
    split_tone.location = (1378.50390625, -41.0)
    lens_distortion_1.location = (671.1334838867188, -80.86578369140625)
    reroute_009_4.location = (616.7164306640625, -41.0)

    # Set dimensions
    post_layer_output.width, post_layer_output.height = 170.8353271484375, 100.0
    post_layer_input.width, post_layer_input.height = 154.64678955078125, 100.0
    frame_001_13.width, frame_001_13.height = 1602.5057373046875, 96.0
    frame_006.width, frame_006.height = 455.64495849609375, 96.0
    frame_16.width, frame_16.height = 883.71728515625, 96.5
    frame_007.width, frame_007.height = 1346.3819580078125, 175.78549194335938
    reroute_006_5.width, reroute_006_5.height = 20.0, 100.0
    reroute_007_6.width, reroute_007_6.height = 20.0, 100.0
    reroute_005_10.width, reroute_005_10.height = 20.0, 100.0
    texture.width, texture.height = 170.73504638671875, 100.0
    reroute_004_9.width, reroute_004_9.height = 20.0, 100.0
    sharpness.width, sharpness.height = 175.73878479003906, 100.0
    clarity.width, clarity.height = 172.8656768798828, 100.0
    curves_1.width, curves_1.height = 195.64495849609375, 100.0
    color_blending.width, color_blending.height = 194.00572204589844, 100.0
    values.width, values.height = 146.86895751953125, 100.0
    saturation_1.width, saturation_1.height = 169.08709716796875, 100.0
    value_saturation.width, value_saturation.height = 201.94776916503906, 100.0
    hue_correct_3.width, hue_correct_3.height = 176.6262664794922, 100.0
    lift_gamma_gain.width, lift_gamma_gain.height = 180.0, 100.0
    vignette_1.width, vignette_1.height = 160.0, 100.0
    preserve_color.width, preserve_color.height = 169.08709716796875, 100.0
    fix_clipping_1.width, fix_clipping_1.height = 162.7245635986328, 100.0
    density.width, density.height = 169.08709716796875, 100.0
    mix_25.width, mix_25.height = 140.0, 100.0
    reroute_18.width, reroute_18.height = 20.0, 100.0
    reroute_002_11.width, reroute_002_11.height = 20.0, 100.0
    reroute_003_11.width, reroute_003_11.height = 20.0, 100.0
    negative_bleed.width, negative_bleed.height = 171.71728515625, 100.0
    film_grain_fast.width, film_grain_fast.height = 160.8819580078125, 100.0
    film_grain_accurate.width, film_grain_accurate.height = 160.1343536376953, 100.0
    reroute_001_13.width, reroute_001_13.height = 20.0, 100.0
    reroute_008_4.width, reroute_008_4.height = 20.0, 100.0
    split_tone.width, split_tone.height = 194.00572204589844, 100.0
    lens_distortion_1.width, lens_distortion_1.height = 157.50161743164062, 100.0
    reroute_009_4.width, reroute_009_4.height = 20.0, 100.0

    # Initialize _rr_post links

    # curves_1.Image -> sharpness.Image
    _rr_post.links.new(curves_1.outputs[0], sharpness.inputs[0])
    # reroute_004_9.Output -> reroute_005_10.Input
    _rr_post.links.new(reroute_004_9.outputs[0], reroute_005_10.inputs[0])
    # texture.Image -> clarity.Image
    _rr_post.links.new(texture.outputs[0], clarity.inputs[0])
    # preserve_color.Image -> values.Image
    _rr_post.links.new(preserve_color.outputs[0], values.inputs[0])
    # reroute_006_5.Output -> reroute_007_6.Input
    _rr_post.links.new(reroute_006_5.outputs[0], reroute_007_6.inputs[0])
    # sharpness.Image -> texture.Image
    _rr_post.links.new(sharpness.outputs[0], texture.inputs[0])
    # values.Image -> curves_1.Image
    _rr_post.links.new(values.outputs[0], curves_1.inputs[1])
    # value_saturation.Image -> lift_gamma_gain.Image
    _rr_post.links.new(value_saturation.outputs[0], lift_gamma_gain.inputs[1])
    # lift_gamma_gain.Image -> color_blending.Input
    _rr_post.links.new(lift_gamma_gain.outputs[0], color_blending.inputs[0])
    # density.Image -> saturation_1.Image
    _rr_post.links.new(density.outputs[0], saturation_1.inputs[1])
    # post_layer_input.Image -> preserve_color.Image
    _rr_post.links.new(post_layer_input.outputs[0], preserve_color.inputs[0])
    # post_layer_input.sRGB -> preserve_color.sRGB Image
    _rr_post.links.new(post_layer_input.outputs[1], preserve_color.inputs[1])
    # reroute_003_11.Output -> mix_25.A
    _rr_post.links.new(reroute_003_11.outputs[0], mix_25.inputs[6])
    # reroute_002_11.Output -> mix_25.Factor
    _rr_post.links.new(reroute_002_11.outputs[0], mix_25.inputs[0])
    # post_layer_input.Factor -> reroute_18.Input
    _rr_post.links.new(post_layer_input.outputs[2], reroute_18.inputs[0])
    # reroute_007_6.Output -> vignette_1.Image
    _rr_post.links.new(reroute_007_6.outputs[0], vignette_1.inputs[0])
    # reroute_18.Output -> reroute_002_11.Input
    _rr_post.links.new(reroute_18.outputs[0], reroute_002_11.inputs[0])
    # post_layer_input.Image -> reroute_003_11.Input
    _rr_post.links.new(post_layer_input.outputs[0], reroute_003_11.inputs[0])
    # clarity.Image -> negative_bleed.Color
    _rr_post.links.new(clarity.outputs[0], negative_bleed.inputs[0])
    # negative_bleed.Color -> reroute_004_9.Input
    _rr_post.links.new(negative_bleed.outputs[0], reroute_004_9.inputs[0])
    # lens_distortion_1.Image -> film_grain_accurate.Image
    _rr_post.links.new(lens_distortion_1.outputs[0], film_grain_accurate.inputs[1])
    # reroute_001_13.Output -> film_grain_accurate.Factor
    _rr_post.links.new(reroute_001_13.outputs[0], film_grain_accurate.inputs[0])
    # reroute_009_4.Output -> reroute_001_13.Input
    _rr_post.links.new(reroute_009_4.outputs[0], reroute_001_13.inputs[0])
    # reroute_001_13.Output -> reroute_008_4.Input
    _rr_post.links.new(reroute_001_13.outputs[0], reroute_008_4.inputs[0])
    # color_blending.Image -> split_tone.Image
    _rr_post.links.new(color_blending.outputs[0], split_tone.inputs[0])
    # split_tone.Image -> reroute_006_5.Input
    _rr_post.links.new(split_tone.outputs[0], reroute_006_5.inputs[0])
    # fix_clipping_1.Image -> mix_25.B
    _rr_post.links.new(fix_clipping_1.outputs[0], mix_25.inputs[7])
    # mix_25.Result -> lens_distortion_1.Image
    _rr_post.links.new(mix_25.outputs[2], lens_distortion_1.inputs[1])
    # reroute_002_11.Output -> reroute_009_4.Input
    _rr_post.links.new(reroute_002_11.outputs[0], reroute_009_4.inputs[0])
    # reroute_009_4.Output -> lens_distortion_1.Factor
    _rr_post.links.new(reroute_009_4.outputs[0], lens_distortion_1.inputs[0])
    # reroute_008_4.Output -> film_grain_fast.Factor
    _rr_post.links.new(reroute_008_4.outputs[0], film_grain_fast.inputs[0])
    # film_grain_accurate.Image -> film_grain_fast.Image
    _rr_post.links.new(film_grain_accurate.outputs[0], film_grain_fast.inputs[1])
    # film_grain_fast.Image -> post_layer_output.Image
    _rr_post.links.new(film_grain_fast.outputs[0], post_layer_output.inputs[0])
    # vignette_1.Image -> fix_clipping_1.Image
    _rr_post.links.new(vignette_1.outputs[0], fix_clipping_1.inputs[1])
    # saturation_1.Image -> value_saturation.Image
    _rr_post.links.new(saturation_1.outputs[0], value_saturation.inputs[1])
    # reroute_005_10.Output -> hue_correct_3.Input
    _rr_post.links.new(reroute_005_10.outputs[0], hue_correct_3.inputs[1])
    # hue_correct_3.Image -> density.Image
    _rr_post.links.new(hue_correct_3.outputs[0], density.inputs[0])
    # post_layer_input.sRGB -> hue_correct_3.sRGB
    _rr_post.links.new(post_layer_input.outputs[1], hue_correct_3.inputs[2])

    return _rr_post


_rr_post = _rr_post_node_group()

def _rr_alpha_fix_node_group():
    """Initialize .RR_alpha_fix node group"""
    _rr_alpha_fix = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_alpha_fix")

    _rr_alpha_fix.color_tag = 'NONE'
    _rr_alpha_fix.description = ""
    _rr_alpha_fix.default_group_node_width = 140
    # _rr_alpha_fix interface

    # Socket Image
    image_socket_54 = _rr_alpha_fix.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_54.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_54.attribute_domain = 'POINT'
    image_socket_54.default_input = 'VALUE'
    image_socket_54.structure_type = 'AUTO'

    # Socket Input
    input_socket_3 = _rr_alpha_fix.interface.new_socket(name="Input", in_out='INPUT', socket_type='NodeSocketColor')
    input_socket_3.default_value = (0.0, 0.0, 0.0, 1.0)
    input_socket_3.attribute_domain = 'POINT'
    input_socket_3.default_input = 'VALUE'
    input_socket_3.structure_type = 'AUTO'

    # Socket Method
    method_socket = _rr_alpha_fix.interface.new_socket(name="Method", in_out='INPUT', socket_type='NodeSocketFloat')
    method_socket.default_value = 1.0
    method_socket.min_value = 0.0
    method_socket.max_value = 1.0
    method_socket.subtype = 'FACTOR'
    method_socket.attribute_domain = 'POINT'
    method_socket.default_input = 'VALUE'
    method_socket.structure_type = 'AUTO'

    # Socket Factor
    factor_socket_19 = _rr_alpha_fix.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket_19.default_value = 0.5
    factor_socket_19.min_value = 0.0
    factor_socket_19.max_value = 1.0
    factor_socket_19.subtype = 'FACTOR'
    factor_socket_19.attribute_domain = 'POINT'
    factor_socket_19.default_input = 'VALUE'
    factor_socket_19.structure_type = 'AUTO'

    # Initialize _rr_alpha_fix nodes

    # Node Group Output
    group_output_35 = _rr_alpha_fix.nodes.new("NodeGroupOutput")
    group_output_35.name = "Group Output"
    group_output_35.is_active_output = True

    # Node Group Input
    group_input_31 = _rr_alpha_fix.nodes.new("NodeGroupInput")
    group_input_31.name = "Group Input"

    # Node Alpha Convert
    alpha_convert = _rr_alpha_fix.nodes.new("CompositorNodePremulKey")
    alpha_convert.name = "Alpha Convert"
    alpha_convert.mapping = 'STRAIGHT_TO_PREMUL'

    # Node Mix
    mix_26 = _rr_alpha_fix.nodes.new("ShaderNodeMix")
    mix_26.name = "Mix"
    mix_26.hide = True
    mix_26.blend_type = 'MIX'
    mix_26.clamp_factor = False
    mix_26.clamp_result = False
    mix_26.data_type = 'RGBA'
    mix_26.factor_mode = 'UNIFORM'

    # Node Alpha Convert.001
    alpha_convert_001 = _rr_alpha_fix.nodes.new("CompositorNodePremulKey")
    alpha_convert_001.name = "Alpha Convert.001"
    alpha_convert_001.mapping = 'STRAIGHT_TO_PREMUL'

    # Node Mix.001
    mix_001_16 = _rr_alpha_fix.nodes.new("ShaderNodeMix")
    mix_001_16.name = "Mix.001"
    mix_001_16.hide = True
    mix_001_16.blend_type = 'MIX'
    mix_001_16.clamp_factor = False
    mix_001_16.clamp_result = False
    mix_001_16.data_type = 'RGBA'
    mix_001_16.factor_mode = 'UNIFORM'

    # Node Reroute
    reroute_19 = _rr_alpha_fix.nodes.new("NodeReroute")
    reroute_19.name = "Reroute"
    reroute_19.socket_idname = "NodeSocketColor"
    # Set locations
    group_output_35.location = (460.0, 40.0)
    group_input_31.location = (-500.0, 60.0)
    alpha_convert.location = (-200.0, -180.0)
    mix_26.location = (260.0, 0.0)
    alpha_convert_001.location = (-200.0, -60.0)
    mix_001_16.location = (20.0, -40.0)
    reroute_19.location = (160.0, 40.0)

    # Set dimensions
    group_output_35.width, group_output_35.height = 140.0, 100.0
    group_input_31.width, group_input_31.height = 140.0, 100.0
    alpha_convert.width, alpha_convert.height = 140.0, 100.0
    mix_26.width, mix_26.height = 140.0, 100.0
    alpha_convert_001.width, alpha_convert_001.height = 140.0, 100.0
    mix_001_16.width, mix_001_16.height = 140.0, 100.0
    reroute_19.width, reroute_19.height = 20.0, 100.0

    # Initialize _rr_alpha_fix links

    # group_input_31.Input -> alpha_convert.Image
    _rr_alpha_fix.links.new(group_input_31.outputs[0], alpha_convert.inputs[0])
    # reroute_19.Output -> mix_26.A
    _rr_alpha_fix.links.new(reroute_19.outputs[0], mix_26.inputs[6])
    # mix_26.Result -> group_output_35.Image
    _rr_alpha_fix.links.new(mix_26.outputs[2], group_output_35.inputs[0])
    # group_input_31.Factor -> mix_26.Factor
    _rr_alpha_fix.links.new(group_input_31.outputs[2], mix_26.inputs[0])
    # group_input_31.Input -> alpha_convert_001.Image
    _rr_alpha_fix.links.new(group_input_31.outputs[0], alpha_convert_001.inputs[0])
    # alpha_convert_001.Image -> mix_001_16.A
    _rr_alpha_fix.links.new(alpha_convert_001.outputs[0], mix_001_16.inputs[6])
    # alpha_convert.Image -> mix_001_16.B
    _rr_alpha_fix.links.new(alpha_convert.outputs[0], mix_001_16.inputs[7])
    # mix_001_16.Result -> mix_26.B
    _rr_alpha_fix.links.new(mix_001_16.outputs[2], mix_26.inputs[7])
    # group_input_31.Method -> mix_001_16.Factor
    _rr_alpha_fix.links.new(group_input_31.outputs[1], mix_001_16.inputs[0])
    # group_input_31.Input -> reroute_19.Input
    _rr_alpha_fix.links.new(group_input_31.outputs[0], reroute_19.inputs[0])

    return _rr_alpha_fix


_rr_alpha_fix = _rr_alpha_fix_node_group()

def _rr_clipping_node_group():
    """Initialize .RR_clipping node group"""
    _rr_clipping = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = ".RR_clipping")

    _rr_clipping.color_tag = 'NONE'
    _rr_clipping.description = ""
    _rr_clipping.default_group_node_width = 140
    # _rr_clipping interface

    # Socket Image
    image_socket_55 = _rr_clipping.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_55.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    image_socket_55.attribute_domain = 'POINT'
    image_socket_55.default_input = 'VALUE'
    image_socket_55.structure_type = 'AUTO'

    # Socket Image
    image_socket_56 = _rr_clipping.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_56.default_value = (0.0, 0.0, 0.0, 1.0)
    image_socket_56.attribute_domain = 'POINT'
    image_socket_56.default_input = 'VALUE'
    image_socket_56.structure_type = 'AUTO'

    # Socket Black Overlay
    black_overlay_socket = _rr_clipping.interface.new_socket(name="Black Overlay", in_out='INPUT', socket_type='NodeSocketColor')
    black_overlay_socket.default_value = (0.0, 0.004159970209002495, 1.0, 1.0)
    black_overlay_socket.attribute_domain = 'POINT'
    black_overlay_socket.default_input = 'VALUE'
    black_overlay_socket.structure_type = 'AUTO'

    # Socket Black Threshold
    black_threshold_socket = _rr_clipping.interface.new_socket(name="Black Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    black_threshold_socket.default_value = 9.999999747378752e-05
    black_threshold_socket.min_value = -10000.0
    black_threshold_socket.max_value = 10000.0
    black_threshold_socket.subtype = 'NONE'
    black_threshold_socket.attribute_domain = 'POINT'
    black_threshold_socket.default_input = 'VALUE'
    black_threshold_socket.structure_type = 'AUTO'

    # Socket White Overlay
    white_overlay_socket = _rr_clipping.interface.new_socket(name="White Overlay", in_out='INPUT', socket_type='NodeSocketColor')
    white_overlay_socket.default_value = (1.0, 0.004159970209002495, 0.0, 1.0)
    white_overlay_socket.attribute_domain = 'POINT'
    white_overlay_socket.default_input = 'VALUE'
    white_overlay_socket.structure_type = 'AUTO'

    # Socket White Threshold
    white_threshold_socket = _rr_clipping.interface.new_socket(name="White Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    white_threshold_socket.default_value = 0.9999899864196777
    white_threshold_socket.min_value = -10000.0
    white_threshold_socket.max_value = 10000.0
    white_threshold_socket.subtype = 'NONE'
    white_threshold_socket.attribute_domain = 'POINT'
    white_threshold_socket.default_input = 'VALUE'
    white_threshold_socket.structure_type = 'AUTO'

    # Socket Saturation Overlay
    saturation_overlay_socket = _rr_clipping.interface.new_socket(name="Saturation Overlay", in_out='INPUT', socket_type='NodeSocketColor')
    saturation_overlay_socket.default_value = (1.0, 1.0, 1.0, 0.0)
    saturation_overlay_socket.attribute_domain = 'POINT'
    saturation_overlay_socket.default_input = 'VALUE'
    saturation_overlay_socket.structure_type = 'AUTO'

    # Socket Saturation Threshold
    saturation_threshold_socket = _rr_clipping.interface.new_socket(name="Saturation Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_threshold_socket.default_value = 0.9999899864196777
    saturation_threshold_socket.min_value = -10000.0
    saturation_threshold_socket.max_value = 10000.0
    saturation_threshold_socket.subtype = 'NONE'
    saturation_threshold_socket.attribute_domain = 'POINT'
    saturation_threshold_socket.default_input = 'VALUE'
    saturation_threshold_socket.structure_type = 'AUTO'

    # Socket Saturation Multiply
    saturation_multiply_socket = _rr_clipping.interface.new_socket(name="Saturation Multiply", in_out='INPUT', socket_type='NodeSocketFloat')
    saturation_multiply_socket.default_value = 0.25
    saturation_multiply_socket.min_value = -10000.0
    saturation_multiply_socket.max_value = 10000.0
    saturation_multiply_socket.subtype = 'NONE'
    saturation_multiply_socket.attribute_domain = 'POINT'
    saturation_multiply_socket.default_input = 'VALUE'
    saturation_multiply_socket.structure_type = 'AUTO'

    # Initialize _rr_clipping nodes

    # Node Group Output
    group_output_36 = _rr_clipping.nodes.new("NodeGroupOutput")
    group_output_36.name = "Group Output"
    group_output_36.is_active_output = True

    # Node Group Input
    group_input_32 = _rr_clipping.nodes.new("NodeGroupInput")
    group_input_32.name = "Group Input"
    group_input_32.outputs[1].hide = True
    group_input_32.outputs[2].hide = True
    group_input_32.outputs[3].hide = True
    group_input_32.outputs[4].hide = True
    group_input_32.outputs[5].hide = True
    group_input_32.outputs[6].hide = True
    group_input_32.outputs[8].hide = True

    # Node Mix
    mix_27 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_27.name = "Mix"
    mix_27.blend_type = 'MIX'
    mix_27.clamp_factor = False
    mix_27.clamp_result = False
    mix_27.data_type = 'RGBA'
    mix_27.factor_mode = 'UNIFORM'

    # Node Math
    math_28 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_28.name = "Math"
    math_28.hide = True
    math_28.operation = 'LESS_THAN'
    math_28.use_clamp = False

    # Node Mix.001
    mix_001_17 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_001_17.name = "Mix.001"
    mix_001_17.blend_type = 'MIX'
    mix_001_17.clamp_factor = False
    mix_001_17.clamp_result = False
    mix_001_17.data_type = 'RGBA'
    mix_001_17.factor_mode = 'UNIFORM'

    # Node Math.001
    math_001_22 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_001_22.name = "Math.001"
    math_001_22.hide = True
    math_001_22.operation = 'GREATER_THAN'
    math_001_22.use_clamp = False

    # Node Math.002
    math_002_21 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_002_21.name = "Math.002"
    math_002_21.hide = True
    math_002_21.operation = 'MULTIPLY'
    math_002_21.use_clamp = False

    # Node Math.003
    math_003_20 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_003_20.name = "Math.003"
    math_003_20.hide = True
    math_003_20.operation = 'MULTIPLY'
    math_003_20.use_clamp = False

    # Node Mix.002
    mix_002_7 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_002_7.name = "Mix.002"
    mix_002_7.blend_type = 'MIX'
    mix_002_7.clamp_factor = False
    mix_002_7.clamp_result = False
    mix_002_7.data_type = 'RGBA'
    mix_002_7.factor_mode = 'UNIFORM'

    # Node Math.004
    math_004_19 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_004_19.name = "Math.004"
    math_004_19.hide = True
    math_004_19.operation = 'GREATER_THAN'
    math_004_19.use_clamp = False

    # Node Math.005
    math_005_17 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_005_17.name = "Math.005"
    math_005_17.hide = True
    math_005_17.operation = 'MULTIPLY'
    math_005_17.use_clamp = False

    # Node Reroute.002
    reroute_002_12 = _rr_clipping.nodes.new("NodeReroute")
    reroute_002_12.name = "Reroute.002"
    reroute_002_12.socket_idname = "NodeSocketFloat"
    # Node Value.003
    value_003 = _rr_clipping.nodes.new("ShaderNodeValue")
    value_003.name = "Value.003"

    value_003.outputs[0].default_value = 25.0
    # Node Mix.003
    mix_003_4 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_003_4.name = "Mix.003"
    mix_003_4.blend_type = 'MULTIPLY'
    mix_003_4.clamp_factor = False
    mix_003_4.clamp_result = False
    mix_003_4.data_type = 'RGBA'
    mix_003_4.factor_mode = 'UNIFORM'
    # B_Color
    mix_003_4.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)

    # Node Mix.004
    mix_004_3 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_004_3.name = "Mix.004"
    mix_004_3.blend_type = 'MULTIPLY'
    mix_004_3.clamp_factor = False
    mix_004_3.clamp_result = False
    mix_004_3.data_type = 'RGBA'
    mix_004_3.factor_mode = 'UNIFORM'
    # B_Color
    mix_004_3.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)

    # Node Mix.005
    mix_005_3 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_005_3.name = "Mix.005"
    mix_005_3.blend_type = 'MULTIPLY'
    mix_005_3.clamp_factor = False
    mix_005_3.clamp_result = False
    mix_005_3.data_type = 'RGBA'
    mix_005_3.factor_mode = 'UNIFORM'
    # B_Color
    mix_005_3.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)

    # Node Reroute.004
    reroute_004_10 = _rr_clipping.nodes.new("NodeReroute")
    reroute_004_10.name = "Reroute.004"
    reroute_004_10.socket_idname = "NodeSocketFloat"
    # Node Map Range
    map_range_19 = _rr_clipping.nodes.new("ShaderNodeMapRange")
    map_range_19.name = "Map Range"
    map_range_19.clamp = True
    map_range_19.data_type = 'FLOAT'
    map_range_19.interpolation_type = 'LINEAR'
    # From Min
    map_range_19.inputs[1].default_value = 0.5
    # From Max
    map_range_19.inputs[2].default_value = 1.0
    # To Min
    map_range_19.inputs[3].default_value = 0.0
    # To Max
    map_range_19.inputs[4].default_value = 1.0

    # Node Separate Color.002
    separate_color_002_7 = _rr_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_002_7.name = "Separate Color.002"
    separate_color_002_7.mode = 'HSL'
    separate_color_002_7.ycc_mode = 'ITUBT709'
    separate_color_002_7.outputs[0].hide = True
    separate_color_002_7.outputs[2].hide = True

    # Node Separate Color.003
    separate_color_003_6 = _rr_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_003_6.name = "Separate Color.003"
    separate_color_003_6.mode = 'HSV'
    separate_color_003_6.ycc_mode = 'ITUBT709'
    separate_color_003_6.outputs[0].hide = True
    separate_color_003_6.outputs[1].hide = True
    separate_color_003_6.outputs[3].hide = True

    # Node Reroute.005
    reroute_005_11 = _rr_clipping.nodes.new("NodeReroute")
    reroute_005_11.name = "Reroute.005"
    reroute_005_11.socket_idname = "NodeSocketFloat"
    # Node Reroute.003
    reroute_003_12 = _rr_clipping.nodes.new("NodeReroute")
    reroute_003_12.name = "Reroute.003"
    reroute_003_12.socket_idname = "NodeSocketFloat"
    # Node Reroute.007
    reroute_007_7 = _rr_clipping.nodes.new("NodeReroute")
    reroute_007_7.name = "Reroute.007"
    reroute_007_7.socket_idname = "NodeSocketFloat"
    # Node Math.006
    math_006_13 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_006_13.name = "Math.006"
    math_006_13.hide = True
    math_006_13.operation = 'MULTIPLY'
    math_006_13.use_clamp = False

    # Node Map Range.001
    map_range_001_19 = _rr_clipping.nodes.new("ShaderNodeMapRange")
    map_range_001_19.name = "Map Range.001"
    map_range_001_19.clamp = True
    map_range_001_19.data_type = 'FLOAT'
    map_range_001_19.interpolation_type = 'LINEAR'
    # From Min
    map_range_001_19.inputs[1].default_value = 0.0
    # From Max
    map_range_001_19.inputs[2].default_value = 0.5
    # To Min
    map_range_001_19.inputs[3].default_value = 1.0
    # To Max
    map_range_001_19.inputs[4].default_value = 0.0

    # Node Math.007
    math_007_12 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_007_12.name = "Math.007"
    math_007_12.hide = True
    math_007_12.operation = 'MULTIPLY'
    math_007_12.use_clamp = False

    # Node Mix.006
    mix_006_2 = _rr_clipping.nodes.new("ShaderNodeMix")
    mix_006_2.name = "Mix.006"
    mix_006_2.hide = True
    mix_006_2.blend_type = 'MIX'
    mix_006_2.clamp_factor = False
    mix_006_2.clamp_result = False
    mix_006_2.data_type = 'RGBA'
    mix_006_2.factor_mode = 'UNIFORM'

    # Node Map Range.002
    map_range_002_13 = _rr_clipping.nodes.new("ShaderNodeMapRange")
    map_range_002_13.name = "Map Range.002"
    map_range_002_13.clamp = True
    map_range_002_13.data_type = 'FLOAT'
    map_range_002_13.interpolation_type = 'LINEAR'
    # From Min
    map_range_002_13.inputs[1].default_value = 0.0
    # To Min
    map_range_002_13.inputs[3].default_value = 0.0
    # To Max
    map_range_002_13.inputs[4].default_value = 1.0

    # Node Math.008
    math_008_11 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_008_11.name = "Math.008"
    math_008_11.hide = True
    math_008_11.operation = 'ADD'
    math_008_11.use_clamp = False

    # Node Group Input.001
    group_input_001_13 = _rr_clipping.nodes.new("NodeGroupInput")
    group_input_001_13.name = "Group Input.001"
    group_input_001_13.outputs[0].hide = True
    group_input_001_13.outputs[1].hide = True
    group_input_001_13.outputs[2].hide = True
    group_input_001_13.outputs[3].hide = True
    group_input_001_13.outputs[4].hide = True
    group_input_001_13.outputs[5].hide = True
    group_input_001_13.outputs[7].hide = True
    group_input_001_13.outputs[8].hide = True

    # Node Reroute
    reroute_20 = _rr_clipping.nodes.new("NodeReroute")
    reroute_20.name = "Reroute"
    reroute_20.socket_idname = "NodeSocketFloat"
    # Node Frame
    frame_17 = _rr_clipping.nodes.new("NodeFrame")
    frame_17.label = "Saturation"
    frame_17.name = "Frame"
    frame_17.label_size = 20
    frame_17.shrink = True

    # Node Reroute.008
    reroute_008_5 = _rr_clipping.nodes.new("NodeReroute")
    reroute_008_5.name = "Reroute.008"
    reroute_008_5.socket_idname = "NodeSocketFloat"
    # Node Reroute.009
    reroute_009_5 = _rr_clipping.nodes.new("NodeReroute")
    reroute_009_5.name = "Reroute.009"
    reroute_009_5.socket_idname = "NodeSocketFloat"
    # Node Reroute.010
    reroute_010_4 = _rr_clipping.nodes.new("NodeReroute")
    reroute_010_4.name = "Reroute.010"
    reroute_010_4.socket_idname = "NodeSocketFloat"
    # Node Reroute.011
    reroute_011_4 = _rr_clipping.nodes.new("NodeReroute")
    reroute_011_4.name = "Reroute.011"
    reroute_011_4.socket_idname = "NodeSocketFloat"
    # Node Reroute.012
    reroute_012_4 = _rr_clipping.nodes.new("NodeReroute")
    reroute_012_4.name = "Reroute.012"
    reroute_012_4.socket_idname = "NodeSocketFloat"
    # Node Group Input.002
    group_input_002_7 = _rr_clipping.nodes.new("NodeGroupInput")
    group_input_002_7.name = "Group Input.002"
    group_input_002_7.outputs[0].hide = True
    group_input_002_7.outputs[1].hide = True
    group_input_002_7.outputs[2].hide = True
    group_input_002_7.outputs[5].hide = True
    group_input_002_7.outputs[6].hide = True
    group_input_002_7.outputs[7].hide = True
    group_input_002_7.outputs[8].hide = True

    # Node Reroute.013
    reroute_013_3 = _rr_clipping.nodes.new("NodeReroute")
    reroute_013_3.name = "Reroute.013"
    reroute_013_3.socket_idname = "NodeSocketFloat"
    # Node Group Input.003
    group_input_003_6 = _rr_clipping.nodes.new("NodeGroupInput")
    group_input_003_6.name = "Group Input.003"
    group_input_003_6.outputs[0].hide = True
    group_input_003_6.outputs[1].hide = True
    group_input_003_6.outputs[2].hide = True
    group_input_003_6.outputs[3].hide = True
    group_input_003_6.outputs[4].hide = True
    group_input_003_6.outputs[6].hide = True
    group_input_003_6.outputs[7].hide = True
    group_input_003_6.outputs[8].hide = True

    # Node Reroute.014
    reroute_014_2 = _rr_clipping.nodes.new("NodeReroute")
    reroute_014_2.name = "Reroute.014"
    reroute_014_2.socket_idname = "NodeSocketFloat"
    # Node Reroute.006
    reroute_006_6 = _rr_clipping.nodes.new("NodeReroute")
    reroute_006_6.name = "Reroute.006"
    reroute_006_6.socket_idname = "NodeSocketFloat"
    # Node Group Input.004
    group_input_004_7 = _rr_clipping.nodes.new("NodeGroupInput")
    group_input_004_7.name = "Group Input.004"
    group_input_004_7.outputs[3].hide = True
    group_input_004_7.outputs[4].hide = True
    group_input_004_7.outputs[5].hide = True
    group_input_004_7.outputs[6].hide = True
    group_input_004_7.outputs[7].hide = True
    group_input_004_7.outputs[8].hide = True

    # Node Reroute.001
    reroute_001_14 = _rr_clipping.nodes.new("NodeReroute")
    reroute_001_14.name = "Reroute.001"
    reroute_001_14.socket_idname = "NodeSocketFloat"
    # Node Math.009
    math_009_9 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_009_9.name = "Math.009"
    math_009_9.hide = True
    math_009_9.operation = 'MULTIPLY'
    math_009_9.use_clamp = False

    # Node Separate Color
    separate_color_11 = _rr_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_11.name = "Separate Color"
    separate_color_11.hide = True
    separate_color_11.mode = 'RGB'
    separate_color_11.ycc_mode = 'ITUBT709'

    # Node Math.010
    math_010_7 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_010_7.name = "Math.010"
    math_010_7.hide = True
    math_010_7.operation = 'MULTIPLY'
    math_010_7.use_clamp = False

    # Node Separate Color.001
    separate_color_001_9 = _rr_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_001_9.name = "Separate Color.001"
    separate_color_001_9.hide = True
    separate_color_001_9.mode = 'RGB'
    separate_color_001_9.ycc_mode = 'ITUBT709'

    # Node Math.011
    math_011_7 = _rr_clipping.nodes.new("ShaderNodeMath")
    math_011_7.name = "Math.011"
    math_011_7.hide = True
    math_011_7.operation = 'MULTIPLY'
    math_011_7.use_clamp = False

    # Node Separate Color.004
    separate_color_004_4 = _rr_clipping.nodes.new("CompositorNodeSeparateColor")
    separate_color_004_4.name = "Separate Color.004"
    separate_color_004_4.hide = True
    separate_color_004_4.mode = 'RGB'
    separate_color_004_4.ycc_mode = 'ITUBT709'

    # Node Wave Texture
    wave_texture = _rr_clipping.nodes.new("ShaderNodeTexWave")
    wave_texture.name = "Wave Texture"
    wave_texture.bands_direction = 'DIAGONAL'
    wave_texture.rings_direction = 'X'
    wave_texture.wave_profile = 'SIN'
    wave_texture.wave_type = 'BANDS'
    # Vector
    wave_texture.inputs[0].default_value = (0.0, 0.0, 0.0)
    # Distortion
    wave_texture.inputs[2].default_value = 0.0
    # Detail
    wave_texture.inputs[3].default_value = 0.0
    # Detail Scale
    wave_texture.inputs[4].default_value = 1.0
    # Detail Roughness
    wave_texture.inputs[5].default_value = 0.5
    # Phase Offset
    wave_texture.inputs[6].default_value = 0.0

    # Node Reroute.015
    reroute_015_2 = _rr_clipping.nodes.new("NodeReroute")
    reroute_015_2.name = "Reroute.015"
    reroute_015_2.socket_idname = "NodeSocketFloat"
    # Node Frame.001
    frame_001_14 = _rr_clipping.nodes.new("NodeFrame")
    frame_001_14.label = "Pattern"
    frame_001_14.name = "Frame.001"
    frame_001_14.label_size = 20
    frame_001_14.shrink = True

    # Node Frame.002
    frame_002_12 = _rr_clipping.nodes.new("NodeFrame")
    frame_002_12.label = "Blacks"
    frame_002_12.name = "Frame.002"
    frame_002_12.label_size = 20
    frame_002_12.shrink = True

    # Node Reroute.016
    reroute_016_2 = _rr_clipping.nodes.new("NodeReroute")
    reroute_016_2.name = "Reroute.016"
    reroute_016_2.socket_idname = "NodeSocketFloat"
    # Node Frame.003
    frame_003_9 = _rr_clipping.nodes.new("NodeFrame")
    frame_003_9.label = "Whites"
    frame_003_9.name = "Frame.003"
    frame_003_9.label_size = 20
    frame_003_9.shrink = True

    # Node Reroute.017
    reroute_017_2 = _rr_clipping.nodes.new("NodeReroute")
    reroute_017_2.name = "Reroute.017"
    reroute_017_2.socket_idname = "NodeSocketColor"
    # Set parents
    mix_27.parent = frame_002_12
    math_28.parent = frame_002_12
    mix_001_17.parent = frame_003_9
    math_001_22.parent = frame_003_9
    math_002_21.parent = frame_002_12
    math_003_20.parent = frame_003_9
    math_004_19.parent = frame_17
    math_005_17.parent = frame_17
    value_003.parent = frame_001_14
    mix_004_3.parent = frame_002_12
    mix_005_3.parent = frame_003_9
    map_range_19.parent = frame_001_14
    reroute_003_12.parent = frame_17
    reroute_007_7.parent = frame_17
    math_007_12.parent = frame_17
    mix_006_2.parent = frame_17
    math_008_11.parent = frame_17
    group_input_001_13.parent = frame_17
    reroute_20.parent = frame_17
    reroute_008_5.parent = frame_17
    reroute_009_5.parent = frame_17
    reroute_010_4.parent = frame_17
    group_input_002_7.parent = frame_003_9
    group_input_004_7.parent = frame_002_12
    math_009_9.parent = frame_002_12
    separate_color_11.parent = frame_002_12
    math_010_7.parent = frame_003_9
    separate_color_001_9.parent = frame_003_9
    wave_texture.parent = frame_001_14
    reroute_016_2.parent = frame_001_14
    reroute_017_2.parent = frame_003_9

    # Set locations
    group_output_36.location = (3567.96337890625, -48.6419677734375)
    group_input_32.location = (-1469.1876220703125, -125.43833923339844)
    mix_27.location = (876.1748046875, -64.85348510742188)
    math_28.location = (275.53973388671875, -66.03388977050781)
    mix_001_17.location = (1026.1531982421875, -35.79212188720703)
    math_001_22.location = (384.6353759765625, -69.37996673583984)
    math_002_21.location = (493.52593994140625, -41.04161071777344)
    math_003_20.location = (635.267578125, -62.38709259033203)
    mix_002_7.location = (3355.260986328125, -21.408540725708008)
    math_004_19.location = (217.812744140625, -102.92811584472656)
    math_005_17.location = (426.484375, -170.26853942871094)
    reroute_002_12.location = (-415.5043640136719, 143.42791748046875)
    value_003.location = (28.8377685546875, -276.4676513671875)
    mix_003_4.location = (2492.0224609375, -251.9801483154297)
    mix_004_3.location = (263.61016845703125, -260.453369140625)
    mix_005_3.location = (391.7008056640625, -226.51568603515625)
    reroute_004_10.location = (-286.22100830078125, -654.9863891601562)
    map_range_19.location = (447.4639892578125, -35.94708251953125)
    separate_color_002_7.location = (-1021.9806518554688, 211.7505645751953)
    separate_color_003_6.location = (-1024.4571533203125, 55.312496185302734)
    reroute_005_11.location = (-410.3529968261719, 19.280038833618164)
    reroute_003_12.location = (34.02001953125, -187.8243865966797)
    reroute_007_7.location = (173.52392578125, -76.38682556152344)
    math_006_13.location = (-556.9832153320312, 198.92703247070312)
    map_range_001_19.location = (2229.185302734375, -274.61865234375)
    math_007_12.location = (636.58544921875, -211.56275939941406)
    mix_006_2.location = (869.4677734375, -174.02073669433594)
    map_range_002_13.location = (-793.8276977539062, -9.352422714233398)
    math_008_11.location = (652.716796875, -41.76551818847656)
    group_input_001_13.location = (34.804443359375, -108.55028533935547)
    reroute_20.location = (37.516845703125, -76.95652770996094)
    frame_17.location = (2026.78271484375, 227.8225555419922)
    reroute_008_5.location = (44.43505859375, -229.33035278320312)
    reroute_009_5.location = (38.482421875, -40.69200134277344)
    reroute_010_4.location = (38.221923828125, -58.80955505371094)
    reroute_011_4.location = (2064.688720703125, -704.2261352539062)
    reroute_012_4.location = (2062.542724609375, -654.9863891601562)
    group_input_002_7.location = (33.31085205078125, -90.58544158935547)
    reroute_013_3.location = (972.8742065429688, -654.9863891601562)
    group_input_003_6.location = (2238.524169921875, -541.6599731445312)
    reroute_014_2.location = (853.4822387695312, 182.87574768066406)
    reroute_006_6.location = (998.23193359375, 120.16681671142578)
    group_input_004_7.location = (29.162750244140625, -198.92306518554688)
    reroute_001_14.location = (878.2142944335938, 5.913060188293457)
    math_009_9.location = (689.5203857421875, -83.21430969238281)
    separate_color_11.location = (486.6629638671875, -104.98908996582031)
    math_010_7.location = (839.2967529296875, -101.4102554321289)
    separate_color_001_9.location = (631.0892333984375, -135.27047729492188)
    math_011_7.location = (3116.88427734375, -39.56313705444336)
    separate_color_004_4.location = (2768.40234375, -123.917724609375)
    wave_texture.location = (234.922607421875, -86.900146484375)
    reroute_015_2.location = (-285.6304016113281, -702.7700805664062)
    frame_001_14.location = (-1173.9600830078125, -677.6880493164062)
    frame_002_12.location = (-407.8800048828125, -100.42800903320312)
    reroute_016_2.location = (631.341796875, -129.12139892578125)
    frame_003_9.location = (693.2740478515625, -117.52800750732422)
    reroute_017_2.location = (34.01995849609375, -199.48892211914062)

    # Set dimensions
    group_output_36.width, group_output_36.height = 140.0, 100.0
    group_input_32.width, group_input_32.height = 140.0, 100.0
    mix_27.width, mix_27.height = 140.0, 100.0
    math_28.width, math_28.height = 160.5870819091797, 100.0
    mix_001_17.width, mix_001_17.height = 140.0, 100.0
    math_001_22.width, math_001_22.height = 151.7386016845703, 100.0
    math_002_21.width, math_002_21.height = 140.0, 100.0
    math_003_20.width, math_003_20.height = 129.2882537841797, 100.0
    mix_002_7.width, mix_002_7.height = 140.0, 100.0
    math_004_19.width, math_004_19.height = 160.5870819091797, 100.0
    math_005_17.width, math_005_17.height = 145.5039825439453, 100.0
    reroute_002_12.width, reroute_002_12.height = 13.5, 100.0
    value_003.width, value_003.height = 140.0, 100.0
    mix_003_4.width, mix_003_4.height = 140.0, 100.0
    mix_004_3.width, mix_004_3.height = 140.0, 100.0
    mix_005_3.width, mix_005_3.height = 140.0, 100.0
    reroute_004_10.width, reroute_004_10.height = 13.5, 100.0
    map_range_19.width, map_range_19.height = 140.0, 100.0
    separate_color_002_7.width, separate_color_002_7.height = 140.0, 100.0
    separate_color_003_6.width, separate_color_003_6.height = 140.0, 100.0
    reroute_005_11.width, reroute_005_11.height = 13.5, 100.0
    reroute_003_12.width, reroute_003_12.height = 13.5, 100.0
    reroute_007_7.width, reroute_007_7.height = 13.5, 100.0
    math_006_13.width, math_006_13.height = 140.0, 100.0
    map_range_001_19.width, map_range_001_19.height = 140.0, 100.0
    math_007_12.width, math_007_12.height = 145.5039825439453, 100.0
    mix_006_2.width, mix_006_2.height = 140.0, 100.0
    map_range_002_13.width, map_range_002_13.height = 140.0, 100.0
    math_008_11.width, math_008_11.height = 140.0, 100.0
    group_input_001_13.width, group_input_001_13.height = 140.0, 100.0
    reroute_20.width, reroute_20.height = 13.5, 100.0
    frame_17.width, frame_17.height = 1038.937255859375, 264.7225646972656
    reroute_008_5.width, reroute_008_5.height = 13.5, 100.0
    reroute_009_5.width, reroute_009_5.height = 13.5, 100.0
    reroute_010_4.width, reroute_010_4.height = 13.5, 100.0
    reroute_011_4.width, reroute_011_4.height = 13.5, 100.0
    reroute_012_4.width, reroute_012_4.height = 13.5, 100.0
    group_input_002_7.width, group_input_002_7.height = 140.0, 100.0
    reroute_013_3.width, reroute_013_3.height = 13.5, 100.0
    group_input_003_6.width, group_input_003_6.height = 140.0, 100.0
    reroute_014_2.width, reroute_014_2.height = 13.5, 100.0
    reroute_006_6.width, reroute_006_6.height = 13.5, 100.0
    group_input_004_7.width, group_input_004_7.height = 140.0, 100.0
    reroute_001_14.width, reroute_001_14.height = 13.5, 100.0
    math_009_9.width, math_009_9.height = 140.0, 100.0
    separate_color_11.width, separate_color_11.height = 140.0, 100.0
    math_010_7.width, math_010_7.height = 140.0, 100.0
    separate_color_001_9.width, separate_color_001_9.height = 140.0, 100.0
    math_011_7.width, math_011_7.height = 140.0, 100.0
    separate_color_004_4.width, separate_color_004_4.height = 140.0, 100.0
    wave_texture.width, wave_texture.height = 150.0, 100.0
    reroute_015_2.width, reroute_015_2.height = 13.5, 100.0
    frame_001_14.width, frame_001_14.height = 665.36181640625, 404.83197021484375
    frame_002_12.width, frame_002_12.height = 1045.0400390625, 500.4120178222656
    reroute_016_2.width, reroute_016_2.height = 13.5, 100.0
    frame_003_9.width, frame_003_9.height = 1195.2459716796875, 466.75201416015625
    reroute_017_2.width, reroute_017_2.height = 13.5, 100.0

    # Initialize _rr_clipping links

    # math_28.Value -> math_002_21.Value
    _rr_clipping.links.new(math_28.outputs[0], math_002_21.inputs[1])
    # math_001_22.Value -> math_003_20.Value
    _rr_clipping.links.new(math_001_22.outputs[0], math_003_20.inputs[1])
    # reroute_001_14.Output -> math_001_22.Value
    _rr_clipping.links.new(reroute_001_14.outputs[0], math_001_22.inputs[0])
    # reroute_017_2.Output -> mix_001_17.A
    _rr_clipping.links.new(reroute_017_2.outputs[0], mix_001_17.inputs[6])
    # reroute_006_6.Output -> math_003_20.Value
    _rr_clipping.links.new(reroute_006_6.outputs[0], math_003_20.inputs[0])
    # reroute_005_11.Output -> math_28.Value
    _rr_clipping.links.new(reroute_005_11.outputs[0], math_28.inputs[0])
    # math_004_19.Value -> math_005_17.Value
    _rr_clipping.links.new(math_004_19.outputs[0], math_005_17.inputs[0])
    # separate_color_002_7.Alpha -> reroute_002_12.Input
    _rr_clipping.links.new(separate_color_002_7.outputs[3], reroute_002_12.inputs[0])
    # mix_003_4.Result -> mix_002_7.B
    _rr_clipping.links.new(mix_003_4.outputs[2], mix_002_7.inputs[7])
    # reroute_004_10.Output -> mix_004_3.Factor
    _rr_clipping.links.new(reroute_004_10.outputs[0], mix_004_3.inputs[0])
    # mix_004_3.Result -> mix_27.B
    _rr_clipping.links.new(mix_004_3.outputs[2], mix_27.inputs[7])
    # reroute_013_3.Output -> mix_005_3.Factor
    _rr_clipping.links.new(reroute_013_3.outputs[0], mix_005_3.inputs[0])
    # mix_005_3.Result -> mix_001_17.B
    _rr_clipping.links.new(mix_005_3.outputs[2], mix_001_17.inputs[7])
    # map_range_19.Result -> reroute_004_10.Input
    _rr_clipping.links.new(map_range_19.outputs[0], reroute_004_10.inputs[0])
    # group_input_32.Image -> separate_color_002_7.Image
    _rr_clipping.links.new(group_input_32.outputs[0], separate_color_002_7.inputs[0])
    # group_input_32.Image -> separate_color_003_6.Image
    _rr_clipping.links.new(group_input_32.outputs[0], separate_color_003_6.inputs[0])
    # separate_color_003_6.Blue -> reroute_005_11.Input
    _rr_clipping.links.new(separate_color_003_6.outputs[2], reroute_005_11.inputs[0])
    # reroute_007_7.Output -> math_004_19.Value
    _rr_clipping.links.new(reroute_007_7.outputs[0], math_004_19.inputs[0])
    # reroute_006_6.Output -> reroute_003_12.Input
    _rr_clipping.links.new(reroute_006_6.outputs[0], reroute_003_12.inputs[0])
    # separate_color_002_7.Green -> math_006_13.Value
    _rr_clipping.links.new(separate_color_002_7.outputs[1], math_006_13.inputs[0])
    # reroute_20.Output -> reroute_007_7.Input
    _rr_clipping.links.new(reroute_20.outputs[0], reroute_007_7.inputs[0])
    # reroute_011_4.Output -> map_range_001_19.Value
    _rr_clipping.links.new(reroute_011_4.outputs[0], map_range_001_19.inputs[0])
    # map_range_001_19.Result -> mix_003_4.Factor
    _rr_clipping.links.new(map_range_001_19.outputs[0], mix_003_4.inputs[0])
    # math_005_17.Value -> math_007_12.Value
    _rr_clipping.links.new(math_005_17.outputs[0], math_007_12.inputs[0])
    # mix_002_7.Result -> group_output_36.Image
    _rr_clipping.links.new(mix_002_7.outputs[2], group_output_36.inputs[0])
    # mix_001_17.Result -> mix_002_7.A
    _rr_clipping.links.new(mix_001_17.outputs[2], mix_002_7.inputs[6])
    # reroute_008_5.Output -> math_007_12.Value
    _rr_clipping.links.new(reroute_008_5.outputs[0], math_007_12.inputs[1])
    # math_005_17.Value -> mix_006_2.A
    _rr_clipping.links.new(math_005_17.outputs[0], mix_006_2.inputs[6])
    # math_007_12.Value -> mix_006_2.B
    _rr_clipping.links.new(math_007_12.outputs[0], mix_006_2.inputs[7])
    # separate_color_003_6.Blue -> map_range_002_13.Value
    _rr_clipping.links.new(separate_color_003_6.outputs[2], map_range_002_13.inputs[0])
    # map_range_002_13.Result -> math_006_13.Value
    _rr_clipping.links.new(map_range_002_13.outputs[0], math_006_13.inputs[1])
    # math_008_11.Value -> mix_006_2.Factor
    _rr_clipping.links.new(math_008_11.outputs[0], mix_006_2.inputs[0])
    # reroute_009_5.Output -> math_008_11.Value
    _rr_clipping.links.new(reroute_009_5.outputs[0], math_008_11.inputs[0])
    # reroute_010_4.Output -> math_008_11.Value
    _rr_clipping.links.new(reroute_010_4.outputs[0], math_008_11.inputs[1])
    # group_input_32.Saturation Multiply -> map_range_002_13.From Max
    _rr_clipping.links.new(group_input_32.outputs[7], map_range_002_13.inputs[2])
    # group_input_001_13.Saturation Threshold -> math_004_19.Value
    _rr_clipping.links.new(group_input_001_13.outputs[6], math_004_19.inputs[1])
    # math_006_13.Value -> reroute_20.Input
    _rr_clipping.links.new(math_006_13.outputs[0], reroute_20.inputs[0])
    # reroute_003_12.Output -> math_005_17.Value
    _rr_clipping.links.new(reroute_003_12.outputs[0], math_005_17.inputs[1])
    # reroute_012_4.Output -> reroute_008_5.Input
    _rr_clipping.links.new(reroute_012_4.outputs[0], reroute_008_5.inputs[0])
    # math_003_20.Value -> reroute_009_5.Input
    _rr_clipping.links.new(math_003_20.outputs[0], reroute_009_5.inputs[0])
    # reroute_014_2.Output -> reroute_010_4.Input
    _rr_clipping.links.new(reroute_014_2.outputs[0], reroute_010_4.inputs[0])
    # reroute_015_2.Output -> reroute_011_4.Input
    _rr_clipping.links.new(reroute_015_2.outputs[0], reroute_011_4.inputs[0])
    # reroute_013_3.Output -> reroute_012_4.Input
    _rr_clipping.links.new(reroute_013_3.outputs[0], reroute_012_4.inputs[0])
    # group_input_002_7.White Threshold -> math_001_22.Value
    _rr_clipping.links.new(group_input_002_7.outputs[4], math_001_22.inputs[1])
    # group_input_002_7.White Overlay -> mix_005_3.A
    _rr_clipping.links.new(group_input_002_7.outputs[3], mix_005_3.inputs[6])
    # reroute_004_10.Output -> reroute_013_3.Input
    _rr_clipping.links.new(reroute_004_10.outputs[0], reroute_013_3.inputs[0])
    # group_input_003_6.Saturation Overlay -> mix_003_4.A
    _rr_clipping.links.new(group_input_003_6.outputs[5], mix_003_4.inputs[6])
    # math_002_21.Value -> reroute_014_2.Input
    _rr_clipping.links.new(math_002_21.outputs[0], reroute_014_2.inputs[0])
    # reroute_002_12.Output -> math_002_21.Value
    _rr_clipping.links.new(reroute_002_12.outputs[0], math_002_21.inputs[0])
    # reroute_002_12.Output -> reroute_006_6.Input
    _rr_clipping.links.new(reroute_002_12.outputs[0], reroute_006_6.inputs[0])
    # group_input_004_7.Image -> mix_27.A
    _rr_clipping.links.new(group_input_004_7.outputs[0], mix_27.inputs[6])
    # group_input_004_7.Black Threshold -> math_28.Value
    _rr_clipping.links.new(group_input_004_7.outputs[2], math_28.inputs[1])
    # group_input_004_7.Black Overlay -> mix_004_3.A
    _rr_clipping.links.new(group_input_004_7.outputs[1], mix_004_3.inputs[6])
    # reroute_005_11.Output -> reroute_001_14.Input
    _rr_clipping.links.new(reroute_005_11.outputs[0], reroute_001_14.inputs[0])
    # math_009_9.Value -> mix_27.Factor
    _rr_clipping.links.new(math_009_9.outputs[0], mix_27.inputs[0])
    # math_002_21.Value -> math_009_9.Value
    _rr_clipping.links.new(math_002_21.outputs[0], math_009_9.inputs[0])
    # mix_004_3.Result -> separate_color_11.Image
    _rr_clipping.links.new(mix_004_3.outputs[2], separate_color_11.inputs[0])
    # separate_color_11.Alpha -> math_009_9.Value
    _rr_clipping.links.new(separate_color_11.outputs[3], math_009_9.inputs[1])
    # math_010_7.Value -> mix_001_17.Factor
    _rr_clipping.links.new(math_010_7.outputs[0], mix_001_17.inputs[0])
    # math_003_20.Value -> math_010_7.Value
    _rr_clipping.links.new(math_003_20.outputs[0], math_010_7.inputs[0])
    # mix_005_3.Result -> separate_color_001_9.Image
    _rr_clipping.links.new(mix_005_3.outputs[2], separate_color_001_9.inputs[0])
    # separate_color_001_9.Alpha -> math_010_7.Value
    _rr_clipping.links.new(separate_color_001_9.outputs[3], math_010_7.inputs[1])
    # math_011_7.Value -> mix_002_7.Factor
    _rr_clipping.links.new(math_011_7.outputs[0], mix_002_7.inputs[0])
    # mix_006_2.Result -> math_011_7.Value
    _rr_clipping.links.new(mix_006_2.outputs[2], math_011_7.inputs[0])
    # mix_003_4.Result -> separate_color_004_4.Image
    _rr_clipping.links.new(mix_003_4.outputs[2], separate_color_004_4.inputs[0])
    # separate_color_004_4.Alpha -> math_011_7.Value
    _rr_clipping.links.new(separate_color_004_4.outputs[3], math_011_7.inputs[1])
    # value_003.Value -> wave_texture.Scale
    _rr_clipping.links.new(value_003.outputs[0], wave_texture.inputs[1])
    # wave_texture.Fac -> map_range_19.Value
    _rr_clipping.links.new(wave_texture.outputs[1], map_range_19.inputs[0])
    # reroute_016_2.Output -> reroute_015_2.Input
    _rr_clipping.links.new(reroute_016_2.outputs[0], reroute_015_2.inputs[0])
    # wave_texture.Fac -> reroute_016_2.Input
    _rr_clipping.links.new(wave_texture.outputs[1], reroute_016_2.inputs[0])
    # mix_27.Result -> reroute_017_2.Input
    _rr_clipping.links.new(mix_27.outputs[2], reroute_017_2.inputs[0])

    return _rr_clipping


_rr_clipping = _rr_clipping_node_group()

def render_raw_001_node_group():
    """Initialize Render Raw.001 node group"""
    render_raw_001 = bpy.data.node_groups.new(type = 'CompositorNodeTree', name = "Render Raw.001")

    render_raw_001.color_tag = 'NONE'
    render_raw_001.description = ""
    render_raw_001.default_group_node_width = 140
    # render_raw_001 interface

    # Socket Image
    image_socket_57 = render_raw_001.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    image_socket_57.default_value = (0.0, 0.0, 0.0, 0.0)
    image_socket_57.attribute_domain = 'POINT'
    image_socket_57.default_input = 'VALUE'
    image_socket_57.structure_type = 'AUTO'

    # Socket Glare
    glare_socket_3 = render_raw_001.interface.new_socket(name="Glare", in_out='OUTPUT', socket_type='NodeSocketColor')
    glare_socket_3.default_value = (0.0, 0.0, 0.0, 1.0)
    glare_socket_3.attribute_domain = 'POINT'
    glare_socket_3.default_input = 'VALUE'
    glare_socket_3.structure_type = 'AUTO'

    # Socket Image
    image_socket_58 = render_raw_001.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
    image_socket_58.default_value = (1.0, 1.0, 1.0, 1.0)
    image_socket_58.attribute_domain = 'POINT'
    image_socket_58.default_input = 'VALUE'
    image_socket_58.structure_type = 'AUTO'

    # Socket Sidebar / Node / Properties
    sidebar___node___properties_socket = render_raw_001.interface.new_socket(name="Sidebar / Node / Properties", in_out='INPUT', socket_type='NodeSocketFloat')
    sidebar___node___properties_socket.default_value = 0.0
    sidebar___node___properties_socket.min_value = -3.4028234663852886e+38
    sidebar___node___properties_socket.max_value = 3.4028234663852886e+38
    sidebar___node___properties_socket.subtype = 'NONE'
    sidebar___node___properties_socket.attribute_domain = 'POINT'
    sidebar___node___properties_socket.hide_value = True
    sidebar___node___properties_socket.default_input = 'VALUE'
    sidebar___node___properties_socket.structure_type = 'AUTO'

    # Initialize render_raw_001 nodes

    # Node Frame.005
    frame_005_3 = render_raw_001.nodes.new("NodeFrame")
    frame_005_3.label = "Color Transform"
    frame_005_3.name = "Frame.005"
    frame_005_3.use_custom_color = True
    frame_005_3.color = (0.0, 0.6066304445266724, 0.18137890100479126)
    frame_005_3.label_size = 20
    frame_005_3.shrink = True

    # Node Version
    version = render_raw_001.nodes.new("NodeFrame")
    version.label = "(1, 2, 19)"
    version.name = "Version"
    version.label_size = 20
    version.shrink = True

    # Node Convert Colorspace
    convert_colorspace_3 = render_raw_001.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace_3.name = "Convert Colorspace"
    convert_colorspace_3.use_custom_color = True
    convert_colorspace_3.color = (0.043683141469955444, 0.2698829770088196, 0.11681622266769409)
    convert_colorspace_3.hide = True
    convert_colorspace_3.from_color_space = 'Linear Rec.709'
    convert_colorspace_3.to_color_space = 'sRGB'

    # Node Render Raw Output
    render_raw_output = render_raw_001.nodes.new("NodeGroupOutput")
    render_raw_output.label = "Render Raw Output"
    render_raw_output.name = "Render Raw Output"
    render_raw_output.hide = True
    render_raw_output.is_active_output = True
    render_raw_output.inputs[2].hide = True

    # Node Render Raw Input
    render_raw_input = render_raw_001.nodes.new("NodeGroupInput")
    render_raw_input.label = "Render Raw Input"
    render_raw_input.name = "Render Raw Input"
    render_raw_input.hide = True
    render_raw_input.outputs[1].hide = True
    render_raw_input.outputs[2].hide = True

    # Node Blender Version
    blender_version = render_raw_001.nodes.new("NodeFrame")
    blender_version.label = "(4, 5, 4)"
    blender_version.name = "Blender Version"
    blender_version.label_size = 20
    blender_version.shrink = True

    # Node Layer Pre
    layer_pre = render_raw_001.nodes.new("CompositorNodeGroup")
    layer_pre.label = "New Layer"
    layer_pre.name = "Layer Pre"
    layer_pre.use_custom_color = True
    layer_pre.color = (0.4260903298854828, 0.13837237656116486, 0.6079999804496765)
    layer_pre.hide = True
    layer_pre.node_tree = _rr_pre
    layer_pre.inputs[1].hide = True
    # Socket_2
    layer_pre.inputs[1].default_value = 1.0

    # Node Layer Post
    layer_post = render_raw_001.nodes.new("CompositorNodeGroup")
    layer_post.label = "New Layer"
    layer_post.name = "Layer Post"
    layer_post.use_custom_color = True
    layer_post.color = (0.42610031366348267, 0.13837093114852905, 0.6080166697502136)
    layer_post.hide = True
    layer_post.node_tree = _rr_post
    layer_post.inputs[2].hide = True
    # Socket_2
    layer_post.inputs[2].default_value = 1.0

    # Node Exposure
    exposure_1 = render_raw_001.nodes.new("CompositorNodeExposure")
    exposure_1.name = "Exposure"
    exposure_1.use_custom_color = True
    exposure_1.color = (0.0, 0.0, 0.0)
    exposure_1.mute = True
    exposure_1.hide = True
    exposure_1.inputs[1].hide = True
    # Exposure
    exposure_1.inputs[1].default_value = 0.0

    # Node Gamma
    gamma_2 = render_raw_001.nodes.new("CompositorNodeGamma")
    gamma_2.name = "Gamma"
    gamma_2.use_custom_color = True
    gamma_2.color = (0.0, 0.0, 0.0)
    gamma_2.mute = True
    gamma_2.hide = True
    gamma_2.inputs[1].hide = True
    # Gamma
    gamma_2.inputs[1].default_value = 1.0

    # Node Pre Layer Input
    pre_layer_input_1 = render_raw_001.nodes.new("NodeReroute")
    pre_layer_input_1.name = "Pre Layer Input"
    pre_layer_input_1.socket_idname = "NodeSocketColor"
    # Node Pre Layer Output
    pre_layer_output_1 = render_raw_001.nodes.new("NodeReroute")
    pre_layer_output_1.name = "Pre Layer Output"
    pre_layer_output_1.socket_idname = "NodeSocketColor"
    # Node Post Layer Input
    post_layer_input_1 = render_raw_001.nodes.new("NodeReroute")
    post_layer_input_1.name = "Post Layer Input"
    post_layer_input_1.socket_idname = "NodeSocketColor"
    # Node Manage Alpha
    manage_alpha = render_raw_001.nodes.new("CompositorNodeGroup")
    manage_alpha.label = "Manage Alpha"
    manage_alpha.name = "Manage Alpha"
    manage_alpha.use_custom_color = True
    manage_alpha.color = (0.0, 0.0, 0.0)
    manage_alpha.hide = True
    manage_alpha.node_tree = _rr_alpha_fix
    manage_alpha.inputs[1].hide = True
    manage_alpha.inputs[2].hide = True
    # Socket_3
    manage_alpha.inputs[1].default_value = 1.0
    # Socket_2
    manage_alpha.inputs[2].default_value = 0.5

    # Node Clipping
    clipping = render_raw_001.nodes.new("CompositorNodeGroup")
    clipping.label = "Clipping"
    clipping.name = "Clipping"
    clipping.use_custom_color = True
    clipping.color = (0.0, 0.0, 0.0)
    clipping.mute = True
    clipping.hide = True
    clipping.node_tree = _rr_clipping
    clipping.inputs[1].hide = True
    clipping.inputs[2].hide = True
    clipping.inputs[3].hide = True
    clipping.inputs[4].hide = True
    clipping.inputs[5].hide = True
    clipping.inputs[6].hide = True
    clipping.inputs[7].hide = True
    # Socket_2
    clipping.inputs[1].default_value = (0.0, 0.004159970209002495, 1.0, 1.0)
    # Socket_7
    clipping.inputs[2].default_value = 9.999999747378752e-05
    # Socket_5
    clipping.inputs[3].default_value = (1.0, 0.004159970209002495, 0.0, 1.0)
    # Socket_8
    clipping.inputs[4].default_value = 0.9999899864196777
    # Socket_6
    clipping.inputs[5].default_value = (1.0, 1.0, 1.0, 1.0)
    # Socket_9
    clipping.inputs[6].default_value = 0.9999899864196777
    # Socket_10
    clipping.inputs[7].default_value = 0.25

    # Node Post Layer Output
    post_layer_output_1 = render_raw_001.nodes.new("NodeReroute")
    post_layer_output_1.name = "Post Layer Output"
    post_layer_output_1.socket_idname = "NodeSocketColor"
    # Node Convert Colorspace Glare
    convert_colorspace_glare = render_raw_001.nodes.new("CompositorNodeConvertColorSpace")
    convert_colorspace_glare.name = "Convert Colorspace Glare"
    convert_colorspace_glare.use_custom_color = True
    convert_colorspace_glare.color = (0.043683141469955444, 0.2698829770088196, 0.11681622266769409)
    convert_colorspace_glare.hide = True
    convert_colorspace_glare.from_color_space = 'Linear Rec.709'
    convert_colorspace_glare.to_color_space = 'sRGB'

    # Node sRGB Conversion
    srgb_conversion = render_raw_001.nodes.new("CompositorNodeConvertColorSpace")
    srgb_conversion.label = "sRGB"
    srgb_conversion.name = "sRGB Conversion"
    srgb_conversion.use_custom_color = True
    srgb_conversion.color = (0.043683141469955444, 0.2698829770088196, 0.11681622266769409)
    srgb_conversion.hide = True
    srgb_conversion.from_color_space = 'Linear Rec.709'
    srgb_conversion.to_color_space = 'sRGB'

    # Node sRGB
    srgb = render_raw_001.nodes.new("NodeReroute")
    srgb.name = "sRGB"
    srgb.socket_idname = "NodeSocketColor"
    # Node Inverse Transform
    inverse_transform = render_raw_001.nodes.new("CompositorNodeConvertColorSpace")
    inverse_transform.label = "Inverse Transform"
    inverse_transform.name = "Inverse Transform"
    inverse_transform.hide = True
    inverse_transform.from_color_space = 'sRGB'
    inverse_transform.to_color_space = 'Linear Rec.709'

    # Node Inverse Transform.001
    inverse_transform_001 = render_raw_001.nodes.new("CompositorNodeConvertColorSpace")
    inverse_transform_001.label = "Inverse Transform"
    inverse_transform_001.name = "Inverse Transform.001"
    inverse_transform_001.hide = True
    inverse_transform_001.from_color_space = 'sRGB'
    inverse_transform_001.to_color_space = 'Linear Rec.709'

    # Set parents
    convert_colorspace_3.parent = frame_005_3
    render_raw_output.parent = blender_version
    render_raw_input.parent = version
    convert_colorspace_glare.parent = frame_005_3
    srgb_conversion.parent = frame_005_3
    srgb.parent = frame_005_3

    # Set locations
    frame_005_3.location = (530.0, 124.0)
    version.location = (-280.5, 41.0)
    convert_colorspace_3.location = (30.0, -115.33948516845703)
    render_raw_output.location = (29.934326171875, -41.012855529785156)
    render_raw_input.location = (29.829421997070312, -41.0)
    blender_version.location = (2155.5, 42.0)
    layer_pre.location = (275.0, 0.0)
    layer_post.location = (1075.0, 0.0)
    exposure_1.location = (-30.67058753967285, 0.0)
    gamma_2.location = (1352.0096435546875, 8.979880332946777)
    pre_layer_input_1.location = (182.60592651367188, -10.0)
    pre_layer_output_1.location = (502.17596435546875, -2.456186294555664)
    post_layer_input_1.location = (886.57568359375, -1.339483618736267)
    manage_alpha.location = (1718.8814697265625, 8.979880332946777)
    clipping.location = (1538.88134765625, 8.979880332946777)
    post_layer_output_1.location = (1313.7076416015625, -1.339483618736267)
    convert_colorspace_glare.location = (30.0, -195.3394775390625)
    srgb_conversion.location = (30.0, -41.05445098876953)
    srgb.location = (282.8245849609375, -50.38792419433594)
    inverse_transform.location = (1901.030029296875, 8.979880332946777)
    inverse_transform_001.location = (1897.696533203125, -69.40071105957031)

    # Set dimensions
    frame_005_3.width, frame_005_3.height = 317.8245849609375, 250.5
    version.width, version.height = 211.06954956054688, 96.0
    convert_colorspace_3.width, convert_colorspace_3.height = 217.5537567138672, 100.0
    render_raw_output.width, render_raw_output.height = 162.2763671875, 100.0
    render_raw_input.width, render_raw_input.height = 151.06954956054688, 100.0
    blender_version.width, blender_version.height = 222.2763671875, 96.0
    layer_pre.width, layer_pre.height = 140.0, 100.0
    layer_post.width, layer_post.height = 140.0, 100.0
    exposure_1.width, exposure_1.height = 140.0, 100.0
    gamma_2.width, gamma_2.height = 140.0, 100.0
    pre_layer_input_1.width, pre_layer_input_1.height = 20.0, 100.0
    pre_layer_output_1.width, pre_layer_output_1.height = 20.0, 100.0
    post_layer_input_1.width, post_layer_input_1.height = 20.0, 100.0
    manage_alpha.width, manage_alpha.height = 140.0, 100.0
    clipping.width, clipping.height = 141.8230743408203, 100.0
    post_layer_output_1.width, post_layer_output_1.height = 20.0, 100.0
    convert_colorspace_glare.width, convert_colorspace_glare.height = 217.5537567138672, 100.0
    srgb_conversion.width, srgb_conversion.height = 217.5537567138672, 100.0
    srgb.width, srgb.height = 20.0, 100.0
    inverse_transform.width, inverse_transform.height = 196.85800170898438, 100.0
    inverse_transform_001.width, inverse_transform_001.height = 196.85800170898438, 100.0

    # Initialize render_raw_001 links

    # post_layer_input_1.Output -> layer_post.Image
    render_raw_001.links.new(post_layer_input_1.outputs[0], layer_post.inputs[0])
    # render_raw_input.Image -> exposure_1.Image
    render_raw_001.links.new(render_raw_input.outputs[0], exposure_1.inputs[0])
    # pre_layer_input_1.Output -> layer_pre.Image
    render_raw_001.links.new(pre_layer_input_1.outputs[0], layer_pre.inputs[0])
    # layer_pre.Image -> pre_layer_output_1.Input
    render_raw_001.links.new(layer_pre.outputs[0], pre_layer_output_1.inputs[0])
    # clipping.Image -> manage_alpha.Input
    render_raw_001.links.new(clipping.outputs[0], manage_alpha.inputs[0])
    # gamma_2.Image -> clipping.Image
    render_raw_001.links.new(gamma_2.outputs[0], clipping.inputs[0])
    # layer_post.Image -> post_layer_output_1.Input
    render_raw_001.links.new(layer_post.outputs[0], post_layer_output_1.inputs[0])
    # inverse_transform_001.Image -> render_raw_output.Glare
    render_raw_001.links.new(inverse_transform_001.outputs[0], render_raw_output.inputs[1])
    # pre_layer_output_1.Output -> convert_colorspace_3.Image
    render_raw_001.links.new(pre_layer_output_1.outputs[0], convert_colorspace_3.inputs[0])
    # convert_colorspace_3.Image -> post_layer_input_1.Input
    render_raw_001.links.new(convert_colorspace_3.outputs[0], post_layer_input_1.inputs[0])
    # srgb.Output -> layer_post.sRGB
    render_raw_001.links.new(srgb.outputs[0], layer_post.inputs[1])
    # pre_layer_output_1.Output -> srgb_conversion.Image
    render_raw_001.links.new(pre_layer_output_1.outputs[0], srgb_conversion.inputs[0])
    # srgb_conversion.Image -> srgb.Input
    render_raw_001.links.new(srgb_conversion.outputs[0], srgb.inputs[0])
    # exposure_1.Image -> pre_layer_input_1.Input
    render_raw_001.links.new(exposure_1.outputs[0], pre_layer_input_1.inputs[0])
    # post_layer_output_1.Output -> gamma_2.Image
    render_raw_001.links.new(post_layer_output_1.outputs[0], gamma_2.inputs[0])
    # manage_alpha.Image -> inverse_transform.Image
    render_raw_001.links.new(manage_alpha.outputs[0], inverse_transform.inputs[0])
    # inverse_transform.Image -> render_raw_output.Image
    render_raw_001.links.new(inverse_transform.outputs[0], render_raw_output.inputs[0])
    # convert_colorspace_glare.Image -> inverse_transform_001.Image
    render_raw_001.links.new(convert_colorspace_glare.outputs[0], inverse_transform_001.inputs[0])
    # layer_pre.Glare -> convert_colorspace_glare.Image
    render_raw_001.links.new(layer_pre.outputs[1], convert_colorspace_glare.inputs[0])

    return render_raw_001


render_raw_001 = render_raw_001_node_group()

def scene_1_node_group():
    """Initialize Scene node group"""
    scene_1 = scene.node_tree

    # Start with a clean node tree
    for node in scene_1.nodes:
        scene_1.nodes.remove(node)
    scene_1.color_tag = 'NONE'
    scene_1.description = ""
    scene_1.default_group_node_width = 140
    # scene_1 interface

    # Initialize scene_1 nodes

    # Node Render Layers
    render_layers = scene_1.nodes.new("CompositorNodeRLayers")
    render_layers.name = "Render Layers"
    render_layers.layer = 'ViewLayer'

    # Node Viewer
    viewer = scene_1.nodes.new("CompositorNodeViewer")
    viewer.name = "Viewer"
    viewer.ui_shortcut = 0

    # Node Composite
    composite = scene_1.nodes.new("CompositorNodeComposite")
    composite.name = "Composite"

    # Node Render Raw
    render_raw = scene_1.nodes.new("CompositorNodeGroup")
    render_raw.label = "Render Raw"
    render_raw.name = "Render Raw"
    render_raw.node_tree = render_raw_001
    # Socket_3
    render_raw.inputs[1].default_value = 0.0

    # Set locations
    render_layers.location = (769.658203125, 562.46630859375)
    viewer.location = (1525.0870361328125, 382.16632080078125)
    composite.location = (1525.0870361328125, 506.76629638671875)
    render_raw.location = (1084.658203125, 562.46630859375)

    # Set dimensions
    render_layers.width, render_layers.height = 240.0, 100.0
    viewer.width, viewer.height = 140.0, 100.0
    composite.width, composite.height = 140.0, 100.0
    render_raw.width, render_raw.height = 175.0, 100.0

    # Initialize scene_1 links

    # render_raw.Image -> composite.Image
    scene_1.links.new(render_raw.outputs[0], composite.inputs[0])
    # render_layers.Image -> render_raw.Image
    scene_1.links.new(render_layers.outputs[0], render_raw.inputs[0])
    # render_raw.Image -> viewer.Image
    scene_1.links.new(render_raw.outputs[0], viewer.inputs[0])

    return scene_1


scene_1 = scene_1_node_group()

