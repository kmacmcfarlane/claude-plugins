---
id: wi-body-edits-whitespace-only-body-headi-23a8
title: "wi body edits: whitespace-only body heading, fenced headings, newline in --doing, import --update coverage"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T05:58Z
created: 2026-09-19
updated: 2026-09-19
---

From the e832 review (2026-09-19), all low/nit, no data loss: (1) _append_section glues '## Notes' onto a whitespace-only body with no trailing newline (wi.py:348); (2) a fenced '## Handoff' inside Notes makes later notes land inside the fence (section scan ignores fences); (3) --doing/--next values with a newline leave unowned lines or inject headings — reject or escape newlines; (4) no test covers newline='' on the write side; (5) import --update not in the preservation matrix.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

## Dispatch
- dispatch: implementer opus — executable logic (wi.py)

## Implementer result
- round 1 DONE_WITH_CONCERNS 0ca993e (opus): fence-aware headings (CommonMark), heading on own line after whitespace-only body, handoff values reject line breaks (exit 1, unwritten), CRLF write-side test, import --update in matrix. 5 suites green; revert-to-verify 26 failures. Concern: §2 dot-slash lint FAIL is the pre-existing ./.work/ prose (item 34a2).
- implementer open (not in scope): done --note / block reason / import-todo may carry line breaks too; fenced `- doing:` bullets inside Handoff still owned.
- held: operator paused 2026-09-19; next is reviewer opus.
- dispatch: reviewer opus — rule 4 (impl opus)
