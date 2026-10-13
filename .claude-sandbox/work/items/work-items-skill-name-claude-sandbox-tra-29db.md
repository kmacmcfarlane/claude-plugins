---
id: work-items-skill-name-claude-sandbox-tra-29db
title: "work-items skill: name CLAUDE_SANDBOX_TRACK_IN_HOST in the wi init rule"
short_display_name: name the sandbox track variable
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T17:23Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer claude-sandbox librarian, 2026-10-13 (its item d54f)
---

The claude-sandbox librarian (peer, 2026-10-13) is building d54f: the launcher exports CLAUDE_SANDBOX_TRACK_IN_HOST=true|false from the merged trackInHost of the config cascade (every .claude-sandbox/config.yaml from / down to the project), unset when none defines it (launcher then behaves as false); set in every new container, inherited by joined sessions. Acceptance: once d54f lands on claude-sandbox main (the peer messages the commit), the work-items SKILL.md init rule names the variable: true → wi init --track; false or unset → --no-track; not in claude-sandbox → ask the operator. Waits on that landing.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
note: 2026-10-13 claude-sandbox d54f landed at 7fd9f1c (spec CS-LNCH-184), per its librarian: CLAUDE_SANDBOX_TRACK_IN_HOST=true|false from the merged cascade trackInHost; no -e passed when no config defines it, so it is unset unless a cascade env file sets it; layout treats unset as false; present from the next launch, not in running containers
target: work-items SKILL.md init rule names CLAUDE_SANDBOX_TRACK_IN_HOST: true → --track; false or unset → --no-track; a sandbox launched before the export lacks it, so unset inside a sandbox reads as false (the launcher's own default); outside claude-sandbox (no CLAUDE_SANDBOX_CONTAINER) ask the operator; format.md if it repeats the rule
dispatch: implementer sonnet medium — build (doc line naming a landed variable: canonical kind)
