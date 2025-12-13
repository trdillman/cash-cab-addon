# 2025-12-13 — Merged `main` + `REPAIR--UI` (worktree) into `main`

## Goal
Consolidate all active development work from:
- Primary worktree: `cash-cab-addon/` (`main`)
- Secondary worktree: `cash-cab-addon.worktrees/features-test/` (`REPAIR--UI`)

…into a single, shippable `main` branch while preserving the latest features from both.

## What Landed On `main`

### 1) Blender 4.5+ property registration correctness
Blender 4.5 requires PropertyGroup/Operator properties to use annotated definitions (`name: bpy.props.*`).
Converted properties so runtime values are real Python values (not `_PropertyDeferred`).

Key files:
- `gui/properties.py` (PropertyGroup annotations)
- `gui/operators.py` (Operator property annotations)

### 2) Headless/e2e import reliability: writable data dir override
Added env override for the data directory used by OSM downloads so headless runs can write files even when the
default dev `.../data/osm` location is not writable.

Key file:
- `app/blender.py` (`BLOSM_DATA_DIR` support in `setDataDir`)

### 3) CAR_TRAIL “Custom Window” (drivers + UI controls)
Expose driver-controlled trimming for CAR_TRAIL bevel window using scene properties and drivers:
- `blosm_car_trail_start_adjust`
- `blosm_car_trail_end_adjust`
- `blosm_car_trail_tail_shift`

Drivers apply to `CAR_TRAIL` curve data:
- `bevel_factor_start`
- `bevel_factor_end`

Key files:
- `__init__.py` (Scene properties register/unregister)
- `route/pipeline_finalizer.py` (driver expressions + variables)
- `gui/panels.py` (UI controls under “Car Trail Custom Window”)

UI note:
- Animation Controls panel is above Extend City.
- Animation Controls is collapsed by default.

### 4) Route import + pipeline features from `REPAIR--UI`
Pulled the feature work from the `REPAIR--UI` branch (secondary worktree) into `main`, including:
- Route import operator flow and route processing
- Centerline snapping support (where applicable in existing operator flow)
- Water manager integration and related pipeline finalizers
- Bulk/inline fixers and supporting docs

Key files (non-exhaustive):
- `route/fetch_operator.py`
- `route/utils.py`
- `route/water_manager.py`
- `route/pipeline_finalizer.py`
- `gui/panels.py`, `gui/properties.py`
- `diffs/2025-12-12_inline_fixers_and_bulk_addon.md`

### 5) Repo hygiene: remove tracked `__pycache__/*.pyc`
Removed `__pycache__` and `*.pyc` files from git tracking (they were already ignored, but historically tracked).

## Test / Verification
Headless e2e import + strict audit + render audit (Blender 4.5.4) was run successfully with a writable data dir:

PowerShell example:
```powershell
$env:BLOSM_DATA_DIR = Join-Path $env:LOCALAPPDATA 'Temp\cashcab_blosm_data'
$env:TEMP = Join-Path $env:LOCALAPPDATA 'Temp'
$env:TMP = $env:TEMP
blender --factory-startup -b --python test_e2e_then_strict_toronto.py
```

Note: the test harness may fail to save `.blend` outputs if `Desktop\CashCab_QA` is not writable; audits can still pass.

