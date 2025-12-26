from __future__ import annotations

import bpy
import time


_SUSPEND_UPDATES = 0
_LIVE_APPLY_PENDING = False
_LIVE_APPLY_SCENE_NAME: str | None = None

_REGEN_PENDING = False
_REGEN_SCENE_NAME: str | None = None
_REGEN_LAST_CHANGE_T = 0.0


def _get_scene(name: str | None) -> bpy.types.Scene | None:
    if not name:
        return None
    try:
        return bpy.data.scenes.get(name)
    except Exception:
        return None


def _schedule_live_apply(scene: bpy.types.Scene) -> None:
    global _LIVE_APPLY_PENDING, _LIVE_APPLY_SCENE_NAME
    _LIVE_APPLY_SCENE_NAME = scene.name
    if _LIVE_APPLY_PENDING:
        return
    _LIVE_APPLY_PENDING = True

    def _timer():
        global _LIVE_APPLY_PENDING
        _LIVE_APPLY_PENDING = False
        scn = _get_scene(_LIVE_APPLY_SCENE_NAME)
        if scn is None:
            return None
        try:
            from . import camera_anim

            camera_anim.apply_live_orbit_ortho_preview(scene=scn)
        except Exception:
            pass
        return None

    bpy.app.timers.register(_timer, first_interval=0.0)


def _schedule_regen(scene: bpy.types.Scene) -> None:
    global _REGEN_PENDING, _REGEN_SCENE_NAME, _REGEN_LAST_CHANGE_T
    _REGEN_SCENE_NAME = scene.name
    _REGEN_LAST_CHANGE_T = time.monotonic()
    if _REGEN_PENDING:
        return
    _REGEN_PENDING = True

    def _timer():
        global _REGEN_PENDING
        scn = _get_scene(_REGEN_SCENE_NAME)
        if scn is None:
            _REGEN_PENDING = False
            return None

        settings = getattr(scn, "routerig", None)
        debounce_ms = int(getattr(settings, "routerig_live_update_debounce_ms", 600)) if settings else 600
        debounce_s = max(0.0, float(debounce_ms) / 1000.0)
        now = time.monotonic()
        if (now - float(_REGEN_LAST_CHANGE_T)) < debounce_s:
            return 0.1

        _REGEN_PENDING = False
        try:
            from .camera_anim import generate_camera_animation
            from .finders import find_object, find_object_any
            from .style_profile import load_default_profile

            start_obj = find_object("MARKER_START")
            end_obj = find_object("MARKER_END")
            route_obj = find_object_any(["ROUTE", "Route"])
            car_obj = find_object("CAR_LEAD")
            if not (start_obj and end_obj and route_obj and car_obj):
                return None

            profile = load_default_profile()
            generate_camera_animation(
                scene=scn,
                start_obj=start_obj,
                end_obj=end_obj,
                car_obj=car_obj,
                route_obj=route_obj,
                camera_name="ROUTERIG_CAMERA",
                keyframes=None,
                profile=profile,
            )
        except Exception:
            pass
        return None

    bpy.app.timers.register(_timer, first_interval=0.1)


def _on_routerig_live_preview_update(self, context: bpy.types.Context) -> None:
    if _SUSPEND_UPDATES:
        return
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    settings = getattr(scene, "routerig", None)
    if not settings or not bool(getattr(settings, "routerig_live_preview", True)):
        return
    _schedule_live_apply(scene)


def _on_routerig_live_orbit_ortho_update(self, context: bpy.types.Context) -> None:
    if _SUSPEND_UPDATES:
        return
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    settings = getattr(scene, "routerig", None)
    if not settings or not bool(getattr(settings, "routerig_live_preview", True)):
        return
    _schedule_live_apply(scene)


def _on_routerig_live_regen_update(self, context: bpy.types.Context) -> None:
    if _SUSPEND_UPDATES:
        return
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    settings = getattr(scene, "routerig", None)
    if not settings or not bool(getattr(settings, "routerig_live_update", False)):
        return
    _schedule_regen(scene)


class ROUTERIG_SceneSettings(bpy.types.PropertyGroup):
    frame_active_end: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Active End Frame",
        default=160,
        min=1,
    )
    frame_total: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Total Frames",
        default=160,
        min=1,
    )
    sample_step: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Sample Step",
        default=5,
        min=1,
        description="Frame step for analysis sampling (lower is slower but more detailed)",
    )

    report_dir: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="Report Folder",
        default="//routerig_reports",
        subtype="DIR_PATH",
        description="Relative paths are resolved from the .blend file location",
    )

    routerig_seed: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Seed",
        default=0,
        description="Deterministic seed for micro-variation (0 disables)",
        update=_on_routerig_live_regen_update,
    )
    routerig_variance: bpy.props.FloatProperty(  # type: ignore[valid-type]
        name="Variance",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Micro-variation strength (0 disables)",
        update=_on_routerig_live_regen_update,
    )

    routerig_endpose_visibility: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Fix End Occlusion",
        default=False,
        description="At the final frame, nudge camera to keep CAR_LEAD unoccluded",
        update=_on_routerig_live_regen_update,
    )
    routerig_endpose_blend_window: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="End Blend Window",
        default=8,
        min=1,
        max=60,
        description="Frames to blend into the adjusted end pose (if applied)",  
        update=_on_routerig_live_regen_update,
    )

    routerig_orbit_deg: bpy.props.FloatProperty(  # type: ignore[valid-type]
        name="Orbit Angle (deg)",
        default=0.0,
        min=-180.0,
        max=180.0,
        description="Rotate camera around CAR_LEAD at keyed frames (degrees)",
        update=_on_routerig_live_orbit_ortho_update,
    )
    routerig_orbit_radius: bpy.props.FloatProperty(  # type: ignore[valid-type]
        name="Orbit Radius Offset",
        default=0.0,
        min=-500.0,
        max=500.0,
        description="Offset camera distance in XY plane during orbit (scene units)",
        update=_on_routerig_live_orbit_ortho_update,
    )
    routerig_orbit_apply_to_keys_only: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Orbit Keyframes Only",
        default=True,
        description="Apply orbit adjustments only to keyed frames",
        update=_on_routerig_live_orbit_ortho_update,
    )
    routerig_ortho_delta: bpy.props.FloatProperty(  # type: ignore[valid-type]
        name="Ortho Scale Delta",
        default=0.0,
        min=-500.0,
        max=500.0,
        description="Additive delta applied to keyed orthographic scales",
        update=_on_routerig_live_orbit_ortho_update,
    )

    routerig_live_preview: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Live Preview (Orbit/Ortho)",
        default=True,
        description="Apply orbit + ortho delta immediately to the existing RouteRig camera animation",
        update=_on_routerig_live_preview_update,
    )
    routerig_live_update: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Live Update (Debounced Regen)",
        default=False,
        description="Regenerate the RouteRig camera after tweaking seed/variance/end-occlusion (debounced)",
    )
    routerig_live_update_debounce_ms: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Debounce (ms)",
        default=600,
        min=0,
        max=5000,
        description="Delay before regenerating RouteRig camera after changes",
    )

    routerig_variants_count: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Variant Count",
        default=5,
        min=1,
        max=30,
        description="How many additional RouteRig cameras to spawn",
    )
    routerig_variants_variation: bpy.props.FloatProperty(  # type: ignore[valid-type]
        name="Variation",
        default=0.35,
        min=0.0,
        max=1.0,
        description="Randomness strength when spawning variant cameras",
    )
    routerig_variants_make_active: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Make Last Active",
        default=True,
        description="After spawning variants, set the last one as the active scene camera",
    )


def _suspend_updates_begin() -> None:
    global _SUSPEND_UPDATES
    _SUSPEND_UPDATES += 1


def _suspend_updates_end() -> None:
    global _SUSPEND_UPDATES
    _SUSPEND_UPDATES = max(0, _SUSPEND_UPDATES - 1)
