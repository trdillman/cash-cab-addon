from __future__ import annotations

import bpy

from .properties import BulkRouteItem, BulkSettings
from .ops import (
    BLOSM_OT_BulkFetchManifest,
    BLOSM_OT_BulkSelectAll,
    BLOSM_OT_BulkDeselectAll,
    BLOSM_OT_BulkToggleGroup,
    BLOSM_OT_BulkRunSelected,
)
from .panels import BLOSM_UL_BulkRoutes, BLOSM_PT_BulkImport

_classes = (
    BulkRouteItem,
    BulkSettings,
    BLOSM_OT_BulkFetchManifest,
    BLOSM_OT_BulkSelectAll,
    BLOSM_OT_BulkDeselectAll,
    BLOSM_OT_BulkToggleGroup,
    BLOSM_OT_BulkRunSelected,
    BLOSM_UL_BulkRoutes,
    BLOSM_PT_BulkImport,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cashcab_bulk = bpy.props.PointerProperty(type=BulkSettings)


def unregister():
    if hasattr(bpy.types.Scene, "cashcab_bulk"):
        try:
            del bpy.types.Scene.cashcab_bulk
        except Exception:
            pass
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            continue
