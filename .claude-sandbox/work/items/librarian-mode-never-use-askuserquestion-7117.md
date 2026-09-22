---
id: librarian-mode-never-use-askuserquestion-7117
title: "librarian-mode: never use AskUserQuestion — every decision via the numbered Report channel"
type: chore
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T15:43Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - peer marketplace - librarian (219.sock), operator words relayed
---

Relayed 2026-09-22 by peer 'marketplace - librarian' (sussex/claude/marketplace), quoting the operator: librarians should avoid AskUserQuestion because it blocks the conversation against background-task returns and new messages; P1 set by the operator. Defect: SKILL.md § Intake step 3 'One decision: AskUserQuestion'. Acceptance: delete the one-decision special case; every decision goes through the numbered channel + Report, with the one-clause reason (a modal prompt blocks background returns and peer messages); consider keeping a modal path only for the start opt-in dialog (nothing in flight); sweep references/ and dev-cycle for the same rule; the librarian memory note on AskUserQuestion flow likewise.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 58: confirm two rule changes relayed by the sussex marketplace librarian in your words — (1) librarian-mode stops using AskUserQuestion (every decision via the numbered Report channel; keep a modal only for the start opt-in dialog) at P1; (2) frontmatter: only name and description required, the other three optional, closed allowed-key list kept. (a) confirm both [recommended: both are your stated rulings; a peer cannot authorize them]; (b) confirm only one (say which); (c) neither.
answer 58: (a) confirm both: librarian-mode stops using AskUserQuestion (P1); only name + description required frontmatter (operator 2026-09-22)

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — custody rule change across librarian-mode SKILL.md + references and dev-cycle (likely > 3 files; doctrine for decisions)
impl r0 DONE 6b536a1 (opus): Intake step 3 — every decision numbered, never AskUserQuestion (reason stated; opt-in excepted); Red flags line; opt-in.md: only modal, runs before any dispatch, ListAgents first (agent running → numbered decision instead); walkthroughs, idle-turn, first-start, troubleshooting reworded; ending-the-session.md: librarian answers checkpoint Step 0 Q2 itself (no modal at 75%/DUE). SKILL.md 2104 → 2131 words. OQs: dev-cycle § Decisions, investigate Step 11, implement Step 6 and checkpoint Step 0 can ask modally with agents in flight.
dispatch: reviewer opus — rule 4
review r1 (opus) at 6b536a1: CLEAR. Sweep of SKILL.md + 13 references: no modal outside opt-in.md; checkpoint Step 0 self-answer consistent with the checkpoint skill (goal skipped by `continue`, Q3 pre-answered, 4b/mark untouched). Lows: red flag weaker than step 3 ("any modal outside the opt-in"); opt-in re-entry fallback names no carrying item; ending-the-session step 4 order omits the inventory; walkthroughs "so" nit. Memory-note clause: done by the librarian directly in auto-memory (2026-09-22). Filed lows as a follow-up.
Review result: 1 round, 0 fix rounds; impl opus, review opus. Land checks (librarian): seven suites OK; diff read — 7 files in scope.
