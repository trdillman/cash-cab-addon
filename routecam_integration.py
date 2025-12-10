"""
RouteCam integration helpers for the CashCab addon.

This module integrates the updated RouteCam from geo_nodes_camera/routecam_project/addon.
RouteCam is registered via addon.__init__.py but its UI panel is hidden.
CashCab uses RouteCam's VIZ engine headlessly to auto-generate 5 cameras on route import.

Integration is automatic when RouteCam operators are available.
"""

from __future__ import annotations

from typing import Optional

import bpy


def _has_routecam_ops() -> bool:
    """Return True if RouteCam operators are available in bpy.ops."""
    try:
        ops_routecam = getattr(bpy.ops, "routecam", None)
        if ops_routecam is None:
            return False
        return hasattr(ops_routecam, "random_batch")
    except Exception:
        return False


def _ensure_routecam_collection(context) -> bpy.types.Collection:
    """Get or create the dedicated RouteCam output collection."""
    col_name = "CAMERAS"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        if context.scene:
            context.scene.collection.children.link(col)
    return col

def _fix_cntower_collections(context):
    """Ensure objects named like 'CNTower' are ONLY in 'ASSET_CNTower' collection."""
    target_col_name = "ASSET_CNTower"
    
    # 1. Identify CN Tower objects
    tower_objs = []
    for obj in bpy.data.objects:
        if "cntower" in obj.name.lower().replace(" ", "") or "cn_tower" in obj.name.lower():
            tower_objs.append(obj)
            
    if not tower_objs:
        return

    # 2. Get or Create Target Collection
    target_col = bpy.data.collections.get(target_col_name)
    if not target_col:
        target_col = bpy.data.collections.new(target_col_name)
        context.scene.collection.children.link(target_col)
        
    # 3. Fix Collections for each object
    for obj in tower_objs:
        # Unlink from all current collections
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
            
        # Link only to the target collection
        if obj.name not in target_col.objects:
            target_col.objects.link(obj)
            
    print(f"[CashCab] Fixed collections for {len(tower_objs)} CN Tower objects")

def maybe_run_routecam(context: bpy.types.Context, route_obj: Optional[bpy.types.Object]) -> None:
    """Optionally generate RouteCam cameras for the given route curve.

    HOTFIX Batch F2:
    - RouteCam should NOT run by default now that toggles were removed.
    - This hook remains import-safe but exits early unless explicitly
      enabled by future call sites.

    Integration notes (kept for future opt-in wiring):
    - Requires RouteCam operators to be registered (random_batch).
    - Uses RouteCam's VIZ engine to generate cameras automatically.
    - Moves cameras from temp "RouteCam_Batch" to permanent "CAMERAS" collection.
    - Never raises; logs to console on failure.
    """

    # Early exit: RouteCam auto-integration disabled by default.
    # The CN Tower collection fix remains active elsewhere in the pipeline,
    # so we do not rely on RouteCam for scene correctness.
    return
    
    # NOTE: Legacy auto-generation logic has been disabled here.
    # It is preserved in routecam_integration.py.backup for reference
    # if a future version re-introduces an explicit opt-in control.
