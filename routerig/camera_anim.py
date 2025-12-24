from __future__ import annotations

import math
from dataclasses import dataclass

import bmesh
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import log
from .camera_spawn import _ortho_scale_to_fit_points, _rotation_from_forward_up, _set_safe_clipping
from .finders import find_collection
from .style_profile import Keyframe1D, eval_keys


@dataclass
class CameraState:
    frame: int
    location: Vector
    rotation_quaternion: Quaternion
    ortho_scale: float
    focus_points_world: list[Vector]


def _deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def _rad(deg: float) -> float:
    return deg * math.pi / 180.0


def _forward_from_yaw_pitch(yaw_deg: float, pitch_deg: float) -> Vector:
    yaw = _rad(yaw_deg)
    pitch = _rad(pitch_deg)
    c = math.cos(pitch)
    return Vector((c * math.cos(yaw), c * math.sin(yaw), math.sin(pitch))).normalized()


def _ensure_quat_continuity(prev: Quaternion | None, curr: Quaternion) -> Quaternion:
    if prev is None:
        return curr
    if prev.dot(curr) < 0.0:
        return -curr
    return curr


def _ensure_euler_continuity(prev: Euler | None, curr: Euler) -> Euler:
    """Unwrap Euler angles to avoid 180/360 jumps between successive keys."""
    if prev is None:
        return curr
    out = curr.copy()
    for i in range(3):
        a = float(out[i])
        b = float(prev[i])
        while a - b > math.pi:
            a -= 2.0 * math.pi
        while a - b < -math.pi:
            a += 2.0 * math.pi
        out[i] = a
    return out


def _clear_routerig_camera_animation(cam_obj: bpy.types.Object) -> None:
    """Remove prior RouteRig fcurves so reruns don't leave quaternion curves behind."""
    actions: list[bpy.types.Action] = []
    if cam_obj.animation_data and cam_obj.animation_data.action:
        actions.append(cam_obj.animation_data.action)
    if cam_obj.data and cam_obj.data.animation_data and cam_obj.data.animation_data.action:
        actions.append(cam_obj.data.animation_data.action)

    for action in actions:
        for fc in list(action.fcurves):
            dp = str(getattr(fc, "data_path", "") or "")
            if dp in ("location", "rotation_quaternion", "rotation_euler") or dp.endswith("ortho_scale"):
                try:
                    action.fcurves.remove(fc)
                except Exception:
                    pass


def _heading_yaw_deg(car_pos: Vector, car_pos2: Vector) -> float:
    v = Vector((car_pos2.x - car_pos.x, car_pos2.y - car_pos.y, 0.0))
    if v.length < 1e-6:
        return 0.0
    return _deg(math.atan2(v.y, v.x))


def _keys_from_profile_pitch(profile: dict) -> list[Keyframe1D]:
    keys = []
    for k in profile.get("angle", {}).get("pitch_keys_deg", []):
        keys.append(Keyframe1D(frame=int(k["frame"]), value=float(k["pitch"])))
    keys.sort(key=lambda x: x.frame)
    return keys


def _keys_from_profile_heading_weight(profile: dict) -> list[Keyframe1D]:
    keys = []
    for k in profile.get("angle", {}).get("yaw_model", {}).get("heading_weight_keys", []):
        keys.append(Keyframe1D(frame=int(k["frame"]), value=float(k["w_heading"])))
    keys.sort(key=lambda x: x.frame)
    return keys


def _keys_from_profile_target_weights(profile: dict) -> list[dict]:
    keys = profile.get("composition", {}).get("target_weights_keys", [])
    return sorted(
        [{"frame": int(k["frame"]), "start": float(k["start"]), "car": float(k["car"]), "end": float(k["end"])} for k in keys],
        key=lambda x: x["frame"],
    )


def _keys_from_profile_distance(profile: dict) -> list[Keyframe1D]:
    keys = []
    for k in profile.get("camera", {}).get("distance_keys", []):
        keys.append(Keyframe1D(frame=int(k["frame"]), value=float(k["distance"])))
    keys.sort(key=lambda x: x.frame)
    return keys


def _keys_from_profile_yaw_offset(profile: dict) -> list[Keyframe1D]:
    keys = []
    for k in profile.get("angle", {}).get("yaw_model", {}).get("offset_keys", []):
        keys.append(Keyframe1D(frame=int(k["frame"]), value=float(k["offset"])))
    keys.sort(key=lambda x: x.frame)
    return keys


def _keys_from_profile_yaw_base(profile: dict) -> list[dict]:
    keys = profile.get("angle", {}).get("yaw_model", {}).get("base_keys", [])
    return sorted([{"frame": int(k["frame"]), "base": str(k["base"])} for k in keys], key=lambda x: x["frame"])


def _eval_yaw_base(keys: list[dict], frame: int) -> str:
    if not keys:
        return "car_heading"
    # Step function: pick the last base <= frame.
    best = keys[0]["base"]
    for k in keys:
        if k["frame"] <= frame:
            best = k["base"]
        else:
            break
    return best


def _keys_from_profile_fit_anchors(profile: dict) -> list[dict]:
    keys = profile.get("ortho", {}).get("fit_anchors_keys", [])
    return sorted(
        [
            {
                "frame": int(k["frame"]),
                "start": bool(k.get("start", True)),
                "car": bool(k.get("car", True)),
                "end": bool(k.get("end", True)),
            }
            for k in keys
        ],
        key=lambda x: x["frame"],
    )


def _eval_fit_anchors(keys: list[dict], frame: int) -> tuple[bool, bool, bool]:
    if not keys:
        return True, True, True
    best = keys[0]
    for k in keys:
        if k["frame"] <= frame:
            best = k
        else:
            break
    return bool(best["start"]), bool(best["car"]), bool(best["end"])


def _keys_from_profile_route_window(profile: dict) -> list[dict]:
    keys = profile.get("ortho", {}).get("route_window_keys", [])
    return sorted(
        [{"frame": int(k["frame"]), "u0": float(k.get("u0", 0.0)), "u1": float(k.get("u1", 1.0))} for k in keys],
        key=lambda x: x["frame"],
    )


def _eval_route_window(keys: list[dict], frame: int) -> tuple[float, float]:
    if not keys:
        return 0.0, 1.0
    best = keys[0]
    for k in keys:
        if k["frame"] <= frame:
            best = k
        else:
            break
    u0 = max(0.0, min(1.0, float(best["u0"])))
    u1 = max(0.0, min(1.0, float(best["u1"])))
    if u1 < u0:
        u0, u1 = u1, u0
    return u0, u1


def _eval_target_weights(keys: list[dict], frame: int) -> tuple[float, float, float]:
    if not keys:
        return 0.0, 1.0, 0.0
    if frame <= keys[0]["frame"]:
        k = keys[0]
        return k["start"], k["car"], k["end"]
    if frame >= keys[-1]["frame"]:
        k = keys[-1]
        return k["start"], k["car"], k["end"]
    for a, b in zip(keys, keys[1:]):
        if a["frame"] <= frame <= b["frame"]:
            t = (frame - a["frame"]) / float(b["frame"] - a["frame"])
            return (
                a["start"] + (b["start"] - a["start"]) * t,
                a["car"] + (b["car"] - a["car"]) * t,
                a["end"] + (b["end"] - a["end"]) * t,
            )
    k = keys[-1]
    return k["start"], k["car"], k["end"]


def _ensure_camera(scene: bpy.types.Scene, name: str) -> bpy.types.Object:
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
        if cam_obj.type != "CAMERA":
            raise RuntimeError(f"Object '{name}' exists but is not a camera")
        return cam_obj
    cam_data = bpy.data.cameras.new(name=f"{name}_DATA")
    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)
    return cam_obj


def _find_kp_by_frame(fc: bpy.types.FCurve, frame: int) -> bpy.types.KeyframePoint | None:
    best: bpy.types.KeyframePoint | None = None
    best_dx = 1e9
    for kp in fc.keyframe_points:
        dx = abs(float(kp.co.x) - float(frame))
        if dx < best_dx:
            best_dx = dx
            best = kp
    if best is None or best_dx > 0.25:
        return None
    return best


def _iter_bbox_world_points(obj: bpy.types.Object):
    bb = getattr(obj, "bound_box", None)
    if not bb:
        return
    mw = obj.matrix_world
    for co in bb:
        yield mw @ Vector(co)


def _bbox_extents_in_camera_space(
    *,
    cam_mw_inv: Matrix,
    points_world: list[Vector],
) -> tuple[float, float]:
    if not points_world:
        return 0.0, 0.0
    pts_cam = [cam_mw_inv @ p for p in points_world]
    min_x = min(float(p.x) for p in pts_cam)
    max_x = max(float(p.x) for p in pts_cam)
    min_y = min(float(p.y) for p in pts_cam)
    max_y = max(float(p.y) for p in pts_cam)
    return max(0.0, max_x - min_x), max(0.0, max_y - min_y)


def _camera_view_height(ortho_scale: float, res_x: int, res_y: int) -> float:
    if not res_x:
        return float(ortho_scale)
    return float(ortho_scale) * (float(res_y) / float(res_x))


def _ortho_scale_for_bbox_fraction(
    *,
    bbox_w_cam: float,
    bbox_h_cam: float,
    res_x: int,
    res_y: int,
    target_frac: float,
    extra_margin: float,
) -> float:
    """
    Pick an ortho_scale such that the bbox occupies ~target_frac of the view width/height.

    In ortho cameras:
      view_width  = ortho_scale
      view_height = ortho_scale * (res_y / res_x)
    """
    frac = max(1e-4, min(0.95, float(target_frac)))
    need_w = float(bbox_w_cam) / frac if bbox_w_cam > 0.0 else 0.0
    view_h = _camera_view_height(1.0, res_x, res_y)
    # view_h is (res_y/res_x) when ortho_scale=1.0, so:
    # bbox_h_cam <= frac * ortho_scale * (res_y/res_x)
    # ortho_scale >= bbox_h_cam / (frac * (res_y/res_x))
    need_h = float(bbox_h_cam) / (frac * max(1e-6, view_h)) if bbox_h_cam > 0.0 else 0.0
    need = max(need_w, need_h, 0.001)
    return max(0.001, float(need) * max(1.0, float(extra_margin)))


def _resolve_car_mesh_object(car_obj: bpy.types.Object) -> bpy.types.Object:
    """
    Prefer ASSET_CAR for framing (has real bounds). Fall back to provided car_obj.
    """
    asset_car = bpy.data.objects.get("ASSET_CAR")
    if asset_car is not None:
        return asset_car
    return car_obj


def _build_world_bvh(buildings_col: bpy.types.Collection, depsgraph: bpy.types.Depsgraph) -> BVHTree | None:
    bm = bmesh.new()
    added = False
    for o in buildings_col.all_objects:
        if o.type != "MESH":
            continue
        oe = o.evaluated_get(depsgraph)
        me = oe.to_mesh()
        me.transform(oe.matrix_world)
        bm.from_mesh(me)
        oe.to_mesh_clear()
        added = True

    if not added:
        bm.free()
        return None

    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    return bvh


def _min_clearance_to_bvh(p: Vector, bvh: BVHTree | None) -> float:
    if bvh is None:
        return 1e9
    loc, normal, index, dist = bvh.find_nearest(p)
    if loc is None:
        return 1e9
    return float(dist)


def _push_out_from_buildings(
    *,
    cam_loc: Vector,
    forward: Vector,
    cam_rot: Matrix,
    ortho_scale: float,
    bvh: BVHTree | None,
    profile: dict,
) -> tuple[Vector, float]:
    cfg = profile.get("collision", {}) if isinstance(profile, dict) else {}
    radius = float(cfg.get("camera_clearance_radius", 2.0))
    max_iter = int(cfg.get("max_push_iterations", 30))
    step = float(cfg.get("push_step", 1.0))
    push_order = cfg.get("push_order", ["+Z", "-V", "+RIGHT", "-RIGHT", "+UP", "-UP"])
    expand = float(profile.get("ortho", {}).get("scale_expand_on_collision", 1.05))

    if bvh is None or radius <= 0.0 or max_iter <= 0 or step <= 0.0:
        return cam_loc, ortho_scale

    right = cam_rot.col[0].to_3d().normalized()
    up = cam_rot.col[1].to_3d().normalized()

    def dir_from_token(tok: str) -> Vector | None:
        t = str(tok).strip().upper()
        if t == "+Z":
            return Vector((0.0, 0.0, 1.0))
        if t == "-Z":
            return Vector((0.0, 0.0, -1.0))
        if t == "+V":
            return forward.normalized()
        if t == "-V":
            return (-forward).normalized()
        if t == "+RIGHT":
            return right
        if t == "-RIGHT":
            return (-right)
        if t == "+UP":
            return up
        if t == "-UP":
            return (-up)
        return None

    pushed = False
    for _ in range(max_iter):
        if _min_clearance_to_bvh(cam_loc, bvh) >= radius:
            break
        for tok in push_order:
            d = dir_from_token(tok)
            if d is None:
                continue
            cam_loc = cam_loc + d * step
            pushed = True
            if _min_clearance_to_bvh(cam_loc, bvh) >= radius:
                break

    if _min_clearance_to_bvh(cam_loc, bvh) < radius:
        raise RuntimeError("Collision avoidance failed: could not clear ASSET_BUILDINGS within limits")

    if pushed and expand > 0.0 and abs(expand - 1.0) > 1e-9:
        ortho_scale = float(ortho_scale) * expand
    return cam_loc, ortho_scale


def _apply_generic_curve_profile_to_fcurve(*, fc: bpy.types.FCurve, curve_keys: list[dict]) -> None:
    frames = [int(k["frame"]) for k in curve_keys]
    by_frame = {int(k["frame"]): k for k in curve_keys}

    kp_by_frame: dict[int, bpy.types.KeyframePoint] = {}
    for f in frames:
        kp = _find_kp_by_frame(fc, f)
        if kp is None:
            return
        kp_by_frame[f] = kp

    # First: set interpolation and unlock handles so coordinates stick.
    for f in frames:
        kp = kp_by_frame[f]
        k = by_frame[f]
        interp = k.get("interpolation")
        if isinstance(interp, str) and interp:
            kp.interpolation = interp
        kp.handle_left_type = "FREE"
        kp.handle_right_type = "FREE"

    # Second: set handle coordinates using normalized ratios from the template curve.
    for idx, f in enumerate(frames):
        kp = kp_by_frame[f]
        k = by_frame[f]

        if idx > 0 and isinstance(k.get("left"), dict):
            prev_f = frames[idx - 1]
            prev = kp_by_frame[prev_f]
            dt = float(kp.co.x - prev.co.x)
            if abs(dt) > 1e-9:
                lx = float(k["left"].get("x_ratio", 0.5))
                kp.handle_left.x = float(prev.co.x) + lx * dt
                dy = float(kp.co.y - prev.co.y)
                ly = k["left"].get("y_ratio")
                if ly is None or abs(dy) < 1e-9:
                    kp.handle_left.y = float(kp.co.y)
                else:
                    kp.handle_left.y = float(prev.co.y) + float(ly) * dy

        if idx + 1 < len(frames) and isinstance(k.get("right"), dict):
            next_f = frames[idx + 1]
            nxt = kp_by_frame[next_f]
            dt = float(nxt.co.x - kp.co.x)
            if abs(dt) > 1e-9:
                rx = float(k["right"].get("x_ratio", 0.5))
                kp.handle_right.x = float(kp.co.x) + rx * dt
                dy = float(nxt.co.y - kp.co.y)
                ry = k["right"].get("y_ratio")
                if ry is None or abs(dy) < 1e-9:
                    kp.handle_right.y = float(kp.co.y)
                else:
                    kp.handle_right.y = float(kp.co.y) + float(ry) * dy


def _apply_curve_profile_to_camera(*, cam_obj: bpy.types.Object, profile: dict) -> None:
    curve_profile = profile.get("timeline", {}).get("curve_profile")
    if not isinstance(curve_profile, dict):
        return
    if str(curve_profile.get("mode", "")) != "generic_keyframe_ratios_v1":
        return
    curve_keys = curve_profile.get("keys")
    if not isinstance(curve_keys, list) or not curve_keys:
        return

    if cam_obj.animation_data and cam_obj.animation_data.action:
        for fc in cam_obj.animation_data.action.fcurves:
            _apply_generic_curve_profile_to_fcurve(fc=fc, curve_keys=curve_keys)

    if cam_obj.data.animation_data and cam_obj.data.animation_data.action:
        for fc in cam_obj.data.animation_data.action.fcurves:
            _apply_generic_curve_profile_to_fcurve(fc=fc, curve_keys=curve_keys)


def _force_linear_rotation_euler(*, cam_obj: bpy.types.Object) -> None:
    """Prevent Euler Bezier overshoot that can manifest as apparent spins."""
    ad = getattr(cam_obj, "animation_data", None)
    action = getattr(ad, "action", None) if ad else None
    if not action:
        return
    for fc in getattr(action, "fcurves", []) or []:
        if str(getattr(fc, "data_path", "") or "") != "rotation_euler":
            continue
        for kp in getattr(fc, "keyframe_points", []) or []:
            try:
                kp.interpolation = "LINEAR"
                kp.handle_left_type = "VECTOR"
                kp.handle_right_type = "VECTOR"
            except Exception:
                pass


def _enforce_hold_last(*, cam_obj: bpy.types.Object, frame_hold: int) -> None:
    actions: list[bpy.types.Action] = []
    if cam_obj.animation_data and cam_obj.animation_data.action:
        actions.append(cam_obj.animation_data.action)
    if cam_obj.data.animation_data and cam_obj.data.animation_data.action:
        actions.append(cam_obj.data.animation_data.action)
    for action in actions:
        for fc in action.fcurves:
            kp = _find_kp_by_frame(fc, int(frame_hold))
            if kp is not None:
                kp.interpolation = "CONSTANT"


def _apply_screen_offset_for_point(
    *,
    cam_loc: Vector,
    cam_rot: Matrix,
    ortho_scale: float,
    res_x: int,
    res_y: int,
    point_world: Vector,
    desired_nx: float,
    desired_ny: float,
) -> Vector:
    """
    Adjust camera location in its plane so that point_world appears at desired normalized coordinates.
    """
    width = ortho_scale
    height = ortho_scale * (float(res_y) / float(res_x)) if res_x else ortho_scale
    desired_x = desired_nx * (width * 0.5)
    desired_y = desired_ny * (height * 0.5)

    cam_mw = Matrix.Translation(cam_loc) @ cam_rot.to_4x4()
    inv = cam_mw.inverted()
    p_cam = inv @ point_world

    # right/up world from rotation matrix columns (local X/Y)
    right = cam_rot.col[0].to_3d().normalized()
    up = cam_rot.col[1].to_3d().normalized()
    dx = p_cam.x - desired_x
    dy = p_cam.y - desired_y
    return cam_loc + right * dx + up * dy


def _eval_screen_anchor(profile: dict, anchor: str, frame: int) -> tuple[float, float]:
    keys = profile.get("composition", {}).get("desired_screen_keys", {}).get(anchor, [])
    if not keys:
        return 0.0, 0.0
    nx_keys = [Keyframe1D(int(k["frame"]), float(k["nx"])) for k in keys]
    ny_keys = [Keyframe1D(int(k["frame"]), float(k["ny"])) for k in keys]
    nx_keys.sort(key=lambda x: x.frame)
    ny_keys.sort(key=lambda x: x.frame)
    return float(eval_keys(nx_keys, frame)), float(eval_keys(ny_keys, frame))


def _screen_coords_for_point(
    *, cam_loc: Vector, cam_rot: Matrix, ortho_scale: float, res_x: int, res_y: int, point_world: Vector
) -> tuple[float, float]:
    width = float(ortho_scale)
    height = float(ortho_scale) * (float(res_y) / float(res_x)) if res_x else float(ortho_scale)
    cam_mw = Matrix.Translation(cam_loc) @ cam_rot.to_4x4()
    inv = cam_mw.inverted()
    p_cam = inv @ point_world
    nx = float(p_cam.x / (width * 0.5)) if width > 1e-9 else 0.0
    ny = float(p_cam.y / (height * 0.5)) if height > 1e-9 else 0.0
    return nx, ny


def _solve_yaw_for_composition(
    *,
    yaw_guess_deg: float,
    pitch_deg: float,
    distance: float,
    target: Vector,
    margin: float,
    res_x: int,
    res_y: int,
    car: Vector,
    end: Vector,
    start: Vector,
    match_start: bool,
    desired_car: tuple[float, float],
    desired_end: tuple[float, float],
    desired_start: tuple[float, float],
    desired_dir_deg: float,
    fit_points_factory,
) -> float:
    """
    Pick a yaw that places anchors similarly to the learned profile.
    We always place the car via plane-offset; the yaw is chosen to best place end (+ optionally start).
    """

    def score(yaw_deg: float) -> float:
        forward = _forward_from_yaw_pitch(yaw_deg=yaw_deg, pitch_deg=pitch_deg)
        rot = _rotation_from_forward_up(forward, Vector((0.0, 0.0, 1.0)))
        cam_loc = target - forward * float(distance)
        fit_points = fit_points_factory(rot, cam_loc)
        cam_mw = Matrix.Translation(cam_loc) @ rot.to_4x4()
        ortho = _ortho_scale_to_fit_points(
            cam_matrix_world=cam_mw, points_world=fit_points, res_x=res_x, res_y=res_y, margin=float(margin)
        )
        # Apply the same car placement we use for the final camera.
        cam_loc = _apply_screen_offset_for_point(
            cam_loc=cam_loc,
            cam_rot=rot,
            ortho_scale=ortho,
            res_x=res_x,
            res_y=res_y,
            point_world=car,
            desired_nx=desired_car[0],
            desired_ny=desired_car[1],
        )
        nx_end, ny_end = _screen_coords_for_point(cam_loc=cam_loc, cam_rot=rot, ortho_scale=ortho, res_x=res_x, res_y=res_y, point_world=end)
        err = (nx_end - desired_end[0]) ** 2 + (ny_end - desired_end[1]) ** 2
        if match_start:
            nx_s, ny_s = _screen_coords_for_point(
                cam_loc=cam_loc, cam_rot=rot, ortho_scale=ortho, res_x=res_x, res_y=res_y, point_world=start
            )
            err += (nx_s - desired_start[0]) ** 2 + (ny_s - desired_start[1]) ** 2

        # Route direction preference (car->end) to avoid 180° ambiguities.
        cam_mw2 = Matrix.Translation(cam_loc) @ rot.to_4x4()
        inv2 = cam_mw2.inverted()
        car_cam = inv2 @ car
        end_cam = inv2 @ end
        dvx = float(end_cam.x - car_cam.x)
        dvy = float(end_cam.y - car_cam.y)
        if abs(dvx) > 1e-6 or abs(dvy) > 1e-6:
            ang = _deg(math.atan2(dvy, dvx))
            dang = (ang - float(desired_dir_deg) + 180.0) % 360.0 - 180.0
            err += 0.15 * (dang / 180.0) ** 2

        # Gentle regularization to stay near the guess.
        d = (yaw_deg - yaw_guess_deg + 180.0) % 360.0 - 180.0
        err += 0.01 * (d / 180.0) ** 2
        return float(err)

    # Coarse search around the guess, then refine.
    best_yaw = float(yaw_guess_deg)
    best_s = score(best_yaw)
    for step, span in ((12.0, 180.0), (3.0, 24.0), (1.0, 6.0)):
        y0 = best_yaw
        for i in range(int((2 * span) / step) + 1):
            y = y0 - span + i * step
            s = score(y)
            if s < best_s:
                best_s = s
                best_yaw = y
    # Normalize to [-180, 180] like our yaw reporting.
    best_yaw = (best_yaw + 180.0) % 360.0 - 180.0
    return float(best_yaw)


def _route_world_points(route_obj: bpy.types.Object, depsgraph: bpy.types.Depsgraph) -> list[Vector]:
    """
    Return a downsampled list of world-space points along the ROUTE curve.
    Uses spline control points (fast, stable) and tolerates non-curve objects.
    """
    route_eval = route_obj.evaluated_get(depsgraph)
    if route_eval.type != "CURVE":
        # Fallback: for meshes/empties, use the bounding box points.
        bb = getattr(route_eval, "bound_box", None)
        if not bb:
            return []
        mw = route_eval.matrix_world
        return [mw @ Vector(co) for co in bb]

    curve = route_eval.data
    mw = route_eval.matrix_world
    pts: list[Vector] = []
    for spline in curve.splines:
        if spline.type == "BEZIER":
            for bp in spline.bezier_points:
                pts.append(mw @ bp.co)
        else:
            for p in spline.points:
                pts.append(mw @ Vector((p.co.x, p.co.y, p.co.z)))

    # Downsample aggressively if needed.
    if len(pts) > 400:
        step = max(1, int(len(pts) / 400))
        pts = pts[::step]
    return pts


def _route_window_points(*, route_pts: list[Vector], start: Vector, end: Vector, u0: float, u1: float) -> list[Vector]:
    if not route_pts:
        return []
    d = Vector((end.x - start.x, end.y - start.y, 0.0))
    if d.length < 1e-6:
        return route_pts
    d.normalize()
    svals = []
    for p in route_pts:
        v = Vector((p.x - start.x, p.y - start.y, 0.0))
        svals.append(v.dot(d))
    smin = min(svals)
    smax = max(svals)
    if abs(smax - smin) < 1e-9:
        return route_pts

    out: list[Vector] = []
    for p, s in zip(route_pts, svals):
        u = (s - smin) / (smax - smin)
        if u0 <= u <= u1:
            out.append(p)
    return out if out else route_pts


def _filter_camera_path(states: list[CameraState], profile: dict, keyframes: list[int] | None = None) -> list[CameraState]:
    # Determine the final active end frame from the profile.
    timeline = profile.get("timeline", {}) if isinstance(profile, dict) else {}
    frame_total = int(timeline.get("frame_total", 160))

    filtered_states: list[CameraState] = []
    state_map = {s.frame: s for s in states}

    # Iterate through the expected keyframes (prefer explicit list passed in).
    expected_keyframes = keyframes if keyframes else profile.get("timeline", {}).get("keyframes", [])
    expected_keyframes = sorted(list(set(int(k) for k in expected_keyframes)))

    for f in expected_keyframes:
        if f > frame_total: # Remove frames beyond the new total
            continue

        current_state = state_map.get(f)

        if current_state: # This keyframe was calculated, use it.
            filtered_states.append(current_state)
        else: # This keyframe was removed (e.g., frame 131), interpolate it.
            # Find the nearest surrounding keyframes that *do* exist.
            prev_kfs = [s.frame for s in filtered_states if s.frame < f]
            next_kfs = [s_f for s_f in expected_keyframes if s_f > f and s_f in state_map]

            if prev_kfs and next_kfs:
                prev_frame = max(prev_kfs)
                next_frame = min(next_kfs)
                
                prev_state = state_map[prev_frame]
                next_state = state_map[next_frame]

                # Linear interpolation for location, slerp for rotation, linear for scale.
                t = (f - prev_frame) / (next_frame - prev_frame)
                interp_loc = prev_state.location.lerp(next_state.location, t)
                interp_rot = prev_state.rotation_quaternion.slerp(next_state.rotation_quaternion, t)
                interp_scale = (1 - t) * prev_state.ortho_scale + t * next_state.ortho_scale

                interpolated_state = CameraState(
                    frame=f,
                    location=interp_loc,
                    rotation_quaternion=interp_rot,
                    ortho_scale=interp_scale,
                    focus_points_world=[] # Not interpolating these for now, may need more thought
                )
                filtered_states.append(interpolated_state)
            else: # Should not happen if expected_keyframes is well-formed, but just in case.
                log.get_logger().warning(f"Could not interpolate frame {f}, adding raw state if available.")
                if state_map.get(f):
                    filtered_states.append(state_map[f])

    # Ensure the states are sorted by frame after interpolation
    filtered_states.sort(key=lambda s: s.frame)

    # Re-apply continuity to interpolated quaternions
    final_smoothed_states: list[CameraState] = []
    prev_quat_smoothed: Quaternion | None = None
    for state in filtered_states:
        q_curr_smoothed = _ensure_quat_continuity(prev_quat_smoothed, state.rotation_quaternion)
        final_smoothed_states.append(CameraState(
            frame=state.frame,
            location=state.location,
            rotation_quaternion=q_curr_smoothed,
            ortho_scale=state.ortho_scale,
            focus_points_world=state.focus_points_world # Keep original focus points
        ))
        prev_quat_smoothed = q_curr_smoothed

    return final_smoothed_states


def _resolve_camera_active_end(*, scene: bpy.types.Scene, profile: dict) -> int:
    """Prefer scene animation vars over template defaults so camera timing matches car animation."""
    try:
        v = int(getattr(scene, "blosm_anim_end", 0) or 0)
        if v > 0:
            return v
    except Exception:
        pass

    timeline = profile.get("timeline", {}) if isinstance(profile, dict) else {}
    try:
        v = int(timeline.get("frame_active_end", 0) or 0)
        if v > 0:
            return v
    except Exception:
        pass

    try:
        return int(scene.frame_end)
    except Exception:
        return 160


def _effective_keyframes(
    *,
    scene: bpy.types.Scene,
    profile: dict,
    keyframes_override: list[int] | None,
    active_end: int,
) -> list[int]:
    """
    Choose the camera animation keys used for calculation + keyframe insertion.

    Goals:
    - Align the last key to the *actual* car animation end (blosm_anim_end).
    - Avoid harsh/abrupt motion; fewer late keys when not needed.
    - Remove problematic mid/late key (frame ~120) that can cause Z-corrections.
    """
    timeline = profile.get("timeline", {}) if isinstance(profile, dict) else {}
    ks_in = (
        list(keyframes_override)
        if keyframes_override
        else list(timeline.get("keyframes", []) or [])
    )

    if not ks_in:
        # Derive from standard 1/47/79 ratios mapped to active_end
        r1 = 47.0 / 150.0
        r2 = 79.0 / 150.0
        k1 = max(2, int(round(active_end * r1)))
        k2 = max(k1 + 1, int(round(active_end * r2)))
        ks_in = [1, k1, k2, active_end]

    ks = [int(k) for k in ks_in if int(k) >= 1]
    ks = [k for k in ks if k <= max(active_end, 1)]
    if not ks:
        ks = [1]
    if ks[-1] != active_end:
        ks.append(active_end)

    # Drop the mid/late key that creates abrupt rotation (commonly 120).
    if len(ks) >= 4 and 120 in ks:
        ks = [k for k in ks if k != 120]
        if ks[-1] != active_end:
            ks.append(active_end)

    ks = sorted(set(ks))
    if len(ks) == 1:
        ks.append(max(ks[0] + 1, active_end))
    return ks


def _apply_bezier_auto_handles(*, cam_obj: bpy.types.Object, active_end: int, buffer_mode: str) -> None:
    """Smooth motion while reducing overshoot and preserving hold_last."""

    def _tune_action(action: bpy.types.Action) -> None:
        for fc in getattr(action, "fcurves", []) or []:
            dp = str(getattr(fc, "data_path", "") or "")
            if dp not in ("location", "rotation_euler") and not dp.endswith("ortho_scale"):
                continue
            for kp in getattr(fc, "keyframe_points", []) or []:
                try:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"
                except Exception:
                    pass
            # Force constant at active_end for buffer/hold
            if buffer_mode == "hold_last":
                kp = _find_kp_by_frame(fc, int(active_end))
                if kp is not None:
                    try:
                        kp.interpolation = "CONSTANT"
                    except Exception:
                        pass

    ad = getattr(cam_obj, "animation_data", None)
    if ad and getattr(ad, "action", None):
        _tune_action(ad.action)

    cam_data = getattr(cam_obj, "data", None)
    dad = getattr(cam_data, "animation_data", None) if cam_data else None
    if dad and getattr(dad, "action", None):
        _tune_action(dad.action)


def generate_camera_animation(
    *,
    scene: bpy.types.Scene,
    start_obj: bpy.types.Object,
    end_obj: bpy.types.Object,
    car_obj: bpy.types.Object,
    route_obj: bpy.types.Object,
    camera_name: str = "ROUTERIG_CAMERA",
    keyframes: list[int] | None = None,
    profile: dict,
) -> bpy.types.Object:
    """
    First-pass camera generator:
    - keys location/rotation/ortho at keyframes derived from a style profile
    - heading-driven yaw with anchor blending
    - pitch ramp from profile
    """
    res_x = int(scene.render.resolution_x)
    res_y = int(scene.render.resolution_y)

    timeline = profile.get("timeline", {}) if isinstance(profile, dict) else {}
    buffer_mode = str(timeline.get("buffer_mode", ""))
    active_end = _resolve_camera_active_end(scene=scene, profile=profile)
    frame_total = active_end  # use active_end; hold_last handled by constant interp
    ks = _effective_keyframes(scene=scene, profile=profile, keyframes_override=keyframes, active_end=active_end)

    # Filter out problematic keyframe 131 from calculation if it exists in the input list
    # The _filter_camera_path function will handle interpolation for it later if it's in the profile
    # but we want to avoid calculating it raw if we know it's bad.
    # However, the logic is: calculate what we can, then filter.
    # If frame 131 produces a bad result, we might want to skip calculating it entirely.
    # For now, let's calculate everything requested in 'ks' and let the filter deal with it.
    
    pitch_keys = _keys_from_profile_pitch(profile)
    yaw_offset_keys = _keys_from_profile_yaw_offset(profile)
    yaw_base_keys = _keys_from_profile_yaw_base(profile)
    heading_w_keys = _keys_from_profile_heading_weight(profile)
    target_w_keys = _keys_from_profile_target_weights(profile)
    distance_keys = _keys_from_profile_distance(profile)
    fit_anchor_keys = _keys_from_profile_fit_anchors(profile)
    route_window_keys = _keys_from_profile_route_window(profile)

    margin = float(profile.get("composition", {}).get("margins", {}).get("soft_clip", 0.90))
    # Convert to a fit multiplier: soft_clip=0.90 -> margin=1/0.90
    margin = max(1.0, 1.0 / max(1e-6, margin))

    # Desired screen placement: use the car keys if present, else center.
    car_screen_keys = profile.get("composition", {}).get("desired_screen_keys", {}).get("car", [])

    def eval_car_screen(frame: int) -> tuple[float, float]:
        if not car_screen_keys:
            return 0.0, 0.0
        # Treat as two independent key lists.
        nx_keys = [Keyframe1D(int(k["frame"]), float(k["nx"])) for k in car_screen_keys]
        ny_keys = [Keyframe1D(int(k["frame"]), float(k["ny"])) for k in car_screen_keys]
        nx_keys.sort(key=lambda x: x.frame)
        ny_keys.sort(key=lambda x: x.frame)
        return eval_keys(nx_keys, frame), eval_keys(ny_keys, frame)

    cam_obj = _ensure_camera(scene, camera_name)
    cam_obj.data.type = "ORTHO"
    cam_obj.rotation_mode = "XYZ"
    _clear_routerig_camera_animation(cam_obj)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    hold_cache: dict[str, object] | None = None

    buildings_collection_name = str(profile.get("collision", {}).get("buildings_collection_name", "ASSET_BUILDINGS"))
    buildings_col = find_collection(buildings_collection_name) if buildings_collection_name else None
    bvh = _build_world_bvh(buildings_col, depsgraph) if buildings_col else None

    prev_quat: Quaternion | None = None
    calculated_states: list[CameraState] = []

    for f in ks:
        if buffer_mode == "hold_last" and f == frame_total and hold_cache is not None:
            # For buffer frames, use the cached state from active_end
            # We recreate a CameraState for consistency in the list
            current_state = CameraState(
                frame=f,
                location=hold_cache["loc"].copy(),
                rotation_quaternion=hold_cache["quat"].copy(),
                ortho_scale=hold_cache["ortho"],
                focus_points_world=[p.copy() for p in hold_cache["focus_points_world"]],
            )
            calculated_states.append(current_state)
            continue

        scene.frame_set(f)
        depsgraph.update()

        start = start_obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()
        end = end_obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()
        car = car_obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()
        car_mesh_obj = _resolve_car_mesh_object(car_obj)
        car_mesh = car_mesh_obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()
        route_pts_all = _route_world_points(route_obj, depsgraph)

        # Heading from a forward sample; clamp to within timeline.
        f2 = min(scene.frame_end, f + 1)
        scene.frame_set(f2)
        depsgraph.update()
        car2 = car_obj.evaluated_get(depsgraph).matrix_world.to_translation().copy()

        scene.frame_set(f)
        depsgraph.update()

        heading_yaw = _heading_yaw_deg(car, car2)
        pitch = eval_keys(pitch_keys, f) if pitch_keys else -30.0
        w_heading = eval_keys(heading_w_keys, f) if heading_w_keys else 0.0
        w_start, w_car, w_end = _eval_target_weights(target_w_keys, f)

        # Yaw model: either base+offset, or screen-space solve around that guess.
        base = _eval_yaw_base(yaw_base_keys, f)
        if base == "start_to_end":
            v = Vector((end.x - start.x, end.y - start.y, 0.0))
            base_yaw = _deg(math.atan2(v.y, v.x)) if v.length > 1e-6 else 0.0
        elif base == "end_to_start":
            v = Vector((start.x - end.x, start.y - end.y, 0.0))
            base_yaw = _deg(math.atan2(v.y, v.x)) if v.length > 1e-6 else 0.0
        elif base == "car_to_end":
            v = Vector((end.x - car.x, end.y - car.y, 0.0))
            base_yaw = _deg(math.atan2(v.y, v.x)) if v.length > 1e-6 else heading_yaw
        elif base == "car_to_start":
            v = Vector((start.x - car.x, start.y - car.y, 0.0))
            base_yaw = _deg(math.atan2(v.y, v.x)) if v.length > 1e-6 else heading_yaw
        else:
            base_yaw = heading_yaw

        yaw_offset = eval_keys(yaw_offset_keys, f) if yaw_offset_keys else 0.0
        yaw_guess = base_yaw + yaw_offset
        yaw = yaw_guess
        if w_heading > 0.0 and abs(w_heading) > 1e-6:
            # Blend angles in XY.
            a = Vector((math.cos(_rad(yaw)), math.sin(_rad(yaw)), 0.0))
            b = Vector((math.cos(_rad(heading_yaw)), math.sin(_rad(heading_yaw)), 0.0))
            d = (a * (1.0 - w_heading) + b * w_heading)
            if d.length > 1e-6:
                yaw = _deg(math.atan2(d.y, d.x))

        # Optionally refine yaw to better match learned screen placement of anchors.
        yaw_mode = str(profile.get("angle", {}).get("yaw_model", {}).get("mode", "base_offset"))

        desired_car = _eval_screen_anchor(profile, "car", f)
        desired_end = _eval_screen_anchor(profile, "end", f)
        desired_start = _eval_screen_anchor(profile, "start", f)
        desired_dir_deg = 90.0
        for k in profile.get("composition", {}).get("route_dir_keys", []):
            if int(k.get("frame", -1)) == int(f):
                desired_dir_deg = float(k.get("angle_deg", desired_dir_deg))
                break

        forward_guess = _forward_from_yaw_pitch(yaw_deg=yaw, pitch_deg=pitch)
        distance = eval_keys(distance_keys, f) if distance_keys else 2000.0

        if yaw_mode == "solve_screen":
            # Build fit points factory (depends on rot for camera-plane projection of points).
            inc_start, inc_car, inc_end = _eval_fit_anchors(fit_anchor_keys, f)
            u0, u1 = _eval_route_window(route_window_keys, f)
            route_pts_window = (
                route_pts_all
                if inc_start
                else _route_window_points(route_pts=route_pts_all, start=start, end=end, u0=u0, u1=u1)
            )

            def fit_points_factory(rot: Matrix, cam_loc: Vector) -> list[Vector]:
                pts: list[Vector] = []
                if inc_start:
                    pts.append(start)
                if inc_car:
                    pts.append(car)
                if inc_end:
                    pts.append(end)
                if not pts:
                    pts = [car]
                if route_pts_window:
                    pts.extend(route_pts_window[:400])
                return pts

            yaw = _solve_yaw_for_composition(
                yaw_guess_deg=yaw_guess,
                pitch_deg=pitch,
                distance=distance,
                target=(start * w_start + car * w_car + end * w_end),
                margin=margin,
                res_x=res_x,
                res_y=res_y,
                car=car,
                end=end,
                start=start,
                match_start=bool(_eval_fit_anchors(fit_anchor_keys, f)[0]),
                desired_car=desired_car,
                desired_end=desired_end,
                desired_start=desired_start,
                desired_dir_deg=desired_dir_deg,
                fit_points_factory=fit_points_factory,
            )

        forward = _forward_from_yaw_pitch(yaw_deg=yaw, pitch_deg=pitch)
        rot = _rotation_from_forward_up(forward, Vector((0.0, 0.0, 1.0)))

        # Target is weighted blend of anchors.
        active_end = int(profile.get("timeline", {}).get("frame_active_end", scene.frame_end))
        end_focus_window = int(profile.get("composition", {}).get("end_focus_window_frames", 40))
        end_focus_start = max(1, active_end - max(0, end_focus_window))

        # End framing rule: in the final window, center on the car and control ortho scale by car size,
        # not by route/end marker composition.
        in_end_focus = f >= end_focus_start

        if in_end_focus:
            w_start, w_car, w_end = 0.0, 1.0, 0.0
            target = car_mesh
        else:
            target = start * w_start + car * w_car + end * w_end

        cam_loc = target - forward * float(distance)

        # Fit ortho scale using only anchors expected to be visible at this keyframe.
        inc_start, inc_car, inc_end = _eval_fit_anchors(fit_anchor_keys, f)
        focus_points: list[Vector] = [] # Renamed from fit_points to avoid confusion with internal usage
        if in_end_focus:
            focus_points = [car_mesh]
        else:
            if inc_start:
                focus_points.append(start)
            if inc_car:
                focus_points.append(car)
            if inc_end:
                focus_points.append(end)
        if not focus_points:
            focus_points = [car_mesh if in_end_focus else car]

        # Also fit to the ROUTE curve so the shot reads as a "map route".
        # Heuristic: when start is visible, include the whole route; otherwise, bias toward the latter segment.
        if (not in_end_focus) and route_pts_all:
            if inc_start:
                route_pts = route_pts_all
            else:
                u0, u1 = _eval_route_window(route_window_keys, f)
                # Fallback profile-free behavior: zoom in toward the end over time.
                if not route_window_keys:
                    if f >= 145:
                        u0, u1 = 0.80, 1.00
                    elif f >= 131:
                        u0, u1 = 0.65, 1.00
                    elif f >= 120:
                        u0, u1 = 0.40, 1.00
                    else:
                        u0, u1 = 0.30, 1.00
                route_pts = _route_window_points(route_pts=route_pts_all, start=start, end=end, u0=u0, u1=u1)
            # Avoid exploding point counts in the fit call.
            focus_points.extend(route_pts[:400])

        cam_mw = Matrix.Translation(cam_loc) @ rot.to_4x4()
        ortho_scale = _ortho_scale_to_fit_points(
            cam_matrix_world=cam_mw, points_world=focus_points, res_x=res_x, res_y=res_y, margin=margin
        )

        if in_end_focus:
            # Target: car is dead-center; ortho_scale sized so car occupies ~5-10% of screen (default 8%).
            target_frac = float(profile.get("composition", {}).get("end_car_target_frac", 0.08))
            extra = float(profile.get("composition", {}).get("end_car_extra_margin", 1.10))
            try:
                car_eval = car_mesh_obj.evaluated_get(depsgraph)
                car_bb = list(_iter_bbox_world_points(car_eval)) if getattr(car_eval, "type", "") == "MESH" else []
                if car_bb:
                    cam_inv = cam_mw.inverted()
                    bb_w, bb_h = _bbox_extents_in_camera_space(cam_mw_inv=cam_inv, points_world=car_bb)
                    ortho_scale = _ortho_scale_for_bbox_fraction(
                        bbox_w_cam=bb_w,
                        bbox_h_cam=bb_h,
                        res_x=res_x,
                        res_y=res_y,
                        target_frac=target_frac,
                        extra_margin=extra,
                    )
            except Exception:
                pass

            cam_loc = _apply_screen_offset_for_point(
                cam_loc=cam_loc,
                cam_rot=rot,
                ortho_scale=ortho_scale,
                res_x=res_x,
                res_y=res_y,
                point_world=car_mesh,
                desired_nx=0.0,
                desired_ny=0.0,
            )
        else:
            nx, ny = eval_car_screen(f)
            cam_loc = _apply_screen_offset_for_point(
                cam_loc=cam_loc,
                cam_rot=rot,
                ortho_scale=ortho_scale,
                res_x=res_x,
                res_y=res_y,
                point_world=car,
                desired_nx=nx,
                desired_ny=ny,
            )

        if bvh is not None:
            cam_loc, ortho_scale = _push_out_from_buildings(
                cam_loc=cam_loc,
                forward=forward,
                cam_rot=rot,
                ortho_scale=ortho_scale,
                bvh=bvh,
                profile=profile,
            )
        
        # Ensure quaternion continuity to avoid "long way" spins.
        q_curr = rot.to_quaternion()
        q_curr = _ensure_quat_continuity(prev_quat, q_curr)
        prev_quat = q_curr

        current_state = CameraState(
            frame=f,
            location=cam_loc.copy(),
            rotation_quaternion=q_curr.copy(),
            ortho_scale=ortho_scale,
            focus_points_world=[p.copy() for p in focus_points] # Store copies
        )
        calculated_states.append(current_state)

        if buffer_mode == "hold_last" and f == active_end:
            hold_cache = {
                "loc": cam_loc.copy(),
                "quat": q_curr.copy(),
                "ortho": float(ortho_scale),
                "focus_points_world": [p.copy() for p in focus_points] # Store copies
            }
    
    smoothed_states = _filter_camera_path(calculated_states, profile, keyframes=ks)

    # --- Keyframe insertion phase ---
    prev_euler: Euler | None = None
    for state in smoothed_states:
        scene.frame_set(state.frame)
        cam_obj.location = state.location
        e = state.rotation_quaternion.to_euler("XYZ")
        e = _ensure_euler_continuity(prev_euler, e)
        prev_euler = e.copy()
        cam_obj.rotation_euler = e
        cam_obj.data.ortho_scale = state.ortho_scale
        _set_safe_clipping(cam_obj=cam_obj, focus_points_world=state.focus_points_world)

        cam_obj.keyframe_insert(data_path="location", frame=state.frame)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=state.frame)
        cam_obj.data.keyframe_insert(data_path="ortho_scale", frame=state.frame)

    _apply_curve_profile_to_camera(cam_obj=cam_obj, profile=profile)
    _apply_bezier_auto_handles(cam_obj=cam_obj, active_end=active_end, buffer_mode=buffer_mode)
    if buffer_mode == "hold_last":
        _enforce_hold_last(cam_obj=cam_obj, frame_hold=active_end)

    scene.camera = cam_obj
    return cam_obj
