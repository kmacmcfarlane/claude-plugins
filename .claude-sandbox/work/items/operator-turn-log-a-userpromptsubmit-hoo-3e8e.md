---
id: operator-turn-log-a-userpromptsubmit-hoo-3e8e
title: "operator turn log: a UserPromptSubmit hook appends ids and timestamps of each operator turn to a host-shared file"
short_display_name: operator turn log hook
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T03:35Z
created: 2026-10-03
updated: 2026-10-08
refs:
  - peer operator-attention 2026-10-03 (their serial 09, R47)
---

peer operator-attention 2026-10-03, relaying the operator's answers to our 0c4d delta 01 (their commit c598050; serial .claude-sandbox/investigations/decision-collector/09_operator-answers-10-03.md in their repo; spec R47, new R49). Relayed operator answers — re-confirmed with the operator before any build acts on them. (3) Operator turn timing, proposed to dissolve (the operator's idea, relayed): a UserPromptSubmit hook fires exactly when the operator takes a turn, in every session (hooks run from the shared config dir), and appends {ts, session_id, cwd/repo, estate} — ids and timestamps only, no content — to a host-shared file. Readers: the agents ledger, operator-attention's scheduler, claude-analytics; 'seen N' becomes computable as a turn in the raising session after shown N with none elsewhere between. Caveats: installed per config tree (a tree exporting its own config dir writes a second file, readers merge); no content. Precedent: statusline-hub's per-session sensor record. A live service is allowed but not needed. Placement is ours: README rule 1 puts hooks only in a plugin whose aim is that behaviour — context-guard already hooks UserPromptSubmit (the context gate); operator-interaction is knowledge-only today; or a small dedicated plugin. That placement is an operator decision when planned. Acceptance (draft): one hook, append-only, ids/timestamps only, safe under concurrent sessions, a documented file path and record shape, tests, a reader note in the decisions skill for computing seen N.

## Handoff
- doing: —
- next: answer 151 b: dispatch the plan now (placement comes back as a decision)
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
decision 151: Confirm the relayed proposal for an operator turn log: a hook writing only ids and timestamps of your turns to a shared file? — options: (a) confirm: plan it when there's room [recommended] | (b) confirm and plan it now | (c) don't build it | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: the operator turn log hook (3e8e): every turn you take appends {time, session id, repo}, no content, to one host-shared file that other tools read
  why now: it is not scheduled; it is planned when you say; blocks: nothing
  why ask: trust — a hook that runs on every turn in every session, recording when you are active, is yours to approve, even with no content in it
  context: the idea came from you in operator-attention's session, relayed here · you confirm it before it is planned — then: none
  impact: → a hook may log the time, session and repo (no content) of each of your turns to one shared file, planned when there's room · later: other tools keep scraping transcripts for turn times · reach: every session on this host · undo: remove the hook
  stakes: reversible, narrow — a hook in every session; no content recorded
  (a) confirm: plan it when there's room — where it lives comes back to you as a placement question in the plan
  (b) confirm and plan it now — a plan costs roughly $20-30; the week is at 5%
  (c) don't build it — the item is dropped
  (z) decide later — the item waits
  rec: (a) · basis partial — it removes transcript scraping for every reader of operator turn times; nothing waits on it yet
  unknown: whether a config tree that exports its own config dir is used much
answer 151: b — "5% on wednesday is not very far into the quota, why is this a concern? Also, I'm getting a lot of budget decisions coming in, we should bump up the budget to really only flag big spends (based on real data)." (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:47:39.192Z; read as: (b) confirm and plan it now; the quota note was stale caution, not a concern; plus a new request filed: raise budgets from real data)
dispatch: planner opus high — plan, answer 151 b
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e
agent: planner a47a01aeb320c74e5

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
return: DONE_WITH_CONCERNS series 00_initial.md (open: placement blocking, rec new turn-log plugin; retention 13 months; seen rule via 0999; probe P1 on undocumented transcript fields gates the origin step)
dispatch: reviewer opus high — plan review 1
baseline: plan review 1 — c50324f2a9b946435eac4f737b22252576eb947f14e83e1d05e802fa4fb4ce36 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/00_initial.md; 
agent: reviewer a5f686d69e11c3812
verdict: plan review 1 NEEDS_CHANGES (must-fix 5: 00_initial.md is a misfiled 0999 draft, scratchpad collision; INDEX wrong; documented transcript lag; "no transcript reading" hidden as assumption; seen defined twice vs 0999; lows 6-8). Recovered draft: scratchpad/3e8e-review/00_reconstructed.md
correction: my parallel planner briefs gave both planners the same session scratchpad with no per-agent subdirectory; both drafted scratchpad/00_initial.md and the 3e8e serial got 0999's draft. Every brief now names a per-item scratch subdirectory.
dispatch: planner opus high — plan fix round 1 (resume a47a01aeb320c74e5)
return: DONE_WITH_CONCERNS series 01_turn-log-plan.md (00 voided as the misfiled 0999 draft; origin resolved at Stop/SessionEnd; open: placement blocking, transcript read blocking, retention 13 months, P1 rates)
baseline: plan review 2 — c50324f2a9b946435eac4f737b22252576eb947f14e83e1d05e802fa4fb4ce36 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/00_initial.md; e655523d0bcef2c7e250f10f69655c8a5ffd20a5af1173db52f325949e4e0256 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/01_turn-log-plan.md; 
dispatch: reviewer opus high — plan review 2 (resume a5f686d69e11c3812)
verdict: plan review 2 NEEDS_CHANGES (must-fix 3, down from 5: worksheet sentence spells seen N: and a store-local decision number; SessionEnd 1.5 s documented budget; Stop's 4 MiB backward search misses long turns; lows 4-6)
dispatch: planner opus high — plan fix round 2 (resume a47a01aeb320c74e5)
return: DONE_WITH_CONCERNS series 02_review-2-fixes.md (findings 1-6; worksheet sentence names turn-log, so README.md:650 and 0999's Patterns line need revising at build)
baseline: plan review 3 — c50324f2a9b946435eac4f737b22252576eb947f14e83e1d05e802fa4fb4ce36 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/00_initial.md; e655523d0bcef2c7e250f10f69655c8a5ffd20a5af1173db52f325949e4e0256 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/01_turn-log-plan.md; 974c5dc1a77fe938bf10c2695ee85b22494b0112c01dbc486159d8da6f5c96de .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/02_review-2-fixes.md; 
dispatch: reviewer opus high — plan review 3 (resume a5f686d69e11c3812)
verdict: plan review 3 NEEDS_CHANGES (must-fix 1, down from 3: tx_at in the shared log leaks per-turn content volume against the privacy rule; low ENOENT tx_at 0; nit wording); README:650 naming ruled fine under principle 4
dispatch: planner opus high — plan fix round 3 (resume a47a01aeb320c74e5)
return: DONE series 03_pending-sidecar.md (tx_at moved to a 0600 per-session sidecar; ENOENT tx_at 0; 0999 wording)
baseline: plan review 4 — c50324f2a9b946435eac4f737b22252576eb947f14e83e1d05e802fa4fb4ce36 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/00_initial.md; e655523d0bcef2c7e250f10f69655c8a5ffd20a5af1173db52f325949e4e0256 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/01_turn-log-plan.md; 974c5dc1a77fe938bf10c2695ee85b22494b0112c01dbc486159d8da6f5c96de .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/02_review-2-fixes.md; 032078bdf2c3e94e03ff0fbf1e4348ac32d0de6cd4362ebe072a55c1caf08d95 .claude-sandbox/investigations/operator-turn-log-a-userpromptsubmit-hoo-3e8e/03_pending-sidecar.md; 
dispatch: reviewer opus high — plan review 4 (resume a5f686d69e11c3812)
verdict: plan review 4 NEEDS_CHANGES (must-fix 1, not lower than review 3's 1: sidecar flock does not survive os.replace; low: prune unlinks non-regular entries)
decided: cap — plan stop and carry at the convergence stop (authority answer 114); if left: finding 1 (per-turn pending files, O_CREAT|O_EXCL|O_NOFOLLOW, unlinked after the origin line; no rewrite, no lock) and low 2 (prune lstat-unlinks non-regular entries) go into the build's acceptance; a round costs another planner and review pass for a one-sentence layout change the build can carry
findings: carried — (1) make each pending turn its own file pending/<safe_sid>/<prompt_id> holding tx_at, created with O_CREAT|O_EXCL|O_NOFOLLOW (0600) and unlinked by the origin step only after that turn's origin line is written; no rewrite, no lock; the prune removes per-turn files over 24 h and empty session dirs; (2) the prune lstats each entry and unlinks any non-regular entry (symlink included, never followed) as well as regular ones over 24 h
decision 181: Where should the operator turn log live? — options: (a) a new small plugin turn-log, off switch TURN_LOG_RECORD=off [recommended] | (b) inside context-guard, CONTEXT_GUARD_TURN_LOG | (c) inside operator-interaction, OPERATOR_INTERACTION_TURN_LOG | (z) decide later
  raised: 2026-10-08T06:30Z
  why ask: placement — a new plugin and its name are API (principle 5) and the operator's to name
  impact: Effect → the turn-log build can start · Wait: blocks the build · reach: the marketplace catalog, one new plugin · undo: renaming later breaks installs and the data path · cost: none now
decision 182: May the turn-log hook read its own session's transcript, at Stop and SessionEnd only, to learn whether a turn was typed by the operator? — options: (a) yes, for the origin kind only [recommended] | (b) no: log every prompt with no origin | (z) decide later
  raised: 2026-10-08T06:30Z
  why ask: trust — the relayed design said "no transcript reading"; reversing it is the operator's call
  impact: Effect → the log can tell your turns from agent reports, peer messages and scheduled tasks · Wait: blocks the origin step of the build · reach: every session with the plugin on · undo: easy, drop the origin step · cost: none
decision 183: How long should the turn log keep its lines? — options: (a) 13 months [recommended] | (b) 3 months | (c) no limit | (z) decide later: build with 13 months
  raised: 2026-10-08T06:30Z
  why ask: retention of a record of the operator's activity is the operator's call
  impact: Effect → sets the prune age, one constant · Wait: nothing, the build uses 13 months meanwhile · reach: the turn-log file on this host · undo: easy; shortening later loses nothing needed · cost: none
correction: no budget: line was written with this item's target: line on 2026-10-08; the build default ($22, other build) applies
