# CashCab Addon - Agent-Executable Refactoring Specification

## Objective

Transform the high-level refactoring workflow into **detailed, agent-executable prompts** with:
- 12 specialized agent prompts (Phases 2-4: Performance, Quality, Testing/Docs)
- Zero-context dependency (fresh agents can pick up any step)
- State-based handoff mechanism (JSON checkpoint files)
- Dual progress tracking (Markdown + JSON)
- Specific testing procedures per agent
- Minimal context approach (file paths + success criteria only)

**Scope**: Skip security (handled by another team), focus on performance optimization (Phase 2) + code quality refactoring (Phase 3) + testing/documentation (Phase 4). **Timeline**: 20 weeks.

**Current Status**: Some refactoring already completed:
- ✅ Route services layer implemented (`route/services/` with base.py, google_maps.py, preparation.py)
- ✅ Type hints coverage at 78% (101/128 files)
- ⚠️ 659 print() statements still need logging conversion
- ⚠️ God object `route/fetch_operator.py` still at 1,780 lines (target: <500 per module)

---

## Recent Codebase Changes (as of 2025-01-15)

### Implemented Features (Pre-Refactoring)

**1. Route Services Layer (Partial God Object Refactor)**
- ✅ Created `route/services/` module structure
- ✅ Implemented `base.py` with `ServiceResult` and `ServiceError` abstractions
- ✅ Implemented `google_maps.py` for geocoding and route calculation (187 lines)
- ✅ Implemented `preparation.py` for route preparation services
- **Status**: Service layer exists but `fetch_operator.py` still 1,780 lines
- **Implication**: Agent 008 should extend existing services rather than create from scratch

**2. Type Hints (Near Completion)**
- ✅ 78% coverage (101/128 Python files use type hints)
- ⚠️ Target: 80%
- **Status**: Agent 009 work is mostly done, only need to add hints to remaining 27 files
- **Implication**: Agent 009 effort estimate can be reduced from 24 hours to ~4-6 hours

**3. Routerig Camera System**
- ✅ Added complete camera rig system (2,551 lines across 14 files)
- ✅ Implemented smooth camera keyframes and timeline alignment
- ✅ Added camera animation, spawning, and scene props
- **Status**: Complete, not in refactor scope
- **Implication**: None (separate module from route/)

**4. GUI Enhancements**
- ✅ Added 167 lines of operators and improved panels
- ✅ Added preferences system for Google API key
- ✅ Updated properties with better organization
- **Status**: Complete, minor cleanup may be needed

### Outstanding Issues

**1. Logging vs Print Statements**
- **Current**: 659 print() statements in non-test code
- **Target**: 0 print() statements (except tests)
- **Logging Usage**: Only 6 files import logging module
- **Implication**: Agent 010 has significant work ahead (16 hours estimate realistic)

**2. God Object (`route/fetch_operator.py`)**
- **Current**: 1,780 lines
- **Target**: <500 lines per module (split into 4 services)
- **Status**: Service layer exists but not fully utilized
- **Implication**: Agent 008 should refactor fetch_operator to delegate to existing services

**3. Code Duplication**
- **Current**: 15% duplication rate
- **Target**: <5%
- **Implication**: Agent 011 still needed (8 hours)

**4. Test Coverage**
- **Current**: 9.1% (26 test files exist)
- **Target**: 40%
- **Implication**: Agent 012 significant work ahead

---

## Live To-Do Checklist

### Quick Wins (No Dependencies)

- [ ] **Geocode Caching** (8 hours)
  - Implement LRU cache for address → coordinate mappings
  - Target: 100 ms/route savings, 90% hit rate
  - Quick win with high ROI
  - Can run immediately (Phase 2, Agent 003)

- [ ] **Code Cleanup** (4 hours)
  - Remove 200+ unused imports identified by code review
  - Fix 3 BOM encoding issues
  - Remove temporary files and safe commented code
  - Use generated cleanup script from Unused Code Cleaner agent
  - Can run in parallel with Phase 2 or Phase 3 (Agent 008)

---

### Phase 2: Performance Optimization (Weeks 1-4)

- [ ] **[002] XML Streaming Parser** (`prompts/002_xml_parsing_agent.md`)
  - Replace ElementTree with `iterparse()` streaming parser
  - Target: 40-60% memory and import time reduction
  - Output: `progress/phase-2-agent-002-checkpoint.json`

- [ ] **[003] Geocode Caching** (`prompts/003_geocode_caching_agent.md`)
  - Implement LRU cache for address → coordinate mappings
  - Target: 100 ms/route savings, 90% hit rate
  - Quick win with high ROI
  - No dependencies (can run immediately)
  - Output: `progress/phase-2-agent-003-checkpoint.json`

- [ ] **[004] Asset Connection Pooling** (`prompts/004_asset_loading_agent.md`)
  - Implement `AssetConnectionPool` for .blend asset loading
  - Target: 30-50% performance improvement
  - Output: `progress/phase-2-agent-004-checkpoint.json`

- [ ] **[005] Memory Management** (`prompts/005_memory_management_agent.md`)
  - Fix memory leaks, add BMesh cleanup, enhance garbage collection
  - Target: Reduce memory growth from 1-2GB to <500MB
  - Dependencies: Must read Agent 002 checkpoint first
  - Output: `progress/phase-2-agent-005-checkpoint.json`

- [ ] **[006] Coordinate Caching** (`prompts/006_coordinate_caching_agent.md`)
  - Implement LRU cache for coordinate transformations
  - Target: 10-15% performance gain
  - Dependencies: Must read Agents 002-005 checkpoints first
  - Output: `progress/phase-2-agent-006-checkpoint.json`

**Phase 2 Gate**: All 5 agents complete, performance score 62→80/100

---

### Phase 3: Code Quality Refactoring (Weeks 5-14)

- [ ] **[007] Code Cleanup** (`prompts/007_code_cleanup_agent.md`)
  - Remove 200+ unused imports identified by code review
  - Fix 3 BOM encoding issues
  - Remove temporary files and safe commented code
  - Use generated cleanup script from Unused Code Cleaner agent
  - No dependencies (can run anytime)
  - Output: `progress/phase-3-agent-007-checkpoint.json`

- [ ] **[008] God Object Refactor** (`prompts/008_god_object_refactor_agent.md`)
  - Split `route/fetch_operator.py` (1,780 lines) into 4 focused services
  - **Note**: `route/services/` already exists with base.py, google_maps.py, preparation.py
  - Target: Extend existing services, <500 lines per module, 3-5 responsibilities per class
  - Output: `progress/phase-3-agent-008-checkpoint.json`

- [ ] **[009] Type Hints** (`prompts/009_type_hints_agent.md`)
  - Add type hints to remaining modules (27 files missing hints)
  - **Note**: Already 78% complete (101/128 files have hints)
  - Target: 80% type hint coverage (only 2% more needed)
  - Estimated effort: 4-6 hours (reduced from 24 hours)
  - Output: `progress/phase-3-agent-009-checkpoint.json`

- [ ] **[010] Error Handling** (`prompts/010_error_handling_agent.md`)
  - Replace all `print()` with logging, standardize exceptions
  - Target: Zero `print()` statements (except tests)
  - Output: `progress/phase-3-agent-010-checkpoint.json`

- [ ] **[011] Code Deduplication** (`prompts/011_code_deduplication_agent.md`)
  - Remove duplicate property registration, extract shared utilities
  - Target: Reduce code duplication from 15% to <5%
  - Dependencies: MUST wait for Agents 008-010 (avoid merge conflicts)
  - Output: `progress/phase-3-agent-011-checkpoint.json`

**Phase 3 Gate**: All 5 agents complete, code quality score 58→75-80/100

---

### Phase 4: Testing & Documentation (Weeks 15-20)

- [ ] **[012] Route Services Tests** (`prompts/012_route_services_tests_agent.md`)
  - Create unit tests with mocked external APIs
  - Target: 60% route/services/ coverage
  - Dependencies: MUST wait for Agent 008
  - Output: `progress/phase-4-agent-012-checkpoint.json`

- [ ] **[013] Documentation** (`prompts/013_documentation_agent.md`)
  - Create API reference, developer guide, user guide
  - Target: 75% documentation coverage
  - Dependencies: MUST wait for Agent 012 (stable codebase)
  - Output: `progress/phase-4-agent-013-checkpoint.json`

**Phase 4 Gate**: Both agents complete, test coverage 9.1%→40%, documentation 48%→75%

---

## Agent Dependency Graph

```
Phase 2 (Performance) - Parallel groups:
├─ [002] XML Parsing ──────┐
├─ [003] Geocode Cache ────┤ (Quick Win, no dependencies)
├─ [004] Asset Loading ─────┤
├─ [005] Memory Management ─┤
└─ [006] Coordinate Caching* ┴──> [PHASE 2 GATE] ──┐

Quick Wins (Can run anytime):
├─ [003] Geocode Cache (Phase 2) ─┐
└─ [007] Code Cleanup (Phase 3) ───┴─> No dependencies

Phase 3 (Quality) - Parallel groups:
├─ [007] Code Cleanup ──────────────┐ (Quick Win, no dependencies)
├─ [008] God Object Refactor ────────┤
├─ [009] Type Hints ─────────────────┤
├─ [010] Error Handling ─────────────┤
└─ [011] Code Deduplication** ────────┴──> [PHASE 3 GATE] ──┤

Phase 4 (Testing/Docs) - Sequential:
├─ [012] Route Services Tests ─────────┴──> [PHASE 4 GATE] │
└─ [013] Documentation Generation***                        │

                                                        [FINAL GATE]
```

* Agent 006 waits for baseline metrics from Agents 002-005
** Agent 011 must wait for 008-010 to avoid merge conflicts
*** Agent 013 requires stable codebase from 012

---

## Progress Dashboard

### Overall Status

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Performance Score | 62/100 | 80/100 | Pending Phase 2 |
| Code Quality Score | 58/100 | 75-80/100 | Pending Phase 3 |
| Test Coverage | 9.1% | 40% | Pending Phase 4 |
| Documentation Coverage | 48% | 75% | Pending Phase 4 |
| Code Duplication | 15% | <5% | Pending Agent 011 |
| Memory Growth | 1-2GB | <500MB | Pending Agent 005 |
| Geocode Cache Hit Rate | 0% | 90% | Pending Agent 003 |
| Type Hints Coverage | 78% | 80% | ⚠️ Almost there (Agent 009) |
| Print Statements | 659 | 0 | Pending Agent 010 |
| Route Services Layer | ✅ Implemented | Complete | Pre-refactored |
| God Object Size | 1,780 lines | <500 lines | Pending Agent 008 |

### Agent Execution Status

| Phase | Agent | Name | Status | Checkpoint |
|-------|-------|------|--------|------------|
| 2 | 002 | XML Parsing | Pending | `progress/phase-2-agent-002-checkpoint.json` |
| 2 | 003 | Geocode Caching | Pending | `progress/phase-2-agent-003-checkpoint.json` |
| 2 | 004 | Asset Loading | Pending | `progress/phase-2-agent-004-checkpoint.json` |
| 2 | 005 | Memory Management | Pending | `progress/phase-2-agent-005-checkpoint.json` |
| 2 | 006 | Coordinate Caching | Pending | `progress/phase-2-agent-006-checkpoint.json` |
| 3 | 007 | Code Cleanup | Pending | `progress/phase-3-agent-007-checkpoint.json` |
| 3 | 008 | God Object Refactor | Pending | `progress/phase-3-agent-008-checkpoint.json` |
| 3 | 009 | Type Hints | Pending | `progress/phase-3-agent-009-checkpoint.json` |
| 3 | 010 | Error Handling | Pending | `progress/phase-3-agent-010-checkpoint.json` |
| 3 | 011 | Code Deduplication | Pending | `progress/phase-3-agent-011-checkpoint.json` |
| 4 | 012 | Route Services Tests | Pending | `progress/phase-4-agent-012-checkpoint.json` |
| 4 | 013 | Documentation | Pending | `progress/phase-4-agent-013-checkpoint.json` |

---

## Phase Gate Success Criteria

### Phase 2 Gate (after Agent 006)
- [ ] Performance score improved from 62 to 80/100
- [ ] Memory usage reduced by 500MB+
- [ ] Import time reduced by 40-60%
- [ ] Asset loading improved by 30-50%
- [ ] Coordinate transformations 10-15% faster
- [ ] Geocode caching achieves 90% hit rate
- [ ] All Phase 2 tests passing

### Phase 3 Gate (after Agent 011)
- [ ] Code quality score improved from 58 to 75-80/100
- [ ] No modules exceed 500 lines (except legacy)
- [ ] All classes have 3-5 responsibilities maximum
- [ ] Type hint coverage at 80%+
- [ ] Zero `print()` statements (except tests)
- [ ] Code duplication reduced to <5%
- [ ] All 200+ unused imports removed
- [ ] All Phase 3 tests passing

### Phase 4 Gate (after Agent 013)
- [ ] Test coverage increased from 9.1% to 40%
- [ ] Route services test coverage at 60%
- [ ] Documentation coverage at 75%
- [ ] API reference complete
- [ ] Developer guide complete
- [ ] User guide complete
- [ ] All Phase 4 tests passing

### Final Gate
- [ ] All 10 agents completed successfully
- [ ] All checkpoints validated
- [ ] All phase gates passed
- [ ] Rollback procedures tested
- [ ] Documentation complete
- [ ] Ready for production release

---

## Testing Procedures Per Phase

### Phase 2 Testing

**Agent 002 (XML Parsing):**
```bash
# Baseline measurement
python tests/performance/test_xml_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_002_xml_parsing.py -v

# Validation
python tests/performance/test_xml_validation.py
```

**Agent 003 (Geocode Caching):**
```bash
# Test cache hit rate
python tests/performance/test_geocode_cache.py

# Verify LRU cache behavior
python -m pytest tests/unit/test_geocode_cache.py -v
```

**Agent 004 (Asset Loading):**
```bash
# Baseline measurement
python tests/performance/test_asset_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_004_asset_loading.py -v

# Validation
python tests/performance/test_asset_validation.py
```

**Agent 005 (Memory Management):**
```bash
# Baseline measurement
python tests/performance/test_memory_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_005_memory_management.py -v

# Validation
python tests/performance/test_memory_validation.py
```

**Agent 006 (Coordinate Caching):**
```bash
# Baseline measurement
python tests/performance/test_coordinate_cache_baseline.py

# Run unit tests
python -m pytest tests/unit/test_agent_006_coordinate_cache.py -v

# Validation
python tests/performance/test_coordinate_cache_validation.py
```

### Phase 3 Testing

**Agent 007 (Code Cleanup):**
```bash
# Run cleanup script
python refactor/cleanup_script.py

# Verify no imports broken
python -m pytest tests/ -v

# Check for remaining unused imports
flake8 cashcab/ --select=F401
```

**Agent 008 (God Object Refactor):**
```bash
# Verify module size limits
python scripts/count_lines.py route/services/
# All must be <500 lines

# Verify responsibility count
python scripts/analyze_responsibilities.py route/services/
# All must have 3-5 responsibilities

# Run integration tests
python -m pytest tests/integration/test_agent_008_refactor.py -v
```

**Agent 009 (Type Hints):**
```bash
# Run mypy on target modules
mypy building/manager.py building/renderer.py osm/import_operator.py bulk/panels.py --strict

# Run unit tests
python -m pytest tests/unit/test_agent_009_type_hints.py -v

# Verify all existing tests still pass
python -m pytest tests/ -v
```

**Agent 010 (Error Handling):**
```bash
# Verify no print() statements remain
grep -rn "print(" cashcab/ | grep -v "test" | wc -l
# Output must be 0

# Run unit tests
python -m pytest tests/unit/test_agent_010_error_handling.py -v

# Verify all existing tests still pass
python -m pytest tests/ -v
```

**Agent 011 (Code Deduplication):**
```bash
# Measure code duplication
pylint cashcab/ --disable=all --enable=duplicate-code | tee reports/duplication_final.txt
# Must show <5% duplication

# Run unit tests
python -m pytest tests/unit/test_agent_011_deduplication.py -v

# Verify all existing tests still pass
python -m pytest tests/ -v
```

### Phase 4 Testing

**Agent 012 (Route Services Tests):**
```bash
# Run route services tests
python -m pytest tests/unit/services/ -v

# Verify all existing tests still pass
python -m pytest tests/ -v

# Generate coverage report for route/services/
python -m pytest tests/unit/services/ --cov=cashcab.route.services --cov-report=html:reports/services_coverage
# Must show >=60% coverage
```

**Agent 013 (Documentation):**
```bash
# Verify documentation coverage
python -m pydocstyle cashcab/ --select=D100,D101,D102,D103 --statistics
# Must show >=75% coverage

# Build documentation (if sphinx is used)
sphinx-build -b html docs/ docs/_build/html

# Verify all existing tests still pass
python -m pytest tests/ -v
```

---

## Rollback Procedures

### Per-Agent Rollback

Each agent creates a checkpoint before making changes. To rollback:

1. **Identify the agent checkpoint to revert:**
   ```bash
   # List checkpoints
   ls -la progress/

   # Read checkpoint to see files modified
   cat progress/phase-X-agent-XXX-checkpoint.json
   ```

2. **Restore files from git:**
   ```bash
   # Checkout modified files from checkpoint
   git checkout HEAD -- file1.py file2.py ...
   ```

3. **Remove created files:**
   ```bash
   # Delete files created by agent
   rm new_file1.py new_file2.py ...
   ```

4. **Validate rollback:**
   ```bash
   # Run all tests to ensure system is stable
   python -m pytest tests/ -v
   ```

### Phase Rollback

To rollback an entire phase:

1. **Identify all checkpoints in phase:**
   ```bash
   # List all checkpoints for phase
   ls progress/phase-X-*
   ```

2. **Rollback each agent in reverse order:**
   - Follow per-agent rollback procedure
   - Start from last agent, work backwards

3. **Validate phase rollback:**
   ```bash
   # Run all tests to ensure system is stable
   python -m pytest tests/ -v

   # Run phase-specific validation
   # (e.g., performance tests for Phase 2)
   ```

### Full Rollback

To rollback entire refactoring:

1. **Create rollback branch:**
   ```bash
   git checkout -b rollback/full-rollback
   ```

2. **Reset to pre-refactoring commit:**
   ```bash
   # Identify commit before refactoring started
   git log --oneline | head -20

   # Reset to that commit
   git reset --hard <commit-hash>
   ```

3. **Validate system:**
   ```bash
   # Run all tests
   python -m pytest tests/ -v

   # Run end-to-end tests
   python test-and-audit/test_final_gate_run.py
   ```

---

## Checkpoint JSON Schema

All agents read/write checkpoint files in `progress/` directory:

```json
{
  "agent_id": "002",
  "agent_name": "XML Parsing Optimization Agent",
  "phase": 2,
  "status": "completed",
  "timestamp": "2025-01-15T14:30:00Z",
  "files_modified": [
    "C:/.../parse/osm/__init__.py",
    "C:/.../route/utils.py"
  ],
  "files_created": [
    "C:/.../parse/osm/streaming_parser.py"
  ],
  "files_deleted": [],
  "tests_passed": [
    "test_streaming_parser_basic",
    "test_memory_usage",
    "test_backward_compat"
  ],
  "tests_failed": [],
  "metrics": {
    "memory_usage_reduction_mb": 450,
    "import_time_reduction_pct": 45
  },
  "next_steps": [
    "Agent 003 (Geocode Caching) can proceed in parallel",
    "Agent 004 (Asset Loading) can proceed in parallel"
  ],
  "handoff_notes": "Backward compatibility maintained. No conflicts detected.",
  "conflicts": []
}
```

---

## Critical Files Referenced

### Performance Issues (Phase 2)
- `route/fetch_operator.py` - God Object (1,780 lines, 40+ methods)
- `route/utils.py` - XML parsing bottleneck (40-60% of import time)
- `asset_manager/loader.py` - No connection pooling
- `route/performance_optimizer.py` - Memory leak sources

### Code Quality Issues (Phase 3)
- `route/fetch_operator.py` - God Object needing refactoring
- ⚠️ **Note**: Service layer exists at `route/services/` but not fully utilized
- `__init__.py` - Duplicate property registration (lines 121-149 vs 177-205)
- Multiple files - 659 print() statements (need logging conversion)
- 200+ unused imports across codebase

### Already Implemented (Pre-Refactoring)
- ✅ `route/services/base.py` - Service abstractions (ServiceResult, ServiceError)
- ✅ `route/services/google_maps.py` - Geocoding service (187 lines)
- ✅ `route/services/preparation.py` - Route preparation service
- ✅ Type hints in 78% of files (101/128)
- ✅ `routerig/` - Complete camera rig system (2,551 lines, not in refactor scope)

### Target Modules (Per Phase)

**Phase 2 (Performance):**
- `parse/osm/__init__.py` - XML streaming parser
- `route/utils.py` - Geocode caching + coordinate caching
- `asset_manager/loader.py` - Connection pooling
- `route/performance_optimizer.py` - Memory management

**Phase 3 (Quality):**
- `refactor/cleanup_script.py` - Code cleanup (auto-generated)
- `route/fetch_operator.py` - **Extend** existing services (don't create from scratch)
- **Type Hints** - Only 27 remaining files (78% already done)
- All modules with `print()` - Replace with logging (659 statements)
- `__init__.py` - Remove duplicate registration

**Phase 4 (Testing/Docs):**
- `tests/unit/services/` - Route services unit tests
- `docs/api_reference.md` - API documentation
- `CONTRIBUTING.md` - Developer guide
- `docs/user_guide.md` - User documentation

---

## Success Metrics

| Metric | Current | Target | Timeline | Notes |
|--------|---------|--------|----------|-------|
| Performance Score | 62/100 | 80/100 | 4 weeks | |
| Code Quality Score | 58/100 | 75-80/100 | 14 weeks | |
| Test Coverage | 9.1% | 40% | 20 weeks | 26 test files exist |
| Documentation Coverage | 48% | 75% | 20 weeks | |
| Code Duplication | 15% | <5% | 14 weeks | |
| Memory Growth | 1-2GB | <500MB | 4 weeks | |
| Type Hint Coverage | **78%** | 80% | **4-6 hours** | ⚠️ Almost there! |
| Geocode Cache Hit Rate | 0% | 90% | 4 weeks | |
| Unused Imports | 200+ | 0 | 4 hours | |
| Print Statements | **659** | 0 | 16 hours | Only 6 files use logging |
| Route Services Layer | **Implemented** | Complete | ✅ Done | Base abstractions exist |

---

## Template Files Reference

- **`prompts/_templates/checkpoint_schema.md`** - JSON schema for checkpoint files
- **`prompts/_templates/testing_procedure.md`** - Testing procedure template

---

## Execution Instructions for Agents

Each agent prompt follows this structure:

1. **System Prompt** - Role, expertise, constraints, success criteria
2. **User Prompt**:
   - Task Overview
   - Files to Read (with absolute paths)
   - Files to Modify (with absolute paths)
   - Files to Create (with absolute paths)
   - Implementation Steps
   - Testing Procedure (specific bash commands)
   - Checkpoint Protocol (JSON schema reference)
   - Handoff Notes (dependencies and next steps)
3. **Execution Steps** - Sequential workflow

**Zero-Context Dependency**: Each prompt includes only:
- File paths (absolute)
- Success criteria (measurable)
- Testing commands (copy-paste ready)
- Checkpoint location

No code explanations, no architectural context, no project history - just what the agent needs to do the job.

---

## Handoff Protocol

### Reading Checkpoints

Before starting, each agent MUST read relevant checkpoints:

```bash
# Read checkpoint JSON
cat progress/phase-X-agent-XXX-checkpoint.json

# Extract relevant information
# - files_modified (avoid conflicts)
# - metrics (baseline for comparison)
# - handoff_notes (important for next agent)
# - conflicts (known issues to watch for)
```

### Writing Checkpoints

After completion, each agent MUST write checkpoint:

```bash
# Create checkpoint JSON
cat > progress/phase-X-agent-XXX-checkpoint.json << 'EOF'
{
  "agent_id": "XXX",
  "agent_name": "Agent Name",
  "phase": X,
  "status": "completed",
  "timestamp": "2025-01-15T14:30:00Z",
  "files_modified": ["path1", "path2"],
  "files_created": ["path3"],
  "files_deleted": [],
  "tests_passed": ["test1", "test2"],
  "tests_failed": [],
  "metrics": {
    "metric1": value1,
    "metric2": value2
  },
  "next_steps": ["Next agents that can proceed"],
  "handoff_notes": "Important information for next agent",
  "conflicts": []
}
EOF
```

---

## Final Notes

### Parallel Execution Opportunities

**Can run in parallel:**
- Agents 002-004 (Phase 2) - XML Parsing, Geocode Caching, Asset Loading
- Agent 005 after 002-004 (Phase 2)
- Agent 006 after 002-005 (Phase 2)
- Agents 009-010 (Phase 3) - Type Hints, Error Handling
- Agent 007 (Phase 3) - Code Cleanup, anytime (no dependencies)

**Must run sequentially:**
- Agent 006 waits for 002-005
- Agent 011 waits for 008-010
- Agent 012 waits for 008
- Agent 013 waits for 012

### Stability Principles

- No broad refactors without approval
- Maintain object naming conventions
- Preserve animation driver connections
- Keep CAR_TRAIL as auto-generated derived asset
- All changes must pass existing tests

### Communication

- Update this master spec after each agent completes
- Mark completed agents with [X]
- Update progress dashboard metrics
- Document any deviations from plan

---

**End of Specification**

This specification is agent-executable and ready for implementation. Each of the 10 agent prompts in `prompts/` contains all necessary information for a zero-context agent to complete its task successfully.
