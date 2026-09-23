---
id: context-guard-correct-the-1-4-compaction-8519
title: "context-guard: correct the 1.4% compaction-survival claim and the one-shot PreCompact wording"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-23T00:02Z
created: 2026-09-22
updated: 2026-09-23
refs:
  - "peer: agents - librarian (uds 122.sock); agents decisions/0007"
---

Relayed 2026-09-22 (agents decision 0007, 62b8a9b, decisions/0007-correct-0004-compaction-facts.md): (1) the 1.4% figure came from a MANUAL /compact; across four compact_boundary records the summary stays in a ~14-18K band, so the percentage falls with depth by arithmetic — it is not auto-compact's survival rate; (2) PreCompact re-defers on every automatic attempt until a checkpoint or HARD (precompact_gate.py:46-60), not one-shot. Acceptance: checkpoint SKILL.md and references/design-rationale.md (and any other context-guard text) state the corrected facts with the 0007 pointer; 0d6b (DUE ladder) reads them first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-correct-the-1-4-compaction-8519 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-correct-the-1-4-compaction-8519
dispatch: implementer sonnet — factual doc corrections, one plugin
