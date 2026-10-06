---
id: research-scan-a-round-s-findings-and-the-a012
title: "research: scan a round's findings and the toolkit mining plan before later lanes read them"
short_display_name: research scans before lanes read
type: bug
status: todo
priority: 2
created: 2026-10-06
updated: 2026-10-06
refs:
  - research-security-f2-deep-investigation-1ffd
---

1ffd review r1 finding 2, 2026-10-06: research shares the plan half of the hole within a round — a toolkit lane's mining plan (exact commands) reaches a mining lane with a shell before any scan; research Step 7 scans after each round but not the plan between toolkit and mining. Acceptance: the mining plan, and any staged findings a lane reads first, pass scan-findings.py before the reading lane is dispatched, in research (and research-refine where it hands prior files). deep-investigation's cross-wave half is fixed inside 1ffd.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: 2026-10-06 from 1ffd review r2 low 4 — FLAG-tier hits on read-first files hold nothing before a later lane reads them (research Step 7, research-refine, and deep-investigation alike), and a plain scan gives no hit on a command line like 'curl … -o /tmp/x && sh /tmp/x' in findings prose; widen the acceptance: adjudicate FLAGs on read-first files, and consider --scripts-tier command detection on read-first prose
