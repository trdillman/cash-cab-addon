"""
Road Detection Module
Handles detection, classification, and filtering of OSM road data
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

from .config import (
    RoadProcessorConfig,
    RoadCategory,
    ROAD_TYPES,
    HIGHWAY_TYPES,
    ROAD_WIDTHS
)
from .processor import RoadSegment

log = logging.getLogger(__name__)

class RoadDetector:
    """Detects and classifies road segments from OSM data"""

    def __init__(self, config: RoadProcessorConfig):
        """
        Initialize road detector

        Args:
            config: Road processor configuration
        """
        self.config = config

        # Cache for node coordinates
        self._node_cache = {}

        # Statistics
        self._stats = {
            'total_ways': 0,
            'filtered_ways': 0,
            'road_segments': 0,
            'by_category': defaultdict(int),
            'by_highway_type': defaultdict(int)
        }

    def detect_road_segments(self, osm_data: Dict) -> List[RoadSegment]:
        """
        Detect and classify road segments from OSM data

        Args:
            osm_data: OSM data dictionary containing ways and nodes

        Returns:
            List of classified road segments
        """
        self._reset_stats()

        try:
            # Extract nodes and ways
            nodes = osm_data.get('nodes', {})
            ways = osm_data.get('ways', {})

            if not nodes or not ways:
                log.warning("No nodes or ways found in OSM data")
                return []

            log.info(f"Processing {len(ways)} ways with {len(nodes)} nodes")

            # Cache node coordinates for faster access
            self._cache_nodes(nodes)

            # Detect road segments
            segments = []
            for way_id, way_data in ways.items():
                try:
                    segment = self._process_way(way_id, way_data)
                    if segment:
                        segments.append(segment)
                        self._update_stats(segment)
                except Exception as e:
                    log.warning(f"Failed to process way {way_id}: {str(e)}")
                    continue

            # Sort segments by priority
            segments.sort(key=lambda s: s.priority)

            log.info(f"Detected {len(segments)} road segments")
            self._log_statistics()

            return segments

        except Exception as e:
            log.error(f"Road detection failed: {str(e)}")
            return []

    def _reset_stats(self):
        """Reset detection statistics"""
        self._stats = {
            'total_ways': 0,
            'filtered_ways': 0,
            'road_segments': 0,
            'by_category': defaultdict(int),
            'by_highway_type': defaultdict(int)
        }

    def _cache_nodes(self, nodes: Dict):
        """Cache node coordinates for faster access"""
        self._node_cache.clear()
        for node_id, node_data in nodes.items():
            if 'lat' in node_data and 'lon' in node_data:
                self._node_cache[node_id] = (node_data['lat'], node_data['lon'])

    def _process_way(self, way_id: str, way_data: Dict) -> Optional[RoadSegment]:
        """
        Process a single OSM way to create a road segment

        Args:
            way_id: OSM way ID
            way_data: Way data dictionary

        Returns:
            RoadSegment or None if way is not a road
        """
        self._stats['total_ways'] += 1

        # Check if way has highway tag
        tags = way_data.get('tags', {})
        highway_type = tags.get('highway')

        if not highway_type:
            return None

        # Check if highway type should be processed
        if not self._should_process_highway_type(highway_type):
            self._stats['filtered_ways'] += 1
            return None

        # Get way nodes
        way_nodes = way_data.get('nodes', [])
        if len(way_nodes) < 2:
            log.debug(f"Way {way_id} has insufficient nodes: {len(way_nodes)}")
            return None

        # Build coordinate list
        coordinates = self._build_coordinates(way_nodes)
        if not coordinates:
            log.debug(f"Way {way_id} has no valid coordinates")
            return None

        # Determine road category and width
        category = self._get_road_category(highway_type)
        width = self._get_road_width(highway_type, tags)

        # Validate against configuration
        if not self.config.should_process_road(highway_type, width):
            self._stats['filtered_ways'] += 1
            return None

        # Calculate priority
        priority = self._get_priority(highway_type, category)

        # Create segment
        segment = RoadSegment(
            osm_id=way_id,
            highway_type=highway_type,
            category=category,
            coordinates=coordinates,
            width=width,
            name=tags.get('name'),
            tags=tags,
            priority=priority
        )

        return segment

    def _should_process_highway_type(self, highway_type: str) -> bool:
        """Check if highway type should be processed"""
        # Skip excluded types
        if highway_type in self.config.excluded_highway_types:
            return False

        # Check if type is recognized
        if highway_type not in ROAD_TYPES:
            log.debug(f"Unknown highway type: {highway_type}")
            return False

        # Check if category should be processed
        category = ROAD_TYPES[highway_type]
        if category not in self.config.process_categories:
            return False

        return True

    def _build_coordinates(self, way_nodes: List[str]) -> List[Tuple[float, float]]:
        """
        Build coordinate list from way nodes

        Args:
            way_nodes: List of node IDs

        Returns:
            List of (lat, lon) coordinate tuples
        """
        coordinates = []
        missing_nodes = 0

        for node_id in way_nodes:
            if node_id in self._node_cache:
                coordinates.append(self._node_cache[node_id])
            else:
                missing_nodes += 1

        if missing_nodes > 0:
            log.debug(f"Missing {missing_nodes} nodes for way")

        # Filter out duplicate consecutive coordinates
        filtered_coords = []
        for i, coord in enumerate(coordinates):
            if i == 0 or coord != coordinates[i-1]:
                filtered_coords.append(coord)

        return filtered_coords

    def _get_road_category(self, highway_type: str) -> RoadCategory:
        """Get road category for highway type"""
        return ROAD_TYPES.get(highway_type, RoadCategory.LOCAL_ROAD)

    def _get_road_width(self, highway_type: str, tags: Dict) -> float:
        """
        Get road width from tags or use default

        Args:
            highway_type: OSM highway type
            tags: OSM tags dictionary

        Returns:
            Road width in meters
        """
        # Check for explicit width tag
        if 'width' in tags:
            try:
                width = float(tags['width'])
                if width > 0:
                    return width
            except (ValueError, TypeError):
                pass

        # Check for lane count
        if 'lanes' in tags:
            try:
                lanes = int(tags['lanes'])
                if lanes > 0:
                    # Estimate width based on lane count (3.5m per lane average)
                    base_width = lanes * 3.5
                    return max(base_width, self.config.min_road_width)
            except (ValueError, TypeError):
                pass

        # Use configured default
        return self.config.get_road_width(highway_type)

    def _get_priority(self, highway_type: str, category: RoadCategory) -> int:
        """Get processing priority for road"""
        # Start with category priority
        priority = HIGHWAY_TYPES.get(highway_type, {}).get('priority', 999)

        # Add category priority if available
        if hasattr(RoadCategory, 'value'):
            category_map = {
                RoadCategory.MAJOR_HIGHWAY: 1000,
                RoadCategory.SECONDARY_ROAD: 2000,
                RoadCategory.LOCAL_ROAD: 3000,
                RoadCategory.SERVICE_ROAD: 4000,
                RoadCategory.SPECIAL_ROAD: 5000
            }
            priority += category_map.get(category, 9999)

        return priority

    def _update_stats(self, segment: RoadSegment):
        """Update detection statistics"""
        self._stats['road_segments'] += 1
        self._stats['by_category'][segment.category] += 1
        self._stats['by_highway_type'][segment.highway_type] += 1

    def _log_statistics(self):
        """Log detection statistics"""
        log.info("Road Detection Statistics:")
        log.info(f"  Total ways: {self._stats['total_ways']}")
        log.info(f"  Filtered ways: {self._stats['filtered_ways']}")
        log.info(f"  Road segments: {self._stats['road_segments']}")

        if self._stats['by_category']:
            log.info("  By category:")
            for category, count in self._stats['by_category'].items():
                log.info(f"    {category.value}: {count}")

        if self._stats['by_highway_type']:
            log.info("  By highway type:")
            for highway_type, count in self._stats['by_highway_type'].items():
                log.info(f"    {highway_type}: {count}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return dict(self._stats)

    def validate_road_data(self, osm_data: Dict) -> Dict[str, Any]:
        """
        Validate OSM data for road processing

        Args:
            osm_data: OSM data dictionary

        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }

        try:
            # Check basic structure
            if not isinstance(osm_data, dict):
                validation['valid'] = False
                validation['errors'].append("OSM data must be a dictionary")
                return validation

            # Check for required sections
            if 'nodes' not in osm_data:
                validation['errors'].append("Missing 'nodes' section in OSM data")
                validation['valid'] = False

            if 'ways' not in osm_data:
                validation['errors'].append("Missing 'ways' section in OSM data")
                validation['valid'] = False

            if not validation['valid']:
                return validation

            # Analyze data
            nodes = osm_data.get('nodes', {})
            ways = osm_data.get('ways', {})

            validation['statistics'] = {
                'total_nodes': len(nodes),
                'total_ways': len(ways),
                'ways_with_highway_tag': 0,
                'highway_types': set(),
                'nodes_with_coordinates': 0
            }

            # Analyze nodes
            for node_id, node_data in nodes.items():
                if 'lat' in node_data and 'lon' in node_data:
                    validation['statistics']['nodes_with_coordinates'] += 1

            # Analyze ways
            for way_id, way_data in ways.items():
                tags = way_data.get('tags', {})
                if 'highway' in tags:
                    validation['statistics']['ways_with_highway_tag'] += 1
                    validation['statistics']['highway_types'].add(tags['highway'])

            # Add warnings for potential issues
            node_ratio = validation['statistics']['nodes_with_coordinates'] / len(nodes) if nodes else 0
            if node_ratio < 0.9:
                validation['warnings'].append(
                    f"Only {node_ratio:.1%} of nodes have coordinates"
                )

            highway_ratio = validation['statistics']['ways_with_highway_tag'] / len(ways) if ways else 0
            if highway_ratio == 0:
                validation['warnings'].append("No ways have highway tags")

        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Validation failed: {str(e)}")

        return validation