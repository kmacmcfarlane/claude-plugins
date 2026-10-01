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
| `table-placement` | decided alone | exactly one row of the repo's placement table settles it (in this marketplace, CLAUDE.md's Aim → home); a repo with no placement table has no `table-placement`, and its placements are `placement` |
| `reply-reading` | decided alone | the reading is echoed; raised when it drives a one-way act, or one others rely on |
| `forwarding` | decided alone | once forwarding with watched custody lands (item 3460): to the repo that owns the work, and with no live owner, raised as a `blocker`. Until then SKILL.md § Critical governs: a request outside Scope is declined and routed back to the operator |
| `trade-off` | raised | after the sign test (§ What makes a trade-off real) |
| `wider-scope` | raised | — |
| `rule-change` | raised | including narrowing or widening a ruled rule, and moving a class across this line; except the narrowing an operator's undo asks for (§ How the line moves) |
| `placement` | raised | — |
| `api-name` | raised | before it ships: plugin, skill, env var, stored field, parsed tag, settings key |
| `relay` | raised | as a batchable confirm (`ok N-M`) |
| `one-way` | raised | ⚠ when high impact, never batched |
| `trust` | raised | except a case a ruled permission covers |
| `spend` | raised | outside a standing grant |
| `cap` | raised | with a high left, or a build cap the round budget does not cover (SKILL.md § The cycle); a plan's cap with no high left (stopped and carried) and a build's one self-granted round are decided alone, authority `answer 114`, their `if left:` and `round costs:` in the `decided:` line's what. Both are two-way: a stop's reopen is the round the operator grants on reading it; a round's is "say stop: the round ends and its commits do not land" |
| `blocker` | raised | — |
| `unclassed` | raised | when in doubt, ask |

A class decided alone is decided alone only under the FYI rule (`operator-interaction:decisions`
skill): an action that is two-way, narrow, relied on by nobody before the operator reviews it,
and inside authority the operator already gave; never for ⚠, never when others rely on it. A
case that fails any of these is raised, under the class that names what failed. A question
whose `why ask:` cannot be filled is decided alone when the FYI rule allows; otherwise it is
asked.

*Evidence* (investigation 263c, decisions 1-101 classed by subject; 8dee's check on 1-97).
The decided-alone side rests on the operator's own words ("reversable, low impact,
high-probability decisions you can just run with and be sure I see", 2026-09-22; "trivial
documentation … just do it"; "you decide" on the wording decisions 9 and 95) and on a thin
record: wording and minor design took the recommendation 2 of 2 each. Scope changes took it 4
of 5, but 34 was a narrowing the operator kept in and 94 was redirected, which is why a
narrowing says how to pull it back. The raised side is where they steered: 6 of 11 real
trade-offs diverged from the recommendation, the options did not fit 7 of 11 placements, 3 of
4 trust calls diverged, and 93 reversed a recommended stored field. Applied to decisions 1-97,
the line decides about 26 of 94 alone with a standing quota grant (about 15 without one); on 4
of those 26 (53, 62, 34 and 94, all two-way), the operator's answer differed from what the line
would have done.

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
wrong if the librarian took its recommendation alone. When nothing would, it is not a
trade-off: it is decided alone under the class whose terms it meets (`wording`, or
`minor-design` only while its four terms hold), and otherwise keeps the raised class that
fits it. Every raised card names the kind in its `why ask:` (§ Raised). Because a decision whose options converge is not raised, the decisions
skill's line-only branch "or the options converge" rarely meets a raised decision.

## How the line moves

- **Promotion to a count line.** A class decided alone shows one `Done:` line per ruling until
  it is promoted. Promotion changes what the operator sees, so it is asked, never
  self-granted. The librarian proposes it when a class has 10 `decided:` lines since its last
  promotion ask with no undo or reopen among them: a `decision N:` of class `rule-change`, its
  card carrying those lines as the spot-check sample. When the
  operator marks none of them for reversal and answers yes, the class shows from then as one
  count line in the done-alone group (`- **Done: <count> <class>** — *promoted by answer N ·
  the rulings are on the items · say so to see or undo any*`), and the `decided:` lines are
  still written, one per ruling.
- **Per-class narrowing.** An undo the operator asks for on a `Done:` line (§ The Report)
  narrows that class and no other: a promoted class goes back to one line per ruling, and
  the kind of case reversed is written into that class's row (its condition). The operator's
  undo is the authority: the edit is filed and lands through the cycle with no new ask, and is
  shown in the next Report as a landed change. Until it lands, cases of that kind are
  raised.
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
cycle with no ask (SKILL.md § Intake step 5), and the words it picks are `wording`.

What counts (answer 113 (b), 2026-09-30): prose-only docs, which the `dev-cycle` skill's
Step 2 rule 5 already self-reviews (the review waiver), **plus skill wording that changes no
rule**: a typo, a broken link or path, a sentence restating an existing rule. Both take the
waiver's `review: self` instead of a reviewer; every other leg of that waiver still holds
(the `dev-cycle` skill's `references/model-routing.md` § Review waiver: `full` mode, no Model
floor). Everything else keeps today's path: a fresh reviewer. The wider reading covers this
librarian's own Ground only. A write into another repo, if one is ever allowed, takes the
prose-only test.

**Skill wording** is the body of a `SKILL.md` and its `references/`. The frontmatter
(`name`, `description`: what makes a skill load), agent files, hooks, scripts, tests,
config, `.claude-plugin/`, CLAUDE.md and templates are never skill wording: they keep a
reviewer whatever the edit.

**The test: the same agent, both texts.** Read the old line and the new line as the agent
that loads the skill would. A line changes no rule only when an agent following the new text
does, writes, asks, skips and stops exactly as one following the old would, in every case the
text covers, not just the usual one. A line fails when it adds, removes or alters any of:

- a must, should, may, never, always, only, unless, except or when;
- a number, threshold, cap, default or order of steps;
- a name, field, tag or line shape an agent writes or parses;
- a command, path, host, permission or config value an agent uses;
- who does a step, or which file or section is authoritative;
- an example (examples teach the rule agents copy).

The three kinds, each held to the test:

- **A typo:** the misspelled or ungrammatical word is fixed, and no other word moves. A typo
  inside a name, command, path or value is that thing, not a typo: a reviewer.
- **A broken link or path:** a pointer that leads nowhere is fixed to the file or section the
  text already meant, and it exists. Repointing at different content, or changing a path an
  agent writes to or runs, is a rule.
- **A restatement:** the sentence restates a rule already in force, cites where it lives, and
  keeps every scope-bearing noun and restriction verbatim ("the librarian may self-review"
  never becomes "a session may"). A restatement that narrows, widens or reorders the rule
  is the rule changed.

One failing line fails the change. **When in doubt, today's path:** a fresh reviewer. Doubt
includes not being able to name the kind, or a line the test reads two ways.

**The `review: self` line says why it changes no rule** — the kind, the file, and the rule
left untouched or the rule restated with where it lives: `review: self at <sha> — rule-free
skill wording: typo in <file>; no instruction moves` or `— rule-free skill wording:
restates <rule> (<file> § <section>) verbatim in <file>`. A clause that cannot be written
that way is the doubt above. A later fix round is tested afresh on the cumulative diff
(the waiver's own rule).

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
group, after the four lines per landed change and before the push outcome — except a class
the operator promoted by `answer N` (§ How the line moves), whose rulings show as one count
line:

```
**Done alone** — *N since my last report · say so in your own words to undo or reopen any*
- **Done: <what was done>** — *<class> · <why it was safe: two-way, narrow> · <authority, in words> · undo: <how>*
```

- Rendered from the `decided:` lines (`git -C "$MAIN" log --since=<last Report>` over the
  store, or the item bodies), never from memory; one line per ruling, never merged, bar a
  promoted class's count line. Any class not promoted by an answer keeps one line per
  ruling.
- No group when nothing was decided alone; a single line may drop the heading.
- With the `operator-interaction:decisions` skill loaded, the line is that skill's FYI line
  (`decisions.md` § The Report places the group); a promoted class's count line is this
  binding's own, beside those lines.
- An operator reply against a line is read as any reply: an undo is echoed, done through the
  cycle like any change, and noted on the item with the operator's words; a reopen is raised
  as a new `decision N:` whose `why now:` names the `decided:` line it reopens.

## Raised: `why ask:` and the class

Every decision the librarian raises carries, in its stored card, directly under `why now:`:

```
  why ask: <class> — <what would go wrong if the librarian took its recommendation alone>
```

With no recommendation, the reason says why the call is not the librarian's. Every raised
card names the kind of impact the options differ on (§ What makes a trade-off real). Where
the class names its own kind, the class stands for it: `one-way` (reversibility), `trust`
(trust and security), `spend` (spend), `api-name` (contracts and stored data), `wider-scope`
and `rule-change` (scope and precedent). Every other class — `trade-off`, `placement`,
`relay`, `cap`, `blocker`, `unclassed` — opens the reason with the kind:
`why ask: trade-off — spend: <what would go wrong …>`. It is one
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
