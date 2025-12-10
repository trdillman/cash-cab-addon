"""
Single File Asset Loader for BLOSM Asset Manager

Provides functionality to load assets from single blend files for the renderer.
This is particularly useful for live asset development and testing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any, List
import bpy

from .asset_extractor import AssetExtractor, find_best_asset_source


def get_live_asset_for_renderer(asset_type: str, assets_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Get live assets from the most recent blend file for renderer use

    Args:
        asset_type: Type of asset to load (e.g., 'roads', 'buildings', 'car')
        assets_dir: Directory containing asset blend files

    Returns:
        Dictionary containing extracted assets, or None if no suitable file found
    """
    try:
        # Find the best asset source file
        asset_file = find_best_asset_source(assets_dir)
        if not asset_file:
            print(f"[SingleFileLoader] No suitable asset file found for type: {asset_type}")
            return None

        # Extract assets from the file
        extractor = AssetExtractor()
        extracted_assets = extractor.extract_all_assets(asset_file)

        # Validate that we have the required assets
        is_valid, missing = extractor.validate_asset_completeness(extracted_assets)
        if not is_valid:
            print(f"[SingleFileLoader] Asset validation failed: {missing}")
            return None

        print(f"[SingleFileLoader] Successfully loaded live assets from {asset_file.name}")
        return extracted_assets

    except Exception as e:
        print(f"[SingleFileLoader] Error loading live assets: {e}")
        return None


class SingleFileAssetLoader:
    """Load and manage assets from a single blend file

    This class provides a clean interface for loading CashCab assets
    from a single blend file, useful for development and testing.
    """

    def __init__(self, blend_file_path: Optional[Path] = None):
        """Initialize the single file asset loader

        Args:
            blend_file_path: Path to the blend file containing assets.
                           If None, will search for the best candidate.
        """
        self.blend_file_path = blend_file_path
        self.extractor = AssetExtractor()
        self.cached_assets: Optional[Dict[str, Any]] = None

    def set_asset_file(self, blend_file_path: Path) -> None:
        """Set the blend file to load assets from

        Args:
            blend_file_path: Path to the blend file containing assets
        """
        self.blend_file_path = blend_file_path
        self.cached_assets = None  # Clear cache

    def load_assets(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Load assets from the configured blend file

        Args:
            force_reload: If True, reload assets even if cached

        Returns:
            Dictionary containing extracted assets by type, or None if loading failed
        """
        if self.cached_assets is not None and not force_reload:
            return self.cached_assets

        # Determine which file to load from
        asset_file = self.blend_file_path
        if asset_file is None:
            asset_file = find_best_asset_source()

        if asset_file is None:
            print("[SingleFileAssetLoader] No asset file available")
            return None

        try:
            # Extract assets
            extracted_assets = self.extractor.extract_all_assets(asset_file)

            # Validate completeness
            is_valid, missing = self.extractor.validate_asset_completeness(extracted_assets)
            if not is_valid:
                print(f"[SingleFileAssetLoader] Asset validation failed: {missing}")
                return None

            self.cached_assets = extracted_assets
            print(f"[SingleFileAssetLoader] Successfully loaded assets from {asset_file.name}")
            return extracted_assets

        except Exception as e:
            print(f"[SingleFileAssetLoader] Failed to load assets: {e}")
            return None

    def get_objects(self) -> List[Any]:
        """Get loaded objects"""
        assets = self.load_assets()
        return assets.get('objects', []) if assets else []

    def get_collections(self) -> List[Any]:
        """Get loaded collections"""
        assets = self.load_assets()
        return assets.get('collections', []) if assets else []

    def get_materials(self) -> List[Any]:
        """Get loaded materials"""
        assets = self.load_assets()
        return assets.get('materials', []) if assets else []

    def get_node_groups(self) -> List[Any]:
        """Get loaded node groups"""
        assets = self.load_assets()
        return assets.get('node_groups', []) if assets else []

    def get_curves(self) -> List[Any]:
        """Get loaded curves"""
        assets = self.load_assets()
        return assets.get('curves', []) if assets else []

    def is_valid(self) -> bool:
        """Check if the current asset file is valid and complete"""
        assets = self.load_assets()
        if not assets:
            return False

        is_valid, _ = self.extractor.validate_asset_completeness(assets)
        return is_valid

    def get_extraction_log(self) -> List[str]:
        """Get detailed extraction log for debugging"""
        return self.extractor.get_extraction_log()

    def clear_cache(self) -> None:
        """Clear the cached assets"""
        self.cached_assets = None