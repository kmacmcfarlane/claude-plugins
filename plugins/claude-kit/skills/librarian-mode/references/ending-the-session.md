# Ending the session

The steps SKILL.md § Ending the session points at, in full — moved here out of SKILL.md.

Before the session ends, compacts, or is cleared:

```bash
$WI handoff <id> --doing "<state>" --next "<step>" [--blocked "<why>"] [--learned "<what>"]
```

on **every** open item — yours and the ones dispatched. Then push what landed:
`git -C "$MAIN" push origin main` — `main` only, fast-forward only, never `--force`,
never worktree branches or tags. A rejected non-fast-forward push is not fixed by
pulling, fetching, rebasing or merging: stop, and carry it under `decisions needed` in
the final Report. Send that final Report last — the one time the push precedes its
Report — so it reports the push as well as the landings. The context-gate ledger and
HANDOFF are session-addressed and do not replace this; the librarian rehydrates from
`wi prime` and git.

## At 75% context used

The trigger: the context gate's 75% advisory (`context_warn.py`, `BANDS = (60, 75)`), or
the status-line gauge reading 75% used or more. The session does not end here — it
checkpoints, the operator compacts when convenient, and it continues. Operator SOP,
2026-09-18. In the turn the trigger arrives, finish the step in hand, then:

1. **Handoffs** — `$WI handoff` on every open item, as above.
2. **Push** — `main`, as above; a rejection stops the same way and goes under
   `decisions needed`.
3. **Checkpoint** — run the checkpoint skill with goal *continue* (argument `continue`,
   so its Step 0 skips the goal question). The manifest it writes and the checkpoint it
   records are what make the compaction safe; the rehydration hook re-injects the
   manifest afterwards.
4. **Prompt the operator to compact, and stop.** This turn's closing message is the
   final Report of the sequence above: the four-line Report for anything landed since
   the last one, the push outcome, then the checkpoint's own close — its Step 5
   recommendation as `/compact <guidance>`, to run at the operator's convenience (the
   next morning is fine), with `/librarian-mode start` as the Step 7 opener. Never run
   `/compact` yourself, and start no new work — no dispatch, no merge — in that turn.

After the compaction, Rehydrate (SKILL.md) and carry on from `wi prime`; the manifest
and ledger outrank the machine summary.
