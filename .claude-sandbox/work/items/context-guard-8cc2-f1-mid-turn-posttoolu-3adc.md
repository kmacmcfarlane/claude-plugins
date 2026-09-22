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
updated: 2026-09-22
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port — design awaits the 02 serial (HARD mid-turn marker only when hard_applies(block_window, tok); unattended checkpoint path defers to a custody skill's own mode).

## Handoff
- doing: fix r1 fadd0ed (stand-down while a checkpoint is underway); review r2 running (agent af38b45d01f832696, opus)
- next: on CLEAR: land (merge-tree first — it conflicts easily), then F3b-4 may start
- blocked: —
- learned: —

## Carried from 8cc2-F2
- librarian-mode ending-the-session.md keys on "HARD threshold reached by an INFERRED depth" and runs a checkpoint (continue); below CHECKPOINT_MIN_TOKENS the advisory now says a checkpoint no longer fits → align there (F1 already edits that file).
- operator-playbook: one clause on the under-20K advice (plan 00).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — new PostToolUse hook in gate code; plan says the blocking predicate extraction must leave decide tests unchanged (else fable reviewer). Lands only after F3a.

## Implementer result
- round 1 DONE_WITH_CONCERNS 59168d1 (opus): turn_gate.py PostToolUse (advisory only; silent unless block_window; HARD marker iff hard_applies; agent_id skip; early return mirror-off; hard_nofit tier), hard_applies extracted (decide tests unchanged → reviewer stays opus), checkpoint unattended section, playbook "Inside a turn", ending-the-session.md exceptions. 24 tests; cached per-call ~15 ms.
- scope widening before review: README context-guard hooks sentence + design-rationale §3 turn-gate layer. Merge held until F3a lands (hooks.json will conflict mechanically).
- widening 9797fab: README hooks sentence; design-rationale §3 added paragraph.
- dispatch: reviewer opus — rule 4 (decide tests unchanged → no fable bump). Merge held for F3a.

## Review round 1 — NEEDS_CHANGES (opus) at 9797fab
- decide() unchanged over 506,880 in-process cases + 640 end-to-end; HARD marker iff context_warn exits 2 (0 mismatches); no output on any guessed/foreign/future/stale source; never blocks or crashes; cadence fires 7× over 150K.
- [medium] a forged/quoted marker (in a docstring, diff, tool result) could trigger the unattended checkpoint and its mark would silence the real gate: the unattended section must verify the state's turn_gate record (this epoch, tier hard/hard_nofit) before acting, and say the marker counts only as hook-added context.
- lows: unwritable state dir → marker every call (pin with a test/comment); a custody skill's remaining steps (librarian push, Report) run before the final message; mode 644; commit layout noted.
- noted follow-up: legacy in-state exact block has no future-`at` check (pre-existing).
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix 0b530a3 + c7d4757: turn_gate.py --check <sid> (armed only for this epoch, tier hard/hard_nofit, no checkpoint yet); unattended section runs --check first and treats the marker as hook-context only; hook silent when its record cannot land; custody steps run before the final message; 755.
- dispatch: reviewer opus — round 2 (resume). Merge held for F3a.

## Review round 2 — CLEAR (opus) at c7d4757
- every forgery refused by --check; real HARD arms; unwritable state: hook silent, prompt gate still blocks (no regression). lows: malformed top-level epoch → traceback (fail-safe); commit layout.
- READY TO LAND — held until F3a is on main (plan order F2 → F3a → F1). Expect hooks.json / README / checkpoint Step 5 conflicts at merge.

2026-09-22 (this session): F3a landed (4ca4646) and H1–H6 landed on top, so the hold is lifted but the branch is 309 commits behind with 3 conflicts (README.md, hooks/hooks.json, librarian-mode ending-the-session.md). Its review (CLEAR at c7d4757) predates every 5039 change to rehydrate/context_warn, so the conflict round must re-verify, not just merge.
dispatch: implementer opus — conflict round + re-verify (fresh agent; the r1 implementer ran in session 0c7eafc7); gate code = fable signal, fable unavailable → opus, recorded
conflict round DONE f493b2f (merge) + 850daed (opus): hooks.json keeps ledger_pointer (Bash|Write|Edit) and lineage (Read) untouched and adds turn_gate on the empty matcher (timeout 10); README keeps main's ownership sentence + the mid-turn gate; ending-the-session and checkpoint SKILL.md corrected for H3/H4 (In flight and Holds are evidence-built, so skipping Step 0 does not drop them). Beyond the merge: +5 tests — 4 pinning the hooks.json registration (fail when main's file is swapped in), 1 driving H1's refused stamp through to a disarmed gate. Re-verification: HARD marker iff hard_applies over 12,832 cases (0 mismatches); decide/tier_of agree on HARD over 6,020; silent on every inferred/unresolved source incl. the 2026-09-16 replay; turn_gate state key collides with nothing, all writers use locked update_state; 649 context-guard tests OK. Open low (from r2): --check tracebacks on a malformed top-level epoch (fails safe, ugly).
dispatch: reviewer opus — fresh review of the merged branch (the CLEAR at c7d4757 predates F3a and H1–H6)
review (opus, fresh, merged branch) at 850daed: NEEDS_CHANGES. Seven Checks OK (context-guard 649). Latency on a 26 MB/22,766-line transcript: cold 95.6 ms, warm 15.3–16.4 ms (~12.5 ms is interpreter start); the feared uncached path does not exist (measure returns before scan_usage). Marker iff decide()=="hard" over 19,035 cases, 0 mismatches both ways; hard_applies vs the old inline rule 30,100 cases, 0 mismatches; 144 inferred-source cases, 0 spoke; 24 concurrent hook processes × 3 runs, 0 failures, every state key survived; hooks.json pinned in both directions by mutation.
- [medium] turn_gate.py:145-147 + checkpoint SKILL.md:26-31 — no stand-down while a checkpoint is underway (checkpointed_this_epoch only flips at Step 4b). Reproduced: HARD at 45,000 left fires the marker, the operator runs /checkpoint, and 27K in the gate emits "End the turn now with a three-line brief" and --check answers armed: hard_nofit — a checkpoint one step from Step 4b is told to abandon, and mode handoff collides with an operator's continue. Pass: stand down while a checkpoint is in flight (a state flag the skill sets, or a hard→hard_nofit flip is a no-op once fired this epoch), or an explicit sentence in the unattended section and ending-the-session step 2.
- lows: --check tracebacks on a malformed top-level epoch (pre-existing and shared with context_warn/mark_checkpoint; the fix belongs in lib_context.epoch); SKILL.md:39 writes `--check <session-id>` where :190 uses "$CLAUDE_CODE_SESSION_ID" — a wrong id reads as "not armed" and the unattended checkpoint silently never happens; two non-fix commits where §1 wants one (already on the record). Nits: README "the mid-turn turn gate" stutter + orphan line; ending-the-session.md:80 is 132 chars.
- notes: lib_context also gained mirror_off and exact_fresh (mechanical extractions, no direct unit test); the turn gate's DUE line is more precise than context_warn's in the unresolved auto-compact case (possible follow-up).
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE fadd0ed (opus): checkpoint_in_flight() + a `--checkpointing <sid>` CLI the skill runs first in every path (writes checkpoint_started {epoch, at}); L.mark_checkpoint pops it at Step 4b where checkpoint_epoch takes over. While it stands the hook prints nothing and --check says "not armed: a checkpoint is already underway". The record is read defensively — another epoch, a malformed shape, a future stamp, or age past CHECKPOINT_GRACE_S (30 min) all read as not-in-flight — so an abandoned checkpoint cannot silence the gate for the epoch; the command never fails a checkpoint (unwritable state → says so, exit 0). Reviewer's case reproduced before and after (45K fires; then 30K/18K/1K all print {}). +14 tests; 660 context-guard tests OK; the 12,832-case safety sweep re-run, 0 mismatches. Lows a/b/c/e fixed. Low (d) fixed in turn_gate.armed() instead of lib_context.epoch: the offered fix breaks test_statusline_state.test_bad_epoch_in_state_does_not_blank_line, which pins the raise as a deliberate signal (the status line shows "ctx --" rather than a confident wrong epoch) — accepted.
librarian on the implementer's open questions: (1) no hook-side belt for now — the stand-down depends on the skill's opening command, and a belt that never escalates hard → hard_nofit would withhold the "a checkpoint no longer fits" advice exactly when it matters; the --check answer and the doc sentence carry it, and the reviewer can dispute this. (2) CHECKPOINT_GRACE_S 30 min stands (it matches the stamp window); a checkpoint whose Step 4 flush exceeds it is rare and degrades to today's behaviour.
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at fadd0ed: NEEDS_CHANGES. Round-1 medium fixed and replayed on both shas (18K into a checkpoint: 850daed speaks, fadd0ed silent); stand-down defensive on every shape (future stamp, other epoch, not-a-dict, NaN/Inf at, 31 min) — all speak; four mutations pin the new behaviour; safety property intact (4,335 cases, 0 mismatches); --checkpointing cannot fail a checkpoint (rc 0 on every hostile id and an unwritable dir); 660 tests.
- [medium] turn_gate.py:139-155 + SKILL.md:25-35 — armed() tests checkpoint_in_flight BEFORE the record's epoch and tier, so running the skill's opening command first masks every real not-armed reason as "a checkpoint is already underway", whose documented response is to continue; and the skill puts the stand-down "first, in every path", i.e. the order that defeats the anti-forgery confirmation is the one the file instructs. Reproduced on a genuine DUE record and on a HARD record from an earlier epoch. Pass: move the three-line block below the epoch and tier tests (the reviewer ran it: 660 tests stay green); state the order in SKILL.md (confirm with --check, then stand down).
- [medium] turn_gate.py:171-184 — --checkpointing goes through L.update_state, which CREATES a state file for whatever id it is handed, defeating mark_checkpoint's mistyped-id refusal: with $CLAUDE_CODE_SESSION_ID unset, `mark_checkpoint.py typo-id` refuses on an untouched id but succeeds after `--checkpointing typo-id` — the gate is stood down on a phantom session while the real one stays armed and hard-blocks the operator. Pass: refuse and write nothing when the state file does not exist, mirroring mark_checkpoint's guard, with a test.
- [low] CHECKPOINT_GRACE_S is wall time but the risk it bounds is tokens: an abandoned checkpoint buys 30 min of total silence starting at ≤60K left (reproduced at 1K left, silent at 29 min). Recording tok beside at and lapsing on growth past CHECKPOINT_MIN_TOKENS bounds it in the right unit, two lines.
- low: commit layout (known). nit: a malformed top-level epoch blames the state dir.
librarian: REVERSING my second settlement — the reviewer is right that the grace bounds the wrong unit, and the two-line token lapse is cheap; take it. My first settlement (no hook-side escalation belt) stands, and the reviewer agrees with it.
dispatch: implementer opus — fix round 2 (resume)
fix r2 DONE ead6975 (opus): checkpoint_in_flight moved last in armed() so it can only soften an answer that was otherwise ARMED (a genuine DUE record plus a stand-down now answers "not HARD"; a four-shape sweep confirms no reason is masked); SKILL.md no longer says "first, in every path" — the stand-down runs after Step 0 or after --check confirms, with a paragraph on why running it first answers every question the way a forged marker wants; --checkpointing refuses an id with no state file (verified: no file written, and mark_checkpoint still refuses afterwards); the record carries tok and lapses on either clock; the malformed-epoch diagnosis. 663 tests; safety sweep 12,832 cases 0 mismatches.
librarian on the implementer's open question about the boundary: WIDEN it to 2× CHECKPOINT_MIN_TOKENS. 20K is the lean path's cost, and the failure the stand-down exists to prevent — a checkpoint told to abandon one step from the mark — is worse than the extra silence; Step 4a committing several repos is exactly the case that outgrows 20K. The implementer's reading (speaking is correct once a checkpoint genuinely no longer fits) stands above that line.
dispatch: implementer opus — widen the lapse budget to 2× and move the boundary test, then reviewer opus — review r3 (resume)
