---
id: review-checklist-2-lint-a-sibling-skill-d95a
title: "review-checklist §2 lint: a sibling skill name ending a line before an indented path is not recognised"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:53Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - F4 review r1
---

e770 F4 review r1 note, 2026-09-22: the §2 sibling-name regex (`name`(?: skill)?'s with a single space) misses a backticked sibling name that ends the previous line when the next line is indented — a wrap the checklist itself allows — so it FAILs a valid pointer (librarian-mode SKILL.md:95-96 at b4ed234). Acceptance: the regex accepts newline+indentation between the name and the path; test on both shapes. File: plugins/dev-flow/skills/dev-cycle/references/review-checklist.md.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full review-checklist-2-lint-a-sibling-skill-d95a /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/review-checklist-2-lint-a-sibling-skill-d95a
dispatch: implementer opus — the lint is executable logic (a shell/regex check every review runs), rule 2
