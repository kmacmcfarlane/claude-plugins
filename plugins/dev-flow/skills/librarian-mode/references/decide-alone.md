# Decided alone

Loaded from SKILL.md § Intake step 3, the decision channel (§ The cycle) and § Report, and
from `decisions.md`. What the librarian decides without asking is **recorded and shown**: a
`decided:` line on the item when it decides, a `Done:` line in the next Report. Every decision
it raises carries `why ask:` and a class. This file holds the line (which classes are decided
alone and which are raised), what makes a trade-off real, how the line moves, the triage of a
planner's questions, the record, the Report group and the class names.

## The line

The operator drew it (answers 111 (b) and 112 (b)): raise a decision when it is one-way, a
trust boundary, a real trade-off, a new or changed rule, an API name, wider scope, spend
outside a standing grant, or a high-impact finding left at a cap; decide the rest alone,
record it and show it. Each decision gets its class (§ Class names) when it arises, and the
class puts it on one side:

| Class | Side | Condition |
|---|---|---|
| `wording` | decided alone | a name something parses or stores is `api-name` |
| `minor-design` | decided alone | only while all four of its terms hold (§ Class names); touching a shared contract, doctrine or a ruling makes it `trade-off` or `rule-change` |
| `narrowing` | decided alone | the part left is filed as a linked follow-up first; the `Done:` line says "pull back <tag>" reverses it |
| `ruled-rule-case` | decided alone | the authority is `answer N`; narrowing or widening the ruled rule is `rule-change`, and an answer that states a policy in the operator's words is filed as a rule change they see land |
| `table-placement` | decided alone | exactly one row of the README's placement table (CLAUDE.md's Aim → home) settles it |
| `reply-reading` | decided alone | the reading is echoed; raised when it drives a one-way act, or one others rely on |
| `forwarding` | decided alone | to the repo that owns the work; with no live owner, raised as a `blocker` |
| `trade-off` | raised | after the sign test (§ What makes a trade-off real) |
| `wider-scope` | raised | — |
| `rule-change` | raised | including narrowing or widening a ruled rule, and moving a class across this line |
| `placement` | raised | — |
| `api-name` | raised | before it ships: plugin, skill, env var, stored field, parsed tag, settings key |
| `relay` | raised | as a batchable confirm (`ok N-M`) |
| `one-way` | raised | ⚠ when high impact, never batched |
| `trust` | raised | except a case a ruled permission covers |
| `spend` | raised | outside a standing grant |
| `cap` | raised | as the decision channel raises it (SKILL.md § The cycle) |
| `blocker` | raised | — |
| `unclassed` | raised | when in doubt, ask |

A class decided alone is decided alone only under the FYI rule (`operator-interaction:decisions`
skill): an action that is two-way, narrow, relied on by nobody before the operator reviews it,
and inside authority the operator already gave; never for ⚠, never when others rely on it. A
case that fails any of these is raised, under the class that names what failed. A question
whose `why ask:` cannot be filled is decided alone when the FYI rule allows; otherwise it is
asked.

*Evidence* (investigation 263c, decisions 1-101 by class): each class decided alone is one the
operator delegated in their own words ("you decide" on 9, 10 and 95) or where they took every
recommendation (wording 2 of 2, minor design 2 of 2). Each class raised is one where they
steered: 6 of 11 real trade-offs diverged from the recommendation, the options fit 4 of 11
placements, 3 of 4 trust calls diverged, and 93 reversed a recommended stored field. On
decisions 1-97 the line decides about 26 of 94 alone with a standing quota grant, about 15
without one.

## What makes a trade-off real

A trade-off is real when the options differ on an impact like these, and no rule, earlier
answer or class in § The line already settles which way to go:

- **Reversibility** — one option is hard to undo: a push others pull, publishing, deleting
  something.
- **Who else is affected** — other repos, peer sessions, the team, people who use the plugins.
- **Spend** — quota, money, wall time, or the operator's time and attention.
- **Trust and security** — what an agent can read, run, fetch or send, and who can approve
  what.
- **Behaviour the operator relies on** — a default, a rule agents follow, what the operator
  sees and when.
- **Contracts and stored data** — a file format, a store line, a CLI name, another plugin's
  interface, data that would need migrating.
- **Scope and precedent** — it adds or drops a capability, commits the repo to maintaining
  something, or sets a rule for later decisions.
- **Quality against speed** — thoroughness traded for time or cost where no rule sets a floor.

It is **not** a real trade-off when any option would do, when only taste differs and nothing
depends on it, when a rule already settles it, or when one option is both cheaper and safer.

The list is examples, not complete: anything else where the options' consequences really
differ, and a reasonable operator could weigh them differently, counts too. When in doubt,
ask.

**The sign test**, at birth: name the kind of impact the options differ on, and what would go
wrong if the librarian took its recommendation alone. When nothing would, the question is
`minor-design` (or `wording`) and is decided alone. A raised `trade-off` names the kind in its
`why ask:` (§ Raised). Because a decision whose options converge is not raised, the decisions
skill's line-only branch "or the options converge" rarely meets a raised decision.

## How the line moves

- **Promotion to a count line.** A class decided alone shows one `Done:` line per ruling until
  it is promoted. Promotion changes what the operator sees, so it is asked, never
  self-granted: a `decision N:` of class `rule-change`, its card carrying that class's
  `decided:` lines since the last promotion or narrowing as the spot-check sample. When the
  operator marks none of them for reversal and answers yes, the class shows from then as one
  count line in the done-alone group (`- **Done: <count> <class>** — *promoted by answer N ·
  the rulings are on the items · say so to see or undo any*`), and the `decided:` lines are
  still written, one per ruling.
- **Per-class narrowing.** An undo the operator asks for on a `Done:` line (§ The Report)
  narrows that class and no other: a promoted class goes back to one line per ruling, and
  the kind of case reversed is filed as a rule change to this table (its row's condition),
  which lands through the cycle and is shown like any change. Until it lands, cases of that
  kind are raised.
- **Widening** a class, moving it from raised to decided alone, is a raised `rule-change`.
  Silence never widens anything.

## A planner's questions

Under this binding, a blocking open question a planner (or any sub-agent) returns passes
through § The line before it reaches the operator. A decided-alone class is decided: a
`decided:` line with authority `class <class>`, and the ruling goes back to the plan the way
an answer would. A raised class becomes a `decision N:` with its `why ask:`. A non-blocking
question stays in the series.

## Trivial documentation

Trivial documentation just gets done: it is work, not a decision, filed and run through the
cycle with no ask (SKILL.md § Intake step 5), and the words it picks are `wording`. Which docs
take a self-review is the `dev-cycle` skill's Step 2 rule 5 (the review waiver) until the
wider reading of answer 113 (b) is written here.

## The record: `decided:`

One line in the item body when the librarian decides something alone, appended with Bash
like every record line — one physical line, never wrapped, at the start of the line:

```
decided: <UTC time> <class> — <what was decided, and why it was safe to decide alone> · authority: <authority> · reopen: <how to undo it>
```

- **UTC time** in the form `raised:` uses, `2026-09-30T14:05Z`.
- **class** — one name from § Class names, as written there.
- **what, and why it was safe** — plain words: what was decided, and why it was safe to
  decide alone (two-way, narrow, nobody relies on it before the operator sees it); the
  `Done:` line's safety clause is read from here. Items by plain name, the tag trailing; no
  bare id. It never contains ` · authority: ` or ` · reopen: `, the separators the regex
  splits on; reword instead.
- **authority** — what let the librarian decide it, one of:
  - `task` — the request filed as this item;
  - `answer N` — an answered decision whose case this is;
  - `class <class>` — a class § The line marks decided alone.

  These are the FYI rule's three authorities, and no other.
- **reopen** — how it is undone: `revert <short sha>`, `one edit to <what>`, or the reply that
  pulls it back.

It matches neither `^decision [0-9]` nor `^answer [0-9]`, so `wi needs-input` and the decision
counter do not read it. It is split by
`^decided: (\S+) ([a-z-]+) — (.*?) · authority: (.*?) · reopen: (.*)$`. The line is written
when the librarian acts, not at Report time; one line per ruling.

## The Report: the done-alone group

Every `decided:` line written since the last Report gets one `Done:` line in a **Done alone**
group, after the four lines per landed change and before the push outcome:

```
**Done alone** — *N since my last report · say so in your own words to undo or reopen any*
- **Done: <what was done>** — *<class> · <why it was safe: two-way, narrow> · <authority, in words> · undo: <how>*
```

- Rendered from the `decided:` lines (`git -C "$MAIN" log --since=<last Report>` over the
  store, or the item bodies), never from memory; one line per ruling, never merged.
- No group when nothing was decided alone; a single line may drop the heading.
- With the `operator-interaction:decisions` skill loaded, the line is that skill's FYI line
  (`decisions.md` § The Report places the group).
- An operator reply against a line is read as any reply: an undo is echoed, done through the
  cycle like any change, and noted on the item with the operator's words; a reopen is raised
  as a new `decision N:` whose `why now:` names the `decided:` line it reopens.

## Raised: `why ask:` and the class

Every decision the librarian raises carries, in its stored card, directly under `why now:`:

```
  why ask: <class> — <what would go wrong if the librarian took its recommendation alone>
```

With no recommendation, the reason says why the call is not the librarian's. A `trade-off`
opens the reason with the kind of impact the options differ on (§ What makes a trade-off
real): `why ask: trade-off — spend: <what would go wrong …>`. It is one
physical line, indented like every card line (`decisions.md` § What the store records), and
split by `^\s+why ask: ([a-z-]+) — (.*)$`. The class is picked at birth, when the decision is
raised, never assigned later. A card stored before `why ask:` existed is backfilled on its
next re-show (`decisions.md` § What the store records) in one fixed form, which keeps the
grammar:

```
  why ask: unclassed — not recorded (raised before why ask)
```

Without the decisions skill, the headline stays as SKILL.md § Report gives it, and the
`why ask:` line still goes under it.

## Class names

Each decision, raised or decided alone, gets one of these names. The clause after each only
tells the classes apart; § The line says which side each class is on. The
spellings are provisional until the operator confirms them; they are written as spelled
meanwhile, and if they are renamed, the `decided:` and `why ask:` lines written in between are
migrated to the new spellings.

| Class | What it names |
|---|---|
| `wording` | the words of a text, a message or a label, not a name something parses |
| `minor-design` | minor design (inside one item, reversible by an edit, no shared contract, the alternatives the status quo or strictly worse) |
| `trade-off` | a design choice with a real trade-off (§ What makes a trade-off real) |
| `narrowing` | leaving part of the work to a filed, linked follow-up |
| `wider-scope` | taking on more than the request or the Scope covers |
| `ruled-rule-case` | a new case of a rule the operator ruled, citing `answer N` |
| `rule-change` | a new standing rule, or a change to one |
| `table-placement` | where a thing lives, when exactly one row of the placement table settles it |
| `placement` | where a thing lives, when the placement table does not settle it |
| `api-name` | a name something parses or stores: a plugin, skill, env var, stored field or parsed tag |
| `reply-reading` | the reading of an unclear reply |
| `forwarding` | sending work that belongs to another repo to its owner |
| `relay` | a rule or answer relayed from another session or repo |
| `one-way` | an action that cannot be taken back, or only at real cost |
| `trust` | a trust boundary: credentials, permissions, what may reach whom |
| `spend` | quota or money outside a standing grant |
| `cap` | a review cap reached, and whether to spend another round |
| `blocker` | an item that cannot go on without the operator |
| `unclassed` | none of the above; the case the class table does not cover yet |

A class name is a parsed tag: renaming one is a raised `api-name` decision.
