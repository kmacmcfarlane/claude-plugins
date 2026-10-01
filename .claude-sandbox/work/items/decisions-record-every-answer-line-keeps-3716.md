---
id: decisions-record-every-answer-line-keeps-3716
title: "decisions record: every answer line keeps the operator's reply verbatim"
short_display_name: verbatim answer lines
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T01:01Z
created: 2026-09-30
updated: 2026-10-01
refs:
  - .claude-sandbox/investigations/5140-decision-lifecycle/03_final.md
---

5140 C7 (no question; rests on the operator's 2026-09-29 05:53Z words, 'a good source of truth to be able to go back to'). Acceptance: 5140 02/03 C7 — every answer line keeps the reply verbatim, including you-decide, drop, reframe, redirect and hold forms, which append — "<verbatim>"; the read-as stays. Same lines as the 100 b build (librarian decisions.md:98-121), which goes first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-record-every-answer-line-keeps-3716 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-record-every-answer-line-keeps-3716
dispatch: implementer opus medium — opus signal: changes a stored-record contract (answer lines); given plan 5140 02/03 C7 (wave 3, 132 a)
agent: implementer a9fb658940aaa4746 round 1
return: implementer DONE_WITH_CONCERNS f73da6b
changed:
  plugins/dev-flow/skills/librarian-mode/references/decisions.md — Answered: verbatim reply on every answer line; forms append — "<reply>"; batch; indented verbatim N line for late additions
  plugins/work-items/skills/work-items/references/format.md — § Operator questions: <reply> verbatim, one physical line
note: verbatim N (indented) is the store's existing interim line shape, not a new parsed field
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a37c322ccef1c42c2 round 1
