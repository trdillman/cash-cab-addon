# Feature Spec: Street Labels (Text Objects in Hidden `STREET_LABELS` Collection)

## Purpose

Provide an optional, lightweight way to generate **street name labels** inside Blender for QA and layout, without affecting renders.

This feature adds:
- One dedicated collection: `STREET_LABELS`
- Operators to **Generate** and **Clear** labels (idempotent)
- A UI toggle to show/hide labels in viewport

This spec is designed for a brand new coding agent to implement with minimal context.

---

## Hard Requirements (Pass/Fail)

### Collection rules
- Create **ONE** collection named `STREET_LABELS`.
- `STREET_LABELS` must be:
  - Hidden from render: `collection.hide_render = True`
  - Hidden in viewport by default: `collection.hide_viewport = True`
  - Not enabled by default: stays hidden after import unless user turns it on

### Label object rules
- Labels are **Text objects** (font curves) so they appear in viewport when shown.
- Labels must never render:
  - Enforce `obj.hide_render = True` for every label object (belt-and-suspenders).

### UI requirements (CashCab panel)
Add in the existing CashCab UI panel:
- Toggle: `Show Street Labels` (controls `STREET_LABELS.hide_viewport`)
- Button: `Generate Street Labels`
- Button: `Clear Street Labels`

### Generate behavior
- Generate must be **idempotent**:
  - “Generate” does `Clear + rebuild` every time.

### Safety behavior
- No crashes if roads are missing.
- If roads are missing, log:
  - `[BLOSM] WARN street labels: ...`
  - and do a safe no-op.

---

## What To Label

Preferred scope:
- Only **major roads** AND closest intersections to START and END points.

If meaningfully harder in this codebase, acceptable fallback:
- Label **all road names** you can reliably extract.

### “Major road” heuristic (MVP acceptable)
Use OSM tags if available:
- `highway` in `{motorway, trunk, primary, secondary, tertiary}`

Fallback if tags are missing/unavailable:
- If no tags exist, include all named roads.
- Optionally: include all roads, but only label if name exists.

---

## Intersections (Nice-to-have)

Only implement if it’s easy and safe:
- If you can locate start/end marker objects (e.g., `MARKER_START` / `MARKER_END` or `Start` / `End`):
  - Place **2–6 additional labels near each** (NOT “26”; treat that as a typo and use a small number).
  - Find nearest road objects by bbox-center distance.
  - Label as `<Road A>  x  <Road B>` if two distinct road names exist nearby; otherwise label the single closest road name.

If intersection detection is too costly/complex:
- Skip intersections.
- Document that only per-road labels were generated.

---

## Where To Get Names + Positions

### Avoid helper/temporary objects
Logs and assets indicate helper objects exist (e.g., `profile_roads_*`, way profiles, merged mesh `ASSET_ROADS`). You must:
- Avoid labeling profile/helper objects.
- Prefer real “road” objects/collections that represent imported roads.

### Candidate extraction strategy (ordered; stop at first feasible)
1) **Preferred**: per-road objects before any join (if the pipeline keeps them).
   - Look for collections that contain road objects with name metadata or OSM tags.
2) **Next**: any metadata stored during import that maps object → OSM tags (e.g., `name`, `highway`).
3) **Fallback**: label based on object names if that’s all that exists.
4) **Last resort**: if everything is merged into a single `ASSET_ROADS` mesh with no per-road names, then:
   - Generate **only a minimal label set** near start/end by sampling nearest objects/collections with plausible names (or skip with warning).

### Placement (MVP acceptable)
For each candidate road object:
- Compute world-space label position using **bbox center**:
  - `pos = 0.5 * (obj.bound_box min/max)`, transformed by `obj.matrix_world`
- Optional (only if easy): for curve roads, sample spline midpoint.

---

## Text Object Settings (Readable MVP)

When creating labels:
- Create a Text object (Font curve):
  - `bpy.data.curves.new(type='FONT')` + `bpy.data.objects.new()`
  - `curve.body = street_name`
- Set transform:
  - Place at computed world position.
  - Orient to face up:
    - If needed: rotate X by +90 degrees so it reads on ground plane.
- Set size:
  - Use a consistent, readable size (pick a value that works in your scene scale).
  - Suggested starting point: `data.size = 3.0` (adjust based on scene; do not over-style).
- Rendering:
  - Always enforce `obj.hide_render = True`.
- Viewport-only:
  - No requirement for color/material; keep minimal.

---

## When To Run

- Do **NOT** auto-generate during import.
- Only generate on **button press**.
- Optional: ensure the `STREET_LABELS` collection exists after import (still hidden by default), but it’s acceptable to create it lazily on “Generate”.

---

## Implementation Map (Files / Where To Work)

### UI panel
- `cash-cab-addon/gui/panels.py`
  - Add a “Street Labels” row/box under existing “Extra Features” (or another appropriate section).

### Properties
- `cash-cab-addon/gui/properties.py`
  - Add BoolProperty: `ui_show_street_labels` (or similar) that toggles viewport visibility.
  - Implementation note: the toggle should set `STREET_LABELS.hide_viewport` (create collection if missing).

### Operators
- `cash-cab-addon/gui/operators.py`
  - Add:
    - `BLOSM_OT_GenerateStreetLabels` (`blosm.generate_street_labels`)
    - `BLOSM_OT_ClearStreetLabels` (`blosm.clear_street_labels`)

### Registration
- `cash-cab-addon/gui/__init__.py`
  - Register new operator classes.

### New feature module (recommended)
Add a new module to keep logic out of UI:
- `cash-cab-addon/road/street_labels.py` (preferred domain)
  - or `cash-cab-addon/route/street_labels.py` if roads are tightly coupled to route.

This module should expose:
- `ensure_street_labels_collection(scene) -> bpy.types.Collection`
- `clear_street_labels(scene) -> int` (returns count removed)
- `generate_street_labels(scene) -> int` (returns count created)
- `set_street_labels_visible(scene, visible: bool) -> None`

---

## Detailed Behavior (Pseudo)

### `ensure_street_labels_collection(scene)`
1. Find collection named `STREET_LABELS`.
2. If missing:
   - Create it and link it under `scene.collection`.
3. Enforce:
   - `hide_render = True`
   - `hide_viewport = True` (default hidden)
4. Return collection.

### `clear_street_labels(scene)`
1. Ensure collection exists.
2. Delete all objects linked to that collection (only those objects).
3. Return deleted count.
4. Keep collection itself (recommended) so the toggle works.

### `generate_street_labels(scene)`
1. Ensure collection exists.
2. Clear existing labels (idempotent).
3. Find candidate roads and names (see “Where To Get Names”).
4. Build unique label entries:
   - De-dupe by `(street_name, rounded_position)` to avoid duplicates.
5. Create text objects under the `STREET_LABELS` collection:
   - Set `hide_render = True`
6. Keep collection hidden by default after generating.
7. Return created count.

### UI toggle “Show Street Labels”
- Implementation: set `collection.hide_viewport = not show`
- Do not touch `hide_render` (always True).

---

## Testing & Audits

### Minimal sanity (must-do)
1. Register/unregister addon without errors.
2. Run “Fetch Route & Map”.
3. Confirm UI shows:
   - Toggle: Show Street Labels
   - Button: Generate Street Labels
   - Button: Clear Street Labels
4. Click Generate:
   - Creates `STREET_LABELS`
   - Creates at least 1 label object (if roads exist)
   - Collection remains hidden by default (viewport)
5. Toggle Show:
   - Labels appear/disappear in viewport
6. Confirm labels never render:
   - `STREET_LABELS.hide_render == True`
   - every label object `hide_render == True`
7. Click Clear:
   - Removes label objects
   - Safe to run multiple times

### Headless tests (recommended)
If feasible, add a small unit/integration test under:
- `cash-cab-addon/tests/`

Run:
- From `cash-cab-addon/`: `blender -b --python tests/test_runner.py`

Also run any existing audits the repo uses (examples from repo root):
- `python test_scene_audit_strict.py`
- `python test_render_settings_audit.py`

Environment note:
- Some environments need `TEMP`/`TMP` set to a writable dir (e.g. `%LOCALAPPDATA%\\Temp`)
- If OSM file writes fail, set `BLOSM_DATA_DIR` to a writable dir

---

## Diff Log Requirement (MANDATORY)

When implementing this feature, create a markdown diff log at:
- `cash-cab-addon/diffs/YYYY-MM-DD_street_labels_text_objects.md`

The diff log must include:
- Scope (files changed)
- Summary
- Key implementation notes:
  - how names were extracted
  - how “major roads” were chosen (or explain fallback to “all roads”)
  - how placement was computed
- How to test in Blender UI (2–3 steps; concise, numbered)
- Explicit PASS/FAIL checklist (copy the Acceptance Criteria below)

---

## Acceptance Criteria Checklist (copy into diff log)

- [ ] After Fetch Route & Map, UI shows: Show / Generate / Clear controls.
- [ ] Clicking Generate creates `STREET_LABELS` and adds ≥1 text label if roads exist.
- [ ] `STREET_LABELS` is hidden in viewport by default after generation until user toggles Show on.
- [ ] Labels never render (`collection.hide_render=True` and each label `obj.hide_render=True`).
- [ ] Clear removes only label objects and is safe to run repeatedly.
- [ ] No crashes if roads are missing; logs `[BLOSM] WARN street labels: ...` and no-ops.

