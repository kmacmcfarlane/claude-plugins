---
id: librarian-mode-a-concise-team-summary-af-a934
title: "librarian-mode: a concise team summary after each push (prose, no table)"
type: feature
status: doing
priority: 0
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - peer marketplace - librarian (219.sock), operator words relayed
---

Relayed 2026-09-22 by peer 'marketplace - librarian' (sussex/claude/marketplace), quoting the operator: 'I want a p0 item to summarize changes concisely when changes are pushed so I can notify my team (don't use a table for copy-paste readibility).' Additive to § Report's four lines (unchanged: they are the audit trail). Acceptance: after each push, one short prose/bullet summary covering everything in that push, written for people who did not watch the run — what changed, not how it was reviewed; says whether anything changes what a human reader must DO; ends with the commit range; no tables (Slack/Teams/email/phone paste). Scope: librarian-mode SKILL.md § Report + references; consider dev-cycle's land report likewise.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 61: confirm the P0 relayed by the sussex marketplace librarian in your words — after each push the librarian also writes one concise prose summary of the whole push for your team (what changed, anything a human must now do, commit range last; no tables); the four-line Report stays as is. (a) confirm [recommended: your stated ask; a peer cannot authorize it]; (b) change the shape (say how); (c) drop.
answer 61: (a) confirmed (operator 2026-09-22)

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — librarian-mode custody doctrine (Report / push rule)
impl r0 DONE 32c91eb (opus): references/team-summary.md (when, shape, pasteability — no table/headings/bold, fenced text block, do-line, Commits: old..new last, two examples); § Report 2-line pointer (+26 words); ending-the-session + walkthroughs place it after the final Report. Deviation: no summary for a rejected or store-only push. OQ: dev-cycle land report on a chosen push.
dispatch: reviewer opus — rule 4
review r1 (opus) at 32c91eb: NEEDS_CHANGES. Seven Checks OK; four Report lines byte-identical.
- [medium] team-summary.md:36-40 + SKILL.md:228 — OLD must be captured before the push, but the pointer says "after each push" → a librarian reads the recipe after pushing and gets new..new. Pass: OLD from `origin/main@{1}` after the push (reflog verified), or capture in SKILL.md's push line.
- lows: say the fence is only the operator's copy boundary, not part of the message; backticks show literally in email/SMS (note or limit to commands); no origin remote → treat like Push: none; nit: description "four lines".
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE c7da3c6 (opus): OLD from origin/main@{1} after the push + a log check; fallback: the push's own old..new output line, then note origin/main before each push; lows a/b/c fixed; (d) declined — the description stays short. OQs → follow-up: dev-cycle land report on a chosen push.
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at c7da3c6: CLEAR — origin/main@{1} correct on a fresh clone's first push, a normal push, a second push, after a no-op fetch; fails loudly with no reflog. Nits: SKILL.md fallback wording, NEW from origin/main, pointer omits no-origin — follow-up.
Review result: 2 rounds, 1 fix round; impl opus, review opus. Land checks (librarian): seven suites OK; diff read.
