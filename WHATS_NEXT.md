# What's Next (Post Final Gate - 2025-12-09)

The rollback-prune branch passed the final release gate. Keep the addon stable and focus on small, high-signal follow-ups.

## Immediate hygiene
- Keep `diffs/` up to date for any change.
- Use `tmp/` for scratch files; keep `cash-cab-addon/` clean.
- Re-run `test_final_gate_run.py` before any release tagging.

## High-priority monitoring
- Watch for CAR_TRAIL/ROUTE regressions (geometry or transform mismatches, duplicates, library links).
- Environment assets: ensure water/ground/island shoreline objects continue to append; treat missing .blend as WARN-only.
- Render settings: maintain Fast GI + AO + clamp settings enforced by `test_render_settings_audit.py`.

## Potential follow-up tasks
- RouteTrace GN/driver warnings (if they reappear): normalize node group naming and driver targets.
- Minor UI polish only if discrepancies are observed during manual review.
- Performance profiling on large routes (optional) while preserving current invariants.

## When making changes
- Run `test_scene_audit_strict.py` and `test_render_settings_audit.py` for any pipeline/UI change.
- For release candidates, run three fresh Toronto routes via `test_final_gate_run.py`.

**Owner focus:** stability and audit readiness; no broad refactors without approval.
