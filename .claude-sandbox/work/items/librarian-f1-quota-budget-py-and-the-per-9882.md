---
id: librarian-f1-quota-budget-py-and-the-per-9882
title: "librarian F1: quota_budget.py and the per-subscription librarian store"
type: feature
status: done
priority: 1
parent: librarian-work-unblocked-items-and-pre-i-1222
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
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

review r1 (opus) on a9e4edb: NEEDS_CHANGES. Seven Checks OK; §1–§5 clean. Findings:
- R1 [high] quota_budget.py:520-594 — plan § F1 says prints mode/N/next_check (absent signal → normal, N=2); script prints neither.
- R2 [medium] :132, :261 — RecursionError from deeply nested JSON escapes readers → exit 1 every call; poisoned samples line persists through prune.
- R3 [medium] :539, :547 — future-stamped sink line keeps sink "live" and wins max(at).
- R4 [medium] :434-471 — claim create/refresh is read-then-replace; 12 concurrent sessions all got `created`; refresh can clobber a takeover.
- R5 [medium] tests — no tests for R2/R3/R4, usage-cache-*.jsonl ignored by the sink, epoch ms heuristic, worktree→main repo_name.
- R6–R13 [low] budget.md dir-mode wording; exit-code 1 on internal error undocumented; glob claude-analytics* → claude-analytics-*; README/plugin.json/marketplace.json name claude-analytics as shipping (suggest "external, planned"); README "without it … no signal" not quite true; refresh nulls stored identity fields; prune drops concurrent appends / no fsync; a9e4edb subject form.
- reviewer note: allowed rate unbounded just before a reset — F2 should cap/ignore a window about to reset.
decision (librarian, 2026-09-22) on R1: mode and N move to F2. F2 owns the mode table and the N formula (per-agent rates, active-librarian count), and the agents policy (c79e) changes that count to claims heartbeats via serial 01 before F2; computing N in F1 would bake in a formula about to change. F1 prints the numbers behind them + next_check; budget.md cites this decision. Not an operator decision reversed (plan text, not operator).
dispatch: fix round 1 implementer opus — resume a363290 (tier kept, rule 6)
fix r1 (opus, a363290): 12ac598 — R1 per decision (budget.md cites it); R2–R12 fixed (72 tests; race test fails 3/3 on a9e4edb); R13 declined (needs amend — accepted). New store file samples.lock (flock). OQs → F2 (c79e).
dispatch: reviewer opus — review r2 (resume r1 reviewer on 12ac598)

review r2 (opus) on 12ac598: CLEAR. R2–R12 fixed (16-way create race → 1 created/15 conflict ×3; 8×50 concurrent appends under prune → 400/400). Lows L1–L4 (replaced-unreadable too wide: oversized/mode-000 foreign claim replaced; samples.lock opened O_WRONLY without O_NOFOLLOW — read-only lock exits 1, planted symlink creates target outside store; read_jsonl `except Exception` hides parser bugs; budget.md:8 decision citation ungrammatical) — author's call; librarian filed them as a follow-up item rather than a third round (quota; none medium+).
Review result: 2 review rounds, 1 fix round (+ one pre-review scope addition); findings fixed R2–R12; declined R13 (needs amend); final verdict CLEAR; impl opus, review opus.
land checks (librarian, worktree 12ac598): all seven suites OK; diff read against doctrine — 9 files, all in item scope.
- 2026-09-22 done: 0f8d803
