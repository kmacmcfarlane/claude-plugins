---
name: factor-analysis
description: Analyze how a repository, plugin, library, or toolset should be factored into coherent standalone pieces — cohesion evidence, candidate shapes, scenario matrix, doctrine, staged decisions. Use when the user asks "should this be its own plugin/package/module", "what's the right shape for this repo", "find the natural splits", "how should we bucket this", "factor this", or when a grab-bag project needs better boundaries. Not for planning a single scoped change (use investigate) or executing an agreed refactor (use implement).
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch
argument-hint: [what to factor, e.g. "this repo" or a directory]
---

# Factor analysis

Answer "what shape should this be?" with evidence instead of vibes, and land the answer as
decisions the owner actually made — not a proposal that dies in scrollback. The method came
from a live session that refactored a plugin marketplace; each step below earned its place
there.

**The deliverable is a target shape + a factoring doctrine + filed work items.** State
migration is planned by `implement` later; this skill decides *where the lines are*.

## Step 1 — Find the taxonomy axis

Ask for (or locate) the project's mission sentence — what it exists to do, in the owner's
words. The axis for factoring is almost always **aim-indexed**: a piece is the answer to a
sentence a user would say ("I keep losing context", "I want unattended runs"). Name the
current axis too — usually *history-indexed* ("stuff I needed somewhere to put") or
*artifact-indexed* (by file type) — so the mismatch is explicit.

While applying the axis, watch for **distinct product families** (e.g. harness capabilities
vs domain expertise packs). Conflated families are often the root muddle, and separating them
can be the biggest single win.

## Step 2 — Gather cohesion evidence (never skip to opinions)

Two passes, both cheap:

1. **Reference grep** — for every unit (skill, module, package), grep all other units for
   mentions of it, its CLIs, its file formats, its paths. Distinguish *real* dependencies
   from **path-convention hits** (a shared directory-name prefix is not a dependency) and
   from **vocabulary collisions** (two units saying "ledger" about different ledgers).
   Verify surprising hits by reading the match in context.
2. **Workflow adjacency** — references miss lifecycle glue. Ask: which units are used
   *together in one workflow*? Who produces what another consumes (a format contract is the
   hardest coupling there is)? Which share a CLI or a state store? Which run on the same
   machines / serve the same audience? Ask the owner — they know workflow ties the text
   doesn't show.

Output: named clusters, each with internal glue strength (hard contract / shared tool /
prose mention) and outward ties (hard vs soft). Note orphans and deprecated units — retiring
them is usually a free win the factoring legitimizes.

## Step 3 — Candidate shapes

Propose 3–5 shapes spanning the range: status quo, the minimal cut, the cluster-faithful
cut, and the maximal (per-unit) cut. Rules:

- **Never cut through a hard contract** (producer/consumer format, direct file invocation
  across the boundary). If a shape requires it, reject that shape early and say why.
- Special-case units that alter shared behavior (hooks, global config, daemons): they must
  live in a piece whose *stated aim* is that behavior — never as passengers.
- The maximal shape is usually the strawman; include it anyway so its rejection is reasoned,
  not assumed.

## Step 4 — Scenario matrix

Generate a thorough set of plausible adoption scenarios — real machines, real users, real
workflows: "wants only X", "unattended host", "teammate asking what's that", "maintainer
syncing", "session context budget", "temporarily disabling one concern". Ground them in the
owner's actual situation where known. Evaluate **every shape against every scenario** in one
table; the favorable factoring lines are the cuts that win or tie across scenarios. Include
maintenance burden and migration cost as scenarios — they are where good shapes die.

## Step 5 — Distill the doctrine

The shape decays without rules. Write the values that make it self-maintaining — typically:
one piece one aim; the standalone-install test; behavior-altering code quarantined to pieces
aimed at that behavior; dependencies soft, declared, directional; names are API (they end up
in paths and muscle memory); new aim → new piece, never a stretched description; a
problem-indexed catalog as the front door with a contributor decision tree. Codifying the
doctrine in README/CLAUDE.md is always the **first** work item — it is the ruler the other
items are measured against.

## Step 6 — Stage the decisions

The structural calls belong to the owner. Two rules learned the hard way:

- **Never end an analysis-heavy turn with a question dialog.** The dialog blocks the owner
  from reacting to the prose. End the turn with the analysis plus "N quick decisions queued —
  react first, or say go"; fire AskUserQuestion the next turn.
- In each question, put your recommendation first, marked, with the honest cost of every
  option. Free-text answers to a question are common and often reshape the tree — treat a
  rich answer as new requirements, not a selected option.

## Step 7 — Land it

An agreed shape that lives only in conversation is lost. Before ending:

1. **Work items** (`work-items` skill): one epic; one item per extraction with real
   dependency edges (doctrine first; the "refit/cleanup" item depends on all extractions);
   descriptions carry the settled decisions with dates so a cold session can act.
2. **Investigation series** (`investigate` format) recording the evidence, target shape,
   per-phase steps, switchover checklist, and open questions — for `implement` to consume.
3. Sequence extractions independent-after-doctrine, each leaving the project consistent, so
   the owner can stop after any phase.
