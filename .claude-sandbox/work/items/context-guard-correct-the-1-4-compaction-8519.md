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
- doing: review r2 in flight at 95cba7f: reviewer a0a81a13103b14bc3 round 2
- next: on CLEAR: land; on NEEDS_CHANGES: resume implementer a94723f9f73124a7c
- blocked: —
- learned: —

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-correct-the-1-4-compaction-8519 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-correct-the-1-4-compaction-8519
dispatch: implementer sonnet — factual doc corrections, one plugin
agent: implementer a94723f9f73124a7c round 1
return: implementer DONE d3cb48e
changed: checkpoint SKILL.md, references/{operator-playbook,design-rationale}.md
dispatch: reviewer opus — rule 4 floor (impl sonnet)
agent: reviewer a0a81a13103b14bc3 round 1
verdict: NEEDS_CHANGES round 1 at d3cb48e (precompact_gate.py:46-60 behaviour confirmed)
findings:
- [medium] operator-playbook.md:73 — the /compact <guidance> row still says "keeps ~2%" (the ratio framing 0007 retires). Pass: "keeps a ~14–18K-token summary, whatever the depth (agents decision 0007)".
- [low] design-rationale.md:46-48 "confirmed … across manual and auto (14–18K, n=4)" overclaims — 0007 has one auto case, band 13.7–18.4K; [low] :138 stale "matcher auto" (hooks.json registers ""; the script filters manual); [low] SKILL.md:11-13 sentence no longer parses; [nit] :3-4 banner "a one-shot compact gate".
note for 0d6b: the deferral also ends at unknown depth and at a new epoch (PostCompact/clear reset).
dispatch: implementer sonnet — fix round 1 (resume)
agent: implementer a94723f9f73124a7c round 2
return: implementer DONE 95cba7f
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a0a81a13103b14bc3 round 2
