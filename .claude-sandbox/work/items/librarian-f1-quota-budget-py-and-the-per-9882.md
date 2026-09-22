---
id: librarian-f1-quota-budget-py-and-the-per-9882
title: "librarian F1: quota_budget.py and the per-subscription librarian store"
type: feature
status: doing
priority: 1
parent: librarian-work-unblocked-items-and-pre-i-1222
owner: unknown@360f41058e92
claimed: 2026-09-22T08:20Z
created: 2026-09-22
updated: 2026-09-22
---

Reads the claude-analytics sink when installed, else samples the sensor record; velocity per resets_at window; allowed rate; prints mode/N/next_check; store under ${CLAUDE_CONFIG_DIR}/claude-kit/librarian/ (samples.jsonl, intent.json, claims/); references/budget.md codifies the location; tests. Opus (executable logic). Plan: .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md § F1.

## Handoff
- doing: implementer dispatched (opus, agent a363290b7595fc80f)
- next: review r1 (opus)
- blocked: —
- learned: —
- agents policy: claims move to claims/<repo>.json (not per session); samples/intent unchanged; away 5h reserve 10% (00 said 5 in F1).

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
- dispatch: implementer opus — executable logic (new script + store); weekly at 26% with 6.1 days left (~2x sustainable pace): single dispatch while decision 53 is open

impl r0 (opus, a363290): DONE_WITH_CONCERNS at 5233da5 — 5 files, 51 new tests; all six Checks green per agent.
librarian on OQs (2026-09-22): OQ1 add the new suite to CLAUDE.md `## Librarian` Checks in this feature (a Checks line for a suite this item creates is part of the item); OQ2 in scope — README dev-flow row/section must stop claiming "no state of its own", name claude-analytics as the soft quota sink (fallback self-sampling), widen the statusline-hub soft-dep wording, and mirror the words in dev-flow plugin.json + marketplace.json per plan § F1. OQ3/OQ4 stay as briefed (flat reserves, done-for-the-day 5h reserve 0) — agents policy OQ3/decaying reserve are F2 inputs. OQ5 → F2. OQ6 → claude-analytics / agents 8ad9, not this repo.
dispatch: implementer opus — scope addition before review r1 (resume a363290; doctrine/shape signal)
impl r0b (opus, a363290): DONE at a9e4edb — CLAUDE.md Checks line, README dev-flow row (claude-analytics soft, store named), plugin.json + marketplace.json mirrored. OQ: claude-analytics named before it exists (same as OQ6).
dispatch: reviewer opus — executable logic + marketplace shape (rule 4, implementer opus)
