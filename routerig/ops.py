from __future__ import annotations

from pathlib import Path
import random

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
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)
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

        from . import camera_anim
        active_end = camera_anim._resolve_camera_active_end(scene=context.scene, profile=profile)
        keyframes = camera_anim._effective_keyframes(
            scene=context.scene,
            profile=profile,
            keyframes_override=None,
            active_end=active_end,
        )

        settings = context.scene.routerig
        log.info(
            "RouteRig seed=%d variance=%.3f end_vis=%s orbit_deg=%.2f orbit_radius=%.2f ortho_delta=%.2f keys_only=%s",
            int(getattr(settings, "routerig_seed", 0)),
            float(getattr(settings, "routerig_variance", 0.0)),
            bool(getattr(settings, "routerig_endpose_visibility", False)),
            float(getattr(settings, "routerig_orbit_deg", 0.0)),
            float(getattr(settings, "routerig_orbit_radius", 0.0)),
            float(getattr(settings, "routerig_ortho_delta", 0.0)),
            bool(getattr(settings, "routerig_orbit_apply_to_keys_only", True)),
        )

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


def _next_available_camera_name(prefix: str, *, digits: int = 3) -> str:
    existing = set(bpy.data.objects.keys())
    for i in range(1, 10**digits):
        name = f"{prefix}{i:0{digits}d}"
        if name not in existing:
            return name
    # Fallback: let Blender suffixing happen if we somehow exhaust.
    return f"{prefix}{'9' * digits}"


class ROUTERIG_OT_spawn_new_camera(bpy.types.Operator):
    bl_idname = "routerig.spawn_new_camera"
    bl_label = "Spawn New RouteRig Camera (Keep Existing)"
    bl_description = "Generate a new RouteRig camera without overwriting the existing one"
    bl_options = {"REGISTER", "UNDO"}

    make_active: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Make Active",
        default=True,
        description="Set the spawned camera as the active scene camera",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        route_obj = find_object_any(CANON_ROUTE_ALIASES)
        car_obj = find_object(CANON_CAR)
        if not (start_obj and end_obj and route_obj and car_obj):
            self.report({"WARNING"}, "Cannot spawn: missing MARKER_START/END/ROUTE/CAR_LEAD")
            return {"CANCELLED"}

        profile = load_default_profile()
        cam_name = _next_available_camera_name("ROUTERIG_CAMERA_V")
        cam_obj = generate_camera_animation(
            scene=context.scene,
            start_obj=start_obj,
            end_obj=end_obj,
            car_obj=car_obj,
            route_obj=route_obj,
            camera_name=cam_name,
            keyframes=None,
            profile=profile,
        )
        if bool(self.make_active):
            context.scene.camera = cam_obj
        self.report({"INFO"}, f"Spawned {cam_obj.name}")
        return {"FINISHED"}


class ROUTERIG_OT_spawn_variant_cameras(bpy.types.Operator):
    bl_idname = "routerig.spawn_variant_cameras"
    bl_label = "Spawn Variant RouteRig Cameras"
    bl_description = "Spawn multiple RouteRig cameras using randomized tweak settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        start_obj = find_object(CANON_START)
        end_obj = find_object(CANON_END)
        route_obj = find_object_any(CANON_ROUTE_ALIASES)
        car_obj = find_object(CANON_CAR)
        if not (start_obj and end_obj and route_obj and car_obj):
            self.report({"WARNING"}, "Cannot spawn variants: missing MARKER_START/END/ROUTE/CAR_LEAD")
            return {"CANCELLED"}

        settings = context.scene.routerig
        count = int(getattr(settings, "routerig_variants_count", 5))
        variation = float(getattr(settings, "routerig_variants_variation", 0.35))
        make_active = bool(getattr(settings, "routerig_variants_make_active", True))

        # Snapshot original settings to restore.
        original = {
            "routerig_seed": int(getattr(settings, "routerig_seed", 0)),
            "routerig_variance": float(getattr(settings, "routerig_variance", 0.0)),
            "routerig_endpose_visibility": bool(getattr(settings, "routerig_endpose_visibility", False)),
            "routerig_endpose_blend_window": int(getattr(settings, "routerig_endpose_blend_window", 8)),
            "routerig_orbit_deg": float(getattr(settings, "routerig_orbit_deg", 0.0)),
            "routerig_orbit_radius": float(getattr(settings, "routerig_orbit_radius", 0.0)),
            "routerig_orbit_apply_to_keys_only": bool(getattr(settings, "routerig_orbit_apply_to_keys_only", True)),
            "routerig_ortho_delta": float(getattr(settings, "routerig_ortho_delta", 0.0)),
        }

        from . import scene_props

        profile = load_default_profile()
        spawned: list[bpy.types.Object] = []

        scene_props._suspend_updates_begin()
        try:
            for i in range(1, max(1, count) + 1):
                # Conservative random ranges; "variation" scales the magnitude.
                setattr(settings, "routerig_seed", random.randint(1, 2_000_000_000))
                setattr(
                    settings,
                    "routerig_variance",
                    max(0.0, min(1.0, float(original["routerig_variance"]) + random.random() * 0.6 * variation)),
                )
                setattr(settings, "routerig_endpose_visibility", bool(original["routerig_endpose_visibility"]))
                setattr(settings, "routerig_endpose_blend_window", int(original["routerig_endpose_blend_window"]))
                setattr(
                    settings,
                    "routerig_orbit_deg",
                    float(original["routerig_orbit_deg"]) + random.uniform(-15.0, 15.0) * variation,
                )
                setattr(
                    settings,
                    "routerig_orbit_radius",
                    float(original["routerig_orbit_radius"]) + random.uniform(-30.0, 30.0) * variation,
                )
                setattr(settings, "routerig_orbit_apply_to_keys_only", bool(original["routerig_orbit_apply_to_keys_only"]))
                setattr(
                    settings,
                    "routerig_ortho_delta",
                    float(original["routerig_ortho_delta"]) + random.uniform(-150.0, 150.0) * variation,
                )

                cam_name = _next_available_camera_name("ROUTERIG_CAMERA_RAND_", digits=2)
                cam_obj = generate_camera_animation(
                    scene=context.scene,
                    start_obj=start_obj,
                    end_obj=end_obj,
                    car_obj=car_obj,
                    route_obj=route_obj,
                    camera_name=cam_name,
                    keyframes=None,
                    profile=profile,
                )
                spawned.append(cam_obj)

        finally:
            # Restore user settings.
            for k, v in original.items():
                try:
                    setattr(settings, k, v)
                except Exception:
                    pass
            scene_props._suspend_updates_end()

        if make_active and spawned:
            context.scene.camera = spawned[-1]

        self.report({"INFO"}, f"Spawned {len(spawned)} camera(s)")
        return {"FINISHED"}
