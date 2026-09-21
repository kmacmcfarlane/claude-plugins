---
id: frontmatter-quote-every-argument-hint-th-68ea
title: "frontmatter: quote every argument-hint (three break strict YAML parsers) + add a strict-parse lint"
type: bug
status: done
priority: 1
created: 2026-09-20
updated: 2026-09-21
closed: 2026-09-21
refs:
  - "peer: agent-harness-fc (uds 160.sock)"
---

Peer report 2026-09-20 from agent-harness-fc (their item quote-three-argument-hint-values-that-br-c476; evidence agent-harness .claude-sandbox/reports/pi-0.86.0-probes.md section P4). A value starting with '[' that contains a second '[...]' group parses as a flow sequence and then errors, so the WHOLE SKILL.md is rejected and the skill vanishes silently (pi 0.86.0's yaml loader: 16/19 skills loaded). REPRODUCED here with ruamel.yaml, independent of pi: hard PARSE-FAIL in context-guard/skills/checkpoint, dev-flow/skills/dev-cycle, statusline/skills/install-statusline; plus 8 more whose hint silently parses as a LIST, not a string (chat/product-research, dev-flow/chain-of-verification, dev-flow/librarian-mode, kit-dev/factor-analysis, ralph/backlog-grooming, ralph/backlog-yaml, sandbox/sandbox, work-items/work-items). Acceptance: double-quote argument-hint in every skill (house style already: update-kit writes it quoted), so each parses as a string; add a lint that parses each touched SKILL.md's frontmatter with a strict YAML parser and asserts argument-hint is a string - in the dev-cycle review-checklist hygiene section and create-skill's authoring rules; note the rule in the frontmatter reference. Careful: three of these files are also touched by in-flight branches (dev-cycle by fb09) - rebase or land order matters.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: f128089

## Dispatch
- dispatch: implementer opus — >3 files across several plugins; adds a lint (executable snippet)

## Implementer result
- round 1 DONE_WITH_CONCERNS 3ca1871 (opus): 18 hints quoted (text identical, checked by script), strict-YAML lint in dev-cycle review-checklist §2 (ruamel, PyYAML fallback, SKIP when neither), create-skill rule + reference. Lint on main: 3 parse FAIL + 8 list FAIL; branch: 0. Pre-existing dot-slash FAILs (34a2) only.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at 3ca1871
- hint text byte-identical for all 19; lint FAILs 11 on base, 0 on HEAD; SKIP path and PyYAML fallback verified; no body edits; merge-tree clean.
- [medium] librarian-mode's own review-checklist §2 and both agent briefs lack the rule. Resolution: librarian-mode's checklist and agent-brief become tombstones pointing at dev-cycle's in F2 (fb09), so 68ea lands AFTER F2 and the single copy carries the lint; the dev-cycle agent-brief "reject on sight" rule is added in this fix round.
- [low] review-checklist:178 — frontmatter without a closing --- passes silently: FAIL "frontmatter not closed".
- dispatch: implementer opus — fix round 1 (resume, same tier)
- round 1 fix aec45c8: agent-brief rule + "frontmatter not closed" FAIL; medium resolved by F2 tombstones (landed f39a146).
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — CLEAR (opus) at aec45c8
- medium resolved by F2 tombstones on main; lint fixtures all behave; [nit] empty frontmatter reports "not closed" (required-keys check catches it anyway).
## Landed
- f128089 (checks green; strict-YAML sweep on main: 0 failures). 1 fix round.
