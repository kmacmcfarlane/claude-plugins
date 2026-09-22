---
id: librarian-loop-use-claude-code-s-native-8ab6
title: "librarian loop: use Claude Code's native /loop (and CronCreate / ScheduleWakeup) to drive the librarian's idle turn"
type: spike
status: todo
priority: 2
parent: librarian-work-unblocked-items-and-pre-i-1222
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: 'perhaps we should be using the native claude code loop feature to help drive the librarian loop?' Investigate how /loop (dynamic and interval modes), ScheduleWakeup and cron routines relate to 1222's idle-turn design (F2 self-wake, quiet mode, stop), what each can and cannot do (does a loop tick survive compaction? does it re-enter the skill? how does it interact with background agents, peer messages and the context gate?), and what librarian-mode should adopt vs keep. Output: findings + a recommendation, factored items if adopted.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Spike result (opus, 2026-09-22) — series .claude-sandbox/investigations/8ab6-native-loop/ (00_findings.md, INDEX.md)
/loop has two modes: interval (a CronCreate cron) and dynamic (the model re-arms with ScheduleWakeup, delay 60–3600 s). A tick is a fresh user turn in the SAME session with the same context; it does not re-invoke the skill — the prompt is a sentinel meaning "run the loop instructions established earlier; else no-op". Ticks fire only while the REPL is idle, which for a librarian includes "idle while background agents work" — so an ungated tick would re-run the idle turn and double-dispatch. A no-op tick refreshes claims/<repo>.json, which removes the condition behind budget.md's 2h/4h freshness split. next_check is NOT redundant: quota_budget clamps it to 60–3600, the same range as delaySeconds, so F2 feeds one into the other; interval mode cannot read it. Loops die silently at /clear, session exit, OOM, three quiet ticks, and probably at a HARD gate (the sentinel is not whitelisted in context_warn). Cloud routines are ruled out (fresh clone, no local state/MCP). Cost: a tick is a full billed turn, cache-warm; 2–3/h is noise beside a dispatch, and the loop makes *stop* mode enforceable for the first time.
Recommendation: (A) dynamic /loop as a fallback HEARTBEAT (agent returns stay the primary wake), delay from next_check, tick order in-flight check → budget → act. (B) interval /loop 30m as a documented fallback. (C) cloud routines ruled out, recorded. (D) an external ralph-shaped supervisor — separate spike, the only thing that survives session death.
F2 drops: the bespoke self-wake mechanism, its own wakeup prompt, the ≤1 h bound, and quiet mode's terminal-narration half. It keeps the policy: when to wake, at what delay, what a tick may do.
Open: Q1 does a dynamic loop survive compaction (binary and docs conflict) — run a 15-min live test before F2 is written; Q2 assume a HARD gate erases a tick, so re-arm in the checkpoint sequence; Q3 use a skill rule, not CLAUDE_CODE_LOOP_PERSISTENT; Q5 interval mode is not the default.
decision 63: adopt the native loop for the librarian — (a) A: dynamic /loop as the fallback heartbeat, delay from next_check, every tick gated by an in-flight check; file items 1–6 and 8, and F2 drops its bespoke self-wake [recommended]; (b) A plus start the live compaction test (Q1) in this session now; (c) B: interval /loop 30m only; (d) not now — keep F2's own self-wake.
