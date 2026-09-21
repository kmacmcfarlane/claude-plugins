---
id: dev-flow-discoverability-investigate-vs-4ca4
title: "dev-flow discoverability: investigate vs deep-investigation at listing level"
type: chore
status: done
priority: 3
created: 2026-09-20
updated: 2026-09-21
closed: 2026-09-21
refs:
  - "peer: agent-harness-fc (uds 160.sock)"
---

Peer relay 2026-09-19/20 from agent-harness-fc: the operator who commissioned both skills did not know deep-investigation existed; both descriptions lead with research-shaped verbs and nothing at listing level distinguishes them. Acceptance: investigate's description names deep-investigation as the escalation (and vice versa where it fits, within the 1024-char limit and the house rule); README dev-flow section carries a one-line 'which dev-flow skill' table (investigate / deep-investigation / implement / dev-cycle / librarian-mode). Failure it prevents: fanning out a narrow question, or reading through a landscape question one session at a time. Escalation test, in the peer's words: 'can you name the three-to-five categories of evidence that would answer it, and does no single one suffice'.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 19be497

## Dispatch
- dispatch: implementer opus — README text (doctrine surface) + two skill descriptions

## Implementer result
- round 1 DONE_WITH_CONCERNS d196c43 (opus): investigate/deep-investigation descriptions name each other with the escalation test; README "Which dev-flow skill" table (6 rows). plugin.json untouched (aim unchanged, principle 1).
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at d196c43
- lows (landed as CLEAR; carry to be39, which rewrites investigate): README:240 restates the escalation test (drift) → "broad landscape (deep-investigation)"; README:245 CoVe "Not when" is not the skill's own boundary; README:242 implement also fans out to worktrees; nit: comma in investigate description.
## Landed
- 19be497.
