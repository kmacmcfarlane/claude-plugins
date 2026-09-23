---
id: operator-interaction-fast-follow-librari-d44e
title: "operator-interaction fast-follow: librarian-mode renders its decisions per the decisions skill"
type: feature
status: doing
priority: 0
deps:
  - dev-flow-a-decision-presentation-skill-d-7113
parent: checkpoint-around-continuation-how-agent-d3ee
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-23T07:55Z
created: 2026-09-23
updated: 2026-09-23
refs:
  - operator 2026-09-23
---

Operator 2026-09-23: 'I'd like to see this wired into librarian-mode as a fast follow. I make lots of decisions in those sessions and want to try it tomorrow … Do the librarian wiring as a fast-follow and land it right after you finish this.' Acceptance: librarian-mode's Report 'decisions needed:', its decision channel and its Idle-turn questions render decisions per operator-interaction's decisions skill (content floor, levels, ordering, hint line, reply parsing with echo, decide-later wake at the next Report); the decision counter stays in the store; dev-cycle's decision channel points to the same skill; the soft dependency is declared in dev-flow's description and README row (principle 4); it degrades gracefully when operator-interaction is not installed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

note: started in parallel with 9f98's review to meet the operator's morning deadline; merges after 9f98 lands (merge-tree checked at land)
target: full operator-interaction-fast-follow-librari-d44e /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/operator-interaction-fast-follow-librari-d44e
dispatch: implementer opus (fork of the librarian, effort xhigh) — doctrine: dev-flow skill text + soft-dependency declaration (README row, plugin.json, marketplace.json); full mode (investigate then implement)
agent: implementer adda2a62cd119c07a round 1
return: implementer DONE 0891f07 (new references/decisions.md in librarian-mode; SKILL.md Rehydrate/Intake/Decision channel/Report; idle-turn.md; dev-cycle bindings § Decisions and Step 6; soft dependency declared in dev-flow plugin.json, marketplace.json and README; deviations: new `wake N:` store line, `answer N:` records the echo's reading; merge-tree clean against 9f98)
dispatch: reviewer opus — implementer tier opus (doctrine: dev-flow skill text, soft-dependency declaration)
agent: reviewer a6ae517fc4495dcda round 1
