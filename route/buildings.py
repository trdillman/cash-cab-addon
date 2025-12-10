"""Operators for applying building Geometry Nodes setups."""

from __future__ import annotations

import bpy

from bpy.types import Operator

from . import assets as route_assets
from . import resolve as route_resolve
from .config import DEFAULT_CONFIG

BUILDING_MODIFIER_NAME = DEFAULT_CONFIG.objects.building_modifier_name


def _normalize_socket_type(value: str | None) -> str | None:
    if value is None:
        return None
    value_str = str(value)
    if value_str in {'MATERIAL', 'OBJECT'}:
        return value_str
    value_lower = value_str.lower()
    if 'material' in value_lower:
        return 'MATERIAL'
    if 'object' in value_lower:
        return 'OBJECT'
    return value_str


def _object_input_index(node_group: bpy.types.NodeTree) -> int | None:
    inputs = getattr(node_group, 'inputs', None)
    if inputs is not None:
        for idx, socket in enumerate(inputs):
            if _normalize_socket_type(getattr(socket, 'type', None)) == 'OBJECT':
                return idx
        return None
    interface = getattr(node_group, 'interface', None)
    if interface is None:
        return None
    interface_inputs = getattr(interface, 'inputs', None)
    if interface_inputs is not None:
        for idx, socket in enumerate(interface_inputs):
            if _normalize_socket_type(getattr(socket, 'socket_type', None)) == 'OBJECT':
                return idx
        return None
    items_tree = getattr(interface, 'items_tree', None)
    if items_tree is not None:
        index = 0
        for item in items_tree:
            if getattr(item, 'item_type', None) == 'SOCKET' and getattr(item, 'in_out', None) == 'INPUT':
                if _normalize_socket_type(getattr(item, 'socket_type', None)) == 'OBJECT':
                    return index
                index += 1
    return None


def _discover_building_group() -> tuple[str | None, bpy.types.NodeTree | None]:
    summary = route_assets.get_last_summary()
    name = summary.get('bld_ng') if summary else None
    if name and bpy.data.node_groups.get(name):
        return name, bpy.data.node_groups.get(name)
    candidates = route_resolve.list_blend_datablocks(route_assets.BUILD_BLEND_PATH, 'node_groups')
    route_resolve.ensure_appended(route_assets.BUILD_BLEND_PATH, 'node_groups', candidates)
    picked = None
    for candidate in candidates:
        if candidate and 'build' in candidate.casefold():
            picked = candidate
            break
    if picked is None and candidates:
        picked = candidates[0]
    return picked, bpy.data.node_groups.get(picked) if picked else None


def _discover_car_object(context: bpy.types.Context) -> bpy.types.Object | None:
    summary = route_assets.get_last_summary()
    name = summary.get('car_obj') if summary else None
    if name and bpy.data.objects.get(name):
        return bpy.data.objects.get(name)
    return route_resolve.resolve_object((name,) if name else None, context=context)


def _candidate_building_objects() -> list[bpy.types.Object]:
    candidates: dict[str, bpy.types.Object] = {}
    for collection in bpy.data.collections:
        if 'building' in collection.name.casefold():
            for obj in collection.objects:
                if obj.type == 'MESH':
                    candidates[obj.name] = obj
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'building' in obj.name.casefold():
            candidates.setdefault(obj.name, obj)
    return list(candidates.values())


def apply_building_nodes(context: bpy.types.Context):
    group_name, node_group = _discover_building_group()
    if not node_group:
        raise RuntimeError('Building node group not available')
    car_obj = _discover_car_object(context)
    if not car_obj:
        raise RuntimeError('ASSET_CAR object missing')
    object_input_index = _object_input_index(node_group)
    candidates = _candidate_building_objects()
    modified = 0
    skipped = 0
    for obj in candidates:
        modifier = obj.modifiers.get(BUILDING_MODIFIER_NAME)
        if modifier and modifier.type == 'NODES':
            skipped += 1
        else:
            modifier = obj.modifiers.new(BUILDING_MODIFIER_NAME, 'NODES')
            modified += 1
        modifier.node_group = node_group
        if object_input_index is not None:
            modifier[f"Input_{object_input_index}"] = car_obj
        # Enable the modifier so Building GeoNodes are active; the pipeline
        # finalizer will still perform any additional visibility tweaks.
        modifier.show_viewport = True
        modifier.show_render = True
    return {
        'group_name': group_name,
        'car_obj': car_obj.name,
        'candidates': len(candidates),
        'modified': modified,
        'skipped': skipped,
    }


class BLOSM_OT_apply_building_nodes(Operator):
    bl_idname = "blosm.apply_building_nodes"
    bl_label = "Apply Buildings GeoNodes (disabled)"
    bl_description = "Attach the Building Geometry Nodes (disabled) to building meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            summary = apply_building_nodes(context)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}

        print(
            f"[BLOSM] building_nodes_applied: group={summary['group_name']}, car={summary['car_obj']}, "
            f"candidates={summary['candidates']}, modified={summary['modified']}, skipped={summary['skipped']}, disabled=True"
        )
        return {'FINISHED'}


class BLOSM_OT_building_nodes_check(Operator):
    bl_idname = "blosm.building_nodes_check"
    bl_label = "Building Nodes Self-Check"
    bl_description = "Report status of Building Geometry Nodes on building meshes"
    bl_options = {'REGISTER'}

    def execute(self, context):
        summary = route_assets.get_last_summary()
        group_name = summary.get('bld_ng') if summary else None
        car_name = summary.get('car_obj') if summary else None
        car_obj = bpy.data.objects.get(car_name) if car_name else None
        candidates = _candidate_building_objects()
        sampled = candidates[:10]
        ok = True
        disabled_all = True
        object_ok = True
        for obj in sampled:
            modifier = obj.modifiers.get(BUILDING_MODIFIER_NAME)
            if not modifier or modifier.type != 'NODES' or not modifier.node_group:
                ok = False
                break
            if group_name and modifier.node_group.name != group_name:
                ok = False
            disabled_all = disabled_all and not modifier.show_viewport and not modifier.show_render
            idx = _object_input_index(modifier.node_group)
            if idx is not None:
                value = modifier.get(f"Input_{idx}")
                if car_obj and value is not car_obj:
                    object_ok = False
            else:
                object_ok = False
        print(
            f"[BLOSM] building_nodes_check: sampled={len(sampled)}, ok={ok}, disabled_all={disabled_all}, object_ok={object_ok}"
        )
        return {'FINISHED'}


__all__ = (
    'apply_building_nodes',
    'BUILDING_MODIFIER_NAME',
)


def register():
    bpy.utils.register_class(BLOSM_OT_apply_building_nodes)
    bpy.utils.register_class(BLOSM_OT_building_nodes_check)


def unregister():
    bpy.utils.unregister_class(BLOSM_OT_building_nodes_check)
    bpy.utils.unregister_class(BLOSM_OT_apply_building_nodes)
