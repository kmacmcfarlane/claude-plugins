---
id: usage-report-state-the-transcript-parsin-8605
title: "usage-report: state the transcript-parsing fixture rule (streamed usage spans lines; resumed copies across files)"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock); agents retro/2026-09-20-agent-telemetry-investigate-run.md @ agents 74b45f9 § candidate skill changes"
---

Relayed 2026-09-22. Fixtures for transcript-parsing code must use multi-line streaming usage (one message.id across several lines, output_tokens growing to its last line) plus a resumed-session copy across two files. 8246 (120f1a4) may already test this in usage_report — verify; if so the item is only whether the rule is stated generally (usage-report SKILL.md testing note, or references/) so the next parser (e.g. statusline's subagent reader, c0cc) inherits it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
