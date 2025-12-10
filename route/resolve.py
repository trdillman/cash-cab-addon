from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence

import bpy

from . import assets as route_assets

_KIND_ATTR = {
    "materials": "materials",
    "node_groups": "node_groups",
    "objects": "objects",
    "collections": "collections",
    "worlds": "worlds",
}

ROUTE_NAME_CANDIDATES = ("ROUTE", "Route", "route")


def _get_kind_container(kind: str):
    attr = _KIND_ATTR.get(kind)
    if not attr:
        raise ValueError(f"Unsupported datablock kind: {kind}")
    container = getattr(bpy.data, attr, None)
    if container is None:
        raise ValueError(f"Unsupported datablock container: {kind}")
    return container


def list_blend_datablocks(filepath: Path | str, kind: str) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        print(f"[BLOSM] WARN asset library missing: {path}")
        return []
    try:
        with bpy.data.libraries.load(str(path), link=False) as (data_from, _):
            values = getattr(data_from, kind, []) or []
            return [name for name in values if isinstance(name, str) and name]
    except Exception as exc:
        print(f"[BLOSM] ERROR asset scan failed for {path.name}: {exc}")
        return []


def ensure_appended(filepath: Path | str, kind: str, names: Iterable[str] | None = None) -> Dict[str, bool]:
    all_names = list(names) if names is not None else list_blend_datablocks(filepath, kind)
    result: Dict[str, bool] = {}
    if not all_names:
        return result

    container = _get_kind_container(kind)
    missing = [name for name in all_names if name and name not in container]
    appended_now: set[str] = set()
    if missing:
        path = Path(filepath)
        if not path.exists():
            print(f"[BLOSM] WARN asset file missing: {path}")
        else:
            try:
                with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
                    available = set(getattr(data_from, kind, []) or [])
                    to_load = [name for name in missing if name in available]
                    setattr(data_to, kind, to_load)
                    appended_now.update(to_load)
            except Exception as exc:
                print(f"[BLOSM] ERROR append failed for {path.name}: {exc}")
    for name in all_names:
        appended = name in appended_now
        present = bool(name and name in container)
        result[name] = appended if present else False
    return result


def get_present_names(kind: str) -> set[str]:
    container = _get_kind_container(kind)
    return {item.name for item in container}


def choose(kind: str, prefer_substring: str | None = None) -> Optional[str]:
    names = sorted(get_present_names(kind))
    if not names:
        return None
    if prefer_substring:
        needle = prefer_substring.casefold()
        for name in names:
            if needle in name.casefold():
                return name
    return names[0]


def _iter_scene_curves(context: bpy.types.Context):
    scene = getattr(context, "scene", None)
    if scene:
        for obj in scene.objects:
            if obj.type == 'CURVE':
                yield obj


def resolve_route_obj(context: bpy.types.Context) -> Optional[bpy.types.Object]:
    view_layer = getattr(context, 'view_layer', None)
    if view_layer:
        layer_objects = getattr(view_layer, 'objects', None)
        if layer_objects is not None:
            active = getattr(layer_objects, 'active', None)
            if active and active.type == 'CURVE':
                try:
                    if active.select_get():
                        return active
                except Exception:
                    return active
    selected = getattr(context, 'selected_objects', None)
    if selected:
        for obj in selected:
            if obj and obj.type == 'CURVE':
                return obj
    for obj in _iter_scene_curves(context):
        return obj
    for candidate in ROUTE_NAME_CANDIDATES:
        existing = bpy.data.objects.get(candidate)
        if existing and existing.type == 'CURVE':
            return existing
    for obj in bpy.data.objects:
        if obj.type == 'CURVE' and 'route' in obj.name.casefold():
            return obj
    return None


def _link_to_assets_collection(
    obj: Optional[bpy.types.Object],
    *,
    context: Optional[bpy.types.Context] = None,
) -> None:
    if obj is None:
        return
    collection = bpy.data.collections.get(route_assets.ASSETS_COLLECTION_NAME)
    scene = getattr(context, 'scene', None) if context else getattr(bpy.context, 'scene', None)
    if collection is None:
        collection = bpy.data.collections.new(route_assets.ASSETS_COLLECTION_NAME)
        if scene:
            try:
                scene.collection.children.link(collection)
            except RuntimeError:
                pass
    if collection and obj.name not in collection.objects.keys():
        try:
            collection.objects.link(obj)
        except RuntimeError:
            pass
    if collection:
        collection.hide_viewport = False
        collection.hide_render = False


def _prune_duplicate_cars(active: bpy.types.Object, canonical: str) -> None:
    active_data = getattr(active, 'data', None)
    for other in list(bpy.data.objects):
        if other is active:
            continue
        name_cf = other.name.casefold()
        if other.name == canonical or other.name.startswith(f"{canonical}.") or name_cf.startswith('routepreview'):
            same_mesh = getattr(other, 'data', None) is active_data if active_data else False
            if same_mesh or name_cf.startswith('routepreview'):
                try:
                    bpy.data.objects.remove(other, do_unlink=True)
                except Exception:
                    pass


def _pick_from_candidates(
    candidates: Sequence[str],
    prefer: Sequence[str] | None = None,
    *,
    fallback_contains: str | None = None,
) -> Optional[str]:
    ordered = [name for name in candidates if name]
    if not ordered:
        return None
    prefer = prefer or ()
    for name in prefer:
        if name and name in ordered:
            return name
    if fallback_contains:
        needle = fallback_contains.casefold()
        for name in ordered:
            if needle in name.casefold():
                return name
    return ordered[0]


def resolve_material(preferred_names: Sequence[str] | None = None) -> Optional[bpy.types.Material]:
    names = list_blend_datablocks(route_assets.ROUTE_BLEND_PATH, 'materials')
    ensure_appended(route_assets.ROUTE_BLEND_PATH, 'materials', names)
    pick = _pick_from_candidates(names, preferred_names, fallback_contains='route')
    if pick is None:
        pick = choose('materials', 'route')
    return bpy.data.materials.get(pick) if pick else None


def resolve_node_group(preferred_names: Sequence[str] | None = None) -> Optional[bpy.types.NodeTree]:
    names = list_blend_datablocks(route_assets.ROUTE_BLEND_PATH, 'node_groups')
    ensure_appended(route_assets.ROUTE_BLEND_PATH, 'node_groups', names)
    pick = _pick_from_candidates(names, preferred_names, fallback_contains='route')
    if pick is None:
        pick = choose('node_groups', 'route')
    return bpy.data.node_groups.get(pick) if pick else None


def resolve_object(
    preferred_names: Sequence[str] | None = None,
    *,
    context: Optional[bpy.types.Context] = None,
) -> Optional[bpy.types.Object]:
    names = list_blend_datablocks(route_assets.CAR_BLEND_PATH, 'objects')
    # Only append the specific car object we intend to use, to avoid
    # bringing in template/curve objects (e.g. CAR_TRAIL) from the asset.
    pick = _pick_from_candidates(names, preferred_names, fallback_contains='car')
    if not pick and names:
        pick = names[0]
    if pick:
        ensure_appended(route_assets.CAR_BLEND_PATH, 'objects', [pick])
    else:
        pick = choose('objects', 'car')
    obj = bpy.data.objects.get(pick) if pick else None
    if obj is None:
        return None
    canonical = pick
    if obj.name != canonical:
        try:
            obj.name = canonical
        except Exception:
            canonical = obj.name
    _prune_duplicate_cars(obj, canonical)
    _link_to_assets_collection(obj, context=context)
    obj.hide_viewport = False
    obj.hide_render = False
    try:
        obj.hide_set(False)
    except AttributeError:
        pass
    return obj


def resolved_names() -> Dict[str, Optional[str]]:
    material = resolve_material()
    node_group = resolve_node_group()
    car_obj = resolve_object()
    return {
        'route_material': material.name if material else None,
        'route_node': node_group.name if node_group else None,
        'car_object': car_obj.name if car_obj else None,
    }
