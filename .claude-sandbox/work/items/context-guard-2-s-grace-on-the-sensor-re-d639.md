---
id: context-guard-2-s-grace-on-the-sensor-re-d639
title: "context-guard: 2 s grace on the sensor record after a compaction (EPOCH_GRACE_S)"
type: feature
status: todo
priority: 3
created: 2026-09-28
updated: 2026-09-28
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
