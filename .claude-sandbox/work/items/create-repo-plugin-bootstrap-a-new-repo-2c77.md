---
id: create-repo-plugin-bootstrap-a-new-repo-2c77
title: "create-repo plugin: bootstrap a new repo and launch an attachable agent session on it"
type: feature
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T19:50Z
created: 2026-09-19
updated: 2026-09-21
refs:
  - "peer: claude-sandbox-93 (uds 91.sock), operator relay"
---

Operator request 2026-09-19, relayed by peer claude-sandbox-93. New plugin create-repo with a skill: mkdir + git init -b main + seed README naming the purpose; claude-sandbox init --yes (inherits workspace config); initial commit; launch a session with a bootstrap prompt (write CLAUDE.md /init-style, then the thread's first investigation); tell the user the copy-paste attach command (cd <repo> && claude-sandbox --attach). Ecosystem support where needed. Rough edges (claude-sandbox side, tracked in its store, e.g. detached launch f9dc): no detached mode yet, so a launch under the agent's pty dies with the launching session; until --detach, prefer one copy-paste command that launches AND attaches in the user's terminal; in-sandbox launch needs host-visible TMPDIR; launch lock is per-container. Principle notes: marketplace shape (catalog row, CLAUDE.md layout, marketplace.json in the same feature); overlaps kit-dev new-project-from-template; claude-sandbox is a soft dependency (degrade to plain claude).

## Handoff
- doing: review r1 NEEDS_CHANGES (3 medium) — held by 810f
- next: fix round 1 after the hold lifts
- blocked: —
- learned: —

decision 43: placement — (a) new plugin create-repo as asked, with new-project-from-template (kit-dev) left as is and cross-noted [recommended: the operator named it; catalog row first]; (b) new plugin create-repo that also absorbs kit-dev new-project-from-template (one aim: start a new repo); (c) a skill in the sandbox plugin instead of a new plugin.

## Operator answer 2026-09-19
- 43 → (a) new plugin create-repo; kit-dev new-project-from-template stays, cross-pointed. PLUS: an optional arg lets the user name a claude-templates template as the goal (via new-project-from-template), gated on a check that kit-dev is installed; if not, offer to install it with instructions (soft dependency, principle 4).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — new plugin (marketplace shape) + a launcher that runs claude-sandbox

## Implementer result
- round 1 DONE_WITH_CONCERNS 76400de (opus): plugins/create-repo (skill create-repo: path confirm, bind-mount check, git init -b main, README, claude-sandbox init --yes, first commit, ONE launch+attach command; --template via kit-dev new-project-from-template when installed, else install hint); catalog/layout/marketplace; kit-dev pointer. Launch command not run (by design); flags checked against claude-sandbox --help and its source.
- scope widening before review: kit-dev plugin.json + marketplace description name the soft pointer to create-repo (principle 4).
- widening 4c6a764: kit-dev descriptions declare the soft pointer.
- dispatch: reviewer opus — rule 4
answer 43: (a) new plugin create-repo; new-project-from-template stays, cross-pointed; plus optional template goal via kit-dev (operator 2026-09-19) (migrated)

## Review round 1 — NEEDS_CHANGES (opus) at 4c6a764 (held: operator hold 810f)
- steps verified in a scratch workspace; hostile quoting byte-exact through `sq`; flags real; safety checks hold; merge-tree clean.
- [medium] default parent from --show-toplevel is the worktree in worktree sessions → use --git-common-dir's parent or $CLAUDE_SANDBOX_PROJECT_DIR.
- [medium] no instruction on putting the user's purpose into $PROMPT/$NAME safely → quoted heredoc or Write-tool file, never interpolate in double quotes (else the purpose's $() runs in the agent shell).
- [medium] bootstrap prompt names dev-flow's investigate — undeclared soft coupling → declare dev-flow (soft) in both descriptions + catalog row, or drop the name.
- lows: kit-dev pointer should name /create-repo:create-repo (model can't invoke it); template branch re-reads REPO/NAME and trackInHost from what new-project-from-template created; "sparse (only trackInHost set)"; quote the attach hint path; worktree-mode caveat; catalog notation "repo" vs "tool"; commit layout.
- next: fix round 1 (resume the implementer) once the hold lifts.
