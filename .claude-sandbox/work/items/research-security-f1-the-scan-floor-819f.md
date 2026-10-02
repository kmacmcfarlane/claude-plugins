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
updated: 2026-10-02
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
decision 136: The research scan floor hit the 4-round review cap with one medium left; finish it how? — options: (a) one more fix round: bound the two patterns plus a test, and a fresh review [recommended] | (b) land it now with the linearity sentence struck, the bound filed as a follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-01
  revised: 2026-10-01T07:06Z — backfilled: context:, if left:, round costs:, stakes:; headline trimmed to the question
  what: whether the scan floor (the first research-security build) lands after one more small round or as is
  why now: the review cap; blocks: the deep-investigation parity build (1ffd)
  why ask: cap — another round past the cap is yours to grant
  context: you saw this card on 2026-10-01 during the unattended run · you decide whether the scan floor gets one more round — then: none
  if left: two markup patterns (comment and link) go quadratic on a hostile file of unclosed openers, so the docs' "every pass is linear" is false; it fails safe (a timeout holds the run, nothing leaks); all else left is low
  round costs: about 20-30 minutes and roughly 1% of weekly quota; another answer from you if it does not settle
  stakes: reversible, narrow — research runs
  (a) one more fix round — a one-line bound on each pattern plus a test, fresh review; lands clean — undo: n/a — who: research runs
  (b) land now, sentence struck — lands at once; a hostile lane can still force a slow scan that holds the run until the follow-up lands
  (c) leave it unlanded — nothing lands; the parity build keeps waiting
  (z) decide later — as (c)
  rec: (a) · basis strong — the reviewer measured it and names the exact fix
  unknown: none
answer 136: 136a - ask for more rounds if you can justify it based on where we are at (read as: (a) one more fix round past the cap — bound the two spans plus a test, fresh review; if that round does not clear, another round may be asked with its justification)
dispatch: implementer opus medium — resume (fix round 4 past the cap, answer 136: R1 only)
agent: implementer a33ea65041c3dc364 round 5
return: implementer DONE 638479b
dispatch: reviewer opus high — fresh review, round 5 (granted past the cap, answer 136)
agent: reviewer a0a35fdcad507b97f round 5
verdict: NEEDS_CHANGES round 5 at 638479b
findings:
  R1 FIXED (0.11 s on 100k "<!-- "); the bounds reopen split forms (nested opener, >1000-char comment/link text) — rated low, docstring names them residual
  1. [medium] scan-findings.py:104,113,118 — other patterns still stall on tiny inputs: _ATTRS (control-tag) exponential ('<system' + ' a="x"'*40, 247 bytes, >60 s), control-tag \s*/?\s* and agent-addressed \s*,?\s+ quadratic (20k spaces: 11-14 s); docstring :52 "every pass is linear" and the Bounded tests' claim false; fail-closed only if the caller times out, and run-record.md:271-273's commands carry no timeout, so one string in a fetched page can stall a research run; fix: unquoted value [^\s>"']+, \s*(?:/\s*)?, (?:\s*,)?\s+, timeout 120 on the run-record commands, Bounded cases for the three inputs
  2. [low] scan-findings.py:142 — replace _COMMENT with a linear find loop (no length cap), closing the nested-opener and long-comment split forms
  note: harness flagged instruction-shaped text in this return — the reviewer's hostile test strings (control tags), not directives
decision 138: The research scan floor's granted round fixed the slow comment and link patterns, but the fresh review found three other patterns that stall on a tiny hostile string, and the research run's scan commands have no timeout; another round? — options: (a) one more fix round: the three pattern rewrites the reviewer gives, a timeout on the scan commands, tests, plus the linear comment loop; same reviewer re-checks [recommended] | (b) land now and file the stall fix as a P1 follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-01T07:22Z
  what: whether the scan floor (the first research-security build) gets a sixth review round to close a newly found stall
  why now: the granted round 5 ended NEEDS_CHANGES; blocks: the deep-investigation parity build (1ffd), and through it the confinement hook (20d8)
  why ask: cap — you said to ask for more rounds when I can justify them (answer 136)
  context: you granted one round past the cap on 2026-10-01 to bound two slow patterns · you decide whether a newly found stall in three other patterns gets one more round — then: none
  if left: a 247-byte string in any fetched page can make the scan run for minutes to hours, and the research run's scan commands carry no timeout, so the run stalls instead of failing closed; nothing leaks. Also low: the new bounds let a split phrase hide behind a nested comment opener or 1000+ characters of comment or link text (the linear comment loop closes the comment half)
  round costs: about 30-40 minutes and roughly 1% of weekly quota (weekly at 58%); your attention again only if this round does not clear
  stakes: reversible, narrow — research runs
  (a) one more fix round — exact fixes the reviewer already checked on 500 KB inputs (0.04 s), a timeout on the commands, regression tests; lands with no known medium — undo: n/a — who: research runs
  (b) land now, P1 follow-up — the scan floor and its wiring land at once; until the follow-up, a hostile page can stall a research run
  (c) leave it unlanded — nothing lands; the parity build and the hook keep waiting
  (z) decide later — as (c)
  rec: (a) · basis strong — the reviewer measured each stall and verified the rewritten pattern matches the same samples in 0.04 s
  unknown: whether a further fresh look would find more slow patterns; this round's reviewer read every pattern in the file
answer 138: a
dispatch: implementer opus medium — resume (fix round 5, answer 138: finding 1 + low 2)
agent: implementer a33ea65041c3dc364 round 6
return: implementer DONE 0767b69 (plus two script-write stalls beyond the brief)
librarian ruling: the script-write fixes are accepted — same finding (the docstring's "every pass is linear" claim), same file, tested; the reviewer checks them
dispatch: reviewer opus high — resume (round 6, checks round-5 fixes)
agent: reviewer a0a35fdcad507b97f round 6
verdict: NEEDS_CHANGES round 6 at 0767b69
findings:
  round-5 1 FIXED (measured: 0.02-0.16 s on every prior hostile input), 2 FIXED (strip_comments exact and linear)
  1. [medium] scan-findings.py:120,129,148 — three more patterns backtrack: pipe-to-shell sudo option chain ("sudo " + "-curl|sudo "*2000: 9.1 s; x8000 killed at 60 s), script-secret-path /proc/\S*environ ("/proc/"*20000: 5.9 s), _CONCAT_GAP \s*\+?\s* ('"a"' + 80k spaces: 11.6 s); a timeout holds the whole run (no lines to strip); fix: (?:-\S+\s+){0,8}, /proc/\S{0,64}?environ, \s*(?:\+\s*)?, NoBacktracking cases
  2. [medium] scan-findings.py:107,116 — control-tag HOLD bypassed by a bare attribute (every round), regression this round (unquoted value containing a quote no longer matches), and a tag split across lines never matched; fix: _ATTRS = (?:\s+[\w:-]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>"'][^\s>]*))?)* (checked linear and matching), HOLD an unclosed opener at line end or name it as a residual, tests
  3. [low] scan-findings.py:128 — the 200-char open() cap lets open(<201 chars>, "w") through; the rule was already easy to evade (method calls, variable modes); optional residual note
decision 143: The scan floor's sixth review found two more mediums — three more patterns that stall, and a cheap way past the control-tag hold — each with an exact fix; another round? — options: (a) one more fix round with the exact fixes, plus a test that times every pattern against a standard set of hostile shapes so no further stall is left to find one at a time [recommended] | (b) land now and file both as a P1 follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-02T07:46Z
  what: whether the research scan floor (819f) gets a seventh review round
  why now: the round you granted (answer 138) ended with changes still needed; blocks: the deep-investigation parity build (1ffd), and through it the confinement hook (20d8)
  why ask: cap — you asked me to ask for more rounds when I can justify them (answer 136)
  context: you granted round 6 to fix three stalling patterns; they are fixed · you decide whether the two new mediums get one more round — then: none
  if left: (1) three more patterns stall on a 22-120 KB hostile string; the run now fails closed under the 2-minute timeout, but the whole run is held instead of stripping the bad lines; (2) a tag like <system-reminder foo> with one bare word inside slips past the control-tag hold (true in every round so far), and this round's change also let a quoted value slip through
  round costs: about 40 minutes and roughly 1% of weekly quota; your attention again if this round does not clear — each fresh pass so far has found new slow patterns, which is why (a) adds a test over every pattern instead of fixing them one at a time
  stakes: reversible, narrow — research runs
  (a) one more fix round + a timing test over every pattern — the reviewer's exact fixes (each checked: 0.002-2 s on 500 KB, the real cases still match) and a test that runs every pattern against repeated prefixes, long space runs and unclosed openers, so the next review checks a property, not a list — undo: n/a — who: research runs
  (b) land now, P1 follow-up — the scan floor protects runs from tonight; until the follow-up, a hostile page can hold a run for 2 minutes and a bare-word tag slips past the hold
  (c) leave it unlanded — the parity build and the hook keep waiting
  (z) decide later — as (c)
  rec: (a) · basis strong — the reviewer measured each stall and bypass and verified each fix; the timing test turns the remaining unknown into a check
  unknown: whether the property test will surface more patterns that need the same treatment
answer 143: a
dispatch: implementer opus medium — resume (fix round 6, answer 143: round-6 1, 2 + a timing property test over every pattern)
agent: implementer a33ea65041c3dc364 round 7
return: implementer DONE f818c50 (property test tests/test_scan_patterns.py; the suggested _ATTRS was itself quadratic, fixed with no < in values)
dispatch: reviewer opus high — resume (round 7, checks round-6 fixes and the property test)
agent: reviewer a0a35fdcad507b97f round 7
verdict: NEEDS_CHANGES round 7 at f818c50
findings:
  round-6 1 FIXED (all linear 60 KB → 500 KB, measured), 2 FIXED for the forms named; a 5-token fuzz finds no stall on f818c50
  1. [medium] scan-findings.py:110,119 — banning < from attribute values opens a 6-character control-tag bypass: <system-reminder a="<">, </system-reminder a="<">, data-x="1<2", a=<> all scan 0 hold (the joined view's _TAG too); fix: hold on a glued opener alone, full attribute parse only for the spaced form: <(?:/\s*)?TAGS(?![\w-])(?=[\s/>]|$) | <\s+(?:/\s*)?TAGS(?![\w-])_ATTRS\s*(?:/\s*)?> (checked: matches all bypasses, samples, bare attrs, a=b"c, unclosed at line end; rejects <path>, <systems> and finding 2's false positive; 500 KB ≤0.02 s)
  2. [low] scan-findings.py:119 — the end-of-line alternative with <\s* false-HOLDs prose ("context < system prompt size", "the <instructions element"); fix 1 drops it
  3. [low] tests/test_scan_patterns.py:21,35 — a fixed 1 s at 60 KB is too loose (small-constant quadratics pass) and close to flaky (0.24-0.30 s linear cases); test growth: time at N and 4N, fail when the ratio > ~8 and the larger time > ~50 ms; keep an absolute stall guard (~10 s)
  4. [nit] the property test's "every compiled pattern" misses two inline trivially linear regexes; hoist or soften the wording
decision 144: The scan floor's seventh review confirmed every stall fixed, but found a 6-character way past the control-tag hold that this round's stall fix opened; another round? — options: (a) one more fix round: the reviewer's checked tag rule (a bare tag opener holds on its own), a growth-rate check in the timing test, the two lows; then land, and file any further bypass the next review finds as a follow-up instead of another round [recommended] | (b) land now and file the bypass and the lows as a P1 follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-02T17:08Z
  what: whether the research scan floor (819f) gets an eighth review round, and whether bypass-hunting stops gating the landing after it
  why now: the round you granted (answer 143) ended with changes still needed; blocks: the deep-investigation parity build (1ffd), and through it the confinement hook (20d8)
  why ask: cap — you asked me to ask for more rounds when I can justify them (answer 136)
  context: you granted round 7 for three more stalls plus a timing test over every pattern; the stalls are fixed and the test caught a slow pattern on its first run · you decide whether one bypass gets one more round, and whether later bypass findings stop holding the landing — then: none
  if left: an injected tag written <system-reminder a="<"> (6 extra characters) escapes the control-tag hold, so a hijacked page could carry instructions past the floor; also low: ordinary prose like "context < system prompt size" now holds a whole run, and the timing test could miss a slow pattern with a small constant
  round costs: measured on this item — a fix round about $6 of list-price spend (about 0.16% of a week) and 10-20 minutes; my earlier cards' "about 1% of weekly, 30-40 minutes" overstated it; your attention again only if (a)'s round does not clear
  stakes: reversible, narrow — research runs
  (a) one more round, then land — the reviewer's tag rule (checked against every bypass, the samples and the false positive, linear at 500 KB), the test checks growth from 30 KB to 120 KB instead of a fixed time, and the two lows; every review so far found a new bypass, so after this round a further bypass is filed as a follow-up and does not hold the landing — undo: n/a — who: research runs
  (b) land now, P1 follow-up — the stall fixes and the floor protect runs at once; until the follow-up, a 6-character tag escapes the hold and some ordinary prose holds a run
  (c) leave it unlanded — the parity build and the hook keep waiting
  (z) decide later — as (c)
  rec: (a) · basis strong — the reviewer verified the fix against every known form; the stop rule ends the one-bypass-per-round pattern
  unknown: how many more bypass forms a determined page could find; a pattern-based floor never closes all of them
  revised: 2026-10-02T17:10Z — decision 144's round cost: the cost-budget plan review (f65b) found the per-item dollars priced the 5.5 models too high (~1.7x); at cited prices a fix round on this item is about $3-4 list price, not $6; options and recommendation unchanged
  revised: 2026-10-02T17:18Z — decision 144's round cost again: measured at cited prices, an 819f fix round is $3.57-5.21 (median $4.73), 8-30 minutes; about $4-5, about 0.2% of a week; options and recommendation unchanged
  revised: 2026-10-02T17:28Z — decision 144's round cost settled: $3.57-5.21 per 819f fix round, median $4.73 (about $4-5, about 0.2% of a week), confirmed after the cost evidence was corrected
answer 144: a
dispatch: implementer opus medium — resume (fix round 7, answer 144: round-7 1-4; after this round a further bypass is filed as a follow-up and does not hold the landing)
agent: implementer a33ea65041c3dc364 round 8
