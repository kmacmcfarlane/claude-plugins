---
id: 2edb-7117-review-lows-frontmatter-wordin-4b6a
title: 2edb + 7117 review lows (frontmatter wording, no-modal wording)
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:40Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 2edb/7117 reviews
---

From 2edb and 7117 reviews (both CLEAR) 2026-09-22. 2edb: review-checklist.md:75 'Quote argument-hint whenever it is present'; create-skill SKILL.md template: note 'delete these lines unless needed' beside the three optional keys (example disable-model-invocation: true is the opposite of the default); agent-brief.md:72 rewrap. 7117: SKILL.md red flag → 'Opening any modal question outside the opt-in dialog (references/opt-in.md)'; opt-in.md re-entry fallback: file/reuse an item for the opt-in decision, options Scope/Checks/Push; ending-the-session.md step 4 order names the inventory before the checkpoint close; walkthroughs.md:18 'three decisions, each numbered'.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full 2edb-7117-review-lows-frontmatter-wordin-4b6a /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/2edb-7117-review-lows-frontmatter-wordin-4b6a
dispatch: implementer opus — more than one plugin (kit-dev create-skill + dev-flow), rule 2
agent: implementer a812050d4754bed89 round 1
return: implementer DONE 724c92b
changed: dev-cycle references/{review-checklist,agent-brief}.md, kit-dev create-skill SKILL.md (template), librarian-mode SKILL.md (red flag), references/{opt-in,ending-the-session,walkthroughs}.md
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a5190c17bfd9cc6ac round 1
verdict: NEEDS_CHANGES round 1 at 724c92b
findings:
- [medium] opt-in.md:42-44 — the re-entry fallback files a work item, but opt-in runs before the store exists (first-start.md:14 inits only once a Scope is written). Librarian decision on the pass: carry the decisions in the Report with no item, and file them once the store exists (no store-creation exception).
- [low] :43 "Scope, Checks, Push" — the Scope-alone path asks only Scope; [low] review-checklist.md:86 106 chars; [low] ending-the-session.md:124 114 chars; [nit] SKILL.md:273 red flag omits "never with agents in flight".
dispatch: implementer opus — fix round 1 (resume)
agent: implementer a812050d4754bed89 round 2
