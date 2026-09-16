---
id: usage-report-transcript-parser-dedupe-pr-eff1
title: "usage-report: transcript parser, dedupe, price table, tests"
type: feature
status: doing
priority: 2
parent: spike-analyze-claude-code-usage-across-c-e5a7
owner: unknown@4d338747396e
claimed: 2026-09-16T17:33Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator approval 2026-09-16
---

F1 of the approved analyzer plan (see parent item and .claude-sandbox/investigations/analyze-usage/research.md). New skill dir plugins/claude-kit/skills/usage-report/ with scripts/usage_report.py (library + CLI skeleton) and tests/: walk ~/.claude/projects/<slug>/<sid>.jsonl and <sid>/subagents/agent-*.jsonl + .meta.json; dedupe usage by message.id per file; join each sub-agent file to its parent session and its requested tier (meta.model) and actual model (message.model); versioned price table as data (json) with cache read/write multipliers; compute tokens by class, Opus-equivalent normalised tokens, and list-price dollars; nested dispatches (spawnDepth 2+) rolled up into the parent dispatch by default with a flat option. Acceptance: unit tests on synthetic fixtures for dedupe (a 3-line split response counts once), sub-agent join, price lookup with unknown-model fallback (warn, not crash), roll-up; the SKILL.md for the skill is a stub that F2 completes; README catalog row is F2's. Approved answers: tokens by class + Opus-equivalent + labelled dollar estimate; default scope this project, --all and --since flags; CLI prints tables, --json; roll-up default, --flat; local estimate only, no API calls; new skill, not lib_context.py.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (scripts/, judgement)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer opus returned DONE, commit 028c697 (18 tests; real-data smoke: 17 sessions, 85 dispatches on this project). Open: three legacy model ids aliased to current same-family prices; Opus-equivalent = per-class tokens x price ratio. Reviewer opus round 1 dispatched 2026-09-16 17:41:46
- review round 1: reviewer wrote CLEAR but listed 1 medium (a usage line with no message.model is silently priced
  as the default model and bucketed under it, no warning) — librarian treats the verdict as NEEDS_CHANGES (a
  medium is never CLEAR). 5 lows: per-row rounding + no 'main' bucket in by_requested_tier; scope fallback is a
  string-prefix match and the docstring over-promises for worktrees; a docstring says 'run' but the regex is
  per-character; no test for file-scoped dedupe / missing .meta.json / empty scope; legacy price aliases invisible
  in the report. Hand cross-check of this session: tool == jq dedupe on all five figures. Lows 2 and 6 are
  report-surface gaps -> appended to F2 (7e8f). Fix round 1 sent 2026-09-16 17:47:26, tier unchanged (opus, resumed).
