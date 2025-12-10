"""
Validation utilities for BLOSM Asset Manager.

Provides functions to validate individual assets and entire registries
without requiring Blender to be available.
"""

from __future__ import annotations

from typing import Iterable, List

from .schema import AssetDefinition, AssetType, TransformData


def _is_number_triplet(value: Iterable[float]) -> bool:
    try:
        seq = list(value)
        if len(seq) != 3:
            return False
        # Accept ints or floats
        _ = [float(v) for v in seq]
        return True
    except Exception:
        return False


def validate_asset(asset: AssetDefinition) -> List[str]:
    """Validate a single ``AssetDefinition``.

    Returns a list of human-readable issues. An empty list means valid.
    """
    issues: List[str] = []

    if not asset.id or not isinstance(asset.id, str):
        issues.append("id must be a non-empty string")

    if not asset.name or not isinstance(asset.name, str):
        issues.append("name must be a non-empty string")

    if not isinstance(asset.type, AssetType):
        issues.append("type must be an AssetType value")

    if not asset.blend_file or not asset.blend_file.endswith('.blend'):
        issues.append("blend_file must end with .blend")

    if not asset.datablock_name:
        issues.append("datablock_name must be provided")

    dt: TransformData = asset.default_transform
    if not _is_number_triplet(dt.location):
        issues.append("default_transform.location must be a 3-number sequence")
    if not _is_number_triplet(dt.rotation_euler):
        issues.append("default_transform.rotation_euler must be a 3-number sequence")
    if not _is_number_triplet(dt.scale):
        issues.append("default_transform.scale must be a 3-number sequence")

    if not isinstance(asset.tags, list):
        issues.append("tags must be a list")

    if asset.collection_name is not None and not isinstance(asset.collection_name, str):
        issues.append("collection_name must be a string or None")

    if not isinstance(asset.hide_viewport, bool) or not isinstance(asset.hide_render, bool):
        issues.append("hide_viewport and hide_render must be booleans")

    if not isinstance(asset.properties, dict):
        issues.append("properties must be a dict")

    return issues


def validate_registry_assets(assets: Iterable[AssetDefinition]) -> List[str]:
    """Validate a collection of assets and check for duplicate IDs."""
    issues: List[str] = []
    seen = set()
    for asset in assets:
        if asset.id in seen:
            issues.append(f"duplicate asset id: {asset.id}")
        else:
            seen.add(asset.id)
        issues.extend([f"{asset.id}: {msg}" for msg in validate_asset(asset)])
    return issues

