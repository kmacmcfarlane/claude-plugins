---
id: librarian-mode-bare-repo-session-name-no-9a3a
title: "librarian-mode: bare <repo> session name, no ' - librarian' suffix"
type: feature
status: done
priority: 0
created: 2026-09-26
updated: 2026-09-26
closed: 2026-09-26
refs:
  - "peer: claude-sandbox - librarian, relaying the operator 2026-09-26"
---

Operator request relayed by claude-sandbox - librarian 2026-09-26 (a request, not an approval; the operator says it can be fixed immediately): drop the ' - librarian' suffix from the librarian-mode session-name convention; the conversation name is the repo name (e.g. brainboy), because claude-sandbox will name tmux windows from it (their item 1d0e, operator decisions 42 and 44). Librarian decision on the peer-discovery trade-off: the bare <repo> name is reserved for the repo's librarian, so a peer still finds it by exact name; any other session working in that repo takes a qualified name (<repo> - <task>). Where: references/session-name.md (canonical form, WANT, the /rename line, status text, the older-forms note now listing '<repo> - librarian'), SKILL.md start/status wording; the quota test fixture name for consistency. Acceptance: the gate asks for the bare name, the old suffixed form reads as an older form, and nothing else in the plugin names the suffixed form.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-26 claimed by Kyle-McFarlane@1827d80083e0
target: branch worktree-librarian-mode-bare-repo-session-name-no-9a3a at .claude/worktrees/librarian-mode-bare-repo-session-name-no-9a3a, base main (a2a3a51)
dispatch: implementer opus — changes what the skill does (the name gate)
agent: implementer a543f6c1a8dd0640b round 1
return: implementer round 1 DONE ff8b274 (session-name.md + test fixture; no other doc named the suffix)
dispatch: reviewer opus — fresh
agent: reviewer a518afe7c5d717dc2 round 1 at ff8b274
verdict: reviewer round 1 NEEDS_CHANGES at ff8b274 — 1 medium (create-repo launches a non-librarian session with the bare <repo> name the change reserves), 1 low (nameSource collision)
librarian decision: keep create-repo as is (the operator names conversations by repo); the reservation becomes advisory — the bare name marks the librarian when one runs, a create-repo first session holding it is expected and is the usual way a repo gets its librarian; on a collision, rename the other session to <repo> - <task> or keep the current name
dispatch: implementer opus — resume, fix round 1
agent: implementer a543f6c1a8dd0640b fix round 1
return: implementer fix round 1 DONE 441de40
dispatch: reviewer opus — resume, round 2
agent: reviewer a518afe7c5d717dc2 round 2 at 441de40
verdict: reviewer round 2 CLEAR at 441de40 (2 low: dangling "reservation"; the collision line tells the librarian to rename another session) — taking both, the second misdirects
dispatch: implementer opus — resume, fix round 2 (lows)
agent: implementer a543f6c1a8dd0640b fix round 2
return: implementer fix round 2 DONE 8b51004
dispatch: reviewer opus — resume, round 3
agent: reviewer a518afe7c5d717dc2 round 3 at 8b51004
verdict: reviewer round 3 CLEAR at 8b51004 (no findings)
landed: da3b1c5 (merge --no-ff into main)
- 2026-09-26 done
