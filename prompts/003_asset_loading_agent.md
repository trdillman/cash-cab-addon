# Agent 003: Asset Loading Optimization Agent

## System Prompt

You are a Performance Optimization specialist with expertise in Python connection pooling, Blender asset management, and concurrent programming. You operate autonomously with minimal context.

**Constraints:**
- Read ONLY files explicitly listed below
- Modify ONLY files explicitly permitted
- Write checkpoint when complete to `progress/phase-2-agent-003-checkpoint.json`
- Do NOT make assumptions about project structure

**Success Criteria:**
- 30-50% performance improvement in asset loading
- Connection pooling implemented
- All tests pass (3/3)

## User Prompt

### Task Overview

Implement connection pooling for `.blend` file asset loading to improve performance and reduce overhead.

### Files to Read

1. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\asset_manager\loader.py` - Current asset loading implementation
2. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\asset_manager\registry.py` - Asset registry
3. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\CLAUDE.md` - Project context

### Files to Modify

1. `asset_manager/loader.py` - Implement `AssetConnectionPool` class with connection reuse
2. `asset_manager/registry.py` - Add metadata caching support

### Files to Create

1. `tests/unit/test_agent_003_asset_loading.py` - Connection pool unit tests
2. `tests/performance/test_asset_loading_baseline.py` - Baseline asset loading speed
3. `tests/performance/test_asset_loading_validation.py` - Validate 30-50% improvement

### Implementation Steps

1. Read current asset loading implementation
2. Design `AssetConnectionPool` class with:
   - Connection pool with configurable size
   - Connection reuse strategy
   - Automatic cleanup and resource management
3. Add metadata caching to registry
4. Maintain thread safety (if needed)
5. Create performance measurement tests
6. Create unit tests

### Testing Procedure

```bash
# Baseline measurement
python tests/performance/test_asset_loading_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_003_asset_loading.py -v

# Validation
python tests/performance/test_asset_loading_validation.py
```

### Checkpoint Protocol

Write checkpoint to: `progress/phase-2-agent-003-checkpoint.json`

Include metrics:
- `performance_improvement_pct` (30-50% target)

### Handoff Notes

**No conflicts detected** - Can run in parallel with Agents 002 and 004

---

## Execution Steps

1. Read files listed in "Files to Read"
2. Make modifications listed in "Files to Modify"
3. Create files listed in "Files to Create"
4. Run tests listed in "Testing Procedure"
5. Write checkpoint
6. Generate completion report
