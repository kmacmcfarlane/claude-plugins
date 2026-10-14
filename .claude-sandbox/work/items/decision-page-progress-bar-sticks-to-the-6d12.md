---
id: decision-page-progress-bar-sticks-to-the-6d12
title: "decision-page: progress bar sticks to the top when scrolled past; page titled after the session name"
short_display_name: sticky progress, session-name title
type: feature
status: todo
priority: 1
created: 2026-10-14
updated: 2026-10-14
refs:
  - operator message 2026-10-14
---

Operator 2026-10-14, on the open-decisions page: (1) the progress bar should stay visible wherever you scroll, sticking to the top bar once scrolled past; (2) the page should be titled after the Claude Code session name shown in the top bar, e.g. '(kmacmcfarlane) claude-plugins context-guard stopping', not a generic 'Open Decisions'. Acceptance: template change for (1); the decision-page skill's publish step names the title rule for (2) (tab <title> and page.title), with where the writer finds the session name; the open-decisions page republished with both.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decided: 2026-10-14T07:00Z data — the open-decisions page retitled at once (page.title and tab title, data only; version 3); the template and skill rule go through the cycle
target: an agent worktree branch off main (b12bd09f); plugins/operator-interaction/skills/decision-page/{assets/index.html, SKILL.md, references/cards-schema.md, references/writer-digest.md}, tests
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — sticky progress bar in the template; title-after-session-name rule in the skill
agent: implementer ae03c4ed992c8b482 round 1
result: DONE round 1 at 0da9eab3 (bar moved out of the header, sticky top 0 with bg/z-index/scroll-padding; title rule in SKILL.md Step 3 from the session registry as already recorded observed in statusline.py and session-name.md; test_sticky.py; operator-interaction 143, kit-dev 21 OK)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer a67b6d52f6064e806 round 1 at 0da9eab3
verdict: NEEDS_CHANGES round 1 at 0da9eab3 (2 medium: env vars are documented, cite env-vars; version label 2.1.293 should be 2.1.292; lows: fixed scroll padding under a 3-line bar, title set after the pre-publish check, CLAUDE.md layout misses test_sticky.py, owner source assumed; nits: grouped selectors in the test, title format copied in schema)
decided: 2026-10-14T07:15Z words — owner prefix reads the remote's owner segment for any host (the operator's example matches the GitHub owner; open question carried in the Report)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer ae03c4ed992c8b482 round 2
result: DONE round 2 at 2646a1bf after merging main (0f4ba6eb); ResizeObserver line guarded for node; title rule moved to Step 2; operator-interaction 145, kit-dev 21 OK
dispatch: reviewer opus high — resume, round 2
agent: reviewer a67b6d52f6064e806 round 2 at 2646a1bf
