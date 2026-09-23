---
id: dev-flow-a-decision-presentation-skill-d-7113
title: "decisions: a standalone plugin for how agents present decisions - attributes, use cases, detail levels (research)"
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
