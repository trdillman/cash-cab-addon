from __future__ import annotations

import math

import bpy
from mathutils import Matrix, Vector

from . import log
from .finders import find_collection

CANON_BUILDINGS = "ASSET_BUILDINGS"


def _euler_from_quat_continuous(prev_euler, quat):
    """Convert quaternion to Euler and unwrap to avoid 180/360 jumps."""
    e = quat.to_euler("XYZ")
    if prev_euler is None:
        return e
    for i in range(3):
        a = float(e[i])
        b = float(prev_euler[i])
        while a - b > math.pi:
            a -= 2.0 * math.pi
        while a - b < -math.pi:
            a += 2.0 * math.pi
        e[i] = a
    return e


def _deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def _rad(deg: float) -> float:
    return deg * math.pi / 180.0


def _world_loc_at_frame(obj: bpy.types.Object, frame: int, scene: bpy.types.Scene) -> Vector:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(frame)
    depsgraph.update()
    return obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()


def _forward_from_yaw_pitch(yaw_deg: float, pitch_deg: float) -> Vector:
    yaw = _rad(yaw_deg)
    pitch = _rad(pitch_deg)
    c = math.cos(pitch)
    return Vector((c * math.cos(yaw), c * math.sin(yaw), math.sin(pitch))).normalized()


def _rotation_from_forward_up(forward: Vector, up_ref: Vector) -> Matrix:
    """
    Build a 3x3 world rotation matrix for a Blender camera object where:
    - local -Z points along forward
    - local +Y is as close as possible to up_ref

    Uses Blender's track quaternion logic to avoid “upside-down” ambiguity.
    """
    f = forward.normalized()
    up_ref_n = up_ref.normalized()

    # Build a stable basis from forward + up_ref:
    # right = forward x up, up = right x forward
    right = f.cross(up_ref_n)
    if right.length < 1e-9:
        # Degenerate (forward parallel to up), pick an arbitrary up_ref.
        up_ref_n = Vector((0.0, 1.0, 0.0))
        right = f.cross(up_ref_n)
    right.normalize()
    up = right.cross(f).normalized()
    back = (-f).normalized()

    # Ensure "up" isn't flipped (prevents upside-down cameras).
    if up.dot(Vector((0.0, 0.0, 1.0))) < 0.0:
        right.negate()
        up.negate()

    # Columns are the local axes in world space (X, Y, Z).
    return Matrix((right, up, back)).transposed()


def _ortho_scale_to_fit_points(
    *,
    cam_matrix_world: Matrix,
    points_world: list[Vector],
    res_x: int,
    res_y: int,
    margin: float,
) -> float:
    """
    Blender orthographic camera:
    - ortho_scale defines view width (world units)
    - view height = ortho_scale * (res_y / res_x)
    Fit points such that all are inside with an extra margin multiplier.
    """
    if not points_world:
        return 10.0

    inv = cam_matrix_world.inverted()
    pts_cam = [inv @ p for p in points_world]
    max_abs_x = max(abs(p.x) for p in pts_cam)
    max_abs_y = max(abs(p.y) for p in pts_cam)
    aspect = float(res_x) / float(res_y) if res_y else 1.0
    width_needed = 2.0 * max(max_abs_x, max_abs_y * aspect)
    return max(0.001, float(width_needed * margin))


def _iter_bbox_world_points(obj: bpy.types.Object):
    # bound_box is 8 points in object local space.
    bb = getattr(obj, "bound_box", None)
    if not bb:
        return
    mw = obj.matrix_world
    for co in bb:
        yield mw @ Vector(co)


def _set_safe_clipping(
    *,
    cam_obj: bpy.types.Object,
    focus_points_world: list[Vector],
    extra_collection_name: str = CANON_BUILDINGS,
) -> None:
    """
    Ensure clip distances cover the scene scale.
    For ortho cameras, distance doesn't affect framing but it *does* affect clipping.
    """
    cam_data: bpy.types.Camera = cam_obj.data
    cam_loc = cam_obj.matrix_world.to_translation()

    far_points: list[Vector] = list(focus_points_world)
    buildings = find_collection(extra_collection_name)
    if buildings is not None:
        for o in buildings.all_objects:
            if o.type != "MESH":
                continue
            far_points.extend(list(_iter_bbox_world_points(o)))

    if far_points:
        max_d = max((p - cam_loc).length for p in far_points)
    else:
        max_d = 10000.0

    # Conservative defaults; keep near plane small and far plane large.
    cam_data.clip_start = 0.1
    cam_data.clip_end = max(10000.0, float(max_d * 2.0))


def spawn_start_camera_from_features(
    *,
    scene: bpy.types.Scene,
    camera_name: str,
    start_obj: bpy.types.Object,
    end_obj: bpy.types.Object,
    car_obj: bpy.types.Object,
    frame: int,
    pitch_deg: float,
    yaw_offset_deg: float,
    margin: float,
) -> bpy.types.Object:
    """
    Minimal “start camera” spawner:
    - target is midpoint of (start, car)
    - yaw is derived from car heading + yaw_offset_deg
    - pitch is explicit (style-driven)
    - roll is locked via world-up tracking (no user roll control yet)
    - ortho_scale fits start+car+end with margin
    """
    res_x = int(scene.render.resolution_x)
    res_y = int(scene.render.resolution_y)

    p_start = _world_loc_at_frame(start_obj, frame, scene)
    p_end = _world_loc_at_frame(end_obj, frame, scene)
    p_car = _world_loc_at_frame(car_obj, frame, scene)

    # Car heading from a small delta (fall back to world +X).
    p_car2 = _world_loc_at_frame(car_obj, frame + 5, scene)
    v = Vector((p_car2.x - p_car.x, p_car2.y - p_car.y, 0.0))
    if v.length < 1e-6:
        heading_yaw = 0.0
    else:
        heading_yaw = _deg(math.atan2(v.y, v.x))
    yaw_deg = heading_yaw + float(yaw_offset_deg)

    forward = _forward_from_yaw_pitch(yaw_deg=yaw_deg, pitch_deg=pitch_deg)
    up_ref = Vector((0.0, 0.0, 1.0))

    target = (p_start + p_car) * 0.5

    # Distance doesn't affect ortho framing; keep it reasonably away to avoid clip issues.
    distance = 2000.0
    cam_loc = target - forward * distance

    rot = _rotation_from_forward_up(forward, up_ref)

    if camera_name and camera_name in bpy.data.objects:
        cam_obj = bpy.data.objects[camera_name]
        if cam_obj.type != "CAMERA":
            raise RuntimeError(f"Object '{camera_name}' exists but is not a camera")
    else:
        cam_data = bpy.data.cameras.new(name=f"{camera_name or 'ROUTERIG_CAMERA'}_DATA")
        cam_obj = bpy.data.objects.new(camera_name or "ROUTERIG_CAMERA", cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_loc

    # For now: always lock orientation from the computed forward/up (no user roll control).
    cam_obj.rotation_mode = "XYZ"
    cam_obj.rotation_euler = _euler_from_quat_continuous(None, rot.to_quaternion())

    cam_obj.data.type = "ORTHO"

    # Fit start+car+end at the start frame.
    cam_mw = cam_obj.matrix_world.copy()
    cam_obj.data.ortho_scale = _ortho_scale_to_fit_points(
        cam_matrix_world=cam_mw,
        points_world=[p_start, p_car, p_end],
        res_x=res_x,
        res_y=res_y,
        margin=margin,
    )
    _set_safe_clipping(cam_obj=cam_obj, focus_points_world=[p_start, p_car, p_end])

    # Make it the active camera (so you can hit play immediately).
    scene.camera = cam_obj

    # REPORT: Generate a spawn report for the user.
    logger = log.get_logger()
    logger.info("--- Spawn Test Camera Report ---")
    logger.info(f"  Frame: {frame}")
    logger.info(f"  Features: Start='{start_obj.name}', Car='{car_obj.name}', End='{end_obj.name}'")
    logger.info(f"  Target: ({target.x:.2f}, {target.y:.2f}, {target.z:.2f})")
    logger.info(f"  Camera Loc: ({cam_loc.x:.2f}, {cam_loc.y:.2f}, {cam_loc.z:.2f})")
    logger.info(f"  Forward: ({forward.x:.2f}, {forward.y:.2f}, {forward.z:.2f})")
    logger.info(f"  Ortho Scale: {cam_obj.data.ortho_scale:.2f}")
    logger.info(f"  Clip: {cam_obj.data.clip_start:.2f} .. {cam_obj.data.clip_end:.2f}")
    logger.info(f"  Angles: Yaw={yaw_deg:.1f}°, Pitch={pitch_deg:.1f}°")
    logger.info("--------------------------------")

    return cam_obj
