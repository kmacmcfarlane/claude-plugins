---
id: chat-product-research-drop-the-allowed-t-49be
title: "chat:product-research: drop the allowed-tools restriction"
type: chore
status: dropped
priority: 3
created: 2026-09-19
updated: 2026-09-19
closed: 2026-09-19
refs:
  - operator decision 11
---

Operator decision 11 (2026-09-19): let product-research use all tools. Acceptance: remove the allowed-tools frontmatter key (or leave it unrestricted per create-skill rules — check what omitting means) in plugins/chat/skills/product-research/SKILL.md; skill lint clean.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer sonnet — default

impl: DONE 6128212 (key removed; allowed-tools only pre-approves, never restricts — docs quote).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES/high — allowed-tools only pre-approves listed tools for the invoking turn (docs: "does not restrict which tools are available… When omitted… no tools are pre-approved"). Removing it grants nothing and adds prompts on WebSearch/WebFetch, the opposite of decision 11; also fails the checklist key-set lint. Librarian: the operator intent (use all tools) is ALREADY met on main — every tool is callable. Branch dropped unmerged (6128212 discarded); no change to the skill.
- 2026-09-19 dropped
