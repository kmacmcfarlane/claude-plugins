---
id: dev-flow-ten-role-agents-with-pinned-mod-900a
title: "dev-flow: ten role agents with pinned model and effort (2eb7 F1)"
short_display_name: role agents with pinned effort
type: feature
status: done
priority: 0
parent: model-routing-set-reasoning-effort-per-r-2eb7
created: 2026-09-29
updated: 2026-09-29
closed: 2026-09-29
refs:
  - 2eb7
---

Build F1 of .claude-sandbox/investigations/2eb7-effort-routing (00-04, plan review r4 CLEAR): the ten agent files in plugins/dev-flow/agents (scribe, scout, implementer, implementer-critical, implementer-deep, planner, planner-deep, reviewer, cross-checker, cross-checker-deep) with name, description, model, effort only; the pin test plugins/dev-flow/tests/test_agents.py; plugin.json and marketplace.json parity; CLAUDE.md layout, conventions and a new ## Librarian Checks line (a work-item edit of that section); README; kit-dev update-kit repo-map.md. Acceptance per 01-04 (a88a r4 and 6421 r4 fixes as acceptance).

## Handoff
- doing: —
- next: CLEAR at b0af914; merge after decision 109 (names), then b3c5 on CLEAR; 9 Checks; push
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — marketplace shape change and new agents (routing rule 2); runs at the inherited session effort, which this item exists to fix
agent: a7a61a3e688e0313b (implementer r1)
r1 DONE b0af914: 10 agent files (name, description, model, effort), test_agents.py (24 tests, fail-first shown), manifests in parity, CLAUDE.md (layout, conventions, new Checks line), README, repo-map; claude plugin validate passes (pre-existing version warnings only); names provisional pending the naming question
dispatch: reviewer opus — fresh reviewer, round 1
agent: a542958cf2490ac7f (reviewer r1)
decision 109: What should the new role agents be called? — options: (a) role names with a -deep suffix for the xhigh variant and -critical for the opus-high builder: scribe, scout, implementer, implementer-critical, implementer-deep, planner, planner-deep, reviewer, cross-checker, cross-checker-deep [recommended] | (b) names that carry the effort: implementer-medium, implementer-high, implementer-xhigh, planner-high, planner-xhigh and so on | (c) the librarian picks names at build time and reports them | (z) decide later
  raised: 2026-09-29T16:37Z
  stakes: reversible but wide (ten files, the pin test, four docs and every dispatch site name them; a rename after F2 lands touches all of them)
  why now: the files are built and in review; answering before they land avoids a rename
  rec: (a) · basis partial — names say the job and how hard it digs; efforts can change later without renaming files
review r1 CLEAR at b0af914 (2 lows, 2 nits carried into F2 b3c5: forward refs resolved by F2; README implementer row; subTest placement; SUPPORTED_KEYS experimental); smoke dispatches confirmed dev-flow:scribe on sonnet low and dev-flow:cross-checker-deep on fable xhigh
librarian ruling: hold the merge until decision 109 (names) is answered, to avoid a rename; F2 builds now on top of this branch
answer 109: a — "this sounds good, but I'm open to other better ideas that get raised to me during implementation" (read as: keep the proposed names; better names found during implementation may be raised)
landed: cb7eea7
checks on main cb7eea7: all 9 OK (dev-flow 24)
- 2026-09-29 done
