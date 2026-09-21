---
id: context-guard-8cc2-f1-mid-turn-posttoolu-3adc
title: "context-guard 8cc2-F1: mid-turn PostToolUse depth check (silent unless it could hard-block)"
type: feature
status: doing
priority: 1
deps:
  - context-guard-8cc2-f3a-re-inject-handoff-5126
parent: context-guard-turn-gate-8cc2
owner: unknown@360f41058e92
claimed: 2026-09-21T19:08Z
created: 2026-09-21
updated: 2026-09-21
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port — design awaits the 02 serial (HARD mid-turn marker only when hard_applies(block_window, tok); unattended checkpoint path defers to a custody skill's own mode).

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Carried from 8cc2-F2
- librarian-mode ending-the-session.md keys on "HARD threshold reached by an INFERRED depth" and runs a checkpoint (continue); below CHECKPOINT_MIN_TOKENS the advisory now says a checkpoint no longer fits → align there (F1 already edits that file).
- operator-playbook: one clause on the under-20K advice (plan 00).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — new PostToolUse hook in gate code; plan says the blocking predicate extraction must leave decide tests unchanged (else fable reviewer). Lands only after F3a.
