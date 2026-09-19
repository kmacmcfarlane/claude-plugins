---
id: create-skill-review-checklist-allowed-to-c5fc
title: "create-skill + review-checklist: allowed-tools semantics and the frontmatter key-set rule"
type: chore
status: todo
priority: 2
deps:
  - dev-flow-cross-skill-reference-conventio-05bb
created: 2026-09-19
updated: 2026-09-19
---

From the 49be review (2026-09-19): (1) create-skill frontmatter-reference.md:49-52 says allowed-tools 'Restricts which tools the skill can use' / 'Be as restrictive as possible' and SKILL.md:38 'list only the tools the skill actually needs' — the docs (code.claude.com/docs/en/skills) say it only pre-approves the listed tools for the invoking turn and never restricts; omitted = nothing pre-approved. Rewrite accordingly. (2) librarian-mode review-checklist §2 (and agent-brief:59) require exactly name/description/disable-model-invocation/allowed-tools/argument-hint, while create-skill says all but name are optional and documents model, license, compatibility, metadata, context. Make them agree (house rule stated explicitly, or checklist accepts the documented optional fields). Lands after 05bb (same checklist) and before 07c3 F1 moves the checklist.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
