---
id: context-guard-conversations-compact-whil-22b2
title: "context-guard: conversations compact while idle, without the operator driving it"
short_display_name: idle compaction without operator
type: bug
status: todo
priority: 1
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
