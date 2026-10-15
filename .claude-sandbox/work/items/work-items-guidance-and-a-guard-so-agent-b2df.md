---
id: work-items-guidance-and-a-guard-so-agent-b2df
title: "work-items: guidance and a guard so agents' git operations cannot destroy or lose a .work-items/ store"
short_display_name: protect work-item stores from git
type: spike
status: todo
priority: 0
created: 2026-10-15
updated: 2026-10-15
refs:
  - operator message 2026-10-15
---

Operator 2026-10-15, after the nested-repo pitfalls: add guidance to the work-items skill that mitigates the named risks (git clean -x/-X/-ff, stash --all, worktrees and clones without the store, commit failures, concurrent writers, embedded-repo surprises, secrets in local history) with examples of safe patterns; investigate, present the plan for review, land before the migration. Also weigh the operator's idea of a guard hook that blocks risky git operations, and how a fix reaches running sessions without /reload-plugins in each. Observed 2026-10-15 (git 2.39.5, scratch repo): git clean -fdx, -fdX and -fxd leave a store that is its own git repo; only -ffdx deletes it. Documented: hook edits in settings files are picked up by the file watcher (https://code.claude.com/docs/en/hooks).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/work-items-guidance-and-a-guard-so-agent-b2df/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the store-safety guidance and guard options
agent: planner a2cdd001d65a75437 round 1
