# CashCab Refactoring - Complete Orchestrator Guide

## Table of Contents
1. [Overview](#overview)
2. [Pre-Launch Checklist](#pre-launch-checklist)
3. [Setup Phase](#setup-phase)
4. [Execution Strategy](#execution-strategy)
5. [Step-by-Step Execution Plan](#step-by-step-execution-plan)
6. [Milestone Checkpoints](#milestone-checkpoints)
7. [Prompt Templates](#prompt-templates)
8. [Troubleshooting](#troubleshooting)
9. [Success Criteria](#success-criteria)

---

## Overview

This guide provides **complete step-by-step instructions** for orchestrating the 11-agent CashCab addon refactoring pipeline. It includes:
- Exact prompts to use at each phase
- MCP server integration instructions
- Milestone checkpoints for validation
- Progress tracking templates
- All commands and workflows needed

**Timeline:** 20 weeks (compressed)
**Agents:** 11 specialized agents across 3 phases
**Working Directory:** `C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\`

---

## Pre-Launch Checklist

### ✅ Verify Prerequisites

Before launching the orchestrator, verify:

- [ ] **Git Repository Clean**
  ```bash
  cd C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon
  git status
  # Should show: On branch bulk-importer, minimal uncommitted changes
  ```

- [ ] **All Agent Prompts Created**
  ```bash
  ls prompts/
  # Should show: 002-012 agent prompts (11 files total)
  ```

- [ ] **Directory Structure Ready**
  ```bash
  ls -la progress/ reports/
  # Both should exist with .gitkeep files
  ```

- [ ] **Tests Pass Before Starting**
  ```bash
  python -m pytest tests/ -v
  # All existing tests should pass
  ```

- [ ] **Backup Current State**
  ```bash
  git checkout -b backup-before-refactoring
  git push origin backup-before-refactoring
  git checkout bulk-importer
  ```

- [ ] **MCP Servers Available**
  - Task Orchestrator (mcp__MCP_DOCKER) ✅
  - Serena (mcp__serena) ✅
  - Repomix (mcp__repomix) ✅

---

## Setup Phase

### Step 1: Initialize Task Orchestrator Project

**Milestone 1: Project Structure Created**

**Prompt to Use:**
```
Create a Task Orchestrator project for the CashCab refactoring pipeline:

1. Create project with name "CashCab Refactoring"
2. Summary: "11-agent pipeline for performance optimization, code quality refactoring, and testing/documentation"
3. Tags: "refactoring, blender, addon, phase-2, phase-3, phase-4"
4. Status: "in-development"

Working directory: C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon
```

**Execute via MCP:**
```python
# Using mcp__MCP_DOCKER
create_project(
    name="CashCab Refactoring",
    summary="11-agent pipeline for performance optimization, code quality refactoring, and testing/documentation. Split into 3 phases: Performance (4 agents), Quality (4 agents), Testing/Docs (3 agents).",
    status="in-development",
    tags="refactoring,blender,addon,phase-2,phase-3,phase-4"
)
```

**Expected Output:** Project created with UUID, record in checkpoint

---

### Step 2: Create Phase Features

**Milestone 2: Features Created**

**Prompt to Use:**
```
Create 3 features in Task Orchestrator, one for each phase:

Feature 1: "Phase 2: Performance Optimization"
- Summary: "Agents 002-005: XML streaming parser, asset connection pooling, memory management, coordinate caching"
- Priority: "high"
- Status: "pending"
- Tags: "performance,optimization,phase-2"

Feature 2: "Phase 3: Code Quality Refactoring"
- Summary: "Agents 006-009: God object refactor, type hints, error handling, code deduplication"
- Priority: "high"
- Status: "pending"
- Tags: "quality,refactoring,phase-3"

Feature 3: "Phase 4: Testing & Documentation"
- Summary: "Agents 010-012: Security tests, route services tests, documentation generation"
- Priority: "high"
- Status: "pending"
- Tags: "testing,documentation,phase-4"
```

**Execute via MCP:**
```python
# Feature 1
create_feature(
    name="Phase 2: Performance Optimization",
    summary="Agents 002-005 implement XML streaming parser (40-60% memory reduction), asset connection pooling (30-50% improvement), memory management (<500MB growth), and coordinate caching (10-15% gain).",
    priority="high",
    status="pending",
    tags="performance,optimization,phase-2,xml,memory,caching"
)

# Feature 2
create_feature(
    name="Phase 3: Code Quality Refactoring",
    summary="Agents 006-009 split God Object into services, add 80% type hints, replace print() with logging, and reduce duplication from 15% to <5%.",
    priority="high",
    status="pending",
    tags="quality,refactoring,phase-3,type-hints,error-handling,deduplication"
)

# Feature 3
create_feature(
    name="Phase 4: Testing & Documentation",
    summary="Agents 010-012 create security test suite (30% coverage), route services unit tests with mocks (60% coverage), and comprehensive documentation (75% coverage).",
    priority="high",
    status="pending",
    tags="testing,documentation,phase-4,security,unit-tests"
)
```

**Expected Output:** 3 features created with UUIDs

---

### Step 3: Create Agent Tasks

**Milestone 3: All 11 Tasks Created**

Create tasks for each agent with proper dependencies. Below are the exact prompts to use:

#### Phase 2 Tasks

**Task 002:**
```python
create_task(
    title="Agent 002: XML Streaming Parser",
    summary="Replace ElementTree with iterparse() streaming parser in parse/osm/__init__.py and route/utils.py. Target: 40-60% memory and import time reduction. Creates parse/osm/streaming_parser.py and performance tests.",
    featureId="phase-2-feature-uuid",
    priority="high",
    complexity=7,
    tags="phase-2,performance,xml,parsing,streaming",
    status="pending"
)
```

**Task 003:**
```python
create_task(
    title="Agent 003: Asset Connection Pooling",
    summary="Implement AssetConnectionPool class in asset_manager/loader.py for .blend asset loading. Target: 30-50% performance improvement. Creates metadata caching and connection pool tests.",
    featureId="phase-2-feature-uuid",
    priority="high",
    complexity=6,
    tags="phase-2,performance,assets,connection-pool",
    status="pending"
)
```

**Task 004:**
```python
create_task(
    title="Agent 004: Memory Management",
    summary="Fix memory leaks, enhance garbage collection, add explicit BMesh cleanup in route/performance_optimizer.py and BMesh-heavy modules. Target: Reduce memory growth from 1-2GB to <500MB. Depends on Agent 002 for baseline metrics.",
    featureId="phase-2-feature-uuid",
    priority="high",
    complexity=8,
    tags="phase-2,performance,memory,garbage-collection,bmesh",
    status="pending"
)
```

**Task 005:**
```python
create_task(
    title="Agent 005: Coordinate Caching",
    summary="Implement LRU cache for coordinate transformations in route/utils.py. Target: 10-15% performance gain. Depends on Agents 002-004 for baseline metrics.",
    featureId="phase-2-feature-uuid",
    priority="medium",
    complexity=5,
    tags="phase-2,performance,caching,coordinates,lru",
    status="pending"
)
```

#### Phase 3 Tasks

**Task 006:**
```python
create_task(
    title="Agent 006: God Object Refactor",
    summary="Split route/fetch_operator.py (1,756 lines) into 4 focused services: geocoding_service.py, osm_fetch_service.py, route_object_service.py, animation_service.py. Target: <500 lines per module, 3-5 responsibilities per class.",
    featureId="phase-3-feature-uuid",
    priority="high",
    complexity=10,
    tags="phase-3,quality,refactor,god-object,services",
    status="pending"
)
```

**Task 007:**
```python
create_task(
    title="Agent 007: Type Hints",
    summary="Add comprehensive type hints to building/manager.py, building/renderer.py, osm/import_operator.py, bulk/panels.py. Target: 80% type hint coverage. Creates mypy_config.ini and type validation tests.",
    featureId="phase-3-feature-uuid",
    priority="medium",
    complexity=6,
    tags="phase-3,quality,type-hints,mypy,validation",
    status="pending"
)
```

**Task 008:**
```python
create_task(
    title="Agent 008: Error Handling Standardization",
    summary="Replace all print() statements with proper logging in all modules. Extend exception hierarchy in route/exceptions.py. Target: Zero print() statements (except tests). Creates core/logging.py if needed.",
    featureId="phase-3-feature-uuid",
    priority="high",
    complexity=5,
    tags="phase-3,quality,error-handling,logging,exceptions",
    status="pending"
)
```

**Task 009:**
```python
create_task(
    title="Agent 009: Code Deduplication",
    summary="Remove duplicate scene property registration (lines 177-205 from __init__.py), extract core/state_manager.py for consolidated state management. Target: Reduce code duplication from 15% to <5%. Depends on Agents 006-008 to avoid merge conflicts.",
    featureId="phase-3-feature-uuid",
    priority="medium",
    complexity=6,
    tags="phase-3,quality,deduplication,refactor,state",
    status="pending"
)
```

#### Phase 4 Tasks

**Task 010:**
```python
create_task(
    title="Agent 010: Security Tests",
    summary="Create comprehensive security test suite: test_api_keys.py, test_input_validation.py, test_code_execution.py, test_command_injection.py, test_xxe_protection.py. Target: 30% security test coverage. Can run in parallel with Agent 011.",
    featureId="phase-4-feature-uuid",
    priority="high",
    complexity=7,
    tags="phase-4,testing,security,vulnerabilities",
    status="pending"
)
```

**Task 011:**
```python
create_task(
    title="Agent 011: Route Services Tests",
    summary="Create unit tests for all route services with mocked external APIs (Google Maps, Overpass). Target: 60% route/services/ coverage. Depends on Agent 006 (services must exist). Can run in parallel with Agent 010.",
    featureId="phase-4-feature-uuid",
    priority="high",
    complexity=8,
    tags="phase-4,testing,unit-tests,mocks,services",
    status="pending"
)
```

**Task 012:**
```python
create_task(
    title="Agent 012: Documentation Generation",
    summary="Generate comprehensive documentation: docs/api_reference.md, CONTRIBUTING.md developer guide, docs/user_guide.md. Add module-level docstrings to all modules. Target: 75% documentation coverage. Depends on Agents 010-011 (stable codebase required).",
    featureId="phase-4-feature-uuid",
    priority="medium",
    complexity=6,
    tags="phase-4,documentation,api-reference,guides",
    status="pending"
)
```

**Expected Output:** 11 tasks created with UUIDs

---

### Step 4: Create Dependencies

**Milestone 4: Dependencies Configured**

**Prompt to Use:**
```
Create dependencies between tasks based on the agent dependency graph:

Dependencies to create:
1. Agent 005 BLOCKED BY Agents 002, 003, 004 (needs baseline metrics)
2. Agent 009 BLOCKED BY Agents 006, 007, 008 (avoid merge conflicts)
3. Agent 011 BLOCKED BY Agent 006 (services must exist first)
4. Agent 012 BLOCKED BY Agents 010, 011 (stable codebase required)

All other agents can run in parallel within their phase groups.
```

**Execute via MCP:**
```python
# Agent 005 depends on 002-004
create_dependency(
    fromTaskId="agent-005-task-uuid",
    toTaskId="agent-002-task-uuid",
    type="IS_BLOCKED_BY"
)
create_dependency(
    fromTaskId="agent-005-task-uuid",
    toTaskId="agent-003-task-uuid",
    type="IS_BLOCKED_BY"
)
create_dependency(
    fromTaskId="agent-005-task-uuid",
    toTaskId="agent-004-task-uuid",
    type="IS_BLOCKED_BY"
)

# Agent 009 depends on 006-008
create_dependency(
    fromTaskId="agent-009-task-uuid",
    toTaskId="agent-006-task-uuid",
    type="IS_BLOCKED_BY"
)
create_dependency(
    fromTaskId="agent-009-task-uuid",
    toTaskId="agent-007-task-uuid",
    type="IS_BLOCKED_BY"
)
create_dependency(
    fromTaskId="agent-009-task-uuid",
    toTaskId="agent-008-task-uuid",
    type="IS_BLOCKED_BY"
)

# Agent 011 depends on 006
create_dependency(
    fromTaskId="agent-011-task-uuid",
    toTaskId="agent-006-task-uuid",
    type="IS_BLOCKED_BY"
)

# Agent 012 depends on 010-011
create_dependency(
    fromTaskId="agent-012-task-uuid",
    toTaskId="agent-010-task-uuid",
    type="IS_BLOCKED_BY"
)
create_dependency(
    fromTaskId="agent-012-task-uuid",
    toTaskId="agent-011-task-uuid",
    type="IS_BLOCKED_BY"
)
```

**Expected Output:** Dependencies created, Task Orchestrator shows blocked tasks

---

## Execution Strategy

### Choose Your Approach

#### Option 1: Fully Automated (Fastest) ⭐⭐⭐
- Uses `/multi:orchestrate` command
- Launches all agents automatically
- Best for: Quick execution, minimal oversight
- Time: 1-2 hours active monitoring

#### Option 2: Orchestrator Agent (Recommended) ⭐⭐
- Creates dedicated orchestrator using `/create-agent`
- Step-by-step execution with checkpoints
- Best for: Control + automation balance
- Time: 2-3 hours across sessions

#### Option 3: Fully Manual (Learning)
- Execute each agent manually
- Best for: Learning system, complete control
- Time: 4-6 hours manual work

**RECOMMENDATION:** Use Option 2 for optimal balance of speed and control.

---

## Step-by-Step Execution Plan

### PHASE 0: Launch Orchestrator Agent

**Milestone 5: Orchestrator Agent Launched**

**Command:**
```bash
/create-agent cashcab-orchestrator "Expert orchestrator for 11-agent CashCab refactoring pipeline. Uses Task Orchestrator MCP for tracking, Serena for code operations, and manages dependencies, checkpoints, and phase gates across 3 phases (Performance, Quality, Testing/Docs)."
```

**Then provide the orchestrator with this comprehensive instruction prompt:**

---

### ORCHESTRATOR AGENT MASTER PROMPT

Copy and paste this entire prompt to the orchestrator agent:

```
You are the CashCab Refactoring Orchestrator. Your job is to coordinate 11 specialized agents across 3 phases to refactor the CashCab Blender addon.

## WORKING DIRECTORY
C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\

## YOUR RESPONSIBILITIES

1. Track all 11 agents using Task Orchestrator MCP
2. Launch agents in dependency-correct order
3. Monitor progress via checkpoint files in progress/ directory
4. Use Serena MCP for all code operations (more reliable than bash/Read)
5. Validate phase gates before proceeding
6. Handle failures with rollback and re-execution
7. Report progress after each agent and phase completion

## PHASE 2 EXECUTION PLAN (Week 1-4)

### Parallel Launch Group 1
Launch these 3 agents in PARALLEL (no dependencies):

**Agent 002 Prompt:**
```
Read prompts/002_xml_parsing_agent.md and execute all implementation steps:
1. Read checkpoint from Agent 002 (if exists)
2. Identify XML parsing bottlenecks in parse/osm/__init__.py
3. Replace ElementTree with iterparse() streaming parser
4. Create parse/osm/streaming_parser.py
5. Run testing procedures
6. Write checkpoint to progress/phase-2-agent-002-checkpoint.json
7. Update Task Orchestrator task status to "completed"

Use Serena MCP (mcp__serena) for code modifications:
- find_symbol to locate XML parsing functions
- replace_symbol_body to refactor functions
- search_for_pattern to find ElementTree usage

Target metrics: 40-60% memory reduction, 40-60% import time reduction
```

**Agent 003 Prompt:**
```
Read prompts/003_asset_loading_agent.md and execute all implementation steps:
1. Identify asset loading bottlenecks in asset_manager/loader.py
2. Implement AssetConnectionPool class
3. Add metadata caching
4. Run testing procedures
5. Write checkpoint to progress/phase-2-agent-003-checkpoint.json
6. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications.
Target metrics: 30-50% performance improvement
```

**Agent 004 Prompt:**
```
Read prompts/004_memory_management_agent.md and execute all implementation steps:
1. Read progress/phase-2-agent-002-checkpoint.json for baseline metrics
2. Identify memory leak sources in route/performance_optimizer.py
3. Enhance garbage collection triggers
4. Add explicit BMesh cleanup to all BMesh-heavy modules
5. Run testing procedures
6. Write checkpoint to progress/phase-2-agent-004-checkpoint.json
7. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications.
Target metrics: Reduce memory growth from 1-2GB to <500MB
```

**WAIT for all 3 agents to complete.**

**Validate Group 1:**
- Verify all 3 checkpoints show status: "completed"
- Verify all tests_passed lists have 3+ tests each
- Verify tests_failed lists are empty
- If any failed, rollback and re-launch

### Sequential Agent 005
**Agent 005 Prompt:**
```
Read prompts/005_coordinate_caching_agent.md and execute all implementation steps:
1. Read checkpoints from Agents 002-004 for baseline metrics
2. Identify coordinate transformation hotspots in route/utils.py
3. Design CoordinateCache utility with LRU cache
4. Integrate cache into transformation functions
5. Run testing procedures
6. Write checkpoint to progress/phase-2-agent-005-checkpoint.json
7. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications.
Target metrics: 10-15% performance gain
```

**Validate Phase 2 Gate:**
- Run all Phase 2 tests: python -m pytest tests/performance/ tests/unit/test_agent_00* -v
- Verify performance score 80/100
- Verify memory usage <500MB
- Verify import time reduced 40-60%
- Update Task Orchestrator "Phase 2" feature status to "completed"

## PHASE 3 EXECUTION PLAN (Week 5-14)

### Sequential Agent 006
**Agent 006 Prompt:**
```
Read prompts/006_god_object_refactor_agent.md and execute all implementation steps:
1. Analyze route/fetch_operator.py structure (1,756 lines)
2. Split into 4 focused services:
   - route/services/geocoding_service.py
   - route/services/osm_fetch_service.py
   - route/services/route_object_service.py
   - route/services/animation_service.py
3. Preserve animation driver connections
4. Run testing procedures
5. Write checkpoint to progress/phase-3-agent-006-checkpoint.json
6. Update Task Orchestrator task status to "completed"

Use Serena MCP for code operations:
- find_symbol to locate methods to extract
- insert_after_symbol to add new service files
- replace_symbol_body to refactor extracted methods
- find_referencing_symbols to update all call sites

Target metrics: <500 lines per module, 3-5 responsibilities per class
```

**WAIT for Agent 006 to complete.**

### Parallel Launch Group 2
Launch these 2 agents in PARALLEL (both depend only on 006):

**Agent 007 Prompt:**
```
Read prompts/007_type_hints_agent.md and execute all implementation steps:
1. Read progress/phase-3-agent-006-checkpoint.json to identify new service files
2. Add type hints to building/manager.py, building/renderer.py, osm/import_operator.py, bulk/panels.py
3. Create mypy_config.ini
4. Create type validation tests
5. Run mypy strict mode on all modified modules
6. Fix type errors until mypy passes
7. Run testing procedures
8. Write checkpoint to progress/phase-3-agent-007-checkpoint.json
9. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications.
Target metrics: 80% type hint coverage
```

**Agent 008 Prompt:**
```
Read prompts/008_error_handling_agent.md and execute all implementation steps:
1. Search for all print() statements: grep -rn "print(" cashcab/ | grep -v "test"
2. Replace print() with appropriate logging (error, warning, info, debug)
3. Standardize exception messages in route/exceptions.py
4. Create core/logging.py if centralized logging config needed
5. Create error handling consistency tests
6. Run testing procedures
7. Write checkpoint to progress/phase-3-agent-008-checkpoint.json
8. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications:
- search_for_pattern to find print() statements
- replace_content (regex mode) to replace print() with logging

Target metrics: Zero print() statements (except tests)
```

**WAIT for both agents to complete.**

**Validate Group 2:**
- Verify both checkpoints show status: "completed"
- Verify grep -rn "print(" cashcab/ | grep -v "test" | wc -l returns 0
- Verify mypy passes on all modified modules

### Sequential Agent 009
**Agent 009 Prompt:**
```
Read prompts/009_code_deduplication_agent.md and execute all implementation steps:
1. Read checkpoints from Agents 006-008 to understand refactored code
2. Run pylint to find duplicate code: pylint cashcab/ --disable=all --enable=duplicate-code
3. Remove duplicate scene property registration (lines 177-205 from __init__.py)
4. Create core/state_manager.py for consolidated state management
5. Run testing procedures
6. Verify code duplication reduced to <5%
7. Write checkpoint to progress/phase-3-agent-009-checkpoint.json
8. Update Task Orchestrator task status to "completed"

Use Serena MCP for code modifications.
Target metrics: Code duplication <5%
```

**Validate Phase 3 Gate:**
- Run all Phase 3 tests: python -m pytest tests/unit/test_agent_007* tests/unit/test_agent_008* tests/unit/test_agent_009* -v
- Verify quality score 75-80/100
- Verify type hint coverage 80%+
- Verify zero print() statements
- Verify code duplication <5%
- Update Task Orchestrator "Phase 3" feature status to "completed"

## PHASE 4 EXECUTION PLAN (Week 15-20)

### Parallel Launch Group 3
Launch these 2 agents in PARALLEL (both depend only on 006):

**Agent 010 Prompt:**
```
Read prompts/010_security_tests_agent.md and execute all implementation steps:
1. Read progress/phase-3-agent-008-checkpoint.json for error handling patterns
2. Identify security vulnerabilities in target modules
3. Create 5 security test files:
   - tests/security/test_api_keys.py
   - tests/security/test_input_validation.py
   - tests/security/test_code_execution.py
   - tests/security/test_command_injection.py
   - tests/security/test_xxe_protection.py
4. Ensure all tests are non-destructive
5. Run testing procedures
6. Write checkpoint to progress/phase-4-agent-010-checkpoint.json
7. Update Task Orchestrator task status to "completed"

Target metrics: 30% security test coverage
```

**Agent 011 Prompt:**
```
Read prompts/011_route_services_tests_agent.md and execute all implementation steps:
1. Read progress/phase-3-agent-006-checkpoint.json to identify created service files
2. Verify services exist: geocoding_service.py, osm_fetch_service.py, route_object_service.py, animation_service.py
3. Create unit tests for each service with mocked external APIs
4. Create mock utilities in tests/mocks/__init__.py
5. Run testing procedures
6. Write checkpoint to progress/phase-4-agent-011-checkpoint.json
7. Update Task Orchestrator task status to "completed"

Target metrics: 60% route/services/ coverage
```

**WAIT for both agents to complete.**

**Validate Group 3:**
- Verify both checkpoints show status: "completed"
- Verify security test coverage >=30%
- Verify route services coverage >=60%

### Sequential Agent 012
**Agent 012 Prompt:**
```
Read prompts/012_documentation_agent.md and execute all implementation steps:
1. Read checkpoints from Agents 010-011
2. Check documentation coverage: python -m pydocstyle cashcab/ --select=D100,D101,D102,D103 --statistics
3. Create docs/api_reference.md with complete API documentation
4. Create CONTRIBUTING.md developer guide
5. Create docs/user_guide.md user guide
6. Add module-level docstrings to all public modules
7. Add class docstrings to all public classes
8. Add function docstrings to all public functions
9. Use NumPy style docstring format
10. Run testing procedures
11. Write checkpoint to progress/phase-4-agent-012-checkpoint.json
12. Update Task Orchestrator task status to "completed"

Target metrics: 75% documentation coverage
```

**Validate Phase 4 Gate:**
- Run all Phase 4 tests: python -m pytest tests/security/ tests/unit/services/ -v
- Verify test coverage 40%+
- Verify security coverage 30%
- Verify documentation coverage 75%
- Update Task Orchestrator "Phase 4" feature status to "completed"

## MONITORING PROGRESS

After each agent completes, check the checkpoint file:
```bash
cat progress/phase-X-agent-00X-checkpoint.json | python -m json.tool
```

Verify:
- status: "completed"
- tests_failed: []
- metrics meet target values

Use Task Orchestrator MCP to track progress:
```python
# Get overview of all tasks
get_overview(summaryLength=100)

# Search for pending tasks
search_tasks(status="pending")

# Search for in-progress tasks
search_tasks(status="in-progress")
```

## HANDLING FAILURES

If an agent fails tests:

1. Read checkpoint to identify failed tests:
   ```bash
   cat progress/phase-X-agent-00X-checkpoint.json | grep tests_failed
   ```

2. Read test output to understand the error

3. Roll back changes using git:
   ```bash
   git checkout HEAD -- affected_file.py
   ```

4. Fix the issue identified in test output

5. Re-launch the agent with the same prompt

6. Re-validate tests

## PHASE GATE VALIDATION

Before proceeding to next phase, verify ALL criteria:

**Phase 2 Gate:**
- [ ] Performance score 80/100
- [ ] Memory usage <500MB (down from 1-2GB)
- [ ] Import time reduced 40-60%
- [ ] All Phase 2 tests pass (3/3 agents complete)

**Phase 3 Gate:**
- [ ] Quality score 75-80/100
- [ ] Type hints 80%+ coverage
- [ ] Zero print() statements (verified via grep)
- [ ] Code duplication <5%
- [ ] All Phase 3 tests pass (4/4 agents complete)

**Phase 4 Gate:**
- [ ] Test coverage 40%+
- [ ] Security test coverage 30%
- [ ] Route services coverage 60%
- [ ] Documentation coverage 75%
- [ ] All Phase 4 tests pass (3/3 agents complete)

## REPORTING

Report status after each:
- Agent completion (with metrics from checkpoint)
- Phase gate validation (with pass/fail for each criterion)
- Failure encountered (with rollback actions taken)

Final report should include:
- All 11 agents completed with timestamps
- All phase gates passed with validation results
- Final metrics comparison (before/after)
- Production readiness status

## MCP SERVERS TO USE

1. **Task Orchestrator (mcp__MCP_DOCKER)** ⭐⭐⭐
   - Track all agents as tasks
   - Manage dependencies
   - Monitor progress
   - Commands: create_task, update_task, get_overview, search_tasks

2. **Serena (mcp__serena)** ⭐⭐⭐
   - All code modifications
   - More reliable than bash/Read/Edit
   - Commands: find_symbol, replace_symbol_body, search_for_pattern, insert_after_symbol

3. **Repomix (mcp__repomix)** ⭐
   - Optional: Pre-refactoring codebase analysis
   - Use before Agent 006 to analyze god object
   - Commands: pack_codebase, grep_repomix_output

Begin execution now with Phase 2, Group 1 (Agents 002-004 in parallel).
```

---

## Milestone Checkpoints

### Milestone 6: Phase 2 Group 1 Launched ✅
**When:** After launching Agents 002, 003, 004
**Verify:**
- [ ] 3 agents running in parallel
- [ ] Task Orchestrator shows 3 tasks with status "in-progress"
- [ ] Serena being used for code operations

### Milestone 7: Phase 2 Group 1 Complete ✅
**When:** After Agents 002, 003, 004 finish
**Verify:**
- [ ] All 3 checkpoints exist with status "completed"
- [ ] All tests_passed lists populated
- [ ] All tests_failed lists empty
- [ ] Metrics meet targets:
  - [ ] Memory reduction 40-60% (Agent 002)
  - [ ] Performance improvement 30-50% (Agent 003)
  - [ ] Memory <500MB (Agent 004)

### Milestone 8: Phase 2 Complete ✅
**When:** After Agent 005 finishes
**Verify:**
- [ ] Agent 005 checkpoint shows status "completed"
- [ ] Phase 2 gate validation passed
- [ ] Task Orchestrator "Phase 2" feature status "completed"

### Milestone 9: Phase 3 Agent 006 Complete ✅
**When:** After Agent 006 finishes
**Verify:**
- [ ] 4 service files created in route/services/
- [ ] All services <500 lines
- [ ] Animation drivers preserved
- [ ] Tests pass
- [ ] Checkpoint written

### Milestone 10: Phase 3 Group 2 Complete ✅
**When:** After Agents 007, 008 finish
**Verify:**
- [ ] Type hint coverage 80%+
- [ ] Zero print() statements (grep verification passes)
- [ ] mypy passes on all modified modules
- [ ] Both checkpoints show status "completed"

### Milestone 11: Phase 3 Complete ✅
**When:** After Agent 009 finishes
**Verify:**
- [ ] Code duplication <5%
- [ ] Duplicate registration removed
- [ ] Phase 3 gate validation passed
- [ ] Task Orchestrator "Phase 3" feature status "completed"

### Milestone 12: Phase 4 Group 3 Complete ✅
**When:** After Agents 010, 011 finish
**Verify:**
- [ ] Security test coverage 30%+
- [ ] Route services coverage 60%+
- [ ] All security tests non-destructive
- [ ] External APIs properly mocked

### Milestone 13: Phase 4 Complete ✅
**When:** After Agent 012 finishes
**Verify:**
- [ ] Documentation coverage 75%+
- [ ] API reference complete
- [ ] Developer guide complete
- [ ] User guide complete
- [ ] Phase 4 gate validation passed
- [ ] Task Orchestrator "Phase 4" feature status "completed"

### Milestone 14: Refactoring Complete ✅
**When:** All phases validated
**Verify:**
- [ ] All 11 agents completed
- [ ] All 3 phase gates passed
- [ ] Final metrics meet all targets
- [ ] Production ready

---

## Prompt Templates

### Template: Agent Execution Prompt

Use this template for executing individual agents:

```
AGENT EXECUTION PROMPT FOR AGENT XXX

Read prompts/00X_agent_name.md and execute:

1. PREREQUISITE CHECK
   - Read checkpoint: progress/phase-Y-agent-ZZZ-checkpoint.json (if applicable)
   - Verify dependencies are complete
   - Update Task Orchestrator task status to "in-progress"

2. IMPLEMENTATION
   - Read files listed in "Files to Read" section
   - Make modifications listed in "Files to Modify" section
   - Create files listed in "Files to Create" section
   - Use Serena MCP for all code operations:
     * find_symbol to locate code
     * replace_symbol_body to refactor functions
     * search_for_pattern to find patterns
     * insert_after_symbol to add code

3. TESTING
   - Run testing procedures listed in prompt
   - Verify all tests pass
   - Record test results

4. CHECKPOINT
   - Write checkpoint to progress/phase-Y-agent-00X-checkpoint.json
   - Include all required fields:
     * agent_id: "00X"
     * agent_name: "Agent Name"
     * phase: Y
     * status: "completed" (or "failed" if tests fail)
     * timestamp: ISO8601 format
     * files_modified: [list of files]
     * files_created: [list of files]
     * tests_passed: [list of tests]
     * tests_failed: [list of tests]
     * metrics: {key: value}
     * handoff_notes: "Summary for next agent"
     * conflicts: [list of conflicts]

5. TASK UPDATE
   - Update Task Orchestrator task status to "completed"
   - Record metrics in task notes

6. REPORT
   - Report completion with metrics
   - Report any issues or conflicts
   - Recommend next steps

Target metrics from prompt: [list target metrics]

Working directory: C:\Users\Tyler\Dropbox\CASH_CAB_TYLER\cash-cab-addon-rollback\cash-cab-addon-dev-folder\cash-cab-addon\
```

### Template: Phase Gate Validation Prompt

Use this template for validating phase gates:

```
PHASE GATE VALIDATION PROMPT FOR PHASE X

Validate Phase X gate criteria:

1. RUN ALL TESTS
   ```bash
   python -m pytest tests/ -v
   ```
   - All tests should pass
   - Record test count and pass rate

2. VERIFY METRICS
   - [ ] Metric 1: [target value] - [actual value]
   - [ ] Metric 2: [target value] - [actual value]
   - [ ] Metric 3: [target value] - [actual value]

3. CHECKPOINT VALIDATION
   - Verify all Phase X checkpoints exist
   - Verify all show status: "completed"
   - Verify tests_failed lists are empty
   ```bash
   grep -l '"status": "completed"' progress/phase-X-*.json | wc -l
   ```
   Should show: [number of agents in phase]

4. UPDATE TASK ORCHESTRATOR
   - Set Phase X feature status to "completed"
   - Record gate validation results

5. REPORT RESULTS
   - Pass/Fail for each criterion
   - Overall gate status: PASSED or FAILED
   - If failed: which criteria failed and recommended actions

Phase X Gate: [PASSED/FAILED]

If PASSED: Proceed to next phase
If FAILED: Address failed criteria before proceeding
```

---

## Troubleshooting

### Issue: Agent Won't Launch

**Symptoms:** Task stays "pending", no execution starts

**Solutions:**
1. Check Task Orchestrator connection
2. Verify agent prompt file exists: `ls prompts/00X*`
3. Check for circular dependencies
4. Verify all prerequisite checkpoints exist

### Issue: Serena Operations Fail

**Symptoms:** find_symbol returns empty, replace_symbol_body fails

**Solutions:**
1. Verify Serena MCP is connected
2. Use get_symbols_overview first to understand file structure
3. Check file path is relative to project root
4. Fall back to Read/Edit if Serena unavailable

### Issue: Tests Fail Consistently

**Symptoms:** Same test fails across multiple re-runs

**Solutions:**
1. Check if test requirements are realistic
2. Verify baseline metrics are correct
3. Review implementation for bugs
4. Consider adjusting success criteria (document justification)

### Issue: Checkpoint File Not Created

**Symptoms:** progress/phase-X-agent-00X-checkpoint.json missing

**Solutions:**
1. Check file system permissions: `ls -la progress/`
2. Verify agent completed execution
3. Check console for error messages
4. Manually create checkpoint if agent succeeded but didn't write file

### Issue: Git Rollback Fails

**Symptoms:** git checkout doesn't restore file

**Solutions:**
1. Check git status: `git status`
2. Verify file was actually modified: `git diff file.py`
3. Use hard reset if needed: `git reset --hard HEAD`
4. Create backup branch before major operations

---

## Success Criteria

### Refactoring Complete When:

- [ ] **All 11 Agents Completed**
  - [ ] Agent 002 (XML Parser): ✅
  - [ ] Agent 003 (Asset Pooling): ✅
  - [ ] Agent 004 (Memory): ✅
  - [ ] Agent 005 (Caching): ✅
  - [ ] Agent 006 (God Object): ✅
  - [ ] Agent 007 (Type Hints): ✅
  - [ ] Agent 008 (Error Handling): ✅
  - [ ] Agent 009 (Deduplication): ✅
  - [ ] Agent 010 (Security Tests): ✅
  - [ ] Agent 011 (Service Tests): ✅
  - [ ] Agent 012 (Documentation): ✅

- [ ] **All 3 Phase Gates Validated**
  - [ ] Phase 2 Gate: Performance 80/100, Memory <500MB ✅
  - [ ] Phase 3 Gate: Quality 75-80/100, Types 80%, Duplication <5% ✅
  - [ ] Phase 4 Gate: Coverage 40%, Security 30%, Docs 75% ✅

- [ ] **All Existing Tests Pass**
  ```bash
  python -m pytest tests/ -v
  # Should show: X passed in Y seconds
  ```

- [ ] **No Critical Bugs Introduced**
  - [ ] Zero high-priority issues
  - [ ] Zero security vulnerabilities
  - [ ] Zero breaking changes to public API

- [ ] **Documentation Complete**
  - [ ] API reference: docs/api_reference.md ✅
  - [ ] Developer guide: CONTRIBUTING.md ✅
  - [ ] User guide: docs/user_guide.md ✅
  - [ ] All modules have docstrings ✅

### Production Ready When:

- [ ] All refactoring success criteria met
- [ ] End-to-end test passes (3 Toronto routes):
  ```bash
  python test-and-audit/test_final_gate_run.py
  ```
- [ ] Scene integrity audit passes:
  ```bash
  blender -b test.blend --python ..\\test-and-audit\\test_scene_audit_strict.py
  ```
- [ ] Render settings audit passes:
  ```bash
  blender -b test.blend --python ..\\test-and-audit\\test_render_settings_audit.py
  ```
- [ ] Rollback procedures tested and verified
- [ ] Team trained on new architecture
- [ ] Monitoring/alerting configured (if applicable)

---

## Quick Reference Commands

### Monitor Progress
```bash
# Count completed agents
grep -l '"status": "completed"' progress/*.json | wc -l

# Show pending agents
grep -l '"status": "pending"' progress/*.json

# View specific checkpoint
cat progress/phase-2-agent-002-checkpoint.json | python -m json.tool

# Watch all checkpoints in real-time
watch -n 5 'for f in progress/*.json; do echo "=== $f ==="; cat $f | python -m json.tool | head -20; done'
```

### Validate Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific phase tests
python -m pytest tests/performance/ tests/unit/test_agent_00* -v
python -m pytest tests/unit/test_agent_007* tests/unit/test_agent_008* tests/unit/test_agent_009* -v
python -m pytest tests/security/ tests/unit/services/ -v

# Generate coverage report
python -m pytest tests/ --cov=cashcab --cov-report=html:reports/coverage
```

### Check Metrics
```bash
# Check code duplication
pylint cashcab/ --disable=all --enable=duplicate-code | tee reports/duplication.txt

# Check for print() statements
grep -rn "print(" cashcab/ | grep -v "test" | wc -l
# Should return: 0

# Check type hint coverage
python -m pydocstyle cashcab/ --select=D100,D101,D102,D103 --statistics

# Check documentation coverage
python -m pydocstyle cashcab/ --select=D100,D101,D102,D103 --statistics
```

### Git Operations
```bash
# Create backup branch
git checkout -b backup-$(date +%Y%m%d)

# Rollback specific agent
git checkout HEAD -- file1.py file2.py

# Rollback entire phase (4 commits)
git reset --soft HEAD~4

# Commit successful agent
git add .
git commit -m "feat(agent-002): Implement XML streaming parser

- Replace ElementTree with iterparse() for 40-60% memory reduction
- Add parse/osm/streaming_parser.py
- Create performance tests
- Write checkpoint progress/phase-2-agent-002-checkpoint.json

Metrics:
- Memory reduction: 52%
- Import time reduction: 48%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Appendix: Complete Agent Prompt Directory

All agent prompts are located in `prompts/` directory:

**Phase 2 - Performance Optimization:**
- `prompts/002_xml_parsing_agent.md`
- `prompts/003_asset_loading_agent.md`
- `prompts/004_memory_management_agent.md`
- `prompts/005_coordinate_caching_agent.md`

**Phase 3 - Code Quality:**
- `prompts/006_god_object_refactor_agent.md`
- `prompts/007_type_hints_agent.md`
- `prompts/008_error_handling_agent.md`
- `prompts/009_code_deduplication_agent.md`

**Phase 4 - Testing & Documentation:**
- `prompts/010_security_tests_agent.md`
- `prompts/011_route_services_tests_agent.md`
- `prompts/012_documentation_agent.md`

---

**End of Complete Orchestrator Guide**

This guide provides everything needed to execute the 11-agent CashCab refactoring pipeline successfully. Follow the steps sequentially, validate each milestone, and use the provided prompt templates for consistent execution.

**Recommended Next Step:** Launch orchestrator agent using `/create-agent` command, then provide it with the "ORCHESTRATOR AGENT MASTER PROMPT" section above.

**Last Updated:** 2025-01-15
**Version:** 2.0 (Complete)
**Status:** Ready for Execution
