---
id: checkout-guard-hook-6e29
title: "PreToolUse hook: enforce checkout/worktree convention for tracked-file edits"
type: feature
status: done
priority: 2
tags: [claude-kit]
created: 2026-09-14
updated: 2026-09-14
closed: 2026-09-14
refs:
  - pintail-11 relaying operator, 2026-09-14; builds on checkout-process-convention-9e6d (merge 3db9c47)
---

Operator (2026-09-14, via pintail-11): enforce the process-in-checkout/work-in-worktree convention from the missing direction — the harness blocks worktree sessions from editing the main checkout, but nothing stops a main-checkout session editing tracked files. Add a PreToolUse hook (claude-kit/hooks on main's layout): trigger on Edit|Write|NotebookEdit (and MultiEdit if the harness sends it) when cwd is a git MAIN checkout (git rev-parse --git-dir == --git-common-dir); block when the target is tracked (git ls-files --error-unmatch) with message pointing at EnterWorktree / Agent worktree isolation / the sandbox skill's convention section. Allow: untracked files, .claude-sandbox/ and .claude/ paths, files outside the repo, all reads. Ralph exempt (runs in a worktree, so the main-checkout condition already excludes it — implementer verifies rather than special-cases). Escape hatches: env CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1, plus a per-repo marker documented next to the convention in the sandbox skill. Bash writes (sed/heredoc) OUT of scope for cut 1 — record as open question, do not parse shell. DECISION FLAGGED FOR OPERATOR: as spec'd the hook enforces by default in every repo where the plugin is installed; alternative is per-repo opt-in. Implemented as spec'd, surfaced in the landing report. Post-factoring placement open: context-guard is the only hooks plugin under the factored doctrine but this is not its aim — note for the migration, do not solve here.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-14 claimed by librarian
- 2026-09-14 done: cf75148 merged to local main; review CLEAR round 2; default-on decision pending with operator

## Review
- Round 1 (35618de): NEEDS_CHANGES — 1 HIGH: implementer's "MultiEdit is not a current tool
  name" claim falsified (docs + Anthropic's security-guidance plugin both match it); a
  MultiEdit bypassed the guard. 1 MEDIUM: submodule files false-allow from the superproject
  checkout (live-verified). 32 attack probes otherwise clean: no false blocks, no crash
  paths, correct deny contract (hookSpecificOutput permissionDecision deny, exit 0).
- Round 2 (7c74008): CLEAR — MultiEdit in matcher + exact-JSON test; submodule gap documented
  as a limitation next to Bash writes (deferred fix per directive); rev-parse collapsed to
  one call (main-checkout path 2 subprocesses, routing re-probed unchanged); NotebookEdit
  file_path-spelling test added. 79 tests OK. 1 pathological nit accepted (newline in repo
  path, fails toward allow).
- Known limitations (documented in the skill): Bash writes unguarded; submodule files
  unguarded from the superproject checkout. Escape hatches: CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1
  env, .claude/allow-checkout-edits marker file.
- OPERATOR DECISION PENDING: enforce-by-default in every repo with the plugin (as spec'd and
  landed) vs per-repo opt-in. Post-factoring placement also open (not context-guard's aim).
