---
id: decisions-skill-cards-and-blocks-in-chat-2bc1
title: "decisions skill: cards and blocks in chat get a Context section like the decision page"
short_display_name: Context section in chat cards
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T20:43Z
created: 2026-10-12
updated: 2026-10-12
refs:
  - operator, chat 2026-10-12
---

Operator, 2026-10-12: the decisions skill's TUI output should have a context section for cards and blocks, similar to how the decision-page works (TLDR, then Context, then Impact). Acceptance: rendering.md's card and block templates lead with a Context section shaped like the page's; gallery and tests follow; relates to decision 206 (chat cards follow the page), still open.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
decided: 2026-10-12T22:25Z scope — the operator's words set the shape (cards and blocks carry a Context section like the page's); no separate plan: the page's context field and its order (TLDR, Context, Impact) are the model; decision 206 (Effect across all options) stays its own question
target: rendering.md card and block templates carry a Context section shaped like the page's context field, in the page's order; worksheet, replies re-show and gallery follow; operator-interaction tests cover it
dispatch: implementer opus medium — build
