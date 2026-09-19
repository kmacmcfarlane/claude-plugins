---
id: wi-body-edits-whitespace-only-body-headi-23a8
title: "wi body edits: whitespace-only body heading, fenced headings, newline in --doing, import --update coverage"
type: chore
status: todo
priority: 4
created: 2026-09-19
updated: 2026-09-19
---

From the e832 review (2026-09-19), all low/nit, no data loss: (1) _append_section glues '## Notes' onto a whitespace-only body with no trailing newline (wi.py:348); (2) a fenced '## Handoff' inside Notes makes later notes land inside the fence (section scan ignores fences); (3) --doing/--next values with a newline leave unowned lines or inject headings — reject or escape newlines; (4) no test covers newline='' on the write side; (5) import --update not in the preservation matrix.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
