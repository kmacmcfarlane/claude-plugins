# Troubleshooting

Failure modes the librarian meets while running SKILL.md's loop, and what to do about
each. Pointed at from SKILL.md § Troubleshooting; the Rehydrate and Review steps point
here for the glob and orphan-worktree cases.

- **`wi` not found by the glob.** Normal when the repo does not carry the plugin: use the
  installed copy and set `WI_ROOT` explicitly. No store at either standard root: `start`
  and `intake` run `$WI init` once a custody layer resolves; `status` reports "not opted
  in; `start` offers opt-in" when CLAUDE.md has no `## Librarian` section, else "no
  store", and stops.
- **`wi claim` exits 4.** Another session holds the item. Do not force; report it.
- **Agent (implementer or reviewer) returns `BLOCKED` on permissions.** A decision for
  the operator, not a reason to do the work yourself: block the item and report.
- **Merge conflict on `main`.** Resolve by reading both sides with the item's approach as
  tiebreaker; never take one side wholesale. If the resolution needs judgement, re-dispatch
  with `main` as the new base.
- **Orphan worktree from a crashed session.** Dirty: surface it, do not remove. Clean and
  merged: remove it; clean and unmerged: ask.
- **A fable dispatch returns HTTP 429 or a usage-credits error.** Not a `BLOCKED`: the
  reset time decides between opus and asking — a `model: fable` pin always asks —
  `model-routing.md` § Fallback.
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
root and carries no `wi`), same `WI_ROOT`. The key is the harness's own install record, `installed_plugins.json`
`plugins['work-items@kmacmcfarlane'][0].installPath`; the newest cached version (`ls -t`)
is the fallback when that record is missing or unreadable:

```bash
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
WI_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["work-items@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py | head -1)
WI="python3 $WI_PY"
```

An empty `WI_PY` after both means `work-items` is not installed on this machine — install
it (`/plugin install work-items@kmacmcfarlane`) before continuing.
