---
id: usage-report-dedupe-by-message-id-reques-8246
title: "usage-report: dedupe by (message.id, requestId) across all files, keep max output_tokens"
type: bug
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-21T18:01Z
created: 2026-09-19
updated: 2026-09-21
refs:
  - "peer: agents-61 (uds 266.sock)"
---

From peer agents-61 (claude-analytics, operator decision 2026-09-19: fix in context-guard first, then retire into claude-analytics). usage_report.py:335-339 keeps the FIRST line per message.id, but only the LAST carries final output_tokens: output undercounted 39% overall, 85% for subagents. File-scoped dedupe also double-counts history copied by resumed/forked sessions (~10% cache over-count; 792 cross-file ids, all same requestId, no id reuse). Acceptance: key (message.id, requestId) across ALL files, keep the record with max output_tokens (ccusage 20.x parity, to the token); regression fixtures with differing usage per line and a cross-file resumed copy (current fixture tests:41-58 uses identical usage on every line, so it misses both). Evidence: claude-analytics/.claude-sandbox/investigations/agent-telemetry/r4-verify.md once saved.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic (usage_report.py)
