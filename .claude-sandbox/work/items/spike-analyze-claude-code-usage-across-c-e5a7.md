---
id: spike-analyze-claude-code-usage-across-c-e5a7
title: "spike: analyze Claude Code usage across conversations with a skill"
type: spike
status: doing
priority: 3
owner: unknown@4d338747396e
claimed: 2026-09-16T17:08Z
created: 2026-09-16
updated: 2026-09-18
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16: investigate how a skill could analyze token/model usage across conversations (per session, per model, per sub-agent dispatch), to measure the effect of model routing. Process when worked: background research agent first (transcript/JSONL locations, ccusage-style tools, statusline data, OTEL export), then an implementation plan reviewed by the operator, then implementation as child feature items.

## Handoff
- doing: F1 parser landed (cf5ddb1); F2 7e8f and F3 8482 held until plugin-factoring merges (usage-report moves to context-guard)
- next: after the merge: dispatch F2 (report tables, skill doc, catalog row; includes the by_requested_tier main bucket and legacy-alias visibility from the F1 review), then F3
- blocked: awaiting operator review of the plan (2026-09-16)
- learned: —

## Operator clarification (2026-09-16)
The research phase must include WEB research, not only local inspection. Goal: a robust
context of best practices with real examples found on the internet — how others measure
Claude Code / agent token usage across sessions and sub-agents (ccusage and similar tools,
OTEL/metrics exports, transcript JSONL parsing, cost dashboards, per-model breakdowns,
statusline integrations), what they report, and what they got wrong. The research agent
(background, web-enabled) writes a sourced findings file; the implementation plan cites it.

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: researcher opus — spike, judgement-heavy web synthesis (no implementer/reviewer role; recorded for the usage record)
research output: .claude-sandbox/investigations/analyze-usage/research.md (gitignored, host-persistent, the investigate/implement convention)

## Research phase done (2026-09-16)
Output: .claude-sandbox/investigations/analyze-usage/research.md (2,563 words, sourced, [V]/[R] marked).
Key verified facts: every sub-agent dispatch has its own JSONL + .meta.json under <session>/subagents/ with the
requested tier (model: sonnet/opus/fable/inherit), parentAgentId, spawnDepth, agentType; the JSONL carries the
actual message.model. costUSD is gone; cost is a local estimate. Trap: one API response is written as several
lines with identical usage (apiBlockIndex) — naive sums over-count ~3x; dedupe by message.id per session. ccusage
works but gives no per-dispatch rows and disagreed ~2.7x on cache-read with a hand dedupe. OTEL export has the
right attributes but is prospective only. lib_context.scan_usage is a depth gauge, not a spend meter.

## Librarian's proposed plan (awaiting operator review)
Approach A (native JSONL analyzer) as a new skill `usage-report` under plugins/claude-kit/skills/ with
scripts/usage_report.py; B (ccusage) only as a test oracle; C (OTEL) documented as the upgrade path.
Recommended answers to the research's open questions: (1) report tokens by class AND an Opus-equivalent
normalised figure; dollars as list-price estimate, labelled; (2) default: this project slug, --all and --since
flags; (3) slash command printing tables, --json for artifacts; (4) roll nested dispatches up into the parent
dispatch, with --flat; (5) self-consistent local estimate, with a documented /usage reconciliation step, no API;
(6) new skill + script, not lib_context.py (different concern; keep the statusline path untouched).
Factoring, on approval: F1 parser+dedupe+price table+tests (base main); F2 report/CLI+skill doc+README catalog
row (dep F1); F3 optional ccusage oracle test (dep F1). Routing: F1 opus (scripts/, judgement), F2 opus
(catalog), F3 sonnet.
