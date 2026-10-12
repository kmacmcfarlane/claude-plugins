---
id: one-way-to-reach-wi-from-outside-work-it-b9e4
title: one way to reach wi from outside work-items
short_display_name: one way to reach wi
type: refactor
status: done
priority: 3
created: 2026-10-08
updated: 2026-10-12
closed: 2026-10-12
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F5 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F5 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
note: from 9385's build — dev-cycle bindings.md § Store's wi lookup ends with WI="python3 " when work-items is absent (same shape as DF-8's bug); in scope here if this item is the single wi-reach path
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
target: as 72ef F5 (with 01, 02 applied); also the `WI="python3 "` fallback noted on it; all Checks green
dispatch: implementer opus medium — build (cross-plugin refactor of a lookup snippet; not a canonical mechanical kind)
agent: implementer af358fa9b3916d4ee
return: DONE cedc039, then merge of main ec83083 (README, marketplace.json, dev-flow plugin.json resolved keep-both); 12/12 Checks OK; judgement: dev-flow research and librarian-mode copies replaced by pointers to bindings § Store; WI=no-wi-found when nothing resolves (exit 127, never a bare python3); disclosure only, no install tip
dispatch: reviewer opus high — review round 1 of ec83083
agent: reviewer a4d208aa5ffbc9603
verdict: review round 1 NEEDS_CHANGES (must-fix 2: medium 1 — python3 -c in the install-record line puts cwd first on sys.path, so a json.py in the repo runs and breaks the lookup; fix -I in all copies plus the create-skill and spend-reader lookups; medium 2 — research's own copy removed against the operator's 2026-10-02 ruling (e184, point 1: keep research separate from dev-cycle); lows/nits: foundation drives wi bare, store test should require items/, checkpoint "once per repo whose store it writes", merge main again)
decided: 2026-10-12T19:20Z scope — finding 2 option (a): restore research's copy in the fixed form, as the operator ruled on 2026-10-02; librarian-mode's pointer stays (it already depends on dev-cycle throughout)
dispatch: implementer opus medium — fix round 1 (resume af358fa9b3916d4ee)
return: DONE dc138ad (fix round 1) + merge of main 423d490 (clean); 12/12 Checks OK (context-guard 731); harness 72 runs (4 copies × 9 scenarios × bash/sh) correct, no markers
dispatch: reviewer opus high — review round 2 of 423d490 (resume a4d208aa5ffbc9603)
verdict: review round 2 CLEAR (must-fix 0; low: README dev-flow cell and section omit foundation from the shared lookup and its no-wi fallback; note: other python3 -c snippets without -I, filed as shell-snippets-run-python3-c-without-i-a-9782; inherited WI_ROOT qualified in prose ruled acceptable; 80-run harness re-extracted from 423d490 all correct)
decided: 2026-10-12T20:10Z cap — a finish round of the README wording (authority answer 145)
dispatch: implementer opus medium — finish round (resume af358fa9b3916d4ee)
verdict: finish round CLEAR — diff read: README cell and section name foundation in the shared lookup and its no-wi fallback
landed: 27385e5 (merge of cedc039..ce23605, with two merges of main); Checks 12/12 OK; cc_scan clean
- 2026-10-12 done
