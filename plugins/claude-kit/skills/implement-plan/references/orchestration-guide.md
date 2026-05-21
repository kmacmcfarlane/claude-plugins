# Orchestration Guide

Detailed reference for the implement-plan skill's orchestration logic.

## Dependency Analysis Heuristics

When breaking a plan into a dependency tree, use these signals:

### Explicit Dependencies
- Task says "after X is done", "requires X", "depends on X"
- Task references files/APIs that another task creates
- Task says "using the X from step N"

### Implicit Dependencies
- **Schema before consumers**: Database migrations before code that queries new tables
- **Types before implementations**: Interface/type definitions before code that uses them
- **Infrastructure before application**: Config, env setup, build tooling before feature code
- **Shared utilities before features**: Helper functions, shared components before features that use them
- **Backend before frontend**: API endpoints before UI that calls them (unless mocked)

### Parallelizable Signals
- Tasks touch completely different files/directories
- Tasks are in different domains (e.g., one is CSS styling, another is database logic)
- Tasks are independent features with no shared state
- Tasks are different test suites

### Interconnection Signals (handle inline)
- Tasks modify the same file
- Task A's output is Task B's input AND they need iterative refinement together
- Tasks share complex state that's hard to describe in a prompt
- Architectural decisions in one task constrain another

## File Timestamp Convention

Two timestamps are in play:
- **Plan timestamp**: embedded in the plan filename (e.g., `plan-2026-05-21T00-00-00Z.md`) — when the plan was created.
- **Session timestamp (`TS`)**: generated once when the orchestrator starts — used for all outputs of that run (dependency tree, commits, etc.). These differ because you may run against an older plan.

```bash
TS=$(date -u '+%Y-%m-%dT%H-%M-%SZ')
```

Outputs:
- `.claude/tasks/dependency-tree-${TS}.md` — dependency tree for this run
- Plan file is read from the most recent `.claude/tasks/plan-*.md` (or user-specified path)

To find the most recent plan:
```bash
# Lexicographic sort works because the YYYY-MM-DDTHH-MM-SSZ format has fixed width
# and sorts chronologically. Do not change to a localized timestamp format.
ls -1 .claude/tasks/plan-*.md 2>/dev/null | sort -r | head -1
```

## Sub-Agent I/O Contracts

Structured blocks delimited by `_START` / `_END` markers ensure the orchestrator can reliably parse sub-agent output.

### Parsing Rules

1. The report block MUST be the **last thing** in the sub-agent's response. Nothing may appear after `_END`.
2. The format is **line-oriented**, not YAML. Each field is `key: value` on a single line, or `key:` followed by indented `  - item` lines.
3. Optional fields (test_output, notes) should be **omitted entirely** when not applicable — not set to empty or placeholder values.
4. **On parse failure**: re-prompt the sub-agent once asking for ONLY the report block. If the second attempt also fails, treat the task as BLOCKED and escalate to the user via AskUserQuestion.

### IMPLEMENTER_REPORT

Produced by: implementer sub-agent (after initial work or after addressing feedback).
Consumed by: orchestrator (to build shared context for downstream tasks) and reviewer (to verify accuracy and scope `git diff`).

```
IMPLEMENTER_REPORT_START
status: DONE
files_created:
  - path/to/new/file.go
files_modified:
  - path/to/changed/file.go
decisions:
  - Chose X over Y because Z
tests_run: passed
IMPLEMENTER_REPORT_END
```

Fields:
- **status**: `DONE` = task complete. `BLOCKED` = cannot proceed. If BLOCKED, the `notes` field must explain why.
- **files_created / files_modified**: Exhaustive list of files touched. The reviewer uses these to scope `git diff -- <paths>`. The orchestrator uses these for `git add`.
- **decisions**: Architectural or design choices not prescribed by the plan. Propagated to downstream tasks via shared context.
- **tests_run**: Exactly one of: `passed`, `failed`, `none`.
- **test_output** (optional): 1-2 line summary. Include only if tests_run is `failed`.
- **notes** (optional): Free-form. Include only if there are warnings, assumptions, or things downstream tasks need to know.

### REVIEW_VERDICT

Produced by: reviewer sub-agent.
Consumed by: orchestrator (to decide approve/reject/escalate).

```
REVIEW_VERDICT_START
result: APPROVED
summary: Implementation matches spec, tests pass
issues:
  - severity: minor
    file: path/to/file.go
    description: Consider renaming X for clarity
REVIEW_VERDICT_END
```

Fields:
- **result**: Exactly one of: `APPROVED` or `REJECTED`.
- **summary**: One line the orchestrator can log or display.
- **issues**: Structured list. Each item has three sub-fields: `severity` (critical/major/minor), `file`, `description`.
- If `APPROVED`, issues may be empty or contain only minor items.
- If `REJECTED`, there MUST be at least one critical or major issue.

### Context Propagation

**Only include reports from direct dependencies.** When building the Shared Context for task T6 (depends on: T3, T4), include IMPLEMENTER_REPORTs from T3 and T4 only — not from T1, T2, T5. This keeps prompts focused and prevents unbounded growth on large plans.

From each direct-dependency IMPLEMENTER_REPORT, extract:
1. `files_created` and `files_modified` — so the implementer knows what exists
2. `decisions` — so the implementer respects architectural choices
3. `notes` — so the implementer inherits warnings/assumptions

## Git Isolation

### Worktree-based isolation (parallel tasks)

Each parallel task runs with `isolation: "worktree"` on the Agent call. This gives the sub-agent its own working directory and branch (`worktree-agent-<id>`). The sub-agent commits in its worktree.

The reviewer runs against the worktree branch, using `git diff HEAD~1` to see only that task's changes.

### Commit strategy: once per group

Do NOT commit after each individual task. Instead:

1. All parallel tasks in a group run in isolated worktrees and commit there.
2. After all tasks in the group pass review, the orchestrator squash-merges each worktree branch into the main working tree:
   ```bash
   # For each approved worktree branch:
   git merge --squash worktree-agent-<id>
   # After all branches merged:
   git commit -m "implement-plan group [N]: [group name]

   Tasks:
   - [T1]: [summary]
   - [T2]: [summary]"
   # Clean up worktree branches:
   git branch -D worktree-agent-<id>
   ```
3. The next group's worktrees start from this committed state, so they have access to all prior work.

**Solo tasks** (groups with a single task) can run without worktree isolation since there's no parallel contamination risk. The orchestrator commits after the task passes review.

### Merge conflict handling

If `git merge --squash` conflicts (two parallel tasks touched the same lines despite being classified as independent), the orchestrator resolves the conflicts directly. It has the top-down view: both tasks' IMPLEMENTER_REPORTs, the plan, and the dependency tree. Use that context to make informed merge decisions. After resolving, continue with the group commit as normal.

### Why not commit per task?

Per-task commits create noisy git history and make it harder to review the plan as a whole. Group-level commits keep the history clean and allow a final holistic review of all changes together.

## Prompt Construction

### Implementer Prompt Template

The implementer prompt has six sections. All are required:

1. **Your Task**: The specific task, copied verbatim from the dependency tree row.
2. **Expected Scope**: The Estimated Scope from the dependency tree (e.g., "2 files create, 1 file modify"). Gives the reviewer something concrete to compare against.
3. **Plan Context**: The path to the full plan file.
4. **Shared Context**: Built from direct-dependency IMPLEMENTER_REPORTs only.
5. **Instructions**: Standard implementation instructions.
6. **Required Output Format**: The IMPLEMENTER_REPORT block specification with field definitions.

### Reviewer Prompt Template

The reviewer prompt has seven sections:

1. **Task That Was Implemented**: The task spec from the dependency tree.
2. **Expected Scope**: From the dependency tree row — gives the reviewer a baseline.
3. **Implementer Report**: The full IMPLEMENTER_REPORT block.
4. **Prior Review Verdicts**: All prior REVIEW_VERDICTs for this task (if re-review). Include a note: "The prior rejection was about [summary]. Verify those are fixed and check for new issues."
5. **Plan Context**: Path to the plan file.
6. **What to Review**: The 6 review criteria. For worktree tasks, use `git diff HEAD~1 -- <files>` (the sub-agent committed in the worktree). For non-worktree tasks, use `git diff -- <files>`.
7. **Required Output Format**: The REVIEW_VERDICT block specification with field definitions.

### Feedback Prompt (on reject)

On reject, spawn a fresh implementer. The prompt must include full prior context since the new agent has no memory of prior attempts:

1. The original task description and expected scope
2. All prior IMPLEMENTER_REPORTs for this task
3. All prior REVIEW_VERDICTs for this task
4. The attempt counter ("This is attempt 2/3")
5. Explicit instruction: "Fix the issues from the latest review. Do not start over."
6. Reminder to re-run tests
7. Reminder to include an IMPLEMENTER_REPORT at the end

See `todo.md` for planned SendMessage adoption, which would allow resuming the same agent with full context instead of re-constructing it.

## Orchestration State Tracking

Use Claude Code tasks to track execution state:

```
TaskCreate: "Group 1: Foundation" (parent)
  TaskCreate: "Task A: [name]" (child) — status: in_progress
  TaskCreate: "Task B: [name]" (child) — status: in_progress
TaskCreate: "Group 2: Core Features" (parent)
  TaskCreate: "Task C: [name]" (child) — status: pending
```

Update tasks as they complete. This gives the user visibility into progress.

## Review Cycle State

Track review attempts per task:

```
Task C: attempt 1/3
  - Implementer: done
  - Reviewer: REJECTED — "missing error handling in API endpoint"
  - Sending feedback to implementer...
Task C: attempt 2/3
  - Implementer: done (fixed)
  - Reviewer: APPROVED — verified prior issue fixed, no new issues
```

Note: each reviewer is fresh and stateless. Pass all prior verdicts so the new reviewer can verify prior issues are fixed rather than raising entirely different concerns (moving-target problem).

## Edge Cases

### Task produces no code changes
Some tasks are research/analysis. If an implementer reports "no code changes needed", the reviewer should still verify the analysis is correct and complete.

### Plan changes mid-execution
If the user modifies the plan during execution, re-read the plan file and re-analyze the dependency tree for remaining tasks. Completed tasks stay completed.

### Sub-agent crashes or times out
Treat as a failed attempt. Use AskUserQuestion to ask the user whether to retry, skip, or abort.

### Too many inline tasks
If the plan-architect flags >30% of tasks as interconnected (inline), the plan may not be well-suited for sub-agent delegation. Warn the user and offer options: re-plan with coarser boundaries, proceed with mostly-inline execution, or abort.

## Quality Signals

The orchestrator should monitor for these quality signals across the execution:

- **Test coverage**: Are new features tested?
- **Consistency**: Do sub-agents follow the same patterns?
- **Drift**: Is the implementation diverging from the plan?
- **Technical debt**: Are sub-agents taking shortcuts?

If you notice systemic issues, pause and discuss with the user rather than continuing to dispatch tasks that will accumulate the same problems.
