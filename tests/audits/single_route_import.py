from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import bpy


def _load_addon_module() -> None:
    """Load/register the addon from this repo so we test the current code."""
    repo_root = Path(__file__).resolve().parents[2]
    init_path = repo_root / "__init__.py"
    module_name = "cash_cab_addon"

    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        spec = importlib.util.spec_from_file_location(
            module_name,
            str(init_path),
            submodule_search_locations=[str(repo_root)],
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load addon module spec")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    register = getattr(module, "register", None)
    if callable(register):
        try:
            register()
        except ValueError:
            pass


def _abspath(p: str) -> Path:
    return Path(bpy.path.abspath(p)).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless single-route import (regular operator) and save blend.")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--padding-m", type=float, default=0.0)
    parser.add_argument("--out-blend", required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

    _load_addon_module()

    scene = bpy.context.scene
    addon = getattr(scene, "blosm", None)
    if addon is None:
        raise RuntimeError("Scene.blosm missing; addon did not register correctly")

    # Match the user's described settings.
    addon.route_start_address = str(args.start)
    addon.route_end_address = str(args.end)
    addon.route_padding_m = float(args.padding_m)
    addon.route_create_preview_animation = True
    addon.route_generate_camera = True

    # Ensure standard animation window (what RouteRig keys against).
    if hasattr(scene, "blosm_anim_start"):
        scene.blosm_anim_start = 15
    if hasattr(scene, "blosm_anim_end"):
        scene.blosm_anim_end = 150
    if hasattr(scene, "blosm_route_start"):
        scene.blosm_route_start = 15
    if hasattr(scene, "blosm_route_end"):
        scene.blosm_route_end = 150

    res = bpy.ops.blosm.fetch_route_map("EXEC_DEFAULT")
    if "FINISHED" not in res:
        raise RuntimeError(f"blosm.fetch_route_map failed: {res}")

    out = _abspath(str(args.out_blend))
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print(f"[SingleImport] Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

