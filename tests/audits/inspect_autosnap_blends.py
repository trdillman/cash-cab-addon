from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import bpy


def _ensure_addon_enabled() -> None:
    """
    Ensure CashCab addon is registered so Scene.blosm is available when inspecting files.
    Prefer loading from the repo checkout to match dev workflows.
    """
    try:
        # If the property is already registered, we're good.
        if hasattr(bpy.types.Scene, "blosm"):
            return
    except Exception:
        pass

    try:
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from tests.test_e2e_toronto_strict import _load_addon_module

        _load_addon_module()
        return
    except Exception:
        pass

    # Fallback: try enabling installed addon.
    try:
        import addon_utils

        for module in ["cash_cab_addon", "cash-cab-addon", "blosm"]:
            try:
                is_default, is_loaded = addon_utils.check(module)
                if is_loaded:
                    return
                if is_default:
                    bpy.ops.preferences.addon_enable(module=module)
                    return
            except Exception:
                continue
    except Exception:
        pass


def _iter_blends_from_dir(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*.blend") if p.is_file()], key=lambda p: p.name.lower())


def _resolve_scene() -> bpy.types.Scene:
    # Prefer the canonical CashCab scene name when present.
    try:
        scn = bpy.data.scenes.get("CashCab")
        if scn is not None:
            return scn
    except Exception:
        pass
    return bpy.context.scene


def _safe_getattr(obj, name: str, default=None):
    try:
        return getattr(obj, name)
    except Exception:
        return default


def _snap_kind(label: str) -> str:
    txt = (label or "").strip()
    if not txt:
        return "NONE"
    if txt.lower() == "bulk":
        return "BULK_COORDS"
    return "AUTO_OR_MANUAL"


def _inspect_open_file(path: Path) -> dict[str, object]:
    _ensure_addon_enabled()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = _resolve_scene()
    addon = _safe_getattr(scene, "blosm", None)

    auto_snap = bool(_safe_getattr(addon, "auto_snap_addresses", False)) if addon else False
    start_label = str(_safe_getattr(addon, "start_snapped_coords", "") or "") if addon else ""
    end_label = str(_safe_getattr(addon, "end_snapped_coords", "") or "") if addon else ""
    start_lat = _safe_getattr(addon, "route_start_address_lat", None) if addon else None
    start_lon = _safe_getattr(addon, "route_start_address_lon", None) if addon else None
    end_lat = _safe_getattr(addon, "route_end_address_lat", None) if addon else None
    end_lon = _safe_getattr(addon, "route_end_address_lon", None) if addon else None

    return {
        "blend": str(path),
        "scene": str(getattr(scene, "name", "")),
        "auto_snap_addresses": auto_snap,
        "start_snapped_coords": start_label,
        "end_snapped_coords": end_label,
        "start_snap_kind": _snap_kind(start_label),
        "end_snap_kind": _snap_kind(end_label),
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Inspect saved .blend files for auto-snap state.")
    parser.add_argument("--dir", help="Directory to search for .blend files (recursive).")
    parser.add_argument("--blend", action="append", help="Specific .blend file path (repeatable).")
    args = parser.parse_args(argv)

    blends: list[Path] = []
    if args.dir:
        blends.extend(_iter_blends_from_dir(Path(bpy.path.abspath(args.dir)).resolve()))
    if args.blend:
        for raw in args.blend:
            blends.append(Path(bpy.path.abspath(raw)).resolve())

    blends = [b for b in blends if b.exists() and b.suffix.lower() == ".blend"]
    if not blends:
        print("[AutoSnapInspect] No .blend files found.")
        return 2

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "blend",
            "scene",
            "auto_snap_addresses",
            "start_snap_kind",
            "start_snapped_coords",
            "end_snap_kind",
            "end_snapped_coords",
            "start_lat",
            "start_lon",
            "end_lat",
            "end_lon",
        ],
    )
    writer.writeheader()

    counts = {
        "files": 0,
        "auto_snap_true": 0,
        "start_nonempty": 0,
        "end_nonempty": 0,
    }

    for path in blends:
        row = _inspect_open_file(path)
        counts["files"] += 1
        if row["auto_snap_addresses"]:
            counts["auto_snap_true"] += 1
        if str(row["start_snapped_coords"] or "").strip():
            counts["start_nonempty"] += 1
        if str(row["end_snapped_coords"] or "").strip():
            counts["end_nonempty"] += 1
        writer.writerow({k: row.get(k, "") for k in writer.fieldnames})

    print(
        f"[AutoSnapInspect] files={counts['files']} "
        f"auto_snap_true={counts['auto_snap_true']} "
        f"start_nonempty={counts['start_nonempty']} "
        f"end_nonempty={counts['end_nonempty']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    raise SystemExit(main(argv))
