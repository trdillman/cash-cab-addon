# Routerig Feature Add Spec

This doc tells a fresh coding agent how to add three small RouteRig features. It is self-contained: no prior context required. You can run tasks manually or spawn an orchestrator agent to execute end-to-end.

## How to use this doc
1) Read the section for the feature you want (1–3).
2) Start a coding agent in the repo root: `cd cash-cab-addon-dev-folder\cash-cab-addon`.
3) If using an orchestrator agent, point it to this file and ask it to execute the “Steps” list for the chosen feature.
4) If doing manually, follow the steps and file edit notes. Run tests/audits as indicated.

## Shared repo context
- Blender addon source: `routerig/`, `route/`, `tests/audits/`.
- Camera generation entrypoint: `routerig/camera_anim.py`; operators: `routerig/ops.py`; spawn helpers: `routerig/camera_spawn.py`.
- Default profile: `routerig/style_profile_learned.json` (fallback _default.json).
- Audit script: `tests/audits/routerig_camera_audit.py` (headless sanity check).

---

## Feature 1: Seeded micro-variation for framing
Goal: allow a user/automation to specify a seed and small variance to gently perturb camera framing (screen nx/ny and target_weights) while keeping timing/anchors intact.

### Plan
- Add properties for `routerig_seed` (int) and `routerig_variance` (float 0–1, default 0).
- Before keyframe solving, derive a deterministic RNG from seed and slightly offset:
  - `composition.desired_screen_keys` (car, start, end) nx/ny by variance * ~0.03.
  - `composition.target_weights_keys` values by variance * ~0.05 then renormalize to sum=1.
- Seed=0 or variance=0 → no-op. Log the seed when generating.

### Files to edit
- `routerig/scene_props.py` (add properties if using Scene.*).
- `routerig/camera_anim.py` (jitter profile before evaluation).
- `routerig/ops.py` (surface seed/variance and log).
- Optional helper: `routerig/style_profile.py` to clone/jitter profile dict.
- Tests: `tests/audits/routerig_camera_audit.py` can print the seed used.

### Steps
1) Add seed/variance properties (Scene or routerig settings container).
2) Implement `jitter_profile(profile, seed, variance)` that returns a new dict with adjusted nx/ny and target_weights (clamped, renormed).
3) Call jitter in `generate_camera_animation` before key extraction; pass seed/variance from Scene.
4) Defaults must be no-op.
5) Run: `python -m py_compile routerig/*.py` and a headless audit on a sample blend.

### Subagent prompt
“Implement seeded framing jitter per routerig_feature_add_spec.md (Feature 1). Add seed/variance props, jitter profile for nx/ny and target_weights, integrate into generate_camera_animation, defaults no-op. Run audits.”

---

## Feature 2: End-pose visibility solver (keep car unoccluded at end)
Goal: at the final active frame, adjust camera position minimally to avoid buildings occluding CAR_LEAD, without breaking pacing/style.

### Plan
- After camera states are computed, add a post-pass that checks LOS from camera to CAR_LEAD at the active_end frame.
- If occluded (ray hits ASSET_BUILDINGS before the car), push the camera using existing collision push order with limited iterations and distance cap.
- Re-key the end frame (and optionally a short blend window, e.g., last 8 frames) to smoothly land on the adjusted pose.

### Files to edit
- `routerig/camera_anim.py`: add `_adjust_end_pose_for_visibility(cam_obj, car_obj, bvh, active_end, blend_window=8)`; call after states are built, before keyframe insertion.
- Optional flag in `routerig/style_profile_default.json` if you want a toggle.

### Steps
1) Reuse the buildings BVH built in camera generation.
2) At active_end, cast a ray cam→car; if hit occurs before car, iteratively nudge camera along push order until LOS clears or budget exhausted.
3) If moved, blend the last N frames toward the new end pose to avoid pops.
4) Keyframe with the adjusted end pose; keep hold_last behavior.
5) Run the audit script on a test blend to confirm in-view PASS.

### Subagent prompt
“Add end-pose visibility solver per routerig_feature_add_spec.md Feature 2: LOS check at active_end, push camera if occluded, blend last ~8 frames, key end pose, keep pacing.”

---

## Feature 3: Orbit nudge + ortho-scale delta controls
Goals:
- Orbit nudge: user-adjustable angle/radius applied only at keyed frames to ‘orbit’ around CAR_LEAD without altering timing.
- Ortho-scale delta: a slider that adds/subtracts from keyed ortho_scale values at generation time (not a duplicate key).

### Plan
- Add properties: `routerig_orbit_deg`, `routerig_orbit_radius`, `routerig_orbit_apply_to_keys_only` (bool, default True), and `routerig_ortho_delta` (float, default 0, clamp reasonable bounds).
- In `generate_camera_animation`, after states are computed (and after optional visibility fix), adjust each keyed state:
  - Orbit: rotate camera position around CAR_LEAD on XY plane by orbit_deg with radius offset; rotate orientation to keep looking at CAR_LEAD.
  - Ortho: add `ortho_delta` to `state.ortho_scale` and clamp > 0.
- Re-key with adjusted states; honor hold_last and handle smoothing.

### Files to edit
- `routerig/scene_props.py` (new props).
- `routerig/camera_anim.py` (apply orbit and ortho delta before key insertion).
- `routerig/ops.py` (surface props/logging if desired).

### Steps
1) Add props with defaults: orbit_deg=0, orbit_radius=0, apply_to_keys_only=True, ortho_delta=0.
2) Implement `_apply_orbit_and_ortho_delta(states, car_obj, orbit_deg, orbit_radius, ortho_delta, keys_only=True)`.
3) Call helper just before keyframe insertion; if keys_only, modify only keyed states (current design keys only at ks).
4) Re-run audit to confirm no spins and framing is stable.

### Subagent prompt
“Implement orbit nudge and ortho-scale delta per routerig_feature_add_spec.md Feature 3: add props, adjust keyed states before keying, defaults no-op, preserve pacing/handles.”

---

## Testing checklist
- `python -m py_compile routerig/*.py tests/audits/*.py`
- Headless camera audit: `blender -b <blend> --factory-startup --python tests/audits/routerig_camera_audit.py -- --report-path /tmp/a.md --save-blend /tmp/out.blend`
- Optional bulk smoke: `blender -b --python tests/audits/run_bulk_single_route.py -- --manifest <csv> --output-dir <dir> --version V01`

## Notes
- Defaults must be no-op to preserve current behavior.
- Clamp deltas/variance to small ranges to avoid breaking style.
- Log seed/flags in operators to aid reproducibility.
