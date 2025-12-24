from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


def _abspath(path: str) -> str:
    return str(Path(bpy.path.abspath(path)).resolve())


def _ensure_addon_enabled() -> None:
    """
    Ensure the *installed/enabled* CashCab addon is available.

    This script is intentionally not loading the repo's __init__.py; it should
    operate through the normal Blender addon system.
    """
    import addon_utils

    candidates = ["cash_cab_addon", "cash-cab-addon", "blosm"]
    for module in candidates:
        try:
            is_default, is_loaded = addon_utils.check(module)
            if is_loaded:
                return
            if is_default:
                bpy.ops.preferences.addon_enable(module=module)
                return
        except Exception:
            continue


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CashCab bulk import for a local manifest (headless-safe).")
    parser.add_argument("--manifest", required=True, help="Path to local CSV manifest.")
    parser.add_argument("--output-dir", required=True, help="Directory to write shot folders + .blend outputs.")
    parser.add_argument("--version", default="V01", help="Version label like V01.")
    parser.add_argument("--auto-snap", action="store_true", help="Enable auto-snap (requires Google API key).")
    argv = sys.argv
    args = parser.parse_args(argv[argv.index("--") + 1 :] if "--" in argv else [])

    _ensure_addon_enabled()

    scene = bpy.context.scene
    settings = getattr(scene, "cashcab_bulk", None)
    if settings is None:
        raise RuntimeError("Scene.cashcab_bulk not registered; is the addon enabled?")

    settings.manifest_source = "LOCAL_FILE"
    settings.local_file_path = _abspath(args.manifest)
    settings.output_dir = _abspath(args.output_dir)
    settings.version_label = str(args.version or "V01")
    settings.auto_snap_addresses = bool(args.auto_snap)

    # Ensure "standard" timing exists on the driver scene so it gets transferred to workers.
    # This is what RouteRig expects by default.
    if hasattr(scene, "blosm_anim_start"):
        scene.blosm_anim_start = int(getattr(scene, "blosm_anim_start", 15) or 15)
    if hasattr(scene, "blosm_anim_end"):
        scene.blosm_anim_end = int(getattr(scene, "blosm_anim_end", 150) or 150)
    if hasattr(scene, "blosm_route_start"):
        scene.blosm_route_start = int(getattr(scene, "blosm_route_start", 15) or 15)
    if hasattr(scene, "blosm_route_end"):
        scene.blosm_route_end = int(getattr(scene, "blosm_route_end", 150) or 150)

    res = bpy.ops.blosm.bulk_fetch_manifest("EXEC_DEFAULT")
    if "FINISHED" not in res:
        raise RuntimeError(f"bulk_fetch_manifest failed: {res}")

    # Select all routes in the manifest.
    sel = bpy.ops.blosm.bulk_select_all("EXEC_DEFAULT")
    if "FINISHED" not in sel:
        raise RuntimeError(f"bulk_select_all failed: {sel}")

    run = bpy.ops.blosm.bulk_run_selected("EXEC_DEFAULT")
    if "FINISHED" not in run:
        raise RuntimeError(f"bulk_run_selected failed: {run}")

    print("[BulkSingle] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
