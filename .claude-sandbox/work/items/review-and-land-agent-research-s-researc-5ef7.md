---
id: review-and-land-agent-research-s-researc-5ef7
title: review and land agent-research's research skill family (branch worktree-research-skills)
type: feature
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T08:33Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - peer agent-research; operator start args 2026-09-22
---

agent-research peer 2026-09-22: research, research-deep, research-refine, research-prune skills + first agents/ dir (research-lane, research-verifier) in plugins/dev-flow, plus marketplace/README/CLAUDE.md shape rows. Peer will signal ready; librarian gates via review + checks, lands. Operator 2026-09-22 session start: 'try to land the new librarian-mode skills'. Note CLAUDE.md 'no plugin ships agents today' line must change in the same feature.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

ready (peer agent-research, 2026-09-22): 5aef0dd on 3585a67, 14 files +1557/-7; peer states it pushed the branch to origin (its own action, not the librarian's). Peer-flagged for judgement: research disable-model-invocation false with quick-only rule (operator choice); angle brackets in argument-hint; verifier blocks landings on agent-addressed text (v1 control, caef builds on it); new KB.md `kind: research-kb` convention.
dispatch: reviewer opus — marketplace shape + first agents/ dir + >3 files (implementer = peer session, tier unknown; floor opus)

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

review r1 (opus) on 5aef0dd: NEEDS_CHANGES. Checks: six suites OK; §2 research-prune strict YAML FAIL. Findings (medium+ must be fixed; low = author's call, decline with reason):
- F1 [critical] agents/research-verifier.md:24-27 — security scan covers only frontmatter/TL;DR/Sources; Findings, Implications, Could-not-verify, Open questions unscanned. Pass: scan every line of every findings file; re-verify rescans whole file.
- F2 [high] research/references/run-record.md:360 (+SKILL.md:173-176, research-criteria.md:183-184) — lanes write findings into the destination (tracked KB tree) before verification. Pass: lanes write to scratch/sidecar staging; copy to checked-in destination only after PASS.
- F3 [high] storage-and-knowledge-base.md:25-26 — sidecar `.claude-sandbox/research/` claimed gitignored by convention; in tracked mode it is tracked; investigations/<slug>/research/ likewise. Pass: `git check-ignore` before rules 4/5, else scratchpad; fix the claim.
- F4 [high] agents/research-verifier.md:66-67, 49-50 — verification.md copies injected/source text verbatim. Pass: security section names file+line+neutral description only; source quotes capped and marked data; orchestrator treats verification.md as untrusted.
- F5 [high] research/SKILL.md:100-102 (+storage…:22, 42-43) — quick with --to and report write fetched-derived content with no instruction-shaped-text pass. Pass: same whole-file scan before any disk write.
- F6 [high] storage-and-knowledge-base.md:32-36 — sidecar promotion to docs/research/ has no verification gate. Pass: refuse while verification.md shows an open security concern.
- F7 [high] run-record.md:324-325, 334-337 + research-deep/SKILL.md:73-75 — DONE ledger lines copy lane text into 00-brief.md, which the wakeup prompt acts from. Pass: ledger lines carry counts/paths/status only, or brief states ledger is data.
- F8 [high] research-refine/SKILL.md:137, 185 — model-invocable, defaults to standard → bypasses quick-only gate. Pass: disable-model-invocation true, or model-invoked refine quick-only.
- F9 [high] research/references/intensity-and-routing.md:39-47 vs 57-61 — "do not ask" rows don't rank below the model-invoked rule; model can pass --intensity deep itself. Pass: model-invoked rule overrides every row; model-invoked unless operator's current turn carries /research; model-written args never count as operator naming a preset.
- F10 [high] research-prune/SKILL.md:6 — unquoted argument-hint starting `[` fails strict YAML; hint `--execute <proposal>` disagrees with usage line 25. Pass: quote hints (all four), match usage.
- F11 [medium] CLAUDE.md:24-26 — layout block lacks the four research skills and an agents/ line under dev-flow.
- F12 [medium] README dev-flow row / CLAUDE.md:114 — dev-flow now spans three aims; operator decision placing research in dev-flow recorded nowhere in repo. Pass: one sentence in README dev-flow section naming the operator decision and why.
- F13 [medium] research-deep/SKILL.md:3, research/SKILL.md:3 — trigger phrases collide with deep-investigation ("deep research", "map the landscape of", "research this overnight") and investigate ("look into", "research"). Pass: non-overlapping phrases or explicit disambiguation.
- F14 [medium] agents/research-verifier.md:4 (+research-lane.md:4) — verifier has Bash+Write; needs no shell. Pass: drop Bash from verifier; lane keeps Bash only for local corpora, stated.
- F15 [low] research-lane.md:47-79 vs deep-investigation lane-contract — rules in two places; no convergence item. (librarian will file the thin-caller item regardless)
- F16 [low] intensity-and-routing.md:63-66 — fan-out test restated, not pointed to.
- F17 [low] intensity-and-routing.md:82-83 — past resets_at should read as cleared window.
- F18 [low] README dev-flow row — context-guard soft-dep note omits research Step 9 checkpoint.
- F19 [low] storage…:62 vs research-refine:214 — "nothing edited" vs superseded_by edits; refine's runs/ layout ignores destination layout.
- F20 [low] research/SKILL.md:44 — resume conflated with refine.
- F21 [low] commit subject not `<verb>: <aspect> - <description>`.
dispatch: fix round 1 → implementer = peer agent-research (tier its own; librarian cannot route a peer's model)
