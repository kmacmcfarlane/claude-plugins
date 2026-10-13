---
id: audit-claude-sandbox-on-origin-for-claud-abb8
title: audit .claude-sandbox/ on origin for Claude Code internals
short_display_name: audit published sandbox files
type: chore
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T19:32Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer claude-sandbox librarian, 2026-10-13 (its decision 95 a)
---

Peer request 2026-10-13: 489 files under .claude-sandbox/ are on origin/main of this public repo (485 under work/, plus an old HANDOFF.md). Audit them for Claude Code internals per CLAUDE.md § Claude Code source material (minified names, bundle offsets, quoted bundle code, leaked-source references), using cc_scan with the local deny-list and reading the hits; report file:line only, never echo a hit's text. Removal from the tree does not reach history: a rewrite stays the operator's one-way call (relates to 4151).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
dispatch: scout sonnet medium — read-only audit, file:line only
