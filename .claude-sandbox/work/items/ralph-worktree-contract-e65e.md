---
id: ralph-worktree-contract-e65e
title: "ralph skills: worktree-run contract (base_sha, no per-story branches)"
type: feature
status: done
priority: 2
tags: [ralph]
created: 2026-09-08
updated: 2026-09-08
closed: 2026-09-08
refs:
  - claude-sandbox librarian session, 2026-09-08
---

Sandbox librarian (2026-09-08, landed on claude-sandbox main 8b2f22a + 7e6abd7): ralph runs in one worktree per run named ralph, reopened each iteration; ralph never merges — branch worktree-<name> is the deliverable a human fast-forwards from; per-story branches are GONE in both modes. New contract for the ralph skills (backlog-yaml/backlog-entry/backlog-grooming): story gains optional base_sha, recorded by next-work --claim (git HEAD of agent cwd) and on every entry to in_progress; review/QA context bundle is git diff <base_sha> (working tree vs story base), NEVER git diff main; developer brief line: **Base**: <base_sha> (work on the current branch; do not create branches or merge). Writes to .claude-sandbox/ from inside the worktree go through Bash (harness blocks Edit/Write to main checkout). Legacy scripts/worktree helper and .worktrees/<id> / story/<id> convention deleted; migration recipe in claude-sandbox docs/MIGRATION.md. CAVEAT unverified live: whether Bash writes from the worktree into the gitignored sidecar pass the harness guard — flag in skill text as unverified until a ralph run confirms.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: 0594dd8 merged to local main; review CLEAR round 2

## Review
- Round 1 (ef7225b): NEEDS_CHANGES — 1 medium: grooming Step 2.4 auto-committed the sidecar
  while backlog-yaml's SOP mandates prompt-first; every upstream fact verified accurate
  against claude-sandbox @ 7e6abd7 (--claim atomics, base_sha 7-40 hex, diff rule, Base line
  verbatim). Fixed prompt-first in edb1dd5; backlog-yaml SOP untouched.
- Round 2 (edb1dd5): CLEAR — fix verified at grooming SKILL.md:240-243; trackInHost:true
  direct-commit boundary ruled sound (both prompt-first statements self-scope to the sidecar;
  host-mode direct commit predates this change). Reviewer note: extending prompt-first to
  host-mode commits would be a policy change in backlog-yaml + sandbox skills, not a defect.
- Open: Bash-into-sidecar harness-guard behavior UNVERIFIED in skill text pending the sandbox
  side's verify-ralph-worktree-live run. Possible follow-up: cli-reference add-section
  optional-fields list is a partial sync with canonical backlog.py.
