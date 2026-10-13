---
id: plain-names-in-the-reports-and-consumers-8e04
title: plain names in the Reports and consumers (0b2d F3)
type: feature
status: done
priority: 2
deps:
  - operator-interaction-the-plain-names-ski-cad6
  - work-items-optional-short-display-name-f-928d
parent: operator-interaction-refer-to-work-items-0b2d
created: 2026-09-29
updated: 2026-09-29
closed: 2026-09-29
refs:
  - 0b2d
---

Build F3 of series .claude-sandbox/investigations/0b2d-plain-item-names (03 + 04, plan review s04-r2 CLEAR). After F1 and F2. Fold lows L1 (dbfc tip 9332809 moved anchors), L2 (03:122-123 and 03:642-645 superseded), L4 (filing sites state the 40-char cap; exit 1 means shorten and retry).

## Handoff
- doing: —
- next: review r1 running at 4500b87; land on CLEAR
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — rule wording across librarian-mode, dev-cycle, work-review, plugin descriptions (routing rule 2)
agent: a4a6196cdb2a5b64a (implementer r1)
r1 DONE_WITH_CONCERNS 4500b87: 10 files; dev-cycle SKILL.md now 4076 words (fefd covers the trim); deviations: no commit trailer claim, name-only targets, tables stacked
dispatch: reviewer opus — fresh reviewer, round 1
agent: a40cc33f41d4c005c (reviewer r1)
review r1 NEEDS_CHANGES (0H 1M 2L): M exit 1 has four causes, not only a long name — tie the retry to the message, say it once at Intake and dev-cycle Step 0; L idle-turn restates half the repeat rule; L hold-name rule (5 words, no until) vs stored names (6 words)
dispatch: implementer opus — resume, fix round 1
r1 fixes 1b2195a: exit 1 told apart by message at Intake/Step 0 (others point there); full repeat rule; stored name or 5 words, never until; HOLD reason fixed
dispatch: reviewer opus — fresh reviewer, round 2
agent: a110d48e38a9d6147 (reviewer r2)
review r2 CLEAR at 1b2195a (1 low filed as a follow-up: the exit-2 rule should key on "unrecognized arguments: --short-display-name")
landed: d7d64e8
checks on main d7d64e8: all 8 OK
- 2026-09-29 done
