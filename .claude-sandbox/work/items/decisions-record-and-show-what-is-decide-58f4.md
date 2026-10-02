---
id: decisions-record-and-show-what-is-decide-58f4
title: "decisions: record and show what is decided alone — decided: line, done-alone group, why ask:, class tag"
short_display_name: decided-alone record
type: feature
status: done
priority: 1
created: 2026-09-30
updated: 2026-09-30
closed: 2026-09-30
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
return: implementer DONE_WITH_CONCERNS f20c96a
changed: (same 8 files; this round: decisions.md, decide-alone.md, format.md, rendering.md, gallery.md)
note: implementer's concern — the ruled provisional sentence blocks every store write of decided: and why ask: until 134 is answered; accepted as intended (a short wait on one operator answer; nothing is lost, the Report still shows what was done alone)
dispatch: reviewer opus high — resume
agent: reviewer a46d8fc8aba824c9d round 2
verdict: NEEDS_CHANGES round 2 at f20c96a
findings:
  prior 1-8 FIXED; 9 first half FIXED, second half DECLINED (accepted)
  10. [medium] decide-alone.md:88-89 — "nothing writes a class tag to a store before then" contradicts the lines that require one (decide-alone.md:4-6, 15-23, 64-67, 73-78; decisions.md:57, 82; SKILL.md:158-160) and gives no interim rule; add it next to the provisional sentence (until 134: no decided: line and no Done alone group; why ask: shown on the card but not stored; no backfill written) and have the mandating lines defer to it
  11. [nit] format.md:400 — joined long line
dispatch: implementer opus medium — resume
agent: implementer ad599a521afa99e57 round 3
return: implementer DONE cf29358
changed: (same 8 files; this round: decide-alone.md interim rule, decisions.md and SKILL.md deferral clauses, format.md rewrap)
dispatch: reviewer opus high — resume
agent: reviewer a46d8fc8aba824c9d round 3
verdict: NEEDS_CHANGES round 3 at cf29358
findings:
  10. [medium] PARTIAL — decisions.md:90-94 (backfill), :82-84 (stored why ask), :43, :153-154 and SKILL.md:301-303 (Done alone group), SKILL.md:159-161 (decided: line) still mandate what the interim rule forbids
  11. [nit] FIXED
  12. [medium] decide-alone.md:94-95 — interim rule contradicts untouched text: (a) why ask shown but not stored breaks "renders only from stored fields" (decisions.md:90, rendering.md:221-232) on every re-show; (b) no Done alone group contradicts the generic skill's shown-after rule (decisions SKILL.md:125-129, 277-279; rendering.md:182-184)
C: root cause is my round-1 ruling ("nothing writes a class tag until 134"). Reversed: no interim rule. The tags are written as spelled; they stay provisional until 134 is answered, and a rename then migrates the lines written in between. No librarian uses this text before the operator updates the plugin and restarts, so 134 will usually be answered first.
revised 134 (2026-09-30): (a) keep — nothing to migrate; (b) rename — a sed over the decided:/why ask: lines written since the plugin update, if any; (z) later — tags are written as spelled meanwhile
dispatch: implementer opus medium — resume (fix round 3; the next review is round 4, the cap)
agent: implementer ad599a521afa99e57 round 4
return: implementer DONE 46afbf2
changed: (same 8 files; this round: decide-alone.md sentence replaced, interim rule removed; decisions.md and SKILL.md back to f20c96a)
dispatch: reviewer opus high — resume
agent: reviewer a46d8fc8aba824c9d round 4
verdict: CLEAR round 4 at 46afbf2
notes: prior 10, 12 FIXED; new 13 [low] decide-alone.md:88-90 — the migrate-on-rename sentence names no owner (suggest: the change that renames them migrates those lines in the same landing) — carried as a follow-up; reviewer flags 134's stored card as stale (revise before showing)
landed: 0c2757b
- 2026-09-30 done: 0c2757b
  revised: 2026-09-30 — decision 134's card: the "nothing writes a tag until you answer" rule was withdrawn in fix round 3. why now: the build landed (0c2757b); tags are written as spelled from the next plugin update. (a) keep — nothing to migrate; (b) rename some — the change that renames them migrates the decided:/why ask: lines written since the update; (z) later — tags written as spelled meanwhile
decision 134: The decided-alone record uses 19 class tags on stored decision lines (wording, minor-design, trade-off, narrowing, wider-scope, ruled-rule-case, rule-change, table-placement, placement, api-name, reply-reading, forwarding, relay, one-way, trust, spend, cap, blocker, unclassed); keep these spellings? — options: (a) keep them as written [recommended] | (b) rename some (say which) | (z) decide later
  raised: 2026-09-30
  revised: 2026-10-01T07:06Z — backfilled: context:, stakes:; why now and options restated as one card (the interim no-tags rule was withdrawn in fix round 3)
  what: the class names written on every decided: and why ask: line; wi and other repos' tools may parse them
  why now: the decided-alone record landed (0c2757b, pushed) with the names marked provisional, and they are already written as spelled, so each new decision adds a line a rename must migrate; blocks: nothing
  why ask: api-name — a parsed tag's name is yours before it ships (answer 111 b)
  context: you last saw this card on 2026-09-30 while the decided-alone record was in review · you decide now whether its 19 tag names stand — then: none
  stakes: reversible, wide — every librarian store
  (a) keep them as written — the tags stop being provisional; nothing to migrate — undo: a later rename migrates the stored lines — who: every librarian store
  (b) rename some — the change that renames them migrates the decided:/why ask: lines written since the update, in the same landing
  (z) decide later — tags keep being written as spelled; each new decision adds a line a later rename must migrate
  rec: (a) · basis partial — the names follow the class list the reviewer checked; it found no clash, only that you had not seen them
  unknown: whether other repos' parsers want a different case or prefix
note: operator 2026-10-01 on decision 134, verbatim: "134 - these seem pretty specific to the data you happen to have analyzed. Investigate a better shape for this" (read as: dig into — investigate a more general shape for the class tags; the result comes back on 134 with options) — spike decisions-a-general-shape-for-decision-c-90bc
decision 134: What shape should decision classes take, now that the 19 tags turn out to be fitted to this repo's cases? — options: (a) two words: why it is yours (for a raised one) and what changed (for one decided alone) [recommended] | (b) the same flat list, made generic | (c) full axes on every line | (z) decide later
  raised: 2026-09-30
  revised: 2026-10-01T07:38Z — dig into came back (spike 90bc, plan CLEAR after 3 review rounds): the question changes from "keep the 19 spellings?" to "which shape?"; options and recommendation replaced
  what: the shape of the class written on every decided: and why ask: line, which also decides what is raised and what is decided alone; the spellings (OQ1 of the decision-class plan) ride with the answer
  why now: you asked for a better shape (dig into on 134); the 19 keep being written meanwhile, so the migration grows; blocks: nothing
  why ask: api-name — names stored on every decision line are yours (answer 111 b), and (a) also moves rules you ruled (OQ3 of the plan)
  context: you said the 19 tags looked fitted to the data I happened to analyze and asked me to investigate a better shape · you pick the shape, and may rename any word in your reply — then: the 19 each sit on one of four axes (kind of change, stakes, authority, how it came up) and were picked where this store's decisions fell; tested on decisions from other repos, half did not fit; none meant "affects people or services outside the repo", "behaviour others rely on" or "this is your own call", so live changes like a DHCP range fell into a class decided alone
  stakes: reversible, wide — every librarian store, and what every librarian asks you
  (a) two words — a raised line says why it is yours: blocker, one-way, trust, contract (a name, format, interface or behaviour something outside this work relies on), reach (people or services beyond the repo), spend, precedent (a new standing rule, or where something lives with no rule to settle it), your-call, then an open catch-all trade-off; checked in that order, doubt raises as unclassed. A decided line says what changed: words, design, place, scope, reading, cap. 16 words (19 today). It also changes, unless you split them off: promotion keyed on word plus answer; scope merging narrowing with forwarding; design covering config values and dependency bumps — undo: rename back via the same retired-spellings table — who: every librarian store; one sed here, each other librarian rewrites its own tags at Rehydrate
  (b) the same flat list, made generic — about 13 renamed words, the smallest diff; the side is still looked up from the word, so the gaps for reach and behaviour others rely on stay
  (c) full axes on every line — four fields per line, machine-checkable; the line grammar changes and old lines read "not recorded"
  (z) decide later — the 19 keep being written, and the later migration grows
  rec: (a) · basis partial — the gaps are real on held-out kinds of case (a changed default, webhook timing, a value that deploys on push), but held-out real decisions barely separate the shapes because those stores had already raised them
  basis: observed — 16 sample decisions across 5 repos + 12 held-out (series 00, 03, 04); observed — plan review CLEAR round 3
  unknown: whether 16 words is the right size in practice; how often reach and contract raise in daily use
decision 134: What shape should decision classes take, now that the 19 tags turn out to be fitted to this repo's cases? — options: (a) two words: why it is yours (for a raised one) and what changed (for one decided alone) [recommended] | (b) the same flat list, made generic | (c) full axes on every line | (z) decide later
  raised: 2026-09-30
  revised: 2026-10-02T16:46Z — expanded to a block on the operator's word ("144: expand", read as 134): backfilled undo/who on every option
  what: the shape of the class written on every decided: and why ask: line, which also decides what is raised and what is decided alone; the spellings (OQ1 of the decision-class plan) ride with the answer
  why now: you asked for a better shape (dig into on 134); the 19 keep being written meanwhile, so the migration grows; blocks: nothing
  why ask: api-name — names stored on every decision line are yours (answer 111 b), and (a) also moves rules you ruled (OQ3 of the plan)
  context: you said the 19 tags looked fitted to the data I happened to analyze and asked me to investigate a better shape · you pick the shape, and may rename any word in your reply — then: the 19 each sit on one of four axes (kind of change, stakes, authority, how it came up) and were picked where this store's decisions fell; tested on decisions from other repos, half did not fit; none meant "affects people or services outside the repo", "behaviour others rely on" or "this is your own call", so live changes like a DHCP range fell into a class decided alone
  stakes: reversible, wide — every librarian store, and what every librarian asks you
  (a) two words — a raised line says why it is yours: blocker, one-way, trust, contract (a name, format, interface or behaviour something outside this work relies on), reach (people or services beyond the repo), spend, precedent (a new standing rule, or where something lives with no rule to settle it), your-call, then an open catch-all trade-off; checked in that order, doubt raises as unclassed. A decided line says what changed: words, design, place, scope, reading, cap. 16 words (19 today). It also changes, unless you split them off: promotion keyed on word plus answer; scope merging narrowing with forwarding; design covering config values and dependency bumps — undo: rename back via the same retired-spellings table — who: every librarian store; one sed here, each other librarian rewrites its own tags at Rehydrate
  (b) the same flat list, made generic — about 13 renamed words, the smallest diff; the side is still looked up from the word, so the gaps for reach and behaviour others rely on stay — undo: a sed back — who: every librarian store
  (c) full axes on every line — four fields per line, machine-checkable; the line grammar changes and old lines read "not recorded" — undo: hard; lines written with four fields would need rewriting to go back — who: every librarian store and anything that reads decision lines
  (z) decide later — the 19 keep being written, and the later migration grows — undo: n/a — who: nobody yet
  rec: (a) · basis partial — the gaps are real on held-out kinds of case (a changed default, webhook timing, a value that deploys on push), but held-out real decisions barely separate the shapes because those stores had already raised them
  basis: observed — 16 sample decisions across 5 repos + 12 held-out (.claude-sandbox/investigations/90bc-decision-classes/ serials 00, 03, 04); observed — plan review CLEAR round 3
  unknown: whether 16 words is the right size in practice; how often reach and contract raise in daily use
note: operator 2026-10-02 on decision 134, verbatim: "134 - give me some examples of what this would be like in different scenarios" (read as: tell me — worked examples of the two-words shape, given in the reply from the decision-class plan cases T1-T18, H1-H12; nothing in the card changes)
note: operator 2026-10-02, verbatim: "134 - show the examples table again" (read as: tell me — the examples table re-shown; nothing in the card changes)
