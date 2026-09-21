---
id: dot-slash-lint-three-standing-fails-are-34a2
title: "dot-slash lint: three standing FAILs are sibling-repo/store paths, not skill references"
type: chore
status: doing
priority: 4
owner: unknown@360f41058e92
claimed: 2026-09-21T18:37Z
created: 2026-09-19
updated: 2026-09-21
---

From 07c3 F0/F1 (2026-09-19): review-checklist §2's dot-slash grep FAILs on kit-dev/new-project-from-template SKILL.md:21 ("../claude-templates"), kit-dev/update-kit references/repo-map.md (../claude-* sibling repos), work-items SKILL.md:55 + references (./.work/). They are real paths to sibling repos and the store, not skill references. Either teach the grep to ignore paths that are not references/ paths, or reword the three skills. Goal: a full-repo lint run is clean.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — lint snippet (executable) + 3 skills

## Implementer result
- round 1 DONE fe66ebf (opus): §2 grep flags only reference-shaped ./ ../ paths (into references/scripts/assets or a .md) + the skill-dir variable; work-items ./.work/ → .work/; sibling-repo paths in kit-dev left (real commands). All 19 skills clean; fixture with real references FAILs.
- decision (librarian): narrowing the lint supersedes bc3e's "reword, do not narrow" — this item's acceptance allowed it, and the old grep flagged real sibling-repo commands.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at fe66ebf
- all 19 skills clean under GNU grep and ugrep; false-positive fixture passes.
- [medium] .md branch allows at most one dir: ../../dev-flow/skills/dev-cycle/SKILL.md now passes (coverage loss). Fix ([A-Za-z0-9_.-]+/)* + prose l.154.
- [low] grep exit 2 (bad pattern) silently passes — note or guard.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix dd72b99: any depth before .md; rc guard FAILs when grep cannot run.
- dispatch: reviewer opus — round 2 (resume)
