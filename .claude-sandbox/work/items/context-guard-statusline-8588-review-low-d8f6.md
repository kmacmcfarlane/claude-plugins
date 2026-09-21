---
id: context-guard-statusline-8588-review-low-d8f6
title: "context-guard/statusline: 8588 review lows (id rule on cache-path name, shlex.quote hatch path, installPath scope)"
type: chore
status: todo
priority: 4
created: 2026-09-21
updated: 2026-09-21
---

From the 8588 review (all low): statusline/hooks/owner.py:106-108 derive the cache-path data-dir name with the same re.sub id rule as installed_by_record; context_warn.py:119-129 quote the hatch path with shlex.quote (a ! in the path triggers bash history expansion in double quotes); operator-playbook.md:152 pick the installPath entry by scope, not [0].

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
