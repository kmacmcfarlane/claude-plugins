---
id: make-the-standalone-test-mechanical-each-193f
title: "make the standalone test mechanical: each plugin's tests run alone, every edge declared"
short_display_name: mechanical standalone test
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T07:11Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F8 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F8 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order). Waits on decision 192 (where the checks live).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (chore; acceptance from the 72ef series; answers 190 a / 192 a)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a5654365709ad831d
return: DONE worktree-agent-a5654365709ad831d a4d383f (kit-dev/tests: test_standalone.py runs each plugin's suites alone, test_declared_edges.py lints cross-plugin references with shrink-only ALLOWED/UNDECLARED lists; two skips added: statusline live-hub subtest (F8), dev-flow TestDocs (beyond F8); Librarian Check added; 5 undeclared edges listed for F7/F3)
dispatch: reviewer opus high — review round 1 of a4d383f
agent: reviewer a58bf62f2fe13b988
