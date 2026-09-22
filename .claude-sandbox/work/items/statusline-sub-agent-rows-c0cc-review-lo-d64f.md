---
id: statusline-sub-agent-rows-c0cc-review-lo-d64f
title: "statusline sub-agent rows: c0cc review lows"
type: bug
status: done
priority: 4
created: 2026-09-21
updated: 2026-09-22
closed: 2026-09-22
refs:
  - c0cc reviewer
---

From c0cc review r3 2026-09-21 (CLEAR with lows). (1) subagent_statusline._usage_in on a >1 MiB line counts the last "usage" key anywhere, not only message.usage (synthetic toolUseResult.usage read wrong; none in 768 real sidechains); (2) a usage object missing a field borrows it from any object within 2048 bytes — stop at the object's closing brace; (3) test a usage key/fields straddling a chunk edge (LINE_MAX 4096, key at LINE_MAX-3 and +1); (4) README catalog row (line ~85) and decision tree (~110) mirror the one-clause description / name subagentStatusLine.

## Handoff
- doing: implementer dispatched (opus, agent a46f875508daa4c69)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — renderer logic
- 2026-09-22 done: 455a96b

## Implementer result
- round 1 DONE 9a5132e (opus): streamed structural scanner (root → message → usage only, strings skipped); chunk-straddle tests; no borrowing; README catalog row + decision tree. Open: invalid JSON inside skipped values not detected; compact_boundary checked only in first 4096 bytes on the long path.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at 9a5132e
- acceptance 1-4 met; 205,978 real lines 0 mismatches; 2.06M fuzz runs, valid lines 0 mismatches, 0 exceptions. Both open questions judged not defects (compact markers all before byte 4096).
- [medium] Python-level loop per bracket/token: ~4.5 MB/s on dense structure; a >~20 MB dense line exceeds the 5 s kill, the cache offset never advances → every later tick killed, rows stuck on default. Fix: a deadline/token cap in _long_line marking the scan bad but returning n so the offset advances; test with a patched small cap.
- lows: _SKIP backtracking ~190 MB peak per 1 MiB chunk of "", (fix claim or possessive/atomic, or smaller chunk); commit-message timing wording (carried in merge message).
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE 964b9a5 (opus): LINE_SECS 1.0 per line + TICK_SECS 1.5 per tick (line passed over, offset advances, depth kept); stateless regexes (0 MiB growth vs 165); worst tick ~3 s; tests fail 2 without. Declined: commit wording (merge message).
- dispatch: reviewer opus — review r2 (same reviewer resumed)

## Review round 2 — CLEAR (opus) at 964b9a5
- lows not taken: unscanned remainder of a passed-over line read without a time limit (GB-sized only); docstring line length; escape at chunk edge not checked for control char (invalid JSON only).
- landed 455a96b
