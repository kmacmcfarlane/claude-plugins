---
id: context-guard-ignore-transcript-token-co-428e
title: "context-guard: ignore transcript token counts written before the compaction started"
type: bug
status: doing
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:41Z
created: 2026-09-28
updated: 2026-09-28
refs:
  - spike bace
---

Fix from spike bace (series .claude-sandbox/investigations/bace-stale-depth-warning/, 00+01 CLEAR). Cause: the transcript's 100 ms write queue is not flushed before hooks, so a queued opener's UserPromptSubmit can read the last pre-compaction usage and score it against the fresh epoch (stale warning, latched bands, possible false HARD erase). Acceptance: the series' Proposed Fix and acceptance tests as revised by 01 (lib_context.py measure() drops counts stamped at or before epoch_at; cur_at carried through _SCAN_KEYS/snap/base/_cache_start; malformed → None; tests in test_lib_context.py and test_window_mirror.py incl. the cached-resume path and the HARD case), plus OQ1's 2 s sensor grace (EPOCH_GRACE_S) with a test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-context-guard-ignore-transcript-token-co-428e at .claude/worktrees/context-guard-ignore-transcript-token-co-428e, base main (23e09b5)
dispatch: implementer opus — hook code and tests (rule 2)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
agent: implementer a669542ca04a59ebf round 1
