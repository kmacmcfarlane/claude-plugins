---
id: implement-step-6-lows-no-question-gate-e-e08c
title: "implement: Step 6 lows (no-question gate, evidence with each question) + size"
type: chore
status: done
priority: 4
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

From the 0cc6 review (lows): Step 6 'Ask the decision-class questions first… End the turn there' — add 'if there are any; otherwise go straight to the plan'; each question carries the evidence and recommendation it rests on. implement/SKILL.md is ~4.3k words; trim if near guidance.

## Handoff
- doing: implementer dispatched (sonnet, agent aeefd96d31c19c993)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer sonnet — one skill doc, no judgement signal
- 2026-09-21 done: c2a19ab

## Implementer result
- round 1 DONE_WITH_CONCERNS 61d3b14 (sonnet): Step 6 asks only when questions exist, each with evidence + recommendation; 4338 words. Trim not done: the file is ~6.6k tokens (proxy) vs the 5000-token guidance before this change — a structural cut, filed separately.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 61d3b14
- low not taken: 'If there are none' sits after the defer paragraphs (wording).
- landed c2a19ab
