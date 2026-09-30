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
