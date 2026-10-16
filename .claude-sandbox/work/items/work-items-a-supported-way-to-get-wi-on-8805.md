---
id: work-items-a-supported-way-to-get-wi-on-8805
title: "work-items: a supported way to get wi on PATH (plugin bin/, alias or install step); wi init outside a git repo"
short_display_name: wi on PATH
type: feature
status: todo
priority: 1
created: 2026-10-16
updated: 2026-10-16
refs:
  - peer claude-sandbox 2026-10-16 (operator report)
---

claude-sandbox relayed an operator report 2026-10-16: wi init in /home/rt/work/src/github.com/kmacmcfarlane (workspace dir, not a git repo) failed because wi is not a command; it exists only as skills/work-items/scripts/wi.py in the plugin install path. Acceptance: a documented, supported way for a person and any agent to run wi (a plugin-provided bin/ if Claude Code supports one, else a documented alias or install step), and a stated answer whether wi init outside a git repo is supported.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: outside a git repo, wi init is supported as built at d1e9 F3 (local main f77dab82, unpushed): the store reads as dedicated (no host), --no-track gives it its own repo, --track records tracked with no repo; the installed wi predates that, which the plan must check
dispatch: planner opus high — plan: wi on PATH (docs check for plugin bin/ support), non-git init
agent: planner aad36ca72d09d8143 plan round 1
return: planner DONE (00_initial.md; plugin bin/wi launcher on the Bash tool PATH (plugins-reference § Standard layout); person: copy to ~/.local/bin/wi, resolves the install from installed_plugins.json; snippets get a command -v wi step; non-git init supported (format.md); OQ1-OQ4 incl. workspace dir became a git repo 2026-10-16 01:20)
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer a7ab74622040b4c11 plan round 1
note: asked claude-sandbox whether it made the workspace dir a git repo (OQ4); alert raised to the operator
