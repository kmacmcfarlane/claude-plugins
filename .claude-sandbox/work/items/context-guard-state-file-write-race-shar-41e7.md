---
id: context-guard-state-file-write-race-shar-41e7
title: "context-guard state file: write race, shared temp name, unsanitised session_id path"
type: bug
status: done
priority: 2
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
---

From the 81a5 review (2026-09-18), pre-existing on main: (1) every writer does an unlocked load-modify-save of the whole <sid>.json, so statusline can write back a stale epoch/checkpoint_epoch after reset_epoch/mark_checkpoint (undoing a compaction epoch or checkpoint stand-down); (2) all writers share the temp name <sid>.json.tmp (lib_context.py:59) — concurrent writers can interleave and os.replace installs corrupt JSON -> load_state returns {} and every field is lost; (3) state_path joins session_id unsanitised (sid ../../evil wrote outside the dir; verified); (4) install-statusline SKILL.md:68 documents a non-atomic manual write. Acceptance: unique temp names (mkstemp in the same dir), sid validated (uuid-ish charset) or hashed, and a merge-on-save or per-key lock (fcntl, bounded) so writers never clobber each other's keys; tests with concurrent writers. Hook code that gates -> routing per model-routing (non-trivial gating/state -> fable, or opus fallback).

## Handoff
- doing: dispatched in worktree
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer fable — rule 3: non-trivial change to gating hook state (lib_context state writes feed the HARD gate); fallback per § Fallback if unavailable

impl round 0 (fable): FAILED — HTTP 429 out of usage credits (req_011CfBUwewqQYmA4HNnLQHCJ); worktree clean, nothing committed; reset unknown (no rate_limits in this session state: the session runs the pre-81a5 cached status line).
dispatch: implementer opus — fable unavailable (unknown); fallback

impl (opus fallback): DONE_WITH_CONCERNS d5c472f (update_state + flock 0.2s fail-open; own O_EXCL temp instead of tempfile for 5ms; safe_sid hash; decide() refactor in context_warn; 202 tests).
dispatch: reviewer opus — fable unavailable (unknown); fallback (rule 4 floor opus)

review round 1 (opus, fable fallback): CLEAR. Gate equivalence: 32/33 byte-identical vs main; the 33rd (state file holding a JSON list) crashed on main and now gates correctly. Lows to follow-up.
- 2026-09-18 done: 28fb60b
