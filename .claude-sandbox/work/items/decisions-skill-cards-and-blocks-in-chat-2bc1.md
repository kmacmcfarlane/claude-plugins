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
agent: implementer af0c58c783a457a0b
return: DONE 2dd7a22; 12/12 OK (operator-interaction 137); order title → What → Context → Impact → Why now → Why ask → options; cue folds into Context as its last clause; stored context: line reused, older cards render as before; ruling recorded with the operator's words as direction; follow-ups filed as librarian-decisions-md-and-the-page-sche-25da
dispatch: reviewer opus high — review round 1 of 2dd7a22
agent: reviewer a80c72469591f38ff
verdict: review round 1 NEEDS_CHANGES (must-fix 2: block size rule says high for a ⚠ or wide cold block, but both gallery blocks and the test are medium; "New to you:" is stored and goes stale on every re-show; minors: card 87 restates What, ruling omits two build designs, sentence counter misses lowercase starts; info: librarian reads cue-only context lines as block facts (decision 160 open) — added to 25da)
decided: 2026-10-12T23:05Z design — finding 1 option A: a chat block's Context is the page's medium size; high stays a page-only level
dispatch: implementer opus medium — fix round 1 (resume af0c58c783a457a0b)
