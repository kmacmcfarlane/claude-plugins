---
id: decisions-how-well-one-turn-handles-a-ba-6d2c
title: "decisions: how well one turn handles a batch of free-form decision replies (research spike)"
type: spike
status: done
priority: 2
created: 2026-09-29
updated: 2026-09-30
closed: 2026-09-30
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'could there be a performance difference in replying to a bunch of decisions at once versus a different flow? ... research spike to understand the dynamics of the LLM in terms of how it can think about responding to a bunch of (maybe not-super-related) decisions at once? Perhaps these free-form types of decision responses should get their own separation within your turn or a more robust way to evaluate them ... is this giving you the most traction?' Acceptance: a series with external evidence on multi-item instruction handling by LLMs and our own transcripts (primary sample: the operator's 2026-09-29 reply to 89-97), candidate flows (per-reply handling, structured parse-then-act, per-reply sub-agents, one decision at a time), how to measure traction, and a recommendation.

## Handoff
- doing: —
- next: series closed at the cap; decision 100 wakes at the pyramid turn (69ee)
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — research spike with web evidence, plan mode (series 6d2c-batched-decision-replies)
agent: a3aadbcfa2cdcba92 (planner r1)
notify: send agents a pointer when this series lands (agents asked)
series 00 written: 16 multi-decision replies/109 parts audited, 0 dropped, 1 misread (pre-echo), 1 question acted on without words; rec (b) ledger before acting; 3 open questions
dispatch: plan reviewer opus — fresh, round 1 (verify sources)
agent: a3f07ddf0e7d185f9 (plan reviewer r1)
plan review r1 NEEDS_CHANGES (2H 8M 9L): H1 self-check evidence contradicts current-model guidance; H2 pilot adopts on noise; M1-M3 literature transfers overstated (two already relayed to the operator in chat as findings -> CORRECTION owed); M4 counts miss rows 4 and 8; M5 costly-to-undo undefined; M6-M8 question options
CORRECTION owed to operator: "misses are follow-through items" and "one per turn does worse" were relayed as findings; the sources do not support them for this case
dispatch: planner opus — resume, serial 01
serial 01 written: rec now (c) single pass + two sentences + hold on materially ambiguous relied-on actions; pilot is priced option (g) ~$47-70; one open question
dispatch: plan reviewer opus — fresh, round 2
agent: a37520fd95af6852f (plan reviewer r2)
plan review r2 NEEDS_CHANGES (2H 3M 5L): H1 hold firings miscounted, caught 0 errors when counted consistently; H2 pilot (g) cannot separate the flows; M1-M3 hold conflicts with replies/decisions-last and overlaps 8dee; lows: 1 reading problem not 2
dispatch: planner opus — resume, serial 02
serial 02 written: confirm-first caught 0 errors, rec (b) two sentences; ladder a-d + z; pilot not offered; correction on the two relayed lines already delivered to the operator after r1
dispatch: plan reviewer opus — fresh, round 3
agent: a61ded2910fee94aa (plan reviewer r3)
review r3 NEEDS_CHANGES (0H 2M 5L): card wording only — (b) line must say reply-driven pushes/peer messages still act before the operator sees them; sentence 2 repeats the existing echo rule; echo rewording must keep the ⚠ read-back and its purpose; lows incl. correction already delivered, 8dee handoff line (added)
dispatch: planner opus — resume, serial 03 (round 4 is the cap)
serial 03 final card written: ladder (a)-(d)+(z), rec (b) answer questions in words, echo per part, echo timing matches practice except the ⚠ read-back
dispatch: plan reviewer opus — fresh, round 4 (the cap)
agent: a0e5ae3828b64d323 (plan reviewer r4)
plan review r4 (the cap) NEEDS_CHANGES (0H 1M 5L), all wording: M build step-3 text must keep "When in doubt, ask" for actions others rely on and state the echo limit (reviewer wording at reviews/plan-review-r4.md:42-53); lows: (b) card line tightened (r4:67-83), 3 of 23 not 3 of 78, (b) stakes wide, two Supersedes misses, three unglossed terms
librarian ruling: no round past the cap — every finding is wording; the card goes out with the reviewers wording applied, and the build text (M1) is carried as acceptance on the build item; the series closes on 00-03 + review r4
decision 100: How should the librarian handle a message that answers several decisions at once? — options: (a) change nothing | (b) answer questions in words: every question inside a reply gets an answer in words, each part of a mixed message gets its Read-as line, the echo happens with the actions, the ⚠ read-back still waits [recommended] | (c) (b), plus confirm-first on uncertain readings that drive actions others rely on (line set by 8dee) | (d) (c), plus a visible list of every part and its planned action before anything changes | (z) decide later
  raised: 2026-09-29T06:36Z
  stakes: reversible, wide (every librarian session follows it)
  why now: the operator asked (2026-09-29) whether one pass over a batch gives the best traction; one question in the 89-97 batch got an action and no words
  rec: (b) · basis partial — the question gap is observed; the confirm-first check would have caught 0 errors in 16 batches
reply 100 noted (not an answer): "Your recommendation about how to handle batched-replies sounds sound to me" — and a low-priority follow-up filed (decisions-refine-and-test-the-batched-re-852f)
wake 100: the pyramid decision turn (decision-handling-the-pyramid-shaped-dec-69ee) — operator 2026-09-29: "let's continue before making final decisions"
answer 100: b (pyramid answer page, 2026-09-30T20:55Z)
2026-09-30 build filed from 100 b: decisions-answer-every-question-inside-a-9ea7 (M1 carried as acceptance); no confirm-first trigger (8dee F6 not built). Spike closed on its series 00-03 + review r4; the agents pointer goes with 0c4d's delta-01.
- 2026-09-30 done
