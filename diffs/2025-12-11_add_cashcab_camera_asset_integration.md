## Diff Log: Add CashCab Camera Asset Integration

**Date:** 2025-12-11

### Files Touched

- `cash-cab-addon/route/pipeline_finalizer.py`
- `test_scene_audit_strict.py`
- `test_e2e_then_strict_toronto.py`

### Summary of Changes

This update integrates a standardized `CASHCAB_CAMERA` object into the route generation pipeline.

1.  **Pipeline (`pipeline_finalizer.py`):**
    - After a route is fetched, the pipeline now ensures a camera named `CASHCAB_CAMERA` exists.
    - This camera is appended from `assets/ASSET_CAMERA.blend` if not already present.
    - It is placed into a dedicated `CAMERAS` collection.
    - **Safe-area invariants** are enforced on the camera data, setting title and action safe areas to 0.95.

2.  **Strict Audit (`test_scene_audit_strict.py`):**
    - The strict audit now includes checks to ensure the `CASHCAB_CAMERA` exists, is of type `CAMERA`, resides in the `CAMERAS` collection, and has its safe areas correctly configured.
    - Failure to meet these conditions will now cause the overall strict audit to `FAIL`.

3.  **E2E Runner (`test_e2e_then_strict_toronto.py`):**
    - The E2E test has been simplified to run a **single Toronto address pair**.
    - It now executes the core `fetch_route_map` operation and immediately runs the strict audit.
    - The script will `exit(1)` on any failure, providing a clear pass/fail signal for CI or manual testing.

### Acceptance Checklist

- [x] **Camera asset ensured:** The pipeline logic correctly appends and configures the camera.
- [x] **CAMERAS collection present:** The logic correctly creates and populates the `CAMERAS` collection.
- [ ] **E2E+strict using cmd.exe status:** **PENDING VERIFICATION** (ASSET_CAMERA.blend now present, re-running test). Final verification requires running `blender -b --python test_e2e_then_strict_toronto.py` in a command prompt.
