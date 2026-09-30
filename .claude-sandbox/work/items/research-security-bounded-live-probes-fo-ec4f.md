---
id: research-security-bounded-live-probes-fo-ec4f
title: "research security: bounded live probes for the six facts the docs leave open"
short_display_name: security probes
type: task
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/caef-research-security/05_second-opinion-closing.md
  - caef answer 103
---

caef G-probe under answer 103 a: haiku, throwaway directory, a temporary --settings file, public test URLs and a closed loopback port only, at most ~15 sessions, every command and result kept in evidence. Settles the facts F3/F4 build on.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: plan research-security-bounded-live-probes-fo-ec4f /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security
dispatch: planner opus high — G-probe under answer 103 a; results as a new caef serial + evidence
agent: planner a5ed8bf89325b00cd round 1
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security (06_g-probe-results.md; 12 of 15 probe sessions, haiku, CLI 2.1.286; six facts settled, RFC 1918 fetch unsettled (Q20, bounds exclude LAN); A3.11, A3.12, A4.3 added)
note: the harness flagged the planner's return for a settings-json pattern (mentions of --settings files); read as data — no directive in it
note: probe sessions' own Claude Code bookkeeping wrote transcripts, tool-results, session-env, history.jsonl and ~/.claude.json entries under the config dir (needed for the resume and PDF facts); left in place
librarian ruling on Q19: confirm fail-closed — build only the session-id branch; a missing session id denies (the safer branch, reversible later)
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe 00_initial.md f6378546b4596c7a835a823b2e0c7a54c663f0cfe856f8b45d68552ef29ac264 01_probe-evidence-and-review-fixes.md 278af36fbb78ecc54b8502f4de4dc498a5abe086f2ae19fe925b68460222d4a2 02_read-write-rules-composed.md 7cef67d3052866c26fa1b780227e61054b29ce07f16e5fcf0501007c960af92c 03_f3-authority-and-adversary-walk.md dd48c863d6ee6c96a18f72c42aaccf499ec3d1b959d43fbb5c96beb688667642 04_round-4-fixes.md 47e56da84e3fdd2810da222f0dbdf5fd75602f944a0c13d4dd6ed9fbaf5b4c3c 05_second-opinion-closing.md 2e85a92a73234745039df66a4030422645f64e979c2a79a5f3028771fa914795 06_g-probe-results.md 
dispatch: reviewer opus high — plan review round 1 of serial 06 (rule 4)
agent: reviewer ad04a11756bc2fdf2 round 1
verdict: NEEDS_CHANGES round 1 at .claude-sandbox/investigations/caef-research-security
findings:
  1. [medium] 06:20-30 — 108 a's Supersedes misses 05:175 (A3.2 admits transcript dirs), 03:327-329 (Q18 test), walk row 15 (03:249, 04:163), 05 Risk 5's transcript clause; INDEX.md:70 cites A3.1-A3.10 whole
  2. [medium] 06:163-181, 235-236 — facts 5 and 6 settled only in -p sessions without the operator's plugins; A3.11/A3.12 do not carry that scope; the pre-announce live re-check has no pass condition tied to them
  3. [low] 06:145 — S8's server-side negative graded strong though its log was transcribed
  4. [low] 06:192-193 — A4.3's getaddrinfo check has no command/output in evidence
  5. [low] 06:40-43, 86-89; INDEX.md:49 — RFC 1918 half of P5b stated as confirmed; "all six settled"
  6. [low] 06:113-124 — three unexplained plugins in init lines and the global CLAUDE.md loaded; not stated
  7. [low] evidence:15,613,680 — S4 fetched a literal IP httpbin had rotated off
  8. [nit] evidence:332 — S12 settings body not recorded
  9. [nit] 06:200-238 — section order
  10. [nit] INDEX.md:19 — "reach loopback" overstates
notes: fact 5 can use the harness-written deferred_tools_delta difference; Q19 fail-closed is decided (record it in INDEX); IPv4-mapped IPv6 literal test for A4.3
dispatch: planner opus high — resume
agent: planner a5ed8bf89325b00cd round 2
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/caef-research-security (07_probe-serial-fixes.md; 0 new probes; all 10 findings fixed; evidence addendum A1-A6 appended)
baseline: f14d66cd2e1d3f07cb07fdb02c539e85633d52d2255c85fefeacb16870ed21fe 00_initial.md f6378546b4596c7a835a823b2e0c7a54c663f0cfe856f8b45d68552ef29ac264 01_probe-evidence-and-review-fixes.md 278af36fbb78ecc54b8502f4de4dc498a5abe086f2ae19fe925b68460222d4a2 02_read-write-rules-composed.md 7cef67d3052866c26fa1b780227e61054b29ce07f16e5fcf0501007c960af92c 03_f3-authority-and-adversary-walk.md dd48c863d6ee6c96a18f72c42aaccf499ec3d1b959d43fbb5c96beb688667642 04_round-4-fixes.md 47e56da84e3fdd2810da222f0dbdf5fd75602f944a0c13d4dd6ed9fbaf5b4c3c 05_second-opinion-closing.md 2e85a92a73234745039df66a4030422645f64e979c2a79a5f3028771fa914795 06_g-probe-results.md 1aba2061ecc91c141be96754443902ea17effe55fd3941ea555d23c26b46a69c 07_probe-serial-fixes.md 
dispatch: reviewer opus high — resume
agent: reviewer ad04a11756bc2fdf2 round 2
verdict: NEEDS_CHANGES round 2 at .claude-sandbox/investigations/caef-research-security
findings:
  prior 1-10 FIXED
  N1. [high] 07:187-190 — A3.2′ denies any command naming a path under the Claude config dir with no exception for the run's own staging dir (03:139-140 (c1)); in claude-sandbox the temp root is inside the config dir, so local mining breaks; add the staging exception and a sandbox-shaped test
  N2. [medium] 07:211-212, 167-168, 246, 310 — PB-1 claimed "under 103 (a)'s bounds" but runs from the builder's real session with the operator's plugins, no settings file, no throwaway dir
  N3. [medium] 07:211 — PB-1's dispatcher may be a background builder sub-agent (depth 2), not the interactive main thread research uses
  N4. [low] 07:163-166, 224-227 — PB-1 (a) checks transcript sessionId not hook session_id; scratchpad-path id claim contradicts 03:112-113 (fork keeps old path)
  N5. [low] 07:191-198 — A3.2′ tests lack ~, $HOME, ${CLAUDE_CONFIG_DIR}, /home/claude alias, relative, glob, staging-symlink forms
  N6. [nit] INDEX.md:196 — "IP-literal half" should be "RFC 1918 half"
librarian ruling on N2/N3: PB-1 runs from the MAIN THREAD of a disposable interactive session: throwaway cwd, a temporary --settings file, haiku, counted against 103 (a)'s ~15-session bound (12 used) — inside the answer's bounds as written. An interactive session needs the operator, so PB-1 is an operator-attended step, carded when F3 is next; F3's build (20d8) waits for it and does not run unattended tonight. PA-2 (a hand resume mid-run) is carded at announce time.
dispatch: planner opus high — resume
agent: planner a5ed8bf89325b00cd round 3
