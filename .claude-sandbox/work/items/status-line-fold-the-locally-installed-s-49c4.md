---
id: status-line-fold-the-locally-installed-s-49c4
title: "status line: fold the locally installed status line into the plugins repo"
type: feature
status: done
priority: 2
created: 2026-09-17
updated: 2026-09-19
closed: 2026-09-19
refs:
  - operator message 2026-09-17
---

Operator 2026-09-17: the status line appears to be installed only locally, not delivered through the claude-plugins marketplace. Fold it into the repo so installing the plugin gives the status line. Investigate first: what settings.json statusLine points at on this machine and on the operator's host, whether that path is inside a plugin cache/data dir or a hand-copied local file, and how it differs from the repo's statusline.py.

## Handoff
- doing: investigated in this sandbox: already plugin-delivered here
- next: operator confirms statusLine path in the config dir where it looked local (test scenario 2); likely covered by the factoring merge
- blocked: operator check during the factoring manual test
- learned: —

## Findings (librarian, 2026-09-17)
- In this sandbox (config dir /home/rt/.claude) the statusLine is NOT local: settings.json runs
  plugins/data/claude-kit-kmacmcfarlane/current-hooks/statusline.py, a symlink into the marketplace cache
  (claude-kit 27282f3), i.e. the repo's plugins/claude-kit/hooks/statusline.py delivered by the plugin.
- The operator's other config dir (the other project's CLAUDE_CONFIG_DIR) was seen earlier with its own
  context-gate state; its statusLine entry has not been inspected (read-only mount from this sandbox).
- The plugin-factoring branch moves the status line into context-guard, whose SessionStart hook migrates or
  restores the statusLine entry and keeps it on a stable data-dir symlink. That branch is under manual test now.
- Likely outcome: resolved by the factoring merge for every config dir that installs context-guard; the
  remaining gap is any config dir whose statusLine points at a hand-copied path. Next: operator reports what
  statusLine shows in the config dir where they saw it (test scenario 2), then either close as covered by 9b93
  or scope a migration for hand-copied paths.

## Notes
- 2026-09-19 done: superseded: the statusline plugin (3c48) installs itself and takes over hand-copied/predecessor entries
