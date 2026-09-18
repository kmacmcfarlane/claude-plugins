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
carry it under `decisions needed` in the final Report. Send that final Report last — the
one time the push precedes its Report — so it reports the push as well as the landings.
The context-gate ledger and HANDOFF are session-addressed and do not replace this; the
librarian rehydrates from `wi prime` and git.

## At 75% or DUE — checkpoint, then continue

The trigger is the first of these `[claude-kit context gate]` advisories to arrive: the
"…% of the window is used" one at 75%, "DUE: … tokens left", or "HARD threshold reached
by an INFERRED depth". They ride on the operator's prompts, so a librarian working
through agent notifications also reads the status-line gauge when the operator's next
prompt arrives, and treats 75% used there as the same trigger. The session does not end
here: it checkpoints, the operator compacts when convenient, and it continues. Finish
the step in hand, then:

1. **Handoffs** — `$WI handoff` on every open item, as above.
2. **Checkpoint** — run the checkpoint skill with the argument `continue`, and answer its
   Step 0 question 3 up front with the `/compact <guidance>` arm of its Step 5 (not
   `/rewind`), so only question 2 is left to ask. Custody holds throughout: its residue
   goes into item bodies (append) or new items (`$WI add`), never into CLAUDE.md or a
   skill file; its commits are store-only — the work-item store and the manifest.
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
and carry on from `wi prime`; the manifest and ledger outrank the machine summary.
