---
id: spike-destructive-action-safety-for-unat-6e13
title: "spike: destructive-action safety for unattended agents (dangerous-rm sub-agent stalls, recoverable deletes)"
short_display_name: permission pop-up and delete safety
type: spike
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - operator message 2026-10-15; .claude-sandbox/temp/spike-agent-deletion-safety.md
---

Operator 2026-10-15: dropped .claude-sandbox/temp/spike-agent-deletion-safety.md to file as a work item for the tool permission pop-ups (dangerous-rm prompts stalling sub-agents with no auto-deny) and recoverable deletes. Workstreams E1-E7; E1 (stop the stall, deny hook) highest. Acceptance per the doc section 7. Overlaps b2df's guard hook (decisions 233-239). Launcher snapshots (E2) and OpenCode parity (E7) likely belong to claude-sandbox.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
brief: the operator's spike doc copied to .claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/brief-operator-spike.md (temp/ is scratch)
decided: plan mode first (spike); experiments that need nested claude runs (E1 steps 1, 3, 5) wait for the operator, per the standing rule; desk research, design and harmless local probes proceed
dispatch: planner opus high — spike plan, E1 first; fold b2df guard-hook overlap; placement of the hook
agent: planner a17fe67421b5a97f3 plan round 1
return: planner DONE .claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13 (00_initial.md; E1 = L1 PermissionRequest backstop + L2 PreToolUse predictor R1-R6; home: new hook plugin shell-guard; merge b2df guard as a second rule pack (234 moot); OQ1-OQ9; unverified: L1 firing in sub-agents, hook deny under bypass, agent_id in input)
baseline: 77165043a85c70a4e8c46e5edaa7bf1b318815c5e8f2cd655220d19f0c4f8f56  00_initial.md 793399525965e9c1965ca5dce53cb3ecc4f7dae72a200064d547b3ab2450e126  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer afdc46fe247e2b56b plan round 1
verdict: NEEDS_CHANGES plan round 1 (16: 5 medium — -p denial is documented (headless) so the stall is interactive-only; X6 must run interactive bypass; L2 misses documented forms (logs/*/*, var+top-level name, trailing substitution, backslash, additional-dir globs); aim may be two aims and F2's row promises F7; OQ vs b2df 233-239 mapping; brief section 7 deliverables map; lows: R4 vs #94704 semicolon cd, L1 scope wording, L1 message for non-rm prompts, deny reason for stricter rules, R6 basis, X4 cwd, F7 files, nits)
dispatch: planner opus high — resume, plan fix round 1
agent: planner a17fe67421b5a97f3 round 2
return: planner DONE .claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13 (01_review-round-1.md; all 16 applied, 5 argued differently: aim fixed from F2, parenthetical grows at F7; L2 re-cut N1-N8 + G1-G4; b2df 233-239 mapping with revised: line)
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer afdc46fe247e2b56b plan round 2
verdict: NEEDS_CHANGES plan round 2 (15 of 16 closed; new: A N1 lets ${HOME:?}/* through though docs say use a literal for normally-set vars; B b2df map's revised: lines break the decision doctrine (close as superseded, rewrite cards); C folding 233 drops its guidance-only option; D G2 ambiguous on ${T:?}; lows E 236 ask options recreate the stall, F N2 name list fixed, G catalog parenthetical)
dispatch: planner opus high — resume, plan fix round 2
agent: planner a17fe67421b5a97f3 round 3
return: planner DONE (02_review-round-2.md; A-G applied; D chose drop G2; 233 stays as revised card (a) build / (c) guidance only; OQ1-OQ9 + b2df 233)
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer afdc46fe247e2b56b plan round 3
verdict: NEEDS_CHANGES plan round 3 (A-G closed; H medium: bare normally-set operand "${HOME:?}" / "${PWD:?}" / "${PWD:?}/.." passes every L2 rule — map in N8; lows J 236 (b) unverified premises, L 233 revised line references OQ5 before it exists; nits I reason line, K 233 letters and (z))
dispatch: planner opus high — resume, plan fix round 3 (exact fixes given)
agent: planner a17fe67421b5a97f3 round 4
return: planner DONE (03_review-round-3.md; H-L applied; N8 (b) fixed mapping HOME/PWD/TMPDIR/OLDPWD from the hook env)
dispatch: reviewer opus high — resume, plan review round 4
agent: reviewer afdc46fe247e2b56b plan round 4
verdict: CLEAR plan round 4 (H-L closed; no regressions)
note: spike plan done; OQ1-OQ9 raised as 242-250 with b2df's revised 233/236/237 and closed 235 in one store commit (03 § Rollout″)
decision 242: 6e13 OQ1 — where do the shell guard hooks live? — options: (a) one new hook-owning plugin holding the stall fix and b2df's store pack [recommended] | (b) two new plugins, one per guard | (c) inside sandbox, beside its checkout guard | (d) inside dev-flow | (z) decide later
  raised: 2026-10-15T07:17Z
  what: the home of the dangerous-delete stall fix (E1) and, if built, b2df's store guard
  why now: the spike plan cleared; nothing can be built until the home is picked
  why ask: scope — a new plugin changes the marketplace's shape, which is the operator's call
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) one plugin, one parser, one Python start per Bash call; (b) two of each; (c) stretches sandbox's aim; (d) breaks README principle 3 (dev-flow owns no hooks) · later: blocks F2-F7 · reach: every session with the plugin · undo: move files before the first push; after it, a rename
  (a) one new plugin — catalog row, hooks.json, tests; closes b2df 234 as superseded
  (b) two plugins — each carries its own copy of the shell lexer (plugins cannot share code)
  (c) sandbox — the stall also happens outside claude-sandbox, so the aim stretches
  (d) dev-flow — not allowed by placement rule 1 as written
  (z) decide later — the stall fix waits; sub-agents keep stalling on dangerous-rm prompts
  rec: (a) · basis strong — README/CLAUDE.md placement rules read; two reviews agreed
  basis: documented — README principle 3, CLAUDE.md § Placement rules (read)
  unknown: none
decision 243: 6e13 OQ2 — the new plugin's name? — options: (a) shell-guard [recommended] | (b) command-guard | (c) local-data-guard (b2df's name, widened) | (d) another name | (z) decide later
  raised: 2026-10-15T07:17Z
  what: the plugin name (provisional, as every plugin name here)
  why now: needed before F2 writes the catalog row
  why ask: your preference — no fact settles a name
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a)-(d) differ only in the name · later: blocks F2 · reach: catalog, install commands · undo: rename before the first push is free
  (a) shell-guard — names what it reads: shell commands
  (b) command-guard — wider, near an existing third-party tool's name
  (c) local-data-guard — b2df's name, but the stall fix is not about data
  (d) your name
  (z) decide later — F2 waits
  rec: (a) · basis partial — preference; (a) matches the aim clause
  basis: inferred — from the aim clause in 01/02
  unknown: none
decision 244: 6e13 OQ3 — where do the two layers run? — options: (a) the backstop (L1) in sub-agents and teammates in bypass mode; the pre-check (L2) in every agent in bypass mode [recommended] | (b) both in sub-agents only | (c) (a) plus auto mode | (d) (a), then L1 narrowed by agent type after experiment X3 | (z) decide later
  raised: 2026-10-15T07:17Z
  what: the scope of L1 (deny the permission prompt itself) and L2 (deny an unresolvable delete before it runs)
  why now: raised with the plan; blocks nothing (status quo default (a))
  why ask: scope — L1 denies prompts an attended operator could have answered
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) the main agent keeps its own prompts, sub-agents never stall; (b) the main agent gets no pre-check; (c) also judges auto-mode sessions; (d) narrower L1 later · later: none, builds as (a) · reach: bypass sessions with the plugin · undo: a config change
  (a) as recommended
  (b) sub-agents only — main-agent deletes still meet the native prompt (it times out at 2 min)
  (c) plus auto — auto mode has its own classifier; doubled judgement
  (d) (a) now, narrowed once X3 shows agent_type
  (z) decide later — builds as (a)
  rec: (a) · basis partial — L1 firing in sub-agents is unverified until X3
  basis: documented — permission-modes, hooks (fetched 2026-10-15); unverified — PermissionRequest carries agent_id (X3)
  unknown: whether L1 fires at all in a sub-agent (X3)
decision 245: 6e13 OQ4 — how strict is the pre-check? — options: (a) the native-mirroring rules N1-N8 plus stricter G1, G3, G4, kept under the plan's keep bar [recommended] | (b) native-mirroring rules only | (c) the brief's regex as given | (z) decide later
  raised: 2026-10-15T07:17Z
  what: which deletes L2 refuses
  why now: raised with the plan; blocks nothing (default (a))
  why ask: your preference — false positives cost retries, false negatives cost stalls
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) more refusals with a rewrite each, tuned by the FP measurement; (b) fewer refusals, unguarded $X deletes pass; (c) known misses (logs/*/*, $HOME) · later: none · reach: every bypass Bash call · undo: rule toggles
  (a) as recommended — kept if FP ≤ the keep bar, tuned by measurement
  (b) native only — only what would prompt anyway
  (c) brief regex — misses documented forms (review round 1)
  (z) decide later — builds as (a)
  rec: (a) · basis partial — FP rate unmeasured until F5
  basis: documented — permission-modes § critical paths; reported — #94704, #100848
  unknown: the real FP rate
decision 246: 6e13 OQ5 — how does the guard reach sessions already running? — options: (a) one interim copy in your user settings for all packs, installed on your explicit yes [recommended] | (b) plugin only: sessions get it on their next reload | (c) claude-sandbox's managed settings | (z) decide later
  raised: 2026-10-15T07:17Z
  what: interim delivery before every session reloads the plugin
  why now: plugin hooks reach a session only after /reload-plugins; settings hooks are picked up live
  why ask: reach — user settings are the host file and also run in your host sessions
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) live at once everywhere, including host sessions, removed by a tracked item later; (b) each session after its reload; (c) only sandboxes, via a claude-sandbox change · later: blocks F6 · reach: (a) every session on the machine · undo: delete the settings entry
  (a) on your yes at that moment — closes b2df 235 as superseded
  (b) plugin only — no settings write
  (c) managed settings — claude-sandbox's change, not this repo's
  (z) decide later — F6 waits; the plugin alone ships
  rec: (a) · basis strong — documented hook reload behaviour
  basis: documented — https://code.claude.com/docs/en/hooks (settings file watcher; plugins need /reload-plugins)
  unknown: none
decision 247: 6e13 OQ6 — who runs the experiments that need nested Claude sessions? — options: (a) you | (b) an agent you authorise, in a throwaway sandbox container (the 24-hour soak as an interactive launch) [recommended] | (c) skip X3 (L1 stays unverified) | (z) decide later
  raised: 2026-10-15T07:17Z
  what: who runs X1-X4 and X6: repro the stall, test hooks in sub-agents, the native-check oracle, the 24-hour soak
  why now: standing rule: nested headless claude runs wait for the operator
  why ask: authority — the standing rule reserves nested claude runs to you
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) your time; (b) agent time and quota in a disposable container; (c) L1 ships unproven · later: blocks the keep/tune verdict and the 24-hour acceptance · reach: one throwaway container · undo: two-way
  (a) you run them from the plan's steps
  (b) an authorised agent — throwaway container, versions recorded
  (c) skip X3 — L1 ships on the docs' word only
  (z) decide later — the build can proceed; acceptance waits
  rec: (b) · basis strong — the steps are written; isolation is a fresh container
  basis: documented — the brief's rules § 2
  unknown: quota cost of a 24-hour interactive soak
decision 248: 6e13 OQ7 — may an agent read session transcripts to measure false positives? — options: (a) an agent reads them read-only, output redacted, only aggregates in the series [recommended] | (b) you run the measurement | (c) synthetic commands only | (z) decide later
  raised: 2026-10-15T07:17Z
  what: the false-positive measurement's data source
  why now: needed for the F5 run
  why ask: reach — transcripts hold your conversations and may hold secrets
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) real FP rate, redacted; (b) your time; (c) no real-world rate · later: blocks the F5 run · reach: ~/.claude/projects transcripts, read only · undo: delete the scratch output
  (a) read-only, redacted, aggregates only
  (b) you run it
  (c) synthetic only — the keep bar rests on guesses
  (z) decide later — F5's run waits
  rec: (a) · basis strong — read-only, nothing committed but aggregates
  basis: inferred — the brief § E1.4
  unknown: none
decision 249: 6e13 OQ8 — implementation language? — options: (a) Python standard library with a hand-written quote-aware lexer [recommended] | (b) Go with mvdan.cc/sh | (z) decide later
  raised: 2026-10-15T07:17Z
  what: the hook's language
  why now: raised with the plan; blocks nothing (default (a))
  why ask: your preference — the brief prefers Go for custom tools
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) matches every other hook here, no build step; (b) a real shell parser, a compiled binary to ship per platform · later: none · reach: the plugin · undo: a port later
  (a) Python — port to Go only if the measurement traces misses to the lexer
  (b) Go — a binary per platform in a plugin
  (z) decide later — builds as (a)
  rec: (a) · basis partial — Go's parser is better; Python's shlex is not enough (probed)
  basis: observed — shlex drops newlines and splits $(…) (planner probe, 2026-10-15)
  unknown: whether the hand lexer's misses matter
decision 250: 6e13 OQ9 — where do the other workstreams (E2-E7) go? — options: (a) launcher snapshots (E2) and the host-side trash service to claude-sandbox, OpenCode parity (E7) to opencode, the rest as spikes here, E2 first [recommended] | (b) all in this spike | (c) E2 only, the rest dropped | (z) decide later
  raised: 2026-10-15T07:17Z
  what: routing of snapshots, trash, command-guard evaluation, auto mode, agent-native FS and OpenCode parity
  why now: raised with the plan; blocks only those follow-ons
  why ask: scope — routes work into other repos
  context: spike 6e13 plan CLEAR at review 4 (.claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/) — then: none
  impact: → (a) each repo owns its part, snapshots first (btrfs here, reflink works); (b) this repo plans the launcher it doesn't own; (c) drops trash/guard/auto-mode research · later: blocks the E2-E7 follow-ons only · reach: claude-sandbox, opencode · undo: re-route
  (a) as recommended — relays sent to claude-sandbox
  (b) all here
  (c) E2 only
  (z) decide later — E1 proceeds alone
  rec: (a) · basis strong — repo ownership per CLAIM/README
  basis: observed — checkouts on btrfs, reflink copy works (planner probe 2026-10-15)
  unknown: none
