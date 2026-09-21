---
id: statusline-set-the-terminal-title-while-8c2c
title: "statusline: set the terminal title while a dialog hides the status line (prototype)"
type: spike
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
---

From spike 7e3b: PreToolUse (AskUserQuestion, ExitPlanMode) and PermissionRequest fire synchronously as a dialog opens; a hook may return a terminalSequence (OSC 0/2) that the harness writes. Prototype: a statusline hook that sets the terminal title to '<session name> · <ctx left> · waiting on you' while a dialog is up and restores it after (PostToolUse / next render). Verify live that the sequence renders during a dialog in 2.1.277 [U in the series]; harness quarantine: belongs in statusline (its aim is orientation display) — or statusline-hub once it exists; decide at build time. Operator pain: 'harder to orient to that session when I switch there'.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
