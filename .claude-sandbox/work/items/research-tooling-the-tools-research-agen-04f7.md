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
- 2026-09-24 agent-research - librarian filed research-tooling-the-tools-research-agen-39ae (spike); list comes back after its review
- 2026-09-24 claude-sandbox librarian (item a864): small stable Debian tools such as poppler-utils go in the base image (batch them, since each change rebuilds every child); heavy or niche tools (pandoc, tesseract, Chromium, LaTeX) go in a documented opt-in child-Dockerfile snippet; pip only as a degraded path; skills must detect and name a missing tool; it measures sizes once the list arrives and puts the cut to the operator
