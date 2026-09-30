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
