---
id: research-apply-answers-85-and-86-work-ar-adef
title: "research: apply answers 85 and 86 (work around, request tools; pdftotext for web lanes) with the verifier PDF rule"
type: feature
status: done
priority: 1
parent: research-tooling-the-tools-research-agen-04f7
created: 2026-09-25
updated: 2026-09-25
closed: 2026-09-25
refs:
  - operator 2026-09-25 answers 85, 86; absorbs research-verifier-pdf-rule-and-a-tools-l-822c
---

Operator 2026-09-25. (85) A research run never blocks on a missing tool, attended or not: it works around it (whole-PDF Read up to ~5 MB, WebFetch-saved file, could-not-verify beyond), installs nothing, and its report to the orchestrator carries a tool request (each missing tool, why, the one-line fix, and where it belongs: host or sandbox image) that the orchestrator raises to the operator. Replaces the interim stop BLOCKED and the attended ask-once in run-record.md § The tool preflight. (86) research-lane rule 8 gains a narrow exception: pdftotext and pdfinfo, only on a file the lane itself saved, output to its scratchpad; lane rule 9 gains branch (b). Also absorbs research-verifier-pdf-rule-and-a-tools-l-822c (same files): the verifier PDF rule in research-verifier.md, a Tools: line in the lane-prompt skeleton, set -f in tool-preflight.sh, run-record.md:22 wrap. Opus (agent contracts + script).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-25 claimed by Kyle-McFarlane@bf9f9839222c
target: branch worktree-research-apply-answers-85-and-86-work-ar-adef at .claude/worktrees/research-apply-answers-85-and-86-work-ar-adef, base main (f675c71)
dispatch: implementer opus — agent contracts + script
agent: implementer a150d524782df8f8b round 1
return: implementer round 1 DONE_WITH_CONCERNS 8730f9f (decisions skill named generically; TOOL GAPS lines)
dispatch: reviewer opus — fresh
agent: reviewer a1fb6bdd621b47144 round 1 at 8730f9f
verdict: reviewer round 1 NEEDS_CHANGES at 8730f9f — 2 medium (pdftotext command form: lane-chosen unquoted output name, shared scratchpad collisions, input wider than "a file the lane saved"; the operator global CLAUDE.md "Missing Tools: stop and ask" is not reconciled with never-ask), 4 low, 2 nit
dispatch: implementer opus — resume, fix round 1
agent: implementer a150d524782df8f8b fix round 1
return: implementer fix round 1 DONE_WITH_CONCERNS 457c1cc (context-guard flake once, d1e3)
dispatch: reviewer opus — resume, round 2
agent: reviewer a1fb6bdd621b47144 round 2 at 457c1cc
verdict: reviewer round 2 NEEDS_CHANGES at 457c1cc — 1 medium (nothing creates <staging>/pdf/; pdftotext cannot create it), 2 nit
librarian decision: the orchestrator creates <staging>/pdf/ with staging; lanes get no mkdir
dispatch: implementer opus — resume, fix round 2
agent: implementer a150d524782df8f8b fix round 2
return: implementer fix round 2 DONE ad8246c
dispatch: reviewer opus — resume, round 3
agent: reviewer a1fb6bdd621b47144 round 3 at ad8246c
verdict: reviewer round 3 CLEAR at ad8246c (1 low: research-refine names no staging pdf/ creation; 1 nit: SKILL.md:243 still 153 cols — filed)
landed: 115222e (merge --no-ff into main)
- 2026-09-25 done
