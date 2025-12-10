"""Route Exception Hierarchy
Defines a structured exception system for route operations within BLOSM.
"""

class RouteServiceError(Exception):
    """Base exception for all route-related errors."""
    pass


class GeocodingError(RouteServiceError):
    """Geocoding service failures."""
    pass


class RoutingError(RouteServiceError):
    """Route calculation failures."""
    pass


class OverpassError(RouteServiceError):
    """Overpass API failures."""
    pass


class TileImportError(RouteServiceError):
    """Tile import or validation failure."""
    pass


class TileValidationError(RouteServiceError):
    """Tile validation failure."""
    pass


class RouteObjectError(RouteServiceError):
    """Route object creation or manipulation error."""
    pass


class GeocodeError(RouteServiceError):
    """Geocoding data error."""
    pass


class RouteStateError(RouteServiceError):
    """Route state management error."""
    pass


class ConfigurationError(RouteServiceError):
    """Configuration or dependency resolution errors."""
    pass