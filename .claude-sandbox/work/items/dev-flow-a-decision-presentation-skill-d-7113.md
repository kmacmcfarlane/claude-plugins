---
id: dev-flow-a-decision-presentation-skill-d-7113
title: "operator-interaction: a plugin for the agent-operator interface, starting with how decisions are raised and shown (research)"
type: spike
status: doing
priority: 1
parent: checkpoint-around-continuation-how-agent-d3ee
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-23T04:45Z
created: 2026-09-23
updated: 2026-09-23
refs:
  - "peer: marketplace - librarian (operator relay 2026-09-23)"
---

Ideas 3+4 of the parent: research how best to communicate decisions to an operator; levels (one line, options with description+impact, block per option) and the rule for picking one; re-presentation after rehydration at medium/high detail; near-term: the format agents use in conversation, Reports and summaries. Reconcile with the operator-attention session's decision-UI work and librarian-mode's numbered decision channel.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-23 agents - librarian proposes an ownership split, recorded on agents 374f (communication-standards-estate-wide-home-374f). agents would own the convention: detail levels and the rule for choosing one, the lettered+numbered labels, the two-line recap, and where it applies. claude-plugins would own the mechanics: ideas 1, 2, 4 and 5, plus the dev-flow skill that implements the format. This is a peer proposal: the operator settles it in the interactive session, and agents decision 2 (where estate-wide standards live) is still open. agents evidence for idea 5: they have four decisions open and nothing in flight, so compacting would only be "so the operator can answer", which none of the current modes names.

- 2026-09-23 operator-attention requirements gathering and research: the decision-UI work is theirs (operator, 2026-09-22). This item builds on it and does not restart it. Everything below is read-only, at /home/rt/work/src/github.com/kmacmcfarlane/operator-attention (commits 7c96b2c, e9d8ad0, 9bdc35e):
  - evidence base: research/findings/dc2-decision-brief-format.md (card fields, detail levels, ordering, batching)
  - prior art: research/findings/dc1-decision-inbox-landscape.md (agent-brief-me is the only close precedent)
  - research/findings/dc3-local-decision-sources.md: prose questions are rare next to structured ones
  - research/findings/dc-verification.md: apply its two citation corrections
  - plan: .claude-sandbox/investigations/decision-collector/00_initial.md (13 operator decisions, 4 of them blocking)
  - older inputs that still apply: pocs/CONVENTIONS.md (decision_brief schema v1), research/findings/{c2-theory-of-mind,e2-priority-model,e3-blocker-protocol}.md
  Their gist:
  - Three detail levels. A two-way door gets one line (recommendation, confidence, reversibility) and a single keypress. A one-way door, low confidence or unfamiliar ground gets the full block.
  - Add a reversibility field; it also gates whether an unanswered decision may fire its default.
  - Don't argue for batching from decision fatigue, which doesn't replicate. Argue from the cost of re-grounding on each switch, plus e2's queueing model.
  - Show the agent's confidence raw and calibrated side by side.
  - OD-6 (handed to us): optional indented detail lines under `decision N:` (impact, one-/two-way, confidence, default, expires, raising session) that today's wi ignores.
  - Keep the fast-pass grammar (`3: a`, `ok 1-4`).
  - R44 (notices outlive the session that raised them) is the same principle as idea 4.
  Proposed split: claude-plugins owns the format and the checkpoint/rehydration skills; operator-attention owns collection, ranking and routing answers back, and adopts our format (tell them if 7113 fixes the card schema).
- CONFLICT for the operator: agents - librarian (374f) proposes that agents owns the format's convention (levels, when-to-use rule, labels, recap), while operator-attention proposes that claude-plugins owns the format. Both agree on the checkpoint and rehydration mechanics, and on operator-attention keeping collection.

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

## Operator 2026-09-23 (in this session), reframing the item
- Reversibility is one factor, not the main driver of detail level. The operator's words: "If I don't have enough context in the place where you're showing me the decision to understand what decision I'm making and what the impact is, then I can't even figure out how to answer the question." High impact often comes from being hard to reverse, which argues for more detail. Find the other factors that affect impact, and the other reasons more or less detail helps in a given use case.
- Organize the use cases first (their examples: one line / options with impact / a block per option; at a checkpoint; after rehydration; in a Report), then fill in what should happen in each.
- Reversibility becomes a metadata field on a decision. Use web research to find the attributes and characteristics decisions have in general.
- It should probably be its own plugin, not part of dev-flow: "a pretty core primitive agent guidance component that has very high importance to the work we do together". A new plugin writes its README catalog row first (placement rule 5).
- RULING (operator): claude-plugins owns the rules and implements the decisions skill. The agents repo does NOT own them. It is the knowledge base, playground and planning area for the agentic-coding vertical, kept in the loop so it builds an understanding of LLM agents that becomes requirements for other repos. This supersedes the agents - librarian proposal above; the conflict is settled.
- Keep operator-attention and agents - librarian in the loop as the research lands. Review the key findings interactively with the operator, and let them drive planning and grooming of the checkpoint work (2b15).
- Research: dev-flow research, standard intensity, run under the series .claude-sandbox/investigations/7113-decisions/research/.

dispatch: research-lane sonnet ×6 — research run 2026-09-23-decision-attributes (standard; lanes w1-w5, l1); brief .claude-sandbox/investigations/7113-decisions/research/2026-09-23-decision-attributes/00-brief.md
agent: research-lane w1 af2676f324c760267, w2 afcc358d208451c60, w3 a2814d4cbc0f44413, w4 a1c7606f82052395c, w5 a84ee9f23cf7b043c, l1 a2ecacc4f1e75d1ec round 1
dispatch: research-lane sonnet — round 2 w6-primary-recovery (gap conditions 1 and 4)
agent: research-lane w6 acead026ed497554b round 2
dispatch: research-verifier haiku — verify run 2026-09-23-decision-attributes, sample 12
agent: research-verifier a462f7eb0fb761e8a
return: research run DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/7113-decisions/research/2026-09-23-decision-attributes/01-synthesis.md (7 lanes, 2 rounds, verifier 9/12 supported, gate PASS); review with the operator next

- 2026-09-23 agents - librarian: findings filed as agents knowledge-hold-the-decision-raising-find-2613, which is blocked on agents 39f1 (the operator's scope conversation). Their caution for the design: a raise-time check does not help if decisions are never read (they have four open decisions, nothing in flight, and the operator away). Make a decision's AGE and BLOCKING COST visible, not just its content. Carry this into the plan: age is a collector field, and blocking cost is the floor's "what it blocks" line.
- 2026-09-23 operator-attention (commit 38c50d4; their decision-collector/02_format-research-inputs.md; R46 carries the floor and the event-flag rule):
  - They will supply age, repo, session, the context-distance events and staleness.
  - They are adding a per-decision last-touched record now, since it cannot be backfilled.
  - Staleness stays "unknown" unless our format defines the condition as a checkable predicate, not prose.
  - Two conflicts for the operator review: (R6) defaults — their OD-13 never auto-applies, while our synthesis allows the fast tier (two-way and narrow); (R7) confidence — they keep calibrated confidence as an internal ranking input and never display a number. They ask whether our format forbids the number end to end.
  - Refinement: the fast pass selects, but the answer screen still shows the floor.

## Operator answers 2026-09-23 (review R1-R7 of the synthesis)
- answer R1: (a) the content floor is enforced when a decision is raised. The operator asks us to consider whether there are cases where the extra work isn't worth it, or other obvious exceptions from the research.
- answer R2: the operator likes the grid. "The recency of interaction is a key component here" (relayed to operator-attention). But they feel there must be more than two dimensions: "type is vague, that's a smell of hidden variables". Find out which dimensions are relevant.
- answer R3: (a) decisions that are hard or impossible to reverse and have high impact get more context when shown, and are answered one at a time (never inside a batch like `ok 1-4`).
- answer R4: consider reporting the evidence basis instead of a confidence number: complete / incomplete / none; direct / indirect evidence; inference; "memory"/"vibes". The quality and source of the evidence are factors too. How do we project all that down into a simpler indicator for operators? "Agents can juggle all the dimensions easily, but humans need to interact using their attention."
- answer R5:
  - "Decide later" must always be one of the options presented. It is not the same as "do nothing".
  - The question is also about scope: directories and names create scope boundaries.
  - The plugin is **operator-interaction**, "a plugin that enhances the interface and flow between agent and human operator". It overlaps with operator-attention.
  - Side request, filed separately: a dev-conventions skill.
- answer R6: REJECTED AS POSED: "You have given me a decision without explaining the impact of it … The goal isn't to get the decision, the goal is for the operator to understand the decision (including its context and impact)." The operator asks for:
  - reasonable scenarios where it is a good idea not to get a decision, purely because time has passed;
  - a way to facilitate the common response that isn't a decision: a request for more context or an impact analysis.
- answer R7: REJECTED AS POSED: what is the impact, based on the research? The operator questions how valuable an internal confidence number could be, and whether it would do more harm than good. Research more if needed. Impacts often need analysis and research, so some decisions should offer an option to pull known threads or gather background when the impact isn't fully understood.
- Operator feedback: the restated card-form questions were "a better experience than your first try".

dispatch: research-lane sonnet ×5 — refine run 2026-09-23-decision-attributes-r2 (extend; lanes w7-w11) from the operator review R1-R7
agent: research-lane w7 ad9380480045bac87, w8 a97b7ee4c7fdaff97, w9 afe3daea085397cb2, w10 a165cba7bdc2b0cc7, w11 ab6eeeb8aeb9a0404 (r2 round 1)
- 2026-09-23 operator-attention (commit 2f7cc3b; their decision-collector/03_operator-review-rulings.md):
  - Recency is now their spec R47.
  - They stamp last-touched-by-operator from each record's first version.
  - The evidence basis replaces the confidence number; they rank on it ordinally.
  - "Decide later" is a third disposition, and a deferral counts as an interaction.
  - Their fast pass will refuse to batch Type 1 decisions, which matches the operator's "addressed individually".
  - A floor-conforming card is assumed; a malformed card is reported back to the raising agent.
  - Asks: (1) define what wakes a deferred decision — they suggest an event, not a clock; w9 researches time vs event; (2) their dc3 kinds (decision line, grooming, blocked naming the operator, registry waiting, parked AskUserQuestion or plan approval) are available as a second corpus for decomposing "kind"; use them in the r2 synthesis.
- 2026-09-23 operator-attention counts, both estates, measured 2026-09-23. Aggregates only. For the r2 synthesis.
  - Pending decisions by channel, counting open items only:
    - unanswered decision lines: personal 18 across 8 items, sussex 11 across 8 items (29 in all);
    - blocked items: 8 personal, 2 sussex;
    - sessions the registry marks waiting: 2 of 62;
    - parked AskUserQuestion: 0 (last measured by dc3).
  - Open items: 231 personal, 25 sussex.
  - Cautions:
    - Without the open-item filter, the unanswered count is 60, not 29. Closed items carry historical decision lines in an old answer format, so a count that skips the filter overstates the backlog about twofold.
    - Sussex holds a third of the backlog from an eighth of the open items.
  - The channel predicts volume and possibly urgency; the kind must come from the card, stated by the raising agent.
  - They withdrew their push for event-only wake. If time-based wake is supported, it should still record the events since the deferral, so the re-ask can say what changed.
dispatch: research-verifier haiku — verify r2, sample 12
agent: research-verifier a3447e88ef8532253 (r2)
return: refine r2 DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/7113-decisions/research/2026-09-23-decision-attributes-r2/01-synthesis.md (5 lanes, verifier gate CONCERNS: grounding/S2 at 1 from PDF tooling); present cards to the operator next
- 2026-09-23 operator-attention on r2 (commit bf40411; their decision-collector/04_dimension-groups.md):
  - Adopted as proposals: group A (depth) is theirs, group D feeds ranking, and their R7 now carries the three clocks and the no-confidence-scalar rule.
  - Offered proxies for interruption TIMING (not cost): operator availability (their R8, recommended), registry busy/idle (4 of 62 busy), and the statusline-hub sensor.
  - Flag 1: "you" is ambiguous. They build it as "hand back to the raising agent". Assigning to a named person would need an assignee field and a second path back.
  - Flag 2: standing approvals change the scheduler and the risk posture, not the presentation. They touch the sandbox permission model (their R37: nothing runs unsandboxed silently), and a wrong call there cannot be recovered by answering more slowly. Not in their v0; it needs its own requirement.
  - They adopted status-quo defaults as distinct from action defaults, and both wake kinds for deferral, with the re-ask carrying a diff.

## Operator answers 2026-09-23 (r2 cards)
- answer R2: (a) the five-group model. The operator named this card as the exemplar: "This is a good example of the kind of information I need to make a decision in your presentation here. The amount of information matches the importance of the decision well, and I feel like I have an organized understanding of the context, options (with inline, separate colored impact statements), and I'm liking that you called out the strength of the evidence and what's unknown."
- NEW ACCEPTANCE (operator): "We'll need to do a round of test output for me to evaluate for different scenarios to exercise the skill as a sort of verification that the formatting is working as intended." That is, a gallery of rendered decisions across scenarios, for the operator to evaluate before or at landing.
- R9 not yet answered. The operator likes the palette of reply types, but is concerned about how someone learns the special words, and about the space they take if offered as choices: "It's kind of opinionated to create a semantic decision dialect. How can we communicate this in line or is that just not possible or feasible? Give me some alternative strategies to compare this against with pros and cons to each approach."
- Timing (operator): "it's late, I want to use the skill tomorrow while I work". After it lands, a follow-up fable review (filed separately).
- answer R9: (b). The skill carries clear guidance for parsing natural-language responses, and the agent echoes how it read each one. Add a hint that encourages an unambiguous dialect, "to control the decision behavior contract we are implementing". The hint is a subtle, colored text pattern that includes the meta placeholders (e.g. `later [when]`): "It doesn't make the hint much bigger, but it should help with adoption."
- answer R11: (a) build tonight, BUT first show the operator example decision lists at each detail level, for quick prototype feedback before implementing. R1, R4, R6, R7, R8 and R10 remain unanswered; they ship as the librarian's recommendations, marked provisional.
- Prototype feedback (operator, 2026-09-23):
  1. Bold the decision's title in list lines; the information on the line is good.
  2. Italic hint variant (A).
  3. "the higher the stakes, the more info and the slower the decision should be made".
  4. The ⚠ marker was confusing.
  Asked: whether `more` raises the detail level, and alternative words for it; the recommended order of decisions (a field sort vs the agent's judgment); and research guidance on "decision fatigue" and tackling urgent and important decisions first.
- Hint line (operator, verbatim): `Reply with a letter (72: a) or in your own words · later [when] · more [what] · dig into [what] · you decide · drop`. Reconciled with answer R12: `more [what]` becomes `tell me [what]`, and `expand` is added. The plan asks the operator to confirm.
- answer R12: `tell me [what]` adds context or a specific fact to the decision (the semantic the operator liked for `more`). Add a separate `expand` response that raises that decision's detail level in the next round. The plan must give a strategy for showing decisions at different levels together.
- answer R13: keep the ⚠ symbol, with a space after it; the label is "⚠ one-way". The operator found "one-way: answer alone" confusing compared with plain "one-way".
- answer R14: (c) stakes first. "The human will give better decisions for grouped related items and it reduces context-switching in their mind" (so also group related items).
- Operator: "Make the plan for me to review".
dispatch: planner opus — plan mode (spike 7113); a fork of the librarian, because it must carry ~30 operator rulings from this conversation; writes 00_plan in the 7113-decisions series
