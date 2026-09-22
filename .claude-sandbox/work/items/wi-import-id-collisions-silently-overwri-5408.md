---
id: wi-import-id-collisions-silently-overwri-5408
title: "wi import: id collisions silently overwrite an item (data loss)"
type: bug
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T00:14Z
created: 2026-09-21
updated: 2026-09-22
refs:
  - 370b reviewer
---

Found by the 370b reviewer 2026-09-21 (pre-existing): make_id uses a 4-hex random suffix; a fresh import of many items whose titles slug alike (e.g. ~44 titles → item-…) can generate the same id twice, and the second write silently replaces the first — one fuzz run lost an item. Acceptance: id generation never returns an id already in the store or earlier in the same batch (check + retry, or widen on collision); import/add refuse to overwrite an existing file they did not read; test forcing a collision (patched RNG) shows both items survive.

## Handoff
- doing: review r1 dispatched (opus)
- next: CLEAR → land
- blocked: —
- learned: —

## Carried in (librarian)
- from 370b review: _story_value — a blocked_reason empty after strip() imports as no value (as a padded — does); test.
- dispatch: implementer opus — wi.py data-loss fix

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

## Implementer result
- round 1 DONE 764672e (opus): make_id retries against taken_ids (store + archive + batch), exits 3 after 1024 draws; save_items refuses a new item over an existing/archived/duplicate path; atomic_write create=True via hard link (O_EXCL fallback); archive checks destinations first; blank blocked_reason → no value. 6 tests (44 same-title import lost 29 on main).
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at 764672e
- main fix holds (4×30 concurrent adds, tight id space exit 3, archive refusal, updates overwrite own file); merge-tree clean.
- [high] _link_no_clobber fallback (no hard links): O_EXCL empty file then in-place copy → ENOSPC/kill leaves an empty/half file and every wi command exits 3; raw OSError; same for archive. Fix: reserve with O_EXCL, then os.replace over our own reservation; on error remove the reservation if ours and empty, raise WiError.
- [medium] no test forces the fallback (success + failure paths).
- lows: add-retry test passes on main (use a stray file whose name ≠ its id); update test errors on main only via _id_suffix; docstring width.
- open questions: blank blocked_reason → lint catches (keep); non-atomic fallback → fix (high).
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE 22529af (opus): _move_no_clobber — hard link+unlink, else O_EXCL reserve + os.replace over own reservation, cleanup if ours, WiError 3; 4 fallback tests (EPERM) + stray-file test; tests independent of _id_suffix.
- dispatch: reviewer opus — review r2 (same reviewer resumed)
