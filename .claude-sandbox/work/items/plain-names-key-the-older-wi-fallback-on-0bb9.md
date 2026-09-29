---
id: plain-names-key-the-older-wi-fallback-on-0bb9
title: "plain names: key the older-wi fallback on the 'unrecognized arguments' message, not any exit 2"
short_display_name: older-wi fallback wording
type: chore
status: todo
priority: 3
created: 2026-09-29
updated: 2026-09-29
refs:
  - 8e04
---

From 8e04 review r2 2026-09-29: librarian-mode SKILL.md:146-147 and dev-cycle SKILL.md:96-98 say an exit 2 naming --short-display-name means an older wi, but the current wi's argparse errors (a bad -t/-p value, a name starting with '-') also exit 2 and show the flag in the usage block; an agent would drop the flag and file without a stored name. Acceptance: the rule reads 'an exit 2 whose error reads unrecognized arguments: --short-display-name means an older wi', in both places.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
