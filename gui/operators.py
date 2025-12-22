"""
BLOSM Route Import - GUI Operators - FIXED

Extended with asset manager helpers for appending assets and capturing new ones.
UPDATED to use the new Dict-based asset isolation interface.
"""

import shutil
from pathlib import Path
import time

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


class BLOSM_OT_SetViewportClip(bpy.types.Operator):
    """Set viewport clip start and end for all 3D viewports"""

    bl_idname = "blosm.set_viewport_clip"
    bl_label = "Set Viewport Clip"
    bl_description = "Set clip start/end ranges for all 3D viewports to improve far-distance visibility"
    bl_options = {'REGISTER', 'UNDO'}

    clip_start: bpy.props.FloatProperty(
        name="Clip Start",
        description="Viewport clip start distance",
        default=1.0,
        min=0.001,
        soft_max=1000.0
    )

    clip_end: bpy.props.FloatProperty(
        name="Clip End",
        description="Viewport clip end distance",
        default=1000000.0,
        min=1.0,
        soft_max=1000000.0
    )

    def execute(self, context):
        update_count = 0

        # Iterate through all screens and areas to find VIEW_3D spaces
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.clip_start = self.clip_start
                            space.clip_end = self.clip_end
                            update_count += 1

        # Fallback: if no VIEW_3D spaces were updated globally, try the current context
        if update_count == 0:
            if context.area and context.area.type == 'VIEW_3D':
                if context.space_data and context.space_data.type == 'VIEW_3D':
                    context.space_data.clip_start = self.clip_start
                    context.space_data.clip_end = self.clip_end
                    update_count = 1
                    self.report({'INFO'}, f"Updated current viewport: clip_start={self.clip_start}, clip_end={self.clip_end}")
                    return {'FINISHED'}

            # No viewports found at all
            self.report({'WARNING'}, "No 3D viewports found to update")
            return {'CANCELLED'}

        # Success: updated viewports globally
        self.report({'INFO'}, f"Updated {update_count} viewport(s): clip_start={self.clip_start}, clip_end={self.clip_end}")
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


class BLOSM_OT_GenerateStreetLabels(bpy.types.Operator):
    """Generate STREET_LABELS text objects for visible road names (idempotent)."""

    bl_idname = "blosm.generate_street_labels"
    bl_label = "Generate Street Labels"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = getattr(context, "scene", None)
        if scene is None:
            self.report({'ERROR'}, "No active scene")
            return {'CANCELLED'}

        try:
            from ..road import street_labels

            created = int(street_labels.generate_street_labels(scene))
            self.report({'INFO'}, f"Street labels generated: {created}")
            return {'FINISHED'}
        except Exception as exc:
            print(f"[BLOSM] WARN street labels: generate failed: {exc}")
            self.report({'WARNING'}, f"Street labels generate failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_ClearStreetLabels(bpy.types.Operator):
    """Clear STREET_LABELS text objects."""

    bl_idname = "blosm.clear_street_labels"
    bl_label = "Clear Street Labels"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = getattr(context, "scene", None)
        if scene is None:
            self.report({'ERROR'}, "No active scene")
            return {'CANCELLED'}

        try:
            from ..road import street_labels

            removed = int(street_labels.clear_street_labels(scene))
            self.report({'INFO'}, f"Street labels cleared: {removed}")
            return {'FINISHED'}
        except Exception as exc:
            print(f"[BLOSM] WARN street labels: clear failed: {exc}")
            self.report({'WARNING'}, f"Street labels clear failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_ApplyUTurnTrim(bpy.types.Operator):
    """Apply or restore start/end U-turn trimming on the ROUTE curve."""

    bl_idname = "blosm.apply_uturn_trim"
    bl_label = "Apply U-Turn Trim"
    bl_description = "Apply (or restore) trimming of small U-turn loops near the start/end of the route"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = getattr(context, "scene", None)
        addon = getattr(scene, "blosm", None) if scene else None
        enabled = bool(getattr(addon, "route_trim_end_uturns", False)) if addon else False
        try:
            from ..route.uturn_trim import apply_route_uturn_trim
        except Exception as exc:
            self.report({'ERROR'}, f"U-turn trim module import failed: {exc}")
            return {'CANCELLED'}

        ok = False
        try:
            ok = bool(apply_route_uturn_trim(context, enabled=enabled))
        except Exception as exc:
            self.report({'ERROR'}, f"U-turn trim failed: {exc}")
            return {'CANCELLED'}

        if not ok:
            self.report({'WARNING'}, "No ROUTE curve found (or route too short)")
            return {'CANCELLED'}

        self.report({'INFO'}, "U-turn trim applied" if enabled else "U-turn trim restored (raw route)")
        return {'FINISHED'}


def _recompute_route_camera_if_possible(context) -> bool:
    """Rebuild the Route Camera animation after route geometry changes."""
    try:
        # Mirror RouteRig deps: MARKER_START / MARKER_END / ROUTE(or Route) / CAR_LEAD
        start_obj = bpy.data.objects.get("MARKER_START")
        end_obj = bpy.data.objects.get("MARKER_END")
        route_obj = bpy.data.objects.get("ROUTE") or bpy.data.objects.get("Route")
        car_obj = bpy.data.objects.get("CAR_LEAD")
        if not (start_obj and end_obj and route_obj and car_obj):
            return False

        res = bpy.ops.routerig.generate_camera_animation()
        return "FINISHED" in (res or set())
    except Exception:
        return False


class BLOSM_OT_RouteAdjusterCreateControls(bpy.types.Operator):
    """Create or resync route control empties (start/end)."""

    bl_idname = "blosm.route_adjuster_create_controls"
    bl_label = "Create/Sync Route Controls"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon = getattr(getattr(context, "scene", None), "blosm", None)
        try:
            from ..route import route_adjuster

            ok = bool(route_adjuster.ensure_route_control_empties(context.scene))
            if not ok:
                self.report({'WARNING'}, "No ROUTE curve found")
                return {'CANCELLED'}
            if addon is not None:
                addon.route_adjuster_last_error = ""
            self.report({'INFO'}, "Route control empties ensured")
            return {'FINISHED'}
        except Exception as exc:
            if addon is not None:
                addon.route_adjuster_last_error = str(exc)
            self.report({'ERROR'}, f"Route controls failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_RouteAdjusterRecompute(bpy.types.Operator):
    """Recompute route from control empties."""

    bl_idname = "blosm.route_adjuster_recompute"
    bl_label = "Recompute Route Now"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon = getattr(getattr(context, "scene", None), "blosm", None)
        try:
            from ..route import route_adjuster

            ok = bool(route_adjuster.recompute_route_from_controls(context))
            if not ok:
                if addon is not None:
                    addon.route_adjuster_last_error = "Missing ROUTE or controls"
                self.report({'WARNING'}, "Route recompute skipped (missing ROUTE or controls)")
                return {'CANCELLED'}
            if addon is not None:
                addon.route_adjuster_last_error = ""
            if not _recompute_route_camera_if_possible(context):
                self.report(
                    {'WARNING'},
                    "Route recomputed, but Route Camera was not updated (missing MARKER_START/MARKER_END/ROUTE/CAR_LEAD)",
                )
            self.report({'INFO'}, "Route recomputed from controls")
            return {'FINISHED'}
        except Exception as exc:
            if addon is not None:
                addon.route_adjuster_last_error = str(exc)
            self.report({'ERROR'}, f"Route recompute failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_RouteAdjusterAddVia(bpy.types.Operator):
    """Add a via control empty."""

    bl_idname = "blosm.route_adjuster_add_via"
    bl_label = "Add Via Point"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon = getattr(getattr(context, "scene", None), "blosm", None)
        try:
            from ..route import route_adjuster

            obj = route_adjuster.create_via_control(context.scene)
            if obj is None:
                self.report({'WARNING'}, "No ROUTE curve found")
                return {'CANCELLED'}
            if addon is not None:
                addon.route_adjuster_last_error = ""
            self.report({'INFO'}, f"Added via control: {obj.name}")
            return {'FINISHED'}
        except Exception as exc:
            if addon is not None:
                addon.route_adjuster_last_error = str(exc)
            self.report({'ERROR'}, f"Add via failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_RouteAdjusterClearVias(bpy.types.Operator):
    """Clear all via control empties."""

    bl_idname = "blosm.route_adjuster_clear_vias"
    bl_label = "Clear Via Points"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon = getattr(getattr(context, "scene", None), "blosm", None)
        try:
            from ..route import route_adjuster

            removed = int(route_adjuster.clear_via_controls())
            if addon is not None:
                addon.route_adjuster_last_error = ""
            self.report({'INFO'}, f"Via controls cleared: {removed}")
            return {'FINISHED'}
        except Exception as exc:
            if addon is not None:
                addon.route_adjuster_last_error = str(exc)
            self.report({'ERROR'}, f"Clear vias failed: {exc}")
            return {'CANCELLED'}


class BLOSM_OT_RouteAdjusterLiveUpdateModal(bpy.types.Operator):
    """Debounced live recompute watcher for ROUTE_CTRL_* empties."""

    bl_idname = "blosm.route_adjuster_live_update_modal"
    bl_label = "Route Adjuster Live Update"
    bl_options = {'INTERNAL'}

    _is_running = False
    _timer = None
    _last_positions = None
    _last_change_t = 0.0
    _pending = False
    _suppress_until = 0.0

    def _collect_positions(self):
        from ..route import route_adjuster

        positions = {}
        for obj in route_adjuster.iter_all_controls():
            try:
                positions[obj.name] = obj.matrix_world.translation.copy()
            except Exception:
                continue
        return positions

    def invoke(self, context, event):
        cls = type(self)
        scene = getattr(context, "scene", None)
        addon = getattr(scene, "blosm", None) if scene else None
        if addon is None or not bool(getattr(addon, "route_adjuster_enabled", False)):
            return {'CANCELLED'}
        if not bool(getattr(addon, "route_adjuster_live_update", False)):
            return {'CANCELLED'}

        if cls._is_running:
            return {'CANCELLED'}

        if cls._timer is None:
            cls._is_running = True
            cls._timer = context.window_manager.event_timer_add(0.2, window=context.window)
            context.window_manager.modal_handler_add(self)
            cls._last_positions = self._collect_positions()
            cls._last_change_t = 0.0
            cls._pending = False
            cls._suppress_until = 0.0
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        cls = type(self)
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        scene = getattr(context, "scene", None)
        addon = getattr(scene, "blosm", None) if scene else None
        if addon is None or not bool(getattr(addon, "route_adjuster_enabled", False)):
            return self._cancel(context)
        if not bool(getattr(addon, "route_adjuster_live_update", False)):
            return self._cancel(context)

        now = time.monotonic()
        debounce_ms = int(getattr(addon, "route_adjuster_debounce_ms", 250))
        debounce_s = max(0.0, float(debounce_ms) / 1000.0)

        current = self._collect_positions()
        moved = False
        if cls._last_positions is None:
            cls._last_positions = current
        else:
            if now >= cls._suppress_until:
                for name, pos in current.items():
                    prev = cls._last_positions.get(name)
                    if prev is None:
                        moved = True
                        continue
                    if (pos - prev).length > 1e-5:
                        moved = True
                        break

        cls._last_positions = current
        if moved and now >= cls._suppress_until:
            cls._pending = True
            cls._last_change_t = now

        if cls._pending and now >= cls._suppress_until:
            if cls._last_change_t and (now - cls._last_change_t) >= debounce_s:
                try:
                    from ..route import route_adjuster

                    ok = bool(route_adjuster.recompute_route_from_controls(context))
                    if not ok:
                        addon.route_adjuster_last_error = "Missing ROUTE or controls"
                    else:
                        addon.route_adjuster_last_error = ""
                        _recompute_route_camera_if_possible(context)
                except Exception as exc:
                    addon.route_adjuster_last_error = str(exc)
                cls._pending = False
                cls._suppress_until = time.monotonic() + 0.5
                cls._last_positions = self._collect_positions()

        return {'PASS_THROUGH'}

    def _cancel(self, context):
        cls = type(self)
        try:
            if cls._timer is not None:
                context.window_manager.event_timer_remove(cls._timer)
        except Exception:
            pass
        cls._timer = None
        cls._last_positions = None
        cls._pending = False
        cls._is_running = False
        return {'CANCELLED'}

    def cancel(self, context):
        return self._cancel(context)


class BLOSM_OT_BakeAllGeonodes(bpy.types.Operator):
    """Bake all geometry nodes modifiers in the scene with custom frame logic"""

    bl_idname = "blosm.bake_all_geonodes"
    bl_label = "Bake All Geonodes"
    bl_description = "Bake all geometry nodes modifiers with automatic frame range adjustment for animated bakes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene_frame_start = scene.frame_start
        scene_frame_end = scene.frame_end
        scene_frame_duration = scene_frame_end - scene_frame_start

        # Calculate bake frame range (50 frames longer than timeline)
        bake_frame_start = scene_frame_start
        bake_frame_end = scene_frame_end + 50

        total_baked = 0
        processed_objects = []
        errors = []

        # Iterate through all objects in the scene
        for obj in scene.objects:
            if obj is None:
                continue

            obj_has_geonodes = False
            obj_baked_count = 0

            # Check for geometry nodes modifiers
            for mod in getattr(obj, "modifiers", []):
                if getattr(mod, "type", None) != "NODES":
                    continue

                obj_has_geonodes = True

                # Iterate through all bake sessions for this modifier
                for bake in getattr(mod, "bakes", []):
                    if bake is None:
                        continue

                    try:
                        # Set custom frame range for this bake
                        if hasattr(bake, "frame_start"):
                            bake.frame_start = bake_frame_start
                        if hasattr(bake, "frame_end"):
                            bake.frame_end = bake_frame_end

                        # Perform the bake operation
                        bpy.ops.object.geometry_node_bake_single(
                            session_uid=getattr(obj.id_data, "session_uid", 0) or 0,
                            modifier_name=mod.name,
                            bake_id=bake.bake_id,
                        )

                        obj_baked_count += 1
                        total_baked += 1

                    except Exception as exc:
                        error_msg = f"Failed to bake '{mod.name}' on object '{obj.name}': {exc}"
                        errors.append(error_msg)
                        print(f"[BLOSM] ERROR: {error_msg}")

                processed_objects.append(obj.name)

            # Report success for this object
            if obj_has_geonodes and obj_baked_count > 0:
                print(f"[BLOSM] Baked {obj_baked_count} geometry node modifier(s) on '{obj.name}'")

        # Final report
        if total_baked > 0:
            self.report({'INFO'}, f"Baked {total_baked} geometry node modifier(s) across {len(processed_objects)} object(s)")
            if errors:
                self.report({'WARNING'}, f"Completed with {len(errors)} errors - see console for details")
        else:
            self.report({'INFO'}, "No geometry node modifiers found to bake")

        return {'FINISHED'}





class BLOSM_OT_SnapAddress(bpy.types.Operator):
    """Geocode and snap address using Google Maps API"""
    bl_idname = "blosm.snap_address"
    bl_label = "Snap Address"
    bl_description = "Convert address to road-snapped GPS coordinates using Google API"
    bl_options = {'REGISTER'}

    type: bpy.props.EnumProperty(
        name="Type",
        items=[('START', "Start", "Start Address"), ('END', "End", "End Address")],
        default='START'
    )

    def execute(self, context):
        from ..gui.preferences import BlosmPreferences
        
        # Get preferences correctly
        # The preferences are on the addon object, not the scene
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        api_key = prefs.google_api_key
        from ..route import utils as route_utils
        api_key = route_utils.resolve_google_api_key(context, api_key)
        
        addon = context.scene.blosm
        if self.type == 'START':
            address = addon.route_start_address
        else:
            address = addon.route_end_address
            
        print(f"\n[BLOSM Snap] processing {self.type}: '{address}'")

        try:
            from ..route.utils import snap_address_logic
            res = snap_address_logic(address, api_key)
            
            if not res["success"]:
                self.report({'WARNING'}, res["error"])
                return {'CANCELLED'}
            
            self.report({'INFO'}, f"Result: {res['display_text']}")

            # Update Property
            if self.type == 'START':
                addon.start_snapped_coords = res["display_text"]
                addon.route_start_address_lat = res["lat"]
                addon.route_start_address_lon = res["lon"]
            else:
                addon.end_snapped_coords = res["display_text"]
                addon.route_end_address_lat = res["lat"]
                addon.route_end_address_lon = res["lon"]

        except Exception as e:
            self.report({'ERROR'}, f"Snap Exception: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}
