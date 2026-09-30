---
id: decisions-answer-every-question-inside-a-9ea7
title: "decisions: answer every question inside a batched reply in words, one Read-as per part"
short_display_name: batched replies in words
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T23:30Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/6d2c-batched-decision-replies/INDEX.md
---

6d2c (b), answer 100 b (pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: 6d2c 03 and review r4 — every question inside a reply gets an answer in words; each part of a mixed message gets its Read-as line; the echo happens with the actions; the ⚠ read-back still waits; the build text M1 carried from the series (librarian ruling 2026-09-29). After the build, the in-sample smoke test on rows 13, 15, 16 (about $8-10). No confirm-first trigger (100 is not (c)/(d); 122 moot).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-answer-every-question-inside-a-9ea7 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-answer-every-question-inside-a-9ea7
dispatch: implementer opus medium — opus signal: changes what the decisions skill does (reply handling); given plan 6d2c 03 + r4 M1 (wave 2, 132 a)
agent: implementer a70699c5ec56ef8c2 round 1
return: implementer DONE_WITH_CONCERNS 502bf95
changed:
  plugins/operator-interaction/skills/decisions/references/replies.md — step 3 reworded (r4 M1: echo with the actions, its limit, what stops an action first); new § A message with several replies
  plugins/operator-interaction/skills/decisions/SKILL.md — § Replies table: one row pointing to the new section
  plugins/operator-interaction/skills/decisions/references/gallery.md — example 25, a mixed batch
note: smoke test not run (it would write into the shared config dir, load the operator's hooks, join the peer registry; 35 MB transcript) — filed as an operator-attended follow-up
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a89d6ae7dfaf0dc3f round 1
