---
id: decisions-skill-fix-the-trigger-miss-rec-c2e7
title: "decisions skill: fix the trigger miss — reconcile the dialog guidance, consider a nudge when a turn ends with decisions"
short_display_name: decisions skill trigger miss
type: feature
status: todo
priority: 1
parent: decisions-skill-operator-feedback-from-t-ac53
created: 2026-10-03
updated: 2026-10-03
refs:
  - peer scribe 2026-10-03
---

Finding 1: the skill's description covers listing open decisions and asking the operator to decide, yet it never loaded over many decision turns in scribe. Named cause: project memory feedback_askuserquestion_flow (claude-plugins) described when to fire AskUserQuestion and that multiple choice is fast, while the skill says not to raise decisions through a modal dialog (the librarian's memory copy was rewritten 2026-10-03 to defer to the skill). Acceptance: the skill names the cases where a dialog is acceptable (the opt-in, an explicit operator request) in one place; trigger wording tested against decision-shaped turns; evaluate a hook that nudges when a turn ends with decision-shaped content (placement: a harness-behaviour plugin, README rule 1) — a plan question.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
