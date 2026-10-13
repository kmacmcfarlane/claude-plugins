---
id: librarian-mode-a-manifest-pinned-cached-20fb
title: "librarian-mode: a manifest-pinned cached wi copy can lag the store format at intake"
short_display_name: stale cached wi at intake
type: bug
status: todo
priority: 3
created: 2026-10-02
updated: 2026-10-02
refs:
  - peer brainboy 2026-10-02
---

Peer brainboy 2026-10-02: its manifest pinned a cached wi copy that lacked --short-display-name, so filing failed on the first try. librarian-mode Intake step 1 handles an exit 2 by filing without the flag, but the real fix is likely Rehydrate step 1 / troubleshooting.md: prefer the newest installed wi, or warn when the pinned copy is older than the plugin's. Acceptance: a librarian in a repo without the plugin resolves a wi that supports the current flags, or is told once which copy it uses and why.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
