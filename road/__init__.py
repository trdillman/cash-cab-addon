"""
Road Processing Module for CashCab
Handles unified road object detection, processing, and mesh generation
"""

import bpy
from typing import Dict, List, Optional, Set, Any, Tuple
import logging

# Import simple functions for test compatibility
from .processor import (
    process_roads,
    get_road_objects,
    create_unified_material,
    create_roads_collection,
    convert_curve_to_mesh,
    join_road_objects
)

# Import configuration constants
from .config import (
    AUTO_ADAPT_ROADS,
    KEEP_ROADS_VISIBLE,
    UNIFIED_ROAD_MATERIAL_NAME,
    ROAD_COLLECTION_NAME,
    KEEP_ORIGINAL_CURVES,
    ROAD_MESH_RESOLUTION
)

# Module-level logger
log = logging.getLogger(__name__)

__all__ = [
    'process_roads',
    'get_road_objects',
    'create_unified_material',
    'create_roads_collection',
    'convert_curve_to_mesh',
    'join_road_objects',
    'AUTO_ADAPT_ROADS',
    'KEEP_ROADS_VISIBLE',
    'UNIFIED_ROAD_MATERIAL_NAME',
    'ROAD_COLLECTION_NAME',
    'KEEP_ORIGINAL_CURVES',
    'ROAD_MESH_RESOLUTION',
    'log'
]