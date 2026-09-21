---
id: wi-body-edits-whitespace-only-body-headi-23a8
title: "wi body edits: whitespace-only body heading, fenced headings, newline in --doing, import --update coverage"
type: chore
status: done
priority: 4
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
---

From the e832 review (2026-09-19), all low/nit, no data loss: (1) _append_section glues '## Notes' onto a whitespace-only body with no trailing newline (wi.py:348); (2) a fenced '## Handoff' inside Notes makes later notes land inside the fence (section scan ignores fences); (3) --doing/--next values with a newline leave unowned lines or inject headings — reject or escape newlines; (4) no test covers newline='' on the write side; (5) import --update not in the preservation matrix.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009
- 2026-09-21 done: 421baaf

## Dispatch
- dispatch: implementer opus — executable logic (wi.py)

## Implementer result
- round 1 DONE_WITH_CONCERNS 0ca993e (opus): fence-aware headings (CommonMark), heading on own line after whitespace-only body, handoff values reject line breaks (exit 1, unwritten), CRLF write-side test, import --update in matrix. 5 suites green; revert-to-verify 26 failures. Concern: §2 dot-slash lint FAIL is the pre-existing ./.work/ prose (item 34a2).
- implementer open (not in scope): done --note / block reason / import-todo may carry line breaks too; fenced `- doing:` bullets inside Handoff still owned.
- held: operator paused 2026-09-19; next is reviewer opus.
- dispatch: reviewer opus — rule 4 (impl opus)

## Review round 1 — NEEDS_CHANGES (opus) at 0ca993e
- [high] _heading_flags: an unclosed fence hides the real ## Handoff after it; each handoff then appends another Handoff block (5 after 4 calls), show reports empty values, lint fails. Fix: an opener with no matching closer is not a fence (re-scan); test + format.md sentence.
- [medium] pre-existing: block reason, set values, done/drop --note, import-todo titles accept line breaks → front-matter injection (item becomes unloadable) or a heading that hijacks Handoff. Folded into this round (same file, same one-line guard) rather than a follow-up.
- [low] test helper owned_handoff_lines has a simpler fence scanner than production; [nit] format.md:136 long line.
- Live-store equivalence held: 10 sampled items byte-identical under base and head; no live item contains a fence.
- dispatch: implementer opus — fix round 1 (resume, same tier)
- round 1 fix f38ef29: unclosed opener is plain text; one-line guard on handoff/block/set/note/add; helper uses _heading_flags. Open: backlog-yaml import multi-line values.
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — NEEDS_CHANGES (opus) at f38ef29
- round-1 high fixed; live-copy equivalence holds on all 125 items.
- [medium] unclosed opener still pairs with a LATER section's bare fence (CommonMark rule) → real ## Handoff hidden → duplicate Handoff (stops at 2). Fix: safety net in set_handoff/append_note — no section found but a column-0 `## Handoff`/`## Notes` line inside a fence → exit non-zero, never append a duplicate; test.
- [medium] one-line guard is per command; misses claim --as, next --claim, add --tag/--dep/--parent/--ref/--slug, unblock --dep, import. Fix: guard once at the writer (_emit_scalar/emit_front or pre-save): reject \n/\r in any front-matter value, exit 1, write nothing.
- [high, pre-existing on main] import --format backlog-yaml copies multi-line YAML (review_feedback: |, titles, blocked_reason) into front matter → whole store unreadable (next/ls/lint exit 3). The writer-level guard covers it if import folds or rejects such values — folded into this round.
- [nit] lookahead O(n^2) in unclosed openers.
- dispatch: implementer opus — fix round 2 (resume, same tier)
- round 2 fix 0e1593d: set_handoff/append_note refuse (exit 3) when the section is only inside a fence; one-line check at emit_front for every front-matter value, whole batch renders before any write; import folds multi-line values (notes excepted); linear fence scan. 96 tests; all 133 live items render unchanged in memory.
- dispatch: reviewer opus — round 3 (resume)

## Review round 3 — NEEDS_CHANGES (opus) at 0e1593d
- all round-2 findings fixed; live-copy equivalence on all 125 items; import folding verified; fence scan 6.1s → 0.005s.
- [medium] refusal fires on a CLOSED fenced example containing ## Notes/## Handoff with no real section (misleading message). Fix: refuse only when the hiding fence also contains a later column-0 ## line; message names both fixes; test.
- [low, pre-existing] import notes: | containing ## Handoff shadows the imported Handoff — follow-up item or format.md line.
- dispatch: implementer opus — fix round 3 after a high (round 2): fable signal; fable unavailable (unknown); fallback. Review round 4 is the last before the cap.

## Review round 4 — CLEAR (opus) at 40340fb
- live-copy equivalence on all 135 items; e832 invariant held every round. lows accepted: a closed example with ## Notes + another ## in the same fence still refuses (message gives a working fix); unclosed-fence leftovers render like CommonMark, no bytes lost.
## Landed
- 421baaf. 3 fix rounds (round 3 fable-signal on opus fallback).
