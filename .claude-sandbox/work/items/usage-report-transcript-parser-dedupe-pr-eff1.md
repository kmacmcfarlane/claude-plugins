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
