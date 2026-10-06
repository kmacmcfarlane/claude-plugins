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
- doing: —
- next: —
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
