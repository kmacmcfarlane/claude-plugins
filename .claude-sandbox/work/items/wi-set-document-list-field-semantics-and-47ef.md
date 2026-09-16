---
id: wi-set-document-list-field-semantics-and-47ef
title: "wi set: document list-field semantics and validate deps/parent targets"
type: feature
status: done
priority: 3
tags: [work-items]
created: 2026-09-08
updated: 2026-09-08
closed: 2026-09-08
refs:
  - claude-sandbox librarian session, 2026-09-08; their spike set-list-into-work-items-79ef
---

Peer request (claude-sandbox librarian, 2026-09-08): wi set <id> tags|deps|refs a,b exists (cmd_set, LIST_FIELDS) but is undocumented in SKILL.md's verb table and references/format.md; and unlike wi add --dep / wi block --on, cmd_set does not validate that deps or parent targets resolve — a dangling id only surfaces at wi lint. Do: (1) document set in the verb table and format.md — replace semantics for list fields, --clear if it exists (verify against cmd_set first, describe reality); (2) make cmd_set validate deps/parent like add does: reject dangling ids, allow ext: refs, honour --force; exit codes per the existing convention (note provider-interface.md documents schema-validation exiting 3). Tests for both. Not urgent.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: 7933fd4 merged to local main; review CLEAR round 2

## Review
- Round 1 (c8cef8d): NEEDS_CHANGES — 2 medium (Editing-fields section swallowed format.md's
  "## Body sections" heading; self-dep/self-parent accepted, surfacing only at lint — the
  class this item exists to close), 1 low (quoting wording on --clear). Behavioral claims
  otherwise verified live incl. archive resolution, byte-identical rejection, ext: handling.
- Round 2 (e566aa9): CLEAR — heading parity re-verified against main; self-references exit 1
  before the force-guarded branch, --force never bypasses, files byte-identical on rejection;
  49 tests OK. 1 nit accepted (verb-table row omits the self-reference exception; format.md
  carries it). Pre-existing out of scope: set priority notanumber tracebacks (also on main).
- Requester note: no --clear flag exists; "" or — clears (documented reality per the
  provider-interface rule). provider-interface.md absent on main; nothing to update there.
