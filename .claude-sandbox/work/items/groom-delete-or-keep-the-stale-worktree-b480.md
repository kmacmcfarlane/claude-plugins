---
id: groom-delete-or-keep-the-stale-worktree-b480
title: "groom: delete or keep the stale worktree-librarian-mode branch"
short_display_name: stale librarian-mode branch
type: chore
status: done
priority: 3
created: 2026-09-30
updated: 2026-09-30
closed: 2026-09-30
---

Found at rehydrate (handoff 5, Aware of): branch worktree-librarian-mode, one commit f1f07ca (2026-09-04), an early draft of the librarian-mode skill under plugins/kit-dev/ (6 files, +522); main landed the skill from worktree-librarian-mode-main (e1b3459) and later moved it to dev-flow. No worktree uses it. Deleting is one-way, so asked (decision 131).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 131: Delete the stale branch worktree-librarian-mode (one commit, the 2026-09-04 kit-dev draft of librarian-mode)? — options: (a) delete it; main keeps the landed version [recommended] | (b) keep it | (z) decide later
  raised: 2026-09-30T21:15Z
  stakes: one-way, narrow (the draft commit becomes unreachable and is pruned eventually)
  why now: nothing forces it; it shows in every tree inventory
  (a): gone; main keeps e1b3459's landed skill, since rewritten in dev-flow — undo: none after pruning — who: nobody
  (b): nothing changes
  (z): it stays
  rec: (a) · basis strong — git diff main...branch adds only the kit-dev draft (6 files), superseded on main
  unknown: —
answer 131: a — "131a" (2026-09-30T22:14Z, chat)
closed 131: acted — branch deleted (was f1f07ca)

## Notes
- 2026-09-30 done
