---
id: work-items-skill-name-claude-sandbox-tra-29db
title: "work-items skill: name CLAUDE_SANDBOX_TRACK_IN_HOST in the wi init rule"
short_display_name: name the sandbox track variable
type: chore
status: blocked
priority: 3
blocked: waits on claude-sandbox d54f landing (peer will message the commit)
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
