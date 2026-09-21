---
id: context-guard-legacy-in-state-exact-bloc-73a6
title: "context-guard: legacy in-state exact block lacks the future-at check"
type: bug
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
---

From the 8cc2-F1 review (pre-existing): only the sensor file's exact block is rejected when its at is in the future (lib_context._sensor_exact); a clock-skewed legacy in-state exact block from the deprecated statusline copy counts as fresh for the prompt gate's block and the turn gate. Acceptance: the same future-skew rule for both sources; a test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
