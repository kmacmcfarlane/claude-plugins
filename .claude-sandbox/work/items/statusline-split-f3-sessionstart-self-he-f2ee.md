---
id: statusline-split-f3-sessionstart-self-he-f2ee
title: "statusline split F3: SessionStart self-heal, takeover, first-run install, prune"
type: feature
status: doing
priority: 1
deps:
  - statusline-split-f2-the-statusline-plugi-a67f
parent: status-line-its-own-independently-instal-3c48
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T20:52Z
created: 2026-09-18
updated: 2026-09-18
---

3c48 plan §F3. Size M; opus (settings writes).

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — settings writes / hook code (rule 2); fable not needed: not a gate

impl: DONE be6d73d (session_start.py; --replace / --write-read-only split; splice write; prune; 198 tests). Out-of-scope notes: CLAUDE.md:35 layout line should name session_start; README context-guard section still says run /install-statusline.
dispatch: reviewer opus — rule 4
