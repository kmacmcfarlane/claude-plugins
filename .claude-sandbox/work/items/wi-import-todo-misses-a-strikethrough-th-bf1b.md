---
id: wi-import-todo-misses-a-strikethrough-th-bf1b
title: wi import-todo misses a strikethrough that wraps only the bold title
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T22:48Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (wi-import-todo-misses-strikethrough-wrap-1b1b). '- [ ] ~~**Title**~~ rest' imports as open with literal ~~**…**~~ in the title; closed-entry detection expects the strike to wrap the whole entry. Acceptance: a strike wrapping the title counts as closed and the markers are stripped; test with both wrap shapes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full wi-import-todo-misses-a-strikethrough-th-bf1b /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-import-todo-misses-a-strikethrough-th-bf1b
dispatch: implementer opus — executable logic (wi.py), rule 2
agent: implementer ae88fb9e69adfe405 round 1
return: implementer DONE 3b54e22
changed: wi.py, tests/test_wi.py
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a9569a76c211e6e99 round 1
verdict: NEEDS_CHANGES round 1 at 3b54e22
findings:
- [medium] wi.py:2185-2195 + cmd_import_todo:2215 — re-import after this change duplicates items imported before it (dedupe marker norm_title changes from "t rest" to "t"); SKILL.md:48 promises idempotent migration. Pass: _bullet_item also yields the pre-fix title, cmd_import_todo skips when either marker exists; test importing under the legacy title then re-importing creates nothing.
- [medium] wi.py:2177 WHOLE_STRIKE_RE anchored on $ over the joined entry — a struck first line with an unstruck indented continuation (or trailing note) stays open with markers. Pass: judge the whole-entry strike on the title line only, continuation to desc; multi-line test.
- [low] test_wi.py:562-603 — add a regression test for a struck title followed by ~~ in the rest text.
dispatch: implementer opus — fix round 1 (resume)
return: implementer DONE 7dc3546
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a9569a76c211e6e99 round 2
verdict: NEEDS_CHANGES round 2 at 7dc3546 (both r1 mediums confirmed closed by the reviewer's own main-then-HEAD reproduction)
findings:
- [medium] wi.py:2190 STRUCK_PLAIN_LINE_RE — any text after a dash closes: `- [ ] ~~Migrate to PG15~~ — PG16 instead` imports done and the open task leaves the queue. Pass: close a plain struck line only when nothing follows, a paren follows, or a dash is followed by a closure word (done/fixed/landed/closed/resolved/dropped/merged/wontfix) and/or a date; test the `~~X~~ — Y instead` shape stays open.
- [low] wi.py:2213-2216 empty strike `~~ ~~` imports done with an empty title (lint fails). Pass: None on empty; require non-space inside.
- [low] wi.py:2211 `~~**T** x~~y` desc `xy` — join with a space.
dispatch: implementer opus — fix round 2 (resume)
agent: implementer ae88fb9e69adfe405 round 3
return: implementer DONE 991acd4
dispatch: reviewer opus — review r3 (resume)
agent: reviewer a9569a76c211e6e99 round 3
verdict: NEEDS_CHANGES round 3 at 991acd4 (round-2 medium, idempotence and lows confirmed closed)
findings:
- [medium] wi.py:2193 STRUCK_PLAIN_LINE_RE paren branch closes whatever the paren says: `~~Use Redis~~ (use Memcached instead)`, `~~X~~ (not yet)` import done. Pass: the paren branch takes the same closure-word-or-date test; test `~~X~~ (use Y instead)` stays open.
- [low] :2189 _CLOSURE_WORD ends \b — `fixed-width`, `closed-source`, `done-ish`, `done?` close. Pass: (?![\w-]), optionally reject `?` after.
- [low, record only] any text after a closure word accepted — deliberate, kept.
dispatch: implementer opus — fix round 3 (resume); medium, not critical/high, so no rule-3 bump; the last round under the cap
agent: implementer ae88fb9e69adfe405 round 4
