---
id: context-guard-f3b-3-the-owner-sid-legacy-c3e1
title: "context-guard F3b-3: the owner==sid legacy copy and the stamp-step warning (warn only)"
type: feature
status: doing
priority: 2
deps:
  - context-guard-f3b-4-the-checkpoint-contr-0426
parent: context-guard-8cc2-f3b-where-handoff-md-a49b
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T22:53Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - a49b
---

Plan of record .claude-sandbox/investigations/8cc2-turn-gate-port, 08_f3b3-warn-only.md final form (supersedes 07). After F3b-4 (06 order). Brief carries the four 08 lows and F3b-1's trim-budget low (see a49b). Route opus/opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-f3b-3-the-owner-sid-legacy-c3e1 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-f3b-3-the-owner-sid-legacy-c3e1
dispatch: implementer opus — hook logic deciding what memory a session is given; plan routes opus
agent: implementer a3dabe735be8fe6d2 round 1
return: implementer DONE_WITH_CONCERNS 1e37c0b
changed: hooks/rehydrate.py, hooks/mark_checkpoint.py, tests/{test_rehydrate,test_lineage,test_rehydrate_stale}.py, checkpoint references/{handoff-format,operator-playbook}.md
librarian: test_rehydrate_stale.py accepted into Files in scope (a fixture the copy freezes by design, same change as the in-scope tests).
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a05d99543406d4ed4 round 1
verdict: NEEDS_CHANGES round 1 at 1e37c0b
findings:
- [medium] rehydrate.py:1210 — copy trusts the repo file's session: line alone: a peer editing S's stamped file in place (keeping session: S; its own mark refuses) gets its body copied into S's store at S's next SessionStart, and S keeps it as own memory permanently, where main drops to the foreign header once P rewrites. Pass: copy only while the bytes are still S's stamp — mtime within STAMP_TOUCH_S after written: (mark_checkpoint's _own_stamp relation); else fall back to the live read; test the in-place edit.
- [medium] rehydrate.py:1123-1125 — the <sid>/ dir-link guard is untested (mutant green; with it removed a planted <store>/S -> elsewhere gets HANDOFF.md written into elsewhere). Pass: a TestLegacyCopy case with a symlinked <sid>/ dir: no copy, target dir empty, no legacy_copy.
- [low] :1113-1115 CRLF manifests never copied (raw-bytes sha vs text-mode sha) — hash as read_text reads, or document.
- [low] mark_checkpoint.py:369 — a FIFO at legacy_copy.path hangs the mark (gate stand-down blocks). Pass: S_ISREG before reading.
notes: copy mechanics, warn-only, trim decision, four lows and 3a8f all confirmed; the warning retires with the copy (08 OQ: agree).
librarian: medium 1 takes the reviewer's pass (the obvious fail-safe fix, no operator decision: it narrows what is copied, never widens).
dispatch: implementer opus — fix round 1 (resume)
agent: implementer a3dabe735be8fe6d2 round 2
return: implementer DONE 169dec5
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a05d99543406d4ed4 round 2
