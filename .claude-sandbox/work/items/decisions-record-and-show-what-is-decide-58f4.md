---
id: decisions-record-and-show-what-is-decide-58f4
title: "decisions: record and show what is decided alone — decided: line, done-alone group, why ask:, class tag"
short_display_name: decided-alone record
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/8dee-the-line/INDEX.md
  - 69ee answers 110, 111, 112
---

8dee F1, unblocked by answers 110 a (build here now), 111 b and 112 b (operator, pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: 8dee 00 § Landable features F1 as amended by 01-03 — the decided: store line (class, authority, reopen), the Report's done-alone group of Done: lines, why ask: on every raised card, a class tag on every decision as raised, decide-alone.md seeded with the class names, generic FYI authority in the decisions skill. Goes before any class widens. Coordinate: 0999, the 100 b build, 5140 C2/C7 and 2eb7 edit the same files.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-record-and-show-what-is-decide-58f4 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-record-and-show-what-is-decide-58f4
dispatch: implementer opus medium — opus signal: changes what a skill does (decisions skill, librarian decisions.md, work-items format); feature with no plan: /investigate then /implement (waves 1-3, 132 a)
agent: implementer ad599a521afa99e57 round 1
return: implementer DONE_WITH_CONCERNS 1f35cb8
changed:
  plugins/operator-interaction/skills/decisions/SKILL.md — why ask as floor item 3; FYI authority by caller class; shown-after paragraph; two Rulings
  plugins/operator-interaction/skills/decisions/references/rendering.md — class slot, Why ask line, Done alone group
  plugins/operator-interaction/skills/decisions/references/worksheet.md — FYI rule restated; § E why-ask and class fields
  plugins/operator-interaction/skills/decisions/references/gallery.md — Why ask on every card; example 24
  plugins/dev-flow/skills/librarian-mode/references/decide-alone.md — new: decided: record, done-alone group, class names
  plugins/dev-flow/skills/librarian-mode/references/decisions.md — class rows, why ask on stored cards, decided: bullet
  plugins/dev-flow/skills/librarian-mode/SKILL.md — pointers in Intake step 3 and § Report
  plugins/work-items/skills/work-items/references/format.md — Card lines; § Decided alone
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a46d8fc8aba824c9d round 1
verdict: NEEDS_CHANGES round 1 at 1f35cb8
findings:
  1. [medium] librarian-mode references/decisions.md:151 — Done alone inserted as Report item 2 renumbers 2-4; idle-turn.md:83's "§ The Report's item 4" now points at the wrong item; fold into item 2, revert the :175 edit
  2. [medium] decide-alone.md:28 — `authority: rule <file> § <section>` is a fourth authority the FYI rule (decisions SKILL.md:119-123, rendering.md:195-196, decisions.md:42) does not accept
  3. [medium] decide-alone.md:67-68 vs decisions.md:89-93 — backfilled pre-F1 cards get `why ask: not recorded`, breaking the grammar/regex; state an explicit backfill form (e.g. `why ask: unclassed — not recorded (raised before why ask)`)
  4. [medium] decide-alone.md:45-49, rendering.md:199-200, worksheet.md:88 — Done: line needs "why it was safe" but the decided: grammar has no field for it (gallery 24 shows the gap)
  5. [low] decide-alone.md:79-80 — minor-design gloss drops "the alternatives the status quo or strictly worse"; trade-off gloss defines what makes a trade-off real (F2 00ef owns it)
  6. [low] decide-alone.md:74-96, :98 — kebab-case tag spellings are new parsed API names not yet put to the operator
  7. [low] decide-alone.md:35, format.md:672 — nothing forbids " · authority: " / " · reopen: " inside the what field; the lazy regex splits wrongly
  8. [nit] rendering.md:176 — stale Labels table placement
  9. [nit] gallery.md:166, 487-492 — example 7 why ask repeats why no recommendation; example 24 copies the librarian's exact grammar into the generic skill
librarian ruling on 6: the tag spellings go to the operator as decision 134 (api-name, 111 b); the build lands with them marked provisional and no librarian writes a class tag to the store until 134 is answered (the running librarian uses the installed plugin, which has none); renaming before first use costs no migration
dispatch: implementer opus medium — resume
agent: implementer ad599a521afa99e57 round 2
decision 134: The decided-alone record introduces 19 class tags stored on decision lines (wording, minor-design, trade-off, narrowing, wider-scope, ruled-rule-case, rule-change, table-placement, placement, api-name, reply-reading, forwarding, relay, one-way, trust, spend, cap, blocker, unclassed); keep these spellings? — options: (a) keep them as written [recommended] | (b) rename some (say which) | (z) decide later
  raised: 2026-09-30
  what: the tag names every stored decision will carry; wi and other repos' tools will parse them
  why now: the build lands with them marked provisional; nothing writes a tag until you answer
  why ask: api-name — new stored names are yours (111 b)
  (a): tags go live with the next plugin update — undo: a rename later means migrating stored lines — who: every librarian store
  (b): renamed in a small follow-up before first use; no migration
  (z): they stay provisional; librarians keep raising and recording without class tags
  rec: (a) · basis partial — the names follow 263c's and 8dee's class list; the reviewer found no clash, only that you had not seen them
  unknown: whether other repos' parsers want a different case or prefix
