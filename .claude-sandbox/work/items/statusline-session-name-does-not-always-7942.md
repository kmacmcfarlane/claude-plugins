---
id: statusline-session-name-does-not-always-7942
title: "statusline: session name does not always match /rename or an agent-set name"
type: bug
status: doing
priority: 3
deps:
  - statusline-progress-bars-for-session-fab-28ad
owner: unknown@4d338747396e
claimed: 2026-09-16T18:04Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16: the session name shown by hooks/statusline.py does not always match what /rename set, or a name the agent set itself. Investigate first: which payload key(s) Claude Code sends (session_name? a nested session object? does it change after /rename without a re-render? is the agent-set name a different field?), read the statusline docs and check a live payload capture; then fix statusline.py to prefer the current name with a fallback chain, and add tests. Depends on 28ad (same file). Harness file -> fable (rule 3).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: implementer fable — rule 3 (harness file hooks/statusline.py); research step included in the brief
dispatch: reviewer fable — rule 4
- implementer fable returned DONE_WITH_CONCERNS, commit 4b4162b. Research: payload has only session_name
  (custom title or AI title; lags /rename until the next render); registry $CLAUDE_CONFIG_DIR/sessions/<pid>.json
  carries name + nameSource (user|peer|collision|auto|hook|derived); peer/collision names never reach the payload —
  that is the operator's mismatch. Open question: payload-first (as briefed) vs registry-first.
- librarian ruling: the registry wins when its nameSource is explicit (user, peer, hook, collision); the payload
  session_name is the fallback; derived/auto registry names are never shown. Sent to the implementer as a
  pre-review adjustment 2026-09-16 18:12:26; reviewer fable after.
- ruling applied as commit 043ad36 (113 tests); reviewer fable round 1 dispatched 2026-09-16 18:13:47
- review round 1: NEEDS_CHANGES — 2 medium (control chars/newlines in a registry or payload name break the one-line contract; ancestor walk untested — every registry test places the file at the direct parent), 2 lows (eager /proc walk costs 4+3 opens; non-Linux degrades silently to payload-only, undocumented), 1 note. Reviewer confirmed collision as explicit and closest-ancestor precedence. Fix round 1 sent 2026-09-16 18:19:46, tier unchanged (fable, resumed).
- fix round 1 implementer killed by the API rate limit (2026-09-16 20:01:53) before any change; fresh fable implementer re-dispatched with the findings (same round, same tier).
- fix round 1 (re-dispatched) returned DONE, commit 7a7545f (122 tests; clean() sanitiser + 60-char cap; lazy interleaved walk; docs). Re-review dispatched 2026-09-16 20:06:00 (reviewer fable, resumed).
