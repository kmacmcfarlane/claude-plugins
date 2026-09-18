---
id: statusline-split-f5-remove-compat-one-re-a95a
title: "statusline split F5: remove compat one release later"
type: chore
status: todo
priority: 3
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-18
---

3c48 plan §F5: delete context-guard's deprecated copy, old-path read and notice. Size S; opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- (F4 review lows) notice treats any statusline-* data dir as owning — check owner.json state/entry; notice misses marker-less project/local-scope entries; publish_gauge reads gauge.json with a blocking open (FIFO) — use read_json_file; future-at reject only on the sensor, not the legacy block; sensor-contract.md should state the regular-file and +60s rules; notice text add "then start a new session"; _touch_stamp docstring width. OPERATOR RISK at F5: if the operator has not been taken over by F3 when the deprecated copy is deleted, the gate drops silently to inferred depth — F5 must check/announce.

- (F3 review lows) tracked-and-ignored settings.local.json notice should say git rm --cached; blocked notice never re-speaks when the reason changes; git check fail-open on exit 128 (safe.directory); takeover of a predecessor in a tracked project settings.json has no git guard; --local manual install has no git-ignore check; README context-guard section still says run /install-statusline (now automatic).
