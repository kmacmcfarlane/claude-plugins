---
id: update-kit-point-skill-md-at-references-aa14
title: "update-kit: point SKILL.md at references/repo-map.md"
type: chore
status: done
priority: 4
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 5a18 review
---

From the 5a18 review 2026-09-28: update-kit SKILL.md mentions only the project-level agent/claude-kit-repo-map.md; references/repo-map.md (the upstream repo structures) is never pointed at, so a run loads it only by chance. Acceptance: one line in SKILL.md naming references/repo-map.md where the upstream structures are needed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-update-kit-point-skill-md-at-references-aa14 at .claude/worktrees/update-kit-point-skill-md-at-references-aa14, base main (577d93b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer sonnet — one pointer line (rule 1)
agent: implementer a74dc1b32405e5115 round 1
return: implementer DONE da15bcb
changed: plugins/kit-dev/skills/update-kit/SKILL.md
dispatch: reviewer opus — fresh (rule 4; skill text keeps a reviewer)
agent: reviewer a878e66e6b674a616 round 1 at da15bcb
verdict: CLEAR round 1 at da15bcb (1 low: a 115-char line — declined, the file is already inconsistent)
landed: d4598b1
- 2026-09-28 done: d4598b1
