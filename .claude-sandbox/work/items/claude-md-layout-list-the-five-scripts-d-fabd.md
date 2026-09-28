---
id: claude-md-layout-list-the-five-scripts-d-fabd
title: "CLAUDE.md layout: list the five scripts/ dirs that exist on disk"
type: chore
status: done
priority: 4
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 5a18 implementer
---

Found by the 5a18 implementer 2026-09-28: CLAUDE.md's Repository Layout block omits context-guard/skills/checkpoint/scripts, context-guard/skills/usage-report/scripts, dev-flow/skills/librarian-mode/scripts, statusline-hub/skills/install-statusline-hub/scripts and work-items/skills/work-items/scripts. Acceptance: the layout block names them (one-line gloss each, existing style), and update-kit's repo-map.md follows in the same commit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 from the 5a18 review: also add '+ hooks.json' to the context-guard hooks/ note in both CLAUDE.md and repo-map.md; the comparison script is at scratchpad review-5a18/cmp.py
target: branch worktree-claude-md-layout-list-the-five-scripts-d-fabd at .claude/worktrees/claude-md-layout-list-the-five-scripts-d-fabd, base main (577d93b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer sonnet — layout list entries and pointers (rule 1)
agent: implementer ab981aef7dec5f043 round 1
return: implementer DONE 739fca5
changed: CLAUDE.md, plugins/kit-dev/skills/update-kit/references/repo-map.md
dispatch: reviewer opus — fresh (rule 4; CLAUDE.md keeps a reviewer)
agent: reviewer a69331eccfff66356 round 1 at 739fca5
verdict: CLEAR round 1 at 739fca5 (2 nit: a double space in repo-map.md:85; mild repetition with the existing installer line — declined, cosmetic)
landed: 7a418f3
- 2026-09-28 done: 7a418f3
