# Meta-Verification Procedure

Use this prompt to review a conversation log from a test run of the implement-plan skill. The goal is to verify the skill behaved as specified and surface divergences, bugs, or design weaknesses.

## Prerequisites

The reviewer needs access to:
- The conversation log from the test run (attach as a file if long)
- `SKILL.md`
- `references/orchestration-guide.md`
- `references/dependency-tree-example.md`

If running in a context that already has the skill docs loaded, the attachments are unnecessary.

## Verification Prompt

Paste or adapt the following into a fresh Claude session with the log and skill docs attached.

---

You are reviewing a conversation log from a test run of a Claude Code skill called `implement-plan`. The skill orchestrates plan execution through sub-agents with dependency-aware scheduling and a review loop. The SKILL.md, orchestration guide, and dependency tree format spec are attached.

Your job is to verify whether the skill behaved as specified and to surface any divergences, bugs, or design weaknesses revealed by the actual run.

### What to check

Work through these in order. For each, cite specific evidence from the log (quotes, turn numbers, or tool-call references).

#### 1. Plan location and reading

- Did the orchestrator locate the plan correctly (argument path, most-recent timestamped plan, or fallback glob)?
- Did it actually read the full plan before proceeding?

#### 2. Dependency tree construction

- Was the plan-architect sub-agent dispatched with a prompt containing the plan path and output path?
- Does the produced dependency tree match the format in `dependency-tree-example.md` (header fields, Inline Tasks section, Groups with ID/Task/Dependencies/Estimated Scope columns, Notes)?
- Was the tree presented to the user and was confirmation obtained before execution started?
- Is the dependency analysis defensible? Flag tasks that look mis-grouped (e.g., parallelized tasks that touch the same file, or sequential tasks that could have run in parallel).

#### 3. Task execution discipline

- Were groups executed sequentially?
- Within each group, were independent tasks actually dispatched in parallel (concurrent tool calls), or was it serialized?
- Was every implementer return followed by a reviewer dispatch, with no task marked complete before review approved?
- Was a fresh sub-agent spawned per new task (not reused across different tasks)?

#### 4. Sub-agent I/O contracts

- Did every implementer response end with a parseable `IMPLEMENTER_REPORT_START`/`_END` block containing all required fields (status, files_created, files_modified, decisions, tests_run; optional: test_output, notes)?
- Did every reviewer response end with a parseable `REVIEW_VERDICT_START`/`_END` block with result, summary, and issues?
- Were any blocks malformed, missing, duplicated, wrapped in code fences, or otherwise hard to parse? If so, how did the orchestrator handle it?
- For REJECTED verdicts, was there at least one critical or major issue as required?

#### 5. Review-reject cycle

- If any task was rejected, was the rejection feedback passed forward into the next implementer dispatch with the attempt counter and all prior REVIEW_VERDICTs?
- Was a new sub-agent spawned with the prior context embedded in the prompt? (The current design spawns fresh on reject — SendMessage is not yet available.)
- Was the 3-attempt cap respected? If a task hit 3 rejections, did the orchestrator stop and escalate to the user with the full feedback history?

#### 6. Context propagation

- For tasks with dependencies, did the implementer prompt's "Shared Context" section include relevant info from upstream tasks' IMPLEMENTER_REPORTs (files created/modified, decisions, notes)?
- Was Shared Context scoped to direct dependencies only, or did it grow unboundedly?

#### 7. Git isolation and worktree behavior

- Were parallel tasks dispatched with `isolation: "worktree"`?
- Did the reviewer's git diff show only the task's own changes, or did it pick up changes from sibling parallel tasks (cross-contamination)?
- Were worktree branches squash-merged after all tasks in a group passed review?
- Was there one commit per group (not per task)?
- Any merge conflicts? If so, did the orchestrator resolve them using its top-down context?

#### 8. State tracking

- Were TaskCreate/TaskUpdate/TaskGet/TaskList used to track orchestration state?
- Were statuses updated as tasks progressed?

#### 9. Post-completion verification (Steps 4-5)

- Did the orchestrator run the test suite and linters after all tasks completed?
- Were in-scope failures treated as blocking (fix and re-review)?
- Were pre-existing failures reported as informational at the end without blocking?

#### 10. Interconnected-task handling

- If the architect flagged any tasks as inline (too interconnected to delegate), were they handled directly in the orchestrator session?
- Was a review sub-agent still run on inline work?
- If >30% of tasks were flagged inline, was the user warned?

#### 11. File and timestamp conventions

- Were artifacts written to `.claude/tasks/` with the `YYYY-MM-DDTHH-MM-SSZ` format?
- Was a single `TS` value used consistently across all outputs in the run?

#### 12. Failure modes and escalations

- Any sub-agent crashes, timeouts, or empty responses? How were they handled?
- Did the orchestrator surface blockers to the user, or silently work around things?
- Were AskUserQuestion calls used at the specified escalation points?

#### 13. Quality drift

- Across the run, did implementer quality stay consistent or degrade?
- Any signs of scope creep, shortcut-taking, or skipped tests?
- Did sub-agents follow consistent patterns, or did each task look stylistically different?

### Output format

Produce a report with three sections:

**Conformance summary** — a table with one row per check above, columns: Check, Status (Pass / Partial / Fail / N/A), Evidence (one-line pointer to the log).

**Issues found** — for each Fail or Partial, a paragraph describing what happened, where in the log, why it matters, and a recommended fix to the SKILL.md or orchestration logic.

**Design observations** — anything the test run revealed about the design of the skill (not just execution): brittle assumptions, missing edge cases, prompts that produced unexpected behavior, contracts that didn't hold up in practice.

Be specific. "The reviewer didn't catch the bug" is not actionable; "in turn 47 the reviewer approved despite the implementer reporting tests_run: failed, suggesting the reviewer prompt doesn't enforce a test-status gate" is.

---

## Usage Tips

- **Long logs**: Attach the log as a file rather than pasting inline. Tell the reviewer to work through it section by section.
- **Already in context**: If the skill docs are already loaded (e.g., continuing a session), drop the "attached" framing from the prompt.
- **Focused re-runs**: If a specific class of failure dominates the run, re-run with a narrowed prompt focused on just that area for a deeper look.
