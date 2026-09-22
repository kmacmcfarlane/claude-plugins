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
