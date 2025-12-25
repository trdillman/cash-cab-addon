# Suggested Commands for CashCab Addon Development

## Root Level Testing (Preferred)
- End-to-end: `python test-and-audit/test_final_gate_run.py`
- Scene integrity: `python test-and-audit/test_scene_audit_strict.py`
- Render settings: `python test-and-audit/test_render_settings_audit.py`
- Operator tests: `python test-and-audit/test_operator_invoke.py`
- Camera integration: `blender -b --python test-and-audit/test_e2e_camera_integration.py`

## Blender Headless Testing
- Use `blender --factory-startup` flag to avoid addon conflicts
- Example: `blender --factory-startup --python test-and-audit/test_scene_audit_strict.py`

## Addon Development (from cash-cab-addon/)
- Package addon: `python build.py`
- Core tests: `blender -b --python tests/test_runner.py`
- Single test: `python -m unittest tests.test_filename.test_methodname`

## Bulk Processing
- `blender -b --python bulk-pipeline-v2/bulk_import_v2.py -- <input> <output_dir> [options]`
- Input: CSV with columns `task_id,pickup,dropoff[,date]`

## Asset Management
- Update registry: `python asset_manager/cli.py update`
- Validate assets: `python asset_manager/cli.py validate`
- Extract assets: `python asset_manager/asset_extractor.py`
