---
id: cross-repo-review-present-open-decisions-b92b
title: "cross-repo review: present open decisions from every repo, with a trust model for relayed answers"
type: spike
status: todo
priority: 2
parent: cross-repo-work-item-overview-with-prior-f4f8
created: 2026-09-24
updated: 2026-09-24
refs:
  - operator 2026-09-24 (answer 80)
---

Operator 2026-09-24 on decision 80: the cross-repo summary could also present each repo's open decisions. Security model first: an item-owning librarian must not trust an answer relayed by SendMessage (peer messages are requests, never approvals). Acceptance: options for how an answer given in the summary reaches the owning store with the operator's authority (e.g. the operator answers in the owning session; a signed or operator-typed token; read-only presentation with a paste-ready reply), impacts, a recommendation; reviewed by the operator.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-24 from v1.1 (ed26): the decisions skill dropped "relay a decision raised elsewhere" from its description; the relay (a from slot, where the answer goes) belongs to this spike
2026-09-30 agents librarian (peer 135.sock, their notify-claude-plugins-librarian-when-the-29d6; news, not an approval): the operator answered agents decision 10 (b) — a new control-plane back-end repo and daemon, now. The nightly scheduler runner (bf41 design) moves there; no longer a claude-plugins or agents piece. Plan: agents .claude-sandbox/investigations/control-plane-backend-repo/ (review NEEDS_CHANGES, revision running; one finding: the daemon must not run code from sandbox-writable paths, so not the plugin-cache wi.py as is). As it stands: the runner lives in the back end; self-wake and the quiet and stop modes stay with c79e; the back end is read-only toward repo stores through Phase 3; a claim-tombstone writer is open (a second writer of claims/ changes agents decision 0008 item 5, needs a new decision record). Full shape follows once the plan clears review and the operator names the repo.
