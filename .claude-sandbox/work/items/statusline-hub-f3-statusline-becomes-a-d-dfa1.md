---
id: statusline-hub-f3-statusline-becomes-a-d-dfa1
title: "statusline-hub F3: statusline becomes a display hook (hard dependency on the hub)"
type: feature
status: todo
priority: 2
deps:
  - statusline-hub-f2-owner-mode-hooks-d-reg-b28f
parent: spike-status-line-multiplexer-dependency-d193
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F3. statusline declares statusline-hub in plugin.json dependencies (principle 4 as amended by 5343: statusline has no function without the hub), catalog (hard); stops writing settings; the hub owns the sensor write. context-guard/analytics/dev-flow stay soft readers.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Carried from F1
- README consumer rows: context-guard and dev-flow notes name statusline-hub (soft) as a sensor source; context-guard/hooks/statusline.py:5 tells users to install statusline for a sensor record — mention the hub.
- statusline sensor.py docstring already names both writers (F1).

## Carried from F2
- statusline owner.data_dir scan fallback picks statusline-hub-* (sorts first) — fix; statusline heal recognises the hub command and stands down quietly; statusline writes hooks.d/statusline.json as a display hook (enables the hub takeover); display hook still running when CC cancels a render is not killed — document in the contract.

## Carried from F2 review (lows)
- statusline owner.py scan: exclude names starting "statusline-hub-" outright (not only when current-hooks lacks statusline.py); resync the hub vendored copy.
- registry in_git_tree: a custom CLAUDE_CONFIG_DIR inside a git-tracked dir under $HOME refuses all hooks quietly — surface the reason once (SessionStart message) rather than only in --status.
