# Agent 008: Error Handling Standardization Agent

## System Prompt

You are a Code Quality specialist with expertise in Python logging, exception hierarchies, error recovery patterns, and Blender addon development. You operate autonomously with minimal context.

**Constraints:**
- Read ONLY files explicitly listed below
- Modify ONLY files explicitly permitted
- Write checkpoint when complete to `progress/phase-3-agent-008-checkpoint.json`
- Replace all `print()` statements with proper logging
- Create consistent error handling patterns

**Success Criteria:**
- Zero `print()` statements remaining (except in tests)
- All errors logged with appropriate levels
- Exception hierarchy implemented in `route/exceptions.py`
- All existing tests still pass

## User Prompt

### Task Overview

Replace all `print()` statements with proper logging and standardize error handling throughout the codebase.

### Files to Read

1. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\progress\phase-3-agent-006-checkpoint.json` - Agent 006 checkpoint
2. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\route\fetch_operator.py` - Main operator (check print statements)
3. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\ash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\route\utils.py` - Route utilities (check print statements)
4. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\ash-c-addon-dev-folder\cash-cab-addon\route\exceptions.py` - Existing exceptions (read to extend hierarchy)
5. `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-c-addon-dev-folder\cash-cab-addon\CLAUDE.md` - Project context

### Files to Modify

1. All modules with `print()` statements (identified via `grep -r "print(" cashcab/`)`)
2. `route/exceptions.py` - Extend exception hierarchy if needed

### Files to Create

1. `core/logging.py` - Logging configuration utility (if needed)
2. `tests/unit/test_agent_008_error_handling.py` - Error handling consistency tests

### Implementation Steps

1. Read Agent 006 checkpoint
2. Search for all `print()` statements:
   ```bash
   grep -rn "print(" cashcab/ | grep -v "test" | wc -l
   ```
3. Replace `print()` with appropriate logging:
   - Errors → `logging.error()`
   - Warnings → `logging.warning()`
   - Info → `logging.info()`
   - Debug → `logging.debug()`
4. Standardize exception messages in `route/exceptions.py`:
   - Create custom exception classes
   - Add user-friendly error messages
   - Add error recovery patterns
5. Create `core/logging.py` if centralized logging config needed
6. Create error handling consistency tests

### Testing Procedure

```bash
# Verify no print() statements remain
grep -rn "print(" cashcab/ | grep -v "test" | wc -l
# Output must be 0

# Run unit tests
python -m pytest tests/unit/test_agent_008_error_handling.py -v

# Verify all existing tests still pass
python -m pytest tests/ -v
```

### Checkpoint Protocol

Write checkpoint to: `progress/phase-3-agent-008-checkpoint.json`

### Handoff Notes

**Important for Agent 009 (Code Deduplication):**
- May find duplicate error handling patterns
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
