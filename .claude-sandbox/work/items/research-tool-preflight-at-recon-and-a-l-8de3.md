---
id: research-tool-preflight-at-recon-and-a-l-8de3
title: "research: tool preflight at recon and a lane PDF rule (Read branch)"
type: feature
status: done
priority: 2
parent: research-tooling-the-tools-research-agen-04f7
created: 2026-09-24
updated: 2026-09-24
closed: 2026-09-24
refs:
  - agent-research 39ae series 02 § Preflight
---

Port the ungated core of agent-research's research-tooling spike: the POSIX preflight script (02 § Preflight, 29 cases tested under dash and bash, env stubs RESEARCH_PREFLIGHT_*) run at research Step 5.1 recon, naming the missing package and the one-line fix per environment, never telling a session to create a project Dockerfile; the lane PDF rule branch (a) (Read whole PDF up to ~5 MB; WebFetch-saved file; else could-not-verify) in research-lane.md; plus the three review lows (matched Dockerfile still exists and chain position before nearer=; pwd -P fallback; OQ7 gates pip only when OQ5 allows). Unattended branch waits on decision 85; branch (b) waits on 86. Opus implementer (script + agent contract).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-24 claimed by Kyle-McFarlane@bf9f9839222c
target: branch worktree-research-tool-preflight-at-recon-and-a-l-8de3 at .claude/worktrees/research-tool-preflight-at-recon-and-a-l-8de3, base main (fe9dff0)
dispatch: implementer opus — script + agent contract
agent: implementer a6ece86b8174847a8 round 1
return: implementer round 1 DONE_WITH_CONCERNS b92eabd (verifier PDF rule and run-record lane-prompt Tools: line not in scope — filed)
dispatch: reviewer opus — fresh
agent: reviewer a2c8ec6d8fe0d1271 round 1 at b92eabd
verdict: reviewer round 1 CLEAR at b92eabd (6 low, 1 nit) — taking all: shipped text cites an internal decision number, states an inferred limit as fact, and tells an unattended run to ask
dispatch: implementer opus — resume, fix round 1 (lows)
agent: implementer a6ece86b8174847a8 fix round 1
return: implementer fix round 1 DONE_WITH_CONCERNS 1c526e3 (one context-guard failure then two passes — the known timing flake, d1e3)
dispatch: reviewer opus — resume, round 2
agent: reviewer a2c8ec6d8fe0d1271 round 2 at 1c526e3
verdict: reviewer round 2 CLEAR at 1c526e3 (2 nits: set -f for glob chars in paths; run-record.md:22 width — carried to 822c)
landed: 5c7025b (merge --no-ff into main)
- 2026-09-24 done
