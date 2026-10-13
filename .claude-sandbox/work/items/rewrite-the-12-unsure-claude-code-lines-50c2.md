---
id: rewrite-the-12-unsure-claude-code-lines-50c2
title: rewrite the 12 unsure Claude Code lines in three work items to the hint form
short_display_name: unsure internals lines, hint form
type: chore
status: todo
priority: 1
created: 2026-10-13
updated: 2026-10-13
refs:
  - audit-claude-sandbox-on-origin-for-claud-abb8
---

From the abb8 audit, 2026-10-13: 12 current-tree lines in d63e (29,40,59,64,84,87,90,97), 8ab6 (23,29) and e347 (23) state Claude Code facts with no observation method or quote short tool-contract text. Per CLAUDE.md rule 5 when unsure treat as internal: label each with how and on which version it was observed and its doc URL, or replace it with the 'can be derived from Claude Code's internals' hint form, or delete it. Store text only; pushed with the next store push.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (832cec4f); store text only (items d63e, 8ab6, e347)
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — rewrite 12 unsure lines to hint or labelled form (CC source rule)
agent: implementer a7b933fa8b09ebdba round 1
result: DONE round 1 at 46ac071c (d63e 8 lines, 8ab6 2, e347 1; options per line in the agent report)
dispatch: reviewer opus high — fresh (rule 4), review 46ac071c against main for the CC source rule
agent: reviewer a3886ca079d5ad572 round 1 at 46ac071c
verdict: NEEDS_CHANGES round 1 at 46ac071c (3 medium: d63e old-90 hint wrong, observed 2.1.286 in lib_context.py; d63e old-84 hint implies undocumented locations, rule 4; 8ab6:23 unlabelled tick claim from a v2.1.280 read + hint topic is prompt content; 3 low/nit: 8ab6:23 inference under a documented label, 8ab6:29 unlabelled Skill-tool fact, d63e:43 compaction cite; nit d63e:29 cite platform context-windows page)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer a7b933fa8b09ebdba round 2
result: DONE round 2 at 1394dbeb (all 7 findings applied; /clear hint and HARD-gate clause on 8ab6:23 kept)
dispatch: reviewer opus high — resume, round 2
agent: reviewer a3886ca079d5ad572 round 2 at 1394dbeb
verdict: NEEDS_CHANGES round 2 at 1394dbeb (2 low, exact wording: 8ab6:23 anchor run-a-prompt-repeatedly-with-/loop; HARD-gate clause cite hooks#userpromptsubmit; all round-1 fixes exact; /clear hint accepted)
decided: 2026-10-13T21:10Z cap — 2 low with exact wording left: a finish round (authority answer 145)
dispatch: implementer opus medium — resume, finish round
agent: implementer a7b933fa8b09ebdba round 3 (finish)
result: DONE finish at c4b68f0b (both lows exact; diff read by the librarian: 2 words on 8ab6:23)
verdict: CLEAR after 2 fix rounds, 1 finish at c4b68f0b (finish read by the librarian, exact)
