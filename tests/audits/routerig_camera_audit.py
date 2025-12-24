import argparse
import importlib.util
import math
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import bpy

try:
    from bpy_extras.object_utils import world_to_camera_view
except Exception:  # pragma: no cover
    world_to_camera_view = None


def _load_addon_module() -> None:
    """Load/register the addon so RouteRig operators are available in headless."""
    repo_root = Path(__file__).resolve().parents[2]
    init_path = repo_root / "__init__.py"

    module_name = "cash_cab_addon"
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        spec = importlib.util.spec_from_file_location(
            module_name,
            str(init_path),
            submodule_search_locations=[str(repo_root)],
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load addon module spec")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    register = getattr(module, "register", None)
    if callable(register):
        try:
            register()
        except ValueError:
            # Likely already registered.
            pass


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _quat_angle_delta(q1, q2) -> float:
    """Return angular delta in radians between two quaternions."""
    try:
        dot = abs(_safe_float(q1.dot(q2), 1.0))
        dot = max(-1.0, min(1.0, dot))
        return 2.0 * math.acos(dot)
    except Exception:
        return 0.0


def _unwrap_angle_deg(prev: Optional[float], cur: float) -> float:
    """Unwrap cur degrees to be continuous with prev (both in degrees)."""
    if prev is None:
        return float(cur)
    delta = (cur - prev + 180.0) % 360.0 - 180.0
    return float(prev + delta)


def _camera_world_quat(cam_obj: bpy.types.Object):
    try:
        return cam_obj.matrix_world.to_quaternion()
    except Exception:
        return cam_obj.rotation_quaternion.copy()


def _camera_world_yaw_deg(cam_obj: bpy.types.Object) -> float:
    """
    Compute a planar heading/spin angle in degrees.

    - If the camera has meaningful horizontal forward direction, use the forward vector.
    - If the camera is mostly looking straight down (forward XY ~ 0), use the camera's
      right vector projected into XY to detect "spins" around the view axis.
    """
    try:
        m3 = cam_obj.matrix_world.to_3x3()
        fwd = m3 @ bpy.mathutils.Vector((0.0, 0.0, -1.0))
        fxy = math.hypot(float(fwd.x), float(fwd.y))
        if fxy > 1e-4:
            return float(math.degrees(math.atan2(float(fwd.y), float(fwd.x))))
        right = m3 @ bpy.mathutils.Vector((1.0, 0.0, 0.0))
        return float(math.degrees(math.atan2(float(right.y), float(right.x))))
    except Exception:
        return 0.0


def _frame_range(scene: bpy.types.Scene) -> tuple[int, int]:
    try:
        return int(scene.frame_start), int(scene.frame_end)
    except Exception:
        return 1, 250


def _resolve_feature_obj(name: str) -> Optional[bpy.types.Object]:
    try:
        return bpy.data.objects.get(name)
    except Exception:
        return None


def _resolve_car_obj() -> Optional[bpy.types.Object]:
    return _resolve_feature_obj("CAR_LEAD") or _resolve_feature_obj("ASSET_CAR")


@dataclass
class MotionStats:
    frames: int
    step: int
    speed_max: float
    speed_p95: float
    accel_max: float
    rot_step_max_deg: float
    rot_step_p95_deg: float
    yaw_step_max_deg: float
    yaw_step_p95_deg: float
    yaw_spininess_deg: float
    yaw_spininess_window_deg: float
    ortho_min: float
    ortho_max: float
    car_in_view_pct: float
    car_in_safe_pct: float
    car_worst_xy: tuple[float, float]
    car_worst_frame: int
    speed_worst_frame: int
    rot_worst_frame: int
    out_of_view_ranges: list[tuple[int, int]]


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    idx = int(round((len(vals) - 1) * max(0.0, min(1.0, p))))
    return float(vals[idx])


def _camera_keyframe_summary(cam_obj: bpy.types.Object) -> dict[str, Any]:
    """Return counts of keyframes on object and camera datablock."""
    def _count_keyframes(ad) -> int:
        if not ad or not getattr(ad, "action", None):
            return 0
        total = 0
        for fc in getattr(ad.action, "fcurves", []) or []:
            total += len(getattr(fc, "keyframe_points", []) or [])
        return total

    obj_k = _count_keyframes(getattr(cam_obj, "animation_data", None))
    data_k = _count_keyframes(getattr(getattr(cam_obj, "data", None), "animation_data", None))
    return {"object_keyframes": obj_k, "data_keyframes": data_k}


def _camera_last_keyframe(cam_obj: bpy.types.Object) -> float:
    ad = getattr(cam_obj, "animation_data", None)
    action = getattr(ad, "action", None) if ad else None
    if not action:
        return 0.0
    last = 0.0
    for fc in getattr(action, "fcurves", []) or []:
        dp = str(getattr(fc, "data_path", "") or "")
        if dp not in ("location", "rotation_euler", "rotation_quaternion"):
            continue
        for kp in getattr(fc, "keyframe_points", []) or []:
            try:
                last = max(last, float(kp.co.x))
            except Exception:
                pass
    return float(last)


def _car_net_distance(scene: bpy.types.Scene, car_obj: bpy.types.Object, f0: int, f1: int) -> float:
    try:
        scene.frame_set(int(f0))
        p0 = car_obj.matrix_world.translation.copy()
        scene.frame_set(int(f1))
        p1 = car_obj.matrix_world.translation.copy()
        return float((p1 - p0).length)
    except Exception:
        return 0.0


def _analyze_camera_motion(
    *,
    scene: bpy.types.Scene,
    cam_obj: bpy.types.Object,
    soft_clip: float,
    step: int,
) -> MotionStats:
    start_f, end_f = _frame_range(scene)
    car_obj = _resolve_car_obj()

    margin = max(0.0, (1.0 - float(soft_clip)) * 0.5)
    safe_min = 0.0 + margin
    safe_max = 1.0 - margin

    locs: list[tuple[int, Any]] = []
    rots: list[tuple[int, Any]] = []
    yaws: list[tuple[int, float]] = []
    scales: list[tuple[int, float]] = []
    car_xy: list[tuple[int, float, float]] = []
    car_in_view = 0
    car_in_safe = 0
    worst_dist = -1.0
    worst_frame = start_f
    worst_xy = (0.5, 0.5)

    for f in range(start_f, end_f + 1, step):
        scene.frame_set(f)
        locs.append((f, cam_obj.matrix_world.translation.copy()))
        rots.append((f, _camera_world_quat(cam_obj)))
        yaws.append((f, _camera_world_yaw_deg(cam_obj)))
        try:
            scales.append((f, float(cam_obj.data.ortho_scale)))
        except Exception:
            scales.append((f, 0.0))

        if car_obj is not None and world_to_camera_view is not None:
            try:
                p = car_obj.matrix_world.translation
                uvw = world_to_camera_view(scene, cam_obj, p)
                x = float(uvw.x)
                y = float(uvw.y)
                car_xy.append((f, x, y))
                in_view = 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0
                if in_view:
                    car_in_view += 1
                    if safe_min <= x <= safe_max and safe_min <= y <= safe_max:
                        car_in_safe += 1

                # Worst-case distance outside the safe window (0 means inside).
                dx = 0.0
                if x < safe_min:
                    dx = safe_min - x
                elif x > safe_max:
                    dx = x - safe_max
                dy = 0.0
                if y < safe_min:
                    dy = safe_min - y
                elif y > safe_max:
                    dy = y - safe_max
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > worst_dist:
                    worst_dist = dist
                    worst_frame = f
                    worst_xy = (x, y)
            except Exception:
                pass

    speeds: list[float] = []
    accels: list[float] = []
    rot_d: list[float] = []
    yaw_steps: list[float] = []
    speed_frames: list[int] = []
    rot_frames: list[int] = []
    yaw_frames: list[int] = []

    for i in range(1, len(locs)):
        f1, p0 = locs[i - 1]
        f2, p1 = locs[i]
        try:
            speeds.append(float((p1 - p0).length))
        except Exception:
            speeds.append(0.0)
        speed_frames.append(int(f2))

    for i in range(1, len(speeds)):
        accels.append(abs(float(speeds[i] - speeds[i - 1])))

    for i in range(1, len(rots)):
        f1, q0 = rots[i - 1]
        f2, q1 = rots[i]
        rot_d.append(_quat_angle_delta(q0, q1))
        rot_frames.append(int(f2))

    # Yaw continuity and "spininess" heuristics (captures smooth 360 spins).
    yaw_unwrapped: list[tuple[int, float]] = []
    prev_yaw: Optional[float] = None
    for f, yaw in yaws:
        uy = _unwrap_angle_deg(prev_yaw, float(yaw))
        yaw_unwrapped.append((int(f), uy))
        prev_yaw = uy

    for i in range(1, len(yaw_unwrapped)):
        f2, y1 = yaw_unwrapped[i]
        _, y0 = yaw_unwrapped[i - 1]
        yaw_steps.append(abs(float(y1 - y0)))
        yaw_frames.append(int(f2))

    yaw_net = 0.0
    yaw_travel = 0.0
    if yaw_unwrapped:
        yaw_net = abs(float(yaw_unwrapped[-1][1] - yaw_unwrapped[0][1]))
    if yaw_steps:
        yaw_travel = float(sum(yaw_steps))
    yaw_spininess = max(0.0, yaw_travel - yaw_net)

    # Window around the user-reported issue area.
    win_lo = 105
    win_hi = 130
    win_yaw = [(f, y) for (f, y) in yaw_unwrapped if win_lo <= f <= win_hi]
    win_steps: list[float] = []
    if len(win_yaw) >= 2:
        for i in range(1, len(win_yaw)):
            win_steps.append(abs(float(win_yaw[i][1] - win_yaw[i - 1][1])))
        win_net = abs(float(win_yaw[-1][1] - win_yaw[0][1]))
        win_travel = float(sum(win_steps))
        yaw_spininess_window = max(0.0, win_travel - win_net)
    else:
        yaw_spininess_window = 0.0

    ortho_vals = [s for _, s in scales]

    total_samples = max(1, len(list(range(start_f, end_f + 1, step))))
    car_in_view_pct = 100.0 * float(car_in_view) / float(total_samples)
    car_in_safe_pct = 100.0 * float(car_in_safe) / float(total_samples)

    # Build out-of-view ranges for the car (sampled frames only).
    out_frames: list[int] = []
    if car_xy:
        for f, x, y in car_xy:
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                out_frames.append(int(f))
    ranges: list[tuple[int, int]] = []
    if out_frames:
        out_frames = sorted(out_frames)
        s = out_frames[0]
        e = s
        for f in out_frames[1:]:
            if f == e + step:
                e = f
            else:
                ranges.append((s, e))
                s = e = f
        ranges.append((s, e))

    speed_worst_frame = speed_frames[speeds.index(max(speeds))] if speeds and speed_frames else start_f
    rot_worst_frame = rot_frames[rot_d.index(max(rot_d))] if rot_d and rot_frames else start_f

    return MotionStats(
        frames=(end_f - start_f + 1),
        step=step,
        speed_max=max(speeds) if speeds else 0.0,
        speed_p95=_percentile(speeds, 0.95),
        accel_max=max(accels) if accels else 0.0,
        rot_step_max_deg=math.degrees(max(rot_d)) if rot_d else 0.0,
        rot_step_p95_deg=math.degrees(_percentile(rot_d, 0.95)) if rot_d else 0.0,
        yaw_step_max_deg=max(yaw_steps) if yaw_steps else 0.0,
        yaw_step_p95_deg=_percentile(yaw_steps, 0.95) if yaw_steps else 0.0,
        yaw_spininess_deg=float(yaw_spininess),
        yaw_spininess_window_deg=float(yaw_spininess_window),
        ortho_min=min(ortho_vals) if ortho_vals else 0.0,
        ortho_max=max(ortho_vals) if ortho_vals else 0.0,
        car_in_view_pct=car_in_view_pct,
        car_in_safe_pct=car_in_safe_pct,
        car_worst_xy=worst_xy,
        car_worst_frame=int(worst_frame),
        speed_worst_frame=int(speed_worst_frame),
        rot_worst_frame=int(rot_worst_frame),
        out_of_view_ranges=ranges,
    )


def _delete_old_camera_candidates(scene: bpy.types.Scene) -> list[str]:
    deleted: list[str] = []
    targets = [
        o
        for o in bpy.data.objects
        if o.type == "CAMERA"
        and (o.name.startswith("ROUTERIG_CAMERA") or o.name == "ASSET_CAMERA")
    ]
    for cam in targets:
        deleted.append(cam.name)
        cam_data = getattr(cam, "data", None)
        try:
            bpy.data.objects.remove(cam, do_unlink=True)
        except Exception:
            pass
        try:
            if cam_data and getattr(cam_data, "users", 0) == 0:
                bpy.data.cameras.remove(cam_data)
        except Exception:
            pass

    if scene.camera and scene.camera.name in deleted:
        scene.camera = None
    return deleted


def _render_settings_summary(scene: bpy.types.Scene) -> dict[str, Any]:
    try:
        return {
            "frame_start": int(scene.frame_start),
            "frame_end": int(scene.frame_end),
            "fps": int(scene.render.fps),
            "fps_base": float(scene.render.fps_base),
            "engine": str(scene.render.engine),
        }
    except Exception:
        return {}


def _write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit RouteRig camera animation and regenerate camera.")
    parser.add_argument("--save-blend", type=str, default="", help="Optional path to save a copy of the blend after regenerating camera.")
    parser.add_argument("--report-path", type=str, default="", help="Optional path to write a markdown report.")
    parser.add_argument("--sample-step", type=int, default=1, help="Frame step for motion sampling.")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

    _load_addon_module()

    scene = bpy.context.scene
    blend_path = Path(bpy.data.filepath) if bpy.data.filepath else Path("unsaved.blend")
    out_dir = Path(args.report_path).resolve().parent if args.report_path else blend_path.parent
    report_path = Path(args.report_path).resolve() if args.report_path else (out_dir / f"{blend_path.stem}.routerig_audit.md")
    save_blend = Path(args.save_blend).resolve() if args.save_blend else (blend_path.parent / f"{blend_path.stem}_ROUTERIG_REGEN.blend")

    # Load profile for expectations.
    try:
        from cash_cab_addon.routerig.style_profile import load_default_profile
        profile = load_default_profile()
    except Exception:
        profile = {}
    keyframes = profile.get("timeline", {}).get("keyframes", []) or [1, 47, 79, 120, 160]
    soft_clip = float(profile.get("composition", {}).get("margins", {}).get("soft_clip", 0.90))

    report_lines: list[str] = []
    report_lines.append(f"# RouteRig Camera Audit")
    report_lines.append("")
    report_lines.append(f"- Blend: `{blend_path}`")
    report_lines.append(f"- Scene: `{scene.name}`")
    report_lines.append(f"- Render: `{_render_settings_summary(scene)}`")
    report_lines.append(f"- RouteRig profile keyframes: `{keyframes}`")
    report_lines.append(f"- RouteRig soft_clip: `{soft_clip}`")
    report_lines.append("")

    # Pre-state
    cameras = [o for o in bpy.data.objects if o.type == "CAMERA"]
    report_lines.append("## Pre-existing Cameras")
    for cam in cameras:
        ks = _camera_keyframe_summary(cam)
        report_lines.append(f"- `{cam.name}` (active={scene.camera == cam}) keyframes(obj={ks['object_keyframes']}, data={ks['data_keyframes']}) type={getattr(getattr(cam,'data',None),'type',None)}")
    report_lines.append("")

    # Treat ROUTERIG_CAMERA as old if present, otherwise fall back to ASSET_CAMERA.
    old_routerig = bpy.data.objects.get("ROUTERIG_CAMERA") or bpy.data.objects.get("ASSET_CAMERA")
    old_stats = None
    if old_routerig and old_routerig.type == "CAMERA":
        try:
            old_stats = _analyze_camera_motion(scene=scene, cam_obj=old_routerig, soft_clip=soft_clip, step=max(1, int(args.sample_step)))
        except Exception:
            old_stats = None

    deleted = _delete_old_camera_candidates(scene)
    report_lines.append("## Camera Regeneration")
    report_lines.append(f"- Deleted old RouteRig camera objects: `{deleted}`")

    # Generate new
    spawn_res = bpy.ops.routerig.spawn_test_camera("EXEC_DEFAULT")
    anim_res = bpy.ops.routerig.generate_camera_animation("EXEC_DEFAULT")
    report_lines.append(f"- spawn_test_camera: `{spawn_res}`")
    report_lines.append(f"- generate_camera_animation: `{anim_res}`")
    report_lines.append("")

    new_cam = bpy.data.objects.get("ROUTERIG_CAMERA")
    if not new_cam or new_cam.type != "CAMERA":
        report_lines.append("## ERROR")
        report_lines.append("- Failed to create `ROUTERIG_CAMERA`. Scene may be missing required objects (MARKER_START, MARKER_END, ROUTE, CAR_LEAD).")
        _write_report(report_path, "\n".join(report_lines) + "\n")
        return 2

    new_stats = _analyze_camera_motion(scene=scene, cam_obj=new_cam, soft_clip=soft_clip, step=max(1, int(args.sample_step)))

    # ---- Test Results (PASS/FAIL) ----
    # Rotation "no spin/flip" tests are heuristics:
    # - large instantaneous world-rotation steps indicate flips
    # - large yaw spininess indicates unwanted accumulated rotation loops
    ROT_STEP_MAX_OK_DEG = 30.0
    YAW_SPININESS_OK_DEG = 180.0
    YAW_SPININESS_WINDOW_OK_DEG = 90.0

    cam_last_key = _camera_last_keyframe(new_cam)
    scene_end = int(getattr(scene, "frame_end", 0) or 0)
    car_obj = _resolve_car_obj()
    car_dist_after_cam = 0.0
    if car_obj is not None and scene_end > 0 and cam_last_key > 0.0:
        car_dist_after_cam = _car_net_distance(scene, car_obj, int(round(cam_last_key)), scene_end)
    TIMELINE_CAR_DIST_OK = 5.0
    timeline_ok = bool(cam_last_key >= float(scene_end) or car_dist_after_cam <= TIMELINE_CAR_DIST_OK)

    regen_ok = bool(new_cam and new_cam.name == "ROUTERIG_CAMERA")
    rot_ok = (
        float(new_stats.rot_step_max_deg) <= ROT_STEP_MAX_OK_DEG
        and float(new_stats.yaw_spininess_deg) <= YAW_SPININESS_OK_DEG
        and float(new_stats.yaw_spininess_window_deg) <= YAW_SPININESS_WINDOW_OK_DEG
    )
    in_view_ok = float(new_stats.car_in_view_pct) >= 99.0
    safe_ok = float(new_stats.car_in_safe_pct) >= 90.0

    report_lines.append("## Test Results")
    report_lines.append(f"- Regenerate camera (delete old first): `{'PASS' if regen_ok else 'FAIL'}`")
    report_lines.append(
        f"- Timeline alignment (camera keys cover car motion): `{'PASS' if timeline_ok else 'FAIL'}` (camera_last_key `{cam_last_key:.1f}`, scene_end `{scene_end}`, car_dist_after_cam `{car_dist_after_cam:.1f}`)"
    )
    report_lines.append(
        f"- Rotation continuity (no flip/spin): `{'PASS' if rot_ok else 'FAIL'}` (rot_step_max_deg `{new_stats.rot_step_max_deg:.2f}`, yaw_spininess `{new_stats.yaw_spininess_deg:.1f}`, yaw_spininess_window(105-130) `{new_stats.yaw_spininess_window_deg:.1f}`)"
    )
    report_lines.append(
        f"- Car stays in view: `{'PASS' if in_view_ok else 'FAIL'}` (in_view `{new_stats.car_in_view_pct:.1f}%`, worst frame `{new_stats.car_worst_frame}`)"
    )
    report_lines.append(
        f"- Car stays in safe window: `{'PASS' if safe_ok else 'FAIL'}` (safe `{new_stats.car_in_safe_pct:.1f}%`, soft_clip `{soft_clip}`)"
    )
    report_lines.append("")

    report_lines.append("## Motion Summary (Old vs New)")
    if old_stats:
        report_lines.append(f"- Old max speed/frame: `{old_stats.speed_max:.3f}` (p95 `{old_stats.speed_p95:.3f}`), max accel: `{old_stats.accel_max:.3f}`")
        report_lines.append(f"- Old rot step max/p95 (deg): `{old_stats.rot_step_max_deg:.3f}` / `{old_stats.rot_step_p95_deg:.3f}` (worst frame `{old_stats.rot_worst_frame}`)")
        report_lines.append(f"- Old yaw step max/p95 (deg): `{old_stats.yaw_step_max_deg:.3f}` / `{old_stats.yaw_step_p95_deg:.3f}`; yaw spininess `{old_stats.yaw_spininess_deg:.1f}` (window 105-130 `{old_stats.yaw_spininess_window_deg:.1f}`)")
        report_lines.append(f"- Old ortho_scale min/max: `{old_stats.ortho_min:.3f}` / `{old_stats.ortho_max:.3f}`")
        report_lines.append(f"- Old car in view/safe (%): `{old_stats.car_in_view_pct:.1f}` / `{old_stats.car_in_safe_pct:.1f}`")
        report_lines.append(f"- Old worst frame car XY: `f={old_stats.car_worst_frame}` `({old_stats.car_worst_xy[0]:.3f}, {old_stats.car_worst_xy[1]:.3f})`")
        if old_stats.out_of_view_ranges:
            report_lines.append(f"- Old car out-of-view ranges (sampled): `{old_stats.out_of_view_ranges[:8]}`")
    else:
        report_lines.append("- Old RouteRig camera not found (or not analyzable).")
    report_lines.append(f"- New max speed/frame: `{new_stats.speed_max:.3f}` (p95 `{new_stats.speed_p95:.3f}`), max accel: `{new_stats.accel_max:.3f}` (worst speed frame `{new_stats.speed_worst_frame}`)")
    report_lines.append(f"- New rot step max/p95 (deg): `{new_stats.rot_step_max_deg:.3f}` / `{new_stats.rot_step_p95_deg:.3f}` (worst frame `{new_stats.rot_worst_frame}`)")
    report_lines.append(f"- New yaw step max/p95 (deg): `{new_stats.yaw_step_max_deg:.3f}` / `{new_stats.yaw_step_p95_deg:.3f}`; yaw spininess `{new_stats.yaw_spininess_deg:.1f}` (window 105-130 `{new_stats.yaw_spininess_window_deg:.1f}`)")
    report_lines.append(f"- New ortho_scale min/max: `{new_stats.ortho_min:.3f}` / `{new_stats.ortho_max:.3f}`")
    report_lines.append(f"- New car in view/safe (%): `{new_stats.car_in_view_pct:.1f}` / `{new_stats.car_in_safe_pct:.1f}`")
    report_lines.append(f"- New worst frame car XY: `f={new_stats.car_worst_frame}` `({new_stats.car_worst_xy[0]:.3f}, {new_stats.car_worst_xy[1]:.3f})`")
    if new_stats.out_of_view_ranges:
        report_lines.append(f"- New car out-of-view ranges (sampled): `{new_stats.out_of_view_ranges[:8]}`")
    report_lines.append("")

    report_lines.append("## Apparent Issues (Heuristics)")
    if new_stats.car_in_view_pct < 99.0:
        report_lines.append(f"- Car leaves camera view in `{100.0 - new_stats.car_in_view_pct:.1f}%` of sampled frames (check ROUTE/CAR_LEAD alignment and ortho framing).")
    if new_stats.car_in_safe_pct < 90.0:
        report_lines.append(f"- Car frequently breaches soft safe window (soft_clip={soft_clip}); worst at frame `{new_stats.car_worst_frame}`.")
    if new_stats.rot_step_max_deg > ROT_STEP_MAX_OK_DEG:
        report_lines.append(f"- Large single-step world-rotation delta detected (max `{new_stats.rot_step_max_deg:.2f} deg`); indicates flip/interpolation artifacts.")
    if new_stats.yaw_spininess_window_deg > YAW_SPININESS_WINDOW_OK_DEG:
        report_lines.append(f"- Excess yaw spininess detected around frames 105-130 (spininess `{new_stats.yaw_spininess_window_deg:.1f} deg`); likely Bezier overshoot or angle wrapping.")
    elif new_stats.yaw_spininess_deg > YAW_SPININESS_OK_DEG:
        report_lines.append(f"- Excess yaw spininess across full shot (spininess `{new_stats.yaw_spininess_deg:.1f} deg`); likely unwanted accumulated rotations.")
    if new_stats.accel_max > new_stats.speed_p95 * 2.0 and new_stats.accel_max > 0.0:
        report_lines.append(f"- Speed spikes detected (max accel `{new_stats.accel_max:.3f}` vs p95 speed `{new_stats.speed_p95:.3f}`); indicates non-smooth translation.")
    if not any(l.startswith("- ") for l in report_lines[-4:]):
        report_lines.append("- No obvious heuristics-triggered issues; review visually for composition taste (parallax, end focus window, skyline anchors).")
    report_lines.append("")

    report_lines.append("## Likely Causes")
    report_lines.append("- RouteRig is purely scene-feature driven (MARKER_START/END, ROUTE curve, CAR_LEAD motion). Any mismatch in those primitives propagates into camera motion.")
    report_lines.append("- If your car animation timing differs from expected (frame ranges, fps), camera keyframe schedule may not match the car's actual travel pacing.")
    report_lines.append(f"- Timing check: camera_last_key `{cam_last_key:.1f}`, scene_end `{scene_end}`, car_dist_after_cam `{car_dist_after_cam:.1f}`.")
    report_lines.append("- If buildings are missing or extremely sparse/dense, learned style anchoring can over/under-react (skyline/streetscape cues).")
    report_lines.append("")

    report_lines.append("## Next Steps (User Approval)")
    report_lines.append(f"- Approve saving regenerated camera into: `{save_blend}`")
    report_lines.append("- If motion still feels wrong: confirm `ROUTE` exists and `CAR_LEAD` follows the route with correct timing; then regenerate RouteRig again.")
    report_lines.append("- If timing mismatch exists (car moves after camera stops): approve adding a RouteRig option to auto-adapt camera keyframes to the car animation window (pending).")
    report_lines.append(f"- For this file: approve extending RouteRig beyond frame `{cam_last_key:.1f}` to scene end `{scene_end}` (or align scene end to RouteRig frame_active_end).")
    report_lines.append("- If car breaches safe window: adjust RouteRig style profile (soft_clip / keyframe schedule) and re-run.")
    report_lines.append("- Optionally run strict scene audit on the saved file to catch unrelated rig/driver issues.")
    report_lines.append("")

    # Save copy
    try:
        save_blend.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_blend))
        report_lines.append(f"- Saved: `{save_blend}`")
    except Exception as exc:
        report_lines.append(f"- WARN: could not save regenerated blend: `{exc}`")

    _write_report(report_path, "\n".join(report_lines) + "\n")
    print(f"[ROUTERIG_AUDIT] Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover
        print(f"[ROUTERIG_AUDIT] ERROR: {exc}")
        traceback.print_exc()
        raise SystemExit(1)
