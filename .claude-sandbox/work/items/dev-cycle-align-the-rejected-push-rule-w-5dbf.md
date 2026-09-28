---
id: dev-cycle-align-the-rejected-push-rule-w-5dbf
title: "dev-cycle: align the rejected-push rule with librarian-mode (merge origin/main, never rebase/force)"
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:20Z
created: 2026-09-22
updated: 2026-09-28
refs:
  - 25fa OQ
---

From 25fa (librarian-mode push rule, answer 52) OQ, 2026-09-22: dev-cycle troubleshooting.md:77-78 and bindings.md:138 still say never pull/fetch/merge around a rejected push. Align with librarian-mode's new procedure (or point at it), so the two skills agree. Lands after 25fa.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-dev-cycle-align-the-rejected-push-rule-w-5dbf at .claude/worktrees/dev-cycle-align-the-rejected-push-rule-w-5dbf, base main (3d7760d)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes a skill rule (rule 2)
agent: implementer a8163efe6299339b1 round 1
return: implementer DONE_WITH_CONCERNS dfa67b7 (standalone: ask once, 'Leave it unpushed' first, else checked merge of origin/<base>)
changed: plugins/dev-flow/skills/dev-cycle/references/troubleshooting.md, plugins/dev-flow/skills/dev-cycle/references/bindings.md
librarian decision: standalone asks before merging others' commits (conservative: a user-asked push covers the cycle's own landing only); kept, graded by the reviewer
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a6b9885e5628ae3c8 round 1 at dfa67b7
verdict: NEEDS_CHANGES round 1 at dfa67b7 (1 medium, 2 low; ask-first standalone choice endorsed)
findings:
  [medium] troubleshooting.md:122-131 — no recovery when the session dies between merge --no-commit origin/<base> and the commit (MERGE_HEAD + unchecked staged merge; resume S2 reports and stops); pass: a § Landing bullet — MERGE_HEAD == origin/<base> is a push-rejection merge, never commit it as found, merge --abort then redo from fetch/ask or report the push not done; resume.md part to a follow-up
  [low] troubleshooting.md:131 — the conflict "decision for the user" names no options; name a reviewed conflict round in a worktree (fix-loop.md § A merge conflict) or resolving on origin
  [low] troubleshooting.md:124-126 — ragged line breaks; reflow
dispatch: implementer opus — resume, fix round 1
agent: implementer a8163efe6299339b1 round 2
return: implementer DONE 3c546e9 (fix round 1)
dispatch: reviewer opus — resume, round 2
agent: reviewer a6b9885e5628ae3c8 round 2 at 3c546e9
