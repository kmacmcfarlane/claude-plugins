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
