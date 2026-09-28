---
id: no-modal-askuserquestion-while-backgroun-09f1
title: "no modal AskUserQuestion while background agents run: dev-cycle, investigate, implement, checkpoint"
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:46Z
created: 2026-09-22
updated: 2026-09-28
refs:
  - 7117 OQs
---

From 7117 (operator ruling, answer 58) open questions, 2026-09-22: standalone dev-cycle § Decisions (one pending decision via AskUserQuestion while its implementer/reviewer may run); investigate Step 11 (asks while a background verify batch runs); implement Step 6 review gate (asks while a Step-3 agent may run); context-guard checkpoint Step 0 (called mid-session with the caller's agents in flight). Decide per skill: numbered channel whenever an agent may be in flight; keep closed-choice dialogs only where nothing runs.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-no-modal-askuserquestion-while-backgroun-09f1 at .claude/worktrees/no-modal-askuserquestion-while-backgroun-09f1, base main (b29422b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes what four skills do (rule 2)
agent: implementer a44821e7103e482ac round 1
return: implementer DONE 1fbc6bf (OQ: implement Step 7 + edge-cases.md, dev-cycle troubleshooting push-rejection ask, dev-cycle Step 0.2/checks/Land dialogs on a resumed run, investigate Step 3a — left)
changed: plugins/dev-flow/skills/dev-cycle/references/bindings.md, plugins/dev-flow/skills/investigate/SKILL.md, plugins/dev-flow/skills/implement/SKILL.md, plugins/context-guard/skills/checkpoint/SKILL.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer aacdb3acf5fca1b43 round 1 at 1fbc6bf
verdict: NEEDS_CHANGES round 1 at 1fbc6bf (2 high, 2 medium, 2 low, 1 nit)
findings:
  [high] checkpoint SKILL.md:109-113 — the list path deadlocks at the HARD prompt gate: context_warn erases every prompt but /checkpoint /compact /clear, so a free-text list answer is erased; re-running /checkpoint loops
  [high] context-guard plugin.json:3, README.md:79 — checkpoint now names operator-interaction:decisions; undeclared soft dependency (principle 4)
  [medium] checkpoint SKILL.md:109-113 — "end the turn there" is unconditional; breaks librarian-mode ending-the-session (continue, answers 2/3 itself, needs 4b + mark + push in one turn); --checkpointing placement vs the list turn unstated
  [medium] dev-cycle bindings.md:179-184 — "none of this cycle's agents" narrower than answer 58 ("whenever an agent may be in flight"); make it the session's, record as the cycle's own evidence, ListAgents for the rest
  [low] implement SKILL.md:171-173 restates investigate's rule; trim to the Step 3 tell
  [low] investigate SKILL.md:65 "always" — only in a round that launched a batch
  [nit] checkpoint allowed-tools lacks ListAgents (pre-existing)
librarian decision: for the undeclared dependency, drop the checkpoint's pointer to the decisions skill (its three questions are plain numbered questions) rather than widen context-guard's declared deps; for the HARD gate, the list path must accept the answers as the /checkpoint argument (whitelisted) and say so in the list, never rely on a free-text reply under the gate
dispatch: implementer opus — resume, fix round 1
agent: implementer a44821e7103e482ac round 2
return: implementer DONE 71cc30c (fix round 1; all 7 fixed)
dispatch: reviewer opus — resume, round 2
agent: reviewer aacdb3acf5fca1b43 round 2 at 71cc30c
verdict: NEEDS_CHANGES round 2 at 71cc30c (1 medium, 1 low; all round-1 fixed; HARD-gate path traced end to end; librarian composition holds)
findings:
  [medium] checkpoint SKILL.md:115-116 — the reply line drops `then <next-skill>` and focus text; pass: repeat the original argument, mode first, before the answers
  [low] SKILL.md:94-96 argument rule doesn't mention the `— 2: … 3: …` answers; :26 "after Step 0 has been asked" → "after Step 0"
dispatch: implementer opus — resume, fix round 2
agent: implementer a44821e7103e482ac round 3
