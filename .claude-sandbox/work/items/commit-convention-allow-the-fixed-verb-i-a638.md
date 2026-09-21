---
id: commit-convention-allow-the-fixed-verb-i-a638
title: "commit convention: allow the fixed: verb in agent-brief and review guidance"
type: chore
status: done
priority: 4
created: 2026-09-18
updated: 2026-09-21
closed: 2026-09-21
---

From the d72e review (2026-09-18): agent-brief.md's Commit section allows added/updated/removed/bumped, but main's history uses fixed: 19+ times and librarian briefs today allow it. Decide and align agent-brief, review-brief and any CLAUDE.md/README convention text. Lands after 07c3 F1/F2 (agent-brief moves to dev-cycle).

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 03d46d1

## Dispatch
- dispatch: implementer sonnet — default (verb list in briefs). decision (librarian): allow fixed: — main's history uses it 19+ times and a commit-subject finding is low anyway

## Implementer result
- round 1 DONE 35f2552 (sonnet): fixed added to the verb lists in dev-cycle agent-brief and implement SKILL.md (the only two enumerations).
- dispatch: reviewer opus — rule 4 floor

## Review round 1 — CLEAR (opus) at 35f2552
- only two enumerations exist; no commit-msg validator anywhere; other fixed prefixes (docs:, chore:, merge:) are per-flow, not lists. History: 41 fixed:. nit: agent-brief:117 97 chars.
## Landed
- 03d46d1.
