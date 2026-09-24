---
id: research-tooling-the-tools-research-agen-04f7
title: "research tooling: the tools research agents always need, and how each environment gets them"
type: spike
status: todo
priority: 2
created: 2026-09-24
updated: 2026-09-24
refs:
  - operator 2026-09-24 (R10, poppler-utils)
---

Operator 2026-09-24, instead of adding poppler-utils alone (R10): ask agent-research - librarian to list the tools the research skills should always have (pdftotext/poppler-utils was the first gap: lanes could not read PDF primaries) and the proper steps to get them in each scenario (sandbox child Dockerfile, the upstream claude-sandbox base image, a host session, pip-only fallbacks) before a run needs them; get claude-sandbox - librarian's input, since adding them to the upstream parent Dockerfile may be the most ergonomic. Acceptance: a list with per-scenario steps and a recommendation on where each tool lives, back to the operator; then a research-skill note (preflight/fallback) filed here if needed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
