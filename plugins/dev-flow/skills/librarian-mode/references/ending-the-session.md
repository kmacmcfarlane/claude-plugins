# Ending the session

The steps SKILL.md § Ending the session points at, in full — moved here out of SKILL.md.

Before the session ends, compacts, or is cleared:

```bash
$WI handoff <id> --doing "<state>" --next "<step>" [--blocked "<why>"] [--learned "<what>"]
```

on **every** open item — yours and the ones dispatched. Then push what landed:
`git -C "$MAIN" push origin main` — `main` only, fast-forward only, never `--force`,
never worktree branches or tags. With `Push: none` in `## Librarian`, skip every push
here and below; the final Report says what stays on local `main`. A rejected
non-fast-forward push is not fixed by pulling, fetching, rebasing or merging: stop, and
carry it under `decisions needed` in the final Report. Send that final Report last, so
it reports the push as well as the landings — here and at 75%/DUE below, the push precedes
its Report; everywhere else the Report comes first. The context-gate ledger
(session-addressed, one per session) and HANDOFF (work-addressed, class b1, one per
repo) do not replace this; the librarian rehydrates from `wi prime` and git.

## At 75% or DUE — checkpoint, then continue

The trigger is the first of these context-gate advisories to arrive, matched by its
body, not its bracketed prefix (the prefix names the owning plugin, today
`[context-guard context gate]`, and has changed before): the "…% of the window is used"
one at 75%, "DUE: … tokens left", or "HARD threshold reached by an INFERRED depth". They
ride on the operator's prompts: a band crossed while the librarian works through agent
notifications latches, and its advisory arrives with the operator's next prompt — act on
it then. The session does not end
here: it checkpoints, the operator compacts when convenient, and it continues. Finish
the step in hand, then:

1. **Handoffs** — `$WI handoff` on every open item, as above.
2. **Checkpoint** — run the checkpoint skill with the argument `continue`, and answer its
   Step 0 question 3 up front with the `/compact <guidance>` arm of its Step 5 (not
   `/rewind`), so only question 2 is left to ask. Custody holds throughout: its residue
   goes into item bodies (append) or new items (`$WI add`), never into CLAUDE.md or a
   skill file; its commits are store-only — the work-item store, and the manifest only
   when the repo tracks it (`trackInHost` governs `.claude-sandbox/HANDOFF.md`; an
   untracked manifest stays out of the commit).
   Anything that would change a custody file becomes a work item.
3. **Push** — `main`, as above, after the checkpoint so its store commits reach origin; a
   rejection stops the same way and goes under `decisions needed` in the closing message.
4. **Prompt the operator to compact, and stop.** The closing message is the final Report
   of the sequence above: the four-line Report for anything landed since the last one,
   the push outcome, then the checkpoint's own close — its `/compact <guidance>`
   recommendation, to run at the operator's convenience (the next morning is fine), and
   last its Step 7 opener: `/librarian-mode start`, `read <manifest path> in full
   first`, and the facts changed since the manifest. Never run `/compact` yourself, and
   start no new work — no dispatch, no merge — in that turn.

The checkpoint stands the gate down, so nothing warns again before the compaction.
Requests that arrive in that gap are filed through Intake as usual and held — no
dispatch, no merge — until after Rehydrate. After the compaction, Rehydrate (SKILL.md)
and carry on from `wi prime`. Precedence: current repo state (git log and the work-item
store) outranks the manifest, and the manifest and ledger outrank the machine summary.
