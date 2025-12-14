"""
Runtime helpers for trimming start/end U-turns on the ROUTE curve.

This is a convenience feature intended to be toggled after route import without
changing object identity (constraints/materials keep working).
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import bpy
from mathutils import Vector

from .config import DEFAULT_CONFIG
from .geometry_simplifier import trim_end_uturns


_RAW_FLAT_KEY = "cc_route_raw_coords_flat"
_RAW_COUNT_KEY = "cc_route_raw_coords_count"


def _flatten_coords(coords: Sequence[Tuple[float, float, float]]) -> List[float]:
    flat: List[float] = []
    for x, y, z in coords:
        flat.extend((float(x), float(y), float(z)))
    return flat


def _unflatten_coords(flat: Sequence[float], count: int) -> List[Tuple[float, float, float]]:
    coords: List[Tuple[float, float, float]] = []
    n = min(len(flat) // 3, int(count))
    for i in range(n):
        x = float(flat[3 * i + 0])
        y = float(flat[3 * i + 1])
        z = float(flat[3 * i + 2])
        coords.append((x, y, z))
    return coords


def _route_obj_from_context(context) -> Optional[bpy.types.Object]:
    scene = getattr(context, "scene", None)
    addon = getattr(scene, "blosm", None) if scene else None

    route_obj = None
    if addon is not None:
        route_obj = getattr(addon, "route_curve_obj", None)
        if route_obj is None:
            name = getattr(addon, "route_curve_name", "") or ""
            if name:
                route_obj = bpy.data.objects.get(name)

    if route_obj is None:
        route_obj = bpy.data.objects.get(DEFAULT_CONFIG.objects.route_object_name)
    if route_obj is None:
        route_obj = bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")
    if route_obj is None or getattr(route_obj, "type", None) != "CURVE":
        return None
    return route_obj


def _curve_poly_coords_local(route_obj: bpy.types.Object) -> List[Tuple[float, float, float]]:
    curve = route_obj.data
    if not curve.splines:
        return []
    spline = curve.splines[0]
    pts = getattr(spline, "points", None)
    if pts is None:
        return []
    coords = [(float(p.co[0]), float(p.co[1]), float(p.co[2])) for p in pts]
    return coords


def _set_curve_poly_coords_local(route_obj: bpy.types.Object, coords: Sequence[Tuple[float, float, float]]) -> None:
    if len(coords) < 2:
        raise ValueError("Route geometry is too short")

    curve = route_obj.data
    curve.dimensions = DEFAULT_CONFIG.objects.curve_dimensions
    curve.bevel_depth = DEFAULT_CONFIG.objects.curve_bevel_depth
    curve.splines.clear()

    spline = curve.splines.new("POLY")
    spline.use_cyclic_u = False
    spline.points.add(len(coords) - 1)
    for idx, (x, y, z) in enumerate(coords):
        spline.points[idx].co = (float(x), float(y), float(z), 1.0)

    route_obj.location = (0.0, 0.0, 0.0)
    route_obj.select_set(False)

    try:
        route_obj["blosm_origin"] = "osm"
        route_obj["blosm_role"] = "route_curve_osm"
    except Exception:
        pass


def ensure_route_raw_coords(route_obj: bpy.types.Object, coords_raw: Sequence[Tuple[float, float, float]]) -> None:
    """Persist the untrimmed local-space route coordinates on the ROUTE object."""
    try:
        route_obj[_RAW_FLAT_KEY] = _flatten_coords(coords_raw)
        route_obj[_RAW_COUNT_KEY] = int(len(coords_raw))
    except Exception:
        # ID properties can fail for extremely large routes or when locked; keep it best-effort.
        pass


def get_route_raw_coords(route_obj: bpy.types.Object) -> Optional[List[Tuple[float, float, float]]]:
    flat = route_obj.get(_RAW_FLAT_KEY)
    count = route_obj.get(_RAW_COUNT_KEY)
    if flat is None or count is None:
        return None
    try:
        return _unflatten_coords(list(flat), int(count))
    except Exception:
        return None


def compute_trimmed_coords(
    coords_raw: Sequence[Tuple[float, float, float]],
    *,
    window_fraction: float = 0.10,
    corner_angle_min: float = 70.0,
    direction_reverse_deg: float = 150.0,
    max_uturn_fraction: float = 0.10,
) -> List[Tuple[float, float, float]]:
    pts = [Vector((float(c[0]), float(c[1]), float(c[2]))) for c in coords_raw]
    trimmed = trim_end_uturns(
        pts,
        window_fraction=float(window_fraction),
        corner_angle_min=float(corner_angle_min),
        direction_reverse_deg=float(direction_reverse_deg),
        max_uturn_fraction=float(max_uturn_fraction),
    )
    return [(float(p.x), float(p.y), float(p.z)) for p in trimmed]


def apply_route_uturn_trim(context, *, enabled: bool) -> bool:
    """Apply or restore end-segment U-turn trimming on the ROUTE curve."""
    route_obj = _route_obj_from_context(context)
    if route_obj is None:
        return False

    coords_raw = get_route_raw_coords(route_obj)
    if coords_raw is None:
        # Fallback: capture current geometry as "raw" so the toggle remains reversible.
        current = _curve_poly_coords_local(route_obj)
        if len(current) < 2:
            return False
        coords_raw = current
        ensure_route_raw_coords(route_obj, coords_raw)

    coords_target = coords_raw
    if enabled:
        scene = getattr(context, "scene", None)
        addon = getattr(scene, "blosm", None) if scene else None
        coords_target = compute_trimmed_coords(
            coords_raw,
            window_fraction=float(getattr(addon, "route_trim_window_fraction", 0.10)) if addon else 0.10,
            corner_angle_min=float(getattr(addon, "route_trim_corner_angle_min", 70.0)) if addon else 70.0,
            direction_reverse_deg=float(getattr(addon, "route_trim_direction_reverse_deg", 150.0)) if addon else 150.0,
            max_uturn_fraction=float(getattr(addon, "route_trim_max_uturn_fraction", 0.10)) if addon else 0.10,
        )

    if len(coords_target) < 2:
        return False

    _set_curve_poly_coords_local(route_obj, coords_target)

    # Keep Start/End empties aligned to route endpoints if present.
    start_obj = bpy.data.objects.get(DEFAULT_CONFIG.objects.start_marker_name) or bpy.data.objects.get("Start")
    end_obj = bpy.data.objects.get(DEFAULT_CONFIG.objects.end_marker_name) or bpy.data.objects.get("End")
    if start_obj is not None:
        start_obj.location = coords_target[0]
    if end_obj is not None:
        end_obj.location = coords_target[-1]

    # Best-effort: keep CAR_TRAIL equivalent to ROUTE if it exists.
    try:
        from . import pipeline_finalizer

        pipeline_finalizer._force_car_trail_polyline_from_route(getattr(context, "scene", None))
        pipeline_finalizer.run_resample_on_car_trail()
    except Exception:
        pass

    return True
