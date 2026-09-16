---
id: context-gate-hard-stop-on-1m-context-mod-99cb
title: "context gate: HARD STOP on 1M-context model and checkpoint whitelist misses plugin-prefixed command"
type: bug
status: done
priority: 0
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16, urgent: in a session on Opus 5 (1M context) the UserPromptSubmit hook context_warn.py blocked with 'HARD STOP: 13,546 tokens left of 200,000 (inferred)' while the statusline showed 813k left. Retrying with '/claude-kit:checkpoint' was also blocked although the message says /checkpoint is whitelisted. Acceptance: (1) the gate never infers a 200k window when the statusline or session data shows a larger one, and an inferred limit never hard-blocks, only warns; (2) the checkpoint whitelist matches the plugin-prefixed form /claude-kit:checkpoint as well as /checkpoint; (3) a documented operator escape hatch exists; (4) tests cover all three.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Diagnosis (librarian, 2026-09-16)
State file of the blocked session (config dir <other-project CLAUDE_CONFIG_DIR>,
session 3abff11c): `exact` = {tokens 186454, window 1000000, pct 19, at 1789573377}; the hook
wrote window 200000 / pct 93.2. So the status line HAD the exact 1M window, but the record was
older than EXACT_MAX_AGE_S (600 s) when the prompt was submitted (operator idle while typing
a long prompt / waiting on an agent), and lib_context.depth() fell through to inference.
Inference guesses the window from the transcript peak: 186454 < 0.95*200000, so it chose 200k
and computed 13,546 left -> under hard (40k) -> exit 2. Two defects:

A. Staleness fallback discards the known window. The window of a session does not decay with
   time; only the token count does. Fix: when `exact` is stale, keep its window (and its
   tokens as a floor) and only re-derive tokens from the transcript; also lower the guess
   risk by treating any exact window ever seen as the minimum window.
B. An inferred depth can HARD block. Inference is a guess (docstring: "a wrong guess
   under-reports pressure" is not even true here — it over-reported). Fix: source ==
   "inferred" caps the gate at DUE (additionalContext + systemMessage); HARD requires exact.
C. WHITELIST uses prompt.startswith(("/checkpoint", ...)); the operator typed
   /claude-kit:checkpoint (the plugin-qualified form Claude Code offers) and was blocked
   again. Fix: whitelist matches the command name with an optional `<plugin>:` prefix, e.g.
   regex ^/(?:[\w-]+:)?(checkpoint|compact|clear)\b.
D. Escape hatch: CLAUDE_KIT_CONTEXT_WINDOW env var exists but is undocumented in the
   install-statusline / checkpoint skill; document it, and document the state-file stand-down
   (set checkpoint_epoch = epoch) as the emergency unblock.

Immediate unblock applied by the librarian: session 3abff11c state file got
checkpoint_epoch=0 and a refreshed exact.at (backup at <file>.bak-librarian).

Files in scope: plugins/claude-kit/hooks/lib_context.py, plugins/claude-kit/hooks/context_warn.py,
plugins/claude-kit/hooks/tests/test_lib_context.py, plugins/claude-kit/hooks/tests/test_hooks.py,
and the one skill doc that describes the gate for the escape-hatch line (install-statusline or
checkpoint SKILL.md — implementer picks the one that already documents the hook, reports which).
model: fable (rule 3: hook that gates prompts)
dispatch: implementer fable (rule 3), reviewer fable (rule 4)

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
Correction: the unblock could NOT be applied from the librarian sandbox — the operator's
config dir is a read-only mount here. Handed to the operator as a host-side one-liner.
Timing note: exact.at = 15:42:57 UTC, later than the blocks; the hook saw either no exact
record or a stale one. Both cases are covered by fixes A and B.
- 2026-09-16 done: 56eb5fc

## Dispatch log
- implementer: fable (rule 3, gating hook) — returned DONE, commit 8afe5d0
- reviewer: fable (rule 4, matches implementer) — round 1 dispatched 2026-09-16 15:57:03
- review round 1: NEEDS_CHANGES. 1 medium (regex \b lets /clear-all, /checkpoint-x through under HARD), 3 low
  (stale-exact token floor ignores a later compaction; SKILL.md wording says stale/missing can still block;
  inferred-under-hard advisory has no cadence and omits the env pin), 1 low out of scope (checkpoint
  operator-playbook.md still says HARD blocks every prompt) — the out-of-scope one moved to item
  checkpoint-skill-describe-the-gate-s-inf-80ab. Fix round 1 sent to the implementer 2026-09-16 16:01:58.
- fix round 1 returned DONE, new commit 398e365, nothing declined; re-review dispatched 2026-09-16 16:04:23 (reviewer fable, resumed)
- re-review: CLEAR. Findings 1-4 FIXED; 2 nits raised in the re-review (docstrings not updated with the
  boundary exception; redundant save_state on the inferred-hard path) — left as-is, not blocking.
- reviewer NOTES kept: shared due cadence can suppress the inferred-hard advisory for up to 2 prompts after
  an exact DUE fire (by design, never blocks); once a compact_boundary exists the stale-exact token floor is
  off for the session; boundary-then-no-usage reports tokens=0 honestly.
- landed: merge 56eb5fc on main, 2026-09-16 16:07:19. Checks on main: 87 hook tests OK, py_compile ok, json ok, marketplace==disk.
