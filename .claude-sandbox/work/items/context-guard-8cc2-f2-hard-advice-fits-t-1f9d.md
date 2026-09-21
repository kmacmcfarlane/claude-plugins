---
id: context-guard-8cc2-f2-hard-advice-fits-t-1f9d
title: "context-guard 8cc2-F2: HARD advice fits the space left (CHECKPOINT_MIN_TOKENS)"
type: feature
status: doing
priority: 1
parent: context-guard-turn-gate-8cc2
owner: unknown@360f41058e92
claimed: 2026-09-21T18:41Z
created: 2026-09-21
updated: 2026-09-21
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port (00 + 01; plan review round 2 cleared F2 to go). context_warn advises /clear or /compact instead of /checkpoint when too little is left to afford a checkpoint; CHECKPOINT_MIN_TOKENS in lib_context derived from the thresholds() docstring (lib_context.py ~520, lean-path floor ~16K + margin); measured against block_window; also the inferred-not-blocked message. Verify whether /compact still works at ~1K left (plan OQ3) or keep /clear first.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic in a gating hook (advice text only; the blocking predicate is untouched) — fable signal not met
