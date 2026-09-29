# Model routing

Signal tables and worked examples for SKILL.md § Step 2 (Route). The eight rules there
are the contract; this file is how to apply them without re-deriving them per dispatch.
It is the one home of dev-cycle's routing, and of every caller that runs dev-cycle as its
cycle spec (`librarian-mode`). It routes the dispatches of a development cycle — planner,
implementer, reviewer, and the second opinion's cross-checker — and the helper and
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
effort. The model is the file's default, and the per-call `model` moves it. A cell marked
(default) is the routing in force while the operator has not chosen otherwise for that
stage; another choice changes that row here.

| Agent | Pin: model / effort | Dispatched when |
|---|---|---|
| `scribe` | sonnet / low | a helper with no judgement on its dispatch line: render a decision card, fill a brief from its template, summarise given text |
| `scout` | sonnet / medium; `model: opus` on the call after a sonnet `scout` returned "could not determine" on a question the work depends on | a read-only question: locating code, read-and-reason, a diagnostic — a question that asks for a plan goes to a planner instead |
| `implementer` | sonnet / medium; `model: opus` on any opus signal; `model: fable` under a pin | every implementer dispatch the two rows below do not take: sonnet for the canonical kinds in a kit repo, and for wording and docs elsewhere; opus otherwise (§ Implementer) |
| `implementer-critical` | opus / high | an implementer dispatch on work the operator called critical (§ Critical work) |
| `implementer-deep` | opus / xhigh | an implementer dispatch under an `effort: xhigh` pin (SKILL.md § Step 2 rule 8) |
| `planner` | opus / high | every plan dispatch not sent to `planner-deep`, from the first; the trial's control arm (default, § The xhigh trial) |
| `planner-deep` | opus / xhigh | a plan dispatch under an `effort: xhigh` pin (rule 8); the trial's bump arm (default, § The xhigh trial) |
| `reviewer` | opus / high | every review and every plan review, at high whatever the change (default) |
| `cross-checker` | fable / high | the optional second opinion after an opus `CLEAR` (default, § Second opinion) |
| `cross-checker-deep` | fable / xhigh | none under the defaults |

- **xhigh runs only on the three `-deep` files**, and every dispatch of one names its
  signal on its `dispatch:` line: the effort pin, or the trial's bump arm. No reviewer file
  runs above high, and an effort pin never reaches a reviewer.
- **The two pins compose.** A plan with both `effort: xhigh` and `model: fable` is
  `planner-deep` with `model: fable` (rule 8).
- **A caller's own helpers and questions** — a decision card, a filled brief, a summary; a
  `dig into` or a diagnostic — go to `scribe` and `scout` by the rows above, recorded like
  any dispatch (§ Recording).

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

When the operator called the work critical — in the item body, or in the request it was
filed from — every implementer dispatch on it, fix rounds included, goes to
`implementer-critical`: opus high, one tier and one effort for the whole build. Its plan
stays on `planner`: "critical" raises the build's effort, not the plan's. Under an effort
pin the build is `implementer-deep` instead (rule 8).

### Fable

Fable is no implementer tier by signal: no size, surface or round routes an implementer to
it. It runs only when a human names it — a `model: fable` Model floor (rule 8), which runs
every role on fable — or as the cross-checker's second opinion (§ Second opinion).

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

Always opus, always fresh, always the `reviewer` file (opus high): a new sub-agent that
never saw the implementer's conversation. Never a fork of the orchestrator or the
implementer, never the implementer resumed as its own reviewer, never the orchestrator
itself — except § Review waiver. A fresh context and a different model from a sonnet
implementer are what make the review worth its cost.

| Implementer | Reviewer |
|---|---|
| sonnet | `reviewer`, opus |
| opus (any implementer file) | `reviewer`, opus |
| fable (a pin) | `reviewer`, fable (the pin is a floor for every role) |

A sonnet reviewer never exists. The reviewer's tier does not follow the implementer's
bumps, and its effort does not follow an effort pin: it is `reviewer` at opus from the
first round to the last, so the same reviewer is resumed for its own re-reviews (it has
seen only reviews). `review <branch>` mode has no implementer; its reviewer is `reviewer`
at opus all the same.

### Second opinion

On a complex plan an opus planner made — a `plan` mode series whose subject is
greenfield architecture or a major refactor — the orchestrator may add one fresh
cross-check after the opus reviewer's `CLEAR` on the series: the `cross-checker` file,
fable high (default). It runs at the file's high, not at the session's effort that a
second opinion inherited before the role agents. It is a second reviewer, never a
substitute: the opus review runs first and in full. It reviews a plan, never a built
diff, and never a text change; a feature that wants one is planned first in `plan` mode.
It is optional.

- Not when the opus `CLEAR` was review round 4: a second opinion never pushes past the
  cap.
- Brief it with the plan-review variant (`review-brief.md`). Record
  `dispatch: cross-checker fable high — second opinion (<greenfield | major refactor>)`.
- Its verdict is a review round like any other and counts toward the cap. A
  `NEEDS_CHANGES` opens a fix round whose re-review goes to the **opus** reviewer — the
  last `agent: reviewer` line — resumed, with the cross-check's findings pasted for
  verification; the cross-checker is never resumed, so every fix lands under an opus
  review.
- One per cycle, one dispatch. Its `CLEAR` goes on as any `CLEAR` does.
- A second opinion that cannot run — fable unavailable, or the agent lost — is dropped,
  never fallen back to opus and never asked about: the opus `CLEAR` before it stands
  (`resume.md` § The state table, S3b). Name the drop under Step 6's `open questions:`.
  A `cross-checker` that is not loaded is not a drop: it falls back as any unpinned
  dispatch does (§ Fallback).

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
moves only with the file an effort pin or the trial picks. A resumed agent keeps its
file, its model and its effort, so a change of file or model is a fresh dispatch with the
full brief and the prior findings pasted in; resume — SendMessage, the agent has the
context — only when both are unchanged (`fix-loop.md` § A NEEDS_CHANGES round). A
planner's rounds keep its file — `planner`, or `planner-deep` under an effort pin — and
inside a trial unit's window every planner round is fresh, in both arms (§ The xhigh
trial). The reviewer stays `reviewer` throughout.

## The xhigh trial

Whether xhigh earns its cost on a plan that turns out hard is unmeasured: the record shows
no difference either way. Until the operator settles when xhigh runs, planners run this
trial (default). It routes plan rounds only; builds stay out, since they close a median of
one round after a late high.

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
  plan reviewer — read the effort its transcript ran at:

  ```bash
  grep -o '"effort":"[a-z]*"' <session dir>/subagents/agent-<id>.jsonl | sort | uniq -c
  ```

  `<id>` is the dispatch's `agent:` id. `<session dir>` is
  `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<project>/<session id>`, where `<project>` is
  the dispatching session's working directory with every `/` written `-`. A planner must
  show its arm's effort, `high` for control and `xhigh` for bump; a plan reviewer must
  show `high` in both arms. **The first mismatch excludes the unit** there and then,
  before its arm can read as full: append
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
  exclusion, counted over every store whose cycles run the trial:

  ```bash
  grep -lx 'trial: xhigh-planner bump' items/*.md          # the bump arm's lines...
  grep -l '^trial: xhigh-planner bump excluded' items/*.md  # ...minus these
  ```

  A later unit whose arm is already full routes as the control and writes no `trial:`
  line.
- **Pass and fail.** Pass: the bump arm misses `CLEAR` by the third plan review at least
  **3 fewer times** than the control arm (bump 2 of 6 against control 5 of 6, say). Fail:
  anything else. With no real effect a false pass is about 7% at worst (7.3% at a 50%
  base); if xhigh halves an 86% miss rate, the trial passes about 54% of the time. It
  detects only a large effect.
- **Close.** When both arms hold 6 units and each has reached `CLEAR` or its third plan
  review, report the counts to the operator. A pass means every unit's window runs on
  `planner-deep` from then on; a fail means `planner-deep` runs only under an effort pin.
  Either result is a routing change made here.
- **Pause.** If the review cap changes so that fewer than three plan reviews can run, or
  changes what a round is, the trial pauses until this section is re-read against it.

## Fallback

Two things can stop a routed dispatch from running as routed: its role agent is not
loaded, or fable is unavailable.

### A role agent not loaded

**Not loaded** means `dev-flow:<agent>` is missing from the session's agent list — the
agent types the Agent tool offers — or a call naming it fails as an unknown agent type:
dev-flow was updated without a restart, or not updated since the agent shipped.

- **An unpinned dispatch** falls back silently. Dispatch `general-purpose` with the routed
  `model`: it runs at the session's effort, and nothing better is available. Record
  `inherit` as the effort and name the missing agent after the signal —
  `dispatch: reviewer opus inherit — rule 4; dev-flow:reviewer not loaded` — and say it
  once under the Report's `open questions:`: "role agents not loaded; sub-agents run at the
  session's effort; update dev-flow and restart". Never block or ask over it.
- **A dispatch under an effort pin** never falls back silently. When `planner-deep` or
  `implementer-deep` is not loaded the pin cannot run, and it is asked through the
  decision channel as a fable pin is (below): update dev-flow and restart, then run; or run
  now on `general-purpose` at the session's effort. An answer of "run now" is recorded
  before the dispatch, naming the answer:

  ```
  dispatch: planner opus inherit — effort pin; dev-flow:planner-deep not loaded; answer <N>
  ```

### Fable unavailable

Only a pin puts a dev-cycle dispatch on fable by requirement, so only a pin can fail to
run for want of it. (A second opinion that cannot run is dropped — § Second opinion.)

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

- `<role>` is the role word: `scribe`, `scout`, `implementer`, `planner`, `reviewer` or
  `cross-checker`.
- `<model>` is the per-call `model`: `sonnet`, `opus` or `fable`.
- `<effort>` is the dispatched file's pin — `low`, `medium`, `high` or `xhigh` — or
  `inherit` when the fallback dispatched `general-purpose` (§ Fallback). Role and effort
  together name the file, since each file is one role at one effort: `planner xhigh` is
  `planner-deep`, `implementer high` is `implementer-critical`.

A line written before the effort field existed, its model followed directly by the `—`,
reads as effort unrecorded (`record-lines.md`). The trial's `trial:` lines: § The xhigh
trial.

The brief's `Model:` line carries the same model, so the agent's transcript and the item
agree. A self-review writes its `review: self` line instead (§ Review waiver). Step 6's
`verified:` line then names both:

```
verified: review CLEAR after 1 fix round (impl sonnet, review opus); <checks>
verified: review CLEAR after 0 fix rounds (impl sonnet, review self); <checks>
```

Name the final tiers; write `sonnet→opus` when a round bumped one, `opus+fable` for the
reviewer when a second opinion ran (`opus, fable dropped` when it was dropped), and mark
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
the split been planned first as a `plan` mode series redrawing the plugin boundaries, the
orchestrator could add a fable second opinion after the opus plan review's `CLEAR`:

```
dispatch: cross-checker fable high — second opinion (major refactor)
```

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
`trial: xhigh-planner bump excluded — planner showed high (fallback)`.

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
