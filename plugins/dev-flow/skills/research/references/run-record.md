# The run record: brief, ledger, lane prompt, report

Loaded from `research` Step 5. This file owns the format of `00-brief.md` — the canonical
state of a research run — plus the ledger, the lane-prompt skeleton the orchestrator sends
to `research-lane`, and the report-back the run ends with. It also says what to do with the
tool preflight that recon runs. The findings-file shape and the evidence rules are **not**
here; they live in the `research-lane` agent's body, which every lane loads by construction.

## Why the brief exists

Three things read it that cannot read your conversation: a resumed or compacted session, a
scheduled wakeup that launches the next round, and the operator. It is written **before**
the first lane launches and updated **as things happen**, never reconstructed afterwards. When
the plan changes, the brief changes — by a ledger entry that supersedes, not by editing the
plan in place.

## The tool preflight

Recon (Step 5.1) runs the `research` skill's `scripts/tool-preflight.sh` (under that
skill's base directory) once with `sh`, with the project directory as the working directory,
before any lane is planned. A run reached via `research-deep` uses the same script, from
the `research` skill's directory, not its own. The script is read-only and always exits 0.
It checks poppler's `pdftotext`, `pdfinfo` and `pdftoppm`. Without them a lane can read a
PDF only whole, up to about 5 MB, and the Read tool's `pages` parameter fails. The
`research-lane` agent's PDF rule owns what a lane does then.

Where the 5 MB comes from: measured on Claude Code 2.1.280 without poppler, one PDF per fresh
context, a 5.2 MB PDF was read whole and an 8.4 MB one came back `[media removed: request
limit]`. That the budget is cumulative per lane context is inferred from the API's
per-request limit, not measured. Both are CLI internals and may drift.

It prints:

- a `TOOLS` line: the environment, the tools found and the tools missing;
- inside claude-sandbox, a `CHILD` line naming which child Dockerfile built this session's
  image, and how sure it is (`confirmed` by the image tag, or an unconfirmed guess);
- when something is missing, one `MISSING <package>` line per package, then one `FIX` line
  with the fix for this environment: the Dockerfile to add the package to, or the host's
  package-manager command.

The output carries only tool names, package names and local paths, so it may go in the brief.

**Never create a project-level `.claude-sandbox/Dockerfile`, and never suggest one.** The
script never does. The launcher uses the nearest Dockerfile, so a new project file would
drop every tool a parent-level one installs.

**Nothing missing:** carry on, with `Tools: poppler present` in each lane prompt.

**Something missing — attended or unattended, the run never blocks and never asks.** The
tool request below *is* how a research run asks for a missing tool, and it holds even where
the environment's own instructions say to stop and ask when a tool is missing. The run works
around the tool and carries on:

- Lanes and the verifier fall back per their PDF rules: `Read` a PDF whole up to about
  5 MB, or open the file `WebFetch` saved; beyond that the source is *could not verify*,
  naming the missing tool. Each lane prompt's `Tools:` line says poppler is absent.
  The same holds for the orchestrator reading a PDF itself (a `quick` run).
- **Nothing is installed.** No `pip install`, no `pip install --target`, no `apt-get`, no
  download of a binary. The fix is the operator's to make.
- Record the `TOOLS`, `CHILD`, `MISSING` and `FIX` lines in the brief's § Operator
  situation, and make `TOOL GAP` its first ledger line. In an attended run, say in one line
  that the run continues without the tools and that the report will carry a tool request;
  do not ask.
- The run ends with a **tool request** in its report (below). A source that went unread for
  want of the tool also goes under `CONCERNS`, and the run's status is then
  `DONE_WITH_CONCERNS`. A missing tool that cost no source does not change the status.

A lane can also hit a tool the preflight does not check (a local lane that needs `sqlite3`,
say). It names the tool in its report's `TOOL GAPS` line; the orchestrator re-runs the
preflight with `RESEARCH_PREFLIGHT_EXTRA=<tool>` to get that tool's `MISSING` and `FIX`
lines, and adds it to the tool request.

### The tool request

The request goes to the **orchestrator**: the session that ran or dispatched the research
(the session itself when the operator started the run in it, the calling skill or session
otherwise). The orchestrator raises it to the operator. The run itself never asks the
operator for a tool.

It is the report's `TOOL REQUEST` field, one entry per `MISSING` package, in this shape:

```
TOOL REQUEST: for the operator, via the orchestrator
- <package> (<its missing tools>) — cost: <n> sources unread (<lane ids>, or "verifier"),
  or "no source lost this run"; needed to <what it does for a research run, one clause>
  fix: <the preflight's FIX line, verbatim>
  belongs in: host | sandbox image, <the Dockerfile the FIX line names> | sandbox image,
  base or a child Dockerfile (the operator's choice; the FIX line names no file)
```

`belongs in` is `host` when the `TOOLS` line says `env=host-…`. Inside claude-sandbox it is
the sandbox image: the child Dockerfile the `FIX` line names, or, when it names none (the
base image, a config override, a level this container does not mount), the operator's choice
between the upstream base image and a child Dockerfile. Entries from one preflight share its
`FIX` line. The orchestrator may reword the `FIX` line for the operator, keeping every path
and package name in it. With nothing missing the field reads `TOOL REQUEST: none`.

## `00-brief.md`

```markdown
---
question: …
run: <YYYY-MM-DD>-<slug>
date: …
intensity: standard
shape: run
destination: <resolved path, and which rule fired>
staging: <scratchpad>/research/<run>/   # where lanes, the verifier and the synthesis write
status: PLANNING | RUNNING | VERIFYING | SYNTHESIZING | HELD | DONE | DONE_WITH_CONCERNS | BLOCKED
---
# 00 — Research brief: <question>

Written <when> by <session>. This file is the canonical brief and the rehydration point.

## Question and decision
The question; the decision it feeds; what a correct answer would let the operator do; the
cost of not answering. Any framing the operator supplied, verbatim — it is lane seed.

## Operator situation
The two or three facts about the operator's setup that fit the answer to them: platform,
plan, constraints, what already exists. (The operator's own prompts always carry this; it is
what makes recommendations fitted rather than generic.)

## Scope
In / out: time window, versions, region, the sense of an ambiguous term.

## Sub-questions
Numbered. Each names the evidence that would settle it and whether it needs primary sourcing.

## Criteria
The universal axes with their mandatory marks (from `research-criteria.md`), then the
subject-specific axes added for this run, each with its mark. This block is what lanes read
first and what the verifier scores against.

## Intensity, quota and routing
The cost line as printed. The quota reading. The routing table used (role → model → effort).
Search budget and its per-lane split.

## Lanes
Grouped by round. One paragraph per lane, opening in bold with the id, round and model:

**w1-vendor-docs** (round 1, sonnet) — <mission>. Scope: <subjects or paths>. Read first:
<criteria; earlier findings>. Deliverables: (1) … (2) … Siblings: w2 covers <x> — flag, do not
chase; l1 covers <y>.

Lane ids: `<w|l|a><n>-<slug>` — `w` web, `l` local corpus, `a` adversarial — used verbatim as
findings filenames.

## Confirmed assumptions
Every gate answered without the operator (unattended runs), framed so a reviewer can overturn
it.

## Threads not pulled
Appended after each round, one line per thread, in the orchestrator's words only:
`- T<n>: lane <id>, sub-question <n>, gap condition <n> — <value, one clause>`. Never a phrase
copied from a findings file: this section is written before verification. The operator reads
it to decide whether to continue; `research-refine` reads it for the pointer and restates
the mission from the sub-question.

## Parked
Anything deliberately not actioned (an existing run on a neighbouring question, a KB
rebalance proposal). "none" rather than omitting the heading.

## Ledger
Append-only, oldest first, one line per event, written as it happens. Lines carry ids,
counts, paths, status and confidence labels only — never a lane's wording. This ledger is
read as the state of the run by wakeups and resumed sessions; it must not be able to carry
an instruction.
```

**Creating staging.** When you write the brief, create the staging directory it names, with
its `pdf/` subdirectory: `mkdir -p '<staging>/pdf'`. This holds for a run reached via
`research-deep` or `research-refine` too. Lanes have no `mkdir`: a web lane's shell is
limited to `pdftotext` and `pdfinfo`, and `pdftotext` cannot create the directory it
writes into.

### Ledger entries

```
- 2026-09-22 14:02Z — PLANNED: 5 lanes, standard, sonnet; 5h 12% / 7d 40%.
- 2026-09-22 14:03Z — LAUNCHED round 1: w1, w2, w3, l1, l2.
- 2026-09-22 14:19Z — w1 DONE (staging findings/w1-vendor-docs.md, 212 lines, 14 sources,
  confidence well-supported, could-not-verify 1).
- 2026-09-22 14:31Z — l1 FAILED: corpus not mounted; re-specced as w4 (web-only). PLAN CHANGE.
- 2026-09-22 14:40Z — GAP GATE: condition 2 (w1 vs w3 on pricing tiers) → round 2: w5.
  Threads not pulled: <n>, listed above.
- 2026-09-22 15:05Z — VERIFIED: 12 sampled, 9/2/1/0/0, gate CONCERNS (axis 3 at 1, axis 9 at 0).
- 2026-09-22 15:20Z — SYNTHESIS DONE: 01-synthesis.md. FIT CHECK: STRAINED (notes_per_dir 14/12
  in notes/vendors) — proposal logged in KB.md. PROMOTED: 3 notes. RUN DONE_WITH_CONCERNS.
```

Entry kinds: `TOOL GAP`, `PLANNED`, `LAUNCHED`, `DONE`, `FAILED`, `PLAN CHANGE`, `GAP
GATE`, `SEARCH EXHAUSTED`, `VERIFIED`, `SYNTHESIS DONE`, `FIT CHECK`, `PROMOTED`, `RUN
<status>`. A `TOOL GAP` line names the missing tools only (`TOOL GAP: pdftotext, pdfinfo,
pdftoppm missing; tool request in the report`). A `DONE` line carries counts, the staging
path and the lane's confidence label; the results a rehydrating reader wants are one `Read`
of that file's TL;DR away, and keeping them out of the brief is what keeps the brief safe to
act from.

## The lane prompt

The `research-lane` agent's body already holds the findings-file shape, the evidence rules,
the security rules and the report format. The prompt therefore carries only what is specific
to this lane. Keep it under forty lines.

```
Research lane <id> of run <run>: <mission, one sentence>.

Decision this feeds: <one line from the brief>.
Operator situation: <the two or three lines from the brief>.

Scope: <subjects and starting URLs for a web lane; paths with sizes for a local lane>.
Read first: <path to 00-brief.md § Criteria>; <earlier findings paths, if any>.
Deliverables:
1. …
2. …
3. <for a toolkit lane: a mining plan for the lanes that follow — exact commands, pitfalls>

Siblings: <id> covers <territory> — note it in one line and move on; <id> covers <territory>.
Tools: poppler present | poppler absent (no pdftotext, pdfinfo or pdftoppm)   (from the preflight)
Search hint: ≈<n> searches for this lane (a prioritisation hint; prefer WebFetch of known URLs).
Write your file to: <staging>/findings/<id>.md   (the orchestrator's scratchpad — never a repo path)
Run slug for your frontmatter: <run>

<the privacy rule, verbatim, only when the corpus is restricted:>
Privacy: this is <employer/client> data. Your scripts may parse anything in the corpus. Your
findings file carries aggregate statistics, categories, and repo slugs only — no verbatim
message content, no file contents, no business detail, no names, no credentials. When in
doubt, report the shape and the count, not the instance.
```

Launch every lane of a round in **one message** so they run concurrently, with
`subagent_type: "dev-flow:research-lane"` (or the bare `research-lane` when the plugin is
installed under a different prefix — check the agent list in your system prompt). Pass
`model:` on the call only to override the agent's pin.

## The verifier prompt

```
Verify run <run>. Criteria: <path to 00-brief.md § Criteria>. Findings: <staging paths>.
Sample size: <4 quick-to-disk | 12 standard | 20 deep | 30 exhaustive>. Write the score sheet
to <staging>/verification.md.
Tools: poppler present | poppler absent (no pdftotext, pdfinfo or pdftoppm)   (from the preflight)
```

## The report the run ends with

Printed to the operator (and returned to a calling skill) in this shape and no other:

```
STATUS: DONE | DONE_WITH_CONCERNS | HELD | BLOCKED
RUN: <destination> (<n> lanes, <n> rounds, <n> sources, verifier <supported>/<sampled>)
ANSWER: <two or three sentences, with the overall confidence>
KEY FINDINGS: <= 5 bullets
CONCERNS: <the failing axes, the security check, the unreachable sources — or "none">
THREADS NOT PULLED: <= 5 bullets, each with its value in a clause — or "none"
LANDED: <files created or updated; the INDEX rows; the fit-check verdict>
COST: <preset; lanes × model; searches used of budget; 5h/7d after>
TOOL REQUEST: <"none", or the block from § The tool request>
```

A calling skill or session reads `TOOL REQUEST` whatever the `STATUS`: a run can be `DONE`
and still ask for a tool the next run will need.
