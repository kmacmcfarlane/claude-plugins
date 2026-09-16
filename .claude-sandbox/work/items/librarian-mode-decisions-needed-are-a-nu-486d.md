---
id: librarian-mode-decisions-needed-are-a-nu-486d
title: "librarian-mode: decisions needed are a numbered list the operator can reference"
type: feature
status: todo
priority: 2
deps:
  - librarian-mode-push-main-after-each-repo-e3a9
parent: librarian-mode-push-main-after-each-repo-e3a9
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16 ('use a list so I can reference it'): when the librarian needs operator decisions, present them as a numbered list, one decision per number, each with its options and their impact, so the operator can answer by number. Acceptance: Report section's 'decisions needed' line format says numbered list; Intake step 3 (Decide, or ask) says the same for multi-decision asks; Examples/model-routing walkthrough updated if they show the line; SKILL.md stays under 19,000 chars. Depends on the push item because both edit the Report section.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (doctrine: Report format)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit 577cfe9; ten trims to pay (claimed duplication-only; two touch text defended in 1420's reviews: 'The transcript is not the record.' in Review 5 and Delegate 3's field list). Reviewer opus round 1 dispatched 2026-09-16 17:58:02 with that focus.
- (from 939c review) rule on the mechanism seam: AskUserQuestion dialog vs numbered prose list — say when each applies.
- review round 1: NEEDS_CHANGES — 2 medium (numbering counter is transcript-only state, contradicting Critical 6;
  Intake 3 says AskUserQuestion while the example shows a numbered prose list — mechanism seam unruled), 1 low
  (trim 8 removed 'The transcript is not the record.' from Review 5, previously restored by 1420), 2 nits. Trims
  1-4, 6, 7, 9 ruled clean duplicates.
- librarian rulings: (1) the counter lives in the store: when a decision is raised, append 'decision N: <one line>'
  to the body of the item it concerns; on re-entry continue from the highest N in any open item, else start at 1.
  (2) one decision -> AskUserQuestion (options with impact, recommendation first); two or more -> the numbered
  prose list, numbered from the counter; in both cases never in the same turn as a heavy analysis.
  (3) restore 'The transcript is not the record.' with a paired trim.
  Fix round 1 sent 2026-09-16 18:01:51, tier unchanged (opus, resumed).
