"""
Route Preparation Service

Handles geocoding addresses and calculating routes between locations.
Encapsulates all external API calls (Nominatim, OSRM) and provides
clean interface for route preparation.
"""

from dataclasses import dataclass
from typing import Optional

from ..config import RouteConfig
from ..utils import (
    RouteContext,
    RouteServiceError,
    prepare_route as utils_prepare_route
)
from .base import IService, ILogger, ConsoleLogger, ServiceResult


@dataclass
class RoutePreparationResult:
    """
    Result of route preparation operation

    Contains either a successful route context or error information.
    """

    context: Optional[RouteContext]
    error: Optional[str]
    over_limit: bool
    tile_count: int = 0
    distance_km: float = 0.0
    width_m: float = 0.0
    height_m: float = 0.0

    @property
    def success(self) -> bool:
        """Check if preparation was successful"""
        return self.context is not None and self.error is None

    @classmethod
    def from_context(cls, context: RouteContext, bbox_limit_m: float) -> 'RoutePreparationResult':
        """Create result from successful route context"""
        over_limit = (
            context.width_m > bbox_limit_m or
            context.height_m > bbox_limit_m
        )

        return cls(
            context=context,
            error=None,
            over_limit=over_limit,
            tile_count=context.tile_count,
            distance_km=context.route.distance_m / 1000.0,
            width_m=context.width_m,
            height_m=context.height_m,
        )

    @classmethod
    def from_error(cls, error: str) -> 'RoutePreparationResult':
        """Create result from error"""
        return cls(
            context=None,
            error=error,
            over_limit=False,
        )


class RoutePreparationService(IService):
    """
    Service for preparing routes

    Handles:
    - Address geocoding via Nominatim
    - Route calculation via OSRM
    - Bounding box calculation and padding
    - Tile calculation for Overpass

    This service has no Blender dependencies and can be tested independently.
    """

    def __init__(
        self,
        config: RouteConfig,
        logger: Optional[ILogger] = None
    ):
        """
        Initialize route preparation service

        Args:
            config: Route configuration
            logger: Optional logger for service operations
        """
        self.config = config
        self.logger = logger or ConsoleLogger()
        self._last_result: Optional[RoutePreparationResult] = None

    def validate(self) -> bool:
        """
        Validate service configuration

        Returns:
            bool: True if configuration is valid
        """
        return self.config.validate()

    def prepare(
        self,
        start_address: str,
        end_address: str,
        padding_m: float,
        user_agent: Optional[str] = None
    ) -> RoutePreparationResult:
        """
        Prepare a route from start to end address

        This performs:
        1. Geocode start address → lat/lon
        2. Geocode end address → lat/lon
        3. Calculate route via OSRM
        4. Calculate bounding box
        5. Add padding to bbox
        6. Calculate tiles for Overpass
        7. Check size limits

        Args:
            start_address: Starting address (e.g., "123 Main St, Toronto")
            end_address: Ending address
            padding_m: Padding in meters to add around route
            user_agent: Optional user agent override

        Returns:
            RoutePreparationResult: Result with context or error
        """
        # Use configured user agent if not provided
        user_agent = user_agent or self.config.api.nominatim_user_agent

        # Log operation start
        self.logger.info(
            f"Preparing route: '{start_address}' → '{end_address}' "
            f"(padding: {padding_m}m)"
        )

        try:
            # Call utility function that does the actual work
            context = utils_prepare_route(
                start_address,
                end_address,
                padding_m,
                user_agent
            )

            # Create result from context
            result = RoutePreparationResult.from_context(
                context,
                self.config.operator.bbox_soft_limit_m
            )

            # Log success
            self.logger.info(
                f"Route prepared successfully: "
                f"{result.distance_km:.2f} km, "
                f"{result.tile_count} tiles"
            )

            # Warn if over size limit
            if result.over_limit:
                self.logger.warning(
                    f"Route exceeds size limit: "
                    f"{result.width_m:.0f}m × {result.height_m:.0f}m "
                    f"(limit: {self.config.operator.bbox_soft_limit_m}m)"
                )

            # Cache result
            self._last_result = result
            return result

        except RouteServiceError as e:
            # Service-specific error
            error_msg = str(e)
            self.logger.error(f"Route preparation failed: {error_msg}")

            result = RoutePreparationResult.from_error(error_msg)
            self._last_result = result
            return result

        except Exception as e:
            # Unexpected error
            error_msg = f"Unexpected error during route preparation: {e}"
            self.logger.error(error_msg)

            result = RoutePreparationResult.from_error(error_msg)
            self._last_result = result
            return result

    def get_last_result(self) -> Optional[RoutePreparationResult]:
        """
        Get the last preparation result

        Useful for retrieving cached results without re-preparing.

        Returns:
            Optional[RoutePreparationResult]: Last result or None
        """
        return self._last_result

    def clear_cache(self):
        """Clear cached preparation result"""
        self._last_result = None

    def prepare_with_validation(
        self,
        start_address: str,
        end_address: str,
        padding_m: float,
        user_agent: Optional[str] = None,
        max_bbox_m: Optional[float] = None
    ) -> RoutePreparationResult:
        """
        Prepare route with additional validation

        This version adds extra checks before and after preparation.

        Args:
            start_address: Starting address
            end_address: Ending address
            padding_m: Padding in meters
            user_agent: Optional user agent
            max_bbox_m: Maximum bbox size (hard limit)

        Returns:
            RoutePreparationResult: Result with context or error
        """
        # Validate inputs
        if not start_address or not start_address.strip():
            return RoutePreparationResult.from_error("Start address is empty")

        if not end_address or not end_address.strip():
            return RoutePreparationResult.from_error("End address is empty")

        if padding_m < 0:
            return RoutePreparationResult.from_error("Padding must be non-negative")

        # Prepare route
        result = self.prepare(start_address, end_address, padding_m, user_agent)

        # Additional validation if requested
        if result.success and max_bbox_m is not None:
            if result.width_m > max_bbox_m or result.height_m > max_bbox_m:
                error_msg = (
                    f"Route exceeds maximum size: "
                    f"{result.width_m:.0f}m × {result.height_m:.0f}m "
                    f"(max: {max_bbox_m}m)"
                )
                self.logger.error(error_msg)
                return RoutePreparationResult.from_error(error_msg)

        return result


__all__ = [
    'RoutePreparationService',
    'RoutePreparationResult',
]
