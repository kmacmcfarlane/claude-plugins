---
id: librarian-mode-push-main-after-each-repo-e3a9
title: "librarian-mode: push main after each Report"
type: feature
status: done
priority: 1
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
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
- fix round 1 returned DONE, new commit 7014a59, all four findings fixed; re-review dispatched 2026-09-16 17:40:41 (reviewer opus, resumed)
- re-review (review round 2): NEEDS_CHANGES — findings 1-4 FIXED; NEW medium 5: '--force' now appears nowhere
  in SKILL.md and only in ending-the-session.md, so at a mid-session rejection the librarian has no text
  forbidding a force push (implementer's claim that Report still carried it was wrong); low 6: session-end
  push-before-Report inversion not acknowledged by Critical / Red flags 'Pushing early'.
- fix round 2 (last before the cap): implementer opus -> fable (rule 3), fresh dispatch; reviewer -> fable,
  fresh, prior findings pasted. Dispatched 2026-09-16 17:42:36.
dispatch: implementer fable — rule 3, fix round 2
dispatch: reviewer fable — rule 4
- fix round 2 returned DONE, new commit d4d4931 (SKILL.md 18,998 chars; --force in Critical, Report and troubleshooting; session-end exception in Critical; four wording trims to pay). Review round 3 (last): fresh fable reviewer dispatched 2026-09-16 17:45:57
- 2026-09-16 done: 44a1cce
- review round 3: CLEAR (all prior FIXED; 2 new lows: Troubleshooting pointer list does not advertise the push cases; Critical omits 'fetch/merge' that the references name — recorded, not sent back). Landed merge 44a1cce 2026-09-16 17:48:49. NOTE: the first push under the new rule is held until the operator answers whether the store commit 49952ee (contains a private path) should be scrubbed first.
