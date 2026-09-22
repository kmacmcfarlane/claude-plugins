---
id: review-checklist-2-agent-brief-only-name-2edb
title: "review-checklist §2 + agent-brief: only name and description are required frontmatter keys"
type: chore
status: done
priority: 2
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - peer marketplace - librarian (219.sock), operator words relayed
---

Relayed 2026-09-22 by peer 'marketplace - librarian', quoting the operator's ruling in that repo: disable-model-invocation, allowed-tools and argument-hint are optional; their absence is desired (invocable, free-form args, unrestricted tools). dev-cycle references/review-checklist.md § 2 requires five keys and agent-brief.md repeats it as reject-on-sight; 72 of 75 skills in that repo fail it. Acceptance: required set = name, description; keep the closed allowed-key list (unknown keys still fail); both files move together; check README doctrine and kit-dev create-skill for the same five-key rule.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
answer 58: (a) confirmed (operator 2026-09-22)

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — two plugins (dev-flow dev-cycle references, kit-dev create-skill) + doctrine (house frontmatter rule)
impl r0 DONE 246e529 (opus): review-checklist §2 requires name+description only (closed 20-key list kept); agent-brief reject-on-sight rule relaxed; create-skill SKILL.md + frontmatter-reference.md mark the three keys optional (absence = desired default). §2 over all 22 skills: 0 FAIL before/after; synthetic two-key skill passes, unknown key still fails. README/CLAUDE.md do not state the rule.
dispatch: reviewer opus — rule 4
review r1 (opus) at 246e529: CLEAR. Mutation tests: two-key skill passes; missing name/description, unknown key, "Model", duplicate, angle brackets, 1100-char description all FAIL; §2 over all 22 skills 0 FAIL. Lows: review-checklist.md:75 "Quote argument-hint always" → "whenever it is present"; create-skill template example `disable-model-invocation: true` could be copy-pasted; agent-brief.md:72 rewrap. Filed as a follow-up.
Review result: 1 round, 0 fix rounds; impl opus, review opus. Land checks (librarian): seven suites OK; diff read — 4 files in scope.
- 2026-09-22 done: 2675024
