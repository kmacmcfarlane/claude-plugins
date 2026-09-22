---
id: handoff-h6-remind-unread-read-in-full-pa-b6de
title: "handoff H6: remind unread Read-in-full paths once, in the next prompt's context"
type: feature
status: doing
priority: 1
deps:
  - handoff-h1-mark-checkpoint-stamps-writte-9852
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
---

Track the manifest's Read-in-full list against Read tool calls; one context line on the next prompt naming unread ones; no extra turn. Opus/opus. Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — context-guard hook logic
impl r0 DONE_WITH_CONCERNS e461b9d (opus): read_list.py (parse ## Read in full → existing files, realpath dedup, ≤10), recorded only on a full owned injection; lineage.py marks a whole-file Read; context_warn appends one line on the next non-whitelisted, non-hard, non-sub-agent prompt; 18 tests (fail on main). Deviations: Bash cat does not count (OQ6); header-only tiers record nothing; whitelisted/HARD prompts carry the reminder forward.
librarian on OQ (timing): keep "next prompt" — after a manual /compact or /clear it is an up-front nudge on the opener, after an auto-compaction mid-turn a follow-through; both are useful and arming after the first turn needs new ordering state. Overlap with H3 noted (read_list._SECTION must follow any heading rename).
dispatch: reviewer opus — hook logic
