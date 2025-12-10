"""
Route State Manager for BLOSM Route System

This module provides state management functionality for the route system,
extracted from the original fetch_operator.py to improve separation of concerns
and maintainability.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

import bpy
from ..app import blender as blenderApp
from .exceptions import RouteStateError
from .config import DEFAULT_CONFIG


@dataclass
class TileConfiguration:
    """Configuration for tile import"""
    south: float
    west: float
    north: float
    east: float
    include_roads: bool
    include_buildings: bool


@dataclass
class AddonState:
    """State captured from addon for restoration"""
    bbox: List[float]
    route_import_roads: bool
    route_import_buildings: bool
    route_import_separate_tiles: bool
    route_start_address: str
    route_start_address_lat: float
    route_start_address_lon: float
    route_end_address: str
    route_end_address_lat: float
    route_end_address_lon: float
    route_padding_m: float
    route_waypoints: List[Dict[str, Any]]

    def apply_to_addon(self, addon) -> None:
        """Apply captured state to addon"""
        addon.bbox = self.bbox
        addon.route_import_roads = self.route_import_roads
        addon.route_import_buildings = self.route_import_buildings
        addon.route_import_separate_tiles = self.route_import_separate_tiles
        addon.route_start_address = self.route_start_address
        addon.route_start_address_lat = self.route_start_address_lat
        addon.route_start_address_lon = self.route_start_address_lon
        addon.route_end_address = self.route_end_address
        addon.route_end_address_lat = self.route_end_address_lat
        addon.route_end_address_lon = self.route_end_address_lon
        addon.route_padding_m = self.route_padding_m

        if hasattr(addon, 'route_waypoints'):
            # Clear existing waypoints and add new ones
            addon.route_waypoints.clear()
            for waypoint_data in self.route_waypoints:
                waypoint = addon.route_waypoints.add()
                if isinstance(waypoint_data, dict):
                    waypoint.address = waypoint_data.get('address', '')
                else:
                    waypoint.address = str(waypoint_data)


class StateContext:
    """Context for route operations"""
    def __init__(self, tiles: List[Any], width_m: float, height_m: float,
                 bbox_area_km2: float, tile_count: int):
        """
        Initialize route context.

        Args:
            tiles: List of tile data
            width_m: Width in meters
            height_m: Height in meters
            bbox_area_km2: Area of bounding box in km²
            tile_count: Number of tiles
        """
        self.tiles = tiles
        self.width_m = width_m
        self.height_m = height_m
        self.bbox_area_km2 = bbox_area_km2
        self.tile_count = tile_count

        # Calculate padded bounding box
        if tiles:
            min_south = min(tile.get('bounds', [0, 0, 0, 0])[0] for tile in tiles)
            min_west = min(tile.get('bounds', [0, 0, 0, 0])[1] for tile in tiles)
            min_north = min(tile.get('bounds', [0, 0, 0, 0])[2] for tile in tiles)
            min_east = min(tile.get('bounds', [0, 0, 0, 0])[3] for tile in tiles)

            max_south = max(tile.get('bounds', [0, 0, 0, 0])[0] for tile in tiles)
            max_west = max(tile.get('bounds', [0, 0, 0, 0])[1] for tile in tiles)
            max_north = max(tile.get('bounds', [0, 0, 0, 0])[2] for tile in tiles)
            max_east = max(tile.get('bounds', [0, 0, 0, 0])[3] for tile in tiles)

            self.padded_bbox = [min_south, min_west, max_north, max_east]
        else:
            self.padded_bbox = [0.0, 0.0, 0.0, 0.0]

    @property
    def route(self):
        """Get route object from context"""
        scene = getattr(blenderApp.app, 'scene', None)
        if scene and hasattr(scene, 'blosm'):
            return getattr(scene.blosm, 'route', None)
        return None


class RouteStateManager:
    """
    Manages route state operations with improved modularity and error handling.

    This class encapsulates state capture, restoration, and configuration
    logic that was previously scattered throughout the fetch_operator.
    """

    def __init__(self):
        """
        Initialize route state manager.
        """
        # Simple logger implementation
        self.logger = self

    def info(self, message: str) -> None:
        """Log info message"""
        print(f"[BLOSM RouteStateManager] INFO: {message}")

    def error(self, message: str) -> None:
        """Log error message"""
        print(f"[BLOSM RouteStateManager] ERROR: {message}")

    def warning(self, message: str) -> None:
        """Log warning message"""
        print(f"[BLOSM RouteStateManager] WARNING: {message}")

    def capture_state(self, addon) -> AddonState:
        """
        Capture current addon state for later restoration.

        Args:
            addon: BLOSM addon object

        Returns:
            AddonState with captured state
        """
        try:
            state = AddonState(
                bbox=getattr(addon, 'bbox', []),
                route_import_roads=getattr(addon, 'route_import_roads', False),
                route_import_buildings=getattr(addon, 'route_import_buildings', False),
                route_import_separate_tiles=getattr(addon, 'route_import_separate_tiles', False),
                route_start_address=getattr(addon, 'route_start_address', ''),
                route_start_address_lat=getattr(addon, 'route_start_address_lat', 0.0),
                route_start_address_lon=getattr(addon, 'route_start_address_lon', 0.0),
                route_end_address=getattr(addon, 'route_end_address', ''),
                route_end_address_lat=getattr(addon, 'route_end_address_lat', 0.0),
                route_end_address_lon=getattr(addon, 'route_end_address_lon', 0.0),
                route_padding_m=getattr(addon, 'route_padding_m', 0.0),
                route_waypoints=[{'address': wp.address} for wp in getattr(addon, 'route_waypoints', [])]
            )

            self.logger.info("State captured successfully")
            return state

        except Exception as e:
            self.logger.error(f"Failed to capture state: {e}")
            raise RouteStateError(f"State capture failed: {e}")

    def configure_for_tile_import_bounds(self, addon, south: float, west: float,
                                       north: float, east: float, include_roads: bool,
                                       include_buildings: bool) -> None:
        """
        Configure addon for tile import with specific bounds.

        Args:
            addon: BLOSM addon object
            south, west, north, east: Bounding box coordinates
            include_roads: Whether to import roads
            include_buildings: Whether to import buildings
        """
        try:
            # Set bounding box
            addon.bbox = [south, west, north, east]

            # Set import options
            addon.route_import_roads = include_roads
            addon.route_import_buildings = include_buildings

            # Clear any existing route data
            if hasattr(addon, 'route'):
                delattr(addon, 'route')

            self.logger.info(f"Configured for tile import: {include_roads}, {include_buildings}")

        except Exception as e:
            self.logger.error(f"Failed to configure addon: {e}")
            raise RouteStateError(f"Configuration failed: {e}")

    def restore_state(self, addon, state: Union[AddonState, Dict[str, Any]]) -> None:
        """
        Restore previously captured state to addon.

        Args:
            addon: BLOSM addon object
            state: State to restore (AddonState or dict)
        """
        try:
            if isinstance(state, AddonState):
                # Apply AddonState object directly
                state.apply_to_addon(addon)
                self.logger.info("State restored from AddonState object")
            else:
                # Apply legacy dictionary state
                for key, value in state.items():
                    setattr(addon, key, value)
                self.logger.info("State restored from dictionary")

        except Exception as e:
            self.logger.error(f"Failed to restore state: {e}")
            raise RouteStateError(f"State restoration failed: {e}")

    def create_tile_configuration(self, south: float, west: float, north: float, east: float,
                                   include_roads: bool, include_buildings: bool) -> TileConfiguration:
        """
        Create a tile configuration object.

        Args:
            south, west, north, east: Bounding box coordinates
            include_roads: Whether to include roads
            include_buildings: Whether to include buildings

        Returns:
            TileConfiguration object
        """
        return TileConfiguration(
            south=south,
            west=west,
            north=north,
            east=east,
            include_roads=include_roads,
            include_buildings=include_buildings
        )

    def validate_tile_bounds(self, south: float, west: float, north: float, east: float) -> bool:
        """
        Validate tile bounds for consistency.

        Args:
            south, west, north, east: Bounding box coordinates

        Returns:
            True if bounds are valid, False otherwise
        """
        # Basic validation - check if bounds form a valid box
        if south >= north or west >= east:
            self.logger.warning(f"Invalid tile bounds: south={south}, west={west}, north={north}, east={east}")
            return False

        return True