---
id: decision-handling-the-pyramid-shaped-dec-69ee
title: "decision handling: the pyramid-shaped decision turn on the decisions skill and its future"
short_display_name: decision-handling pyramid
type: chore
status: doing
priority: 1
deps:
  - present-tonight-s-research-to-the-operat-2081
  - librarian-where-the-line-sits-between-ju-8dee
  - research-light-which-signals-show-how-fr-a99c
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T18:48Z
created: 2026-09-29
updated: 2026-09-30
refs:
  - operator 2026-09-29
---

Operator 2026-09-29 (.claude-sandbox/investigations/5140-decision-lifecycle/evidence/operator-notes-2026-09-29-stream.md): 'based on these notes, let's continue before making final decisions. When you are ready to present the decisions about the decisions skill and future of decision handling, then build me a pyramid-shaped decision turn I can work through with these thoughts in mind.' Acceptance: one turn, apex first (the direction for decision handling: short term in operator-interaction, long term an attention scheduler in operator-attention and the agents work system), then the layers it decides (what reaches the operator: 8dee; durability and the decision ledger: 98, 99; answerability and freshness: S2; batched replies: 100), each lower decision marked by which apex answer it depends on; sourced from 5140, 6d2c, d618, 8dee, S1, S2.

## Handoff
- doing: —
- next: answers 113 (re-asked) and 130 (124 vs 125); then F9 if 113 is (b)/(c), F2b's estate-wide stage per 130; close when both are answered and 0c4d's delta-01 is sent
- blocked: —
- learned: —
agents replied: decision ledger and attention scheduler filed on their 76bc (scheduler as a component for control-plane contract 0a7c); wants pointers to 263c and a99c with the others
operator-attention replied: filed r48-decision-scheduling-decisions-as-a-s-0495 (spec R48, their commit 9ef1ab1; their series decision-collector/06_decision-scheduling.md); adds two requirements: group by what a decision turns on (same fact) across sessions, and arrival-vs-clearance throughput as the scheduler metric; wants pointers to a99c and 263c; flags one decision ledger (in the unified work system) with their collector as a reader, relayed to agents
agents replied: ledger design recorded on 76bc, to be settled with 0a7c (waits on agents decision 10); asked operator-attention (relayed) not to build a private ledger store meanwhile — a request, not a ruling
operator-attention (c4443d7, their 07_ledger-split.md): accepts one ledger, drops private decisions.jsonl; proposes a timestamps-only observation log (shown|answered|deferred|swept) because no store records "shown"; moot if 76bc takes a shown field; will not build until agents or the operator answers — relayed to agents with our 5140 finding (no shown-at time in the store)
agents position (76bc): ledger records timestamped lifecycle events (raised, shown, answered, deferred with wake, swept/dropped); no objection to operator-attention interim ids-and-timestamps log (their call); claude-plugins shown-at item filed as 0999, both peers told
operator-attention: not building the interim log (591a428); 0999 shape requirements recorded on 0999
order: the research briefing (2081) goes first, so the operator is warm when the pyramid decisions arrive
pyramid note (b3c5 review r1): 6421 Q2 (z) impact must read "keeps its trigger but runs at fable high, down from the xhigh it inherits today"
pyramid built 2026-09-29T18:42Z: 24 decisions in the Claude Doc "Decision Handling Pyramid" (link on the next line once created); apex 110-111; the line 112-117; the record 98-99; answerable when shown 118-121; replies 100, 122; routing branch 123-128; research security 101, 108. Every card has a rec; none is one-way. Sources: 8dee 01-03 + r4 lows (apex (c) names what L1a (c) still raises; L4 tier 3 covers P3-P4; a wake re-shows a row and age counts from that Report), a99c 01-03 + r4 (D3 asks 78 (a) and offers the no-number variant, per answer 106), 5140 02-03, 6d2c 03, 6421 03 + r4 lows (Q1 cost at one planner round; Q2 base is one data point; Q2 (z) at fable high), a88a 03.
decision 110: Where is decision handling built: here now and handed to the scheduler later, or wait for it? — options: (a) build here now (operator-interaction + librarian-mode), the store's decision lines are the record until agents 76bc's ledger lands, then this repo writes to it and operator-attention (R48) reads it [recommended] | (b) answer the layers now, build nothing here until 76bc/R48 are specified | (c) build an attention scheduler here in operator-interaction now | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide (where two peers build; what is transitional here)
  why now: the operator's 09-29 notes proposed it ("operator-interaction [short term] and operator-attention [long term]"); agents 76bc and operator-attention 0495 have filed it; every build below follows it
  rec: (a) · basis partial — both peers agreed one ledger and filed their parts; 76bc waits on agents decision 10, date unknown
decision 111: What reaches the operator as a decision, and what the librarian decides alone and shows after (8dee apex)? — options: (a) events, as today | (b) by stakes, shown after: raised when one-way, trust, a real trade-off, a new or changed rule, an API name, wider scope, spend outside a grant, or a high left at a cap; the rest decided alone, recorded and shown [recommended] | (c) delegate by default: raise one-way and trust (L1a (c) still raises new rules, wider scope, relays and spend) | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide (every librarian session)
  why now: 97 asked for the line; 94 asks in 13 days, 55 born from a sub-agent's question; the review gate called "annoying"
  rec: (b) · basis partial — about 26 of 94 decided alone with a grant (15 without); the operator's answer differed on 4, all two-way
decision 112: Which classes are decided alone, and how are they shown (8dee L1a)? — options: (a) record and show only what is decided alone today | (b) 263c's class table: wording, minor design, narrowing to a linked follow-up, a new case of a ruled rule, a table-settled placement, a reply reading, forwarding decided alone; a decided: line and a done-alone group in the Report; every raise carries why ask: and its class [recommended] | (c) (b) plus trade-offs with a rec, API names and every placement | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide
  why now: 5140 OQ1/OQ2/OQ5 and b8d6 wait on it; the visibility surface must land before any class widens
  rec: (b) · basis partial — each class decided alone is one the operator delegated or always took the rec on
decision 113: What do "trivial documentation" and "a simple fix" mean here (8dee L1b)? — options: (a) prose-only, today's path (82 (e)); skill text is not trivial [recommended] | (b) plus skill wording that changes no rule, self-reviewed | (c) prose-only with less process: the librarian writes and lands it itself | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide (every librarian's docs review path)
  why now: the operator's 97 words ("trivial documentation … just do it"); in-scope work already runs unasked, so the question is process, not asks
  rec: (a) · basis partial — 82 (e) is the operator's own ruling on the docs path
decision 114: What does a review cap end in, and what may be spent unasked (8dee L2)? — options: (a) stop and carry at every cap | (b) plans raise only on a high left, else stop and carry; builds get at most one self-granted round inside a standing grant with headroom above the reserve, else ask [recommended] | (c) impact-gated on both, nothing spent unasked | (d) plans impact-gated, builds asked as today | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide; a spent round is bounded at one per item
  why now: the operator called the gate "annoying" and asked that it still stop research eating quota; 105-107 reached the operator
  rec: (b) · basis partial — matches all 5 choosing plan answers; builds ask as today when no grant is in force
decision 115: May "trivial documentation, just do it" reach another repo's files (8dee L3a)? — options: (a) this repo only; forward the rest [recommended] | (b) other repos' prose docs too, prepared on a branch and forwarded; the receiver's Intake step 2 changes | (c) (b) and merged into a down owner's main | (d) other repos' skill text too, prepared and forwarded for the owner's review; rule changes still raised by the owner | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, wide (every librarian as forwarder and receiver)
  why now: the reading has been open since 6d2c (row 16); 97's case was skill text in another repo
  rec: (a) · basis partial — forwarding fixes what the operator objected to; (d) changes only who drafts a content refresh
decision 116: How is work another repo owns forwarded (8dee L3b; the parked routing branch 3460)? — options: (a) the operator routes it; drop the branch | (b) forward with watched custody: accepted/declined replies after the Scope check, watched until it lands, lands back on the operator's next turn if silent; amend and land 3460 [recommended] | (c) (b) plus writing into a down owner's store | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible (four skill files), wide
  why now: 97 ("forwarding is the right move … can't get lost"); the branch is parked and conflicts with main; b514 open
  rec: (b) · basis partial — what the operator described; the branch carries most of it
decision 117: How do blockers reach the operator and escalate (8dee L4)? — options: (a) as today: every blocker is a numbered decision | (b) impact tiers: tier 1 for main/push, P0-P1, a hold's end or a deadline only; tier 2 for P2 or aged; tier 3 for P3-P4 or nothing; age lifts at most to tier 2, counted at Reports; a numbered decision only when there is a choice [recommended] | (c) (b) plus a Discord ping for tier 1 while away | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible; narrow in Reports, wider in the stores
  why now: A:7 asked for blockers that escalate by impact; a blocker with nothing to decide costs a card today
  rec: (b) · basis partial — built from parts that exist (priority, deps, Groom table); the tiers are untested
decision 118: While the operator is away, should each Report print the open decisions in full again (a99c D3)? — options: (a) keep re-printing | (b) away = a second message since the operator's last turn and more time than their upper-quartile turn gap (87 min this week, derived); while away a card already shown is a line; the turn back owes a card re-show [recommended] | (c) (b) with no time part (the no-number variant) | (d) hold every decision until the operator pulls | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow; changes the Seen ruling both ways
  why now: 19 blocks printed in one 6 h absence; 84-86 were counted seen by an unrelated turn and came back "need more detail"
  rec: (b) · basis partial — 8 of 9 lost-context answers carded (today 5); asks whether a derived number satisfies 78 (a); (c) if not
decision 119: What should a card shown to a cold reader re-supply (a99c D2)? — options: (a) context in blocks only | (b) a Context: resume cue stored when raised (where you left it · what you decide now) [recommended] | (c) every cold decision as a block | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: 84-86 were answered from three full blocks; cold cards carry nothing on where the operator left off
  rec: (b) · basis partial — cue studies (Trafton 2005, Mark 2005); untested here
decision 120: Should work in another session make the operator cold on a decision (a99c D1)? — options: (a) keep today's triggers; drop the event rule | (b) the event rule now, from other projects' transcripts | (z) decide later, wake when 0999 stores seen N: and 76bc or R48 publishes turn times [recommended]
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: 0999's shape is being set; with 118 (b) it cards no further lost-context answer
  rec: (z) · basis partial — D1 (b) adds nothing over D3 (b) on the corrected score
decision 121: Where should the operator's cross-session attention signals come from (a99c D4)? — options: (a) the decisions skill reads other projects' transcripts | (b) send 76bc and R48 the requirements with the pointers owed; read their record when present [recommended] | (c) a timestamp hook in this repo now | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: both homes are specifying now; pointers are owed to both
  rec: (b) · basis partial — both homes filed; when either lands is unknown
decision 122: Which actions may an uncertain reading of a reply not drive unconfirmed (8dee L5; only if 100 is (c) or (d))? — options: (a) no trigger | (b) keyed to the classes 112 raises [recommended] | (c) 6d2c's "relied on": pushes, merges, messages another session acts on | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: 100 (c) has no trigger until this is set
  rec: (b) · basis partial — one list decides both; 0 errors caught on the history either way
decision 123: When should the extra-deep opus tier (xhigh) run (6421 Q1)? — options: (a) plans start at opus high; a plan that turns hard in review 1-2 gets its next round at xhigh on half such plans, as a two-week trial; pins always get it [recommended] | (b) xhigh from the first planner dispatch on every plan with a depth signal | (c) only when the operator pins it | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow (spend)
  why now: the operator asked for an xhigh tier on 09-29; F2b of the routing work waits on it
  rec: (a) · basis partial — no evidence either way on xhigh planning; +$3-12 a week during the trial
decision 124: When should fable cross-check the work (6421 Q2)? — options: (a) only where fable has changed an outcome, at fable xhigh | (b) (a) plus the planning stage at fable high, kept only if it finds a missed high in 2 of its first 8 [recommended] | (c) (a) plus planning at fable xhigh from the start | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow (spend)
  why now: the operator asked for fable as a cross-check on foundational planning and research; F2b waits
  rec: (b) · basis thin — the base is one fable review after an opus pass; the keep rule protects either way
decision 125: Should the deepest fable tier run on estate-wide plans automatically (6421 Q3)? — options: (a) yes, once per series on the final plan [recommended] | (b) only when the operator names it | (c) never | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow (1-2 a month, about $2 each)
  why now: matches the operator's "enormous impact on the ecosystem"; F2b waits
  rec: (a) · basis partial — cost is small and the plans are the widest
decision 126: How hard should reviewers work by kind of change (6421 Q4)? — options: (a) opus high on every review | (b) opus medium only for fact and docs changes in the home-network and product-docs repos [recommended] | (c) (b) plus non-security claude-sandbox builds | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: F2b waits; adds reviewer-light if (b) or (c)
  rec: (b) · basis partial — those reviews found no high in 30 items
decision 127: What happens when quota runs low (6421 Q5)? — options: (a) below the reserve, xhigh steps down to high and fable cross-checks queue; pins still ask [recommended] | (b) deep-tier items wait for headroom | (c) no rule | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow
  why now: F2b waits; the week's grant stops at the 15% reserve
  rec: (a) · basis partial — deep items keep moving and the reserve holds
decision 128: When do the review-only agents get read-only tools (a88a Q1)? — options: (a) a later item once the agent files and routing have landed, judged on real dispatches [recommended] | (b) now, as its own change | (c) never; review-only stays a rule in the brief | (z) decide later
  raised: 2026-09-29T18:42Z
  stakes: reversible, narrow (reviewer, cross-checker, cross-checker-deep, scout)
  why now: the agent files landed without tool limits (900a); the operator asked what limits are for (reply 101)
  rec: (a) · basis partial — limits are for containment first; a reviewer needing Write for a scratch file would return BLOCKED
pyramid doc: https://claude.ai/code/artifact/73ea6f51-443e-45ae-8af0-61627e3f36af (Claude Docs project 73ea6f51-443e-45ae-8af0-61627e3f36af, prose root 011f43e0-dda4, rev 9; Answer column enum b2c061f0-12a1; one comment on 110 (a), thread 114480b2-fb9d, asking whether the build-here-now split is what the operator meant)
render notes: cards rendered by the librarian from the reviewed series, no fresh review of the render (quota hold until the dev-flow update); 98's (b)/(c) worded from the stored options (as today / per-series made visible); 128 (b) reworded "now, as its own change" since F1 (900a) landed; 123 (a) and (z) note the trial is what landed with b3c5

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
operator 2026-09-30 (doc controls): "The pyramid is cool, but it's not useful to select a/b/c/z in a dropdown next to a line that only shows the recommendation isn't very helpful ("Use Recommendation" and "Later" buttons would be more ergonomic with the short items at the top). The place for the drop-down would be on the cards below with two selectors (a/b/c...z and later/tell me/expand/dig into/you decide/drop w/ a free-form input beside it as a text area. That would work better. Can you update it?"
librarian: done in place (doc read at rev 9: no picks to carry). Map column becomes a two-choice picker (Use recommendation | Later): docs have no persistent buttons, and widget controls do not persist. Each card gains an answer row: Option picker (that card's letters), Reply picker (later, tell me, expand, dig into, you decide, drop), and a Your words cell to type in. Reading order when answers come: card row first, then the map's quick pick, words verbatim into answer N:. Candidate for the decisions skill later: a doc answer surface, noted for the post-pyramid follow-ups.
operator 2026-09-30T02:50Z (interrupting the edit above, before any doc change): "actually, instead of a selector for a/b/c/z, a button in each option to select with a radio for the later/tell me/expand/dig into/you decide/drop that has the text area beside would be best. Do you have a suggestion? We really just want a selection from the decision OR the other follow-up selections, but not both? How can we do that with form inputs? I'd like some options you think of here"
librarian: doc edit not made (doc still rev 9). Checked the artifact runtime: db is available to this user, so a real form page is possible; doc widgets keep no clicks or typed text across reload.
decision 129: How should the pyramid take answers? — options: (a) an answer page beside the doc: per card one radio group covering the option buttons and the follow-ups (exclusive by construction), a text area, map buttons Use recommendation / Later; saved to the page's shared database and read back by the librarian [recommended] | (b) in the doc: one picker per card holding the letters and the follow-ups, plus a Your words cell; map picker Use recommendation / Later | (c) in the doc: a tick box per option and per follow-up, plus a words line; exclusivity not enforced, conflicts asked back | (z) decide later
  raised: 2026-09-30T02:50Z
  stakes: reversible, narrow (how 24 answers are entered; answers stored verbatim either way)
  why now: the operator asked for options; the pyramid waits on its answer surface
  rec: (a) · basis partial — the only option with real radio buttons, either/or enforced and a text area; the runtime's db capability is available; untested here
answer 129: "129a, if I don't like that, then c is the most attractive. The "continuation options" (e.g. later/dit into/ etc) should have the meta placeholder hint in their dropdown label (e.g. `later [when]`) to preserve the hinting we have in the TUI." (read as: build the answer page; fallback (c) tick boxes in the doc if the page does not suit; follow-up labels carry the hint's placeholders: later [when], tell me [what], dig into [what])
answer page (129 a): https://claude.ai/artifact/PaNDz5iaFpRnqnWEdTJaWQ ("Pyramid Answer Sheet", capability db, private to the operator; source scratchpad pyramid-answers.html). Store: collection answers, one doc per decision number {n, choice, kind option|follow-up, words, rec, at}; read with ArtifactData list answers. Per card one radio group (option buttons + follow-ups later [when], tell me [what], expand, dig into [what], you decide, drop) so one choice only; Your words text area; map rows have Use recommendation / Later. Functional pass: probe doc written, listed, deleted (v1). No render preview available in this session.
doc rev 10: lead points at the answer page; the map's Answer column (enum b2c061f0-12a1, now unused) removed; the doc is the reading copy.
operator 2026-09-30T05:05Z (answer page feedback, verbatim): "First impressions, this is excellent. a major improvement in my usability of interacting with the decision list. / How long does it take you to generate a decision artifact like this? Because that could be a limiting factor. / Feedback looking at Decision 111: \"Your reply to 97 asked for the line\" it would be great if `97` were the short name for the decision (maybe that should have some brackets/bolding to indicate it's a decision slug, if the decision exists in the pyramid, then it should be interactable with a card popup on click/hover that displays the related decision without scrolling. This pyramid/tree paradigm of ready to expose information under a simple interface you can drill into is useful, because it allows the operator to get to the level of context they need without parsing extra information. My teeam also had good results at work with our tickt format by making the most important information flat and hidding the extra layers of detail in accordion panes (see the sussex marketplace kappa-dev:kappa-jira-ticket skill)."
librarian: timings from the transcript: answer page 4m46s from 129's answer to publish (about 4 of it typing the 24 cards into the page); doc 5m31s birth to last fill, after about 20 min reading the series. kappa-jira-ticket is not on this machine (sussex marketplace not installed); built from the operator's description. v2: page becomes a template + cards.json (data published beside it), decision references become slugs "N · short name" with a hover/click popup (pyramid decisions: compact card + open; answered ones: question and the operator's answer from the store), cards keep what/options/answer flat and move why now, stakes and evidence into accordion panes; each option's long body goes in its own pane.
answer page v2 published (version 1790744872-d72b, same URL): template index.html + cards.json (24 cards, 13 referenced answered decisions with short names, questions and answers); decision references render as slugs "[N · short name]" with a hover/click popup (pyramid: compact card with option heads, your answer, Open card, Use recommendation; answered: question and answer); cards flat: what, the question for you, option heads with impacts, follow-ups and words, recommendation; accordions: each option's "How it works", Why now, Stakes and what it depends on, Evidence and unknowns. Check: both files listed live; answers store intact (the operator's 110 (a), set 03:47Z on v1, survived). Durable copy: .claude-sandbox/investigations/69ee-pyramid-answer-page/ (index.html, cards.json, v1-index.html).
operator 2026-09-30T18:51Z (verbatim): "the skill is in git.sussexdirectories.com/sussex/claude/marketplace/plugins/kappa-dev/kappa-jira-ticket/, use that as the reference I mentioned. / Give me a summary of the changes that have landed and are ready to push"
librarian: read locally (clone at ~/work/src/git.sussexdirectories.com/..., skills/kappa-jira-ticket/references/ticket-formats.md § TBP, § Description, § The layout). Taken for v3: a TLDR of fragment bullets first; options as ≤6-word verb-first titles with one line each (because: on the rec, not recommended because: on the others, if left: on (z)); named folds one level deep, detail increasing downward (Background, Options in full, Stakes and dependencies, Evidence and unknowns); a visible budget near 150 words. Push summary: 31 merges since 09-28, all on origin; nothing waiting.
answer page v3 published (version 1790794337-b81b, same URL), after the kappa-jira-ticket layout: each card opens on a TLDR (3 fragment bullets), options as ≤6-word titles with one line each (because / not recommended because / if left), follow-ups and words, then four folds one level deep (Background, Options in full, Stakes and dependencies, Evidence and unknowns); only the recommended option bold; visible text 55-101 words a card. Card titles, TLDRs and option one-liners written by the librarian from the reviewed cards, not reviewed themselves; full text unchanged in Options in full. Answers store intact (110 a). Durable copy updated.
answer 110: a (answer page, 2026-09-30T03:47Z)
answer 111: b (answer page, 2026-09-30T18:54Z)
answer 112: b — "What would these classes look like?" (answer page, 2026-09-30T18:55Z; read as: (b), plus a question about the classes, answered in chat with examples from this session's work)
note: dev-flow installed at b27e7b72 (2026-09-30T05:33Z) carries the role agents; this session predates it, so dispatches still fall back until a restart. F1 (record and show) and F2 (the class table) are unblocked by 111 b and 112 b; filed with the rest after the pyramid, and dispatched after the restart.
reply 112 (2026-09-30T21:10Z, chat): "112 - I think we need to expand on the "real tradeoffs" part. There should be specific guidance about the types of impacts that would be considered a "real tradeoff" so it's clear. Also, those types should not be considered an exhaustive list" (read as: 112 (b) stands; its build adds specific guidance on the kinds of impact that make a trade-off real, written as examples and saying the list is not exhaustive; carried into F2's acceptance with a draft list given in chat)
answer 113: later — "after dependent answers above settle" (answer page, 2026-09-30T20:48Z; read as: decide later, wake when the answers it depends on (111, 112, 114, 115) settle)
wake 113: 111, 112, 114 and 115 answered by 2026-09-30T21:01Z — the wake fired; re-asked 2026-09-30T21:10Z with what changed ((a) stays the working reading meanwhile, per the card)
answer 114: b (answer page, 2026-09-30T20:49Z)
answer 115: a (answer page, 2026-09-30T20:49Z; F4b not built)
answer 116: b (answer page, 2026-09-30T20:50Z; F4 amends and lands the routing branch 3460, b514 folds in)
answer 117: b (answer page, 2026-09-30T20:51Z)
answer 118: b (answer page, 2026-09-30T20:53Z)
answer 119: b (answer page, 2026-09-30T20:54Z)
answer 120: z (answer page, 2026-09-30T20:54Z; the recommended later: wake when 0999 stores seen N: and agents 76bc or operator-attention R48 publishes turn times)
wake 120: when 0999 stores seen N: lines and agents 76bc or operator-attention R48 publishes operator turn times
answer 121: b (answer page, 2026-09-30T20:55Z; the requirements and owed pointers go to 76bc and R48 with the delta, F8)
answer 122: b (answer page, 2026-09-30T20:56Z; read as: recorded, but it applies only if 100 is (c) or (d); 100 is (b), so no confirm-first trigger is built (F6 not filed) unless the operator says they meant 100 (c))
answer 123: a (answer page, 2026-09-30T20:57Z)
answer 124: b — "Identify when a cross-check would be helpful and why. The operator needs to decide to add the fable cross-check explicitly, but you should offer it when appropriate." (answer page, 2026-09-30T20:59Z; read as: (b)'s stages stand as the places a fable cross-check is offered, never run unasked: the librarian names the stage and why it would help, and the operator adds it; (b)'s keep rule counts the ones the operator accepts. Conflicts with 125 (a), answered a minute earlier: asked back as 130)
answer 125: a (answer page, 2026-09-30T20:58Z; held against 124's words: decision 130)
answer 126: b (answer page, 2026-09-30T20:59Z)
answer 127: a (answer page, 2026-09-30T21:00Z; with 124's words, "fable cross-checks queue" reads as "fable offers wait")
answer 128: a (answer page, 2026-09-30T21:00Z)
decision 130: Your 124 words say every fable cross-check is offered and added by you; your 125 (a) says the deepest fable tier runs on estate-wide plans automatically. Which holds for estate-wide plans? — options: (a) offered like the rest: once per estate-wide series, on the final plan, the librarian offers fable xhigh with why; it runs only on your yes [recommended] | (b) 125 (a) stands as the one exception: estate-wide plans get fable xhigh without asking, once per series | (z) decide later
  raised: 2026-09-30T21:10Z
  what: whether the estate-wide fable xhigh check runs by itself or is offered
  why now: the effort-routing build (2eb7 F2b) writes the fable stages; it cannot write both
  (a): nothing fable runs unasked; you see 1-2 extra offers a month — undo: say "run them automatically" — who: you
  (b): 1-2 fable xhigh runs a month without an ask, about $2 more each than fable high — undo: reverse the answer — who: you (spend)
  (z): F2b builds everything else; estate-wide plans get the ordinary 124 offer (fable high) until you answer
  why ask: your own two answers conflict; not mine to pick
  rec: (a) · basis strong — both answers read from the answer page with timestamps; 124's words came last (20:59Z vs 125 at 20:58Z) and state a general rule
  unknown: whether you meant estate-wide plans as the exception
2026-09-30 builds filed from the answers: 8dee F1 decisions-record-and-show-what-is-decide-58f4, F2 librarian-mode-the-decided-alone-class-t-00ef (carries reply 112), F3 review-caps-and-spend-plans-raise-only-o-5579, F4 = 3460 (unparked), F7 = da89, F5 librarian-mode-blockers-reach-the-operat-d91e; F8 goes as a message with 0c4d delta-01; not filed: F4b (115 a), F6 (100 b), F9 (waits on 113). a99c: D2 decisions-store-a-context-resume-cue-wit-6e8e, D3 decisions-while-the-operator-is-away-sho-602b; D4 (121 b) with the delta; D1 (120 z) waits at its wake. 6421: 2eb7 F2b model-routing-f2b-the-xhigh-trial-fable-fa73; 128 a: dev-flow-read-only-tools-for-the-review-4766. 5140, 6d2c and caef builds listed on those items.
answer 112 (follow-on): "112: looks good" (2026-09-30T22:14Z, chat; read as: the draft real-trade-off guidance on F2 00ef is accepted as the starting text)
answer 130: a — "130a" (2026-09-30T22:14Z, chat; estate-wide plans get the fable xhigh offer like the rest; nothing fable runs unasked)
answer 113: b — "113b" (2026-09-30T22:14Z, chat; trivial docs = prose-only plus skill wording that changes no rule, self-reviewed; 8dee F9 filed)
