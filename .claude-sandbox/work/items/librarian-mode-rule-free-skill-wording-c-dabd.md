---
id: librarian-mode-rule-free-skill-wording-c-dabd
title: "librarian-mode: rule-free skill wording counts as trivial docs, self-reviewed"
short_display_name: wider trivial docs
type: feature
status: done
priority: 2
deps:
  - librarian-mode-the-decided-alone-class-t-00ef
created: 2026-09-30
updated: 2026-10-01
closed: 2026-10-01
refs:
  - .claude-sandbox/investigations/8dee-the-line/INDEX.md
  - 69ee answer 113
---

8dee F9 under answer 113 b (operator, 2026-09-30T22:14Z): trivial documentation is prose-only plus skill wording that changes no rule (a typo, a broken link, a sentence restating an existing rule), self-reviewed; the author states why it changes no rule on the review: self line. Acceptance: 8dee F9 — the test in decide-alone.md and the dev-cycle Step 2 rule 5 pointer; Risk: the author judges where a rule begins (8dee Risk L1b).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
dispatch: implementer opus medium — build (8dee F9, answer 113 b; rule wording, not mechanical)
target: full librarian-mode-rule-free-skill-wording-c-dabd /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-rule-free-skill-wording-c-dabd
agent: implementer aff18569d0f41dc19 round 1
return: implementer DONE_WITH_CONCERNS 861858e
librarian ruling on concern 1: keep the wider reading to cycles run under librarian-mode — answer 113 b is about this repo's librarian, and a standalone dev-cycle has no repo-scoped place to hold it; narrower is the safe side (more review, not less). Concern 2 accepted: Step 4.5 and record-lines.md still carry the review: self record.
dispatch: reviewer opus high — review round 1
agent: reviewer aca335493b9a7887c round 1
verdict: NEEDS_CHANGES round 1 at 861858e
findings:
  1. [medium] decide-alone.md:143-162 — the always-fails list is unconditional, so restatement (copies its must/never) and broken-link (alters a path) can never pass; fix: judge against the rule in force — words copied verbatim from the cited home are not added, any differing word is; one meaning of path: only a file / § section pointer the agent reads for instructions is fixable as a link; any path read for data, written, run or passed to a tool is a rule; a cited section heading is a name
  2. [medium] decide-alone.md:145 — the condition-word list misses if, not/no/none, quantifiers (every, each, any, all), sequence words (before, after, until, first), and/or joining conditions; fix: add them; the list is a floor, not a definition
  3. [medium] decide-alone.md:159-162 — restatement does not exclude rewording the rule's own home; fix: a restatement is a sentence outside the home that cites it; an edit to the home is never rule-free (bar a pure typo)
  4. [medium] decide-alone.md:135-138 — nothing keeps a reviewer on the self-review gate itself; fix: the waiver's own files (model-routing.md § Review waiver, decide-alone.md § Trivial documentation, dev-cycle Step 2 rule 5, review-brief.md, review-checklist.md, fix-loop.md) are never skill wording
  5. [low] decide-alone.md:137 — "templates never" vs ":135 and its references/"; name the template files or say a references file pasted into a brief or written to a store is a template
  6. [low] dev-cycle SKILL.md:442 — red flag example lost "skill text"; write "(skill text, bar librarian-mode's rule-free wording, CLAUDE.md, an agent, a script, any operational claim)"
  7. [low] decide-alone.md:167-170 — no clause form for a broken link, none for several kinds; add the link form and one clause per kind separated by ;
  8. [low] decide-alone.md:3-8 — header names neither § Trivial documentation nor its new loaders
  9. [nit] librarian-mode SKILL.md:37, record-lines.md:110 — rewrap to ~90
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer aff18569d0f41dc19 round 2
return: implementer DONE 318462c
dispatch: reviewer opus high — resume (round 2)
agent: reviewer aca335493b9a7887c round 2
verdict: CLEAR round 2 at 318462c
findings:
  1-8 FIXED; 9 PARTIAL [nit] record-lines.md:111 still 109 chars — declined for this landing (cosmetic), left for the next edit of that file
landed: 2f66939
- 2026-10-01 done: landed 2f66939 (CLEAR r2)
