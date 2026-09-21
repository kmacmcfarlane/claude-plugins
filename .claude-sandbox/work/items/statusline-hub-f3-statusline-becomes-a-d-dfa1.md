---
id: statusline-hub-f3-statusline-becomes-a-d-dfa1
title: "statusline-hub F3: statusline becomes a display hook (hard dependency on the hub)"
type: feature
status: doing
priority: 2
deps:
  - statusline-hub-f2-owner-mode-hooks-d-reg-b28f
parent: spike-status-line-multiplexer-dependency-d193
owner: unknown@360f41058e92
claimed: 2026-09-21T19:50Z
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F3. statusline declares statusline-hub in plugin.json dependencies (principle 4 as amended by 5343: statusline has no function without the hub), catalog (hard); stops writing settings; the hub owns the sensor write. context-guard/analytics/dev-flow stay soft readers.

## Handoff
- doing: review r2 dispatched (opus, reviewer resumed)
- next: CLEAR → land (expect a rehydrate.py conflict with 81ae)
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

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic + settings ownership + a hard plugin dependency (doctrine); fable signal (settings/ownership handover): fable unavailable (unknown); fallback

## Implementer result (held: operator hold 810f)
- round 1 DONE_WITH_CONCERNS 7f3d125 (opus, fable-signal fallback): statusline writes hooks.d/statusline.json (display, --segment) each session and no longer writes settings; statusline owner.py + installer DELETED (07 § F3), hub owner.py is the only copy; statusline declares statusline-hub (hard) — catalog/§5 show 1 declared; hub takes over older context-guard/claude-kit footer entries; honours a statusline removed marker; refusal notice for directory-level refusals; test_handover covers every scenario. Suites: statusline 151, hub 142, all green.
- open: fresh-machine race (footer at session 3); disabled footer lingers ≤14 days; context-guard rehydrate.py statusline_notice counts the hub's data dir as statusline; context-guard statusline.py:52 still names /install-statusline; framework auto-install of the hard dep unverified on 2.1.277 (#88663).
- next (after the hold lifts): reviewer opus (fable-signal fallback) — settings handover + a hard dependency.
- dispatch: reviewer opus — rule 4; fable signal (settings/ownership handover): fable unavailable, fallback (post-checkpoint #4)

## Review round 1 — NEEDS_CHANGES (opus) at 7f3d125
- [high] #88663 reproduced on 2.1.278: `plugin update statusline` does not pull the hub → footer lost once a stale entry drops; no notice. Fix: statusline SessionStart detects no statusline-hub@ install record and says once (stamped) to re-run `/plugin install statusline@kmacmcfarlane`; test + README/SKILL note.
- [medium] hub heal treats kind `statusline` as foreign → permanent `yielded` after a stale write-back; repoint when statusline_hooked().
- [medium] context-guard + dev-flow descriptions (plugin.json + marketplace) still say soft dep statusline; catalog says statusline-hub.
- [medium] context-guard rehydrate.py:403-440 stale comment; `statusline-` prefix matches `statusline-hub-*`.
- [medium] context-guard statusline.py:51-52 docstring credits statusline's SessionStart.
- [medium] kit-dev update-kit repo-map.md:93-95 stale (owner, installer; hub missing).
- [medium] checkpoint design-rationale.md:129 stale owner.
- lows: fresh-machine race (skip wait when installed statusline has no hooks/owner.py); 14-day linger (documented); README team enabledPlugins snippet list both; refusal fallback text fragile.
- verified live: fresh `plugin install statusline@` brings the hub (+1 dependency).
- dispatch: implementer opus — fix round 1 (fresh agent; round-1 implementer lost at compaction; tier kept, fable-signal fallback)
- fix round 1 DONE bbe5ea4 (opus): hub-missing notice (3 signals absent → say once, stamped); heal repoints a stale statusline entry when hooked, else waits; context-guard rehydrate prefix fix + test; descriptions/credits updated; repo-map mirrors layout; README #88663 note + team snippet both plugins; race low + refusal text fixed. Declined low: 14-day linger (documented).
- dispatch: reviewer opus — review r2 (same reviewer resumed)
