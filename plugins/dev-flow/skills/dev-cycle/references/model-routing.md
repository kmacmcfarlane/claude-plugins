# Model routing

Signal tables and worked examples for SKILL.md § Step 2 (Route). The eight rules there
are the contract; this file is how to apply them without re-deriving them per dispatch.
It is the one home of dev-cycle's routing, and of every caller that runs dev-cycle as its
cycle spec (`librarian-mode`). It routes the dispatches of a development cycle — planner,
implementer, reviewer, and the fable cross-checks the operator adds — and the helper and
read-only dispatches a caller makes around them (§ Profiles). The research skills
(`research`, `research-deep`, `research-refine`, `research-prune`) and their
`research-lane` and `research-verifier` agents keep their own routing, and nothing here
governs them.

## Why route at all

A sub-agent inherits the parent's model unless the Agent tool's `model` field says
otherwise, and that field wins over everything else, the agent file's own `model`
included. The orchestrator often runs on the dearest tier, so an unrouted dispatch is the
dearest dispatch — every implementer, every reviewer, every helper. Per million tokens the
tiers sit roughly at fable 10/50, opus 5/25, sonnet 2/10 (in/out). The brief constrains the
work tightly enough that a cheap failure costs a re-dispatch, not a landing; the review is
where the cycle spends, and it spends on opus.

A sub-agent also inherits the session's **effort**, live, unless its agent file pins one:
a `general-purpose` dispatch runs at whatever level the operator's session is at, however
high, whatever its task. The Agent tool takes no effort parameter; only an agent file's
`effort` sets it. So effort is routed by the choice of agent file (§ Mechanism).

## Mechanism

- **Dispatch a role agent**: `subagent_type: "dev-flow:<agent>"`, one of § Profiles, and
  pass `model` on every call as well — `"sonnet"`, `"opus"` or `"fable"`. The file pins the
  effort; the per-call `model` sets the model and wins over the file's, so one file serves
  more than one tier (an `implementer` on opus). A forgotten `model` falls to the file's
  own pin, never to your model. Haiku is out of scope — the checks it could run, the
  orchestrator runs itself.
- **One role and one effort per file.** A role that needs a second effort has a second
  file (`planner` and `planner-deep`), so an effort change is a change of file, and a
  change of file is a fresh dispatch.
- **A resume keeps the file** — its effort, and its model. Resume (SendMessage) only when
  the next round's file and model are both unchanged (§ Rounds; `fix-loop.md` § A
  NEEDS_CHANGES round).
- **What outranks a pin.** `CLAUDE_CODE_EFFORT_LEVEL`, set in the environment, overrides
  every file's `effort`, and a `maxEffortLevel` setting caps it: leave both unset where
  these pins should hold.
- **Nested dispatches are outside this routing.** An agent's own sub-agents — the
  dispatches of the /investigate and /implement an implementer runs in its worktree — are
  routed by those skills. Whether a nested sub-agent takes its parent's pin or the
  session's effort is not documented: treat it as the session's.
- **Not loaded**: `general-purpose` with the same `model`, recorded `inherit` (§ Fallback).

## Profiles

The role agents dev-cycle and its callers dispatch, each file one role at one pinned
effort. The model is the file's default, and the per-call `model` moves it. The rows carry
the operator's answers of 2026-09-30 on when each tier runs (answers 123–127 and 130 on the
decision-handling item 69ee); a change to one is a routing change made here.

| Agent | Pin: model / effort | Dispatched when |
|---|---|---|
| `scribe` | sonnet / low | a helper with no judgement on its dispatch line: render a decision card, fill a brief from its template, summarise given text |
| `scout` | sonnet / medium; `model: opus` on the call after a sonnet `scout` returned "could not determine" on a question the work depends on | a read-only question: locating code, read-and-reason, a diagnostic. A question that needs a plan runs as a spike, in a cycle of its own |
| `implementer` | sonnet / medium; `model: opus` on any opus signal; `model: fable` under a pin | every implementer dispatch the two rows below do not take: sonnet for the canonical kinds in a kit repo, and for wording and docs elsewhere; opus otherwise (§ Implementer) |
| `implementer-critical` | opus / high | an implementer dispatch on work the operator called critical: the item or its refs quote the operator calling it critical, crucial, foundational or important, or asking for fable (§ Critical work) |
| `implementer-deep` | opus / xhigh | an implementer dispatch under an `effort: xhigh` pin (SKILL.md § Step 2 rule 8) |
| `planner` | opus / high | every plan dispatch not sent to `planner-deep`, from the first; the trial's control arm (§ The xhigh trial); a bump-arm round stepped down below the quota reserve (§ Below the quota reserve) |
| `planner-deep` | opus / xhigh | a plan dispatch under an `effort: xhigh` pin (rule 8); the trial's bump arm, above the quota reserve (§ The xhigh trial) |
| `reviewer` | opus / high | every review and every plan review not sent to `reviewer-light`; the fresh opus review that stands in for a fable cross-check on work fable wrote (§ Fable cross-checks) |
| `reviewer-light` | opus / medium | a review of a fact and docs change in the home-network and product-docs repos (§ Reviewer effort by kind) |
| `cross-checker` | fable / high | a plan-stage cross-check the operator accepted, while the keep rule holds that stage at high (§ Fable cross-checks) |
| `cross-checker-deep` | fable / xhigh | a cross-check the operator accepted at the estate-wide, post-landing or at-the-cap stage, or at the plan stage's second try (§ Fable cross-checks) |

- **xhigh runs only on the three `-deep` files**, and every dispatch of one names its
  signal on its `dispatch:` line: the effort pin, the trial's bump arm, or the operator's
  answer accepting a cross-check. No reviewer file runs above high, and an effort pin never
  reaches a reviewer.
- **No fable cross-check runs unasked.** Both `cross-checker` files run only on the
  operator's yes to an offer (§ Fable cross-checks).
- **The two pins compose.** A plan with both `effort: xhigh` and `model: fable` is
  `planner-deep` with `model: fable` (rule 8).
- **A caller's own helpers and questions** — a decision card, a filled brief, a summary; a
  `dig into` or a diagnostic — go to `scribe` and `scout` by the rows above. The caller
  records each as a **helper line**, a `dispatch:` with role `scribe` or `scout`
  (`record-lines.md`). A helper line is a rider, never a phase of the cycle, so it never
  displaces the cycle's own state or a pending decision (`resume.md` § Phase lines and
  riders).

## Implementer

Sonnet when every edit in the change is mechanical; opus on any one opus signal. When a
change is not plainly mechanical, it is opus. Either way the dispatch is the `implementer`
file (medium) with the tier as its `model`, except in two cases:

- work the operator called critical goes to `implementer-critical` (§ Critical work);
- an item under an `effort: xhigh` pin goes to `implementer-deep`, on opus or on a higher
  `model:` pin, even when its edits are canonical kinds or it was called critical (rule 8).

### Sonnet — every edit one of these

What counts as mechanical depends on the repo.

**In a kit repo** — a repo whose text agents follow as rules: a plugin marketplace or an
agent-policy repo (for this marketplace's estate: `claude-plugins`, `agents` and
`agent-research`) — only the **canonical kinds**, each named on the dispatch line:

| Kind | Reads as |
|---|---|
| Pointer or path | a reference or path corrected to where the thing already is |
| Link | a link corrected to its target |
| Frontmatter | a `name`, `description` or other key edited to the house rule, the skill's behaviour unchanged |
| Catalog row or layout line | a README catalog row or CLAUDE.md layout line brought in line with what already exists. A table row elsewhere, or a routing-map row, is not a catalog row |
| Listing | a list entry naming what already exists, added or corrected, such as a reference map's file list |

Everything else in a kit repo is opus, wording included: text there is a rule an agent
follows.

**Elsewhere**, the same kinds, plus wording that changes no behaviour — a typo, a clearer
sentence, formatting, alignment; no rule, command or value moves — and docs that change
no documented behaviour (§ Product repos).

Breadth alone does not raise the tier: the same pointer fix across five files is still
mechanical.

### Opus — any one signal

| Signal | Reads as |
|---|---|
| Behaviour | a change to what a skill, agent, CLAUDE.md or doctrine rule does — a new step, a changed rule, a new case |
| A format bump | a record, file or report format gains, loses or changes a field |
| Executable logic | a hook, anything under `scripts/`, tests, a status line, a `settings.json` write; in a product repo, any code inside Ground |
| Marketplace shape beyond a row | `marketplace.json`, a plugin added, split, moved or retired |
| Judgement in the item | the body records a real trade-off, or the acceptance uses judgement words that ask for a trade-off (coherent, reconcile, align two rules) — not "align" naming a path or value to match |
| A prior `NEEDS_CONTEXT` return | the first run could not settle it from the brief alone |
| Kit-repo text | any edit in a kit repo that is not a canonical kind (above) |

A planner is opus at least (SKILL.md § Step 1): a plan is judgement. It runs on `planner`
(§ Profiles).

### Critical work

**The operator called the work critical** when the item body or its refs quote the operator
calling it critical, crucial, foundational or important, or asking for fable. Only the
operator's own words count: these words are rare, so routing never relies on them to find
deep work, and never infers them from the work itself. When they are present they are
the operator's ruling.

Every implementer dispatch on such work, fix rounds included, goes to
`implementer-critical`: opus high, one tier and one effort for the whole build. A request
for fable reads the same way: it sets no model by itself, and only a `model: fable` pin
puts the build on fable, with `implementer-critical` as its file (rule 8). The plan stays
on `planner`: the operator's word raises the build's effort, not the plan's. Under an
effort pin the build is `implementer-deep` instead (rule 8).

### Fable

Fable is no implementer tier by signal: no size, surface or round routes an implementer to
it. It runs only when a human names it — a `model: fable` Model floor (rule 8), which runs
every role on fable — or as a cross-check the operator accepted (§ Fable cross-checks).

## Product repos

When the Ground binding holds product code (a whole repo, or source paths), the same
tables apply; only what counts as a signal widens:

| Change inside Ground | Tier |
|---|---|
| Docs only — README, `docs/`, comments with no code change — and mechanical | sonnet |
| Docs that change a documented behaviour, command or setting | opus (behaviour) |
| Any code — source, tests, build files, scripts, a security surface | opus (executable logic) |

The Checks binding does not move the tier: they run at review and Land whatever it is.

## Reviewer

Always opus, always fresh: a new sub-agent that never saw the implementer's conversation.
Never a fork of the orchestrator or the implementer, never the implementer resumed as its
own reviewer, never the orchestrator itself — except § Review waiver. A fresh context and
a different model from a sonnet implementer are what make the review worth its cost. The
file is `reviewer` (opus high), except the one kind § Reviewer effort by kind sends to
`reviewer-light` (opus medium).

| Implementer | Reviewer |
|---|---|
| sonnet | `reviewer` (or `reviewer-light`), opus |
| opus (any implementer file) | `reviewer` (or `reviewer-light`), opus |
| fable (a pin) | `reviewer`, fable (the pin is a floor for every role) |

A sonnet reviewer never exists. The reviewer's tier does not follow the implementer's
bumps, and its effort does not follow an effort pin: it is opus from the first round to
the last, on the file its first review took, so the same reviewer is resumed for its own
re-reviews (it has seen only reviews). `review <branch>` mode has no implementer; its
reviewer is opus all the same.

### Reviewer effort by kind

The operator's answer (answer 126 b): **opus medium only for fact and docs changes in the
home-network and product-docs repos. Host config, security work, plans and the kit repos
all stay at high.** So a review goes to `reviewer-light` only when all of these hold, read
off the full diff at the review's HEAD, never off the brief:

- the repo is one of the home-network and product-docs repos — for this estate,
  `mcfacehead-plugins`, `mcfacehead.com`, `opencode`, `hooper`, `clustertool` and
  `brainboy`: never a kit repo (§ Implementer) and never `claude-sandbox`;
- every changed file is a fact or docs change;
- it is not a plan (a plan review is `reviewer`);
- no security work: nothing names credentials, secrets, root-run code, host mounts,
  egress, injection, permissions or a threat model;
- no host config: no sysctl, systemd unit, service user, router or firewall rule, cron
  entry, installer, config key, YAML or JSON;
- the item carries no pin: a `model:` or `effort:` pin keeps `reviewer`.

Any doubt is `reviewer`. The test is read at the first review and again at each fix
round on the cumulative diff: a round that no longer passes goes to `reviewer`, a fresh
dispatch (a change of file), and stays there. A reviewer never moves down.

## Fable cross-checks

A fable cross-check is one fresh fable reviewer, run after the opus review at the stages
below, where the record shows fable changing outcomes: a second reviewer, never a
substitute — the opus review runs first and in full.

**Offered, never run unasked.** The operator's words (answer 124 b): *"Identify when a
cross-check would be helpful and why. The operator needs to decide to add the fable
cross-check explicitly, but you should offer it when appropriate."* Every stage below,
the estate-wide one included (answer 130 a), is therefore an **offer**: the orchestrator
names the stage and why a cross-check would help this work, through the decision channel
(`bindings.md` § Decisions) as a tagged `decision: fable-offer — …` (`record-lines.md`)
— its options: add the cross-check (the file and its effort), or go on without it — and
dispatches it only on the operator's yes. The GATE never reads the tagged pair, so an
offer neither holds a run nor stands in for another decision's answer; the orchestrator
reads its answer itself when it next acts on the item. The at-the-cap offer is instead an
option of the cap's own, untagged decision. Silence is never a yes. An offer is not made again once answered on the item, nor on a plan whose record
already shows a fable cross-check after its last `CLEAR` (an older record's
orchestrator-added second opinion included). Below the quota reserve an offer waits
(§ Below the quota reserve).

| Stage | Offered when | File | What it reviews |
|---|---|---|---|
| **Plan stage** | after the opus plan review's `CLEAR`, on plans that change a contract other plugins or repos use, change doctrine, or that the operator called critical; and on research syntheses whose decision no plan covers, when the synthesis lands in the orchestrator's hands (its run's own verification done) | `cross-checker` while the keep rule holds the stage at high; `cross-checker-deep` on its second try; none once it drops | the series (or synthesis), plan-review variant |
| **Estate-wide plan** | once per series, on the final plan, after its opus `CLEAR`: plans that change what every repo's agents do — routing, agent factoring, librarian doctrine, plugin boundaries. On that plan it takes the plan stage's place | `cross-checker-deep` | the series, plan-review variant |
| **Post-landing** | after the last piece of a multi-item capability lands: the item has a parent, or is a feature of a plan series, and it is the last open child | `cross-checker-deep` | the whole capability on the base at the landing sha |
| **At the cap** | a plan at the review cap with a high still open: an option of the cap's own decision, "one fable cross-check: stop or continue" | `cross-checker-deep` | the series as it stands, plan-review variant |

Reading the plan stage's nouns: a contract other plugins or repos use is a contract file
in scope (`record-lines.md`, a `format.md`, `provider-interface.md`, `sensor-contract.md`,
`hook-contract.md`, this file) or a body naming two or more consuming plugins or repos;
doctrine is README principles or catalog, `marketplace.json`, a plugin added or moved, or
CLAUDE.md § Placement rules; the operator called it critical as § Critical work reads it.

**An offer never holds the build.** The plan's build proceeds while a fable offer is
open, deferred, or waiting below the reserve; a `plan` run closes as usual, the offer under
its Report's `decisions needed:`. An accepted plan-stage or estate-wide check runs when
headroom allows. Its accepted findings that arrive **before the build's `CLEAR`** are
written onto the build's item — the item whose cycle builds that series — as a
`findings: cross-check (<stage>) — …` block (`record-lines.md`), and open its next fix
round: the build's next review brief pastes them, a reviewer already running is sent them
before it returns, and that review's verdict carries each that stands, counted toward the
build's cap. Whatever its verdict, that reviewer rules on each one — stands or withdrawn,
with a reason — and the ruling is recorded as a `cross-check-rulings:` block under its
verdict (`record-lines.md`); a withdrawn one is named under the Report's
`open questions:`. Any that arrive **after the build's `CLEAR`** — merged or not — or on a plan
whose build has not started become a follow-up item. A post-landing offer holds
nothing: the landing stands. The at-the-cap offer is part of the cap's decision.

**The author rule.** On work fable wrote — a `model: fable` pin's plan or build — a fresh
opus review stands in for the fable cross-check at every stage: the offer names `reviewer`
(opus high) in its place, never fable checking fable. It is offered and run exactly as a
cross-check (below), recorded `dispatch: reviewer opus high — cross-check stand-in
(<stage>); answer <N>`: the one opus dispatch a `model: fable` pin allows, by the
operator's answer 124 b, and no review round. Its return line reads `stand-in` in place
of an effort, so it never counts toward the keep rule.

**The keep rule** (plan stage, research syntheses included). The stage is kept only if at
least 2 of its first 8 checks find a high the opus review missed; else it tries xhigh for
8 more, then drops. A check counts only when it ran — an offer the operator accepted; a
dropped check is not a trial and never counts — and it finds one when it raises a high
or critical the opus `CLEAR` missed and the orchestrator accepts. `<n>` counts the
orchestrator's acceptance when the check returns, not the build reviewer's later ruling
on each finding, which is recorded apart (below). When each cross-check returns, append
`cross-check: <stage> <high | xhigh | stand-in> <n> accepted highs <UTC time>`
(`record-lines.md`), `<n>` 0 for a `CLEAR`, the time as `YYYY-MM-DDTHH:MMZ`; the keep
rule reads the `plan-stage` ones with a numeric `<n>`. Before each plan-stage offer, take
the **first 8** lines by that time over the trial's stores (§ The xhigh trial, Sample), so
concurrent sessions read the same 8:

```bash
for s in $STORES; do grep -hE '^cross-check: plan-stage high [0-9]+ ' "$s"/items/*.md; done | sort -k7,7 | head -8
```

- Fewer than 8 `high` lines: the stage offers `cross-checker`.
- 8, at least 2 of those first 8 with `<n>` of 1 or more: kept at high.
- Otherwise the same on the first 8 `xhigh` lines, offering `cross-checker-deep`; a short
  8 there drops the stage — no more plan-stage offers. The operator can still ask for one.

A move to xhigh or a drop is said once, under the Report's `open questions:`.

**Running one**, on the operator's yes:

- Record `dispatch: cross-checker fable <high | xhigh> — cross-check (<stage>); answer <N>`
  on the item that carries the answer. It is a **rider**, like a helper line
  (`record-lines.md`): no review round, and it never moves that item's cycle. It runs at
  its file's effort, never the session's, and is never resumed.
- **Plan, estate-wide and at-the-cap stages** review a plan, never a built diff; brief them
  with the plan-review variant (`review-brief.md`). Their accepted findings go to the build
  as § An offer never holds the build says. The plan and estate-wide stages are not offered when the opus `CLEAR` was review
  round 4: that is the cap, and only the at-the-cap stage runs there, as the operator's
  grant; its verdict and findings go back to the operator with the cap's decision, stop or
  continue.
- **Post-landing** reviews the base at the landing sha, recorded on the capability's
  parent item, or on a work item filed for it when there is none — never in the landed
  item's record. Its brief is the review-mode variant with a whole-capability intent:
  does it work for its operator. Its findings become follow-up work items and decisions;
  it never reverts a landing.
- One dispatch per accepted offer.
- A cross-check that cannot run — fable unavailable, or the agent lost — is dropped,
  never fallen back to opus: the opus `CLEAR` before it stands. Write its
  `cross-check: … dropped` line and name the drop under Step 6's `open questions:`, so
  the operator can accept it again; a resume finds a lost one the same way
  (`resume.md` § Phase lines and riders). A `cross-checker` file that is not loaded is
  not a drop: it falls back as any unpinned dispatch does (§ Fallback).

## Review waiver

Rule 5's one exception to a fresh reviewer: the orchestrator reviews the change itself.

**The test** — all of these, read off the full diff `git -C <workspace> diff
<base>...HEAD` at the HEAD about to be reviewed, never off the brief or the plan:

- Every changed file is a doc outside the agent layer: nothing under a plugin's
  `skills/`, `agents/`, `hooks/` or `.claude-plugin/` (skill assets and templates
  included), no skill text anywhere (`SKILL.md`, `references/`), not CLAUDE.md, not a
  script, test, config file or any code.
- Every changed line is pure prose: wording, formatting or alignment. None adds, removes
  or alters a command, a host, a path, a permission, a config value, or a rule agents
  follow.
- The mode is `full`. A `plan` series is rules its implementer follows, and `review
  <branch>` mode was asked for a reviewer: both always get one.
- No Model floor. An item with a `model:` pin or an `effort:` pin always gets a reviewer:
  at the `model:` pin's tier or above when there is one, otherwise `reviewer` at opus high
  (rule 8). The operator pinned the item, so it keeps its reviewer.

When in doubt, a reviewer. A later fix round is tested afresh on the cumulative diff: a
fix that makes an operational claim ends the waiver, and the next review is a fresh opus
reviewer with the full brief.

**The self-review** — the orchestrator reads the full diff, every hunk, runs every
command in `review-checklist.md` that applies and the Checks binding, and grades what it
finds on the review brief's severity scale. It fixes nothing (SKILL.md § Critical): a
finding goes to the implementer as a fix round, exactly as a reviewer's would. Record,
before the verdict:

```
review: self at <sha> — <why it qualifies, one clause>
verdict: <CLEAR | NEEDS_CHANGES> round <n> at <sha>
```

then, on `NEEDS_CHANGES`, the `findings:` block (`record-lines.md`). There is no
`dispatch:` or `agent:` pair: nothing was dispatched.

## Rounds

Fix round n = the nth re-dispatch or resume with review findings = review round n+1. The
cap is 4 review rounds — the first review plus three fix rounds; a fourth review without
`CLEAR` means the brief or the item is wrong, not the code: block the change and raise it
through the decision channel, with the justification `bindings.md` § Decisions gives an ask
for another round.

| Dispatch | Implementer tier |
|---|---|
| First run | per the tables above, or the Model floor's `model:` pin; an `effort:` pin picks the `-deep` file (rule 8) |
| Re-dispatch after `NEEDS_CONTEXT` | at least opus (opus signal) |
| A sonnet implementer, the fix round after a review with a critical or high finding | opus — a mechanical edit does not earn a critical or high |
| A sonnet implementer, fix round 2 | opus, whatever the severity — sonnet gets one fix round |
| Any other fix round | unchanged — the brief gets sharper, not the model |

Opus never bumps: fable is not a round tier. A tier only rises across rounds, never
falls, and a pinned tier never falls below its pin. Effort does not move by round: it
moves only with the file an effort pin, the trial, the step-down below the quota reserve
(§ Below the quota reserve) or § Reviewer effort by kind picks. A resumed agent keeps its
file, its model and its effort, so a change of file or model is a fresh dispatch with the
full brief and the prior findings pasted in; resume — SendMessage, the agent has the
context — only when both are unchanged (`fix-loop.md` § A NEEDS_CHANGES round). A
planner's rounds keep its file — `planner`, or `planner-deep` under an effort pin — and
inside a trial unit's window every planner round is fresh, in both arms (§ The xhigh
trial). The reviewer keeps its file throughout, except a `reviewer-light` that moves up
to `reviewer` (§ Reviewer effort by kind).

## The xhigh trial

Whether xhigh earns its cost on a plan that turns out hard is unmeasured: the record shows
no difference either way. The operator's answer (answer 123 a): **plans start at opus
high; when a plan turns out hard in its first or second review, its next planner round
runs at xhigh on half such plans, chosen by item id, as a two-week trial against the other
half; an item the operator pins always gets xhigh** (rule 8, never a trial unit). This
section is that trial. It routes plan rounds only; builds stay out, since they close a
median of one round after a late high. A window planner round due below the quota
reserve excludes its unit, in either arm (§ Below the quota reserve).

- **Unit.** A `plan` run whose **late high** (L) falls at plan-review round 1 or 2: at
  least one critical or two highs at round 1, or any high at round 2, read off the
  `verdict:` and `findings:` lines before the next planner dispatch. L at round 3 or later
  is not a unit, and routes as usual. Also **not a unit**, writing no `trial:` line and
  routing by its own rules:
  - an item with an `effort:` pin or a `model:` pin, which routes by its pins;
  - a target with no work item, which has no id to assign it by.
- **Assignment.** The item id's last hex digit: **even → bump, odd → control**. No shared
  state, so concurrent sessions cannot collide.
- **The window and the arms.** The window runs from the planner round after L until the
  plan is `CLEAR` or has had its third plan review. Every planner round in it is a
  **fresh** dispatch, never a resume, in both arms, the series carrying the context:
  - bump: `planner-deep` (opus xhigh), for every planner round in the window;
  - control: `planner` (opus high).

  The plan reviewer is `reviewer` (opus high) in both arms, so the arms differ in the
  planner's effort only. After the window, rounds route as usual.
- **Record.** Before the window's first planner dispatch, one line:
  `trial: xhigh-planner bump` or `trial: xhigh-planner control` (`record-lines.md`). Each
  window dispatch names its arm on its `dispatch:` line, such as
  `dispatch: planner opus xhigh — trial bump (L at round 1)`.
- **Check at each return.** When each window dispatch returns — every planner, and every
  plan reviewer, the last one included: the review whose verdict closes the window, the
  plan's `CLEAR` or its third plan review — read the effort its transcript ran at. Find
  the transcript by the dispatch's `agent:` id, never by rebuilding the project
  directory's name:

  ```bash
  f=$(find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects" -path "*/subagents/agent-<id>.jsonl")
  grep -o '"effort":"[a-z]*"' "$f" | sort | uniq -c
  ```

  A planner must show its arm's effort, `high` for control and `xhigh` for bump; a plan
  reviewer must show `high` in both arms. **The first mismatch excludes the unit** there
  and then, before its arm can read as full — at the window's last review, before the
  unit counts as closed: append
  `trial: xhigh-planner <bump | control> excluded — <reason>`, the reason naming the
  dispatch and the effort seen (`planner showed xhigh (fallback)`). The next unit of that
  parity takes its place.
  - A dispatch through the fallback (`general-purpose`, recorded `inherit`) counts only
    when its transcript shows its arm's effort.
  - This holds across sessions: a session that has not restarted since dev-flow gained its
    role agents still enrols units by parity, and a control it runs at the session's own
    effort is excluded, never miscounted.
- **Measure.** Whether the plan is **not `CLEAR` by its third plan review**. A plan
  `CLEAR` earlier counts as a hit.
- **Sample.** Exactly the first 6 units per arm, in the order of their L verdicts. An arm's
  units are the items carrying its `trial:` line, minus the items that also carry its
  exclusion, counted over **the trial's stores**: every work-item store `$WI estate` lists
  — the repos beside this one, this one included — each at its repo's `path` plus its
  `store`. A `wi` without `estate` leaves this repo's own store alone (`bindings.md`
  § Store).

  ```bash
  STORES=$($WI estate --json | python3 -c 'import json,sys; print("\n".join(r["path"] + "/" + r["store"] for r in json.load(sys.stdin)["repos"]))') || STORES=$WI_ROOT
  for s in $STORES; do
    grep -lx 'trial: xhigh-planner bump' "$s"/items/*.md             # the bump arm's lines...
    grep -l '^trial: xhigh-planner bump excluded' "$s"/items/*.md     # ...minus these
  done
  ```

  **The full-arm test** belongs to the trial routing step at enrolment, the moment L is
  read before the next planner dispatch (SKILL.md § Step 1): it counts the unit's arm
  first, and a unit whose arm already holds 6 routes as the control and writes no
  `trial:` line.
- **Pass and fail.** Pass: the bump arm misses `CLEAR` by the third plan review at least
  **3 fewer times** than the control arm (bump 2 of 6 against control 5 of 6, say). Fail:
  anything else. With no real effect a false pass is about 7% at worst (7.3% at a 50%
  base); if xhigh halves an 86% miss rate, the trial passes about 54% of the time. It
  detects only a large effect.
- **Close.** The same step owns it, at the return that closes a unit's window, once that
  return's check has passed: it counts both arms over the trial's stores. When each arm
  holds 6 units whose windows have all closed, that run's Report names the result and the
  counts under `open questions:`. A pass means every unit's window runs on `planner-deep`
  from then on; a fail means `planner-deep` runs only under an effort pin. Either result
  is a routing change made here, as a change of its own.
- **Pause.** If the review cap changes so that fewer than three plan reviews can run, or
  changes what a round is, the trial pauses until this section is re-read against it.

## Below the quota reserve

The operator's answer (answer 127 a, with 124's words): **below the operator's reserve,
the extra-deep opus tier steps down to high and fable offers wait until the reset. Pinned
items still ask.**

**Below the reserve** means the quota sense's reading shows a window spent down to its
reserve: `headroom` ≤ 0 in the **weekly** (`seven_day`) window (the `librarian-mode`
skill's `references/budget.md` § The numbers). The five-hour window never triggers it. A librarian uses its latest reading; a
standalone run takes one with that skill's `scripts/quota_budget.py --read-only`. No
signal reads as not below. Read it before each dispatch or offer the table names.

| What would run | Below the reserve |
|---|---|
| `planner-deep` with no pin — the trial's bump arm | `planner`, a fresh dispatch, recorded `dispatch: planner opus high — trial bump stepped down (below the quota reserve)` |
| Any trial window's planner round, either arm | the unit is excluded: `trial: xhigh-planner <bump \| control> excluded — below the quota reserve` (§ The xhigh trial), so both arms count only windows run above the reserve |
| A fable cross-check offer (§ Fable cross-checks) | waits: not raised until a reading is above the reserve again, after the reset; the Report's `open questions:` names it waiting. The build never waits for it |
| An accepted cross-check not yet dispatched | waits the same way; the operator's yes stands |
| An item's `effort: xhigh` or `model: fable` pin | asks through the decision channel: run at the pin now, or wait for the reset. Once per item until the reset: the answer covers the item's later dispatches until then |
| Reviewers, `implementer`, `implementer-critical`, `scribe`, `scout` | unchanged: no reviewer file runs above high, and a reviewer's file is set at its first review |

A step-down is not a hold and not a quota block (the `librarian-mode` skill's
`references/idle-turn.md`): dispatch goes on at high.

## Fallback

Two things can stop a routed dispatch from running as routed: its role agent is not
loaded, or fable is unavailable.

### A role agent not loaded

**Not loaded** means `dev-flow:<agent>` is missing from the session's agent list — the
agent types the Agent tool offers — or a call naming it fails as an unknown agent type:
dev-flow was updated without a restart, or not updated since the agent shipped.

- **A dispatch with no effort pin** falls back silently — a dispatch under a `model:` pin
  alone included, since the per-call `model` still carries that pin. Dispatch
  `general-purpose` with the routed `model`: it runs at the session's effort, and nothing
  better is available. Record `inherit` as the effort and name the missing agent after
  the signal — `dispatch: reviewer opus inherit — rule 4; dev-flow:reviewer not loaded` —
  and say it once under the Report's `open questions:`: "role agents not loaded;
  sub-agents run at the session's effort; update dev-flow and restart". Never block or
  ask over it.
- **A dispatch under an effort pin** never falls back silently. When `planner-deep` or
  `implementer-deep` is not loaded the pin cannot run, and it is asked through the
  decision channel as a fable pin is (below): update dev-flow and restart, then run; or run
  now on `general-purpose` at the session's effort, for the rest of this item. An answer
  of "run now" is recorded before the dispatch, naming the answer:

  ```
  dispatch: planner opus inherit — effort pin; dev-flow:planner-deep not loaded; answer <N>
  ```

  **It covers the rest of the item.** A file that is not loaded stays so until the
  session restarts, so asking again at every dispatch would only repeat the question. Each
  later dispatch on the item checks afresh: one that finds its `-deep` file loaded takes
  it; one that still does not runs on `general-purpose` the same way and names the same
  answer on its `dispatch:` line, never asking again. The answer is carried by those
  dispatch lines, not by the answer's own in-force window (`bindings.md` § Decisions).
  An answer to update and restart first leaves the item waiting until then.

### Fable unavailable

Only a pin puts a dev-cycle dispatch on fable by requirement, so only a pin can fail to
run for want of it. (A cross-check that cannot run is dropped — § Fable cross-checks.)

**Unavailable** means the Agent tool returns HTTP 429 or a usage-credits error (such as
"out of usage credits") for a fable call. Any other failure is not a fallback: it is the
agent's own `BLOCKED` or error, handled as such.

**A pin is never fallen back.** A `model: fable` Model floor is a human's own choice
(rule 8): an unavailable pinned tier is always asked through the decision channel —
wait for the reset, or run opus now — whatever the reset time. Put the reset time in the
question; take the first source that has one:

1. the error text, when it carries a reset time;
2. the status line's `rate_limits` in its sensor record,
   `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<session>.json` (the `statusline`
   plugin), else in the older context-guard state record,
   `${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/context-gate/<session>.json`, when present:
   the exhausted window's `resets_at` (epoch seconds). The record keeps its last
   `rate_limits` block when a later payload carries none, so check it before trusting
   it: a `resets_at` already in the past is stale and counts as no reset time; otherwise
   read the block's `at` (epoch seconds when its payload was read) and name its age in
   the question when it is over an hour old;
3. otherwise, unknown.

An answer of "opus now" is recorded before the dispatch, naming the answer; the agent file
stays the one routing chose, so the effort is its pin:

```
dispatch: <implementer|planner|reviewer> opus <effort> — fable pin unavailable (resets in <X>h); answer <N>
```

and Step 6's `verified:` line names it, e.g. `(impl fable→opus — pin waived, review
fable→opus — pin waived)`.

**Asking** is a decision like any other: it goes through the decision channel
(`bindings.md` § Decisions), recorded in the record sink first. A caller running several
pinned cycles in parallel sees fable run out one notification at a time: it asks once, on
the first 429, and lets that pending decision cover every later 429 in the same group
("fable out, resets in <X>; wait, or opus for items A, B, C") rather than raising one per
cycle; the one answer settles them all. Answer scope (`bindings.md` § Decisions) is read
per record, so the caller appends that one `decision N:` to each covered item's record
and its one `answer N:` to each as well: every copy is then in force on its own item
until that item's next phase line — the dispatch the answer chose — and a resume of any
one of them finds it answered. A standalone cycle has one change and asks once.

**A mid-run 429.** A background fable agent cut off mid-run may leave commits or edits in
its worktree. Whatever runs next continues from the worktree as it stands, never
discarding it: the orchestrator lists what the interrupted run committed
(`git log <reviewed sha>..HEAD`, or `<base>..HEAD` on a first run) and notes its
uncommitted edits (`git status --short`) in the brief, and re-dispatches on top of them.

An answer covers the dispatch it chose; the next one checks afresh and routes to fable
again once it is back. A fallback does not reset the round count.

## Recording

Before each Agent call, append one line to the record sink (Bash):

```
dispatch: <role> <model> <effort> — <the signal, or "default">
```

The fields, who writes the line (the cycle's roles, or a caller's helper line), and how a
line written before the effort field reads are `record-lines.md`'s, the one home of record
shapes. The effort is the dispatched file's pin, or `inherit` under § Fallback. The
trial's `trial:` lines: § The xhigh trial; the keep rule's `cross-check:` lines: § Fable
cross-checks.

The brief's `Model:` line carries the same model, so the agent's transcript and the item
agree. A self-review writes its `review: self` line instead (§ Review waiver). Step 6's
`verified:` line then names both:

```
verified: review CLEAR after 1 fix round (impl sonnet, review opus); <checks>
verified: review CLEAR after 0 fix rounds (impl sonnet, review self); <checks>
```

Name the final tiers; write `sonnet→opus` when a round bumped one, add `; fable
cross-check` after the tiers when one ran on the item (`; fable cross-check dropped` when
it was dropped), and mark
a waived pin as § Fallback shows. N counts fix rounds (see Rounds), so a first-pass
`CLEAR` is `after 0 fix rounds`.

## Worked examples

**"The implement skill's worktree section still says `.worktrees/`; align it with the
harness-native path."** One file, a path fix — a canonical kind in this kit repo; "align"
here names a path to match, not a trade-off. Implementer sonnet. It is skill text, so no
waiver: reviewer opus. Record:

```
dispatch: implementer sonnet medium — mechanical (path fix)
dispatch: reviewer opus high — rule 4
```

The reviewer returns `NEEDS_CHANGES` with one medium. Fix round 1 (review round 2):
implementer stays sonnet, resumed with the finding; the same reviewer is resumed. `CLEAR`.
Report: `verified: review CLEAR after 1 fix round (impl sonnet, review opus)`. Had review
round 2 failed too, fix round 2 re-dispatches the implementer fresh at opus with the full
brief and every findings list — a resumed agent keeps its model — and the opus reviewer
is resumed as before. Had review round 1 carried a high, fix round 1 would already have
gone to opus.

**"Reflow the install section of `docs/overview.md`; no content change," in a product
repo.** A doc, not skill text; every line wording and formatting, no command or path
moved. Implementer sonnet — wording outside a kit repo; in a kit repo it would be opus
(§ Implementer). Review waived. Record:

```
dispatch: implementer sonnet medium — mechanical (wording, no behaviour)
review: self at 4d5e6f — pure prose in docs/overview.md; no command, path or value moved
verdict: CLEAR round 1 at 4d5e6f
```

Report: `verified: review CLEAR after 0 fix rounds (impl sonnet, review self)`. Had the
reflow also corrected an install command, that line is an operational claim: a fresh
opus reviewer.

**"Add a PreToolUse hook that blocks edits to the main checkout from a worktree
session."** Executable logic: opus. Implementer opus; reviewer opus. That the hook
gates edits does not reach fable: the fresh opus review is the safeguard, not a dearer
implementer. A later "strip CRLF from that hook's input" is still executable logic: opus
for both roles. Had the operator called the hook critical, the build would run on
`implementer-critical` (`dispatch: implementer opus high — operator called it critical`).

**"Split ralph's backlog skills into their own plugin."** Marketplace shape: opus.
Implementer opus; reviewer opus. Had the item body carried `model: fable` (the Model
floor), both roles would run fable — the pin is a floor for every role on that item. Had
the split been planned first as a `plan` mode series redrawing the plugin boundaries — an
estate-wide plan — the orchestrator would offer, after the opus plan review's `CLEAR` on
the final serial, one fable xhigh cross-check, naming why: the plan moves a boundary every
repo's agents route by. Only on the operator's yes:

```
decision 41: fable-offer — Add a fable xhigh cross-check of the ralph split plan? It redraws plugin boundaries every repo's agents rely on — options: (a) add it (cross-checker-deep): one fable xhigh review of the final plan; its findings join the build's fix loop [recommended] | (b) go on without it: no fable spend; the opus CLEAR stands | (z) decide later: the build goes ahead; the offer stays open
answer 41: a
dispatch: cross-checker fable xhigh — cross-check (estate-wide plan); answer 41
```

The build starts without waiting for the answer. Had the operator answered (b), nothing
fable runs. Had
a `model: fable` pin written the plan, the offer would name a fresh `reviewer` at opus
high instead (the author rule).

**An item pinned `effort: xhigh`, planned and built.** The planner is `planner-deep`, and
the item is not a trial unit. Every build round is `implementer-deep` on opus, its
canonical-kind edits included. Every review stays on `reviewer`, and the review waiver
never applies:

```
dispatch: planner opus xhigh — effort pin
dispatch: reviewer opus high — plan review; the effort pin keeps reviewer
dispatch: implementer opus xhigh — effort pin
dispatch: reviewer opus high — rule 4
```

**A trial unit.** A `plan` item whose id ends `…4e1a` gets two highs at plan review
round 1: L at round 1, and `a` is even, so bump. Before the next planner round:

```
trial: xhigh-planner bump
dispatch: planner opus xhigh — trial bump (L at round 1)
```

The planner is fresh, not resumed. Its transcript shows `xhigh` at its return, and the
plan reviewer after it shows `high`. Had a session without the role agents dispatched that
round through the fallback at `high`, the unit would be out:
`trial: xhigh-planner bump excluded — planner showed high (fallback)`. Had the quota
reading shown the weekly window at its reserve when the round was due, the round would
step down, and the unit would be out the same way:

```
trial: xhigh-planner bump
dispatch: planner opus high — trial bump stepped down (below the quota reserve)
trial: xhigh-planner bump excluded — below the quota reserve
```

**A facts fix in a home-network repo.** "Correct brainboy's pool size in the
`mcfacehead-plugins` skill." A fact change in a home-network repo, no host config, no
security work, no pin: implementer sonnet (docs elsewhere), reviewer `reviewer-light`.
Had it also changed a systemd unit, the review would be `reviewer`:

```
dispatch: implementer sonnet medium — mechanical (a fact, no behaviour)
dispatch: reviewer opus medium — rule 4; fact and docs change in a home-network repo
```

**Product repo, a Go CLI whose Ground is the whole repo.** "Add a `--json` flag to
`list`." Code inside Ground: opus. Implementer opus; reviewer opus. Both briefs carry the
Checks binding (say `go test` over every package and `make lint`) and the Workflow
binding; a feature, so the implementer runs /investigate then /implement in its worktree,
each in its orchestrated mode (each skill's § Running under an orchestrator) — none of
their git or dialogs. "Fix a typo in the README": docs only, sonnet; pure prose, so
`review: self`. "Let `run` bind-mount the host's docker socket": code and a security
surface, opus for both roles. Item body for the first:

```
dispatch: implementer opus medium — code inside a product repo's Ground
dispatch: reviewer opus high — rule 4
```

**Role agents not loaded.** A session started before dev-flow gained its role agents
routes as usual and dispatches `general-purpose` with the routed model:

```
dispatch: implementer opus inherit — code inside a product repo's Ground; dev-flow:implementer not loaded
```

The Report's `open questions:` says once that the role agents are not loaded. An item
under an effort pin asks instead (§ Fallback).

**Fallback: a `model: fable` pin, fix round 2.** The item has run fable from its first
dispatch; at fix round 2 the Agent call returns HTTP 429 "out of usage credits", and the
sensor record's `rate_limits` shows the window resetting in 5 hours. A pin is never fallen
back: the orchestrator asks through the decision channel — wait about 5h, or opus now. The
operator answers opus now (answer 7). Record:

```
dispatch: implementer opus medium — fable pin unavailable (resets in 5h); answer 7
```

Report: `verified: review CLEAR after 2 fix rounds (impl fable→opus — pin waived, review
fable→opus — pin waived); <checks>`.
