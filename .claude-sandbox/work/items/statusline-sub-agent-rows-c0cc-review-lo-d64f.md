---
id: statusline-sub-agent-rows-c0cc-review-lo-d64f
title: "statusline sub-agent rows: c0cc review lows"
type: bug
status: todo
priority: 4
created: 2026-09-21
updated: 2026-09-21
refs:
  - c0cc reviewer
---

From c0cc review r3 2026-09-21 (CLEAR with lows). (1) subagent_statusline._usage_in on a >1 MiB line counts the last "usage" key anywhere, not only message.usage (synthetic toolUseResult.usage read wrong; none in 768 real sidechains); (2) a usage object missing a field borrows it from any object within 2048 bytes — stop at the object's closing brace; (3) test a usage key/fields straddling a chunk edge (LINE_MAX 4096, key at LINE_MAX-3 and +1); (4) README catalog row (line ~85) and decision tree (~110) mirror the one-clause description / name subagentStatusLine.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
