---
id: checkpoint-before-the-manifest-write-con-6c43
title: "checkpoint: before the manifest, write conversation-only residue into every open item the session touched"
short_display_name: checkpoint writes residue to items
type: feature
status: done
priority: 1
created: 2026-10-07
updated: 2026-10-08
closed: 2026-10-08
refs:
  - peer kappa-3567 2026-10-07
---

Relayed 2026-10-07 by peer kappa-3567 (sussex/communications/email), feedback from the operator there: 'it should be SOP to add details like this to open work-items before checkpointing.' At their checkpoint an open item lacked six conversation-only points (an unconfirmed operator rule, an alternative proposal, a ticket refinement, an unanswered question about another team's ticket, a bug file:line, a product design question). Suggested: in checkpoint Steps 2/3/4a, for every open or doing item the session touched (the manifest's items: set), audit that its file holds the conversation-only residue (open questions, unconfirmed operator statements, proposals and alternatives, refinements, file:line pointers) and append what is missing (dated section or wi handoff) before writing the manifest. Relayed: confirm with the operator here before building.

## Handoff
- doing: —
- next: answer 179 a: dispatch the build (context-guard checkpoint skill, a residue-audit step for every open item in the manifest's items: set before 4b)
- blocked: —
- learned: —
decision 179: Should checkpoint write conversation-only details into every open item the session touched before it writes the manifest (the operator's request, relayed from the kappa-3567 session)? — options: (a) yes, as relayed: audit each item in the manifest's items: set and append what only the conversation holds [recommended] | (b) no | (z) decide later
  raised: 2026-10-07T18:14Z
  what: a step in the context-guard checkpoint skill, before the manifest: for each open or doing item the session touched, append to the item what exists only in the conversation — open questions, unconfirmed operator statements, proposals and alternatives, refinements, file:line pointers
  why now: relayed today; blocks: its build
  why ask: your-call — you gave it in another session ("it should be SOP to add details like this to open work-items before checkpointing"), and a relayed answer is not one I can act on
  context: you told the kappa-3567 session it should be standard procedure · you confirm it here
  impact: → after any checkpoint, each open item carries what was said about it, so a fresh session or another agent picks it up whole · later: items stay as thin as each session leaves them · reach: every session that checkpoints · undo: an edit
  (a) yes — one more step in every checkpoint; a little more writing at checkpoint time
  (b) no — the manifest stays the only carrier of conversation residue
  (z) decide later — the item waits
  rec: (a) · basis strong — your words, relayed with the case that prompted them
  unknown: none
answer 179: a (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:43:41.825Z; read as: (a) build it)
dispatch: implementer opus medium — build, answer 179 a (skill wording, not mechanical)
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/checkpoint-before-the-manifest-write-con-6c43
agent: implementer ab4e9dc2adb7e867f

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
return: DONE_WITH_CONCERNS 34279a4 (Step 4a½ open-items residue; Step 2 kind 6 pending points; lean and unattended forms; series 00_initial.md)
changed: plugins/context-guard/skills/checkpoint/SKILL.md (Step 4a½ and its hooks into Steps 2, 3, 4a, 4b, lean and unattended paths), references/handoff-format.md (names 4a½), references/design-rationale.md (why)
dispatch: reviewer opus high — review round 1
agent: reviewer afc9882ab7a84380f
verdict: review 1 NEEDS_CHANGES at 34279a4 (must-fix 6: decision line marker, wi handoff claim, cross-store items:, Bash not Edit, --brief omits Notes, undeclared work-items soft dep; medium 7 wi lint misses prefixed KEY=value, filed to work-items; lows 8-11)
decided: scope — finding 6 accepted into scope: README.md catalog row and plugins/context-guard/.claude-plugin/plugin.json declare the existing soft use of work-items (narrow, two-way, inside context-guard's aim)
dispatch: implementer opus medium — fix round 1 (resume ab4e9dc2adb7e867f)
return: DONE_WITH_CONCERNS 7209145 fix round 1 (F1-F7, F9, F11 fixed; F10 part; F8 and F10 trim declined)
changed: README.md (context-guard row: work-items soft dep), plugins/context-guard/.claude-plugin/plugin.json and .claude-plugin/marketplace.json (description in step, F6)
dispatch: reviewer opus high — review round 2 (resume afc9882ab7a84380f)
verdict: review 2 CLEAR at 7209145 (must-fix 0; low 1 store never committed with items: empty, low 2 printf cannot place a line mid-file, nit 3 long line; marketplace.json edit ruled in)
decided: words — fix round 2 for lows 1 and 2 (a store left uncommitted and an instruction no allowed tool can follow; review 2 is below the cap)
dispatch: implementer opus medium — fix round 2, lows 1-3 (resume ab4e9dc2adb7e867f)
return: DONE 8a43631 fix round 2 (low 1 fix text; low 2 python3 insert after the last Notes line; nit 3 fenced grep)
dispatch: reviewer opus high — review round 3 (resume afc9882ab7a84380f)
verdict: review 3 NEEDS_CHANGES at 8a43631 (must-fix 1: the insert snippet reads fenced ## lines as headings; lows: CRLF rewritten to LF, in-place truncate without temp-and-rename)
dispatch: implementer opus medium — fix round 3 (resume ab4e9dc2adb7e867f)
return: DONE 2cc2e0a fix round 3 (fence-aware, CRLF-safe, atomic insert; 22-line snippet; 4145 words)
dispatch: reviewer opus high — review round 4 (resume afc9882ab7a84380f)
verdict: review 4 CLEAR at 2cc2e0a (must-fix 0; lows: no cross-section fence refusal, strict heading match, untested inline snippet; nits: splitlines, blank line) — carried to a wi note follow-up
landed: c6dc5fd (merge --no-ff into main; Checks 10/10 OK; push scan read, clean)
- 2026-10-08 done
