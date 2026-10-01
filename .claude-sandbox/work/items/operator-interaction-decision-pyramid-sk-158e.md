---
id: operator-interaction-decision-pyramid-sk-158e
title: "operator-interaction: decision-pyramid skill — put a set of decisions to the operator as an answer page"
short_display_name: decision pyramid skill
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T01:17Z
created: 2026-10-01
updated: 2026-10-01
refs:
  - operator 2026-10-01 chat
  - .claude-sandbox/investigations/69ee-pyramid-answer-page/
  - decision-streams-decisions-carry-a-sourc-4d29
---

Operator 2026-10-01: 'file it and plan it now so we can get it landed now' (after asking whether the decision pyramid skill had landed, to try it in another conversation). Authorizes this item beyond tonight's waves 1-3. Acceptance: a new skill in plugins/operator-interaction (name decision-pyramid, the operator's words) that renders a set of decisions — in the decisions skill's current card format (why ask with class, Context: cue, options with impacts, rec, basis) — into the 69ee answer page as template + data (assets: index.html, cards.json schema), publishes it with the Artifact tool and the db capability, reads answers back with ArtifactData and hands them to the caller to record (verbatim, per the caller's store rules); 4d29's layout requirements (short names, decision slugs with popups, flat essentials plus folds, template + data); a fallback when page artifacts are unavailable (the tick-box doc from 129 (c), or the plain decisions block); generic — no path into dev-flow; README catalog row and CLAUDE.md layout in the same change.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
target: full operator-interaction-decision-pyramid-sk-158e /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/operator-interaction-decision-pyramid-sk-158e
dispatch: implementer opus medium — opus signal: a new skill (marketplace shape: catalog + layout); feature with no plan: /investigate then /implement (operator-authorized 2026-10-01)
agent: implementer aee46bd9c5802babb round 1
