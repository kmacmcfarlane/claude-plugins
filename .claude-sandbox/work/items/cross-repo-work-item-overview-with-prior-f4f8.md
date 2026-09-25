---
id: cross-repo-work-item-overview-with-prior-f4f8
title: cross-repo work-item overview with prioritization advice, then a reusable skill for it
type: feature
status: done
priority: 1
created: 2026-09-24
updated: 2026-09-25
closed: 2026-09-25
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
verdict: reviewer round 1 NEEDS_CHANGES at 6654302 — 1 high (skill example names real estate items and security gaps), 4 medium (default dir can sweep /home or $HOME; linked worktrees and symlinked repos double-counted; non-UTF-8 names crash text mode; plugin.json description gained an "and"), 4 low, 1 nit
dispatch: implementer opus — resume, fix round 1
agent: implementer ab98f8271aed44186 fix round 1
return: implementer fix round 1 DONE_WITH_CONCERNS 5c1f4cf (real names remain in 6654302 history)
librarian decision: land f4f8 from a single squashed commit of the reviewed tree (new branch, then merge --no-ff as usual), so 6654302, which names real items and security gaps, never reaches origin
dispatch: reviewer opus — resume, round 2
agent: reviewer a93634735827126c9 round 2 at 5c1f4cf
verdict: reviewer round 2 NEEDS_CHANGES at 5c1f4cf — 1 medium (a .git-file entry is dropped silently even when its main checkout is not in the scan: bare repo + worktree, --separate-git-dir, submodule under --dir superproject), 1 low (escaped non-UTF-8 JSON path unusable for --root)
dispatch: implementer opus — resume, fix round 2
agent: implementer ab98f8271aed44186 fix round 2
return: implementer fix round 2 DONE 7998e6a (dedupe by git common dir, skipped list, path_raw)
dispatch: reviewer opus — resume, round 3
agent: reviewer a93634735827126c9 round 3 at 7998e6a
verdict: reviewer round 3 NEEDS_CHANGES at 7998e6a — 1 medium (NUL byte in a pointer file raises ValueError and stops the whole sweep), 1 low (FIFO commondir hangs)
dispatch: implementer opus — resume, fix round 3 (review round 4 is the cap)
agent: implementer ab98f8271aed44186 fix round 3
return: implementer fix round 3 DONE de4de98 (NUL and FIFO pointer files)
dispatch: reviewer opus — resume, round 4 (cap)
agent: reviewer a93634735827126c9 round 4 at de4de98
verdict: reviewer round 4 CLEAR at de4de98 (1 nit: stat/open race, not realistic)
landed: 6635238 (squashed land-f4f8, merge --no-ff into main)
- 2026-09-25 done
