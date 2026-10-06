---
id: claude-code-knowledge-plugin-placement-p-ea9f
title: "Claude Code knowledge plugin: placement (private internals vs public scrubbed) and plan review of the handed-over series"
short_display_name: Claude Code knowledge plugin
type: spike
status: todo
priority: 1
created: 2026-10-06
updated: 2026-10-06
refs:
  - peer claude-sandbox librarian 2026-10-06
---

Handed over 2026-10-06 by peer claude-sandbox librarian at the operator's request (their item proposal-a-reusable-claude-code-knowledg-31bd, closed there). Series, read-only in their repo: /home/rt/work/src/github.com/kmacmcfarlane/claude-sandbox/.claude-sandbox/investigations/claude-code-knowledge-skill/ (INDEX, 00_initial.md, 01_review-fixes.md superseding parts of 00); one opus review NEEDS_CHANGES (11 findings) answered in 01, not re-reviewed; OQ1-OQ14 open. Planner rec H5: claude-code-internals private in mcfacehead-plugins now, a scrubbed public claude-code here later; window_rules.py keeps runtime values, drops minified names and the re-derivation recipe (overlaps e347). Operator leans private ('muddies the waters'). Planner concerns: mcfacehead-plugins README says homelab infra and has no Checks; removing content here does not rewrite git history. Scope: work in mcfacehead-plugins is outside this librarian's Scope — routed to the operator / that repo's librarian; this repo's share is the scrub (e347) and any later public plugin. Acceptance: operator's placement answer; then the in-scope part re-reviewed through the cycle.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 163: Where should the Claude Code knowledge plugin live? — options: (a) private first: claude-code-internals in mcfacehead-plugins now, a scrubbed public claude-code here later (the planner's H5) [recommended] | (b) private only, in mcfacehead-plugins | (c) public only, scrubbed, here | (z) decide later
  raised: 2026-10-06T03:39Z
  what: the home of a consolidated Claude Code knowledge plugin (facts now spread over about 90 files in 8 repos, versions 2.1.205-2.1.290), per the series claude-sandbox handed over (OQ1); its other open questions (OQ2-OQ14) follow from the home
  why now: claude-sandbox handed the thread over at your request today; blocks: everything else in the series
  why ask: your-call — public vs private publication of material partly read from the Claude Code binary is a judgement you lean on ("muddies the waters")
  context: you asked for this thread to move here and lean private · you choose where it lives
  stakes: reversible while unpublished; publishing anything public is one-way for copies taken
  (a) private first (H5) — the full skill ships privately where binary-read facts can live; a public version comes later with only documented and observed facts; the private build is mcfacehead-plugins' librarian's (outside my Scope), whose marketplace README says homelab infrastructure and has no Checks yet — undo: drop the public stage — who: every session that installs it
  (b) private only — simplest; nothing public to scrub; sessions outside your private marketplace never get it — undo: add a public stage later — who: your sessions only
  (c) public only, here — one home and the doctrine's catalog; everything binary-read is cut first, so the plugin knows less — undo: hard once published — who: anyone
  (z) decide later — the series waits; the window_rules.py scrub (e347) proceeds on its own
  rec: (a) · basis partial — it matches your private lean and keeps a public path for the documented facts; the planner's recommendation after one review round
  unknown: whether mcfacehead-plugins should take a content plugin (its README scope), and the series' 01 has not been re-reviewed
answer 163: "163 - In the light of that, I'm comfortable with the claude-code plugin being public as long as: it contains no verbatime code snippets and doesn't disclose any features that are still unreleased since the leak (probably few of those remain, but important to have a check for that before we commit and push anything publicly" (2026-10-06T04:06Z, chat; read as: (c) public, here in claude-plugins, gated: no verbatim code or prompts, and no feature still unreleased since the leak, checked before any commit and push)
note: 2026-10-06T07:04Z the knowledge-plugin re-plan waits for the e347 plan's per-passage classification (observable / documented / internal-only), which the public plugin's content rules build on
