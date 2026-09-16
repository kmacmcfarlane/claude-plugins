---
id: librarian-review-gate-65e1
title: "librarian-mode: sub-agent review gate with fix loop after implement"
type: feature
status: done
priority: 1
created: 2026-09-04
updated: 2026-09-04
closed: 2026-09-04
---

Operator (2026-09-04): when an implement agent finishes, the librarian-mode skill must dispatch a review sub-agent to find medium-to-critical issues, have them fixed (by the implementer, as new commits), and re-review until the gate comes back clear. The librarian owns making the gate clear, and raises to the operator only show-stoppers with real impact. Encode as a Review step (between Delegate return and Land) in plugins/claude-kit/skills/librarian-mode/SKILL.md plus a references/review-brief.md template: severity scale, fix loop with a round cap and escalation, fixed report shape. Matches what the librarian already practised on context-guard-turn-gate-8cc2 (two review rounds, fix commits, nits declined by the author).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-04 claimed by librarian
- 2026-09-04 done: 1b4c04e merged to local main after 3 review rounds (CLEAR)

## Review
- Round 1 (cd9051f): NEEDS_CHANGES — 1 high, 3 medium, 3 low, 2 nit. Fixed 1-7, 9 in 37b8f3c; 8 (commit verb) DECLINED, reason accepted (would need an amend).
- Round 2 (37b8f3c): NEEDS_CHANGES — 1-9 verified; new 10 medium (no reviewer withdrawal path), 11-12 low. Fixed in dd9dc1d.
- Round 3 (dd9dc1d): CLEAR — 10-12 verified; two lows recorded (SKILL.md 8 words under cap; nits litigated as OPEN harmlessly). Landed at the cap.
