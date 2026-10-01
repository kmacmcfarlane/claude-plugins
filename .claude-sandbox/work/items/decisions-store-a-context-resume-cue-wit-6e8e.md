---
id: decisions-store-a-context-resume-cue-wit-6e8e
title: "decisions: store a Context: resume cue with every decision when it is raised"
short_display_name: resume cue
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T00:01Z
created: 2026-09-30
updated: 2026-10-01
refs:
  - .claude-sandbox/investigations/a99c-operator-freshness-signals/INDEX.md
---

a99c D2, answer 119 b (pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: a99c 01/03 D2 — a Context: cue (where you left it · what you decide now) stored when raised and shown under while it waited on a cold re-show.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-store-a-context-resume-cue-wit-6e8e /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-store-a-context-resume-cue-wit-6e8e
dispatch: implementer opus medium — opus signal: changes what the decisions skill and librarian-mode do; given plan a99c D2 (wave 2, 132 a)
agent: implementer ab8913da1d118e0f0 round 1
return: implementer DONE_WITH_CONCERNS 9e9b1e6
changed:
  plugins/operator-interaction/skills/decisions/SKILL.md — Card entry names the cold reader's Context: cue
  plugins/operator-interaction/skills/decisions/references/rendering.md — card template, when the cue is written, cold re-show order, backfill
  plugins/operator-interaction/skills/decisions/references/gallery.md — example 20 cards carry the cue
  plugins/dev-flow/skills/librarian-mode/references/decisions.md — stored context: field on every card, backfill
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a471fb33f7c6d3d58 round 1
verdict: NEEDS_CHANGES round 1 at 9e9b1e6
findings:
  1. [medium] librarian decisions.md:58, 83-88 — context: now holds the cue only; a block's lost-context facts have no stored field, and rendering renders only from stored fields
  2. [medium] gallery.md:18-55 — example 1's cold cards 41/45 lack Context:, block 43 does not open with the cue
  3. [low] decisions SKILL.md:139-141 — wording ties writing the cue to a cold reader
  4. [low] SKILL.md § Rulings — no entry for 119 b with (c) as the alternative not taken
  5. [low] decisions.md:93-98 — backfill misses old block context: lines holding facts
  6. [low] worksheet.md:17-18 — cold card's cue not mentioned (scope widened: one clause)
  7. [nit] rendering.md:80-85 — a caller with no store: where the cue lives until re-show
librarian ruling on 1: no new stored field name (that would be an api-name the operator has not seen); the block's facts ride on the same context: line after the cue (one physical line, a fixed separator), and an old block context: line with facts and no cue is read as facts with the cue backfilled (closes 5)
dispatch: implementer opus medium — resume
agent: implementer ab8913da1d118e0f0 round 2
return: implementer DONE_WITH_CONCERNS a3c7c1a
changed: + decisions references/worksheet.md (one clause, finding 6); SKILL.md § Rulings entry (finding 4)
dispatch: reviewer opus high — resume
agent: reviewer a471fb33f7c6d3d58 round 2
