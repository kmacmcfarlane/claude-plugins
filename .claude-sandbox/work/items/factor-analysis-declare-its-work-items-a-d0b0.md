---
id: factor-analysis-declare-its-work-items-a-d0b0
title: "factor-analysis: declare its work-items and dev-flow needs and degrade without them"
short_display_name: factor-analysis declare and degrade
type: bug
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T08:35Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F3 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F3 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
note: from 4bd4 OQ2 (2026-10-09T08:34Z): this item also carries its peer hint step (KD-2 for factor-analysis / DF-9 for librarian-mode), per .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/ INDEX.md
dispatch: implementer opus medium — build, worktree (bug; acceptance from the 72ef series; doctrine and kit-dev lint on main)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a8b71c236d66dc1af
return: DONE worktree-agent-a8b71c236d66dc1af cdcb523 (kit-dev declares work-items and dev-flow; factor-analysis Step 7 fallbacks with one-clause disclosure; KD-2/KD-3 UNDECLARED and seven stale ALLOWED excuses removed; 11/11 Checks; peer-hint step left for 4bd4)
dispatch: reviewer opus high — review round 1
agent: reviewer ab4397e3c484bd9a0
verdict: review round 1 NEEDS_CHANGES (medium 1: the KD-2 peer hint was left out on a wrong reason — prose hints need no helper (CLAUDE.md Peer hints, Prose skills); the four steps and the KD-2 text are in the 4bd4 series 00:350-370, 01:219; lows: marketplace.json's kit-dev description out of step with plugin.json; the dev-flow fallback path borrows .claude-sandbox/investigations; nits 4-6)
correction: my d0b0 and 64c7 briefs told the builders to leave the peer-hint step out because 'the helper isn't built yet'; prose hints use no helper, so the step belongs in these items, as the 4bd4 OQ2 decision said
dispatch: implementer opus medium — fix round 1 (resume a8b71c236d66dc1af)
