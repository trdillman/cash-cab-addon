"""Diagnostics stubs for BLOSM route add-on."""

from __future__ import annotations

import bpy


class BLOSM_OT_route_diagnostics(bpy.types.Operator):
    bl_idname = "blosm.route_diagnostics"
    bl_label = "Run Route Diagnostics"
    bl_description = "Run BLOSM route diagnostics"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("[BLOSM] diagnostics_stub: not yet implemented")
        return {'FINISHED'}


_CLASSES = (
    BLOSM_OT_route_diagnostics,
)


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
