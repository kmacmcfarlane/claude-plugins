---
id: claude-md-librarian-checks-add-the-statu-66f5
title: "CLAUDE.md ## Librarian Checks: add the statusline-hub test suite"
type: chore
status: done
priority: 2
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

statusline-hub landed with its own suite: (cd plugins/statusline-hub/hooks && python3 -m unittest discover -s tests -q). The Checks list in CLAUDE.md ## Librarian is the operator's opt-in answer; adding the suite of a new plugin keeps its intent (every plugin suite checked). One-line edit; the librarian may not edit custody files, so dispatched.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: c27e375

## Dispatch
- dispatch: implementer sonnet — default (one line)

## Implementer result
- round 1 DONE 0822b6f (sonnet): one Checks line.
- dispatch: reviewer opus — rule 4 floor

## Review round 1 — CLEAR (opus) at 0822b6f
- all six plugin suites now listed.
## Landed
- c27e375.
