---
id: shell-snippets-run-python3-c-without-i-a-9782
title: "shell snippets run python3 -c without -I: a json.py in the cwd runs"
short_display_name: python snippets without -I
type: bug
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T19:47Z
created: 2026-10-12
updated: 2026-10-12
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
