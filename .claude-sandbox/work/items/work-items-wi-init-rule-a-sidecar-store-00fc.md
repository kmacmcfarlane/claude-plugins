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
agent: implementer adba9146eca7aabb0
return: DONE 473f18d8; sidecar check first (test -e .claude-sandbox/.git, as wi's sandbox_shape); scratch: --track in a sidecar records tracked, lint clean, no /work/ line; --no-track reproduces the bug and lint misses it (filed as wi-lint-misses-a-sidecar-store-recorded-3c06); work-items 365, kit-dev 21 OK
dispatch: reviewer opus high — review round 1 of 473f18d8
agent: reviewer af4ea7ba3ba76bb00
verdict: review round 1 NEEDS_CHANGES (must-fix 1: the sidecar test is cwd-relative; from a worktree in a sidecar layout it fails and the rule picks --no-track; should-fix: scope the check to a store at .claude-sandbox/work/; nit: a 120-char line; note: acceptance asks for a worked example — the reviewer's scratch table meets it, recorded here)
note: worked example (reviewer scratch, 2026-10-13): host-tracked true/false/empty → track/no-track/track; host-ignored no sidecar false/empty → no-track; sidecar any → track; outside sandbox → ask; .work/ store with a sidecar → host tracks
dispatch: implementer sonnet medium — fix round 1 (resume adba9146eca7aabb0)
