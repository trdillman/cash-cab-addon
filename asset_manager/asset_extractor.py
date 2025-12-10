"""
Live Asset Development System - Asset Extraction

Extract CashCab assets from any blend file saved to assets folder.
Enables flexible asset development where users can save working files
and have them automatically available for new route imports.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import bpy

from .schema import AssetType


class AssetExtractionError(Exception):
    """Raised when asset extraction fails"""
    pass


class AssetValidationError(Exception):
    """Raised when asset validation fails"""
    pass


class AssetExtractor:
    """Extract and validate CashCab assets from any blend file"""

    # Asset recognition patterns
    ASSET_PATTERNS = {
        'objects': re.compile(r'^ASSET_.*$', re.IGNORECASE),
        'collections': re.compile(r'^ASSET_.*$', re.IGNORECASE),
        'materials': [
            re.compile(r'^ASSET_.*$', re.IGNORECASE),
            re.compile(r'^RouteLine$', re.IGNORECASE),
            re.compile(r'^UniversalShader.*$', re.IGNORECASE),
            re.compile(r'^RoadUnified$', re.IGNORECASE),
        ],
        'node_groups': [
            re.compile(r'^ASSET_.*$', re.IGNORECASE),
            re.compile(r'^route.*$', re.IGNORECASE),
            re.compile(r'^build.*$', re.IGNORECASE),
            re.compile(r'.*RouteTrace.*$', re.IGNORECASE),
            re.compile(r'.*BuildingGeoNodes.*$', re.IGNORECASE),
            re.compile(r'.*BASE_.*$', re.IGNORECASE),
        ],
        'custom_properties': re.compile(r'^cashcab_.*$', re.IGNORECASE)
    }

    # Renderer-specific assets that need to be extracted
    RENDERER_PATTERNS = {
        'objects': [
            re.compile(r'^profile_.*$', re.IGNORECASE),  # Way profile curves
            re.compile(r'^way_.*$', re.IGNORECASE),      # Way-related assets
        ],
        'curves': [
            re.compile(r'^profile_.*$', re.IGNORECASE),  # Way profile curves
            re.compile(r'^way_.*$', re.IGNORECASE),      # Way-related curves
        ]
    }

    # Required core assets for a complete CashCab setup
    # Using flexible keyword matching for better compatibility
    REQUIRED_ASSETS = {
        'objects': {'car', 'roads'},  # Keywords to match
        'collections': {'car', 'route', 'buildings'},  # Keywords to match
        'materials': {'routeline', 'route'},  # Keywords to match
        'node_groups': {'routetrace', 'building', 'route', 'build'}  # Keywords to match
    }

    def __init__(self):
        self.extraction_log: List[str] = []

    def scan_assets_folder(self, assets_dir: Optional[Path] = None) -> List[Path]:
        """Scan assets folder for blend files containing CashCab assets

        Args:
            assets_dir: Path to assets directory, defaults to addon assets folder

        Returns:
            List of blend file paths containing CashCab assets
        """
        if assets_dir is None:
            assets_dir = Path(__file__).resolve().parent.parent / "assets"

        if not assets_dir.exists():
            self.extraction_log.append(f"Assets directory not found: {assets_dir}")
            return []

        blend_files = list(assets_dir.glob("*.blend"))
        candidate_files = []

        for blend_file in blend_files:
            try:
                if self._contains_cashcab_assets(blend_file):
                    candidate_files.append(blend_file)
                    self.extraction_log.append(f"Found CashCab assets in: {blend_file.name}")
            except Exception as e:
                self.extraction_log.append(f"Error scanning {blend_file.name}: {e}")

        # Sort by modification time (newest first)
        candidate_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return candidate_files

    def _contains_cashcab_assets(self, blend_file: Path) -> bool:
        """Quick check if blend file contains any CashCab assets"""
        try:
            with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
                # Check for ASSET_ prefixed objects
                if any(self.ASSET_PATTERNS['objects'].match(obj_name)
                      for obj_name in data_from.objects):
                    return True

                # Check for ASSET_ prefixed collections
                if any(self.ASSET_PATTERNS['collections'].match(col_name)
                      for col_name in data_from.collections):
                    return True

                # Check for CashCab materials
                for mat_name in data_from.materials:
                    if any(pattern.match(mat_name) for pattern in self.ASSET_PATTERNS['materials']):
                        return True

                # Check for relevant node groups
                for ng_name in data_from.node_groups:
                    if any(pattern.match(ng_name) for pattern in self.ASSET_PATTERNS['node_groups']):
                        return True

                # Check for renderer assets (way profiles, etc.)
                for obj_name in data_from.objects:
                    if any(pattern.match(obj_name) for pattern in self.RENDERER_PATTERNS['objects']):
                        return True

                for curve_name in getattr(data_from, 'curves', []):
                    if any(pattern.match(curve_name) for pattern in self.RENDERER_PATTERNS['curves']):
                        return True

        except Exception as e:
            self.extraction_log.append(f"Error checking {blend_file.name}: {e}")

        return False

    def extract_all_assets(self, blend_file: Path) -> Dict[str, Any]:
        """Extract all CashCab assets from blend file

        Args:
            blend_file: Path to blend file containing assets

        Returns:
            Dictionary containing extracted assets by type

        Raises:
            AssetExtractionError: If extraction fails
        """
        if not blend_file.exists():
            raise AssetExtractionError(f"Blend file not found: {blend_file}")

        self.extraction_log.append(f"Extracting assets from: {blend_file.name}")

        try:
            extracted_assets = {
                'objects': self._extract_objects(blend_file),
                'collections': self._extract_collections(blend_file),
                'materials': self._extract_materials(blend_file),
                'node_groups': self._extract_node_groups(blend_file),
                'curves': self._extract_curves(blend_file),  # Add curves for renderer assets
                'worlds': self._extract_worlds(blend_file),
                'lights': self._extract_lights(blend_file)
            }

            # Log extraction summary
            for asset_type, assets in extracted_assets.items():
                if assets:
                    self.extraction_log.append(f"  {asset_type}: {len(assets)} extracted")

            return extracted_assets

        except Exception as e:
            raise AssetExtractionError(f"Failed to extract assets from {blend_file.name}: {e}")

    def _extract_objects(self, blend_file: Path) -> List[str]:
        """Extract CashCab objects from blend file"""
        objects_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            # Find ASSET_ prefixed objects
            for obj_name in data_from.objects:
                if self.ASSET_PATTERNS['objects'].match(obj_name):
                    objects_to_extract.append(obj_name)

            # Also check for objects with CashCab custom properties
            # This requires more detailed inspection which we'll do separately

            data_to.objects = objects_to_extract

        # Return just the names for consistency with other extraction methods
        return objects_to_extract

    def _extract_curves(self, blend_file: Path) -> List[str]:
        """Extract CashCab curves from blend file (includes renderer assets)"""
        curves_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            # Extract ASSET_ prefixed curves
            for curve_name in getattr(data_from, 'curves', []):
                if self.ASSET_PATTERNS['objects'].match(curve_name):
                    curves_to_extract.append(curve_name)

            # Extract renderer-specific curves (way profiles, etc.)
            for curve_name in getattr(data_from, 'curves', []):
                if any(pattern.match(curve_name) for pattern in self.RENDERER_PATTERNS['curves']):
                    curves_to_extract.append(curve_name)

            data_to.curves = curves_to_extract

        return curves_to_extract

    def _extract_collections(self, blend_file: Path) -> List[str]:
        """Extract CashCab collections from blend file"""
        collections_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            for col_name in data_from.collections:
                if self.ASSET_PATTERNS['collections'].match(col_name):
                    collections_to_extract.append(col_name)

            data_to.collections = collections_to_extract

        return collections_to_extract

    def _extract_materials(self, blend_file: Path) -> List[str]:
        """Extract CashCab materials from blend file"""
        materials_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            for mat_name in data_from.materials:
                if any(pattern.match(mat_name) for pattern in self.ASSET_PATTERNS['materials']):
                    materials_to_extract.append(mat_name)

            data_to.materials = materials_to_extract

        return materials_to_extract

    def _extract_node_groups(self, blend_file: Path) -> List[str]:
        """Extract CashCab node groups from blend file"""
        node_groups_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            for ng_name in data_from.node_groups:
                if any(pattern.match(ng_name) for pattern in self.ASSET_PATTERNS['node_groups']):
                    node_groups_to_extract.append(ng_name)

            data_to.node_groups = node_groups_to_extract

        return node_groups_to_extract

    def _extract_worlds(self, blend_file: Path) -> List[str]:
        """Extract world settings from blend file"""
        worlds_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            for world_name in data_from.worlds:
                # Extract worlds that might be used by CashCab assets
                # For now, extract all worlds (there are usually few)
                if world_name:  # Non-empty name
                    worlds_to_extract.append(world_name)

            data_to.worlds = worlds_to_extract

        return worlds_to_extract

    def _extract_lights(self, blend_file: Path) -> List[str]:
        """Extract light objects from blend file"""
        lights_to_extract = []

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            for obj_name in data_from.objects:
                # Check if object is a light and might be part of CashCab setup
                # We'll extract lights that are in ASSET_ collections
                if obj_name:  # Non-empty name
                    lights_to_extract.append(obj_name)

            # Filter for actual lights after loading
            data_to.objects = lights_to_extract

        # Post-process to filter actual lights
        actual_lights = []
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT' and obj.name in lights_to_extract:
                actual_lights.append(obj.name)

        return actual_lights

    def validate_asset_completeness(self, extracted_assets: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that extracted assets contain all required components

        Args:
            extracted_assets: Dictionary of extracted assets by type

        Returns:
            Tuple of (is_valid, list_of_missing_assets)
        """
        missing_assets = []

        for asset_type, required_keywords in self.REQUIRED_ASSETS.items():
            if asset_type not in extracted_assets:
                missing_assets.extend(f"{asset_type}: {', '.join(required_keywords)}")
                continue

            # Convert to lowercase for case-insensitive matching
            # Handle both string names and Blender objects
            extracted_names = []
            for item in extracted_assets[asset_type]:
                if hasattr(item, 'name'):
                    # Blender object (has .name attribute)
                    extracted_names.append(item.name.lower())
                elif isinstance(item, str):
                    # String name
                    extracted_names.append(item.lower())
                else:
                    # Other type, convert to string
                    extracted_names.append(str(item).lower())

            # Check if any extracted asset contains each required keyword
            missing_keywords = []
            for keyword in required_keywords:
                keyword_lower = keyword.lower()
                found = any(keyword_lower in name for name in extracted_names)
                if not found:
                    missing_keywords.append(keyword)

            if missing_keywords:
                missing_assets.append(f"{asset_type}: keywords '{', '.join(missing_keywords)}' not found")

        # Log validation results
        if missing_assets:
            self.extraction_log.append(f"Validation failed - missing: {'; '.join(missing_assets)}")
            return False, missing_assets
        else:
            self.extraction_log.append("Asset validation passed - all required assets present")
            return True, []

    def get_extraction_log(self) -> List[str]:
        """Get detailed extraction log for debugging"""
        return self.extraction_log.copy()

    def clear_extraction_log(self):
        """Clear the extraction log"""
        self.extraction_log.clear()


def find_best_asset_source(assets_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the best blend file containing CashCab assets

    Args:
        assets_dir: Path to assets directory

    Returns:
        Path to best asset source file, or None if not found
    """
    extractor = AssetExtractor()
    candidate_files = extractor.scan_assets_folder(assets_dir)

    if not candidate_files:
        return None

    # Return the most recently modified file
    return candidate_files[0]


def validate_and_extract_assets(blend_file: Path) -> Optional[Dict[str, Any]]:
    """Convenience function to validate and extract assets from a blend file

    Args:
        blend_file: Path to blend file

    Returns:
        Extracted assets dictionary, or None if validation fails
    """
    extractor = AssetExtractor()

    try:
        extracted_assets = extractor.extract_all_assets(blend_file)
        is_valid, missing = extractor.validate_asset_completeness(extracted_assets)

        if is_valid:
            return extracted_assets
        else:
            print(f"[AssetExtractor] Validation failed for {blend_file.name}: {missing}")
            return None

    except AssetExtractionError as e:
        print(f"[AssetExtractor] Extraction failed for {blend_file.name}: {e}")
        return None
    except Exception as e:
        print(f"[AssetExtractor] Unexpected error with {blend_file.name}: {e}")
        return None