---
id: sandbox-skill-repoint-relative-claude-sa-3827
title: "sandbox skill: repoint relative .claude-sandbox/ commands for worktree-mode cwd"
type: chore
status: done
priority: 3
tags: [sandbox]
created: 2026-09-08
updated: 2026-09-08
closed: 2026-09-08
---

Reviewer note (2026-09-08, sandbox-skill-worktree-78c0 round 1): pre-existing commands in the sandbox skill assume cwd = project root — touch .claude-sandbox/ralph/stop, git -C .claude-sandbox (sidecar SOP), grep of config.yaml — which is false inside a worktree where .claude-sandbox/ is gitignored and absent. CLAUDE_SANDBOX_PROJECT_DIR is the escape hatch; update those commands to use it (or state the cd) now that worktree mode is default-on. Also reviewer's nit: the banner troubleshooting entry recommends --no-worktree to 'make the stand-down explicit' — verify against the launcher whether the banner still prints with --no-worktree before keeping that sentence.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: 51b6729 merged to local main; review CLEAR round 1

## Review
- Round 1 (135991a): CLEAR (reviewer verdict PASS; 1 low accepted — workspace-root host cwd
  with a catch-all .claude-sandbox/ silently targets the wrong sidecar, same as before the
  change; 2 pre-existing nits: grep -l -A15 dead flag at :167, ancestor walk inspects
  unmounted host paths in-container). Banner fact verified against launcher source
  root.go:487-518,647: with --no-worktree the banner reads "Worktree: off (shared checkout)";
  the not-a-git-repository variant requires StoodDown (mode ON + no git root). Env var
  CLAUDE_SANDBOX_PROJECT_DIR confirmed set in every container incl. ralph iterations.
