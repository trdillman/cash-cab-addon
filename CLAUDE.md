# CLAUDE.md (Synced With AGENTS.md)

This file is intentionally **synced** with `AGENTS.md` so that both humans and assistants
use the same operational instructions for developing and validating `cash-cab-addon`.

## Project Overview

CashCab is a Blender addon for importing real-world routes + OpenStreetMap (OSM) data to produce
an animated scene (ROUTE, car, CAR_TRAIL, camera) and studio-ready render settings.

**Primary Operator:** `bpy.ops.blosm.fetch_route_map` (`route/fetch_operator.py`)

## Google Maps API Key (Headless + CI + Bulk)

For address auto-snap in headless workflows, set:

- `CASHCAB_GOOGLE_API_KEY=<your key>`

The UI still supports storing the key in addon preferences; headless runs should prefer the env var.

## Bulk Import (Native)

Bulk Import is implemented in `bulk/` and runs each route in a fresh headless Blender process to
avoid state corruption/memory leaks from long sequences.

### Key Concepts
- Manifest source: Google Sheet URL (CSV export) or local CSV
- Routes are displayed with sheet status (no “Pending” placeholder)
- “Run Selected” spawns headless workers and writes per-route logs

### Logs
- UI shows `Log Root` while running
- Default location: `%TEMP%\\cashcab_bulk_native\\<timestamp>\\*.log`

If you see **empty shot folders with no `.blend` output**, it usually means the worker didn’t run
or died early — check the per-route log and restart Blender after updating the addon.

## Developer Validation (Recommended)

### Regular Import (headless)
Run a single route import:

- `blender --factory-startup -b --python <script>.py`

### Bulk Import (headless)
Run bulk operators end-to-end:

- `blender --factory-startup -b --python <bulk_script>.py`

### Strict Scene Audits (per .blend)
These scripts live one directory above this repo (`../test-and-audit/`):

- `blender -b <file.blend> --python ..\\test-and-audit\\test_scene_audit_strict.py`
- `blender -b <file.blend> --python ..\\test-and-audit\\full_e2e_inspect.py`

Additional lightweight checks can be run via custom audit scripts.

## Known Behavior Notes

- `route_padding_m = 0` may still be expanded internally for the smart-water workflow (minimum 500m).
- Street labels are designed to be viewport-only and never render; default is hidden.

