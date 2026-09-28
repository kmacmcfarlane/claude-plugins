---
id: librarian-mode-gate-the-push-on-green-ba-da89
title: "librarian-mode: gate the push on green base checks after a landing merge"
type: chore
status: todo
priority: 2
created: 2026-09-28
updated: 2026-09-28
refs:
  - f6fd review
---

From the f6fd review 2026-09-28: librarian-mode pushes main after its Report ('unless Push: none, push') with no explicit gate on the post-merge base checks; dev-cycle now says a red base check after landed: pushes nothing and goes on decisions needed. In practice the librarian reads the Checks before pushing (memory feedback_gate_push_on_checks), but the skill text doesn't say so. Acceptance: SKILL.md § Report / Critical say the push waits for green Checks on main after every landing merge, and a red one goes under decisions needed with nothing pushed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
