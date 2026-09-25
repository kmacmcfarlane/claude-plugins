---
id: research-apply-answers-85-and-86-work-ar-adef
title: "research: apply answers 85 and 86 (work around, request tools; pdftotext for web lanes) with the verifier PDF rule"
type: feature
status: doing
priority: 1
parent: research-tooling-the-tools-research-agen-04f7
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-25T18:04Z
created: 2026-09-25
updated: 2026-09-25
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
