---
id: wi-claim-handoff-drops-body-text-appende-e832
title: wi claim/handoff drops body text appended after the Handoff block
type: bug
status: todo
priority: 1
created: 2026-09-19
updated: 2026-09-19
---

Observed 2026-09-19: notes appended (plain '- ...' lines after the '## Handoff' block, no heading) to dev-flow-add-the-dev-cycle-skill-07c3-f1-325d were silently deleted when 'wi claim' + 'wi handoff' rewrote the item (compare git show 0a1c5f9 vs 1d8382e for that file). Items with a '## Notes' or other heading after Handoff seem to survive. Data loss in the store. Acceptance: claim/handoff/every rewrite preserves all body text outside the Handoff block it owns (including trailing unheaded text); regression tests with trailing text, text between sections, and multiple headings. Librarian workaround meanwhile: append notes under a '## ...' heading.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
