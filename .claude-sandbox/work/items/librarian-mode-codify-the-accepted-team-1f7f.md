---
id: librarian-mode-codify-the-accepted-team-1f7f
title: "librarian-mode: codify the accepted team-summary format in references/team-summary.md"
type: chore
status: done
priority: 1
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - peer marketplace - librarian (219.sock), operator words relayed; their item 1a39
---

Relayed 2026-09-22 by peer 'marketplace - librarian' (their item 1a39), quoting the operator: 'that format is good. codify the format in the librarian skill.' Amends what a934 landed (references/team-summary.md); the four-line Report is unchanged and this stays additive. SPEC, from three drafts each of whose corrections narrowed it: one bullet per landed change with a bold title and a short statement of WHAT, not a commit subject or item id; ONE sub-bullet, two at most; the sub-bullet describes WHAT ONLY — no why, no how, no mechanism, no rationale, no evidence (the constraint that does the work and the one a writer keeps breaking: draft two was rejected for carrying rationale); at most two short sentence fragments per line, semicolon-separated, not sentences; no table (copy-paste readability: tables break in Slack, Teams, email and on phones); ordered by what the READER feels, not commit order or priority; maintenance and plumbing collapsed into ONE bullet marked (maintenance); a header line giving where it landed and the action needed to pick it up; a closing line saying whether anything requires action on existing work. One summary per push covering everything in it, never one per item. The peer's own judgement, not the operator's: the commit range goes in the header, not per bullet. Acceptance: references/team-summary.md carries the spec AND a worked example (the shape is easier to copy than to describe — use the abridged one in the peer message, recorded in their 1a39); § Report's pointer unchanged in substance.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 67: confirm the team-summary format relayed by the sussex marketplace librarian in your words — one bullet per change with one what-only sub-bullet (at most two fragments, semicolon-separated), no table, reader-ordered, maintenance collapsed and marked, a header with where it landed and what to run, a closing line on action needed; one summary per push. (a) confirm and codify it in references/team-summary.md [recommended: your stated format, and a peer cannot authorize it]; (b) adjust it (say how); (c) leave the current wording.
answer 67: a (operator 2026-09-22)

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full librarian-mode-codify-the-accepted-team-1f7f /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-codify-the-accepted-team-1f7f
dispatch: implementer sonnet — one reference doc, one plugin, spec given verbatim
agent: implementer a6c2f3c5d074cbe49 round 1
return: implementer DONE ddce83f
changed: plugins/dev-flow/skills/librarian-mode/references/team-summary.md
dispatch: reviewer opus — rule 4 floor (impl sonnet)
agent: reviewer abd61e66838a279f4 round 1
verdict: NEEDS_CHANGES round 1 at ddce83f
findings:
- [high] team-summary.md:91 — sub-bullet "Checkpoints stamp their own time; resume reads that instead of the session clock." is HOW, not WHAT — pass: observable effect only
- [high] team-summary.md:94 — "Reads the same depth counter the main status line already shows." is purely HOW — pass: a WHAT
- [high] team-summary.md:89 — "Checks quota before each dispatch; ..." first fragment is HOW — pass: two observable fragments
- [medium] team-summary.md:92-93 — example bullet hard-wrapped inside the copy-exactly fence — pass: one line per bullet
- [medium] team-summary.md:47-49 — dropped "leave out how the change was made or reviewed: no tiers, models, review rounds, fix rounds or verdicts" (not contradicted by the spec) — pass: keep it
- [low] :69-71 dropped "no headings"; [low] :62-65 no home for "a rule people now follow"; [low] :75 backticked commit range vs the plain-text warning
notes: peer's original example (their 1a39) not reachable locally; example adapted from the old file.
dispatch: implementer sonnet — fix round 1 (resume)
return: implementer DONE c2a8885
dispatch: reviewer opus — review r2 (resume)
verdict: CLEAR round 2 at c2a8885
lows carried to team-summary-nits-dev-cycle-land-report-d978: :58-59 HOW test reads too broadly ("anything the code does internally that the reader never sees"); :93/:97 sub-bullets restate their parent; :95 "right" twice
landed: 0a3b08d
- 2026-09-22 done: 0a3b08d
