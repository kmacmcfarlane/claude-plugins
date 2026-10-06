---
id: research-security-f2-deep-investigation-1ffd
title: "research security F2: deep-investigation parity"
short_display_name: deep-investigation parity
type: feature
status: done
priority: 2
deps:
  - research-security-f1-the-scan-floor-819f
created: 2026-09-30
updated: 2026-10-06
closed: 2026-10-06
refs:
  - .claude-sandbox/investigations/caef-research-security/05_second-opinion-closing.md
---

caef serial 05 F2 (acceptance A2.1), after F1 per the series order.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: full research-security-f2-deep-investigation-1ffd /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/research-security-f2-deep-investigation-1ffd
budget: 2026-10-06T01:53Z build $22 — default other build
dispatch: implementer opus medium — build (caef series F2: 00 § F2 as amended by 01, 02, plus 05 A2.1; on main after e184 7bd41bc)
agent: implementer a4e5c61bb52b28988 round 1
return: implementer DONE_WITH_CONCERNS 421a989 (prose mostly; no live fan-out run; research/research-refine held paths still cwd-relative until F3; read-allow.json left to F3; SKILL.md 3830 words)
changed:
  plugins/dev-flow/skills/deep-investigation/SKILL.md — F2 core: security preamble, staging, research-lane launch, toolkit-gate wait, lane-free ledger, Step 6.5 scan/verify/hold/land, held path at H (A2.1)
  plugins/dev-flow/skills/deep-investigation/references/lane-contract.md — output to staging in the research-lane shape; security from the agent body
  plugins/dev-flow/skills/deep-investigation/references/research-strategy-format.md — Staging: line; lane-free DONE; new entry kinds
  plugins/dev-flow/skills/research/references/intensity-and-routing.md — e184's interim deep-investigation row removed; Profiles rows name deep-investigation
  plugins/dev-flow/agents/research-lane.md — description lists deep-investigation (frontmatter only)
  plugins/dev-flow/tests/test_deep_investigation.py — 17 tests of the F2 rules, H snippet run on a worktree fixture
  CLAUDE.md — layout comment names the new test file
  plugins/kit-dev/skills/update-kit/references/repo-map.md — same layout line
librarian ruling: concerns go to the reviewer; the held-path split between research and deep-investigation until F3 is the series' own sequencing (A3.9 is F3 acceptance)
dispatch: reviewer opus high — review round 1
agent: reviewer a414ae0b52bf6263c round 1
verdict: NEEDS_CHANGES round 1 at 421a989
findings:
  1. [medium] deep-investigation/SKILL.md:235-240 — landing copy is unconditional after the rescan and not limited to step-1-scanned files; a late lane or a HOLDing verification.md lands unscanned or held text. Fix: SKILL.md:237 — "Copy only files that step 1 scanned and in which this rescan finds no HOLD; anything else stays in staging, and a failed rescan holds every file it covered."
  2. [medium] lane-contract.md:84-92 (SKILL.md:125-127, :158-161) — later-wave lanes get earlier lanes' unscanned staged findings as read-first, incl. the toolkit lane's mining plan whose commands a mining lane runs; research scans per round, deep-investigation only at 6.5
  3. [medium] deep-investigation/SKILL.md:345-347 — the sensitive-data edge case ("fix the file in staging before 6.5 lands it") can't be followed (orchestrator first reads at Step 7, after landing; contradicts never-Read/never-clean). Fix: SKILL.md:345-347 — "**Sensitive data appears in a findings file** — the inline rule failed. Remove it from `<series>/findings/` before anything is committed, do not quote it onward, and record it in the retro as a prompt bug."
  4. [low] SKILL.md:233 — "its category marked unexamined" wider than 00 § F2. Fix: SKILL.md:233 — "synthesize without it, the lane marked unexamined."
  5. [low] test_deep_investigation.py:105-106 — test_nothing_unscanned_lands passes on the preamble alone
  6. [low] deep-investigation SKILL.md ~5100 tokens by words; Step 6.5 could move to a reference
  7. [nit] agents/research-verifier.md:3 — description still says "Dispatched by the research skills"
  8. [nit] SKILL.md:221-222 — bare intensity-and-routing.md without the research skill prefix; "routed as Step 4's lanes are" reads as giving the verifier the lane model
cost: 2026-10-06T02:18Z build $8.89 of $22 after review 1 — must-fix 3 — prices 2
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer a4e5c61bb52b28988 round 2
return: implementer DONE_WITH_CONCERNS 70b5d80 (1-5, 7, 8 fixed; 6 partly: gate moved to references/security-gate.md, SKILL.md 3830→3533 words, still ~5500 tokens; mining plan gets a --scripts scan and joins the toolkit review)
changed:
  plugins/dev-flow/skills/deep-investigation/references/security-gate.md — new: pre-read scan, Step 6.5 scan/verify/hold/land with the conditional copy, held path and anchor (moved from SKILL.md)
  plugins/dev-flow/skills/deep-investigation/SKILL.md — Step 6.5 summary pointer; Step 4 scan-before-a-lane-reads-a-lane; sensitive-data edge case
  plugins/dev-flow/skills/deep-investigation/references/lane-contract.md — no lane reads an earlier lane's file before its scan
  plugins/dev-flow/skills/deep-investigation/references/research-strategy-format.md — DONE line values are the orchestrator's own
  plugins/dev-flow/agents/research-verifier.md — description names deep-investigation
  plugins/dev-flow/tests/test_deep_investigation.py — landing condition, pre-read scan, verifier row, edge case tests
dispatch: reviewer opus high — resume (review round 2)
agent: reviewer a414ae0b52bf6263c round 2
verdict: CLEAR round 2 at 70b5d80
findings:
  round 1: 1-5, 7, 8 FIXED; 6 PARTIAL, decline accepted (nit)
  1. [low] security-gate.md:49-55 — "copy only files that step 1 scanned" excludes verification.md, tools-review.md, tools/. Fix: security-gate.md:51 — "Copy only findings that step 1 scanned, and only files in which this rescan finds no HOLD; anything else stays in staging, and a failed rescan holds every file it covered."
  2. [low] security-gate.md:22-25 — a held mining plan can take the interactive clean path, whose recheck is a plain rescan that misses a curl line. Fix: security-gate.md:24 — "A held mining plan is never cleaned: it holds the mining round, as a held toolkit does: the mining lanes are ledgered `FAILED` and the run goes on without them."
  3. [low] SKILL.md:162-165 — the mining plan's --scripts scan and script review live only in the reference. Fix: SKILL.md:164 — "file as `references/security-gate.md` § Before a lane reads another lane's file says (the mining plan also with `--scripts` and into the toolkit gate's script review). A"
  4. [low] security-gate.md:24 — FLAGs on ordinary read-first files hold nothing (parity with research Step 7); family-wide follow-up
  5. [nit] security-gate.md:53 — "ledger it" names no entry kind for a late lane
cost: 2026-10-06T02:30Z build $13.66 of $22 after review 2 — must-fix 0 — prices 2
decided: one more round for lows 1-3 and nit 5 before landing — CLEAR, but 2 and 3 leave a path where a mining lane runs an unflagged network command, the failure F2 exists to close; exact Fix: lines, a resumed round inside the $22 budget; low 4 goes to research-scan-a-round-s-findings-and-the-a012 — class: cap
dispatch: implementer opus medium — resume (fix round 2, lows)
agent: implementer a4e5c61bb52b28988 round 3
return: implementer DONE bc94501 (lows 1-3 and nit 5 fixed with the given wording; late lane marked on its DONE line; tests pin each)
changed:
  plugins/dev-flow/skills/deep-investigation/references/security-gate.md — landing copy scope; held mining plan never cleaned; late-lane marker
  plugins/dev-flow/skills/deep-investigation/SKILL.md — Step 4 bullet names the mining plan's --scripts scan and script review inline
  plugins/dev-flow/skills/deep-investigation/references/research-strategy-format.md — late, not landed marker under DONE
  plugins/dev-flow/tests/test_deep_investigation.py — pins moved and added
dispatch: reviewer opus high — resume (review round 3)
agent: reviewer a414ae0b52bf6263c round 3
verdict: CLEAR round 3 at bc94501
findings:
  round 2: 1, 2, 3, 5 FIXED; 4 OPEN, filed family-wide (research-scan-a-round-s-findings-and-the-a012)
  1. [nit] research-strategy-format.md:120-121, security-gate.md:53 — "finishes after the scan" judged by report arrival; a lane that wrote before step 1 and reported after lands while its DONE line says late, not landed (errs toward under-claiming)
declined: nit 1 — errs safe; the ledger is append-only and a later LANDED line follows
cost: 2026-10-06T02:38Z build $16.24 of $22 after review 3 — must-fix 0 — prices 2
landed: 3626e8b
- 2026-10-06 done: 3626e8b
