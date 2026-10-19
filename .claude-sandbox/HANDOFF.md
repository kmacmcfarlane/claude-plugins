---
handoff: 4
repo: claude-plugins
session: e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73
written: 2026-09-23T00:15:53Z
head: 84a9d8c
branch: main
mode: continue
by: checkpoint
mode_skill: /dev-flow:librarian-mode start
items:
  - read-list-accept-t-headings-say-so-when-c121
  - context-guard-correct-the-1-4-compaction-8519
  - context-guard-tests-testlegacyarmmatches-ba8f
  - librarian-f2-idle-turn-modes-concurrency-c79e
  - librarian-work-unblocked-items-and-pre-i-1222
top: /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins
---
## Holds
None. (Operator rule, standing: push only fast-forward main.)

## In flight
- c121 reviewer a63655af1d1d84f24 round 2 at db28bed (worktree .claude/worktrees/read-list-accept-t-headings-say-so-when-c121); implementer a700b6bf753d6f0b8 for a fix round.
- 8519 reviewer a0a81a13103b14bc3 round 2 at 95cba7f (worktree .claude/worktrees/context-guard-correct-the-1-4-compaction-8519); implementer a94723f9f73124a7c.
- ba8f implementer afaf2a529d1566917 round 1, no return yet (worktree .claude/worktrees/context-guard-tests-testlegacyarmmatches-ba8f); on return dispatch an opus reviewer.
Each item body carries its dispatch:/agent: record lines; resume per the dev-cycle skill's references/resume.md.

## Goal
Operator 2026-09-22: "create a plan to work through the rest of the work items. Use your new approach to mind the quota and see how much you can get done without overrunning the reserve. Then work on the items in turn continuously." Continue the queue under the quota rule recorded in item 1222 ("Queue plan under the quota meter": hard stop weekly 85 / 5h 75, soft checkpoint weekly 64, meter each wave).

## Doing
- Landing the three in flight above, then the next wave from the 1222 handoff next line.
- c79e (librarian F2 idle modes) is BLOCKED on decisions 68, 69, 70 (plan at the 4-round review cap; series .claude-sandbox/investigations/1222-unattended-librarian/ 00-04; review notes in its reviews/).

## Decisions and why
- Every item runs dev-cycle: sonnet only for doc-only/one-file items with no signal; opus for scripts/, hooks, >1 plugin, doctrine; reviewer floor opus; fable only for security/gating code (0836 was fable).
- Scope widened by the librarian when a fix could not land alone (F2 durable binding; bb7e/cd09 soft-dependency declarations; F3b-4 mark-step install).
- One-line typo/path fixes applied directly under the librarian bypass (d22b, F4 wording, 26b0 pointer).
- Brief templates: scratchpad common-brief.md / common-review.md (see Copy forward).

## Aware of
- Meter at checkpoint: weekly 47% (~3.3 pts/h), 5h ~2%, resets weekly in ~130 h. Soft checkpoint at 64 not reached.
- Decisions pending: 68 (c79e cap ruling), 69 (B1 /loop probe), 70 (B2 enforce the pool). Nothing else awaits the operator.
- Known false red: context-guard TestLegacyArmMatchesMain fails in worktrees cut before a context-guard change lands (ba8f fixes it); passes on main.
- One flaky context-guard failure was seen once under heavy CPU load (f381 review) — watch.
- wi claimant is now Kyle-McFarlane@<container> (59ce); old unknown@<host> claims need --steal to re-claim.
- The installed context-guard plugin (aa54bffb43a3) predates F3b-4: this checkpoint used the old repo-file path. After /plugin marketplace update + /reload-plugins the store path applies.

## Read in full
- .claude-sandbox/work/items/librarian-work-unblocked-items-and-pre-i-1222.md — the queue plan and next wave
- .claude-sandbox/work/items/librarian-f2-idle-turn-modes-concurrency-c79e.md — decisions 68-70
- ~/.claude/claude-kit/ledger/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73.md — this session's decisions

## Copy forward
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73/scratchpad/common-brief.md — the dispatch brief template (retarget its scratchpad path)
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73/scratchpad/common-review.md — the review brief template

## Next
1. Resume the three in flight by id (SendMessage); land each on CLEAR (merge-tree first, check on main, push).
2. Then the 1222 next wave: wi.py serial (9197, 0aaa, fc04, 8e14, 6f1c), 3c4f, 87fd, 6641, 0d6b (fable), caef (fable), 8ab6 items, 0599, ee7b, 09f1, 3460, d05d, bfd6, b8d6, 5a18, 0900.
3. On answers 68-70: c79e per the item's handoff next line.
