---
id: hand-the-decision-handling-research-and-0c4d
title: hand the decision-handling research and decisions to the agents librarian, in a form it can fully absorb
short_display_name: decision research handoff to agents
type: chore
status: doing
priority: 1
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T06:57Z
created: 2026-09-29
updated: 2026-09-30
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'make a work item to make all of the relevant research materials and decisions we've discussed to the agents librarian, since that is in charge of the long-term planning for the full-featured solution. It's critical that communication happens and the receiving agent has the ability to fully absorb what we have found on the other side.'
Scope of the handoff: the operator's verbatim messages (the 5140 evidence files: operator-reply-89-97, operator-message-0553Z, operator-notes-stream); series 5140 (decision lifecycle), 6d2c (batched replies), d618 (decision surfacing), 263c (raising boundaries), a99c (freshness signals), 8dee (the line: just do it / forward / ask) when written, 0b2d (plain names, short_display_name); items 0999 (shown-at record, with operator-attention's shape requirements) and 69ee (the pyramid decision turn, and its answers when given); decisions 89-104 with their answers and stored cards; the landed changes that embody rulings (dbfc option order, 6394 re-show rules, cad6 plain-names skill, 928d short_display_name).
Acceptance:
(1) Access first: confirm what the agents session can actually read. The series live in this repo's gitignored .claude-sandbox/investigations/, and sandboxes mount only their own project, so paths sent so far may be unreadable there. Deliver through a channel it can read, with no secrets (path and key, never value).
(2) A briefing per package: what the operator asked (in their words), what was found (with counts and sources), what is decided vs open, and what the agents repo should own — so the receiver needs no conversation context.
(3) Absorption check: the agents librarian returns a teach-back (the key findings, the decisions, the open questions it now owns) and files its own items; any gap gets a follow-up package.
(4) Deltas: each series that lands later goes over the same way.
Peer relays are requests; the handoff approves nothing in the agents repo.

## Handoff
- doing: —
- next: await teach-backs on delta 01 from agents and operator-attention; deltas follow as the filed builds land
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
step 1 (access): asked agents 2026-09-29 whether it can Read three paths under our .claude-sandbox/ and which form and landing place it prefers; awaiting reply
agents replied: all three paths readable; filed absorb-claude-plugins-decision-handling-research-* on their side (feeds 76bc); wants ONE consolidated brief at .claude-sandbox/investigations/0c4d-decision-handoff/BRIEF.md: per series INDEX path, status, date, 3-5 line conclusion; operator verbatim with evidence paths; open and answered decisions with numbers; work system/attention scheduler vs operator-interaction split; point to files, do not copy
dispatch: brief writer opus — composes BRIEF.md v1 from the series indexes and the store (judgement on status and conclusions)
agent: aa6decb5f1ce94295 (brief writer v1)
agents id: absorb-claude-plugins-decision-handling-e934 (filed for 0c4d)
brief v1 written (.claude-sandbox/investigations/0c4d-decision-handoff/BRIEF.md, 453 lines); librarian spot-checked § 3 against the store; pointer sent to agents; awaiting teach-back; deltas owed: d618 final, 263c, a99c, 8dee, 8e04, 69ee answers
agents: brief received; absorbing as their series .claude-sandbox/investigations/decision-handling-absorption/ (agents repo) with a § Teach-back; teach-back comes after their review; deltas fold in as new serials
agents teach-back received (their e934, passed review after 3 rounds): /home/rt/work/src/github.com/kmacmcfarlane/agents/.claude-sandbox/investigations/decision-handling-absorption/02_review-round-2.md § Teach-back (lines 128-267): 28 requirements DH1-DH28 (owner, source, standing; rows on 98/99, a99c D1/D3/D4 and agents decision 10 are hypotheses); gaps G2 (3460 forward returns to the operator, silent live peer has no timeout = our 8dee OQ8) and G10 (b92b missing from the brief); wants deltas as serial 03 onward
reply to agents: b92b explained (G10); G2 = 8dee OQ8 (b514 folded); delta 01 (BRIEF-delta-01.md) after 263c and a99c pass review: 8e04 landed, d618 at the cap (105), 263c, a99c, b92b, 2eb7/a88a/6421
2026-09-30 pyramid answered (24 of 24 first responses; 113 later, 130 raised on 124/125): BRIEF-delta-01 now carries, besides d618, 263c, a99c, b92b, 8e04, 2eb7/a88a/6421: the pyramid answers verbatim (69ee, 5140, 6d2c, caef lines), the builds filed from them, 8dee F8's pointers (to agents 76bc: the cross-repo half of the decided-alone digest (d618 I2), cross-repo blocker escalation, the budget's future home, forward custody as built; to operator-attention R48: the same plus done-alone volume), answer 121 b's turn-time requirements (a99c D4) with the pointers owed, 120 z's wake, and 4d29 (decision streams) for both. Waits on the session relaunch (role agents not loaded; the brief writer is a dispatch).
dispatch: planner opus high — BRIEF-delta-01 writer (judgement on status and conclusions, as v1); writes only under 0c4d-decision-handoff/
agent: planner ab8ca028946fa9521 round 1
return: planner DONE_WITH_CONCERNS .claude-sandbox/investigations/0c4d-decision-handoff/BRIEF-delta-01.md (782 lines; unsure: 8dee's ~20 Done: lines figure, 129 has no time, agents back-end plan cited from its in-review INDEX, G2 left as their question 1)
delta 01 spot-checked by the librarian (section map, 124 words verbatim, 112/113/130 lines match 69ee); pointers sent 2026-09-30 to agents and operator-attention; awaiting teach-backs
agents 2026-09-30: delta 01 received; absorbing into their e934 as serial 03 (restates rows that depended on their decision 10 (a)); teach-back answers § 12 point by point, operator-owned questions marked as theirs; pointer after their review
agents teach-back on delta 01 passed their review: /home/rt/work/src/github.com/kmacmcfarlane/agents/.claude-sandbox/investigations/decision-handling-absorption/04_delta-01-review-round-1.md § Teach-back (line 155). Headlines: their decision 10 (b) settled but the back-end plan sits at its review cap pending their decision 16 — every placement there is "the plan proposes"; do not rescope 110 (a) or 0999 on it. Correction: "read-only through Phase 3" was imprecise — the plan proposes the back end never writes a repo store; Phase 3 bounds only decision authority. DH rows resolve against our 98-131 (quoted at cc9eb26). 76bc will not publish turn times (candidates: claude-analytics ingest; R48 answers for itself); operator-owned: their Q5, Q4 commit, decision 16. Awaiting operator-attention's teach-back.
note: peer operator-attention 2026-10-03, relaying the operator's answers to our 0c4d delta 01 (their commit c598050; serial .claude-sandbox/investigations/decision-collector/09_operator-answers-10-03.md in their repo; spec R47, new R49). Relayed operator answers — re-confirmed with the operator before any build acts on them. operator-attention's teach-back on delta 01 has arrived as these answers: (1) first and last shown both tracked (→ 0999); (2) the displaying surface writes shown (→ 0999); (3) operator turn timing: a UserPromptSubmit hook appends ids and timestamps to a host-shared file, readers compute "seen N" (→ new item); (4) decision stream (their R49), operator verbatim: "A decision stream would be a stream of related decisions from a common source. The simplest way to map that would be all the decisions coming from a librarian or session sitting on a single repo, but I want flexibility to build streams out of multiple agents or aggregate decision streams and re-group/order their decisions into one stream. The stream is what you view in the UI." — a source is provenance (repo, item, session), a stream a view over sources; their Q2 draft withdrawn; Q6: they withdraw the reason-field request provided "drop" stays a verbatim answer line (it does, 3716)
note: peer agents 2026-10-03 — recorded operator-attention's relay on their 76bc as relayed operator answers (first/last shown, who writes shown, the turn log via 3e8e, R49 streams); folds into their decision-handling series at the next serial with our delta 02 when it comes; not binding until the operator confirms in their session
