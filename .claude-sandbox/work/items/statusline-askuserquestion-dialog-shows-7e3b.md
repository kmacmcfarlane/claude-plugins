---
id: statusline-askuserquestion-dialog-shows-7e3b
title: "statusline: AskUserQuestion dialog shows no status line - verify and document"
type: spike
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T18:07Z
created: 2026-09-20
updated: 2026-09-21
refs:
  - "peer: agent-harness-fc (uds 160.sock)"
---

Peer relay 2026-09-19/20 from agent-harness-fc, operator: 'The AskUser question tool also doesn't display the statusline, which is annoying because it's harder to orient to that session when I switch there then.' Worst moment to lose it: the operator switches INTO a session because it is waiting on them. Acceptance: determine whether anything on the plugin side can change this (statusLine render during a permission/question dialog) or whether it is purely harness rendering; if harness, record it as a known limitation in the statusline skill (and, if useful, file upstream) so it stops being rediscovered; relates to the wider 'status line is not a hook' gap (d193 04).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: researcher sonnet — default (verify a harness behaviour; no code); series .claude-sandbox/investigations/7e3b-dialog-statusline/
