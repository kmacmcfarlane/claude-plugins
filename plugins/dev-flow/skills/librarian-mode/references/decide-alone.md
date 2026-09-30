# Decided alone

Loaded from SKILL.md § Intake step 3 and § Report, and from `decisions.md`. What the
librarian decides without asking is **recorded and shown**: a `decided:` line on the item when
it decides, a `Done:` line in the next Report. Every decision it raises carries `why ask:`
and a class. This file holds the record, the Report group and the class names.

**Not here yet:** which classes are decided alone and which are raised, promotion to a count
line, per-class narrowing, and the trivial-docs test. Until they land here, the line stays
where SKILL.md § Intake step 3 draws it: an obvious best way is decided; a real trade-off is
asked. Nothing below moves a class across that line.

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
  - `class <class>` — a class this file marks decided alone (none yet).

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

With no recommendation, the reason says why the call is not the librarian's. It is one
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
tells the classes apart; it says nothing about which side of the line a class is on. The
spellings are provisional until the operator confirms them; nothing writes a class tag to a
store before then.

**Until the operator confirms the spellings,** this interim rule stands in for the store
lines above:

- no `decided:` line is written, so there is no **Done alone** group;
- `why ask:` is shown on every raised card, its class named in words, but not stored;
- no backfill of `why ask:` is written to an older card.

Once they are confirmed, the lines above apply as written.

| Class | What it names |
|---|---|
| `wording` | the words of a text, a message or a label, not a name something parses |
| `minor-design` | minor design (inside one item, reversible by an edit, no shared contract, the alternatives the status quo or strictly worse) |
| `trade-off` | a design choice with a real trade-off; what makes one real is the class table's test, not written here yet |
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
