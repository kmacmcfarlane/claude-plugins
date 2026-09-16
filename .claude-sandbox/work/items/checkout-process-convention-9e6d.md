---
id: checkout-process-convention-9e6d
title: "Convention: process stays in the checkout, work goes in a worktree"
type: feature
status: done
priority: 0
tags: [sandbox]
created: 2026-09-14
updated: 2026-09-14
closed: 2026-09-14
refs:
  - pintail-11 session relaying operator, 2026-09-14; upstream claude-sandbox 75d8197 on worktree-pintail (verified)
---

Operator (2026-09-14, via pintail-11; upstream flip verified at claude-sandbox 75d8197): interactive claude launches now start in the shared checkout because transcripts file by working directory — a worktree cwd gave --resume an empty history and cost a conversation. Ralph still launches in a worktree. Land the convention in the shared skills, sandbox skill as the home: (1) a session starts in the repo checkout; before substantive repo edits, EnterWorktree or delegate to an Agent with worktree isolation; ExitWorktree once merged/handed off; (2) reading, planning, answering questions, and .claude-sandbox/ edits need no worktree; (3) parallel tasks get one worktree each, never shared; (4) a worktree is a fresh checkout — untracked inputs (.env, node_modules) absent unless in .worktreeinclude or the worktree symlink setting; state this wherever a skill says to enter one; (5) ralph is the exception: whole run is work, launcher starts it in a worktree, run branch is the deliverable. Sandbox skill flag updates: --worktree now opt-in for interactive; --no-worktree default and rarely needed; worktree: true|false config key and CLAUDE_SANDBOX_WORKTREE=1|0 set the default for both interactive and ralph (one key governs both, only the fall-through default differs). Troubleshooting: empty --resume picker usually means the session is inside a worktree; Ctrl+W lists worktrees, Ctrl+A all projects. implement, investigate, and work-items skills reference the convention (short pointer, sandbox skill owns the text). PARTIALLY REVERSES sandbox-skill-worktree-78c0's default-on wording (that reflected the pre-flip launcher; both were correct at their time).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-14 claimed by librarian
- 2026-09-14 done: 3db9c47 merged to local main; review CLEAR round 3

## Review
- Round 1 (a3d5285): NEEDS_CHANGES — 2 medium: implement's reference told small plans to work
  inline "in the main checkout", contradicting rule 1 seven lines above the pointer; the
  investigate pointer omitted the fresh-checkout caveat at the exact probe site. All launcher
  facts verified against claude-sandbox 75d8197 (banner suppression, ResolveTristate per-kind
  default, compose-when-on, Ctrl+W). Ctrl+A is an item-spec fact, not upstream.
- Round 2 (a189bdc): fixed both + accepted nit ("the launcher's only off-state banner"; ralph
  loop.go:254-261 still prints its own off line). Implementer flagged the SAME contradiction
  in implement/SKILL.md Step 7, outside the scoped sweep.
- Round 3 (050999e): Step 7 Inline reworked — integration branch created in main checkout
  (process), tasks worked in the session's own worktree, merge from main checkout when done.
  CLEAR; 2 nits accepted (Step 7 doesn't restate the bare-slug collision warning; cleanup
  wording doesn't name ExitWorktree — the sandbox section supplies both).
- Partially reverses sandbox-skill-worktree-78c0's default-on wording; both matched the
  launcher at their time. Upstream: claude-sandbox 75d8197 (worktree-pintail, pending ff).
- 2026-09-14: Ctrl+A confirmed real (operator's Claude Code 2.1.261 resume-picker footer:
  "Ctrl+A to show all projects · Ctrl+B to only show current branch · Ctrl+W to show all
  worktrees · Space to preview · Ctrl+R to rename", via pintail-11). Open question closed;
  skill text stands as written.
