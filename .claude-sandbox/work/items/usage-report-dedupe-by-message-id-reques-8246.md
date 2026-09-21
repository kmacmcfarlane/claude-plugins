---
id: usage-report-dedupe-by-message-id-reques-8246
title: "usage-report: dedupe by (message.id, requestId) across all files, keep max output_tokens"
type: bug
status: done
priority: 1
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
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
- 2026-09-21 done: 9c54f46

## Dispatch
- dispatch: implementer opus — executable logic (usage_report.py)

## Implementer result
- round 1 DONE 120f1a4 (opus): key (message.id, requestId) across all files (session, project, --all), keep max output_tokens; missing requestId -> (id, None); missing id -> never deduped; --since on the kept line. 10 new tests, 9 fail on base. Open: cross-file dupes now count in duplicate_lines_dropped.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 120f1a4
- hand-computed totals match at session/project/--all; 50 file-order shuffles identical; idempotent; 200x2000-line corpus 2.4s/~200MB (base 1.6s/134MB).
- lows (author's call; implementer not resumed — landed as CLEAR): ties go to file-name sort order rather than the spending session (totals unaffected); --since applied per file before the cross-file pass (rare straddle counts a truncated copy); (id, None) key for lines without requestId departs from ccusage (which leaves them undeduped).
- decision (librarian): keep (id, None) — without it streamed lines lacking requestId count ~3x; where both ids exist the result matches ccusage. Told agents-61 (parity owner).
## Landed
- 9c54f46 (checks green in worktree and on main)
