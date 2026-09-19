---
id: chat-product-research-drop-the-allowed-t-49be
title: "chat:product-research: drop the allowed-tools restriction"
type: chore
status: doing
priority: 3
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:27Z
created: 2026-09-19
updated: 2026-09-19
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
