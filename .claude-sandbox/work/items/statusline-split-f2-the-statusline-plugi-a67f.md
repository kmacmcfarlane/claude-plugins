---
id: statusline-split-f2-the-statusline-plugi-a67f
title: "statusline split F2: the statusline plugin (+ catalog in the same commit)"
type: feature
status: done
priority: 1
deps:
  - statusline-split-f1-context-guard-side-o-7576
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
---

3c48 plan §F2: plugins/statusline (statusline.py, sensor.py, owner.py, installer skill, contract doc, tests incl. test_contract.py); delete context-guard's installer; marketplace.json, README catalog/prose, CLAUDE.md layout + aim->home in the same commit. Size L; opus.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — marketplace shape + executable logic (rule 2); no gating code in this feature

impl: DONE_WITH_CONCERNS 47bcaa3 (152 tests; standalone leak test; --force for foreign install; timing 13.4ms).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (two tests assume no data dir; fail from an installed-path copy), 2 (moved playbook section claims CLAUDE_PLUGIN_ROOT is set in Bash; false; escape hatch fails); lows 3 (settings re-serialised: byte diff), 4 (0444 settings silently replaced), 5 (rm -rf ~/.claude/statusline ignores CLAUDE_CONFIG_DIR), 6 (repo-map — pulled into this round), 7 (model-routing old rate_limits path — F4). Coworker simulation passed end to end.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 419ce75 (1-6 + notes; declined 7 = F4). Note: CLAUDE_PLUGIN_ROOT substitution in skill content was verified by the round-1 reviewer from the plugins reference.
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Declined 7 (F4). Lows -> F3.
- 2026-09-18 done: 1d8dc1b
