"""
Simple CLI for inspecting and validating BLOSM asset registry.

Usage examples:
  python -m blosm_clean.asset_manager.cli list
  python -m blosm_clean.asset_manager.cli show default_car
  python -m blosm_clean.asset_manager.cli validate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .registry import AssetRegistry
from .errors import AssetValidationError


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="asset-cli", description="BLOSM Asset Manager CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List asset IDs")

    show_p = sub.add_parser("show", help="Show asset definition as JSON")
    show_p.add_argument("asset_id", help="Asset ID to show")

    val_p = sub.add_parser("validate", help="Validate asset registry")
    val_p.add_argument("--no-strict", action="store_true", help="Do not raise on validation errors")

    load_p = sub.add_parser("load", help="Load a registry file and print summary")
    load_p.add_argument("path", type=Path, help="Path to JSON registry file")

    return p


def cmd_list(reg: AssetRegistry) -> int:
    for aid in reg.list_assets():
        print(aid)
    return 0


def cmd_show(reg: AssetRegistry, asset_id: str) -> int:
    asset = reg.get_asset(asset_id)
    if not asset:
        print(f"Asset not found: {asset_id}")
        return 1
    print(json.dumps(asset.to_dict(), indent=2))
    return 0


def cmd_validate(reg: AssetRegistry, strict: bool) -> int:
    try:
        issues = reg.validate(strict=strict)
        if issues:
            print("Validation issues found:")
            for msg in issues:
                print(f"- {msg}")
            return 1
        print("Registry is valid.")
        return 0
    except AssetValidationError as exc:
        print(f"Validation failed: {exc}")
        return 1


def cmd_load(path: Path) -> int:
    reg = AssetRegistry(config_path=path)
    print(f"Loaded {len(reg.list_assets())} assets from {path}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "load":
        return cmd_load(args.path)

    reg = AssetRegistry()
    if args.cmd == "list":
        return cmd_list(reg)
    if args.cmd == "show":
        return cmd_show(reg, args.asset_id)
    if args.cmd == "validate":
        return cmd_validate(reg, strict=not args.no_strict)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

