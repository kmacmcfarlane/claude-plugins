---
id: foundation-is-filling-a-claim-interfaces-8ee2
title: "foundation: is filling a claim Interfaces entry at G2 a requirements reopen?"
short_display_name: claim interface terms at G2
type: spike
status: done
priority: 4
parent: foundation-follow-ups-build-time-reopens-f3d1
created: 2026-10-09
updated: 2026-10-12
closed: 2026-10-12
refs:
  - foundation-consult-claim-md-skill-in-pha-286d
---

From 286d review 1 finding 3, 2026-10-09: phase 1 names each contract in the claim's ## Interfaces; claim-md counts the terms of an interface as substance, so filling a contract's format or versioning at phase 2 routes to a requirements reopen on most full runs. Decide whether interface terms written at G2 are a reopen or an upkeep fill-in, and say it in gates.md and moves.md.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: a series of the spike's plan: whether filling a claim Interfaces entry's terms at G2 is a requirements reopen or an upkeep fill-in, with the options and a recommendation; nothing landed
dispatch: planner opus high — spike plan
agent: planner a0a736401a11c45be
return: planner — series at .claude-sandbox/investigations/foundation-is-filling-a-claim-interfaces-8ee2/ (00, INDEX); today both readings are flawed: a reopen on every publishing run, or a silent fill-in F0 writes unapproved (claim-md forbids); foundation's substance lists omit interface terms; four options; recommends D
decision 210: How should a contract's terms filled in at gate G2 (format, versioning, compatibility) be approved? — options: (a) requirements reopen: a reopen serial and one more decision per publishing run; claim-md unchanged | (b) upkeep fill-in, reported: no stop, but claim-md gains an upkeep kind and terms without an ADR reach CLAIM.md unseen | (c) the Interfaces entry points to the contract doc for its terms: needs an ownership-plugin ruling that applies to every repo's claim | (d) the terms are a phase-2 part of the claim, approved in G2's own decision [recommended] | (z) decide later
  why ask: your-call — it sets which of your approvals covers a published contract's terms, and option (c) changes a rule in the ownership plugin for every repo's claim
  context: phase 1 names each contract in the claim's Interfaces; claim-md counts an interface's terms as substance, so filling them at G2 is either a reopen on every publishing run or a fill-in nobody approved · you decide which approval covers those terms — then: foundation's own substance lists omit interface terms, so they have drifted from claim-md's rule; every option replaces them with a pointer to claim-md's; a run publishing no contract costs nothing under any option
  impact: (d) → the terms ride G2's decision, usually with the contract's one-way ADR; four foundation files change · wait: the build of this change only · reach: foundation runs that publish a contract · undo: a later ruling and a text change
- 2026-10-12 spike closed on its series; decision 210 raised; the build is filed when 210 is answered
- 2026-10-12 done
shown 210: 2026-10-12T22:54Z chat
