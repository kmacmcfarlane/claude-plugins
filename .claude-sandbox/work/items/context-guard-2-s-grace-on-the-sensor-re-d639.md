---
id: context-guard-2-s-grace-on-the-sensor-re-d639
title: "context-guard: 2 s grace on the sensor record after a compaction (EPOCH_GRACE_S)"
type: feature
status: done
priority: 3
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 428e split
---

Split from 428e 2026-09-28 (series bace OQ1): a status-line render that straddles PostCompact could write the old count with a fresh time. Predicted, never observed. Adding the grace changes the sensor contract: statusline's test_contract.py test_reset_epoch_demotes_an_earlier_record and context-guard test_sensor_gauge / test_hooks fixtures assume a render right after reset reads exact. Acceptance: the grace plus the contract change stated in both plugins' docs (statusline sensor-contract reference), the tests updated in the same commit, and a reviewer covering both plugins. Implementer's first attempt is on 428e's branch history (9a887ef) for reference.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 from the 428e review (carry here): guard _epoch_cur and sensor() against a future epoch_at (_future_skewed(cut)); an e2e test with a band-level stale count (750K prints nothing, latches no bands, then a real 65% band); context_warn.py:18 docstring 'at or before'
target: branch worktree-context-guard-2-s-grace-on-the-sensor-re-d639 at .claude/worktrees/context-guard-2-s-grace-on-the-sensor-re-d639, base main (a66d203)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — hook code across two plugins (rule 2)
agent: implementer a269a8e741ea0a793 round 1
return: implementer DONE b2120c0 (grace + _epoch_cut future guard + band-level e2e + contract doc; open q: _epoch_end_tokens reads raw epoch_at)
changed: plugins/context-guard/hooks/lib_context.py, context_warn.py, tests/test_hooks.py, test_sensor_gauge.py, test_lib_context.py, test_window_mirror.py, plugins/statusline/hooks/tests/test_contract.py, plugins/statusline/skills/install-statusline/references/sensor-contract.md, plugins/context-guard/skills/checkpoint/references/design-rationale.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer afb8341eaa84a1140 round 1 at b2120c0
verdict: NEEDS_CHANGES round 1 at b2120c0 (1 high, 2 medium, 2 low, 2 nit; grace itself correct, fail-first holds)
findings:
  [high] lib_context.py:170-178 _epoch_cut in sensor() — a backward clock step >60 s after a compaction brings the old epoch's exact 95% back (reproduced) → false HARD; pass: sensor() fails toward window-only for pre-reset records under a future cut (or keep the guard in _epoch_cur only) + test
  [medium] sensor-contract.md:67-70 and design-rationale.md:133-134 — "a render that read its payload before the compaction" contradicts at = read time; the case is a payload Claude Code built before and the status line read just after
  [low] _epoch_end_tokens use _epoch_cut; [low] commit message wording; [nit] lib_context.py:65 110-char line; [nit] sensor-contract "first exact reading" stated as fact
dispatch: implementer opus — resume, fix round 1
agent: implementer a269a8e741ea0a793 round 2
return: implementer DONE d353f41 (fix round 1; sensor() back to raw epoch_at; future guard only for transcript counts and _epoch_end_tokens; open q: strict never-block in _epoch_cur too?)
dispatch: reviewer opus — resume, round 2
agent: reviewer afb8341eaa84a1140 round 2 at d353f41
verdict: CLEAR round 2 at d353f41 (2 nit: a 90-char docstring line; the 'only silences for the length of the step' wording is conservative — declined; _epoch_cur keeps its future guard, residual negligible)
landed: 2d879f3
- 2026-09-28 done: 2d879f3
