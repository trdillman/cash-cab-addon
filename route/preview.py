"""Route preview asset append utilities for BLOSM."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import bpy

ASSET_ROUTE_BLEND = Path(__file__).resolve().parent.parent / "assets" / "ASSET_ROUTE.blend"
ASSET_CAR_BLEND = Path(__file__).resolve().parent.parent / "assets" / "ASSET_CAR.blend"
NODE_GROUP_NAME = "ASSET_RouteTrace"
MATERIAL_NAME = "RouteLine"
CAR_OBJECT_NAME = "ASSET_CAR"
PREVIEW_COLLECTION_NAME = "BLOSM_Preview"
ROUTE_OBJECT_NAME = "ROUTE"


class RoutePreviewError(RuntimeError):
    """Raised when preview assets fail to append."""


def _log(message: str) -> None:
    print(f"[BLOSM] {message}")


def _ensure_asset(filepath: Path, description: str) -> Path:
    if not filepath.exists():
        raise RoutePreviewError(f"missing asset file '{filepath}' for {description}")
    return filepath


def _append_node_group(path: Path, name: str) -> Tuple[bpy.types.NodeTree, bool]:
    node_group = bpy.data.node_groups.get(name)
    if node_group:
        return node_group, True
    path = _ensure_asset(path, f"node group '{name}'")
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        if name not in data_from.node_groups:
            raise RoutePreviewError(f"missing datablock '{name}' in {path.name}")
        data_to.node_groups = [name]
    node_group = bpy.data.node_groups.get(name)
    if not node_group:
        raise RoutePreviewError(f"failed to append node group '{name}'")
    return node_group, False


def _append_material(path: Path, name: str) -> Tuple[bpy.types.Material, bool]:
    material = bpy.data.materials.get(name)
    if material:
        return material, True
    path = _ensure_asset(path, f"material '{name}'")
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        if name not in data_from.materials:
            raise RoutePreviewError(f"missing datablock '{name}' in {path.name}")
        data_to.materials = [name]
    material = bpy.data.materials.get(name)
    if not material:
        raise RoutePreviewError(f"failed to append material '{name}'")
    return material, False


def _append_object(path: Path, name: str) -> Tuple[bpy.types.Object, bool]:
    obj = bpy.data.objects.get(name)
    if obj:
        return obj, True
    path = _ensure_asset(path, f"object '{name}'")
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        if name not in data_from.objects:
            raise RoutePreviewError(f"missing datablock '{name}' in {path.name}")
        data_to.objects = [name]
    obj = bpy.data.objects.get(name)
    if not obj:
        raise RoutePreviewError(f"failed to append object '{name}'")
    return obj, False


def _ensure_preview_collection(context: bpy.types.Context) -> bpy.types.Collection:
    collection = bpy.data.collections.get(PREVIEW_COLLECTION_NAME)
    if not collection:
        collection = bpy.data.collections.new(PREVIEW_COLLECTION_NAME)
        context.scene.collection.children.link(collection)
    elif collection.name not in context.scene.collection.children:
        context.scene.collection.children.link(collection)
    collection.hide_viewport = False
    collection.hide_render = False
    _ensure_view_layer_visibility(context.view_layer.layer_collection, collection)
    return collection


def _ensure_view_layer_visibility(layer_collection: bpy.types.LayerCollection, target: bpy.types.Collection) -> None:
    if layer_collection.collection == target:
        layer_collection.exclude = False
        layer_collection.hide_viewport = False
        layer_collection.hide_render = False
        return
    for child in layer_collection.children:
        _ensure_view_layer_visibility(child, target)


def _select_car(context: bpy.types.Context, car_obj: bpy.types.Object) -> None:
    for obj in context.selected_objects:
        obj.select_set(False)
    car_obj.select_set(True)
    context.view_layer.objects.active = car_obj


class BLOSM_OT_append_preview_assets(bpy.types.Operator):
    bl_idname = "blosm.append_preview_assets"
    bl_label = "Append Preview Assets"
    bl_description = "Append preview Geometry Nodes, material, and car assets into the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        appended: Dict[str, bool] = {}
        reused: Dict[str, bool] = {}
        try:
            node_group, reused_node = _append_node_group(ASSET_ROUTE_BLEND, NODE_GROUP_NAME)
            appended['node_group'] = not reused_node
            reused['node_group'] = reused_node
            material, reused_mat = _append_material(ASSET_ROUTE_BLEND, MATERIAL_NAME)
            appended['material'] = not reused_mat
            reused['material'] = reused_mat
            car_obj, reused_obj = _append_object(ASSET_CAR_BLEND, CAR_OBJECT_NAME)
            appended['car_object'] = not reused_obj
            reused['car_object'] = reused_obj
        except RoutePreviewError as exc:
            _log(f"ERROR: {exc}")
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}

        car_obj.location = (0.0, 0.0, 1.5)
        car_obj.rotation_euler = (0.0, 0.0, 0.0)
        car_obj.scale = (20.0, 20.0, 20.0)
        car_obj.hide_viewport = False
        car_obj.hide_render = False
        car_obj.hide_set = False

        preview_collection = _ensure_preview_collection(context)
        if car_obj.name not in preview_collection.objects:
            preview_collection.objects.link(car_obj)
        car_obj.hide_set = False

        _select_car(context, car_obj)
        _log(f"appended={appended} reused={reused}")
        return {'FINISHED'}


class BLOSM_PT_RoutePreviewPanel(bpy.types.Panel):
    bl_label = "Route Preview"
    bl_parent_id = "BLOSM_PT_RouteImportAdvanced"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CashCab"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return bool(obj and obj.type == 'CURVE' and obj.name == ROUTE_OBJECT_NAME)

    def draw(self, context):
        layout = self.layout
        layout.operator(BLOSM_OT_append_preview_assets.bl_idname, icon='ASSET_MANAGER')


_CLASSES = (
    BLOSM_OT_append_preview_assets,
    BLOSM_PT_RoutePreviewPanel,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
