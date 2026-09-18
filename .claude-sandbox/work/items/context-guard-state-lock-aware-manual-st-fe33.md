---
id: context-guard-state-lock-aware-manual-st-fe33
title: "context-guard state: lock-aware manual stand-down, O_NOFOLLOW on lock open, orphan temp/lock cleanup"
type: chore
status: done
priority: 4
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
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

impl: DONE 2ef111a (bundle; also fixed latent postcompact "0 tok" ledger header).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (.swept stamp write follows symlinks: empties a file outside the dir; reproduced); lows 2 (sweep unlinks a locked lock path; _acquire never re-checks inode), 3 (mark_checkpoint with a typo sid creates a stray json and reports success), 4 (glob with two data dirs), nit 5.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 46cdbd9 (1-5; mark_checkpoint refuses unknown ids; scope grew to mark_checkpoint.py + one test for finding 3).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. CORRECTION: the "ledger header always said 0 tok" claim was false — context_warn writes top-level tokens every prompt; the change now prefers exact.tokens. Lows to follow-up.
- 2026-09-18 done: 799cc0b
