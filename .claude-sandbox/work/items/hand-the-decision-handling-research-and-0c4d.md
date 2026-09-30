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
- next: after the session relaunch (role agents loaded): dispatch the brief writer for BRIEF-delta-01 (contents listed 2026-09-30 in Notes), send the pointer to agents and operator-attention, await teach-back
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
