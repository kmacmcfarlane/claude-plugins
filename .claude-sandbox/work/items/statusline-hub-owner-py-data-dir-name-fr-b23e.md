---
id: statusline-hub-owner-py-data-dir-name-fr-b23e
title: "statusline-hub owner.py: data-dir name from the cache path skips the plugin-id rule"
type: bug
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
refs:
  - d8f6 implementer
---

Surfaced by d8f6's implementer 2026-09-21 (the moved form of 8588's first low): plugins/statusline-hub/hooks/owner.py:~122-124 builds statusline-hub-<mkt> from the cache path without re.sub(r'[^A-Za-z0-9_-]', '-', …) as installed_by_record does; a marketplace name with other characters picks the wrong data dir. Acceptance: one shared id rule; test with a marketplace name containing '.' or '@'.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
