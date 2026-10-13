---
id: handoff-h7-spike-stale-depth-warning-rig-bace
title: "handoff H7: spike — stale depth warning right after compaction"
type: spike
status: done
priority: 2
parent: context-guard-compact-and-clear-handoffs-5039
created: 2026-09-22
updated: 2026-09-28
closed: 2026-09-28
---

Two observed cases; cause unconfirmed (.claude-sandbox/investigations/5039-handoff-failures/00_findings.md). Find the cause; any fix to prompt-blocking gate code routes fable. Opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
librarian decision: the item's 'fix routes fable' predates c0d6 routing (fable only by pin); planned with opus, any fix built by opus with a fresh opus reviewer
dispatch: planner opus — spike, plan mode (Step 1)
agent: planner a9d8035671945cec8 round 1
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/bace-stale-depth-warning/ (cause: transcript flush lag after PostCompact; fix: drop transcript counts stamped at/before epoch_at in lib_context.measure; OQ1 sensor 2s grace, OQ2 upstream flush — neither blocking)
baseline: e63ed6146611d807ee18a82042b378435207557f4f8b9ab90bca690885936572  .claude-sandbox/investigations/bace-stale-depth-warning/00_initial.md 
dispatch: reviewer opus — fresh, plan review (rule 4)
agent: reviewer abf5b8ff982a87ffe round 1
verdict: NEEDS_CHANGES round 1 at 00 e63ed614 (2 medium, 5 low; cause, cases and replay reproduced; its claims about Claude Code's internals were not observed and are not recorded here; band latch fixed by the same change)
findings:
  [medium] 00:291-294 — precompact_gate claim reversed: 0 is falsy so never proactive; the compaction is allowed, never deferred
  [medium] 00:268-270,305-312 — no test for the observed S2 path: scan resumed from the persisted cache with no usage line after the offset; cur_at must be saved in _SCAN_KEYS / snap / _cache_start; plus malformed cur_at → None, no rescan
  [low] HARD end-to-end case belongs in test_window_mirror.py (resolved derived source, ~:729), assert exit 0 where today exits 2
  [low] 00:81-86 — replace the dequeue-offset claim with the UserPromptSubmit output offsets (stale 106-123 ms, clean 147-253 ms)
  [low] reader list omits stop_relay.py:35; note turn_gate.depth_now and _epoch_end_tokens read st["tokens"]
  [low] the stale note is never shown (decide() returns None at 0); diagnostic only, or drop from acceptance
  [low] OQ2 lacks a decide-later option
dispatch: planner opus — resume, fix round 1 (serial 01)
agent: planner a9d8035671945cec8 round 2
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/bace-stale-depth-warning/ 01_review-round-1.md (all 7 fixed)
baseline: e63ed6146611d807ee18a82042b378435207557f4f8b9ab90bca690885936572  .claude-sandbox/investigations/bace-stale-depth-warning/00_initial.md fee5d76b924a9de4c85c74938fb7db9a65e950f81eded3ac1884e38574b4ab70  .claude-sandbox/investigations/bace-stale-depth-warning/01_review-round-1.md 
dispatch: reviewer opus — resume, round 2
agent: reviewer abf5b8ff982a87ffe round 2
verdict: CLEAR round 2 at 01 fee5d76b (1 low: 01:74-75 the reviewer's own +147/+228/+253 ms are attachment times, upper bounds only — carried to the build brief as a correction; cause, fix and tests unchanged)
librarian decision: OQ1 (2 s sensor grace, EPOCH_GRACE_S) included in the fix, per the planner's recommendation — one line plus a test in the same file, closes a predicted path; OQ2 (ask upstream to flush) no — the fix holds whatever the flush timing
- 2026-09-28 done: /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/bace-stale-depth-warning/ (00+01, CLEAR r2); fix filed
