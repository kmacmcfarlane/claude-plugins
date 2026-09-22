---
id: work-items-a-front-matter-summary-line-a-8e14
title: "work items: a front-matter summary line agents read instead of the body"
type: feature
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22 (with answer 59): long item bodies (e.g. 426a's six review rounds) cost a full read; adopt the skills pattern — a short summary: field in front matter, printed by wi prime / ls / show --brief / next, so an agent triages from the summary and reads the body only when working the item. Acceptance: format.md defines summary: (one line, ≤ ~200 chars; falls back to title); wi add --summary; wi set summary; lint warns when a body exceeds N lines with no summary; tests. Note: front matter is not cheaper to hold by itself — the saving comes from the CLI printing the summary instead of the body.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
