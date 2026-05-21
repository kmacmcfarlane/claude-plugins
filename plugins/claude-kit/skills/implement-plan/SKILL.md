---
name: implement-plan
description: Orchestrates plan implementation using sub-agents with dependency-aware parallel execution and iterative code review. Creates a plan from user instructions (or reads an existing one), builds a dependency tree, dispatches implementer sub-agents (parallel where safe), and runs review cycles with a hard cap before escalating. Requires agent definitions from the claude-kit plugin.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion, EnterPlanMode, ExitPlanMode
argument-hint: instructions or description of what to build
---

# Implement Plan

Orchestrate plan execution through sub-agents with dependency-aware scheduling and mandatory code review loops.

## Preconditions

Before starting, verify the agent definitions exist:

```bash
ls plugins/claude-kit/agents/{plan-architect,fullstack-developer,plan-reviewer}.md
```

If any are missing, stop and tell the user: "Missing agent definitions from the claude-kit plugin. Install with `/plugin install claude-kit@kmacmcfarlane`."

## Sub-Agent Definitions

This skill uses three agent definitions from `plugins/claude-kit/agents/`:

| Agent | subagent_type | Purpose |
|---|---|---|
| `plan-architect` | `plan-architect` | Analyzes plan, builds dependency tree |
| `fullstack-developer` | `fullstack-developer` | Implements one task at a time |
| `plan-reviewer` | `plan-reviewer` | Reviews implementer changes, produces verdict |

Agent `.md` files define the role, tools, and model. **Task-specific context (plan path, shared context, output format) is always injected via the Agent prompt**, not baked into the agent definitions.

## Critical Rules

- **Max 3 review-reject cycles per task.** After 3 failures, escalate to the user via AskUserQuestion with the feedback history.
- **On reject, spawn a fresh implementer** whose prompt carries forward: the task description, all prior IMPLEMENTER_REPORTs, all prior REVIEW_VERDICTs, and the attempt counter. See `references/todo.md` for future SendMessage adoption.
- **Spawn a fresh agent for each new task.**
- **Parallel tasks use worktree isolation.** Each parallel task runs with `isolation: "worktree"` so sub-agents don't see each other's changes.
- **Commit once per group, not per task.** After all tasks in a group pass review, squash-merge their worktree branches into the main working tree and commit once for the group. Between groups, the commit ensures the next group's worktrees start with prior work.
- **Every implementer return MUST be followed by a reviewer.** No task is complete until review passes.
- **Plan-reading is prompted in sub-agent input**, not baked into agent definitions. Always include the plan file path and relevant section in the Agent prompt.
- **Shared context includes only direct-dependency reports.** Do not accumulate every prior task's IMPLEMENTER_REPORT — only include reports from tasks listed in the current task's `Dependencies` column.

## File Conventions

Plans live in `.claude/plans/` using Claude Code's auto-generated naming convention (e.g., `ticklish-pondering-feather.md`). The dependency tree is written alongside the plan with a `-deps` suffix.

- **Plan file**: `.claude/plans/<name>.md` — created by plan mode or found from a prior session
- **Dependency tree**: `.claude/plans/<name>-deps.md` — created by the plan-architect agent

**Session timestamp (`TS`)** is still used for other outputs (logs, reports):
```bash
TS=$(date -u '+%Y-%m-%dT%H-%M-%SZ')
```

## Workflow

### Step 1: Create or Locate the Plan

The argument is **free-form user instructions** describing what to build or change.

First, check if a plan already exists from this session:
1. If the argument looks like a path to a plan file (e.g., ends in `.md`), read it directly.
2. Otherwise, check `.claude/plans/` for a recent plan — the user may have already gone through plan mode before invoking this skill:
   ```bash
   ls -1t .claude/plans/*.md 2>/dev/null | grep -v -- '-deps\.md$' | head -1
   ```
   If found, read it, present it to the user, and ask: "Use this existing plan, or create a new one from your instructions?"
3. Also review the conversation history for decisions, findings, or constraints the user discussed during prior plan-mode sessions that may not have been written into a plan file yet. If you find unincorporated context, fold it into the plan before proceeding.

If no existing plan applies, create one:
1. Enter plan mode with EnterPlanMode.
2. Analyze the codebase and the user's instructions to understand what needs to be done.
3. Write a plan to `.claude/plans/` (let plan mode generate the filename). The plan should contain:
   - **Goal**: what the user asked for
   - **Context**: relevant codebase observations
   - **Tasks**: discrete, implementable units of work with clear boundaries
   - **Dependencies**: which tasks depend on which
4. Exit plan mode with ExitPlanMode.
5. Present the plan to the user and get confirmation before proceeding. If they want changes, revise and re-present.

### Step 2: Build the Dependency Tree

Derive the dependency tree path from the plan filename:
```bash
# If plan is .claude/plans/ticklish-pondering-feather.md
# then deps go to .claude/plans/ticklish-pondering-feather-deps.md
PLAN_PATH=".claude/plans/<name>.md"
DEPS_PATH="${PLAN_PATH%.md}-deps.md"
```

Dispatch the plan-architect agent to analyze the plan and build the dependency tree:

```
Agent({
  subagent_type: "plan-architect",
  description: "Build dependency tree from plan",
  prompt: "Analyze the plan at [plan file path] and produce a dependency tree.

## Output Path
Write the dependency tree to [DEPS_PATH]

## Required Output Format
Write the dependency tree file AND return its contents. Use exactly the format documented in references/dependency-tree-example.md."
})
```

Read the generated dependency tree file.

**Inline budget check**: If more than ~30% of tasks are flagged as "Inline Tasks" (too interconnected for sub-agents), warn the user: "Most tasks are too interconnected for sub-agent delegation. Consider re-planning with coarser task boundaries, or proceed knowing most work will run in the orchestrator session." Use AskUserQuestion to let them choose: re-plan, proceed, or abort.

Present the dependency tree to the user and get confirmation before proceeding.

### Step 3: Execute Tasks

Process groups sequentially. Within each group, launch parallel Agent calls for independent tasks.

**Git isolation strategy**:
- Before starting each group, ensure the working tree is clean (`git status --porcelain` is empty).
- **Parallel tasks** (multiple tasks in one group): each task runs with `isolation: "worktree"`. The sub-agent commits in its worktree branch. After all tasks in the group pass review, the orchestrator squash-merges each worktree branch into the main working tree and commits once for the group.
- **Sequential tasks** (single task in a group): can run without worktree isolation since there's no parallel contamination risk. The orchestrator commits after the task passes review.
- The reviewer runs in the **same worktree** as the implementer (dispatch with the worktree branch checked out) so `git diff` sees only that task's changes.

**Squash-merge flow** (after all parallel tasks in a group pass review):
```bash
# For each approved worktree branch:
git merge --squash worktree-agent-[id]
# If merge conflicts arise, resolve them — you have the full context
# of both tasks' IMPLEMENTER_REPORTs to make informed decisions.
# After all branches merged:
git commit -m "implement-plan group [N]: [group name]

Tasks:
- [T1]: [summary]
- [T2]: [summary]"
# Clean up worktree branches:
git branch -D worktree-agent-[id]
```

For each task, use this pattern:

#### 3a: Dispatch Implementer

```
Agent({
  subagent_type: "fullstack-developer",
  isolation: "worktree",  // for parallel tasks; omit for solo tasks in a group
  description: "Implement: [task name]",
  prompt: "Your task is one piece of a larger plan.

## Your Task
[Paste the specific task description from the dependency tree]

## Expected Scope
[Paste the Estimated Scope from the dependency tree row, e.g. '2 files create, 1 file modify']

## Plan Context
Read the full plan at [plan file path] for broader context. Focus on your assigned task but ensure your work is compatible with the overall plan.

## Shared Context (from direct dependencies only)
[Paste IMPLEMENTER_REPORTs from tasks listed in this task's Dependencies column]

## Instructions
- Read the plan file first to understand the full picture
- Implement ONLY the assigned task
- Write clean, production-quality code
- Run any relevant tests or linters before finishing
- Commit your changes before finishing (required for worktree merge)

## Required Output Format
You MUST end your response with EXACTLY this block as the LAST thing in your response.
Nothing may appear after IMPLEMENTER_REPORT_END.

IMPLEMENTER_REPORT_START
status: DONE
files_created:
  - path/to/new/file.go
files_modified:
  - path/to/changed/file.go
decisions:
  - Chose X over Y because Z
  - Assumed A based on B
tests_run: passed
test_output: (omit if passed or none)
notes: (omit if nothing to report)
IMPLEMENTER_REPORT_END

Field values:
- status: DONE or BLOCKED (if blocked, explain in notes and stop)
- files_created / files_modified: one path per line, prefixed with '  - '
- decisions: one per line, prefixed with '  - '
- tests_run: exactly one of: passed, failed, none
- test_output: 1-2 line summary if failed, omit the field entirely if passed or none
- notes: free text, or omit the field entirely if nothing to report"
})
```

**If parsing the IMPLEMENTER_REPORT block fails** (missing delimiters, malformed fields): re-prompt the implementer once with: "Your response did not include a valid IMPLEMENTER_REPORT block. Please reply with ONLY the report block in the exact format specified." If the second attempt also fails, treat the task as BLOCKED and escalate to the user.

#### 3b: Dispatch Reviewer

After the implementer returns, dispatch a reviewer. For worktree tasks, the reviewer should run in the same worktree so it sees only that task's changes:

```
Agent({
  subagent_type: "plan-reviewer",
  description: "Review: [task name]",
  prompt: "Review the changes just made for one task in a larger plan.

## Task That Was Implemented
[Paste the specific task description]

## Expected Scope
[Paste the Estimated Scope from the dependency tree row]

## Implementer Report
[Paste the IMPLEMENTER_REPORT from the implementer's response]

## Prior Review Verdicts (if this is a re-review)
[Paste any prior REVIEW_VERDICTs for this task. If this is attempt 2+, include a note:
'The prior rejection was about [summary of prior issues]. Verify those are fixed and check for new issues.']

## Plan Context
Read the full plan at [plan file path] to understand the broader goals.

## What to Review
Run `git diff HEAD~1 -- [space-separated list of files from implementer report]` to see this task's changes. Check:
1. Correctness: Does the implementation match the task requirements?
2. Quality: Clean code, no obvious bugs, no security issues
3. Compatibility: Will this work with the rest of the plan?
4. Tests: Are there tests? Do they pass?
5. No scope creep: Only the assigned task was implemented — compare against Expected Scope
6. Report accuracy: Does the implementer report match what actually changed?

## Required Output Format
You MUST end your response with EXACTLY this block as the LAST thing in your response.
Nothing may appear after REVIEW_VERDICT_END.

REVIEW_VERDICT_START
result: APPROVED
summary: Implementation matches spec, tests pass
issues:
  - severity: minor
    file: path/to/file.go
    description: Consider renaming X for clarity
REVIEW_VERDICT_END

Field values:
- result: exactly one of: APPROVED or REJECTED
- summary: single line
- issues: list of items, each with severity (critical/major/minor), file, description
- If APPROVED, issues may be empty or minor only
- If REJECTED, there MUST be at least one critical or major issue"
})
```

**If parsing the REVIEW_VERDICT block fails**: re-prompt the reviewer once. If the second attempt fails, treat as REJECTED with a note "reviewer output unparseable" and escalate to the user.

#### 3c: Handle Review Result

Parse the `REVIEW_VERDICT` block from the reviewer's response.

- **APPROVED**: Mark task complete. Store the IMPLEMENTER_REPORT for use as shared context in downstream tasks. Do NOT commit yet — wait until all tasks in the group are approved, then squash-merge and commit once for the group (see Git isolation strategy above).

- **REJECTED (attempt < 3)**: Spawn a fresh implementer whose prompt includes:
  - The original task description and expected scope
  - All prior IMPLEMENTER_REPORTs for this task
  - All prior REVIEW_VERDICTs for this task
  - The attempt counter ("This is attempt N/3")
  - Instruction: "Fix the issues from the latest review. Do not start over — address the specific feedback. Re-run tests after fixing."
  Then dispatch a **fresh reviewer** whose prompt includes ALL prior REVIEW_VERDICTs for this task, with a note to verify prior issues are fixed.

- **REJECTED (attempt = 3)**: Escalate via AskUserQuestion:
  - Present: the task name, all 3 REVIEW_VERDICT blocks, current file state
  - Options: "Approve as-is", "I'll fix it manually", "Skip this task", "Abort plan execution"

### Step 4: Collect Execution Stats

Throughout Steps 1–3, the orchestrator must track stats for each sub-agent dispatch. Every Agent tool result includes a `<usage>` block:
```
<usage>total_tokens: 16188
tool_uses: 5
duration_ms: 701376</usage>
```

Parse these from each agent result. Record a wall clock start time at the beginning of the run (`date +%s`) and at the start/end of each group.

**Per-task stats to collect**:
- Task ID (from dependency tree)
- Review attempts (1 = passed first try, max 3)
- Files changed (from IMPLEMENTER_REPORT: count of files_created + files_modified)
- Execution mode: `parallel` (worktree) or `sequential` (inline)
- For each agent dispatch (implementer + reviewer, per attempt):
  - `total_tokens`
  - `tool_uses`
  - `duration_ms`
- Task outcome: `approved`, `escalated`, `skipped`, `blocked`

**Per-group stats** (aggregate from tasks):
- Group name (from dependency tree)
- Task IDs in this group
- Total tokens (sum across all agent dispatches in group)
- Total tool uses (sum)
- Group duration: for parallel groups, `max(task durations)` since they run concurrently; for sequential, sum
- Files changed (deduplicated across tasks)
- Tasks parallel vs sequential

### Step 5: Post-Completion Verification


After all groups complete:

1. Run the full test suite (if one exists).
2. Run linters/formatters (if configured).
3. **Categorize failures**:
   - **Failures in scope** (tests/lints for code this plan touched): treat as blocking. Spawn a fresh implementer to fix them, then re-review. These must pass before the plan is considered complete.
   - **Pre-existing failures** (tests/lints that were already failing before this plan ran): do NOT block plan completion. Handle in Step 5.
4. If in-scope checks pass: report summary — tasks completed, commits created, files changed.

### Step 6: Pre-Existing Issues (final)

If Step 4 found test or lint failures unrelated to this plan's changes, notify the user as the last thing before finishing:

"Plan implementation complete. Note: the following test/lint failures appear to be pre-existing (not caused by this plan's changes): [list failures]. These may warrant separate attention."

This is informational only — do not block, prompt for action, or attempt to fix.

### Step 7: Execution Report

After all work is complete, present a summary report. This is the final output of the skill.

**Per-Group Breakdown**:

```
## Group 1: [group name]
| Task | Attempts | Files Changed | Tokens | Tool Calls | Duration | Mode | Outcome |
|------|----------|---------------|--------|------------|----------|------|---------|
| T1   | 1        | 3             | 12,400 | 8          | 45s      | par  | approved |
| T2   | 2        | 2             | 24,100 | 15         | 92s      | par  | approved |
| **Group Total** | | **5** | **36,500** | **23** | **92s** | | |

## Group 2: [group name]
...
```

Duration for group total: `max(task durations)` if parallel, `sum(task durations)` if sequential.

**Summary**:

```
## Summary
| Metric | Value |
|--------|-------|
| Total tasks | 8 |
| Tasks approved | 7 |
| Tasks escalated | 1 |
| Tasks blocked/skipped | 0 |
| Parallel tasks | 5 |
| Sequential tasks | 3 |
| Total review attempts | 10 |
| Total files changed | 14 |
| Total tokens | 142,300 |
| Total tool calls | 87 |
| Total agent duration | 8m 12s |
| End-to-end wall clock | 10m 45s |
```

End-to-end wall clock = `date +%s` at finish minus `date +%s` at start of Step 1.
Agent duration = sum of all `duration_ms` from agent results (will exceed wall clock when tasks run in parallel — that's expected).

## Handling Interconnected Tasks

If the dependency tree analysis reveals tasks that are too interconnected to delegate:
- Flag them to the user: "Tasks X, Y, Z are highly interconnected. I recommend handling these inline rather than delegating to sub-agents."
- If the user agrees, implement those tasks directly in the orchestrator session.
- Still run a review sub-agent on the inline work.

## Troubleshooting

### Sub-agent loses context
Cause: Prompt didn't include enough shared context.
Fix: Include more detail from direct-dependency IMPLEMENTER_REPORTs in the "Shared Context" section.

### Review loop hits max attempts
Cause: Task may be under-specified or too complex for a single agent.
Fix: Split the task, provide more specific instructions, or handle it inline.

### Parallel tasks create merge conflicts
Cause: Tasks in the same group modified overlapping files despite being classified as independent.
Fix: Re-analyze dependencies — these tasks should not have been parallelized. Move one to a later group. Worktree isolation prevents file-level conflicts during implementation, but `git merge --squash` may still conflict if branches touch the same lines.

### Worktree branch not cleaned up
Cause: Orphaned worktree from a crashed or interrupted sub-agent.
Fix: `git worktree list` to find orphans, `git worktree remove <path>` to clean up.

## Reference

See `references/orchestration-guide.md` for detailed prompt templates and dependency analysis heuristics.
See `references/dependency-tree-example.md` for the exact dependency tree format.
See `references/todo.md` for planned improvements (SendMessage adoption, etc.).
