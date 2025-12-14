"""
Interactive Route Adjuster

Creates route control empties (start/end + optional via points) and provides a
recompute helper that re-routes based on their locations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import bpy
from mathutils import Vector

from . import pipeline_finalizer
from . import uturn_trim
from .config import DEFAULT_CONFIG
from .utils import GeocodeResult, RouteServiceError, fetch_route


CONTROL_COLLECTION_NAME = "ROUTE_CONTROLS"
CTRL_START_NAME = "ROUTE_CTRL_START"
CTRL_END_NAME = "ROUTE_CTRL_END"
CTRL_VIA_PREFIX = "ROUTE_CTRL_VIA_"

MARKER_START_OBJ_NAME = "MARKER_START"
MARKER_END_OBJ_NAME = "MARKER_END"
MARKER_END_Z = 30.0


@dataclass(frozen=True)
class CtrlPoint:
    role: str  # START | VIA | END
    obj: bpy.types.Object


def _ensure_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    coll = bpy.data.collections.get(CONTROL_COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(CONTROL_COLLECTION_NAME)
    coll.hide_render = True
    if scene.collection and coll.name not in scene.collection.children.keys():
        scene.collection.children.link(coll)
    return coll


def _route_obj(scene: bpy.types.Scene) -> Optional[bpy.types.Object]:
    name = getattr(scene, "blosm_route_object_name", "") or ""
    obj = bpy.data.objects.get(name) if name else None
    if obj is None:
        obj = bpy.data.objects.get(DEFAULT_CONFIG.objects.route_object_name)
    if obj is None:
        obj = bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")
    if obj is None or obj.type != "CURVE":
        return None
    return obj


def _curve_endpoints_world(route_obj: bpy.types.Object) -> Tuple[Optional[Vector], Optional[Vector]]:
    data = getattr(route_obj, "data", None)
    splines = list(getattr(data, "splines", []) or [])
    if not splines:
        return None, None
    spline = splines[0]
    if getattr(spline, "type", "") == "BEZIER":
        pts = list(getattr(spline, "bezier_points", []) or [])
        if len(pts) < 2:
            return None, None
        a = route_obj.matrix_world @ pts[0].co
        b = route_obj.matrix_world @ pts[-1].co
        return a, b
    pts = list(getattr(spline, "points", []) or [])
    if len(pts) < 2:
        return None, None
    a = route_obj.matrix_world @ pts[0].co.xyz
    b = route_obj.matrix_world @ pts[-1].co.xyz
    return a, b


def _new_empty(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 10.0
    obj.show_in_front = True
    obj.hide_render = True
    try:
        obj["cc_route_ctrl_name"] = name
    except Exception:
        pass
    return obj


def _ensure_obj_linked(coll: bpy.types.Collection, obj: bpy.types.Object) -> None:
    if obj.name not in coll.objects.keys():
        coll.objects.link(obj)


def ensure_route_control_empties(scene: bpy.types.Scene) -> bool:
    route_obj = _route_obj(scene)
    if route_obj is None:
        return False

    coll = _ensure_collection(scene)
    start_obj = bpy.data.objects.get(CTRL_START_NAME)
    end_obj = bpy.data.objects.get(CTRL_END_NAME)
    if start_obj is None:
        start_obj = _new_empty(CTRL_START_NAME)
    if end_obj is None:
        end_obj = _new_empty(CTRL_END_NAME)

    _ensure_obj_linked(coll, start_obj)
    _ensure_obj_linked(coll, end_obj)

    start_w, end_w = _curve_endpoints_world(route_obj)
    if start_w is not None:
        start_obj.location = start_w
        try:
            start_obj["cc_route_ctrl_role"] = "START"
        except Exception:
            pass
    if end_w is not None:
        end_obj.location = end_w
        try:
            end_obj["cc_route_ctrl_role"] = "END"
        except Exception:
            pass
    return True


def _iter_via_controls() -> List[bpy.types.Object]:
    vias = [o for o in bpy.data.objects if o.name.startswith(CTRL_VIA_PREFIX)]
    vias.sort(key=lambda o: o.name)
    return vias


def iter_all_controls() -> List[bpy.types.Object]:
    objs: List[bpy.types.Object] = []
    start = bpy.data.objects.get(CTRL_START_NAME)
    end = bpy.data.objects.get(CTRL_END_NAME)
    if start is not None:
        objs.append(start)
    objs.extend(_iter_via_controls())
    if end is not None:
        objs.append(end)
    return objs


def create_via_control(scene: bpy.types.Scene) -> Optional[bpy.types.Object]:
    route_obj = _route_obj(scene)
    if route_obj is None:
        return None

    coll = _ensure_collection(scene)
    existing = _iter_via_controls()
    next_idx = len(existing) + 1
    name = f"{CTRL_VIA_PREFIX}{next_idx:03d}"
    obj = _new_empty(name)
    try:
        obj["cc_route_ctrl_role"] = "VIA"
        obj["cc_route_ctrl_index"] = int(next_idx)
    except Exception:
        pass

    a, b = _curve_endpoints_world(route_obj)
    if a is not None and b is not None:
        obj.location = (a + b) * 0.5
    _ensure_obj_linked(coll, obj)
    return obj


def clear_via_controls() -> int:
    vias = _iter_via_controls()
    removed = 0
    for obj in vias:
        try:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
        except Exception:
            pass
    return removed


def _projection(scene: bpy.types.Scene):
    from ..app import blender as blenderApp

    app_obj = blenderApp.app
    proj = getattr(app_obj, "projection", None)
    if proj is None:
        try:
            app_obj.setProjection(0.0, 0.0)
            proj = app_obj.projection
        except Exception:
            proj = None
    return proj


def _world_to_geographic(scene: bpy.types.Scene, world_xyz: Vector) -> Tuple[float, float]:
    proj = _projection(scene)
    if proj is None or not hasattr(proj, "toGeographic"):
        raise RouteServiceError("Projection is not available for route adjustment")
    lat, lon = proj.toGeographic(float(world_xyz.x), float(world_xyz.y))
    return float(lat), float(lon)


def _geographic_to_world(scene: bpy.types.Scene, lat: float, lon: float, z: float) -> Vector:
    proj = _projection(scene)
    if proj is None or not hasattr(proj, "fromGeographic"):
        raise RouteServiceError("Projection is not available for route adjustment")
    x, y, _ = proj.fromGeographic(float(lat), float(lon))
    return Vector((float(x), float(y), float(z)))


def _snap_latlon(
    lat: float,
    lon: float,
    user_agent: str,
    allow_any_highway_fallback: bool,
) -> Tuple[float, float]:
    from . import utils as route_utils

    snapped = route_utils._snap_to_road_centerline(
        lat,
        lon,
        user_agent=user_agent,
        street_name=None,
        allow_any_highway_fallback=allow_any_highway_fallback,
    )
    if snapped is None:
        return lat, lon
    return float(snapped[0]), float(snapped[1])


def _sync_scene_markers(scene: bpy.types.Scene, start_world: Vector, end_world: Vector) -> None:
    start_empty = bpy.data.objects.get(DEFAULT_CONFIG.objects.start_marker_name) or bpy.data.objects.get("Start")
    end_empty = bpy.data.objects.get(DEFAULT_CONFIG.objects.end_marker_name) or bpy.data.objects.get("End")
    if start_empty is not None:
        start_empty.location = start_world
    if end_empty is not None:
        end_empty.location = end_world

    marker_start = bpy.data.objects.get(MARKER_START_OBJ_NAME)
    if marker_start is not None:
        marker_start.location = start_empty.location if start_empty is not None else start_world

    marker_end = bpy.data.objects.get(MARKER_END_OBJ_NAME)
    if marker_end is not None:
        if end_empty is not None:
            marker_end.location = (end_empty.location.x, end_empty.location.y, MARKER_END_Z)
        else:
            marker_end.location = (end_world.x, end_world.y, MARKER_END_Z)


def recompute_route_from_controls(context) -> bool:
    scene = getattr(context, "scene", None)
    if scene is None:
        return False

    route_obj = _route_obj(scene)
    if route_obj is None:
        return False

    addon = getattr(scene, "blosm", None)
    user_agent = getattr(DEFAULT_CONFIG.api, "user_agent", "CashCab/RouteAdjuster")
    snap_points = bool(getattr(addon, "route_adjuster_snap_points", False)) if addon else False
    allow_any_highway = bool(getattr(addon, "route_adjuster_allow_any_highway_fallback", False)) if addon else False

    start_ctrl = bpy.data.objects.get(CTRL_START_NAME)
    end_ctrl = bpy.data.objects.get(CTRL_END_NAME)
    if start_ctrl is None or end_ctrl is None:
        return False

    z = 0.0
    try:
        data = route_obj.data
        if data.splines and data.splines[0].points:
            z = float(data.splines[0].points[0].co[2])
    except Exception:
        z = 0.0

    start_lat, start_lon = _world_to_geographic(scene, start_ctrl.matrix_world.translation)
    end_lat, end_lon = _world_to_geographic(scene, end_ctrl.matrix_world.translation)

    via_objs = _iter_via_controls()
    via_geos: List[Tuple[float, float]] = []
    for o in via_objs:
        lat, lon = _world_to_geographic(scene, o.matrix_world.translation)
        via_geos.append((lat, lon))

    if snap_points:
        start_lat, start_lon = _snap_latlon(
            start_lat,
            start_lon,
            user_agent=user_agent,
            allow_any_highway_fallback=allow_any_highway,
        )
        end_lat, end_lon = _snap_latlon(
            end_lat,
            end_lon,
            user_agent=user_agent,
            allow_any_highway_fallback=allow_any_highway,
        )
        via_geos = [
            _snap_latlon(lat, lon, user_agent=user_agent, allow_any_highway_fallback=allow_any_highway)
            for lat, lon in via_geos
        ]

    start = GeocodeResult(address="Route Control Start", lat=start_lat, lon=start_lon, display_name="Route Control Start")
    end = GeocodeResult(address="Route Control End", lat=end_lat, lon=end_lon, display_name="Route Control End")
    waypoints = [
        GeocodeResult(address=f"Route Via {i+1}", lat=lat, lon=lon, display_name=f"Route Via {i+1}")
        for i, (lat, lon) in enumerate(via_geos)
    ]

    route = fetch_route(start, end, user_agent=user_agent, waypoints=waypoints if waypoints else None)
    if not getattr(route, "points", None) or len(route.points) < 2:
        raise RouteServiceError("Route service returned an empty route")

    coords_world = [_geographic_to_world(scene, lat, lon, z) for (lat, lon) in route.points]
    inv = route_obj.matrix_world.inverted()
    coords_local = [(float((inv @ p).x), float((inv @ p).y), float((inv @ p).z)) for p in coords_world]

    uturn_trim._set_curve_poly_coords_local(route_obj, coords_local)
    uturn_trim.ensure_route_raw_coords(route_obj, coords_local)

    start_ctrl.location = coords_world[0]
    end_ctrl.location = coords_world[-1]
    if snap_points:
        for obj, (lat, lon) in zip(via_objs, via_geos):
            obj.location = _geographic_to_world(scene, lat, lon, z)

    _sync_scene_markers(scene, coords_world[0], coords_world[-1])

    try:
        pipeline_finalizer._force_car_trail_polyline_from_route(scene)
        pipeline_finalizer.run_resample_on_car_trail()
    except Exception:
        pass

    return True

