"""
CashCab Route Import - GUI Panels
Minimal panel definitions for route import functionality only.
"""

import bpy


ROUTE_PANEL_UI_VERSION = "3.0.1"
ROUTE_PANEL_LABEL = f"CashCab ({ROUTE_PANEL_UI_VERSION})"


class BLOSM_UL_DefaultLevels(bpy.types.UIList):
    """UI list for default building levels"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_property):
        row = layout.row()
        row.prop(item, "levels")
        row.prop(item, "weight")


class BLOSM_PT_RouteImport(bpy.types.Panel):
    """Main route import panel with address inputs and fetch button"""

    bl_label = ROUTE_PANEL_LABEL
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CashCab"

    def draw(self, context):
        layout = self.layout
        addon = context.scene.blosm

        # 1. Route Configuration Box
        # We use a single box for both addresses as requested
        route_box = layout.box()
        
        # Add Auto-Snap toggle to header row (if possible) or just inside
        row = route_box.row()
        row.label(text="Route Configuration", icon='SETTINGS')
        row.prop(addon, "auto_snap_addresses", text="Auto Snap", icon='SNAP_ON')
        route_box.separator()

        # START ADDRESS SECTION
        try:
            # Create a specific column for the start address to ensure alignment isolation
            col_start = route_box.column(align=True)
            col_start.label(text="Start Address", icon='HOME')
            
            row_start = col_start.row(align=True)
            row_start.prop(addon, "route_start_address", text="")
            
            # Operator with explicit error handling
            try:
                op_start = row_start.operator("blosm.snap_address", text="", icon='SNAP_ON')
                op_start.type = 'START'
            except Exception as e:
                print(f"Blosm UI Warning: Failed to set op_start.type: {e}")
                # Don't crash the UI for the button
                pass

            # Show snapped coords if available
            snapped_start = getattr(addon, "start_snapped_coords", "")
            if snapped_start:
                col_start.label(text=f"{snapped_start}", icon='CHECKMARK')
        except Exception as e:
            route_box.label(text=f"UI Error (Start): {e}", icon='ERROR')
            print(f"Blosm UI Error (Start): {e}")

        # Spacer between sections
        route_box.separator()

        # END ADDRESS SECTION
        try:
            # Create a NEW column for the end address
            col_end = route_box.column(align=True)
            col_end.label(text="End Address", icon='HOME')
            
            row_end = col_end.row(align=True)
            row_end.prop(addon, "route_end_address", text="")
            
            try:
                op_end = row_end.operator("blosm.snap_address", text="", icon='SNAP_ON')
                op_end.type = 'END'
            except Exception as e:
                print(f"Blosm UI Warning: Failed to set op_end.type: {e}")
                pass
                
            snapped_end = getattr(addon, "end_snapped_coords", "")
            if snapped_end:
                col_end.label(text=f"{snapped_end}", icon='CHECKMARK')
        except Exception as e:
            route_box.label(text=f"UI Error (End): {e}", icon='ERROR')
            print(f"Blosm UI Error (End): {e}")

        # Padding at bottom of box
        try:
            route_box.separator()
            route_box.prop(addon, "route_padding_m")
        except Exception as e:
            route_box.label(text=f"UI Error (Padding): {e}", icon='ERROR')


        # 2. Main Toggles & Imports
        layout.separator()
        layout.prop(addon, "route_create_preview_animation", text="Create Animated Route & Assets")
        layout.prop(addon, "route_generate_camera", text="Auto-generate Camera")


        # 3. Animation Controls (Collapsible)
        anim_box = layout.box()
        header = anim_box.row()
        header.prop(
            addon,
            "ui_show_animation",
            text="",
            icon='TRIA_DOWN' if addon.ui_show_animation else 'TRIA_RIGHT',
            emboss=False,
        )
        header.label(text="Animation Controls", icon='TIME')

        if addon.ui_show_animation:
            # Car animation
            car_col = anim_box.column(align=True)
            car_col.label(text="Car Animation:", icon='AUTO')
            car_col.prop(context.scene, "blosm_anim_start", text="Start Frame")
            car_col.prop(context.scene, "blosm_anim_end", text="End Frame")
            car_col.prop(context.scene, "blosm_lead_frames", text="Lead Frames")

            trail_col = anim_box.column(align=True)
            trail_col.label(text="Car Trail Custom Window", icon='CURVE_PATH')
            trail_col.prop(context.scene, "blosm_car_trail_start_adjust", text="Start Adjust")
            trail_col.prop(context.scene, "blosm_car_trail_end_adjust", text="End Adjust")
            trail_col.prop(context.scene, "blosm_car_trail_tail_shift", text="Tail Shift")


        # 3.5 Camera Controls (Collapsible)
        camera_box = layout.box()
        header = camera_box.row()
        header.prop(
            addon,
            "ui_show_route_camera",
            text="",
            icon='TRIA_DOWN' if addon.ui_show_route_camera else 'TRIA_RIGHT',
            emboss=False,
        )
        header.label(text="Route Camera", icon='CAMERA_DATA')
        
        if addon.ui_show_route_camera:
            row = camera_box.row(align=True)
            row.operator("routerig.spawn_test_camera", text="Spawn Camera", icon='CAMERA_DATA')
            row.operator("routerig.generate_camera_animation", text="Animate Camera", icon='ANIM')


        # 4. Extend City (Collapsible)
        extend_box = layout.box()
        header = extend_box.row()
        header.prop(
            addon,
            "ui_show_extend_city",
            text="",
            icon='TRIA_DOWN' if addon.ui_show_extend_city else 'TRIA_RIGHT',
            emboss=False,
        )
        header.label(text="Extend City", icon='ARROW_LEFTRIGHT')

        if addon.ui_show_extend_city:
            # Check state
            scene = context.scene
            bbox = scene.get("blosm_import_bbox") if scene else None
            tiles = scene.get("blosm_import_tiles") if scene else None
            has_import_state = bbox is not None and len(bbox) == 4 and bool(tiles)

            body = extend_box.column(align=True)
            body.label(text="Tiles are ~1.4 km; raise distance if no tiles change.", icon='INFO')

            row = body.row()
            row.enabled = has_import_state
            row.prop(addon, "route_extend_m", text="Extend by (m)")

            row = body.row()
            row.enabled = has_import_state
            row.operator("blosm.extend_city_area", text="Extend City (delta tiles only)", icon='ADD')

            if not has_import_state:
                body.label(text="Run Fetch Route and Map first to enable extend.", icon='INFO')


        # 5. Extra Features (Collapsible)
        extra_box = layout.box()
        header = extra_box.row()
        header.prop(
            addon,
            "ui_show_extra_features",
            text="",
            icon='TRIA_DOWN' if addon.ui_show_extra_features else 'TRIA_RIGHT',
            emboss=False,
        )
        header.label(text="Extra Features", icon='TOOL_SETTINGS')

        if addon.ui_show_extra_features:
            body = extra_box.column(align=True)
            body.prop(addon, "route_snap_to_road_centerline", text="Snap to road centerlines")
            
            labels_box = body.box()
            labels_box.label(text="Street Labels", icon='FONT_DATA')
            labels_box.prop(addon, "ui_show_street_labels", text="Show Street Labels")
            row = labels_box.row(align=True)
            row.operator("blosm.generate_street_labels", text="Generate Street Labels", icon='OUTLINER_OB_FONT')
            row.operator("blosm.clear_street_labels", text="Clear Street Labels", icon='TRASH')

            body.separator()
            adjuster_box = body.box()
            adjuster_box.label(text="Route Adjuster", icon='EMPTY_AXIS')
            adjuster_box.prop(addon, "route_adjuster_enabled", text="Enable Route Adjuster")

            controls = adjuster_box.column(align=True)
            controls.enabled = bool(addon.route_adjuster_enabled)
            controls.prop(addon, "route_adjuster_live_update", text="Live update (debounced)")
            controls.prop(addon, "route_adjuster_snap_points", text="Snap control points to roads")
            if bool(getattr(addon, "route_adjuster_snap_points", False)):
                controls.prop(addon, "route_adjuster_allow_any_highway_fallback", text="Allow any-highway fallback")
            controls.prop(addon, "route_adjuster_debounce_ms", text="Debounce (ms)")

            row = controls.row(align=True)
            row.operator("blosm.route_adjuster_create_controls", text="Create/Sync Controls", icon='EMPTY_AXIS')
            row.operator("blosm.route_adjuster_recompute", text="Recompute Route Now", icon='FILE_REFRESH')

            row = controls.row(align=True)
            row.operator("blosm.route_adjuster_add_via", text="Add Via", icon='ADD')
            row.operator("blosm.route_adjuster_clear_vias", text="Clear Vias", icon='TRASH')

            if getattr(addon, "route_adjuster_last_error", ""):
                controls.label(text=f"Last error: {addon.route_adjuster_last_error}", icon='ERROR')

            body.separator()
            # Trim U-Turns (Moved to bottom)
            body.prop(addon, "route_trim_end_uturns", text="Trim Start/End U-Turns")
            
            if addon.route_trim_end_uturns:
                body.prop(addon, "route_trim_window_fraction", text="Trim Window")
                body.prop(addon, "route_trim_max_uturn_fraction", text="Max U-Turn Size")
                body.prop(addon, "route_trim_corner_angle_min", text="Corner Angle Min")
                body.prop(addon, "route_trim_direction_reverse_deg", text="Direction Reverse")
            body.operator("blosm.apply_uturn_trim", text="Reapply Trim/Restore", icon='FILE_REFRESH')

        # 6. Pre-flight Checks
        preflight_box = layout.box()
        preflight_box.label(text="Pre-flight Checks", icon='INFO')

        # Removed Apply Render Settings button (now automatic)
        preflight_box.operator("blosm.bake_all_geonodes", text="Bake All Geonodes", icon='MODIFIER')
        preflight_box.operator("blosm.set_viewport_clip", text="Set Clip Start/End", icon='RESTRICT_VIEW_OFF')

        # 7. Main Action Buttons
        layout.separator()
        layout.operator("blosm.fetch_route_map", text="Fetch Route & Map", icon='IMPORT')
        layout.operator("blosm.clean_and_clear", text="Clean & Clear", icon='TRASH')
