---
id: shell-snippets-run-python3-c-without-i-a-9782
title: "shell snippets run python3 -c without -I: a json.py in the cwd runs"
short_display_name: python snippets without -I
type: bug
status: done
priority: 2
created: 2026-10-12
updated: 2026-10-12
closed: 2026-10-12
refs:
  - one-way-to-reach-wi-from-outside-work-it-b9e4
---

From b9e4 review 2, 2026-10-12: snippets outside the wi lookups still run python3 -c or python3 - from the working directory, so a json.py there is imported: dev-cycle model-routing.md:459, checkpoint operator-playbook.md:319, dev-flow review-checklist.md:283,324,325, session-name.md:41, create-repo SKILL.md:73,105, update-kit SKILL.md:350, work-review SKILL.md:74. Acceptance: every such snippet runs python3 -I; a grep test keeps it so.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: every python3 -c / python3 - snippet in skills and references runs -I; a kit-dev or plugin test greps for any without it
dispatch: implementer sonnet medium — build (a mechanical sweep: canonical kind)
agent: implementer a2a41b98a71a74186
return: DONE b0d262a; 15 lines across context-guard, create-repo, dev-flow, kit-dev, work-items; test_isolated_python.py in kit-dev (skips outside the source repo); 12/12 OK (kit-dev 21); open: -m json.tool and -m py_compile left without -I
dispatch: reviewer opus high — review round 1 of b0d262a
agent: reviewer a6051b1f85c3fb961
verdict: review round 1 NEEDS_CHANGES (must-fix 2: medium 1 — -m json.tool and -m py_compile in review-checklist import a planted json.py or re.py (reproduced); -I safe for both, unittest discover exempt; medium 2 — the test misses -m, inline-code prose and /usr/bin/python3; patched test at scratchpad/9782-review/fixed/; nit 3 bare stdin forms (none today); low 4 ruamel under -I degrades on a --user install, optional guard)
dispatch: implementer sonnet medium — fix round 1 (resume a2a41b98a71a74186)
return: DONE c11ed0b (fix round 1); kit-dev 21 OK, dev-flow 78 OK; stdin pattern narrowed to < followed by < or whitespace (placeholders like python3 <path> were flagged)
dispatch: reviewer opus high — review round 2 of c11ed0b (resume a6051b1f85c3fb961)
verdict: review round 2 CLEAR (must-fix 0; nits: pipe form caught only at end of line (widened pattern given, nothing in plugins today); stale comment at test line 28; accepted gaps: python3 <f.py with no space, -uc combined, flags with arguments, ${PY:-python3})
decided: 2026-10-12T21:15Z cap — a finish round of nits 1 and 3, exact (authority answer 145)
dispatch: implementer sonnet medium — finish round (resume a2a41b98a71a74186)
verdict: finish round CLEAR — diff read: widened pipe pattern, four flag cases and one accept case, comment
landed: 1fc17db (merge of b0d262a..2a2b21e); Checks 12/12 OK (kit-dev 21); cc_scan clean
- 2026-10-12 done
