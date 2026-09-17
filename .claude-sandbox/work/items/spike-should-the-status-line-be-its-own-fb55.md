---
id: spike-should-the-status-line-be-its-own-fb55
title: "spike: should the status line be its own plugin?"
type: spike
status: todo
priority: 3
created: 2026-09-17
updated: 2026-09-17
refs:
  - operator message 2026-09-17
---

Operator question 2026-09-17: factor the status line out of context-guard into its own plugin; would that make context-guard depend on it? Librarian assessment recorded in the session; no change until the operator decides. Decision recorded here when made.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes (2026-09-17)
- Coupling today: statusline.py writes the exact depth record into context-guard's state file, and colours the
  gauge with lib_context.thresholds(window) (due/hard remaining: 200K -> 70K/40K, 1M -> 150K/60K) and epoch.
- Window size is not the problem: the status-line payload carries context_window_size exactly. Hooks cannot see
  it; transcripts record the model as e.g. "claude-opus-5" and settings as "opus" — the 1M option is not in the
  model id, so a hook cannot derive the window from the model.
- Cheaper decoupling raised with the operator: context-guard writes its computed thresholds (and epoch) into the
  state file; a separate status-line plugin only reads that record and never copies the policy. Reduces the
  dependency to a data contract. Weakens the librarian's "not yet" recommendation; still pending the operator.
- OPERATOR 2026-09-17: d63e decision 14 answered (d); status line may become its own plugin without a hard dependency.
