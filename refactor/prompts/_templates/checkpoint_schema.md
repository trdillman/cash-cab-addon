# Checkpoint JSON Schema

All agents read and write checkpoint files in `progress/` using this JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CashCab Refactoring Agent Checkpoint",
  "type": "object",
  "required": ["agent_id", "agent_name", "phase", "status", "timestamp"],
  "properties": {
    "agent_id": {
      "type": "string",
      "description": "Agent identifier (e.g., '002', '003')",
      "pattern": "^\\d{3}$"
    },
    "agent_name": {
      "type": "string",
      "description": "Human-readable agent name (e.g., 'XML Parsing Optimization Agent')"
    },
    "phase": {
      "type": "integer",
      "description": "Phase number (2, 3, or 4)",
      "minimum": 2,
      "maximum": 4
    },
    "status": {
      "type": "string",
      "enum": ["pending", "in_progress", "completed", "failed", "blocked"],
      "description": "Agent execution status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of last update"
    },
    "files_modified": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of absolute file paths modified",
      "uniqueItems": true
    },
    "files_created": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of absolute file paths created",
      "uniqueItems": true
    },
    "files_deleted": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of absolute file paths deleted",
      "uniqueItems": true
    },
    "tests_passed": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of test names that passed",
      "uniqueItems": true
    },
    "tests_failed": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of test names that failed (if any)",
      "uniqueItems": true
    },
    "metrics": {
      "type": "object",
      "description": "Agent-specific performance metrics",
      "properties": {
        "memory_usage_reduction_mb": {"type": "number"},
        "import_time_reduction_pct": {"type": "number"},
        "performance_improvement_pct": {"type": "number"},
        "type_hint_coverage_pct": {"type": "number"},
        "code_duplication_pct": {"type": "number"},
        "test_coverage_pct": {"type": "number"},
        "documentation_coverage_pct": {"type": "number"}
      }
    },
    "next_steps": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Recommended next actions for dependent agents",
      "uniqueItems": true
    },
    "handoff_notes": {
      "type": "string",
      "description": "Free-form notes for the next agent (warnings, conflicts, recommendations)"
    },
    "conflicts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {"type": "string"},
          "conflicting_agents": {"type": "array", "items": {"type": "string"}},
          "resolution_strategy": {"type": "string"}
        }
      },
      "description": "File conflicts with other agents (if any)"
    }
  }
}
```

## Checkpoint Protocol

### Reading Checkpoints (at agent start)

Each agent should read previous phase checkpoints before starting work:

1. List all checkpoint files:
   ```bash
   ls progress/phase-*-checkpoint.json
   ```

2. Read all relevant checkpoint files:
   - Phase 2 agents: Read nothing (first phase)
   - Phase 3 agents: Read `progress/phase-2-checkpoint.json`
   - Phase 4 agents: Read `progress/phase-2-checkpoint.json` and `progress/phase-3-checkpoint.json`

3. Extract:
   - Files modified by previous agents (to avoid conflicts)
   - Handoff notes from previous agents
   - Any conflicts flagged

### Writing Checkpoints (at agent completion)

Each agent must write a checkpoint file after completing work:

1. Create checkpoint JSON following schema above
2. Write to: `progress/phase-N-agent-XXX-checkpoint.json` (where N = phase number, XXX = agent ID)
3. Include all required fields
4. Update phase checkpoint after all agents in phase complete

### Checkpoint File Locations

**Individual Agent Checkpoints:**
- `progress/phase-2-agent-002-checkpoint.json`
- `progress/phase-2-agent-003-checkpoint.json`
- ... etc

**Phase-Level Checkpoints (created after all agents in phase complete):**
- `progress/phase-2-checkpoint.json` - Consolidates all Phase 2 agent checkpoints
- `progress/phase-3-checkpoint.json` - Consolidates all Phase 3 agent checkpoints
- `progress/phase-4-checkpoint.json` - Consolidates all Phase 4 agent checkpoints
