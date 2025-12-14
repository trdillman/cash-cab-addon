# Feature Spec: Interactive Route Adjuster (Hook Empties + Road-Snapped Re-route)

## Summary

Add an **interactive route adjuster** to the CashCab Blender addon so users can **drag empties** (start/end + optional intermediate “control points”) and the route updates to follow roads.

The system must:
- Create **start** and **end** “hook” empties automatically after route import.
- Allow adding/removing **extra control empties** along the route for finer control.
- When a control empty moves, recompute the route polyline by snapping/solving to roads and update:
  - the `ROUTE` curve geometry
  - Start/End markers (empties) and any dependent objects (e.g., `CAR_TRAIL`)
  - preview animation remains valid

This spec is written so a new agent can implement it without prior repo knowledge.

---

## Goals

1. **Interactive editing**: User can drag start/end empties and see route update.
2. **Granular control**: User can add “via” empties along route; route passes through them.
3. **Correct snapping**: Route endpoints/via points snap to road centerlines using existing snapping logic; avoid wrong road classes.
4. **Non-destructive**: Store raw route + control state so changes can be reverted.
5. **Auditable**: Add tests/audits to verify the feature works headless and does not break existing imports.

---

## Non-goals (for first iteration)

- Full interactive pathfinding in viewport at 60 FPS for every mouse move. Use throttling/debounce.
- Turn-by-turn UI, lane guidance, or advanced constraints (avoid tolls, etc.).
- True dynamic topology editing of road networks in Blender.

---

## Definitions / Terms

- **ROUTE**: The imported route curve object (typically named `ROUTE`).
- **Control empties**: Empties that represent route constraints:
  - `ROUTE_CTRL_START`, `ROUTE_CTRL_END` (always present)
  - `ROUTE_CTRL_VIA_001`, `ROUTE_CTRL_VIA_002`, ... (optional)
- **Snapping**: Move a geographic point to the nearest appropriate road centerline using Overpass (existing code).
- **Reroute**: Query routing backend to produce a polyline between snapped control points.

---

## User Experience

### On route import
1. Route is imported normally (existing behavior).
2. Addon creates:
   - `ROUTE_CTRL_START` empty at route start.
   - `ROUTE_CTRL_END` empty at route end.
3. Addon optionally creates a `ROUTE_CTRL_COLLECTION` collection to keep these organized.
4. Addon enables a new “Interactive Route Adjuster” subsection in **Extra Features** panel.

### Editing
- User drags `ROUTE_CTRL_START` and/or `ROUTE_CTRL_END`.
- After drag ends (or throttled while dragging), addon:
  1. Converts empty world location → geographic coordinate.
  2. Snaps geo coordinate to road centerline (when enabled).
  3. Reroutes start→end (and via points in order) using routing service.
  4. Updates `ROUTE` curve points in local/projection space.
  5. Updates any dependent route objects (Start/End markers, CAR_TRAIL polyline, etc.).

### Adding via points
- UI: “Add Via Point” button.
- Behavior: creates `ROUTE_CTRL_VIA_###` empty near the current route (e.g., at a selected point or at mid-distance).
- UI: reorder via points (up/down) and delete.
- Each via point is treated as an intermediate waypoint for rerouting.

### Safety controls
- Toggle: `Enable Interactive Updates` (default OFF to avoid surprise heavy reroutes).
- Button: `Recompute Route Now` (manual recompute).
- Toggle: `Snap control points to roads` (default matches route snap default; currently OFF by default in addon).
- Display: last recompute time, route length/duration summary, and warnings if snapping/routing fails.

---

## Data Model / Storage

### Scene/Addon Properties (add to `cash-cab-addon/gui/properties.py`)
Add properties on the main addon PropertyGroup (`BlosmProperties`):

- `route_adjuster_enabled` (Bool, default False)
- `route_adjuster_live_update` (Bool, default False)
- `route_adjuster_snap_points` (Bool, default = existing `route_snap_to_road_centerline`)
- `route_adjuster_debounce_ms` (Int, default 250, min 0 max 2000)
- `route_adjuster_last_error` (String, read-only style)
- `route_adjuster_last_update_timestamp` (String or Float)

Control points collection:
- `route_control_points` (CollectionProperty of new `BlosmRouteControlPoint`)
  - `name` (string)
  - `role` enum: `START`, `END`, `VIA`
  - `object_name` (string)
  - `order` (int; for VIA ordering)

### Object custom properties
Store metadata on each control empty:
- `cc_route_ctrl_role`: `"START" | "END" | "VIA"`
- `cc_route_ctrl_index`: integer (VIA order index)
- `cc_route_ctrl_id`: stable id (uuid-like string) to survive renames

Store raw route geometry on `ROUTE` object (already used by U-turn trim):
- Keep using (or extend) existing raw storage keys in `cash-cab-addon/route/uturn_trim.py`:
  - `cc_route_raw_coords_flat`
  - `cc_route_raw_coords_count`

Add route-adjuster state keys on `ROUTE` object:
- `cc_route_ctrl_ids` (list of ids in order)
- `cc_route_ctrl_geos_flat` (optional, for debugging)
- `cc_route_provider` / `cc_route_snap_provider` (optional)

---

## Implementation Plan (Files / Responsibilities)

### 1) Core routing + snapping conversion utilities
Primary file(s):
- `cash-cab-addon/route/utils.py` (existing snapping, geocode parsing)
- `cash-cab-addon/route/fetch_operator.py` (existing route creation, uses projection)

New module recommended:
- `cash-cab-addon/route/route_adjuster.py`

`route_adjuster.py` responsibilities:
- Find current route object (`ROUTE` or configured name).
- Convert world XY back to geographic lat/lon:
  - Use existing `blenderApp.app.projection` inverse function if available.
  - If no inverse exists, add a helper in `cash-cab-addon/app/blender.py` or projection wrapper.
- Snap lat/lon to road centerline (call existing `_snap_to_road_centerline` logic; do not duplicate).
- Request route polyline from routing backend (reuse existing `prepare_route` / route service call path if possible).
- Convert returned geo polyline to projected coords for curve points.
- Update the `ROUTE` curve geometry safely:
  - Use existing route curve creation/update utilities (see `BLOSM_OT_FetchRouteMap._ensure_route_curve`).
- Preserve raw coords state as needed.

### 2) Control empty creation and management
Where to hook into import:
- After route creation in `cash-cab-addon/route/fetch_operator.py` (near where Start/End/Route objects are created and `context.scene.blosm_route_object_name` is set).

Add functions in `route_adjuster.py`:
- `ensure_route_control_empties(context, route_obj) -> None`
- `sync_control_empties_from_route(route_obj) -> None` (place empties at route endpoints and via points)
- `sync_route_from_control_empties(context) -> bool` (main “reroute now” entry)

Naming convention:
- Start: `ROUTE_CTRL_START`
- End: `ROUTE_CTRL_END`
- Via: `ROUTE_CTRL_VIA_###` (3 digits)

Collection:
- Create a collection named `ROUTE_CONTROLS` under the scene root collection and place empties there.

### 3) Detecting empty movement (live update)
Implement live update via a safe Blender pattern:

Option A (recommended): modal operator that runs while enabled
- Operator: `BLOSM_OT_RouteAdjusterLive`
- When started, it registers a timer and periodically checks:
  - control empties’ matrix_world (or location) vs cached values.
  - if changed, schedule recompute with debounce.

Option B: depsgraph update handler
- Register `bpy.app.handlers.depsgraph_update_post` and detect changes.
- Must throttle heavily to avoid recursion and performance issues.

Spec requirement:
- Use debounce `route_adjuster_debounce_ms`
- Do not reroute on every mouse move by default; only when `route_adjuster_live_update` is enabled.

### 4) GUI
File:
- `cash-cab-addon/gui/panels.py`

Add a new collapsible box in the existing **Extra Features** section:
- Label: `Interactive Route Adjuster`
- Controls:
  - `route_adjuster_enabled`
  - `route_adjuster_live_update`
  - `route_adjuster_snap_points`
  - `route_adjuster_debounce_ms`
  - Button: `Create/Sync Control Empties` (calls ensure + sync)
  - Button: `Recompute Route Now`
  - Via list UI:
    - “Add Via Point”
    - “Remove Via Point”
    - “Move Up/Down”
  - Readout: `Last Error` and last update time

### 5) Operators
File:
- `cash-cab-addon/gui/operators.py`

Add operators:
- `BLOSM_OT_RouteAdjusterCreateControls` (`blosm.route_adjuster_create_controls`)
- `BLOSM_OT_RouteAdjusterRecompute` (`blosm.route_adjuster_recompute`)
- `BLOSM_OT_RouteAdjusterAddVia` (`blosm.route_adjuster_add_via`)
- `BLOSM_OT_RouteAdjusterRemoveVia` (`blosm.route_adjuster_remove_via`)
- `BLOSM_OT_RouteAdjusterMoveViaUp/Down`
- `BLOSM_OT_RouteAdjusterLiveToggle` (optional; starts/stops modal live operator)

Register in:
- `cash-cab-addon/gui/__init__.py`

---

## Routing Behavior (Control Points → Route)

### Ordering
- Route always goes START → VIA(s) → END in VIA order.

### Snapping
- If `route_adjuster_snap_points` is enabled:
  - each control point is snapped to road centerline before routing.
- If disabled:
  - use raw projected inverse coords from empty.

### Reroute segments
- Compute route in segments:
  - START→VIA1, VIA1→VIA2, ..., VIALast→END
- Concatenate polylines, avoiding duplicate join points.

### Failures
- If routing fails for a segment:
  - Keep existing route geometry unchanged.
  - Set `route_adjuster_last_error` and report in operator.
- If snapping fails:
  - either fall back to raw point (configurable), or fail segment with clear error.

---

## Performance Considerations

- Debounce reroutes (default 250ms).
- Cache last snapped lat/lon per control id to avoid re-snapping unchanged points.
- Cache last route request (segment endpoints rounded to ~1e-6) to avoid redundant requests during micro-moves.

---

## Auditing / Testing

### Unit tests (math-only)
If new pure geometry helpers are added, place tests in:
- `cash-cab-addon/tests/`

Follow existing patterns:
- `unittest`
- run via Blender headless (see below)

### Integration tests (headless Blender)
Add a new test file:
- `cash-cab-addon/tests/test_route_adjuster_basic.py`

Test cases:
1. Import a small known route (reuse existing e2e patterns).
2. Ensure `ROUTE_CTRL_START` and `ROUTE_CTRL_END` are created.
3. Move start empty by a small delta (simulate user drag by setting location).
4. Run `Recompute Route Now` operator.
5. Assert route curve endpoints moved and remain near roads (basic sanity: non-zero change).
6. Add a via point, move it, recompute; verify route changes.

### Existing audits to run
From `cash-cab-addon/`:
- Core tests: `blender -b --python tests/test_runner.py`

From repo root (examples):
- `python test_scene_audit_strict.py`
- `python test_render_settings_audit.py`

### Local env notes
Some environments can’t write to `C:\WINDOWS\TEMP`; set:
- `TEMP` and `TMP` to a writable folder (e.g. `%LOCALAPPDATA%\Temp`)

If OSM data writing fails, set:
- `BLOSM_DATA_DIR` to a writable directory.

---

## Acceptance Criteria

1. After route import, start/end control empties exist and match route endpoints.
2. Dragging/moving a control empty and pressing “Recompute Route Now” updates the route to match the new point.
3. With snapping enabled, control points snap to sensible road centerlines (respect existing road filtering logic).
4. Adding/removing/reordering via points produces predictable reroutes.
5. Feature does not break existing route import, car trail drivers, or audits.
6. Headless tests pass.

---

## Implementation Notes / Pointers (Where to Look)

- Route import pipeline: `cash-cab-addon/route/fetch_operator.py`
- Snapping logic: `cash-cab-addon/route/utils.py` (`_snap_to_road_centerline` and related Overpass helpers)
- Post-import updates / CAR_TRAIL sync: `cash-cab-addon/route/pipeline_finalizer.py`
- GUI panels: `cash-cab-addon/gui/panels.py`
- GUI operators: `cash-cab-addon/gui/operators.py`
- Addon properties: `cash-cab-addon/gui/properties.py`
- Test runner: `cash-cab-addon/tests/test_runner.py`

