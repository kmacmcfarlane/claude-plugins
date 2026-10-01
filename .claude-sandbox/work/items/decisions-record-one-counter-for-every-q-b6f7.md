---
id: decisions-record-one-counter-for-every-q-b6f7
title: "decisions record: one counter for every question, closed N: lines, <repo>#N references"
short_display_name: one counter, closed lines
type: feature
status: done
priority: 2
created: 2026-09-30
updated: 2026-10-01
closed: 2026-10-01
refs:
  - .claude-sandbox/investigations/5140-decision-lifecycle/03_final.md
  - 5140 answers 98, 99
---

5140 C2 with answers 98 a and 99 c (pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: librarian references/decisions.md and work-items references/format.md gain closed N: acted <commit|item> | rule <path> | superseded by M, and <repo>#N for another repo's decision; every question put to the operator takes a number from the one counter (series labels R/G/P, OQ become tags; the opt-in dialog is the one exception). ^decision N: / ^answer N: keep their shapes (estate parsers).

## Handoff
- doing: review round 2: reviewer a4c0ac1f35c166622 on 6319e7e
- next: CLEAR → land; then 3716 (C7, same file), 728a and 8edb (after b6f7)
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-record-one-counter-for-every-q-b6f7 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-record-one-counter-for-every-q-b6f7
dispatch: implementer opus medium — opus signal: changes a stored contract (format.md) and librarian rules; given plan 5140 03 C2 (wave 3, 132 a)
agent: implementer aed94609b2cc4a2a3 round 1
return: implementer DONE_WITH_CONCERNS cdb5849
changed:
  plugins/dev-flow/skills/librarian-mode/SKILL.md — § Report numbering sentence: one counter, labels as tags, opt-in exception, <repo>#N
  plugins/dev-flow/skills/librarian-mode/references/decisions.md — numbering row, label: card line, Closed bullet, Another repo's decision
  plugins/work-items/skills/work-items/references/format.md — One counter, <repo>#N, § Closed with a reader regex
note: label: is a new (indented, unparsed) card line — 98 a says labels become tags; reviewer to judge whether it is an api-name needing the operator
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a4c0ac1f35c166622 round 1
verdict: NEEDS_CHANGES round 1 at cdb5849
findings:
  1. [medium] decisions.md:56, 80-84; format.md:345 — label: is a new stored field shipped unraised (api-name)
  2. [medium] format.md:414-415 vs decisions.md:173-174 — drop needs no closed line in one, every answer without one is "not closed" in the other
  3. [medium] decisions.md:169-177; format.md:402-415 — no rule for an answer carried out by several changes, or by no change
  4. [low] decisions.md:82-84 — a rendering rule in the binding; numeric labels collide with decision numbers
  5. [low] <repo> = the sweep's directory name: unstable across machines/worktrees
  6. [low] SKILL.md:290-291 — the rename gate is a second ask outside the counter
  7. [nit] SKILL.md:294 long line; 8. [nit] format.md:345 names librarian-mode's private field
librarian rulings: 1 — no new field: the source label rides in the card's what: line, e.g. "(was OQ3)"; 3 — several changes: the closed N: line is written when the last one lands (the answer stays open until then); no change: `closed N: acted <the item id the answer was recorded on>`; 4 — drop the rendering rule; a label is never a bare number; 5 — <repo> is the name of the repo's origin remote (basename, no .git), else the main checkout's directory name; 6 — the session-name gate is the second named exception; 2, 7, 8 fix as found
dispatch: implementer opus medium — resume
agent: implementer aed94609b2cc4a2a3 round 2
return: implementer DONE_WITH_CONCERNS 6319e7e
dispatch: reviewer opus high — resume
agent: reviewer a4c0ac1f35c166622 round 2
verdict: CLEAR round 2 at 6319e7e
notes: prior 1-8 FIXED; new low 9 (<repo> origin name vs wi estate's directory name), nit 10 (label in text vs what:) — filed with C1 (728a) as acceptance notes; 3716 must keep the 'answer N: drop' wording C1 keys on
landed: 0eb4a50
- 2026-10-01 done: 0eb4a50
