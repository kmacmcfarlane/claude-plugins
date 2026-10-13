---
id: history-scrub-purge-claude-code-bundle-d-4151
title: "History scrub: purge Claude Code bundle-derived content from git history, then force-push"
short_display_name: history scrub of bundle content
type: spike
status: todo
priority: 0
deps:
  - review-claude-code-bundle-derived-conten-e347
created: 2026-10-06
updated: 2026-10-06
refs:
  - operator 2026-10-06, decision 164
---

Operator 2026-10-06 on decision 164: 'I want to perform the history scrub of this content to stay compliant with copyright.' One-way and outward: every sha from 2026-09-19 on changes (the store's recorded landed: shas, parked worktree branches, other clones, peer references); origin needs a force-push, which librarian-mode forbids itself; GitHub may keep unreferenced commits reachable by sha until GC or a support request. Acceptance: a plan (passages to purge, tool such as git filter-repo, pre/post verification, what happens to worktrees, the store and other clones, the GitHub cache step) and a one-way decision before anything runs; runs only after the scrub build (e347) lands.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
wake 171: when the operator has time to oversee it closely — operator, verbatim: "171 - will need to be later when I have time to oversee closely" (2026-10-07T17:38Z, chat; read as: later, wake on the operator's say-so; the history scrub waits; 170, 172-174 wait with it)
note: 2026-10-07T18:35Z purge inputs to add (from the e347 build review): the transcript write-queue/interval/compaction-order passages at plugins/context-guard/hooks/lib_context.py (pre-scrub :73-78, :1662-1669 region), tests/test_window_mirror.py, tests/test_lib_context.py:236, and the bace series' executable-read text if any is tracked
note: 2026-10-07T18:45Z purge inputs: the undocumented loop variable in store item 8ab6:26, on main since e122bdd (deny-listed locally)
answer 171: later (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:51:03.424Z; read as: later, as before — when the operator can oversee it)
