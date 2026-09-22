---
id: handoff-h4-in-flight-roster-role-agent-i-a824
title: "handoff H4: in-flight roster (role, agent id, round) and no handoff files in session scratchpads"
type: feature
status: done
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
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
review r1 (opus) at 83b9a0d: NEEDS_CHANGES. Seven Checks OK.
- [medium] ending-the-session.md:26, checkpoint SKILL.md:120 — "beside the item" = .claude-sandbox/work/items/; a non-item .md there makes wi ls/next/lint exit 3 (reproduced). Pass: name the investigation series or a path outside items/; say never into items/.
- [medium] checkpoint Step 7 / librarian Rehydrate — resume-by-id written only where the predecessor reads it; successor's opener and Rehydrate don't say it. Pass: Step 7's opener carries "resume <ids> with SendMessage, do not re-dispatch" when In flight is not None, and/or librarian Rehydrate step 3 resumes ids from doing:/dispatch: lines.
- [medium] resume rule restated 3×, drifted (fresh-process caveat only in handoff-format). Pass: librarian doc points at the checkpoint skill's In flight rule by name; 4b keeps a one-clause pointer.
- [medium] plan's rehearsal acceptance not run. librarian decision: WAIVED — a rehearsal checkpoint in the live librarian session writes the shared repo HANDOFF.md and stands the gate down; H1 is changing the same write path; re-check at H1/F3b landing instead.
- lows: fresh-process "cannot resume" unverified → "try SendMessage first"; "drained" should count a returned-but-unfinished role; "never trims" only true by placement (+ H3 note); "common briefs" names a local habit; nit: sub-agent rule should say what to do instead.
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE 0e707ca (opus): one full In flight rule in handoff-format (returned-but-unfinished counts; fresh process: try SendMessage first); 4b a pointer; Step 7 opener names ids to resume (+ copy-forward paths); copies go to the series, never items/; librarian doc points by name; all lows fixed. OQs → H3: librarian Rehydrate step 3 resumes roster ids; a test pinning In flight/Copy forward out of the trim list.
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at 0e707ca: CLEAR. One full rule, pointers resolve; Step 7 and the librarian closing line agree on resume. Low: librarian closing line omits the Copy forward fact; nits: "survive the section trim"; SKILL.md:131 reflow — moved to H3 (same docs).
Review result: 2 rounds, 1 fix round; 3 mediums fixed, rehearsal waived (librarian, reason recorded); impl opus, review opus. Land checks (librarian): seven suites OK in the worktree; diff read — 3 files in scope.
- 2026-09-22 done: 85a8eec
