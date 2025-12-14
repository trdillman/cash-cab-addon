Scope (files changed)
- `road/street_labels.py`
- `gui/operators.py`
- `gui/panels.py`
- `gui/properties.py`
- `gui/__init__.py`

Summary
- Adds viewport-only street labels as FONT text objects under a dedicated `STREET_LABELS` collection.
- Adds UI controls (Show/Generate/Clear) under CashCab → Extra Features.
- Enforces non-rendering at both collection and object level (`hide_render=True`).

Key Implementation Notes
- Name extraction:
  - Preferred: parses the most recently downloaded `*.osm` in the addon OSM cache folder and extracts `way` tags (`name`, `highway`).
  - Fallback: attempts to read common custom properties (`name`, `osm:name`, etc.) from candidate road objects and their data blocks.
  - Last resort: uses object names that look like road objects (skips `ASSET_ROADS`).
- Candidate selection:
  - OSM-based mode prefers “major roads” by `highway` tag (`motorway/trunk/primary/secondary/tertiary`), otherwise includes all named ways.
  - Object-based fallback filters out helper/profile objects (e.g., `profile_*`, `way_profiles*`).
- Placement:
  - OSM-based mode places labels at a cheap centroid: average of the way’s node lat/lon projected into the scene using the current projection.
  - Adds optional intersection labels near Start/End markers by finding nearest named OSM ways in projected space.
  - Object-based fallback uses each candidate object’s bounding-box center transformed into world space.

How to test in Blender UI (2–3 steps)
1. Run `Fetch Route & Map` (so roads exist).
2. In the CashCab panel, expand **Extra Features** → **Street Labels**, click **Generate Street Labels**.
3. Toggle **Show Street Labels** to view/hide them in the viewport; click **Clear Street Labels** to remove them.

PASS/FAIL Checklist
- [ ] After Fetch Route & Map, UI shows: Show / Generate / Clear controls.
- [ ] Clicking Generate creates `STREET_LABELS` and adds ≥1 text label if roads exist.
- [ ] `STREET_LABELS` is hidden in viewport by default after generation until user toggles Show on.
- [ ] Labels never render (`collection.hide_render=True` and each label `obj.hide_render=True`).
- [ ] Clear removes only label objects and is safe to run repeatedly.
- [ ] No crashes if roads are missing; logs `[BLOSM] WARN street labels: ...` and no-ops.

