---
id: context-guard-statusline-8588-review-low-d8f6
title: "context-guard/statusline: 8588 review lows (id rule on cache-path name, shlex.quote hatch path, installPath scope)"
type: chore
status: doing
priority: 4
owner: unknown@360f41058e92
claimed: 2026-09-21T23:45Z
created: 2026-09-21
updated: 2026-09-21
---

From the 8588 review (all low): statusline/hooks/owner.py:106-108 derive the cache-path data-dir name with the same re.sub id rule as installed_by_record; context_warn.py:119-129 quote the hatch path with shlex.quote (a ! in the path triggers bash history expansion in double quotes); operator-playbook.md:152 pick the installPath entry by scope, not [0].

## Handoff
- doing: implementer dispatched (opus, agent a16905a74d0077651)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — gate hook code (context_warn); owner.py part moot (deleted in F3)
