---
id: decision-handling-the-pyramid-shaped-dec-69ee
title: "decision handling: the pyramid-shaped decision turn on the decisions skill and its future"
short_display_name: decision-handling pyramid
type: chore
status: todo
priority: 1
deps:
  - present-tonight-s-research-to-the-operat-2081
  - librarian-where-the-line-sits-between-ju-8dee
  - research-light-which-signals-show-how-fr-a99c
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29 (.claude-sandbox/investigations/5140-decision-lifecycle/evidence/operator-notes-2026-09-29-stream.md): 'based on these notes, let's continue before making final decisions. When you are ready to present the decisions about the decisions skill and future of decision handling, then build me a pyramid-shaped decision turn I can work through with these thoughts in mind.' Acceptance: one turn, apex first (the direction for decision handling: short term in operator-interaction, long term an attention scheduler in operator-attention and the agents work system), then the layers it decides (what reaches the operator: 8dee; durability and the decision ledger: 98, 99; answerability and freshness: S2; batched replies: 100), each lower decision marked by which apex answer it depends on; sourced from 5140, 6d2c, d618, 8dee, S1, S2.

## Handoff
- doing: pyramid shown in the doc and chat (110-128 + 98-101, 108)
- next: read answers from chat or the doc's Answer column (read the doc from rev 9); store each answer verbatim; then file 8dee F1-F8 per the answers, 0999 per 98/99/118/120, F2b per 123-127, 128's item, delta to agents/operator-attention
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
