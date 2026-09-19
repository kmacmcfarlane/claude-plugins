---
id: librarian-mode-rehydrate-recovers-the-de-f0dc
title: "librarian-mode: Rehydrate recovers the decision counter with a grep"
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-19
closed: 2026-09-19
refs:
  - reviewer report, item librarian-mode-decisions-needed-are-a-nu-486d
---

From the 486d review 2026-09-16: the decision counter lives in item bodies, but Rehydrate step 3 only runs wi prime and wi show --brief, which hide appended 'decision N:' lines. Acceptance: Rehydrate names the recovery command (grep -rhn '^decision [0-9]' "$WI_ROOT"/items | sort -t' ' -k2 -n | tail -1, or equivalent) in one line; SKILL.md stays under 19,000 chars — 31 chars of headroom remain, so pair it with a trim; consider folding into the size chore.

## Handoff
- doing: bundled in worktree d72e
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — bundled chores in worktree d72e; >3 files (rule 2)

review round 5 (opus, extra per decision 35): CLEAR. Final: CLEAR after 4 fix rounds (impl opus, review opus).
- 2026-09-19 done: cd4b580
