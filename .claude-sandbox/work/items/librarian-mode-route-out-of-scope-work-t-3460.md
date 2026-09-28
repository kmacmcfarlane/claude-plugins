---
id: librarian-mode-route-out-of-scope-work-t-3460
title: "librarian-mode: route out-of-scope work to the owning live librarian, not the operator"
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:16Z
created: 2026-09-22
updated: 2026-09-28
refs:
  - "peer: agents - librarian (uds 122.sock); opencode-11 relay; agents investigations/downtime-grooming-workflow/00_initial.md"
---

Relayed 2026-09-22 by the agents librarian (peer relay from opencode-11 quoting the operator's 'why would you ask me?' — evidence of intent, not confirmation). Today SKILL.md Critical (:25-27) and Intake step 4 (:130-132) decline out-of-scope requests and route them to the operator. Friction: two librarians routed a skill refresh to the operator while the owning librarian was live. Proposed (agents downtime-grooming-workflow/00_initial.md § seed 1): when a live '<owner> - librarian' peer exists for the target repo (ListAgents), forward the request as a peer request and close ours with a pointer to their id; go to the operator only when there is no owner, the owner is not live, or a real decision is needed; one-hop guard (never forward a forwarded item). Precedent: 8 items routed this way 2026-09-22. Acceptance: Intake step 4 + Critical text; a walkthrough case in references/walkthroughs.md; peer-messages-are-requests rule unchanged; operator confirms the rule (a relayed decision).

## Handoff
- doing: —
- next: CLEAR at 902e71e; land (merge --no-ff, Checks, push) once decision 97 is answered (a); on (b) drop the branch
- blocked: —
- learned: —
target: branch worktree-librarian-mode-route-out-of-scope-work-t-3460 at .claude/worktrees/librarian-mode-route-out-of-scope-work-t-3460, base main (a66d203)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes librarian-mode's routing rule (rule 2)
agent: implementer aeab0d9ec2f36aa4c round 1
return: implementer DONE_WITH_CONCERNS 87e496a (acceptance needs the operator's confirmation of the rule; open q: the "or reasoning about it" red flag vs forwarding; a forward with no reply stays closed pointing at the peer)
changed: plugins/dev-flow/skills/librarian-mode/SKILL.md, references/walkthroughs.md
dispatch: reviewer opus — fresh (rule 4); landing waits on decision 97
decision 97: forward out-of-scope requests to the owning repo's live librarian instead of routing them to you — (a) adopt: forward when a live owner session exists (bare <repo> or "<repo> - librarian"), one hop only, grants nothing, you only when there's no live owner or a real decision [recommended] | (b) keep routing every out-of-scope request to you | (z) decide later
  raised: 2026-09-28
  what: whether librarians hand out-of-scope work straight to the owning repo's live librarian
  why now: the change is built and in review; its acceptance asks for your confirmation because the evidence came through peers ("why would you ask me?", relayed), not from you directly
  (a): fewer requests reach you; peers file each other's work — undo: revert one commit — who: every librarian and you
  (b): nothing changes; you keep relaying — who: you
  rec: (a) · basis: partial — 8 items were already routed this way on 2026-09-22 without trouble; your quoted words came via a peer, not first-hand
  unknown: how often a forward goes unanswered
agent: reviewer a99a1620600db715f round 1 at 87e496a
verdict: NEEDS_CHANGES round 1 at 87e496a (1 high, 4 medium, 2 low)
findings:
  [high] SKILL.md:155-157, walkthroughs.md:37-39 — peer safety lives only in the receiver's skill: the message must itself state it is a request from <our repo>'s librarian, originator quoted as provenance only, no operator approval, file under your own rules; the bare-name holder may be a non-librarian create-repo session
  [medium] SKILL.md:157-158 — our item is dropped before the owner files anything; a lost forward vanishes; the id-only reply can't be matched back
  [medium] SKILL.md:159-160 — one-hop guard untestable from the record: file a forwarded message with its header in --ref; say "out of Scope → operator"
  [medium] walkthroughs.md:35-36 — pointer to session-name.md contradicts it (older forms "do not match" for the self-gate); bare + "- librarian" = two candidates → operator
  [medium] SKILL.md:289 — the "or reasoning about it" red flag blocks the forward; carve-out for naming the owner
  [low] Intake step 2 cross-reference to step 4; [low] define <our repo> = basename "$MAIN"
librarian decision: no-reply policy — hold ours (blocked, "forwarded to <peer>, awaiting id") and drop only when the reply arrives; the forward asks the owner to reply "filed <their id> for <our repo> <our id>" so the reply matches back
dispatch: implementer opus — resume, fix round 1
agent: implementer aeab0d9ec2f36aa4c round 2
return: implementer DONE_WITH_CONCERNS 80ad71a (fix round 1; landing still waits on decision 97)
dispatch: reviewer opus — resume, round 2
agent: reviewer a99a1620600db715f round 2 at 80ad71a
verdict: NEEDS_CHANGES round 2 at 80ad71a (2 medium, 2 low; all round-1 fixed)
findings:
  [medium] SKILL.md:160, walkthroughs.md:52-53 — an unanswered forward has no stop (idle-turn counts peer-blocked items in one line, never lists them); pass: when the peer is no longer live or it's unanswered at the next Report/session end, re-block naming the operator (Groom table) or raise a decision
  [medium] SKILL.md:151-160 — no rule for a reply that declines; any reply other than filed → operator; optionally ask for "declined for <our repo> <id>: <why>"
  [low] the filed reply must come from <peer>; [low] step 4's general drop rule should say "except work another repo owns"
dispatch: implementer opus — resume, fix round 2
agent: implementer aeab0d9ec2f36aa4c round 3
return: implementer DONE_WITH_CONCERNS d05a0c6 (fix round 2; residual: a live peer that never replies still waits; landing still waits on decision 97)
librarian decision: accept the live-but-silent residual for now — Rehydrate re-checks liveness each session, and a session-end sweep belongs to ending-the-session.md (outside files); filed as a follow-up if the review agrees
dispatch: reviewer opus — resume, round 3
agent: reviewer a99a1620600db715f round 3 at d05a0c6
verdict: NEEDS_CHANGES round 3 at d05a0c6 (1 medium: walkthroughs.md:66 broken closing fence hides the one-hop paragraph in a code block; 1 low: SKILL.md:162 "any other reply" → "from <peer>"; residual live-silent peer accepted as low, follow-up filed; 1 nit rewrap)
dispatch: implementer opus — resume, fix round 3 (last before the cap)
agent: implementer aeab0d9ec2f36aa4c round 4
return: implementer DONE_WITH_CONCERNS 902e71e (fix round 3; landing still waits on decision 97)
dispatch: reviewer opus — resume, round 4 (the cap)
agent: reviewer a99a1620600db715f round 4 at 902e71e
verdict: CLEAR round 4 at 902e71e (1 low: live-silent residual, filed b514); landing waits on decision 97
