# Route Only Import Feature - Implementation Plan

## Goal
Replace the "Create Animated Route & Assets" toggle with a "Import Route Only" feature. This mode ensures a lightweight import (Route Curve + Empties only) for fast validation/debugging. It provides optional extras to include "Roads & Ground" or "CN Tower" (Landmark) via a dropdown/selection, while bypassing all other heavy assets (Water, etc.) and skipping unnecessary downloads.

## Proposed Changes

### GUI Properties (`gui/properties.py`)
- **Remove**: `route_create_preview_animation` BooleanProperty.
- **Add**: `route_import_only` BooleanProperty (Default: False).
    - Label: "Import Route Only"
    - Description: "Fast import mode: only imports the route curve and start/end empties. Bypasses buildings, water, and other assets unless specified."
- **Add**: `route_import_extras` EnumProperty (options={'ENUM_FLAG'}).
    - Items:
        - `('ROADS_GROUND', "Roads & Ground", "Include Road network and Ground plane")`
        - `('CN_TOWER', "CN Tower", "Include specific CN Tower landmark asset (Not full buildings)")`
    - Description: "Select additional features to import in Route Only mode".

### GUI Panels (`gui/panels.py`)
- **Modify**: `BLOSM_PT_RouteImport` draw method.
- **Remove**: UI for `route_create_preview_animation`.
- **Add**: Checked box for `route_import_only`.
- **Add**: If `route_import_only` is True, show `route_import_extras` (as a row/column of checkboxes or a multi-select menu).

### Route Fetch Operator (`route/fetch_operator.py`)
- **Modify**: `BLOSM_OT_FetchRouteMap.execute` and/or `_import_route`.
- **Logic Change**:
    - Determine `include_roads`, `include_buildings`, `include_water` based on mode.
    - **IF** `addon.route_import_only` is **True**:
        - `include_roads` = `('ROADS_GROUND' in addon.route_import_extras)`
        - **CN Tower Logic**: If `('CN_TOWER' in addon.route_import_extras)`, trigger specific import for CN Tower asset (landmark). DO NOT enable full OSM buildings.
        - `include_water` = `False` (Always bypassed in this mode)
        - `route_create_preview_animation` logic = `False` (RouteCam is deprecated/removed).
    - **ELSE** (`route_import_only` is **False** - Legacy/Full Mode):
        - `include_roads` = Standard properties (`addon.highways` etc.)
        - `include_buildings` = Standard properties (`addon.buildings`)
        - `include_water` = `True` (or standard property if re-introduced).
        - Maintain existing behavior for full import.

## Verification Plan

### Automated Tests
- Since this is a UI/Operator flow change, I will verify by running the operator in "Test Mode" or by inspecting the resulting scene objects in a python script if possible.

### Manual Verification
1.  **Check "Route Only" (No Extras)**:
    - Run `blosm.fetch_route_map`.
    - Verification: Ensure ONLY `Route` curve and `Route_Start`/`Route_End` empties exist. No `Buildings`, No `Roads`, No `Water`.
2.  **Check "Route Only" + "Roads & Ground"**:
    - Select "Roads & Ground" in Extras.
    - Run Import.
    - Verification: Ensure `Route` + `Roads` + `Ground` exist. No `Buildings`.
3.  **Check "Route Only" + "CN Tower"**:
    - Select "CN Tower" in Extras.
    - Run Import.
    - Verification: Ensure `Route` + `CN Tower` (Landmark) exist. No other buildings.
4.  **Confirm RouteCam Removed**:
    - Verify no camera animation tracks are generated.
