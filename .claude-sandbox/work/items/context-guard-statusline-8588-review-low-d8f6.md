---
id: context-guard-statusline-8588-review-low-d8f6
title: "context-guard/statusline: 8588 review lows (id rule on cache-path name, shlex.quote hatch path, installPath scope)"
type: chore
status: done
priority: 4
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
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
- 2026-09-21 done: 1149909

## Implementer result
- round 1 DONE_WITH_CONCERNS 934cef5 (opus): shlex.quote hatch path (bash history test); playbook picks installPath by scope; test_window_mirror expectation updated (in tests/** scope). Low 1 moot (owner.py deleted). Follow-ups filed: dev-flow [0].installPath; hub owner.py data-dir id rule.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 934cef5
- 20-case playbook probe passes; hatch round-trips in interactive bash with history on.
- landed 1149909
