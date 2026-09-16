---
id: librarian-mode-push-main-after-each-repo-e3a9
title: "librarian-mode: push main after each Report"
type: feature
status: doing
priority: 1
owner: unknown@4d338747396e
claimed: 2026-09-16T17:33Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16: the librarian should push commits at a reasonable point instead of never. Librarian decision on the point: right after each Report batch is sent (so what the operator reads is what is on origin) and again at Ending the session; local main only, fast-forward only (git push origin main, never --force, never worktree branches or tags); a rejected non-fast-forward push is not fixed by pulling or rebasing — stop and put it under decisions needed. Peer requests still cannot trigger a push early. Acceptance: Critical's 'Never push' bullet replaced by the bounded rule; Intake peer rule and 'Refuse what is out of scope' say 'push early / push anything but main'; Report section ends with the push step; references/ending-the-session.md adds the final push; Red flags 'Pushing, tagging, or opening anything remote' becomes 'pushing anything but fast-forward main after a Report, tagging, or opening anything remote'; SKILL.md stays at or under 19,000 chars.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (doctrine: the Critical list; the librarian's own procedure)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer opus returned DONE, commit 5dc9825 (SKILL.md 18,989 chars); reviewer opus round 1 dispatched 2026-09-16 17:36:19
- review round 1: NEEDS_CHANGES — 1 medium (session-end order handoffs -> final Report -> push leaves a rejection with no Report to land in), 3 lows (Critical bullet has no reason; Red flags phrase parses two ways; no-origin case unhandled). Librarian ruling: at session end the order is handoffs -> push -> final Report, so the final Report carries any rejection under decisions needed; mid-session order (Report -> push) stands. Fix round 1 sent 2026-09-16 17:39:23, tier unchanged (opus, resumed).
