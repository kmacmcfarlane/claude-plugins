---
id: make-the-standalone-test-mechanical-each-193f
title: "make the standalone test mechanical: each plugin's tests run alone, every edge declared"
short_display_name: mechanical standalone test
type: chore
status: done
priority: 2
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
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
verdict: review round 1 NEEDS_CHANGES (medium 3: slash-command skill form unmatched; data paths built in code missed, two UNDECLARED entries anchored on incidental text; ALLOWED keyed by (file, target) exempts the whole file; lows 4-5: self-test breaks when F3 lands, co-owned path checked against the other owner; nit 6 stub hub.py)
dispatch: implementer opus medium — fix round 1 (resume a5654365709ad831d)
return: DONE 1d59639 on merge a995a44 (slash forms; code-built paths in .py, tests excluded by measurement; ALLOWED/UNDECLARED keyed by line substring in one table; synthetic self-test; co-owned paths skipped; stub hub.py so the live-hub subtest runs alone; kit-dev 16 tests ~124 s)
dispatch: reviewer opus high — review round 2 (resume a58bf62f2fe13b988)
verdict: review round 2 NEEDS_CHANGES (high 1: with current main merged, aebc's repo-wide test_checkpoint_namespaced fails the standalone run (needs CLAUDE.md) and the lint (two lines naming dev-flow and statusline paths); low 2: probe tests assume kit-dev declares no edges, F3 will break them; nits 3 duplicate findings, 4 substring excuse accepted); fix round 1 itself sound, test-file exclusion and ralph entries judged right
dispatch: implementer opus medium — fix round 2 (resume a5654365709ad831d)
return: DONE d752180 on merge 96add79 (aebc's scan skips outside the source repo, two ALLOWED entries keyed on line text; probes from sandbox with a no-edge guard test; findings deduped; 11 suites OK, kit-dev 18 ~125 s)
dispatch: reviewer opus high — review round 3 (resume a58bf62f2fe13b988)
verdict: review round 3 CLEAR (all three round-2 findings fixed; nit: IN_REPO guard skips silently if a root doc goes missing, accepted as for TestDocs)
landed: b08cf12 (merge of a4d383f..d752180); Checks 11/11 OK incl. the new kit-dev Check
- 2026-10-09 done
