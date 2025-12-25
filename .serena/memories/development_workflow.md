# Development Workflow

## Making Changes

### Step 1: Establish Baseline
Before making any changes, run relevant test scripts to establish baseline:
- For pipeline/UI changes: `test_scene_audit_strict.py` and `test_render_settings_audit.py`
- For release candidates: `test_final_gate_run.py` with 3 Toronto routes
- For operator changes: `test_operator_invoke.py`

### Step 2: Document Changes
- Use `diffs/` directory to document all changes with dated markdown files
- Include: what changed, why it changed, testing performed

### Step 3: Selective Testing by Change Type

**Pipeline/UI Changes:**
- Run `test-and-audit/test_scene_audit_strict.py` (objects, roles, relationships)
- Run `test-and-audit/test_render_settings_audit.py` (Fast GI, AO, clamping)

**Animation/Route Changes:**
- Run `test-and-audit/test_e2e_camera_integration.py`
- Verify keyframes exist on ROUTE curve
- Check driver connections in Geometry Nodes

**Release Candidates:**
- Run `test-and-audit/test_final_gate_run.py` (3 Toronto routes)

**Operator Changes:**
- Run `test-and-audit/test_operator_invoke.py`

## Stability Principles

### Core Rules
1. **No broad refactors without approval** - Stability-first approach
2. **Maintain object naming conventions** - ROUTE, CAR_TRAIL, ROUTERIG_CAMERA, RouteTrace, _profile_curve
3. **Preserve blosm_role property system** - Object identification and cleanup depends on it
4. **Preserve animation driver connections** - Scene properties drive animations
5. **Keep CAR_TRAIL auto-generated** - Non-toggleable derived asset from ROUTE

### Protected Patterns
- Manager-Renderer-Layer architecture
- Multiple inheritance pattern (e.g., BuildingManager(BaseBuildingManager, Manager))
- BVH trees for spatial queries
- FOLLOW_PATH constraint for car animation
- Geometry Nodes with drivers for route trace animation

## Testing Strategy

### Use Maintained Test Harnesses
- **Preferred location**: `test-and-audit/` scripts
- **Avoid**: `tmp/` tests (temporary/duplicate copies)

### Test Coverage Types
1. **Comprehensive audit coverage** - Scene integrity, render settings, animation
2. **End-to-end validation** - Real Toronto routes
3. **Focused unit tests** - Individual components
4. **Asset validation** - Registry integrity checks

### Headless Testing Protocol
Use Blender's `--factory-startup` flag to avoid addon conflicts:
```bash
blender --factory-startup --python test-and-audit/test_scene_audit_strict.py
```

## Common Failure Patterns

### Scene Audit Failures
1. **Objects missing blosm_role property** - All created objects must have roles
2. **RENDER layer has no members** - Render layer configuration issue
3. **Scene properties not set** - Animation properties missing or incorrect

### Fix Strategy
- Run individual audit components to isolate issues
- Check console for `[CashCab] Warning:` messages
- Verify object naming and role assignment
- Validate scene properties are registered correctly

## Worktrees

Git worktrees enable parallel feature development:
- **wt_route_adjuster** - Route adjustment controls
- **wt_street_labels** - Street label feature
- **wt_bulk_importer** - Bulk import feature
- **wt_bulk_import_dev** - Bulk import dev

Each worktree has its own working directory but shares the git object database.

## Continuous Improvement

### Monitor
- Token usage and efficiency
- Test pass rates
- Performance metrics

### Refine
- Update test patterns as codebase evolves
- Improve documentation (CLAUDE.md, diffs/)
- Optimize workflows for speed

### Update Capabilities
- Keep agents aligned with current architecture
- Maintain prompt libraries
- Refresh memory files quarterly
