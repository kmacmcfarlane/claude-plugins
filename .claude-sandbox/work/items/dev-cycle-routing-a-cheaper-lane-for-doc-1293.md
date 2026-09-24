---
id: dev-cycle-routing-a-cheaper-lane-for-doc-1293
title: "dev-cycle routing: a cheaper lane for docs-only changes — plan with options for the operator"
type: spike
status: todo
priority: 1
created: 2026-09-24
updated: 2026-09-24
refs:
  - "peer: opencode - librarian (operator relay 2026-09-24)"
---

Operator 2026-09-24, relayed by opencode - librarian: 'running a full review cycle on a docs change seems a bit wasteful. Send a note to the claude-plugins agent to improve our model routing and present me with a plan to decide between the option presented'. Do not pick one and ship it; put the options to the operator as a decision. Evidence from opencode, 2026-09-24: item A, CLAUDE.md, about 80 lines: sonnet implementer ~88k tokens, opus review ~74k (found a real medium, a backwards sudo ~ explanation checked live over ssh), fix round ~104k, re-review ~82k, total ~350k; item B, docs/running-and-logs.md, 12+/2-: ~88k + ~66k = ~155k, CLEAR with two lows, overkill. Candidate options: a docs-only lane that reviews at the implementer's tier (drop the opus floor with no executable surface); orchestrator self-review for small docs diffs that make no operational claims; split docs into factual/operational claims (keep a reviewer) vs prose-only (none); status quo. Acceptance: a plan with options and impacts, raised as a decision card in the librarian's decision channel; the change follows the operator's pick.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 82: a cheaper path for docs-only changes in dev-cycle — (a) split by what the doc claims: prose-only docs (wording, formatting, alignment; no commands, hosts, permissions, config values or rules agents follow) get a librarian self-review (reads the full diff, runs the lint and checks, records "review: self"), while docs with operational claims, skill text included, keep a sub-agent reviewer at the implementer's tier, with no opus floor for docs [recommended]; (b) every docs-only change reviews at the implementer's tier (sonnet), with no opus floor; (c) self-review any docs diff under about 20 changed lines; (d) keep things as they are; (z) decide later
- 2026-09-24 marketplace - librarian relays a policy the operator confirmed in its conversation (context for decision 82, not an approval; the operator is coming here to rule). (1) Implementer: Sonnet for mechanical edits (pointer and path fixes, frontmatter, catalog rows, wording that changes no behaviour); Opus 5.5 for anything that changes what a skill does, format bumps and scripts. (2) Reviewer: always Opus 5.5, always a fresh sub-agent that never saw the implementer's conversation. Fable only as a second opinion on a complex plan made by Opus 5.5 (greenfield architecture, major refactor). Operator, verbatim: "Using a fable reviewer for a text change is too extreme, and we should probably be using claude 5.5 to do reviews anyway now that's out." (3) Review waiver: the librarian self-reviews pure prose with no operational claim ("review: self"); skill text, CLAUDE.md, references and scripts keep a reviewer. Research cited: fresh-context and different-model reviewers (arXiv 2607.21656, 2603.12123); cheapest model that ships verified work; review proportionate to risk. This replaces dev-cycle's fable routing for security and gating code (rule 3) and its reviewer = implementer's tier (rule 4). Where it lands: dev-flow's dev-cycle Step 2 and references/model-routing.md, plus the librarian-mode binding. The marketplace updates its own bindings to point here; send it the commit.
decision 82 update: option (e) added, the operator-confirmed policy above.
