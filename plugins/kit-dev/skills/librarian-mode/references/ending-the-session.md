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
