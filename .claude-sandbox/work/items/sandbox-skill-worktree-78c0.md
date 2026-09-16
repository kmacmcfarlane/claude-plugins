---
id: sandbox-skill-worktree-78c0
title: "sandbox skill: document worktree-mode launch (worktree key, --worktree/--no-worktree, env)"
type: feature
status: done
priority: 2
tags: [sandbox]
created: 2026-09-05
updated: 2026-09-08
closed: 2026-09-08
refs:
  - claude-sandbox librarian session, 2026-09-04
---

claude-sandbox launches claude in worktree mode by default. Settled names (2026-09-04): config key worktree: true|false (default true, cascades); flags --worktree[=NAME] and --no-worktree; env CLAUDE_SANDBOX_WORKTREE (0/false/no disables); precedence CLI > env > cascade YAML > default; worktree name defaults to the container's instance noun so container, worktree and branch share one word; --worktree=NAME reopens an existing one; ralph runs in one worktree named ralph per run and does not merge (branch worktree-ralph is the deliverable); the scaffold-ralph .worktrees/<id> helper is deleted. Update the sandbox skill's flags table and config keys once the launch half lands upstream; the sandbox librarian will send final wording. Also touches ralph skills where they reference the old worktree helper (see dev-flow-worktrees-1ff9).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
Final wording received 2026-09-08 (claude-sandbox librarian; landed upstream 8b2f22a, 7e6abd7):
config key `worktree: true|false` (default true, cascades); flags `--worktree[=NAME]`,
`--no-worktree`; env `CLAUDE_SANDBOX_WORKTREE` (0/false/no = off); precedence CLI > env >
cascade YAML > default on. Worktree `.claude/worktrees/<name>` on branch `worktree-<name>`;
name defaults to the container's instance noun (container/worktree/branch share one word);
`--worktree=NAME` reopens; join runs bare `--worktree`; `--branch` composes `--worktree
<new-noun>` with fork flags. Outside a git work tree: stands down with banner "Worktree: off
(not a git repository)". Per-session choice, excluded from drift fingerprint; container label
claude-sandbox.worktree; `sessions` lists a WORKTREE column; attach reports it. Every
container gets CLAUDE_SANDBOX_PROJECT_DIR = project root; layout adds .claude/worktrees/ to
the host .gitignore in both trackInHost modes. Ralph half tracked in ralph-worktree-contract.
- 2026-09-08 claimed by librarian
- 2026-09-08 done: f8e543f merged to local main; review CLEAR round 1

## Review
- Round 1 (1fe98d0): CLEAR. All ~20 facts verified against the Notes at file:line; 2 nits
  (duplicated sessions/reopen facts across sections mirroring the doc's existing pattern; an
  inferred --no-worktree recommendation in the banner entry, unsourced). Reviewer noted
  pre-existing relative-path commands assume cwd = project root, false inside a worktree —
  follow-up filed as sandbox-skill-worktree-cwd.
