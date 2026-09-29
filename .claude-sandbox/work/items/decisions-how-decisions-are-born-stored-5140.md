---
id: decisions-how-decisions-are-born-stored-5140
title: "decisions: how decisions are born, stored and retired (genesis and lifecycle research spike)"
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T05:26Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29, replying to decisions 89-97: 'how are decisions created and stored? We have talked a lot about how they are asked/presented, but not about their genesis or lifecycle. That is another research spike right there.' Acceptance: a series that maps where decisions come from (what triggers one, who raises it, what makes something a decision vs decided alone), how they are stored, revised, answered, deferred and retired, audited against the store's real decision N / answer N history and transcripts on disk; gaps and a proposed lifecycle. Evidence base overlaps b8d6 (decide-alone class, from conversations on disk). Its genesis findings feed the librarian policy spike.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — research spike, plan mode (series 5140-decision-lifecycle)
agent: a48708cf8f38447a0 (planner r1)
notify: send agents a pointer when this series lands (agents asked)
series 00 written: 94 numbered decisions in 13 days (+38 outside the counter); 72% took the rec; 18 unanswerable as posed; 14 never stored, 9 answer formats; decide-alone invisible; no retirement; 5 open questions; 3 store fixes proposed as rule-in-force
dispatch: plan reviewer opus — fresh, round 1 (verify counts)
agent: ad9b50151acc7fd54 (plan reviewer r1)
plan review r1 NEEDS_CHANGES (2H 5M 9L): H1 Q5/C5 duplicate dbfc; H2 D-1 (68/69 as deferrals) is a guess, not a rule in force; M: 43 bare letters is 29; 18-unanswerable label inconsistent; 175 D lines include restated rulings; stakes: judged too early; Q2(b)/Q5(a) belong to 8dee
CORRECTION owed to operator: "43 as a bare letter" is 29 (43 took the rec as offered)
dispatch: planner opus — resume, serial 01
serial 01 written: recounts (29 bare letters; 195 D lines, <=82 own rulings); only D-3 stays rule-in-force; D-1 -> OQ6; C5 dropped; OQ1,3,4,5,6 (OQ2 to 8dee)
dispatch: plan reviewer opus — fresh, round 2
agent: a19ef8d90eb76190c (plan reviewer r2)
review r2 NEEDS_CHANGES (1H 4M 2L): OQ5 and OQ1 handed to 8dee; D-3 applied by the librarian (caef 96 card re-written, answer 96 recorded); D-2 needs the operator (make it an OQ4 option); corrections owed to the operator for the 05:44Z claims; 05:53Z operator message found in transcript
dispatch: planner opus — resume, serial 02
agent: a48708cf8f38447a0 serial 02 (resumed)
serial 02 written: 3 questions (OQ3 one counter, OQ4 closed N: + restore old answers, OQ6 68/69 hold); C7 answer lines keep replies verbatim (12 of 27 older free-form replies are summaries); corrections list 1-6
dispatch: plan reviewer opus — fresh, round 3
agent: ad6046b51deacaa41 (plan reviewer r3)
review r3 NEEDS_CHANGES (1H 2M 3L): corrections: item 3 went out wrong ("in 13 the options did not fit"), "89-97 stored in your words" wrong (95, 97 were summaries; verbatim lines added now), "no decisions are open" wrong (70 open, 68/69 held); OQ6 why-now false (agents 29d6/bf41 track the scheduler) and must include 70; OQ4 decide-later needs the transcript-retention deadline; C7 grounding; 12 of 27 -> about 5 whole; provenance times fixed (06:08Z, not 07:00Z)
dispatch: planner opus — resume, serial 03 (round 4 is the cap)
serial 03 final: OQ3 one counter (a), OQ4 closed N: + re-record 28 verbatim (c), OQ6 held until agents bf41 (29d6 notifies); verbatim copy of replies 1-63 saved; corrections A-C delivered in the librarian message after 06:22Z
dispatch: plan reviewer opus — fresh, round 4 (the cap)
agent: a303d1e438bcfcb29 (plan reviewer r4)
plan review r4 (the cap) NEEDS_CHANGES (0H 1M 4L), all sentence-level: M OQ4 says nothing of the ~15 recent summary answers (64-88 only in the live transcript); L decision 27 wording exists in 0c7eafc7; L correction C did not echo OQ6; L dbfc cites moved; L glosses
librarian ruling: no round past the cap — the cards go out with these fixed in the rendering (OQ4 (c) widened to the recent summary answers; 27 from the transcript); the build items carry the rest as acceptance; series closes on 00-03 + review r4
decision 98: Should every question put to the operator take a number from the one decision counter? — options: (a) yes; series labels (R/G/P, OQ) become tags, another repo's decision is written <repo>#N, the opt-in dialog is the one exception [recommended] | (b) numbered only when raised on a work item, as today | (c) numbered per series, as today | (z) decide later
  raised: 2026-09-29T06:36Z
  stakes: reversible, wide (every librarian session; readers of decision lines in other repos)
  why now: 25 questions ran outside the counter in 13 days, and 13 more before it existed; they can't be listed, aged or closed
  rec: (a) · basis strong — one counter is what makes every ask findable (5140 series)
decision 99: Should the store record when an answer was carried out, superseded or made into a rule, and restore the answers stored as summaries in the operator's own words? — options: (a) no new line; the commit subject is enough | (b) a closed N: line from now on (acted <commit|item> | rule <path> | superseded by M), and wi lists answered-but-not-closed | (c) (b), plus re-recording in the operator's words the 28 old closed-item answers (from the verbatim evidence copy) and the ~15 recent answers stored as the librarian's summary (from the transcripts) [recommended] | (z) decide later
  raised: 2026-09-29T06:36Z
  stakes: reversible, narrow (this repo's store and wi)
  why now: at least 10 answers became skill rules with no link back; the operator called word-for-word storage "a good source of truth to be able to go back to", yet many answers are summaries
  rec: (c) · basis partial — puts the operator's words in the tracked store at the cost of one short chore
wake 98: the pyramid decision turn (decision-handling-the-pyramid-shaped-dec-69ee) — operator 2026-09-29: "let's continue before making final decisions"
wake 99: the pyramid decision turn (decision-handling-the-pyramid-shaped-dec-69ee) — operator 2026-09-29: "let's continue before making final decisions"
