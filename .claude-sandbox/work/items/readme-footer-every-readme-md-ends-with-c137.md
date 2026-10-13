---
id: readme-footer-every-readme-md-ends-with-c137
title: "README footer: every README.md ends with one line saying it is user-facing documentation, not agent instructions"
short_display_name: README user-facing footer
type: chore
status: done
priority: 2
created: 2026-10-05
updated: 2026-10-06
closed: 2026-10-06
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
decision 158: READMEs that agents are told to read (this repo's root README, the doctrine; the work-item store's README that wi init seeds in every repo) — should they get the "not agent instructions" footer anyway? — options: (a) no footer on a README whose job is agent-read; the rule reads "every README written for humans" [recommended] | (b) add it to every README and move the agent-facing content out (the doctrine to e.g. DOCTRINE.md; the store's README to another name), keeping README.md for humans | (c) add the footer anyway | (z) decide later
  raised: 2026-10-05T23:12Z
  revised: 2026-10-05T23:14Z — the README build's review found a second agent-facing README: .claude-sandbox/work/README.md, seeded by wi init in every repo ("Start with wi prime…"); options and recommendation unchanged, scope widened
  what: how your footer rule (answer 157 a) applies to READMEs agents are told to read
  why now: the README build is ready apart from this wording, and waits on it to land; blocks: that landing
  why ask: your-call — the footer would call agent-read files "not agent instructions"
  context: you confirmed the footer on every README (157 a) · you decide whether agent-read READMEs are an exception, or their content moves — then: none
  stakes: reversible, narrow — this repo's root README, every repo's store README
  (a) an exception for agent-read READMEs — the rule reads "every README written for humans"; both files keep their job, no footer — undo: an edit — who: this repo and every work-item store
  (b) move the agent content out — README.md becomes human-only everywhere; the doctrine and the store guide move to other names, and every pointer follows (CLAUDE.md, librarian-mode, review-checklist, create-skill, wi init) — a larger change, its own items
  (c) footer anyway — simplest; the footer is false on both files, and an agent obeying it could skip the doctrine
  (z) decide later — the README build waits
  rec: (a) · basis partial — the footer marks human docs; agent-read READMEs are exactly the ones it would mislabel
  unknown: whether other repos keep agent-facing READMEs of their own
answer 158: "158 - I think the footer should only apply to README files in skill directories" (read as: narrows answer 157's second half — the footer applies only to README.md files inside skill folders; no footer on the root README, a work-item store's README, or any other README; c137's estate-wide practice shrinks to the skill-folder rule 48a8 already builds)
closed 158: acted skills-allow-a-readme-md-in-a-skill-fold-48a8
landed via 48a8 (12de6eb), narrowed by answer 158 to skill-folder READMEs only; nothing estate-wide remains
- 2026-10-06 done: covered by 48a8 (12de6eb); narrowed by answer 158
