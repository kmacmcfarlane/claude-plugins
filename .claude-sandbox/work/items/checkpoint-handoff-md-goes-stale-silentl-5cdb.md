---
id: checkpoint-handoff-md-goes-stale-silentl-5cdb
title: "checkpoint: HANDOFF.md goes stale silently and misleads the next session"
type: bug
status: doing
priority: 2
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:16Z
created: 2026-09-17
updated: 2026-09-18
refs:
  - peer session claude-sandbox librarian (uds 238.sock), relaying the operator
---

Peer session 'claude-sandbox librarian' relayed on the operator's instruction, 2026-09-17. Case: a fresh librarian was pointed at .claude-sandbox/HANDOFF.md written at head c5af17d while main was 11 commits further on (547aa58). The manifest's 'Next' section named an item that had already been built, reviewed and landed (e002590). The SessionStart hook did flag the file AGED with age, recorded head and dirty count, and that was not enough: it says the file is old, not WHICH claims are now false, and 'Next' reads as an instruction anyway. The precedence line ('corrections outrank recollection') pointed the wrong way — the manifest was the stale thing and what overrode it was ordinary repo state. What saved it: wi prime + git log; the durable state was correct, only the narrative had rotted. Operator's framing: it 'should probably be cleaned up, or we need some way of dealing with the fact that it's stale because it's confusing agents'. Peer's directions (judgement, not spec): manifest names the work-item ids it expects open so rehydration can diff them against the store and say which claims are dead; the hook refuses to present 'Next' once the recorded head diverges from the current one, rather than printing it under a warning; or the manifest drops 'Next' entirely and points at the store, keeping only the reasoning the store cannot hold; possibly expire a manifest after N commits or N hours. Files: checkpoint skill (SKILL.md, references/handoff-format.md) and the rehydration hook (rehydrate.py) — context-guard on the factored layout, claude-kit on main. Peer deleted the one stale file as a one-off; it changed nothing in claude-kit. Full rehydration transcript and item ids available from the peer on request.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
Also (ce46 re-review): ending-the-session.md calls HANDOFF 'session-addressed' while checkpoint/references/handoff-format.md calls it 'Work-addressed (class b1)', one per repo — contradictory, and it matters more now that librarians write HANDOFF.md routinely in a shared checkout.

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic (rehydrate.py hook) + judgement; bundled with 72bf in worktree 5cdb (same SKILL.md)

impl: DONE 70b918b (5cdb), e2680e3 (72bf). Deviations: .work fallback, "?" for unknown head, LANDED skipped, operator-playbook one-clause edit. Open: AGED label still counts store chores (liveness()).
dispatch: reviewer opus — rule 4
