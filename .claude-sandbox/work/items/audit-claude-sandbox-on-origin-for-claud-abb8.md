---
id: audit-claude-sandbox-on-origin-for-claud-abb8
title: audit .claude-sandbox/ on origin for Claude Code internals
short_display_name: audit published sandbox files
type: chore
status: done
priority: 1
created: 2026-10-13
updated: 2026-10-13
closed: 2026-10-13
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
agent: scout a4cf46edd16645513
return: audit at .claude-sandbox/investigations/audit-abb8-report.md (local, not tracked) — current tree on origin/main: 0 internal, 12 unsure lines in d63e, 8ab6, e347 (filed as rewrite-the-12-unsure-claude-code-lines-50c2); history: 14 internal lines in 13 commits (deny-list hits, a minified name, 'the binary' as provenance), all removed from the tree by e7029c03 on 2026-10-07; removing them needs a history rewrite — the operator's one-way call, 4151
- 2026-10-13 done
