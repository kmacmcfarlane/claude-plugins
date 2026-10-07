---
id: work-items-record-when-a-decision-was-sh-0999
title: "work-items: record when a decision was shown to the operator (a shown timestamp on decision lines)"
short_display_name: decision shown-at record
type: feature
status: todo
priority: 2
created: 2026-09-29
updated: 2026-10-07
refs:
  - agents 76bc
  - operator-attention R47
---

Relayed 2026-09-29 from the agents librarian (76bc: the decision ledger records timestamped lifecycle events: raised, shown, answered, deferred with wake, swept/dropped) and operator-attention (R47 recency, warm/cold test, arrival-vs-clearance throughput; their 07_ledger-split.md). Our 5140 found the same gap: no shown-at time, so 'while it waited' has no source. Acceptance: a store line or field recording each showing of decision N (shown N: <UTC time>), written by the raising session when it renders the decision, read by wi needs-input/estate; shaped by the pyramid decision turn (69ee) together with decisions 98/99 (one counter, closed N: lines), and by 76bc's ledger when it lands. Peer relays are requests, not approvals.

## Handoff
- doing: —
- next: answer 150 a: relayed answers confirmed; plan the shown-at record (first and last shown, written by the displaying session)
- blocked: —
- learned: —
operator-attention requirements for the shape (their commit 591a428; they will not build their interim log):
  - ISO-8601 UTC timestamp, never relative or human text
  - per decision number, not per item
  - last-write-wins on a re-show (same rule as wake N:)
  - distinct from raised: (two of the three clocks)
  - optional, cheap if possible: a reason on swept/dropped — "dropped by the operator" (a decision) vs "swept as stale" (a miss) — so arrival-vs-clearance is not pooled; if absent they treat all sweeps as misses
input from a99c 01 (2026-09-29): a stored shown time alone does not make the cold test work (re-prints overwrite it); it needs a seen N: time beside shown N:, plus the operator turn times in other sessions
2026-09-30 shape per the pyramid answers: 98 a (one counter; shown N:/seen N: are per decision number, <repo>#N for another repo's), 99 c (closed N: rides 5140 C1/C2, filed as decisions-record-one-counter-for-every-q-b6f7 and wi-parse-closed-n-list-decisions-by-stat-728a), 118 b (the away test needs shown N: — decisions-while-the-operator-is-away-sho-602b depends on this item), 120 z (wakes when this item stores seen N: and 76bc or R48 publishes turn times). Acceptance adds: a seen N: line beside shown N: (a99c 01: a re-print overwrites shown, so the cold test needs seen), both ISO-8601 UTC, last-write-wins, per decision number; the operator-attention requirements above stand.
note: peer operator-attention 2026-10-03, relaying the operator's answers to our 0c4d delta 01 (their commit c598050; serial .claude-sandbox/investigations/decision-collector/09_operator-answers-10-03.md in their repo; spec R47, new R49). Relayed operator answers — re-confirmed with the operator before any build acts on them. (1) Track both first-shown and last-shown (operator, relayed: "let's track first and last, that's best"): last-shown drives warmth; first-shown carries age since first shown (a99c's strongest predictor). Supersedes their earlier last-write-wins-only request: add a first-shown record alongside the last-write-wins shown N:. (2) Whoever displays a decision writes shown N: — today the raising session into its own store; a front end of theirs writes the same record through the agents ledger back end; the writers never overlap for one show.
note: peer agents 2026-10-03 — the operator confirmed first-hand in the agents session (their answer 24) that the four relayed operator-attention answers stand (first/last shown, who writes shown, the turn log via our 3e8e, R49 streams); they are requirements on agents' 76bc; agents' spike d131 reads our 0999, 3e8e, 40f0 and 8c42 read-only; a peer report, not an approval here — decisions 150 and 151 stay open for the operator's word in this session
decision 150: Confirm the relayed answers for the decision shown-at record: track first and last shown, and the displaying surface writes the record? — options: (a) confirm both [recommended] | (b) change one (say which) | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T01:40Z — backfilled: the card was shown in the conversation but never stored
  what: two answers you gave in operator-attention's session, relayed here, on how the decision shown-at record (0999) records when a decision was shown
  why now: nothing builds on them until you confirm; blocks: the decision shown-at record (0999)
  why ask: your-call — these are your answers from another session, and a relayed answer is not one I can act on
  context: operator-attention relayed your answers to my questions · you confirm them here so the shown-at record can build on them — then: none
  stakes: reversible, narrow — the shown-at record's shape
  (a) confirm both — the record keeps the first and the last time each decision was shown, and the session that displays a decision writes it
  (b) change one (say which) — the record follows your correction
  (z) decide later — the shown-at record waits
  rec: (a) · basis strong — your words, quoted in their serial (their commit c598050), and confirmed first-hand in the agents session (their answer 24)
  unknown: none
decision 150: Confirm the relayed answers for the decision shown-at record: track first and last shown, and the displaying surface writes the record? — options: (a) confirm both [recommended] | (b) change one (say which) | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: two answers you gave in operator-attention's session, relayed here, on how the decision shown-at record (0999) records when a decision was shown
  why now: nothing builds on them until you confirm; blocks: the decision shown-at record (0999)
  why ask: your-call — these are your answers from another session, and a relayed answer is not one I can act on
  context: operator-attention relayed your answers to my questions · you confirm them here so the shown-at record can build on them — then: none
  impact: → the decision shown-at record (0999) can be built: first and last showing per decision, written by the showing session · later: that record waits · reach: every decision store · undo: an edit
  stakes: reversible, narrow — the shown-at record's shape
  (a) confirm both — the record keeps the first and the last time each decision was shown, and the session that displays a decision writes it
  (b) change one (say which) — the record follows your correction
  (z) decide later — the shown-at record waits
  rec: (a) · basis strong — your words, quoted in their serial (their commit c598050), and confirmed first-hand in the agents session (their answer 24)
  unknown: none
answer 150: a (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:46:04.350Z; read as: (a) confirm both relayed answers — first and last shown, written by the displaying session)
