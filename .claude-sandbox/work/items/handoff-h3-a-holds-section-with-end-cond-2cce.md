---
id: handoff-h3-a-holds-section-with-end-cond-2cce
title: "handoff H3: a ## Holds section with end conditions, in every injection tier, never trimmed"
type: feature
status: doing
priority: 1
deps:
  - handoff-h1-mark-checkpoint-stamps-writte-9852
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
---

Holds (e.g. no push until X, keep dispatch small until Y) get their own section with an end condition; shown in full, header-only and foreign-header tiers; librarian ending names holds. Opus/opus. Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

from H4 (a824) review, 2026-09-22 — H3 inputs: keep ## In flight and ## Copy forward out of the trim order (handoff-format note) and add a test pinning it; librarian-mode SKILL.md § Rehydrate step 3 resumes roster agent ids (from doing:/dispatch: lines) with SendMessage before any re-dispatch.
- from H4 r2 (low/nits): ending-the-session.md closing line should carry Step 7's Copy forward fact too (or point to Step 7); handoff-format 'survive the section trim'; checkpoint SKILL.md:131 reflow.

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — context-guard hook logic
impl r0 DONE 0124b9d (opus): ## Holds (HOLD what — why — until <decision N | event | UTC>) in handoff-format + Step 4b; holds on every owned header tier (≤8 lines/800 chars, sanitised), in place on full tiers, never on the foreign header; past UTC end → '[expired? confirm]'; trim rewritten to protect sections by name (Doing, Goal, Holds, In flight, Read in full, Copy forward never trimmed; order items: → Scrolls → Next (withheld line kept) → non-CORRECTION/REFUSED Aware-of → other); librarian ending-the-session Holds paragraph + Copy forward fact; SKILL.md § Rehydrate step 3 resume line; 11 tests (fail on main). Deviations: no owner field; REFUSED stays in Aware-of.
dispatch: reviewer opus — hook trim/injection logic
review r1 (opus) at 0124b9d: NEEDS_CHANGES. Seven Checks OK; header Holds ≤715 chars with 30 holds; foreign header holds-free on every source; expiry parser robust on garbage and far future.
- [high] rehydrate.py:509-513 — the final trim pass revisits already-collapsed Aware of / Next with keep=None, deleting CORRECTION/REFUSED and the Next-withheld line before an earlier extra section (repro: 3000-char Doing, 1500-char ## Context, budget 4400 → 3453 chars, Aware of wiped). Pass: exclude step sections from the final pass or keep their keep pattern; test with an early extra section.
- [medium] ending-the-session.md:20-27 — manifest Holds vs the store's hold items never connected; drift. Pass: Holds lines mirror the active hold items and their end conditions; the store wins.
- lows: a decision/event end clause mentioning a date reads as expired; _CTRL misses U+061C, U+FEFF, U+2060–2064; exact heading match misses '## Holds:'; the spec's template sentence injected as a hold; librarian examples not in HOLD shape; commit subject names only context-guard.
- H6 overlap forecast: merges cleanly; read_list._SECTION is a second parser for ## Read in full — reuse _sections after merge.
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE 3e31799 (opus): last trim pass skips Scrolls/Next/Aware of; a time must lead the end clause; _CTRL widened; headings match ':'/'(…)'; only HOLD lines read; librarian Holds mirror store hold items (store wins); 13 tests (4 new fail on 0124b9d). Slip: fail-first checkout wiped edits once; re-applied. (f) carried in the merge message.
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at 3e31799: NEEDS_CHANGES. Round-1 high and lows fixed (repro keeps CORRECTION/REFUSED at 3496 chars); trim order otherwise unchanged; CAP holds.
- [medium] rehydrate.py:463,475 — regression: _HEAD_TAIL.sub replaced .strip(), so CRLF headings keep '\r' → hold_lines [] (header tiers lose every hold) and no section is recognised as protected (Read in full trimmed, CORRECTION lost at budget 2000). Pass: strip the name; a CRLF test pinning protection and hold_lines.
- lows: 'until:' no longer parsed (a past date not flagged); _HOLD_RE case-sensitive / '**HOLD**' dropped silently.
dispatch: implementer opus — fix round 2 (resume)
fix r2 DONE 841a581 (opus): section names strip CRLF (before and after _HEAD_TAIL); annotate keeps \r; until: accepted; HOLD any case / bold; CRLF test pins recognition, hold_lines and stepped keeps; 3 tests fail on 3e31799 (committed first). OQ: a prose line starting 'hold' now reads as a hold — accepted (holds is its own section).
dispatch: reviewer opus — review r3 (resume)
review r3 (opus) at 841a581: CLEAR — LF, CRLF, mixed and tab/colon headings give identical sections and output; earlier repros hold; trim order unchanged. Low: handoff-format.md:95 "prose is never injected" slightly too strong + lines past the wrap.
Review result: 3 rounds, 2 fix rounds; impl opus, review opus.
land (librarian): merge-tree conflicts with main in librarian-mode references/ending-the-session.md (a934 c465325 + 25fa f4ee4ef rewrote the closing sequences). Not merged. Conflict round → implementer; fold in the r3 low.
dispatch: implementer opus — conflict round (resume)
conflict round DONE 3af254f (merge of main) + 2a3619a: 75%/DUE step 4 keeps all three — Report → push outcome + incoming: → team summary → checkpoint close → Step 7 opener last (roster ids, Copy forward, facts changed, Holds first); Holds paragraph and 25fa merge-through both stand; r3 low fixed. Librarian: the opener staying last is correct (checkpoint Step 7).
dispatch: reviewer opus — resolution verify (resume)
resolution verify (opus) at 2a3619a: CLEAR, no findings — all three changes kept in step 4, opener last; only H3's 6 files; 593 context-guard tests pass on the merged tree. Note for H6's owner: read_list._SECTION matches '## Read in full' exactly while _sections now accepts a suffixed heading.
Review result: 3 review rounds + resolution verify, 2 fix rounds + 1 conflict round; impl opus, review opus.
land (librarian): conflicts with main in hooks/rehydrate.py, checkpoint SKILL.md and handoff-format.md (H5 019c landed c8396a2 there). Not merged. Conflict round → implementer; the linked-clear full branch must wrap the body in annotate_holds (both reviewers flagged it).
dispatch: implementer opus — conflict round (resume)
