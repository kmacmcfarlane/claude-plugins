# Troubleshooting

Failure modes the librarian meets while running SKILL.md's loop, and what to do about
each. Pointed at from SKILL.md § Troubleshooting; the Rehydrate and Review steps point
here for the glob and orphan-worktree cases.

- **`wi` not found by the glob.** Normal when the repo does not carry the plugin: use the
  installed copy and set `WI_ROOT` explicitly. No store at either standard root: `start`
  and `intake` run `$WI init` once a custody layer resolves; `status` reports "no store"
  and stops.
- **`wi claim` exits 4.** Another session holds the item. Do not force; report it.
- **Agent (implementer or reviewer) returns `BLOCKED` on permissions.** A decision for
  the operator, not a reason to do the work yourself: block the item and report.
- **Merge conflict on `main`.** Resolve by reading both sides with the item's approach as
  tiebreaker; never take one side wholesale. If the resolution needs judgement, re-dispatch
  with `main` as the new base.
- **Orphan worktree from a crashed session.** Dirty: surface it, do not remove. Clean and
  merged: remove it; clean and unmerged: ask.
- **Implementer disputes a medium-or-above finding.** It cannot decline it: it fixes, or
  states the counter-case for the re-review. The reviewer withdraws on the merits (the
  failure cannot occur) or holds; if it holds, fix it — that round is spent.
- **Push rejected (non-fast-forward).** Someone pushed to origin/main since the last
  sync. Do not pull, fetch, rebase or merge around it, and never `--force`: stop and put
  it under `decisions needed` — the next Report mid-session, the final Report at session
  end.
- **No `origin` remote.** A custody layer in a repo with no remote has nothing to push to:
  skip the push, and say so once in the Report rather than every cycle.
- **Reviewer returns `SHOW_STOPPER` for something a fix would close.** Ask it to state
  the fix path in one line; if a fix exists inside the item's scope, route the verdict as
  `NEEDS_CHANGES` and note the re-routing in the item — routing only; the finding keeps
  its severity.

The same case as Rehydrate step 1 states it, which is where the installed path is:

An empty glob is normal on a repo that does not carry the plugin in its tree: use the
installed `work-items` plugin's copy (not `${CLAUDE_PLUGIN_ROOT}`, which is this plugin's
root and carries no `wi`), same `WI_ROOT`:

```bash
WI="python3 $(ls -t "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py | head -1)"
```

The newest cached version wins; an empty result means `work-items` is not installed on
this machine — install it (`/plugin install work-items@kmacmcfarlane`) before continuing.
