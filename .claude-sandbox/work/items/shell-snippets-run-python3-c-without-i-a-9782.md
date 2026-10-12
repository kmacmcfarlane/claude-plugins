---
id: shell-snippets-run-python3-c-without-i-a-9782
title: "shell snippets run python3 -c without -I: a json.py in the cwd runs"
short_display_name: python snippets without -I
type: bug
status: todo
priority: 2
created: 2026-10-12
updated: 2026-10-12
refs:
  - one-way-to-reach-wi-from-outside-work-it-b9e4
---

From b9e4 review 2, 2026-10-12: snippets outside the wi lookups still run python3 -c or python3 - from the working directory, so a json.py there is imported: dev-cycle model-routing.md:459, checkpoint operator-playbook.md:319, dev-flow review-checklist.md:283,324,325, session-name.md:41, create-repo SKILL.md:73,105, update-kit SKILL.md:350, work-review SKILL.md:74. Acceptance: every such snippet runs python3 -I; a grep test keeps it so.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
