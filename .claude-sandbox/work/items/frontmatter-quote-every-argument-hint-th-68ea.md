---
id: frontmatter-quote-every-argument-hint-th-68ea
title: "frontmatter: quote every argument-hint (three break strict YAML parsers) + add a strict-parse lint"
type: bug
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-21T18:01Z
created: 2026-09-20
updated: 2026-09-21
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

## Dispatch
- dispatch: implementer opus — >3 files across several plugins; adds a lint (executable snippet)
