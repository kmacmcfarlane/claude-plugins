---
id: librarian-mode-75-sop-follow-up-wording-d72e
title: "librarian-mode 75% SOP: follow-up wording from review"
type: chore
status: todo
priority: 3
created: 2026-09-18
updated: 2026-09-18
refs:
  - reviewer report, item librarian-mode-at-75-context-checkpoint-ce46
---

From the ce46 re-review 2026-09-18 (all low/nit): (10) ending-the-session.md names the advisories by the '[claude-kit context gate]' prefix — after the plugin-factoring merge the gate prints '[context-guard context gate]'; match by the advisory bodies only; (11) 'store-only — the work-item store and the manifest': .claude-sandbox/HANDOFF.md is neither tracked nor ignored and handoff-format.md says trackInHost governs it — commit the manifest only when trackInHost tracks it; (12) drop 'reads the status-line gauge' (the model cannot see it; the advisory latches and arrives on the next prompt) or say read the gate state file; (13) 'the one time the push precedes its Report' is now false (75% does too). Lands on the factored layout after the merge.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

- 2026-09-18 (from 5cdb impl): also fix librarian-mode ending-the-session.md "session-addressed" (handoff-format says work-addressed) and add the repo-state-outranks-manifest clause to its precedence line. Bundle into the librarian chores item.
