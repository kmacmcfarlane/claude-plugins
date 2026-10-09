---
id: checkpoint-namespace-the-reply-hint-as-c-aebc
title: "checkpoint: namespace the reply hint as /context-guard:checkpoint so it pastes"
short_display_name: checkpoint reply hint namespaced
type: bug
status: done
priority: 1
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
refs:
  - operator message 2026-10-09
---

Operator 2026-10-09: the pasteable reply line the checkpoint skill drafts (Step 0) starts '/checkpoint', which collides with a built-in command of the same name, so it does not run the skill when pasted. Acceptance: every reply line, opener and example the checkpoint skill (and context-guard docs, librarian-mode's references to it) tells an agent to print uses '/context-guard:checkpoint'; a test pins it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
note: Step 0's reply and override lines are namespaced by 9652 (86970e6); this item covers the remaining bare /checkpoint printouts, e.g. references/operator-playbook.md:128
dispatch: implementer opus medium — build, worktree (bug; no plan)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer aca6389fa9d43c977
return: DONE worktree-agent-aca6389fa9d43c977 54f07f7 (HARD STOP text and playbook namespaced; gate-whitelist lines left bare by design; whitelist test covers the namespaced form; new test_checkpoint_namespaced.py with allowlist; 10/10 Checks)
dispatch: reviewer opus high — review round 1 of 54f07f7
agent: reviewer a9502a1807ab75325
verdict: review round 1 CLEAR (lows: 1 allowed line can carry a bare instruction; 2 allowlist can grow to hide a regression; nits 3 manifests unscanned, 4 test location acceptable, 5 long lines)
decided: 2026-10-09T07:50Z cap — finish round of exact-fix leftovers 1-3 and 5 (authority answer 145); 4 accepted as is
dispatch: implementer opus medium — finish round (resume aca6389fa9d43c977)
return: DONE cd56c15 (finish round: bare_outside per-fragment check; fragments must name /checkpoint /compact /clear, two reflowed to fit; manifests scanned; reflows; 808 tests)
review: self
verdict: finish round CLEAR — diff read: test tightening plus docstring and playbook reflows, no behaviour change
landed: cb154bd (merge of 54f07f7, cd56c15); Checks 10/10 OK
- 2026-10-09 done
