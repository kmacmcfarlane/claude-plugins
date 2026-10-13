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
/loop has two modes: interval (a CronCreate cron) and dynamic (the model re-arms with ScheduleWakeup, delay 60–3600 s) (documented, with idle-only firing and the stop rules: https://code.claude.com/docs/en/scheduled-tasks). A tick runs as a new turn between the user's turns in the same session (documented: https://code.claude.com/docs/en/scheduled-tasks#how-scheduled-tasks-run); it re-runs a skill only when the loop's prompt names one (documented: https://code.claude.com/docs/en/scheduled-tasks#run-a-prompt-repeatedly-with-/loop); what Claude runs on a self-paced tick can be derived from Claude Code's internals. Ticks fire only while the REPL is idle, which for a librarian includes "idle while background agents work" (inferred from: a scheduled prompt fires between turns, not mid-response, https://code.claude.com/docs/en/scheduled-tasks#how-scheduled-tasks-run) — so an ungated tick would re-run the idle turn and double-dispatch. A no-op tick refreshes claims/<repo>.json, which removes the condition behind budget.md's 2h/4h freshness split. next_check is NOT redundant: quota_budget clamps it to 60–3600, the same range as delaySeconds, so F2 feeds one into the other; interval mode cannot read it. Loops end when the session exits (an OOM kill included) and when an iteration neither reschedules nor stops and its one fallback wakeup does not either (documented: https://code.claude.com/docs/en/scheduled-tasks#limitations, https://code.claude.com/docs/en/scheduled-tasks#stop-a-loop); whether /clear ends a loop can be derived from Claude Code's internals; loops probably also die at a HARD gate (the tick's prompt is not whitelisted in context_warn; a /loop iteration runs UserPromptSubmit hooks, documented: https://code.claude.com/docs/en/hooks#userpromptsubmit). Cloud routines are ruled out (fresh clone, no local state/MCP). Cost: a tick is a full billed turn, cache-warm; 2–3/h is noise beside a dispatch, and the loop makes *stop* mode enforceable for the first time.
Recommendation: (A) dynamic /loop as a fallback HEARTBEAT (agent returns stay the primary wake), delay from next_check, tick order in-flight check → budget → act. (B) interval /loop 30m as a documented fallback. (C) cloud routines ruled out, recorded. (D) an external ralph-shaped supervisor — separate spike, the only thing that survives session death.
F2 drops: the bespoke self-wake mechanism, its own wakeup prompt, the ≤1 h bound, and quiet mode's terminal-narration half. It keeps the policy: when to wake, at what delay, what a tick may do.
Open: Q1 does a dynamic loop survive compaction (not live-verified; the docs leave it open) — run a 15-min live test before F2 is written; Q2 assume a HARD gate erases a tick, so re-arm in the checkpoint sequence; Q3: use a skill rule, not an environment variable; Q5 interval mode is not the default.
decision 63: adopt the native loop for the librarian — (a) A: dynamic /loop as the fallback heartbeat, delay from next_check, every tick gated by an in-flight check; file items 1–6 and 8, and F2 drops its bespoke self-wake [recommended]; (b) A plus start the live compaction test (Q1) in this session now; (c) B: interval /loop 30m only; (d) not now — keep F2's own self-wake.
answer 63: (a) adopt dynamic /loop as the fallback heartbeat, gated by an in-flight check (operator 2026-09-22)
operator requirements with the answer: (1) automatic start is preferred — the librarian should arm the loop itself if it can, not hand the operator a command to run; establish whether an agent can start /loop (the docs list /loop as a bundled skill and say Claude invokes some bundled skills on its own: https://code.claude.com/docs/en/skills#bundled-skills; whether the model may start a loop the user did not ask for can be derived from Claude Code's internals) and record the answer. (2) The loop must BACK OFF when there is no work: SendMessage from other agents and the operator's own turns are the async wake path, and work almost never arrives from anywhere else, so an empty queue means long delays (escalating back-off toward the 3600 s cap), not frequent empty ticks. (operator 2026-09-22)
