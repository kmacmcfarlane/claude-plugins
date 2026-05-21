# Dependency Tree Format

This is the exact format the `plan-architect` agent must produce. The orchestrator parses this file to schedule execution.

## Format Specification

```markdown
# Dependency Tree

source_plan: .claude/tasks/plan-2026-05-21T00-00-00Z.md
generated: 2026-05-21T14-30-00Z

---

## Inline Tasks

Tasks too interconnected for sub-agent delegation. The orchestrator handles these directly.

| Tasks | Reason |
|---|---|
| T3 + T4 | Both modify `internal/auth/middleware.go`; architectural decisions in T3 constrain T4 |

If none, write: *(none)*

---

## Groups

Groups execute sequentially (1 before 2 before 3). Tasks within a group execute in parallel.

### Group 1: Foundation

| ID | Task | Dependencies | Estimated Scope |
|----|------|-------------|-----------------|
| T1 | Define database schema and run migrations | none | 1 file create, 1 file modify |
| T2 | Add configuration for new feature flags | none | 2 files modify |

### Group 2: Core Implementation

| ID | Task | Dependencies | Estimated Scope |
|----|------|-------------|-----------------|
| T3 | Implement user service CRUD endpoints | T1 | 3 files create, 1 file modify |
| T4 | Implement auth middleware for new roles | T1 | 2 files create, 1 file modify |
| T5 | Build notification service integration | T2 | 2 files create |

### Group 3: Integration

| ID | Task | Dependencies | Estimated Scope |
|----|------|-------------|-----------------|
| T6 | Wire up API routes and middleware chain | T3, T4 | 1 file modify |
| T7 | Add notification triggers to user service | T3, T5 | 1 file modify |

### Group 4: Verification

| ID | Task | Dependencies | Estimated Scope |
|----|------|-------------|-----------------|
| T8 | Write integration tests for full user flow | T6, T7 | 2 files create |

---

## Notes

- T3 and T4 were originally one task in the plan ("implement user service"). Split because auth middleware is independently testable and unblocks T6 sooner.
- T5 has no dependency on T1 because it only configures the notification client — it doesn't touch the database.
- Estimated scope is advisory; the implementer should report actual files in IMPLEMENTER_REPORT.
```

## Field Reference

### Header Fields

- **source_plan**: Path to the plan file this tree was derived from.
- **generated**: UTC timestamp of when the tree was built (matches the session `TS`).

### Inline Tasks

A table of task clusters that should NOT be delegated to sub-agents. Each row names the tasks and explains why they're coupled. The orchestrator implements these directly in its session.

### Groups

Each group is a parallelization boundary:
- **ID**: Short identifier (T1, T2, ...) used in dependency references and orchestrator task tracking.
- **Task**: What the implementer should build — concise but unambiguous.
- **Dependencies**: Comma-separated list of task IDs that must complete before this task starts. `none` if independent.
- **Estimated Scope**: Rough count of files to create/modify. Helps the orchestrator judge if a task is right-sized.

### Notes

Free-form observations:
- Why tasks were split or merged relative to the original plan
- Risks or ambiguities the orchestrator should be aware of
- Assumptions about the codebase that informed dependency analysis
