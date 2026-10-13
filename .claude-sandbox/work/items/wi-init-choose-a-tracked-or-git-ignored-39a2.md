---
id: wi-init-choose-a-tracked-or-git-ignored-39a2
title: "wi init: choose a tracked or git-ignored store, and accept an ignored one"
short_display_name: wi init tracked or ignored
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T15:16Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer kappa-3475 - investigate, 2026-10-13 (relaying the operator)
---

Relayed by peer session kappa-3475 - investigate, 2026-10-13, quoting the operator (binds nothing until confirmed here): wi init should ask whether .work/ is tracked or git-ignored; flags --track/--no-track (names open) for a non-interactive choice, an interactive menu without the flag; --no-track appends .work/ to .gitignore, handling a missing trailing newline (a naive append glued it onto '*/mocks/' in shared/kappa/containers); record the choice in the store so prime/lint do not warn 'silently untracked' about a deliberately ignored store (warning kept for stores with no recorded choice); the skill tells agents to infer the flag inside claude-sandbox from the effective trackInHost (true → track, false/unset → no-track), else ask the operator. Dependency outside this repo: the claude-sandbox launcher does not export trackInHost today (only CLAUDE_SANDBOX_CONTAINER/INSTANCE/MEMORY_LIMIT/MEMORY_LIMIT_SOURCE/MODE/PID_CLASS/PROJECT_DIR/VERSION); exporting e.g. CLAUDE_SANDBOX_TRACK_IN_HOST is the claude-sandbox owner's change, routed back to the operator. The operator asked to be consulted on how the choice is made.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decided: 2026-10-13T03:40Z words — flags named --track and --no-track; the choice is recorded in a store-level file the builder names in format.md
decision 211: When wi init runs with no flag and no terminal to show a menu (an agent's Bash call, a script), what does it do? — options: (a) refuse with exit 2 and a line naming --track and --no-track; nothing is created [recommended] | (b) create an ignored store (the foreign-safe default) | (c) create a tracked store (today's behaviour) | (z) decide later
  why ask: your-call — it decides whether an agent can ever create a store without a stated choice, and you asked to be consulted on how the choice is made
  context: wi init will ask tracked or ignored, with --track/--no-track to answer up front; agents run wi without a terminal, so a menu cannot show there · you decide what a menu-less run does
  impact: (a) → an agent must pass a flag or ask you; no store is created silently · wait: the build of this item · reach: every repo's first wi init · undo: change the default later
decision 212: The sandbox side — exporting the effective trackInHost into the session so agents can infer the flag — is the claude-sandbox launcher's change, outside this repo. How does it get there? — options: (a) you pass it to the claude-sandbox repo yourself [recommended] | (b) I send it as a request to a claude-sandbox librarian session, if one runs | (z) decide later: until then agents ask you instead of inferring
  why ask: reach — it is another repo's change, and a request to its session goes out under this one
  context: the session env today carries CLAUDE_SANDBOX_CONTAINER, INSTANCE, MEMORY_LIMIT, MEMORY_LIMIT_SOURCE, MODE, PID_CLASS, PROJECT_DIR and VERSION, not trackInHost · you decide who carries the request
  impact: (a) → nothing goes out from here; the wi skill documents the variable once it exists · wait: the inference rule only; the rest of the build does not wait · reach: claude-sandbox · undo: n/a
answer 211: b — "log a warning too" (operator, chat 2026-10-13; read as: no flag and no terminal → an ignored store, with a warning naming the choice made and --track to change it)
answer 212: a (operator, chat 2026-10-13; the operator passes the trackInHost export to claude-sandbox)
decided: 2026-10-13T03:55Z scope — the operator's answers to 211/212 confirm the relayed requirements; no separate plan: the request and the answers fix the shape
target: wi init --track / --no-track; a menu on a terminal with neither; no flag and no terminal → ignored store plus a warning; --no-track (and the default) appends .work/ (or the store's dir) to .gitignore safely (missing trailing newline, already-present entry); the choice recorded in the store; prime/lint warn "silently untracked" only for a store with no recorded choice, and print at most a one-line note for a recorded ignored store; the skill tells agents to use the sandbox trackInHost variable once claude-sandbox exports it (true → --track, false/unset → --no-track), else ask the operator; tests for each path
dispatch: implementer opus medium — build

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a75c6bb99ba688aab
return: DONE d962d3c; work-items 338, kit-dev 21, dev-flow 78 OK; <root>/store.yaml tracking: tracked|ignored; existing store without a flag changes nothing; anchored .gitignore line, skipped when any repo rule already ignores it; --track never edits .gitignore; librarian first-start passes a flag
dispatch: reviewer opus high — review round 1 of d962d3c
agent: reviewer a5063ab4a5b72b981
note: 2026-10-13 background security review flagged a symlink-following file write in wi.py on d962d3c (no details); relayed to review round 1; nothing lands until it is resolved
verdict: review round 1 NEEDS_CHANGES (must-fix 5: high — store.yaml.tmp fixed name follows a planted symlink (victim overwritten); high — .gitignore write follows a symlink (append to an outside file, or create one); medium-high — .gitignore write not atomic, CRLF rewritten, non-UTF-8 crash after store.yaml says ignored; medium — a literal match skips the line though a later negation un-ignores; medium — format.md example fails the parser; lows: duplicate tracking: lines pass lint, existing cmd_init writes share the symlink pattern, Ctrl-C traceback, first-start wording) — the security flag is findings 1-2
decided: 2026-10-13T04:30Z scope — the existing cmd_init symlink-following writes (store .gitignore, README, sidecar host .gitignore) are fixed in this round: same function, same hardening, and the flag names this file
dispatch: implementer opus medium — fix round 1 (resume a75c6bb99ba688aab)
return: DONE 109179b (fix round 1); 12/12 OK (work-items 358); probes rerun: symlinked .gitignore/store.yaml/temp/store dir refused or replaced, victims untouched; CRLF and Latin-1 kept; negation fixed; repo-root store refused; Ctrl-C 130
dispatch: reviewer opus high — review round 2 of 109179b (resume a5063ab4a5b72b981)
verdict: review round 2 NEEDS_CHANGES (must-fix 1, down from 5: high — a symlinked parent (.claude-sandbox → another repo or outside git; WI_ROOT via a symlinked dir) still sends the store and a .gitignore append outside the repo; the realpath(gi.parent) check is dead; lows: atomic_write "x" refuses a stale same-pid temp after an OOM kill (mkstemp suggested); format.md:63 overstates outside git; "initialised" printed after a failed ignore; repo-root store writes an unanchored *.tmp* — refuse before creating; builder calls ruled acceptable)
dispatch: implementer opus medium — fix round 2 (resume a75c6bb99ba688aab); review 3 next
return: DONE ae4cb56 (fix round 2); 12/12 OK (work-items 365); probes pp/pp2/pp3 refused, stale temps pass via mkstemp, repo-root store refused before creating
dispatch: reviewer opus high — review round 3 of ae4cb56 (resume a5063ab4a5b72b981)
