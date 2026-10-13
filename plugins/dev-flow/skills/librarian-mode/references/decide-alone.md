# Decided alone

Loaded from SKILL.md § Intake step 3, the decision channel (§ The cycle), § Report and
§ Critical, from `decisions.md`, and from the `dev-cycle` skill's `references/model-routing.md`
§ Review waiver. What the librarian decides without asking is **recorded and shown**: a
`decided:` line on the item when it decides, a `Done:` line in the next Report. Every decision
it raises carries `why ask:` opening with its reason. This file holds the line (the reasons
that raise a decision, and the kinds a decision alone is recorded under), what makes a
trade-off real, how the line moves, the triage of a planner's questions, what counts as
trivial documentation and when it is self-reviewed (§ Trivial documentation), the record, the
Report group, and the tag names with their retired spellings.

## The line

The operator drew it (answers 111 (b) and 112 (b)), and answer 134 (a) gave it its shape:
two words, one per question. A raised decision's tag says **why it is the operator's**: a
**reason**. A decision alone's tag says **what changed**: a **kind**. Check the reasons in
the order below; the first that applies, with no answer or standing grant covering the case,
raises the decision and is its tag, and any others may be named in its text. When none
applies, the decision is decided alone under the kind it meets, recorded and shown. The side
is worked out by checking the reasons, never looked up from the tag. Each decision gets its
tag when it arises, one tag per line.

A reason applies only when something could go wrong along it if the librarian took its
recommendation alone (the sign test, § What makes a trade-off real).

### The reasons: why it is yours (raised)

| # | Reason | Applies when | Condition |
|---|---|---|---|
| 1 | `blocker` | the work cannot go on without something only the operator can do or give: a physical act, a privilege, a fact | also work routed to another repo with no live owner (`scope`, below) |
| 2 | `one-way` | it cannot be taken back, or only at real cost: delete, publish, a push others pull, a purchase, a message sent | ⚠ when also high impact, never batched |
| 3 | `trust` | it changes what an agent, a person or a system may read, run, fetch, send or approve: credentials, permissions, exposure, data reaching a third party | a case a ruled permission covers is decided alone, reason word `trust`, authority `answer N` |
| 4 | `contract` | it sets or changes a name, format, interface or behaviour that something outside this work relies on: an API field or a function's default, a parsed tag, an env var, a schema, a URL, an entity id, a host name, another plugin's interface, a webhook's timing, stored data that would need migrating | before it ships: a plugin, skill, env var, stored field, parsed tag or settings key name. A dependency inside the same item is not one |
| 5 | `reach` | it affects someone or something beyond this work before the operator reviews it: other repos or sessions, users, people in the house, a service in use (the operator's own included), a change that deploys when pushed | — |
| 6 | `spend` | quota, money, wall time, a shared machine or the operator's attention beyond a standing grant, including another round past a cap that no answer grants, and thoroughness traded for time | see § Spend and caps below |
| 7 | `precedent` | it sets or changes what happens from now on: a standing rule or default; narrowing or widening a ruled rule; moving a kind or reason across this line; a capability taken on or dropped; work beyond the request; where something lives, unless one standing rule settles it; what the operator sees and when; a rule or answer relayed from another session | except the narrowing an operator's undo asks for (§ How the line moves). A relay is batchable (§ Raised) |
| 8 | `your-call` | the call is the operator's even with nothing else at stake: it would reverse or narrow their own words, their answers conflict, or it is a product or policy call only they can make | — |
| 9 | `trade-off` | the open catch-all: the options' consequences really differ on anything not named above, and a reasonable operator could weigh them differently | after the sign test; not when any option would do, when only taste differs and nothing depends on it, when a rule settles it, or when one option is both cheaper and safer |
| — | `unclassed` | the backfill form (§ Raised), and doubt (below); no other case | when in doubt, ask |

**Doubt raises.** Two cases are kept apart:

- *Cannot be filled.* Each reason has been checked, and for none of them would anything go
  wrong. The decision is decided alone when the FYI rule (below) allows; otherwise it is
  asked.
- *In doubt.* The librarian cannot tell whether a reason applies. The decision is raised,
  tagged `unclassed`, and its text names the reason in doubt:
  `why ask: unclassed — doubt on reach: …`.

Doubt decides the side, not only the tag.

### The kinds: what changed (decided alone)

These apply when no reason applies and the FYI rule's four legs hold.

| Kind | What changed | Condition |
|---|---|---|
| `words` | text people read: docs, messages, labels, comments | a name, format or behaviour something relies on is `contract` |
| `design` | how something works inside the work: code, structure, a config value, a dependency within policy | only while all four of its terms hold (§ Class names); failing one makes it `contract`, `precedent` or `trade-off` |
| `place` | where something lives, when one standing rule settles it (in this marketplace, a row of CLAUDE.md's Aim → home or a CLAUDE.md convention, such as Skill location) | a repo with no standing placement rule has no `place`: its placements are `precedent` |
| `scope` | what work is done: a part split to a linked follow-up, or work routed to the repo that owns it | a split: the part left is filed as a linked follow-up first, and the `Done:` line says "pull back <tag>" reverses it. Routing: once forwarding with watched custody lands (item 3460), to the repo that owns the work, and with no live owner, raised as a `blocker`. Until then SKILL.md § Critical governs: a request outside Scope is declined and routed back to the operator |
| `reading` | what an unclear reply or instruction means | the reading is echoed; one that drives a one-way act, or one others rely on, meets reasons 2-5 and is raised |
| `cap` | what was done at a limit the operator set, under the answer that lets it be done alone | see § Spend and caps below |
| a reason word | a case that would be raised under that reason, decided alone because an answer or standing grant covers it: `trust` under a ruled permission, `spend` inside a grant | the authority is `answer N`. Narrowing or widening the ruled rule is `precedent`. An answer that states a policy in the operator's words is work, not a decision: it is filed and lands with no new ask, shown in the Report as a landed change |

### Spend and caps

- **Raised, `spend`:** outside a standing grant. An item's spend budget is its grant (answer
  145): a round inside it is not outside one. Raised: a budget reached while a fresh weekly
  reading is at or above 50% used, or with no fresh reading (the increase ask), a plan's
  `Estimated cost:` over its build's default, and a round past the fourth review that the
  guard stops (a hold, no weekly reading, below the reserve) — the `dev-cycle` skill's
  `references/bindings.md` §§ Decisions, Spend budget. Also raised as `spend`: a cap at the
  convergence stop or the fallback count, with a high left, leftovers that are not
  exact-fix, or exact-fix leftovers after a finish round in a row (the `dev-cycle` skill's
  `references/bindings.md` § Decisions, What a cap ends in), with its `if left:` and
  `round costs:`. The reason text names what stopped the work: a convergence stop, the
  fallback, or the budget reached. A convergence stop, or the fallback, is named as that
  even when the budget was passed under the waiver (answer 176).
- **Decided alone, reason word `spend`:** a budget reached while a fresh weekly reading is
  below 50% used — noted in the Report as a Done-alone line with the spend against the
  budget, the rounds continuing (authority `answer 176`; that file's § Spend budget, While
  the quota is plentiful).
- **Decided alone, kind `cap`:** a plan's stop and carry (authority `answer 114`) and a
  finish round of exact-fix leftovers (authority `answer 145`), their `if left:` and
  `round costs:` in the `decided:` line's what. Both are two-way: a stop's reopen is the
  round the operator grants on reading it; a round's is "say stop: the round ends and its
  commits do not land".

### The FYI rule

A kind is decided alone only under the FYI rule (`operator-interaction:decisions` skill): an
action that is two-way, narrow, relied on by nobody before the operator reviews it, and
inside authority the operator already gave; never for ⚠, never when others rely on it. A case
that fails any of these is raised, under the reason that names what failed.

*Evidence* (investigation 263c, decisions 1-101 classed by subject; 8dee's check on 1-97).
The decided-alone side rests on the operator's own words ("reversable, low impact,
high-probability decisions you can just run with and be sure I see", 2026-09-22; "trivial
documentation … just do it"; "you decide" on the wording decisions 9 and 95) and on a thin
record: changes to words and to design inside the work took the recommendation 2 of 2 each.
Scope changes took it 4 of 5, but 34 was a split the operator kept in and 94 was
redirected, which is why a split says how to pull it back. The raised side is where they
steered: 6 of 11 real trade-offs diverged from the recommendation, the options did not fit 7
of 11 placements, 3 of 4 trust calls diverged, and 93 reversed a recommended stored field.
Applied to decisions 1-97, the line as it stood before answer 134 decided about 26 of 94
alone with a standing quota grant (about 15 without one); on 4 of those 26 (53, 62, 34 and
94, all two-way), the operator's answer differed from what the line would have done. The
two-word shape narrows the decided-alone side further (live changes, behaviour others rely
on, and the operator's own words now raise). A few cases move the other way, from raised to
decided alone: a placement a CLAUDE.md convention settles (such as Skill location) is now
`place`, where only a row of Aim → home was before; and a config value or a dependency bump
inside policy is now `design` while its four terms hold.

## What makes a trade-off real

A trade-off is real when the options differ on an impact, and no rule, earlier answer or kind
in § The line already settles which way to go. The impacts the operator named (reply 112) are
reasons 2-7, and a real trade-off on one of them takes that reason as its tag:

- **Reversibility** — `one-way`: a push others pull, publishing, deleting something.
- **Trust and security** — `trust`: what an agent can read, run, fetch or send, and who can
  approve what.
- **Contracts and stored data** — `contract`: a file format, a store line, a CLI name,
  another plugin's interface, data that would need migrating, behaviour something outside
  this work relies on.
- **Who else is affected** — `reach`: other repos, peer sessions, the team, people who use
  the plugins.
- **Spend, and quality against speed** — `spend`: quota, money, wall time, or the operator's
  time and attention; thoroughness traded for time or cost where no rule sets a floor.
- **Scope and precedent, and behaviour the operator relies on** — `precedent`: it adds or
  drops a capability, commits the repo to maintaining something, sets a rule for later
  decisions, or changes a default, a rule agents follow, or what the operator sees and when.

It is **not** a real trade-off when any option would do, when only taste differs and nothing
depends on it, when a rule already settles it, or when one option is both cheaper and safer.

The list is examples, not complete: anything else where the options' consequences really
differ, and a reasonable operator could weigh them differently, counts too, and takes
`trade-off` (reason 9). When in doubt, ask.

**The sign test**, at birth: name the reason the options differ on, and what would go wrong
if the librarian took its recommendation alone. When nothing would, it is not a trade-off: it
is decided alone under the kind whose terms it meets (`words`, or `design` only while its
four terms hold), and otherwise keeps the reason that fits it. Every raised card's `why ask:`
opens with its reason (§ Raised). Because a decision whose options converge is not raised,
the decisions skill's line-only branch "or the options converge" rarely meets a raised
decision.

## How the line moves

- **Promotion to a count line.** A kind or reason word decided alone shows one `Done:` line
  per ruling until it is promoted. Promotion changes what the operator sees, so it is asked,
  never self-granted. Promotion keys on the tag, and for a reason word decided alone on the
  tag plus the answer that allowed it (`spend` under `answer 176` counts apart from `spend`
  under another answer). The librarian proposes it when a key has 10 `decided:` lines since
  its last promotion ask with no undo or reopen among them: a `decision N:` tagged
  `precedent`, its card carrying those lines as the spot-check sample. When the operator
  marks none of them for reversal and answers yes, the key shows from then as one count line
  in the done-alone group (`- **Done: <count> <tag>** — *promoted by answer N · the rulings
  are on the items · say so to see or undo any*`), and the `decided:` lines are still
  written, one per ruling.
- **Per-key narrowing.** An undo the operator asks for on a `Done:` line (§ The Report)
  narrows that key and no other: a promoted key goes back to one line per ruling, and the
  kind of case reversed is written into that kind's row (its condition), or the reason
  word's. The operator's undo is the authority: the edit is filed and lands through the
  cycle with no new ask, and is shown in the next Report as a landed change. Until it lands,
  cases of that kind are raised.
- **Widening** a kind, moving a case from raised to decided alone, is a raised `precedent`.
  Silence never widens anything.

## A planner's questions

Under this binding, a blocking open question a planner (or any sub-agent) returns passes
through § The line before it reaches the operator. One no reason applies to is decided: a
`decided:` line under its kind with authority `class <kind>`, and the ruling goes back to
the plan the way an answer would. One a reason applies to, or one in doubt, becomes a
`decision N:` with its `why ask:`. A non-blocking question stays in the series.

## Trivial documentation

Trivial documentation just gets done: it is work, not a decision, filed and run through the
cycle with no ask (SKILL.md § Intake step 5), and the words it picks are of the kind `words`.

What counts (answer 113 (b), 2026-09-30): prose-only docs, which the `dev-cycle` skill's
Step 2 rule 5 already self-reviews (the review waiver), **plus skill wording that changes no
rule**: a typo, a broken link or path, a sentence restating an existing rule. Both take the
waiver's `review: self` instead of a reviewer; every other leg of that waiver still holds
(the `dev-cycle` skill's `references/model-routing.md` § Review waiver: `full` mode, no Model
floor). Everything else keeps today's path: a fresh reviewer. The wider reading covers this
librarian's own Ground only. A write into another repo, if one is ever allowed, takes the
prose-only test.

**Skill wording** is the body of a `SKILL.md` and its `references/`. Never skill wording,
whatever the edit, so they keep a reviewer:

- the frontmatter (`name`, `description`: what makes a skill load), agent files, hooks,
  scripts, tests, config, `.claude-plugin/` and CLAUDE.md;
- templates: an `assets/` file, and any `references/` file pasted into a dispatch brief or
  written to a store (the `dev-cycle` skill's `references/agent-brief.md` and
  `references/review-brief.md` among them);
- the self-review gate itself: this section, the `dev-cycle` skill's Step 2 rule 5, the
  `dev-cycle` skill's `references/model-routing.md` § Review waiver, and the review
  machinery: the `dev-cycle` skill's `references/review-brief.md`, the `dev-cycle` skill's
  `references/review-checklist.md` and the `dev-cycle` skill's `references/fix-loop.md`.

**The test: the same agent, both texts.** Read the old line and the new line as the agent
that loads the skill would. A line changes no rule only when an agent following the new text
does, writes, asks, skips and stops exactly as one following the old would, in every case the
text covers, not just the usual one. The list below is a floor, not a definition: a change
it does not name can still change a rule. It is judged against the rule in force. Words a
restatement copies verbatim from the home it cites are not added; any word that differs is.
A line fails when it adds, removes or alters any of:

- a condition or modal: must, should, may, never, always, only, if, when, unless, except,
  not, no, none; a quantifier (every, each, any, all); a sequence word (before, after,
  until, first, then); an and or or joining conditions;
- a number, threshold, cap, default or order of steps;
- a name, field, tag or line shape an agent writes or parses, and a section heading that
  other files cite (a name, never a typo);
- a command, host, permission or config value an agent uses, and any path an agent reads
  data from, writes to, runs or passes to a tool;
- who does a step, or which file or section is authoritative;
- an example (examples teach the rule agents copy).

"Run every Check after each fix round, if the item touches code" reworded to "Run the Checks
after the fix round" drops a quantifier and a condition: it fails.

The three kinds, each held to the test:

- **A typo:** the misspelled or ungrammatical word is fixed, and no other word moves. A typo
  inside a name, heading, command, path or value is that thing, not a typo: a reviewer.
- **A broken link:** the only path this kind may fix is a `file` or `§ section` pointer the
  agent reads for instructions. One that leads nowhere is fixed to the file or section the
  text already meant, and it exists. Repointing at different content is a rule, and so is
  any path in the list above.
- **A restatement:** a sentence outside the rule's home that restates a rule already in
  force, cites the home, and keeps every scope-bearing noun and restriction verbatim ("the
  librarian may self-review" never becomes "a session may"). A restatement that narrows,
  widens or reorders the rule is the rule changed. Any edit to the sentence that states the
  rule in its home is never rule-free and gets a reviewer, unless it is a pure typo under
  the typo kind.

One failing line fails the change. **When in doubt, today's path:** a fresh reviewer. Doubt
includes not being able to name the kind, or a line the test reads two ways.

**The `review: self` line says why it changes no rule**: the kind, the file, and the rule
left untouched, the target the link already meant, or the rule restated with its home:

- `— rule-free skill wording: typo in <file>; no instruction moves`
- `— rule-free skill wording: broken link in <file> to <target>, the section it already
  meant`
- `— rule-free skill wording: restates <rule> (<file> § <section>) verbatim in <file>`

A change with several kinds lists one clause per kind, separated by `;`. A clause that
cannot be written that way is the doubt above. A later fix round is tested afresh on the
cumulative diff (the waiver's own rule).

## The record: `decided:`

One line in the item body when the librarian decides something alone, appended with Bash
like every record line — one physical line, never wrapped, at the start of the line:

```
decided: <UTC time> <tag> — <what was decided, and why it was safe to decide alone> · authority: <authority> · reopen: <how to undo it>
```

- **UTC time** in the form `raised:` uses, `2026-09-30T14:05Z`.
- **tag** — a kind, or the reason word an answer or standing grant covers, from § Class
  names, as written there.
- **what, and why it was safe** — plain words: what was decided, and why it was safe to
  decide alone (two-way, narrow, nobody relies on it before the operator sees it); the
  `Done:` line's safety clause is read from here. Items by plain name, the tag trailing; no
  bare id. It never contains ` · authority: ` or ` · reopen: `, the separators the regex
  splits on; reword instead.
- **authority** — what let the librarian decide it, one of:
  - `task` — the request filed as this item;
  - `answer N` — an answered decision whose case this is;
  - `class <kind>` — a kind § The line lets be decided alone once no reason applies.

  These are the FYI rule's three authorities, and no other.
- **reopen** — how it is undone: `revert <short sha>`, `one edit to <what>`, or the reply that
  pulls it back.

It matches neither `^decision [0-9]` nor `^answer [0-9]`, so `wi needs-input` and the decision
counter do not read it. It is split by
`^decided: (\S+) ([a-z-]+) — (.*?) · authority: (.*?) · reopen: (.*)$`. The line is written
when the librarian acts, not at Report time; one line per ruling.

## The Report: the done-alone group

Every `decided:` line written since the last Report gets one `Done:` line in a **Done alone**
group, after the four lines per landed change and before the push outcome — except a key
the operator promoted by `answer N` (§ How the line moves), whose rulings show as one count
line:

```
**Done alone** — *N since my last report · say so in your own words to undo or reopen any*
- **Done: <what was done>** — *<tag> · <why it was safe: two-way, narrow> · <authority, in words> · undo: <how>*
```

- Rendered from the `decided:` lines (`git -C "$MAIN" log --since=<last Report>` over the
  store, or the item bodies), never from memory; one line per ruling, never merged, bar a
  promoted key's count line. Any key not promoted by an answer keeps one line per ruling.
- No group when nothing was decided alone; a single line may drop the heading.
- With the `operator-interaction:decisions` skill loaded, the line is that skill's FYI line
  (`decisions.md` § The Report places the group); a promoted key's count line is this
  binding's own, beside those lines.
- An operator reply against a line is read as any reply: an undo is echoed, done through the
  cycle like any change, and noted on the item with the operator's words; a reopen is raised
  as a new `decision N:` whose `why now:` names the `decided:` line it reopens.

## Raised: `why ask:` and the reason

Every decision the librarian raises carries, in its stored card, directly under `why now:`:

```
  why ask: <reason> — <what would go wrong if the librarian took its recommendation alone>
```

With no recommendation, the text says why the call is not the librarian's. The reason is the
impact the options differ on (§ What makes a trade-off real), so the card carries one word:
`why ask: spend — another round past the cap …`. When several reasons apply, the first in
§ The line's order is the tag, and the others may be named in the text
(`why ask: one-way — and reach: …`). A `trade-off` names in plain words what its options
differ on, and its text never opens with a single word and a colon (that shape is retired:
§ Retired spellings). It is one physical line, indented like every card line (`decisions.md`
§ What the store records), and split by `^\s+why ask: ([a-z-]+) — (.*)$`. The reason is
picked at birth, when the decision is raised, never assigned later.

**A relay.** A rule or answer relayed from another session or repo takes the reason that fits
it, and its text opens with the marker `relayed from <repo>: `
(`why ask: precedent — relayed from claude-sandbox: …`). It is offered as a batchable
confirm (`ok N-M`) only when its tag is `precedent` and the card is not ⚠; a relay under any
other reason is a card like any other. Batching reads the marker and the tag together.

A card stored before `why ask:` existed is backfilled on its next re-show (`decisions.md`
§ What the store records) in one fixed form, which keeps the grammar:

```
  why ask: unclassed — not recorded (raised before why ask)
```

Without the decisions skill, the headline stays as SKILL.md § Report gives it, and the
`why ask:` line still goes under it.

## Class names

Each decision, raised or decided alone, gets one tag: a reason when it is raised, a kind (or
a reason word an answer covers) when it is decided alone. The clause after each only tells
the tags apart; § The line says when each applies. The spellings are confirmed by answer 134
(a).

**Reasons** (raised; `why ask: <reason> — …`), in their order:

| Reason | What it names |
|---|---|
| `blocker` | something only the operator can do or give |
| `one-way` | an action that cannot be taken back, or only at real cost |
| `trust` | a trust boundary: credentials, permissions, what may reach whom |
| `contract` | a name, format, interface or behaviour something outside this work relies on |
| `reach` | an effect on someone or something beyond this work before the operator reviews it |
| `spend` | quota, money, time or attention beyond a standing grant, a cap's extra round included |
| `precedent` | what happens from now on: a rule, a default, a capability, wider scope, a placement no rule settles, a relay |
| `your-call` | the operator's own call: their words, their conflicting answers, a product or policy call |
| `trade-off` | a real trade-off on anything the reasons above do not name |
| `unclassed` | the backfill form, or doubt on a named reason |

**Kinds** (decided alone; `decided: <time> <kind> — …`):

| Kind | What it names |
|---|---|
| `words` | the words of a text, a message or a label, not a name something relies on |
| `design` | design inside the work, while all four terms hold: inside one item, reversible by an edit, no shared contract, the alternatives the status quo or strictly worse |
| `place` | where a thing lives, when one standing rule settles it |
| `scope` | what work is done: a part split to a filed, linked follow-up, or work routed to its owning repo |
| `reading` | the reading of an unclear reply or instruction |
| `cap` | what was done at a limit the operator set, under the answer that allows it |

A reason word on a `decided:` line names a case an answer or standing grant covers; the
authority names the answer.

A tag is a parsed name: renaming one is a raised `contract` decision. The change that renames
tags migrates its own repo's store in the same landing, and adds the old spellings to
§ Retired spellings, so every other librarian migrates its own.

### Retired spellings

No heading goes inside this subsection, and it stays last in the file: the residue check for
old spellings skips it up to the next heading. These are the spellings answer 134 (a)
retired, and what each becomes; only the tag token changes, except where the row says so.

| Old tag | On | New tag |
|---|---|---|
| `wording` | `decided:` | `words` |
| `minor-design` | `decided:` | `design` |
| `narrowing` | `decided:` | `scope` |
| `forwarding` | `decided:` | `scope` |
| `table-placement` | `decided:` | `place` |
| `reply-reading` | `decided:` | `reading` |
| `ruled-rule-case` | `decided:` | read by hand: the kind, or the reason word, of its case, the authority kept (a round at a cap → `cap`; the reading of an answer → `reading`) |
| `wider-scope` | `decided:` | `scope` |
| `placement` | `decided:` | `place` |
| `api-name` | `why ask:` | `contract` |
| `wider-scope`, `rule-change`, `placement` | `why ask:` | `precedent` |
| `relay` | `why ask:` | read by hand: `precedent`, the text prefixed `relayed from <repo>: `, the repo read from the item |
| `cap` | `why ask:` | `spend` (on `decided:`, `cap` stays) |
| `trade-off — <impact>: ` | `why ask:` | the reason for that impact, the `<impact>: ` prefix dropped |

`<impact>` is a closed list, the eight impacts the old trade-off list named, each written
whole or by its first word: reversibility → `one-way`; who else is affected → `reach`;
spend → `spend`; trust and security → `trust`; behaviour the operator relies on →
`precedent`; contracts and stored data → `contract`; scope and precedent → `precedent`;
quality against speed → `spend`. Any other word before the colon is not this shape, and the
line is kept. A bare `trade-off — …`, and `one-way`, `trust`, `spend`, `blocker` and
`unclassed`, stay as written.

**Who and when.** At every Rehydrate (no plugin-version trigger exists), the librarian reads
the tags in its own store through the two regexes' captured group, a `decided:` line written
with no time included (`decided: <tag> — …`, its tag token the only thing rewritten):

```bash
grep -nP '^decided: (\S+ )?[a-z-]+ — ' "$WI_ROOT"/items/*.md
grep -nP '^\s+why ask: [a-z-]+ — ' "$WI_ROOT"/items/*.md
```

and writes only on a hit: a captured tag this table lists, or a `trade-off` whose text opens
with one of the eight impacts and a colon. No hit, no write. On a hit it rewrites each matched
line in place — the tag token and the prefix the row names, every other character as
written — reads each `ruled-rule-case` and `relay` by hand, skips an item `doing` under
another `owner:` (that owner's Rehydrate migrates it), stages only the files it rewrote, and
commits the store once.

**Removal.** `wi estate` does not parse tags: the removal check is the same captured-tag grep,
run in each repo's store. The librarian of this marketplace files the removal item when this
table lands, and closes it, removing this subsection, once that grep prints no retired
spelling in any store of the estate.
