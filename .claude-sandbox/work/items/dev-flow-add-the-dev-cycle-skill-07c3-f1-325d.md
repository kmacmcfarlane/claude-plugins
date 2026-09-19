---
id: dev-flow-add-the-dev-cycle-skill-07c3-f1-325d
title: "dev-flow: add the dev-cycle skill (07c3 F1)"
type: feature
status: doing
priority: 2
deps:
  - dev-flow-cross-skill-reference-conventio-05bb
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:47Z
created: 2026-09-18
updated: 2026-09-19
---

07c3 plan §F1: new plugins/dev-flow/skills/dev-cycle (full + plan modes, standalone bindings); README/CLAUDE.md layout/plugin.json/marketplace.json in the same commit; librarian-mode untouched. Size L; opus/opus.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — marketplace shape + doctrine, L (rule 2); no gating code

## Carried notes (restored 2026-09-19; wi claim/handoff had dropped them)
- 2026-09-18 (from 81a5): model-routing § Fallback should say the reader checks rate_limits.at / a past resets_at to spot stale data (the block persists when a payload lacks rate_limits). Carry into the moved model-routing.md.

- 2026-09-18 (from 4a19): the implementer brief should prohibit bare git stash/pop (the stash stack is shared across worktrees and sessions); prefer a temp WIP commit or a scratch copy for revert-to-verify. Carry into the moved agent-brief.md.

- (F0 review lows, fold into the moved review-checklist) path split across lines not read; own file shadows a named sibling; only backtick fences, plain toggle (tilde/nested fences); URLs hit the directory-prefix rule; .md.bak read as .md; CLAUDE.md wording "by its backticked name".
- (c5fc review lows) "a typo Claude Code silently ignores" is unsourced; checklist code keeps a hand copy of the 20 allowed keys (state the count so reviewers can compare); create-skill SKILL.md:44 lists only 4 of 15 optional fields.
