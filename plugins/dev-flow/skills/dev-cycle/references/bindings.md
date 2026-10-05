# Bindings

The ten values a cycle needs from outside itself. SKILL.md § Step 0 resolves them before
any dispatch; every brief, check and landing step reads them from here, never from a
particular repo convention.

A **caller** (a skill that runs cycles, such as `librarian-mode`) supplies each value in
its handoff. A caller's handoff missing a binding is a setup error: stop and name the
missing binding; never fall back to standalone resolution under a caller. A
**standalone** run (the user invoked `/dev-cycle`) resolves each binding itself, in the
order given, and asks the user only where the table says so.

## The ten

| Binding | What it is | Standalone resolves |
|---|---|---|
| **Ground** | What may be touched at all | CLAUDE.md's `## Librarian` `Scope:` minus its `Exclude:` when that section exists (§ A librarian's repo); otherwise the whole repo. Never `.claude-sandbox/` or `.claude/` |
| **Files in scope** | What this change may touch, inside Ground | The item's or plan's files to modify, or the cycle brief's list; when none names files, `undeclared` (§ Undeclared files) |
| **Checks** | Repo commands every change must pass, on top of the generic checklist | § Checks below |
| **Workflow** | Free-text repo workflow notes the change must follow | A `Workflow:` line in CLAUDE.md's `## Librarian` section, read only; otherwise none |
| **Base** | The branch the worktree starts from and the merge lands on | Named by the item or plan (implement's recorded base, re-verified); otherwise the default branch, § Base |
| **Model floor** | The lowest tier any role on this change may run; and its second pin kind, the **effort pin**: the lowest effort for planner and implementer dispatches (SKILL.md § Step 2 rule 8) | A `model: <tier>` line and/or an `effort: xhigh` line in the item body, or the invocation's own words ("at least opus", "at xhigh"); otherwise none |
| **Record sink** | Where the run's record lines are appended (`record-lines.md`) | The item body when a store holds the target; otherwise always the scratchpad run record, `<scratchpad>/dev-cycle/<slug>/record.md`. Never a file in an investigation series: series files belong to `/implement` and are append-only. An item body is durable across sessions; **a scratchpad sink is session-scoped by contract**, so a store-less run's record cannot be read outside the session that wrote it (or one that inherits the same scratchpad) — Step 0's summary says so |
| **Decision channel** | How a decision reaches a human, and the channel's **durability**: **durable** when the question outlives the session that raised it and a human answers it to whichever session reads it next (a caller's channel on a committed item), **ephemeral** when it exists only as a live prompt in this session. A caller states the durability with the channel; a channel supplied without it is a missing binding. A caller may also bind a **caller's stop** with it: what, besides § Decisions' guard, stops a round past the fourth review from opening unasked; none bound means none | AskUserQuestion, or § Decisions' numbered prose list for two or more or with an agent in flight — both **ephemeral**; written per the `operator-interaction:decisions` skill when the session lists it (§ Decisions) |
| **Terminal action** | What Land does with a `CLEAR`, checked branch | Asked once at Land, § Landing |
| **Series home** | Where the plan phase writes an investigation series | `$MAIN/.claude-sandbox/investigations/<slug>/`, the canonical path `/implement` reads |

`<scratchpad>` is the session scratchpad the system prompt names; `<slug>` is the item id,
the series slug, a kebab-case name made from the cycle brief's goal, or — `review
<branch>` mode with no other target — `<branch>` with every `/` written `-`.

## What a librarian binds

For reference, the values `librarian-mode` supplies (its own SKILL.md is authoritative):

| Binding | Librarian value |
|---|---|
| Ground | CLAUDE.md `## Librarian` `Scope:` minus `Exclude:` |
| Files in scope | The feature item's files, from factoring |
| Checks | `## Librarian` `Checks:` |
| Workflow | `## Librarian` `Workflow:` |
| Base | `main`, unless the item names another |
| Model floor | A `model:` pin and/or an `effort:` pin in the item body |
| Record sink | The item body |
| Decision channel | `decision N:` appended to the item, carried under `decisions needed` in its Report — **durable**; caller's stop: a hold in force (its SKILL.md § The cycle, Hold) |
| Terminal action | `git merge --no-ff` into local `main`; the push is the librarian's, after its Report; an item naming another base merges into that base, never pushed |
| Series home | `$MAIN/.claude-sandbox/investigations/<slug>/`, as standalone — tooling state like the store, written by the cycle, never a custody edit; agents write there only the series, and dispatched commits never include `.claude-sandbox/` |

## A librarian's repo

A standalone run in a repo whose CLAUDE.md carries a `## Librarian` section honours it,
read only: Ground is its `Scope:` minus its `Exclude:` (a section with no `Scope:` line,
or `whole repo`, means the whole repo), and its `Checks:` and `Workflow:` feed those
bindings as the table says. The run never refuses because of it and never widens it: a
path outside that Ground is out of scope like any other — the implementer lists it under
OPEN QUESTIONS, and a diff that touches it is a finding at medium. The section is never
written from a cycle.

## Undeclared files

When neither the item, the plan nor the cycle brief names the files to change, the Files in
scope binding is `undeclared` — never a guess. The implementer brief then says
`Files in scope: undeclared`, and the implementer lists every file it changed under
CHANGED with a one-line reason each. The reviewer grades each changed file against the
item's or plan's intent: a file the intent does not justify is a finding at medium. A
declared list keeps the stricter rule: anything outside it is a finding at medium.

After each implementer return, the orchestrator merges that round's CHANGED into one
cumulative block in the record sink — a fix round's CHANGED lists only its own files:

```
changed:
- <path> — <one-line reason>
```

A file changed again keeps one line, with its latest reason. The review brief pastes this
block, and the checklist's scope check (section 1) compares the diff against it.

## Review target

`review <branch>` mode's Step 0 resolves the branch's own worktree in place of Step 3
(no `worktree-<name>` branch is created), and records it as the workspace of the run's
`target:` line — `target: review <branch> <worktree path>` (`record-lines.md`) —
before any dispatch:

1. The main checkout is already on `<branch>` (`git -C "$MAIN" branch --show-current`
   equals it): the worktree path is `$MAIN` itself for reading and reviewing — there is
   no separate worktree to add. Land is different: merging still needs the main checkout
   on `<base>` (SKILL.md § Step 5.3), which case 1 does not satisfy, and the cycle never
   checks `<base>` out over `<branch>` to get there. Land in this case stops and asks
   instead of merging (§ Landing below, `troubleshooting.md` § Landing).
2. Otherwise, an existing worktree already checked out on `<branch>`: `git -C "$MAIN"
   worktree list --porcelain`, matched against `refs/heads/<branch>`. Use its listed path
   as is.
3. Otherwise add one, on the branch itself, at `.claude/worktrees/review-<slug>`, `<slug>`
   being `<branch>` with every `/` written `-` (§ The ten, `<slug>`):

   ```bash
   git -C "$MAIN" worktree add .claude/worktrees/review-<slug> <branch>
   ```

   The same `.git/info/exclude` check as Step 3 applies before adding it. The path that
   command takes is relative to `$MAIN`; what is recorded is the absolute one,
   `"$MAIN"/.claude/worktrees/review-<slug>`.

Every later step reads the worktree by this resolved absolute path, as the `target:`
line carries it, never reconstructed as `"$MAIN"/.claude/worktrees/<name>` — cases 1 and
2 do not live there.

Base still resolves as usual (§ Base below) — it is what Land would merge into, not what
the branch was built from. Files in scope, when a caller, item or plan names them, still
bounds the reviewer's per-file grading, same as any other run; `undeclared` when nothing
does, and the reviewer grades the whole diff against the recorded Intent (§ Intent)
instead of an implementer's per-file reasons.

## Intent

`review <branch>` mode with no work item or plan (SKILL.md § Step 0.2) has no acceptance
to grade against. Before dispatching the reviewer, collect one: ask the user for a
one-line intent in the same question as any other Step 0 ask; if none is given, record
`intent: commit messages are the intent` and use the branch's own commit subjects
(`git -C <worktree path> log --oneline <base>..<branch>`) as what the reviewer grades
against. Record it as `intent: <one line>` (`record-lines.md`) in the record sink.

In this mode, "Files changed, with reasons" in the review brief holds the branch's own
commit list, not the orchestrator's `changed:` block — there was no implementer round to
build one from. The reviewer grades each changed file against the recorded Intent instead
of a per-file reason; a file the Intent does not plausibly cover is still a finding at
medium, but § Undeclared files' "no reason" rule does not apply here — a changed file is
never itself a medium finding merely for lacking a one-line reason, since no implementer
wrote one.

## Record line shapes

Moved to `record-lines.md`, the one copy.

## Checks

Take the first source that answers:

1. A `checks:` line already in the record sink — a resumed or re-run target never asks
   twice.
2. `Checks:` in CLAUDE.md's `## Librarian` section, when the section exists. Read only.
3. Detect, then **ask once**. Look, do not run: read the files named below. Offer at most
   three detected commands in one AskUserQuestion multiSelect question, recommended
   first, then always `None beyond the generic checklist` last; list any further
   detections in the question text so the user can paste them into Other. Ticked
   commands and Other text are the checks; an empty submit or only `None…` means none;
   `None…` ticked alongside commands is ignored.

| Evidence | Offered command |
|---|---|
| `go.mod` at the root | `go test` with the all-packages pattern: `.` then `/...`, written joined (split here only to pass the dot-slash lint) |
| a `Makefile` with a `test:` target | `make test` |
| `package.json` with a `scripts.test` entry | `npm test` |
| `scripts/check-*.sh` | each script, by path |
| `plugins/*/hooks/tests/` | `(cd plugins/<p>/hooks && python3 -m unittest discover -s tests -q)` |

Record the answer in the record sink as one line, `checks: <cmd>; <cmd>` or
`checks: none`. **Never write CLAUDE.md** — not a `## Librarian` section, not a new
`## Checks` section. The answer belongs to the run's record.

## Base

A base named by the item or the plan wins; re-verify it exists
(`git -C "$MAIN" rev-parse --verify <base>`). Otherwise detect the default branch, do not
assume it:

```bash
git -C "$MAIN" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'
```

Empty (no remote, or no remote HEAD): the branch the main checkout is on, stated in the
Step 0 summary so the user can correct it. A non-default base is never chosen silently.

## Decisions

A caller's channel is used as bound. Standalone: exactly one pending decision goes
through AskUserQuestion, whose options carry the choices, recommended first (the
dialog's own convention) — only while no agent of this session's can be running, since a
dialog blocks an agent's return until answered. Two or more, or one raised while an agent
may be in flight, go as one numbered prose list — one decision per number, each with its
own recommendation and its options in (a), (b), (c) order with their impact, the
recommended one in bold, never moved first — so the user answers by number. The cycle's
own evidence is the record sink (an `agent:` line with no `return:` or `verdict:` after it
is in flight); ListAgents covers the session's other agents.

When the session lists the `operator-interaction:decisions` skill (a soft dependency),
load it and write every decision-channel decision to it, whatever the channel. That covers
the decisions this section and SKILL.md send "through the decision channel". It includes
its content floor, its list line / card / block, its order, the echo of a reply, and the
read-back on a one-way choice in a ⚠ decision. A caller's channel still decides where the
decision goes and what the store records. Standalone, those decisions go as text per the
skill, not through AskUserQuestion: a dialog cannot carry the floor, the hint or the echo.
Step 0.2's brief confirmation, the checks question and Land's terminal-action question are
not decision-channel decisions; they stay dialogs, as the skill allows — the first two
come before any dispatch, the third after a `CLEAR` with no agent of the cycle's left
running. Any of the three raised with an agent still in flight (an `agent:` line with no
`return:` or `verdict:` after it, or one ListAgents lists as running) goes as the numbered
list above instead — a resumed run is the likely case.

With the skill or without it: never ask in the same turn as a heavy analysis; end the
turn with the analysis and ask in the next. Append each raised
decision to the record sink as `decision: <question> — options: <a> | <b> | <c>` before
asking — the question in full and its options in letter order, the recommended one
marked `[recommended]`, so the line can be put to a human verbatim by a reader who was not
there — and the reply as `answer: <decision> — <reply>` (`record-lines.md`) as soon as it
arrives.

**What a cap ends in** (SKILL.md § Step 4.3; answers 114 (b), 137, 139 (a), 140 (a), 145
(a)). Read at every verdict that is not `CLEAR`, after the spend check (§ Spend budget) and
before a round opens or anything is raised. Every counted review here is a counted review
**of this phase** (ROUNDS, `resume.md`, which counts from the phase's `target:` line).

**The cap is reached** when any of these holds:

- **the budget**: the phase's last `cost:` line shows spent at or over the amount in force;
- **the convergence stop**: from the fourth counted review on, this review's `must-fix` is
  not lower than the previous counted review's (each review's last `cost:` line; a
  comparison with `?` on either side is not lower) — a count that stops falling means
  the brief or the target is wrong, not the code;
- **the fallback**: no spend reading, and the fourth counted review or later.

The round count survives there and in a plan's stop (step 2), nowhere else.

**A high is left** when a finding still open is critical or high, its `Failure:` sentence
names breakage outside the change (another item, the base, a shared contract, the
operator's data or quota), or it is a must-fix with no severity whose fix the reviewer did
not give verbatim.

**The leftovers** are the findings the verdict's `MUST-FIX:` counts: each new one at medium
or above, and each earlier one at medium or above it marks PARTIAL or OPEN, counted once
when a new one restates it. They are **exact-fix** (answer 139 (a)) when the verdict is
`NEEDS_CHANGES`, no high is left, there are at most three, and each is medium and carries
the reviewer's `Fix:` — written when `review-brief.md` § Report back's conditions hold. A
`Fix:` that names more than one place, offers a menu, or targets anything but prose or
skill text counts as none. A finding from before `Fix:` existed has none; a self-review
writes none. Below the cap a `Fix:` is a suggestion: nothing grades, counts or routes on
it.

Then the first that applies:

1. **An escalation** — a `SHOW_STOPPER`, a scope change, a reversed recorded decision — is
   raised (SKILL.md § Step 4.4), at any round, the end of a granted plan path included.
2. **A plan with no high left**, at a cap or at any counted review from its fourth on,
   stops and carries: the open findings, verbatim with their severities, are **carried**
   — written onto the plan item as a `findings: carried — …` block, a rider no verdict
   carries (store-less: the record sink and Step 6's `open questions:`). Every build
   dispatched from that series copies them into its brief's Acceptance line. A series
   naming another repo's work raises its carried findings to the operator as a `blocker`
   instead, until forwarding (item 3460) lands. Then Step 1's tail runs, with no fable
   offer (the at-the-cap stage needs a high left, and the plan stage is not offered at the
   cap: `model-routing.md` § Fable cross-checks). A plan round past its fourth review
   opens unasked only with a high left (answer 145, Q8 (i)). A plan never takes a finish
   round (step 3).
   **Standalone, every plan cap is raised instead — a stop and a granted plan path's end included — as before answer 145 (decision 156).**
3. **Exact-fix leftovers at a cap** get one **finish round** unasked, when the previous
   counted verdict did not reach the cap, or the round after it was opened by the
   operator — an `answer:` to its decision, or a `budget:` line whose source is
   `operator` or names an answer (`answer N …`, `… (answer N)`), recorded after that
   verdict; a `default … ×2 fable` line opens nothing — so never two in a row unasked.
   The producer is resumed, or re-dispatched where `model-routing.md` § Rounds changes its
   tier (never you: decided on item 5bdd, authority answer 137), with
   `agent-brief.md`'s fix-round clause and its finish-round line; then the same reviewer
   is resumed with the re-review variant, which grades each finding on its failure and
   may still return findings that are not exact-fix: they meet this list at its verdict
   (answer 140 (a)).
4. **Otherwise, at a cap**: raised (an ask for another round, below) — at the budget as an
   increase ask, at the convergence stop or the fallback as an ask for another round. A
   plan with a high left is raised the same way; the at-the-cap fable offer is an option
   of its decision (`model-routing.md` § Fable cross-checks).
5. **No cap**: the next fix round opens unasked, whatever is left, a high included.

**Past the fourth review** (answer 145 (a), Q7 (i)), a round that would open unasked after
the fourth counted review — step 3's or step 5's — opens only when both hold, and is
otherwise raised as an ask for another round:

- the **caller's stop** does not stop it (§ The ten, Decision channel); standalone binds
  none;
- a **fresh weekly reading**, taken at that moment with the `librarian-mode` skill's
  `scripts/quota_budget.py --read-only`, exists and is not below the reserve
  (`model-routing.md` § Below the quota reserve). Here **no signal is a stop**, not a
  pass: a round spent unasked needs evidence the quota is there.

No standing grant is needed: the phase's budget is the grant. Before answer 145 a
standalone run raised every cap, and a librarian took at most one extra build round, inside
a standing grant; rounds past the fourth review running unasked, standalone too, is the
loosening the answer named. A round an operator's answer opens is the operator's and
passes no guard. Rounds up to the fourth review pass none.

**A `model: fable` pin**: its rounds run inside its doubled budget under the same rules. A
finish round on it is not raised as a cap; its producer and reviewer run at fable; the
pin's own asks still apply before each dispatch (`model-routing.md` §§ Below the quota
reserve, Fable unavailable), unless an earlier answer still covers the item. When the
pin's below-the-reserve ask and the guard fall on one round, one decision carries both,
and its answer is the pin's too.

**A round the operator granted** on a plan at a cap ends on the path the grant named: the
cap does not re-apply after it, and whatever is still open at its end, a high included, is
carried as in step 2 (8dee E2). A build's granted round, and a round a raised budget
opens, meet this list again at their verdict.

**Decided, not asked**: a stop and carry and a finish round are recorded as the caller's
decided-alone record (`librarian-mode`: a `decided:` line of class `cap` — a stop's
authority `answer 114`, a finish round's `answer 145`), written before the dispatch or the
carry, with **if left** and **what the round costs** as below. A finish round's reopen
is "say stop: the round ends and its commits do not land". Its `dispatch:` signal reads
`— finish round (exact-fix leftovers at the cap)`, or `— resume (finish round, exact-fix
leftovers at the cap)`: informational, never read by resume. Standalone has no
decided-alone record: a finish round is recorded by its `dispatch:` signal and shows on
`verified:`, and a stop and carry, where one is taken, by its `findings: carried` block.
Resume needs neither signal: an interrupted finish round re-enters at its dispatch or
return (`resume.md` Groups B, C), and a `decided:` line or a `findings: carried` block
after the last verdict means Step 4.3 ran. A round past the fourth review that the guard
lets open is an ordinary round: no `decided:` line.

**An ask for another round** — a cap that is raised (above), a round the guard stops, or
any ask to open one more round — carries its justification, with the skill or without it,
so the user can weigh it: **if left**, each finding still open, its severity, what it would
break (the `Failure:` sentence of the last review's `findings:` block), and whether it
carries a `Fix:`; any finish round spent since the last answer and any `Fix <n> not
applied`. **What the round costs**, measured where a reading exists: **spent**, `$X of $Y`
(dispatched agents) with its share of a week, and the weekly reading and whether it is
below the reserve; **what more buys**: the next round's cost (the median of the
differences between this phase's consecutive reviews' last `cost:` lines; with fewer than
two, spent ÷ counted reviews), the must-fix trend (`4 → 2 → 2`), and the time between the
last two `cost:` lines. With no reading, about how long a round has taken in this run and
its quota share when a weekly reading exists. Either way, one more answer from the user if
the round does not clear. A budget ask's first option names the new total, sized in rounds
("raise to $34, about three rounds here"), recommended when the must-fix count is falling
or every leftover is exact-fix; its answer is written as a `budget:` line with the new
total, `answer N (was $<old>)`, before the round opens. The `decision:` line carries the
justification after its question, so it can still be put verbatim — except under a caller
that stores a card (librarian-mode), where the card's own lines carry them and the headline
keeps the question alone. With the skill loaded, its floor for a round ask governs how this
is written.

A **pending** decision — a `decision:` with no `answer:` — never makes a run wait on a
question this session is not asking: one whose prompt is gone, or one on a durable
channel. A live prompt this session is asking is the ordinary case above, and the run
takes its answer when it comes. For the other two, the channel's durability (§ The ten)
says what the run does instead:

- **Ephemeral (standalone, or a caller binding an ephemeral channel).** A pending
  `decision:` whose prompt is gone — raised by a session that has ended, or in a prompt
  that closed unanswered — is asked again in this session, verbatim from the recorded
  line, its question and options as written. Write **no second `decision:` line**; the
  `answer:`, when it arrives, answers the recorded one. The heavy-analysis rule above
  still holds: a turn that finds it while doing heavy analysis (a resumed run's Step 0
  is one) ends, and the next turn opens with the ask — the session asks on its own, with
  no reply awaited first.
- **Durable (a caller's durable channel).** Hand back: `$WI handoff <id> --blocked
  "awaiting decision N"` (no item: a `blocked:` line in the record sink), report, and
  stop. Waiting is the caller's — its own loop resumes the target once the answer lands
  — and never the cycle's: a cycle that waited on a channel nobody was reading would
  hang.

An `answer:` is in force only while no phase line (`resume.md` § Phase lines and riders)
has been recorded after it, with one exception, the
answer to `review <branch>` mode's ask whether to dispatch an implementer for the
findings, which stays in force wherever it sits in the record until a `spent:` line
recorded after it names it. An answer out of force answers nothing: its question, when
it comes up again, is raised as a new decision.

## Spend budget

Each phase of a target has a **spend budget** in list-price dollars, set when the phase
opens (answer 145 (a)): the plan phase is a `plan`-mode run, the build phase every other
run (SKILL.md § Step 0.3). Rounds run unasked inside it; reaching it is a cap (§ Decisions,
What a cap ends in). No brief carries it, so no producer or reviewer trims its work to fit.

**A phase opens at its `target:` line**, written with its `budget:` line before the
phase's first dispatch (SKILL.md § Step 0.3; a caller writes both where it writes
`target:`). A build on a planned item writes its own pair, so the plan's reviews never
count in its build. A new plan run on a plan that already cleared, with no build since, is
the same mode and ref: it continues the plan phase — its `target:` and `budget:` lines
kept, its reviews counted on from them, its spend added to the phase's, as the reader
keeps one plan phase per record. The reader keeps one phase per kind per record, opened at
that kind's first `budget:` line, so two cases read as one phase: a re-plan after a build
opened puts its plan spend into the build, and a new pair of the same phase with a
different mode or ref resets the amount and ROUNDS while the reader keeps the earlier
spend. The phase that absorbs the spend reads high and asks early; a re-plan after a build
reads its own phase low, so only the fourth-review count and the convergence stop bound
it until follow-up 7421 lands.

**The amount** is the first of these that answers:

1. the operator's own `budget: [plan|build] $<n>` in the item body — a pin, read like
   `model:`, no phase word meaning every phase — or, a store-less run, the invocation's
   own words ("a $30 budget"), as the Model floor reads them (§ The ten); source
   `operator`;
2. for a build, its plan's estimate, **when it is at or under the default, or an answer
   set it** (below);
3. the default:

| Phase | Default |
|---|---|
| plan of a `spike` | $40 |
| plan of any other type, or of none | $28 |
| build of a `chore` | $10 |
| build of a `bug` | $12 |
| build of any other type, or of none | $22 |

A `model: fable` pin doubles the default (Fable 5.1 runs about 2× Opus 5.5 on this
estate's mix); an `effort:` pin does not scale it. One table serves every repo. The figures
are list prices as of 2026-10-02; re-derive them when the price table changes, and revisit
them from the `cost:` lines. The type is the item's `type:`, or the cycle brief's type
(SKILL.md § Step 0.2).

**The plan's estimate.** A plan for a build may state `Estimated cost: $<n> — <why>` (the
`investigate` skill's `references/investigation-format.md`); the line in the highest serial
carrying one is in force. After the plan's `CLEAR` (SKILL.md § Step 1's tail), an estimate
over its build's default goes to the operator as a budget decision with the plan's
blocking open questions — options: the estimate [recommended], the default, another
amount — unless the build item carries the operator's pin. **At the build's Step 0.3** the
estimate is read again:

- at or under the default: it is the amount (`plan <slug> estimate`);
- over it, with an answered budget decision on the plan item — the item whose
  `target: plan` line ends in the series slug,
  `grep -l "^target: plan .*/<series slug>/\?$" "$WI_ROOT"/items/*.md "$WI_ROOT"/archive/*/*.md`,
  else the build item: the amount the answer chose (`plan <slug> estimate (answer N)`;
  `default <kind>` for the default; another amount `answer N (was $<default>)`);
- over it with no answer — a series written outside a dev-cycle plan run, a pending
  decision, a store-less run: the **default** stands (`default <kind>`), and the budget
  decision is raised now on the build item (or asked, standalone) — unless one is already
  pending on the plan item, which is pointed to instead, never raised twice. Its answer
  writes a new `budget:` line, which opens a round as any answer's does.

The decision is found by reading the item's answered decisions — the one raised on that
series' estimate — never by a tag: no new parsed name.

**The `budget:` line**: `budget: <UTC> <phase> $<total> — <source>` (`record-lines.md`). A
resumed run keeps the line it has; a phase with none — a record from before this rule —
has no reading. A raise writes a new line with the new **total**, never a delta:
`budget: <UTC> build $34 — answer 12 (was $22)`. The phase's last `budget:` line is the
amount in force. A `model: fable` pin set after the phase opened writes a new line,
`default <kind> ×2 fable`, before the next dispatch, unless the amount in force is the
operator's or an answer's.

**The reader** is context-guard's `usage-report` (soft), found as `wi` is (§ Store):

```bash
UR_PY=$(ls "$MAIN"/plugins/*/skills/usage-report/scripts/usage_report.py 2>/dev/null | head -1)
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
test -n "$UR_PY" || UR_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["context-guard@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/usage-report/scripts/usage_report.py"
test -f "$UR_PY" || UR_PY=$(ls -t "$P"/cache/kmacmcfarlane/context-guard/*/skills/usage-report/scripts/usage_report.py 2>/dev/null | head -1)
timeout 120 python3 "$UR_PY" item <record sink file> --json --no-week
```

The record sink file is the item's `$WI_ROOT/items/<id>.md`, or the scratchpad
`record.md`. Phase spend is `phases.<phase>.usd` when that phase's `reading` is `read`.
**No reading** is any of: no reader found; a reader too old (`item` exits 2 with an
"invalid choice": an installed context-guard older than the reader — reason `reader too
old (update context-guard)`); any other non-zero exit or a timeout; output that does not
parse; the phase `unread` (a Claude model the price table does not know, with tokens; or a
lost transcript no `cost:` line covers); or no `budget:` line in the phase. Another phase's
`unread` does not matter. A `reader too old` reason is named once under Step 6's `open
questions:`. A card's share of the week comes from one more run without
`--no-week` (`share_of_week_percent`).

**The spend check** reads spend and appends one `cost:` line (`record-lines.md`):
`cost: <UTC> <phase> $<spent> of $<budget> after review <n> — must-fix <m> — prices <version>`,
or with no reading `cost: <UTC> <phase> unread — <reason> — must-fix <m>`. `<m>` is the
verdict's `MUST-FIX:` count (`review-brief.md` § Report back; a self-review's own count),
`?` when the report has none. It runs at every counted verdict (SKILL.md § Step 4.5), and
again before a round opens when any agent line was recorded after the last `cost:` line (a
cross-check, a helper): spend is checked **when the round opens**. It runs only between
rounds, with no agent of the phase running, so nothing is cut off. Everything recorded on
the item counts — cross-checks and helpers included; an accepted cross-check raises nothing
at its return, only at the next check.

## Resume

Taking an interrupted run up again — the reduction, the state table and the GATE:
`resume.md`.

## Landing

Standalone, ask once at Land — AskUserQuestion, options in this order:

1. `Merge to <base> locally, no push` — `git merge --no-ff` into the local base, then the
   cycle's own worktree removed and its own branch deleted (`full` mode:
   `worktree-<name>`; `review <branch>` mode: only a worktree this cycle added itself at
   `.claude/worktrees/review-<slug>` — never `<branch>`, which is the author's and is
   never deleted). Nothing leaves the machine.
2. `Leave the branch` — no merge; whatever the cycle itself added (the worktree, and in
   `full` mode `worktree-<name>`) stays for the user; the item, when there is one, gets a
   handoff instead of `wi done`. `review <branch>` mode never touches `<branch>` itself
   either way — it was never the cycle's to remove.
3. `Merge and push` — option 1, then `git -C "$MAIN" push origin <base>`, fast-forward
   only, never `--force`.

`review <branch>` mode merges `<branch>` itself in place of `worktree-<name>`:

```bash
git -C "$MAIN" merge --no-ff -m "<message>" <branch>
```

from the worktree path § Review target resolved, once the main checkout is on `<base>`
(SKILL.md § Step 5.3) — the same requirement `full` mode has. § Review target's case 1
(the main checkout already on `<branch>` itself) never satisfies that on its own:
checking `<base>` out over `<branch>` to get there would mean checking out over the
user's own work, which the cycle never does. **Case 1 at Land stops and asks**
(`troubleshooting.md` § Landing, "the main checkout is not on the base") instead of
merging — the user switches the main checkout to `<base>` themselves and Land re-runs
its checks and diff, or picks `Leave the branch`, which never needs the main checkout
touched. Cases 2 and 3 (an existing or added worktree elsewhere) merge normally once the
main checkout, separately, is on `<base>`; cleanup then removes only a worktree case 3
added, never `<branch>` itself.

Never push unless the user picked option 3 or the invocation asked for it in words. A
rejected push is never pulled, rebased, reset or forced past: fetch, show the incoming
commits and ask once whether to merge `origin/<base>` in — a checked merge, every Check
re-run before the push, a conflict or red check aborting it — or leave the local merge
unpushed (`troubleshooting.md` § Landing, "Push rejected", which follows the
`librarian-mode` skill's `references/troubleshooting.md` § Push rejected).

Option 3 (or a push the invocation asked for in words), once the push succeeds, also
means Step 6 adds one team summary after the Report — a push left rejected gets none. The
shape is the `librarian-mode` skill's `references/team-summary.md`, read there and not
restated here, with one clause read against this cycle instead of a librarian's: its
commit-range recipe reads `main`/`origin/main` as `<base>`/`origin/<base>`; its
librarian-only timing (the `incoming:` lines, its own SKILL.md § Report,
`ending-the-session.md`, 75%/DUE, noting `origin/<base>` before each push) does not
apply — the summary simply follows the four lines; and its bullets cover only this
cycle's own landing — another commit the push carried is noted as not the cycle's, or
folded into the housekeeping area.

## Store

A work-item store is optional. Look in the main checkout for `.claude-sandbox/work/`, then
`.work/`; the first that exists is the store. No store: the record sink is the scratchpad
run record, and nothing is filed. Never run `wi init` from a
cycle.

`wi` itself comes from the repo's own tree when it carries the `work-items` plugin, else
from the installed plugin:

```bash
export WI_ROOT="$MAIN/.claude-sandbox/work"   # or "$MAIN/.work"
WI_PY=$(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
test -n "$WI_PY" || WI_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["work-items@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
WI="python3 $WI_PY"
```

`${CLAUDE_PLUGIN_ROOT}` is dev-flow's root and carries no `wi`. A store with no `wi`
anywhere: say once that `work-items` is not installed, and run with the scratchpad record
as the sink.

The same resolved line, with absolute paths, is what the briefs' `CLI:` line carries.
