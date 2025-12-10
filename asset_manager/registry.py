"""
Asset Registry - Central configuration management for BLOSM assets

Handles loading, saving, and managing asset definitions via JSON configuration.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .schema import AssetDefinition, AssetType
from .errors import AssetValidationError
from .validation import validate_registry_assets


class AssetRegistry:
    """Central registry for all asset definitions"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the registry

        Args:
            config_path: Path to JSON config file. If None, uses default location.
        """
        if config_path is None:
            # Default to assets/asset_registry.json
            module_dir = Path(__file__).parent.parent
            config_path = module_dir / "assets" / "asset_registry.json"

        self.config_path = Path(config_path)
        self._assets: Dict[str, AssetDefinition] = {}
        self._assets_by_type: Dict[AssetType, List[str]] = {
            asset_type: [] for asset_type in AssetType
        }

        # Auto-load if config exists
        if self.config_path.exists():
            self.load()

    def load(self) -> None:
        """Load asset definitions from JSON config file"""
        if not self.config_path.exists():
            print(f"[AssetRegistry] Config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear existing assets
            self._assets.clear()
            for asset_type in AssetType:
                self._assets_by_type[asset_type] = []

            # Load assets from JSON
            for asset_data in data.get("assets", []):
                asset = AssetDefinition.from_dict(asset_data)
                self.register_asset(asset)

            print(f"[AssetRegistry] Loaded {len(self._assets)} assets from {self.config_path}")

        except json.JSONDecodeError as e:
            print(f"[AssetRegistry] Failed to parse JSON: {e}")
        except Exception as e:
            print(f"[AssetRegistry] Failed to load config: {e}")

    def save(self) -> None:
        """Save current asset definitions to JSON config file"""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert assets to JSON-serializable format
        assets_data = [asset.to_dict() for asset in self._assets.values()]

        data = {
            "version": "1.0.0",
            "assets": assets_data
        }

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            print(f"[AssetRegistry] Saved {len(self._assets)} assets to {self.config_path}")

        except Exception as e:
            print(f"[AssetRegistry] Failed to save config: {e}")

    def register_asset(self, asset: AssetDefinition) -> None:
        """Register an asset definition

        Args:
            asset: Asset definition to register
        """
        self._assets[asset.id] = asset

        # Update type index
        if asset.id not in self._assets_by_type[asset.type]:
            self._assets_by_type[asset.type].append(asset.id)

    def get_asset(self, asset_id: str) -> Optional[AssetDefinition]:
        """Get an asset by ID

        Args:
            asset_id: Unique asset identifier

        Returns:
            Asset definition or None if not found
        """
        return self._assets.get(asset_id)

    def get_assets_by_type(self, asset_type: AssetType) -> List[AssetDefinition]:
        """Get all assets of a specific type

        Args:
            asset_type: Type of assets to retrieve

        Returns:
            List of asset definitions
        """
        asset_ids = self._assets_by_type.get(asset_type, [])
        return [self._assets[aid] for aid in asset_ids if aid in self._assets]

    def get_car_asset(self) -> Optional[AssetDefinition]:
        """Get the default car asset

        Returns:
            Car asset definition or None if not found
        """
        cars = self.get_assets_by_type(AssetType.CAR)
        # Return first car or one tagged as default
        for car in cars:
            if "default" in car.tags:
                return car
        return cars[0] if cars else None

    def list_assets(self) -> List[str]:
        """List all registered asset IDs

        Returns:
            List of asset IDs
        """
        return list(self._assets.keys())

    def remove_asset(self, asset_id: str) -> bool:
        """Remove an asset from the registry

        Args:
            asset_id: ID of asset to remove

        Returns:
            True if removed, False if not found
        """
        if asset_id in self._assets:
            asset = self._assets[asset_id]
            del self._assets[asset_id]

            # Update type index
            if asset_id in self._assets_by_type[asset.type]:
                self._assets_by_type[asset.type].remove(asset_id)

            return True
        return False

    def clear(self) -> None:
        """Clear all registered assets"""
        self._assets.clear()
        for asset_type in AssetType:
            self._assets_by_type[asset_type] = []

    def validate(self, strict: bool = True) -> List[str]:
        """Validate the registry's asset definitions.

        Args:
            strict: If True, raise ``AssetValidationError`` when issues are found.

        Returns:
            List of issue strings (empty when valid).
        """
        issues = validate_registry_assets(self._assets.values())
        if issues and strict:
            raise AssetValidationError("; ".join(issues))
        return issues
