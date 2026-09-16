---
id: readme-catalog-missing-the-chat-plugin-a13d
title: README catalog missing the chat plugin
type: chore
status: done
priority: 3
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - librarian observation at Land of 99cb
---

Noticed at Land 2026-09-16: .claude-plugin/marketplace.json lists claude-kit, ai-scripts, chat; README.md's plugin tables list only claude-kit and ai-scripts. Doctrine: catalog is the front door. Acceptance: README gains a chat plugin section/row consistent with the others.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e

Scope decided by the librarian: README.md (a '### chat' section with its skill table, matching the other
plugins' shape) and CLAUDE.md's layout block (add plugins/chat). Read plugins/chat/skills/*/SKILL.md for the
description; do not edit the plugin itself.
dispatch: implementer opus — rule 2 (doctrine / catalog)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit 3829e3d; reviewer opus round 1 dispatched 2026-09-16 16:43:02
- 2026-09-16 done: 05ab4f3
- review CLEAR, 1 nit (CLAUDE.md lists the literal chat skill dir while siblings use a placeholder — per spec, accepted); landed merge 05ab4f3 2026-09-16 16:44:53
