---
id: context-guard-test-flake-test-a-copy-old-d1e3
title: "context-guard test flake: test_a_copy_older_than_the_window expects 118-119 min, gets 120 under load"
type: bug
status: todo
priority: 2
created: 2026-09-23
updated: 2026-09-23
refs:
  - 923f landing 2026-09-23
---

Seen 2026-09-23 while landing 923f, a docs-only change: tests/test_lineage.py:1753, TestStampGuardWarnsOnly.test_a_copy_older_than_the_window_refuses_and_both_warnings_print, asserts 'was last written 11[89] min ago' for a copy aged 2*3600 s, but the message said 120 min. The minute rounding sits on a boundary. It passed on three reruns and the full suite passed. A similar flake under CPU load was seen before (f381 review). Acceptance: the assertion tolerates 118-120 (or the age is set a margin inside the window), and a note in the test says why.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
