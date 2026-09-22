---
handoff: 4
repo: claude-plugins
session: a1a4c97c-600f-424d-99f5-cd70cb575f79
written: <stamped>
head: <stamped>
branch: main
mode: handoff
by: checkpoint
mode_skill: /dev-flow:librarian-mode start
items:
  - context-guard-the-manifest-read-path-tak-0836
  - librarian-mode-codify-the-accepted-team-1f7f
  - context-guard-8cc2-f3b-where-handoff-md-a49b
  - dev-cycle-design-resume-whole-split-from-e770
  - librarian-work-unblocked-items-and-pre-i-1222
  - librarian-loop-use-claude-code-s-native-8ab6
  - context-guard-compact-and-clear-handoffs-5039
---
## Holds
- HOLD nothing is pushed but fast-forward main; a rejection is merged through per librarian-mode § Push rejected — why: operator rule — until: standing
- HOLD decisions 64, 65, 66 and 67 are the operator's — why: 65 blocks F3b-5, 67 blocks 1f7f; 64 and 66 block nothing — until: answered

## In flight
None. Every agent this session dispatched has returned, every worktree is removed, and every
branch is merged or deleted.

## Goal
mode: handoff — the session reached its context limit with the queue live. Resume the librarian
and keep working the queue; report the weekly burn rate, do not enforce a cap.

## Read in full
- .claude-sandbox/work/items/context-guard-the-manifest-read-path-tak-0836.md — the confirmed
  P1 against landed code; dispatch it first.
- .claude-sandbox/work/items/context-guard-8cc2-f3b-where-handoff-md-a49b.md — the plan of record
  (serials 04-08), five plan-review rounds, and what F3b-3's and F3b-4's briefs must carry.
- .claude-sandbox/work/items/dev-cycle-design-resume-whole-split-from-e770.md — the plan of record
  (serials 00-04); F1 landed, F2 is next.
- ~/.claude/claude-kit/ledger/a1a4c97c-600f-424d-99f5-cd70cb575f79.md — this session's decisions.

## Copy forward
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/a1a4c97c-600f-424d-99f5-cd70cb575f79/scratchpad/common-brief.md — the dispatch brief template
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/a1a4c97c-600f-424d-99f5-cd70cb575f79/scratchpad/common-review.md — the review brief template

## Aware of
- LANDED and pushed today, sixteen changes: 9882, d182, 220b, 5126, 5ef7, 2edb, 7117, a934, 25fa,
  426a, 5039 H1-H6, 3adc, e770 F1, F3b-1, F3b-2. Origin is at 273be71.
- CORRECTION 0836 is a hole in code that has LANDED: a symlink at <store>/<sid>/HANDOFF.md makes
  resolve_manifest return kind "own" with a peer's body, injected in full. Confirmed by probe.
  mark_checkpoint's own_store_manifest is the ready-made fix and test. Dispatch it first.
- DECIDED operator answers 46-63 are in the items. 64, 65, 66 and 67 are open.
- CORRECTION a landing runs `git merge-tree` first and checks MERGE_HEAD after; a script that ran
  past a conflict left a half-done merge on main once (aborted clean, nothing committed).
- CORRECTION a fail-first `git checkout <ref> -- <path>` wipes uncommitted edits; three
  implementers lost work that way, and the brief template now warns.
- F3b-4's brief carries: checkpoint SKILL.md:213 (four machine fields where handoff-format says
  five), operator-playbook.md:154 ("run from the repo"), handoff_path.py's argv contract.
- F3b-3's brief carries: the four plan-delta lows, plus F3b-1's trim-budget low (the notice
  subtracted from the budget costs protected content in trim's extreme regime).
- e770 F3's brief carries: the § Record line shapes move into references/record.md with the
  reviewer's three riders, and fix-loop.md's "paste none" sentence.
- UNVERIFIED whether an agent can arm /loop itself, and whether a dynamic loop survives compaction.

## Next
1. Dispatch 0836 first (P1, confirmed, against landed code; fable signal, opus fallback).
2. Then F3b-4, then F3b-3, then F3b-5 on decision 65.
3. Then e770 F2, F3, F4 in order.
4. Then 1f7f on decision 67, the H7 spike, caef (fable), the 8ab6 loop items, 0599, ee7b, 8e14
   and the review-low follow-ups.
