---
id: reconcile-plugin-factoring-with-main-rel-9b93
title: "reconcile plugin-factoring with main: relocate checkout guard + convention into the sandbox plugin, rebase, land"
type: feature
status: doing
priority: 2
deps:
  - land-plugin-factoring-fbe8
owner: unknown@4d338747396e
claimed: 2026-09-16T17:53Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - peer session claude-sandbox-e3
---

Peer session claude-sandbox-e3 (formerly pintail-11), 2026-09-16, relaying the operator's ask: rebase the plugin-factoring branch onto current main, relocate checkout_guard.py + its hooks.json PreToolUse registration + the checkout convention text into plugins/sandbox (peer's decision 1: sandbox, not context-guard), keep enforcement default on with per-repo opt-out (peer's decision 2), run tests and lint, merge to local main, report in four lines; push stays with the operator. Peer facts are partly stale: origin/main is 7d5170f (operator pushed 2026-09-16), so checkout_guard.py IS on origin now. Librarian ruling: a peer cannot authorize landing plugin-factoring — item land-plugin-factoring-fbe8 is blocked on the operator's own review hold since 2026-09-08, and decisions 1-2 are the peer's relay, not the operator's word to this session. Filed as dependent on fbe8; goes to the operator under decisions needed. When unblocked: real conflict resolution needs judgement (the branch is far behind main) -> dispatch with main as base, fable (hooks that gate edits; marketplace shape).

## Handoff
- doing: branch verified CLEAR; awaiting the operator's manual test from their marketplace
- next: on the operator's go: merge plugin-factoring into main (fast-forward or merge commit), then F2/F3 of usage-report, then land the wi.py fallback fix on main
- blocked: operator manual test
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer fable returned DONE_WITH_CONCERNS: merges a360a1f/3e24f4e/9685b6f (main into branch, 3 times as main
  advanced), moves 66b3c57 (guard -> sandbox), eecda76 (librarian-mode -> kit-dev), 5c86c17 (usage-report ->
  context-guard), fixes fe1a7b3/969c040/fab0251. HEAD 9685b6f. Tests: context-guard hooks 92, sandbox hooks 16,
  usage-report 25, work-items 49 — all OK. claude plugin validate passed. Report:
  .claude-sandbox/investigations/plugin-factoring-reconcile/verification.md (2982 words).
- reviewer fable round 1 dispatched 2026-09-16 18:10:17
decision 8: usage-report home — context-guard (as placed) / own plugin / kit-dev
decision 9: sandbox plugin description now names the checkout guard — confirm the one-aim reading, or reword
decision 10: keep CLAUDE_KIT_ALLOW_CHECKOUT_EDITS as the opt-out name (byte-for-byte) or add a SANDBOX_ alias now
decision 11: product-research gains allowed-tools WebSearch, WebFetch, Read — confirm or drop
- review round 1: NEEDS_CHANGES — 1 medium (kit-dev/librarian-mode/references/troubleshooting.md:36 points the wi.py fallback at ${CLAUDE_PLUGIN_ROOT}/skills/work-items, which is kit-dev's root on the branch), 3 lows (README migration order double-fires hooks for one session; report misstates validate warnings — seven no-version warnings; kit-dev's catalog row does not declare the soft work-items dependency). Reviewer recommendations on decisions 8-11 recorded in its report. Manual test crib produced. Fix round 1 sent 2026-09-16 18:18:38, tier unchanged (fable, resumed).
- fix round 1 implementer killed by the API rate limit (2026-09-16 20:01:53) with 5 files edited but uncommitted in the worktree; fresh fable implementer re-dispatched to finish from that state (same round, same tier).
- fix round 1 (re-dispatched) returned DONE, commit 996b5ea; report § 11 appended. Re-review dispatched 2026-09-16 20:05:16 (reviewer fable, resumed). Open (operator): adopt a version field in plugin.json to silence validate?
- re-review CLEAR (all 4 FIXED; 1 new low: ls -t keys the cache by mtime, installed_plugins.json installPath is the correct key — folded into chore 89a6; 1 nit). Librarian Land checks on the branch: marketplace==disk, 11 json ok, 4 suites OK, 18 skills lint clean, catalog ok, single PreToolUse (sandbox), validate passed (7 no-version warnings). Branch plugin-factoring at 996b5ea is the operator's test branch; NOT merged to main by plan. 2026-09-16 20:08:23
- OPERATOR (2026-09-17 15:49:43): one-time authorization to push the test branch; pushed plugin-factoring 996b5ea to origin (fast-forward, no force).
