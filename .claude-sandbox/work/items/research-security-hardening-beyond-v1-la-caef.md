---
id: research-security-hardening-beyond-v1-la-caef
title: research security hardening beyond v1 lane contract
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T21:55Z
created: 2026-09-22
updated: 2026-09-29
refs:
  - peer agent-research, 2026-09-22
---

Operator called security critical (relayed by agent-research 2026-09-22). v1 ships lane-contract rule + verifier instruction-shaped-text pass. Wanted: URL allow/deny lists, quarantine of checked-in findings, tests for the verifier detector. Security surface: route fable (Route rule 3) / ask operator.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
librarian decision: plan mode first (security surface, open policy choices such as allow/deny lists go to the operator); fable second opinion on the plan after the opus review's CLEAR (operator called security critical)
dispatch: planner opus — plan mode (Step 1)
agent: planner a533b9e5c8c4a9126 round 1
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security/ (F1 scan floor+detector tests, F2 deep-investigation parity, F3 confinement hook, F4 URL policy, F5 quarantine; Q1-Q12, Q1-Q6/Q8/Q12 blocking parts; deviation: ran live claude -p haiku probe sessions with throwaway hook settings in the scratchpad — not briefed, flagged to the operator; read agent-research, operator-attention, agents repos read-only as corpora)
note: harness flagged the planner's report as instruction-shaped (permissions allow/deny) — the topic of the plan itself; relayed to the operator, not acted on
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe  .claude-sandbox/investigations/caef-research-security/00_initial.md 
dispatch: reviewer opus — fresh, plan review (rule 4)
agent: reviewer aa3ef03d44451c197 round 1
verdict: NEEDS_CHANGES round 1 at 00_initial.md f14d66cd (1 critical, 5 high, 9 medium, 4 low)
findings: verbatim at .claude-sandbox/investigations/caef-research-security/reviews/plan-review-r1.md — critical: F3's Write rule falsely blocks held-run re-verify and every host (non-sandbox) research run (CLAUDE_CODE_TMPDIR unset); highs: unmatched tools pass (MCP, Agent, ToolSearch-loaded), Read denylist bypassable (/proc env, ~/.config…) and Q4 impact overstated, local lane's residuals understated, loopback deny is name-based (nip.io), probe claims lack recorded evidence
librarian decision: no new `claude -p` probe sessions in the fix round (not operator-cleared); unrecorded probe facts are marked unverified and re-probing becomes a gate before F3/F4 build
dispatch: planner opus — resume, fix round 1 (serial 01)
agent: planner a533b9e5c8c4a9126 round 2
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security/ 01_probe-evidence-and-review-fixes.md + evidence/probe-record-2026-09-28.txt (all 20 fixed; P4/P5b/P12b/P13 unverified → gate G-probe; Q16 asks whether live probes are allowed; Q1-Q17, many blocking F3/F4/F5)
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe  .claude-sandbox/investigations/caef-research-security/00_initial.md f6378546b4596c7a835a823b2e0c7a54c663f0cfe856f8b45d68552ef29ac264  .claude-sandbox/investigations/caef-research-security/01_probe-evidence-and-review-fixes.md 
dispatch: reviewer opus — resume, round 2
agent: reviewer aa3ef03d44451c197 round 2
verdict: NEEDS_CHANGES round 2 at 01 f6378546 (1 high, 2 medium, 3 low, 2 nit; all r1 fixed, probe grading honest)
findings: verbatim at .claude-sandbox/investigations/caef-research-security/reviews/plan-review-r2.md — high: verifier read allowlist filled from lane-cited paths admits secrets (denylist must always win, cited paths only under brief-declared roots)
note: harness flagged the reviewer's report as instruction-shaped (settings-json) — the plan's own subject; relayed, not acted on
dispatch: planner opus — resume, fix round 2 (serial 02)
agent: planner a533b9e5c8c4a9126 round 3
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security/ 02_read-write-rules-composed.md (all 8 fixed; composed per-agent re-check; one further gap closed: held re-verify read roots)
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe  .claude-sandbox/investigations/caef-research-security/00_initial.md f6378546b4596c7a835a823b2e0c7a54c663f0cfe856f8b45d68552ef29ac264  .claude-sandbox/investigations/caef-research-security/01_probe-evidence-and-review-fixes.md 278af36fbb78ecc54b8502f4de4dc498a5abe086f2ae19fe925b68460222d4a2  .claude-sandbox/investigations/caef-research-security/02_read-write-rules-composed.md 
dispatch: reviewer opus — resume, round 3 (last before the cap)
agent: reviewer aa3ef03d44451c197 round 3
verdict: NEEDS_CHANGES round 3 at 02 278af36f (2 high, 2 medium, 3 low; all r2 fixed; new highs: runs never stop being live so allows union over past runs; config-dir deny blocks the transcript corpora the plan names)
findings: verbatim at .claude-sandbox/investigations/caef-research-security/reviews/plan-review-r3.md
note: harness flagged the report as instruction-shaped (settings-json) — the plan's subject; relayed, not acted on
dispatch: planner opus — resume, fix round 3 (serial 03; review round 4 is the cap)
agent: planner a533b9e5c8c4a9126 round 4
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security/ 03_f3-authority-and-adversary-walk.md (all 7 fixed; 03 is F3's sole authority; 28-row adversary walk; Q18 transcripts; residuals: local lane Bash bounded by OS user only, verifier corpus+WebFetch bounded only by strict URL mode)
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe  .claude-sandbox/investigations/caef-research-security/00_initial.md f6378546b4596c7a835a823b2e0c7a54c663f0cfe856f8b45d68552ef29ac264  .claude-sandbox/investigations/caef-research-security/01_probe-evidence-and-review-fixes.md 278af36fbb78ecc54b8502f4de4dc498a5abe086f2ae19fe925b68460222d4a2  .claude-sandbox/investigations/caef-research-security/02_read-write-rules-composed.md 7cef67d3052866c26fa1b780227e61054b29ce07f16e5fcf0501007c960af92c  .claude-sandbox/investigations/caef-research-security/03_f3-authority-and-adversary-walk.md 
dispatch: reviewer opus — resume, round 4 (the cap)
agent: reviewer aa3ef03d44451c197 round 4
verdict: NEEDS_CHANGES round 4 at 03 7cef67d3 — the 4-round cap (1 high, 4 medium, 2 low, 1 nit; findings verbatim at .claude-sandbox/investigations/caef-research-security/reviews/plan-review-r4.md; reviewer: each a line or two of spec, none reshapes the plan)
decision 96: the research security plan hit the 4-round review cap — (a) waive the cap for one more planner round, fresh opus reviewer, then the fable second opinion [recommended] | (b) stop planning; take the plan to your 18 questions now and carry the round-4 findings into the build items as acceptance | (c) park the security work | (z) decide later
  raised: 2026-09-28
  what: whether the security plan gets one more fix-and-review round past the cap
  why now: the cap blocks the item; nothing in the security work can move until you rule
  context: 4 reviews; each round fixed its findings, and the last two each opened new holes in the rules they added; round 4's remaining findings are each a line or two of spec (a default that would deny all research web fetches when no URL list exists yet; a missing state transition; a hash check that drops the orchestrator's own clean-up; an overstated bound on the local lane's shell; an agent split not offered)
  (a): one more planner round (~15-25 min) and a fresh reviewer who has not seen the plan — undo: none needed — who: this repo
  (b): the questions come to you now; the build items carry the fixes, reviewed at build time — undo: re-plan later — who: you (18 questions on a plan with known gaps)
  (c): nothing lands; the research tools stay on the v1 contract (prompt-level rules only) — who: every research run
  rec: (a) · basis: strong — four review files in the series; reviewer's own note that none of the findings reshapes the plan
  unknown: whether a fresh reviewer finds new classes of holes (the last two rounds each did)
reply 96 (2026-09-29T05:25Z): tell me — "each ask for another turn needs to justify why it's worth the cost of an operator decision along with the ask. If the impact is high, it's justified. I have no insight into the impact, so I can't make a decision" (read as: tell me the impact of the leftover findings and the cost of the round; re-shown with both)
  revised: 2026-09-29T05:25Z — added: impact of round-4's findings if left unfixed (high: installing the guard denies every research web fetch by default, since the URL list starts missing; mediums: a re-source round after failed verification is impossible, the orchestrator's own clean-up is dropped at landing, one protection claim is overstated, one option missing from Q4/Q18 that changes what you'd be asked) and the round's cost (one planner round, a fresh reviewer, a fable second opinion; about an hour and roughly 1% of weekly quota; none of your time until the questions)
note 2026-09-29: the `reply 96` line above is a line kind the spec does not define; superseded by the re-written card below (5140 review r2, D-3)
decision 96: give the research security plan one more review round past the 4-round cap? — options: (a) waive the cap for one more planner round, fresh opus reviewer, then the fable second opinion [recommended] | (b) stop planning; take the plan's 18 questions now and carry the round-4 findings into the build items as acceptance | (c) park the security work | (z) decide later
  raised: 2026-09-28
  revised: 2026-09-29T05:25Z — tell me; the operator's words: "each ask for another turn needs to justify why it's worth the cost of an operator decision along with the ask. If the impact is high, it's justified. I have no insight into the impact, so I can't make a decision"
  if left: installing the guard denies every research web fetch by default (the URL list starts missing); a re-source round after failed verification is impossible; the orchestrator's own clean-up is dropped at landing; one protection claim is overstated; one option missing from Q4/Q18 changes what the operator is asked
  round costs: one planner round, a fresh reviewer, a fable second opinion; about an hour and roughly 1% of weekly quota (estimate from earlier rounds); none of the operator's time until the questions
answer 96: "96 - you are approved to continue, but this gate is annoying, how can we improve it while still preventing research consuming too much resources?" (read as: (a); the gate itself goes to policy spike 8dee) — given 2026-09-29T05:53Z, found in the session transcript at ~07:00Z, not seen live
dispatch: planner opus — round 5 past the cap (answer 96 a), resume on reviews/plan-review-r4.md
agent: a533b9e5c8c4a9126 round 5 (resumed)
serial 04 written (round 5, answer 96 a): all round-4 findings folded; missing policy file = built-in defaults (open mode); verifier split recommended in Q18; 12 of 17 questions blocking
dispatch: plan reviewer opus — fresh, round 5 (then the fable second opinion)
agent: a27ff4a6ce81e8f99 (plan reviewer r5)
correction 2026-09-29T06:22Z: answer 96 above says "found in the session transcript at ~07:00Z"; the librarian found and acted on it by about 06:08Z (committed 5268efa)
review r5 NEEDS_CHANGES (1H 3M 3L): H Q2(b) shell confinement bypassable (dangerouslyDisableSandbox, cwd writable); M bwrap missing -> silent unsandboxed, project-settings keys ignored; M research-verifier-local has no F3 rules; M Risk 5 overstated; about 7 of 12 questions need the operator (Q1.2, Q3, Q18.2 librarian-decidable; merges proposed); the one waived round is spent
dispatch: second opinion fable — per answer 96 (a), on 00-04 and reviews r1-r5
agent: a72dfd5f1fa641aab (fable second opinion)
second opinion (fable): build-with-acceptance after a closing serial 05 that narrows claims (honest-by-default confinement; verifier split deferred; F1->F2 first; r5 findings carried as acceptance with failing tests first); librarian decides Q1 (a)/(a), Q3 (a), Q6 (a)/(a), Q14 (a), Q18.2 one verifier now, Q7/Q9/Q10/Q17 defaults; operator gets 4 cards now (Q2 shell, URL policy Q4+Q5+Q13, Q16 probes, Q18.1 transcripts), F5 (Q8+Q15) later
librarian ruling: take the second opinion; serial 05 records it, no further review round (the waived round is spent; the build items are reviewed)
dispatch: planner opus — resume, closing serial 05 per the second opinion
