---
id: context-guard-lineage-read-adoption-by-c-87fd
title: "context-guard lineage: Read adoption by content match; reject empty session id"
type: chore
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5126 review r2
---

From 5126 review r2 (CLEAR), 2026-09-22: (1) lineage.py adopts by sha of the file at hook time, not the Read's content — when tool_response.type=='text', numLines==totalLines and no truncatedByTokenCap, adopt only if content matches the file on disk (trailing newlines ignored); else (incl. file_unchanged) keep today's behaviour; (2) mark_checkpoint.py: reject an empty $CLAUDE_CODE_SESSION_ID before the state lookup (today maps to unknown.json).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (9b5d12b2); context-guard hooks lineage.py, mark_checkpoint.py + tests
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — Read adoption by content; reject empty session id
agent: implementer a10af6552cb6da062 round 1
result: BLOCKED part 1, DONE part 2 at 18603610 (empty session id refused; 732 OK). Part 1 needs Read response field names that appear nowhere in repo code/tests or the public hooks docs; their only source is this item's own text, written at 5126 review r2 from an internals read (the log entry was scrubbed in e7029c03, the item text was not)
decision 215: How should the Read-adoption half of this item proceed, given its field names have no observed or documented source? — options: (a) observe them: with the operator present, capture one real Read hook input on a public release and label it (version, how), then build as specified [recommended] | (b) build a weaker rule now: adopt only when the Read's response text contains the file's content, treating the response as opaque | (c) drop part 1, land only the empty-id fix | (z) decide later: part 2 can land alone meanwhile
dispatch: reviewer opus high — fresh (rule 4), part 2 only
agent: reviewer ad92b363a1ed6b7c4 round 1 at 18603610
verdict: CLEAR round 1 at 18603610, part 2 (lows: docs and docstring miss the refusal; test misses the --from form; nit comment; turn_gate.py --checkpointing has the same empty-id hole)
decided: 2026-10-13T22:27Z cap — lows and nit with exact wording, plus the turn_gate hole (same rule, exact fix given): one finish round, read by the librarian (authority answer 145)
dispatch: implementer opus medium — resume, finish round (part 2)
agent: implementer a10af6552cb6da062 round 2 (finish)
result: DONE finish at 068e7e5e (all six exact; diff read by the librarian; 733 OK)
verdict: CLEAR part 2 after 1 finish at 068e7e5e; part 1 open on decision 215
