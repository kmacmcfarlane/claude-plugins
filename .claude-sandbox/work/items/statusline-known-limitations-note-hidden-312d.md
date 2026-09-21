---
id: statusline-known-limitations-note-hidden-312d
title: "statusline: known-limitations note — hidden during dialogs and permission prompts"
type: chore
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T18:37Z
created: 2026-09-21
updated: 2026-09-21
---

From spike 7e3b (series .claude-sandbox/investigations/7e3b-dialog-statusline/00_findings.md, drafted text there): Claude Code hides the status line during permission prompts, AskUserQuestion, plan approval (documented). Acceptance: a short Known limitations note in the statusline plugin's skill docs using the drafted text, naming the upstream issues (#21349, #26847, #30232) and the title-hook workaround if that lands.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer sonnet — default (one doc note)

## Implementer result
- round 1 DONE dca7de5 (sonnet): ## Known limitations in install-statusline SKILL.md.
- dispatch: reviewer opus — rule 4 floor

## Review round 1 — NEEDS_CHANGES (opus) at dca7de5
- [medium] "Tracked upstream" but all three issues are closed (#21349 completed, #26847 duplicate, #30232 not_planned/stale).
- lows: separate documented (permission prompts) from observed (AskUserQuestion, plan approval); links not clickable.
- dispatch: implementer sonnet — fix round 1 (resume)
- round 1 fix 658ec13: closed-issue states stated; documented vs observed separated; links.
- dispatch: reviewer opus — round 2 (resume)
