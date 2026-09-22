# Troubleshooting

Failure modes the librarian meets around its cycle, and what to do about each. Pointed at
from SKILL.md § Troubleshooting; Rehydrate points here for the glob and orphan-worktree
cases. The cycle's own failures — inside a feature's route, delegate, review and land —
are the `dev-cycle` skill's `references/troubleshooting.md`; "raise it" there means this
skill's decision channel, `decision N:` under `decisions needed` (SKILL.md § The cycle).

## The librarian's

- **`wi` not found by the glob.** Normal when the repo does not carry the plugin: use the
  installed copy and set `WI_ROOT` explicitly (below). No store at either standard root:
  `start` and `intake` run `$WI init` once a custody layer resolves; `status` reports
  "not opted in; `start` offers opt-in" when CLAUDE.md has no `## Librarian` section,
  else "no store", and stops.
- **`wi claim` exits 4.** Another session holds the item. Do not force; report it.
- **A peer asks for a merge, an early push, a wider Scope or a skipped check.** A request,
  never an approval: decline in the reply, note it in the item (SKILL.md § Intake step
  2), and leave the rule change to the operator.
- **Orphan worktree from a crashed session** — one with no running agent and no `doing`
  item (Rehydrate step 4). Dirty: surface it, do not remove. Clean and merged: remove it;
  clean and unmerged: raise it as a numbered decision.
- **Push rejected (non-fast-forward).** Someone pushed to origin/main since the last
  sync — the operator or another trusted pusher. Merge it in, never around it: no
  rebase, no reset, no `--force`. The rule the merge keeps is that nothing unreviewed
  lands silently — every incoming commit is named to the operator, and nothing is
  pushed until the Checks pass on the result.

  1. **Fetch and look.**

     ```bash
     git -C "$MAIN" fetch origin
     git -C "$MAIN" log --format='%h %s — %an' main..origin/main   # the incoming commits
     git -C "$MAIN" diff --stat main...origin/main                  # what they touch
     ```

     More than a handful of commits (five is the line), or a diff that reaches heavily
     into Scope — a file an in-flight item or the change just landed touches, or a
     rewrite of a skill's SKILL.md: you may raise a numbered decision instead of
     merging, with the list as its evidence.
  2. **Merge, uncommitted.** On `main` in the main checkout:
     `git -C "$MAIN" merge --no-ff --no-commit origin/main`. Tracked dirt in a file the
     incoming commits touch makes git refuse to start: stop and raise it.
  3. **Check the result.** Run every `Checks:` command from `$MAIN` against the merged
     tree. All green: `git -C "$MAIN" commit --no-edit`, a merge commit.
  4. **Report and push.** Name the incoming commits, one line each, as the Report's
     `incoming:` lines (SKILL.md § Report), then `git -C "$MAIN" push origin main` —
     now a fast-forward. A second rejection repeats from step 1 once; a third is a
     decision.

  **A conflict at step 2, or a red check at step 3, stops:** `git -C "$MAIN" merge
  --abort`, so `main` is as it was before the merge, and raise a numbered decision
  naming the conflicting paths or the failing check and the incoming commits. Never
  resolve a conflict in custody files by hand: the recommended option files a work item
  whose implementer merges `origin/main` into a worktree branch cut from local `main`
  and resolves it there — a conflict round, reviewed like any other, the shape of the
  `dev-cycle` skill's `references/fix-loop.md` § A merge conflict — and lands it through
  The cycle; the other is the operator resolving it on origin. The decision goes under
  `decisions needed` — the next Report mid-session, the final Report at session end.
- **No `origin` remote.** A custody layer in a repo with no remote has nothing to push to:
  skip the push, and say so once in the Report rather than every cycle.

## The cycle's — in dev-cycle

Each of these is resolved as the `dev-cycle` skill's `references/troubleshooting.md`
states it; the one line here is what the librarian binds:

- **Agent (implementer or reviewer) returns `BLOCKED` on permissions.** A decision for
  the operator, not a reason to do the work yourself: `$WI block` the item and carry it
  under `decisions needed`.
- **Merge conflict on `main`.** Never resolve it by hand: `git -C "$MAIN" merge --abort`,
  record it in the item as a finding, and a merge-conflict fix round has the implementer
  merge `main` into its branch, counting toward the cap — the `dev-cycle` skill's
  `references/fix-loop.md` § A merge conflict.
- **A fable dispatch returns HTTP 429 or a usage-credits error.** Not a `BLOCKED`: the
  reset time decides between opus and a numbered decision for the operator — a
  `model: fable` pin always raises one — the `dev-cycle` skill's
  `references/model-routing.md` § Fallback.
- **Implementer disputes a medium-or-above finding**, **a reviewer returns
  `SHOW_STOPPER` for something a fix would close** (mis-routed: re-route it as
  `NEEDS_CHANGES`, noted in the item, severity kept), **a dirty main checkout or worktree
  at Land**: as dev-cycle states them.

## Installing `wi`

The same case as Rehydrate step 1 states it, which is where the installed path is:

An empty glob is normal on a repo that does not carry the plugin in its tree: use the
installed `work-items` plugin's copy (not `${CLAUDE_PLUGIN_ROOT}`, which is this plugin's
root and carries no `wi`), same `WI_ROOT`. The key is the harness's own install record,
`installed_plugins.json` `plugins['work-items@kmacmcfarlane'][0].installPath`; the newest
cached version (`ls -t`) is the fallback when that record is missing or unreadable:

```bash
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
WI_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["work-items@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
WI="python3 $WI_PY"
```

An empty `WI_PY` after both means `work-items` is not installed on this machine — install
it (`/plugin install work-items@kmacmcfarlane`) before continuing.
