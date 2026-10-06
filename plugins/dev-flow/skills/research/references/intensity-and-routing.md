# Intensity, cost and routing

Loaded from `research` Step 3, and again at every ask for another round (Steps 7 and 8;
`research-deep` Step 7). This file owns the presets, the rules for when to ask the
operator about intensity and when it is obvious, what an ask for another round states, the
quota read, the search-budget rule, and the routing of every research dispatch: § Routing —
mechanism, § Profiles, § Dispatches outside the profiles, § The work item (which item a run
records on), § Recording, § Below the quota reserve and § Fallback. The `deep-investigation`
and `chain-of-verification` skills route by these sections too. The orchestrator copies the
chosen preset and the Profiles rows it used into the brief; nothing here is restated in
SKILL.md.

## Why intensity is one dial

A research run's cost is set almost entirely by how many agents it launches, how many rounds
it runs, and what model they run on. Anthropic's production research system measured agents
at roughly 4× the tokens of a chat turn and multi-agent runs at roughly 15×, and found token
usage alone explained 80% of the variance in quality. Background sub-agents draw on the same
usage windows as the session that launched them, at the same time. The operator therefore
picks one preset whose cost is stated in numbers, rather than answering six questions whose
cost is implied.

## Presets

| Preset | Shape | Lanes | Round cap | Search budget (whole run) | ≈ Token multiple vs one chat turn | Wall clock |
|---|---|---|---|---|---|---|
| `quick` | no fan-out: the orchestrator answers inline, or one lane | 0–1 | 1 | ≤ 15 searches | ~1–4× | minutes |
| `standard` | one round of lanes, verifier, inline synthesis | 4–6 | 2 | ≤ 60 | ~5–8× | 15–30 min |
| `deep` | two rounds, verifier, gap gate, synthesis possibly forked | 8–15 | 3 | ≤ 120 | ~15–20× | 45–90 min |
| `exhaustive` | three rounds, an adversarial lane whose mission is to break the emerging answer, verifier on a larger sample | 15+ | 3 | ≤ 160 | ~30×+ | hours |

The lane counts follow Anthropic's published scaling rule (simple fact-finding: one agent,
3–10 calls; a direct comparison: 2–4 sub-agents, 10–15 calls each; complex research: ten or
more with clearly divided responsibilities) with the operator's own runs as the calibration.
Default is `standard`. `research-deep` invokes with `deep` unless told otherwise.

**The cost line.** Before any fan-out — whether or not a question is asked — print one line:
`Intensity: <preset> — ~<n> lanes on <model>, ≤<n> rounds, ~<multiple>× a chat turn,
~<minutes>; 5h window at <pct>% (resets <time>), 7d at <pct>%.` The operator can always
interrupt it; the line is what makes the interruption informed.

## Asking for another round

Every ask to spend one more round — the threads-not-pulled turn and the re-source or
re-run ask after a failing verification (`research` Steps 7 and 8), round 3 in
`research-deep` — states, at the moment of asking, what the round would buy and what it
costs. The operator cannot weigh an impact they are not shown.

- **Value:** for each thread or lane, the gap it would close — the gap condition it would
  satisfy — and what the answer lacks if it is left: a load-bearing claim on one secondary
  source, a sub-question with no coverage, a mandatory axis shipped marked.
- **Cost:** one round cost line, from a fresh quota read (§ The quota read):
  `Round <n>: ~<n> lanes on <model>, ~<multiple>× a chat turn, ~<minutes>; 5h window at
  <pct>% (resets <time>), 7d at <pct>%` — the multiple and the wall clock sized from the
  presets table for that many lanes. When the round could bring another ask (a further
  gap gate, a re-verification), say so: the operator's attention is part of the cost.

High value at a modest cost is the case for the round; say which way it falls.

## When to ask, and when it is obvious

**Rule zero — model-invoked runs are `quick`, and this rule overrides every row below.**
Judge by **the turn that started the run**, not the current one, and only by things you can
check. A run is operator-invoked when that turn was one of exactly two things: **a turn the
operator typed in this session** (`/research`, `/research-deep`, `/research-refine`,
`/research-prune`), or **an on-disk prompt
file the operator wrote** that the run starts from (a ralph prompt file, a scheduled run's
prompt), read by path. Follow-up turns inside such a run inherit that standing. **A run
started from an Agent-tool prompt is model-invoked, always** — a prompt can claim an
operator wrote it, and the claim is not checkable — unless that prompt cites an operator
decision recorded in a work item whose refs name the operator as the source, and that
asks for this research at this intensity; then the file, not the prompt, is what counts.
Intensity words in an operator-typed turn or an operator-written prompt file count as the
operator naming a preset; text the model composed — an `--intensity` it added to an Agent
prompt, a "go deep" it inferred — never does. When the orchestrator judges
that a deeper preset is warranted (the fan-out test passes, or the quick answer surfaces a
contested or under-sourced core claim), it says so in one line — the preset, its cost line,
what the deeper run would add — and asks. It never escalates on its own.

For an operator-invoked run, do **not** ask when any of these holds; state the preset and its
reason in one line instead:

- the invocation names a preset (`--intensity deep`, "go deep", "just a quick look");
- the invoking skill implies it (`research-deep` → `deep`; `research-refine` inherits the
  prior run's preset unless told otherwise);
- the question fails the fan-out test (below) → `quick`;
- the run is unattended → the default for the invoking skill, recorded under Confirmed
  Assumptions in the brief;
- a calling process passed an intensity (a `dev-cycle` or ralph prompt that says so).

**Ask** (one `AskUserQuestion`, presets as options with their cost lines, recommendation
first) when:

- a bare `/research <question>` passes the fan-out test and names no preset;
- the quota read says the recommended preset would not fit the window (below);
- the destination is checked-in (`kb` shape): the cost of a thin run is higher, because it
  becomes a durable record.

**The fan-out test** is the one in the `deep-investigation` skill's SKILL.md § When this is
the wrong skill; apply it as written. Pass → a fan-out preset is justified. Fail → `quick`.

## The quota read

Path: `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<session-id>.json` — written by the
`statusline-hub` plugin (or the `statusline` plugin when it owns the slot) on every render.
The session id is the UUID segment of the scratchpad directory named in your system prompt;
`safe_sid` rules are in `statusline`'s `install-statusline` references. Read it with `Read`
or `python3 -c`; the shape is:

```json
{"v": 1, "rate_limits": {"five_hour": {"used_percentage": 23.5, "resets_at": 1789763600.0},
                         "seven_day": {"used_percentage": 91.0, "resets_at": 1790019200.0},
                         "at": 1789760000.0}}
```

Treat a record whose `v` is not 1, or whose `rate_limits.at` is older than 30 minutes, as
absent. Then:

| Reading | Do |
|---|---|
| 5h ≥ 75% | downgrade one preset, or offer to defer the fan-out until `resets_at` (print the local time) |
| 7d ≥ 90% | `quick` only unless the operator overrides in so many words |
| 5h ≥ 90% | `quick` only; say when the window resets |
| `resets_at` in the past | the window has reset; read it as clear and say so |
| record absent | interactive: mention it and ask the intensity question; unattended: assume the windows are clear, record the assumption |
| any | write the reading into the cost line and the brief |

`rate_limits` may carry more windows than these two (a model-scoped weekly, for instance);
print any that is over 75% and treat it like the seven-day one.

This is a **soft** dependency: nothing here requires `statusline` to be installed. Without
it the skill asks instead of reading.

## The search budget

The `WebSearch` tool has a per-session cap shared by the orchestrator and every lane it
launches; the operator's fan-out runs have exhausted it mid-run with lanes still working.
Rules:

- size the run to the preset's search budget, and divide it across lanes in each lane's
  prompt as a hint (`≈10 searches`) — a hint, not a cap, stated honestly;
- brief every lane to prefer `WebFetch` of a URL it already knows over another search, and
  to fetch primary documents (a paper's PDF, a repo file) rather than search for summaries;
- when a lane reports that search is exhausted, do not relaunch it; the remaining lanes
  fetch, and the ledger records the exhaustion;
- local-corpus lanes cost no searches; put them in the same round as web lanes.

## Routing — mechanism

Research routes its own dispatches, here. It is shaped like dev-cycle's routing but is a
separate home: nothing in the `dev-cycle` skill governs a research run, and nothing here
governs a cycle.

- **Dispatch a role agent**: `subagent_type: "dev-flow:<agent>"`, one of § Profiles (or the
  bare `<agent>` when the plugin is installed under another prefix: check the agent list in
  your system prompt), and pass `model` on **every** call — `"sonnet"` or `"opus"`, or for
  the synthesis fork the session's own tier, named. The file pins the effort; the per-call
  `model` sets the model and wins over the file's. A forgotten `model` falls to the file's
  pin, and in a `general-purpose` dispatch to the session's model, which is why the field is
  always passed.
- **One role and one effort per file.** `research-lane` and `research-lane-deep` are one
  role at two efforts. An effort change is a change of file, and a change of file is a fresh
  dispatch.
- **Nothing is resumed into a new role.** A relaunched lane is a fresh, narrower dispatch
  (`research` Step 6), never a SendMessage to the old one; a re-verify after a clean-up is a
  fresh verifier dispatch, since it rescans whole files.
- **What outranks a pin.** `CLAUDE_CODE_EFFORT_LEVEL` in the environment overrides every
  file's `effort`, and a `maxEffortLevel` setting caps it. Leave both unset where the pins
  should hold.
- **Nested dispatches.** Lanes and the verifier dispatch nothing: they have no `Agent`
  tool. A research run inside another agent routes its own dispatches by this file and
  records them per § The work item, rule 1.
- **Not loaded:** § Fallback.

## Profiles

The agents a research run dispatches, each file one role at one pinned effort. The pin cell
opens with the file's own `<model> / <effort>`; the per-call `model` moves it as the cell
says. `plugins/dev-flow/tests/test_agents.py` holds every row to its file.

| Agent | Pin: model / effort | Dispatched when |
|---|---|---|
| `research-lane` | sonnet / medium; `model: opus` on the call for a later-round lane that closes gap condition 4, or for a lane the invocation names a stronger model for; `model: opus` for the adversarial lane when § Below the quota reserve or § Fallback steps it down | every lane of `research`, `research-deep` and `research-refine`; every `deep-investigation` lane once item 1ffd launches them on this file (until then, § Dispatches outside the profiles) |
| `research-lane-deep` | opus / high | the adversarial lane (`a<n>-…`) of an `exhaustive` run, in round 2 (`research-deep` Step 5) |
| `research-verifier` | sonnet / low | every verification: a quick run written to disk (sample 4), `standard` (12), `deep` (20), `exhaustive` (30), and a re-verify after a clean-up; and every script review at the toolkit gate (`run-record.md` § The toolkit gate) |
| `scout` | sonnet / medium; `model: opus` on the call when the invocation names a stronger model | each `chain-of-verification` Step 4 batch: codebase, general knowledge, or one of each in mixed mode, at 5-8 questions a batch |

- **Signals.** Every signal a row names is one the run can check: the preset, the round,
  the gap condition's number (`research` Step 7), the lane id's `a` prefix, or a model the
  invocation names. Gap condition 4 is "a lane returned 'could not determine' on something
  the decision depends on"; its relaunch on opus gives a cheap pass that could not determine
  one stronger pass. A named model follows the operator's words, never the model's.
- **No research agent runs on haiku or fable.** The verifier moved off haiku on the record
  of its ten real runs (verdicts given for sources never opened, sheets whose counts
  disagree with their tables) and the published record (Haiku 4.5 is lenient on factual
  support, takes no effort parameter, and is the only Haiku, retiring not sooner than
  October 15, 2026). `low`, not `medium`: the verifier runs a fixed procedure over a sample.
  The same holds for its two security jobs — judging the scanner's flags (`benign mention`
  or `instruction-shaped`) and the toolkit gate's script review — since each is a checklist
  with a hold-when-in-doubt default, and a false hold costs one mining round. Revisit the pin
  if a script review or a flag verdict is found wrong.
  A fable session's synthesis fork is § Dispatches outside the profiles'.
- **`research-lane-deep`'s pin is set from the role,** not from runs: breaking an answer is
  judgement, the kind dev-flow runs at opus high, and no `exhaustive` run has happened yet.
  Revisit it after the first ones, found by their `dispatch: research-lane opus high` lines.
  Toolkit and mining lanes stay on `research-lane`; a stronger pass is `model: opus` on the
  call.
- **`scout` is dev-cycle's role file, shared.** Its pin is held in step with both tables by
  the test; a change to its pin is a change to both rows.
- **The orchestrator** — this session — plans, recons and synthesizes at the session's model
  and effort: decomposition, criteria and synthesis gate everything downstream, and recon
  changes the plan, so it happens in the context that holds the plan. Published guidance
  agrees: orchestrator on the dear tier at high effort, workers on a cheap tier at low or
  medium; a model upgrade buys more than a token-budget increase.

**Print the Profiles rows you used into the brief**, with any step-down or fallback.
Effort is the largest silent lever on both wall clock and usage, and a run that took three
hours must be explicable afterwards. Effort is pinned in the agents' frontmatter, not in
prompts: prompts get paraphrased, frontmatter does not.

## Dispatches outside the profiles

| Dispatch | Agent and model | Effort | Why |
|---|---|---|---|
| Orchestrator, recon, the quick-run answer | this session | the session's | no dispatch |
| Synthesis fork (`research` Step 9; `research-deep` Step 9) | `general-purpose`, `model:` the session's own tier, named (`sonnet`, `opus` or `fable`) | `inherit` | the orchestrator's own pass, moved to a fork only for context room; no file pins the orchestrator's effort, and the fork must keep it |
| `deep-investigation` lanes, until item 1ffd lands | `general-purpose`, `model:` the lane model from its Step 1 (default `sonnet`, the `research-lane` row) | `inherit` | `research-lane`'s body forbids the tracked `<series>/findings/` path these lanes write today; 1ffd moves them to staging and onto `research-lane`, and deletes this row. Until then these lanes are routed by model and recorded, but not effort-pinned |
| POC break-out (`deep-investigation` Step 8.4) | not routed here | — | each POC is an `investigate`-format spec, which is build work: it leaves the run and is carried by `dev-cycle` or `implement`, under their own routing. The run records no dispatch for it; its record ends at the synthesis |
| `research-prune` | — | — | dispatches nothing |

Both `general-purpose` rows are recorded with effort `inherit` (§ Recording).

## The work item

A research run that dispatches an agent records its dispatches on a work item, where a
spend reader can join them by agent id. The run's orchestrator decides which item, once,
before its first dispatch.

### Which item

The first rule that matches wins:

1. **The run's orchestrator is a sub-agent** — the run started from an Agent-tool prompt (a
   planner's `/investigate`, a librarian's spike, any dispatched agent). The run files
   nothing and writes its lines to its state file's `## Record`, **even when `--item` names
   an item**. Why: the item's own orchestrator is its single writer, and the run's spend is
   already counted under its parent's `agent:` line, since a spend reader counts nested
   transcripts under their parent; a second listing would double it. A librarian's research
   is always this rule.
2. **The invocation names an item** — `--item <id>`, passed by the operator or a calling
   process — or a resumed run's state file names one. Record onto it, file nothing, and
   never close it: its owner does. A named item with no store or no `wi` resolving (below)
   falls to rule 4.
3. **A store and `wi` resolve (below).** File one (§ Filing). Every skill that dispatches
   files: `research`, `research-deep`, `research-refine`, `deep-investigation` and
   `chain-of-verification`, model-invoked runs included.
4. **Otherwise** — no store, or no `wi`. Write the state file's `## Record`. Never run
   `wi init`; say once that the run has no work-item store.

So a run records on no item in two cases only: inside a sub-agent (rule 1), or with no store
or no `wi` (rule 4). Where a rule says `## Record` and the run has no state file (a quick
run to disk; `chain-of-verification`), the lines go in the report instead: `research`'s
`COST` field carries `record: none (<reason>)` followed by the lines, `; `-separated, and
`chain-of-verification`'s Verification Summary carries its `Record:` line.

A run that dispatches nothing (a quick answer in the reply, `research-prune`) records
nothing.

### Stored names

Each name below is defined here and only here; a rename is an edit to this table and to the
lines that quote it.

| Name | What it is |
|---|---|
| `research-run` | the tag on every item a run files |
| `item: <id> \| none — <reason>` | the brief's frontmatter field naming the run's item (`Item:` in a strategy doc's opening paragraph); beside it, `wi:` (the resolved command) and `item_file:` (the item's absolute path) when there is an item |
| `## Record` | the state file's section just above its ledger, used when the run records on no item: a sub-agent run, or no store |
| `--item <id>` | the argument that names an existing item (rule 2) |
| `synthesis` | the role word on a synthesis fork's `dispatch:` line |
| `Record:` | `chain-of-verification`'s Verification Summary line, `- Record: item <id>` when the run filed or named one, else `- Record: none (<reason>) — <dispatch lines>`, the lines one per batch and separated by `; ` |

### Filing

When:

| Skill | Files the item |
|---|---|
| `research`, `research-deep`, `research-refine` | after `00-brief.md` is on disk (`research` Step 5.5), before Step 6; a quick run that writes to disk files at Step 4, before its verifier |
| `deep-investigation` | after `00_research-strategy.md` is on disk (its Step 4), before the first lane |
| `chain-of-verification` | after Step 3 classifies the mode, before the first Step 4 batch |

```bash
$WI add "<research: … | deep investigation: … | chain-of-verification: …> <the question or subject, in your words>" -t spike \
    --tag research-run --short-display-name "<3-6 word noun phrase, ≤ 40 chars>" \
    --ref <brief, strategy doc or destination path; none for chain-of-verification> \
    --desc "<the decision it feeds; the preset; the destination — chain-of-verification: the subject and its mode>"
$WI claim <id>
$WI handoff <id> --doing "<run> running" --next "report and close"
```

The handoff keeps `$WI lint` clean while the run is open.

- **Type `spike`**: a research run produces knowledge, not code. **Tag `research-run`**
  keeps these items separable from plan spikes in any spend population. Priority is `wi`'s
  default.
- **The id goes into the run's state file** — the brief's `item:` field, the strategy doc's
  `Item:` line; `none — <reason>` when there is no item. With an item (filed or named),
  write beside it the resolved command, `wi: python3 <absolute wi.py> --root <absolute
  WI_ROOT>`, and the file the record lines are appended to, `item_file: <WI_ROOT>/items/<id>.md`:
  shell variables do not survive between Bash calls or into a wakeup or a resumed session,
  and these lines do. A resumed run reads them and never files a second.
- A `research-refine` run's item carries `--ref wi:<prior run's item>` when the prior brief
  names one.

### Resolving the store

From the working directory, the main checkout's `.claude-sandbox/work/`, then `.work/`; the
first that exists is the store. `wi` comes from the repo's own tree when it carries the
`work-items` plugin, else from the installed plugin:

```bash
MAIN=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) && MAIN=$(dirname "$MAIN") || MAIN=$PWD
for d in "$MAIN/.claude-sandbox/work" "$MAIN/.work"; do test -d "$d" && { export WI_ROOT="$d"; break; }; done
WI_PY=$(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
test -n "$WI_PY" || WI_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["work-items@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
WI="python3 $WI_PY"
```

Rule 4's test is `test -n "$WI_ROOT" && test -f "$WI_PY"`: when it fails, rule 4. Run the
snippet once, at the record's opening, and from then on use the `wi:` and `item_file:` lines
the state file carries (with no state file — a quick run, `chain-of-verification` — re-run
the snippet in each Bash call that needs `wi`, and carry the item id in the conversation). This snippet restates the `dev-cycle` skill's
store resolution in research's own home; a change to `wi`'s install path touches both.

### Closing

At the run's report (`research` Step 11, `deep-investigation` Step 8,
`chain-of-verification` Step 6), on an item the run filed only:

| Status | Do |
|---|---|
| `DONE` / `DONE_WITH_CONCERNS` | `$WI done <id> --note "<run> <STATUS>: <n> lanes, <n> rounds, verifier <gate> <supported>/<sampled>; <destination>"` |
| `HELD` | `$WI block <id> "held: security concern; <held path>"` |
| `BLOCKED` | `$WI block <id> "<the reason, in your words>"` |
| `deep-investigation` done | `$WI done <id> --note "deep investigation: <n> lanes, <n> waves; <series path>"` |
| `chain-of-verification` done | `$WI done <id> --note "CoVe <VERIFIED\|CORRECTED\|PARTIAL>: <n> claims checked, <consistent>/<contradicted>/<unverified>; <n> batches"` |

A run that stops mid-way leaves its item `doing`, and the stale claim shows in `wi next`. A
held run's item stays blocked until `research-refine` cleans the run; that refine run files
its own item with `--ref wi:<held item>`, and then closes the held item with a note naming
the new one.

### What the item holds

- **Only** the `dispatch:` and `agent:` lines (§ Recording), appended to `item_file:`, the
  handoff, the closing note, and the filing's title, description, tag and refs. The brief and its ledger stay the run's state
  and rehydration point; the findings, verification sheet and synthesis stay in staging and
  at the destination.
- **Every word on the item is the orchestrator's** — ids, counts, models, efforts, paths,
  status. Never a lane's or a source's words (the ledger's rule, `run-record.md`), and never
  a secret. Run `$WI lint` after a hand edit.
- **No dev-cycle phase lines.** A research run writes no `return:`, `verdict:`, `target:`,
  `decision:` or `answer:` line: those move a cycle, and an item named by `--item` may also
  carry a cycle's record.
- **The item file is the run's one tracked write besides its destination.** The run never
  commits it; the report's `LANDED` names it (`item <id>`; `chain-of-verification`: its
  `Record:` line).

## Recording

**Before each Agent call**, write one line to the record sink — appended to the item's
`item_file:` (§ The work item); else at the end of the state file's `## Record`, by an edit
above the ledger, never a `>>` to the file; else in the report:

```
dispatch: <role> <model> <effort> — <signal>
```

| Field | Values |
|---|---|
| `<role>` | `research-lane` (both lane files), `research-verifier`, `scout` or `synthesis` |
| `<model>` | the per-call model |
| `<effort>` | the dispatched file's pin, so `research-lane high` is `research-lane-deep`; or `inherit` for a `general-purpose` dispatch |
| `<signal>` | the preset, round and lane id; or the gap condition, the sample, `script review <toolkit lane id>`, or the fallback or step-down reason |

**As each call returns its agent id**, append `agent: <role> <id> round <n>`, where `<n>` is
a lane's run round (1-3), the verifier's pass (1, then 2 on a re-verify after a clean-up),
1 for the fork, 1 for a `chain-of-verification` batch, and for a script review at the
toolkit gate the round of the toolkit lane it reviews. A round's lanes launch in one
message: write all their `dispatch:` lines in one append before it, then their `agent:`
lines as the ids come back.

```
dispatch: research-lane sonnet medium — standard round 1 w1-vendor-docs
agent: research-lane a1b2c3d4e5f60718 round 1
dispatch: research-lane opus medium — round 2 gap 4 w6-pricing
dispatch: research-lane opus high — adversarial (exhaustive) round 2 a1-break-answer
dispatch: research-verifier sonnet low — verify sample 30
dispatch: research-verifier sonnet low — script review l1-log-toolkit
dispatch: synthesis opus inherit — fork (findings over 2,500 lines)
dispatch: research-lane sonnet inherit — deep-investigation lane b2 wave 1; general-purpose until deep-investigation parity
dispatch: scout sonnet medium — cove general batch 1 of 2
dispatch: research-lane opus medium — adversarial (exhaustive) round 2 a1-break-answer; dev-flow:research-lane-deep not loaded
```

Each line is one physical line, unindented, in the orchestrator's words. The lane prompt's
model mention is unchanged, so the transcript and the record agree.

## Below the quota reserve

A run is below the reserve when the weekly window is spent down to the operator's reserve:
`windows.seven_day.headroom` ≤ 0 from the `librarian-mode` skill's
`scripts/quota_budget.py --read-only` (dev-flow's quota sense). Read it once, before the
round that would dispatch `research-lane-deep`. No script, or no signal, reads as not below.

§ The quota read (the sensor record's five-hour and weekly percentages) sizes the preset;
§ Below the quota reserve (the quota sense's weekly headroom) steps down only the deep lane
file.

| What would run | Below the reserve |
|---|---|
| `research-lane-deep` (the adversarial lane) | `research-lane` with `model: opus`, recorded `dispatch: research-lane opus medium — adversarial (exhaustive) round 2 <id>; stepped down (below the quota reserve)` |
| A lane model the invocation names | runs as named: the operator's words are the pin; the cost line carries the reading |
| `research-lane`, `research-verifier`, `scout`, the synthesis fork | unchanged |
| The preset | unchanged here: § The quota read's table sizes it (a 7d ≥ 90% reading is `quick` only) |

A step-down is not a hold: the run goes on.

## Fallback

**Not loaded** means `dev-flow:<agent>` is missing from the session's agent list, or a call
naming it fails as an unknown agent type — typically after a plugin update without a
restart. Nothing here is asked: research has no operator effort pin to protect.

| Not loaded | Dispatch instead | Recorded |
|---|---|---|
| `research-lane-deep` | `research-lane`, `model: opus`: the step-down's shape, and the best pinned file left | `dispatch: research-lane opus medium — …; dev-flow:research-lane-deep not loaded` |
| `research-lane` or `research-verifier` | `general-purpose`, the routed `model`, with the agent file's body pasted as the prompt's first section | `dispatch: <role> <model> inherit — …; dev-flow:<agent> not loaded`, plus a ledger line |
| `scout` (`chain-of-verification`) | `general-purpose`, the routed `model` | `dispatch: scout <model> inherit — …; dev-flow:scout not loaded` |

- **Say it once** in the report's `CONCERNS` (`chain-of-verification`: its Summary): "role
  agents not loaded; update dev-flow and restart".
- **A usage-limit error** (HTTP 429, "out of usage credits") on a dispatch is not a
  fallback: the lane is `FAILED` per `research` Step 6, with the reset time in its ledger
  line. No research dispatch is pinned to fable, so there is no fable row.
