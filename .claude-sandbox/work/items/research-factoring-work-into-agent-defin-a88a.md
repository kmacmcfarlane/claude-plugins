---
id: research-factoring-work-into-agent-defin-a88a
title: "research: factoring work into agent definitions vs skills (investigate, research stages, implementation profiles)"
short_display_name: agent-definition factoring
type: spike
status: doing
priority: 0
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T07:05Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'this is a good point to dip more into using agent definitions instead of just skills. We should consider how that factoring works for investigations, research (at different stages and different intensity skill invocations), implementation (different agent profiles for different effort/use-case scenarios in broad strokes). Do a research spike on how that factoring should work as well, that'll be foundational to the rest of the week's progress if we can use resources more effectively.'
Acceptance: a sourced series on (1) what agent definitions can pin in Claude Code (model, effort, tools, permission mode, skills preloaded, hooks, isolation, memory) versus what a skill carries, and how each is dispatched and overridden; (2) today's kit: every dispatch site in plugins/ (investigate, implement, dev-cycle, librarian-mode, research family at each stage and intensity, checkpoint, review) with the role, model and effort it gets today; (3) a proposed factoring: a small set of agent profiles by role and effort/use case, which skills load them, the contract each agent body holds (CLAUDE.md: role, tools, model; task context via the prompt), naming, and where each lives (placement rules); (4) the quota effect, estimated from the store's dispatch lines; (5) landable features. Reconcile with 2eb7 (effort routing, in planning): 2eb7's agent names and table must fit this factoring before 2eb7 builds.

## Handoff
- doing: —
- next: planner r1 running (research lanes for web evidence); then a fresh plan review
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — research spike, plan mode (series a88a-agent-factoring); instructed to gather web evidence through dev-flow:research-lane agents (sonnet, medium) to save quota
agent: a1f0aa368080b709e (planner r1)
input from the operator for a88a (2026-09-29): profiles must include an opus xhigh tier for deep complex work and a fable high/xhigh cross-check for foundational cross-cutting planning and research; criteria come from spike research-criteria-for-each-model-and-eff-6421
the operator tier input was relayed to the running a88a planner (queued at its next tool round)
series 00 written: seven profiles (scribe sonnet/low, scout sonnet/medium, implementer sonnet/medium, planner and reviewer opus/high, deep-worker opus/xhigh, cross-checker fable/high) in dev-flow/agents, fallback general-purpose recorded as inherit; census: 868 dispatch lines (reviewer 380, implementer 375, planner 61, plan reviewer 30); sub-agents about 65-70% of project spend; estimate -28 to -36% sub-agent spend net; F1-F6; 2 open questions; harness flagged a lane report as instruction-shaped (it named bypassPermissions as a finding) — treated as data
dispatch: plan reviewer opus — fresh, round 1
agent: a32498eb13540d165 (plan reviewer r1)
plan review r1 NEEDS_CHANGES (0H 4M 8L): M1 deep-worker covers three roles at one effort (breaks one-role-per-file; review via deep-worker escapes read-only tools); M2 slots give 6421 opus medium/high criteria nowhere to land (effort is per file, so a new role-effort pair is a new file); M3 F4 research cross-check underspecified; M4 quota drops the comparison with last week as run (+30-60%), cross-check cost, task-mix caveat; lows incl. the 868 count
librarian ruling: hold serial 01 until 6421 lands, then fold r1 and 6421 together (M1/M2 turn on 6421 criteria); then 2eb7 reconciles
dispatch: planner opus — resume, serial 01 folding review r1 and 6421 00 (in parallel with 6421 review; a delta follows if that review moves numbers)
agent: a1f0aa368080b709e serial 01 (resumed)
serial 01 written: one role per file; deep-worker withdrawn; profiles scribe, scout, implementer, implementer-deep, planner, planner-deep, reviewer, cross-checker, cross-checker-deep (+ reviewer-light / reviewer-deep conditional on 6421 Q4/Q1); saving 30-47% vs today, +26-66% vs last week as run; 2 questions left (read-only tools later; -deep/-light naming)
dispatch: plan reviewer opus — fresh, round 2
agent: a3b28734ba95cb5fa (plan reviewer r2)
plan review r2 NEEDS_CHANGES (0H 1M 4L): M the map of 6421 answers to files misses Q5 (a) (xhigh steps down to high; no implementer file at opus high) and Q4 (c) (needs reviewer-light); lows: research cross-check stage ownership, 00 deployment rule not superseded, Q2 blocks/naming wording, file counts and research-refine
librarian ruling: hold serial 02 until 6421 serial 01 lands (r1 changes criteria that drive the file map), then fold r2 and 6421 01 together
dispatch: planner opus — resume, serial 02 folding review r2 and 6421 serial 01
agent: a1f0aa368080b709e serial 02 (resumed)
serial 02 written: base ten files (adds implementer-critical opus/high), up to two conditional (reviewer-light, reviewer-deep); recommended answers ship eleven; answer-to-files map for 6421 Q1-Q5
dispatch: plan reviewer opus — fresh, round 3
agent: a6fd7cd904891c48c (plan reviewer r3)
plan review r3 NEEDS_CHANGES (0H 1M 3L): M Q5 (a) step-down: pinned items still ask; research cross-checks are never queued; step down only from an items first review; lows: pin test wording, reviewer-deep trigger no longer an option, all-(z) defaults inconsistent, Q1/Q2 wording
librarian ruling: hold serial 03 (final, round 4 is the cap) until 6421 serial 02 lands, then fold both
dispatch: planner opus — resume, serial 03 (final; round 4 is the cap) folding r3 and 6421 02
agent: a1f0aa368080b709e serial 03 (resumed)
serial 03 final: reviewer-deep removed; ten base files, reviewer-light conditional on 6421 Q4 (b)/(c): eleven at most; Q5 (a) pinned items ask, research cross-checks dropped and named, reviewers never step down mid-item
dispatch: plan reviewer opus — fresh, round 4 (the cap)
agent: adb528de431ffdc9d (plan reviewer r4)
plan review r4 (the cap) NEEDS_CHANGES (0H 1M 2L), none changes a file or a pin: M the research changes (F4) route through 02's older per-answer table: research syntheses must go through Q2 (b)'s keep rule, and (c) to cross-checker-deep; L research-verifier's inert low effort vs the "low only on scribe" rule; L quota step-down table lacks Q1 (b)'s first-dispatch planner-deep row
decision 107: The agent-definitions research (a88a) hit the review cap with one medium left, in how research runs route to the cross-checkers; close it and carry the three fixes into the effort-routing build (2eb7) as acceptance, or run one more round? — options: (a) close the series; 2eb7's reconcile and build take review r4's three fixes as acceptance items [recommended] | (b) one more planner round and a fresh review | (c) park the series | (z) decide later
  raised: 2026-09-29T08:20Z
  stakes: reversible, narrow (no file or pin changes; routing text only)
  if left: research syntheses could be cross-checked at fable high without the keep rule, and option (c) could route to the wrong file, unless 2eb7 builds from review r4, which (a) requires
  round costs: one planner round plus a fresh reviewer, about 15-20 minutes and roughly 0.5-1% of weekly quota; none of the operator's time
  rec: (a) · basis strong — review r4 states each fix exactly and confirms the file set and pins
