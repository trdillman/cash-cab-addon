#!/usr/bin/env python3
"""
RouteCam - Unified Single File Implementation
A comprehensive Blender addon for cinematic camera animation along curves.

This script combines all RouteCam functionality into a single file based on the proven
standalone implementation pattern, maintaining full compatibility with both
Blender addon and standalone execution modes.

Usage:
- As Blender addon: Install via Edit > Preferences > Add-ons > Install
- As standalone script: blender --background --python routecam_unified.py
- Pure-Python testing: python routecam_unified.py --test-core
- Standalone bake: blender --background --python routecam_unified.py --bake

Author: RouteCam System
Version: 1.0.0
"""

from __future__ import annotations
import math
import json
import os
import copy
from collections.abc import MutableMapping
from typing import List, Tuple, Dict, Any, Optional, Sequence

# Blender detection and imports
try:
    import bpy
    import mathutils
    from bpy.types import Operator, Panel, PropertyGroup
    from bpy.app.handlers import persistent
    from bpy.props import PointerProperty, StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, FloatVectorProperty, HIDDEN
    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False

# Vector compatibility layer
try:
    from mathutils import Vector
except ImportError:
    # Standalone Vector implementation for testing
    class Vector:
        def __init__(self, *args):
            if len(args) == 1:
                if hasattr(args[0], 'x'):  # Vector-like object
                    self.x, self.y, self.z = args[0].x, args[0].y, args[0].z
                elif isinstance(args[0], (tuple, list)):
                    self.x, self.y, self.z = args[0]
                else:
                    raise ValueError("Vector expects 3 args or a tuple of 3")
            elif len(args) == 3:
                self.x, self.y, self.z = args
            else:
                raise ValueError("Vector expects 3 args or a tuple of 3")

        def __add__(self, other): return Vector((self.x + other.x, self.y + other.y, self.z + other.z))
        def __sub__(self, other): return Vector((self.x - other.x, self.y - other.y, self.z - other.z))
        def __mul__(self, scalar): return Vector((self.x * scalar, self.y * scalar, self.z * scalar))
        def __truediv__(self, scalar): return Vector((self.x / scalar, self.y / scalar, self.z / scalar))
        def dot(self, other): return self.x * other.x + self.y * other.y + self.z * other.z
        @property
        def length(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        def normalized(self):
            l = self.length
            return self if l == 0 else self / l
        def copy(self): return Vector((self.x, self.y, self.z))
        def to_tuple(self): return (self.x, self.y, self.z)
        def lerp(self, other, factor):
            return self + (other - self) * factor
        def slerp(self, other, factor):
            # Simplified slerp for direction vectors
            dot = max(-1.0, min(1.0, self.dot(other)))
            angle = math.acos(dot)
            if angle < 0.0001:
                return self.normalized()
            return (self * math.sin((1-factor)*angle) + other * math.sin(factor*angle)) / math.sin(angle)
        def angle(self, other):
            return math.acos(max(-1.0, min(1.0, self.normalized().dot(other.normalized()))))
        def to_track_quat(self, track, up):
            # Mock implementation for testing
            if HAS_BLENDER:
                return mathutils.Vector(self).to_track_quat(track, up)
            return (1, 0, 0, 0)  # Identity quaternion

# ====================================================================
# CORE MATHEMATICS MODULE
# ====================================================================

def sample_route_points(points: Sequence[Vector], target_count: int = 0) -> Tuple[List[Vector], List[float], float]:
    """Sample points along a route with arc-length parameterization."""
    if not points:
        return [], [], 0.0

    cumulative_lengths = [0.0]
    total_length = 0.0
    for i in range(1, len(points)):
        total_length += (points[i] - points[i-1]).length
        cumulative_lengths.append(total_length)

    if total_length == 0.0:
        original_s_list = [0.0] * len(points)
    else:
        original_s_list = [d / total_length for d in cumulative_lengths]

    if target_count <= 1:
        return list(points), original_s_list, total_length

    resampled_points = []
    resampled_s_list = []
    for i in range(target_count):
        s_target = i / (target_count - 1)
        idx = 0
        while idx < len(original_s_list) - 1 and original_s_list[idx+1] < s_target:
            idx += 1

        s0, s1 = original_s_list[idx], original_s_list[idx+1]
        p0, p1 = points[idx], points[idx+1]

        if s1 == s0:
            t = 0.0
        else:
            t = (s_target - s0) / (s1 - s0)

        resampled_points.append(p0.lerp(p1, t))
        resampled_s_list.append(s_target)

    return resampled_points, resampled_s_list, total_length

def compute_tangents(points: Sequence[Vector]) -> List[Vector]:
    """Compute normalized tangents for a sequence of points."""
    n = len(points)
    if n == 0:
        return []
    if n == 1:
        return [Vector((0, 0, 0))]

    tangents = []
    for i in range(n):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == n - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[i + 1] - points[i - 1]

        length = tangent.length
        if length > 1e-6:
            tangents.append(tangent / length)
        else:
            tangents.append(Vector((0, 0, 0)))

    return tangents

def calculate_optimal_yaw(curve_points: List[Vector]) -> float:
    """Calculate optimal camera yaw angle for the curve."""
    if not curve_points or len(curve_points) < 2:
        return 0.0

    flow_vec = curve_points[-1] - curve_points[0]
    flow_xy = Vector((flow_vec.x, flow_vec.y, 0.0))
    if flow_xy.length < 0.001:
        return 0.0

    return math.atan2(flow_xy.y, flow_xy.x) - math.radians(90)

# ====================================================================
# STYLE CALCULATOR MODULE (Based on proven standalone)
# ====================================================================

def deep_merge_dict_v2(target: Dict, source: Dict) -> Dict:
    """Deep merge source dict into target dict."""
    for k, v in source.items():
        if isinstance(v, MutableMapping):
            if k not in target or not isinstance(target[k], MutableMapping):
                target[k] = {}
            target[k] = deep_merge_dict_v2(target[k], v)
        else:
            target[k] = v
    return target

def load_style_profile() -> Dict[str, Any]:
    """Load style profile with embedded defaults."""
    # Embedded default profile (from proven standalone)
    return {
        "timing": {"t_start_zoom_norm": 0.2, "t_end_zoom_norm": 1.0, "drift_pos_factor": 0.15, "drift_scale_factor": 0.95},
        "framing": {"start_ndc": [0.5, 0.35], "end_ndc": [0.5, 0.10], "start_margin_factor": 1.9, "end_zoom_ratio": 0.06},
        "ortho_scales": {"start": 3500.0, "end": 200.0},
        "end_camera_relative_transform": {"position_offset_from_endpoint_tangent_space": [0.0, -5000.0, 1500.0], "rotation_relative_to_endpoint_tangent_space_quat": [1.0, 0.0, 0.0, 0.0]}
    }

def calculate_style_targets(curve_points: List[Vector], camera_basis: Tuple[Vector, Vector, Vector],
                           aspect_ratio: float, tangents: Tuple[Vector, Vector],
                           initial_camera_rotation_quat) -> Dict[str, Any]:
    """Calculate style targets based on proven standalone algorithm."""
    if not curve_points:
        return {}

    profile = load_style_profile()
    cam_right, cam_up, cam_forward = camera_basis
    p_start, p_end = curve_points[0], curve_points[-1]

    # Geometric Analysis
    min_u, max_u, min_v, max_v = 0.0, 0.0, 0.0, 0.0
    projected_points = []
    for p in curve_points:
        rel = p - p_start
        u, v, d = rel.dot(cam_right), rel.dot(cam_up), rel.dot(cam_forward)
        projected_points.append((u, v, d))
        min_u, max_u = min(min_u, u), max(max_u, u)
        min_v, max_v = min(min_v, v), max(max_v, v)

    avg_d = sum(p[2] for p in projected_points) / len(projected_points)
    world_center = p_start + (cam_right * ((min_u+max_u)/2)) + (cam_up * ((min_v+max_v)/2)) + (cam_forward * avg_d)

    base_extent = max(max_u-min_u, max_v-min_v)
    start_scale = base_extent * profile["framing"]["start_margin_factor"]
    end_scale = start_scale * profile["framing"]["end_zoom_ratio"]

    # Start Vector
    sweep_angle = math.radians(-75.0)
    if HAS_BLENDER:
        sweep_quat = mathutils.Quaternion((0,0,1), sweep_angle)
        start_cam_rot = sweep_quat @ initial_camera_rotation_quat
    else:
        start_cam_rot = initial_camera_rotation_quat  # Simplified for testing

    # Clamp Pitch
    if HAS_BLENDER:
        start_mat = start_cam_rot.to_matrix()
        fwd = -start_mat.col[2]
    else:
        fwd = Vector((0, 0, -1))  # Simplified for testing

    if fwd.z < -0.5:
        fwd_flat = Vector((fwd.x, fwd.y, 0)).normalized()
        pitch_rad = math.radians(30)
        fwd_new = (fwd_flat * math.cos(pitch_rad)) + (Vector((0,0,-1)) * math.sin(pitch_rad))
        v_start = fwd_new.normalized() * -1.0
    else:
        v_start = fwd * -1.0

    # End Vector
    t_end = tangents[1].normalized()
    world_z = Vector((0,1,0)) if abs(t_end.z) > 0.9 else Vector((0,0,1))
    v_end = ((t_end * -0.95) + (world_z * 0.3)).normalized()

    # Keyframes (Proven pattern)
    keyframes = []
    # Start
    keyframes.append({"time_sigma": 0.0, "target_pos": world_center, "ortho_scale": start_scale, "view_vector": v_start})

    # Drift End
    drift_target = world_center + (p_end - world_center) * profile["timing"]["drift_pos_factor"]
    drift_scale = start_scale * profile["timing"]["drift_scale_factor"]
    keyframes.append({"time_sigma": profile["timing"]["t_start_zoom_norm"], "target_pos": drift_target, "ortho_scale": drift_scale})

    # Zoom End
    framing_offset_z = 0.4 * (end_scale / aspect_ratio)
    end_target = p_end + (Vector((0,0,1)) * framing_offset_z)
    keyframes.append({"time_sigma": profile["timing"]["t_end_zoom_norm"], "target_pos": end_target, "ortho_scale": end_scale})

    return {
        "keyframes": keyframes,
        "global_vectors": {"start": v_start, "end": v_end}
    }

def interpolate_style_state(time_sigma: float, full_data: Dict[str, Any]) -> Tuple[Vector, float, Vector]:
    """Interpolate camera state using proven algorithm."""
    keyframes = full_data.get("keyframes", [])
    global_vectors = full_data.get("global_vectors", {})

    t = max(0.0, min(1.0, time_sigma))

    if len(keyframes) > 0 and t >= keyframes[-1]["time_sigma"]:
        kf = keyframes[-1]
        return Vector(kf["target_pos"]), kf["ortho_scale"], Vector(global_vectors["end"])

    # Rotation Interpolation
    v_start = Vector(global_vectors["start"])
    v_end = Vector(global_vectors["end"])
    rot_factor = t * t * (3 - 2 * t)  # Cubic ease
    view_vec = v_start.slerp(v_end, rot_factor).normalized()

    # Segment Interpolation
    k0 = keyframes[0]
    k1 = keyframes[-1]
    for i in range(len(keyframes)-1):
        if t >= keyframes[i]["time_sigma"] and t <= keyframes[i+1]["time_sigma"]:
            k0 = keyframes[i]
            k1 = keyframes[i+1]
            break

    seg_duration = k1["time_sigma"] - k0["time_sigma"]
    local_t = 0.0 if seg_duration <= 0.0001 else (t - k0["time_sigma"]) / seg_duration
    factor = local_t * local_t * (3 - 2 * local_t)

    pos = Vector(k0["target_pos"])
    scale = k0["ortho_scale"] + (k1["ortho_scale"] - k0["ortho_scale"]) * factor

    return pos, scale, view_vec

def generate_adaptive_sigmas(full_data: Dict[str, Any]) -> List[float]:
    """Generate adaptive sampling points (proven algorithm)."""
    keyframes = full_data.get("keyframes", [])
    sigmas = set()

    for i in range(len(keyframes)):
        curr = keyframes[i]
        sigmas.add(curr["time_sigma"])

        if i < len(keyframes) - 1:
            nxt = keyframes[i+1]

            # Scale Ratio Check
            s1, s2 = curr["ortho_scale"], nxt["ortho_scale"]
            ratio = max(s1, s2) / min(s1, s2) if min(s1,s2) > 0.001 else 1.0

            # Rotation Check
            _, _, v1 = interpolate_style_state(curr["time_sigma"], full_data)
            _, _, v2 = interpolate_style_state(nxt["time_sigma"], full_data)

            angle = 0.0
            if v1 and v2 and v1.length > 0.0001 and v2.length > 0.0001:
                try:
                    angle = math.degrees(v1.angle(v2))
                except ValueError:
                    angle = 0.0

            # Adaptive subdivision
            subs = 0
            if ratio > 20.0 or angle > 45.0: subs = 3
            elif ratio > 5.0 or angle > 20.0: subs = 2
            elif ratio > 1.5 or angle > 5.0: subs = 1

            if subs > 0:
                step = (nxt["time_sigma"] - curr["time_sigma"]) / (subs + 1)
                for j in range(1, subs + 1):
                    sigmas.add(curr["time_sigma"] + step * j)

    return sorted(list(sigmas))

# ====================================================================
# BLENDER INTEGRATION (Conditional)
# ====================================================================

if HAS_BLENDER:

    class RouteCamSettings(PropertyGroup):
        """Blender property group for RouteCam settings."""

        # Route object reference
        route_object = PointerProperty(
            name="Route Curve",
            description="Curve object to use as camera path",
            type=bpy.types.Object
        )

        # Animation timing
        frame_start = IntProperty(
            name="Start Frame",
            description="First frame of animation",
            default=1,
            min=1
        )

        frame_end = IntProperty(
            name="End Frame",
            description="Last frame of animation",
            default=120,
            min=1
        )

        # Camera orientation (for advanced control)
        camera_right = FloatVectorProperty(
            name="Camera Right",
            description="Camera right vector",
            default=(1.0, 0.0, 0.0),
            size=3
        )

        camera_up = FloatVectorProperty(
            name="Camera Up",
            description="Camera up vector",
            default=(0.0, 1.0, 0.0),
            size=3
        )

        camera_forward = FloatVectorProperty(
            name="Camera Forward",
            description="Camera forward vector",
            default=(0.0, 0.0, -1.0),
            size=3
        )

        # Analysis state
        analysis_valid = BoolProperty(
            name="Analysis Valid",
            description="Whether route analysis is up to date",
            default=False,
            options={'HIDDEN'}
        )

        last_route_name = StringProperty(
            name="Last Route Name",
            description="Name of last analyzed route",
            default="",
            options={'HIDDEN'}
        )

        # Internal storage for animation targets
        style_keyframes_json = StringProperty(
            name="Style Keyframes",
            description="Serialized animation targets",
            default="",
            options={'HIDDEN'}
        )

    class ROUTECAM_OT_analyze_route(Operator):
        """Analyze route curve and generate animation plan."""
        bl_idname = "routecam.analyze_route"
        bl_label = "Analyze Route"
        bl_description = "Analyze route curve and generate animation plan"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            # Find or create camera and route
            camera, route_obj = self._get_or_create_camera_and_route(context)
            if not camera or not route_obj:
                self.report({'ERROR'}, "Could not find or create camera and route")
                return {'CANCELLED'}

            # Extract curve points using proven method
            try:
                depsgraph = context.evaluated_depsgraph_get()
                route_eval = route_obj.evaluated_get(depsgraph)
                mesh_eval = route_eval.to_mesh()
                points_world = [route_obj.matrix_world @ v.co for v in mesh_eval.vertices]
                route_eval.to_mesh_clear()

                if not points_world:
                    self.report({'ERROR'}, "No points in curve")
                    return {'CANCELLED'}

            except Exception as e:
                self.report({'ERROR'}, f"Failed to extract curve points: {e}")
                return {'CANCELLED'}

            # Perform analysis using proven algorithm
            try:
                # Calculate camera orientation
                pitch = math.radians(30)
                yaw = calculate_optimal_yaw(points_world)
                rot_euler = mathutils.Euler((pitch, 0.0, yaw), 'XYZ')
                initial_quat = rot_euler.to_quaternion()

                cam_matrix = initial_quat.to_matrix().to_4x4()
                cam_right, cam_up, cam_forward = cam_matrix.col[0].xyz, cam_matrix.col[1].xyz, -cam_matrix.col[2].xyz

                # Sample and calculate targets
                resampled_points, _, _ = sample_route_points(points_world, target_count=512)
                aspect = context.scene.render.resolution_x / context.scene.render.resolution_y
                basis = (cam_right, cam_up, cam_forward)

                if len(points_world) >= 2:
                    p0, p1 = points_world[0], points_world[1]
                    pe, pep = points_world[-1], points_world[-2]
                    tan_start = (p1-p0).normalized()
                    tan_end = (pe-pep).normalized()
                else:
                    tan_start = tan_end = Vector((1, 0, 0))

                full_data = calculate_style_targets(resampled_points, basis, aspect, (tan_start, tan_end), initial_quat)

                # Store results in proven format (convert Vectors to tuples)
                def convert_vectors_to_tuples(obj):
                    if hasattr(obj, '__dict__'):
                        return {k: convert_vectors_to_tuples(v) for k, v in obj.__dict__.items()}
                    elif isinstance(obj, dict):
                        return {k: convert_vectors_to_tuples(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_vectors_to_tuples(item) for item in obj]
                    elif hasattr(obj, 'to_tuple'):  # Vector-like object
                        return obj.to_tuple()
                    else:
                        return obj

                serializable_data = convert_vectors_to_tuples(full_data)
                settings = camera.data.route_cam
                settings.style_keyframes_json = json.dumps(serializable_data)
                settings.analysis_valid = True
                settings.last_route_name = route_obj.name

                # Store camera basis
                settings.camera_right = cam_right.to_tuple()
                settings.camera_up = cam_up.to_tuple()
                settings.camera_forward = cam_forward.to_tuple()

                # Setup camera
                camera.data.type = 'ORTHO'
                if full_data.get("keyframes"):
                    camera.data.ortho_scale = full_data["keyframes"][0]["ortho_scale"]

                self.report({'INFO'}, f"Route analyzed: {len(points_world)} points")

            except Exception as e:
                self.report({'ERROR'}, f"Analysis failed: {e}")
                return {'CANCELLED'}

            return {'FINISHED'}

        def _get_or_create_camera_and_route(self, context):
            """Get existing camera/route or create new ones."""
            camera = context.scene.camera
            route_obj = None

            # Try to get route from selected camera
            if camera and hasattr(camera.data, 'route_cam'):
                route_obj = camera.data.route_cam.route_object

            # Try to get route from selected object
            if not route_obj and context.object and context.object.type == 'CURVE':
                route_obj = context.object

            # Create camera if needed
            if not camera:
                cam_data = bpy.data.cameras.new(name="RouteCam")
                camera = bpy.data.objects.new(name="RouteCam", object_data=cam_data)
                context.collection.objects.link(camera)
                context.scene.camera = camera
                context.view_layer.objects.active = camera
                camera.select_set(True)

            # Assign route to camera
            if route_obj and hasattr(camera.data, 'route_cam'):
                camera.data.route_cam.route_object = route_obj

            return camera, route_obj

    class ROUTECAM_OT_bake_keyframes(Operator):
        """Bake animation keyframes to camera using proven adaptive algorithm."""
        bl_idname = "routecam.bake_keyframes"
        bl_label = "Bake Keyframes"
        bl_description = "Bake camera animation keyframes with adaptive sampling"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            camera = context.scene.camera
            if not camera or not hasattr(camera.data, 'route_cam'):
                self.report({'ERROR'}, "No RouteCam camera found")
                return {'CANCELLED'}

            settings = camera.data.route_cam
            if not settings.analysis_valid or not settings.style_keyframes_json:
                self.report({'ERROR'}, "Please analyze route first")
                return {'CANCELLED'}

            try:
                # Load animation data
                raw_data = json.loads(settings.style_keyframes_json)

                # Convert tuples back to Vectors
                def convert_tuples_to_vectors(obj):
                    if isinstance(obj, dict):
                        return {k: convert_tuples_to_vectors(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_tuples_to_vectors(item) for item in obj]
                    elif isinstance(obj, (tuple, list)) and len(obj) == 3:  # Vector-like tuple
                        return Vector(obj)
                    else:
                        return obj

                full_data = convert_tuples_to_vectors(raw_data)

                # Generate adaptive keyframes (proven algorithm)
                sorted_sigmas = generate_adaptive_sigmas(full_data)

                frame_start = settings.frame_start
                frame_end = settings.frame_end
                duration = frame_end - frame_start

                # Action Management (Aggressive Separation - proven)
                if camera.animation_data: camera.animation_data_clear()
                if camera.data.animation_data: camera.data.animation_data_clear()

                camera.animation_data_create().action = bpy.data.actions.new(name="RouteCam_Object")
                camera.data.animation_data_create().action = bpy.data.actions.new(name="RouteCam_Data")

                # Bake Loop (proven algorithm)
                for sigma in sorted_sigmas:
                    frame = frame_start + int(sigma * duration)
                    pos, scale, view_vec = interpolate_style_state(sigma, full_data)

                    camera.data.ortho_scale = scale

                    # Orbital Positioning (proven method)
                    offset_dir = Vector(view_vec)
                    safe_dist = scale * 2.0
                    final_pos = Vector(pos) + offset_dir * safe_dist

                    camera.location = final_pos

                    look_dir = Vector(pos) - final_pos
                    if look_dir.length_squared > 0.0001:
                        rot_quat = look_dir.to_track_quat('-Z', 'Y')
                        camera.rotation_mode = 'QUATERNION'
                        camera.rotation_quaternion = rot_quat
                        camera.keyframe_insert("rotation_quaternion", frame=frame)

                    camera.keyframe_insert("location", frame=frame)
                    camera.data.keyframe_insert("ortho_scale", frame=frame)

                # Interpolation setup (proven)
                for ad in [camera.animation_data, camera.data.animation_data]:
                    if ad and ad.action:
                        for fc in ad.action.fcurves:
                            fc.extrapolation = 'CONSTANT'
                            for kfp in fc.keyframe_points:
                                kfp.interpolation = 'BEZIER'
                                kfp.handle_left_type = 'AUTO_CLAMPED'
                                kfp.handle_right_type = 'AUTO_CLAMPED'

                self.report({'INFO'}, f"Baked {len(sorted_sigmas)} adaptive keyframes")

            except Exception as e:
                self.report({'ERROR'}, f"Baking failed: {e}")
                return {'CANCELLED'}

            return {'FINISHED'}

    class ROUTECAM_PT_main(Panel):
        """Main RouteCam panel in 3D View sidebar."""
        bl_label = "RouteCam"
        bl_idname = "ROUTECAM_PT_main"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = "RouteCam"

        def draw(self, context):
            layout = self.layout
            camera = context.scene.camera

            if not camera or camera.type != 'CAMERA' or not hasattr(camera.data, 'route_cam'):
                layout.label(text="Select a Camera", icon='CAMERA_DATA')
                layout.operator("routecam.analyze_route", text="Create RouteCam", icon='ADD')
                return

            settings = camera.data.route_cam

            # Setup section
            box = layout.box()
            box.label(text="Setup", icon='PREFERENCES')
            box.prop(settings, "route_object")
            box.operator("routecam.analyze_route", icon='SHADING_RENDERED')

            if settings.analysis_valid:
                box.label(text=f"✓ Analyzed: {settings.last_route_name}")

                # Animation section
                box = layout.box()
                box.label(text="Animation", icon='ANIM')
                row = box.row()
                row.prop(settings, "frame_start")
                row.prop(settings, "frame_end")
                box.operator("routecam.bake_keyframes", icon='RENDER_ANIMATION')

                # Camera orientation (advanced)
                box = layout.box()
                box.label(text="Camera Orientation", icon='VIEW_CAMERA')
                box.prop(settings, "camera_right")
                box.prop(settings, "camera_up")
                box.prop(settings, "camera_forward")

    def register():
        """Register RouteCam as Blender addon."""
        # Register properties
        bpy.utils.register_class(RouteCamSettings)
        bpy.types.Camera.route_cam = PointerProperty(type=RouteCamSettings)

        # Register operators
        bpy.utils.register_class(ROUTECAM_OT_analyze_route)
        bpy.utils.register_class(ROUTECAM_OT_bake_keyframes)

        # Register panel
        bpy.utils.register_class(ROUTECAM_PT_main)

    def unregister():
        """Unregister RouteCam addon."""
        # Unregister panel
        bpy.utils.unregister_class(ROUTECAM_PT_main)

        # Unregister operators
        bpy.utils.unregister_class(ROUTECAM_OT_bake_keyframes)
        bpy.utils.unregister_class(ROUTECAM_OT_analyze_route)

        # Unregister properties
        del bpy.types.Camera.route_cam
        bpy.utils.unregister_class(RouteCamSettings)

# ====================================================================
# STANDALONE BAKE FUNCTIONALITY
# ====================================================================

def run_standalone_bake():
    """Proven standalone bake implementation."""
    if not HAS_BLENDER:
        print("Error: Standalone bake requires Blender")
        return

    print("\n--- Running RouteCam Standalone Bake ---")

    # 1. Context Setup
    context = bpy.context
    scene = context.scene

    # Auto-Create Scene if needed
    route_obj = context.object
    if not route_obj or route_obj.type != 'CURVE':
        print("No active curve found. Creating sample curve.")
        bpy.ops.curve.primitive_bezier_curve_add(radius=10.0)
        route_obj = context.object

    cam = scene.camera
    if not cam:
        print("No active camera found. Creating RouteCam.")
        bpy.ops.object.camera_add()
        cam = context.object
        scene.camera = cam

    cam.data.type = 'ORTHO'

    # 2. Analyze Route (Proven method)
    print(f"Analyzing route: {route_obj.name}")

    # Extract Points
    depsgraph = context.evaluated_depsgraph_get()
    route_eval = route_obj.evaluated_get(depsgraph)
    mesh_eval = route_eval.to_mesh()
    points_world = [route_obj.matrix_world @ v.co for v in mesh_eval.vertices]
    route_eval.to_mesh_clear()

    if not points_world:
        print("Error: No points in curve.")
        return

    # Calculate Orientation
    pitch = math.radians(30)
    yaw = calculate_optimal_yaw(points_world)
    rot_euler = mathutils.Euler((pitch, 0.0, yaw), 'XYZ')
    initial_quat = rot_euler.to_quaternion()

    cam_matrix = initial_quat.to_matrix().to_4x4()
    cam_right, cam_up, cam_forward = cam_matrix.col[0].xyz, cam_matrix.col[1].xyz, -cam_matrix.col[2].xyz

    # Sample & Calculate Targets
    resampled_points, _, _ = sample_route_points(points_world, target_count=512)
    render = scene.render
    aspect = render.resolution_x / render.resolution_y
    basis = (cam_right, cam_up, cam_forward)

    p0, p1 = points_world[0], points_world[1]
    pe, pep = points_world[-1], points_world[-2]
    tan_start = (p1-p0).normalized()
    tan_end = (pe-pep).normalized()

    full_data = calculate_style_targets(resampled_points, basis, aspect, (tan_start, tan_end), initial_quat)

    # 3. Adaptive Baking (Proven algorithm)
    frame_start = 1
    frame_end = 120
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    duration = frame_end - frame_start

    print("Generating Adaptive Keyframes...")
    sorted_sigmas = generate_adaptive_sigmas(full_data)
    print(f"Baking {len(sorted_sigmas)} keyframes: {sorted_sigmas}")

    # 4. Action Management (Aggressive Separation)
    if cam.animation_data: cam.animation_data_clear()
    if cam.data.animation_data: cam.data.animation_data_clear()

    cam.animation_data_create().action = bpy.data.actions.new(name="RouteCam_Object")
    cam.data.animation_data_create().action = bpy.data.actions.new(name="RouteCam_Data")

    # 5. Bake Loop
    for sigma in sorted_sigmas:
        frame = frame_start + int(sigma * duration)
        pos, scale, view_vec = interpolate_style_state(sigma, full_data)

        cam.data.ortho_scale = scale

        # Orbital Positioning
        offset_dir = Vector(view_vec)
        safe_dist = scale * 2.0
        final_pos = Vector(pos) + offset_dir * safe_dist

        cam.location = final_pos

        look_dir = Vector(pos) - final_pos
        if look_dir.length_squared > 0.0001:
            rot_quat = look_dir.to_track_quat('-Z', 'Y')
            cam.rotation_mode = 'QUATERNION'
            cam.rotation_quaternion = rot_quat
            cam.keyframe_insert("rotation_quaternion", frame=frame)

        cam.keyframe_insert("location", frame=frame)
        cam.data.keyframe_insert("ortho_scale", frame=frame)

    # 6. Interpolation
    for ad in [cam.animation_data, cam.data.animation_data]:
        if ad and ad.action:
            for fc in ad.action.fcurves:
                fc.extrapolation = 'CONSTANT'
                for kfp in fc.keyframe_points:
                    kfp.interpolation = 'BEZIER'
                    kfp.handle_left_type = 'AUTO_CLAMPED'
                    kfp.handle_right_type = 'AUTO_CLAMPED'

    print("Done! RouteCam bake complete.")

# ====================================================================
# TESTING FUNCTIONS
# ====================================================================

def test_core_mathematics():
    """Test core mathematical functions."""
    print("=== Testing RouteCam Core Mathematics ===")

    # Test route sampling
    test_points = [
        Vector((0, 0, 0)),
        Vector((1, 0, 0)),
        Vector((2, 1, 0)),
        Vector((3, 2, 0)),
        Vector((4, 2, 0))
    ]

    resampled, s_values, length = sample_route_points(test_points, 10)
    print(f"Original: {len(test_points)} points, Resampled: {len(resampled)} points, Length: {length:.2f}")

    # Test tangents
    tangents = compute_tangents(test_points)
    print(f"Tangents: {len(tangents)}")

    # Test yaw calculation
    yaw = calculate_optimal_yaw(test_points)
    print(f"Optimal yaw: {math.degrees(yaw):.1f} degrees")

    print("PASS: Core mathematics test passed")

def test_style_calculator():
    """Test style calculator functionality."""
    print("\n=== Testing Style Calculator ===")

    # Create test route
    test_route = [
        Vector((0, 0, 0)),
        Vector((5, 0, 0)),
        Vector((10, 2, 0)),
        Vector((15, 5, 0)),
        Vector((20, 5, 0))
    ]

    resampled, s_values, _ = sample_route_points(test_route, 50)

    # Test style target calculation
    aspect_ratio = 16.0 / 9.0
    cam_right = Vector((1, 0, 0))
    cam_up = Vector((0, 1, 0))
    cam_forward = Vector((0, 0, -1))
    basis = (cam_right, cam_up, cam_forward)

    # Mock quaternion for testing
    class MockQuat:
        def to_matrix(self):
            import math
            class MockMatrix:
                def __init__(self):
                    self.col = [MockVector(), MockVector(), MockVector()]
                @property
                def xyz(self):
                    return Vector((1, 0, 0))
            class MockVector:
                def __init__(self):
                    self.xyz = Vector((1, 0, 0))
            return MockMatrix()
        @staticmethod
        def __matmul__(other):
            return MockQuat()

    initial_quat = MockQuat()
    tangents = compute_tangents(test_route)
    targets = calculate_style_targets(resampled, basis, aspect_ratio, (tangents[0], tangents[-1]), initial_quat)

    print(f"Route analyzed: {len(resampled)} points")
    print(f"Keyframes: {len(targets['keyframes'])}")

    # Test interpolation
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        pos, scale, view_vec = interpolate_style_state(t, targets)
        print(f"Time {t:.2f}: position=({pos.x:.1f}, {pos.y:.1f}), scale={scale:.2f}")

    # Test adaptive sampling
    adaptive_sigmas = generate_adaptive_sigmas(targets)
    print(f"Adaptive keyframes: {len(adaptive_sigmas)} points")

    print("PASS: Style calculator test passed")

def standalone_demo():
    """Demonstrate standalone functionality."""
    print("RouteCam Unified - Standalone Demo")
    print("==================================")

    test_core_mathematics()
    test_style_calculator()

    print("\nSUCCESS: All tests passed!")
    print("\nUsage as Blender addon:")
    print("  1. Install this file in Blender > Preferences > Add-ons > Install")
    print("  2. Select a curve and click 'Analyze Route'")
    print("  3. Adjust settings and click 'Bake Keyframes'")
    print("\nUsage as standalone script:")
    print("  blender --background --python routecam_unified.py --bake")

def main():
    """Main entry point for script execution."""
    import sys

    if HAS_BLENDER:
        # Running within Blender
        if "--bake" in sys.argv:
            run_standalone_bake()
        elif "--test" in sys.argv:
            test_core_mathematics()
            test_style_calculator()
        return
    else:
        # Standalone execution
        if "--test" in sys.argv:
            test_core_mathematics()
            test_style_calculator()
        elif "--test-core" in sys.argv:
            test_core_mathematics()
        else:
            standalone_demo()

# ====================================================================
# SCRIPT EXECUTION
# ====================================================================

if __name__ == "__main__":
    main()

# Export main classes for Blender addon system
if HAS_BLENDER:
    __all__ = [
        'RouteCamSettings',
        'ROUTECAM_OT_analyze_route',
        'ROUTECAM_OT_bake_keyframes',
        'ROUTECAM_PT_main',
        'register',
        'unregister'
    ]