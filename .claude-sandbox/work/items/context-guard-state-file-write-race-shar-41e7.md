---
id: context-guard-state-file-write-race-shar-41e7
title: "context-guard state file: write race, shared temp name, unsanitised session_id path"
type: bug
status: todo
priority: 2
created: 2026-09-18
updated: 2026-09-18
---

From the 81a5 review (2026-09-18), pre-existing on main: (1) every writer does an unlocked load-modify-save of the whole <sid>.json, so statusline can write back a stale epoch/checkpoint_epoch after reset_epoch/mark_checkpoint (undoing a compaction epoch or checkpoint stand-down); (2) all writers share the temp name <sid>.json.tmp (lib_context.py:59) — concurrent writers can interleave and os.replace installs corrupt JSON -> load_state returns {} and every field is lost; (3) state_path joins session_id unsanitised (sid ../../evil wrote outside the dir; verified); (4) install-statusline SKILL.md:68 documents a non-atomic manual write. Acceptance: unique temp names (mkstemp in the same dir), sid validated (uuid-ish charset) or hashed, and a merge-on-save or per-key lock (fcntl, bounded) so writers never clobber each other's keys; tests with concurrent writers. Hook code that gates -> routing per model-routing (non-trivial gating/state -> fable, or opus fallback).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- held until 81a5 lands (statusline.py) ; lands before d63e (both edit lib_context state handling).

- 2026-09-18 (81a5 review, low): statusline.py:358-361 — a context_window_size in (0,1) passes the <=0 check then int() truncates to 0 (display shows HARD gate; no exact write). Check size < 1 or after int().
