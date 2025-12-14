"""
Street label generation (viewport-only) for CashCab.

Creates FONT (Text) objects under a single collection named STREET_LABELS.
The collection and objects are forced to never render.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
import os
import xml.etree.ElementTree as ET

import bpy
from mathutils import Vector


COLLECTION_NAME = "STREET_LABELS"

_MAJOR_HIGHWAYS: Set[str] = {"motorway", "trunk", "primary", "secondary", "tertiary"}


@dataclass(frozen=True)
class _RoadCandidate:
    name: str
    highway: Optional[str]
    obj: bpy.types.Object
    center_world: Tuple[float, float, float]


def _log_warn(msg: str) -> None:
    print(f"[BLOSM] WARN street labels: {msg}")


def ensure_street_labels_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(coll)

    coll.hide_render = True
    coll.hide_viewport = True
    return coll


def set_street_labels_visible(scene: bpy.types.Scene, visible: bool) -> None:
    coll = ensure_street_labels_collection(scene)
    coll.hide_viewport = not bool(visible)


def clear_street_labels(scene: bpy.types.Scene) -> int:
    coll = ensure_street_labels_collection(scene)
    objs = list(coll.objects)
    removed = 0
    for obj in objs:
        try:
            coll.objects.unlink(obj)
        except Exception:
            pass

        # If the label is only used here, remove fully; otherwise just unlink.
        try:
            if getattr(obj, "users_collection", None) and len(obj.users_collection) == 0:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
            elif len(obj.users_collection) <= 1:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
        except Exception:
            # If removal fails for any reason, keep it but ensure it is not renderable.
            try:
                obj.hide_render = True
            except Exception:
                pass
    return removed


def _bbox_center_world(obj: bpy.types.Object) -> Optional[Tuple[float, float, float]]:
    bb = getattr(obj, "bound_box", None)
    if not bb:
        return None
    try:
        pts = [Vector((v[0], v[1], v[2])) for v in bb]
        min_v = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        max_v = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center_local = (min_v + max_v) * 0.5
        center_world = obj.matrix_world @ center_local
        return float(center_world.x), float(center_world.y), float(center_world.z)
    except Exception:
        return None


def _road_name_from_object(obj: bpy.types.Object) -> Optional[str]:
    # Try common tag/property conventions first.
    for key in ("name", "osm:name", "osm_name", "road_name", "street_name"):
        try:
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        except Exception:
            pass

    data = getattr(obj, "data", None)
    if data is not None:
        for key in ("name", "osm:name", "osm_name", "road_name", "street_name"):
            try:
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            except Exception:
                pass

    # Last resort: infer from object name if it contains readable words.
    n = (obj.name or "").strip()
    if not n:
        return None
    low = n.lower()
    if low in {"asset_roads", "roads"}:
        return None
    if low.startswith(("profile_", "profile-roads", "profile_roads", "way_profiles")):
        return None
    if "road" in low and len(n) <= 64:
        return n
    return None


def _highway_from_object(obj: bpy.types.Object) -> Optional[str]:
    for key in ("highway", "osm:highway", "osm_highway"):
        try:
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        except Exception:
            pass
    data = getattr(obj, "data", None)
    if data is not None:
        for key in ("highway", "osm:highway", "osm_highway"):
            try:
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            except Exception:
                pass
    return None


def _iter_candidate_road_objects(scene: bpy.types.Scene) -> Iterable[bpy.types.Object]:
    # Preferred: objects from a known roads collection.
    for coll_name in ("ASSET_ROADS", "ROADS", "Roads"):
        coll = bpy.data.collections.get(coll_name)
        if coll is not None:
            for obj in list(coll.all_objects):
                yield obj
            return

    # Fallback: any object that looks like a road object by name.
    for obj in bpy.data.objects:
        low = (obj.name or "").lower()
        if "road" in low and "profile" not in low and "way_profile" not in low:
            yield obj


def _try_get_osm_dir(scene: bpy.types.Scene) -> Optional[str]:
    # Try explicit osmFilepath first (if present).
    addon = getattr(scene, "blosm", None)
    if addon is not None:
        p = getattr(addon, "osmFilepath", "") or ""
        if p and os.path.exists(p):
            return os.path.dirname(os.path.realpath(p))

    try:
        from ..app import blender as blenderApp

        app_obj = blenderApp.app
        data_dir = getattr(app_obj, "dataDir", None)
        osm_subdir = getattr(app_obj, "osmDir", "osm")
        if data_dir:
            cand = os.path.join(str(data_dir), str(osm_subdir))
            if os.path.isdir(cand):
                return cand
    except Exception:
        pass
    return None


def _find_latest_osm_file(scene: bpy.types.Scene) -> Optional[str]:
    osm_dir = _try_get_osm_dir(scene)
    if not osm_dir:
        return None
    try:
        osm_files = [
            os.path.join(osm_dir, f)
            for f in os.listdir(osm_dir)
            if f.lower().endswith(".osm") and os.path.isfile(os.path.join(osm_dir, f))
        ]
        if not osm_files:
            return None
        osm_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return osm_files[0]
    except Exception:
        return None


def _parse_osm_named_ways(osm_path: str) -> List[Tuple[str, Optional[str], float, float]]:
    """Parse an .osm XML file and return (name, highway, lat, lon) for named ways.

    Uses average node lat/lon as a cheap centroid.
    """
    tree = ET.parse(osm_path)
    root = tree.getroot()

    nodes: Dict[str, Tuple[float, float]] = {}
    for n in root.findall("node"):
        nid = n.get("id")
        lat = n.get("lat")
        lon = n.get("lon")
        if not nid or lat is None or lon is None:
            continue
        try:
            nodes[nid] = (float(lat), float(lon))
        except Exception:
            continue

    out: List[Tuple[str, Optional[str], float, float]] = []
    for w in root.findall("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag") if t.get("k")}
        name = (tags.get("name") or "").strip()
        if not name:
            continue
        highway = tags.get("highway")

        nds = [nd.get("ref") for nd in w.findall("nd") if nd.get("ref")]
        coords = [nodes.get(ref) for ref in nds if ref in nodes]
        coords = [c for c in coords if c is not None]
        if len(coords) < 2:
            continue
        lat_avg = sum(c[0] for c in coords) / float(len(coords))
        lon_avg = sum(c[1] for c in coords) / float(len(coords))
        out.append((name, highway, float(lat_avg), float(lon_avg)))
    return out


def _project_latlon_to_world_xy(scene: bpy.types.Scene, lat: float, lon: float) -> Optional[Tuple[float, float]]:
    try:
        from ..app import blender as blenderApp

        proj = getattr(blenderApp.app, "projection", None)
        if proj is None or not hasattr(proj, "fromGeographic"):
            return None
        x, y, _ = proj.fromGeographic(float(lat), float(lon))
        return float(x), float(y)
    except Exception:
        return None


def _road_candidates(scene: bpy.types.Scene) -> List[_RoadCandidate]:
    out: List[_RoadCandidate] = []
    for obj in _iter_candidate_road_objects(scene):
        if obj is None:
            continue
        if obj.type not in {"MESH", "CURVE"}:
            continue
        if obj.name.startswith(("profile_", "profile_roads", "way_profiles")):
            continue
        if obj.name == COLLECTION_NAME:
            continue

        center = _bbox_center_world(obj)
        if center is None:
            continue

        name = _road_name_from_object(obj)
        highway = _highway_from_object(obj)
        if name is None:
            continue

        out.append(_RoadCandidate(name=name, highway=highway, obj=obj, center_world=center))
    return out


def _create_text_label(
    coll: bpy.types.Collection,
    *,
    name: str,
    location: Tuple[float, float, float],
    text: str,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name=f"{name}_DATA", type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 3.0

    obj = bpy.data.objects.new(name=name, object_data=curve)
    obj.location = location
    obj.rotation_euler = (radians(90.0), 0.0, 0.0)
    obj.hide_render = True
    obj.hide_viewport = False

    # Link only into STREET_LABELS.
    coll.objects.link(obj)
    return obj


def _find_marker(scene: bpy.types.Scene, names: Sequence[str]) -> Optional[bpy.types.Object]:
    for n in names:
        obj = bpy.data.objects.get(n)
        if obj is not None:
            return obj
    return None


def _add_intersection_labels(
    coll: bpy.types.Collection,
    *,
    candidates: List[_RoadCandidate],
    marker_obj: bpy.types.Object,
    prefix: str,
) -> int:
    if not candidates:
        return 0

    loc = marker_obj.matrix_world.translation
    origin = (float(loc.x), float(loc.y), float(loc.z))

    # Find up to 2 distinct names nearby.
    by_dist = sorted(candidates, key=lambda c: (Vector(c.center_world) - Vector(origin)).length)
    names: List[str] = []
    for c in by_dist:
        if c.name not in names:
            names.append(c.name)
        if len(names) >= 2:
            break

    if not names:
        return 0

    label = f"{names[0]}  x  {names[1]}" if len(names) >= 2 else names[0]
    pos = (origin[0], origin[1], origin[2] + 2.0)
    _create_text_label(coll, name=f"{prefix}_INTERSECTION", location=pos, text=label)
    return 1


def generate_street_labels(scene: bpy.types.Scene) -> int:
    coll = ensure_street_labels_collection(scene)
    # Idempotent behavior: clear first.
    clear_street_labels(scene)

    # Preferred: parse the latest OSM file and label named ways.
    picked_names: List[Tuple[str, Optional[str], float, float]] = []
    osm_path = _find_latest_osm_file(scene)
    if osm_path and os.path.exists(osm_path):
        try:
            picked_names = _parse_osm_named_ways(osm_path)
        except Exception as exc:
            _log_warn(f"Failed to parse OSM for names ({osm_path}): {exc}")
            picked_names = []

    created = 0
    seen_names: Set[str] = set()
    if picked_names:
        # Prefer major highways when tag exists.
        majors = [w for w in picked_names if (w[1] in _MAJOR_HIGHWAYS)]
        use = majors if majors else picked_names

        # De-dupe by name and cap to avoid scene spam.
        max_labels = 200
        for name, highway, lat, lon in use:
            if created >= max_labels:
                break
            key = name.strip().lower()
            if key in seen_names:
                continue
            xy = _project_latlon_to_world_xy(scene, lat, lon)
            if xy is None:
                continue
            seen_names.add(key)
            _create_text_label(
                coll,
                name=f"STREET_{created+1:04d}",
                location=(xy[0], xy[1], 0.0),
                text=name,
            )
            created += 1

        # Intersections (best-effort): use nearest named roads by projected distance to markers.
        start_marker = _find_marker(scene, ("MARKER_START", "Start"))
        end_marker = _find_marker(scene, ("MARKER_END", "End"))
        if start_marker is not None or end_marker is not None:
            # Precompute all candidate road points in XY
            road_pts: List[Tuple[str, float, float]] = []
            for name, highway, lat, lon in picked_names:
                xy = _project_latlon_to_world_xy(scene, lat, lon)
                if xy is None:
                    continue
                road_pts.append((name, xy[0], xy[1]))

            def nearest_two(marker_obj: bpy.types.Object) -> List[str]:
                m = marker_obj.matrix_world.translation
                mx, my = float(m.x), float(m.y)
                by_dist = sorted(road_pts, key=lambda r: (r[1] - mx) ** 2 + (r[2] - my) ** 2)
                names: List[str] = []
                for n, _, _ in by_dist:
                    if n not in names:
                        names.append(n)
                    if len(names) >= 2:
                        break
                return names

            if start_marker is not None:
                names = nearest_two(start_marker)
                if names:
                    label = f"{names[0]}  x  {names[1]}" if len(names) >= 2 else names[0]
                    pos = start_marker.matrix_world.translation
                    _create_text_label(
                        coll,
                        name="START_INTERSECTION",
                        location=(float(pos.x), float(pos.y), float(pos.z) + 2.0),
                        text=label,
                    )
                    created += 1
            if end_marker is not None:
                names = nearest_two(end_marker)
                if names:
                    label = f"{names[0]}  x  {names[1]}" if len(names) >= 2 else names[0]
                    pos = end_marker.matrix_world.translation
                    _create_text_label(
                        coll,
                        name="END_INTERSECTION",
                        location=(float(pos.x), float(pos.y), float(pos.z) + 2.0),
                        text=label,
                    )
                    created += 1
    else:
        # Fallback: object-based detection (may only find ASSET_ROADS in some scenes).
        candidates = _road_candidates(scene)
        if not candidates:
            _log_warn("No candidate road objects found; nothing to label.")
            return 0

        majors = [c for c in candidates if (c.highway in _MAJOR_HIGHWAYS)]
        picked = majors if majors else candidates

        seen: Set[Tuple[str, int, int]] = set()
        for c in picked:
            key = (c.name, int(c.center_world[0] // 10), int(c.center_world[1] // 10))
            if key in seen:
                continue
            seen.add(key)

            _create_text_label(
                coll,
                name=f"STREET_{len(seen):04d}",
                location=c.center_world,
                text=c.name,
            )
            created += 1

        start_marker = _find_marker(scene, ("MARKER_START", "Start"))
        end_marker = _find_marker(scene, ("MARKER_END", "End"))
        if start_marker is not None:
            created += _add_intersection_labels(coll, candidates=candidates, marker_obj=start_marker, prefix="START")
        if end_marker is not None:
            created += _add_intersection_labels(coll, candidates=candidates, marker_obj=end_marker, prefix="END")

    # Always enforce non-render visibility; keep collection hidden by default.
    coll.hide_render = True
    coll.hide_viewport = True
    for obj in list(coll.objects):
        try:
            obj.hide_render = True
        except Exception:
            pass

    return created

