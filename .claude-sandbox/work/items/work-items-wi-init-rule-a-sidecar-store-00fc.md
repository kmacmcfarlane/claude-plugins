---
id: work-items-wi-init-rule-a-sidecar-store-00fc
title: "work-items wi init rule: a sidecar store is tracked even when the host ignores .claude-sandbox/"
short_display_name: wi init rule in a sidecar layout
type: bug
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T19:51Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer claude-sandbox librarian, 2026-10-13 (fe52 planner's scratch test)
---

The landed 29db rule maps CLAUDE_SANDBOX_TRACK_IN_HOST false (and, when empty, a host that git-ignores .claude-sandbox/) to --no-track. In a sidecar layout (.claude-sandbox/ is its own git repo) the store is tracked in the sidecar, and --no-track would add /work/ to .claude-sandbox/.gitignore so new items land in neither repo. Acceptance: the rule checks for a sidecar first (.claude-sandbox/.git exists, or git -C .claude-sandbox rev-parse finds a repo whose top is .claude-sandbox) → --track; only then the variable and the layout probe; tests or a worked example for host-tracked, host-ignored-no-sidecar, sidecar, outside sandbox.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
dispatch: implementer sonnet medium — build (rule text fix)
