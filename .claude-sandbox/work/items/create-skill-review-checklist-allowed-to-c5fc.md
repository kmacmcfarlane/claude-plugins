---
id: create-skill-review-checklist-allowed-to-c5fc
title: "create-skill + review-checklist: allowed-tools semantics and the frontmatter key-set rule"
type: chore
status: done
priority: 2
deps:
  - dev-flow-cross-skill-reference-conventio-05bb
created: 2026-09-19
updated: 2026-09-19
closed: 2026-09-19
---

From the 49be review (2026-09-19): (1) create-skill frontmatter-reference.md:49-52 says allowed-tools 'Restricts which tools the skill can use' / 'Be as restrictive as possible' and SKILL.md:38 'list only the tools the skill actually needs' — the docs (code.claude.com/docs/en/skills) say it only pre-approves the listed tools for the invoking turn and never restricts; omitted = nothing pre-approved. Rewrite accordingly. (2) librarian-mode review-checklist §2 (and agent-brief:59) require exactly name/description/disable-model-invocation/allowed-tools/argument-hint, while create-skill says all but name are optional and documents model, license, compatibility, metadata, context. Make them agree (house rule stated explicitly, or checklist accepts the documented optional fields). Lands after 05bb (same checklist) and before 07c3 F1 moves the checklist.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — doctrine (create-skill + checklist rule)

impl: DONE dd57773 (house rule: 5 required + model/context/license/compatibility/metadata allowed; allowed-tools = pre-approve only).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (key extractor misses underscore/caps/quoted keys; "no other key" unenforced), 2 (house rule silently excludes 10 documented fields incl disallowed-tools, when_to_use, effort, no reason); lows 3 ("exactly these five"), 4 (omitted = nothing pre-approved is inferred), 5 (pre-existing stale model/description-cap/SlashCommand facts). Librarian decision on 2: allow every field Claude Code documents; keep the 5 required.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE c7aacb5 (widened rule; hardened key check; doc facts fixed).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Lows carried to 07c3 F1.
- 2026-09-19 done: 46cc1be
