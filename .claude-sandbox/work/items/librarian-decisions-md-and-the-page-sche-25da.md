---
id: librarian-decisions-md-and-the-page-sche-25da
title: librarian decisions.md and the page schema follow the chat Context section
short_display_name: Context section follow-ups
type: chore
status: done
priority: 2
deps:
  - decisions-skill-cards-and-blocks-in-chat-2bc1
created: 2026-10-12
updated: 2026-10-12
closed: 2026-10-12
refs:
  - decisions-skill-cards-and-blocks-in-chat-2bc1
---

From 2bc1's build, 2026-10-12: dev-flow librarian-mode references/decisions.md still says a card shows the cue alone as its Context for a cold reader; it should show the stored Context every time (text before ' — then: ' is the terms plus the cue). decision-page cards-schema.md names the decisions block's 'Context you may have lost', a label 2bc1 retired; reword the pointer. Acceptance: both match the decisions skill after 2bc1.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: 2026-10-12 from 2bc1 review 1 finding 7: librarian decisions.md:129-131 reads a context: line with no " — then: " as a block's facts to backfill, while rendering.md now shows it as the card's Context as it stands; decision 160 (20d8, deferred) has such a line; align them

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: librarian decisions.md shows the stored Context every time and reads a context: line as the decisions skill now does (text before " — then: " is the card's Context, after it the block's bullets; a line with no separator is the card's Context as it stands); decision-page cards-schema.md's pointer reworded; decision 160's stored line renders correctly
dispatch: implementer sonnet medium — build (doc alignment to a landed rule: canonical kind)
agent: implementer a9e98bb4769db4a60
return: DONE e0f2f18; dev-flow 78, operator-interaction 138, kit-dev 21 OK; decision 160's line has no separator, renders as the card's Context as it stands, terms then cue; template placeholder also updated
dispatch: reviewer opus high — review round 1 of e0f2f18
agent: reviewer aef7a273eff53b181
verdict: review round 1 NEEDS_CHANGES (must-fix 1: decisions.md:100-101 names references/rendering.md, a path into operator-interaction from dev-flow; minor: a no-separator line carries no block facts, say so; nit: cards-schema pointer, the block shows the facts at medium)
dispatch: implementer sonnet medium — fix round 1 (resume a9e98bb4769db4a60)
return: DONE b912da7 (fix round 1); dev-flow 78, operator-interaction 138, kit-dev 21 OK
dispatch: reviewer opus high — review round 2 of b912da7 (resume aef7a273eff53b181)
verdict: review round 2 CLEAR (must-fix 0; nit: two edited lines not rewrapped, not taken)
landed: 29a1135 (merge of e0f2f18..b912da7); Checks 12/12 OK; cc_scan clean
- 2026-10-12 done
