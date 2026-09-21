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
- doing: Reviewed twice by the librarian; ready at 05e6c68 (4 commits on plugin-factoring, 90 tests OK)
- next: After plugin-factoring lands on main: rebase onto main, re-run suite, librarian merges
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
