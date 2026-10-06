---
id: review-claude-code-bundle-derived-conten-e347
title: Review Claude Code bundle-derived content in the public tree (context-guard window rules, minified identifiers)
short_display_name: bundle-derived content review
type: spike
status: todo
priority: 0
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
