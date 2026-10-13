---
id: context-guard-ledger-p-entries-for-commi-6641
title: "context-guard ledger: P-entries for commits in other repos name the session cwd"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (ledger-pointer-attributes-cross-repo-com-03b8). Ledger P-entries for a commit made in another repo say '-> .../<session cwd>': the hook uses the payload cwd, not the repo the commit landed in. Acceptance: derive the repo from the command's git -C / cd context (or the commit's own repo), fall back to cwd; test with a git -C <other> commit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (9b5d12b2); context-guard hooks ledger_pointer.py + tests
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — P-entry names the commit's repo
agent: implementer ac59fa52819a075cd round 1
result: DONE round 1 at d94b7258 (commit_repo: shlex split, cd chain, git -C, toplevel; falls back to cwd; 739 OK; subshell (cd x && …) not handled)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer a7c12829ab9c31b95 round 1 at d94b7258
verdict: NEEDS_CHANGES round 1 at d94b7258 (1 medium: newline-separated and continued commands still fall back to cwd, mid-word # comments; lows: subshell/brace group, pushd/cd --/cd -P, untested hard shapes; nits: git -C '', background &, docstring limits)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer ac59fa52819a075cd round 2
result: DONE round 2 at e4883e2a (operator-char tokens, subshell/brace, pushd/cd -/options, git -C '', background & handled; 748 OK)
dispatch: reviewer opus high — resume, round 2
agent: reviewer a7c12829ab9c31b95 round 2 at e4883e2a
verdict: CLEAR round 2 at e4883e2a (low: test the &&\n and ;\n\n operator tokens; nits: docstring on a closed subshell or pipeline cd, quoted ';' comment)
decided: 2026-10-13T22:45Z cap — low 1 and nit 2 with exact wording: one finish round, read by the librarian (authority answer 145); nit 3 declined (no case changes the result)
dispatch: implementer opus medium — resume, finish round
agent: implementer ac59fa52819a075cd round 3 (finish)
result: DONE finish at c1a3372d (exact; read by the librarian; 748 OK)
verdict: CLEAR after 1 fix round, 1 finish at c1a3372d
