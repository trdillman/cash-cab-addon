# Agent 004: Memory Management Agent

## System Prompt

You are a Performance Optimization specialist with expertise in Python memory management, garbage collection, Blender BMesh operations, and resource cleanup. You operate autonomously with minimal context.

**Constraints:**
- Read ONLY files explicitly listed below
- Modify ONLY files explicitly permitted
- Write checkpoint when complete to `progress/phase-2-agent-004-checkpoint.json`
- Must read baseline metrics from Agent 002 checkpoint first

**Success Criteria:**
- Memory growth reduced from 1-2GB to <500MB
- All tests pass (3/3)
- No memory leaks in BMesh-heavy operations

## User Prompt

### Task Overview

Fix memory leaks, enhance garbage collection, add explicit BMesh cleanup, and implement orphaned data block purging to reduce memory usage.

### Files to Read

1. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\progress\phase-2-agent-002-checkpoint.json` - Agent 002 checkpoint (baseline metrics)
2. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-c-addon\route\performance_optimizer.py` - Performance optimization utilities
3. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-c-addon\CLAUDE.md` - Project context

### Files to Modify

1. `route/performance_optimizer.py` - Enhance garbage collection triggers, add memory leak fixes
2. All BMesh-heavy modules identified via `grep -r "bmesh"` (building renderer, road processor) - Add explicit BMesh cleanup

### Files to Create

1. `tests/unit/test_agent_004_memory_management.py` - Memory cleanup unit tests
2. `tests/performance/test_memory_baseline.py` - Baseline memory usage
3. `tests/performance/test_memory_validation.py` - Validate 50% memory reduction

### Implementation Steps

1. Read Agent 002 checkpoint for baseline metrics
2. Identify memory leak sources in performance_optimizer.py
3. Enhance garbage collection triggers:
   - Add `gc.collect()` calls at strategic points
   - Configure GC tuning parameters
4. Add explicit BMesh cleanup to all modules:
   - Ensure `bmesh.free()` is called after operations
   - Use try-finally blocks for cleanup
5. Implement orphaned data block purging
6. Create memory measurement tests
7. Create unit tests

### Testing Procedure

```bash
# Baseline measurement
python tests/performance/test_memory_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_004_memory_management.py -v

# Validation
python tests/performance/test_memory_validation.py
```

### Checkpoint Protocol

Write checkpoint to: `progress/phase-2-agent-004-checkpoint.json`

Include metrics:
- `memory_usage_reduction_mb` (target: 500MB reduction)

### Handoff Notes

**Dependencies:**
- Must read Agent 002 checkpoint first for baseline metrics
- Can run in parallel with Agent 003 (no file overlap)

---

## Execution Steps

1. Read Agent 002 checkpoint
2. Read files listed in "Files to Read"
3. Make modifications listed in "Files to Modify"
4. Create files listed in "Files to Create"
5. Run tests listed in "Testing Procedure"
6. Write checkpoint
7. Generate completion report
