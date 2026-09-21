---
id: usage-report-optional-ccusage-cross-chec-8482
title: "usage-report: optional ccusage cross-check test"
type: feature
status: todo
priority: 4
deps:
  - usage-report-transcript-parser-dedupe-pr-eff1
parent: spike-analyze-claude-code-usage-across-c-e5a7
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator approval 2026-09-16
---

F3 of the approved analyzer plan: a test (skipped when npx/ccusage is unavailable or offline) that runs ccusage session --json on a fixture directory and compares its per-session totals with the parser's, reporting any discrepancy beyond a tolerance. Research noted a ~2.7x cache-read disagreement on one real session — the test's job is to make that visible, not to hide it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- librarian 2026-09-16: held until the plugin-factoring reconcile (9b93) lands, so usage-report is placed once in the factored layout.

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

## Hold 2026-09-19
- Do NOT build: operator intends usage-report to retire into kmacmcfarlane/claude-analytics (peer agents-61); close when `ca report usage` reaches parity and the skill is removed (their Phase 3).
