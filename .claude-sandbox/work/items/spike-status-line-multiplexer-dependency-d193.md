---
id: spike-status-line-multiplexer-dependency-d193
title: "spike: status line multiplexer — dependency plugin vs self-contained; plugin-dependency research"
type: spike
status: done
priority: 1
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
refs:
  - operator message 2026-09-19
---

Operator 2026-09-19: the status line multiplexer/hook/dispatcher keeps being needed. Research how others implement status line multiplexing/composition and how Claude plugin authors handle one plugin depending on another (web search), and what the Anthropic marketplace/plugin framework offers (dependencies, auto-install, prune). Then recommend: A) a new plugin others depend on, or B) one plugin that provides the status line and holds the things that need it (operator leans against a kitchen-sink horizontal layout, just refactored away from it). Acceptance: an investigation series with sourced findings, options with impact, a recommendation; decision goes to the operator.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009
- 2026-09-21 done: series .claude-sandbox/investigations/d193-statusline-multiplexer/; features statusline-hub-f1-new-plugin-tee-command-bfe2..statusline-hub-f5-wrap-mode-run-a-foreig-7e71

## Dispatch
- dispatch: researcher opus — judgement (doctrine/marketplace shape trade-off); plan variant, no worktree; series at .claude-sandbox/investigations/d193-statusline-multiplexer/

## Result
- research DONE (opus): series .claude-sandbox/investigations/d193-statusline-multiplexer/ (start at 03_recommendation.md). Framework `dependencies` exist but are hard only (unsatisfied → dependent disabled; no optional kind); nothing lets a plugin own or compose the status line. Recommends C: statusline stays sole slot owner and becomes the dispatcher (segment drop dir, embed mode, then wrap mode); everyone else soft-depends on the file contract.
decision 38: packaging — (c) statusline becomes the dispatcher, file-drop segments, soft contract [recommended]; (a) separate multiplexer plugin via hard `dependencies`; (b) one plugin absorbs the status line's consumers.
decision 39: aim — (a) widen statusline's catalog aim to "the status line and the segments others add" (no new plugin) [recommended]; (b) a new plugin for the dispatcher.
decision 40: wrap-mode first run when a foreign statusLine exists — (a) stay deferred, one-line hint naming /install-statusline --wrap [recommended]; (b) ask once on first run.

## Operator direction 2026-09-19 (answers 38/39 in shape; pending round 2)
- Wants an independent utility: one unified status-line dispatcher script that lets multiple plugins hook into Claude Code's status-line call; statusline (context/quota display), analytics (usage-report) and context-guard depend on it. context-guard only READS the status-line data; statusline's aim is display, as one hook of the dispatcher.
- Concern: incompatible with other plugins/users' status lines — if a popular third-party dispatcher exists, requiring it may be better.
- Asked to verify by web search that the data is NOT available another way (positive confirmation: open GitHub issues asking for it). Round 1 cited open #84904, #92853, #83289, #77910, #76988 but did not sweep alternative channels (OTel, transcript, OAuth usage endpoint, SDK/-p output, /context, env).
- dispatch: researcher opus — round 2, new serial superseding 03 where needed

## Round 2 result
- research DONE_WITH_CONCERNS (opus): serials 04–07 (start at 07_recommendation-dispatcher.md; 07 supersedes 03). No other live channel for window size or rate_limits in an interactive session [V]; confirming open issues #13585 (124 reactions), #84904, #92853, #83289, #77910, none with a maintainer reply. De-facto third-party dispatcher: ccstatusline (Custom Command widgets get full stdin JSON). Recommends option iv: new independent hub plugin owns the slot, tees stdin to the sensor record, runs display hooks; statusline hard-depends on it; context-guard/analytics/dev-flow stay soft readers of the sensor record. First feature: `hub tee` (usable as a ccstatusline widget).
- decisions 38, 39 superseded by the operator direction (new plugin); 40 carried.
- agent notes: ran `jq has` for one key's presence in ~/.claude.json (no value read); stray *_readme.md files a sub-agent wrote into the repo root were moved to the scratchpad (repo root verified clean).
decision 41: hub plugin name — (a) statusline-hub [provisional, recommended by research]; (b) another name the operator gives. Names are API (data dir, settings path); blocks F1.
decision 42: statusline → hub edge — (a) amend principles 2/4: a hard `dependencies` edge is allowed only when the dependent has no function without the support plugin, same marketplace [recommended]; (b) no doctrine change: fold the display into the hub. Data consumers stay soft either way; blocks F3.

## Operator answers 2026-09-19
- 40 → (b) ask to wrap on first run (so the user knows they were wrapped).
- 41 → (a) statusline-hub, approved.
- 42 → (a) amend principles 2/4, BUT first present the current and proposed hard-dependency graph and codify the approach explicitly (doctrine text) — that presentation precedes F3.

## Consumer requirement: claude-analytics (peer agents-61, 2026-09-19)
- Wants a SINK REGISTRY, not a history log: entries {name, command, timeout_ms, display}; after the sensor write, fan out the RAW stdin payload; recording sinks detached (never block render); display sinks hard timeout; a failing sink never blanks the line; dead entries pruned in the existing prune pass; a sink contract doc beside sensor-contract.md. claude-analytics registers its sampler from its own SessionStart hook.
- Reconcile with 07's hooks.d: one registry at CFG/statusline-hub/hooks.d/<name>.json with a kind (display | record); record = detached, raw stdin. Told the peer this path is proposed and lands with hub F2 (record kind could come earlier, with F1 tee). Carry into the F1/F2 briefs.
- agents-61 ack 2026-09-19: their Phase 1 targets CFG/statusline-hub/hooks.d/<name>.json {name, command, timeout_ms, kind}; hub F2 is ours. Their acceptance for the record kind (carry into the F2 brief verbatim): the record hook gets the raw payload byte-for-byte on every render; a crashing or slow record hook leaves the gauge and the sensor record intact. Ping agents-61 (or the claude-analytics repo session later) if path or kind moves.
- agents-61 2026-09-20: agent-telemetry series landed at claude-analytics/.claude-sandbox/investigations/agent-telemetry/ (private sidecar; host repo public). Proposal for the record-hook contract: each hook owns its errors and writes a small health file {last_ok, last_error, error, runs, errors} by atomic replace; hooks.d entry gains an OPTIONAL `health_path`; at render the hub does one small read and shows a one-glyph warning when the last run errored or there is no last_ok within N minutes. Their `ca doctor` catches it end-to-end regardless.
- decision (librarian): accept for hub F2 as OPTIONAL — a silent recording sink that dies unnoticed is the failure mode the gauge exists to prevent, and the cost is one small read of a file the hook already writes. Constraints for the brief: health_path is optional and stays inside CFG; a missing, stale, oversized or malformed health file shows nothing (never an error, never a blank line); the read is capped like every other hub read; no glyph while the hook has never run. Reviewer checks it against the record-kind acceptance (raw payload byte-for-byte; a crashing or slow hook leaves gauge and sensor intact).
- contract correspondence moves to the claude-analytics repo session when the operator switches.

## Closed 2026-09-21
- spike complete: series 00–07; decisions 40 (b ask), 41 (statusline-hub), 42 (a, landed as 5343). Features filed: statusline-hub-f1-new-plugin-tee-command-bfe2, statusline-hub-f2-owner-mode-hooks-d-reg-b28f, statusline-hub-f3-statusline-becomes-a-d-dfa1, statusline-hub-f4-segment-drop-dir-file-d182, statusline-hub-f5-wrap-mode-run-a-foreig-7e71.
