# Model routing

Signal tables and worked examples for SKILL.md § Step 2 (Route). The eight rules there
are the contract; this file is how to apply them without re-deriving them per dispatch.
It is the one home of dev-cycle's routing, and of every caller that runs dev-cycle as its
cycle spec (`librarian-mode`). It routes the planner, implementer and reviewer of a
development cycle only: the research skills (`research`, `research-deep`,
`research-refine`, `research-prune`) and their `research-lane` and `research-verifier`
agents keep their own routing, and nothing here governs them.

## Why route at all

A sub-agent inherits the parent's model unless the Agent tool's `model` field says
otherwise, and that field wins over everything else. The orchestrator often runs on the
dearest tier, so an unrouted dispatch is the dearest dispatch — every implementer, every
reviewer, every helper. Per million tokens the tiers sit roughly at fable 10/50, opus
5/25, sonnet 2/10 (in/out). The brief constrains the work tightly enough that a cheap
failure costs a re-dispatch, not a landing; the review is where the cycle spends, and it
spends on opus.

Mechanism: pass `model: "sonnet"`, `"opus"` or `"fable"` on every Agent call. Haiku is
out of scope — the checks it could run, the orchestrator runs itself.

## Implementer

Sonnet when every edit in the change is mechanical; opus on any one opus signal. When a
change is not plainly mechanical, it is opus.

### Sonnet — every edit one of these

| Edit | Reads as |
|---|---|
| Pointer or path fix | a reference, link or path corrected to where the thing already is |
| Frontmatter | a `name`, `description` or other key edited to the house rule, the skill's behaviour unchanged |
| Catalog row | a README catalog row or CLAUDE.md layout line brought in line with what already exists |
| Wording that changes no behaviour | a typo, a clearer sentence, formatting, alignment — no rule, command or value moves |

Breadth alone does not raise the tier: the same pointer fix across five files is still
mechanical.

### Opus — any one signal

| Signal | Reads as |
|---|---|
| Behaviour | a change to what a skill, agent, CLAUDE.md or doctrine rule does — a new step, a changed rule, a new case |
| A format bump | a record, file or report format gains, loses or changes a field |
| Executable logic | a hook, anything under `scripts/`, tests, a status line, a `settings.json` write; in a product repo, any code inside Ground |
| Marketplace shape beyond a row | `marketplace.json`, a plugin added, split, moved or retired |
| Judgement in the item | the body records a real trade-off, or the acceptance uses words like coherent, align, reconcile |
| A prior `NEEDS_CONTEXT` return | the first run could not settle it from the brief alone |

A planner is opus at least (SKILL.md § Step 1): a plan is judgement.

### Fable

Fable is no implementer tier by signal: no size, surface or round routes an implementer to
it. It runs only when a human names it — a `model: fable` Model floor (rule 8), which runs
every role on fable — or as the reviewer's second opinion (§ Second opinion).

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
a different model from a sonnet implementer are what make the review worth its cost.

| Implementer | Reviewer |
|---|---|
| sonnet | opus |
| opus | opus |
| fable (a pin) | fable (the pin is a floor for every role) |

A sonnet reviewer never exists. The reviewer's tier does not follow the implementer's
bumps: it is opus from the first round to the last, so the same reviewer is resumed for
its own re-reviews (it has seen only reviews). `review <branch>` mode has no implementer;
its reviewer is opus all the same.

### Second opinion

On a complex plan an opus agent made — a `plan` mode series, or a feature whose opus
implementer planned it in its worktree — for greenfield architecture or a major refactor,
the orchestrator may add one fresh fable reviewer after the opus reviewer's `CLEAR`. It is
a second reviewer, never a substitute: the opus review runs first and in full. It is
optional and never for a text change.

- Brief it as the next review round: the full brief, or the plan-review variant for a
  series (`resume.md` § The reduction, VARIANT). Record
  `dispatch: reviewer fable — second opinion (<greenfield | major refactor>)`.
- Its verdict is a review round like any other: it counts toward the cap, and a
  `NEEDS_CHANGES` opens a fix round whose re-review resumes the fable reviewer.
- One per cycle. Once it is `CLEAR`, the cycle goes on from that verdict, as from any
  `CLEAR`.
- A second opinion that cannot run — fable unavailable, or the agent lost — is dropped,
  never fallen back to opus and never asked about: the opus `CLEAR` before it stands
  (`resume.md` § The state table, S3b). Name the drop under Step 6's `open questions:`.

## Review waiver

Rule 5's one exception to a fresh reviewer: the orchestrator reviews the change itself.

**The test** — all of these, read off the full diff `git -C <workspace> diff
<base>...HEAD` at the HEAD about to be reviewed, never off the brief or the plan:

- Every changed file is a doc: not skill text (`SKILL.md`, anything under
  `references/`), not CLAUDE.md, not an agent definition, not a script, test, hook,
  config file or any code.
- Every changed line is pure prose: wording, formatting or alignment. None adds, removes
  or alters a command, a host, a path, a permission, a config value, or a rule agents
  follow.
- The mode is `full`. A `plan` series is rules its implementer follows, and `review
  <branch>` mode was asked for a reviewer: both always get one.

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
through the decision channel.

| Dispatch | Implementer tier |
|---|---|
| First run | per the tables above, or the Model floor |
| Re-dispatch after `NEEDS_CONTEXT` | at least opus (opus signal) |
| A sonnet implementer, the fix round after a review with a critical or high finding | opus — a mechanical edit does not earn a critical or high |
| A sonnet implementer, fix round 2 | opus, whatever the severity — sonnet gets one fix round |
| Any other fix round | unchanged — the brief gets sharper, not the model |

Opus never bumps: fable is not a round tier. A tier only rises across rounds, never
falls, and a pinned tier never falls below its pin. A resumed agent keeps its model, so a
bump is a fresh dispatch with the full brief and the prior findings pasted in; resume —
SendMessage, the agent has the context — only when the tier is unchanged. The reviewer
stays opus throughout.

## Fallback

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

An answer of "opus now" is recorded before the dispatch, naming the answer:

```
dispatch: <implementer|reviewer> opus — fable pin unavailable (resets in <X>h); answer <N>
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
dispatch: <implementer|reviewer> <sonnet|opus|fable> — <the signal, or "default">
```

The brief's `Model:` line carries the same value, so the agent's transcript and the item
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
harness-native path."** One file, a path fix — mechanical; "align" here names a path to
match, not a trade-off. Implementer sonnet. It is skill
text, so no waiver: reviewer opus. Record:

```
dispatch: implementer sonnet — mechanical (path fix)
dispatch: reviewer opus — rule 4
```

The reviewer returns `NEEDS_CHANGES` with one medium. Fix round 1 (review round 2):
implementer stays sonnet, resumed with the finding; the same reviewer is resumed. `CLEAR`.
Report: `verified: review CLEAR after 1 fix round (impl sonnet, review opus)`. Had review
round 2 failed too, fix round 2 re-dispatches the implementer fresh at opus with the full
brief and every findings list — a resumed agent keeps its model — and the opus reviewer
is resumed as before. Had review round 1 carried a high, fix round 1 would already have
gone to opus.

**"Reflow the install section of `docs/overview.md`; no content change."** A doc, not
skill text; every line wording and formatting, no command or path moved. Implementer
sonnet; review waived. Record:

```
dispatch: implementer sonnet — mechanical (wording, no behaviour)
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
for both roles.

**"Split ralph's backlog skills into their own plugin."** Marketplace shape: opus.
Implementer opus; reviewer opus. Had the item body carried `model: fable` (the Model
floor), both roles would run fable — the pin is a floor for every role on that item. Had
the split been planned first as a `plan` mode series redrawing the plugin boundaries, the
orchestrator could add a fable second opinion after the opus plan review's `CLEAR`.

**Product repo, a Go CLI whose Ground is the whole repo.** "Add a `--json` flag to
`list`." Code inside Ground: opus. Implementer opus; reviewer opus. Both briefs carry the
Checks binding (say `go test` over every package and `make lint`) and the Workflow
binding; a feature, so the implementer runs /investigate then /implement in its worktree,
each in its orchestrated mode (each skill's § Running under an orchestrator) — none of
their git or dialogs. "Fix a typo in the README": docs only, sonnet; pure prose, so
`review: self`. "Let `run` bind-mount the host's docker socket": code and a security
surface, opus for both roles. Item body for the first:

```
dispatch: implementer opus — code inside a product repo's Ground
dispatch: reviewer opus — rule 4
```

**Fallback: a `model: fable` pin, fix round 2.** The item has run fable from its first
dispatch; at fix round 2 the Agent call returns HTTP 429 "out of usage credits", and the
sensor record's `rate_limits` shows the window resetting in 5 hours. A pin is never fallen
back: the orchestrator asks through the decision channel — wait about 5h, or opus now. The
operator answers opus now (answer 7). Record:

```
dispatch: implementer opus — fable pin unavailable (resets in 5h); answer 7
```

Report: `verified: review CLEAR after 2 fix rounds (impl fable→opus — pin waived, review
fable→opus — pin waived); <checks>`.
