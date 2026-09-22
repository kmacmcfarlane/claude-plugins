---
id: statusline-hub-owner-py-data-dir-name-fr-b23e
title: "statusline-hub owner.py: data-dir name from the cache path skips the plugin-id rule"
type: bug
status: done
priority: 3
created: 2026-09-21
updated: 2026-09-22
closed: 2026-09-22
refs:
  - d8f6 implementer
---

Surfaced by d8f6's implementer 2026-09-21 (the moved form of 8588's first low): plugins/statusline-hub/hooks/owner.py:~122-124 builds statusline-hub-<mkt> from the cache path without re.sub(r'[^A-Za-z0-9_-]', '-', …) as installed_by_record does; a marketplace name with other characters picks the wrong data dir. Acceptance: one shared id rule; test with a marketplace name containing '.' or '@'.

## Handoff
- doing: implementer dispatched (opus, agent a4228a067f35ad1c1)
- next: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
- dispatch: implementer opus — hub owner code (settings ownership path)
- 2026-09-22 done: 29b641a

## Implementer result
- round 1 DONE 37fa55c (opus): owner.data_name(plugin_id) shared by the cache-path fallback and installed_by_record; 3 tests (fail 16 without); no other hub/statusline copy of the flaw.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 37fa55c
- rule verified in docs + binary; lows not taken: non-BMP (UTF-16) divergence; raw-name cache subtests.
- landed 29b641a
