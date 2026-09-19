---
id: status-line-its-own-independently-instal-3c48
title: "status line: its own independently installable plugin"
type: feature
status: done
priority: 1
parent: spike-should-the-status-line-be-its-own-fb55
created: 2026-09-18
updated: 2026-09-19
closed: 2026-09-19
refs:
  - operator message 2026-09-18
---

Operator 2026-09-18: split the status line out of context-guard into its own plugin, shareable with coworkers and installable without any other kmacmcfarlane plugin. Coupling today: statusline.py imports lib_context (thresholds, update_state, load_state, _base_dir); it writes exact depth + rate_limits into context-guard's state file (claude-kit/context-gate/<sid>.json), read by context-guard's gate and librarian-mode's fable fallback; context-guard's rehydrate.py restores/migrates the statusLine setting; install-statusline skill lives in context-guard. Acceptance: new plugin (name: statusline, unless the operator objects) with statusline.py, a vendored minimal state helper (atomic, locked write), the install-statusline skill, and its own SessionStart self-heal for the statusLine setting; works standalone (default gauge thresholds; reads context-guard's published thresholds when present — decision 17 -> publish); keeps writing the same sensor record so context-guard and librarian-mode keep working (data contract, documented, soft in both directions); context-guard stops owning statusLine and hands existing installs over without clobbering; marketplace.json, README catalog, CLAUDE.md layout/placement in the same commit; coworker-facing install instructions in the skill. Lands after the 3685+fe33 bundle (same files). Design plan first (opus) -> librarian review -> implement.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Plan (2026-09-18; .claude-sandbox/investigations/3c48-statusline-plugin/plan.md) — adopted by the librarian (operator: "get as much as you can done yourself")
- Name `statusline` (told the operator; no objection). Neutral sensor path ~/.claude/statusline/sensor/<sid>.json (v1), no lock (single writer) — deliberate deviation from this item's "same record, locked write" acceptance: nothing claude-kit-branded leaks to coworkers; context-guard reads both paths for one release. context-guard publishes claude-kit/context-gate/gauge.json (v1 anchors/labels); statusline's context-guard mode needs gauge.json v1 AND this session's state file. First-session self-install into the enabled scope, never over a foreign entry. Only-context-guard installs keep a deprecated copy one release with a notice, no settings writes. Findings: `claude plugin uninstall` deletes the data dir unless --keep-data (remove the setting first); the operator's live statusLine points into claude-kit-kmacmcfarlane/ with no marker -> takeover recognises legacy by command path.
- Risk: stale worktree-context-guard-turn-gate (8cc2, Sep 4) changes the lib_context API — conflicts with F1 if revived.
Features: F1 context-guard side of the contract (ANCHORS, dual-path read, epoch-start demotion, gauge.json) — M, fable (HARD gate) / opus fallback; F2 statusline plugin + catalog same commit — L, opus; F3 statusline SessionStart self-heal/takeover/first install/prune — M, opus; F4 context-guard handover + dev-flow model-routing Fallback path — M, opus (F3, F4 parallel after F2); F5 one release later: delete compat — S, opus.

## Notes
- 2026-09-19 done: split landed: F1 69d3283, F2 1d8dc1b, F3 29cc134, F4 ad71f30, docs a618a04; F5 (a95a) follows one release later
