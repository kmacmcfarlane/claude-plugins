---
id: wi-claim-handoff-drops-body-text-appende-e832
title: wi claim/handoff drops body text appended after the Handoff block
type: bug
status: done
priority: 1
created: 2026-09-19
updated: 2026-09-19
closed: 2026-09-19
---

Observed 2026-09-19: notes appended (plain '- ...' lines after the '## Handoff' block, no heading) to dev-flow-add-the-dev-cycle-skill-07c3-f1-325d were silently deleted when 'wi claim' + 'wi handoff' rewrote the item (compare git show 0a1c5f9 vs 1d8382e for that file). Items with a '## Notes' or other heading after Handoff seem to survive. Data loss in the store. Acceptance: claim/handoff/every rewrite preserves all body text outside the Handoff block it owns (including trailing unheaded text); regression tests with trailing text, text between sections, and multiple headings. Librarian workaround meanwhile: append notes under a '## ...' heading.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009
- 2026-09-19 done: 6149396

## Dispatch
dispatch: implementer opus — executable logic (wi.py), data loss

impl: DONE 2d871e2 (root cause: handoff replaced the whole Handoff section incl trailing unheaded text; all rewrites rebuilt the body/CRLF. Now raw-body in-place edits; 11 tests; mutation 92 fails on main).
dispatch: reviewer opus — rule 4

review round 1 (opus): CLEAR. 107/107 real-store items round-trip byte-identical; prime/lint/show identical. Lows to follow-up.
