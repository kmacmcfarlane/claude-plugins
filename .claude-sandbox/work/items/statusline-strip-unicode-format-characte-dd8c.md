---
id: statusline-strip-unicode-format-characte-dd8c
title: "statusline: strip Unicode format characters from session names; cap by column width"
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-18
closed: 2026-09-18
refs:
  - reviewer report, item statusline-session-name-does-not-always-7942
---

From the 7942 re-review 2026-09-16: clean() lets Cf characters through (bidi override U+202E can visually reverse the row; zero-width chars pad invisibly; a name that is only U+202E counts as non-empty and shadows the payload); the 60-char cap counts code points so 60 CJK/emoji take ~120 columns. Acceptance: add \u200b-\u200f \u202a-\u202e \u2060-\u2064 \u2066-\u2069 \ufeff to _UNSAFE (keep combining marks and ZWJ-in-emoji working — test an emoji ZWJ sequence still renders); cap by east_asian_width column count; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic (status line)

impl: DONE 4856907 (Cf stripped wholesale, ZWJ kept between visible non-ASCII, tag chars kept, columns() cap, lone surrogates stripped, SCAN_MAX backstop; 25 new tests)
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (FE0F emoji presentation counted 1 col), 2 (tag run after flag unbounded); lows 3 (ZWJ after combining marks), 4 (SCAN_MAX all-Cf hides later name), 5 (main() still raises on surrogate cwd/model or non-dict payload — librarian pulls into this item: file in scope, never-raise rule), 6 (fix: verb; not fixable without history rewrite — new commits use fixed:).
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 17dbd2e (all fixed; declined 6 = history rewrite; also rewrote raw invisible chars in the test source as escapes; last-resort guard on main()).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Lows carried to 81a5 (same file): non-numeric used_percentage blanks the whole line via the last-resort guard; SCAN_HARD-padded name shows a spurious ellipsis (documented). Declined: 6 (fix: subject, no history rewrite).
- 2026-09-18 done: 151c7f5
