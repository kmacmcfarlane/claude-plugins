---
id: wi-add-re-appends-claude-sandbox-to-host-7772
title: wi add re-appends /.claude-sandbox/ to host .gitignore (7f00 recurrence)
type: bug
status: doing
priority: 2
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:16Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - recurrence note in 7f00 body, 2026-09-18
---

Noticed at rehydrate 2026-09-18: an uncommitted recurrence note was appended to closed item 7f00 by another session. In operator-attention, after the ignore line was removed and committed (e5516d2), a later 'wi add' re-appended /.claude-sandbox/ to the working-tree .gitignore, silently ignoring the new item. Acceptance: wi add (and every store-creating path, not only wi init) leaves a host .gitignore that already tracks the store alone. Held until plugin-factoring merges (wi.py moves to the work-items plugin).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic (wi.py)

impl: DONE_WITH_CONCERNS bdc506b — could not reproduce in wi.py; only cmd_init sidecar branch writes host .gitignore. Real writer: claude-sandbox launcher layout.Setup (cmd/claude-sandbox/root.go:739 -> internal/layout/layout.go:115 gitignoreAdd "/.claude-sandbox/", prompt default yes) when trackInHost: false (operator-attention config.yaml:109). Commit is regression tests only (TestHostGitignoreUntouched, mutation-checked). Premise of the title is wrong (like 7f00). Relayed launcher fix to the claude-sandbox librarian.
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — high 1: every_command skips `import` (mutation in cmd_import undetected); lows 2 (global git config isolation), 3 (inherited GIT_DIR etc.), nit 4. Root cause confirmed independently (launcher; claude-sandbox 18a7 filed and dispatched there).
dispatch: implementer opus fix round 1 — resume
