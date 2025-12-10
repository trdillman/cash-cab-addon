"""
RouteCam v2 Core Math Library
=============================
Geometric primitives and curve analysis tools designed for robustness.
Acts as a shim for 'mathutils' when running outside Blender.
"""

import math
from collections import namedtuple

# -----------------------------------------------------------------------------
# 1. Vector Math Shim (Robustness Layer)
# -----------------------------------------------------------------------------
try:
    import mathutils
    Vector = mathutils.Vector
    Quaternion = mathutils.Quaternion
    Matrix = mathutils.Matrix
    IS_BLENDER = True
except ImportError:
    IS_BLENDER = False
    
    class Vector:
        __slots__ = ('x', 'y', 'z')
        def __init__(self, args):
            if isinstance(args, (tuple, list)):
                self.x, self.y, self.z = args
            else: # assume 3 args passed unwrapped (not standard for mathutils but good for internal)
                # actually mathutils.Vector takes a single tuple/list arg
                raise ValueError("Vector expects a tuple/list")
                
        def __repr__(self): return f"Vector(({self.x:.4f}, {self.y:.4f}, {self.z:.4f}))"
        def __add__(self, o): return Vector((self.x+o.x, self.y+o.y, self.z+o.z))
        def __sub__(self, o): return Vector((self.x-o.x, self.y-o.y, self.z-o.z))
        def __mul__(self, s): return Vector((self.x*s, self.y*s, self.z*s))
        def __truediv__(self, s): return Vector((self.x/s, self.y/s, self.z/s))
        def __neg__(self): return Vector((-self.x, -self.y, -self.z))
        
        def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
        def cross(self, o):
            return Vector((
                self.y*o.z - self.z*o.y,
                self.z*o.x - self.x*o.z,
                self.x*o.y - self.y*o.x
            ))
            
        @property
        def length(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        
        def normalized(self):
            l = self.length
            if l < 1e-8: return Vector((0,0,0))
            return self / l
            
        def lerp(self, other, t):
            return self + (other - self) * t
            
        def copy(self): return Vector((self.x, self.y, self.z))
        def to_tuple(self): return (self.x, self.y, self.z)

# -----------------------------------------------------------------------------
# 2. Data Structures
# -----------------------------------------------------------------------------

CurveSample = namedtuple('CurveSample', [
    'position',  # Vector
    'tangent',   # Vector (Normalized)
    'normal',    # Vector (Normalized, RMF)
    'binormal',  # Vector (Normalized, RMF)
    'curvature', # Float (Scalar metric)
    'arc_len',   # Float (Cumulative distance)
    'u'          # Float (0.0 to 1.0 normalized param)
])

# -----------------------------------------------------------------------------
# 3. Curve Analysis Algorithms
# -----------------------------------------------------------------------------

def calculate_cumulative_lengths(points):
    """Returns list of cumulative lengths and total length."""
    if not points: return [], 0.0
    dists = [0.0]
    total = 0.0
    for i in range(1, len(points)):
        d = (points[i] - points[i-1]).length
        total += d
        dists.append(total)
    return dists, total

def resample_curve(points, count):
    """Resample a list of Vectors to 'count' evenly spaced points."""
    if not points: return []
    if len(points) < 2: return [points[0].copy() for _ in range(count)]
    
    dists, total_len = calculate_cumulative_lengths(points)
    if total_len <= 0.00001: return [points[0].copy() for _ in range(count)]
    
    resampled = []
    step = total_len / (count - 1)
    
    # Simple linear interpolation resampling
    # (Could upgrade to Catmull-Rom later for smoothness)
    idx = 0
    for i in range(count):
        target_dist = i * step
        
        # Clamp (floating point safety)
        if target_dist >= total_len:
            resampled.append(points[-1].copy())
            continue
            
        # Advance index
        while idx < len(dists)-1 and dists[idx+1] < target_dist:
            idx += 1
            
        # Interpolate
        segment_len = dists[idx+1] - dists[idx]
        if segment_len < 1e-6:
            resampled.append(points[idx].copy())
        else:
            t = (target_dist - dists[idx]) / segment_len
            resampled.append(points[idx].lerp(points[idx+1], t))
            
    return resampled

def compute_rmf_frames(points):
    """
    Computes Rotation Minimizing Frames (RMF) / Parallel Transport Frames.
    Returns lists of (tangents, normals, binormals).
    Better than Frenet frames because they don't flip at inflection points.
    """
    count = len(points)
    if count < 2: return [], [], []
    
    tangents = []
    normals = []
    binormals = []
    
    # 1. Compute Tangents (Central Differences)
    for i in range(count):
        if i == 0:
            t = (points[1] - points[0]).normalized()
        elif i == count - 1:
            t = (points[-1] - points[-2]).normalized()
        else:
            # Catmull-Rom tangent direction
            t = (points[i+1] - points[i-1]).normalized()
        tangents.append(t)
        
    # 2. Initial Frame (Arbitrary, using World Up logic)
    # Just need a stable starting Normal perpendicular to T[0]
    t0 = tangents[0]
    world_up = Vector((0,0,1))
    if abs(t0.dot(world_up)) > 0.9: # If going straight up
        world_up = Vector((0,1,0))
        
    n0 = t0.cross(world_up).normalized()
    b0 = t0.cross(n0).normalized()
    
    normals.append(n0)
    binormals.append(b0)
    
    # 3. Propagate Frames (Projection Method)
    # Project previous normal onto plane defined by current tangent
    for i in range(1, count):
        t_prev = tangents[i-1]
        t_curr = tangents[i]
        n_prev = normals[i-1]
        
        # Mirror reflection method (Double Reflection) is more accurate for sharp turns,
        # but Projection is simpler: N_curr = N_prev - (N_prev . T_curr) * T_curr
        
        vec_n = n_prev - t_curr * n_prev.dot(t_curr)
        
        if vec_n.length < 1e-6:
            # Fallback if N_prev is parallel to T_curr (very sharp 90 deg turn)
            # Use previous frame as is
            n_curr = n_prev
        else:
            n_curr = vec_n.normalized()
            
        b_curr = t_curr.cross(n_curr).normalized()
        
        normals.append(n_curr)
        binormals.append(b_curr)
        
    return tangents, normals, binormals

def compute_curvature(points):
    """
    Estimates curvature scalar (k) at each point.
    k = 2 * sin(angle) / chord_length  (approx)
    """
    count = len(points)
    curvature = [0.0] * count
    
    for i in range(1, count-1):
        p_prev = points[i-1]
        p_curr = points[i]
        p_next = points[i+1]
        
        v1 = p_curr - p_prev
        v2 = p_next - p_curr
        
        # Menger curvature or Angle change
        # Simple Angle change per unit length
        l1 = v1.length
        l2 = v2.length
        
        if l1 < 1e-6 or l2 < 1e-6:
            continue
            
        v1 = v1 / l1
        v2 = v2 / l2
        
        dot = max(-1.0, min(1.0, v1.dot(v2)))
        angle = math.acos(dot)
        
        # Curvature k = d_theta / d_s
        # Average segment length
        ds = (l1 + l2) / 2.0
        if ds > 0:
            curvature[i] = angle / ds
            
    return curvature

def sample_curve_with_metrics(points, count=100):
    """
    Primary API: Takes raw points, returns list of full CurveSample objects.
    Performs resampling, RMF frame generation, and curvature analysis.
    """
    # 1. Resample
    resampled_pts = resample_curve(points, count)
    dists, total_len = calculate_cumulative_lengths(resampled_pts)
    
    # 2. Frames
    tangents, normals, binormals = compute_rmf_frames(resampled_pts)
    
    # 3. Curvature
    curvatures = compute_curvature(resampled_pts)
    
    # 4. Pack
    samples = []
    for i in range(count):
        u = dists[i] / total_len if total_len > 0 else 0.0
        samples.append(CurveSample(
            position=resampled_pts[i],
            tangent=tangents[i],
            normal=normals[i],
            binormal=binormals[i],
            curvature=curvatures[i],
            arc_len=dists[i],
            u=u
        ))
        
    return samples, total_len
