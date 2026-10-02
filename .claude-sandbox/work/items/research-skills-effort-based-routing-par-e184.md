---
id: research-skills-effort-based-routing-par-e184
title: "research skills: effort-based routing parity with dev-cycle's role profiles"
short_display_name: research routing parity
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-02T21:57Z
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

## Notes
- 2026-10-02 claimed by Kyle-McFarlane@401123cbad11
note: operator 2026-10-02, verbatim: "let's just update the research skills' routing to be shaped along the lines of how dev-cycle was updated in-place instead of depnding on the dev-cycle skills. That seems cleaner. / 1. keep them separate / 2. we should have a work item for all research runs, then we can adopt that as the place to store that similarly / 3. it's okay for us to use haiku for this task if evidence supports that decision / 4. approved a second file to control effort / 5. let's have it for every call in research skills too / 6. you decide / bring along deep-investigation and chain-of-verification / go ahead and plan it and land it" (read as: plan and land; research gets its own routing reference shaped like dev-cycle's model-routing.md, in place, not a pointer into dev-cycle; every research run files a work item, which becomes its record sink for dispatch: lines; the verifier stays on haiku only if evidence supports it, else sonnet low; a second lane file at a higher effort is approved; model: on every research dispatch; deep-investigation and chain-of-verification are in scope)
decided: 2026-10-02T21:57Z ruled-rule-case — tests: plugins/dev-flow/tests/test_agents.py keeps every research agent file's model and effort pin in step with the research routing table, as it does for dev-cycle's Profiles · authority: the operator's "6. you decide" (2026-10-02) · reopen: say so
decided: 2026-10-02T21:57Z ruled-rule-case — the second lane file is named research-lane-deep, after planner-deep and implementer-deep; its effort is the plan's to set from evidence · authority: the operator's "4. approved a second file to control effort" (2026-10-02) · reopen: rename in the reply
dispatch: planner opus high — plan (operator: plan it and land it)
target: plan research-skills-effort-based-routing-par-e184 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e184-research-routing
agent: planner a755d6374fee501cb round 1
return: planner PLAN_READY .claude-sandbox/investigations/e184-research-routing/ (INDEX, 00, evidence/verifier-record.md); verifier to sonnet/low on evidence; research-lane-deep opus/high
baseline: 978f34264739 00_initial.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer a20dd05df1987148f round 1
