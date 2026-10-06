---
id: agent-scope-protocol-declared-scope-the-51df
title: "agent scope protocol: declared scope, the access it needs, overlaps escalated to the operator"
short_display_name: agent scope of responsibility
type: spike
status: todo
priority: 1
created: 2026-10-03
updated: 2026-10-03
refs:
  - operator 2026-10-03
---

Operator 2026-10-03, verbatim: "I think that there sound be a protocol where the librarians (or any other hovering on a repo agent) understand their scope of responsibility. When agents are assigned or claim responsibility, they should also be given the observability and (where necessary) credentialed access to do what's inside their scope of work and purview as defined. Agents should advertise their expected area of control and escelate discrepencies betweeen agegents to the operator to settle what the apparently blurry lines are." Related: librarian-mode's Scope/Exclude and claims, the forwarding item 3460, the cross-session handoff skill 2bbe (roles, per-action consent), the agents repo's control-plane back end (claims report-only, ledger), and today's blurry lines (clustertool and brainboy on the tank work; consent relayed across sessions). Spike: what a scope declaration holds (repos, paths, systems, actions, credentials needed); where it is advertised (session registry, the store, the agents ledger); how assignment or a claim grants observability and access, and who grants credentials (a trust decision); how overlaps and gaps are detected and put to the operator; which parts belong here versus the agents control plane.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: answer 152 (a), shaped by the operator: short term = librarian-mode-interview-the-repo-s-scop-5925 (librarian-mode interview); long term worked with the agents librarian, asked 2026-10-04
note: peer agents 2026-10-04, pointers and their librarian's reading (no operator ruling); their item answer-claude-plugins-51df-agent-scope-* (search "51df"); paths under agents .claude-sandbox/investigations/. (1) Back end covers: liveness (Phase 2, control-plane-backend-repo/01 § E′) and budget claims (claim files owned by our 1222; agents decisions/0008 item 5; r4-control-plane/01-synthesis.md § 4); its reaper only reports (writing claims/ needs a new agents decision, 01 § O, OQ5′); no scope or capability registry planned; claims confer no authority to act; tags alone insufficient for routing (01-synthesis § 5, H4) — "who may act on what" is ours to shape. (2) Where scope lives: the repo's own CLAUDE.md ## Librarian block is the authority today (agents routing/truth-map.md "Librarian charter, per repo", no mirrors; delivery after /clear: agents 5ca7); their reading — keep it the single authority (each repo writes only its own, CONSTITUTION art 19/21) and have the back end publish a derived, read-only, read-time-stamped copy in its estate snapshot (a new back-end requirement they will file if our plan wants it); not in the decision ledger. (3) Credentials: their reading — grants stay with the operator per session through claude-sandbox's launch config; the control plane holds none; the back end refuses any boundary claim since every sandbox reaches every path (back-end 03 § T′; their security note security-note-every-sandbox-in-the-kmacm-1c2f); a grant mechanism belongs in claude-sandbox's launch-config threat model (F2 privileges banner, F4 diff-and-prompt, their item 8554, decision 36); a credential broker would need the operator's ruling and claude-sandbox's agreement. Discrepancies between agents → the decisions work (operator-interaction), not the back end.
