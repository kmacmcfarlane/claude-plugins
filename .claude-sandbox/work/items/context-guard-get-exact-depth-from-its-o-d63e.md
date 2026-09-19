---
id: context-guard-get-exact-depth-from-its-o-d63e
title: "context-guard: get exact depth from its own hooks, not the status line"
type: feature
status: doing
priority: 2
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:27Z
created: 2026-09-17
updated: 2026-09-19
refs:
  - operator message 2026-09-17
---

Operator 2026-09-17: remove context-guard's dependency on the status line as its depth sensor; context-guard should own its own hook. Librarian facts: hooks receive no context-window size or usage (docs: common fields session_id, prompt_id, transcript_path, cwd, scratchpad_dir, permission_mode, effort, hook_event_name; none for window/usage). Token count is already exact from transcript usage blocks (cross-checked equal to the status-line record). The only missing input is the WINDOW SIZE (200K vs 1M), which the model id in transcripts ('claude-opus-5') and settings ('opus') does not carry. The 2.1.273 binary shows SessionStart hooks receive an undocumented 'model' field and there are PreModelSwitch/PostModelSwitch hook events with from_model/to_model — if those carry the 1M variant, hooks can know the window without the status line. Step 1 (spike): capture the live payloads. Step 2: plan + operator review. Step 3: implement on the factored layout (context-guard), fable.

## Handoff
- doing: review round 4 (final) running; impl at a1188d3
- next: CLEAR -> land + close 6d60; else block + ask operator
- blocked: decision 14
- learned: —

## Spike result (live capture, 2026-09-17; findings copied to .claude-sandbox/investigations/hook-window-capture-findings.md)
- No hook payload field or hook env var carries the window, on any of 6 headless runs (opus, opus[1m], sonnet,
  sonnet[1m], haiku, resume-with-switch). SessionStart's optional `model` never appeared. Model-switch hooks did
  not fire headless.
- The transcript carries an `attachment.type:"model"` line at session start and on every model change, with
  identity.modelId (e.g. "claude-opus-5[1m]") — readable by a hook.
- The model id does not decide the window alone: plain opus-5 / sonnet-5 / fable-5 / opus-4-7+ are natively 1M;
  haiku-4-5 is 200K; overrides: CLAUDE_CODE_DISABLE_1M_CONTEXT, CLAUDE_CODE_MAX_CONTEXT_TOKENS (with compaction
  disabled), and an account-side 1M-credits cap that a hook cannot see.
- Status line in -p mode: did not fire. Its context_window_size remains the only exact source.
decision 14: depth source for context-guard — (a) hook-derived window (transcript model line + model table + env
  overrides) as the default, status line optional and wins when present, derived depth warns but never hard-blocks
  (recommended); (b) keep the status line as the required sensor (status quo); (c) hook-derived window allowed to
  hard-block.
- OPERATOR 2026-09-17: rejects "only the status line is exact"; wants context-guard's hook to do what the status
  line does, duplicated logic acceptable. Librarian agrees on the approach: the status line computes nothing — Claude
  Code hands it context_window_size — so the hook must duplicate Claude Code's own window selection instead:
  transcript `attachment.type:"model"` identity.modelId → [1m] suffix / native-1M model table → env overrides
  (CLAUDE_CODE_DISABLE_1M_CONTEXT, CLAUDE_CODE_MAX_CONTEXT_TOKENS with compaction disabled) → the account-side 1M
  gate, which IS cached on disk in ~/.claude.json (seen: s1mAccessCache{<account>:{hasAccess,hasAccessNotAsDefault,
  timestamp}}, cachedExtraUsageDisabledReason, oauthAccount.hasExtraUsageEnabled) — exact semantics to be pinned in
  the plan by reading the 2.1.273 selection code. Tokens: transcript usage (already exact).
decision 14 (revised): (d) hook derives the window by duplicating Claude Code's selection logic, including the
  cached account gate; the derived depth may hard-block when every input resolved (known model, readable fresh
  cache); unresolved input → warn-only; status line, when installed, is a cross-check that wins on disagreement and
  logs the mismatch so drift in the duplicated logic is visible. Recommended; awaiting the operator.
- CORRECTION (librarian): the config scan that found the cached gate printed one stored MCP API key value from
  ~/.claude.json into this session's tool output; operator told, rotation suggested.
- OPERATOR 2026-09-17: decision 14 ANSWERED — (d) mirror Claude Code's window selection in context-guard's hook
  ("assuming there's really no other way, I'm cool with mirroring the claude code internals"). Librarian confirmed no
  documented third way (hooks cannot query the harness). Status line becomes an optional cross-check; this also frees
  the status line to become its own plugin with no hard dependency (spike fb55).

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

- 2026-09-18 (peer "agent front-ends", ex "Paseo stop-gap"): headless front-ends depend on this: Paseo option B (Claude Agent SDK provider wrapping claude-sandbox) has no status line, so exact depth needs this mirror. Option A (PTY terminal tabs running claude-sandbox) does not. Source: operator-attention research/findings/p1-paseo-stopgap.md; trial item operator-attention 6dc1.

## Plan (2026-09-18, opus plan-writer; .claude-sandbox/investigations/d63e-window-mirror/plan.md)
- CORRECTION to decision 14's premise: Claude Code 2.1.277 never reads s1mAccessCache/hasAccessNotAsDefault (stale leftover, 2026-02-24). cachedExtraUsageDisabledReason gates only the /model picker; hasExtraUsageEnabled only usage-limit messages. The real account 1M gate is an in-memory flag set by a 429 "usage credits required for long context" error, which is written to the transcript -> the hook never needs ~/.claude.json.
- Mirrors lf(model, sdkBetas): native-1M table, [1m] rule, CLAUDE_CODE_DISABLE_1M_CONTEXT (caps all at 200K), CLAUDE_CODE_MAX_CONTEXT_TOKENS (first under DISABLE_COMPACT, last for custom models). 11-step algorithm, 21-row truth table; new window_rules.py; depth() order: fresh status line > derived resolved (may block) > derived unresolved (warn) > inferred; mismatch log window-mismatch.jsonl demotes that CC version to warn-only; new SessionStart/PostModelSwitch bookkeeping. Size M (~700 lines incl. tests), fable implementer + reviewer.
- Security: a directory listing printed the served-catalog cache filename (contains account/org UUIDs) into the plan-writer's tool output; no ~/.claude.json values printed beyond allowed booleans/timestamps/keys.
decision 31: approve the d63e plan for implementation (fable, or opus fallback while fable is out)
decision 32: drop ~/.claude.json from the design entirely (plan rec: yes)
decision 33: CC version the table was copied from: record + demote to warn-only after a real mismatch (plan rec) vs gate hard-block on exact version
decision 34: auto-compact window (CLAUDE_CODE_AUTO_COMPACT_WINDOW etc.): follow-up item, not this one (plan rec)

OPERATOR 2026-09-19: decision 31 approved; 32 a (drop ~/.claude.json entirely); 33 a (record CC version, demote to warn-only after a real mismatch); 34 b (include the auto-compact window in d63e).

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — fable unavailable (unknown); fallback (rule 3: non-trivial HARD-gate code)

## Round log
impl (opus fallback): DONE d513ea9 + cf69579 (window_rules.py 2.1.277; measure(); 357 tests; 42-case gate matrix: existing users identical except E7 stale+model line now blocks and A3 configured auto-compact window now gates fresh-sensor users). Librarian accepts A3 as decision 34b working as intended (the gate should respect the real compaction threshold); reported to the operator. Kill switch CONTEXT_GUARD_DERIVE=off. Timing 11->49ms fresh, 71->95ms none on a 52MB transcript.
dispatch: reviewer opus — fable unavailable (unknown); fallback

review round 1 (opus, fable fallback): NEEDS_CHANGES — critical 1 (autoCompactWindow not range-validated: 50000 blocks at 20K), 2 (settings window resolved though --settings/--setting-sources can override), 3 (legacy autoCompactEnabled in ~/.claude.json unobservable), 4 (credits latch matched by phrase, not apiError), 5 (provider gate on the 1M beta); high 6 (overestimate -> precompact defers needed compactions; latch key unchecked), 7 (stale proc record trusted); medium 8 (URL.host/port, CLAUDE_CODE_USE_GATEWAY), 9 (README), 10 (HARD STOP escapes; CLAUDE_KIT_CONTEXT_WINDOW pin no longer honoured); lows 11-12, nit 13. Librarian decisions: false blocks are never acceptable — every unobservable override makes the input unresolved (warn-only); precompact_gate defers only on exact depth; the pin beats derivation; 6d60 docs folded in.
dispatch: implementer opus fix round 1 — resume (fable unavailable)

fix round 1 (opus): DONE 26f7c7b + 6db9fd3 (all 13; 387 tests; kill switch byte-identical on 42 cases; scan cache: 16ms steady state). Librarian accepts: precompact keeps main's exact-or-inferred deferral (derived never defers); an absent remote-settings cache = no remote policy; macOS (no /proc) = warn-only above 200K. 6d60 docs folded in.
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): NEEDS_CHANGES — critical 1 (proc_info trusts any ancestor with a registry entry; shared registry across sandboxes -> wrong cmdline), 2 (policy tier is first-wins, not merged), 3 (CLAUDE_CODE_MANAGED_SETTINGS_PATH unread); medium 4 (remote policy may live in a storage backend, not remote-settings.json), 5 (escapes missing when the auto-compact block has a fresh status line); lows 6-8. Model window now safe. Librarian decision: adopt the simplest safe rule — a settings-derived auto-compact window is unresolved whenever any policy tier is present, CLAUDE_CODE_MANAGED_SETTINGS_PATH is set, remote policy cannot be ruled out, or the ancestor is not verified as the Claude Code binary.
dispatch: implementer opus fix round 2 — resume

fix round 2 (opus): DONE c27cd37 + 4aa7c87 (verified claude ancestor; any policy / MANAGED_SETTINGS_PATH / unrulable remote policy -> unresolved; auto-compact window never hard-blocks on 2.1.277; sidechain cache; escapes on mirror-bounded blocks). Librarian: keep the resolution machinery (REMOTE_POLICY_RULED_OUT=False) for a future CC.
dispatch: reviewer opus review round 3 — resume

review round 3 (opus): NEEDS_CHANGES — critical 1: proc_info walks past an unregistered child claude (CLAUDE_CODE_CHILD_SESSION=1 children do not register) and borrows the outer claude's key, so a nested run's credits latch hard-blocks the operator's own session (reproduced). Everything else holds; playbook matches code.
dispatch: implementer opus fix round 3 (last) — fable unavailable (unknown); fallback (rule 3: last round after a critical)

fix round 3 (opus fallback): DONE a1188d3 (walk stops at the first claude; CHILD_SESSION unverified; pidDomain checked; nested probe clean).
dispatch: reviewer opus review round 4 (final) — resume

## Cap
review round 4 (opus, final): NEEDS_CHANGES — no false hard-block remains (0 kill-switch diffs every run); high: CC 2.1.277 sets CLAUDE_CODE_CHILD_SESSION=1 (and CLAUDE_PID) in EVERY command hook env, so the new env check marks every real session unverified -> derived windows above 200K never hard-block inside real CC (safe but the mirror's main purpose is inert). Fix: drop the env test; key the first claude ancestor only when its pid == the hook's CLAUDE_PID. CAP HIT (4).
decision 37: d63e cap: (a) one extra round (key on CLAUDE_PID), re-review, land [recommended]; (b) land now safe-but-inert (200K windows and DISABLE_COMPACT+max tokens still block; above 200K warns), fix in a follow-up; (c) hold unmerged.

OPERATOR 2026-09-19: decision 37 a — one extra round (key on CLAUDE_PID).
dispatch: implementer opus fix round 4 (extra) — fable unavailable (unknown); fallback — resume
