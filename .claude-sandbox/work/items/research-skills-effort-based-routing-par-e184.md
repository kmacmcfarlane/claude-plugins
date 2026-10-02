---
id: research-skills-effort-based-routing-par-e184
title: "research skills: effort-based routing parity with dev-cycle's role profiles"
short_display_name: research routing parity
type: spike
status: todo
priority: 2
created: 2026-10-02
updated: 2026-10-02
refs:
  - operator 2026-10-02
---

Operator 2026-10-02, verbatim: 'is the effort-based model routing agent persona stuff in the research skill entrypoints like it is for dev-cycle?' Answer at filing (librarian read): only partly. research, research-deep, research-refine, research-prune launch two pinned agents (research-lane sonnet/medium, research-verifier haiku/low), with model: on the call only to override; research-deep's exhaustive adversarial lane overrides to opus but keeps the lane's medium effort (effort cannot change per call); the synthesis forks on the session's own model. dev-cycle references/model-routing.md:8-11 says the research skills keep their own routing and nothing there governs them: no profiles or -deep effort variants, no dispatch: lines, no quota reserve, no fable offer. deep-investigation launches lanes with a 'cheap model from Step 1' on a plain Agent; chain-of-verification uses general-purpose. Spike: decide whether to bring research dispatches under model-routing.md's profiles (e.g. an opus/high or -deep lane file for adversarial and exhaustive lanes, routed verifier tiers, dispatch: records and the quota sense), and how that interacts with the cost-budget work (f65b, decision 145) and the research-security builds (819f, 1ffd).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: operator 2026-10-02, verbatim: "Since the skills are in the same plugin, we could just piggy-back on the dev-cycle's routing schema, right? Does the shape fit, or does it need some refactoring in that case?" Librarian's read (model-routing.md § Mechanism, § Profiles, § Below the quota reserve, § Fallback, § Recording): the mechanism fits as is (role file + per-call model, one effort per file, dispatch: lines, reserve, fallback, pins composing); a same-plugin pointer is allowed by CLAUDE.md's cross-skill rule. Refactor needed: (1) split model-routing.md into plugin-wide sections and cycle-only sections, and drop the "research keeps its own routing" carve-out (:8-11); (2) a research binding for the record sink (a run's brief/ledger, not an item body) and for which signals exist outside an item; (3) the mechanism puts haiku out of scope but research-verifier is pinned haiku/low — a real choice; (4) a second lane file for adversarial/exhaustive lanes, since effort cannot move per call; (5) research passes model: only to override, the mechanism wants it on every call; (6) research rows in Profiles and the below-reserve table; test_agents.py follows. deep-investigation and chain-of-verification are a scope question.
