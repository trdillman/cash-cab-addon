"""
Route module configuration - Single source of truth for all constants

This module centralizes all configuration values that were previously
hard-coded throughout the route module. Configuration is organized into
logical groups using frozen dataclasses for immutability and type safety.

Usage:
    from .config import DEFAULT_CONFIG

    # Access configuration
    timeout = DEFAULT_CONFIG.api.nominatim_timeout_s
    car_location = DEFAULT_CONFIG.objects.car_default_location
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class APIConfig:
    """
    External API configuration

    Controls behavior of external service calls:
    - Nominatim (address geocoding)
    - OSRM (route calculation)
    - Overpass (OSM data fetching)
    """

    # Nominatim (geocoding) configuration
    nominatim_min_interval_s: float = 1.0
    nominatim_timeout_s: float = 30.0
    nominatim_user_agent: str = "BLOSM Route Import"
    nominatim_country_codes: str = "ca"  # Default to Canada

    # OSRM (routing) configuration
    osrm_base_url: str = "https://router.project-osrm.org"
    osrm_timeout_s: float = 30.0

    # Overpass (OSM data) configuration
    overpass_servers: Tuple[str, ...] = (
        "https://overpass-api.de",
        "https://overpass.kumi.systems",
        "https://z.overpass-api.de",
    )
    overpass_min_interval_ms: int = 1000
    overpass_timeout_s: float = 200.0  # Increased from 30s to allow full 180s query + 20s buffer
    overpass_max_retries: int = 3
    overpass_tile_max_m: float = 2000.0
    overpass_query_timeout: int = 180  # Overpass query timeout in seconds


@dataclass(frozen=True)
class GoogleAPIConfig:
    """
    Google Maps Platform API configuration
    """
    # Optional environment variable name to source a key from (useful for local testing)
    api_key_env_var: str = "AIzaSyB8LYSZ2_EBoi04kQQK8-2GDK-4wCNxMWU"
    # Optional hardcoded default key (leave blank for safety; only set locally for testing)
    api_key_default: str = "AIzaSyB8LYSZ2_EBoi04kQQK8-2GDK-4wCNxMWU"
    # Default to driving mode
    default_travel_mode: str = "driving"
    # Timeout for Google API requests
    timeout_s: float = 30.0


@dataclass(frozen=True)
class GeographyConfig:
    """
    Geographic and projection constants

    Physical constants used for geographic calculations and projections.
    """

    earth_radius_m: float = 6_371_000  # Earth radius in meters
    meters_per_degree_lat: float = 111_132.0  # Meters per degree latitude

    # Coordinate validation limits
    min_latitude: float = -90.0
    max_latitude: float = 90.0
    min_longitude: float = -180.0
    max_longitude: float = 180.0


@dataclass(frozen=True)
class RouteOperatorConfig:
    """
    Route operator UI and behavior configuration

    Controls the behavior of the BLOSM_OT_FetchRouteMap operator including
    UI dialogs, warnings, and operational limits.
    """

    # Size limits and warnings
    bbox_soft_limit_m: float = 5000.0  # Soft limit for bbox size in meters
    tile_warning_limit: int = 16  # Warn if tile count exceeds this

    # Behavior flags
    enable_logging: bool = True  # Enable console logging
    enable_dialog: bool = True  # Show confirmation dialog

    # Dialog dimensions
    dialog_width: int = 360  # Dialog width in pixels

    # Import defaults
    default_padding_m: float = 100.0  # Default route padding in meters
    default_import_roads: bool = True
    default_import_buildings: bool = True
    default_create_animation: bool = True


@dataclass(frozen=True)
class BlenderObjectConfig:
    """
    Blender object names and default settings

    Centralized naming convention for all Blender objects, modifiers,
    and constraints created by the route system.
    """

    # ===== Object Names =====
    route_object_name: str = "Route"
    start_marker_name: str = "Start"
    end_marker_name: str = "End"
    lead_object_name: str = "RouteLead"
    car_object_name: str = "ASSET_CAR"

    # Collection names
    route_collection_name: str = "ASSET_ROUTE"
    car_collection_name: str = "ASSET_CAR"  # Same as car object name
    assets_collection_name: str = "BLOSM_Assets"
    buildings_collection_name: str = "ASSET_BUILDINGS"

    # ===== Modifier Names =====
    route_modifier_name: str = "RouteTrace"
    building_modifier_name: str = "BuildingGeo"

    # ===== Constraint Names =====
    lead_constraint_name: str = "RouteLeadFollow"
    car_constraint_name: str = "RoutePreviewFollow"
    damped_track_name: str = "DT_to_Lead"

    # ===== Default Transforms =====
    # Car object defaults
    car_default_location: Tuple[float, float, float] = (0.0, 0.0, 1.5)
    car_default_scale: Tuple[float, float, float] = (20.0, 20.0, 20.0)
    car_default_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    # Lead object defaults
    lead_default_location: Tuple[float, float, float] = (0.0, 0.0, 1.5)
    lead_default_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    # ===== Empty/Marker Settings =====
    empty_display_size: float = 5.0
    empty_display_type: str = 'PLAIN_AXES'

    # Lead object settings
    lead_display_type: str = 'PLAIN_AXES'
    lead_display_size: float = 2.0

    # ===== Curve Settings =====
    curve_dimensions: str = '3D'
    curve_bevel_depth: float = 0.0
    curve_spline_type: str = 'POLY'


@dataclass(frozen=True)
class AnimationConfig:
    """
    Animation system configuration

    Default values for route animation including frame ranges,
    timing, and constraint settings.
    """

    # Frame ranges
    default_frame_start: int = 1
    default_frame_end: int = 250
    default_lead_frames: int = 10

    # Path/curve settings
    path_duration: int = 250
    use_path: bool = True
    use_curve_follow: bool = True
    use_fixed_location: bool = True

    # Constraint axes
    follow_forward_axis: str = 'FORWARD_X'
    follow_up_axis: str = 'UP_Z'
    track_axis: str = 'TRACK_NEGATIVE_Z'
    track_up_axis: str = 'UP_Y'
    damped_track_axis: str = 'TRACK_Y'
    damped_up_axis: str = 'UP_Z'

    # Camera follow settings
    camera_offset_location: Tuple[float, float, float] = (0.0, -20.0, 6.0)
    camera_rotation_x_deg: float = -10.0  # Rotation in degrees

    # Driver settings
    driver_variable_name_start: str = "v_start"
    driver_variable_name_end: str = "v_end"
    driver_variable_name_lead: str = "v_lead"
    driver_variable_name_frame: str = "frame"

    # Animation property names
    prop_anim_start: str = "blosm_anim_start"
    prop_anim_end: str = "blosm_anim_end"
    prop_lead_frames: str = "blosm_lead_frames"
    prop_base_start: str = "blosm_base_start"
    prop_base_end: str = "blosm_base_end"

    # GeoNodes socket names
    gn_offset_factor_socket: str = "OffsetFactor"
    gn_profile_radius_socket: str = "ProfileRadius"


@dataclass(frozen=True)
class ViewportConfig:
    """
    Viewport and rendering configuration

    Settings for viewport display and camera clipping.
    """

    # View clipping
    min_clip_end: float = 1000.0
    clip_end_multiplier: float = 1.5
    max_clip_end: float = 1.0e9

    # View updates
    scale_clip_factor: float = 10.0  # Factor to scale clip_end by


@dataclass(frozen=True)
class AssetPathConfig:
    """
    Asset file paths configuration

    Paths to asset .blend files relative to the route module.
    """

    # Asset directory (relative to route module)
    asset_directory_name: str = "assets"

    # Asset file names
    route_blend_filename: str = "ASSET_ROUTE.blend"
    car_blend_filename: str = "ASSET_CAR.blend"
    buildings_blend_filename: str = "ASSET_BUILDINGS.blend"
    world_blend_filename: str = "ASSET_WORLD.blend"
    base_start_blend_filename: str = "ASSET_BASE-START.blend"
    base_end_blend_filename: str = "ASSET_BASE-END.blend"

    # Asset names within .blend files
    route_material_name: str = "RouteLine"
    route_nodegroup_name: str = "ASSET_RouteTrace"
    car_object_name: str = "ASSET_CAR"
    world_name: str = "ASSET_WORLD"


@dataclass(frozen=True)
class ImportConfig:
    """
    OSM import configuration

    Settings specific to OSM data import process.
    """

    # Import modes
    data_type_osm: str = "osm"
    osm_source_server: str = "server"
    mode_3d_simple: str = "3Dsimple"

    # Tile import settings
    tile_centroid_threshold_m: float = 5.0  # Max centroid offset for tile validation

    # State capture keys
    state_keys: Tuple[str, ...] = (
        "dataType", "osmSource", "minLat", "maxLat", "minLon", "maxLon",
        "buildings", "highways", "water", "forests", "vegetation", "railways",
        "relativeToInitialImport"
    )


@dataclass(frozen=True)
class LoggingConfig:
    """
    Logging and debugging configuration
    """

    log_prefix: str = "[BLOSM]"
    enable_route_summary: bool = True
    enable_tile_progress: bool = True
    enable_asset_logging: bool = True

    # Log message formats
    route_summary_format: str = "Route summary: {}"
    tile_progress_format: str = "Route import: tile {}/{} ({:.0f}%)"
    error_format: str = "[BLOSM] ERROR: {}"
    warning_format: str = "[BLOSM] WARN: {}"


@dataclass
class RouteConfig:
    """
    Master configuration container

    This is the main configuration object that aggregates all sub-configurations.
    It is mutable to allow runtime updates from addon preferences.

    Usage:
        # Get default config
        config = RouteConfig()

        # Create from preferences
        config = RouteConfig.from_addon_preferences(context.preferences.addons['blosm'])

        # Access sub-configs
        timeout = config.api.nominatim_timeout_s
        car_pos = config.objects.car_default_location
    """

    api: APIConfig = field(default_factory=APIConfig)
    google_api: GoogleAPIConfig = field(default_factory=GoogleAPIConfig)
    geography: GeographyConfig = field(default_factory=GeographyConfig)
    operator: RouteOperatorConfig = field(default_factory=RouteOperatorConfig)
    objects: BlenderObjectConfig = field(default_factory=BlenderObjectConfig)
    animation: AnimationConfig = field(default_factory=AnimationConfig)
    viewport: ViewportConfig = field(default_factory=ViewportConfig)
    assets: AssetPathConfig = field(default_factory=AssetPathConfig)
    import_config: ImportConfig = field(default_factory=ImportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_addon_preferences(cls, addon_prefs):
        """
        Create configuration from Blender addon preferences

        Args:
            addon_prefs: Blender addon preferences object

        Returns:
            RouteConfig: Configuration with values from preferences
        """
        # Extract user agent from preferences if available
        user_agent = APIConfig.nominatim_user_agent
        if hasattr(addon_prefs, 'preferences'):
            pref_obj = addon_prefs.preferences
            if hasattr(pref_obj, 'nominatimUserAgent'):
                user_agent = pref_obj.nominatimUserAgent or user_agent

        return cls(
            api=APIConfig(
                nominatim_user_agent=user_agent
            )
        )

    def validate(self) -> bool:
        """
        Validate configuration consistency

        Returns:
            bool: True if configuration is valid
        """
        # Validate geography constraints
        if not (-90.0 <= self.geography.min_latitude <= self.geography.max_latitude <= 90.0):
            return False

        if not (-180.0 <= self.geography.min_longitude <= self.geography.max_longitude <= 180.0):
            return False

        # Validate timeouts are positive
        if self.api.nominatim_timeout_s <= 0:
            return False

        if self.api.overpass_timeout_s <= 0:
            return False

        # Validate frame ranges
        if self.animation.default_frame_start < 1:
            return False

        if self.animation.default_frame_end <= self.animation.default_frame_start:
            return False

        return True

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary

        Useful for serialization and debugging.

        Returns:
            dict: Configuration as nested dictionary
        """
        return {
            'api': {
                'nominatim_user_agent': self.api.nominatim_user_agent,
                'nominatim_timeout_s': self.api.nominatim_timeout_s,
                'overpass_timeout_s': self.api.overpass_timeout_s,
                'overpass_max_retries': self.api.overpass_max_retries,
            },
            'operator': {
                'bbox_soft_limit_m': self.operator.bbox_soft_limit_m,
                'tile_warning_limit': self.operator.tile_warning_limit,
            },
            'objects': {
                'route_object_name': self.objects.route_object_name,
                'car_default_location': self.objects.car_default_location,
            },
            # Add more as needed
        }


# ===== Global Default Instance =====
# This is the primary way to access configuration throughout the codebase
DEFAULT_CONFIG = RouteConfig()


# ===== Convenience Functions =====

def get_config() -> RouteConfig:
    """
    Get the global default configuration

    Returns:
        RouteConfig: The default configuration instance
    """
    return DEFAULT_CONFIG


def create_config_from_context(context) -> RouteConfig:
    """
    Create configuration from Blender context

    Args:
        context: Blender context object

    Returns:
        RouteConfig: Configuration with values from context
    """
    try:
        addon_name = "blosm"
        prefs = context.preferences.addons
        if addon_name in prefs:
            return RouteConfig.from_addon_preferences(prefs[addon_name])
    except Exception:
        pass

    return RouteConfig()


# ===== Exports =====
__all__ = [
    'APIConfig',
    'GoogleAPIConfig',
    'GeographyConfig',
    'RouteOperatorConfig',
    'BlenderObjectConfig',
    'AnimationConfig',
    'ViewportConfig',
    'AssetPathConfig',
    'ImportConfig',
    'LoggingConfig',
    'RouteConfig',
    'DEFAULT_CONFIG',
    'get_config',
    'create_config_from_context',
]
