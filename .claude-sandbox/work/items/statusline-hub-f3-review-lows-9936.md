---
id: statusline-hub-f3-review-lows-9936
title: statusline-hub F3 review lows
type: bug
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T23:07Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - dfa1 reviewer
---

From dfa1 review r2 2026-09-21 (CLEAR with lows). (1) hub session_start.py:320-326 fresh machine where the hub runs first: use the footer wording when _statusline_installs_only_hooks(); (2) session_start.py:182-184 heal waits silently forever on a footer entry after statusline was uninstalled — wait only while a statusline@ install record exists, else yield with the message; (3) README team enabledPlugins snippet: list statusline-hub@ beside statusline@ (auto-install from enabledPlugins unverified).

## Handoff
- doing: implementer dispatched (opus, agent ad4c93ef652d4ecc3)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — hub session_start owns the statusLine slot (fable signal: settings ownership; fable unavailable, fallback)

## Implementer result
- round 1 DONE 64c6513 (opus): footer wording when hub runs first; heal yields a footer entry when records readable and no statusline@; waits otherwise; tests fail 2 without. README already lists both (bbe5ea4). Open: repoint after uninstall while the 14-day manifest lingers.
- dispatch: reviewer opus — rule 4 (fable-signal fallback)

## Review round 1 — NEEDS_CHANGES (opus) at 64c6513
- [medium] session_start.py:256-258,190 permanent yield keyed on parsed install list: a non-list statusline@ value (v1 shape), plugins {} or no statusline-hub@ record (--plugin-dir) → yields wrongly. Fix: yield only when plugins is a dict holding statusline-hub@ and no statusline@ key at all; None otherwise; test v1-shaped value → Wait.
- lows: _statusline_installs_only_hooks ignores enabled state; yield message could say the leftover entry belongs to the removed statusline plugin. Deferral judged legit: repoint while a ≤14-day manifest lingers.
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE 815efbc (opus): yield only when plugins is a dict with statusline-hub@ and no statusline@ key (any shape); five wait tests; lows a,b fixed; fail 6 without.
- dispatch: reviewer opus — review r2 (same reviewer resumed)
