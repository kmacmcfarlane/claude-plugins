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
