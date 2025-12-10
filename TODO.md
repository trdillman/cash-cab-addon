# CashCab Addon — TODO (Rollback Dev)

This TODO list tracks concrete, near‑term work items for the rollback‑prune branch, building on the recent water/environment and CAR_TRAIL fixes.

## High Priority

- [ ] **Fix RouteTrace GN/driver warnings**
  - Locate RouteTrace wiring in `route/pipeline_finalizer.py` (or related module).
  - Normalize GN node group naming (`ASSET_RouteTrace` vs `ASSET_RouteTrace.002`).
  - Ensure the expected driver exists on `modifiers["RouteTrace"]["Socket_10"]` (or canonical socket) and targets runtime objects/scene properties.
  - Add a focused diff log (e.g. `diffs/YYYY-MM-DD_fix_routetrace_gn_drivers.md`) and quick QA notes.

- [ ] **Document RouteTrace behaviour & expectations**
  - Extend `README.md` and/or `WHATS_NEXT.md` with:
    - canonical RouteTrace object, modifier, and node group names;
    - a brief explanation of how RouteTrace is meant to react to scene animation controls.

## Medium Priority

- [ ] **Batch C — UI cleanup**
  - Remove any lingering references to removed properties or Asset Manager from `gui/panels.py` and comments.
  - Ensure labels and tooltips accurately describe:
    - auto‑import for roads/buildings/water/environment;
    - the fact that RouteCam does not auto‑run; and
    - CAR_TRAIL being a derived, non‑toggled asset.

- [ ] **Batch D — Import enhancements**
  - Reintroduce World Z+90 behaviour without Asset Manager.
  - Decide on and implement a Smooth modifier strategy for the route (if still desired).

- [ ] **Batch E — Confirmation dialogs**
  - Clarify and enhance confirmation dialogs for:
    - Fetch Route & Map (long‑running operation).
    - Any destructive cleanup operators.

## Low Priority / Nice to Have

- [ ] **Additional audit coverage**
  - Add a second audit script for RouteTrace (GN + driver verifications).
  - Optionally add a simple script that lists objects by `blosm_role` for quick debugging.

- [ ] **Developer docs refresh**
  - Once Batch C/D/E are implemented, update:
    - `BATCH_A_B_SUMMARY.md` (or create `BATCH_C_D_E_SUMMARY.md`) to record the next rounds of work.
    - Any onboarding notes for new agents/contributors.

