"""Operators for attaching route-related Geometry Nodes."""

from __future__ import annotations

import bpy
from typing import Optional

from bpy.types import Operator

from . import assets as route_assets
from . import resolve as route_resolve
from .config import DEFAULT_CONFIG

ROUTE_MODIFIER_NAME = DEFAULT_CONFIG.objects.route_modifier_name


def _resolve_modifier_input(modifier: bpy.types.Modifier | None, index: int | None) -> str | None:
    if modifier is None or index is None:
        return None
    node_group = getattr(modifier, 'node_group', None)
    if node_group is None:
        return None
    interface = getattr(node_group, 'interface', None)
    if interface is not None:
        items_tree = getattr(interface, 'items_tree', None)
        if items_tree is not None:
            count = 0
            for item in items_tree:
                if getattr(item, 'item_type', None) == 'SOCKET' and getattr(item, 'in_out', None) == 'INPUT':
                    if count == index:
                        identifier = getattr(item, 'identifier', None)
                        if identifier and identifier in modifier.keys():
                            return identifier
                        break
                    count += 1
    inputs = getattr(node_group, 'inputs', None)
    if inputs and 0 <= index < len(inputs):
        socket = inputs[index]
        identifier = getattr(socket, 'identifier', None)
        if identifier and identifier in modifier.keys():
            return identifier
    candidate = f'Input_{index}'
    if candidate in modifier.keys():
        return candidate
    return None


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


def _iter_group_inputs(node_group: bpy.types.NodeTree):
    inputs = getattr(node_group, 'inputs', None)
    if inputs is not None:
        for idx, socket in enumerate(inputs):
            yield idx, _normalize_socket_type(getattr(socket, 'type', None)), getattr(socket, 'name', '')
        return
    interface = getattr(node_group, 'interface', None)
    if interface is None:
        return
    interface_inputs = getattr(interface, 'inputs', None)
    if interface_inputs is not None:
        for idx, socket in enumerate(interface_inputs):
            yield idx, _normalize_socket_type(getattr(socket, 'socket_type', None)), getattr(socket, 'name', '')
        return
    items_tree = getattr(interface, 'items_tree', None)
    if items_tree is None:
        return
    index = 0
    for item in items_tree:
        if getattr(item, 'item_type', None) == 'SOCKET' and getattr(item, 'in_out', None) == 'INPUT':
            yield index, _normalize_socket_type(getattr(item, 'socket_type', None)), getattr(item, 'name', '')
            index += 1


def _find_route_material_input(node_group: bpy.types.NodeTree) -> int | None:
    index_by_type = None
    for idx, socket_type, name in _iter_group_inputs(node_group):
        if socket_type == 'MATERIAL':
            if name and 'route' in name.casefold():
                return idx
            if index_by_type is None:
                index_by_type = idx
    return index_by_type


def _find_route_curve(context: bpy.types.Context) -> bpy.types.Object | None:
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
    scene = getattr(context, 'scene', None)
    if scene:
        for obj in scene.objects:
            if obj.type == 'CURVE':
                return obj
    for candidate in route_resolve.ROUTE_NAME_CANDIDATES:
        existing = bpy.data.objects.get(candidate)
        if existing and existing.type == 'CURVE':
            return existing
    for obj in bpy.data.objects:
        if obj.type == 'CURVE' and 'route' in obj.name.casefold():
            return obj
    return None


def _discover_route_node_group() -> tuple[Optional[str], Optional[bpy.types.NodeTree]]:
    """Find or append the route Geometry Nodes group from ASSET_ROUTE.blend.

    This prefers the route asset summary but will fall back to scanning the
    ASSET_ROUTE.blend node_groups if needed. Returns (name, node_group) or
    (None, None) if absolutely nothing usable can be found.
    """
    summary = route_assets.get_last_summary()
    name = summary.get('route_ng') if summary else None

    # 1) Prefer the explicit route_ng name from the asset summary
    if name:
        try:
            route_resolve.ensure_appended(
                route_assets.ROUTE_BLEND_PATH,
                'node_groups',
                (name,),
            )
        except Exception as exc:
            print(f"[BLOSM] WARN route node group append failed for {name}: {exc}")
        group = bpy.data.node_groups.get(name)
        if group is not None:
            return name, group

    # 2) Fallback: scan ASSET_ROUTE.blend for any node group that looks like a route GN
    try:
        candidates = route_resolve.list_blend_datablocks(
            route_assets.ROUTE_BLEND_PATH,
            'node_groups',
        )
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[BLOSM] WARN route node group listing failed: {exc}")
        candidates = []

    if candidates:
        preferred = None
        # Prefer a candidate containing 'route' (case-insensitive)
        for candidate in candidates:
            if 'route' in candidate.casefold():
                preferred = candidate
                break
        if not preferred:
            preferred = candidates[0]
        try:
            route_resolve.ensure_appended(
                route_assets.ROUTE_BLEND_PATH,
                'node_groups',
                (preferred,),
            )
        except Exception as exc:
            print(f"[BLOSM] WARN route node group append failed for {preferred}: {exc}")
        group = bpy.data.node_groups.get(preferred)
        if group is not None:
            return preferred, group

    return None, None


def _discover_route_material() -> tuple[Optional[str], Optional[bpy.types.Material]]:
    """Resolve the route material, appending it from ASSET_ROUTE.blend if needed.

    This prefers the last asset import summary but will fall back to the
    route resolver helper, which ensures the material datablock is appended.
    """
    summary = route_assets.get_last_summary()
    preferred_name = summary.get('route_mat') if summary else None

    # 1) Prefer the explicit name from the last asset import if present
    if preferred_name:
        material = bpy.data.materials.get(preferred_name)
        if material is not None:
            return preferred_name, material

    # 2) Use the resolver helper, which will append from ASSET_ROUTE.blend
    #    and choose a material containing 'route' when possible.
    try:
        material = route_resolve.resolve_material(
            (preferred_name,) if preferred_name else None
        )
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[BLOSM] WARN route material resolve failed: {exc}")
        material = None

    if material is not None:
        return material.name, material

    # 3) Final fallback: choose from any existing materials containing 'route'
    name = route_resolve.choose('materials', 'route')
    return name, bpy.data.materials.get(name) if name else None


def ensure_route_nodes(context: bpy.types.Context):
    route_obj = _find_route_curve(context)
    if not route_obj:
        raise RuntimeError('Route curve not found')

    node_group_name, node_group = _discover_route_node_group()
    if not node_group:
        raise RuntimeError(
            f"Route node group not available (summary route_ng={node_group_name!r})"
        )

    modifier = route_obj.modifiers.get(ROUTE_MODIFIER_NAME)
    if not modifier or modifier.type != 'NODES':
        modifier = route_obj.modifiers.new(ROUTE_MODIFIER_NAME, 'NODES')
    modifier.node_group = node_group
    if modifier.node_group is None:
        raise RuntimeError(
            f"Route Geometry Nodes modifier '{ROUTE_MODIFIER_NAME}' was created but no node_group could be assigned"
        )

    material_name, material = _discover_route_material()
    material_index = _find_route_material_input(node_group)
    prop_name = _resolve_modifier_input(modifier, material_index) if material_index is not None else None
    material_set = False
    if material:
        if prop_name:
            modifier[prop_name] = material
            material_set = True
        elif prop_name is None:
            print('[BLOSM] WARN route material input not found')

        # Ensure the route curve itself always has the RouteLine material
        # in its material slot for viewport/render consistency.
        curve_data = getattr(route_obj, 'data', None)
        materials = getattr(curve_data, 'materials', None) if curve_data else None
        if materials is not None:
            try:
                if len(materials):
                    materials[0] = material
                else:
                    materials.append(material)
            except Exception:
                pass
        try:
            route_obj.active_material = material
        except Exception:
            pass

    return {
        'route_obj': route_obj,
        'node_group': node_group_name,
        'node_group_assigned': bool(modifier.node_group),
        'material': material_name,
        'material_set': material_set,
    }


class BLOSM_OT_attach_route_nodes(Operator):
    bl_idname = "blosm.attach_route_nodes"
    bl_label = "Attach Route Nodes"
    bl_description = "Attach the Route Geometry Nodes and material to the active route curve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            summary = ensure_route_nodes(context)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}

        route_obj = summary['route_obj']
        applied = bool(summary.get('material_set'))
        print(
            f"[BLOSM] route_nodes_attached: object={route_obj.name}, modifier={ROUTE_MODIFIER_NAME}, "
            f"group={summary.get('node_group')}, material={summary.get('material')}, applied={applied}"
        )
        return {'FINISHED'}


class BLOSM_OT_route_nodes_check(Operator):
    bl_idname = "blosm.route_nodes_check"
    bl_label = "Route Nodes Self-Check"
    bl_description = "Report status of the Route Geometry Nodes setup"
    bl_options = {'REGISTER'}

    def execute(self, context):
        route_obj = _find_route_curve(context)
        modifier = route_obj.modifiers.get(ROUTE_MODIFIER_NAME) if route_obj else None
        modifier_exists = bool(modifier and modifier.type == 'NODES')
        group_ok = bool(modifier_exists and modifier.node_group)
        material_ok = False
        material_name = None
        if modifier_exists and modifier.node_group:
            idx = _find_route_material_input(modifier.node_group)
            prop_name = _resolve_modifier_input(modifier, idx) if idx is not None else None
            if prop_name and prop_name in modifier.keys():
                value = modifier[prop_name]
                if isinstance(value, bpy.types.Material):
                    material_ok = True
                    material_name = value.name
        print(
            f"[BLOSM] route_nodes_check: route_exists={bool(route_obj)}, modifier_exists={modifier_exists}, "
            f"group_ok={group_ok}, material_ok={material_ok}, mat='{material_name}'"
        )
        return {'FINISHED'}


__all__ = (
    'ROUTE_MODIFIER_NAME',
    'ensure_route_nodes',
)


def register():
    bpy.utils.register_class(BLOSM_OT_attach_route_nodes)
    bpy.utils.register_class(BLOSM_OT_route_nodes_check)


def unregister():
    # Unregister defensively: Blender may already have unregistered some
    # classes when disabling addons or reloading scripts.
    for cls in (BLOSM_OT_route_nodes_check, BLOSM_OT_attach_route_nodes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            # Class not registered or already unregistered
            continue
        except Exception:
            # Do not let shutdown fail because of unregister issues
            continue
