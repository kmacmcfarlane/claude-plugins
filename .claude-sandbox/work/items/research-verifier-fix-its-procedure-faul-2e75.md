---
id: research-verifier-fix-its-procedure-faul-2e75
title: "research-verifier: fix its procedure faults (unopened sources, hand-typed counts, leading prompts)"
short_display_name: verifier procedure faults
type: bug
status: todo
priority: 2
deps:
  - research-security-f1-the-scan-floor-819f
created: 2026-10-02
updated: 2026-10-02
refs:
  - research-skills-effort-based-routing-par-e184
---

From the research-routing plan (e184, series .claude-sandbox/investigations/e184-research-routing/, evidence/verifier-record.md): moving the verifier to sonnet alone will not fix verdicts given for sources never opened (at least 13 of 112 across 5 runs), header counts typed by hand instead of tallied from the table, leading fetch prompts, and the run's own files cited as sources. Lands after 819f (same files). Acceptance: an unopened source is an UNREACHABLE/NOT_FOUND verdict; header counts derived from the table; neutral fetch prompts; own-run files excluded as sources; tests where a script can check it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
