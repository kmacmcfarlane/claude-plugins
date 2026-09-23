---
id: read-list-accept-t-headings-say-so-when-c121
title: "read_list: accept '##\\t' headings; say so when an unclosed fence hides Read in full"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-23T00:02Z
created: 2026-09-22
updated: 2026-09-23
refs:
  - H6 review r2
---

From H6 review r2 (CLEAR) low, 2026-09-22: section_lines requires '## ' (tab no longer matched); an unclosed earlier fence hides the section quietly. Also reuse rehydrate._sections once H3 lands (a second parser drifts).

## Handoff
- doing: CLEAR round 2 at db28bed (reviewer done)
- next: land: merge-tree, merge --no-ff worktree-read-list-accept-t-headings-say-so-when-c121, context-guard check on main, clean up, wi done, push
- blocked: —
- learned: —

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

target: full read-list-accept-t-headings-say-so-when-c121 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/read-list-accept-t-headings-say-so-when-c121
dispatch: implementer opus — executable logic (read_list hook)
agent: implementer a700b6bf753d6f0b8 round 1
return: implementer DONE_WITH_CONCERNS 1e5ad64 (no shared parser: rehydrate._sections splits on "^## " only and ignores fences; import would be circular)
changed: hooks/read_list.py, hooks/rehydrate.py (fence_note in the full tier), hooks/tests/test_read_list.py
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a63655af1d1d84f24 round 1
verdict: NEEDS_CHANGES round 1 at 1e5ad64 (deviation claims verified; the note cannot carry manifest text; trim accounting correct)
findings:
- [medium] rehydrate.py:1300-1303 — rl_note is computed before withhold_next, the read list after it; withhold_next can remove a stale ## Next holding the fence opener, so the note says "not recorded" while the paths are recorded (reproduced). Pass: emit only when the post-withhold text still hides the section, keeping the original line number; test with a stale Next holding the fence.
- [low] read_list.py:45 — line numbers via splitlines() split on \x0b,\x0c,\x1c-\x1e,\x85, ; use text.split("\n") for numbering.
dispatch: implementer opus — fix round 1 (resume)
agent: implementer a700b6bf753d6f0b8 round 2
return: implementer DONE db28bed
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a63655af1d1d84f24 round 2
verdict: CLEAR round 2 at db28bed — land after Rehydrate (post-checkpoint gap: no merge)
low carried to 3c4f: withhold_next is fence-blind; it can remove a closing fence inside ## Next, so the list is lost and the note is silent (pre-existing loss; contrived).
