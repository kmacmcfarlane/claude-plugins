---
id: context-guard-state-lock-aware-manual-st-fe33
title: "context-guard state: lock-aware manual stand-down, O_NOFOLLOW on lock open, orphan temp/lock cleanup"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:59Z
created: 2026-09-18
updated: 2026-09-18
---

From the 41e7 review (2026-09-18), low/nit: (1) install-statusline SKILL.md:68 manual stand-down is atomic but takes no lock (~1ms window can drop checkpoint_epoch) — flock inside the one-liner or point at mark_checkpoint.py; (2) lib_context._acquire opens .<sid>.lock without O_NOFOLLOW (symlink creates a file outside the dir); (3) SIGKILL mid-write leaks .<sid>.<pid>.<hex>.tmp forever, .lock files never cleaned — sweep stale dotfiles (e.g. on SessionStart, older than N days); (4) postcompact_epoch st_before unlocked read (tokens only); nits: rehydrate pops custom_instructions only when not None; long docstring line lib_context.py:30.

## Handoff
- doing: bundled in worktree 3685
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic; bundled 3685+fe33 (both touch rehydrate.py)
