---
id: librarian-mode-allow-merging-origin-main-25fa
title: "librarian-mode: allow merging origin/main on a rejected push (never rebase/force)"
type: chore
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator answer 52, 2026-09-22
---

Operator 2026-09-22 (answer 52): 'Why would we forbid doing a pull? That seems like a weird policy.' The no-pull rule exists so unreviewed commits don't land in what the librarian vouches for silently; rebase/force rewrite history. Acceptance: on a non-fast-forward rejection the librarian fetches and merges origin/main (a merge commit, never rebase or --force), runs Checks on the result, lists the incoming commits in the Report, then pushes; a conflict or red check stops and asks. Edit SKILL.md § Critical/Report + troubleshooting.md; dev-cycle likewise if it carries the rule.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — librarian-mode custody doctrine (Report / push rule)
