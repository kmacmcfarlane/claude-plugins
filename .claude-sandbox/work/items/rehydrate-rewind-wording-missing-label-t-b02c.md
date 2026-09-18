---
id: rehydrate-rewind-wording-missing-label-t-b02c
title: "rehydrate: rewind wording, missing label tests, CRLF frontmatter, git-unavailable label"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:47Z
created: 2026-09-18
updated: 2026-09-18
---

From the 4a19 review (2026-09-18), all low: (1) pure rewind reads 'head moved 0 commits … not an ancestor' — use rev-list --left-right --count rec...HEAD (same single call) for 'N ahead, M behind'; (2) tests for STALE(<reason>) and AGED on a diverged branch; (3) _trim_items frontmatter opener regex rejects ---\r\n; (4) under a hung git the label reads FRESH — label '(git unavailable)'; nit: blank lines before def trim. Files: plugins/context-guard/hooks/rehydrate.py, tests, checkpoint references/handoff-format.md.

## Handoff
- doing: dispatched in worktree
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic (SessionStart hook; informs, does not gate)
