---
id: review-claude-code-bundle-derived-conten-e347
title: Review Claude Code bundle-derived content in the public tree (context-guard window rules, minified identifiers)
short_display_name: bundle-derived content review
type: spike
status: doing
priority: 0
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T07:04Z
created: 2026-10-06
updated: 2026-10-06
refs:
  - peer claude-sandbox librarian 2026-10-06
---

Relayed by peer claude-sandbox librarian 2026-10-06 with the license request: public code includes content derived from Claude Code's bundle — plugins/context-guard/hooks/window_rules.py (pushed c27cd37: a recipe for re-deriving its rules from the bundle, a transcribed model catalog, quoted 429 phrases, minified identifiers), lib_context.py:1300/1330 names e7r()/RLe(), context_warn.py:170 'read from the binary'. The operator noted leaked-source material 'muddies the waters'. Acceptance: an inventory of every such passage with path:line and what it is; options for each (rewrite from public docs/behaviour, remove, keep) for the operator; interacts with the license choice and whether the repo stays public.

## Handoff
- doing: plan stopped and carried (05, 4 reviews)
- next: on 167-169: dispatch the scrub build with the carried findings; on 170-174: the history scrub (4151)
- blocked: —
- learned: —
helper: scout sonnet medium — inventory of Claude Code bundle-derived passages in the tree (read-only) for decision 162 and this review
helper-return: scout — inventory at .claude-sandbox/investigations/e347-bundle-derived-content/00_inventory.md: all in context-guard (plus one statusline comment); 1 recipe, 6 transcribed tables, 3 quoted-string groups, ~20 mangled identifiers, ~12 provenance comments; every row pushed since 2026-09-19; runtime-used: the window tables, ACW clamp, LATCH_API_ERROR, REMOTE_POLICY_RULED_OUT, pidDomain/CLAUDE_PID
decision 164: How should the bundle-derived passages in context-guard be handled? — options: (a) scrub: remove the recipe, the mangled names and bundle control-flow wording; keep runtime values, re-labelled as observed or documented where they can be checked, else as the version they were last confirmed on [recommended] | (b) rebuild: also drop the transcribed tables and derive the window only from what Claude Code reports at runtime | (c) leave as is | (z) decide later
  raised: 2026-10-06T03:41Z
  what: what to do with the Claude Code bundle-derived content the scout inventoried (00_inventory.md): one extraction recipe, six transcribed tables, quoted 429 strings, about 20 minified identifiers and about 12 "from the binary / 2.1.277" comments, all in context-guard's window-rules and helpers, all pushed since 2026-09-19
  why now: you asked for a license immediately and said leaked-source material muddies the waters; a license grants only what you own; blocks: nothing (162 lands independently)
  why ask: your-call — publication of material read from Anthropic's binary is your judgement
  context: the claude-sandbox librarian relayed your concern with the license request · you choose how far to scrub
  stakes: (a) and (b) are reversible edits; none of them removes the content from git history, which only a history rewrite and force-push would, outside my authority
  (a) scrub — one build: the recipe, every minified name and the bundle control-flow wording go; the window tables and the clamp stay as data labelled by version, observed facts (pidDomain, CLAUDE_PID, the apiError code) re-labelled as observed; the window gate keeps working as today — undo: revert — who: context-guard users (no behaviour change)
  (b) rebuild — (a) plus the tables replaced by the runtime-reported window (statusline context_window_size and the cross-check path); the gate loses its predictive rules for unseen models and needs a plan — undo: revert — who: context-guard users (behaviour changes)
  (c) leave — nothing changes; the passages stay public under whatever license 162 picks
  (z) decide later — the inventory waits on the item
  rec: (a) · basis partial — removes what reads as copied internals while keeping the gate working; the runtime values are facts about behaviour, most of them observable
  basis: observed — scout inventory over tracked files at 514f88a (00_inventory.md)
  unknown: whether the tables' values are all publicly documented (no docs were fetched); whether you also want the history rewritten
answer 164: "164a - exactly, only keep facts we can observe, we should not publish internals. We can and should instead hint that you could derive things we can't observe from internals so that my agents continue to reference the source when helpful. I want to perform the history scrub of this content to stay compliant with copyright." (2026-10-06T04:06Z, chat; read as: (a), narrowed — keep only facts observable at runtime; anything only internals show is removed and replaced by a hint that it can be derived from Claude Code's internals, with no content; plus a history scrub, filed as its own one-way item)

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: plan review-claude-code-bundle-derived-conten-e347 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e347-bundle-derived-content
budget: 2026-10-06T07:04Z plan $28 — default plan
dispatch: planner opus high — plan (scrub per answer 164 a, plus the history scrub plan for item history-scrub-purge-claude-code-bundle-d-4151)
agent: planner a17bc769f2e8fbff8 round 1
note: 2026-10-06 6a07 review: pushed work-item store items also hold bundle-derived material (this item's own body line 16; the context-guard exact-depth item line 61); the scrub and the history scrub cover .claude-sandbox/work too
note: 2026-10-06 the scrub should seed the local deny-list (.git/info/claude-code-denylist, never committed) with the exact internal strings it removes, and cover the test fixtures' quoted message text (the new rule forbids it even when observed)
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e347-bundle-derived-content (01_scrub-build.md part A, 02_history-scrub.md part B; open A1-A4, B1 ⚠, B2-B5)
baseline: 6a32e05643bf 00_inventory.md 5805bf0009fc 01_scrub-build.md e35451e07fc6 02_history-scrub.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer a1a6bdd4c2725f74c round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings: (summarised here without internal strings; verbatim in the fix dispatch)
  1. [critical] 02:209-213, :330-334 — Step 8's reset --hard of the main checkout runs with tracked edits there; no backup
  2. [high] 01:382-386 and related — false claims: env-vars § Variables documents the boolean spellings and numeric forms; build would rewrite tests to a misreading
  3. [medium] 02:216-222 — mirror clone without --no-local hardlinks packs; filter-repo's fresh-clone check aborts
  4. [medium] 02:338-340 — reflog expire / gc prune destroy reflogs and unreachable objects with no backup
  5. [medium] 02:224-238, :260-279 — verification too weak (literal-only V1, unspecified class regexes, bare labels matching inside identifiers, V3 path-only)
  6. [medium] 01:556-568; 02:119-161 — store passages missed (7647:11, d63e:86, 1f9d:29, and six binary-as-source lines in 9f90, c0cc, b23e, 8ab6, bace)
  7. [medium] 01:378-428 — internal-only claims in window_rules.py (:95-97, :337-342, :374) and tests unclassified; one may be an unreleased feature
  8. [medium] 01:308-316 — the credits message kept as quoted text against 6a07 rule 2; needs an operator call
  9. [medium] 01:689-694 — Step 7 check: no deny-list seeding, no reading pass, impossible zero-hit bar
  10. [medium] 01:202-204 — hint names no topic; no unreleased test
  11. [medium] 01:851-859 — A3 offers non-compliant options
  12. [medium] 01:838-850 — behaviour changes (lost hard stops) contradict decision 164's card ("no behaviour change"); A1, A2 must block
  13. [medium] 02:297-305 — remap table would publicly index unpurged shas under B1(a)
  14. [medium] 02:361-363, :458 — librarian writing into sibling repos' stores is outside Scope
  15-21. [low/nit] branch count; transcript field for detection; test sub-cases; lib_context.py:40-41 repeat; statusline value lists; first changed commit; counts in prose
correction: decision 164's card told the operator option (a) meant "the window gate keeps working as today… no behaviour change"; the plan shows the scrub does change behaviour (some hard stops become warnings, two models gain them); those changes go back to the operator as blocking A1/A2 before the build
cost: 2026-10-06T07:40Z plan $15.56 of $28 after review 1 — must-fix 14 — prices 2
dispatch: planner opus high — resume (plan fix round 1)
agent: planner a17bc769f2e8fbff8 round 2
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e347-bundle-derived-content (03_review-round-1.md; 21 findings applied; A5 (c) added; A1, A2, A5, B1-B3 blocking)
baseline: 6a32e05643bf 00_inventory.md 5805bf0009fc 01_scrub-build.md e35451e07fc6 02_history-scrub.md 22bf553537f6 03_review-round-1.md 
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer a1a6bdd4c2725f74c round 2
verdict: NEEDS_CHANGES round 2 (plan)
findings:
  round 1: 1-4, 6-8, 10-21 FIXED; 5, 9 PARTIAL
  1. [medium] 03:440-441, :386-387, :404-406 — short labels in the deny-list match inside ordinary words (grep -F, no boundaries); Step 3 would rewrite ordinary lines across history or V1 never passes. Fix: keep labels of four characters or fewer out of the deny-list; B keeps them as boundary regexes in $S/label-regexes.txt; V3 accepts a changed line only if it matched a deny-list entry or one of those regexes
  2. [medium] 03:201, :347 — the SDK name in window_rules.py:395 is publicly documented (hooks, settings-reference, agent-sdk/typescript); keep, cited; delete the :347 bullet
  3. [medium] 03:476 — 03 lacks a Risk Assessment section (A5 (c) lost hard stops, deny-list over-match, tar backup as the only copy of unreachable objects)
  4. [low] 03:396-397 — V1's cc_scan must run from $R so the deny-list resolves
  5. [low] 03:288-296 — A5 (c) impact omits that the credits event's category value is unobserved (under-warn, never block)
  6. [low] 03:303-336 — behaviour list inaccuracies (change 2's Sonnet 4.0/4.5 already warn only; opening line wrong for 11, 12; change 8 unresolved 1M; change 12 peer case)
  7. [low] 03:296, :481 — A5 (c) is safe only with A1 (a); couple them, with a test that a latch under (c) never yields a resolved window
  8. [nit] 03:97-99; INDEX:8-9 — cite the landed rule (86a0227), not the branch
cost: 2026-10-06T07:53Z plan $21.47 of $28 after review 2 — must-fix 3 — prices 2
dispatch: planner opus high — resume (plan fix round 2)
agent: planner a17bc769f2e8fbff8 round 3
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e347-bundle-derived-content (04_review-round-2.md; findings 1-8 applied; the build refuses A5 (c) with A1 (b))
baseline: 6a32e05643bf 00_inventory.md 5805bf0009fc 01_scrub-build.md e35451e07fc6 02_history-scrub.md 22bf553537f6 03_review-round-1.md fc9c1192c481 04_review-round-2.md 
dispatch: reviewer opus high — resume (plan review round 3)
agent: reviewer a1a6bdd4c2725f74c round 3
verdict: NEEDS_CHANGES round 3 (plan)
findings:
  round 2: 2-8 FIXED; 1 PARTIAL
  1. [medium] 04:76-88 — boundary label regexes still match ordinary prose (one-letter and English-word labels; hundreds of store lines), and replace-text runs over every blob. Fix: 04:79 — short labels never become free-standing regex: expressions; Step 3 harvests, from every historical version of the purge-list paths only, each distinct whole line holding a short label (non-identifier boundaries, plus the call parenthesis for function labels) as a whole-line literal; V3 accepts a changed line only if it is a harvested line or holds a deny-list entry; V1 counts label hits only within the purge-list paths
  2. [low] 04:177-179, :232-241 — change 10's early-stop exception missing from A2's impact. Fix: 04:236 — add "Also: a model the build observes at 200K could hard-stop early if Claude Code's downloaded model list ever gives it more; unobserved, and only without a status line (change 10)."
  3. [nit] 04:20-35 — Supersedes cites § numbers 04 does not have
cost: 2026-10-06T07:58Z plan $24.77 of $28 after review 3 — must-fix 1 — prices 2
dispatch: planner opus high — resume (plan fix round 3)
agent: planner a17bc769f2e8fbff8 round 4
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e347-bundle-derived-content (05_review-round-3.md; 1-3 and notes applied)
baseline: 6a32e05643bf 00_inventory.md 5805bf0009fc 01_scrub-build.md e35451e07fc6 02_history-scrub.md 22bf553537f6 03_review-round-1.md fc9c1192c481 04_review-round-2.md 04d42f9f9d2f 05_review-round-3.md 
dispatch: reviewer opus high — resume (plan review round 4)
agent: reviewer a1a6bdd4c2725f74c round 4
verdict: NEEDS_CHANGES round 4 (plan)
findings:
  round 3: 1-3 FIXED
  1. [medium] 05:6-74 — 05 has no Confirmed Assumptions section (format never-omit). Fix: 05:31 — insert "## Confirmed Assumptions" / "None new; 04 § Confirmed Assumptions stands, with main read as of the build (§ Supersedes)."
  2. [low] 05:49-51 — no restart procedure after a V3 stop: on any V3 stop, add the path or line to the inputs, delete $S/rewrite.git, restart from Step 2's --no-local clone; never re-run filter-repo on the rewritten mirror
  3. [low] 05:46-47 — only a manual read drops a wrongly harvested ordinary line; Step 3 prints each harvested line beside its label for the reviewer
cost: 2026-10-06T08:01Z plan $25.79 of $28 after review 4 — must-fix 1 — prices 2
decided: the plan stops and carries — convergence stop at the fourth review (must-fix 1, not lower than review 3's 1), no high left (bindings.md § What a cap ends in, step 2) — class: cap
findings: carried — round 4 findings 1 [medium], 2 [low], 3 [low] above, verbatim; into the scrub build and the history-scrub build (4151)
decision 167: When Claude Code reports the long-context credits error, should the window gate hard-stop at 200K or only warn? — options: (a) warn only [recommended] | (b) keep the 200K hard stop | (z) decide later
  raised: 2026-10-06T08:01Z
  what: what the gate does after the credits error (A1 of the scrub plan, e347)
  why now: the scrub plan stopped and carried after 4 reviews; blocks the scrub build
  why ask: trade-off — a hard stop you rely on today becomes a warning
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → after that error, sessions above 200K get a warning instead of a hard stop · later: the scrub build waits · reach: context-guard users · undo: an edit
  (a) warn only — the only choice safe with 169 (c) — reach: context-guard users — undo: an edit
  (b) keep the 200K hard stop — allowed only with 169 (a) or (b); with 169 (c) it would hard-stop a 1M session after any rate-limit error
  (z) decide later — the scrub build waits
  rec: (a) · basis partial — the error cannot be recognised without quoting internal text, and only warn-only is safe with the text-free recognition
  unknown: none
decision 168: What may make a context window 'resolved', so the gate can hard-stop on it? — options: (a) only the Claude Code docs or a window observed with claude -p [recommended] | (b) also the API's context-window table | (z) decide later
  raised: 2026-10-06T08:01Z
  what: the gate's sources of truth once the internal tables go (A2); decision 164 (a) was put to you as no behaviour change, and this is one of the changes it brings
  why now: the scrub plan stopped and carried after 4 reviews; blocks the scrub build
  why ask: trade-off — hard stops kept vs. sources Claude Code itself documents
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → without a status line, Mythos, Claude 3.x and Opus 4.0/4.1/4.5 only warn, Opus and Sonnet 5.5 gain a hard stop, and one never-observed case could stop early · later: the scrub build waits · reach: context-guard users without a status line · undo: an edit
  (a) Claude Code docs or an observed window — reach: context-guard users without a status line — undo: an edit
  (b) also the API table — those older models keep a hard stop, but the table disagrees with Claude Code on the 4.6 models
  (z) decide later — the scrub build waits
  rec: (a) · basis partial — only Claude Code's own docs and observations say what Claude Code does
  unknown: none
decision 169: How should the gate recognise the credits error in a transcript? — options: (a) the documented message text, cited | (b) a short documented fragment | (c) observed machine values only, no text [recommended] | (z) decide later
  raised: 2026-10-06T08:01Z
  what: how the latch is detected (A5)
  why now: the scrub plan stopped and carried after 4 reviews; blocks the latch change and the history scrub
  why ask: rule-change — (a) and (b) are in tension with the new CLAUDE.md rule against quoted message text
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → no quoted message text in the tree; after any rate-limit error, sessions above 200K only warn for the rest of that Claude Code process · later: an internal string stays in the tree, which also blocks the history scrub · reach: context-guard users · undo: an edit
  (a) documented text, cited — conflicts with the rule; may never match, as the transcript lacks the documented prefix
  (b) a short fragment — same problems, smaller quote
  (c) observed machine values only — over-matches toward warn-only; a credits event with an unobserved category goes undetected (under-warns, never blocks); safe only with 167 (a)
  (z) decide later — an internal string stays; the history scrub is blocked
  rec: (c) · basis partial — the only option that quotes nothing; its errors all fall toward warning, never a false block
  unknown: which category value the credits error itself carries
decision 170: Where should git-filter-repo be installed for the one-time history rewrite? — options: (a) per-session pip in this sandbox [recommended] | (b) the child Dockerfile | (c) the host, with you running the rewrite there | (z) decide later
  raised: 2026-10-06T08:01Z
  what: the tool the history scrub needs (A4); it is not installed
  why now: the scrub plan stopped and carried after 4 reviews; blocks the history scrub only
  why ask: your-call — the sandbox image and the host are yours
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → installed in this sandbox for the one run, gone when the container exits · later: the history scrub cannot run · reach: this sandbox · undo: —
  (a) per-session pip — nothing persists
  (b) child Dockerfile — every future session has it
  (c) host — you run the rewrite outside the sandbox
  (z) decide later — the history scrub cannot run
  rec: (a) · basis strong — a one-time run needs no permanent install
  unknown: none
decision 171: How should the public history be replaced? ⚠ one-way — options: (a) rewrite and force-push | (b) rewrite, delete and recreate the GitHub repo [recommended] | (c) no rewrite | (z) decide later
  raised: 2026-10-06T08:01Z
  what: B1 of the history scrub (4151)
  why now: the scrub plan stopped and carried after 4 reviews; blocks the history scrub
  why ask: one-way — publishing or deleting history cannot be undone
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → old commits stop resolving on GitHub at once; repo settings re-applied; same URL · later: the internals stay readable in public history · reach: the public repo and every clone · undo: (b) none — the deletion is permanent; (a) old commits stay reachable by id
  (a) force-push — old commits stay reachable by id on GitHub, and Support may decline to purge them; every clone must reset; the remap table stays local
  (b) delete and recreate — the repo has no forks, pull requests, issues or stars; only settings need re-applying
  (c) no rewrite — the build (scrub) still lands; history keeps the internals
  (z) decide later — the history scrub waits
  rec: (b) · basis partial — only deleting the repo stops old commits resolving; nothing of value is lost
  unknown: none
decision 172: How much should the history scrub purge? — options: (a) tier 1: recipe, labels, internal strings and facts | (b) tier 1 plus wording that cites 'the binary' as a source [recommended] | (c) also version pins and tables | (z) decide later
  raised: 2026-10-06T08:01Z
  what: B2, the purge scope
  why now: the scrub plan stopped and carried after 4 reviews; blocks the history scrub
  why ask: your-call — how far a one-way rewrite reaches
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → the recipe, labels, internal strings and 'verified in the binary' wording leave all history since 2026-09-19 · later: the history scrub waits · reach: every commit since 2026-09-19 · undo: from the backup while it is kept
  (a) tier 1 only
  (b) tier 1 plus binary-as-source wording
  (c) also version pins and tables — nothing copied, many blobs churned
  (z) decide later — the history scrub waits
  rec: (b) · basis partial — removes every internal source claim without rewriting harmless version data
  unknown: none
decision 173: Who runs the history scrub's force/recreate step and the in-place reset of this checkout? — options: (a) you, from commands I prepare [recommended] | (b) I do, under an explicit waiver of my no-force and no-reset rules for those two steps only | (z) decide later
  raised: 2026-10-06T08:01Z
  what: B3
  why now: the scrub plan stopped and carried after 4 reviews; blocks the history scrub's last steps
  why ask: rule-change — my rules forbid force-push and reset; only you can waive them
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → you run the two destructive steps; every session sharing this checkout stops first · later: the history scrub waits · reach: this checkout, its worktrees, every session on it · undo: from the .git tar backup
  (a) you run them — my rules stand
  (b) a waiver for two named steps only
  (z) decide later — the history scrub waits
  rec: (a) · basis strong — destructive one-way steps stay with you
  unknown: none
decision 174: How long should the history-scrub backups be kept? — options: (a) until the post-push checks pass, plus a week [recommended] | (b) delete right after the checks | (c) keep them offline indefinitely | (z) decide later
  raised: 2026-10-06T08:01Z
  what: B4
  why now: the scrub plan stopped and carried after 4 reviews; blocks nothing
  why ask: your-call — keeping the purged material is a copyright choice too
  context: you chose to scrub internals and rewrite history (164 a) · you settle the plan's open choices — then: none
  impact: → the only rollback, and the only copy of the purged material, is kept a week after the checks, then deleted · later: kept until you say · reach: local disk only · undo: deletion is final
  (a) a week after the checks
  (b) right after the checks — no rollback
  (c) offline indefinitely — the purged material survives
  (z) decide later — kept until you answer
  rec: (a) · basis partial — a short rollback window, then gone
  unknown: none
open question: which other machines hold a clone of claude-plugins or its marketplace (each needs a re-clone or reset after the history scrub) — owner: operator (B5)
note: 2026-10-06T16:36Z operator on 167, verbatim: "167 - what rule bans quoted message text? Is this due to the not using internal source verbatim? The message text is obversable, so I don't think that would be a justification to ban the method in this case" (read as: tell me, and a challenge to the rule — answered: CLAUDE.md § Claude Code source material rule 2's last sentence; it came from the librarian's own ruling 4 during the 6a07 review, not from the operator's words, which named code and prompts; raised as decision 175)
decision 167: When Claude Code reports the long-context credits error, should the window gate hard-stop at 200K or only warn? — options: (a) warn only | (b) keep the 200K hard stop [recommended] | (z) decide later
  raised: 2026-10-06T05:40Z
  revised: 2026-10-06T19:04Z — answer 175 a allows quoting externally observable text, so the error can be matched exactly (169 a) and the hard stop kept; recommendation moved from (a) to (b)
  what: what the gate does after Claude Code's long-context credits error (A1 of the scrub plan, e347)
  why now: blocks the scrub build
  why ask: trade-off — a hard stop kept vs. a warning
  context: you allowed quoting externally observable text (175 a) · you decide whether the gate keeps its 200K hard stop after the error
  impact: → after that error, sessions above 200K keep today's hard stop at 200K, matching what Claude Code does · later: the scrub build waits · reach: context-guard users · undo: an edit
  (a) warn only — sessions above 200K lose today's hard stop after the error — undo: an edit
  (b) keep the 200K hard stop — today's behaviour; needs 169 (a) or (b), never (c) — undo: an edit
  (z) decide later — the scrub build waits
  rec: (b) · basis partial — with exact matching, the hard stop reflects Claude Code's documented fall-back to 200K
  unknown: whether the transcript holds the rest of the message in full; the build checks before relying on it
decision 169: How should the gate recognise the credits error in a transcript? — options: (a) the externally observable message text, cited and labelled [recommended] | (b) a short fragment of it | (c) observed machine values only, no text | (z) decide later
  raised: 2026-10-06T05:40Z
  revised: 2026-10-06T19:04Z — answer 175 a allows quoting externally observable text; recommendation moved from (c) to (a)
  what: how the gate detects the credits error (A5)
  why now: blocks the gate change and the history scrub
  why ask: trade-off — exact matching vs. over-matching
  context: you allowed quoting externally observable text (175 a) · you choose how the error is detected
  impact: → the gate spots exactly that error from its transcript text, cited to the public errors page, with no false triggers on other rate limits · later: an internal string stays in the tree, blocking the history scrub · reach: context-guard users · undo: an edit
  (a) the observable message text — the build first confirms the text in a real transcript line (the documented prefix is absent on 2.1.274); a miss under-warns, never blocks
  (b) a short fragment — tolerant of wording drift, slightly looser
  (c) machine values only — after any rate-limit error, sessions above 200K only warn for the rest of the process; safe only with 167 (a)
  (z) decide later — the internal string stays; the history scrub is blocked
  rec: (a) · basis partial — exact and now allowed by your rule
  unknown: whether the transcript holds the message text in full
correction: 2026-10-06T19:10Z my plan fix round 3 brief told the planner "the planning budget has about $3 left", and my round-4 review brief told the reviewer the budget was nearly spent; bindings.md § Spend budget says no brief carries the budget so no producer or reviewer trims its work to fit — the plan stopped by the convergence rule ($25.79 of $28), but the pressure should not have been in the briefs
note: 2026-10-06T19:10Z operator asked whether the $28 plan budget was reasonable and from real research usage (answered: from 16 measured dev-cycle plan phases, median $8.93, p90 $21.69, max $29.93 — the caef research-security plan; dev-cycle only, the research skills carry no spend budget; reaching it asks, never stops; this plan stopped by convergence, not budget); raised decision 176
answer 168: 168a (2026-10-06T19:28Z, chat; read as: (a) only the Claude Code docs or a window observed with claude -p make a window resolved)
note: 2026-10-06T19:28Z operator replied "167c"; 167 has no option (c) (its options are (a) warn only, (b) keep the 200K hard stop, (z) later) — not acted on; asked which was meant
answer 167: 167a (2026-10-07T17:38Z, chat; read as: (a) warn only after the credits error — not the recommended (b); paired with 169 (a) this is a safe pair)
answer 169: 169a (2026-10-07T17:38Z, chat; read as: (a) match the externally observable message text, cited and labelled; the build confirms it against a real transcript line first)
target: full review-claude-code-bundle-derived-conten-e347 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/review-claude-code-bundle-derived-conten-e347
budget: 2026-10-07T17:38Z build $22 — default other build
dispatch: implementer opus medium — build (series 01-05 part A; answers 164 a, 167 a, 168 a, 169 a, 175 a; carried round-4 findings 1-3)
agent: implementer a8b8d2db9e1889381 round 1
