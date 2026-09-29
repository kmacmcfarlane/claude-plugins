---
id: operator-interaction-refer-to-work-items-0b2d
title: "operator-interaction: refer to work items by a plain-language name in operator-facing text, not a bare hash"
type: spike
status: doing
priority: 1
parent: checkpoint-around-continuation-how-agent-d3ee
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T21:55Z
created: 2026-09-24
updated: 2026-09-29
refs:
  - operator 2026-09-24
---

Operator 2026-09-24: 'using hashes in messaging like this about work items is really opaque to me. Make a work item to figure out a better way for me to know what work item you are talking about than bf41. That's great for agent use, but not helpful for making a decision.' Example they pasted: an agents-librarian echo of their answers ('bf41 stays parked until then'). They add: 'It's just the echo of the decisions, so I don't need the reference to be very detailed, but a hash is a black-box to me … I'm cool with [it having value to you] and generally gloss over this part.' Scope: every operator-facing surface — decision echoes, Reports (changed: lines), team summaries, relays, peer messages the operator reads. Question: what handle does the operator get (a short plain name, e.g. 'the local-GPU routing research'; the item title; a name with the id as a trailing tag)? Where does the rule live (the decisions skill's floor already says to gloss ids; extend it to echoes and to every operator-facing mention; librarian-mode's Report)? Acceptance: a recommendation raised as a decision card, then a change to the operator-interaction skill (and librarian-mode's Report wording if needed).

## Handoff
- doing: —
- next: planner serial 03 folds answers 90-95 (93b: optional short_display_name field in wi; 94 relayed to agents); plan review; then build F1 plain-names skill, F2 template wording, and the wi field
- blocked: —
- learned: —

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — spike, plan mode (Step 1)
agent: planner acf7dd0ddde558b47 round 1
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/0b2d-plain-item-names/
baseline: 827ec9b97bc2637789deb64e0c35f18e8336df206b5ab97553136b7cf4d84e2d  .claude-sandbox/investigations/0b2d-plain-item-names/00_initial.md 
dispatch: reviewer opus — fresh, plan review (rule 4)
agent: reviewer ad7dd60fd821162c6 round 1
verdict: NEEDS_CHANGES round 1 at 00_initial.md 827ec9b9 (1 high, 5 medium, 3 low)
findings:
  [high] 00:171-176,529-534,412-413 — a 4-hex tag resolves silently to a different item when another id starts with it (7113, d44e, 2edb live); an exact-4-hex ref with both prefix and suffix match must raise AmbiguousId; test bar-7113 beside 7113-foo-dc6f; restate D5
  [medium] D2/F1.5/F1.6 — aim, catalog-row and plugin.json wording not given; "and" = second aim (principle 1); give concrete sentences framed as the agent-operator interface (README:190), justify under principle 6
  [medium] D2(a) promises a load step no feature builds — add librarian Rehydrate step 2, dev-cycle ~:354, work-review ~:113 load edits with fallbacks
  [medium] surface survey misses librarian Intake expected output (:159), "tell the requester" (:153), idle-turn hold: line leading <hold-id> (:48), held (<hold-id>) (:85,:158), table example "after cd34" (:53)
  [medium] F1.6 targets README § Structure, which deliberately lists no skills — drop; CLAUDE.md layout only
  [medium] F3.2 (wi resolves 4-hex tags) is beyond acceptance — make it conditional on D5 with no default build, or a follow-up item; needs-input/estate titles stay
  [low] decision entries lack a "why now" line
  [low] F2.6 HOLD lines: HOLD_LINE_MAX 240 / HOLDS_BUDGET 800, and hold_end parses text after the last "until" — note both
  [low] store-chore commit subjects left alone — raise as a one-line question
dispatch: planner opus — resume, fix round 1 (serial 01)
agent: planner acf7dd0ddde558b47 round 2
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/0b2d-plain-item-names/ 01_review-fixes.md (all 9 fixed; concern: aim-wording finding meets answer 71, which kept the catalog line — plan keeps it, rewording offered as W2)
baseline: 827ec9b97bc2637789deb64e0c35f18e8336df206b5ab97553136b7cf4d84e2d  .claude-sandbox/investigations/0b2d-plain-item-names/00_initial.md 6b39adddc31f44930ffb8742e576de1f0c3ea04779b2d8b332372dd5cb7a0f16  .claude-sandbox/investigations/0b2d-plain-item-names/01_review-fixes.md 
dispatch: reviewer opus — resume, round 2
agent: reviewer ad7dd60fd821162c6 round 2
verdict: NEEDS_CHANGES round 2 at 01_review-fixes.md 6b39addd (1 medium, 2 low; all round-1 findings fixed; W1/W2 via answer 71 ruled valid)
findings:
  [medium] 01 § The aim wording (plugin.json row) and D2 W1 — under W1 the plan still rewords plugin.json's aim sentence to W2's "address you" and settles the conflict in prose; pass: W1 opens plugin.json with the ruled phrasing (README:573), "address you" for W2 only, or make it a D2 sub-choice
  [low] 01 § Confirmed Assumptions — collision-check command misses archive/*/ and uses ^<tag>- narrower than wi's startswith
  [low] 01 D2 card does not name principle 6; add one clause to W1
  note: D5 rec "(c) with (d)" should render as one option
dispatch: planner opus — resume, fix round 2 (serial 02)
agent: planner acf7dd0ddde558b47 round 3
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/0b2d-plain-item-names/ 02_aim-sentence-fix.md (all 3 fixed)
baseline: 827ec9b97bc2637789deb64e0c35f18e8336df206b5ab97553136b7cf4d84e2d  .claude-sandbox/investigations/0b2d-plain-item-names/00_initial.md 6b39adddc31f44930ffb8742e576de1f0c3ea04779b2d8b332372dd5cb7a0f16  .claude-sandbox/investigations/0b2d-plain-item-names/01_review-fixes.md 3336dbf9fcda4a04643d3965d91ee03f8d6b366725b4a925f277f5f09e8629d7  .claude-sandbox/investigations/0b2d-plain-item-names/02_aim-sentence-fix.md 
dispatch: reviewer opus — resume, round 3
agent: reviewer ad7dd60fd821162c6 round 3
verdict: CLEAR round 3 at 02_aim-sentence-fix.md 3336dbf9 (2 low: find stderr when no archive/, serial label — cosmetic, carried to the build brief)
- 2026-09-28 series CLEAR at round 3 (00+01+02); raising D2, D4 (blocking) and D1, D3, D5, D6 (not blocking) as decisions 90-95
decision 90: (series D2) where the plain-names rule lives — (a) new generic `plain-names` skill in operator-interaction, decisions/librarian-mode/dev-cycle/work-review point at it, aim line kept as ruled in 71 (W1) [recommended] | (b) extend decisions only | (c) work-items format.md | (d) both a and c | (a)+W2 reword the aim line (reverses 71) | (z) decide later
  raised: 2026-09-28 · blocks F1 · rec (a)+plain-names+W1 · basis partial — answer 71, README:190-191 · unknown: whether you count reports and relays as "what they need from you"
decision 91: (series D4) the Report's changed: line — (a) `changed: <plain name> (<tag>) — …` [recommended] | (b) keep the full id | (c) plain name plus full id | (z) decide later
  raised: 2026-09-28 · blocks F2's two Report lines · basis strong — no parser reads the line
decision 92: (series D1) the handle — (a) plain name then 4-hex tag [recommended] | (b) name only | (c) title verbatim + tag | (d) full slug | (z)
decision 93: (series D3) name source — (a) agent writes it from the title each time, no stored field [recommended] | (b) optional name: field in wi | (c) wi derives from title | (z)
decision 94: (series D5) wi resolving a 4-hex tag — (d) file the ambiguity-rule version as its own follow-up item; no wi change here [recommended] | (a) build it now | (c) never | (z)
decision 95: (series D6) store-chore commit subjects — (a) leave them terse [recommended] | (b) plain names there too | (z) · basis thin
answer 90: a (read as: new plain-names skill in operator-interaction, aim line kept as ruled in 71) — with skill feedback filed as dbfc (option order a-b-c, rec bolded)
answer 91: a (read as: changed: <plain name> (<tag>) — …)
answer 92: a (read as: plain name, then the 4-hex tag)
answer 93: b — "call it the idiomatically capitalized and separated version of 'short display name' which makes it clear to agents what the intention is for the field" (read as: an optional short_display_name: field in wi's item format, snake_case like the store's other multi-word keys; reverses the series' rec (a))
answer 94: "this seems really related to the stuff I'm working on with the agents agent to get a real work system in place" (read as: no wi change here and no follow-up item in this repo; relayed to the agents librarian as input to its work system)
answer 95: you decide — chose (a) leave store-commit subjects terse, because the operator says they are mostly for human debugging and not important, and a plain name lengthens every store commit
next: planner serial 03 folds answers 90-95 (93b adds a wi field) before the build
dispatch: planner opus — serial 03 folding answers 90-95
agent: a945c3247aaba07d8 (planner serial 03)
