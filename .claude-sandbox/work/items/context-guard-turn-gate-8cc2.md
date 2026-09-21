---
id: context-guard-turn-gate-8cc2
title: "context-guard: turn gate, HARD advice, session-addressed manifest"
type: feature
status: doing
priority: 1
tags: [context-guard]
deps:
  - land-plugin-factoring-fbe8
owner: unknown@360f41058e92
claimed: 2026-09-21T18:18Z
created: 2026-09-04
updated: 2026-09-21
---

Mid-turn PostToolUse depth gate; HARD gate stops recommending an unaffordable checkpoint; rehydration manifest made session-addressed (claude-kit/handoff/<sid>.md) because several sandbox sessions share one work dir; legacy repo HANDOFF.md adopted-if-owned else ignored. Worktree .claude/worktrees/context-guard-turn-gate, branch worktree-context-guard-turn-gate (off plugin-factoring; rebase onto main after plugin-factoring lands).

## Handoff
- doing: port plan in fix round 1 (serial 01)
- next: plan CLEAR → file F2/F3a/F1 features; decision on manifest location
- blocked: land-plugin-factoring-fbe8
- learned: Round-2 nits: inode+mtime cache key, update_state() merge instead of load-modify-save

## Notes
- 2026-09-04 claimed by e163e159
- 2026-09-04 learned: Several sandbox sessions share one work dir: session state must be session-addressed. Claude Code 1M auto-compacts only at the limit; a blocked prompt at 1K left wedges the session.
- 2026-09-04 learned: Several sandbox sessions share one work dir: session state must be session-addressed. Claude Code 1M auto-compacts only at the limit. Per-tool-call hooks must merge state keys, not load-modify-save, or they race the status line.
- 2026-09-04 learned: Round-2 nits: inode+mtime cache key, update_state() merge instead of load-modify-save
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch 2026-09-21
- decision (librarian): the branch is 4 commits off plugin-factoring (merge-base d118f48b, early Sept), predating the context-guard move, the d63e window mirror and the statusline split; a rebase is effectively a rewrite of gate code. Run dev-cycle plan mode first: which of its four behaviours are still wanted and absent on main, and a port plan onto current main.
- dispatch: planner opus — gate code (fable signal; fable unavailable (unknown); fallback); plan mode, no worktree; series .claude-sandbox/investigations/8cc2-turn-gate-port/

## Plan result
- planner DONE_WITH_CONCERNS (opus): series .claude-sandbox/investigations/8cc2-turn-gate-port/00_initial.md. (1) mid-turn check and (2) affordable HARD advice still wanted, absent on main — rewrite on current measure(); (3) session-addressed manifest conflicts with main's repo HANDOFF.md, but the harm is live (rehydrate injects another session's manifest on compaction); /clear regenerates the session id (verified in the binary). Port: F2 advice, F1 turn_gate, F3a authorship check (safe now), F3b location (blocked). Review nits already covered on main.
- dispatch: plan reviewer opus — dev-cycle plan-review variant

## Plan review round 1 — NEEDS_CHANGES (opus)
- verdicts, manifest-injection claim and /clear sid claim all verified (binary 2.1.278); Open Question 4 answerable: skip on agent_id only.
- [high] F3a breaks the handoff/stage-boundary flow: a successor after /clear or a fresh session loses its inherited manifest (incl. CORRECTION/REFUSED) on compaction → adoption rule (clear predecessor via _proc record, a Read of the manifest, fork parent).
- [high] F1 can end an unattended turn on an inferred depth (DUE text + ported unattended section) — informational only off BLOCKING_SOURCES.
- mediums: F3a before F1; agent_type skip wrong; fork parent persisted; ending-the-session.md is a definite F1 file; F1 routing must argue the blocking-predicate refactor (or fable reviewer); B′ costs overstated.
- dispatch: planner opus — plan fix round 1 (resume); revision as serial 01 with Supersedes
- plan fix round 1: serial 01_review-round-1.md — F3a adoption rule (writer / descent via fork parent + /clear predecessor, chain ≤8 / whole-file Read), new hooks/lineage.py; F1 silent off blocking sources, distinct HARD mid-turn marker, agent_id skip; order F2 → F3a → F1 → F3b; OQ1 recommendation now C.
- dispatch: plan reviewer opus — round 2 (resume)

## Plan review round 2 — NEEDS_CHANGES (opus)
- all 11 round-1 findings resolved; F2 cleared to dispatch. New: [high] adoption keyed on author not version (a fork parent's later rewrite reaches the child); [medium] a bystander's Read adopts — the hook's own header invites it (adopt by Read only for mode: handoff); [medium] F1 test treats an unresolved auto-compact window as non-blocking — restate as "no HARD marker unless hard_applies(block_window, tok)"; lows: one-main-session-per-process assumption; unattended section defers to a custody skill's mode.
- features filed: context-guard-8cc2-f2-hard-advice-fits-t-1f9d (dispatched), context-guard-8cc2-f3a-re-inject-handoff-5126, context-guard-8cc2-f1-mid-turn-posttoolu-3adc, context-guard-8cc2-f3b-where-handoff-md-a49b (blocked on decision 47).
- dispatch: planner opus — plan fix round 2 (serial 02)
decision 47: where HANDOFF.md lives — (a) C: each session keeps its own manifest (config dir, per session) for its own memory, plus a repo HANDOFF.md written only in handoff mode for the next session [recommended by the planner; honours "no repo-singleton session state" and keeps product-repo stage handoffs]; (b) A: keep one repo HANDOFF.md, made safe by the lineage check (smallest change; concurrent sessions still overwrite each other); (c) B′: per-session only (breaks product-repo stage handoffs and unattended chains).
- plan fix round 2: serial 02_review-round-2.md — adoption pinned to manifest version (manifest_sha); Read adopts only mode: handoff; conditional header wording; F1 HARD marker iff hard_applies(block_window, tok); one-main-session-per-process noted; unattended section defers to a custody skill's mode.
- dispatch: plan reviewer opus — round 3 (resume)
