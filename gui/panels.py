"""
CashCab Route Import - GUI Panels
Minimal panel definitions for route import functionality only.
"""

import bpy




ROUTE_PANEL_UI_VERSION = "2.2.0"
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

        # Address inputs
        col = layout.column(align=True)
        col.prop(addon, "route_start_address", text="Start Address")

        # Waypoints section
        waypoints_box = layout.box()
        waypoints_box.label(text="Waypoints (Optional)", icon='CURVE_PATH')
        for idx, waypoint in enumerate(addon.route_waypoints):
            row = waypoints_box.row(align=True)
            row.prop(waypoint, "address", text=f"{idx+1}")
            row.operator("blosm.remove_waypoint", text="", icon='X').index = idx
        waypoints_box.operator("blosm.add_waypoint", text="Add Stop", icon='ADD')

        col = layout.column(align=True)
        col.prop(addon, "route_end_address", text="End Address")
        layout.prop(addon, "route_padding_m")

        # Import layer toggles
        layout.label(text="Auto-importing: Roads, Buildings, Water, RouteCam", icon='IMPORT')
        layout.prop(addon, "route_create_preview_animation", text="Create Animated Route & Assets")

        # Animation settings - grouped in a collapsible tab-like box
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

        # City extension controls in a collapsible section (similar to Animation Controls)
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

        # Disable controls until a prior import stored bbox/tiles
        scene = context.scene
        bbox = scene.get("blosm_import_bbox") if scene else None
        tiles = scene.get("blosm_import_tiles") if scene else None
        # Relax type check for IDPropertyArray support
        has_import_state = bbox is not None and len(bbox) == 4 and bool(tiles)
        if addon.ui_show_extend_city:
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

        # Extra Features (collapsible, after Extend City)
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
            body.separator()
            body.prop(addon, "route_trim_end_uturns", text="Trim Start/End U-Turns")
            if addon.route_trim_end_uturns:
                body.prop(addon, "route_trim_window_fraction", text="Trim Window")
                body.prop(addon, "route_trim_max_uturn_fraction", text="Max U-Turn Size")
                body.prop(addon, "route_trim_corner_angle_min", text="Corner Angle Min")
                body.prop(addon, "route_trim_direction_reverse_deg", text="Direction Reverse")
            body.operator("blosm.apply_uturn_trim", text="Reapply Trim/Restore", icon='FILE_REFRESH')

            body.separator()
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

        # Pre-flight confirmations (assets + render settings)
        preflight_box = layout.box()
        preflight_box.label(text="Pre-flight Checks", icon='INFO')
        preflight_box.operator(
            "blosm.assets_update_notice",
            text="Confirm Updated Assets",
            icon='FILE_FOLDER',
        )
        preflight_box.operator(
            "blosm.apply_render_settings",
            text="Apply Render Settings",
            icon='RENDER_STILL',
        )
        preflight_box.operator(
            "blosm.set_viewport_clip",
            text="Set Clip Start/End",
            icon='RESTRICT_VIEW_OFF',
        )


        # RouteCam Controls (hidden by default – handled by separate addon)
        if False and addon.route_enable_routecam:
            # Determine target camera: Active Object > Scene Camera
            target_cam = None
            if context.active_object and context.active_object.type == 'CAMERA':
                target_cam = context.active_object
            elif context.scene.camera:
                target_cam = context.scene.camera

            rc_box = anim_box.box()
            rc_box.label(text="RouteCam Director", icon='CAMERA_DATA')
            
            # Batch Settings (Always Visible)
            row = rc_box.row()
            row.prop(addon, "routecam_batch_v2_count")
            row.prop(addon, "routecam_batch_viz_count")

            if target_cam:
                rc_box.label(text=f"Camera: {target_cam.name}", icon='OUTLINER_OB_CAMERA')
                
                # Ensure property group exists
                if hasattr(target_cam, 'routecam_unified'):
                    s = target_cam.routecam_unified
                    
                    # Engine Select
                    row = rc_box.row()
                    row.prop(s, "engine_mode", expand=True)
                    
                    rc_box.prop(s, "target_curve")
                    rc_box.prop(s, "duration")

                    # Dynamic UI
                    if s.engine_mode == 'V2':
                        v2_col = rc_box.column(align=True)
                        v2_col.prop(s, "margin")
                        v2_col.prop(s, "zoom_ratio")
                        
                        row = v2_col.row(align=True)
                        row.prop(s, "pitch_start")
                        row.prop(s, "pitch_end")
                        
                        v2_col.prop(s, "yaw_offset")
                        
                        row = v2_col.row(align=True)
                        row.prop(s, "beat_drift")
                        row.prop(s, "beat_zoom")
                        
                        op_row = rc_box.row(align=True)
                        op_row.operator("routecam.generate", text="Analyze", icon='FILE_REFRESH')
                        if s.v2_cached_plan:
                            op_row.operator("routecam.bake_v2", text="Bake", icon='ACTION')
                            
                    elif s.engine_mode == 'VIZ':
                        viz_col = rc_box.column(align=True)
                        viz_col.prop(s, "sect1_margin")
                        viz_col.prop(s, "sect1_angle")
                        viz_col.prop(s, "sect2_time")
                        viz_col.prop(s, "sect2_push")
                        
                        rc_box.operator("routecam.generate", text="Generate (Direct Bake)", icon='FILE_REFRESH')
                else:
                    rc_box.label(text="RouteCam properties missing", icon='ERROR')
            else:
                rc_box.label(text="No Camera Selected", icon='INFO')
                rc_box.operator("object.camera_add", text="Create Camera", icon='ADD')

        # Main action buttons
        layout.separator()
        layout.operator("blosm.fetch_route_map", text="Fetch Route & Map", icon='IMPORT')
        layout.operator("blosm.clean_and_clear", text="Clean & Clear", icon='TRASH')
