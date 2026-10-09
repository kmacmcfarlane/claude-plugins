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

## Carried notes

- (F4 review lows) notice treats any statusline-* data dir as owning — check owner.json state/entry; notice misses marker-less project/local-scope entries; publish_gauge reads gauge.json with a blocking open (FIFO) — use read_json_file; future-at reject only on the sensor, not the legacy block; sensor-contract.md should state the regular-file and +60s rules; notice text add "then start a new session"; _touch_stamp docstring width. OPERATOR RISK at F5: if the operator has not been taken over by F3 when the deprecated copy is deleted, the gate drops silently to inferred depth — F5 must check/announce.

- (F3 review lows) tracked-and-ignored settings.local.json notice should say git rm --cached; blocked notice never re-speaks when the reason changes; git check fail-open on exit 128 (safe.directory); takeover of a predecessor in a tracked project settings.json has no git guard; --local manual install has no git-ignore check; README context-guard section still says run /install-statusline (now automatic).
note: 2026-10-08 from the 7dd3 review 2: with context-guard recorded but disabled, its link stays on an orphaned version folder that is pruned after 14 days; from then the link dangles and the hub waits silently. Decide at this removal whether a recorded-but-disabled plugin counts as absent.
decision 209: Remove context-guard's deprecated status-line copy now? It was kept "one release later" (3c48 plan F5, 2026-09-18); this repo has no version numbers, many updates have shipped since, and the hub's heal repoints a stale footer entry — options: (a) remove it now, with its old-path read and notice, then retire the old reset-time source (fbc3) [recommended] | (b) keep it one more stated update, announced in the notice first | (z) decide later
  why ask: reach — anyone still pointed at the old path without the hub loses their status line at the update; the trigger "one release later" has no release to count by
  impact: (a) → old-path status lines stop at the next update, fbc3 unblocks; (b) → nothing changes now, fbc3 waits; (z) → fbc3 stays blocked
