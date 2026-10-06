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
note: peer agents 2026-10-03 — the operator confirmed first-hand in the agents session (their answer 24) that the four relayed operator-attention answers stand (first/last shown, who writes shown, the turn log via our 3e8e, R49 streams); they are requirements on agents' 76bc; agents' spike d131 reads our 0999, 3e8e, 40f0 and 8c42 read-only; a peer report, not an approval here — decisions 150 and 151 stay open for the operator's word in this session
decision 151: Confirm the relayed proposal for an operator turn log: a hook writing only ids and timestamps of your turns to a shared file? — options: (a) confirm: plan it when there's room [recommended] | (b) confirm and plan it now | (c) don't build it | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T01:40Z — backfilled: the card was shown in the conversation but never stored; (b)'s quota note refreshed (5% weekly used now)
  what: the operator turn log hook (3e8e): every turn you take appends {time, session id, repo}, no content, to one host-shared file that other tools read
  why now: it is not scheduled; it is planned when you say; blocks: nothing
  why ask: trust — a hook that runs on every turn in every session, recording when you are active, is yours to approve, even with no content in it
  context: the idea came from you in operator-attention's session, relayed here · you confirm it before it is planned — then: none
  stakes: reversible, narrow — a hook in every session; no content recorded
  (a) confirm: plan it when there's room — where it lives comes back to you as a placement question in the plan
  (b) confirm and plan it now — a plan costs roughly $20-30; the week is at 5%
  (c) don't build it — the item is dropped
  (z) decide later — the item waits
  rec: (a) · basis partial — it removes transcript scraping for every reader of operator turn times; nothing waits on it yet
  unknown: whether a config tree that exports its own config dir is used much
