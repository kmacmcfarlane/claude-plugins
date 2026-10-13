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
target: an agent worktree branch off main (3d839b5c); dev-flow agents/research-verifier.md + research scripts
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — verifier procedure faults
agent: implementer a58a079d03da1daa5 round 1
result: DONE round 1 at dbbc775f (verifier body rules: opened-only, neutral prompts, never a run file, claim as written; new research/scripts/check-sheet.py + 9 tests; test_research_verifier.py; SKILL.md, run-record.md, security-gate.md run the check; CLAUDE.md layout, repo-map; dev-flow 81, research 115, kit-dev 21 OK)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer ac442c0e0fb4c51c7 round 1 at dbbc775f
verdict: NEEDS_CHANGES round 1 at dbbc775f (2 medium: Opened cell is free text and its target is never compared with Source; Source cell undefined when following a run file back; 5 low: digit text can reach stderr, bare/cwd/file:// run-file paths missed, empty table passes, deep-investigation has no place for a sheet defect, research-refine prior record not a run file; 5 nits incl. pyright annotations; transcript cross-check filed as a follow-up)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer a58a079d03da1daa5 round 2
result: DONE round 2 at 9bd9e0eb (all 12 applied; dev-flow 81, research 123, kit-dev 21 OK)
dispatch: reviewer opus high — resume, round 2
agent: reviewer ac442c0e0fb4c51c7 round 2 at 9bd9e0eb
verdict: NEEDS_CHANGES round 2 at 9bd9e0eb (2 medium: web PDF read from its saved file and repo-relative Source opened by absolute path both flagged opened-elsewhere; 3 low: scheme/trailing slash, UNREACHABLE note, bare name shadowed by --own; 3 nits; all 12 round-1 fixes confirmed; no sheet text leaks)
dispatch: implementer opus medium — resume, fix round 2
agent: implementer a58a079d03da1daa5 round 3
result: DONE round 3 at f90b41dd (all 8 applied; research 126 OK; pyright 0 errors)
dispatch: reviewer opus high — resume, round 3
agent: reviewer ac442c0e0fb4c51c7 round 3 at f90b41dd
