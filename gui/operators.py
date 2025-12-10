"""
BLOSM Route Import - GUI Operators - FIXED

Extended with asset manager helpers for appending assets and capturing new ones.
UPDATED to use the new Dict-based asset isolation interface.
"""

import shutil
from pathlib import Path

import bpy






class BLOSM_OT_AddWaypoint(bpy.types.Operator):
    """Add a waypoint stop to the route"""

    bl_idname = "blosm.add_waypoint"
    bl_label = "Add Waypoint"
    bl_description = "Add an intermediate stop between start and end"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.blosm.route_waypoints.add()
        return {'FINISHED'}


class BLOSM_OT_RemoveWaypoint(bpy.types.Operator):
    """Remove a waypoint stop from the route"""

    bl_idname = "blosm.remove_waypoint"
    bl_label = "Remove Waypoint"
    bl_description = "Remove this waypoint stop"
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        waypoints = context.scene.blosm.route_waypoints
        if 0 <= self.index < len(waypoints):
            waypoints.remove(self.index)
        return {'FINISHED'}


class BLOSM_OT_LevelsAdd(bpy.types.Operator):
    """Add an entry for default building levels"""

    bl_idname = "blosm.levels_add"
    bl_label = "+"
    bl_description = "Add an entry for the default number of levels. " +\
        "Enter both the number of levels and its relative weight between 1 and 100"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        context.scene.blosm.defaultLevels.add()
        return {'FINISHED'}


class BLOSM_OT_LevelsDelete(bpy.types.Operator):
    """Delete an entry from default building levels"""

    bl_idname = "blosm.levels_delete"
    bl_label = "-"
    bl_description = "Delete the selected entry for the default number of levels"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.blosm.defaultLevels) > 1

    def invoke(self, context, event):
        addon = context.scene.blosm
        defaultLevels = addon.defaultLevels
        defaultLevels.remove(addon.defaultLevelsIndex)
        if addon.defaultLevelsIndex >= len(defaultLevels):
            addon.defaultLevelsIndex = 0
        return {'FINISHED'}


class BLOSM_OT_AssetsUpdateNotice(bpy.types.Operator):
    """Show a confirmation/notice about updated asset .blend files."""

    bl_idname = "blosm.assets_update_notice"
    bl_label = "Confirm Updated Assets"
    bl_description = "Confirm that updated asset .blend files have been copied into the addon assets folder"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Updated Assets Confirmation", icon='INFO')
        layout.separator()
        layout.label(text="Before running Fetch Route & Map, confirm that:", icon='BLANK1')
        layout.label(text="- The latest asset .blend files are present in:", icon='BLANK1')
        layout.label(text="  cash-cab-addon/assets", icon='FILE_FOLDER')
        layout.separator()
        layout.label(text="If assets are missing, water/ground/islands/world may be incomplete.", icon='ERROR')

    def execute(self, context):
        self.report({'INFO'}, "Updated assets confirmation acknowledged")
        return {'FINISHED'}


