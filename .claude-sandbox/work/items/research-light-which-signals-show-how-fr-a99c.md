---
id: research-light-which-signals-show-how-fr-a99c
title: "research (light): which signals show how fresh a decision's subject is in the operator's mind"
short_display_name: operator-freshness signals
type: spike
status: done
priority: 1
created: 2026-09-29
updated: 2026-09-29
closed: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29 (.claude-sandbox/investigations/5140-decision-lifecycle/evidence/operator-notes-2026-09-29-stream.md): 'How can we only present decisions in a way that is answerable (depends on how fresh the operator's working memory in their brain is about the subject, may be culled switching between tasks). We have some guidance around recency of response to gauge how interactive the session is. How can we use that better, or are there other signals we should be looking at too?' Acceptance: a light series on signals of operator context freshness (reply latency, task switches across sessions, the subject's last mention, tell-me rounds, answer shape) from transcripts and the store, plus external evidence on task switching and resumption; how the decisions skill's warm/cold reading (worksheet group A) should use them.

## Handoff
- doing: —
- next: planner r1 running; then a fresh plan review; notify agents and operator-attention when it lands
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — light research spike, plan mode (series a99c-operator-freshness-signals)
agent: a8307a75146d1df1b (planner r1)
notify: send agents a pointer when this series lands (agents asked)
notify: send operator-attention a pointer when this series lands (their R48 depends on it)
input from operator-attention: no store records that a decision was shown to the operator; their R47 (recency) and shared warm/cold test rest on it — a shown timestamp is a candidate signal source
series 00 written: age >=12h and >=20 operator turns elsewhere each mark 10 of 11 lost-context answers (1 of 31 otherwise); compaction and latency weak; "show me the decisions" is an observable signal; proposal: long-absence event, full re-show on request, stored context line, no re-printing while away; D1-D4 candidates
dispatch: plan reviewer opus — fresh, round 1
agent: a3e0a42b012f2f697 (plan reviewer r1)
plan review r1 NEEDS_CHANGES (1H 3M 1L): H D1 8h rule untested (counted from last show it catches 0); M coding uneven: recoded 8-9 of 20 vs 0-1 of 31 (not 10 of 11 vs 1 of 31); M the 84-86 re-show was three full blocks, not a context line; M D1/D3 change ruled rules unnamed; L shown timestamp input unanswered
CORRECTION owed to the operator: "10 of 11 vs 1 of 31" is the most favourable coding (8-9 of 20 vs 0-1 of 31); the 84-86 re-show was full blocks, not a context line
dispatch: planner opus — resume, serial 01
serial 01 written: recoded 8 of 20 vs 1 of 31 (range 7-9 vs 0-1); revised D1 (b) a turn counts as seeing only with no work elsewhere in between (adds 84-86); 0999 needs a seen N: time beside shown N:; D2 (b) stored Context: cue (untested); D3 names the rules it changes
dispatch: plan reviewer opus — fresh, round 2
agent: a64a2778a457cb64d (plan reviewer r2)
plan review r2 NEEDS_CHANGES (1H 2M 1L): H with D3 (b) (no re-printing while away) 84-86 would have been cards, so D1 (b) catches nothing extra — make (a)/(z) conditional on D3, gain inferred; M the stated D1 (b) scores 43 cold / 8 warm (1 of 44 re-shown warm), 42/9 was an unstated 5-turn variant; M D4 restated against D1 (b), homes 76bc/R48; L range 7-9 of 20
CORRECTION owed to the operator: "catches exactly 84-86" — the no-re-printing-while-away rule alone would have caught 84-86
dispatch: planner opus — resume, serial 02
serial 02 written: D3 (b) recommended (re-show as cards at the first turn back after being away; all 44 re-shown cold, all 9 lost-context covered); D1 becomes (c) a later refinement once 0999 stores seen N: and 76bc/R48 publish turn times; D4 (b) send requirements to 76bc/R48
dispatch: plan reviewer opus — fresh, round 3
agent: a475313e4557dda4d (plan reviewer r3)
plan review r3 NEEDS_CHANGES (1H 2M 1L): H d3overlap skips D3 (b)s own lines-while-away rule: at least 6 of 44 re-shown are lines (16 if a resets cold ends at the next Report, incl. 96); 84-86 covered only if the re-show waits for the first decisions block after the return and repeats until a turn follows; the away test fires with the operator present; M D3 narrows Seen and reverses gallery 21, unnamed; files omitted; M D1 (c) is really (z) with a wake; L away fires on about 21 of 63 turns
CORRECTION owed to the operator: "covers all 9" is false as worded — at least 6 of 44 re-shown would still be lines
dispatch: planner opus — resume, serial 03 (round 4 is the cap)
serial 03 final: D3 (b) cards 8 of 9 lost-context answers (9 of 9 with the show-me trigger) vs today 5 (6); full cards printed while away 109 -> 1; away test derived from the operators own turn gaps (87 min upper quartile), may conflict with ruling 78 (a); D1 (z) wake at 0999 + 76bc/R48; D2 (b); D4 (b)
dispatch: plan reviewer opus — fresh, round 4 (the cap)
agent: af6e453dc669f6b50 (plan reviewer r4)
plan review r4 (the cap) NEEDS_CHANGES (0H 1M 2L): M the D3 card leaves the conflict with ruling 78 (a) "no arbitrary numbers" as an unknown and offers no number-free option; pass: ask it, offering D3 (b) without the time part (8 of 9 either way; 22 of 55 turns owe a re-show; 96 becomes a line with the pull); L "same at the median" true only without the pull; L "none under an hour apart" follows from the threshold
decision 106: The operator-freshness research (a99c) hit the review cap with one medium left, about how its recommended card is worded; close it and carry that fix into the pyramid card, or run one more round? — options: (a) close the series; the librarian renders the D3 card in the pyramid with the 78 (a) conflict asked as a question and a no-number variant offered, using 03's own figures [recommended] | (b) one more planner round and a fresh review | (c) park the series | (z) decide later
  raised: 2026-09-29T08:00Z
  stakes: reversible, narrow (research input; the fix is to the card the operator will read)
  if left: the pyramid card would hide a conflict with the operator's own "no arbitrary numbers" ruling unless the librarian renders it as (a) says
  round costs: one planner round plus a fresh reviewer, about 15-20 minutes and roughly 0.5-1% of weekly quota at the current sub-agent effort; none of the operator's time
  rec: (a) · basis strong — review r4 gives the exact figures for the no-number variant
answer 106: a (read as: close the series; the librarian renders the D3 card in the pyramid with the 78 (a) conflict asked as a question and a no-number variant offered, from 03 and review r4)
- 2026-09-29 done
