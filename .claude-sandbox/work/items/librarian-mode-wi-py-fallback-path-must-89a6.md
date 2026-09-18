---
id: librarian-mode-wi-py-fallback-path-must-89a6
title: "librarian-mode: wi.py fallback path must not assume the skill's own plugin root"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:32Z
created: 2026-09-16
updated: 2026-09-18
refs:
  - reviewer report, item reconcile-plugin-factoring-with-main-rel-9b93
---

From the 9b93 review 2026-09-16: references/troubleshooting.md and the Rehydrate glob note say the installed copy is ${CLAUDE_PLUGIN_ROOT}/skills/work-items/scripts/wi.py — true only while work-items lives in the same plugin as librarian-mode. On main that still holds; after the factoring merge it does not. Acceptance (main): point at the installed work-items copy by marketplace cache path (ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/*/skills/work-items/scripts/wi.py | head -1) so the line survives the factoring merge unchanged; the branch gets the same line in its fix round.

## Handoff
- doing: bundled in worktree d72e
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — bundled chores in worktree d72e; >3 files (rule 2)
