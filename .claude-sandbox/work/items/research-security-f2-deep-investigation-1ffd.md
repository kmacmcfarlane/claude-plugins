---
id: research-security-f2-deep-investigation-1ffd
title: "research security F2: deep-investigation parity"
short_display_name: deep-investigation parity
type: feature
status: doing
priority: 2
deps:
  - research-security-f1-the-scan-floor-819f
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T01:53Z
created: 2026-09-30
updated: 2026-10-06
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
