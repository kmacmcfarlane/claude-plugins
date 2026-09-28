---
id: context-guard-ignore-transcript-token-co-428e
title: "context-guard: ignore transcript token counts written before the compaction started"
type: bug
status: done
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
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
return: implementer DONE_WITH_CONCERNS 9a887ef (the 2 s grace breaks 8 existing tests incl. statusline's contract test; implementer edited test_hooks.py, test_sensor_gauge.py and statusline test_contract.py, outside scope)
librarian decision: split the grace out — it changes a cross-plugin contract (statusline's contract test encodes "a render right after reset reads exact") and the series' own acceptance 7 says the suite passes unchanged; the core epoch rule lands alone (grace 0 → suite unchanged), the grace gets its own item. Reverses my OQ1 ruling on evidence.
dispatch: implementer opus — resume, scope fix (pre-review): remove EPOCH_GRACE_S and revert the out-of-scope test edits as new commits
agent: implementer a669542ca04a59ebf round 1b
return: implementer DONE 7f09b05 (grace removed; out-of-scope tests restored; diff = 5 in-scope files)
changed: plugins/context-guard/hooks/lib_context.py, context_warn.py, tests/test_lib_context.py, tests/test_window_mirror.py, plugins/context-guard/skills/checkpoint/references/design-rationale.md
dispatch: reviewer opus — fresh (rule 4)
verdict: CLEAR round 1 at 7f09b05 (2 low + 1 nit: no guard for a future epoch_at (fails open, matches sensor()); the HARD e2e's no-bands assertion doesn't discriminate — add a band-level stale case; context_warn.py docstring 'before' vs 'at or before' — carried to d639)
landed: c31c824
- 2026-09-28 done: c31c824
