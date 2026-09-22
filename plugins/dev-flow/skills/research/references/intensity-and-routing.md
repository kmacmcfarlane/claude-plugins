# Intensity, cost and routing

Loaded from `research` Step 3. This file owns the presets, the rules for when to ask the
operator about intensity and when it is obvious, the quota read, the search-budget rule and
the model/effort routing table. The orchestrator copies the chosen preset and the routing
table it used into the brief; nothing here is restated in SKILL.md.

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

## When to ask, and when it is obvious

Do **not** ask when any of these holds; state the preset and its reason in one line instead:

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

**Model-invoked runs** — the skill loaded on the words "research", "look into", "find out"
without a slash — run **`quick` only**. When the orchestrator judges that a deeper preset is
warranted (the question passes the fan-out test, or the quick answer surfaces a contested or
under-sourced core claim), it says so in one line — the preset, its cost line, and what the
deeper run would add — and asks. It never escalates on its own.

**The fan-out test** (from `deep-investigation`): can you name, right now, three to five
categories of evidence that would answer the question, and does no single one of them
suffice? Yes → a fan-out preset is justified. No → `quick`; a fan-out on a narrow question
buys N files that say the same thing.

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

## Routing — model and effort

| Role | Model | Effort | Why |
|---|---|---|---|
| Orchestrator (this session) | the session's — opus or fable | the session's, high | decomposition, criteria and synthesis gate everything downstream; a weak plan is unrecoverable |
| Recon | the orchestrator itself | — | recon changes the plan, so it has to happen in the context that holds the plan |
| Research lane | `research-lane` agent — sonnet | medium (pinned in the agent) | reads a lot, writes ≤300 lines to a fixed shape; not where the dear model earns its keep |
| Adversarial lane (`exhaustive`) | `research-lane` with `model: opus` on the call | medium | breaking an answer needs more judgement than gathering one |
| Verifier | `research-verifier` agent — haiku | low (pinned) | mechanical: open the URL, does it say that |
| Synthesis | the orchestrator, or a fork of it | high | the one pass that cannot be parallelised |

Effort is pinned in the agents' frontmatter, not in prompts: prompts get paraphrased,
frontmatter does not. The per-call `model` on `Agent` overrides the frontmatter when a run
needs it (the adversarial lane; a lane on a restricted corpus the operator wants on a
stronger model). **Print the routing table you used into the brief** — effort is the largest
silent lever on both wall clock and usage, and a run that took three hours must be
explicable afterwards.

Published guidance and the operator's own dev-cycle routing agree: orchestrator on the dear
tier at high effort, workers on a cheap tier at low or medium; and a model upgrade buys more
than a token-budget increase.
