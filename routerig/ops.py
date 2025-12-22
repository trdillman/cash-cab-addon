from __future__ import annotations

from pathlib import Path

import bpy

from .log import get_logger
from .camera_spawn import spawn_start_camera_from_features
from .camera_anim import generate_camera_animation
from .finders import find_collection, find_object, find_object_any
from .scene_summary import build_scene_summary, write_scene_summary
from .style_profile import load_default_profile

log = get_logger()

CANON_START = "MARKER_START"
CANON_END = "MARKER_END"
CANON_ROUTE = "ROUTE"
CANON_CAR = "CAR_LEAD"
CANON_BUILDINGS = "ASSET_BUILDINGS"
CANON_ROUTE_ALIASES = ["ROUTE", "Route"]


class ROUTERIG_OT_validate_scene(bpy.types.Operator):
    bl_idname = "routerig.validate_scene"
    bl_label = "Validate Scene"
    bl_description = "Validate required RouteRig objects/collections exist"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        route_obj = find_object_any(CANON_ROUTE_ALIASES)
        car_obj = find_object(CANON_CAR)
        buildings_col = find_collection(CANON_BUILDINGS)

        missing: list[str] = []
        if start_obj is None:
            missing.append(f"Object: {CANON_START}")
        if end_obj is None:
            missing.append(f"Object: {CANON_END}")
        if route_obj is None:
            missing.append(f"Object: {CANON_ROUTE}")
        if car_obj is None:
            missing.append(f"Object: {CANON_CAR}")
        # Buildings are expected in production shots, but allow missing for training oddballs.
        buildings_missing = buildings_col is None

        if missing:
            msg = "Missing: " + ", ".join(missing)
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        if buildings_missing:
            self.report({"WARNING"}, f"OK (no buildings collection found): {CANON_BUILDINGS}")
        else:
            self.report({"INFO"}, f"OK: {start_obj.name}, {end_obj.name}, {route_obj.name}, {car_obj.name}, {buildings_col.name}")
        return {"FINISHED"}


class ROUTERIG_OT_export_scene_summary(bpy.types.Operator):
    bl_idname = "routerig.export_scene_summary"
    bl_label = "Export Scene Summary"
    bl_description = "Export a JSON summary used for building style profiles"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        settings = context.scene.routerig

        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        route_obj = find_object_any(CANON_ROUTE_ALIASES)
        car_obj = find_object(CANON_CAR)
        buildings_col = find_collection(CANON_BUILDINGS)
        if not (start_obj and end_obj and route_obj and car_obj):
            bpy.ops.routerig.validate_scene()
            return {"CANCELLED"}

        payload = build_scene_summary(
            scene=context.scene,
            camera_name="",
            frames=(1, int(settings.frame_total)),
            step=int(settings.sample_step),
            start_marker_name=start_obj.name,
            end_marker_name=end_obj.name,
            route_object_name=route_obj.name,
            car_lead_name=car_obj.name,
            buildings_collection_name=buildings_col.name if buildings_col else CANON_BUILDINGS,
        )

        report_dir = bpy.path.abspath(settings.report_dir) if settings.report_dir else ""
        if report_dir:
            out_dir = Path(report_dir)
        else:
            out_dir = Path.cwd() / "routerig_reports"

        blend_name = Path(bpy.data.filepath).stem if bpy.data.filepath else "unsaved"
        out_path = out_dir / f"{blend_name}.{context.scene.name}.summary.json"
        write_scene_summary(payload, out_path)

        self.report({"INFO"}, f"Wrote {out_path}")
        return {"FINISHED"}


def _check_deps(op, start_obj, end_obj, route_obj, car_obj) -> bool:
    missing = []
    if not start_obj: missing.append(CANON_START)
    if not end_obj: missing.append(CANON_END)
    if not car_obj: missing.append(CANON_CAR)
    # route_obj is optional for spawn, required for anim?
    # Logic in original ops: 
    # spawn_test_camera checks (start, end, car)
    # generate_camera_animation checks (start, end, route, car)
    
    if missing:
        op.report({"WARNING"}, f"Cannot run RouteRig: Missing {', '.join(missing)}")
        return False
    return True


class ROUTERIG_OT_spawn_test_camera(bpy.types.Operator):
    bl_idname = "routerig.spawn_test_camera"
    bl_label = "Spawn Test Camera"
    bl_description = "Create an orthographic start camera from MARKER_START/MARKER_END/CAR_LEAD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        car_obj = find_object(CANON_CAR)
        
        # Check dependencies gracefully
        if not (start_obj and end_obj and car_obj):
            self.report({"WARNING"}, f"Cannot spawn camera: Missing {CANON_START}, {CANON_END}, or {CANON_CAR}")
            return {"CANCELLED"}

        profile = load_default_profile()
        pitch_keys = profile.get("angle", {}).get("pitch_keys_deg", [])
        pitch = float(pitch_keys[0]["pitch"]) if pitch_keys else -19.0
        # Keep initial yaw offset modest for spawn-debug; animation operator uses the full learned model.
        yaw_offset = 0.0
        soft_clip = float(profile.get("composition", {}).get("margins", {}).get("soft_clip", 0.90))
        margin = max(1.0, 1.0 / max(1e-6, soft_clip))

        cam_obj = spawn_start_camera_from_features(
            scene=context.scene,
            camera_name="ROUTERIG_CAMERA",
            start_obj=start_obj,
            end_obj=end_obj,
            car_obj=car_obj,
            frame=1,
            pitch_deg=float(pitch),
            yaw_offset_deg=float(yaw_offset),
            margin=float(margin),
        )

        # Keyframe the initial pose so it behaves like a “starting cam rig”.
        context.scene.frame_set(1)
        cam_obj.keyframe_insert(data_path="location", frame=1)
        cam_obj.keyframe_insert(data_path="rotation_quaternion", frame=1)
        cam_obj.data.keyframe_insert(data_path="ortho_scale", frame=1)

        self.report({"INFO"}, f"Spawned {cam_obj.name} at frame 1")
        return {"FINISHED"}


class ROUTERIG_OT_generate_camera_animation(bpy.types.Operator):
    bl_idname = "routerig.generate_camera_animation"
    bl_label = "Generate Camera Animation"
    bl_description = "Generate a first-pass 180f orthographic camera animation from scene features"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        route_obj = find_object_any(CANON_ROUTE_ALIASES)
        car_obj = find_object(CANON_CAR)
        
        # Check dependencies gracefully
        if not (start_obj and end_obj and route_obj and car_obj):
            self.report({"WARNING"}, f"Cannot animate camera: Missing {CANON_START}, {CANON_END}, {CANON_ROUTE}, or {CANON_CAR}")
            return {"CANCELLED"}

        profile = load_default_profile()

        keyframes = profile.get("timeline", {}).get("keyframes", []) or [1, 47, 79, 120, 160]

        cam_obj = generate_camera_animation(
            scene=context.scene,
            start_obj=start_obj,
            end_obj=end_obj,
            car_obj=car_obj,
            route_obj=route_obj,
            camera_name="ROUTERIG_CAMERA",
            keyframes=keyframes,
            profile=profile,
        )

        self.report({"INFO"}, f"Generated keys on {cam_obj.name} at {keyframes}")
        return {"FINISHED"}
