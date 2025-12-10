"""
Engine Viz: Logic Port
Based on generalized_routecam_with_ui.py
"""
import bpy
import math
import mathutils

# =============================================================================
# CORE MATH
# =============================================================================

class RouteAnalysis:
    """Encapsulates geometric analysis of the curve."""
    def __init__(self, curve_obj):
        self.curve = curve_obj
        self.points = self._get_points()
        self.valid = len(self.points) > 1
        
        if self.valid:
            self.start_p = self.points[0]
            self.end_p = self.points[-1]
            self.center = self._get_center()
            self.dims = self._get_dims()
            self.flow_vec = (self.end_p - self.start_p).normalized()
            if len(self.points) > 1:
                self.end_tangent = (self.points[-1] - self.points[-2]).normalized()
            else:
                self.end_tangent = mathutils.Vector((0,1,0))
            
            if (self.end_p - self.start_p).length < 0.001:
                if len(self.points) > 1:
                    start_tan = (self.points[1] - self.points[0]).normalized()
                    self.flow_angle = math.atan2(start_tan.y, start_tan.x)
                else:
                    self.flow_angle = 0.0
            else:
                self.flow_angle = math.atan2(self.flow_vec.y, self.flow_vec.x)
            
            self.tangent_angle = math.atan2(self.end_tangent.y, self.end_tangent.x)

    def _get_points(self):
        points = []
        mw = self.curve.matrix_world
        for spline in self.curve.data.splines:
            if spline.type == 'BEZIER':
                for p in spline.bezier_points:
                    points.append(mw @ p.co)
            else:
                for p in spline.points:
                    points.append(mw @ mathutils.Vector((p.co.x, p.co.y, p.co.z)))
        return points

    def _get_center(self):
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return mathutils.Vector((sum(xs)/len(xs), sum(ys)/len(ys), 0.0))

    def _get_dims(self):
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        return max(w, h)

def get_shortest_delta(angle_from, angle_to):
    delta = angle_to - angle_from
    while delta > math.pi: delta -= 2 * math.pi
    while delta < -math.pi: delta += 2 * math.pi
    return delta

def calculate_camera_transform(target_pos, orbit_angle_rad, pitch_rad, ortho_scale, view_offset=(0,0)):
    safe_pitch = min(pitch_rad, math.radians(89.9))
    final_quat = mathutils.Euler((safe_pitch, 0, orbit_angle_rad - math.pi/2), 'XYZ').to_quaternion()
    
    dist = ortho_scale * 1.5
    back_vec = final_quat @ mathutils.Vector((0,0,1))
    location = target_pos + (back_vec * dist)
    
    cam_right = final_quat @ mathutils.Vector((1,0,0))
    cam_up = final_quat @ mathutils.Vector((0,1,0))
    
    shift_vec = (cam_right * -view_offset[0]) + (cam_up * -view_offset[1])
    location += shift_vec * ortho_scale
    
    return location, final_quat

def calculate_state_at_t(t, analysis, props):
    # Access props via dictionary or object, assuming props is an object
    # We will need to wrap the props in the main operator
    
    # Extract values safely
    s1_angle = props.sect1_angle
    s1_pitch = props.sect1_pitch
    s1_margin = props.sect1_margin
    
    s3_angle = props.sect3_angle
    s3_pitch = props.sect3_pitch
    s3_zoom = props.sect3_zoom
    s3_off_x = props.sect3_offset_x
    s3_off_y = props.sect3_offset_y
    
    yaw_1 = analysis.flow_angle + math.radians(s1_angle)
    pitch_1 = math.radians(s1_pitch)
    scale_1 = analysis.dims * s1_margin
    off_1 = mathutils.Vector((0.0, 0.0))
    target_1 = analysis.center
    
    yaw_3 = analysis.tangent_angle + math.radians(s3_angle)
    pitch_3 = math.radians(s3_pitch)
    scale_3 = analysis.dims * s3_zoom
    off_3 = mathutils.Vector((s3_off_x, s3_off_y))
    target_3 = analysis.end_p
    
    drift_t = props.sect2_time
    push = props.sect2_push
    target_drift = analysis.center.lerp(analysis.end_p, push)
    delta_yaw = get_shortest_delta(yaw_1, yaw_3)
    
    if t <= drift_t:
        seg_t = t / drift_t if drift_t > 0 else 0
        curr_target = target_1.lerp(target_drift, seg_t)
    else:
        seg_t = (t - drift_t) / (1.0 - drift_t) if (1.0 - drift_t) > 0 else 0
        curr_target = target_drift.lerp(target_3, seg_t)
    
    curr_pitch = pitch_1 + (pitch_3 - pitch_1) * t
    curr_scale = scale_1 + (scale_3 - scale_1) * t
    curr_offset = off_1.lerp(off_3, t)

    t_rot = math.pow(t, props.rot_power)
    curr_yaw = yaw_1 + (delta_yaw * t_rot)
    
    return curr_target, curr_pitch, curr_scale, curr_offset, curr_yaw

def generate_viz_curve(cam_obj, points):
    viz_name = f"{cam_obj.name}_Path_Viz"
    viz_obj = bpy.data.objects.get(viz_name)
    
    if not viz_obj:
        curve_data = bpy.data.curves.new(name=viz_name, type='CURVE')
        curve_data.dimensions = '3D'
        viz_obj = bpy.data.objects.new(viz_name, curve_data)
        bpy.context.collection.objects.link(viz_obj)
    
    curve_data = viz_obj.data
    curve_data.splines.clear()
    spline = curve_data.splines.new('POLY')
    
    spline.points.add(len(points)-1)
    for i, p in enumerate(points):
        spline.points[i].co = (p.x, p.y, p.z, 1.0)
            
    viz_obj.show_wire = True
    viz_obj.show_in_front = True
    
def run_generation(cam, props):
    curve = props.target_curve
    if not curve: return

    analysis = RouteAnalysis(curve)
    if not analysis.valid: return
        
    if cam.animation_data:
        cam.animation_data_clear()
        
    cam.rotation_mode = 'QUATERNION'
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 100000

    duration = props.duration
    viz_points = []
    
    # Dense baking for simplicity in this engine
    for f in range(1, duration + 1):
        t = (f - 1) / (duration - 1)
        
        c_t, c_p, c_s, c_o, c_y = calculate_state_at_t(t, analysis, props)
        loc, rot = calculate_camera_transform(c_t, c_y, c_p, c_s, c_o)
        
        cam.location = loc
        cam.rotation_quaternion = rot
        cam.data.ortho_scale = c_s
        
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
        cam.data.keyframe_insert("ortho_scale", frame=f)
        
        viz_points.append(loc)
        
    # Update Viz
    generate_viz_curve(cam, viz_points)
    
    # Smooth
    if cam.animation_data and cam.animation_data.action:
        for fc in cam.animation_data.action.fcurves:
            for kf in fc.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO_CLAMPED'
                kf.handle_right_type = 'AUTO_CLAMPED'
