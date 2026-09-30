---
id: research-security-f1-the-scan-floor-819f
title: "research security F1: the scan floor"
short_display_name: research scan floor
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/caef-research-security/05_second-opinion-closing.md
---

caef serial 05 F1 (acceptance A1.1-A1.3; failing tests first). Unblocked: needs no card.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: full research-security-f1-the-scan-floor-819f /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/research-security-f1-the-scan-floor-819f
dispatch: implementer opus medium — opus signal: scripts/ and tests; given plan caef 00-05: /implement (waves 1-3, 132 a)
agent: implementer a33ea65041c3dc364 round 1
return: implementer DONE_WITH_CONCERNS 06a76df
changed:
  plugins/dev-flow/skills/research/scripts/scan-findings.py — new: the scanner (A1.1-A1.3)
  plugins/dev-flow/skills/research/scripts/tests/test_scan_findings.py — new: 42 tests, fixtures built at run time
  plugins/dev-flow/skills/research/SKILL.md — wires the scan into Steps 4, 6, 8, 10
  plugins/dev-flow/skills/research/references/run-record.md — scan floor, toolkit gate, ledger kinds
  plugins/dev-flow/agents/research-verifier.md — judges FLAG lines; script review task
  plugins/dev-flow/skills/research/references/research-criteria.md — HOLD carries the security mark (00 Files to Modify)
  plugins/dev-flow/skills/research/references/storage-and-knowledge-base.md — staging names the scan (00 Files to Modify)
  plugins/dev-flow/skills/research-deep/SKILL.md — toolkit bullet made wrong by the change
  CLAUDE.md — research/scripts layout line names scan-findings.py (00 Files to Modify)
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer af1c1850266095f2a round 1
verdict: NEEDS_CHANGES round 1 at 06a76df
findings:
  1. [high] tests/test_scan_findings.py — untested: unreadable file HOLD (scan-findings.py:245-246), symlinked dir skip+flag (:263-266); no negative for special-token or each script-* rule
  2. [medium] scan-findings.py:209-215, run-record.md:285 — --scripts: any quoted HOLD shape drops to FLAG, in comments and docstrings too (8/8 probed); 02:169-170 runs HOLD over comments and string literals
  3. [medium] scan-findings.py:264-271, 283-284 — a symlink is FLAG and its target never scanned, but verifier and orchestrator follow it; should HOLD
  4. [medium] run-record.md:259, SKILL.md Step 10 (:257-259) — rescan before landing covers findings/ only; verification.md and 01-synthesis.md carry source excerpts and land unscanned
  5. [medium] research-refine SKILL.md:115; research SKILL.md:279, storage-and-knowledge-base.md:72-73 — gate readers still check the verifier sheet only, not the scanner HOLD
  6. [medium] scan-findings.py:243, 112-129; run-record.md:271 — no rule that a timeout/crash/other exit holds the run; FIFO blocks forever; unclosed fences quadratic (80 KB 16.7 s); --strip on unreadable file tracebacks as exit 1
  7. [medium] research SKILL.md:170 vs :201 — Step 7 reads TL;DR and Could-not-verify before Step 8's first scan (pre-existing)
  8. [low] line-based rules miss split overrides, homoglyphs, curl|tee|sh
  9. [low] display() escapes ancestors: a space in the staging path makes every file unsafe-filename FLAG; escaped path unusable by --strip
  10. [low] predictable strip temp name followed through a planted symlink
  11. [low] ^ anchors after a code span: `x` Assistant: hello HOLDs (false positive)
  12. [low] SKILL.md Step 8 (:207-214) — strip procedure: one call or rescan; row→position mapping; line-0 HOLD
  13. [low] --scripts treats *.md as markdown, no script rules
  14. [nit] --help lacks output and exit codes; research SKILL.md size
librarian ruling on 7: fix it here — a small wiring change in a file already in scope (scan at Step 7 and never open a file with a HOLD), not a separate item
dispatch: implementer opus medium — resume
agent: implementer a33ea65041c3dc364 round 2
return: implementer DONE_WITH_CONCERNS 09846cb
changed: + plugins/dev-flow/skills/research-refine/SKILL.md — a prior whose rescan finds a HOLD counts as held (finding 5); others as before
note: the implementer sent SIGTERM by pattern to test processes that were not all its own (pkill absent) — likely other agents' exit 143/144 Check kills tonight; filed dev-cycle-briefs-never-signal-processes-54fe
dispatch: reviewer opus high — resume
agent: reviewer af1c1850266095f2a round 2
