---
id: dev-cycle-e770-f4-the-caller-boundary-li-d81c
title: "dev-cycle e770 F4: the caller boundary, librarian-mode points at dev-cycle's resume"
type: feature
status: doing
priority: 3
deps:
  - dev-cycle-e770-f3-resume-whole-plus-the-acdd
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:10Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - e770
---

Plan of record .claude-sandbox/investigations/e770-dev-cycle-resume (00 § F4; six sites per 02/03). Files: librarian-mode/SKILL.md, librarian-mode/references/ending-the-session.md. Route sonnet impl, opus review.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- rider from F3 (2026-09-22): model-routing.md § Fallback now asks a caller to append the one group fable decision N:/answer N: to EVERY item it covers; librarian-mode must say it does.

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full dev-cycle-e770-f4-the-caller-boundary-li-d81c /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/dev-cycle-e770-f4-the-caller-boundary-li-d81c
dispatch: implementer sonnet — two files, one plugin, mechanical once F3 exists; plan routes sonnet impl, opus review
agent: implementer a1cdaa872072a3b48 round 1
- rider from c100 review (2026-09-22): SKILL.md:105-109 Rehydrate step 4 says "merge --abort, then redo the matching one" — with troubleshooting's new neither case there may be no match; say "the matching redo, or a decision when neither matches".
return: implementer DONE_WITH_CONCERNS b4ed234 (SKILL.md +49 bytes: two required riders)
changed: librarian-mode SKILL.md (Rehydrate steps 3-4, fable-group clause), references/ending-the-session.md (four sites)
dispatch: reviewer opus — rule 4 floor (impl sonnet)
agent: reviewer aae2e168adc2b1526 round 1
verdict: NEEDS_CHANGES round 1 at b4ed234
findings:
- [medium] SKILL.md:95-96 — §2 reference lint FAIL: sibling name and path split across an indented wrap. Pass: name and path on one line.
- [medium] SKILL.md:95-96 — pointer targets § LIVE (the fact) not Group B (S3a/S3b/S13, the action) — the librarian never runs Step 0.4, so this is its only route; and ids named from "doing:/dispatch: line" where dispatch: never carries an id. Pass: "Take each doing item's record up by the `dev-cycle` skill's `references/resume.md`, whose § LIVE probes the ids its agent: lines (and In flight) name, and whose Group B attaches or salvages."
- [medium] SKILL.md:111 — orphan rule lost ListAgents, the only detector of agents no item records. Pass: "no live agent (step 3's probes; ListAgents for one no item records) and no doing item".
- [medium] SKILL.md:206 — "(references/model-routing.md § Fallback)" resolves to librarian-mode's own stub. Pass: the `dev-cycle` skill's references/model-routing.md § Fallback.
- [low] ending-the-session.md:13 repeats record-lines rationale; [low] SKILL.md:205 "its pair" ambiguous.
dispatch: implementer sonnet — fix round 1 (resume)
agent: implementer a1cdaa872072a3b48 round 2
return: implementer DONE fb386a8
dispatch: reviewer opus — review r2 (resume)
agent: reviewer aae2e168adc2b1526 round 2
