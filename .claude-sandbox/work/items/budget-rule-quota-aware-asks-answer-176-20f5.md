---
id: budget-rule-quota-aware-asks-answer-176-20f5
title: "Budget rule: quota-aware asks (answer 176 a), and no budget or spend ever named in a brief"
short_display_name: quota-aware budget, none in briefs
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T19:28Z
created: 2026-10-06
updated: 2026-10-06
refs:
  - operator 2026-10-06, answer 176
---

Operator 2026-10-06: (1) answer 176 a — below 50% weekly use a reached spend budget is noted in the Report and rounds continue; at or above 50% it asks as today; the convergence stop and the quota-reserve guards stay. (2) Operator, verbatim: 'yea, let's update the skill guidance to prevent "so nobody trims their work to fit. I won't do it again."' — after the librarian told a planner 'about $3 left' and a reviewer that the budget was nearly spent (e347). bindings.md already says no brief carries the budget; acceptance adds an explicit prohibition where briefs and resume messages are written (agent-brief, review-brief, fix-loop or the SKILL red flags): never tell a producer or reviewer the budget, the spend so far, or that money or quota is short, nor ask them to be brief for cost. Files: dev-cycle SKILL.md, references/bindings.md, fix-loop.md, agent-brief.md, review-brief.md; librarian-mode budget.md and SKILL.md where they restate the ask.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: full budget-rule-quota-aware-asks-answer-176-20f5 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/budget-rule-quota-aware-asks-answer-176-20f5
budget: 2026-10-06T19:28Z build $22 — default other build
dispatch: implementer opus medium — build (a rule change in dev-cycle and librarian-mode)
agent: implementer ae29d67e84d400eb2 round 1
return: implementer DONE 2a742a2 (7 files; quota-aware rule in bindings.md § Spend budget; prohibition in bindings, agent-brief, review-brief, fix-loop, a SKILL red flag; open: standalone Step 6 pointer, fable-pin reading, resume.md CAP wording, standalone overrun record)
changed:
  plugins/dev-flow/skills/dev-cycle/references/bindings.md — below-50% exception; Never in a brief; Done-alone line
  plugins/dev-flow/skills/dev-cycle/SKILL.md — Step 4.3 clause; Red flag
  plugins/dev-flow/skills/dev-cycle/references/{agent-brief,review-brief,fix-loop}.md — the prohibition
  plugins/dev-flow/skills/librarian-mode/SKILL.md, references/decide-alone.md — decision channel and spend row
dispatch: reviewer opus high — review round 1
agent: reviewer a0bb574eb94a8b64e round 1
