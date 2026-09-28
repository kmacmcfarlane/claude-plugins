---
id: dev-cycle-briefs-small-wording-follow-up-2364
title: "dev-cycle briefs: small wording follow-ups from the 774d and 775a reviews"
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:02Z
created: 2026-09-28
updated: 2026-09-28
refs:
  - 774d, 775a reviews
---

From the 774d review (2026-09-28): checklist §6 should say how to get the pre-merge BASE (W=$MAIN; BASE=$(git -C "$MAIN" rev-parse HEAD^1)); review-brief 'fake of the tool on PATH' should add 'or a stub of the service' for HTTP APIs; agent-brief rule (1) 'from another file' narrows it — 'from anywhere else'; checklist line 5 says all sections re-run after the merge but §6 names 2/4/5. From the 775a review: §3 shape() should use git -c core.quotePath=false and json.dumps(source, sort_keys=True); note the bash-only <( ).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-dev-cycle-briefs-small-wording-follow-up-2364 at .claude/worktrees/dev-cycle-briefs-small-wording-follow-up-2364, base main (4dcf3de)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — checklist commands and brief rules (rule 2)
agent: implementer a8ec0aa89575d5ce5 round 1
