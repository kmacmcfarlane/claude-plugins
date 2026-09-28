---
id: research-agents-glob-grep-listed-in-tool-6d9f
title: "research agents: Glob/Grep listed in tools but possibly not exposed to plugin sub-agents"
type: bug
status: dropped
priority: 2
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - caef planner 2026-09-28
---

Found by the caef planner 2026-09-28 (series caef-research-security Q12): research-lane and research-verifier list Glob, Grep in tools, but this CLI build seems not to expose them to plugin sub-agents; the verifier has no shell, so it could not search at all. Acceptance: probe and confirm; if confirmed, fix the agents' tool lists or their method so the verifier can search.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 correction from the caef planner (series 01, from docs + CLI source): on Linux Glob/Grep are removed by default and come back only for an agent that lists them and NOT Bash; research-verifier (no Bash) keeps them and can search; research-lane (lists Bash) searches via Bash. So the verifier is fine; acceptance narrows to confirming this and documenting it in the agents' bodies if useful
- 2026-09-28 resolved without a change: the caef planner (series 01, from docs and CLI source) and its reviewer (tools-reference:263-269) confirm Linux removes Glob/Grep by default and restores them to a sub-agent that lists them and not Bash — research-verifier (no Bash) keeps them; research-lane searches via Bash

## Notes
- 2026-09-28 dropped
