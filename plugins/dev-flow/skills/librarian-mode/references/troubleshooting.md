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
- **Push rejected (non-fast-forward or fetch first).** Someone pushed to origin/main
  since the last sync — the operator or another trusted pusher. Merge it in, never
  around it: no rebase, no reset, no `--force`. The rule the merge keeps is that nothing
  unreviewed lands silently — every incoming commit is named to the operator, and
  nothing is pushed until the Checks pass on the result. While a push-rejection decision
  is open, skip every later push and carry that decision under the same number.

  1. **Fetch and look.**

     ```bash
     git -C "$MAIN" fetch origin
     git -C "$MAIN" log --format='%h %s — %an' main..origin/main   # the incoming commits
     git -C "$MAIN" diff --stat main...origin/main                  # what they touch
     git -C "$MAIN" log --oneline origin/main..main                 # local commits
     ```

     No local commits (`main` strictly behind): `git -C "$MAIN" merge --ff-only
     origin/main`, send the `incoming:` lines, and there is nothing to push. More than
     five incoming commits, or an incoming file that an in-flight item or this
     session's landings touch: you may raise a numbered decision instead of merging,
     with the list as its evidence — a judgment, not a must; say which you chose.
  2. **Merge, uncommitted.** On `main` in the main checkout:
     `git -C "$MAIN" merge --no-ff --no-commit origin/main`. If git refuses to start —
     tracked dirt in a file the incoming commits touch, staged changes anywhere,
     untracked files in the way — stop and raise it; clear nothing to make it start.
     From here until the merge is committed or aborted, **no other commit to `main`**:
     no store commit, no landing.
  3. **Check the result.** Run every `Checks:` command from `$MAIN` against the merged
     tree. All green: `git -C "$MAIN" commit --no-edit`, a merge commit.
  4. **Push, then send the incoming lines.** `git -C "$MAIN" push origin main` — now a
     fast-forward — then one `incoming: <sha> <subject> — <author>` line per incoming
     commit. The `incoming:` lines go with the push outcome: a short follow-up message
     mid-session, since the Report has gone out; inside the final Report at session end
     and 75%/DUE (SKILL.md § Report). A second rejection repeats from step 1 once; a
     third is a decision.

  **A conflict at step 2, or a red check at step 3, stops:** `git -C "$MAIN" merge
  --abort`, so `main` is as it was before the merge, and raise a numbered decision
  naming the conflicting paths or the failing check and the incoming commits. Never
  resolve a conflict in custody files by hand: the recommended option files a work item
  whose implementer merges `origin/main` into a worktree branch cut from local `main`
  and resolves it there — a conflict round, reviewed like any other, the shape of the
  `dev-cycle` skill's `references/fix-loop.md` § A merge conflict — and lands it through
  The cycle; the other is the operator resolving it on origin. The decision goes under
  `decisions needed` — the next Report mid-session, the final Report at session end.
- **A merge left uncommitted in the main checkout.** `git -C "$MAIN" rev-parse -q
  --verify MERGE_HEAD` succeeds at Rehydrate step 4, or before any store commit: a merge
  was interrupted before its commit or abort (a push-rejection merge after its
  `--no-commit`, a landing merge stopped on a conflict). `MERGE_HEAD` is per-worktree —
  this can only be a merge the main checkout itself ran, never a conflict round's merge
  inside a linked worktree, which is invisible here. Never commit it as found — its
  Checks result is gone. Which merge it was decides the redo, so compare
  `git -C "$MAIN" rev-parse --short MERGE_HEAD` against `origin/main` and the
  `worktree-*` branch tips (`git -C "$MAIN" branch --list 'worktree-*' -v`'s short shas)
  before aborting:
  - **`origin/main`'s commit**: a push-rejection merge (§ Push rejected step 2) —
    `git -C "$MAIN" merge --abort`, then redo § Push rejected from step 1.
  - **A `worktree-*` branch's tip**: a landing merge (`git -C "$MAIN" merge --no-ff
    worktree-<name>`, SKILL.md § The cycle's Terminal action) — `git -C "$MAIN" merge
    --abort`, then re-land that branch through The cycle (Checks again).
  - **Neither**: `origin/main` was fetched again since, or the branch moved after the
    crash — `git -C "$MAIN" merge --abort`, then raise it as a numbered decision.
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
