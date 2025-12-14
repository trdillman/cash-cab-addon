"""
Street label generation (viewport-only) for CashCab.

Creates FONT (Text) objects under a single collection named STREET_LABELS.
The collection and objects are forced to never render.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

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

    candidates = _road_candidates(scene)
    if not candidates:
        _log_warn("No candidate road objects found; nothing to label.")
        return 0

    # Prefer major roads if we have highway tags; otherwise keep all named candidates.
    majors = [c for c in candidates if (c.highway in _MAJOR_HIGHWAYS)]
    picked = majors if majors else candidates

    created = 0
    seen: Set[Tuple[str, int, int]] = set()
    for c in picked:
        # Deduplicate by name + coarse XY position.
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

    # Nice-to-have: add intersection labels near start/end markers if they exist.
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

