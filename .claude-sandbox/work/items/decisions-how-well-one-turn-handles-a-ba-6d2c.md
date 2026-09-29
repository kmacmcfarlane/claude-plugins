---
id: decisions-how-well-one-turn-handles-a-ba-6d2c
title: "decisions: how well one turn handles a batch of free-form decision replies (research spike)"
type: spike
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T05:26Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'could there be a performance difference in replying to a bunch of decisions at once versus a different flow? ... research spike to understand the dynamics of the LLM in terms of how it can think about responding to a bunch of (maybe not-super-related) decisions at once? Perhaps these free-form types of decision responses should get their own separation within your turn or a more robust way to evaluate them ... is this giving you the most traction?' Acceptance: a series with external evidence on multi-item instruction handling by LLMs and our own transcripts (primary sample: the operator's 2026-09-29 reply to 89-97), candidate flows (per-reply handling, structured parse-then-act, per-reply sub-agents, one decision at a time), how to measure traction, and a recommendation.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — research spike with web evidence, plan mode (series 6d2c-batched-decision-replies)
agent: a3aadbcfa2cdcba92 (planner r1)
notify: send agents a pointer when this series lands (agents asked)
