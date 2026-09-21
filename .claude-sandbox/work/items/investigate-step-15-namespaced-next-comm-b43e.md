---
id: investigate-step-15-namespaced-next-comm-b43e
title: "investigate Step 15: namespaced next command, checkpoint path, sub-agent option"
type: feature
status: done
priority: 2
created: 2026-09-20
updated: 2026-09-21
closed: 2026-09-21
refs:
  - "peer: opencode-d0 (uds 256.sock), operator relay"
---

Operator request 2026-09-20 relayed by peer opencode-d0, from a finished investigate run (series opencode-supervised-mode). Two of the four asks are already satisfied by Step 15 (investigate/SKILL.md:549-559): it prints **Wrote:** with the full path and ends with a next command carrying the slug. Three gaps. (1) Namespace the command: emit dev-flow:implement <slug>, not a bare /implement - ambiguous with several plugins installed. (2) Offer a context-guard path CONDITIONAL on a real check that the plugin is installed (the skill ships to estates without it): checkpoint (context-guard:checkpoint), clear, then implement in the fresh session - the case this came from is an investigate pass that burned a lot of context followed by an implement pass whose inputs are files, not the conversation. (3) Present running the implementation in a sub-agent as a third option. Constraint from the peer, worth honouring: Step 15's value is that it is scannable - one line per option, no long branch.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- decision (librarian, correct me): ask 3 reads as running the IMPLEMENTATION in a sub-agent (it follows the checkpoint/clear/implement-here sequence); the peer flagged it did not confirm that with the operator. Shape: point at `dev-flow:dev-cycle <slug>`, which already delegates the build to a background agent in its own worktree - no new machinery. If the operator meant re-running the investigation in a sub-agent, that is a different item.
- ordering: investigate/SKILL.md is also touched by 183a (gates may take a numbered list) and 4ca4 (description names deep-investigation). Land them in one lane or rebase; do not dispatch them in parallel.
- source run for reference: /home/rt/work/src/github.com/kmacmcfarlane/opencode/.claude-sandbox/investigations/opencode-supervised-mode/00_initial.md
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 24373c3

## Dispatch
- dispatch: implementer opus — judgement (report format; conditional plugin check)

## Implementer result
- round 1 DONE_WITH_CONCERNS ec1e878 (opus): Next: list of three one-line options; checkpoint line only when context-guard:checkpoint is in the session skill list. +61 words.
- concern: dev-flow now mentions context-guard (as dev-cycle model-routing and librarian ending-the-session already do) but the catalog declares no dev-flow → context-guard soft edge (principle 4). Librarian: widen scope before review — declare it.
- scope widening 9061ac0: README dev-flow Depends on + prose gains context-guard (soft; …); dev-flow plugin.json and marketplace description clause (identical).
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 9061ac0
- lows carried to be39: README:87 row says librarian "rehydrates from its manifest and ledger" (prose wording "weighs" is right); options lack a leading slash (/dev-flow:implement etc. is the typeable form); nit on the skill-list wording.
## Landed
- 24373c3.
