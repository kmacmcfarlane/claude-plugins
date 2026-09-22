---
id: review-and-land-agent-research-s-researc-5ef7
title: review and land agent-research's research skill family (branch worktree-research-skills)
type: feature
status: blocked
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T08:33Z
blocked: final review not CLEAR (one fail-safe medium); decision 56
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
fix r1 (peer agent-research): fbdd08b — F1–F14, F16–F20 fixed; F15 declined (librarian filed 8189); F21 applied to fix commit subject only (no amend). Peer ran house lint + strict YAML on 4 skills + 2 agents.
dispatch: reviewer opus — review r2 (resume r1 reviewer on fbdd08b)

review r2 (opus) on fbdd08b: NEEDS_CHANGES. §1–§3, §5 clean; strict YAML now parses for 4 skills + 2 agents; six Checks OK. r1: F1–F8, F10–F14, F16–F20 fixed; F9 partial (→N2); F15 declined, accepted (8189); F21 low carried.
- N1 [medium] research/SKILL.md:169-171 (+refine:51) — § Threads not pulled filled at Step 7 from lane TL;DRs before verification; breaks "brief carries no fetched text"; refine takes mission from it. Pass: entries carry lane id + sub-question no. + gap-condition no. only (or written after PASS); refine restates mission.
- N2 [medium] intensity-and-routing.md:39-42 (+refine:56, research/SKILL.md:262, i&r:55) — rule zero test misclassifies /research-refine, unattended/chained operator-authored prompts, and follow-up turns. Pass: judge by the turn that started the run; list /research-refine; intensity in an operator-authored calling prompt counts, model-composed text does not.
- N3 [medium] research/SKILL.md:228-231, 266 (+refine:110-113) — held run lives only in session-scoped scratchpad; brief's staging pointer dies; refine's clean-first path unreachable. Pass: move held staging to an ignored durable sidecar (check-ignore) and record it, or state plainly it is lost with the session.
- N4 [low] SKILL.md:32-34, storage…:16-21 — synthesis/report/sheet claimed scanned; they are orchestrator-authored post-scan. Reword.
- N5 [low] SKILL.md:104-107 — quick run verifier has no Criteria file.
- N6 [low] storage…:43 — "create .claude-sandbox/research/" contradicts untracked-only rule.
- N7 [low] 5aef0dd subject (F21 carried).
dispatch: fix round 2 → implementer = peer agent-research
fix r2 (peer agent-research): b4e0fb4 — N1–N6 fixed; N7 carried (no amend).
dispatch: reviewer opus — review r3 (resume reviewer on b4e0fb4)

review r3 (opus) on b4e0fb4: NEEDS_CHANGES. §1–§3, §5 clean; strict YAML ok; six Checks OK. N1, N4, N5, N6 fixed; N2 gaps fixed but new spoof path (M2); N3 mostly (M1); N7 carried.
- M1 [medium] research/SKILL.md:237-243, storage…:22-24, 46-48 — held-run check-ignore runs from host repo; in claude-sandbox sidecar mode (.claude-sandbox/ its own git repo) the path is ignored by host but tracked by the sidecar (reproduced). Pass: run check-ignore from the nearest existing parent (`git -C <parent> check-ignore -q <rest>`) so the owning repo answers, or require ignored by every enclosing repo (e.g. skill writes a .gitignore in _held/).
- M2 [medium] intensity-and-routing.md:39-48 — "operator-authored prompt" satisfiable by model text; dev-cycle briefs are model-written; Agent-tool prompt can assert operator authorship. Pass: operator-invoked = a turn the operator typed in this session, or an on-disk prompt file the operator wrote that the run starts from (ralph prompt file); an Agent-tool starting prompt is always model-invoked unless it cites an operator decision recorded in a readable file (work item/brief under the operator's name); drop "dev-cycle brief" from the examples.
- M3 [low] run-record.md:28 — status: list lacks HELD.
- M4 [low] SKILL.md:243-244 — "Then, per the shape" reads as landing continues for a held run.
- M5 [low] 5aef0dd subject (carried).
dispatch: fix round 3 → peer agent-research; review r4 is the last before the cap
fix r3 (peer agent-research): 1c89cde — M1–M4 fixed, 4 files +46/−30; M5 carried.
dispatch: reviewer opus — review r4 (cap round; resume reviewer on 1c89cde)

review r4 (opus, cap round) on 1c89cde: NEEDS_CHANGES. §1–§3, §5 clean; six Checks OK. M1 fixed for held runs (every-level ignore check tested: sidecar mode, tracked, nested, non-repo, missing parent — all safe); M2 Agent-prompt case fixed; M3, M4 fixed; M5 carried.
- P1 [high] intensity-and-routing.md:42-43 vs research/SKILL.md:29-30, :3 — rule zero's operator-invoked list now includes "a request for research in their own words" = the model-invoked case; bypasses operator decision 3 quick-only cost gate; skill contradicts itself. Pass: drop that clause.
- P2 [medium] storage…:47-51, 55-57 — every-level ignore check now also gates rules 4/5 (clean runs); in both standard sandbox modes the sidecar tracks .claude-sandbox/research/, so clean runs fall to the scratchpad; acceptance bullet 1 unmet; refine lookup finds nothing later. Pass: every-level check for _held/ only, host answer for rules 4/5; or write _held/.gitignore '*'.
- P3 [low] SKILL.md:245 vs run-record.md:160 — STATUS HELD not in report format. P4 [low] i&r:47-49 — "a brief" is model-written; limit to a work item whose refs name the operator. P5 [low] § name cited two ways. P6 [low] 5aef0dd subject.
Security path: reviewer found no remaining route for fetched text into a tracked file, another agent or an acted-on file.
decision 54: 5ef7 (research skills) hit the 4-round review cap — round 4 found a regression in the round-3 fix: rule zero now counts "research X" in the operator's own words as operator-invoked, bypassing your quick-only cost gate (high; one-clause removal), plus a medium making clean runs fall to the scratchpad instead of .claude-sandbox/research/. Security path is clean. — (a) waive the cap for one more fix round limited to P1+P2 (+ the P3/P4 one-liners) and one review [recommended: both fixes are specified, security is clear]; (b) land as is and fix P1/P2 in a follow-up item (ships the cost-gate bypass meanwhile); (c) park 5ef7 until you review the branch yourself.
answer 54: (a) do another round (operator 2026-09-22)
fix r4 (peer agent-research, cap waived by answer 54): 76c3ffc — P1–P5 fixed, 4 files +31/−23.
dispatch: reviewer opus — review r5 (final, per answer 54; resume reviewer on 76c3ffc)

review r5 (opus, final waived round) on 76c3ffc: NEEDS_CHANGES. §1–§3, §5 clean; strict YAML ok; six Checks OK. P1–P5 fixed; security path and cost gate clean.
- Q1 [medium] storage-and-knowledge-base.md:35-41 — `_held/.gitignore` (`*`) is written only after the every-level check passes, so in sidecar-repo and tracked modes the check fails first and held runs are lost with the session (fails safe; no leak). Pass (tested): write `.claude-sandbox/research/_held/.gitignore` first when `.claude-sandbox/` exists, then run the check → USABLE in sidecar and tracked mode, nothing shows in either repo's status; non-repo root still lost.
- low: 5aef0dd subject (carried). Notes: spec R9 lacks HELD (edit the spec next time).
decision 56: 5ef7 final (waived) review is not CLEAR on one fail-safe medium — held runs are lost with the session in both standard sandbox modes because a .gitignore is written after the check it should satisfy; the fix is a one-sentence reorder the reviewer already tested. (a) one more micro-round: that reorder only, then a verify-only review [recommended: minutes of work, lands the skills as specified]; (b) land now at 76c3ffc and fix it as a follow-up item (safe: nothing leaks, held runs just are not durable yet); (c) hold.
