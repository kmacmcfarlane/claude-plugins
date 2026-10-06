---
id: add-a-license-to-claude-plugins-public-r-cf96
title: Add a LICENSE to claude-plugins (public repo with no license)
short_display_name: add a license
type: chore
status: todo
priority: 0
created: 2026-10-06
updated: 2026-10-06
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
