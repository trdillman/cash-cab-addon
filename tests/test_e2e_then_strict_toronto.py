"""
Compatibility shim for older test scripts.

`test_e2e_outliner_audit.py` expects these symbols to exist. The repo's canonical
E2E harness is `test_e2e_toronto_strict.py`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

import bpy

from test_e2e_toronto_strict import _load_addon_module, _run_fetch, _run_strict_audit


ADDRESS_PAIRS: List[Tuple[str, str]] = [
    ("100 Queen St W, Toronto, ON, Canada", "200 University Ave, Toronto, ON, Canada"),
]


def _ensure_scene_defaults(scene: bpy.types.Scene) -> None:
    # Best-effort defaults for headless runs; keep intentionally minimal.
    addon = getattr(scene, "blosm", None)
    if addon is None:
        return
    try:
        addon.route_create_preview_animation = True
    except Exception:
        pass


def _save_blend(index: int, label: str) -> None:
    # Keep writes local to the current working directory (or an optional override).
    outdir = Path(os.environ.get("CASHCAB_E2E_OUTDIR", os.getcwd()))
    outdir.mkdir(parents=True, exist_ok=True)
    filepath = outdir / f"{label}_{index}.blend"
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
    except Exception:
        pass

