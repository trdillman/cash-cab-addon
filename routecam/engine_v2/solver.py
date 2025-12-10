"""
RouteCam v2 Solver
==================
The "Brain" of the system.
Translates geometric data into a specific Camera Plan.
Implements 'Guided Drift' and 'Adaptive Up'.
"""

import math
from .core import Vector, CurveSample

class CameraPlan:
    def __init__(self, duration_frames):
        self.duration = duration_frames
        self.keyframes = [] # List of dicts {frame, pos, scale, rot_quat}
        self.clip_start = 0.1
        self.clip_end = 1000.0

class AnalyzeContext:
    def __init__(self, samples: list[CurveSample], total_length: float):
        self.samples = samples
        self.total_length = total_length
        self.bbox_center = Vector((0,0,0))
        self.bbox_diag = 0.0
        self._calculate_bbox()
        
    def _calculate_bbox(self):
        if not self.samples: return
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')
        
        for s in self.samples:
            p = s.position
            min_x, max_x = min(min_x, p.x), max(max_x, p.x)
            min_y, max_y = min(min_y, p.y), max(max_y, p.y)
            min_z, max_z = min(min_z, p.z), max(max_z, p.z)
            
        self.bbox_center = Vector(((min_x+max_x)/2, (min_y+max_y)/2, (min_z+max_z)/2))
        dx, dy, dz = max_x-min_x, max_y-min_y, max_z-min_z
        self.bbox_diag = math.sqrt(dx*dx + dy*dy + dz*dz)

    def get_rail_point(self, u):
        """
        Gets a point on the 'Camera Rail' (simplified route).
        For now, just linearly interpolates the samples.
        """
        if not self.samples: return Vector((0,0,0))
        
        # Binary search for sample
        # Since u is monotonic in samples, we can find it
        idx = 0
        count = len(self.samples)
        
        # Fast clamp
        if u <= 0.0: return self.samples[0].position
        if u >= 1.0: return self.samples[-1].position
        
        # Simple linear search (robust enough for 100 samples)
        # Could optimize with binary search later
        for i in range(count-1):
            if u >= self.samples[i].u and u <= self.samples[i+1].u:
                # Interpolate
                s0 = self.samples[i]
                s1 = self.samples[i+1]
                t = (u - s0.u) / (s1.u - s0.u) if (s1.u - s0.u) > 1e-6 else 0.0
                return s0.position.lerp(s1.position, t)
                
        return self.samples[-1].position

def solve_framing(context: AnalyzeContext, t: float, style_config: dict) -> tuple[Vector, float, Vector]:
    """
    Calculates (TargetPos, Scale, ViewVector) for a normalized time t [0.0 - 1.0].
    
    Implements:
    1. Guided Drift (Target blends from Center -> Rail)
    2. Adaptive Up (Orientation)
    """
    
    # --- 1. Style Constants ---
    MARGIN = style_config.get('margin', 1.9)
    ZOOM_RATIO = style_config.get('zoom_ratio', 0.06)
    ESTABLISH_U = style_config.get('establish_end', 0.2)
    
    # --- 2. Scale Logic ---
    # Start Scale = BBox Diag * Margin
    # End Scale = Start Scale * ZoomRatio
    start_scale = context.bbox_diag * MARGIN
    end_scale = start_scale * ZOOM_RATIO
    
    # Simple linear scale interpolation for now (Director will handle easing later)
    # Just need the geometric bounds
    scale = start_scale + (end_scale - start_scale) * t
    
    # --- 3. Guided Drift (Target Logic) ---
    # At t=0, Target is BBox Center
    # At t=1, Target is End Point
    # In between, we want to stay somewhat centered but drift towards the rail
    
    center_pos = context.bbox_center
    rail_pos = context.get_rail_point(t) # The point on the curve at time t
    end_pos = context.samples[-1].position
    
    # Weight Function: How much do we stick to the rail?
    # At t=0 (Establish), we want pure Center.
    # At t=1 (Chase), we want pure Rail (End Point).
    # t^2 curve gives a slow drift start
    rail_weight = t * t 
    
    # Blended Target
    # We blend between the static Center and the dynamic Rail Point
    target_pos = center_pos.lerp(rail_pos, rail_weight)
    
    # --- 4. View Vector (Orientation) ---
    # Global Interpolation Strategy
    
    # Style Config Params
    YAW_OFFSET = style_config.get('yaw_offset', math.radians(-75.0))
    PITCH_START = style_config.get('pitch_start', math.radians(30.0)) # Down positive? No, looking down is usually neg rotation in math, but UI shows pos angle.
    # In our math: vector * cos + ...
    # We assumed pitch down was -30.
    # If user passes +30, we should negate it for "Look Down" convention if that's what the math expects.
    # Let's assume user passes POSITIVE angle for "Down Pitch" (standard camera lang).
    # So we negate it here.
    PITCH_START_RAD = -abs(PITCH_START)
    
    PITCH_END = style_config.get('pitch_end', math.radians(15.0))
    PITCH_END_RAD = -abs(PITCH_END)
    
    # A. Establish Vector (t=0)
    # -------------------------
    p_start = context.samples[0].position
    p_end = context.samples[-1].position
    flow = (p_end - p_start).normalized()
    
    # Adaptive Up: If flow is vertical, use Y-Up
    world_up = Vector((0,0,1))
    if abs(flow.dot(Vector((0,0,1)))) > 0.9:
        world_up = Vector((0,1,0))
        
    # Calculate Right Vector relative to flow
    flow_right = flow.cross(world_up).normalized()
    
    # "Swept" Establish Angle
    # 1. Rotate Flow by YAW_OFFSET around Up
    cos_y = math.cos(YAW_OFFSET)
    sin_y = math.sin(YAW_OFFSET)
    yawed_flow = flow * cos_y + flow.cross(world_up) * sin_y
    
    # 2. Pitch down
    establish_right = yawed_flow.cross(world_up).normalized()
    cos_p = math.cos(PITCH_START_RAD)
    sin_p = math.sin(PITCH_START_RAD)
    
    v_establish = yawed_flow * cos_p + yawed_flow.cross(establish_right) * sin_p
    v_establish = v_establish.normalized()
    
    # B. Chase Vector (t=1)
    # ---------------------
    # Align with End Tangent
    # Pitch down PITCH_END
    t_end = context.samples[-1].tangent
    chase_right = t_end.cross(world_up).normalized()
    
    cos_c = math.cos(PITCH_END_RAD)
    sin_c = math.sin(PITCH_END_RAD)
    
    v_chase = t_end * cos_c + t_end.cross(chase_right) * sin_c
    v_chase = v_chase.normalized()
    
    # C. Interpolate (Global Slerp)
    # -----------------------------
    # Simple t interpolation for now. 
    view_vec = v_establish.lerp(v_chase, t).normalized()
    
    return target_pos, scale, view_vec

def solve_clipping(cam_pos: Vector, view_vec: Vector, context: AnalyzeContext) -> tuple[float, float]:
    """
    Computes optimal clip planes.
    Projects all points onto the View Vector to find min/max depth.
    """
    min_d, max_d = float('inf'), float('-inf')
    
    # We look ALONG view_vec.
    # Distance d = (P - CamPos) . ViewVec
    # Wait, ViewVec is usually "Direction Camera is Looking". 
    # So d should be positive if point is in front.
    
    # Optimization: Just check BBox corners? No, points are safer.
    # We can check strided samples for speed
    step = max(1, len(context.samples) // 20)
    for i in range(0, len(context.samples), step):
        p = context.samples[i].position
        d = (p - cam_pos).dot(view_vec)
        min_d = min(min_d, d)
        max_d = max(max_d, d)
        
    # Padding
    near = max(0.1, min_d * 0.5)
    far = max_d * 1.5
    
    return near, far
