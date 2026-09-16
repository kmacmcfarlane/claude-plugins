---
id: usage-report-report-command-skill-doc-re-7e8f
title: "usage-report: report command, skill doc, README catalog row"
type: feature
status: todo
priority: 2
deps:
  - usage-report-transcript-parser-dedupe-pr-eff1
parent: spike-analyze-claude-code-usage-across-c-e5a7
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator approval 2026-09-16
---

F2 of the approved analyzer plan: complete the usage-report SKILL.md (what/when/triggers; how to run; how to read the tables; the reconciliation step against Claude Code's built-in /usage view; caveat that dollars are list-price estimates), finish the CLI (per session / per model / per dispatch tier / per day tables; --json; --all; --since; --flat), and add the README claude-kit catalog row and the Structure tree entry in the same commit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
From the F1 review (2026-09-16): (a) by_requested_tier needs a "main" bucket (or a key saying main-session tokens
are excluded) so it reconciles with totals, and its opus_equivalent should be summed from unrounded values; (b)
tokens priced through a legacy alias (claude-fable-5, claude-opus-4-7, claude-opus-4-8 -> current same-family
entry) must be visible in the report — a separate row or a marker — not silently merged.
- librarian 2026-09-16: held until the plugin-factoring reconcile (9b93) lands, so usage-report is placed once in the factored layout.
