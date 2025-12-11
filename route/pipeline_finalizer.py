"""Post-pipeline clean-up helpers for BLOSM.

Usage:
- Called automatically by BLOSM_OT_FetchRouteMap once the asset pipeline completes.
- Can also be invoked manually via route.pipeline_finalizer.run(context.scene) for quick driver refresh/cleanup.
- Keep miscellaneous manual helpers in route/maintenance_utils.py instead of editing core pipeline files.
- Tyler's Sandbox (see below) runs last; drop personal tweaks there so they survive updates.
  Example tweak: inside _run_tylers_sandbox, grab the "Route" curve and set `route_curve.data.bevel_depth = 0.6`.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Union
from pathlib import Path

import bpy
import os
from mathutils import Vector
from mathutils.geometry import interpolate_bezier

from . import anim as route_anim
from . import assets as route_assets
from . import nodes as route_nodes
from ..app import blender as blenderApp

CN_TOWER_LAT = 43.6425662
CN_TOWER_LON = -79.3870568
CN_TOWER_OBJECT_NAME = "CN_TOWER"
CN_TOWER_ASSET_BLEND = route_assets.ASSET_DIRECTORY / "ASSET_CNTower.blend"
CAR_TRAIL_NODE_GROUP_NAME = "ASSET_CAR_TRAIL"
CAR_TRAIL_BEVEL_DRIVERS = (
    ("bevel_factor_end", "offset_factor - 0.0055"),
    ("bevel_factor_start", "offset_factor - 0.075"),
)
ROUTE_ROLE_TAG = "route_curve_osm"
CAR_TRAIL_ROLE_TAG = "car_trail"
ASSET_CAR_ROLE_TAG = "asset_car"
CAR_TRAIL_OBJECT_NAME = "CAR_TRAIL"
CAR_TRAIL_TEMPLATE_BLEND = route_assets.ASSET_DIRECTORY / "ASSET_CAR_TRAIL.blend"
CAR_TRAIL_RESAMPLE_SPACING = 10.0  # Project spec: CAR_TRAIL resample spacing (world units)
CAR_TRAIL_SAMPLES_PER_SEGMENT = 16  # Project spec: CAR_TRAIL resample samples per segment
ADDON_ROOT = Path(__file__).resolve().parent.parent
CAMERA_BLEND_PATH = ADDON_ROOT / "assets" / "ASSET_CAMERA.blend"
CAMERAS_COLLECTION_NAME = "CAMERAS"
ASSET_CAMERA_NAME = "ASSET_CAMERA"
SAFE_AREA_TARGET_VALUE = 0.95

# --- AUTO PATCH HELPERS (non-breaking) ---
def _pick_first_object_in_collection(coll):
    if not coll:
        return None
    # prefer EMPTY containing 'BASE'
    for o in coll.objects:
        try:
            if o.type == 'EMPTY' and 'BASE' in o.name.upper():
                return o
        except Exception:
            pass
    for o in coll.objects:
        try:
            if o.type == 'EMPTY':
                return o
        except Exception:
            pass
    return next(iter(coll.objects), None)
# --- END AUTO PATCH HELPERS ---


def _ensure_cn_tower_marker(scene: Optional[bpy.types.Scene]) -> None:
    """Ensure a CN_TOWER mesh object is present and positioned at the real location.

    Prefers the ASSET_CNTower.blend asset (CN_TOWER mesh). If unavailable, falls
    back to the legacy EMPTY marker.
    """
    if scene is None:
        return
    print("[BLOSM] _ensure_cn_tower_marker invoked")

    marker = bpy.data.objects.get(CN_TOWER_OBJECT_NAME)

    # If no CN_TOWER object exists yet, try to append it from ASSET_CNTower.blend
    if marker is None and CN_TOWER_ASSET_BLEND.exists():
        try:
            with bpy.data.libraries.load(str(CN_TOWER_ASSET_BLEND), link=False) as (data_from, data_to):
                # Prefer an object explicitly named CN_TOWER
                if CN_TOWER_OBJECT_NAME in data_from.objects:
                    data_to.objects = [CN_TOWER_OBJECT_NAME]
                elif data_from.objects:
                    # Fallback: bring in all objects; pick by name later
                    data_to.objects = list(data_from.objects)
        except Exception as exc:
            print(f"[BLOSM] WARN CN Tower asset append failed: {exc}")

        # Re-resolve marker after append
        marker = bpy.data.objects.get(CN_TOWER_OBJECT_NAME)

    # Final fallback: legacy EMPTY marker if mesh asset is not available
    if marker is None:
        marker = bpy.data.objects.new(CN_TOWER_OBJECT_NAME, None)
        marker.empty_display_type = 'SPHERE'
        marker.empty_display_size = 10.0

    # Ensure the marker is linked to the scene
    marker_collections = list(getattr(marker, "users_collection", []) or [])
    if scene.collection not in marker_collections:
        try:
            scene.collection.objects.link(marker)
        except RuntimeError:
            pass

    # Optionally keep the tower grouped in its own collection
    def _ensure_tower_collection(scene, marker_obj):
        coll = bpy.data.collections.get("ASSET_CNTower")
        if coll is None:
            coll = bpy.data.collections.new("ASSET_CNTower")
        existing_collection_names = {child.name for child in scene.collection.children}
        if coll.name not in existing_collection_names:
            try:
                scene.collection.children.link(coll)
            except RuntimeError:
                pass
        if marker_obj and marker_obj.name not in {obj.name for obj in coll.objects}:
            try:
                coll.objects.link(marker_obj)
            except RuntimeError:
                pass
        return coll

    tower_coll = _ensure_tower_collection(scene, marker)
    print(f"[BLOSM] CN_TOWER linked into ASSET_CNTower (collections={[c.name for c in getattr(marker, 'users_collection', []) or []]})")

    projection = getattr(blenderApp.app, "projection", None)
    if projection is None:
        origin = None
        try:
            origin = tuple(scene.get("cashcab_projection_origin", ())) if scene else None
        except Exception:
            origin = None
        addon = getattr(scene, "blosm", None)
        try:
            if origin and len(origin) == 2:
                blenderApp.app.setProjection(origin[0], origin[1])
            elif addon:
                center_lat = (getattr(addon, "minLat", CN_TOWER_LAT) + getattr(addon, "maxLat", CN_TOWER_LAT)) / 2
                center_lon = (getattr(addon, "minLon", CN_TOWER_LON) + getattr(addon, "maxLon", CN_TOWER_LON)) / 2
                blenderApp.app.setProjection(center_lat, center_lon)
            projection = getattr(blenderApp.app, "projection", None)
        except Exception as exc:
            print(f"[BLOSM] WARN CN Tower projection setup failed: {exc}")
    if projection is None:
        return
    try:
        x, y, _ = projection.fromGeographic(CN_TOWER_LAT, CN_TOWER_LON)
        marker.location = (x, y, 0.0)
    except Exception as exc:
        print(f"[BLOSM] WARN CN Tower marker placement failed: {exc}")
        return
    print(f"[BLOSM] CN Tower marker placed at ({marker.location.x:.3f}, {marker.location.y:.3f})")


def _ensure_asset_camera(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    summary = {"camera": None, "created": False, "linked_to_cameras": False, "safe_area_configured": False}
    if scene is None:
        return summary

    cameras_coll = bpy.data.collections.get(CAMERAS_COLLECTION_NAME)
    if cameras_coll is None:
        cameras_coll = bpy.data.collections.new(CAMERAS_COLLECTION_NAME)
        if scene.collection and cameras_coll.name not in {child.name for child in scene.collection.children}:
            try:
                scene.collection.children.link(cameras_coll)
            except RuntimeError:
                pass

    camera_obj = bpy.data.objects.get(ASSET_CAMERA_NAME)
    camera_created = False
    if camera_obj is None:
        if not CAMERA_BLEND_PATH.exists():
            print(f"[BLOSM] WARN camera asset not found: {CAMERA_BLEND_PATH}")
            summary["camera"] = None
            return summary

        try:
            with bpy.data.libraries.load(str(CAMERA_BLEND_PATH), link=False) as (data_from, data_to):
                camera_candidates = []
                for name in data_from.objects:
                    # Accessing bpy.data.objects[name] *before* it's loaded might cause issues
                    # Instead, we rely on the name matching expected patterns.
                    if "CAMERA" in name.upper() or name == ASSET_CAMERA_NAME:
                        camera_candidates.append(name)
                data_to.objects = camera_candidates
        except Exception as exc:
            print(f"[BLOSM] WARN camera asset append failed: {exc}")
            return summary

        # After loading, the objects should be available in bpy.data.objects
        # Find the actual camera object, prioritizing ASSET_CAMERA_NAME
        camera_obj = bpy.data.objects.get(ASSET_CAMERA_NAME)
        if camera_obj is None:
            # If exact name not found, iterate through newly appended objects
            for obj_name in data_to.objects:
                candidate = bpy.data.objects.get(obj_name)
                if candidate and candidate.type == 'CAMERA':
                    camera_obj = candidate
                    if obj_name != ASSET_CAMERA_NAME:
                        print(f"[BLOSM] WARN ASSET_CAMERA not found by exact name; using first appended camera: {obj_name}")
                    break
        
        if camera_obj is not None:
            camera_created = True

    if camera_obj is None:
        summary["camera"] = None
        return summary

    linked_to_cameras = False
    if cameras_coll not in getattr(camera_obj, "users_collection", []):
        try:
            cameras_coll.objects.link(camera_obj)
            linked_to_cameras = True
        except Exception:
            pass

    if scene.collection and cameras_coll.name not in {child.name for child in scene.collection.children}:
        try:
            scene.collection.children.link(cameras_coll)
        except Exception:
            pass

    safe_area_configured = False
    data = getattr(camera_obj, "data", None)
    if data is not None:
        try:
            if hasattr(data, "show_safe_areas"):
                data.show_safe_areas = True
            safe_area_configured = True # Assuming pre-configured if show_safe_areas is enabled
        except Exception as exc:
            print(f"[BLOSM] WARN camera safe areas update failed: {exc}")

    summary["camera"] = camera_obj
    summary["created"] = camera_created
    summary["linked_to_cameras"] = linked_to_cameras
    summary["safe_area_configured"] = safe_area_configured
    return summary


def _ensure_car_trail_node_group() -> bpy.types.NodeTree | None:
    ng = bpy.data.node_groups.get(CAR_TRAIL_NODE_GROUP_NAME)
    if ng:
        return ng

    path = route_assets.CAR_BLEND_PATH
    candidate = None
    try:
        with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
            candidates = [name for name in (getattr(data_from, 'node_groups', None) or []) if 'Geometry Nodes' in name]
            if candidates:
                candidate = candidates[0]
                data_to.node_groups = [candidate]
    except Exception as exc:
        print(f"[BLOSM] WARN car trail node group append failed: {exc}")
        return None

    if candidate and candidate in bpy.data.node_groups:
        base = bpy.data.node_groups.get(candidate)
        try:
            copy = base.copy()
            copy.name = CAR_TRAIL_NODE_GROUP_NAME
            return copy
        except Exception as exc:
            print(f"[BLOSM] WARN car trail node group copy failed: {exc}")
            return base
    return None


def _find_route_curve(scene: Optional[bpy.types.Scene]) -> Optional[bpy.types.Object]:
    """Resolve the OSM route curve object.

    Preference order:
    1) Objects tagged with blosm_role == "route_curve_osm"
    2) Name-based fallbacks ("ROUTE", "Route")
    """
    candidates = []
    if scene is not None:
        try:
            candidates = list(getattr(scene, "objects", []) or [])
        except Exception:
            candidates = []
    if not candidates:
        candidates = list(getattr(bpy.data, "objects", []) or [])
    for obj in candidates:
        try:
            if getattr(obj, "type", None) == "CURVE" and obj.get("blosm_role") == ROUTE_ROLE_TAG:
                return obj
        except Exception:
            continue
    return bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")


def _configure_car_trail_drivers(curve_data: bpy.types.Curve, car_obj: Optional[bpy.types.Object]) -> bool:
    if curve_data is None or car_obj is None:
        return False

    follow = next((c for c in car_obj.constraints if c.type == 'FOLLOW_PATH'), None)
    if follow is None:
        print("[BLOSM] WARN car trail driver target constraint missing")
        return False

    anim = curve_data.animation_data_create()
    drivers = getattr(anim, "drivers", None) or []
    for prop, _ in CAR_TRAIL_BEVEL_DRIVERS:
        for existing in list(drivers):
            if existing.data_path == prop:
                anim.drivers.remove(existing)

    created = False
    for prop, expression in CAR_TRAIL_BEVEL_DRIVERS:
        try:
            fcurve = curve_data.driver_add(prop)
            driver = fcurve.driver
            driver.type = 'SCRIPTED'
            driver.expression = expression

            var = driver.variables.new()
            var.name = 'offset_factor'
            target = var.targets[0]
            target.id = car_obj
            target.data_path = f'constraints["{follow.name}"].offset_factor'
            created = True
        except Exception as exc:
            print(f"[BLOSM] WARN car trail driver setup failed for {prop}: {exc}")

    return created


def _append_car_trail_template() -> bpy.types.Object:
    """Append the CAR_TRAIL template object from ASSET_CAR_TRAIL.blend.

    Raises when the asset or object is missing to fail loudly during pipeline execution.
    """
    if not CAR_TRAIL_TEMPLATE_BLEND.exists():
        raise RuntimeError(f"CAR_TRAIL template asset missing: {CAR_TRAIL_TEMPLATE_BLEND}")

    template_obj_name = CAR_TRAIL_OBJECT_NAME
    try:
        with bpy.data.libraries.load(str(CAR_TRAIL_TEMPLATE_BLEND), link=False) as (data_from, data_to):
            names = getattr(data_from, "objects", []) or []
            if template_obj_name not in names:
                raise RuntimeError(f"CAR_TRAIL template object '{template_obj_name}' not found in {CAR_TRAIL_TEMPLATE_BLEND}")
            data_to.objects = [template_obj_name]
    except Exception as exc:
        raise RuntimeError(f"CAR_TRAIL template append failed: {exc}") from exc

    tmpl = bpy.data.objects.get(template_obj_name)
    if tmpl is None:
        raise RuntimeError(f"CAR_TRAIL template append yielded no object named '{template_obj_name}'")
    return tmpl


def _apply_car_trail_template_settings(template_obj: Optional[bpy.types.Object], runtime_obj: bpy.types.Object) -> None:
    """Copy relevant settings from template CAR_TRAIL onto the runtime CAR_TRAIL.

    Does NOT touch runtime_obj.matrix_world so that the transform equality
    invariant with ROUTE remains intact.
    """
    if template_obj is None or runtime_obj is None:
        return

    src_data = getattr(template_obj, "data", None)
    dst_data = getattr(runtime_obj, "data", None)

    # Copy curve data settings (bevel, fill, resolution, etc.) without altering geometry.
    if isinstance(src_data, bpy.types.Curve) and isinstance(dst_data, bpy.types.Curve):
        curve_attrs = (
            "bevel_object",
            "bevel_mode",
            "bevel_depth",
            "bevel_resolution",
            "fill_mode",
            "resolution_u",
            "resolution_v",
            "use_radius",
            "taper_radius_mode",
            "extrude",
            "offset",
        )
        for attr in curve_attrs:
            if hasattr(src_data, attr) and hasattr(dst_data, attr):
                try:
                    setattr(dst_data, attr, getattr(src_data, attr))
                except Exception:
                    pass

    # Copy basic object-level display/visibility flags.
    obj_attrs = ("display_type", "display_bounds_type", "display_size", "hide_viewport", "hide_render")
    for attr in obj_attrs:
        if hasattr(template_obj, attr) and hasattr(runtime_obj, attr):
            try:
                setattr(runtime_obj, attr, getattr(template_obj, attr))
            except Exception:
                pass

    # Copy custom properties.
    try:
        for key, value in template_obj.items():
            runtime_obj[key] = value
    except Exception:
        pass

    # Rebuild modifier stack to mirror template (drivers will be reconfigured separately).
    try:
        for m in list(runtime_obj.modifiers):
            runtime_obj.modifiers.remove(m)
    except Exception:
        pass

    for src_mod in template_obj.modifiers:
        try:
            new_mod = runtime_obj.modifiers.new(name=src_mod.name, type=src_mod.type)
        except Exception:
            continue
        # Copy common flags.
        for attr in ("show_viewport", "show_render"):
            if hasattr(src_mod, attr) and hasattr(new_mod, attr):
                try:
                    setattr(new_mod, attr, getattr(src_mod, attr))
                except Exception:
                    pass
        # For Geometry Nodes modifiers, copy the node group.
        if src_mod.type == "NODES":
            try:
                new_mod.node_group = getattr(src_mod, "node_group", None)
            except Exception:
                pass
            try:
                for key in src_mod.keys():
                    new_mod[key] = src_mod[key]
            except Exception:
                pass


# --- CAR_TRAIL resample helpers (from provided script) ---
def spline_to_polyline_world(obj, spline, samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT):
    mw = obj.matrix_world
    pts = []

    if spline.type == 'BEZIER':
        bps = spline.bezier_points
        count = len(bps)
        cyclic = spline.use_cyclic_u
        if count < 2:
            return []
        last_index = count if not cyclic else count + 1

        for i in range(last_index - 1):
            p0 = bps[i % count]
            p1 = bps[(i + 1) % count]

            seg = interpolate_bezier(
                mw @ p0.co,
                mw @ p0.handle_right,
                mw @ p1.handle_left,
                mw @ p1.co,
                samples_per_segment
            )

            if pts:
                seg = seg[1:]
            pts.extend(seg)

    elif spline.type in {'POLY', 'NURBS'}:
        spos = spline.points
        count = len(spos)
        cyclic = spline.use_cyclic_u
        if count < 2:
            return []

        if spline.type == 'POLY':
            samples_per_segment = 1

        def point_world(p):
            co = p.co
            w = co.w if co.w != 0.0 else 1.0
            return mw @ Vector((co.x / w, co.y / w, co.z / w))

        indices = range(count if not cyclic else count + 1)

        for i in indices:
            p0 = spos[i % count]
            p1 = spos[(i + 1) % count] if i + 1 < count or cyclic else None

            p0w = point_world(p0)
            if p1 is None:
                pts.append(p0w)
                break

            p1w = point_world(p1)

            for j in range(samples_per_segment + 1):
                t = j / float(samples_per_segment)
                pw = p0w.lerp(p1w, t)
                if pts and (pw - pts[-1]).length < 1e-9:
                    continue
                pts.append(pw)
    else:
        return []

    if not pts:
        return []

    clean = [pts[0]]
    for p in pts[1:]:
        if (p - clean[-1]).length > 1e-9:
            clean.append(p)
    return clean


def _curve_world_polyline(obj, samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT):
    if obj is None or getattr(obj, "type", None) != "CURVE":
        return []
    data = getattr(obj, "data", None)
    if data is None or getattr(data, "splines", None) is None:
        return []
    pts = []
    for spline in data.splines:
        pts.extend(spline_to_polyline_world(obj, spline, samples_per_segment))
    return pts


def resample_polyline(points, spacing, cyclic=False):
    if len(points) < 2:
        return points[:]

    work_pts = points + [points[0]] if cyclic else points[:]

    seg_lengths = []
    total_length = 0.0
    for i in range(len(work_pts) - 1):
        d = (work_pts[i + 1] - work_pts[i]).length
        seg_lengths.append(d)
        total_length += d

    if total_length == 0.0:
        return [work_pts[0]]

    num_intervals = max(int(round(total_length / spacing)), 1)
    real_spacing = total_length / num_intervals

    result = [work_pts[0]]

    current_seg = 0
    seg_start = work_pts[0]
    seg_end = work_pts[1]
    seg_accum = 0.0

    for i in range(1, num_intervals):
        target_dist = i * real_spacing

        while current_seg < len(seg_lengths) - 1 and seg_accum + seg_lengths[current_seg] < target_dist:
            seg_accum += seg_lengths[current_seg]
            current_seg += 1
            seg_start = work_pts[current_seg]
            seg_end = work_pts[current_seg + 1]

        seg_len = seg_lengths[current_seg]
        if seg_len == 0.0:
            continue

        t = (target_dist - seg_accum) / seg_len
        p = seg_start.lerp(seg_end, t)
        result.append(p)

    if not cyclic:
        result.append(work_pts[-1])

    return result


def _resample_curve_to_polyline_world(
    obj,
    spacing=CAR_TRAIL_RESAMPLE_SPACING,
    samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT,
):
    """Return a resampled world-space polyline for the given curve without modifying it."""
    if obj is None or getattr(obj, "type", None) != "CURVE":
        return []
    # If this is the already-resampled CAR_TRAIL at spec spacing, avoid double resampling
    if getattr(obj, "name", "") == CAR_TRAIL_OBJECT_NAME and abs(spacing - CAR_TRAIL_RESAMPLE_SPACING) < 1e-6:
        return _curve_world_polyline(obj, samples_per_segment=samples_per_segment)
    pts = []
    data = getattr(obj, "data", None)
    if data is None or getattr(data, "splines", None) is None:
        return pts
    for spline in data.splines:
        poly_world = spline_to_polyline_world(obj, spline, samples_per_segment)
        if len(poly_world) < 2:
            continue
        pts.extend(
            resample_polyline(
                poly_world,
                spacing=spacing,
                cyclic=spline.use_cyclic_u,
            )
        )
    return pts


def resample_curve_object(
    obj,
    spacing=CAR_TRAIL_RESAMPLE_SPACING,
    samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT,
):
    if obj.type != 'CURVE':
        raise TypeError("Target object must be a Curve")

    curve = obj.data
    mw_inv = obj.matrix_world.inverted()
    new_splines_data = []

    for spline in curve.splines:
        poly_world = spline_to_polyline_world(obj, spline, samples_per_segment)
        if len(poly_world) < 2:
            continue

        resampled_world = resample_polyline(
            poly_world,
            spacing=spacing,
            cyclic=spline.use_cyclic_u
        )

        resampled_local = [mw_inv @ p for p in resampled_world]
        new_splines_data.append((spline.use_cyclic_u, resampled_local))

    while curve.splines:
        curve.splines.remove(curve.splines[0])

    for cyclic, pts_local in new_splines_data:
        if len(pts_local) < 2:
            continue

        new_spline = curve.splines.new(type='POLY')
        new_spline.use_cyclic_u = cyclic
        new_spline.points.add(len(pts_local) - 1)
        for i, p in enumerate(pts_local):
            new_spline.points[i].co = (p.x, p.y, p.z, 1.0)


def run_resample_on_car_trail():
    obj = bpy.data.objects.get(CAR_TRAIL_OBJECT_NAME)
    if obj is None:
        raise RuntimeError(f"Object '{CAR_TRAIL_OBJECT_NAME}' not found.")
    if obj.type != 'CURVE':
        raise TypeError(f"Object '{CAR_TRAIL_OBJECT_NAME}' is not a CURVE (found {obj.type}).")

    resample_curve_object(
        obj,
        spacing=CAR_TRAIL_RESAMPLE_SPACING,
        samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT
    )
    print(f"Resampled curve '{obj.name}' with spacing {CAR_TRAIL_RESAMPLE_SPACING}")


def _force_car_trail_polyline_from_route(scene: Optional[bpy.types.Scene]) -> bool:
    """Rebuild CAR_TRAIL splines from the resampled ROUTE polyline to guarantee equivalence."""
    route_obj = _find_route_curve(scene)
    car_trail = bpy.data.objects.get(CAR_TRAIL_OBJECT_NAME)
    if route_obj is None or car_trail is None or getattr(car_trail, "type", None) != "CURVE":
        return False

    pts_world = _resample_curve_to_polyline_world(
        route_obj,
        spacing=CAR_TRAIL_RESAMPLE_SPACING,
        samples_per_segment=CAR_TRAIL_SAMPLES_PER_SEGMENT,
    )
    if len(pts_world) < 2:
        return False

    curve = car_trail.data
    mw_inv = car_trail.matrix_world.inverted()
    resampled_local = [mw_inv @ p for p in pts_world]

    while curve.splines:
        curve.splines.remove(curve.splines[0])

    new_spline = curve.splines.new(type='POLY')
    new_spline.use_cyclic_u = False
    new_spline.points.add(len(resampled_local) - 1)
    for i, p in enumerate(resampled_local):
        new_spline.points[i].co = (p.x, p.y, p.z, 1.0)
    return True


def _ensure_car_trail_material(scene: Optional[bpy.types.Scene]) -> bool:
    """Ensure CAR_TRAIL uses CAR_TRAIL_SHADER material only."""
    car_trail = bpy.data.objects.get(CAR_TRAIL_OBJECT_NAME)
    if car_trail is None or getattr(car_trail, "type", None) != "CURVE":
        return False

    mat = bpy.data.materials.get("CAR_TRAIL_SHADER")
    if mat is None:
        path = CAR_TRAIL_TEMPLATE_BLEND
        try:
            with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
                names = getattr(data_from, "materials", []) or []
                if "CAR_TRAIL_SHADER" in names:
                    data_to.materials = ["CAR_TRAIL_SHADER"]
        except Exception as exc:
            print(f"[BLOSM] WARN car trail material append failed: {exc}")
        mat = bpy.data.materials.get("CAR_TRAIL_SHADER")

    if mat is None:
        print("[BLOSM] WARN CAR_TRAIL_SHADER material missing")
        return False

    try:
        mats = car_trail.data.materials
        if mats:
            mats[0] = mat
        else:
            mats.append(mat)
        while len(mats) > 1:
            mats.pop(index=-1)
        return True
    except Exception as exc:
        print(f"[BLOSM] WARN setting CAR_TRAIL material failed: {exc}")
        return False


def _build_car_trail_from_route(scene: Optional[bpy.types.Scene]) -> bpy.types.Object | None:
    if scene is None:
        return None

    # Prefer explicit scene.blosm route curve tracking when available
    route_obj = None
    addon = getattr(getattr(scene, "blosm", None), "__class__", None)
    props = getattr(scene, "blosm", None)
    if props is not None:
        try:
            if getattr(props, "route_curve_obj", None) is not None:
                route_obj = props.route_curve_obj
            elif getattr(props, "route_curve_name", ""):
                route_obj = bpy.data.objects.get(props.route_curve_name)
        except Exception:
            route_obj = None

    if route_obj is None:
        route_obj = _find_route_curve(scene)
    if route_obj is None:
        return None

    car_collection = bpy.data.collections.get('ASSET_CAR')
    if car_collection is None:
        return None

    existing = bpy.data.objects.get(CAR_TRAIL_OBJECT_NAME)
    if existing:
        for coll in list(getattr(existing, 'users_collection', []) or []):
            coll.objects.unlink(existing)
        bpy.data.objects.remove(existing, do_unlink=True)

    # Append CAR_TRAIL template (if available) so we can later copy its settings.
    template_obj = _append_car_trail_template()
    if template_obj.name == CAR_TRAIL_OBJECT_NAME:
        try:
            template_obj.name = f"{CAR_TRAIL_OBJECT_NAME}_TEMPLATE"
        except Exception:
            pass

    # CAR_TRAIL must be a runtime duplicate of the OSM route curve,
    # never a curve imported from an asset .blend.
    car_trail_data = route_obj.data.copy()
    car_trail_data.name = f"{CAR_TRAIL_OBJECT_NAME}_DATA"
    car_trail = bpy.data.objects.new(CAR_TRAIL_OBJECT_NAME, car_trail_data)

    # Ensure CAR_TRAIL uses the exact same transform as the finalized
    # OSM route curve.
    try:
        car_trail.matrix_world = route_obj.matrix_world.copy()
    except Exception:
        car_trail.location = route_obj.location
        car_trail.rotation_euler = route_obj.rotation_euler
        car_trail.scale = route_obj.scale

    try:
        car_collection.objects.link(car_trail)
    except RuntimeError:
        pass

    # Tag roles for robust resolution in saved files
    try:
        route_obj["blosm_role"] = ROUTE_ROLE_TAG
    except Exception:
        pass
    try:
        car_trail["blosm_role"] = CAR_TRAIL_ROLE_TAG
    except Exception:
        pass

    # Apply template settings verbatim (curve data, modifiers, object flags) if available.
    _apply_car_trail_template_settings(template_obj, car_trail)
    # Remove the temporary template object to avoid name collisions.
    try:
        tmpl_data = getattr(template_obj, "data", None)
        bpy.data.objects.remove(template_obj, do_unlink=True)
        if tmpl_data and tmpl_data.users == 0:
            bpy.data.curves.remove(tmpl_data, do_unlink=True)
    except Exception:
        pass

    # Ensure GN node group and drivers are wired in a runtime-safe way.
    car_obj = _resolve_car(scene)
    if car_obj is None:
        print("[BLOSM] WARN car object not resolved for trail drivers")

    node_group = _ensure_car_trail_node_group()
    if node_group:
        # Prefer an existing NODES modifier from the template; otherwise create one.
        nodes_mod = next((m for m in car_trail.modifiers if m.type == 'NODES'), None)
        if nodes_mod and not getattr(nodes_mod, "node_group", None):
            nodes_mod.node_group = node_group
        elif nodes_mod is None:
            mod = car_trail.modifiers.new(name='CarTrailGeo', type='NODES')
            mod.node_group = node_group
    else:
        print("[BLOSM] WARN car trail node group unavailable")

    _configure_car_trail_drivers(car_trail.data, car_obj)

    data = getattr(car_trail, "data", None)
    if data is not None and getattr(data, "bevel_object", None) is None:
        bevel_source = getattr(route_obj, "data", None)
        bevel_obj = None
        if bevel_source is not None and getattr(bevel_source, "bevel_object", None) is not None:
            bevel_obj = bevel_source.bevel_object
        else:
            bevel_obj = bpy.data.objects.get("_profile_curve")
        if bevel_obj is None:
            # Create a simple fallback bevel profile curve; link into ASSET_CAR if possible
            try:
                bevel_curve = bpy.data.curves.new(name="_profile_curve_DATA", type='CURVE')
                bevel_curve.dimensions = '3D'
                spline = bevel_curve.splines.new('BEZIER')
                spline.bezier_points.add(1)
                spline.bezier_points[0].co = (0.0, 0.1, 0.0)
                spline.bezier_points[1].co = (0.0, -0.1, 0.0)
                bevel_obj = bpy.data.objects.new("_profile_curve", bevel_curve)
                try:
                    car_collection.objects.link(bevel_obj)
                except Exception:
                    bpy.context.scene.collection.objects.link(bevel_obj)
            except Exception as exc_create:
                print(f"[BLOSM] WARN fallback profile curve creation failed: {exc_create}")
                bevel_obj = None

        if bevel_obj is not None:
            try:
                data.bevel_object = bevel_obj
                # Ensure profile is present in ASSET_CAR collection
                if bevel_obj not in getattr(bevel_obj, "users_collection", []):
                    try:
                        car_collection.objects.link(bevel_obj)
                    except Exception:
                        pass
            except Exception as exc_inner:
                print(f"[BLOSM] WARN car trail bevel assign failed: {exc_inner}")

    return car_trail

# --------- Attribute application from a text file (object + GN) ---------
import ast

def _literal(value_str):
    try:
        return ast.literal_eval(value_str)
    except Exception:
        if value_str in {"True", "False", "None"}:
            return eval(value_str)
        return value_str

def _iter_attributes_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(("#", "//", ";")):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            yield key.strip(), val.strip()

def _first_nodes_modifier(obj):
    for m in obj.modifiers:
        if m.type == 'NODES':
            return m
    return None

def _nodes_modifier_by_name(obj, name):
    for m in obj.modifiers:
        if m.type == 'NODES' and m.name == name:
            return m
    return None

def _set_gn_input(mod, socket_name, value):
    ng = getattr(mod, 'node_group', None)
    if not ng:
        return False, "no-node-group"
    try:
        if hasattr(mod, socket_name):
            setattr(mod, socket_name, value)
            return True, "modifier-prop"
    except Exception as e:
        return False, f"prop-error: {e}"
    try:
        for s in ng.inputs:
            if s.name == socket_name:
                if hasattr(mod, socket_name):
                    setattr(mod, socket_name, value)
                    return True, "modifier-prop-fallback"
                return False, "socket-not-exposed"
        return False, "socket-not-found"
    except Exception as e:
        return False, f"inputs-error: {e}"

def _set_modifier_property(obj, mod_name, prop, value):
    m = obj.modifiers.get(mod_name)
    if not m:
        return False, "modifier-not-found"
    try:
        setattr(m, prop, value)
        return True, "ok"
    except Exception as e:
        return False, f"setattr-error: {e}"

def _apply_attribute_pairs(base_object, pairs_iter):
    """Apply object + GN settings from an iterator of (key, raw_val) pairs.
    Mirrors apply_import_attributes() but works without a temp file.
    """
    if not base_object:
        print("[FP][ATTR] No base object.")
        return False

    applied = []
    for key, raw_val in pairs_iter:
        if key.startswith("MOD[") and "]" in key:
            mod_name, prop = key[4:].split("]", 1)
            prop = prop.lstrip(":").strip()
            ok, why = _set_modifier_property(base_object, mod_name, prop, _literal(raw_val))
            applied.append((key, ok, why))
            continue
        if key.startswith("GN[") and "]" in key:
            mod_name, socket = key[3:].split("]", 1)
            socket = socket.lstrip(":").strip()
            mod = _nodes_modifier_by_name(base_object, mod_name)
            ok, why = (_set_gn_input(mod, socket, _literal(raw_val)) if mod else (False, "nodes-mod-not-found"))
            applied.append((key, ok, why))
            continue
        if key.startswith("GN:"):
            socket = key[3:].strip()
            mod = _first_nodes_modifier(base_object)
            ok, why = (_set_gn_input(mod, socket, _literal(raw_val)) if mod else (False, "no-nodes-mod"))
            applied.append((key, ok, why))
            continue
        val = _literal(raw_val)
        try:
            if hasattr(base_object, key):
                setattr(base_object, key, val)
                applied.append((key, True, "object-prop"))
            else:
                applied.append((key, False, "object-prop-not-found"))
        except Exception as e:
            applied.append((key, False, f"object-prop-error: {e}"))

    try:
        bpy.context.view_layer.update()
    except Exception:
        pass

    ok_n = sum(1 for _, ok, _ in applied if ok)
    print(f"[FP][ATTR] Applied {ok_n}/{len(applied)} to '{base_object.name}'.")
    for k, ok, why in applied:
        print(f"   - {k} => {'OK' if ok else 'FAIL'} ({why})")
    return True

def apply_import_attributes(base_object, attributes_file):
    """
    Apply object + GN settings from a simple key=value text file.
    Supported keys:
      � Object: location, rotation_euler, scale, show_name, hide_viewport, hide_render, ...
      � GN (first): GN:Socket Name = <value>
      � GN (by mod): GN[ModifierName]:Socket Name = <value>
      � Modifier:   MOD[ModifierName]:prop = <value>
    Values: Python-like literals (tuples, floats, ints, True/False).
    """
    if not base_object:
        print("[FP][ATTR] No base object.")
        return False

    applied = []
    for key, raw_val in _iter_attributes_lines(attributes_file):
        if key.startswith("MOD[") and "]" in key:
            mod_name, prop = key[4:].split("]", 1)
            prop = prop.lstrip(":").strip()
            ok, why = _set_modifier_property(base_object, mod_name, prop, _literal(raw_val))
            applied.append((key, ok, why))
            continue
        if key.startswith("GN[") and "]" in key:
            mod_name, socket = key[3:].split("]", 1)
            socket = socket.lstrip(":").strip()
            mod = _nodes_modifier_by_name(base_object, mod_name)
            ok, why = (_set_gn_input(mod, socket, _literal(raw_val)) if mod else (False, "nodes-mod-not-found"))
            applied.append((key, ok, why))
            continue
        if key.startswith("GN:"):
            socket = key[3:].strip()
            mod = _first_nodes_modifier(base_object)
            ok, why = (_set_gn_input(mod, socket, _literal(raw_val)) if mod else (False, "no-nodes-mod"))
            applied.append((key, ok, why))
            continue
        val = _literal(raw_val)
        try:
            if hasattr(base_object, key):
                setattr(base_object, key, val)
                applied.append((key, True, "object-prop"))
            else:
                applied.append((key, False, "object-prop-not-found"))
        except Exception as e:
            applied.append((key, False, f"object-prop-error: {e}"))

    try:
        bpy.context.view_layer.update()
    except Exception:
        pass

    ok_n = sum(1 for _, ok, _ in applied if ok)
    print(f"[FP][ATTR] Applied {ok_n}/{len(applied)} to '{base_object.name}'.")
    for k, ok, why in applied:
        print(f"   - {k} => {'OK' if ok else 'FAIL'} ({why})")
    return True
# --------- End attribute helper ---------

# --------- Master attributes file (single file with sections) ---------
def _parse_master_attributes(path: Path) -> dict[str, list[tuple[str, str]]]:
    """Parse active, uncommented key=value pairs per [Section].
    Returns mapping: section_name -> list[(key, raw_val)].
    """
    result: dict[str, list[tuple[str, str]]] = {}
    if not path.exists():
        return result
    current: str | None = None
    try:
        with path.open('r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith(('#',';','//')):
                    continue
                if line.startswith('[') and line.endswith(']') and len(line) > 2:
                    current = line[1:-1]
                    continue
                if current and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    result.setdefault(current, []).append((key, val))
    except Exception as exc:
        print(f"[FP][ATTR] WARN parse master failed: {exc}")
    return result

def _write_master_file(path: Path, objects: list[bpy.types.Object], active: dict[str, list[tuple[str, str]]]) -> None:
    """Rewrite the master file deterministically.
    - Top: Available Attributes block with copy/paste lines.
    - Then [ObjectName] sections only; include only active (uncommented) entries preserved from existing file.
    """
    header = (
        "# BLOSM Route Asset Attributes\n"
        "# This file drives per-object import attributes.\n"
        "# How to use: Under a section [ObjectName], add or uncomment lines you want to apply, then save and re-run.\n"
        "#\n"
        "# Available Attributes (copy/paste under a [Section]):\n"
        "# scale = (1.0, 1.0, 1.0)\n"
        "# location = (0.0, 0.0, 0.0)\n"
        "# rotation_euler = (0.0, 0.0, 0.0)\n"
        "# show_name = True\n"
        "# hide_viewport = True\n"
        "# hide_render = True\n"
        "# GN:Socket Name = 0.0\n"
        "# GN[ModifierName]:Socket Name = 0.0\n"
        "# MOD[ModifierName]:property = 0\n"
        "\n"
    )
    lines: list[str] = [header]
    # Preserve discovery order
    for obj in objects:
        lines.append(f"[{obj.name}]")
        pairs = active.get(obj.name, [])
        for k, v in pairs:
            lines.append(f"{k} = {v}")
        lines.append("")
    try:
        path.write_text("\n".join(lines), encoding='utf-8')
        print(f"[FP][ATTR] Master file written: {path}")
    except Exception as exc:
        print(f"[FP][ATTR] WARN master write failed: {exc}")
# --------- End master file helpers ---------

# --------- Load master into Text Editor ---------
def _try_focus_text_editor(context: bpy.types.Context, text: bpy.types.Text) -> bool:
    if getattr(bpy.app, "background", False):
        return False
    screen = getattr(context, "screen", None) or getattr(bpy.context, "screen", None)
    if screen is None:
        return False
    for area in screen.areas:
        if getattr(area, "type", None) == "TEXT_EDITOR":
            for space in getattr(area, "spaces", []):
                if getattr(space, "type", None) == "TEXT_EDITOR":
                    try:
                        space.text = text
                        area.tag_redraw()
                        return True
                    except Exception:
                        return False
    return False

def _load_master_attributes_into_text_editor(context: bpy.types.Context, master_path: Path, *, focus: bool = False) -> bool:
    try:
        master_path = Path(master_path)
        if not master_path.exists():
            # Create an empty header if missing
            header = (
                "# BLOSM Route Asset Attributes\n"
                "# Edit: uncomment lines under each [ObjectName] and set values.\n\n"
            )
            master_path.write_text(header, encoding='utf-8')

        name = master_path.name
        text = bpy.data.texts.get(name)
        if text is None:
            try:
                text = bpy.data.texts.load(str(master_path))
            except Exception:
                # Fallback: create and fill
                text = bpy.data.texts.new(name)
                try:
                    content = master_path.read_text(encoding='utf-8')
                    text.write(content)
                except Exception:
                    pass
        else:
            # Refresh content from disk
            try:
                content = master_path.read_text(encoding='utf-8')
                text.clear()
                text.write(content)
            except Exception:
                pass
        try:
            text.filepath = str(master_path)
            text.use_fake_user = True
        except Exception:
            pass
        print(f"[FP][ATTR] Text loaded: {text.name} -> {master_path}")
        if focus:
            _try_focus_text_editor(context, text)
        return True
    except Exception as exc:
        print(f"[FP][ATTR] WARN text load failed: {exc}")
        return False
# --------- End text editor helpers ---------

# --------- Building GeoNodes: set Car Object ---------
def _set_building_geo_nodes_car(scene: Optional[bpy.types.Scene]) -> int:
    """Set the 'Car Object' (OBJECT input) on Building GeoNodes modifiers to ASSET_CAR.
    Uses node interface to find the correct modifier property, robust to 'Socket_X' identifiers.
    Returns count of modifiers updated.
    """
    car_obj = _resolve_car(scene) or bpy.data.objects.get(route_assets.CAR_OBJECT) or bpy.data.objects.get("ASSET_CAR")
    if car_obj is None:
        print("[FP][ATTR] WARN BuildingGN: car object not found (ASSET_CAR)")
        return 0

    def assign_car(mod, obj_name):
        ng = getattr(mod, 'node_group', None)
        if not ng:
            return False
        # Find an OBJECT input whose name contains 'car'
        target_idx = None
        for idx, socket_type, name in route_nodes._iter_group_inputs(ng) or []:
            if socket_type == 'OBJECT' and 'car' in (name or '').casefold():
                target_idx = idx; break
        if target_idx is None:
            return False
        prop = route_nodes._resolve_modifier_input(mod, target_idx)
        if not prop:
            return False
        try:
            mod[prop] = car_obj
            print(f"[FP][ATTR] BuildingGN: set '{prop}' on '{obj_name}' -> OK (car={car_obj.name})")
            return True
        except Exception as exc:
            print(f"[FP][ATTR] BuildingGN: set on '{obj_name}' failed: {exc}")
            return False

    count = 0
    for obj in list(bpy.data.objects):
        try:
            for mod in getattr(obj, 'modifiers', []) or []:
                if getattr(mod, 'type', None) != 'NODES':
                    continue
                mname = getattr(mod, 'name', '') or ''
                if (mname == 'ASSET_BuildingGeoNodes') or ('BuildingGeoNodes' in mname):
                    if assign_car(mod, obj.name):
                        count += 1
        except Exception as exc:
            print(f"[FP][ATTR] BuildingGN: error on '{getattr(obj, 'name', '?')}': {exc}")

    try:
        bpy.context.view_layer.update()
    except Exception:
        pass
    return count

def _explicit_building_geo_car_override(scene: Optional[bpy.types.Scene]) -> int:
    """Explicit override for map_*.osm_buildings objects with a 'BuildingGeo' modifier.
    If modifier has property 'Socket_15', set it to ASSET_CAR and enable show_render.
    Returns count of overrides applied.
    """
    car_obj = _resolve_car(scene) or bpy.data.objects.get(route_assets.CAR_OBJECT) or bpy.data.objects.get('ASSET_CAR')
    if car_obj is None:
        return 0
    applied = 0
    for obj in list(bpy.data.objects):
        name = getattr(obj, 'name', '') or ''
        ncf = name.casefold()
        if not (ncf.startswith('map_') and ncf.endswith('.osm_buildings')):
            continue
        mod = obj.modifiers.get('BuildingGeo')
        if not (mod and getattr(mod, 'type', None) == 'NODES'):
            continue
        if 'Socket_15' in mod.keys():
            try:
                mod['Socket_15'] = car_obj
                mod.show_render = True
                applied += 1
                print(f"[FP][ATTR] BuildingGeo explicit: set Socket_15 on '{obj.name}' -> ASSET_CAR; render=ON")
            except Exception as exc:
                print(f"[FP][ATTR] BuildingGeo explicit: failed on '{obj.name}': {exc}")
    try:
        bpy.context.view_layer.update()
    except Exception:
        pass
    return applied
# --------- End Building GeoNodes helpers ---------

# --------- View3D clip_end scaling ---------
def _scale_view3d_clip_end(context: bpy.types.Context, *, factor: float = 2.5, max_end: float = 1.0e9) -> int:
    """Scale all VIEW_3D space clip_end values by a factor on visible screens.
    Skips in background mode. Returns count of VIEW_3D spaces updated.
    """
    try:
        if getattr(bpy.app, "background", False):
            return 0
        updated = 0
        wm = getattr(bpy.context, 'window_manager', None)
        screens = []
        if wm and getattr(wm, 'windows', None):
            for win in wm.windows:
                scr = getattr(win, 'screen', None)
                if scr and scr not in screens:
                    screens.append(scr)
        if not screens:
            scr = getattr(context, 'screen', None) or getattr(bpy.context, 'screen', None)
            if scr:
                screens = [scr]
        for scr in screens:
            for area in getattr(scr, 'areas', []) or []:
                if getattr(area, 'type', None) != 'VIEW_3D':
                    continue
                for space in getattr(area, 'spaces', []) or []:
                    if getattr(space, 'type', None) != 'VIEW_3D':
                        continue
                    try:
                        old = float(getattr(space, 'clip_end', 0.0))
                        if old <= 0.0:
                            continue
                        new = old * float(factor)
                        if max_end is not None:
                            new = min(new, float(max_end))
                        if abs(new - old) > 1e-6:
                            space.clip_end = new
                            updated += 1
                            print(f"[FP][VIEW] VIEW_3D clip_end: {old:.6g} -> {new:.6g}")
                    except Exception:
                        pass
        if updated:
            try:
                context.area.tag_redraw()  # best-effort
            except Exception:
                pass
        return updated
    except Exception as exc:
        print(f"[FP][VIEW] WARN clip_end scale failed: {exc}")
        return 0
# --------- End view helpers ---------

# --------- Map/osm visibility and view layer exclusion ---------
def _ensure_building_geonodes_visible(scene: Optional[bpy.types.Scene]) -> int:
    """Ensure the ASSET_BuildingGeoNodes modifier is visible in render (and viewport)."""
    count = 0
    for obj in list(bpy.data.objects):
        try:
            for mod in getattr(obj, 'modifiers', []) or []:
                if getattr(mod, 'type', None) != 'NODES':
                    continue
                mname = getattr(mod, 'name', '') or ''
                if (
                    mname == 'ASSET_BuildingGeoNodes'
                    or ('BuildingGeoNodes' in mname)
                    or (mname == 'BuildingGeo')
                    or ('BuildingGeo' in mname)
                ):
                    changed = False
                    if getattr(mod, 'show_render', True) is False:
                        mod.show_render = True
                        changed = True
                    if getattr(mod, 'show_viewport', True) is False:
                        mod.show_viewport = True
                        changed = True
                    if changed:
                        count += 1
                        print(f"[FP][MAP] BuildingGN visible for render on '{obj.name}' (modifier={mname})")
        except Exception:
            pass
    try:
        bpy.context.view_layer.update()
    except Exception:
        pass
    return count


def _sync_buildings_geonodes_from_asset(scene: Optional[bpy.types.Scene]) -> int:
    """Copy ASSET_BuildingGeoNodes modifier settings from ASSET_BUILDINGS.blend.

    Copies all ID-property sockets from the asset modifier to the runtime
    BUILDINGS_GEO modifier, except the car socket (Socket_15) which is
    set separately by _set_building_geo_nodes_car().
    Returns 1 on success, 0 otherwise.
    """
    import bpy

    # Find the source modifier in the asset file

    try:
        path = route_assets.BUILD_BLEND_PATH
        with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
            if "BUILDINGS_GEO" in (data_from.objects or []):
                data_to.objects = ["BUILDINGS_GEO"]
            elif data_from.objects:
                data_to.objects = [data_from.objects[0]]
        src_obj = next((o for o in data_to.objects if o is not None), None)
    except Exception as exc:
        print(f"[FP][MAP] WARN load ASSET_BUILDINGS for GN sync failed: {exc}")
        src_obj = None

    if src_obj is None:
        return 0

    src_mod = src_obj.modifiers.get("ASSET_BuildingGeoNodes")
    if src_mod is None or getattr(src_mod, "type", None) != "NODES":
        try:
            bpy.data.objects.remove(src_obj, do_unlink=True)
        except Exception:
            pass
        return 0

    copied_total = 0
    # Apply to every ASSET_BuildingGeoNodes modifier in the scene, regardless of object name
    for obj in list(bpy.data.objects):
        for dest_mod in getattr(obj, "modifiers", []) or []:
            if getattr(dest_mod, "type", None) != "NODES":
                continue
            dest_name = getattr(dest_mod, "name", "") or ""
            if dest_name not in {"ASSET_BuildingGeoNodes", "BuildingGeo"}:
                continue
            if src_mod.node_group:
                dest_mod.node_group = src_mod.node_group
            if dest_name == "BuildingGeo" and not dest_mod.node_group and src_mod.node_group:
                dest_mod.node_group = src_mod.node_group
            copied = 0
            for key in src_mod.keys():
                if key == "Socket_15":
                    continue
                try:
                    dest_mod[key] = src_mod[key]
                    copied += 1
                except Exception:
                    pass
            copied_total += copied

    try:
        bpy.data.objects.remove(src_obj, do_unlink=True)
    except Exception:
        pass

    try:
        if copied_total:
            bpy.context.view_layer.update()
    except Exception:
        pass
    if copied_total:
        print(f"[FP][MAP] Synced {copied_total} GN sockets from asset onto ASSET_BuildingGeoNodes modifiers")
    return copied_total


def _apply_buildings_geonodes_defaults(scene: Optional[bpy.types.Scene]) -> int:
    """Force key BuildingGeo sockets to known-good defaults after import.

    This is a direct, explicit application of the settings you tuned in the
    asset file so that both BUILDINGS_GEO and map_*.osm_buildings objects
    behave identically, even if asset sync fails."""

    def _apply_defaults(mod: bpy.types.NodesModifier | None) -> bool:
        if mod is None or getattr(mod, "type", None) != "NODES":
            return False
        changed = False
        # Core facade / detail controls
        for key, value in (
            ("Socket_2", 25.0),          # Facade Angle
            ("Socket_3", 500.0),         # Target Face Area
            ("Socket_5", 2),             # Iterations
            ("Socket_6", 30.0),          # Target Edge Length
            ("Socket_7", 1_000_000),     # Max Face Count
            ("Socket_8", 0.5),           # Roof Threshold
            ("Socket_9", 0.0),           # Density (Roof Details)
            ("Socket_10", 2.0),          # Roof Cube Base Scale
            ("Socket_11", -0.5),         # Recess Depth
            ("Socket_12", 1.0),          # Inset Scale
            ("Socket_14", 0.0),          # Lights Seed
            ("Socket_16", 0.3),          # Selection Probability
            ("Socket_17", 200.0),        # Radius
            ("Socket_18", True),         # Details ON
            ("Socket_19", True),         # Second Pass (Glass)
            ("Socket_22", False),        # Camera Gate
            ("Socket_26", False),        # Switch / extra flags
            ("Socket_20", 90.00999450683594),  # Route Gate
            ("Socket_21", 1.0),                # Bases Gate
            ("Socket_24", 1250.0),             # Camera Gate: Distance
            ("Socket_25", 100.0),              # Camera Gate: Padding
        ):
            try:
                if key in mod.keys():
                    if mod[key] != value:
                        mod[key] = value
                        changed = True
                else:
                    mod[key] = value
                    changed = True
            except Exception:
                pass
        return changed

    changed = 0
    # Apply to every ASSET_BuildingGeoNodes and BuildingGeo modifier in the scene
    for obj in list(bpy.data.objects):
        for mod in getattr(obj, "modifiers", []) or []:
            if getattr(mod, "type", None) != "NODES":
                continue
            name = getattr(mod, "name", "") or ""
            if name in {"ASSET_BuildingGeoNodes", "BuildingGeo"}:
                if _apply_defaults(mod):
                    changed += 1

    try:
        if changed:
            bpy.context.view_layer.update()
    except Exception:
        pass
    if changed:
        print(f"[FP][MAP] Applied BuildingGeo defaults on {changed} modifier(s)")
    return changed


def _enforce_buildings_asset_modifier(scene: Optional[bpy.types.Scene]) -> bool:
    """Force the visible BUILDINGS modifier to match the asset values."""
    asset_path = route_assets.BUILD_BLEND_PATH
    asset_mod = None
    try:
        with bpy.data.libraries.load(str(asset_path), link=False) as (data_from, data_to):
            if "BUILDINGS_GEO" in (data_from.objects or []):
                data_to.objects = ["BUILDINGS_GEO"]
            elif data_from.objects:
                data_to.objects = [data_from.objects[0]]
        src_obj = next((o for o in data_to.objects if o is not None), None)
        if src_obj:
            asset_mod = src_obj.modifiers.get("ASSET_BuildingGeoNodes")
    except Exception as exc:
        print(f"[FP][MAP] WARN loading asset for enforcement: {exc}")
        asset_mod = None
    if asset_mod is None:
        return False

    target_obj = bpy.data.objects.get("BUILDINGS")
    if not target_obj:
        return False

    mod = target_obj.modifiers.get("ASSET_BuildingGeoNodes") or target_obj.modifiers.get("BuildingGeo")
    if mod is None:
        return False
    if mod.name != "ASSET_BuildingGeoNodes":
        mod.name = "ASSET_BuildingGeoNodes"
    if asset_mod.node_group and mod.node_group != asset_mod.node_group:
        mod.node_group = asset_mod.node_group

    copied = 0
    for key in asset_mod.keys():
        if key == "Socket_15":
            continue
        try:
            mod[key] = asset_mod[key]
            copied += 1
        except Exception:
            pass
    try:
        bpy.data.objects.remove(src_obj, do_unlink=True)
    except Exception:
        pass

    if copied:
        print(f"[FP][MAP] Enforced asset GN values on BUILDINGS modifier ({copied} keys)")
    return bool(copied)


def _normalize_buildings_geonodes(scene: Optional[bpy.types.Scene]) -> int:
    """Ensure BUILDINGS_GEO uses the same GN modifier layout as the asset file.

    - Keep a single ASSET_BuildingGeoNodes modifier, active.
    - Remove any extra 'BuildingGeo' modifier from BUILDINGS_GEO itself
      (map_*.osm_buildings objects still keep their own BuildingGeo)."""
    changed = 0
    for obj in list(bpy.data.objects):
        for mod in getattr(obj, "modifiers", []) or []:
            if getattr(mod, "type", None) != "NODES":
                continue
            name = getattr(mod, "name", "") or ""
            if name == "ASSET_BuildingGeoNodes":
                if not getattr(mod, "is_active", True):
                    mod.is_active = True
                    changed += 1
                if hasattr(mod, "is_override_data") and not mod.is_override_data:
                    mod.is_override_data = True
                    changed += 1
            elif name == "BuildingGeo":
                # Let explicit overrides keep BuildingGeo on map_*.osm_buildings only
                ncf = (getattr(obj, "name", "") or "").casefold()
                if not (ncf.startswith("map_") and ncf.endswith(".osm_buildings")):
                    try:
                        obj.modifiers.remove(mod)
                        changed += 1
                        print(f"[FP][MAP] Removed extra BuildingGeo modifier from '{obj.name}'")
                    except Exception:
                        pass
    try:
        if changed:
            bpy.context.view_layer.update()
    except Exception:
        pass
    return changed

def _mute_map_route_objects(scene: Optional[bpy.types.Scene]) -> dict:
    """In collections named like 'map_*.osm', hide all objects except ones ending with '_buildings'."""
    summary = {"muted": 0, "kept": 0, "collections": 0}
    if scene is None:
        return summary
    for coll in list(bpy.data.collections):
        name = (getattr(coll, 'name', '') or '')
        name_cf = name.casefold()
        if not (name_cf.startswith('map_') and name_cf.endswith('.osm')):
            continue
        summary["collections"] += 1
        try:
            try:
                objs = list(coll.all_objects)
            except AttributeError:
                objs = list(coll.objects)
            for obj in objs:
                if obj is None:
                    continue
                ends_buildings = obj.name.casefold().endswith('_buildings')
                obj.hide_viewport = not ends_buildings
                obj.hide_render = not ends_buildings
                if ends_buildings:
                    summary["kept"] += 1
                else:
                    summary["muted"] += 1
        except Exception:
            pass
    if summary["collections"]:
        print(f"[FP][MAP] map_*.osm filter: collections={summary['collections']} muted={summary['muted']} kept={summary['kept']}")
    return summary


def _strip_building_materials(scene: Optional[bpy.types.Scene]) -> int:
    """Keep only UniversalShader materials on building meshes after import."""
    summary = route_assets.get_last_summary()
    allowed_names: set[str] = set()
    if summary:
        bld_mat = summary.get("bld_mat")
        if bld_mat:
            allowed_names.add(bld_mat)
    for mat in bpy.data.materials:
        mat_name = getattr(mat, "name", "")
        if "universals shader" in mat_name.lower().replace(" ", "") or "universalshader" in mat_name.lower():
            allowed_names.add(mat_name)
    universal_material = None
    for mat in bpy.data.materials:
        if mat.name in allowed_names:
            universal_material = mat
            break

    changed = 0
    for obj in list(bpy.data.objects):
        if getattr(obj, "type", None) != "MESH":
            continue
        name_cf = (getattr(obj, "name", "") or "").casefold()
        if "building" not in name_cf:
            continue
        slots = getattr(obj, "material_slots", None)
        if not slots:
            continue
        keep: list[bpy.types.Material] = []
        seen: set[str] = set()
        for slot in slots:
            mat = getattr(slot, "material", None)
            if mat and mat.name in allowed_names and mat.name not in seen:
                keep.append(mat)
                seen.add(mat.name)
        if not keep and universal_material:
            keep.append(universal_material)
        current_names = tuple(slot.material.name if slot.material else None for slot in slots)
        target_names = tuple(mat.name for mat in keep)
        if current_names == target_names:
            continue
        try:
            obj.data.materials.clear()
            for mat in keep:
                obj.data.materials.append(mat)
            changed += 1
        except Exception:
            pass
    if changed:
        print(f"[FP][MAP] Stripped non-UniversalShader materials from {changed} building mesh(es)")
    return changed

def _exclude_collection_from_view_layers(scene: Optional[bpy.types.Scene], target_name: str) -> int:
    """Exclude all LayerCollection entries whose collection.name matches target_name (case-insensitive)."""
    if scene is None:
        return 0
    target_cf = (target_name or '').casefold()

    # Check if this is a road-related collection and roads should be kept visible
    from ..road.config import KEEP_ROADS_VISIBLE, ROAD_COLLECTION_NAME
    is_road_collection = (target_name.lower() in ['road', 'highway', 'street', 'way'] or
                          target_name.lower() == ROAD_COLLECTION_NAME.lower())

    if KEEP_ROADS_VISIBLE:
        if is_road_collection:
            return 0

    def visit(layer_coll):
        hits = 0
        try:
            if getattr(layer_coll, 'collection', None):
                cname = (layer_coll.collection.name or '').casefold()
                if cname == target_cf:
                    if getattr(layer_coll, 'exclude', False) is False:
                        layer_coll.exclude = True
                        return 1
            for child in getattr(layer_coll, 'children', []) or []:
                hits += visit(child)
        except Exception:
            pass
        return hits
    total = 0
    for vl in getattr(scene, 'view_layers', []) or []:
        try:
            total += visit(vl.layer_collection)
        except Exception:
            pass
    if total:
        print(f"[FP][MAP] Excluded '{target_name}' from view layers (hits={total})")
    return total
# --------- End map/osm helpers ---------

# --------- Promote buildings + group maps and profiles under .other ---------
def _promote_buildings_and_group_others(scene: Optional[bpy.types.Scene]) -> dict[str, int]:
    """For each map_*.osm collection:
    - Move its *_buildings object out into ASSET_BUILDINGS (exclusive move).
    - Exclude the map_*.osm collection from all view layers.
    - Ensure a parent collection '.other' and move both map_*.osm and 'way_profiles' under it (exclusive from root).
    Returns summary counts.
    """
    summary = {"buildings_moved": 0, "maps_excluded": 0, "maps_grouped": 0, "profiles_grouped": 0}
    if scene is None:
        return summary

    # Ensure destination collections (no '.other' grouping anymore)
    bld_coll = bpy.data.collections.get('ASSET_BUILDINGS')
    if bld_coll is None:
        bld_coll = bpy.data.collections.new('ASSET_BUILDINGS')
        try:
            root = getattr(scene, 'collection', None)
            if root and bld_coll.name not in root.children:
                root.children.link(bld_coll)
        except Exception:
            pass

    def exclusive_move_collection(child: bpy.types.Collection, parent: bpy.types.Collection):
        try:
            root = getattr(scene, 'collection', None)
            if root and root.children.get(child.name):
                root.children.unlink(child)
        except Exception:
            pass
        try:
            if parent.children.get(child.name) is None:
                parent.children.link(child)
        except Exception:
            pass

    # Process map collections
    for coll in list(bpy.data.collections):
        name = (getattr(coll, 'name', '') or '')
        ncf = name.casefold()
        if not (ncf.startswith('map_') and ncf.endswith('.osm')):
            continue
        # Move *_buildings object out to ASSET_BUILDINGS
        buildings_obj = None
        try:
            try:
                objs = list(coll.all_objects)
            except AttributeError:
                objs = list(coll.objects)
            for obj in objs:
                if obj and obj.name.casefold().endswith('_buildings'):
                    buildings_obj = obj
                    break
        except Exception:
            pass
        if buildings_obj is not None:
            # Link to ASSET_BUILDINGS and unlink from original map collection
            try:
                if bld_coll not in buildings_obj.users_collection:
                    bld_coll.objects.link(buildings_obj)
                if coll.objects.get(buildings_obj.name):
                    coll.objects.unlink(buildings_obj)
                # Rename to 'BUILDINGS' (exclusive canonical name)
                try:
                    existing = bpy.data.objects.get('BUILDINGS')
                    if existing is not None and existing is not buildings_obj:
                        # Avoid collision by renaming the old one
                        try:
                            existing.name = 'BUILDINGS_OLD'
                        except Exception:
                            pass
                    if buildings_obj.name != 'BUILDINGS':
                        buildings_obj.name = 'BUILDINGS'
                except Exception:
                    pass
                summary["buildings_moved"] += 1
                print(f"[FP][MAP] Moved '{buildings_obj.name}' to ASSET_BUILDINGS")
            except Exception as exc:
                print(f"[FP][MAP] WARN move buildings '{getattr(buildings_obj,'name',None)}': {exc}")

        # Exclude the map collection from view layers
        try:
            summary["maps_excluded"] += _exclude_collection_from_view_layers(scene, coll.name)
        except Exception:
            pass

        # (No grouping under '.other' – leave map collections where they are)
        pass

    # Do not group way_profiles; leave in place
    wp = bpy.data.collections.get('way_profiles')
    if wp is not None:
        pass

    # Remove legacy '.other' collection if it exists
    other = bpy.data.collections.get('.other')
    if other is not None:
        try:
            for sc in bpy.data.scenes:
                root = getattr(sc, 'collection', None)
                if root and root.children.get(other.name):
                    root.children.unlink(other)
        except Exception:
            pass
        try:
            bpy.data.collections.remove(other)
        except Exception:
            pass

    return summary
# --------- End promote/group helpers ---------

# --------- Car collection rehome ---------
def _rehome_car_collection(scene: Optional[bpy.types.Scene]) -> dict[str, int | str]:
    """Create collection 'ASSET_CAR', link the ASSET_CAR object into it, and remove 'BLOSM_Assets'.
    Order of ops: ensure new collection -> link car -> unlink from old -> unlink & remove BLOSM_Assets.
    Returns a small summary dict.
    """
    summary: dict[str, int | str] = {"created": 0, "linked": 0, "unlinked_old": 0, "assets_coll_removed": 0}
    try:
        car_name = getattr(route_assets, 'CAR_OBJECT', 'ASSET_CAR')
        assets_coll_name = getattr(route_assets, 'ASSETS_COLLECTION_NAME', 'BLOSM_Assets')
        car_obj = bpy.data.objects.get(car_name) or _resolve_car(scene)
        if car_obj is None:
            print(f"[FP][CARCOL] WARN car object '{car_name}' not found")
            return summary

        # Ensure/create new collection named like the car object
        new_coll = bpy.data.collections.get(car_name)
        if new_coll is None:
            new_coll = bpy.data.collections.new(car_name)
            summary["created"] = 1
        # Link new collection to scene root if not linked
        if scene is not None:
            root = getattr(scene, 'collection', None)
            if root and root.children.get(new_coll.name) is None:
                try:
                    root.children.link(new_coll)
                except RuntimeError:
                    pass
        # Make sure object is linked to the new collection
        try:
            if new_coll not in car_obj.users_collection:
                new_coll.objects.link(car_obj)
                summary["linked"] = 1
        except Exception:
            pass
        # Unlink car from other collections (especially BLOSM_Assets)
        for coll in list(getattr(car_obj, 'users_collection', []) or []):
            if coll is None or coll == new_coll:
                continue
            try:
                coll.objects.unlink(car_obj)
                summary["unlinked_old"] = summary.get("unlinked_old", 0) + 1
            except Exception:
                pass

        # Remove BLOSM_Assets collection
        assets_coll = bpy.data.collections.get(assets_coll_name)
        if assets_coll is not None:
            # unlink from all scenes' roots first
            for sc in bpy.data.scenes:
                try:
                    parent = getattr(sc, 'collection', None)
                    if parent and parent.children.get(assets_coll.name):
                        parent.children.unlink(assets_coll)
                except Exception:
                    pass
            try:
                bpy.data.collections.remove(assets_coll)
                summary["assets_coll_removed"] = 1
                print(f"[FP][CARCOL] Removed collection '{assets_coll_name}'")
            except RuntimeError as exc:
                print(f"[FP][CARCOL] WARN remove '{assets_coll_name}' failed: {exc}")

        return summary
    except Exception as exc:
        print(f"[FP][CARCOL] WARN rehome failed: {exc}")
        return summary
# --------- End car collection helpers ---------

# --------- RouteTrace diagnostic (non-destructive) ---------
def _check_route_trace(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    """Report RouteTrace modifier, node group, and driver status on the route curve.
    Prints concise [FP][TRACE] logs and returns a summary dict.
    """
    route_obj = None
    try:
        # Prefer the resolver from anim.py if available
        route_obj = route_anim._resolve_route_object(scene)
    except Exception:
        route_obj = None
    if route_obj is None:
        # Heuristic: any curve with our RouteTrace modifier
        for obj in bpy.data.objects:
            try:
                if getattr(obj, 'type', None) != 'CURVE':
                    continue
                mod = obj.modifiers.get(getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace'))
                if mod and getattr(mod, 'type', None) == 'NODES':
                    route_obj = obj
                    break
            except Exception:
                pass

    modifier = route_obj.modifiers.get(getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace')) if route_obj else None
    ng = getattr(modifier, 'node_group', None)

    prop_name = None
    try:
        idx = route_anim._find_gn_input_index(ng, 'FLOAT', 'OffsetFactor') if ng else None
        prop_name = route_anim._resolve_gn_input_property(modifier, idx) if (modifier and idx is not None) else None
    except Exception:
        prop_name = None

    driver_present = False
    expr = None
    data_path = None
    if route_obj and modifier and prop_name:
        data_path = f'modifiers["{modifier.name}"]["{prop_name}"]'
        ad = getattr(route_obj, 'animation_data', None)
        if ad and getattr(ad, 'drivers', None):
            for fc in ad.drivers:
                if getattr(fc, 'data_path', None) == data_path:
                    driver_present = True
                    try:
                        expr = getattr(fc.driver, 'expression', None)
                    except Exception:
                        expr = None
                    break

    # Scene vars snapshot
    scene_vars = {
        'start': getattr(scene, 'blosm_anim_start', None) if scene else None,
        'end': getattr(scene, 'blosm_anim_end', None) if scene else None,
        'lead': getattr(scene, 'blosm_lead_frames', None) if scene else None,
    }

    print("[FP][TRACE] route='{r}' mod={m} group='{g}' prop='{p}' driver={d}".format(
        r=getattr(route_obj, 'name', None),
        m=bool(modifier and getattr(modifier, 'type', None) == 'NODES'),
        g=getattr(ng, 'name', None),
        p=prop_name,
        d=driver_present,
    ))
    if route_obj and modifier and (getattr(ng, 'name', None) not in (None, 'ASSET_RouteTrace')):
        print(f"[FP][TRACE][WARN] node group mismatch: expected 'ASSET_RouteTrace', got '{ng.name}'")
    if route_obj and modifier and not driver_present:
        print(f"[FP][TRACE][WARN] driver missing on {data_path}")
    if route_obj is None:
        print("[FP][TRACE][WARN] route curve not resolved during finalizer")
    if modifier is None or getattr(modifier, 'type', None) != 'NODES':
        print("[FP][TRACE][WARN] RouteTrace modifier missing on route curve")

    print("[FP][TRACE] scene_vars: start={start} end={end} lead={lead}".format(**scene_vars))

    return {
        'route': getattr(route_obj, 'name', None),
        'modifier': getattr(modifier, 'name', None) if modifier else None,
        'node_group': getattr(ng, 'name', None) if ng else None,
        'prop': prop_name,
        'driver': driver_present,
        'data_path': data_path,
        'scene_vars': scene_vars,
    }
# --------- End RouteTrace diagnostic ---------

# --------- RouteTrace explicit ensure (append, attach, driver) ---------
def _ensure_route_trace_explicit(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    """Explicitly ensure ASSET_RouteTrace is appended, attached to the RouteTrace modifier,
    and its driver is created. Keeps it simple and prints [FP][TRACE] logs.
    """
    summary: dict[str, object] = {'appended': False, 'attached': False, 'driver': False,
                                  'material_appended': False, 'material_set': False,
                                  'material_name': None, 'material_prop': None}
    route_obj = None
    try:
        from . import resolve as route_resolve
        route_obj = route_resolve.resolve_route_obj(bpy.context)
    except Exception:
        route_obj = None
    if route_obj is None:
        for obj in bpy.data.objects:
            try:
                if getattr(obj, 'type', None) != 'CURVE':
                    continue
                name_cf = (obj.name or '').casefold()
                if 'route' in name_cf:
                    route_obj = obj
                    break
            except Exception:
                pass
    if route_obj is None:
        print("[FP][TRACE] WARN explicit: route curve not found; skipping")
        return summary

    # Ensure node group is appended
    ng = bpy.data.node_groups.get('ASSET_RouteTrace')
    if ng is None:
        path = route_assets.ROUTE_BLEND_PATH
        try:
            with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
                if 'ASSET_RouteTrace' in (getattr(data_from, 'node_groups', None) or []):
                    data_to.node_groups = ['ASSET_RouteTrace']
        except Exception as exc:
            print(f"[FP][TRACE] WARN explicit append failed: {exc}")
        ng = bpy.data.node_groups.get('ASSET_RouteTrace')
        if ng is not None:
            summary['appended'] = True
            print("[FP][TRACE] explicit: appended node group 'ASSET_RouteTrace'")
        else:
            print("[FP][TRACE] WARN explicit: ASSET_RouteTrace not available in assets")

    # Ensure modifier exists and assign node group if present
    mod_name = getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace')
    mod = route_obj.modifiers.get(mod_name)
    if not mod or getattr(mod, 'type', None) != 'NODES':
        try:
            mod = route_obj.modifiers.new(mod_name, 'NODES')
        except Exception as exc:
            print(f"[FP][TRACE] WARN explicit: cannot create modifier: {exc}")
            mod = None
    if mod and ng:
        try:
            mod.node_group = ng
            summary['attached'] = True
            print(f"[FP][TRACE] explicit: attached node group '{ng.name}' to '{route_obj.name}'")
        except Exception as exc:
            print(f"[FP][TRACE] WARN explicit: cannot assign node group: {exc}")

    # Ensure Route material appended and assigned to GN input if available
    mat = bpy.data.materials.get('RouteLine')
    if mat is None:
        path = route_assets.ROUTE_BLEND_PATH
        try:
            with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
                mat_names = list(getattr(data_from, 'materials', []) or [])
                pick = None
                for cand in mat_names:
                    if cand == 'RouteLine':
                        pick = cand
                        break
                if pick is None:
                    for cand in mat_names:
                        if 'route' in (cand or '').casefold():
                            pick = cand
                            break
                if pick is None and mat_names:
                    pick = mat_names[0]
                if pick:
                    data_to.materials = [pick]
        except Exception as exc:
            print(f"[FP][TRACE] WARN explicit append material failed: {exc}")
        # refresh reference
        if pick:
            mat = bpy.data.materials.get(pick)
            if mat is not None:
                summary['material_appended'] = True
                summary['material_name'] = mat.name
                print(f"[FP][TRACE] explicit: appended material '{mat.name}'")

    if mod and ng and mat:
        try:
            mat_idx = route_nodes._find_route_material_input(ng)
            mat_prop = route_nodes._resolve_modifier_input(mod, mat_idx) if mat_idx is not None else None
        except Exception:
            mat_prop = None
        if mat_prop:
            try:
                mod[mat_prop] = mat
                summary['material_set'] = True
                summary['material_prop'] = mat_prop
                summary['material_name'] = mat.name
                print(f"[FP][TRACE] explicit: set material '{mat.name}' on prop '{mat_prop}'")
            except Exception as exc:
                print(f"[FP][TRACE] WARN explicit: cannot assign material: {exc}")

    # Ensure driver via existing helper
    try:
        if route_anim._ensure_route_trace_keyframes(scene):
            summary['driver'] = True
            print("[FP][TRACE] explicit: driver ensured on RouteTrace input")
    except Exception as exc:
        print(f"[FP][TRACE] WARN explicit: driver setup failed: {exc}")

    return summary
# --------- End explicit ensure ---------

# --------- Route object and lead management ---------
def _ensure_route_collection_and_name(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    """Rename the OSM route object to 'ROUTE' and ensure it is linked to collection 'ASSET_ROUTE'.
    Unlink from other collections. Returns summary.

    Uses _find_route_curve(scene) so that the canonical OSM route (tagged with
    blosm_origin == "osm" and blosm_role == ROUTE_ROLE_TAG) is always the source
    of truth, keeping CAR_TRAIL bindings and strict audits consistent.
    """
    summary = {"renamed": False, "linked": False, "unlinked": 0}
    try:
        route_obj = _find_route_curve(scene)
    except Exception:
        route_obj = None
    if route_obj is None:
        return summary
    if route_obj.name != 'ROUTE':
        try:
            # Only rename if name 'ROUTE' is free or already refers to this object
            if bpy.data.objects.get('ROUTE') in (None, route_obj):
                route_obj.name = 'ROUTE'
                summary["renamed"] = True
        except Exception:
            pass
    coll = bpy.data.collections.get('ASSET_ROUTE')
    if coll is None:
        coll = bpy.data.collections.new('ASSET_ROUTE')
        root = getattr(scene, 'collection', None) if scene else getattr(bpy.context, 'scene', None).collection
        try:
            if root and coll.name not in root.children:
                root.children.link(coll)
        except Exception:
            pass
    if coll and coll not in route_obj.users_collection:
        try:
            coll.objects.link(route_obj)
            summary["linked"] = True
        except Exception:
            pass
    # Unlink from other collections
    for c in list(getattr(route_obj, 'users_collection', []) or []):
        if c is None or c == coll:
            continue
        try:
            c.objects.unlink(route_obj)
            summary["unlinked"] += 1
        except Exception:
            pass
    return summary


def _ensure_route_smooth_modifier(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    """Ensure the ROUTE curve has a Smooth modifier with desired settings.

    Applies only to the canonical OSM route curve resolved via _find_route_curve(scene).
    """
    summary = {"added": False, "updated": False}
    try:
        route_obj = _find_route_curve(scene)
    except Exception:
        route_obj = None
    if route_obj is None or getattr(route_obj, "type", None) != "CURVE":
        return summary

    mod = None
    for existing in getattr(route_obj, "modifiers", []) or []:
        if getattr(existing, "type", None) == 'SMOOTH':
            mod = existing
            break
    if mod is None:
        try:
            mod = route_obj.modifiers.new(name="Smooth", type='SMOOTH')
            summary["added"] = True
        except Exception:
            return summary

    try:
        # Only touch settings if they differ to avoid unnecessary churn
        if getattr(mod, "factor", None) != 2.0 or getattr(mod, "iterations", None) != 7:
            mod.factor = 2.0
            mod.iterations = 7
            if not summary["added"]:
                summary["updated"] = True
    except Exception:
        pass
    return summary

def _rename_lead_and_move_to_car_collection(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
    """Rename 'RouteLead' to 'CAR_LEAD' and move it exclusively into collection 'ASSET_CAR'.
    Mirrors the effect of Outliner 'collection_drop' by linking to target and unlinking from others.
    """
    summary = {"renamed": False, "linked": False, "unlinked": 0}
    lead = bpy.data.objects.get('RouteLead') or bpy.data.objects.get('CAR_LEAD')
    if lead is None:
        return summary
    if lead.name != 'CAR_LEAD':
        try:
            lead.name = 'CAR_LEAD'
            summary["renamed"] = True
        except Exception:
            pass
    # Ensure destination collection exists
    car_coll = bpy.data.collections.get(route_assets.CAR_OBJECT) or bpy.data.collections.get('ASSET_CAR')
    if car_coll is None:
        car_coll = bpy.data.collections.new(route_assets.CAR_OBJECT)
        root = getattr(scene, 'collection', None) if scene else getattr(bpy.context, 'scene', None).collection
        try:
            if root and car_coll.name not in root.children:
                root.children.link(car_coll)
        except Exception:
            pass
    # Link to destination
    if car_coll and car_coll not in lead.users_collection:
        try:
            car_coll.objects.link(lead)
            summary["linked"] = True
        except Exception:
            pass
    # Unlink from all other collections (exclusive move)
    for c in list(getattr(lead, 'users_collection', []) or []):
        if c is None or c == car_coll:
            continue
        try:
            c.objects.unlink(lead)
            summary["unlinked"] += 1
        except Exception:
            pass
    return summary

def _set_route_profile_radius(scene: Optional[bpy.types.Scene], value: float = 1.0) -> bool:
    """Set the 'ProfileRadius' float input on the RouteTrace GN modifier, if present."""
    try:
        from . import resolve as route_resolve
        route_obj = route_resolve.resolve_route_obj(bpy.context)
    except Exception:
        route_obj = None
    if route_obj is None:
        return False
    mod = route_obj.modifiers.get(getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace'))
    if not (mod and getattr(mod, 'type', None) == 'NODES' and getattr(mod, 'node_group', None)):
        return False
    ng = mod.node_group
    target_idx = None
    for idx, socket_type, name in route_nodes._iter_group_inputs(ng) or []:
        nm = (name or '').casefold()
        if socket_type == 'FLOAT' and (('profile' in nm) or (nm.replace(' ', '') == 'profileradius')):
            target_idx = idx; break
    if target_idx is None:
        # fallback by exact common name
        for idx, socket_type, name in route_nodes._iter_group_inputs(ng) or []:
            if socket_type == 'FLOAT' and (name or '').strip() == 'ProfileRadius':
                target_idx = idx; break
    prop = None
    if target_idx is not None:
        prop = route_nodes._resolve_modifier_input(mod, target_idx)
    # Explicit fallback commonly observed as Socket_11
    if not prop and getattr(route_obj, 'name', '') == 'ROUTE':
        if 'Socket_11' in mod.keys():
            prop = 'Socket_11'
    try:
        if prop:
            mod[prop] = float(value)
        else:
            return False
        print(f"[FP][ROUTE] ProfileRadius set to {float(value)} via '{prop}'")
        return True
    except Exception as exc:
        print(f"[FP][ROUTE] WARN set ProfileRadius failed: {exc}")
        return False
# --------- End route/lead helpers ---------

# --------- Route dedupe in ASSET_ROUTE ---------
def _dedupe_route_objects(scene: Optional[bpy.types.Scene]) -> int:
    coll = bpy.data.collections.get('ASSET_ROUTE')
    # Collect candidate route curves from ASSET_ROUTE if available, else from all objects
    candidates = []
    if coll is not None:
        try:
            objs = list(coll.all_objects)
        except AttributeError:
            objs = list(coll.objects)
        candidates = [o for o in objs if getattr(o, 'type', None) == 'CURVE']
    if not candidates:
        candidates = [o for o in bpy.data.objects if getattr(o, 'type', None) == 'CURVE' and 'route' in (o.name or '').casefold()]
    if len(candidates) <= 1:
        return 0
    # Prefer exact name 'ROUTE' as primary; else any with RouteTrace modifier; else first
    primary = next((o for o in candidates if o.name == 'ROUTE'), None)
    if primary is None:
        for o in candidates:
            m = o.modifiers.get(getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace'))
            if m and getattr(m, 'type', None) == 'NODES':
                primary = o; break
    if primary is None:
        primary = candidates[0]
    deleted = 0
    for o in candidates:
        if o is primary:
            continue
        try:
            bpy.data.objects.remove(o, do_unlink=True)
            deleted += 1
            print(f"[FP][ROUTE] deleted duplicate route '{o.name}'")
        except Exception as exc:
            print(f"[FP][ROUTE] WARN delete '{o.name}' failed: {exc}")
    # Ensure primary is named 'ROUTE'
    if primary.name != 'ROUTE' and (bpy.data.objects.get('ROUTE') in (None, primary)):
        try:
            primary.name = 'ROUTE'
        except Exception:
            pass
    return deleted


def _purge_template_route_curves(scene: Optional[bpy.types.Scene]) -> int:
    """Remove obvious template/imported route/CAR_TRAIL curves before building CAR_TRAIL.

    Criteria (any):
      a) object or data is library-linked
      b) name is ROUTE or CAR_TRAIL
      c) name contains ROUTETRACE
      d) blosm_origin is set and != 'osm'

    The OSM route curve must survive:
      - blosm_origin == 'osm'
      - blosm_role   == ROUTE_ROLE_TAG
    """
    deleted = 0
    for obj in list(bpy.data.objects):
        try:
            if getattr(obj, "type", None) != "CURVE":
                continue
            origin = obj.get("blosm_origin")
            role = obj.get("blosm_role")
            if origin == "osm" and role == ROUTE_ROLE_TAG:
                # Always keep the OSM route curve
                continue
            data = getattr(obj, "data", None)
            name = obj.name or ""
            name_upper = name.upper()

            is_template = False
            if getattr(obj, "library", None) is not None or (data is not None and getattr(data, "library", None) is not None):
                is_template = True
            elif name_upper in {"ROUTE", "CAR_TRAIL"}:
                is_template = True
            elif "ROUTETRACE" in name_upper:
                is_template = True
            elif "blosm_origin" in obj.keys() and origin is not None and origin != "osm":
                is_template = True

            if not is_template:
                continue

            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted += 1
                print(f"[FP][ROUTE] purged template curve '{name}'")
            except Exception as exc:
                print(f"[FP][ROUTE] WARN purge '{name}' failed: {exc}")
        except Exception:
            continue
    return deleted


def _dedupe_car_trail_objects(
    scene: Optional[bpy.types.Scene],
    primary: Optional[bpy.types.Object],
) -> int:
    """Ensure exactly one CAR_TRAIL-like curve survives.

    Keeps the provided primary object and deletes:
      - Any curve with blosm_role == CAR_TRAIL_ROLE_TAG
      - Any curve named 'CAR_TRAIL' or starting with 'CAR_TRAIL.'
    """
    if primary is None:
        return 0

    deleted = 0
    for obj in list(bpy.data.objects):
        if obj is primary:
            continue
        if getattr(obj, "type", None) != "CURVE":
            continue
        name = obj.name or ""
        role = obj.get("blosm_role")
        if role == CAR_TRAIL_ROLE_TAG or name == "CAR_TRAIL" or name.startswith("CAR_TRAIL."):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted += 1
                print(f"[FP][CAR] deleted duplicate CAR_TRAIL '{name}'")
            except Exception as exc:
                print(f"[FP][CAR] WARN delete duplicate CAR_TRAIL '{name}' failed: {exc}")
    return deleted


def _resync_car_trail_transform(scene: Optional[bpy.types.Scene]) -> bool:
    """Ensure CAR_TRAIL transform (and basic bevel wiring) matches the finalized route curve."""
    if scene is None:
        return False
    route_obj = _find_route_curve(scene)
    if route_obj is None:
        return False
    car_trail = None
    for obj in bpy.data.objects:
        if getattr(obj, "type", None) != "CURVE":
            continue
        name = obj.name or ""
        role = obj.get("blosm_role")
        if role == CAR_TRAIL_ROLE_TAG or name == "CAR_TRAIL" or name.startswith("CAR_TRAIL."):
            car_trail = obj
            break
    if car_trail is None:
        return False
    try:
        car_trail.matrix_world = route_obj.matrix_world.copy()
        # Keep bevel reference intact: prefer route bevel_object, fallback to _profile_curve.
        data = getattr(car_trail, "data", None)
        src_data = getattr(route_obj, "data", None)
        if data is not None:
            bevel_obj = None
            if src_data is not None and getattr(src_data, "bevel_object", None) is not None:
                bevel_obj = src_data.bevel_object
            else:
                bevel_obj = bpy.data.objects.get("_profile_curve")
            if bevel_obj is not None:
                try:
                    data.bevel_object = bevel_obj
                except Exception as exc_inner:
                    print(f"[FP][CAR] WARN resync bevel object failed: {exc_inner}")
        print(f"[FP][CAR] resynced CAR_TRAIL transform to match route '{route_obj.name}'")
        return True
    except Exception as exc:
        print(f"[FP][CAR] WARN resync CAR_TRAIL transform failed: {exc}")
        return False

# --------- Explicit Socket_11 radius setter ---------
def _set_route_socket11_radius(scene: Optional[bpy.types.Scene], value: float = 1.0) -> bool:
    # Handle both route naming patterns
    route = bpy.data.objects.get('ROUTE') or bpy.data.objects.get('Route')
    if route is None:
        return False
    mod = route.modifiers.get(getattr(route_nodes, 'ROUTE_MODIFIER_NAME', 'RouteTrace'))
    if not mod:
        return False
    if 'Socket_11' not in mod.keys():
        return False
    try:
        mod['Socket_11'] = float(value)
        print(f"[FP][ROUTE] Explicit Socket_11 set to {float(value)} on ROUTE")
        return True
    except Exception as exc:
        print(f"[FP][ROUTE] WARN explicit Socket_11 set failed: {exc}")
        return False
# --------- End route/lead helpers ---------


SceneLike = Union[bpy.types.Scene, bpy.types.Context, None]

ASSET_WORLD_NAME = "ASSET_WORLD"
ASSET_WORLD_BLEND = route_assets.ASSET_DIRECTORY / "ASSET_WORLD.blend"

MAP_COLLECTION_NAME = "Map"






def _ensure_base_end_collection(scene: Optional[bpy.types.Scene]) -> bool:
    blend_path = route_assets.ASSET_DIRECTORY / "ASSET_BASE-END.blend"
    if not blend_path.exists():
        return False
    collection = bpy.data.collections.get("ASSET_BASE-END")
    appended = False
    if collection is None:
        try:
            with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
                if "ASSET_BASE-END" in data_from.collections:
                    data_to.collections = ["ASSET_BASE-END"]
                else:
                    return False
        except Exception as exc:
            print(f"[BLOSM] WARN append ASSET_BASE-END: {exc}")
            return False
        collection = bpy.data.collections.get("ASSET_BASE-END")
        appended = collection is not None

    # Set default visibility - exclude from view layers by default
    if collection:
        collection.hide_viewport = True
        collection.hide_render = True
        if scene:
            _exclude_collection_from_view_layers(scene, "ASSET_BASE-END")
    if collection is None:
        return False
    if scene is not None:
        root = getattr(scene, "collection", None)
        if root and collection.name not in root.children:
            try:
                root.children.link(collection)
            except RuntimeError:
                pass
    parent = None
    if collection is not None:
        parent = collection.objects.get("BASE-END") or collection.objects.get("BASE_END")
    if parent is None:
        parent = bpy.data.objects.get("BASE-END") or bpy.data.objects.get("BASE_END")
    if parent is None and collection is not None:
        parent = _pick_first_object_in_collection(collection)
    target = bpy.data.objects.get("END") or bpy.data.objects.get("End")
    if parent and target:
        for constraint in list(parent.constraints):
            if constraint.type == 'COPY_LOCATION':
                parent.constraints.remove(constraint)
        copy_loc = parent.constraints.new(type='COPY_LOCATION')
        copy_loc.target = target
        copy_loc.use_x = copy_loc.use_y = copy_loc.use_z = True
        view_layer = getattr(bpy.context, 'view_layer', None)
        if view_layer is not None:
            view_layer.update()
    elif parent is None:
        print('[BLOSM] WARN ASSET_BASE-END: parent empty missing')
    elif target is None:
        print('[BLOSM] WARN ASSET_BASE-END: target END missing')
    if appended:
        print('[BLOSM] appended ASSET_BASE-END collection')
    return appended


def _ensure_base_start_collection(scene: Optional[bpy.types.Scene]) -> bool:
    blend_path = route_assets.ASSET_DIRECTORY / "ASSET_BASE-START.blend"
    if not blend_path.exists():
        return False
    collection = bpy.data.collections.get("ASSET_BASE-START")
    appended = False
    if collection is None:
        try:
            with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
                if "ASSET_BASE-START" in data_from.collections:
                    data_to.collections = ["ASSET_BASE-START"]
                else:
                    return False
        except Exception as exc:
            print(f"[BLOSM] WARN append ASSET_BASE-START: {exc}")
            return False
        collection = bpy.data.collections.get("ASSET_BASE-START")
        appended = collection is not None

    # Set default visibility - exclude from view layers by default
    if collection:
        collection.hide_viewport = True
        collection.hide_render = True
        if scene:
            _exclude_collection_from_view_layers(scene, "ASSET_BASE-START")
    if collection is None:
        return False
    if scene is not None:
        root = getattr(scene, "collection", None)
        if root and collection.name not in root.children:
            try:
                root.children.link(collection)
            except RuntimeError:
                pass
    parent = None
    if collection is not None:
        parent = collection.objects.get("BASE-START") or collection.objects.get("BASE_START")
    if parent is None:
        parent = bpy.data.objects.get("BASE-START") or bpy.data.objects.get("BASE_START")
    if parent is None and collection is not None:
        parent = _pick_first_object_in_collection(collection)
    target = bpy.data.objects.get("START") or bpy.data.objects.get("Start")
    if parent and target:
        for constraint in list(parent.constraints):
            if constraint.type == 'COPY_LOCATION':
                parent.constraints.remove(constraint)
        copy_loc = parent.constraints.new(type='COPY_LOCATION')
        copy_loc.target = target
        copy_loc.use_x = copy_loc.use_y = copy_loc.use_z = True
        view_layer = getattr(bpy.context, 'view_layer', None)
        if view_layer is not None:
            view_layer.update()
    elif parent is None:
        print('[BLOSM] WARN ASSET_BASE-START: parent empty missing')
    elif target is None:
        print('[BLOSM] WARN ASSET_BASE-START: target START missing')
    if appended:
        print('[BLOSM] appended ASSET_BASE-START collection')
    return appended




def _resolve_car(scene: Optional[bpy.types.Scene]) -> Optional[bpy.types.Object]:
    """Resolve the runtime ASSET_CAR object.

    Preference order:
    1) Objects tagged with blosm_role == "asset_car" in the active scene.
    2) Name-based fallbacks using route_assets.CAR_OBJECT.
    3) route_anim._resolve_car_object() as a final fallback.
    """
    if scene is not None:
        try:
            for obj in scene.objects:
                try:
                    if obj.get("blosm_role") == ASSET_CAR_ROLE_TAG:
                        return obj
                except Exception:
                    continue
        except Exception:
            pass
        try:
            obj = scene.objects.get(route_assets.CAR_OBJECT)
            if obj is not None:
                return obj
        except Exception:
            pass
    return bpy.data.objects.get(route_assets.CAR_OBJECT) or route_anim._resolve_car_object(context=scene)


def _fix_car_damped_track_target(scene: Optional[bpy.types.Scene], car_obj: bpy.types.Object) -> bool:
    """Fix the Damped Track constraint target after CAR_LEAD has been renamed and moved.

    This ensures that ASSET_CAR's Damped Track constraint points to CAR_LEAD
    after the pipeline finalizer has completed the object reorganization.

    Handles both RouteLead (creation name) and CAR_LEAD (final name) objects
    to ensure constraint fixing works regardless of renaming timing.
    """
    if car_obj is None:
        return False

    # Look for CAR_LEAD object (handle both creation name and final name)
    car_lead = bpy.data.objects.get('CAR_LEAD') or bpy.data.objects.get('RouteLead')

    # Create RouteLead object if it doesn't exist (needed for Damped Track target)
    if car_lead is None:
        try:
            lead_object_name = getattr(route_anim, 'LEAD_OBJECT_NAME', 'RouteLead')
            car_lead = bpy.data.objects.new(lead_object_name, None)
            car_lead.empty_display_type = 'PLAIN_AXES'
            car_lead.empty_display_size = 2.0
            if scene:
                scene.collection.objects.link(car_lead)
            print(f"[FP][CAR] Created {lead_object_name} object for Damped Track target")
        except Exception as exc:
            print(f"[FP][CAR] ERROR creating {lead_object_name} object: {exc}")
            return False

    # Find and fix Damped Track constraint on ASSET_CAR
    fixed = False
    for constraint in car_obj.constraints:
        if constraint.type == 'DAMPED_TRACK':
            current_target = getattr(constraint, 'target', None)
            # Check if target needs to be updated (handle both valid target names)
            valid_target_names = {'CAR_LEAD', 'RouteLead'}
            if current_target is None or current_target.name not in valid_target_names:
                try:
                    constraint.target = car_lead
                    if hasattr(constraint, 'track_axis'):
                        constraint.track_axis = 'TRACK_X'
                    if hasattr(constraint, 'up_axis'):
                        constraint.up_axis = 'UP_Z'
                    fixed = True
                    target_name = car_lead.name if car_lead else 'Unknown'
                    print(f"[FP][CAR] Fixed Damped Track target: {current_target.name if current_target else 'None'} -> {target_name}")
                except Exception as exc:
                    print(f"[FP][CAR] ERROR fixing Damped Track: {exc}")

    return fixed


def _validate_animation_setup(scene: Optional[bpy.types.Scene], car_obj: Optional[bpy.types.Object]) -> dict:
    """Validate that all animation components are properly set up.

    Returns a detailed validation report showing what's working and what needs attention.
    """
    validation = {
        "objects": {},
        "constraints": {},
        "drivers": {},
        "overall_status": "unknown"
    }

    try:
        # Validate objects
        car_lead = bpy.data.objects.get('CAR_LEAD') or bpy.data.objects.get('RouteLead')
        route_obj = bpy.data.objects.get('ROUTE') or bpy.data.objects.get('Route')

        validation["objects"]["CAR_LEAD/RouteLead"] = {
            "found": car_lead is not None,
            "name": car_lead.name if car_lead else None,
            "type": car_lead.type if car_lead else None
        }

        validation["objects"]["ASSET_CAR"] = {
            "found": car_obj is not None,
            "name": car_obj.name if car_obj else None,
            "type": car_obj.type if car_obj else None
        }

        validation["objects"]["ROUTE/Route"] = {
            "found": route_obj is not None,
            "name": route_obj.name if route_obj else None,
            "type": route_obj.type if route_obj else None
        }

        # Validate CAR_LEAD Follow Path constraint
        if car_lead:
            lead_follow_constraint = None
            for constraint in car_lead.constraints:
                if constraint.type == 'FOLLOW_PATH':
                    lead_follow_constraint = constraint
                    break

            if lead_follow_constraint:
                validation["constraints"]["CAR_LEAD_FollowPath"] = {
                    "found": True,
                    "name": lead_follow_constraint.name,
                    "target": lead_follow_constraint.target.name if lead_follow_constraint.target else None,
                    "use_curve_follow": getattr(lead_follow_constraint, 'use_curve_follow', False),
                    "use_fixed_position": getattr(lead_follow_constraint, 'use_fixed_position', False)
                }
            else:
                validation["constraints"]["CAR_LEAD_FollowPath"] = {"found": False}
        else:
            validation["constraints"]["CAR_LEAD_FollowPath"] = {"found": False, "reason": "CAR_LEAD object not found"}

        # Validate ASSET_CAR constraints
        if car_obj:
            car_follow_constraint = None
            damped_track_constraint = None

            for constraint in car_obj.constraints:
                if constraint.type == 'FOLLOW_PATH':
                    car_follow_constraint = constraint
                elif constraint.type == 'DAMPED_TRACK':
                    damped_track_constraint = constraint

            validation["constraints"]["ASSET_CAR_FollowPath"] = {
                "found": car_follow_constraint is not None,
                "name": car_follow_constraint.name if car_follow_constraint else None,
                "target": car_follow_constraint.target.name if car_follow_constraint and car_follow_constraint.target else None,
                "use_curve_follow": getattr(car_follow_constraint, 'use_curve_follow', False) if car_follow_constraint else False
            }

            validation["constraints"]["ASSET_CAR_DampedTrack"] = {
                "found": damped_track_constraint is not None,
                "name": damped_track_constraint.name if damped_track_constraint else None,
                "target": damped_track_constraint.target.name if damped_track_constraint and damped_track_constraint.target else None,
                "track_axis": getattr(damped_track_constraint, 'track_axis', None) if damped_track_constraint else None,
                "up_axis": getattr(damped_track_constraint, 'up_axis', None) if damped_track_constraint else None
            }
        else:
            validation["constraints"]["ASSET_CAR_FollowPath"] = {"found": False, "reason": "ASSET_CAR object not found"}
            validation["constraints"]["ASSET_CAR_DampedTrack"] = {"found": False, "reason": "ASSET_CAR object not found"}

        # Validate drivers
        if car_lead and car_obj:
            car_lead_follow_path = None
            asset_car_follow_path = None

            for constraint in car_lead.constraints:
                if constraint.type == 'FOLLOW_PATH':
                    car_lead_follow_path = constraint
                    break

            for constraint in car_obj.constraints:
                if constraint.type == 'FOLLOW_PATH':
                    asset_car_follow_path = constraint
                    break

            # Check for drivers on constraints
            if car_lead_follow_path and hasattr(car_lead_follow_path, 'id_data'):
                lead_data_path = f'constraints["{car_lead_follow_path.name}"].offset_factor'
                lead_driver = getattr(car_lead_follow_path.id_data, 'animation_data', None)
                lead_driver = lead_driver.drivers.find(lead_data_path) if lead_driver else None
                validation["drivers"]["CAR_LEAD_offset_factor"] = {
                    "found": lead_driver is not None,
                    "data_path": lead_data_path if lead_driver else None
                }

            if asset_car_follow_path and hasattr(asset_car_follow_path, 'id_data'):
                car_data_path = f'constraints["{asset_car_follow_path.name}"].offset_factor'
                anim_data = getattr(asset_car_follow_path.id_data, 'animation_data', None)
                car_driver = anim_data.drivers.find(car_data_path) if anim_data else None
                
                # Check for keyframes if no driver
                car_keyframe = None
                if not car_driver and anim_data and anim_data.action:
                    for fc in anim_data.action.fcurves:
                        if fc.data_path == car_data_path:
                            car_keyframe = fc
                            break

                validation["drivers"]["ASSET_CAR_offset_factor"] = {
                    "found": (car_driver is not None) or (car_keyframe is not None),
                    "data_path": car_data_path,
                    "type": "driver" if car_driver else ("keyframe" if car_keyframe else None)
                }

        # Determine overall status
        objects_ok = all(obj_info["found"] for obj_info in validation["objects"].values())
        constraints_ok = all(
            constraint_info.get("found", False)
            for constraint_info in validation["constraints"].values()
            if "reason" not in constraint_info
        )
        drivers_ok = len(validation.get("drivers", {})) > 0 and all(
            driver_info.get("found", False)
            for driver_info in validation["drivers"].values()
        )

        if objects_ok and constraints_ok and drivers_ok:
            validation["overall_status"] = "ready"
        elif objects_ok and constraints_ok:
            validation["overall_status"] = "needs_drivers"
        elif objects_ok:
            validation["overall_status"] = "needs_constraints"
        else:
            validation["overall_status"] = "needs_objects"

        # Print validation summary
        print(f"[FP][VALIDATION] Overall status: {validation['overall_status']}")
        for obj_name, obj_info in validation["objects"].items():
            status = "?" if obj_info["found"] else "?"
            print(f"[FP][VALIDATION] {status} Object {obj_name}: {obj_info['found']}")

        for constraint_name, constraint_info in validation["constraints"].items():
            if "reason" not in constraint_info:
                status = "?" if constraint_info["found"] else "?"
                print(f"[FP][VALIDATION] {status} Constraint {constraint_name}: {constraint_info['found']}")

        for driver_name, driver_info in validation.get("drivers", {}).items():
            status = "?" if driver_info["found"] else "?"
            print(f"[FP][VALIDATION] {status} Driver {driver_name}: {driver_info['found']}")

    except Exception as exc:
        validation["overall_status"] = "error"
        validation["error"] = str(exc)
        print(f"[FP][VALIDATION] ERROR during validation: {exc}")

    return validation


def _ensure_asset_car_follow_path_constraint(scene: Optional[bpy.types.Scene], car_obj: bpy.types.Object) -> bool:
    """Ensure ASSET_CAR has a Follow Path constraint to ROUTE.

    This creates or updates the Follow Path constraint on ASSET_CAR that
    follows the ROUTE curve for synchronized car animation.

    This is the constraint that gets the animation driver applied to it.
    """
    if car_obj is None:
        print("[FP][CAR] WARN ASSET_CAR object not found for Follow Path constraint")
        return False

    # Find ROUTE object (handle both route curve naming patterns)
    route_obj = route_anim._resolve_route_object(scene)
    if route_obj is None:
        print("[FP][CAR] WARN ROUTE not found for ASSET_CAR Follow Path constraint")
        return False

    # Look for existing Follow Path constraint on ASSET_CAR
    follow_constraint = None
    car_constraint_name = getattr(route_anim, 'CAR_CONSTRAINT_NAME', 'RoutePreviewFollow')

    for constraint in car_obj.constraints:
        if constraint.type == 'FOLLOW_PATH' and constraint.name == car_constraint_name:
            follow_constraint = constraint
            break

    # Create Follow Path constraint if it doesn't exist
    if follow_constraint is None:
        try:
            follow_constraint = car_obj.constraints.new('FOLLOW_PATH')
            follow_constraint.name = car_constraint_name
            print(f"[FP][CAR] Created Follow Path constraint '{car_constraint_name}' on ASSET_CAR")
        except Exception as exc:
            print(f"[FP][CAR] ERROR creating Follow Path constraint: {exc}")
            return False

    # Configure the Follow Path constraint
    try:
        follow_constraint.target = route_obj
        if hasattr(follow_constraint, 'use_curve_follow'):
            follow_constraint.use_curve_follow = False
            
        # Robustly set Fixed Position
        fixed_set = False
        if hasattr(follow_constraint, 'use_fixed_location'):
            follow_constraint.use_fixed_location = True
            fixed_set = True
        if hasattr(follow_constraint, 'use_fixed_position'):
            follow_constraint.use_fixed_position = True
            fixed_set = True
            
        if not fixed_set:
            print(f"[FP][CAR] WARN could not set Fixed Position on {follow_constraint.name}")
            
        if hasattr(follow_constraint, 'forward_axis'):
            follow_constraint.forward_axis = 'FORWARD_X'
        if hasattr(follow_constraint, 'up_axis'):
            follow_constraint.up_axis = 'UP_Z'
            
        print(f"[FP][CAR] Configured ASSET_CAR Follow Path constraint to target {route_obj.name}")
        return True
    except Exception as exc:
        print(f"[FP][CAR] ERROR configuring Follow Path constraint: {exc}")
        return False


def _ensure_car_lead_follow_path_constraint(scene: Optional[bpy.types.Scene], car_obj: bpy.types.Object) -> bool:
    """Ensure CAR_LEAD has a Follow Path constraint to ROUTE.

    This creates or updates the Follow Path constraint on CAR_LEAD that
    follows the ROUTE curve with the appropriate lead offset for smooth
    car animation.

    Handles both RouteLead (creation name) and CAR_LEAD (final name) objects
    to ensure constraint creation works regardless of renaming timing.
    """
    # Look for CAR_LEAD object (handle both creation name and final name)
    car_lead = bpy.data.objects.get('CAR_LEAD') or bpy.data.objects.get('RouteLead')

    # Create RouteLead object if it doesn't exist
    if car_lead is None:
        lead_object_name = 'RouteLead'
        try:
            lead_object_name = getattr(route_anim, 'LEAD_OBJECT_NAME', 'RouteLead')
            car_lead = bpy.data.objects.new(lead_object_name, None)
            car_lead.empty_display_type = 'PLAIN_AXES'
            car_lead.empty_display_size = 2.0
            if scene:
                scene.collection.objects.link(car_lead)
            try:
                car_lead.location = (0.0, 0.0, 4.0)
            except Exception:
                pass
            print(f"[FP][LEAD] Created {lead_object_name} object for Follow Path constraint")
        except Exception as exc:
            print(f"[FP][LEAD] ERROR creating {lead_object_name} object: {exc}")
            return False

    if car_lead is not None:
        try:
            car_lead.location = (0.0, 0.0, 4.0)
        except Exception:
            pass

    # Find ROUTE object (handle both route curve naming patterns)
    route_obj = route_anim._resolve_route_object(scene)
    if route_obj is None:
        print("[FP][LEAD] WARN ROUTE not found for Follow Path constraint")
        return False

    # Look for existing Follow Path constraint on CAR_LEAD
    follow_constraint = None
    for constraint in car_lead.constraints:
        if constraint.type == 'FOLLOW_PATH':
            follow_constraint = constraint
            break

    # Create Follow Path constraint if it doesn't exist
    if follow_constraint is None:
        try:
            follow_constraint = car_lead.constraints.new('FOLLOW_PATH')
            follow_constraint.name = 'RouteLeadFollow'
            print("[FP][LEAD] Created Follow Path constraint on CAR_LEAD")
        except Exception as exc:
            print(f"[FP][LEAD] ERROR creating Follow Path constraint: {exc}")
            return False

    # Configure the Follow Path constraint
    try:
        follow_constraint.target = route_obj
        if hasattr(follow_constraint, 'use_curve_follow'):
            follow_constraint.use_curve_follow = False
            
        # Robustly set Fixed Position
        fixed_set = False
        if hasattr(follow_constraint, 'use_fixed_location'):
            follow_constraint.use_fixed_location = True
            fixed_set = True
        if hasattr(follow_constraint, 'use_fixed_position'):
            follow_constraint.use_fixed_position = True
            fixed_set = True
            
        if not fixed_set:
            print(f"[FP][LEAD] WARN could not set Fixed Position on {follow_constraint.name}")
            
        if hasattr(follow_constraint, 'forward_axis'):
            follow_constraint.forward_axis = 'FORWARD_X'
        if hasattr(follow_constraint, 'up_axis'):
            follow_constraint.up_axis = 'UP_Z'
            
        # Ensure offset_factor is accessible but DO NOT create driver here.
        # We want keyframes (created by route_anim.force_follow_keyframes) 
        # so the user can manually edit the fcurves.
        follow_constraint.offset_factor = 0.0
        
        print("[FP][LEAD] Configured Follow Path constraint: CAR_LEAD -> ROUTE")
        return True

    except Exception as exc:
        print(f"[FP][LEAD] ERROR configuring Follow Path constraint: {exc}")
        return False


def _prune_empty_damped_track(car_obj: Optional[bpy.types.Object]) -> int:
    removed = 0
    if car_obj is None:
        return removed
    constraints = getattr(car_obj, "constraints", None)
    if constraints is None:
        return removed
    for constraint in list(constraints):
        if getattr(constraint, "type", None) == "DAMPED_TRACK" and getattr(constraint, "target", None) is None:
            try:
                constraints.remove(constraint)
                removed += 1
            except Exception:
                pass
    if removed:
        print(f"[BLOSM] finalizer removed {removed} empty Damped Track constraint(s)")
    return removed


def _retarget_follow_path_constraint(
    obj: Optional[bpy.types.Object],
    route_obj: Optional[bpy.types.Object],
    constraint_name: Optional[str] = None,
) -> bool:
    """Retarget an existing Follow Path constraint to the ROUTE curve without
    touching its animation (drivers/keyframes on offset_factor).
    """
    if obj is None or route_obj is None:
        return False
    constraints = getattr(obj, "constraints", None)
    if constraints is None:
        return False
    updated = False
    for constraint in constraints:
        if getattr(constraint, "type", None) != "FOLLOW_PATH":
            continue
        if constraint_name and getattr(constraint, "name", "") != constraint_name:
            continue
        try:
            prev = getattr(constraint, "target", None)
            if prev is not route_obj:
                constraint.target = route_obj
                updated = True
                print(
                    f"[FP][FOLLOW] Retargeted Follow Path on '{obj.name}' "
                    f"from '{getattr(prev, 'name', None)}' to '{route_obj.name}'"
                )
        except Exception as exc:
            print(f"[FP][FOLLOW] WARN retarget Follow Path on '{obj.name}': {exc}")
    return updated


def _ensure_beam_asset(scene: Optional[bpy.types.Scene]) -> Optional[bpy.types.Object]:
    """Ensure ASSET_BEAM object exists, lives in ASSET_BEAM collection, and is
    positioned at the Start marker when available.
    """
    beam = bpy.data.objects.get("ASSET_BEAM")
    if beam is None:
        # Try to append from ASSET_BEAM.blend
        try:
            from . import assets as route_assets
            from . import resolve as route_resolve
            path = route_assets.BEAM_BLEND_PATH
            names = route_resolve.list_blend_datablocks(path, "objects")
            route_resolve.ensure_appended(path, "objects", names)
            pick = None
            for cand in names:
                if cand and "beam" in cand.casefold():
                    pick = cand
                    break
            if pick is None and names:
                pick = names[0]
            beam = bpy.data.objects.get(pick) if pick else None
            if beam and beam.name != "ASSET_BEAM":
                try:
                    beam.name = "ASSET_BEAM"
                except Exception:
                    pass
        except Exception as exc:
            print(f"[BLOSM] WARN ensure beam asset failed: {exc}")
            beam = None
    if beam is None:
        return None

    # Ensure ASSET_BEAM collection
    coll = bpy.data.collections.get("ASSET_BEAM")
    if coll is None:
        coll = bpy.data.collections.new("ASSET_BEAM")
        if scene and coll.name not in scene.collection.children:
            try:
                scene.collection.children.link(coll)
            except Exception:
                pass
    if beam.name not in coll.objects:
        try:
            coll.objects.link(beam)
        except Exception:
            pass

    # Position at Start marker if available
    start = bpy.data.objects.get("Start")
    if start:
        try:
            from mathutils import Matrix
            beam.parent = None
            beam.matrix_parent_inverse = Matrix.Identity(4)
        except Exception:
            pass
        beam.location = start.location

    # Apply final scale and Z offset (artist-approved settings)
    try:
        beam.scale = (100.0, 100.0, 100.0)
        loc = list(beam.location)
        loc[2] = 4200.0
        beam.location = tuple(loc)
    except Exception:
        pass
    beam.hide_viewport = False
    beam.hide_render = False
    try:
        beam.hide_set(False)
    except Exception:
        pass
    return beam


def _apply_map_render_filters(scene: Optional[bpy.types.Scene]) -> dict[str, int]:
    summary = {"disabled": 0, "kept": 0}
    if scene is None:
        return summary
    collection = bpy.data.collections.get(MAP_COLLECTION_NAME)
    if collection is None:
        return summary
    try:
        objects = list(collection.all_objects)
    except AttributeError:
        objects = list(collection.objects)
    for obj in objects:
        if obj is None:
            continue
        name = obj.name.strip()
        last_token = name.split(" ")[-1].casefold() if name else ""
        is_building = last_token == "buildings"
        obj.hide_render = not is_building
        if is_building:
            summary["kept"] += 1
        else:
            summary["disabled"] += 1
    if summary["disabled"] or summary["kept"]:
        print('[BLOSM] finalizer map render filter: disabled={disabled} kept={kept}'.format(**summary))
    return summary


def _collapse_outliner(context: bpy.types.Context, depth: int = 2) -> bool:
    if getattr(bpy.app, "background", False):
        return False
    window = getattr(context, "window", None)
    screen = getattr(context, "screen", None)
    if screen is None:
        wm = getattr(bpy.context, "window_manager", None)
        if wm:
            for candidate in wm.windows:
                scr = getattr(candidate, "screen", None)
                if scr:
                    window = candidate
                    screen = scr
                    break
    if screen is None or window is None:
        return False
    area = None
    for candidate in screen.areas:
        if getattr(candidate, "type", None) == "OUTLINER":
            area = candidate
            break
    if area is None:
        return False
    region = next((r for r in area.regions if r.type == "WINDOW"), None)
    if region is None:
        return False
    space = getattr(area, "spaces", None)
    space_data = space.active if space else None
    override = {
        "window": window,
        "screen": screen,
        "area": area,
        "region": region,
        "space_data": space_data,
        "active_object": getattr(context, "active_object", None),
    }
    try:
        bpy.ops.outliner.show_hierarchy(override)
        for _ in range(max(1, depth)):
            bpy.ops.outliner.expanded_toggle(override)
        area.tag_redraw()
        return True
    except Exception as exc:
        print(f"[BLOSM] WARN outliner collapse failed: {exc}")
    return False


def _ensure_world(scene: Optional[bpy.types.Scene]) -> Optional[bpy.types.World]:
    world = bpy.data.worlds.get(ASSET_WORLD_NAME)
    lighting_missing = bpy.data.collections.get("LIGHTING") is None
    if (world is None or lighting_missing) and ASSET_WORLD_BLEND.exists():
        try:
            with bpy.data.libraries.load(str(ASSET_WORLD_BLEND), link=False) as (data_from, data_to):
                if world is None and ASSET_WORLD_NAME in data_from.worlds:
                    data_to.worlds = [ASSET_WORLD_NAME]
                if lighting_missing and "LIGHTING" in data_from.collections:
                    data_to.collections = ["LIGHTING"]
                    print(f"[BLOSM] Imported LIGHTING collection from ASSET_WORLD.blend")
        except Exception as exc:
            print(f"[BLOSM] WARN finalizer world append: {exc}")
    world = bpy.data.worlds.get(ASSET_WORLD_NAME)
    if world is not None and scene is not None:
        scene.world = world
    lighting_collection = bpy.data.collections.get("LIGHTING")
    if lighting_collection is not None and scene is not None:
        if lighting_collection.name not in {child.name for child in scene.collection.children}:
            try:
                scene.collection.children.link(lighting_collection)
                print(f"[BLOSM] Linked LIGHTING collection to scene")
            except RuntimeError:
                pass
    return world


def run(ctx_or_scene: SceneLike = None) -> dict[str, object]:
    """Run final adjustments after the auto pipeline completes."""
    if ctx_or_scene is None:
        ctx_or_scene = bpy.context
    scene = getattr(ctx_or_scene, "scene", ctx_or_scene)
    if not isinstance(scene, bpy.types.Scene):
        scene = bpy.context.scene
    result: dict[str, object] = {"drivers": False, "car_scale": None, "world": None}
    if scene is None:
        return result

    base_end_added = _ensure_base_end_collection(scene)
    if base_end_added:
        result.setdefault("collections", []).append("ASSET_BASE-END")
    base_start_added = _ensure_base_start_collection(scene)
    if base_start_added:
        result.setdefault("collections", []).append("ASSET_BASE-START")

    # Ensure RouteTrace GN and driver explicitly before driver wiring
    try:
        rt_fix = _ensure_route_trace_explicit(scene)
        if any(rt_fix.values()):
            result["route_trace_fix"] = rt_fix
    except Exception as exc:
        print(f"[FP][TRACE] WARN explicit ensure failed: {exc}")

    # Resolve car object and ensure constraints exist before setting up drivers
    car_obj = _resolve_car(scene)
    if car_obj:
        try:
            # Ensure ASSET_CAR has Follow Path constraint before driver setup
            car_constraint_ok = _ensure_asset_car_follow_path_constraint(scene, car_obj)
            if car_constraint_ok:
                result["car_constraint"] = "created/fixed"
            else:
                result["car_constraint"] = "failed"
        except Exception as exc:
            print(f"[FP][CAR] ERROR ensuring ASSET_CAR Follow Path constraint: {exc}")
            result["car_constraint"] = f"error: {exc}"

        try:
            # Ensure CAR_LEAD has Follow Path constraint before driver setup
            lead_constraint_ok = _ensure_car_lead_follow_path_constraint(scene, car_obj)
            if lead_constraint_ok:
                result["car_lead_constraint"] = "created/fixed"
            else:
                result["car_lead_constraint"] = "failed"
        except Exception as exc:
            print(f"[FP][LEAD] ERROR ensuring CAR_LEAD Follow Path constraint: {exc}")
            result["car_lead_constraint"] = f"error: {exc}"

        try:
            # Fix Damped Track constraint on ASSET_CAR to point to CAR_LEAD
            damped_fixed = _fix_car_damped_track_target(scene, car_obj)
            if damped_fixed:
                result["car_damped_track"] = "fixed"
            else:
                result["car_damped_track"] = "no_fix_needed"
        except Exception as exc:
            print(f"[FP][CAR] ERROR fixing Damped Track constraint: {exc}")
            result["car_damped_track"] = f"error: {exc}"

    driver_status = route_anim.force_follow_keyframes(scene)
    result["drivers"] = driver_status

    if car_obj is not None:
        removed = _prune_empty_damped_track(car_obj)
        if removed:
            result["car_damped_pruned"] = removed
        car_obj.scale = (20.0, 20.0, 20.0)
        scale_tuple = tuple(float(value) for value in car_obj.scale)
        result["car_scale"] = scale_tuple
        print(f"[BLOSM] finalizer car scale set to {scale_tuple}")
        try:
            loc = list(car_obj.location)
            loc[2] = 4.0
            car_obj.location = tuple(loc)
        except Exception:
            pass
    else:
        print('[BLOSM] WARN finalizer: car not found')

    map_filter = _apply_map_render_filters(scene)
    if map_filter:
        result["map_render"] = map_filter

    _collapse_outliner(bpy.context)

    world = _ensure_world(scene)
    if world is not None:
        result["world"] = world.name
        print(f"[BLOSM] finalizer world set to {world.name}")
    else:
        print('[BLOSM] WARN finalizer: world not available')

    # Ensure CN Tower marker import and placement (CashCab integration)
    try:
        _ensure_cn_tower_marker(scene)
    except Exception as exc:
        print(f"[BLOSM] WARN finalizer: CN Tower ensure failed: {exc}")

    # Ensure beam asset presence/placement as a final safety net
    try:
        beam = _ensure_beam_asset(scene)
        if beam is not None:
            result["beam"] = beam.name
    except Exception as exc:
        print(f"[BLOSM] WARN finalizer: beam ensure failed: {exc}")

    # Final safety pass: retarget car and lead Follow Path constraints to ROUTE
    try:
        route_obj = bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")
        car_obj = bpy.data.objects.get("ASSET_CAR")
        lead_obj = bpy.data.objects.get("CAR_LEAD") or bpy.data.objects.get("RouteLead")
        car_constraint_name = getattr(route_anim, "CAR_CONSTRAINT_NAME", "RoutePreviewFollow")
        if route_obj:
            if car_obj:
                _retarget_follow_path_constraint(car_obj, route_obj, car_constraint_name)
            if lead_obj:
                # Lead may have a differently named Follow Path; retarget any
                _retarget_follow_path_constraint(lead_obj, route_obj, None)
    except Exception as exc:
        print(f"[FP][FOLLOW] WARN final retarget failed: {exc}")

    # ---- Apply attributes from single master file: asset_attributes.txt ----
    try:
        attr_dir = Path(__file__).resolve().parent
        master = attr_dir / "asset_attributes.txt"

        def _coll_objects(coll):
            try:
                return list(coll.all_objects)
            except AttributeError:
                return list(coll.objects)

        targets = []
        for coll in bpy.data.collections:
            cname = getattr(coll, "name", "") or ""
            if cname == "BLOSM_Assets" or cname.startswith("ASSET_"):
                for obj in _coll_objects(coll):
                    if obj is not None:
                        targets.append(obj)

        # de-duplicate while preserving order
        seen_ids = set()
        uniq_targets = []
        for obj in targets:
            oid = id(obj)
            if oid in seen_ids:
                continue
            seen_ids.add(oid)
            uniq_targets.append(obj)

        # Rebuild master file deterministically, preserving existing active entries
        existing_active = _parse_master_attributes(master)
        _write_master_file(master, uniq_targets, existing_active)

        # Parse active pairs and apply per object from the rewritten file
        active = _parse_master_attributes(master)
        applied_any = 0
        for obj in uniq_targets:
            pairs = active.get(obj.name, [])
            if not pairs:
                continue
            try:
                _apply_attribute_pairs(obj, pairs)
                applied_any += 1
            except Exception as exc:
                print(f"[FP][ATTR] ERROR master for '{obj.name}': {exc}")

        if applied_any:
            result["attributes_applied"] = applied_any
            print(f"[FP][ATTR] Completed master attribute pass on {applied_any} object(s). File: {master}")
        else:
            print(f"[FP][ATTR] Master present; no active (uncommented) entries. File: {master}")

        # Load or refresh the master text in Blender's Text Editor for easy editing
        if _load_master_attributes_into_text_editor(bpy.context, master):
            result["attributes_text"] = master.name
    except Exception as exc:
        print(f"[FP][ATTR] WARN master attribute pass failed: {exc}")

    # After attributes, sync Building GeoNodes from asset and set car object
    try:
        synced = _sync_buildings_geonodes_from_asset(scene)
        if synced:
            result["building_gn_synced"] = synced
        applied_defaults = _apply_buildings_geonodes_defaults(scene)
        if applied_defaults:
            result["building_gn_defaults"] = applied_defaults
        gn_set = _set_building_geo_nodes_car(scene)
        if gn_set:
            result["building_gn_car_targets"] = gn_set
        # Explicit override for known map_* buildings + 'BuildingGeo' modifier
        gn_explicit = _explicit_building_geo_car_override(scene)
        if gn_explicit:
            result["building_gn_car_explicit"] = gn_explicit
        # Normalize BUILDINGS_GEO modifier layout to mirror asset file
        norm = _normalize_buildings_geonodes(scene)
        if norm:
            result["building_gn_normalized"] = norm
    except Exception as exc:
        print(f"[FP][ATTR] WARN BuildingGN car set failed: {exc}")

    # Ensure Building GeoNodes modifiers render visibility is on
    try:
        gn_vis = _ensure_building_geonodes_visible(scene)
        if gn_vis:
            result["building_gn_visible"] = gn_vis
    except Exception as exc:
        print(f"[FP][MAP] WARN BuildingGN visibility failed: {exc}")

    # Promote buildings and group maps/profiles under .other, exclude maps from view layer
    try:
        prom = _promote_buildings_and_group_others(scene)
        if prom:
            result["map_grouping"] = prom
    except Exception as exc:
        print(f"[FP][MAP] WARN promote/group failed: {exc}")

    try:
        stripped = _strip_building_materials(scene)
        if stripped:
            result["building_materials_pruned"] = stripped
    except Exception as exc:
        print(f"[FP][MAP] WARN stripping building materials failed: {exc}")

    try:
        final_map = _sync_buildings_geonodes_from_asset(scene)
        if final_map:
            result["building_gn_final_synced"] = final_map
        final_defaults = _apply_buildings_geonodes_defaults(scene)
        if final_defaults:
            result["building_gn_final_defaults"] = final_defaults
    except Exception as exc:
        print(f"[FP][MAP] WARN final building GN sync failed: {exc}")

    try:
        enforced = _enforce_buildings_asset_modifier(scene)
        if enforced:
            result["building_gn_enforced"] = enforced
    except Exception as exc:
        print(f"[FP][MAP] WARN enforcing building GN asset values failed: {exc}")

    # In 'map_*.osm' collections: hide everything except *_buildings objects (may be redundant after move)
    try:
        map_sum = _mute_map_route_objects(scene)
        if map_sum and (map_sum.get('muted') or map_sum.get('kept')):
            result["map_osm_filter"] = map_sum
    except Exception as exc:
        print(f"[FP][MAP] WARN map osm filtering failed: {exc}")

    # Exclude 'way_profiles' collection from all view layers
    try:
        excluded = _exclude_collection_from_view_layers(scene, 'way_profiles')
        if excluded:
            result["excluded_way_profiles"] = excluded
    except Exception as exc:
        print(f"[FP][MAP] WARN exclude way_profiles failed: {exc}")

    # Rehome the ASSET_CAR object into its own collection and remove BLOSM_Assets
    try:
        carcol = _rehome_car_collection(scene)
        if any(carcol.values()):
            result["car_collection"] = carcol
    except Exception as exc:
        print(f"[FP][CARCOL] WARN rehome car collection failed: {exc}")

    # Rename RouteLead -> CAR_LEAD and link to car collection
    try:
        leadsum = _rename_lead_and_move_to_car_collection(scene)
        if any(leadsum.values()):
            result["lead_object"] = leadsum
    except Exception as exc:
        print(f"[FP][ROUTE] WARN lead rename/move failed: {exc}")

  
    # Ensure route object is named 'ROUTE' and in ASSET_ROUTE collection
    try:
        rsum = _ensure_route_collection_and_name(scene)
        if any(rsum.values()):
            result["route_object"] = rsum
    except Exception as exc:
        print(f"[FP][ROUTE] WARN route collection/name failed: {exc}")

    # Ensure ROUTE has a Smooth modifier with desired settings
    try:
        sm = _ensure_route_smooth_modifier(scene)
        if any(sm.values()):
            result["route_smooth"] = sm
    except Exception as exc:
        print(f"[FP][ROUTE] WARN route smooth modifier failed: {exc}")

    # Hide/delete duplicate route curves first (keep canonical 'ROUTE')
    try:
        hid = _dedupe_route_objects(scene)
        if hid:
            result["route_deduped"] = hid
    except Exception as exc:
        print(f"[FP][ROUTE] WARN dedupe routes failed: {exc}")

    # Purge template/imported route/CAR_TRAIL curves before building runtime CAR_TRAIL
    try:
        purged = _purge_template_route_curves(scene)
        if purged:
            result["route_templates_purged"] = purged
    except Exception as exc:
        print(f"[FP][ROUTE] WARN purge template curves failed: {exc}")

    try:
        trace_obj = _build_car_trail_from_route(scene)
        if trace_obj:
            deduped = _dedupe_car_trail_objects(scene, trace_obj)
            if deduped:
                result["car_trail_deduped"] = deduped
            result["car_trail"] = trace_obj.name
    except Exception as exc:
        print(f"[FP][CAR] ERROR car trail build failed: {exc}")
        raise

    # ---- Ensure all animation constraints are properly set up after object renaming ----
    car_obj = _resolve_car(scene)
    if car_obj:
        try:
            lead_constraint_ok = _ensure_car_lead_follow_path_constraint(scene, car_obj)
            if lead_constraint_ok:
                result["car_lead_constraint"] = "created/fixed"
            else:
                result["car_lead_constraint"] = "failed"
        except Exception as exc:
            print(f"[FP][LEAD] ERROR ensuring CAR_LEAD Follow Path constraint: {exc}")
            result["car_lead_constraint"] = f"error: {exc}"

        try:
            car_constraint_ok = _ensure_asset_car_follow_path_constraint(scene, car_obj)
            if car_constraint_ok:
                result["car_follow_constraint"] = "created/fixed"
            else:
                result["car_follow_constraint"] = "failed"
        except Exception as exc:
            print(f"[FP][CAR] ERROR ensuring ASSET_CAR Follow Path constraint: {exc}")
            result["car_follow_constraint"] = f"error: {exc}"

        # Fix Damped Track constraint after all objects are properly named
        try:
            damped_fixed = _fix_car_damped_track_target(scene, car_obj)
            if damped_fixed:
                result["car_damped_fixed"] = "fixed"
            else:
                result["car_damped_fixed"] = "no_fix_needed"
        except Exception as exc:
            print(f"[FP][CAR] ERROR fixing Damped Track constraint: {exc}")
            result["car_damped_fixed"] = f"error: {exc}"

        # Validate that all constraints and objects are properly set up
        validation_result = _validate_animation_setup(scene, car_obj)
        result["validation"] = validation_result

        # Re-run drivers after constraints are ensured
        try:
            final_driver_status = route_anim.force_follow_keyframes(scene)
            result["final_drivers"] = final_driver_status
        except Exception as exc:
            print(f"[FP][DRIVERS] ERROR ensuring final drivers: {exc}")
            result["final_drivers"] = f"error: {exc}"

    # Set ProfileRadius to 1.0 on RouteTrace if present
    try:
        pr_ok = _set_route_profile_radius(scene, 1.0)
        # Ensure explicit fallback on ROUTE.Socket_11
        sock_ok = _set_route_socket11_radius(scene, 1.0)
        if pr_ok or sock_ok:
            result["profile_radius"] = 1.0
    except Exception as exc:
        print(f"[FP][ROUTE] WARN profile radius set failed: {exc}")

    # RouteTrace diagnostic snapshot (does not modify anything)
    try:
        rt = _check_route_trace(scene)
        if rt:
            result["route_trace"] = rt
    except Exception as exc:
        print(f"[FP][TRACE] WARN check failed: {exc}")

    # Scale all visible 3D View clip_end by 10x (UI only)
    try:
        view_updated = _scale_view3d_clip_end(bpy.context, factor=10.0)
        if view_updated:
            result["view_clip_end_scaled"] = view_updated
    except Exception as exc:
        print(f"[FP][VIEW] WARN view clip_end scaling failed: {exc}")

    sandbox = _run_tylers_sandbox(scene)
    if sandbox is not None:
        result["sandbox"] = sandbox

    try:
        if _set_roads_z_scale(scene):
            result["roads_scaled_z"] = True
    except Exception as exc:
        print(f"[FP][ROAD] WARN road scale adjust failed: {exc}")

    # Final safety: ensure CAR_TRAIL transform matches finalized route curve
    try:
        if _resync_car_trail_transform(scene):
            result["car_trail_transform_resynced"] = True
    except Exception as exc:
        print(f"[FP][CAR] WARN final CAR_TRAIL transform resync failed: {exc}")

    # Resample CAR_TRAIL after final transform sync to keep world/local alignment stable
    try:
        if _force_car_trail_polyline_from_route(scene):
            result["car_trail_resampled_final"] = True
            print("[FP][CAR] resample complete after final transform sync (from ROUTE)")
        else:
            run_resample_on_car_trail()
            result["car_trail_resampled_final"] = True
            print("[FP][CAR] resample complete after final transform sync")
    except Exception as exc:
        print(f"[BLOSM] WARN CAR_TRAIL resample post-sync failed: {exc}")

    # Ensure CAR_TRAIL material
    try:
        if _ensure_car_trail_material(scene):
            result["car_trail_material"] = "CAR_TRAIL_SHADER"
    except Exception as exc:
        print(f"[BLOSM] WARN CAR_TRAIL material assignment failed: {exc}")

    # --- Camera Asset Integration ---
    try:
        # Ensure the standardized ASSET_CAMERA is present and in the CAMERAS collection
        cam_summary = _ensure_asset_camera(scene)
        cam_obj = cam_summary.get("camera")
        cam_name = cam_obj.name if cam_obj else None
        result["asset_camera"] = cam_name
        result["asset_camera_summary"] = {
            k: str(v) for k, v in cam_summary.items() if k != "camera"
        }
        if cam_obj:
            print("[BLOSM] ASSET_CAMERA ensured in CAMERAS")
        else:
            print("[BLOSM] WARN ASSET_CAMERA not present after ensure")
    except Exception as exc:
        print(f"[BLOSM] WARN finalizer ASSET_CAMERA ensure failed: {exc}")

    return result


@contextmanager
def _with_active_object(obj: bpy.types.Object):
    ctx = bpy.context
    view_layer = getattr(ctx, "view_layer", None)
    view_layer_objects = getattr(view_layer, "objects", None)
    prev_active = view_layer_objects.active if view_layer_objects else None
    prev_selected = list(getattr(ctx, "selected_objects", []))
    try:
        for sel in prev_selected:
            try:
                sel.select_set(False)
            except Exception:
                pass
        try:
            obj.select_set(True)
        except Exception:
            pass
        if view_layer_objects:
            try:
                view_layer_objects.active = obj
            except Exception:
                pass
        yield
    finally:
        for sel in prev_selected:
            try:
                sel.select_set(True)
            except Exception:
                pass
        if view_layer_objects and prev_active:
            try:
                view_layer_objects.active = prev_active
            except Exception:
                pass
        try:
            obj.select_set(False)
        except Exception:
            pass


def _bake_geometry_nodes_modifiers(
    obj: Optional[bpy.types.Object],
    modifier_names: Optional[set[str]] = None,
) -> int:
    if obj is None:
        return 0

    if obj.name not in getattr(bpy.context.scene, "objects", []):
        try:
            bpy.context.scene.collection.objects.link(obj)
        except Exception:
            pass

    baked = 0
    for mod in list(getattr(obj, "modifiers", []) or []):
        if getattr(mod, "type", None) != "NODES":
            continue
        if modifier_names and getattr(mod, "name", "") not in modifier_names:
            continue
        for bake in getattr(mod, "bakes", []):
            if bake is None:
                continue
            session_uid = getattr(obj.id_data, "session_uid", 0) or 0
            try:
                with _with_active_object(obj):
                    bpy.ops.object.geometry_node_bake_single(
                        session_uid=session_uid,
                        modifier_name=mod.name,
                        bake_id=bake.bake_id,
                    )
                baked += 1
            except Exception as exc:
                print(
                    f"[BLOSM] WARN GN bake failed for '{obj.name}' "
                    f"modifier='{mod.name}', bake_id={getattr(bake, 'bake_id', None)}: {exc}"
                )
    return baked


def _bake_buildings_geometry_nodes(scene: Optional[bpy.types.Scene]) -> int:
    """Bake the BUILDINGS geometry nodes modifier at the end of the pipeline."""

    if scene is None:
        return 0
    target = bpy.data.objects.get("BUILDINGS")
    if target is None:
        return 0
    names = {"ASSET_BuildingGeoNodes", "BuildingGeo"}
    count = _bake_geometry_nodes_modifiers(target, modifier_names=names)
    if count:
        print(f"[BLOSM] Baked {count} BUILDINGS geometry node modifier(s)")
    return count


def _bake_beam_geometry_nodes(scene: Optional[bpy.types.Scene]) -> int:
    """Bake the geometry nodes modifier(s) applied to the ASSET_BEAM object."""

    if scene is None:
        return 0
    beam = bpy.data.objects.get("ASSET_BEAM")
    if beam is None:
        return 0

    # Ensure bake frame range is 200 frames
    for mod in list(getattr(beam, "modifiers", []) or []):
        if getattr(mod, "type", None) != "NODES":
            continue
        for bake in getattr(mod, "bakes", []):
            try:
                if hasattr(bake, "frame_start"):
                    bake.frame_start = 1
                if hasattr(bake, "frame_end"):
                    bake.frame_end = 200
                print(f"[BLOSM] Set bake frames 1-200 for beam modifier '{mod.name}'")
            except Exception as exc:
                print(f"[BLOSM] WARN failed to set beam bake frames: {exc}")

    count = _bake_geometry_nodes_modifiers(beam)
    if count:
        print(f"[BLOSM] Baked {count} BEAM geometry node modifier(s)")
    return count


def _run_tylers_sandbox(scene: Optional[bpy.types.Scene]) -> Optional[dict[str, object]]:
    """Tyler's personal hook for post-pipeline tweaks."""
    result: dict[str, object] = {}

    if scene is None:
        return None

    if os.environ.get("BLOSM_TYLER_SANDBOX_TEST"):
        scene["tyler_sandbox_flag"] = True
        result["test_flag_set"] = True
        print("[BLOSM] Tyler's Sandbox test flag set on scene")

    # --- BEGIN Tyler's Sandbox (edit below) ---------------------------------
    # Force final scene hygiene: single car, camera collection, CN_TOWER collection.

    # 1) Dedupe ASSET_CAR collections and car objects
    try:
        car_collections = [c for c in bpy.data.collections if getattr(c, "name", "") == "ASSET_CAR"]
        primary_car_collection = car_collections[0] if car_collections else None
        for extra_coll in car_collections[1:]:
            try:
                for obj in list(extra_coll.objects):
                    try:
                        extra_coll.objects.unlink(obj)
                    except Exception:
                        pass
                if extra_coll.users == 0:
                    bpy.data.collections.remove(extra_coll)
            except Exception:
                pass
        if primary_car_collection and scene.collection and primary_car_collection.name not in scene.collection.children:
            try:
                scene.collection.children.link(primary_car_collection)
            except Exception:
                pass
        base_name = "ASSET_CAR"
        car_objects = [o for o in bpy.data.objects if getattr(o, "type", "") == "MESH" and base_name.lower() in (o.name or "").lower()]
        if car_objects:
            canonical = car_objects[0]
            try:
                canonical.name = base_name
            except Exception:
                pass
            for other in car_objects[1:]:
                if other is canonical:
                    continue
                try:
                    bpy.data.objects.remove(other, do_unlink=True)
                except Exception:
                    pass
        result["car_cleanup"] = True

    except Exception as exc:
        print(f"[BLOSM] Sandbox car cleanup failed: {exc}")



    # 3) Ensure CN_TOWER lives in ASSET_CNTower collection only
    try:
        tower = bpy.data.objects.get(CN_TOWER_OBJECT_NAME)
        if tower:
            target_coll = bpy.data.collections.get("ASSET_CNTower")
            if target_coll is None and scene.collection:
                target_coll = bpy.data.collections.new("ASSET_CNTower")
                try:
                    scene.collection.children.link(target_coll)
                except Exception:
                    pass
            if target_coll:
                for coll in list(getattr(tower, "users_collection", []) or []):
                    if coll is target_coll:
                        continue
                    try:
                        coll.objects.unlink(tower)
                    except Exception:
                        pass
                if tower.name not in target_coll.objects:
                    try:
                        target_coll.objects.link(tower)
                    except Exception:
                        pass
                result["cn_tower_collection"] = target_coll.name
    except Exception as exc:
        print(f"[BLOSM] Sandbox CN_TOWER collection fix failed: {exc}")

    # 4) Force auto-smooth shading on island meshes at the very end
    try:
        import bpy as _bpy  # local alias for clarity
        island_obj = _bpy.data.objects.get("Islands_Mesh")
        if island_obj and getattr(island_obj, "type", None) == "MESH":
            mesh = getattr(island_obj, "data", None)
            if mesh is not None and hasattr(mesh, "use_auto_smooth"):
                mesh.use_auto_smooth = True
            view_layer = getattr(_bpy.context, "view_layer", None)
            if view_layer is not None:
                # Isolate selection and run the operator
                try:
                    for obj in getattr(view_layer, "objects", []):
                        try:
                            obj.select_set(False)
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    island_obj.select_set(True)
                except Exception:
                    pass
                try:
                    view_layer.objects.active = island_obj
                except Exception:
                    pass
                try:
                    _bpy.ops.object.shade_auto_smooth()
                except Exception as exc:
                    print(f"[BLOSM] Sandbox island auto smooth failed: {exc}")
            result["island_auto_smooth"] = True
    except Exception as exc:
        print(f"[BLOSM] Sandbox Islands_Mesh auto-smooth failed: {exc}")

    # 5) Force all cameras to use consistent clipping distances
    try:
        CLIP_START = 0.5
        CLIP_END = 50000.0
        for cam in list(bpy.data.cameras):
            try:
                cam.clip_start = CLIP_START
                cam.clip_end = CLIP_END
            except Exception:
                pass
        result["camera_clip"] = {"start": CLIP_START, "end": CLIP_END}
    except Exception as exc:
        print(f"[BLOSM] Sandbox camera clip distances failed: {exc}")

    # 7) Enforce final ground/water plane scales and Z positions, island Z styling, and route Z offset
    try:
        ground = bpy.data.objects.get("Ground_Plane_Result")
        if ground:
            sx, sy, sz = ground.scale
            ground.scale = (sx * 2.0, sy * 2.0, sz)
            loc = list(ground.location)
            loc[2] = 0.0
            ground.location = tuple(loc)
        water = bpy.data.objects.get("Water_Plane_Result")
        if water:
            sx, sy, sz = water.scale
            water.scale = (sx * 4.0, sy * 4.0, sz)
            loc = list(water.location)
            loc[2] = -0.1
            water.location = tuple(loc)
        emissive = bpy.data.objects.get("Water_Plane_Emissive")
        if emissive:
            sx, sy, sz = emissive.scale
            emissive.scale = (sx * 4.0, sy * 4.0, sz)
        islands = bpy.data.objects.get("Islands_Mesh")
        if islands:
            sx, sy, sz = islands.scale
            islands.scale = (sx, sy, 2.0)
            loc = list(islands.location)
            loc[2] = -21.0
            islands.location = tuple(loc)
        # Route curve Z offset
        route_obj = bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")
        if route_obj:
            loc = list(route_obj.location)
            loc[2] = -0.715
            route_obj.location = tuple(loc)
        result["plane_scales"] = {
            "ground": 2.0,
            "water": 4.0,
            "emissive": 4.0,
        }
    except Exception as exc:
        print(f"[BLOSM] Sandbox plane scale adjustments failed: {exc}")

    # 8) Bake building and beam geometry nodes as a final step
    try:
        baked_buildings = _bake_buildings_geometry_nodes(scene)
        if baked_buildings:
            result["building_gn_baked"] = baked_buildings
    except Exception as exc:
        print(f"[BLOSM] Sandbox building GN bake failed: {exc}")

    try:
        baked_beam = _bake_beam_geometry_nodes(scene)
        if baked_beam:
            result["beam_gn_baked"] = baked_beam
    except Exception as exc:
        print(f"[BLOSM] Sandbox beam GN bake failed: {exc}")

    # --- END Tyler's Sandbox -------------------------------------------------

    return result or None


def _set_roads_z_scale(scene: Optional[bpy.types.Scene]) -> bool:
    """Force the ASSET_ROADS object to use a 0.1 Z-scale for stability."""
    if scene is None:
        return False
    road_obj = bpy.data.objects.get("ASSET_ROADS")
    if road_obj is None:
        return False
    try:
        scale = list(getattr(road_obj, "scale", (1.0, 1.0, 1.0)))
        if len(scale) < 3:
            scale = [scale[0], scale[1], 1.0]
        if abs(scale[2] - 0.1) > 1e-9:
            scale[2] = 0.1
            road_obj.scale = tuple(scale)
        return True
    except Exception:
        return False
