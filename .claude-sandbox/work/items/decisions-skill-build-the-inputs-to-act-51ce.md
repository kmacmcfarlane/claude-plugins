---
id: decisions-skill-build-the-inputs-to-act-51ce
title: "decisions skill: build the inputs-to-act floor item, card part and checks from the dcf8 series"
short_display_name: build decisions carry needed inputs
type: feature
status: doing
priority: 1
deps:
  - decisions-skill-every-decision-carries-t-dcf8
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T06:28Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - decisions-skill-every-decision-carries-t-dcf8
---

Build the CLEAR series .claude-sandbox/investigations/decisions-skill-every-decision-carries-t-dcf8/ (00-03 with Supersedes applied): floor item 10, the inputs part, worksheet F and cold read, gallery 27-28, rationale, Rulings moved whole to references/rulings.md, decision-page act field with its check, tests/test_act.py, librarian decisions.md store line, README.md:647 and CLAUDE.md layout. Waits on decision 184 (names and shape of the inputs part).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
findings: carried — (1) INDEX base is main @ d00a84f with 18c4 landed (SKILL.md and gallery.md only); SKILL.md expected near 3120 words after the change
decision 184: What should the new part of a decision card that lists what you need to act (paths, commands, text to paste) be called, and should it be a separate part at all? — options: (a) a separate part named "To act on (x):" on the card, "act" on the answer page, "to act (x):" in the store [recommended] | (b) a separate part with plainer names: "Steps for (x):", "steps", "steps (x):" | (c) no new part: write the inputs into each option's own text | (z) decide later
  raised: 2026-10-08T05:50Z
  why ask: api-name — the page field and the store line are names other sessions parse and store (principle 5)
  impact: Effect → the build can start; every card that asks you to act carries its paths, commands and paste text in one place · Wait: blocks the build · reach: the decisions and decision-page skills in every repo, and the librarian's store · undo: renaming after it ships breaks stored cards and pages · cost: none
  context: the plan also moves the skill's Rulings list into references/rulings.md to keep the skill under its size guide; no ruling's wording changes
answer 184: a (chat, 2026-10-08T06:28Z; read as: (a) a separate part, To act on (x): / act / to act (x):)
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-skill-build-the-inputs-to-act-51ce
budget: 2026-10-08T06:28Z build waived — operator waiver 2026-10-08T06:28Z (spend still measured)
dispatch: implementer opus medium — build from the CLEAR series (skill rules and tests)

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a29f52488dc1ec5ae
return: DONE a6e76d0 (floor item 10, widened gloss, line-only condition, cold read; rulings.md move; To act on in rendering; gallery 27-28; rationale; page act field and check; test_act.py 15 tests; librarian store line; README, CLAUDE.md; SKILL.md 3515 -> 3152 words)
changed: decisions SKILL.md, references/{rulings (new), worksheet, rendering, gallery, rationale}.md, decision-page assets/{index.html, cards.example.json}, references/{cards-schema, fallback}.md, SKILL.md, tests/test_act.py (new), librarian-mode references/decisions.md, README.md:647-651, CLAUDE.md
dispatch: reviewer opus high — review round 1
agent: reviewer a503a9fb3220443de
