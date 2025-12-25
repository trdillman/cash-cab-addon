# Task Completion Checklist for CashCab Addon

## Pre-Change Validation

### Before Making Any Changes
1. **Establish Baseline**: Run relevant test scripts to verify current functionality
2. **Document Purpose**: Create dated markdown file in `diffs/` directory describing intended changes
3. **Identify Test Strategy**: Determine which test scripts apply to the change type

## Testing Procedures by Change Type

### Pipeline/UI Changes
**Required Tests:**
```bash
# Scene integrity validation
python test-and-audit/test_scene_audit_strict.py

# Render settings validation
python test-and-audit/test_render_settings_audit.py
```

**Success Criteria:**
- All objects have required `blosm_role` property
- RENDER layer has members
- Scene properties correctly set
- Fast GI enabled, AO enabled, clamping values correct

### Animation/Route Changes
**Required Tests:**
```bash
# Scene audit (includes animation checks)
python test-and-audit/test_scene_audit_strict.py

# Camera integration testing
blender -b --python test-and-audit/test_e2e_camera_integration.py
```

**Success Criteria:**
- Keyframes exist on ROUTE curve
- Driver connections intact in Geometry Nodes
- Animation timing properties correct (blosm_anim_start/end, blosm_route_start/end)
- Camera rig properly animated

### Release Candidates
**Required Tests:**
```bash
# End-to-end validation with 3 Toronto routes
python test-and-audit/test_final_gate_run.py
```

**Success Criteria:**
- All 3 routes import successfully
- Scene audit passes for all generated .blend files
- Render settings applied correctly
- Animation plays through without errors

### Operator/Functionality Changes
**Required Tests:**
```bash
# Operator invocation tests
python test-and-audit/test_operator_invoke.py
```

## Headless Testing Protocol

### Preferred Testing Method
Use Blender's `--factory-startup` flag to avoid addon conflicts:
```bash
blender --factory-startup -b --python test-and-audit/test_scene_audit_strict.py
```

### Benefits
- Isolated testing environment
- No addon conflicts
- Reproducible results
- CI/CD compatible

## Validation Checklist Items

### Scene Integrity (test_scene_audit_strict.py)
- [ ] All objects have `blosm_role` property set
- [ ] Objects grouped by role correctly (route, road, building, water, environment)
- [ ] ROUTE curve exists with proper naming
- [ ] CAR_TRAIL derived from ROUTE
- [ ] ROUTERIG_CAMERA auto-generated
- [ ] RENDER layer has members
- [ ] Scene properties registered and accessible

### Render Settings (test_render_settings_audit.py)
- [ ] Fast GI enabled
- [ ] Ambient Occlusion enabled
- [ ] Indirect light clamping = 10.0
- [ ] Direct light clamping = 0.0

### Animation System
- [ ] FOLLOW_PATH constraint on car object
- [ ] Keyframes on ROUTE curve for car animation
- [ ] Geometry Nodes setup for RouteTrace
- [ ] Drivers connected to scene properties
- [ ] blosm_anim_start/end set correctly
- [ ] blosm_route_start/end set correctly
- [ ] blosm_lead_frames configured

### Object Roles Verification
- [ ] `route`: Route curves and animation objects
- [ ] `road`: Road geometry from OSM
- [ ] `building`: Building meshes
- [ ] `water`: Water surfaces and Toronto Islands
- [ ] `environment`: Ground, shoreline assets

## Post-Change Validation

### After Implementing Changes
1. **Re-run Baseline Tests**: Execute same tests used to establish baseline
2. **Compare Results**: Ensure no regressions introduced
3. **Update Documentation**: Update `diffs/` markdown with actual changes made
4. **Tag Issues**: Document any unexpected behaviors or test failures

## Common Failure Patterns

### Missing blosm_role Property
**Symptom:** Scene audit reports objects without roles
**Fix:** Ensure all created objects have `blosm_role` set during creation

### RENDER Layer Empty
**Symptom:** RENDER layer has no members
**Fix:** Verify objects are properly assigned to RENDER collection/layer

### Animation Timing Wrong
**Symptom:** Car or route animation doesn't play correctly
**Fix:** 
- Check blosm_anim_start/end and blosm_route_start/end values
- Verify keyframes exist on ROUTE curve
- Check driver connections in Geometry Nodes

### Buildings Missing
**Symptom:** OSM data imported but no buildings visible
**Fix:**
- Verify OSM data was imported (check for building objects)
- Check building layer visibility in outliner
- Ensure buildings have `blosm_role = "building"`

### CAR_TRAIL Not Visible
**Symptom:** CAR_TRAIL object not showing in viewport
**Fix:**
- Verify ROUTE curve exists
- Check bevel_factor_start/end values
- Adjust blosm_car_trail_*_adjust properties
- Ensure viewport visibility is on

## Asset Validation

### Before Asset Operations
```bash
# Update registry
python asset_manager/cli.py update

# Validate assets
python asset_manager/cli.py validate
```

### Success Criteria
- Registry correctly references all asset files
- Assets pass integrity checks
- No missing or corrupted assets

## Bulk Processing Validation

### Test Single Route First
```bash
# Test bulk pipeline with single route
blender -b --python bulk-pipeline-v2/bulk_import_v2.py -- test_input.csv test_output
```

### Success Criteria
- .blend file generated
- Scene audit passes
- No worker crashes
- Log files show successful completion
