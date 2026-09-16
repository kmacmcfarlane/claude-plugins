---
id: gitignore-config-37d3
title: Circle back on .gitignore un-ignore of config.yaml and stale work README
type: chore
status: todo
priority: 4
created: 2026-09-04
updated: 2026-09-04
---

Working tree has an uncommitted .gitignore change adding '!.claude-sandbox/config.yaml', which would un-ignore a file carrying a private mount path (see the comment at .gitignore:8-9). Operator (2026-09-04) unsure whether intentional; circle back before any commit sweeps the tree. Also: .claude-sandbox/work/README.md still points at the retired claude-kit plugin.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
