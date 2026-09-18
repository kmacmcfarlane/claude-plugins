---
id: librarian-mode-75-sop-follow-up-wording-d72e
title: "librarian-mode 75% SOP: follow-up wording from review"
type: chore
status: doing
priority: 3
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:32Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - reviewer report, item librarian-mode-at-75-context-checkpoint-ce46
---

From the ce46 re-review 2026-09-18 (all low/nit): (10) ending-the-session.md names the advisories by the '[claude-kit context gate]' prefix — after the plugin-factoring merge the gate prints '[context-guard context gate]'; match by the advisory bodies only; (11) 'store-only — the work-item store and the manifest': .claude-sandbox/HANDOFF.md is neither tracked nor ignored and handoff-format.md says trackInHost governs it — commit the manifest only when trackInHost tracks it; (12) drop 'reads the status-line gauge' (the model cannot see it; the advisory latches and arrives on the next prompt) or say read the gate state file; (13) 'the one time the push precedes its Report' is now false (75% does too). Lands on the factored layout after the merge.

## Handoff
- doing: bundled in worktree d72e
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — bundled chores in worktree d72e; >3 files (rule 2)

impl (bundle): DONE 7ace960 (all five; none pre-fixed). Open: agent-brief Commit verbs omit "fixed" (main history uses it).
dispatch: reviewer opus — rule 4
