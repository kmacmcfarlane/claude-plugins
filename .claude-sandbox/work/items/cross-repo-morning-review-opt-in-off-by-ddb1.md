---
id: cross-repo-morning-review-opt-in-off-by-ddb1
title: "cross-repo morning review: opt-in, off by default, runs on the agents repo's scheduler"
type: spike
status: todo
priority: 2
parent: cross-repo-work-item-overview-with-prior-f4f8
created: 2026-09-24
updated: 2026-09-24
refs:
  - operator 2026-09-24 (answer 81)
---

Operator 2026-09-24 on decision 81: the morning form of the cross-repo review, done separately, dependent on the agents repo's scheduler work. Opt-in and off by default. Acceptance: a spike presenting options for how the work-items plugin exposes it (e.g. a config key in the store, a wi command the scheduler calls, a SessionStart brief, where the output lands), each with impact on quota and trust, reviewed by the operator before any build.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
2026-09-30 agents librarian (peer 135.sock, their notify-claude-plugins-librarian-when-the-29d6; news, not an approval): the operator answered agents decision 10 (b) — a new control-plane back-end repo and daemon, now. The nightly scheduler runner (bf41 design) moves there; no longer a claude-plugins or agents piece. Plan: agents .claude-sandbox/investigations/control-plane-backend-repo/ (review NEEDS_CHANGES, revision running; one finding: the daemon must not run code from sandbox-writable paths, so not the plugin-cache wi.py as is). As it stands: the runner lives in the back end; self-wake and the quiet and stop modes stay with c79e; the back end is read-only toward repo stores through Phase 3; a claim-tombstone writer is open (a second writer of claims/ changes agents decision 0008 item 5, needs a new decision record). Full shape follows once the plan clears review and the operator names the repo.
ddb1's title names the agents repo's scheduler: that runner now lives in the control-plane back end (read-only toward stores through Phase 3); re-scope when the full shape arrives
