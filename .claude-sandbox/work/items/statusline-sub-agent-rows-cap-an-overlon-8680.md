---
id: statusline-sub-agent-rows-cap-an-overlon-8680
title: "statusline sub-agent rows: cap an overlong model or string effort so it cannot suppress the description"
short_display_name: long tag hides sub-agent description
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T05:43Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - statusline-agent-panel-rows-show-each-su-7f91 review 2
---

Found by the 7f91 review 2 (finding 7, low), 2026-10-08. After 7f91, a non-empty tag that does not fit drops the description too; a pathological model id (~80+ chars) or a long string effort then hides the description at every width. Acceptance: cap the model length as EFFORT_MAX caps a numeric effort, or apply the cap to string efforts; a test shows the description survives an overlong tag.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-sub-agent-rows-cap-an-overlon-8680
budget: 2026-10-08T05:43Z build $12 — default bug
dispatch: implementer opus medium — renderer code change (not a canonical kind in a kit repo)

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a467aafec85f7118b
return: DONE 4e72c3f (MODEL_MAX 40 columns after the claude- prefix; EFFORT_MAX covers string efforts; a part past its cap drops whole; two tests; sweep extended)
changed: subagent_statusline.py (caps), tests/test_subagent_statusline.py (two tests, sweep), install-statusline SKILL.md (narrow-panel paragraph)
dispatch: reviewer opus high — review round 1
agent: reviewer a3a18497b18089536
