# The worksheet

Fill this in for each decision before you write it. You juggle the dimensions; the operator
sees only what they produce: a level, an answer mode, a place in the order, a basis word and a
card shape. Each group answers one question and sets one thing — merging them into one vague
"type" of decision is what loses information.

## A — Who is reading, and how warm are they? → how much to re-explain

| Field | Values | Who can supply it |
|---|---|---|
| Warmth | **warm** — the operator saw this decision's context in this session, and nothing below happened since; **cold** — any of the events below, or they have never seen it | you, from your own session; a cross-session collector, when one exists |
| Events since the operator last touched it | a context compaction or clear; a different session or repo in between; a hand-off from another agent; **no operator turn since it was last shown** (you printed it while they were away) | you (for your own session); a collector (for others) |
| Age | time since the decision was raised | you, from the decision's record |
| Operator's expected return | when they said they would be back, if they did | you, from what the operator said |

Cold raises the level: a cold reader never gets a line-only decision (the line-only rule in
SKILL.md § Levels), and a block adds a *context you may have lost* part. Re-explaining is
triggered by **events**, not by elapsed time alone: a compaction five minutes ago makes a
reader colder than an idle hour with nothing in between.

The last event is the commonest in a long session. A caller re-entered by background work can
write several messages while the operator is away; a card in the first of them was printed,
not seen. Check your own transcript: if the operator has not taken a turn since the card was
shown, they have not seen it, and it is shown again.

Whether *now* is a good moment to interrupt the operator is a real dimension too, but nothing
observable measures it today; leave it alone rather than guess.

## B — What is at stake if it is wrong? → how it is answered

| Field | Values | Who can supply it |
|---|---|---|
| Reversibility | two-way (a revert, an edit, a re-run undoes it) / one-way (it cannot be taken back, or only at real cost) | you — say how you know; be humble when reversal depends on systems you cannot see |
| Blast radius | narrow (your own branch, sandbox or task) / wide (shared history, other people, other sessions, published artifacts, spend) | you, from what the change touches |
| Others rely on it before review | yes / no — will another agent, session or person act on the outcome before the operator sees it? | you |

Judge **reversibility and blast radius together**; never add them up as two scores. A
decision that is one-way *and* wide (or relied on) is **⚠ one-way**; how it is shown and
answered is SKILL.md § Critical. One-way but narrow is a card marked *one-way, narrow*. Two-way and narrow is the fast tier: a card, or a
line when the line-only rule holds.

## C — How well is it understood? → what evidence is shown, and "investigate first"

| Field | Values | Who can supply it |
|---|---|---|
| Basis | strong / partial / thin / none, with tags (`references/evidence-basis.md`) | you, derived from what you actually ran or read |
| Novelty | seen before (a recurring decision, a template) / new | you |
| Options diverge | the options lead to materially different outcomes / they converge (any would do) | you |
| Options exist | yes / not yet — then it is an open question, not a decision | you |

A thin basis or a new decision raises the level. When the missing fact could change the choice
and finding it costs less than choosing wrong, offer **investigate first** as a priced option
(its time and cost stated). Converging options are one of the conditions of the line-only
rule (SKILL.md § Levels).

## D — What does waiting cost? → the order

| Field | Values | Who can supply it |
|---|---|---|
| Deadline | when something breaks if unanswered (a lock or lease expires, a due time passes), or none — as an absolute time in the operator's zone when known, with the relative time and when you wrote it | you — state it |
| Blocks | what waits on it: your own next step; other work; other sessions | you (your own); a collector (other sessions) |
| Age | as in A | you |

A deadline that falls before the operator is back — or any stated deadline, when their return
is unknown — puts the decision first (SKILL.md § Order). Otherwise waiting cost and age order
it.

Two clocks are in play, and each sets something different:

- **events since the operator last touched it** (group A) set how much to re-explain;
- **time until something breaks** (the deadline) sets urgency.

Age — time since it was raised — is shown on the list line and breaks ties, nothing more.

## E — What kind of ask is it? → the card's shape

| Kind | Shape |
|---|---|
| **Choose** among options | options with impacts, recommendation, decide later |
| **Approve** a proposed action | approve / change it / decide later, with the consequence of each |
| **Preference** — no fact settles it | options with impacts, labelled *your preference — no recommendation* |
| **Outside my authority** | options with impacts, labelled *no recommendation — outside my authority*, with why |
| **Alert** — time-critical | the fact now, bare; the options next |
| **Open question** — not defined yet | listed under *Open questions*, unnumbered, until it has options |
| **FYI after acting** — nothing to answer | one line: what was done, why it was safe to do, how to undo it |

**FYI after acting** is allowed only for an action that is two-way, narrow, relied on by
nobody before the operator reviews it, and inside authority the operator already gave — an
answered decision, or the task you were assigned. Never for ⚠, never when others rely on it.
An action about to happen unless the operator stops it is **not** an FYI: it is an approve
ask, and it waits. When in doubt, ask.
