---
id: readme-footer-every-readme-md-ends-with-c137
title: "README footer: every README.md ends with one line saying it is user-facing documentation, not agent instructions"
short_display_name: README user-facing footer
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-05T23:12Z
created: 2026-10-05
updated: 2026-10-05
refs:
  - peer marketplace 2026-10-05, relaying its operator
---

Peer marketplace 2026-10-05, relaying its operator: every README.md ends with one very short line marking it as user-facing documentation, not agent instructions; kappa-dev uses '*User-facing documentation, not agent instructions.*' and asks us to adopt the same wording or send ours. Scope here: the estate's conventions (kit-dev create-skill, dev-cycle review-checklist) and this repo's own READMEs (root, plugin READMEs). Relayed operator decision: confirm with the operator here (decision 157).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: confirmed by the operator here as answer 157 a (on skills-allow-a-readme-md-in-a-skill-fold-48a8); built together with skills-allow-a-readme-md-in-a-skill-fold-48a8 on one branch

## Notes
- 2026-10-05 claimed by Kyle-McFarlane@401123cbad11
decision 158: This repo's root README.md is the marketplace doctrine that agents are told to read; should it get the "not agent instructions" footer anyway? — options: (a) no footer on a README whose job is agent-read doctrine; the rule says "every README for humans" [recommended] | (b) add it to every README, this one included, and move the doctrine to a file agents read (e.g. DOCTRINE.md), keeping README.md for humans | (c) add the footer anyway | (z) decide later
  raised: 2026-10-05T23:12Z
  what: how your footer rule (answer 157 a) applies to this repo's root README.md, which CLAUDE.md names as the doctrine every agent reads before adding anything
  why now: the README build is running and leaves the root README without the footer until you answer; blocks: nothing
  why ask: your-call — the footer would say the doctrine is not agent instructions, which contradicts how this repo uses it
  context: you confirmed the footer on every README (157 a) · you decide whether a doctrine README is an exception, or the doctrine moves — then: none
  stakes: reversible, narrow — this repo's root README and where its doctrine lives
  (a) an exception for agent-read READMEs — the rule reads "every README written for humans"; the root README keeps doing both jobs — undo: an edit — who: this repo
  (b) move the doctrine out — README.md becomes human-facing with the footer; the doctrine moves to its own file, and every pointer to "README's doctrine" (CLAUDE.md, librarian-mode Rehydrate, review-checklist, create-skill) follows — a larger change, its own item
  (c) footer anyway — simplest; the footer is false on this file, and an agent obeying it could skip the doctrine
  (z) decide later — the root README stays without the footer
  rec: (a) · basis partial — the footer marks human docs; a doctrine file agents must read is the one README it would mislabel
  unknown: whether other repos' READMEs also serve as agent-read doctrine
