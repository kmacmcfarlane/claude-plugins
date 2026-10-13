---
id: dev-cycle-enrol-the-xhigh-trial-when-a-r-4d27
title: "dev-cycle: enrol the xhigh trial when a resumed plan-mode fix round has a late high and no trial line"
short_display_name: trial enrolment on resume
type: chore
status: todo
priority: 3
created: 2026-09-29
updated: 2026-09-29
refs:
  - b3c5
---

From b3c5 review r2 2026-09-29: a plan run that dies between a round-1/2 NEEDS_CHANGES carrying a late high and its trial: line reaches resume S9, which goes straight to fix-loop; fix-loop only says trial units are fresh, so an agent can read the item as no unit and resume the planner (the unit is lost; nothing miscounted). Acceptance: resume.md S9 or fix-loop's trial bullet says a plan-mode fix round with a late high and no trial: line runs model-routing § The xhigh trial's enrolment first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
