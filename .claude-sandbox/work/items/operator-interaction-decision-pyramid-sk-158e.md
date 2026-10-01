---
id: operator-interaction-decision-pyramid-sk-158e
title: "operator-interaction: decision-page skill — put a set of decisions to the operator as an answer page"
short_display_name: decision page skill
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
operator 2026-10-01: "I'd rather call it `decision-page`, pyramid is too metaphorical" — skill renamed to decision-page; relayed to the implementer mid-build
return: implementer DONE e397c93
changed: plugins/operator-interaction/skills/decision-page/ (SKILL.md, references/cards-schema.md, references/fallback.md, assets/index.html, assets/cards.example.json) — the new skill; README.md (operator-interaction skill row, paragraph); CLAUDE.md (layout line); operator-interaction plugin.json + marketplace.json (description names each skill); decisions SKILL.md (two-line pointer)
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a234af080c0fb09f4 round 1
verdict: NEEDS_CHANGES round 1 at e397c93
findings:
  1. [medium] SKILL.md:73,85-86; cards-schema.md:84-86 — stale answers survive a republish and are handed back again (tell me / later re-ask under the same number)
  2. [medium] cards-schema.md:84-85; SKILL.md:62,86,98 — default db rules let any Contributor write; answers are handed over as the operator's
  3. [medium] index.html:204-209,221-239,297 — n, option letters and follow-up keys reach innerHTML unescaped (XSS reproduced in jsdom)
  4-12. [low/nit] empty first-card o throws; all option letters bold; flat Rec line lacks unknown; ⚠ as card not block, no if-left/round-costs/if-unanswered fields; republish needs file_path and a prior files read; "no design pass" vs the Artifact tool's design rule; unbounded retries and overlapping sets; catalog Depends-on for the Artifacts runtime; nits
librarian rulings: 1 — each card carries a revision (bumped when the card changes); an answer counts only when its `at` is after that card's revision time, and the caller records the time of each read so a read hands over only answers newer than the last read; 2 — write rules owner-only (the operator who owns the artifact); readers may view; 3 — escape every field reaching HTML, validate n as an integer and option letters as a-z; 7 — a ⚠ one-way decision renders its per-option sections (what happens, undo, who) and the optional if-left / round-costs / if-unanswered fields exist in the schema; 9 — the template is the page's design: the skill names the artifact-design guidance as satisfied by the shipped template, and any change to the template goes through it; fix 4-6, 8, 10, 12; 11 — add the Artifacts runtime to the plugin's description/catalog note as a soft external need
dispatch: implementer opus medium — resume
agent: implementer aee46bd9c5802babb round 2
