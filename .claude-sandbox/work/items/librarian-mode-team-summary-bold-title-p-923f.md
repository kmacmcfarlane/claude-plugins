---
id: librarian-mode-team-summary-bold-title-p-923f
title: "librarian-mode team summary: bold title plus one bullet per change area, no tables, sub-bullets or file lists"
type: feature
status: doing
priority: 0
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-23T17:50Z
created: 2026-09-23
updated: 2026-09-23
refs:
  - operator 2026-09-23 via marketplace - librarian (90c1)
---

Operator request 2026-09-23, relayed by marketplace - librarian (their item 90c1, confirmed in their conversation) and announced by the operator here ('incoming request I want you to work and land right away'). New shape for references/team-summary.md: (1) a header line naming the plugin, the date, the commit range and 'update your plugins to pick it up', with one short line under it saying everything was reviewed before it merged; (2) each change area as a bold title on its own line with exactly ONE bullet beneath it, one sentence (two at most) saying what changed for the reader; (3) no tables, no sub-bullets, no lists of files or commit shas under each item. The operator felt the fuller multi-line bullet version was too detailed for a team update. The approved example (abridged): '**kappa-dev plugin update, 2026-09-23 (marketplace cbd386d..91a38e8)**' / 'Update your plugins to pick it up. Every change was reviewed before it merged.' / '**Comment review is back**' / '- kappa-code-review reviews the comments in a diff against the kappa-conventions comment rules, and kappa-jira-implement tidies comments before deploy (Step 10a).' / '**Consent enforced on every outward write**' / '- 13 places in kappa-dev skills that wrote to Jira, GitLab or a shared environment without asking now ask first.' Acceptance: team-summary.md specifies this shape, with a generic example (no employer content); every pointer to it (librarian-mode SKILL.md § Report, dev-cycle bindings § Landing) stays consistent.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-23 claimed by Kyle-McFarlane@bf9f9839222c

target: full librarian-mode-team-summary-bold-title-p-923f /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-team-summary-bold-title-p-923f
dispatch: implementer sonnet — doc-only (librarian-mode references/team-summary.md, plus any pointer text); reviewer opus
agent: implementer a9f1423ec295e9095 round 1
return: implementer DONE da1b6d3 (team-summary.md shape and example rewritten; SKILL.md § Report pointer updated; the other five pointers were generic and needed no change; checks OK)
dispatch: reviewer opus — floor opus (doc-only)
agent: reviewer a53754f002de0a934 round 1
verdict: NEEDS_CHANGES round 1 at da1b6d3 (4 medium, all one-clause edits in team-summary.md: the Push: none range; repo vs plugin header; the WHAT-only test restored; example mislabels a context-guard change as dev-flow; 3 low)
dispatch: implementer sonnet — resume, fix round 1 (bindings.md:278 added to scope for the "maintenance bullet" low)
agent: implementer a9f1423ec295e9095 round 2
