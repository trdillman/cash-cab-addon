"""
Asset Manager Module for BLOSM (CashCab)

Provides centralized asset configuration and management via JSON files.
Replaces hardcoded asset values with configurable definitions.

Phase 1: Basic registry system for car asset configuration
"""

from .registry import AssetRegistry
from .schema import AssetDefinition, TransformData, AssetType
from .loader import spawn_asset_by_id
from .simple_asset_updater import SimpleAssetUpdater
from .asset_file_manager import AssetFileManager
from .asset_safety import AssetSafety

__all__ = [
    'AssetRegistry',
    'AssetDefinition',
    'TransformData',
    'AssetType',
    'spawn_asset_by_id',
    'SimpleAssetUpdater',
    'AssetFileManager',
    'AssetSafety',
]

# Module-level registry instance
registry = AssetRegistry()

def register():
    """Register the asset manager module with Blender"""
    # Phase 1: No Blender registration needed, just Python module
    pass

def unregister():
    """Unregister the asset manager module"""
    # Phase 1: No cleanup needed
    pass
