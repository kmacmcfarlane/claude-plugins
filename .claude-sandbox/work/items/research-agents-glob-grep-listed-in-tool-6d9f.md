---
id: research-agents-glob-grep-listed-in-tool-6d9f
title: "research agents: Glob/Grep listed in tools but possibly not exposed to plugin sub-agents"
type: bug
status: todo
priority: 2
created: 2026-09-28
updated: 2026-09-28
refs:
  - caef planner 2026-09-28
---

Found by the caef planner 2026-09-28 (series caef-research-security Q12): research-lane and research-verifier list Glob, Grep in tools, but this CLI build seems not to expose them to plugin sub-agents; the verifier has no shell, so it could not search at all. Acceptance: probe and confirm; if confirmed, fix the agents' tool lists or their method so the verifier can search.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
