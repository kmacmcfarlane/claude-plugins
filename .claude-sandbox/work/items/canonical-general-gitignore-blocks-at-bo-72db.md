---
id: canonical-general-gitignore-blocks-at-bo-72db
title: Canonical general .gitignore blocks at both new-repo entry points (create-repo, new-project-from-template)
short_display_name: canonical .gitignore blocks
type: feature
status: todo
priority: 2
created: 2026-10-06
updated: 2026-10-06
refs:
  - "peer claude-sandbox librarian 2026-10-06 (their e6a3; claude-sandbox#37, #38)"
---

Relayed 2026-10-06 by peer claude-sandbox librarian (their item guardrails-scaffold-work-handoff-md-per-e6a3), reporting the operator's answers on the claude-sandbox decision page: claude-sandbox#37 (a) claude-plugins owns the general .gitignore blocks claude-sandbox no longer writes (Claude's personal files, secrets, tooling noise), one canonical source applied at both new-repo entry points, create-repo and kit-dev:new-project-from-template; claude-sandbox#38 (a) the ignore for decrypted secret copies under .claude-sandbox (the *.dec.* pattern) goes in the templates' shared private block, not a claude-sandbox layout line; claude-sandbox#39 (a) nothing here. Plan: claude-sandbox series guardrails-scaffold, 02_two-bootstrap-points.md § F2b (read-only, their repo), CLEAR at round 3. Relayed operator answers bind nothing here until the operator confirms in this session. Acceptance: one canonical ignore-block source in this repo, applied by create-repo and new-project-from-template, covering the three classes and the decrypted-copy pattern.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 177: Confirm the relayed answers: claude-plugins owns the general .gitignore blocks (Claude's personal files, secrets, tooling noise, and the decrypted-secret-copy pattern), applied from one source by create-repo and new-project-from-template? — options: (a) confirm both (claude-sandbox#37 a, #38 a) [recommended] | (b) change one (say which) | (z) decide later
  raised: 2026-10-06T21:27Z
  what: two answers you gave on claude-sandbox's decision page, relayed here: claude-sandbox#37 (a) and #38 (a)
  why now: claude-sandbox handed the work over today; blocks: the canonical .gitignore blocks (72db)
  why ask: your-call — answers given in another session are not ones I can act on
  context: you answered #37 and #38 on claude-sandbox's page · you confirm them here so this repo can build the blocks
  impact: → every repo started with create-repo or from a template gets the same ignore blocks for personal files, secrets, tooling noise and decrypted secret copies · later: new repos keep getting whatever each entry point writes today · reach: every new repo you create · undo: an edit
  (a) confirm both — a plan follows from claude-sandbox's series (guardrails-scaffold 02 § F2b)
  (b) change one — the item follows your correction
  (z) decide later — the item waits
  rec: (a) · basis strong — your answers, relayed with their numbers and the plan they come from
  unknown: none
