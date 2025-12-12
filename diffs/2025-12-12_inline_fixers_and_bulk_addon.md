# 2025-12-12 – Inline fixer logic + bulk addon scaffold

## Scope

- **Profile curve fixer moved into main pipeline**
  - Added `PROFILE_CURVE_OBJECT_NAME = "_profile_curve"` constant in `route/pipeline_finalizer.py`.
  - New helper `_ensure_profile_curve_asset(scene)`:
    - Appends `_profile_curve` from `ASSET_CAR_TRAIL.blend` when missing.
    - Ensures `_profile_curve` lives in the `ASSET_CAR` collection (exclusive).
  - Called from:
    - `_build_car_trail_from_route(scene)` before CAR_TRAIL construction.
    - `_resync_car_trail_transform(scene)` before bevel fallback.
  - All existing fallbacks now use `PROFILE_CURVE_OBJECT_NAME` instead of a hard-coded string.

- **Render output fixer moved into main pipeline**
  - Added `_ensure_cashcab_render_output(scene)` in `route/pipeline_finalizer.py`:
    - Resolves a shot code from `scene.blosm.shot_code` or `scene["cashcab_shot_code"]`.
    - Sets `scene.render.filepath` to:
      - `//{SHOT}_3D_` when a shot code is available, or
      - `//CashCab_3D_` as a generic default.
    - Ensures `scene.render.use_file_extension = True`.
  - Invoked near the end of `run()` just before camera asset integration.
  - Result key: `result["render_output"]` now records the final path.

- **Batch importer wires shot code into the scene**
  - In `batch_route_import_from_manifest._run_single_route(...)`:
    - Sets `scene["cashcab_shot_code"] = task_id` before configuring route properties.
  - This lets the pipeline derive `//{TASKID}_3D_` without external render-path fixer scripts.

- **New `cash-cab-bulk` addon (sibling to main addon)**
  - Folder: `cash-cab-bulk/`
  - `__init__.py` provides:
    - `CashCabBulkSettings` (`Scene.cashcab_bulk_settings`) with:
      - `manifest_path` (FILE_PATH)
      - `output_root` (DIR_PATH)
    - Operator `cashcab_bulk.import_manifest`:
      - Reuses `batch_route_import_from_manifest.py` via `_load_batch_module()`:
        - Calls `_load_addon_from_this_folder()` to register `cash_cab_addon`.
        - Uses `read_manifest()`, `_slugify()`, and `_run_single_route()` for parity with CLI batch.
      - Saves per-shot `.blend` files matching the existing naming convention.
    - Panel `CASHCAB_BULK_PT_manifest` under `View3D > Sidebar > CashCab Bulk` to:
      - Choose manifest and output folder.
      - Trigger the bulk import operator.

## Testing / sanity checks

- `python -m py_compile` on:
  - `cash-cab-addon/route/pipeline_finalizer.py`
  - `batch_route_import_from_manifest.py`
  - `cash-cab-bulk/__init__.py`
- Recommended manual verification (not run here):
  - Single-route import via main addon:
    - Confirm `_profile_curve` exists in `ASSET_CAR` and `CAR_TRAIL.data.bevel_object` is set correctly.
    - Confirm `Ground_Plane_Result` Z scale and other scene audits still pass.
    - Confirm `scene.render.filepath` is `//CashCab_3D_` when no shot code is set.
  - Manifest-based batch (CLI or bulk addon):
    - Confirm each output file:
      - Uses `//{TASKID}_3D_` as render path.
      - Passes strict scene/render audits previously used with the external fixer scripts.

