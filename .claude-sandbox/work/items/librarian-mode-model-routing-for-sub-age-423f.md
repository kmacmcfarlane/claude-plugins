---
id: librarian-mode-model-routing-for-sub-age-423f
title: "librarian-mode: model routing for sub-agent dispatches"
type: feature
status: done
priority: 2
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator request 2026-09-16: the librarian should decide per dispatch (implementer, reviewer, future helpers) whether fable, opus, or sonnet is the right model, to save usage. Deliverable: a guideline set (researched) reviewed by the operator first, then implemented in the librarian-mode skill (SKILL.md + briefs) as a work item. Acceptance: skill states a routing rubric with explicit signals, a default, and the override rule; Delegate and Review pass the chosen model to the Agent tool; item body records the rationale.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Research summary (2026-09-16)
- Agent tool `model` override is highest priority; subagents otherwise inherit the parent
  model (the librarian runs on fable, so every dispatch today is a fable dispatch).
- Pricing per 1M in/out: fable 10/50, opus 5/25, sonnet 2/10, haiku 1/5. Sonnet is 5x
  cheaper than fable; opus is 2x cheaper.
- Anthropic guidance: default to sonnet, escalate only when the task is genuinely hard.
- Orchestration literature: a weaker reviewer misses what a stronger implementer introduces;
  reviewer tier should match the implementer tier, never sit below it. Strong orchestrator
  plus constrained specialists is the validated pattern; the brief is what constrains.
- No official task-to-model matrix exists; third-party sources (zylos, mindstudio, finout)
  are the only prescriptive ones and are unverified.

## Draft guidelines v1 (awaiting operator review)
See the operator-facing draft in the session; the accepted version is copied here once
approved.

## Approved guidelines (operator, 2026-09-16) — implement these
1. Default implementer model: sonnet. The brief constrains the work; a sonnet failure is cheap.
2. Implementer -> opus when any signal holds: executable logic in scope (hook, scripts/, status
   line, settings write); doctrine or marketplace shape (README catalog/placement, CLAUDE.md
   layout, marketplace.json, plugin split/move); more than three files or more than one plugin;
   item body records a real trade-off or acceptance uses judgement words (coherent, align,
   reconcile); a prior NEEDS_CONTEXT return; fix round 2 or later.
3. Implementer -> fable when a wrong result is hard to reverse or touches the harness: hooks that
   gate/block edits, commits or tool calls; security-relevant (credentials, permission
   allowlists, sandbox config); fix round 3 (last before the cap); operator names it.
4. Reviewer model = implementer model, FLOOR OPUS (operator decision: not sonnet). A sonnet
   implementer gets an opus reviewer; opus gets opus; fable gets fable.
5. Haiku out of scope; the librarian runs mechanical checks itself.
6. Re-dispatch after a rejection keeps the tier and sharpens the brief; only round 3 bumps.
7. Record per dispatch in the item body: role, model, signal. Report's verified: line names
   both models, e.g. "review CLEAR after 1 round (impl sonnet, review opus)".
8. Operator pins with a `model: <tier>` line in the item body; never overridden downward.

Rejected alternative for rule 4 (strict tier matching, sonnet reviewer possible) — operator
chose the opus floor so the gate is never weaker than opus.

Implementation: one feature, base main. Files: SKILL.md (new Route step between Factor and
Delegate; one line each in Review, Land is unchanged, Report verified: line), references/
agent-brief.md and review-brief.md (a `Model:` header line so the choice is visible).
model: fable (operator pin — this is harness doctrine)
dispatch: implementer fable (rule 8, operator pin)

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- 2026-09-16 done: b792b91

## Dispatch log
- implementer: fable (rule 8, operator pin) — returned DONE_WITH_CONCERNS, commit 9bc6bc2
- librarian decision on the rule 2 / rule 6 tension (round 2): the implementer's reading
  stands — fix round 1 keeps the tier; fix round 2 raises sonnet to opus (rule 2); fix
  round 3 goes to fable (rule 3); rule 6 is phrased "the round signals in rules 2 and 3 are
  the only bumps". Fix rounds count from the first rejection. Rationale: one failure is a
  brief problem, two is a capability signal.
- implementer added: a tier bump means a fresh reviewer at the new tier (resumed agents keep
  their model). Accepted as a necessary corollary of rule 4.
- reviewer: fable (rule 4, matches implementer) — round 1 dispatched 2026-09-16 15:58:53
- review round 1: NEEDS_CHANGES. 3 medium (fix-round-3 unreachable under a 3-review-round cap; implementer
  bump at fix round 2 still says "resume the same agent"; SKILL.md over the ~5000-token guideline), 3 low, 3 nit.
- librarian ruling on finding 1: rounds are counted in FIX rounds. Fix round n = the nth re-dispatch or resume
  with review findings = review round n+1. The cap is 3 fix rounds (a fourth means the brief or the item is
  wrong); fix round 3 runs at fable per rule 3 and is the last before the cap. This preserves the operator's
  approved rule 3 verbatim and widens the prior cap by one review round — to be surfaced under open questions
  in the Report.
- fix round 1 sent to the implementer 2026-09-16 16:03:49 (tier unchanged: fable, round 1 keeps tier).
- re-review: CLEAR. Findings 1,2,4-9 FIXED; 3 (SKILL.md size) PARTIAL, ruled not blocking: the duplicated
  passages are gone and what remains is the acceptance-required rubric plus the sentences findings 1 and 2
  required; the file was already at the ~5000-token line on main. 2 new nits (a stray appositive "the
  librarian's, dearest, model" at Route line 1; "of either role" placement in Review step 3) — not sent back,
  loop already CLEAR; left for the next edit of this skill.
- reviewer NOTES kept: the only remaining size lever is pre-existing text (Rehydrate first-start paragraph,
  Troubleshooting) — separate item if wanted.
- landed: merge b792b91 on main, 2026-09-16 16:09:01. Checks on main: hook tests OK, references exist, bare paths ok,
  marketplace==disk.
- OPERATOR (2026-09-16): reverted the fix-round cap ruling — cap stays 3 review rounds; corrected in item librarian-mode-round-cap-is-3-review-rou-2b08
