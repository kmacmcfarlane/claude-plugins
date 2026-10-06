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
- doing: CLEAR at 236f948, waiting to land
- next: on 158: (a) merge as is; (b)/(c) one CLAUDE.md sentence changes first (resume implementer a584d80ad91257072, reviewer aebf5a40fcf3c0f45), then merge, Checks, push; tell marketplace it landed
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
return: implementer DONE 9ebed2f (checklist item + lint, create-skill, CLAUDE.md footer bullet with a root-README exemption sentence that pre-states 158 (a); root README untouched; lint tested on 3 cases)
librarian ruling: the exemption sentence stays in the branch but the landing waits on 158; on (b) or (c) one sentence changes before landing
dispatch: reviewer opus high — review round 1
agent: reviewer aebf5a40fcf3c0f45 round 1
verdict: NEEDS_CHANGES round 1 at 9ebed2f
findings:
  1. [medium] create-skill SKILL.md:139 — end-of-skill checklist still says no README; reword to match :107
  2. [medium] dev-cycle agent-brief.md:80 — implementer briefs still say "No README.md inside a skill folder"; replace with the allowed-with-footer rule
  3. [medium] CLAUDE.md:103-105 — "every README.md ends with the footer … root exempt" is false for the agent-facing .claude-sandbox/work/README.md that wi init seeds in every repo; word it as "every README.md written for humans …; a README agents are told to read carries no footer"
  4. [low] review-checklist.md:104 — normalise trailing whitespace and CR before comparing, say "last non-blank line" at :91 (lint otherwise safe under set -euo pipefail)
  5. [low] review-checklist.md:91-92 — the reviewer also confirms the README carries nothing the agent needs and no copy of SKILL.md
  6. [nit] CLAUDE.md:103 rewrap
dispatch: implementer sonnet medium — resume (fix round 1)
agent: implementer a584d80ad91257072 round 2
return: implementer DONE e18e72e (1-6 fixed; lint passes 5 cases incl CRLF and trailing spaces)
dispatch: reviewer opus high — resume (round 2)
agent: reviewer aebf5a40fcf3c0f45 round 2
verdict: CLEAR round 2 at e18e72e
findings:
  1-6 fixed; no old no-README rule left; lint passes/fails 12 scratch cases correctly
  1. [nit] create-skill SKILL.md:107 — "last non-blank line"
  2. [nit] agent-brief.md:80 — rewrap
decided: 2026-10-05T23:15Z ruled-rule-case — a finish round for the two nits while the landing waits on decision 158 · authority: answer 137 · reopen: say so
dispatch: implementer sonnet medium — resume (finish round: nits 1, 2)
agent: implementer a584d80ad91257072 round 3
hold: landing waits on decision 158 (the CLAUDE.md bullet matches its option (a))
return: implementer DONE 236f948 (two nits)
dispatch: reviewer opus high — resume (round 3, finish round only)
agent: reviewer aebf5a40fcf3c0f45 round 3
verdict: CLEAR round 3 at 236f948
findings: none
note: answer 158 — the footer applies only to skill-folder READMEs; the CLAUDE.md bullet is reworded to that before landing
dispatch: implementer sonnet medium — resume (answer 158: CLAUDE.md bullet to skill-folder READMEs only)
agent: implementer a584d80ad91257072 round 4
