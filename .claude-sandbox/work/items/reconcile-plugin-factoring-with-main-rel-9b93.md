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
- doing: —
- next: —
- blocked: —
- learned: —
- OPERATOR 2026-09-16 (decision 6): unblocked. Librarian plan: (1) land in-flight (F1 eff1) and push main; (2) dispatch
  a fable agent in the existing plugin-factoring worktree: rebase plugin-factoring onto main (or merge main in if the
  rebase is unmanageable — say which), relocate checkout_guard.py + hooks.json PreToolUse registration + the checkout
  convention text into plugins/sandbox (peer decision 1, adopted), keep enforcement default on with per-repo opt-out
  (peer decision 2, adopted), carry every skill landed today (usage-report, model routing, librarian changes,
  context-gate fixes) into the factored layout, fix .claude-sandbox/work/README.md's plugin reference, update README
  catalog + CLAUDE.md layout, run every test suite and the skill lint; (3) fable review; (4) NOT merged to main:
  the branch is the operator's test branch — the librarian verifies everything it can, then hands the operator
  step-by-step marketplace-switch and verification instructions; (5) merge to main after the operator's manual test.
  Pushing the branch: outside the librarian's push rule (main only) — the operator pushes it, or authorizes once.
dispatch: implementer fable — rule 3 (gating hook relocation; marketplace shape; hard to reverse)
dispatch: reviewer fable — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
