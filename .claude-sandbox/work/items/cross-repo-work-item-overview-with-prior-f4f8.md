---
id: cross-repo-work-item-overview-with-prior-f4f8
title: cross-repo work-item overview with prioritization advice, then a reusable skill for it
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-25T16:55Z
created: 2026-09-24
updated: 2026-09-25
refs:
  - operator 2026-09-24
---

Operator 2026-09-24: 'give me an overview of all of the work-items across the kmacmcfarlane repos. I'd like recommendations about how to prioritize what to do next. Think about your approach to this task and how it could be turned into a skill. After presenting me with the output, give me your plan to make it a reusable skill for later.' Part 1, done in session: a read-only sweep of every kmacmcfarlane repo's store plus recommendations. Part 2: a plan for a reusable skill, presented to the operator; building it is a follow-up once they rule on the plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 80: where the cross-repo review skill lives — (a) the work-items plugin: the sweep becomes a `wi` command and the judgement a skill beside it [recommended: it reads work-item stores, and it borrows the decisions skill's presentation]; (b) the operator-interaction plugin, as something presented to the operator; (z) decide later
decision 81: when the cross-repo review runs — (a) on demand first; a morning-brief form later, once the local-GPU routing research says what runs cheaply unattended [recommended]; (b) on demand plus a daily morning brief from the start; (z) decide later
answer 80: (a) the work-items plugin (operator 2026-09-24); the operator asks what the decisions skill has to do with it — it is only how the review presents; their idea (the summary also presents decisions across repos) filed as its own spike, security model first
answer 81: (a) on demand first; the morning review filed separately as a spike, dependent on the agents repo's scheduler work, opt-in and off by default, options for the operator to review (operator 2026-09-24)

## Notes
- 2026-09-25 claimed by Kyle-McFarlane@bf9f9839222c
- 2026-09-25 operator asked whether the interim summary had landed; it had not been dispatched after answers 80/81 (librarian miss). Building the on-demand version now.
target: branch worktree-cross-repo-work-item-overview-with-prior-f4f8 at .claude/worktrees/cross-repo-work-item-overview-with-prior-f4f8, base main (7f00dd1)
dispatch: implementer opus — new wi command (script) + skill; plans first
agent: implementer ab98f8271aed44186 round 1
return: implementer round 1 DONE_WITH_CONCERNS 6654302 (--dir not --root; security keyword hint; skill example names real estate items)
dispatch: reviewer opus — fresh
agent: reviewer a93634735827126c9 round 1 at 6654302
