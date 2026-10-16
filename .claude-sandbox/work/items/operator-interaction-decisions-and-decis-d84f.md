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
verdict: NEEDS_CHANGES plan round 2 (17a withdrawn; mediums: A4a breaks the Context one-line pin; per-item impact lines favour the fix; oneway refusal blanks old ⚠ pages; knock-on blocks between OQs; B2b-e need artifact-design; lows: group heading form, personal data from any source)
dispatch: planner opus high — resume, plan fix round 2
agent: planner a1271b5db6f7609f1 round 3
return: planner DONE (02_review-round-2.md; all 7 applied; B0 renderer; B3 on B2a+A7; knock-on blocks listed)
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer aacef19ee251480a0 plan round 3
verdict: NEEDS_CHANGES plan round 3 (1 medium exact: B0 depends cell; lows: name the lint key oneway:, name B2b's field, OQ4 note on chat bullets vs the mirrored shape)
decided: finish round of the four leftovers (each concrete) — authority answer 145; then review: self
dispatch: planner opus high — resume, finish round
agent: planner a1271b5db6f7609f1 finish round
review: self — finish round 03: exactly the four changes (B0 depends cell; oneway: lint key with test_digest; subject field {name, where, effect}; OQ4 note); supersedes named
verdict: CLEAR plan (round 3 + finish)
note: attachments proposal for the operator at .claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/01_review-round-1.md § The attachments proposal, revised
decision 259: d84f OQ1 — Impact describes what the work builds; process effects only in Wait — options: (a) yes [recommended] | (b) keep today's wording | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: no reversal
  blocks: A1a
  rec: (a)
decision 260: d84f OQ2 — undo shown only on one-way or costly options — options: (a) yes: '⚠ undo:' on that option only (never makes the decision ⚠); the page's 'oneway' row flag refuses a flagged row with no undo [recommended] | (b) yes, with a bold 'undo:' marker instead of ⚠ | (c) keep undo on every option | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: reverses Impact in every view (2026-10-06) and answer 206 (2026-10-14)
  blocks: A2, B1, C1
  rec: (a)
decision 261: d84f OQ3 — why now and why ask as one line above the Rec line in chat — options: (a) one 'Why you, why now:' line, ~25 words; the page keeps its fold; the store keeps two lines [recommended] | (b) keep two lines | (c) drop them | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (c) would reverse Every ask justifies itself (2026-09-30)
  blocks: A3
  rec: (a)
decision 262: d84f OQ4 — the subject: the concrete items a decision acts on — options: (a) named in Context (bullets in chat), one line per item under Impact giving its outcome under each option; a page 'subject' field [recommended] | (b) its own Subject part under What | (c) its own part on the page under the TLDR | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (a) departs in chat from the page's summary shape (your 2026-10-09 direction); (b)/(c) reorder the 2026-10-12 chat order and 2026-10-09 TLDR-first
  blocks: A4a, B2b, C2a
  rec: (a)
decision 263: d84f OQ5 — a bundle needing a pick per item — options: (a) a group of whole item cards under one group heading; one card when one answer fits every item [recommended] | (b) one card with a pick per item | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (b) would reverse A recommendation on every decision (2026-09-29) and Plain integers (2026-10-08)
  blocks: A4b
  rec: (a)
decision 264: d84f OQ6 — the attachments proposal — options: (a) all three kinds now (excerpt, summary with pointer, link) | (b) excerpts first (findings and code), the others when a case asks [recommended] | (c) not now | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: no reversal; settles what a private page may carry, chat inline vs on request, size limits
  blocks: A5b, B2f, C2c (and B0 unless 265 is answered first)
  rec: (b)
decision 265: d84f OQ7 — finding first, then the card — options: (a) in chat and on the page: a findings-style card opens on its finding (what, where, code or example) [recommended] | (b) chat first; on the page under the TLDR | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (a) reverses TLDR first on an answer page (2026-10-09), findings-style cards on the page only
  blocks: A5, B2a, C2b, B3 (and B0 unless 264 is answered first)
  rec: (a)
decision 266: d84f OQ8 — a scope line against the requirements — options: (a) on the title line (a pill on the page): required / shapes the work / outside the criteria; the criterion in Context [recommended] | (b) its own Scope part under What | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (b) reorders the 2026-10-12 and 2026-10-09 orders
  blocks: A6a, B2c, C2d
  rec: (a)
decision 267: d84f OQ9 — likelihood and best response on a risk decision — options: (a) 'Likelihood:' an observed count with its window and source, or 'no data'; 'Best response?:' whether acting is the most important response [recommended] | (b) likelihood only | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: no reversal; changes a design sentence in evidence-basis.md
  blocks: A6b, B2d, C2e
  rec: (a)
decision 268: d84f OQ10 — explain the mechanism everywhere — options: (a) every effect, finding and risk says how it happens, who meets it, and the before and after of the fix [recommended] | (b) only on findings | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: no reversal
  blocks: A1b
  rec: (a)
decision 269: d84f OQ11 — the source's label first in the title, replies by label — options: (a) in chat and on the page ('41 — F7 · …'); a reply by label is read as that decision [recommended] | (b) in chat only; the page keeps no ids | (c) number decisions by the label itself | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: (a) narrows No ids on an answer page (2026-10-09); (b) keeps it whole; (c) reverses Plain integers (2026-10-08)
  blocks: A4c, B2e, C3
  rec: (a)
decision 270: d84f OQ12 — chat by default for findings-style sets — options: (a) chat, finding first, until the page shows the finding; then the page is offered again [recommended] | (b) keep offering the page | (z) decide later
  raised: 2026-10-16T21:01Z
  why ask: a rule of the operator's own skills; relayed feedback binds nothing until confirmed here
  context: the operator's code-review feedback (relayed 2026-10-16); plan CLEAR (.claude-sandbox/investigations/operator-interaction-decisions-and-decis-d84f/) — then: none
  rulings: no reversal
  blocks: A7, B3
  rec: (a)
