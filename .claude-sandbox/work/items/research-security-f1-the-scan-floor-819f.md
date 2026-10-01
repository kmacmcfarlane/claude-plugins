---
id: research-security-f1-the-scan-floor-819f
title: "research security F1: the scan floor"
short_display_name: research scan floor
type: feature
status: blocked
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
blocked: decision 136 (review cap)
created: 2026-09-30
updated: 2026-10-01
refs:
  - .claude-sandbox/investigations/caef-research-security/05_second-opinion-closing.md
---

caef serial 05 F1 (acceptance A1.1-A1.3; failing tests first). Unblocked: needs no card.

## Handoff
- doing: —
- next: blocked on decision 136 (cap): (a) resume implementer a33ea65041c3dc364 to bound _COMMENT/_LINK + test, fresh review; (b) strike the linearity sentence, land, follow-up
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
verdict: NEEDS_CHANGES round 2 at 09846cb
findings:
  prior 1-7, 9-13 FIXED; 8 PARTIAL (two parts DECLINED, accepted); 14 PARTIAL
  N1. [medium] scan-findings.py:246-255 — prose rules run per segment; a code span or quote boundary inside a HOLD phrase splits it: findings-mode `Ig…nore all `previous` instructions`, `` `Human`: ``, `curl … `|` sh`; scripts-mode split/concatenated literals, "\n\nHuman: …", x = "Human: …" — exit 0, no FLAG; contradicts run-record.md:291-294 "hold anywhere in a script"
  N2. [low] scan-findings.py:320 — os.walk without onerror skips an unreadable dir silently
  N3. [low] scan-findings.py:99 — optional opening quote HOLDs benign `"Human:" and "Assistant:" are the role labels.`
  N4. [low] run-record.md:261-263 — FLAG lines in verification.md / 01-synthesis.md at Step 10 are adjudicated by no one
dispatch: implementer opus medium — resume
agent: implementer a33ea65041c3dc364 round 3
return: implementer DONE d79f37e
dispatch: reviewer opus high — resume
agent: reviewer af1c1850266095f2a round 3
verdict: NEEDS_CHANGES round 3 at d79f37e
findings:
  N1 PARTIAL (mid-word quote in markdown silent; run-record.md:282 claim false); N2 FIXED; N3 PARTIAL (bypass N6); N4 PARTIAL (backticked override in verification.md FLAG, lands unadjudicated; STATUS effect unstated)
  N5. [medium] scan-findings.py:242 — joined markdown view drops only backticks: mid-word emphasis, links, inline HTML/comments, entities, backslash, mid-word quote split a HOLD phrase silently
  N6. [low] scan-findings.py:102 — the quote lookahead exempts a real turn Human:'…'
  N7. [medium] scan-findings.py:281 — per-line `have` set walks every hit so far: quadratic in hits (80k flagged lines 66.5 s vs 0.82 s); docstring's linear claim false
  N8. [low] scan-findings.py:281-284 — joined-view check skips a rule already found on the line
  N9. [low] scan-findings.py:237-248 — each literal read as a line start: startswith("Human:") HOLDs a benign parser
librarian ruling: fix N5 (a de-markup pass for the joined view) and N7 (per-line hit set, with a many-hit linear-time test); state what the static floor still cannot catch as a named residual in run-record.md instead of any "still holds" claim; N6, N8, N9 cheap fixes unless declined with reason; N4: say a landing FLAG in an unadjudicated file makes the run DONE_WITH_CONCERNS
dispatch: implementer opus medium — resume (fix round 3; the next review is round 4, the cap)
agent: implementer a33ea65041c3dc364 round 4
return: implementer DONE 827334a
dispatch: reviewer opus high — resume
agent: reviewer af1c1850266095f2a round 4
verdict: NEEDS_CHANGES round 4 at 827334a
findings:
  N1, N4, N5, N7, N9 FIXED; N6, N8 PARTIAL (low)
  R1. [medium] scan-findings.py:139-140 — _COMMENT and _LINK lazy spans are quadratic on unclosed openers (100k "<!-- " 500 KB: 118.9 s); docstring :52 "every pass is linear" false; fail-closed (a timeout holds the run); only a hostile file triggers it; fix: bound the spans (<!--[^\n]{0,1000}?-->) or drop the claim
  R2. [low] _CONCAT_GAP lacks string prefixes (f"", r"")
  R3. [low] a markdown table row with curl | … reads as pipe-to-shell HOLD
cap: 4 review rounds without CLEAR — blocked; decision 136
decision 136: The research scan floor (the first research-security build) hit the 4-round review cap with one medium left: two markup patterns go slow (quadratic) on a hostile file of unclosed openers, so the docs' "every pass is linear" is false; it fails safe (a timeout holds the run). Finish it how? — options: (a) one more fix round: bound the two patterns (a one-line change each) plus a test, and a fresh review [recommended] | (b) land it now with the linearity sentence struck as the only edit, the bound filed as a follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-01
  what: whether the scan floor lands after one more small round or as is
  why now: the review cap; the deep-investigation parity build (1ffd) waits on it
  why ask: cap — another round past the cap is yours to grant
  (a): about 20-30 minutes and roughly 1% of weekly quota; lands clean — undo: n/a — who: research runs
  (b): lands tonight; a hostile lane can still force a slow scan that holds the run (fail-safe) until the follow-up lands
  (c): nothing lands; 1ffd keeps waiting
  (z): as (c)
  rec: (a) · basis strong — the reviewer measured it and names the exact fix; everything else left is low
  unknown: none
