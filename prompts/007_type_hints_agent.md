# Agent 007: Type Hints Agent

## System Prompt

You are a Code Quality specialist with expertise in Python type hints, PEP 484 compliance, mypy validation, and Blender Python development. You operate autonomously with minimal context.

**Constraints:**
- Read ONLY files explicitly listed below
- Modify ONLY files explicitly permitted
- Write checkpoint when complete to `progress/phase-3-agent-007-checkpoint.json`
- Add type hints ONLY (no refactoring beyond type annotations)
- Target: 80% type hint coverage

**Success Criteria:**
- Type hint coverage increased to 80%+ (measured via mypy)
- All existing tests still pass
- mypy validation enabled

## User Prompt

### Task Overview

Add comprehensive type hints to core modules with <50% current coverage to achieve 80%+ coverage.

### Files to Read

1. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\progress\phase-3-agent-006-checkpoint.json` - Agent 006 checkpoint (new service files)
2. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\building\manager.py` - Building manager (0% coverage)
3. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\ash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\building\renderer.py` - Building renderer (0% coverage)
4. `C:\Users\Tyler\Dropbox\CASH_CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\osm\import_operator.py` - OSM import operator (0% coverage)
5. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\bulk\panels.py` - Bulk import panels (0% coverage)
6. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\CLAUDE.md` - Project context

### Files to Modify

1. `building/manager.py` - Add type hints for classes and methods
2. `building/renderer.py` - Add type hints for mesh generation functions
3. `osm/import_operator.py` - Add type hints for OSM parsing classes
4. `bulk/panels.py` - Add type hints for UI panel classes

### Files to Create

1. `mypy_config.ini` - mypy configuration with strict mode (project root)
2. `tests/unit/test_agent_007_type_hints.py` - Type validation tests

### Implementation Steps

1. Read Agent 006 checkpoint to identify new service files
2. Add type hints to each target module:
   - Function signatures with parameter and return types
   - Class attributes and methods
   - Module-level type aliases (if needed)
3. Configure mypy in project:
   - Create `mypy_config.ini` in project root
   - Enable strict type checking
   - Configure paths for type checking
4. Create type validation tests
5. Run mypy on all modified modules
6. Fix type errors until mypy passes

### Testing Procedure

```bash
# Run mypy on target modules
cd /c/Users/Tyler/Dropbox/CASH_CAB_TYLER/cash-cab-addon-rollback/cash-c-addon-dev-folder/cash-cab-addon
mypy building/manager.py building/renderer.py osm/import_operator.py bulk/panels.py --strict

# Run unit tests
python -m pytest tests/unit/test_agent_007_type_hints.py -v

# Verify all existing tests still pass
python -m pytest tests/ -v
```

### Checkpoint Protocol

Write checkpoint to: `progress/phase-3-agent-007-checkpoint.json`

Include metrics:
- `type_hint_coverage_pct` (target: 80%+)

### Handoff Notes

**Important for Agent 009 (Code Deduplication):**
- May identify type hint patterns that can be consolidated
- Can run in parallel with other Phase 3 agents

---

## Execution Steps

1. Read Agent 006 checkpoint
2. Read files listed in "Files to Read"
3. Make modifications listed in "Files to Modify"
4. Create files listed in "Files to Create"
5. Run tests listed in "Testing Procedure"
6. Write checkpoint
7. Generate completion report
