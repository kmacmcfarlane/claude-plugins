# The worksheet

Fill this in for each decision before you write it. You juggle the dimensions; the operator
sees only what they produce: a level, an answer mode, a place in the order, a basis word, a
card shape, what it takes to act, the Context (§ The Context) and the Impact line (§ The
Impact line). Each group answers one question and sets one thing — merging them into one vague
"type" of decision is what loses information.

## A — Who is reading, and how warm are they? → how much to re-explain

| Field | Values | Who can supply it |
|---|---|---|
| Warmth | **warm** — the operator saw this decision's context in this session, and nothing below happened since; **cold** — any of the events below, or they have never seen it | you, from your own session; the caller's record of shown and seen, after a reset or from another session; a cross-session collector, when one exists |
| Events since the operator last touched it | a context compaction or clear; a different session or repo in between; a hand-off from another agent; **no operator turn since it was last shown** (you printed it while they were away) | you (for your own session); the caller's record of shown and seen (the last showing, and whether a turn has seen it); a collector (for others) |
| Age | time since the decision was raised | you, from the decision's record |
| Operator's expected return | when they said they would be back, if they did | you, from what the operator said |

Cold raises the level: a cold reader never gets a line-only decision (the line-only rule in
SKILL.md § Levels). Warmth does not decide whether Context is shown: every card and block
carries it (§ The Context). Re-explaining is triggered by **events**, not by elapsed time
alone: a compaction five minutes ago makes a reader colder than an idle hour with nothing in
between.

The last event is the commonest in a long session. A caller re-entered by background work can
write several messages while the operator is away; a card in the first of them was printed,
not seen. Check your own transcript: if the operator has not taken a turn since the card was
shown, they have not seen it, and it is shown again. Without the transcript (after a reset,
or from another session), read the caller's record of shown and seen, where it keeps one: a
last showing no turn has seen, or no showing recorded, is cold.

Whether *now* is a good moment to interrupt the operator is a real dimension too, but nothing
observable measures it today; leave it alone rather than guess.

## B — What is at stake if it is wrong? → how it is answered

| Field | Values | Who can supply it |
|---|---|---|
| Reversibility | two-way (a revert, an edit, a re-run undoes it) / one-way (it cannot be taken back, or only at real cost) | you — say how you know; be humble when reversal depends on systems you cannot see |
| Blast radius | narrow (your own branch, sandbox or task) / wide (shared history, other people, other sessions, published artifacts, spend) | you, from what the change touches |
| Others rely on it before review | yes / no — will another agent, session or person act on the outcome before the operator sees it? | you |

Judge **reversibility and blast radius together**; never add them up as two scores. A
decision is wide when any of its options is. A decision
that is one-way *and* wide (or relied on) is **⚠ one-way**; how it is shown and answered is
SKILL.md § Critical. One-way but narrow is a card with no ⚠ label, its one-way option
carrying `⚠ undo:`. Two-way and narrow is the fast tier: a card, or a line when the line-only
rule holds. The operator never sees these words as a label: reversibility is shown as
`⚠ undo:` on each option that is one-way or costly to undo (how, at what cost, or why not),
and as nothing on an option reversible at little cost; blast radius is shown as **Reach**
(who or what), § The Impact line. Judge each option's reversibility on its own: the marker
goes on that option, never on the decision.

## C — How well is it understood? → what evidence is shown, and "investigate first"

| Field | Values | Who can supply it |
|---|---|---|
| Basis | strong / partial / thin / none, with tags (`references/evidence-basis.md`) | you, derived from what you actually ran or read |
| Novelty | seen before (a recurring decision, a template) / new | you |
| Options diverge | the options lead to materially different outcomes / they converge (any would do) | you |
| Options exist | yes / not yet — then it is an open question, not a decision | you |
| Still open | what is not known yet about this decision, one line each, or nothing: the card's ▸ Open questions fold (`references/rendering.md` § Folds) | you |

A thin basis raises the level; so does a new decision, unless its options converge (any would
do) — converging options stand in for a seen template in the line-only rule (SKILL.md
§ Levels). When the missing fact could change the choice and finding it costs less than
choosing wrong, offer **investigate first** as a priced option (its time and cost stated).

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

What it blocks and what waiting costs are shown as the **Wait** facet, on every list line and
up (§ The Impact line).

## E — What kind of ask is it? → the card's shape

| Kind | Shape |
|---|---|
| **Choose** among options | options with impacts in letter order, the recommended one bold, decide later |
| **Approve** a proposed action | approve / change it / decide later, with the consequence of each |
| **Another round** — a review-cap waiver, or any "one more round" | as *choose*, plus its justification: what the leftover findings would break if left, and what the round costs in time, quota and the operator's attention (SKILL.md § The floor) |
| **Preference** — no fact settles it | options with impacts, labelled *your preference — no recommendation* |
| **Outside my authority** | options with impacts, labelled *no recommendation — outside my authority*, with why |
| **Alert** — time-critical | the fact now, bare; the options next |
| **Open question** — not defined yet | listed under *Open questions*, unnumbered, until it has options |
| **FYI after acting** — nothing to answer | one `Done:` line in the *Done alone* group: what was done, its class, why it was safe to do, the authority, how to undo it |

**FYI after acting** is allowed only for an action that is two-way, narrow, relied on by
nobody before the operator reviews it, and inside authority the operator already gave — an
answered decision, the task you were assigned, or a decide-alone class the caller's rules
define. Never for ⚠, never when others rely on it.
An action about to happen unless the operator stops it is **not** an FYI: it is an approve
ask, and it waits. When in doubt, ask.

**Why ask, and the class.** Every kind above but the FYI, the alert and the open question
carries *why ask* (SKILL.md § The floor): what would go wrong if you took your recommendation
alone. Fill it before you write the card. On a card it shares one **Why you, why now:** line
with *why now*, about 25 words at most for the two: the class, the reason, then what forces
it now, leaving out what it blocks (the Wait facet says that); a block keeps two lines. When the caller names classes of decision, pick
the one this ask belongs to at birth and open *why ask* with it; one that fits no class says
so in the caller's word for that. An ask whose *why ask* comes out empty — nothing goes wrong
if you take the recommendation — is decided alone when the FYI rule above allows, and shown
after; otherwise it is asked.

| Field | Values | Who can supply it |
|---|---|---|
| Class | one of the caller's class names, or none when the caller names none | the caller's rules; you pick at birth |
| Why ask | what would go wrong if you took your recommendation alone; with no recommendation, why the call is not yours | you |

## F — What does the operator need in hand? → the card's terms and its To act on part

| Field | Values | Who can supply it |
|---|---|---|
| Source | the document or session the decision comes from (a plan, a review, a run's record), and whether the operator has read it | you |
| Source label | the label the source gives the item a decision is raised from (a finding's F7), and its short name: the source's own title for it, or two to six plain words you write (`references/rendering.md` § Source labels) | you, from the source |
| Items | when the decision acts on several things: each one, and whether they need different answers (then a group, one card each) or one answer fits all (then one card) | you |
| Terms | each label, number, acronym or term of art the card would use that the operator has not used themselves, and the words each stands for | you, from the source |
| Operator actions | per option: what the operator must do to carry it out, or *answer only* | you |
| Inputs | per such option, what SKILL.md § The floor, what it takes to act, requires (its specifics: `references/rendering.md` § Card, To act on) | you; the caller, where it keeps the files |

Warm on the decision is not warm on its source's words: group A measures the first only. A
reader who answered the decision before this one may never have read the plan whose labels
its options would use.

## The Context — from the groups above

Every card and block carries a **Context:** section, shaped like the answer page's `context`
field (`references/rendering.md` § Context). Fill it before the Impact line, from groups A
and F, in plain words for the operator:

| Part | From | Who can supply it |
|---|---|---|
| Terms | group F: each label, number, acronym, count, named mode, setting, review, plan or document, or item the card uses, glossed in plain words (a count says what the things are) | you, from the source |
| Where you left it | group A: what the operator last saw or decided on this subject; for a decision whose subject they have never seen, where it came from, worded to stay true once they have (*raised when …*) | you; the caller's record of shown and seen |
| What you decide now | the choice, in the terms of where they left it | you |
| Lost context (a block only) | the facts a reader coming back cold needs: what was tried, what was answered before, where a list or number came from | you, from the source and the record |

A card's Context is the first three, in that order, in one or two sentences (about 30–60
words); it does not restate **What:**. A block's adds the lost context, as bullets. Write it
when the decision is raised, and store it with the card where the caller keeps one, so every
later showing — a re-show after a reset included — reads it instead of composing it again.

## The Impact line — from the groups above

Fill it last, from what the groups produced, in plain words for the operator. The line
carries Wait, Reach, Undo and Cost; Effect is filled per option. The facets and how each view
shows them are in `references/rendering.md` § Impact.

| Facet | From | Who can supply it |
|---|---|---|
| Effect | each option's own effect, never the decision's: what that option changes in the thing the work builds (code, data, users, deploys, downstream consumers), by its mechanism; written with the option (below), and not on the Impact line | you |
| Wait | group D: what waiting costs, what it blocks, what happens at a deadline; every effect on the process (a held review comment, a round, a blocked session) goes here and nowhere else | you; a collector for other sessions |
| Reach | group B's blast radius, named in the system: users, consumers, deploys, which repos, the public | you, from what the change touches |
| Undo | group B's reversibility, only where an option is one-way or costly: *⚠ undo: (a) none — why*, *⚠ undo: (b) a hotfix release, after the outage*; left off when every option is reversible at little cost | you — say how you know |
| Cost | build time, money, quota, per option; the operator's time where the option asks them to act; their attention only on a round ask | you; the caller's budget, when it keeps one |

**Whose system.** In a product repo the system is its code, its users, its deploys and the
consumers downstream. Where the change is to agent behaviour, as in a kit of skills, sessions
and the operator are that system's users, so they may stand in Reach.

**Each option's impact** is written with the option, from the same groups: its effect, said
by its mechanism (how it happens, who meets it and when, before and after), the reach of that
option alone, its undo when it is one-way or costly, and its cost; a facet that does not
apply is left out, and so is the undo of an option reversible at little cost. A card shows it
on an italic line under the option, a block in its table (`references/rendering.md`
§ Impact). Write these first: the closed views read the recommended option's effect off
them, and the Impact line's reach, undo and cost are drawn from them.

Write it when the decision is raised, and store it with the card where the caller keeps one,
so every later view reads it instead of composing it again.

## The cold read

The self-check, run on each card or block after it is written and before it goes out. Read
only the card, as someone who has seen nothing else, and for each option ask:

1. Can you say what it means and what happens if it is chosen, without opening anything?
2. Can you say how it happens — how a failure occurs, who meets it and when, and what is
   different after the fix — not only that it does?
3. Does its effect name what happens to the thing being built, not to the review or the
   process?
4. If it is one-way or costly to undo, does it carry `⚠ undo:`; if it carries one, is it?
5. If the option is the operator's to carry out, does the card meet SKILL.md § The floor,
   what it takes to act, from the card alone?

Then check every label, number or acronym on it against SKILL.md § The floor, item 1: defined
where it first appears — in its **Context:** — or replaced by its words; a source label
carries its short name on first mention. A card that fails is fixed before it is
raised, not after the operator asks.
