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
- doing: —
- next: —
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
