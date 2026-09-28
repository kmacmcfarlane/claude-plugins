---
id: research-security-hardening-beyond-v1-la-caef
title: research security hardening beyond v1 lane contract
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T21:55Z
created: 2026-09-22
updated: 2026-09-28
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
