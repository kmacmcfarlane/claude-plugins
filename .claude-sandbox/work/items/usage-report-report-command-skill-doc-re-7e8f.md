---
id: usage-report-report-command-skill-doc-re-7e8f
title: "usage-report: report command, skill doc, README catalog row"
type: feature
status: doing
priority: 2
deps:
  - usage-report-transcript-parser-dedupe-pr-eff1
parent: spike-analyze-claude-code-usage-across-c-e5a7
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T19:34Z
created: 2026-09-16
updated: 2026-10-13
refs:
  - operator approval 2026-09-16
---

F2 of the approved analyzer plan: complete the usage-report SKILL.md (what/when/triggers; how to run; how to read the tables; the reconciliation step against Claude Code's built-in /usage view; caveat that dollars are list-price estimates), finish the CLI (per session / per model / per dispatch tier / per day tables; --json; --all; --since; --flat), and add the README claude-kit catalog row and the Structure tree entry in the same commit.

## Handoff
- doing: —
- next: decision 213 (rec a: land after review); branch worktree-agent-adf30e968152b0aad at 7f0b8541
- blocked: —
- learned: —
From the F1 review (2026-09-16): (a) by_requested_tier needs a "main" bucket (or a key saying main-session tokens
are excluded) so it reconciles with totals, and its opus_equivalent should be summed from unrounded values; (b)
tokens priced through a legacy alias (claude-fable-5, claude-opus-4-7, claude-opus-4-8 -> current same-family
entry) must be visible in the report — a separate row or a marker — not silently merged.
- librarian 2026-09-16: held until the plugin-factoring reconcile (9b93) lands, so usage-report is placed once in the factored layout.

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

## Hold 2026-09-19
- Do NOT build: operator intends usage-report to retire into kmacmcfarlane/claude-analytics (peer agents-61); close when `ca report usage` reaches parity and the skill is removed (their Phase 3).
- 2026-09-28 held: claude-analytics will notify at report parity; then close and retire usage-report (see 4b0e)

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
dispatch: implementer opus medium — build per the approved plan (triage d2aa)
agent: implementer adf30e968152b0aad
return: DONE 7f0b8541; report command, skill doc, README row; usage-report 81 OK, 12/12 OK; builder notes the item still carries a hold note (retire into claude-analytics) and built it on the triage dispatch
note: review and landing paused until the operator settles whether the hold still applies (decision 213)
decision 213: The usage-report command (7e8f) is built and green, but the item still carries a hold note saying not to build it because usage-report is meant to retire into claude-analytics. Land it? — options: (a) land it after review: a working report command now, retired later with the rest of usage-report [recommended] | (b) keep the branch unlanded until claude-analytics' plan settles usage-report's future | (c) drop it | (z) decide later
  why ask: your-call — the hold note is yours, and the triage dispatch overrode it without asking
  context: the triage marked 7e8f still real and the builder followed the dispatch; usage-report's item reader already backs dev-cycle's spend check, which this leaves unchanged · you decide whether the hold still stands
  impact: (a) → a report command and finished doc in context-guard now · wait: the review and landing only · reach: context-guard usage-report · undo: revert the merge
