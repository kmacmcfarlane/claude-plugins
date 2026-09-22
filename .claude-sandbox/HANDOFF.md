---
handoff: 3
repo: claude-plugins
session: a1a4c97c-600f-424d-99f5-cd70cb575f79
written: <stamped>
head: <stamped>
branch: main
mode: continue
by: checkpoint
mode_skill: /dev-flow:librarian-mode start
items:
  - librarian-work-unblocked-items-and-pre-i-1222
  - context-guard-8cc2-f3b-where-handoff-md-a49b
  - dev-cycle-design-resume-whole-split-from-e770
  - context-guard-turn-gate-8cc2
  - librarian-loop-use-claude-code-s-native-8ab6
  - context-guard-compact-and-clear-handoffs-5039
---
## Holds
- HOLD nothing is pushed but fast-forward main; a rejection is merged through per librarian-mode § Push rejected — why: operator rule — until: standing
- HOLD decisions 64, 65 and 66 are the operator's — why: 65 blocks F3b-5; 64 and 66 block nothing — until: answered
- HOLD F3b-2 is CLEAR but must not land before F3b-1 — why: the plan's order keeps every merge point green — until: F3b-1 lands

## In flight
- reviewer — context-guard-8cc2-f3b-where-handoff-md-a49b (F3b-1) — agent a10c65a451623a781 — round 2 — waiting on its own return
- implementer — context-guard-8cc2-f3b-where-handoff-md-a49b (F3b-1) — agent a3f270c1ce4ff1026 — fix round 1 done at 2568e95 — waiting on review round 2
- implementer — context-guard-8cc2-f3b-where-handoff-md-a49b (F3b-2) — agent af1bebc34259271b0 — CLEAR at 8092d28 — waiting on F3b-1 to land first
- reviewer — context-guard-8cc2-f3b-where-handoff-md-a49b (F3b-2) — agent ac5c07409a1d20e8d — round 2 done, CLEAR — idle
- implementer — dev-cycle-design-resume-whole-split-from-e770 (F1) — agent a58ed2ccb63bee360 — fix round 2 — waiting on its own return
- reviewer — dev-cycle-design-resume-whole-split-from-e770 (F1) — agent ac36c5798576944f0 — round 2 done — waiting on the fix

## Goal
mode: continue — operator 2026-09-22: "continue with the work queue and we'll get to the loop
work item in turn." Work the queue; report the weekly burn rate, do not enforce a cap.

## Read in full
- .claude-sandbox/work/items/context-guard-8cc2-f3b-where-handoff-md-a49b.md — five plan-review
  rounds, the plan of record (serials 04-08), and both features' review records.
- .claude-sandbox/work/items/dev-cycle-design-resume-whole-split-from-e770.md — four plan-review
  rounds plus a corrections serial; the plan of record is 00-04.
- ~/.claude/claude-kit/ledger/a1a4c97c-600f-424d-99f5-cd70cb575f79.md — this session's decisions.

## Copy forward
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/a1a4c97c-600f-424d-99f5-cd70cb575f79/scratchpad/common-brief.md — the dispatch brief template (seven Checks, the fail-first checkout warning)
- /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/a1a4c97c-600f-424d-99f5-cd70cb575f79/scratchpad/common-review.md — the review brief template

## Aware of
- LANDED and pushed today: 9882, d182, 220b, 5126, 5ef7, 2edb, 7117, a934, 25fa, 426a, 5039 H1-H6,
  and 3adc (8cc2 F1) at 15f271c. Origin is at 3cf6dc4 plus store commits.
- DECIDED operator answers 46-63 are in the items. 64, 65 and 66 are open; only 65 blocks anything.
- DECIDED the librarian settles a planner's or implementer's side-question itself when one option
  is plainly better and reversible; it queues it when the operator's own words are the input.
- CORRECTION a landing runs `git merge-tree` first and checks MERGE_HEAD after. A script that ran
  past a conflict left a half-done merge on main once (aborted clean, nothing committed).
- CORRECTION a fail-first `git checkout <ref> -- <path>` wipes uncommitted edits; three
  implementers lost work that way. The brief template warns, and an item covers agent-brief.
- F3b-4's brief must carry: checkpoint SKILL.md:142 (four machine fields where handoff-format now
  says five), operator-playbook.md:143 ("run from the repo"), and handoff_path.py's argv contract.
- F3b-3's brief must carry the four lows from the plan's delta check (the cascade assumption's
  scope, the peer-case warning wording, the AGED-vs-FRESH cost statement, two citations).
- F3's brief (e770) must carry the reviewer's three riders for moving § Record line shapes into
  references/record.md, and 04 § 18.1's identifier count restated against the new paths.
- UNVERIFIED whether an agent can arm /loop itself, and whether a dynamic loop survives compaction.

## Next
1. Resume the four live agents by id before dispatching anything: F3b-1's review, F3b-1's
   implementer, and e770 F1's implementer and reviewer.
2. On F3b-1 CLEAR: land F3b-1, then F3b-2 (already CLEAR at 8092d28), merge-tree first.
3. Then F3b-4 (3adc has landed, so it is unblocked), then F3b-3, then F3b-5 on decision 65.
4. On e770 F1 CLEAR: land it, then F2, F3, F4 in order.
5. Queued after that: H7 spike, caef (fable), the 8ab6 loop items, 0599, ee7b, 8e14 and the
   review-low follow-ups.
