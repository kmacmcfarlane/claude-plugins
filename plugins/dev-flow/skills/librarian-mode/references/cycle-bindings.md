# The cycle's bindings

The bindings SKILL.md § The cycle lists one line each, in full. Each item runs the
`dev-cycle` skill's Steps 1–5 as a spec with these values; the `dev-cycle` skill's
`references/bindings.md` § What a librarian binds mirrors them for reference.

## Ground

`## Librarian` Scope minus Exclude. **Files in scope**: the item's files, from Factor.
**Checks**: `Checks:`. **Workflow**: `Workflow:`. **Base**: `main`, unless the item names
another.

## Routing

Dev-cycle's Step 2 as written; its one home is the `dev-cycle` skill's
`references/model-routing.md`, and nothing here restates or changes it. That covers the
role agent every dispatch names (`dev-flow:<agent>`, its § Profiles), the
`general-purpose` fallback when one is not loaded (its § Fallback), and the dispatches you
make outside a cycle's roles: a helper (a card, a brief, a summary) and a read-only
question (a `dig into`, a diagnostic) route by the same § Profiles, and you record each as
a helper line, which is yours to write and never a phase of the item's cycle (the
`dev-cycle` skill's `references/record-lines.md`).

## Model floor

An operator pin — a `model: <tier>` line and/or an `effort: xhigh` line in the item body;
the model pin for every role, the effort pin for planner and implementer dispatches (the
`dev-cycle` skill's Step 2 rule 8); never overridden downward.

## Hold

An active hold's limit caps tier and concurrency for every dispatch; below a pin's tier
(opus for an `effort:` pin's `-deep` files) or the reviewer's opus (dev-cycle's Step 2
rule 4), the item waits on a decision (SKILL.md § Idle turn). A hold in force stops every
round that would open unasked past a phase's fourth review, a finish round included: it
is raised (the one home of this rule; the `dev-cycle` skill's `references/bindings.md`
§ Decisions names it the caller's stop).

## Record sink

The item body, appended with Bash (not a custody file): a `dispatch: <role> <model>
<effort> — <signal>` line before every Agent call, a `review: self` line above a verdict
you reached yourself, rounds, verdicts, `trial:` lines, declined findings with reasons.

## Decision channel

`decision N:` appended to the item and carried under the Report's `decisions needed` —
only what dev-cycle raises there: a `SHOW_STOPPER`, a scope change or reversed operator
decision, a cap that is raised, a blocked item, a fable-pin wait, an effort pin whose
`-deep` agent is not loaded, a spike's blocking open questions, a fable cross-check offer,
a pin's ask below the quota reserve (the `dev-cycle` skill's `references/model-routing.md`
§§ Fable cross-checks, Below the quota reserve), a spend budget reached while a fresh
weekly reading is at or above 50% used, or with no fresh reading, a plan's estimate over
its build's default, a round past the fourth review that a hold or the quota stops. A
planner's blocking questions pass through the reasons first (`decide-alone.md` § A
planner's questions). **Durable**: the question lives in the committed item body and is
answered to whichever session is librarian next. Shown per the
`operator-interaction:decisions` skill when it is loaded (`decisions.md`).

**Spend budget** (the `dev-cycle` skill's `references/bindings.md` §§ Spend budget,
Decisions): the cycle's own, as standalone — the `budget:` line you write with the item's
`target:` line, the defaults, an operator's `budget:` pin and the increase ask are all
there; the caller's stop you bind with the channel is the Hold above.

**Decided alone.** What the cycle decides alone is a `decided:` line (`decide-alone.md`),
written before the dispatch or carry it opens: of class `cap`, a plan's stop and carry
(authority `answer 114`), and a finish round of exact-fix leftovers (authority `answer
145`), which needs no grant and no reading of its own beyond the guard past the fourth
review; of class `spend`, a budget reached while a fresh weekly reading is below 50% used,
which does not stop the work to ask (authority `answer 176`).

## Terminal action

`git merge --no-ff` into local `main`; the push is yours, after the Report (SKILL.md
§ Critical). An item naming another base merges into that base instead, with the main
checkout on it, and is never pushed. First-start dirt never blocks a merge
(`first-start.md`).

## Series home

`$MAIN/.claude-sandbox/investigations/<slug>/`, durable, `implement`'s path. No Scope
breach: like the store, tooling state the cycle writes, never a custody edit; agents write
only the series there, and commit none of it.

## Dispatch groups

Dispatch a dependency group in one message, one cycle per item, so they run in parallel;
a later group starts only after everything it depends on has landed. A `model: fable` pin
running out mid-group is one decision — `decision N:`, then `answer N:`, on every item it
hits (the `dev-cycle` skill's `references/model-routing.md` § Fallback); meanwhile hand
each waiting item off and take other work.
