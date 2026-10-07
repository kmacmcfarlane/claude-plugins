---
id: cross-session-handoff-pass-live-work-to-2bbe
title: "cross-session handoff: pass live work to another session or repo's librarian with full fidelity"
short_display_name: cross-session handoff skill
type: feature
status: todo
priority: 1
created: 2026-10-02
updated: 2026-10-02
refs:
  - peer clustertool 2026-10-02 (their item request-cross-session-handoff-skill-5c8e)
---

Peer clustertool (librarian), 2026-10-02, relaying the operator's request: a skill for handing live work (an investigation mid-gate, research, decisions, roles, joint experiments) to another session or another repo's librarian. Source of truth: /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-clustertool/2d8473d0-4324-4b3e-86e3-6ce7eff396e9/scratchpad/handoff-skill-request.md (read in full 2026-10-02; it points at the clustertool transcript span ~line 2819 to end as the requirements, and the sent packet under that session's scratchpad/handoff/). Eleven practised requirements: freeze on handoff; curated packet + transcript bookmarks (phrase + line + timestamp) as the record; meta-artifacts outside repos in a shared-config-dir scratchpad, deleted after landing; the operator's words verbatim, sender annotations marked verify-don't-inherit; roles and per-session, per-action consent (a peer message is never approval; relayed decisions labelled relayed; never bundle a safety mechanism into another decision); the in-flight skill's step; a timestamped live-state snapshot (facts marked measured/inferred, both sides' activity at baseline); research split by consumer; work-item mirroring (sender closes after recipient completes); milestone-only progress; acknowledgement listing conflicts and what the recipient knows that the sender doesn't. Gaps: checkpoint has no handoff-to-peer mode (maybe a mode rather than a new skill — ours to judge); no helper to extract subagent research verbatim or bookmark transcripts. Joint-experiment lessons: thresholds validated by each side on live data; safety actions that survive both sessions dying (in-workload dead-man); cross-review of each side's safety lane; state clock zones and API versions; dry-run modes; machine-readable status lines; read-back after every write; summarise config diffs to key names (redaction). Receiving side's lessons: item 66c7. Operator's standing approval 2026-10-02 (on 66c7): file and run it through the cycle; the operator wants to work the skill idea with the librarian first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 149: How do you want to start on the cross-session handoff skill? — options: (a) a planner drafts it first | (b) talk the shape through here first [recommended] | (z) decide later
  raised: 2026-10-02T22:48Z
  revised: 2026-10-06T01:40Z — backfilled: the card was shown in the conversation but never stored; (a)'s quota note refreshed (the weekly window reset 2026-10-05; 5% used now)
  what: the first step on the cross-session handoff skill (2bbe), which you said you want to work through with me
  why now: it has waited since 2026-10-02; blocks: nothing else
  why ask: your-call — you said you want to shape it with me
  context: you pre-approved clustertool's request and said you want to work the skill idea with me · you decide how we begin — then: none
  stakes: reversible, narrow — the first step only
  (a) a planner drafts it first — it reads clustertool's request file, the bookmarked span of their transcript and brainboy's lessons, and comes back with the shape, the home options (a checkpoint transfer mode, a new skill, or both) and questions for you; roughly $20-40 at list price
  (b) talk the shape through here first — you tell me what matters most and I write it on the item; the planner then starts from your direction; costs only this conversation
  (z) decide later — the item waits, filed, with its source file in clustertool's scratchpad
  rec: (b) · basis partial — you said you want to work the idea with me, and a short conversation steers a long plan cheaply
  unknown: how much of the 11 practised points you want in the first version
decision 149: How do you want to start on the cross-session handoff skill? — options: (a) a planner drafts it first | (b) talk the shape through here first [recommended] | (z) decide later
  raised: 2026-10-02T22:48Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: the first step on the cross-session handoff skill (2bbe), which you said you want to work through with me
  why now: it has waited since 2026-10-02; blocks: nothing else
  why ask: your-call — you said you want to shape it with me
  context: you pre-approved clustertool's request and said you want to work the skill idea with me · you decide how we begin — then: none
  impact: → you steer the handoff skill's shape in a short talk before any agent spends on it · later: the cross-session handoff request stays filed, unplanned · reach: sessions that hand work across repos · undo: —
  stakes: reversible, narrow — the first step only
  (a) a planner drafts it first — it reads clustertool's request file, the bookmarked span of their transcript and brainboy's lessons, and comes back with the shape, the home options (a checkpoint transfer mode, a new skill, or both) and questions for you; roughly $20-40 at list price
  (b) talk the shape through here first — you tell me what matters most and I write it on the item; the planner then starts from your direction; costs only this conversation
  (z) decide later — the item waits, filed, with its source file in clustertool's scratchpad
  rec: (b) · basis partial — you said you want to work the idea with me, and a short conversation steers a long plan cheaply
  unknown: how much of the 11 practised points you want in the first version
answer 149: later (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:49:21.924Z; read as: later, default wake — the next Report)
