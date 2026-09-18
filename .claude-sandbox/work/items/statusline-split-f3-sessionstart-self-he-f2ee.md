---
id: statusline-split-f3-sessionstart-self-he-f2ee
title: "statusline split F3: SessionStart self-heal, takeover, first-run install, prune"
type: feature
status: done
priority: 1
deps:
  - statusline-split-f2-the-statusline-plugi-a67f
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
---

3c48 plan §F3. Size M; opus (settings writes).

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — settings writes / hook code (rule 2); fable not needed: not a gate

impl: DONE be6d73d (session_start.py; --replace / --write-read-only split; splice write; prune; 198 tests). Out-of-scope notes: CLAUDE.md:35 layout line should name session_start; README context-guard section still says run /install-statusline.
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (yield/defer message says /install-statusline --replace but the skill refuses it), 2 (read-only/malformed settings fail silently every session), 3 (splice fallback overwrites concurrent multi-key changes — lost update reproduced), 4 (hook creates .claude/settings.local.json without ensuring it is git-ignored); lows 5 (CRLF -> LF), 6 (non-ASCII home escaped in command), 7 (CLAUDE.md:35), nit 8. Coworker first run and operator takeover both clean; 3000-object splice fuzz no loss.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 32ac49b (all 8; blocked state; fresh re-read write; git-ignore guard; CRLF; UTF-8 command; 213 tests).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Lows -> F5.
- 2026-09-18 done: 29cc134
