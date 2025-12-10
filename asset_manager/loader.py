"""
Blender asset loader utilities for BLOSM Asset Manager.

These helpers append or link datablocks from configured .blend files based on
AssetRegistry definitions. Importing this module outside Blender is safe; the
functions will raise a clear error if called without bpy available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple, List, Any

from .registry import AssetRegistry
from .schema import AssetDefinition, AssetType, TransformData


def _require_bpy():
    try:
        import bpy  # type: ignore
        return bpy
    except Exception as exc:
        raise RuntimeError(
            "Blender 'bpy' module is required for asset loading; "
            "run these functions inside Blender or provide a bpy context."
        ) from exc


def _resolve_library_path(asset: AssetDefinition) -> str:
    # Asset blend_file is stored relative to package assets folder.
    # Convert to absolute path using this file as reference.
    pkg_root = Path(__file__).resolve().parent.parent
    assets_dir = pkg_root / "assets"
    lib_path = (assets_dir / asset.blend_file).resolve()
    return str(lib_path)


def _append_or_link(
    asset: AssetDefinition,
    *,
    link: bool,
    bpy: Optional[Any] = None,
) -> Tuple[List[Any], str]:
    """Append or link matching datablocks by name across supported categories.

    Returns (created_items, category) where category is one of
    'objects', 'collections', 'materials', 'node_groups'.
    """
    if bpy is None:
        bpy = _require_bpy()

    lib = _resolve_library_path(asset)
    name = asset.datablock_name

    # Choose category search order based on declared AssetType so that
    # collection assets (like ASSET_CAR) resolve to collections first,
    # materials to materials, etc., while still allowing a graceful
    # fallback to other categories if the registry entry and file
    # contents drift.
    base_categories = [
        ("objects", "objects"),
        ("collections", "collections"),
        ("materials", "materials"),
        ("node_groups", "node_groups"),
        ("worlds", "worlds"),
    ]

    preferred_attr = "objects"
    if asset.type == AssetType.COLLECTION:
        preferred_attr = "collections"
    elif asset.type == AssetType.MATERIAL:
        preferred_attr = "materials"
    elif asset.type == AssetType.NODE_GROUP:
        preferred_attr = "node_groups"
    elif asset.type == AssetType.WORLD:
        preferred_attr = "worlds"

    categories = sorted(
        base_categories,
        key=lambda pair: 0 if pair[0] == preferred_attr else 1,
    )

    for cat_attr, cat_label in categories:
        with bpy.data.libraries.load(lib, link=link) as (data_from, data_to):  # type: ignore
            names: Iterable[str] = getattr(data_from, cat_attr, [])
            if name in names:
                setattr(data_to, cat_attr, [name])
        # After context, the datablock is loaded if name existed
        coll = getattr(bpy.data, cat_attr)
        if name in coll:
            return [coll[name]], cat_label

    raise FileNotFoundError(
        f"Datablock '{name}' not found in '{lib}' for asset '{asset.id}'"
    )


def _apply_transform(obj: Any, tr: TransformData) -> None:
    obj.location = tr.location
    obj.rotation_euler = tr.rotation_euler
    obj.scale = tr.scale


def spawn_asset_by_id(
    asset_id: str,
    *,
    registry: Optional[AssetRegistry] = None,
    link: bool = False,
    collection_name: Optional[str] = None,
    bpy: Optional[Any] = None,
) -> List[Any]:
    """Load an asset by ID and optionally place appended objects.

    - For objects/collections: loaded datablocks are returned; if objects, the
      default transform is applied.
    - For materials/node_groups: the datablock is returned and no transform is applied.
    """
    if registry is None:
        registry = AssetRegistry()

    asset = registry.get_asset(asset_id)
    if not asset:
        raise KeyError(f"Unknown asset id: {asset_id}")

    if bpy is None:
        bpy = _require_bpy()

    created, category = _append_or_link(asset, link=link, bpy=bpy)

    # Optionally move objects into a target collection and apply transform
    if category == "objects":
        target_col = None
        scene = getattr(bpy.context, "scene", None)
        if collection_name:
            target_col = bpy.data.collections.get(collection_name)
            if target_col is None:
                target_col = bpy.data.collections.new(collection_name)
                if scene:
                    scene.collection.children.link(target_col)
        elif scene:
            target_col = scene.collection

        for obj in created:
            _apply_transform(obj, asset.default_transform)
            if target_col:
                # Remove from the master scene collection only if present to avoid noisy errors
                scene_coll = scene.collection if scene else None
                if scene_coll and scene_coll.objects.get(obj.name):
                    try:
                        scene_coll.objects.unlink(obj)
                    except RuntimeError:
                        pass

                if not target_col.objects.get(obj.name):
                    try:
                        target_col.objects.link(obj)
                    except RuntimeError:
                        pass

    return created
