---
id: context-guard-conversations-compact-whil-22b2
title: "context-guard: conversations compact while idle, without the operator driving it"
short_display_name: idle compaction without operator
type: bug
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T17:12Z
created: 2026-10-09
updated: 2026-10-09
refs:
  - operator, chat 2026-10-09
---

Operator, 2026-10-09: context-guard seems to compact conversations while idle, not driven by them; expected only when context gets really full, to pre-empt a naive compaction. Acceptance: say from evidence (gate state, ledger, transcripts) what started each idle compaction and at what fill; if context-guard caused or released one early, fix it so compaction waits for real depth or the operator.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: 2026-10-09 first look, observed from context-guard's gate state files (claude-kit/context-gate/*.json) and ledgers on Claude Code 2.1.292: every recorded compaction has a trigger from Claude Code's PreCompact hook input (auto or manual); context-guard never starts one, it can only defer. Recent auto attempts at low fill, each deferred (compact_deferred true): this session 2026-10-09 16:40:42 UTC at ~276K of 1M while idle on agents; 53cd 2026-10-09 08:07 at ~325K; 7794 2026-10-08 16:40 at ~590K; 2b9f 2026-10-08 08:44 at ~598K. Gaps to check: (1) once a checkpoint has run this epoch, precompact_gate allows any auto compaction at any depth; (2) the Stop relay then asks the model to checkpoint after a low-fill deferral, which unlocks the next attempt; (3) ledger epoch headers show compactions at 435,627 tok (7794, 2026-09-30) — whether those went through early.
dispatch: scout sonnet medium — evidence pass over every ledger epoch header and gate state: fill, trigger, checkpoint before it, operator turn before it
agent: scout ad2b806566bbfd486
note: 2026-10-09 ~17:15 UTC gap 2 observed live in this session: after the 16:40 deferral at ~28% fill, the Stop hook added context asking the model to run the checkpoint now and start no new work; not run, since a checkpoint here would release the next low-fill auto compaction against the operator's stated intent

## Notes
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
return: scout — 19 compactions in 14 days (13 manual, 6 auto); three autos below 85% (72.4%, 81.6%, 80.5%) went through at precompact_gate.py:46 on the checkpointed_this_epoch branch; twice the chain deferral → Stop relay → checkpoint → next idle attempt passes; idle auto attempts arrive 53.7–54.0 minutes after the last turn end (observed from transcripts, Claude Code 2.1.292); report at scratchpad/22b2-evidence.md
decided: 2026-10-09T17:25Z design — the operator's stated expectation settles it: a proactive auto compaction is deferred while remaining > due, whether or not a checkpoint ran; released only at or under due after a checkpoint, or under hard as now; the Stop relay asks for a checkpoint only at or under due, never on a low-fill deferral
target: no auto compaction passes above the due line (850K on 1M); the relay never fires above it; manual /compact untouched; tests for each path, including checkpointed-at-low-fill and the relay
dispatch: implementer opus medium — build (gate behaviour; not a canonical mechanical kind)
agent: implementer a5c4b28f7b81cabbd
return: DONE 2634f72; 12/12 Checks OK (context-guard 718); judgement: inferred depth still defers (the brief misstated the existing rule; kept, since making it allow would let idle compactions through without a status-line reading); compact_deferred set only at or under due; relay on mirrored depth, gate on pre-mirror, as before
dispatch: reviewer opus high — review round 1 of 2634f72
agent: reviewer a6936b3fdd42a185f
verdict: review round 1 NEEDS_CHANGES (must-fix 2: medium 1 — the new above-due hold after a checkpoint can block a recovery compaction (model switch leaves a 1M guess on a 200K model; a batch of reads overflows past the last measured fill) and only a manual /compact ends it; fix: hold above due after a checkpoint only when no user line follows the last usage line (idle); medium 2 — no test on inferred depth, which the idle case runs on; lows: mark_checkpoint docstring, playbook overstates (200K guess, lowered auto-compact window); nits: "at or under hard" wording, a lingering flag); judgement call 1 (inferred still defers) ruled right; call 2 sound
dispatch: implementer opus medium — fix round 1 (resume a5c4b28f7b81cabbd)
return: DONE f560065 (fix round 1); 12/12 Checks OK (context-guard 729); input_since_usage reads the tail backwards, 64 KiB chunks, 4 MiB cap, unreadable or capped counts as pending
dispatch: reviewer opus high — review round 2 of f560065 (resume a6936b3fdd42a185f)
verdict: review round 2 NEEDS_CHANGES (must-fix 1, down from 2: low, playbook caveat understates the no-sensor bands; code correct: probes P1-P5 as intended, real transcripts cut at their auto boundaries — the four idle ones read idle, the five busy ones pending; 3,000-transcript fuzz of the backward scan clean; lows/nits: mark_checkpoint docstring, a garbled caveat phrase, the not-full message omits the pending release, one long line)
decided: 2026-10-09T19:05Z cap — must-fix fell 2 → 1 and every leftover is exact wording: a finish round (authority answer 145)
dispatch: implementer opus medium — finish round (resume a5c4b28f7b81cabbd)
