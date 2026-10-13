---
id: decisions-record-every-answer-line-keeps-3716
title: "decisions record: every answer line keeps the operator's reply verbatim"
short_display_name: verbatim answer lines
type: feature
status: done
priority: 2
created: 2026-09-30
updated: 2026-10-01
closed: 2026-10-01
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
verdict: NEEDS_CHANGES round 1 at f73da6b
findings:
  1. [medium] format.md:422 (decisions.md:133-143) — a verbatim plain reply beginning "drop …" reads as the drop form to the closed-key reader
  2. [medium] decisions.md:28-30 — the verbatim rule does not bind a librarian without operator-interaction; format.md says verbatim unconditionally
  3. [low] dev-cycle record-lines.md:160-169 — says less than the rule (follow-up)
  4. [low] decisions.md:144-152 — the two existing interim verbatim lines do not match the named shape
  5. [low] decisions.md:133-140 — on a ⚠ read-back, which reply is the verbatim one
  6. [low] decisions.md:142-143 — "(a hold, say)" pre-empts OQ6
  7. [nit] quote marks, " / ", " (read as: " split, batched non-letter numbers
librarian rulings: 1 — a plain answer whose reply opens with a form word (drop, later, you decide, tell me, expand, dig into) is written with the reply in double quotes, so `answer N: drop` stays the drop form's key; older lines unchanged; 2 — the verbatim rule is a store rule and applies without the skill (add it to the :28 exemptions); 4 — the interim lines written before this rule are left as written; 5 — the choice's words are the verbatim reply; the confirmation appends — confirmed "<reply>"; 6 — drop the hold example; a hold reply waits on OQ6 (5140); 7 — a reader splits the read-as on the last " (read as: "; a batched part keeps its words as written, number included unless it is an exact letter; no quote escaping; 3 — filed as a follow-up
dispatch: implementer opus medium — resume
agent: implementer a9fb658940aaa4746 round 2
return: implementer DONE 837994e
dispatch: reviewer opus high — resume
agent: reviewer a37c322ccef1c42c2 round 2
verdict: CLEAR round 2 at 837994e
notes: 1-7 FIXED; new low 8 (⚠ read-back template should quote form-word choices) and nit 9 (case/whole-word) added to follow-up 6665
landed: e4ae4fc
- 2026-10-01 done: e4ae4fc
