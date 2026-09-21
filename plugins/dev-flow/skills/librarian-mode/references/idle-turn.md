# Idle turn

Ready work is worked, not left waiting for the operator to notice it. This file holds the
detail behind SKILL.md's Idle turn rule: when it fires, the two tables, the dispatch, the
operator hold, and why a rate limit is not one.

## When it fires

A turn is **idle** when it would otherwise end — the Report is written, the request is
answered, or `start` has finished Rehydrate and passed the session-name gate
(`session-name.md`; a held gate is a wait on the operator, not an idle turn) — and no
background agent is in flight that can still produce work. A running implementer or
reviewer counts as in flight; an agent that returned `BLOCKED`, or an item waiting on the
operator's answer, does not. `status` never runs it: it is read-only.

A question to the operator does not make a turn busy: dispatch first, then close the turn
with the question (Intake step 3). The Report's `decisions needed:` never waits on the
queue, and the queue never waits on it.

## The tables

Gather from the store; never `ls` it by hand. Every command reads open items only
(`todo`, `doing`, `blocked`), so closed items never reach a table; `ls` also leaves
`parked` out by default (the `work-items` skill's format reference, § Parked — its count
shows on `wi prime`'s `PARKED <n>` line), so the decision-line scan below adds it back
in — an unanswered `decision N:` on a parked item still has to show in Groom.

```bash
$WI ls --tag hold                    # active holds (closed ones drop out)
$WI ls --status blocked --plain      # blocked: operator, peers, holds
$WI ls --status doing --plain        # the owner column marks your own
$WI ls --ready --plain               # ready, ranked
for id in $($WI ls --plain | cut -f1) $($WI ls --status parked --plain | cut -f1); do
  grep -H '^\(decision\|answer\) [0-9]' "$WI_ROOT/items/$id.md"; done   # decision lines,
                                     # open items + parked; a `blocked` item whose reason
                                     # starts `PARKED` predates the status —
                                     # `wi migrate-parked --apply` converts it
$WI ls --json | python3 -c 'import json,sys; h=sys.argv[1]; print(*[i["id"] for i in json.load(sys.stdin) if h in (i.get("deps") or [])])' <hold-id>
                                     # the items a scoped hold holds
```

Print a `hold:` line first for each active hold, then two short tables, at most seven
rows each with `+N more` below:

```
hold: <hold-id> — <scope>, until <end condition> ("<operator's words>"); holds <ids>

Groom                                        Work
| item | why                           |     | item | P | next                        |
| ab12 | decision 46: <one line>       |     | cd34 | 1 | dispatch now                |
| ef56 | blocked: operator review      |     | 7890 | 2 | after cd34 (same files)     |
|      |                               |     | 1a2b | 1 | after reset 14:05           |
```

- **Groom** — items that need the operator:
  - `blocked` with a reason that names the operator — including a free-text deferral
    such as "operator holding until spare time", which is not parked (below) and not a
    `hold` item;
  - an unanswered `decision N:` line — one with no `answer N:` line in the same item.
    `answer N: <reply>` (SKILL.md § Report) is the only form the scan reads, so the
    librarian writes one whenever the operator answers;
  - once the `grooming` status exists (wi item b020), every `grooming` item.

  A `hold` item is on the `hold:` line, not here. Items blocked on a peer or an external
  dependency are counted in one line under the table, not listed.
- **Work** — what can move without the operator:
  - ready items (`wi ls --ready`), minus held ones. `status: parked` items already never
    appear here — `--ready` leaves them out by itself (the `work-items` skill's format
    reference, § Parked) — so nothing else has to filter for them;
  - your own `doing` items with no agent in flight and no unanswered decision — an item
    handed off after a rate limit, or one whose decision the operator has since
    answered. dev-cycle claims before its Agent call, so these never show as ready.

  `next` says what happens to each row: `dispatch now`, `resume`, `after <id>` (a
  dependency or the same files), `after reset <time>` (a rate limit), or `held
  (<hold-id>)`.

Nothing in either table: say so in one line and end the turn — that is a real idle.

**One-time migration of older replies.** Replies recorded before `answer N:` existed
take other forms — "decision 45 -> a", "OPERATOR <date>: decision 31 approved; 32 a",
"decision 14 ANSWERED", "- 43 → (a) …" — which the scan cannot see, so their decisions
show as unanswered. The first time the Groom table runs on a store, read each item it
lists under `decision N:`; where the body already records the operator's reply, append
`answer N: <that reply> (migrated)` to the item and drop the row. After that pass, every
new reply is written as `answer N:` and no migration is needed again.

## The dispatch

Then, in the same turn, claim and dispatch the top Work rows through The cycle — a
`resume` row continues its own cycle from its handoff:

- **Rank order**: resumed items first, then `wi ls --ready` as printed.
- **File contention**: items whose Files in scope overlap run one at a time — the second
  waits for the first to land, because two worktrees editing the same file end in a
  merge conflict. Items with disjoint files run in parallel.
- **Dependency groups**: one message per group, as The cycle says; a later group starts
  only after everything it depends on has landed.
- **An active limit** (below) caps the tier and the number in flight.
- An item with no Files in scope yet is factored first (Factor), in the same turn.

The next idle turn — when these agents have landed and nothing else is in flight — prints
the tables again and takes the next rows.

## An operator hold

A hold is the operator telling the librarian to stop or slow dispatch: "pause this until
I go to bed", "nothing on fable today", "one agent at a time". Only it, and `start`'s
session-name gate while it waits (`session-name.md`), stops or caps the dispatch above.
It acts on new dispatch only: agents already in flight finish their cycle unless the
operator says otherwise. It is a request like
any other, so it becomes a work item — and that item is where the hold lives, so a
`/clear` or a compaction cannot lose it and the operator can always see why nothing is
moving.

**Recording it** — one `hold`-tagged item, kept `blocked` for as long as the hold stands.
Block it straight after `add`, before anything else: until it is blocked it is a P0 ready
item that a peer's `wi next --claim` could take.

```bash
$WI add "hold: <scope> until <end condition>" -t chore -p 0 --tag hold \
    --desc "Operator <date>, verbatim: '<their words>'. Scope: <all dispatch | the items listed | a limit>. Ends: <end condition>." \
    --ref "operator <date>"
$WI block <hold-id> "HOLD: <scope> until <end condition>"
```

It records three things:

- **The operator's words**, verbatim — the hold is theirs, not a paraphrase of it.
- **Scope**, one of:
  - `all dispatch` — nothing new goes out;
  - **named items** — each one depends on the hold, so it drops out of the ready queue
    by itself: `$WI block <held-id> --on <hold-id>`. List their ids in the hold's body
    too; the `hold:` line names them;
  - **a limit** that preserves quota — at most N agents in flight, no fable. A limit
    caps and does not stop: dispatch goes on inside it. It binds every dispatch while
    it stands — idle-turn dispatch, Intake, and every fix round (SKILL.md § The cycle,
    the Hold binding). N counts every background agent in flight, implementers and
    reviewers alike: one item's implementer and reviewer never run at once, but a
    reviewer on one item and an implementer on another are two.
- **The end condition** — an event ("until the operator says bedtime"), a time ("until
  18:00"), or `until lifted` when the operator gave none; never invent one.

**A limit against a floor.** The operator's more recent instruction wins, but never
silently: when a limit caps below a floor a dispatch must meet — an item's `model:` pin
(a `model: fable` pin under "no fable"), or the reviewer's opus floor (dev-cycle's
Step 2 rule 4, so a "sonnet only" limit clashes on every review) — that item is not
downgraded. It waits — `next: held (<hold-id>)` — and the clash goes through the
decision channel as one `decision N:` on the item, carried under the next Report's
`decisions needed`: keep it waiting, lift the pin or loosen the limit, or exempt it from
the hold.

Being `blocked`, the hold item never enters the ready queue and shows on `wi prime`'s
BLOCKED line; Rehydrate step 3 reads it explicitly with `$WI ls --tag hold`, since that
line lists only three blocked items. Every idle turn prints it on the `hold:` line.

**Lifting it** — on the end condition, or on the operator's word, close the item with
the reason. `wi done` closes a blocked item directly, keeps its HOLD reason on record,
and resolves the dependency every held item carries. Do not `wi unblock` it first: that
erases the reason and briefly makes the hold a ready P0 item.

```bash
$WI done <hold-id> --note "lifted: <operator's words, or the end condition met>"
```

A time-based end condition is lifted by the librarian at the first turn after it
passes, recorded the same way. Then the turn is an idle turn again, and dispatch resumes.

## A quota block is not a hold

A rate limit or an exhausted usage allowance is the harness saying *not yet*, not the
operator saying *stop*. Never open a hold for one, and never leave the queue idle after
it resets:

- **Fable unavailable**: dev-cycle's Step 2 rule 6, detailed in the `dev-cycle` skill's
  `references/model-routing.md` § Fallback — opus when the reset is over 2h away or
  unknown, a pending decision within 2h or under a `model: fable` pin; meanwhile hand
  each waiting item off and take other work (The cycle).
- **Every tier limited**: hand each affected item off naming the limit and the reset
  time (`$WI handoff <id> --blocked "rate limit, resets <time>"`), say so in one line
  with the reset time, and resume dispatch at the first turn after the reset. The items
  stay `doing` and yours, so the Work table shows them as `after reset <time>` until
  then and `resume` after.
