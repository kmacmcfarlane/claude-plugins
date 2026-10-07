---
id: add-a-license-to-claude-plugins-public-r-cf96
title: Add a LICENSE to claude-plugins (public repo with no license)
short_display_name: add a license
type: chore
status: doing
priority: 0
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-07T20:57Z
created: 2026-10-06
updated: 2026-10-07
refs:
  - peer claude-sandbox librarian 2026-10-06 (their item proposal-a-reusable-claude-code-knowledg-31bd)
---

Operator request relayed by peer claude-sandbox librarian 2026-10-06 (operator's words: 'We absolutely need to get a license up on claude-plugins immediately'). GitHub reports the repo public with license:null; no LICENSE file in the tree. Which license is the operator's call (not asked by the peer). Acceptance: a LICENSE file at the repo root with the operator's chosen license, README names it, marketplace/plugin manifests carry a license field if the operator wants one; landed and pushed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 162: Which license should claude-plugins carry? — options: (a) MIT [recommended] | (b) Apache-2.0 | (c) all rights reserved (source visible, no reuse granted) | (d) another (say it) | (z) decide later
  raised: 2026-10-06T03:39Z
  what: the LICENSE file for this public repo (no license today, so legally nobody may reuse the code), copyright Kyle McFarlane 2026
  why now: you asked for a license immediately (relayed by the claude-sandbox librarian); blocks: the license landing, which takes minutes once you choose
  why ask: your-call — the license is yours to grant; the peer did not ask you which
  context: you said a license must go up on claude-plugins immediately · you pick it
  stakes: one-way once published for any copy taken under it (a grant cannot be withdrawn from those copies), narrow otherwise
  (a) MIT — short and permissive: anyone may reuse with the notice kept; the common choice for Claude Code plugin marketplaces — undo: relicense future versions only — who: anyone who copies the repo
  (b) Apache-2.0 — permissive like MIT, adds an explicit patent grant and a NOTICE convention; longer — undo: relicense future versions only — who: anyone who copies the repo
  (c) all rights reserved — states copyright and grants no reuse; the code stays readable but not reusable — undo: grant a license later — who: nobody gains rights
  (d) another — the build uses yours
  (z) decide later — the repo stays public with no license
  rec: (a) · basis partial — permissive and minimal for a plugin kit; a license grants only what you own, so it does not cover the Claude Code bundle-derived passages, which the separate review (e347) handles
  unknown: whether you want the repo to stay public at all (a GitHub setting, outside my reach)
note: 2026-10-06T04:07Z operator on 162, verbatim: "162 - what license am I using for the other projects? What's the TLDR of just using that one I'm already comfortable with? Are the specific reasons not to use that for this particular repo?" (read as: tell me — answered: the operator's own repos claude-kit, claude-sandbox, claude-analytics, claude-templates, checkpoint-sampler, image-dataset-tool carry GPL-3.0; claude-plugins began as the claude-kit plugin, GPL-3.0 there)
decision 162: Which license should claude-plugins carry? — options: (a) MIT | (b) Apache-2.0 | (c) all rights reserved (source visible, no reuse granted) | (d) another (say it) | (e) GPL-3.0, as your other projects [recommended] | (z) decide later
  raised: 2026-10-06T02:58Z
  revised: 2026-10-06T04:07Z — option (e) added and the recommendation moved from (a) to (e) after the operator's question: their own repos use GPL-3.0 and this repo began as the claude-kit plugin (GPL-3.0)
  what: the LICENSE file for this public repo (no license today, so legally nobody may reuse the code), copyright Kyle McFarlane 2026; sole author (1517 of 1517 commits)
  why now: you asked for a license immediately; blocks: the license landing, minutes after you choose
  why ask: your-call — the license is yours to grant
  context: you asked which license your other projects use · you pick this repo's
  stakes: one-way for any copy taken under it; narrow otherwise
  (a) MIT — anyone may reuse, even in closed projects, keeping the notice — undo: relicense future versions only — who: anyone who copies
  (b) Apache-2.0 — like MIT plus a patent grant; longer — undo: future versions only — who: anyone who copies
  (c) all rights reserved — readable, not reusable — undo: grant one later — who: nobody gains rights
  (d) another — the build uses yours
  (e) GPL-3.0 — anyone may use and change it; whoever distributes a changed copy must share it under GPL-3.0 too; matches claude-kit, claude-sandbox and the rest — undo: future versions only — who: anyone who redistributes changes
  (z) decide later — the repo stays public with no license
  rec: (e) · basis strong — your existing choice across your projects, and this code came out of claude-kit under it; the one cost is that anyone who pastes a changed skill into a project they distribute must license that under GPL too
  unknown: none
decision 162: Which license should claude-plugins carry? — options: (a) MIT | (b) Apache-2.0 | (c) all rights reserved (source visible, no reuse granted) | (d) another (say it) | (e) GPL-3.0, as your other projects [recommended] | (z) decide later
  raised: 2026-10-06T02:58Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: the LICENSE file for this public repo (no license today, so legally nobody may reuse the code), copyright Kyle McFarlane 2026; sole author (1517 of 1517 commits)
  why now: you asked for a license immediately; blocks: the license landing, minutes after you choose
  why ask: your-call — the license is yours to grant
  context: you asked which license your other projects use · you pick this repo's
  impact: → the code becomes legally reusable; anyone distributing changes shares them under GPL · later: nobody may legally reuse the public repo · reach: anyone who copies or redistributes it · undo: future versions only; copies already taken keep their license
  stakes: one-way for any copy taken under it; narrow otherwise
  (a) MIT — anyone may reuse, even in closed projects, keeping the notice — undo: relicense future versions only — who: anyone who copies
  (b) Apache-2.0 — like MIT plus a patent grant; longer — undo: future versions only — who: anyone who copies
  (c) all rights reserved — readable, not reusable — undo: grant one later — who: nobody gains rights
  (d) another — the build uses yours
  (e) GPL-3.0 — anyone may use and change it; whoever distributes a changed copy must share it under GPL-3.0 too; matches claude-kit, claude-sandbox and the rest — undo: future versions only — who: anyone who redistributes changes
  (z) decide later — the repo stays public with no license
  rec: (e) · basis strong — your existing choice across your projects, and this code came out of claude-kit under it; the one cost is that anyone who pastes a changed skill into a project they distribute must license that under GPL too
  unknown: none
answer 162: e — "is this what I'm using for other repos in kmacmcfarlane too?" (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:44:29.732Z; read as: (e) GPL-3.0; the question answered yes: claude-kit, claude-sandbox, claude-analytics, claude-templates, checkpoint-sampler and image-dataset-tool carry GPL-3.0)

## Notes
- 2026-10-07 claimed by Kyle-McFarlane@2d49f8460283
target: full add-a-license-to-claude-plugins-public-r-cf96 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/add-a-license-to-claude-plugins-public-r-cf96
budget: 2026-10-07T20:57Z build $10 — default chore
dispatch: implementer opus medium — build (LICENSE GPL-3.0, answer 162 e)
