---
id: operator-turn-log-a-userpromptsubmit-hoo-3e8e
title: "operator turn log: a UserPromptSubmit hook appends ids and timestamps of each operator turn to a host-shared file"
short_display_name: operator turn log hook
type: feature
status: todo
priority: 2
created: 2026-10-03
updated: 2026-10-03
refs:
  - peer operator-attention 2026-10-03 (their serial 09, R47)
---

peer operator-attention 2026-10-03, relaying the operator's answers to our 0c4d delta 01 (their commit c598050; serial .claude-sandbox/investigations/decision-collector/09_operator-answers-10-03.md in their repo; spec R47, new R49). Relayed operator answers — re-confirmed with the operator before any build acts on them. (3) Operator turn timing, proposed to dissolve (the operator's idea, relayed): a UserPromptSubmit hook fires exactly when the operator takes a turn, in every session (hooks run from the shared config dir), and appends {ts, session_id, cwd/repo, estate} — ids and timestamps only, no content — to a host-shared file. Readers: the agents ledger, operator-attention's scheduler, claude-analytics; 'seen N' becomes computable as a turn in the raising session after shown N with none elsewhere between. Caveats: installed per config tree (a tree exporting its own config dir writes a second file, readers merge); no content. Precedent: statusline-hub's per-session sensor record. A live service is allowed but not needed. Placement is ours: README rule 1 puts hooks only in a plugin whose aim is that behaviour — context-guard already hooks UserPromptSubmit (the context gate); operator-interaction is knowledge-only today; or a small dedicated plugin. That placement is an operator decision when planned. Acceptance (draft): one hook, append-only, ids/timestamps only, safe under concurrent sessions, a documented file path and record shape, tests, a reader note in the decisions skill for computing seen N.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
