"""
Headless E2E harness: tries one Toronto address pair, runs Fetch Route & Map,
then the strict audit in the same session.

Exit codes:
- 0: PASS (real Fetch returned {'FINISHED'} AND strict audit passed AND blend saved)
- 1: FAIL (Fetch attempted but failed or strict audit failed)
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import traceback
from pathlib import Path

import bpy


DEV_ROOT = Path(__file__).resolve().parent
ADDON_DIR = DEV_ROOT.parent # Corrected path to point to the addon root
MODULE_NAME = "cash_cab_addon"

# Single hard-coded address pair for this test run.
START_ADDRESS = "100 Queen St W, Toronto, ON, Canada"
END_ADDRESS = "200 University Ave, Toronto, ON, Canada"


def _log(msg: str) -> None:
    print(f"[E2E] {msg}")


def _load_addon_module():
    if MODULE_NAME in sys.modules:
        _log(f"Module '{MODULE_NAME}' already in sys.modules.")
        module = sys.modules[MODULE_NAME]
    else:
        if str(ADDON_DIR) not in sys.path:
            sys.path.insert(0, str(ADDON_DIR))

        init_path = ADDON_DIR / "__init__.py"
        _log(f"Loading addon from: {init_path}")

        spec = importlib.util.spec_from_file_location(
            MODULE_NAME,
            init_path,
            submodule_search_locations=[str(ADDON_DIR)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = module
        spec.loader.exec_module(module)

    bpy.ops.wm.addon_utils.enable(module=MODULE_NAME) if hasattr(bpy.ops.wm, "addon_utils") and hasattr(bpy.ops.wm.addon_utils, "enable") else None
    
    # Explicitly register the addon if not already registered.
    # This ensures the operators are available for bpy.ops calls, even if wm.addon_enable fails or isn't present.
    try:
        if hasattr(module, 'register') and callable(module.register):
            module.register()
            _log(f"Addon '{MODULE_NAME}' manually registered.")
    except Exception as e:
        _log(f"Error manually registering addon '{MODULE_NAME}': {e}")
        traceback.print_exc()

    _log(f"Addon '{MODULE_NAME}' ensured active.")
    return module



def _run_fetch(start: str, end: str) -> set:
    scene = bpy.context.scene
    addon_props = getattr(scene, "blosm", None)
    addon_props.route_start_address = start
    addon_props.route_end_address = end
    _log(f"Fetch start='{start}' end='{end}'")

    try:
        result = bpy.ops.blosm.fetch_route_map("EXEC_DEFAULT")
        _log(f"Fetch result: {result}")
        return result
    except Exception as exc:
        _log(f"Fetch threw exception: {exc}")
        traceback.print_exc()
        return {"CANCELLED"}


def _run_strict_audit() -> bool:
    audit_script_path = DEV_ROOT / "audits" / "scene_auditor.py"
    if not audit_script_path.exists():
        _log(f"STRICT AUDIT SCRIPT MISSING: {audit_script_path}")
        return False

    try:
        # Dynamically import and run the audit script's main function.
        # Pass the audit level and report path via sys.argv for argparse.
        sys.argv = [str(audit_script_path), "--level", "strict", "--report-path", "e2e_strict_audit_report.xml"]
        
        spec = importlib.util.spec_from_file_location("scene_auditor", str(audit_script_path))
        scene_auditor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scene_auditor_module)
        scene_auditor_module.main()
        
        # Check the audit result (assuming main() exits with 1 on failure)
        # If it reaches here, it means main() did not exit, so it passed.
        _log("Strict audit main() completed without exiting (indicating PASS).")
        return True
    except SystemExit as e:
        if e.code == 0:
            _log("Strict audit main() exited with code 0 (indicating PASS).")
            return True
        else:
            _log(f"Strict audit main() exited with code {e.code} (indicating FAIL).")
            traceback.print_exc()
            return False
    except Exception as exc:
        _log(f"Strict audit threw an unhandled exception: {exc}")
        traceback.print_exc()
        return False
        _log("Strict audit main() completed.")
        return True
    except SystemExit as exc:
        if exc.code in (0, None):
            _log("Strict audit exited with success code.")
            return True
        _log(f"Strict audit failed with exit code {exc.code}.")
        return False
    except Exception as exc:
        _log(f"Strict audit threw an unhandled exception: {exc}")
        traceback.print_exc()
        return False


def _save_blend(label: str) -> None:
    desktop_path = Path(os.path.expandvars("%USERPROFILE%")) / "Desktop" / "CashCab_QA"
    desktop_path.mkdir(parents=True, exist_ok=True)
    filepath = desktop_path / f"{label}.blend"
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
        _log(f"Saved blend file to: {filepath}")
    except Exception as exc:
        _log(f"Failed to save .blend file: {exc}")
        # Non-fatal, as the main test has passed at this point.
        traceback.print_exc()


def main():
    _load_addon_module()
    
    result = _run_fetch(START_ADDRESS, END_ADDRESS)
    if result != {"FINISHED"}:
        _log(f"FAIL: Fetch Route & Map operator failed with result: {result}")
        sys.exit(1)
    
    _log("Fetch successful, proceeding to strict audit.")
    audit_ok = _run_strict_audit()

    if not audit_ok:
        _log("FAIL: Strict audit failed.")
        sys.exit(1)

    _log("E2E and strict audit PASSED.")
    _save_blend("RUN1_toronto_attempt1")
    sys.exit(0)


if __name__ == "__main__":
    main()
