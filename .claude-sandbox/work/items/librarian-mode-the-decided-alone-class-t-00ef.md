---
id: librarian-mode-the-decided-alone-class-t-00ef
title: "librarian-mode: the decided-alone class table, with what makes a trade-off real"
short_display_name: decided-alone class table
type: feature
status: done
priority: 1
deps:
  - decisions-record-and-show-what-is-decide-58f4
created: 2026-09-30
updated: 2026-10-01
closed: 2026-10-01
refs:
  - .claude-sandbox/investigations/8dee-the-line/INDEX.md
  - 69ee reply 112
---

8dee F2 (112 b, pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: 8dee F2 — librarian-mode references/decide-alone.md with the class list (263c as evidence), the trivial-docs and simple-fix tests (113's answer; (a) is the working reading until then), the promotion rule, per-class narrowing, planner-question triage; Intake step 3 and the decision channel point to it. PLUS the operator's reply on 112 (2026-09-30, chat, verbatim on 69ee): specific guidance on the kinds of impact that make a trade-off real (reversibility, who else is affected, spend, trust/security, behaviour the operator relies on, contracts and stored data, scope and precedent, quality vs speed — the draft in 69ee), stated as examples and saying the list is NOT exhaustive; and what is not a real trade-off (options converge, taste only, settled by a rule, one option dominates). A raised card's why ask: names the impact kind. Closes b8d6.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: full librarian-mode-the-decided-alone-class-t-00ef /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-the-decided-alone-class-t-00ef
dispatch: implementer opus medium — opus signal: changes what a skill does (librarian-mode class table); feature with no own plan: /investigate then /implement from 8dee F2 (wave 2, 132 a)
agent: implementer a591ad0e6fcc5cfa5 round 1
return: implementer DONE_WITH_CONCERNS 7419b1c
changed:
  plugins/dev-flow/skills/librarian-mode/references/decide-alone.md — § The line (class sides), § What makes a trade-off real (operator-approved draft), § How the line moves, § A planner's questions, § Trivial documentation pointer
  plugins/dev-flow/skills/librarian-mode/SKILL.md — pointers in Intake step 3 and the decision channel
  plugins/dev-flow/skills/librarian-mode/references/decisions.md — line 42, the class authority binding row
note: promotion is asked (a rule-change decision), never self-granted; per-class narrowing lands as a filed rule change — the conservative reading; accepted for review
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer aaa8f6a2077c19dc1 round 1
verdict: NEEDS_CHANGES round 1 at 7419b1c
findings:
  1. [medium] decide-alone.md:89-96 vs :152-161 — promoted count line contradicts § The Report's "one Done: line per ruling, never merged" (and the decisions skill's FYI form)
  2. [medium] decide-alone.md:177-179, 83-84 — only trade-off cards must name the impact kind; the approved draft says every raised card's why ask names it
  3. [low] decide-alone.md:89-96 — promotion asked plus clean spot-check, with no trigger for when it is proposed
  4. [low] decide-alone.md:97-101 vs :23, :29 — narrowing's rule change: raised or landed on the operator's undo as authority?
  5. [low] decide-alone.md:26 vs SKILL.md:24-26, Intake step 4 — forwarding decided alone before F4 (3460) lands contradicts Critical
  6. [low] decide-alone.md:47-53 — evidence overstated (scope change 4/5; 8dee's 4-of-26 differences dropped; decision 10 misfiled)
  7. [low] walkthroughs.md:18 (out of scope) — example raises catalog wording as a trade-off
  8. [low] decide-alone.md:24 — table-placement keyed to this marketplace's table; say it does not apply where a repo has none
  9. [nit] decide-alone.md:82-83 vs :21 — sign test sends nothing-at-stake to minor-design even when minor-design's terms fail
  10. [nit] SKILL.md:237 — unwrapped line
librarian rulings: 1 — § The Report gets the promoted-class exception (a count line only for a class the operator promoted by answer N); keep the decisions skill generic (its FYI line stays one per ruling unless the caller's rules promote); 3 — keep promotion asked; trigger: proposed when a class has 10 decided: lines since its last promotion ask with no undo or reopen; 4 — the operator's undo is the authority, the narrowing edit lands as a change shown in the Report, not a new ask; 5 — forwarding is decided alone once F4 (3460) lands; until then Critical governs (raised/routed to the operator); 7 — widen scope to walkthroughs.md:18 (one-line fix)
dispatch: implementer opus medium — resume
agent: implementer a591ad0e6fcc5cfa5 round 2
return: implementer DONE f1f03db
changed: + plugins/dev-flow/skills/librarian-mode/references/walkthroughs.md — split-plugin example: catalog wording decided alone (F7, scope widened by the librarian)
dispatch: reviewer opus high — resume
agent: reviewer aaa8f6a2077c19dc1 round 2
verdict: CLEAR round 2 at f1f03db
notes: prior 1, 2, 4-10 FIXED; 3 PARTIAL (low: promotion window anchor/undo marker); new nits 11 (unwrapped line), 12 (backfill form lacks an impact kind) — follow-up filed
landed: d0526b3
- 2026-10-01 done: d0526b3
