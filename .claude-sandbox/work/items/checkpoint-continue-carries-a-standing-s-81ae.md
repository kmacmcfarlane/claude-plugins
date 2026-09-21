---
id: checkpoint-continue-carries-a-standing-s-81ae
title: checkpoint continue carries a standing session mode (opener re-invokes librarian-mode)
type: feature
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T22:44Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - "peer: claude-sandbox librarian (uds 246.sock)"
---

Peer claude-sandbox librarian 2026-09-21, relaying its operator: /context-guard:checkpoint continue in a librarian-mode session produced a Step 7 opener that never re-invoked /dev-flow:librarian-mode start, so 'continue' did not visibly mean staying in librarian mode. Asks: (1) handoff-format records the active standing mode/skill (e.g. frontmatter mode_skill: /dev-flow:librarian-mode, or a Standing mode line in Doing); (2) checkpoint Step 7 opener re-invokes that skill first; (3) librarian-mode references/ending-the-session.md tells the librarian to name itself as the opener's skill. Acceptance: all three, context-guard stays free of any hard knowledge of dev-flow (the key is generic: any skill), soft pointer only.

## Handoff
- doing: implementer dispatched (opus, agent aa86565569c32d63c)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —
- peer's own item: claude-sandbox store relay-checkpoint-continue-should-carry-a-1a58
- dispatch: implementer opus — two plugins (context-guard, dev-flow) + manifest format doctrine

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
