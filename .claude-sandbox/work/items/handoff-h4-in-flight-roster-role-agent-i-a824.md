---
id: handoff-h4-in-flight-roster-role-agent-i-a824
title: "handoff H4: in-flight roster (role, agent id, round) and no handoff files in session scratchpads"
type: feature
status: doing
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:00Z
created: 2026-09-22
updated: 2026-09-22
---

Checkpoint handoff format gains an in-flight list per role with agent ids and round; rule: files a successor needs are never left only in a session scratchpad (copy to the item/series or list for copy). Docs across context-guard checkpoint and dev-flow librarian-mode ending-the-session. Opus/opus. Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — per plan routing (executable hook logic or two-plugin doctrine)
impl r0 DONE 83b9a0d (opus): handoff-format ## In flight (role — item — agent id — round — waiting on) + ## Copy forward; resume-by-id rule (same process; fresh process re-dispatches from the roster's round); scratchpad sweep in Step 4a; never checkpoint inside a sub-agent (FM13); librarian ending-the-session names agent ids per role and where brief templates live. Docs only, 3 files.
dispatch: reviewer opus — rule 4
