"""
BLOSM Route Import - GUI Properties
Minimal property definitions for route import functionality only.
"""

import bpy
try:
    from bpy.props import UNSIGNED  # Blender 4.2+ only
except Exception:
    UNSIGNED = None  # Fallback for older Blender builds



# Simplified - no 3D realistic mode in minimal version
_has3dRealistic = False


def _gather_selected_objects(context):
    if context is None:
        return []
    selected = list(getattr(context, "selected_objects", []) or [])
    active = getattr(context, "active_object", None)
    if active and active not in selected:
        selected.insert(0, active)
    return selected


def _on_uturn_trim_toggle(self, context):
    # Toggle should work immediately after route import; use an operator for consistent context/reporting.
    try:
        bpy.ops.blosm.apply_uturn_trim('EXEC_DEFAULT')
    except Exception as exc:
        print(f"[CashCab] WARN u-turn trim toggle failed: {exc}")


def _on_street_labels_toggle(self, context):
    try:
        from ..road import street_labels

        scene = getattr(context, "scene", None)
        if scene is None:
            return
        street_labels.set_street_labels_visible(scene, bool(getattr(self, "ui_show_street_labels", False)))
    except Exception as exc:
        print(f"[BLOSM] WARN street labels: toggle failed: {exc}")


def _on_uturn_trim_params_update(self, context):
    # Only reapply if trimming is enabled; otherwise leave route untouched.
    try:
        if bool(getattr(self, "route_trim_end_uturns", False)):
            bpy.ops.blosm.apply_uturn_trim('EXEC_DEFAULT')
    except Exception as exc:
        print(f"[CashCab] WARN u-turn trim params update failed: {exc}")


def _on_route_adjuster_live_update_toggle(self, context):
    # Start the modal watcher when toggled on. Turning off is handled by the modal operator itself.
    try:
        if not bool(getattr(self, "route_adjuster_live_update", False)):
            return
        if context is None or getattr(context, "window_manager", None) is None:
            return
        bpy.ops.blosm.route_adjuster_live_update_modal("INVOKE_DEFAULT")
    except Exception as exc:
        try:
            self.route_adjuster_last_error = str(exc)
            self.route_adjuster_live_update = False
        except Exception:
            pass





def _on_start_address_update(self, context):
    """Clear snapped coordinates when address text changes"""
    self.start_snapped_coords = ""
    self.route_start_address_lat = 0.0
    self.route_start_address_lon = 0.0


def _on_end_address_update(self, context):
    """Clear snapped coordinates when address text changes"""
    self.end_snapped_coords = ""
    self.route_end_address_lat = 0.0
    self.route_end_address_lon = 0.0


def getDataTypes(self, context):
    """Return available data types for import"""
    return [
        ("osm", "OpenStreetMap", "OpenStreetMap"),
        ("terrain", "terrain", "Terrain"),
    ]


class BlosmRouteWaypoint(bpy.types.PropertyGroup):
    """Single waypoint/stop address for route"""
    
    address: bpy.props.StringProperty(
        name="Waypoint Address",
        description="Intermediate stop address between start and end",
        default=""
    )


class BlosmDefaultLevelsEntry(bpy.types.PropertyGroup):
    """Entry for default building levels with weight"""

    levels: bpy.props.IntProperty(
        name="Levels",
        description="Default number of levels",
        default=5,
        min=1,
    )

    weight: bpy.props.IntProperty(
        name="Weight",
        description="Relative weight for random selection",
        default=100,
        min=1,
    )


class BlosmProperties(bpy.types.PropertyGroup):
    """Main property group for BLOSM route import addon"""

    # OSM Import settings
    dataType: bpy.props.EnumProperty(
        name="Data",
        items=getDataTypes,
        description="Data type for import",
        default=0,
    )

    mode: bpy.props.EnumProperty(
        name="Mode: 3D or 2D",
        items=(("3Dsimple", "3D", "3D"), ("2D", "2D", "2D")),
        description="Import data in 3D or 2D mode",
        default="3Dsimple",
    )

    osmSource: bpy.props.EnumProperty(
        name="Import OpenStreetMap from",
        items=(
            ("server", "server", "remote server"),
            ("file", "file", "file on the local disk"),
        ),
        description="From where to import OpenStreetMap data: remote server or a file on the local disk",
        default="server",
    )

    osmFilepath: bpy.props.StringProperty(
        name="OpenStreetMap file",
        subtype='FILE_PATH',
        description="Path to an OpenStreetMap file for import",
    )

    # Route Provider settings
    
    # Snapped coordinates display
    start_snapped_coords: bpy.props.StringProperty(
        name="Snapped Coords",
        description="Coordinates snapped to nearest road via Google API",
        default=""
    )

    end_snapped_coords: bpy.props.StringProperty(
        name="Snapped Coords",
        description="Coordinates snapped to nearest road via Google API",
        default=""
    )


    # Coordinate bounds
    minLat: bpy.props.FloatProperty(
        name="min lat",
        description="Minimum latitude of the imported extent",
        precision=4,
        min=-89.0,
        max=89.0,
        default=51.33,
    )

    maxLat: bpy.props.FloatProperty(
        name="max lat",
        description="Maximum latitude of the imported extent",
        precision=4,
        min=-89.0,
        max=89.0,
        default=51.33721,
    )

    minLon: bpy.props.FloatProperty(
        name="min lon",
        description="Minimum longitude of the imported extent",
        precision=4,
        min=-180.0,
        max=180.0,
        default=12.36902,
    )

    maxLon: bpy.props.FloatProperty(
        name="max lon",
        description="Maximum longitude of the imported extent",
        precision=4,
        min=-180.0,
        max=180.0,
        default=12.37983,
    )

    coordinatesAsFilter: bpy.props.BoolProperty(
        name="Use coordinates as filter",
        description="Use coordinates as a filter for the import from the file",
        default=False,
    )

    # Layer import toggles
    buildings: bpy.props.BoolProperty(
        name="Import buildings",
        description="Import building outlines",
        default=True,
    )

    water: bpy.props.BoolProperty(
        name="Import water",
        description="Import water objects (rivers and lakes)",
        default=True,
    )

    forests: bpy.props.BoolProperty(
        name="Import forests",
        description="Import forests and woods",
        default=True,
    )

    vegetation: bpy.props.BoolProperty(
        name="Import other vegetation",
        description="Import other vegetation (grass, meadow, scrub)",
        default=True,
    )

    highways: bpy.props.BoolProperty(
        name="Import roads and paths",
        description="Import roads and paths",
        default=True,
    )

    railways: bpy.props.BoolProperty(
        name="Import railways",
        description="Import railways",
        default=False,
    )

    # General settings
    terrainObject: bpy.props.StringProperty(
        name="Terrain",
        description="Blender object for the terrain",
    )

    singleObject: bpy.props.BoolProperty(
        name="Import as a single object",
        description="Import OSM objects as a single Blender mesh objects instead of separate ones",
        default=True,
    )

    relativeToInitialImport: bpy.props.BoolProperty(
        name="Relative to initial import",
        description="Import relative to the initial import if it is available",
        default=True,
    )

    setupScript: bpy.props.StringProperty(
        name="Setup script",
        subtype='FILE_PATH',
        description="Path to a setup script. Leave blank for default.",
    )

    loadMissingMembers: bpy.props.BoolProperty(
        name="Load missing members of relations",
        description=(
            "Relation members aren't contained in the OSM file if they are located outside of the OSM file extent. "
            "Enable this option to load the missing members of the relations either from a local file (if available) "
            "or from the server."
        ),
        default=True,
    )

    # Route address inputs
    route_start_address: bpy.props.StringProperty(
        name="Start Address",
        description="Starting address for route geocoding",
        default="1 Dundas St. E, Toronto",
        update=_on_start_address_update,
    )

    route_end_address: bpy.props.StringProperty(
        name="End Address",
        description="Ending address for route geocoding",
        default="500 Yonge St, Toronto",
        update=_on_end_address_update,
    )

    route_end_address_lat: bpy.props.FloatProperty(
        name="End Latitude",
        description="Latitude of end address (auto-populated)",
        default=0.0,
    )

    route_end_address_lon: bpy.props.FloatProperty(
        name="End Longitude",
        description="Longitude of end address (auto-populated)",
        default=0.0,
    )

    # Route waypoints collection
    route_waypoints: bpy.props.CollectionProperty(
        type=BlosmRouteWaypoint,
        name="Route Waypoints",
        description="Intermediate stops between start and end",
    )

    # Route geocoded coordinates (stored by geocoding service)
    route_start_address_lat: bpy.props.FloatProperty(
        name="Start Latitude",
        description="Latitude of start address (auto-populated)",
        default=0.0,
    )

    route_start_address_lon: bpy.props.FloatProperty(
        name="Start Longitude",
        description="Longitude of start address (auto-populated)",
        default=0.0,
    )


    route_padding_m: bpy.props.FloatProperty(
        name="Padding (m)",
        description="Padding in meters to expand the route bounding box",
        min=0.0,
        default=2000.0,
    )

  
    route_extend_m: bpy.props.FloatProperty(
        name="Extend by (m)",
        description="Extend the imported city in all directions by this many meters",
        default=200.0,
        min=0.0,
        soft_max=5000.0,
    )

    route_create_preview_animation: bpy.props.BoolProperty(
        name="Create Animated Route & Assets",
        description="Generate a 250 frame animated preview along the imported route",
        default=True,
    )

    route_generate_camera: bpy.props.BoolProperty(
        name="Auto-generate Camera",
        description="Automatically spawn and animate a camera rig after route import",
        default=True,
    )

    route_trim_end_uturns: bpy.props.BoolProperty(
        name="Trim Start/End U-Turns",
        description=(
            "Convenience toggle: detect and remove small U-turn loops near the start/end of the imported route. "
            "Does not modify mid-route geometry."
        ),
        default=False,
        update=_on_uturn_trim_toggle,
    )

    route_trim_window_fraction: bpy.props.FloatProperty(
        name="Trim Window Fraction",
        description="Fraction of total route length analyzed at each end (0.10 = 10%)",
        default=0.10,
        min=0.01,
        max=0.50,
        update=_on_uturn_trim_params_update,
    )

    route_trim_corner_angle_min: bpy.props.FloatProperty(
        name="Corner Angle Min (deg)",
        description="Minimum turn angle to consider as a corner candidate",
        default=70.0,
        min=0.0,
        max=180.0,
        update=_on_uturn_trim_params_update,
    )

    route_trim_direction_reverse_deg: bpy.props.FloatProperty(
        name="Direction Reverse (deg)",
        description="Minimum direction reversal angle to classify as a U-turn",
        default=150.0,
        min=90.0,
        max=180.0,
        update=_on_uturn_trim_params_update,
    )

    route_trim_max_uturn_fraction: bpy.props.FloatProperty(
        name="Max U-Turn Fraction",
        description="Maximum fraction of route length allowed for the trimmed U-turn region",
        default=0.10,
        min=0.01,
        max=0.50,
        update=_on_uturn_trim_params_update,
    )

    route_import_separate_tiles: bpy.props.BoolProperty(
        name="Import separate tiles",
        description="Import Overpass tiles separately for better alignment",
        default=False,
    )

    # Runtime route curve tracking for CAR_TRAIL binding
    route_curve_obj: bpy.props.PointerProperty(
        name="Route Curve Object",
        type=bpy.types.Object,
        description="Runtime reference to the OSM route curve used for CAR_TRAIL",
    )

    route_curve_name: bpy.props.StringProperty(
        name="Route Curve Name",
        description="Fallback name of the OSM route curve used for CAR_TRAIL",
        default="",
    )

    # UI toggles
    ui_show_animation: bpy.props.BoolProperty(
        name="Show Animation Controls",
        description="Toggle visibility of animation control section in the CashCab panel",
        default=False,
    )

    ui_show_route_camera: bpy.props.BoolProperty(
        name="Show Route Camera",
        description="Toggle visibility of route camera section in the CashCab panel",
        default=False,
    )

    ui_show_extend_city: bpy.props.BoolProperty(
        name="Show Extend City Controls",
        description="Toggle visibility of the Extend City controls in the CashCab panel",
        default=False,
    )

    ui_show_extra_features: bpy.props.BoolProperty(
        name="Show Extra Features",
        description="Toggle visibility of extra convenience features in the CashCab panel",
        default=False,
    )

    auto_snap_addresses: bpy.props.BoolProperty(
        name="Auto Snap Addresses",
        description="Automatically snap addresses to road centerlines using Google API during import",
        default=True,
    )

    route_adjuster_enabled: bpy.props.BoolProperty(
        name="Enable Route Adjuster",
        description="Enable interactive route control empties and reroute tools",
        default=False,
    )

    route_adjuster_live_update: bpy.props.BoolProperty(
        name="Live Update (opt-in)",
        description="When enabled, reroute automatically after moving ROUTE_CTRL_* empties (debounced)",
        default=False,
        update=_on_route_adjuster_live_update_toggle,
    )

    route_adjuster_snap_points: bpy.props.BoolProperty(
        name="Snap control points to roads",
        description="When rerouting from controls, snap control points to nearby road centerlines",
        default=False,
    )

    route_adjuster_allow_any_highway_fallback: bpy.props.BoolProperty(
        name="Allow any-highway fallback",
        description="If strict snap fails, allow snapping to any OSM highway (may include service/paths)",
        default=False,
    )

    route_adjuster_debounce_ms: bpy.props.IntProperty(
        name="Debounce (ms)",
        description="Delay before recompute when live updates are enabled",
        default=250,
        min=0,
        max=5000,
    )

    route_adjuster_last_error: bpy.props.StringProperty(
        name="Last Error",
        description="Last route adjuster error message",
        default="",
    )

    ui_show_street_labels: bpy.props.BoolProperty(
        name="Show Street Labels",
        description="Show/hide the STREET_LABELS collection in the viewport (labels never render)",
        default=False,
        update=_on_street_labels_toggle,
    )

    # Fallback building heights (used by route buildings)
    levelHeight: bpy.props.FloatProperty(
        name="Level height",
        description=(
            "Average height of a level in meters to use for OSM tags building:levels and building:min_level"
        ),
        default=5.0,
    )

    defaultLevels: bpy.props.CollectionProperty(type=BlosmDefaultLevelsEntry)

    defaultLevelsIndex: bpy.props.IntProperty(
        subtype='UNSIGNED',
        default=0,
        description="Index of the active entry for the default number of levels",
    )



    straightAngleThreshold: bpy.props.FloatProperty(
        name="Straight angle threshold",
        description=(
            "Threshold for an angle of the building outline: when consider it as straight one. "
            "It may be important for calculation of the longest side of the building outline for a gabled roof."
        ),
        default=175.5,
        min=170.0,
        max=179.95,
        step=10,
    )

    defaultRoofShape: bpy.props.EnumProperty(
        items=(("flat", "flat", "flat shape"), ("gabled", "gabled", "gabled shape")),
        description="Roof shape for a building if the roof shape is not set in OpenStreetMap",
        default="flat",
    )
