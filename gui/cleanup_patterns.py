"""
BLOSM Cleanup Patterns
Configuration for identifying and cleaning addon objects
"""

from typing import Dict, List, Set


# Object name patterns that identify addon objects
OBJECT_PATTERNS: List[str] = [
    'Route', 'ROUTE', 'Start', 'End', 'Lead',
    'ASSET_CAR', 'Car', 'ASSET_', 'BUILDINGS', 'map_', 'way_',
    'profile_roads_', 'profile_paths_', 'BLOSM_', 'Dollar_', 'LOCATOR',
    'Cube.', 'Icosphere.', 'Mesh.', 'Sphere', '$GLOW', 'Base.',
    'BGS.', 'PIN', 'Metal', 'SIGN', 'standardSurface',
    'UnifiedRoadMesh', 'ASSET_ROADS'  # Added unified road mesh patterns
]

# Collection names that identify addon collections
COLLECTION_NAMES: Set[str] = {
    'ASSET_ROUTE', 'ASSET_BUILDINGS', 'BLOSM_Assets',
    'ASSET_BASE-START', 'ASSET_BASE-END', 'ASSET_CAR',
    'ASSET_WORLD', 'way_profiles', 'ASSET_ROADS',  # Added ASSET_ROADS collection
}

# Asset group definitions for related object cleanup
ASSET_GROUPS: Dict[str, List[str]] = {
    'car': ['ASSET_CAR', 'Car', 'Lead', 'LEAD', 'Cube.', 'Mesh.', 'Icosphere.'],
    'route': ['Route', 'ROUTE', 'Start', 'End'],
    'buildings': ['BUILDINGS', 'map_'],
    'markers': ['BASE-START', 'BASE-END', 'Dollar_', 'LOCATOR', 'Sphere'],
    'roads': ['profile_roads_', 'profile_paths_', 'UnifiedRoadMesh', 'ASSET_ROADS'],  # Added unified road mesh
    'assets': ['ASSET_', '$GLOW', 'Base.', 'BGS.', 'PIN', 'Metal', 'SIGN', 'standardSurface'],
}

# Material patterns for cleanup
MATERIAL_PATTERNS: List[str] = [
    'RouteLine', 'ASSET_', '$GLOW', 'Base.', 'BGS.', 'PIN', 'Metal',
    'SIGN', 'standardSurface', 'UniversalShader',
    'RoadUnified', 'RoadMaterial'  # Added road material patterns
]

# Node group patterns for cleanup
NODE_GROUP_PATTERNS: List[str] = [
    'ASSET_', 'ETK_', 'Motion', 'UNISHADER', 'Edges.', 'Shift/', 'NodeGroup.',
    'RoadNodes', 'RoadGeoNodes'  # Added road node group patterns
]

# Image patterns for cleanup
IMAGE_PATTERNS: List[str] = [
    'zwinger_', '.hdr'
]

# Text patterns for cleanup
TEXT_PATTERNS: List[str] = [
    'asset_attributes'
]

# World patterns for cleanup
WORLD_PATTERNS: List[str] = [
    'ASSET_WORLD'
]

# Library patterns for cleanup
LIBRARY_PATTERNS: List[str] = [
    'ASSET_', 'way_profiles'
]
