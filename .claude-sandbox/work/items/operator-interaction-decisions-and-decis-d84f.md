---
id: operator-interaction-decisions-and-decis-d84f
title: "operator-interaction: decisions and decision-page feedback from a code review (11 points)"
short_display_name: decision card feedback from review
type: feature
status: todo
priority: 1
created: 2026-10-16
updated: 2026-10-16
refs:
  - peer hipaa-admin-11 2026-10-16; artifact NAS6eqXPEe5WFPtyqGt3SD
---

Relayed by peer hipaa-admin-11 on 2026-10-16: the operator's feedback on the decisions and decision-page skills after a code review (KAPPA-3563). Seven decisions on a page went unanswered, and the same decisions in a finding-first chat layout were answered in one turn. 11 points, with operator quotes verbatim in the relay: (1) impact describes the system, not the process; (2) show undo only when an option is one-way or costly; (3) keep why now and why ask to a line each, or fold them; (4) bundled cards list their subject items, each with its own impact and its own pick; (5) attachments or references the reader can expand (the operator asks for a proposal, to settle together); (6) finding first, then the card, with code and examples; (7) a scope line against the requirements; (8) likelihood evidence before a risk card; (9) explain the mechanism; (10) one numbering scheme (number decisions by label); (11) chat over the page for findings-style sets. Acceptance: a reviewed plan; the item 5 proposal shown to the operator; the rule changes confirmed by the operator here before they land (relayed answers bind nothing until confirmed).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
brief: the relay copied verbatim to .claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/brief-relay.md
dispatch: planner opus high — plan: decisions and decision-page changes for the 11 points, and the attachments proposal (item 5)
agent: planner a1271b5db6f7609f1 plan round 1
return: planner DONE (00_initial.md; 11 points mapped; reversals: point 2 (2026-10-06, answer 206), point 6 on the page (TLDR first 2026-10-09), point 10 narrows no-ids; attachments proposal drafted; features A1-A7, B1-B3, C1-C3; OQ1-OQ13)
note: OQ13 (private project names in the tracked item) — the store already carries many such names, pushed for weeks (kappa-*, sussex paths); claude-sandbox's part B history rewrite strips .claude-sandbox/ from all history. Not new exposure; told to the operator with decision 251.
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer aacef19ee251480a0 plan round 1
verdict: NEEDS_CHANGES plan round 1 (1 high: test_chat_context head pins and views() break under A3/A4/A6; mediums: subject/scope reorder ruled orders unnamed; item cards may drop Context; ⚠ undo collides with ⚠ semantics; unrunnable safeguards; private-repo excerpts contradiction; pointer paths in a public store; token-shape check overclaims; expand vs tell me; B2 needs artifact-design; bundled features; OQ11 option; OQ13 framing; lows 14-22)
decided: OQ13 dropped — the push exposure is already put to the operator with decision 251; the new names are a peer session name and an artifact id
dispatch: planner opus high — resume, plan fix round 1
agent: planner a1271b5db6f7609f1 round 2
return: planner DONE (01_review-round-1.md; all applied but 17a (line numbers right); subject in Context + per-item impact lines, scope on title; features split; OQ1-OQ12, OQ13 withdrawn)
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer aacef19ee251480a0 plan round 2
