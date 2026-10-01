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
