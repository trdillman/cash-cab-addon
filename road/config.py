"""
Road Processor Configuration
Centralized configuration for road processing workflows
"""

import logging
from typing import Dict, List, Set, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

log = logging.getLogger(__name__)

class RoadCategory(Enum):
    """Road categorization for processing priority"""
    MAJOR_HIGHWAY = "major_highway"
    SECONDARY_ROAD = "secondary_road"
    LOCAL_ROAD = "local_road"
    SERVICE_ROAD = "service_road"
    SPECIAL_ROAD = "special_road"

# Road type classifications
ROAD_TYPES = {
    'motorway': RoadCategory.MAJOR_HIGHWAY,
    'trunk': RoadCategory.MAJOR_HIGHWAY,
    'primary': RoadCategory.MAJOR_HIGHWAY,
    'secondary': RoadCategory.SECONDARY_ROAD,
    'tertiary': RoadCategory.SECONDARY_ROAD,
    'unclassified': RoadCategory.LOCAL_ROAD,
    'residential': RoadCategory.LOCAL_ROAD,
    'service': RoadCategory.SERVICE_ROAD,
    'track': RoadCategory.LOCAL_ROAD,
    'footway': RoadCategory.SPECIAL_ROAD,
    'cycleway': RoadCategory.SPECIAL_ROAD,
    'path': RoadCategory.SPECIAL_ROAD,
    'pedestrian': RoadCategory.SPECIAL_ROAD,
    'living_street': RoadCategory.LOCAL_ROAD,
    'road': RoadCategory.LOCAL_ROAD  # Unclassified road
}

# Highway tag hierarchy (for filtering)
HIGHWAY_TYPES = {
    'motorway': {'priority': 1, 'min_width': 8.0, 'max_width': 12.0},
    'motorway_link': {'priority': 2, 'min_width': 6.0, 'max_width': 8.0},
    'trunk': {'priority': 3, 'min_width': 6.0, 'max_width': 10.0},
    'trunk_link': {'priority': 4, 'min_width': 5.0, 'max_width': 8.0},
    'primary': {'priority': 5, 'min_width': 4.0, 'max_width': 8.0},
    'primary_link': {'priority': 6, 'min_width': 4.0, 'max_width': 6.0},
    'secondary': {'priority': 7, 'min_width': 3.0, 'max_width': 6.0},
    'secondary_link': {'priority': 8, 'min_width': 3.0, 'max_width': 5.0},
    'tertiary': {'priority': 9, 'min_width': 2.5, 'max_width': 5.0},
    'tertiary_link': {'priority': 10, 'min_width': 2.5, 'max_width': 4.0},
    'unclassified': {'priority': 11, 'min_width': 2.0, 'max_width': 4.0},
    'residential': {'priority': 12, 'min_width': 2.0, 'max_width': 4.0},
    'living_street': {'priority': 13, 'min_width': 1.5, 'max_width': 3.0},
    'service': {'priority': 14, 'min_width': 1.5, 'max_width': 3.0},
    'track': {'priority': 15, 'min_width': 1.0, 'max_width': 2.0},
    'footway': {'priority': 16, 'min_width': 0.5, 'max_width': 1.5},
    'cycleway': {'priority': 17, 'min_width': 1.0, 'max_width': 2.0},
    'path': {'priority': 18, 'min_width': 0.5, 'max_width': 1.5},
    'pedestrian': {'priority': 19, 'min_width': 2.0, 'max_width': 4.0},
    'road': {'priority': 20, 'min_width': 2.0, 'max_width': 4.0}
}

# Default road widths (meters)
ROAD_WIDTHS = {
    'motorway': 10.0,
    'trunk': 8.0,
    'primary': 6.0,
    'secondary': 4.0,
    'tertiary': 3.0,
    'unclassified': 2.5,
    'residential': 2.5,
    'service': 2.0,
    'track': 1.5,
    'footway': 1.0,
    'cycleway': 1.5,
    'path': 1.0,
    'pedestrian': 3.0,
    'living_street': 2.0,
    'road': 2.5
}

# Road category mapping
ROAD_CATEGORIES = {
    RoadCategory.MAJOR_HIGHWAY: ['motorway', 'trunk', 'primary'],
    RoadCategory.SECONDARY_ROAD: ['secondary', 'tertiary'],
    RoadCategory.LOCAL_ROAD: ['unclassified', 'residential', 'living_street', 'road'],
    RoadCategory.SERVICE_ROAD: ['service', 'track'],
    RoadCategory.SPECIAL_ROAD: ['footway', 'cycleway', 'path', 'pedestrian']
}

# Processing priority (lower number = higher priority)
ROAD_PRIORITY = {
    RoadCategory.MAJOR_HIGHWAY: 1,
    RoadCategory.SECONDARY_ROAD: 2,
    RoadCategory.LOCAL_ROAD: 3,
    RoadCategory.SERVICE_ROAD: 4,
    RoadCategory.SPECIAL_ROAD: 5
}

# Layer material configurations
LAYER_MATERIALS = {
    'base': {
        'roughness': 0.8,
        'metallic': 0.0,
        'specular': 0.1,
        'color': (0.2, 0.2, 0.2, 1.0)  # Dark gray
    },
    'markings': {
        'roughness': 0.3,
        'metallic': 0.0,
        'specular': 0.5,
        'color': (1.0, 1.0, 1.0, 1.0)  # White
    },
    'sidewalk': {
        'roughness': 0.9,
        'metallic': 0.0,
        'specular': 0.1,
        'color': (0.4, 0.4, 0.4, 1.0)  # Light gray
    }
}

@dataclass
class RoadProcessorConfig:
    """Configuration for road processing workflow"""

    # Filtering options
    enable_road_filtering: bool = True
    min_road_width: float = 1.0
    max_road_width: float = 12.0
    excluded_highway_types: Set[str] = field(default_factory=lambda: {
        'proposed', 'construction', 'abandoned', 'razed', 'removed'
    })

    # Geometry processing
    curve_resolution: int = 12  # Bezier curve resolution
    curve_smoothness: float = 0.8  # Curve smoothness factor
    mesh_bevel_depth: float = 0.1  # Bevel depth for road edges
    simplify_geometry: bool = True
    simplification_threshold: float = 0.5

    # Material settings
    create_materials: bool = True
    material_naming_convention: str = "Road_{type}"
    use_layered_materials: bool = True
    generate_road_markings: bool = True

    # Processing options
    process_categories: List[RoadCategory] = field(default_factory=lambda: [
        RoadCategory.MAJOR_HIGHWAY,
        RoadCategory.SECONDARY_ROAD,
        RoadCategory.LOCAL_ROAD
    ])
    batch_processing: bool = True
    batch_size: int = 50
    parallel_processing: bool = True
    max_workers: int = 4

    # Performance settings
    enable_progress_callback: bool = True
    progress_update_interval: int = 10
    memory_optimization: bool = True
    cleanup_intermediate_data: bool = True

    # Quality settings
    quality_level: str = "medium"  # low, medium, high, ultra

    # Object organization
    organize_by_type: bool = True
    create_road_collections: bool = True
    collection_naming: str = "Roads_{category}"

    # Validation
    validate_geometry: bool = True
    repair_invalid_geometry: bool = True

    def __post_init__(self):
        """Validate and adjust configuration after initialization"""
        self._validate_config()
        self._adjust_for_quality_level()

    def _validate_config(self):
        """Validate configuration parameters"""
        if self.min_road_width < 0 or self.max_road_width < self.min_road_width:
            raise ValueError("Invalid road width configuration")

        if self.curve_resolution < 3 or self.curve_resolution > 64:
            log.warning(f"Curve resolution {self.curve_resolution} may be suboptimal")

        if self.max_workers < 1:
            self.max_workers = 1
            log.warning("Max workers set to minimum value of 1")

    def _adjust_for_quality_level(self):
        """Adjust settings based on quality level"""
        quality_settings = {
            "low": {
                "curve_resolution": 6,
                "simplify_geometry": True,
                "simplification_threshold": 1.0,
                "generate_road_markings": False,
                "batch_size": 100
            },
            "medium": {
                "curve_resolution": 12,
                "simplify_geometry": True,
                "simplification_threshold": 0.5,
                "generate_road_markings": True,
                "batch_size": 50
            },
            "high": {
                "curve_resolution": 24,
                "simplify_geometry": False,
                "simplification_threshold": 0.2,
                "generate_road_markings": True,
                "batch_size": 25
            },
            "ultra": {
                "curve_resolution": 48,
                "simplify_geometry": False,
                "simplification_threshold": 0.1,
                "generate_road_markings": True,
                "batch_size": 10
            }
        }

        if self.quality_level in quality_settings:
            settings = quality_settings[self.quality_level]
            for key, value in settings.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def get_road_width(self, highway_type: str) -> float:
        """Get configured width for a specific highway type"""
        return ROAD_WIDTHS.get(highway_type, self.min_road_width)

    def should_process_road(self, highway_type: str, width: float) -> bool:
        """Check if a road should be processed based on configuration"""
        if not self.enable_road_filtering:
            return True

        if highway_type in self.excluded_highway_types:
            return False

        if width < self.min_road_width or width > self.max_road_width:
            return False

        return True

    def get_category_priority(self, category: RoadCategory) -> int:
        """Get processing priority for a road category"""
        return ROAD_PRIORITY.get(category, 999)

    def get_material_config(self, layer_type: str) -> Dict[str, Any]:
        """Get material configuration for a specific layer"""
        return LAYER_MATERIALS.get(layer_type, LAYER_MATERIALS['base'])

# Simple configuration for test compatibility (from test requirements)
AUTO_ADAPT_ROADS = True
KEEP_ROADS_VISIBLE = True
UNIFIED_ROAD_MATERIAL_NAME = "RoadUnified"
ROAD_COLLECTION_NAME = "ASSET_ROADS"
KEEP_ORIGINAL_CURVES = False
ROAD_MESH_RESOLUTION = 0.01