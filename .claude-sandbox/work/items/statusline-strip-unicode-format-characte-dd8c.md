---
id: statusline-strip-unicode-format-characte-dd8c
title: "statusline: strip Unicode format characters from session names; cap by column width"
type: chore
status: todo
priority: 4
created: 2026-09-16
updated: 2026-09-16
refs:
  - reviewer report, item statusline-session-name-does-not-always-7942
---

From the 7942 re-review 2026-09-16: clean() lets Cf characters through (bidi override U+202E can visually reverse the row; zero-width chars pad invisibly; a name that is only U+202E counts as non-empty and shadows the payload); the 60-char cap counts code points so 60 CJK/emoji take ~120 columns. Acceptance: add \u200b-\u200f \u202a-\u202e \u2060-\u2064 \u2066-\u2069 \ufeff to _UNSAFE (keep combining marks and ZWJ-in-emoji working — test an emoji ZWJ sequence still renders); cap by east_asian_width column count; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
