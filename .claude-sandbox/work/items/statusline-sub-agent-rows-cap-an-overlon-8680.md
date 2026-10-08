---
id: statusline-sub-agent-rows-cap-an-overlon-8680
title: "statusline sub-agent rows: cap an overlong model or string effort so it cannot suppress the description"
short_display_name: long tag hides sub-agent description
type: bug
status: todo
priority: 3
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
