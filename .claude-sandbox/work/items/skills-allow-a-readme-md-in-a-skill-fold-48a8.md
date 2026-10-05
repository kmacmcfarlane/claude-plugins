---
id: skills-allow-a-readme-md-in-a-skill-fold-48a8
title: "skills: allow a README.md in a skill folder when it carries the user-facing footer"
short_display_name: skill-folder README allowed
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-05T23:12Z
created: 2026-10-05
updated: 2026-10-05
refs:
  - peer marketplace 2026-10-05, relaying its operator
---

Peer marketplace (librarian) 2026-10-05, relaying its operator's decision: per-skill human docs live as README.md beside SKILL.md (a page beside the skill stays current); bundled files cost no context until read, so the concern is clutter, not loading. Today three checks fail it: dev-cycle references/review-checklist.md's item 'No README.md inside the skill folder' (~:91) and its lint 'test -f $d/README.md && echo FAIL' (~:103), and kit-dev create-skill (~:107). Change: allow a skill-folder README.md whose last line is the footer (item: README footer); FAIL only when the footer is missing. Relayed operator decision: confirm with the operator here before building (decision 157).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 157: Confirm the relayed README decisions: allow README.md inside a skill folder when it ends with the footer, and end every README with "*User-facing documentation, not agent instructions.*"? — options: (a) confirm both, with that footer wording [recommended] | (b) confirm both with different wording (say it) | (c) not here | (z) decide later
  raised: 2026-10-05T20:51Z
  what: two relayed operator decisions from the marketplace librarian's session: skill-folder READMEs allowed with a footer (skills-allow-a-readme-md-in-a-skill-fold-48a8), and the footer on every README across the estate (readme-footer-every-readme-md-ends-with-c137)
  why now: kappa-dev ships skill READMEs now and treats them as an approved exception until our checks change; it asks for our final wording
  why ask: your-call — these are your decisions made in another session, and they change this repo's skill-layout rule and every README here
  context: the marketplace session relayed your choice of per-skill README pages · you confirm it here so this repo's checks and conventions follow — then: today review-checklist.md (~:91, ~:103) and kit-dev create-skill (~:107) fail a README in a skill folder; skill files cost no context until read
  stakes: reversible, narrow — skill-folder layout and README endings
  (a) confirm both, same wording — both items get planned; kappa-dev and this repo use one footer — undo: an edit — who: every skill author and README here
  (b) different wording — tell me the line; I send it to marketplace so kappa-dev matches
  (c) not here — this repo keeps the no-README rule; marketplace is told
  (z) decide later — kappa-dev keeps its exception
  rec: (a) · basis strong — your own decision, relayed with the evidence that bundled files cost no context until read
  unknown: none
answer 157: a

## Notes
- 2026-10-05 claimed by Kyle-McFarlane@401123cbad11
target: full skills-allow-a-readme-md-in-a-skill-fold-48a8 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/skills-allow-a-readme-md-in-a-skill-fold-48a8
dispatch: implementer sonnet medium — build (rule text + README footers; canonical wording/docs kind in a kit repo; closes c137 too)
agent: implementer a584d80ad91257072 round 1
