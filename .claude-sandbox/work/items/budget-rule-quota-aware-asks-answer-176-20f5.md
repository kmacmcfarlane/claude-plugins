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
verdict: NEEDS_CHANGES round 1 at 2a742a2
findings:
  1. [medium] dev-cycle SKILL.md:396 — Step 6 still says four lines; the standalone Done-alone overrun line is dropped. Fix: after the four-line block add "A budget passed while the weekly quota was below half used adds one `Done alone:` line after the four (`references/bindings.md` § Spend budget, The Done-alone line); under a caller, its own Done-alone group carries it."
  2. [low] resume.md:85-90, :216-218, :225-232 — stale-verdict rows ask on the budget alone below 50%; Group D counts only class cap decided: lines, not the new spend line (out of Files in scope)
  3. [low] bindings.md:386 — the waiver covers only a verdict's spend check, not the one before a round opens (:511-513). Fix: "At a spend check that shows the budget reached (at a verdict, or before a round opens)"
  4. [low] bindings.md:407-415 — standalone, nothing records the waiver, so a resumed run cannot recover the reading for its Report line
  5. [nit] bindings.md:381 — the quoted "I won't do it again" reads as the orchestrator speaking
  6. [nit] decide-alone.md:38 — the class of a convergence stop on a budget already reached is unclear under the waiver
decided: resume.md joins Files in scope for this item — the change made its stale rows and Group D class list wrong, and a follow-up would ship a known contradiction — class: scope
cost: 2026-10-06T19:50Z build $3.62 of $22 after review 1 — must-fix 1 — prices 2
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer ae29d67e84d400eb2 round 2
return: implementer DONE 718bedd (1-6 fixed; resume.md CAP and Group D updated; standalone waiver recorded as a decided: line; open: record-lines.md does not list decided:)
changed:
  plugins/dev-flow/skills/dev-cycle/references/resume.md — CAP waiver, Group D spend line
  plugins/dev-flow/skills/dev-cycle/{SKILL.md, references/bindings.md}, librarian-mode/references/decide-alone.md — round 1 fixes
dispatch: reviewer opus high — resume (review round 2)
agent: reviewer a0bb574eb94a8b64e round 2
verdict: NEEDS_CHANGES round 2 at 718bedd
findings:
  round 1: 1-6 FIXED
  A. [medium] resume.md:85-89 — "unless a fresh weekly reading … below 50%" can be read as waiving ROUNDS ≥ 4 too, skipping the convergence stop and guards. Fix: resume.md:87-89 — "is at or over the amount in force and no fresh weekly reading taken now is below 50% used (`bindings.md` § Spend budget, While the quota is plentiful; a stale verdict's rows read this too);"
  B. [low] resume.md S8/S10 — a stale verdict below 50% re-reviews without a spend check, so no waiver decided: line is written
  C. [low] record-lines.md does not list the decided: shape a standalone run now writes. Fix: add "`decided:` — the shape in the `librarian-mode` skill's `references/decide-alone.md` § The record; writers: the caller, or standalone `bindings.md` § Spend budget, The Done-alone line"
  D. [nit] bindings.md:312 — "Standalone has no decided-alone record" clashes with :417
decided: record-lines.md joins Files in scope (finding C) — class: scope
cost: 2026-10-06T20:02Z build $6.14 of $22 after review 2 — must-fix 1 — prices 2
dispatch: implementer opus medium — resume (fix round 2)
agent: implementer ae29d67e84d400eb2 round 3
return: implementer DONE 19e3a05 (A-D fixed; record-lines.md decided: entry; resume rider list)
changed:
  plugins/dev-flow/skills/dev-cycle/references/{resume.md, record-lines.md, bindings.md} — round 2 fixes
dispatch: reviewer opus high — resume (review round 3)
agent: reviewer a0bb574eb94a8b64e round 3
