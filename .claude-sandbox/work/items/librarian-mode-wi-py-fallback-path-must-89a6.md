---
id: librarian-mode-wi-py-fallback-path-must-89a6
title: "librarian-mode: wi.py fallback path must not assume the skill's own plugin root"
type: chore
status: todo
priority: 4
created: 2026-09-16
updated: 2026-09-16
refs:
  - reviewer report, item reconcile-plugin-factoring-with-main-rel-9b93
---

From the 9b93 review 2026-09-16: references/troubleshooting.md and the Rehydrate glob note say the installed copy is ${CLAUDE_PLUGIN_ROOT}/skills/work-items/scripts/wi.py — true only while work-items lives in the same plugin as librarian-mode. On main that still holds; after the factoring merge it does not. Acceptance (main): point at the installed work-items copy by marketplace cache path (ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/*/skills/work-items/scripts/wi.py | head -1) so the line survives the factoring merge unchanged; the branch gets the same line in its fix round.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
Also (9b93 re-review): prefer installed_plugins.json plugins['work-items@kmacmcfarlane'][0].installPath as the key, ls -t as the fallback; apply on the branch too when it merges.

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.
