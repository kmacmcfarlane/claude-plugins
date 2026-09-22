---
id: dev-cycle-e770-f2-decision-channel-durab-1709
title: "dev-cycle e770 F2: decision channel durability, re-ask, answer scoping"
type: feature
status: done
priority: 2
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - e770
---

Plan of record .claude-sandbox/investigations/e770-dev-cycle-resume (00 § F2 as amended by 01-04; answer 64 a: never wait — ephemeral re-asks, durable hands back). Refiled by the librarian 2026-09-22: e770 closed after F1 landed (daf8758) with F2-F4 unbuilt. Files: plugins/dev-flow/skills/dev-cycle/references/bindings.md. Route opus/opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full dev-cycle-e770-f2-decision-channel-durab-1709 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/dev-cycle-e770-f2-decision-channel-durab-1709
dispatch: implementer opus — recorded trade-off (answer 64), contract judgement; plan routes opus
agent: implementer aaab823df1b681890 round 1
return: implementer DONE_WITH_CONCERNS 5bbab0a
changed: plugins/dev-flow/skills/dev-cycle/references/bindings.md
librarian on OQ1: F2 must land alone (Factor), and alone it makes librarian-mode a missing-binding caller; Files in scope widened to librarian-mode/SKILL.md (the Decision channel binding line only) and bindings.md § What a librarian binds — the word durable. OQ2 accepted: F3 follows immediately in wave 2.
dispatch: implementer opus — scope rider (resume)
return: implementer DONE a00b2b3
changed: + plugins/dev-flow/skills/librarian-mode/SKILL.md (Decision channel binding line)
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a87596981dbf2de0f round 1
verdict: NEEDS_CHANGES round 1 at a00b2b3
findings:
- [medium] bindings.md:305 — "A pending decision … never makes a run wait, in either channel" contradicts :295 ("Standalone: exactly one pending decision goes through AskUserQuestion" — a live prompt the run waits on; Land's ask and review mode's dispatch ask rely on it). Pass: scope it to "never wait on a question this session is not asking — a prompt that is gone, or a durable channel", or drop "pending" from :295.
- [low] :247 spent: "§ Resume's line, which writes and reads it" is false at HEAD — say not yet specified, nothing writes one yet.
- [low] :320-321 inline phase-line definition — F3 rider: re-point at resume.md's definition.
- [low] :24/:308/:315 a caller binding an ephemeral channel has no clear arm; standalone value omits § Decisions' numbered list.
- [low] a00b2b3 second commit before review — the librarian's scope rider; noted only.
F3 rider added (acdd): re-point bindings.md's inline phase-line parenthesis at resume.md's definition; make spent: true once written; model-routing.md:146-151 group fable answer vs positional scoping.
dispatch: implementer opus — fix round 1 (resume)
return: implementer DONE c9a3ccf
dispatch: reviewer opus — review r2 (resume)
verdict: CLEAR round 2 at c9a3ccf
low: c9a3ccf subject reads inverted — carried in the merge message (subject-fix)
landed: 42126b9
- 2026-09-22 done: 42126b9
