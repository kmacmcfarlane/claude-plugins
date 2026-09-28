---
id: context-guard-test-flake-test-a-copy-old-d1e3
title: "context-guard test flake: test_a_copy_older_than_the_window expects 118-119 min, gets 120 under load"
type: bug
status: done
priority: 2
created: 2026-09-23
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 923f landing 2026-09-23
---

Seen 2026-09-23 while landing 923f, a docs-only change: tests/test_lineage.py:1753, TestStampGuardWarnsOnly.test_a_copy_older_than_the_window_refuses_and_both_warnings_print, asserts 'was last written 11[89] min ago' for a copy aged 2*3600 s, but the message said 120 min. The minute rounding sits on a boundary. It passed on three reruns and the full suite passed. A similar flake under CPU load was seen before (f381 review). Acceptance: the assertion tolerates 118-120 (or the age is set a margin inside the window), and a note in the test says why.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-25 seen again at the 2ec4 landing (1 failure in 778; test name not captured because the run was -q); three verbose re-runs on the pushed tree: OK. Also seen once in an implementer's run for adef. Capture names with a verbose rerun wrapper at landing.
target: branch worktree-context-guard-test-flake-test-a-copy-old-d1e3 at .claude/worktrees/context-guard-test-flake-test-a-copy-old-d1e3, base main (9cafb1a)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — test code (rule 2)
agent: implementer a2fd977c438048f4a round 1
return: implementer DONE 5eb0096 (open q: two countdown tests in test_hooks.py share the shape with a 30-60s margin; left alone)
changed: plugins/context-guard/hooks/tests/test_lineage.py
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer aacd269d44608e0b5 round 1 at 5eb0096
verdict: CLEAR round 1 at 5eb0096 (1 low: regex not tied to path — declined, all four callers correct, carried as-is; 1 nit: import placement and PEP 8 spacing match the file — declined; open q graded: countdown tests have 30-60 s margin, acceptable)
landed: 681c8a1
- 2026-09-28 done: 681c8a1
