---
id: handoff-h5-a-linked-clear-successor-gets-019c
title: "handoff H5: a linked /clear successor gets the manifest plus the predecessor's ledger digest"
type: feature
status: doing
priority: 1
deps:
  - handoff-h2-ledger-digest-keeps-reasoning-d0eb
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
---

Per decision 60. Builds on F3a's lineage link (landed 4ca4646); covers item 44a4 if still open. Opus/opus. Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — context-guard hook logic
impl r0 DONE_WITH_CONCERNS 7191232 (opus): linked /clear (F3a link to a predecessor owning the pinned version) → full manifest + predecessor ledger.digest with a labelled block; unlinked/foreign/changed keep header; successor ledger title '# ledger <sid> (successor of <pred>)' written first; flock on ledger writes (SessionStart hooks run concurrently); CAP asserted; 13 tests (6 fail on main); docs. Not done: compact_summary pop (not in acceptance). 44a4: covered for the linked case — close with H5.
librarian on OQ: a LANDED manifest on a linked /clear stays header-only (land = shed the thread; the land path is 'finish, then /clear') — accepted as designed.
dispatch: reviewer opus — hook logic (re-injection); new flock on ledger writes
review r1 (opus) at 7191232: NEEDS_CHANGES. No path gives a successor a manifest its predecessor did not own at the pin; CAP holds at extremes (8,775/9,000); title rewrite keeps every line.
- [medium] ledger.py:15-24 — flock with no timeout (blocked 3.00 s behind a holder); repo convention is LOCK_NB + bounded retry, then proceed unlocked (lib_context._acquire). Pass: bounded loop + a test.
- [medium] rehydrate.py:828-830 — systemMessage claims "and the ledger digest of predecessor X" even when the digest is empty. Pass: compute first; clause only when non-empty; test.
- [medium] plan § H5 bullet 3 (pop compact_summary after the one full injection) not implemented. librarian: implement it (it is in the plan section the acceptance names).
- lows: successor title should add "by /clear; its ledger: <path>" (two-hop chains); playbook line omits the link conditions; no flock tests (concurrent writer, no-fcntl fallback).
- forecast: textual conflicts with H3 (tier docstring, SKILL.md Step 5, handoff-format tiers) and H6 (next to clear_pred/reads_new); the linked tier should wrap the trimmed body in annotate_holds once H3 lands.
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE 9ded9c0 (opus): bounded ledger lock (LOCK_NB until L.LOCK_TIMEOUT_S, then unlocked); append checks size under the lock (no double title) and successor_title replaces a plain title; digest computed first, message names the predecessor only when injected; compact_summary popped after its one use (a newer one kept); playbook link conditions; new tests fail/hang on 7191232. (a) declined — the acceptance fixes the title text and the path follows from the sid (accepted).
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at 9ded9c0: CLEAR — lock waits ≤0.2 s; honest message; CAP 8,775/9,000; stale/hostile/foreign cases get the header; compact_summary pop cannot lose a needed summary. Lows: unlocked after timeout → rare duplicate title (digest skips it) / microsecond lost-line window in successor_title (skip the rewrite when _lock returns False); no-fcntl systems race the epoch header.
land (librarian): merge-tree conflicts with main in hooks/rehydrate.py (H6 b6de landed ae7ea81 — reads_new next to clear_pred, write_back). Not merged. Conflict round → implementer merges main; reviewer verifies the resolution. Also fold in the lows if cheap: successor_title skips its rewrite when _lock returns False.
dispatch: implementer opus — conflict round (resume)
conflict round DONE 8ca085d (merge of main) + e24ca1f: both sides kept in rehydrate.py; a linked /clear records the read list (tests); successor_title skips its rewrite only on a lock timeout (None when no lock is possible still writes).
dispatch: reviewer opus — resolution + e24ca1f verify (resume)
