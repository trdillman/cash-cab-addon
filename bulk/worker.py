from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


def _parse_coords(text: str) -> Optional[Tuple[float, float]]:
    if not text:
        return None
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 2:
        return None
    try:
        lat = float(parts[0])
        lon = float(parts[1])
    except ValueError:
        return None
    return lat, lon


def _ensure_addon_enabled() -> None:
    import bpy
    import importlib.util
    import sys as _sys
    import addon_utils
    
    candidates = ["cash_cab_addon", "cash-cab-addon", "blosm"]
    for module in candidates:
        try:
            is_default, is_loaded = addon_utils.check(module)
            if is_loaded:
                return
            if is_default: # Addon exists in search path
                bpy.ops.preferences.addon_enable(module=module)
                return
        except Exception:
            continue

    addon_root = Path(__file__).resolve().parent.parent
    init_path = addon_root / "__init__.py"
    if not init_path.exists():
        raise RuntimeError("Addon __init__.py not found for manual load")

    spec = importlib.util.spec_from_file_location(
        "cash_cab_addon",
        str(init_path),
        submodule_search_locations=[str(addon_root)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load addon module spec")

    module = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if hasattr(module, "register"):
        module.register()


def _open_base_blend(path: str) -> None:
    import bpy

    if not path:
        return
    blend_path = Path(path).resolve()
    if blend_path.exists():
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))


def _apply_route_settings(payload: dict) -> None:
    import bpy

    scene = bpy.context.scene
    addon = getattr(scene, "blosm", None)
    if addon is None:
        raise RuntimeError("Scene.blosm settings not available")

    start_address = payload.get("start_address") or ""
    end_address = payload.get("end_address") or ""
    addon.route_start_address = start_address
    addon.route_end_address = end_address

    shot_code = (payload.get("shot_code") or "").strip()
    if shot_code:
        try:
            scene["cashcab_shot_code"] = shot_code
        except Exception:
            pass

    auto_snap = bool(payload.get("auto_snap", True))
    addon.auto_snap_addresses = auto_snap

    start_coords = _parse_coords(payload.get("start_coords") or "")
    end_coords = _parse_coords(payload.get("end_coords") or "")

    if start_coords:
        addon.start_snapped_coords = "Bulk"
        addon.route_start_address_lat = float(start_coords[0])
        addon.route_start_address_lon = float(start_coords[1])
    else:
        addon.start_snapped_coords = ""

    if end_coords:
        addon.end_snapped_coords = "Bulk"
        addon.route_end_address_lat = float(end_coords[0])
        addon.route_end_address_lon = float(end_coords[1])
    else:
        addon.end_snapped_coords = ""

    # Pass API key to route configuration via env var
    api_key = payload.get("google_api_key")
    if api_key:
        import os
        from cash_cab_addon.route.config import DEFAULT_CONFIG
        os.environ[DEFAULT_CONFIG.google_api.api_key_env_var] = api_key


def _run_fetch() -> None:
    import bpy

    # Verbose logging for headless runs
    try:
        from cash_cab_addon.route.fetch_operator import BLOSM_OT_FetchRouteMap
        BLOSM_OT_FetchRouteMap._log_enabled = True
    except Exception:
        pass

    result = bpy.ops.blosm.fetch_route_map("EXEC_DEFAULT")
    if "FINISHED" not in result:
        raise RuntimeError("Route fetch failed")


def _validate_scene() -> None:
    import bpy

    if not bpy.data.objects:
        raise RuntimeError("No objects in scene after import")


def _save_output(path: str) -> None:
    import bpy

    if not path:
        raise RuntimeError("Output path missing")
    out_path = Path(path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_path))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_json", required=True)
    return parser.parse_args(argv)


def main() -> int:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    args = _parse_args(argv)
    payload = json.loads(args.job_json)

    print("[BulkWorker] job:", {
        "shot_code": payload.get("shot_code"),
        "start_address": (payload.get("start_address") or "")[:120],
        "end_address": (payload.get("end_address") or "")[:120],
        "auto_snap": bool(payload.get("auto_snap", True)),
        "has_api_key": bool((payload.get("google_api_key") or "").strip() or os.environ.get("CASHCAB_GOOGLE_API_KEY", "").strip()),
        "output_path": payload.get("output_path"),
    })

    _ensure_addon_enabled()
    _open_base_blend(payload.get("base_blend", ""))
    _apply_route_settings(payload)
    _run_fetch()
    _validate_scene()
    _save_output(payload.get("output_path", ""))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[BulkWorker] ERROR: {exc}")
        raise SystemExit(1)
