# Rehydrate

The five steps SKILL.md § Rehydrate lists as headlines, in full. Do this at session start
and after any `/clear` or compaction. Never `ls` the whole store.

## Step 1 — Locate the main checkout and the store

Run the `dev-cycle` skill's `references/bindings.md` § Store snippet, dev-flow's canonical
copy of the lookup: it sets `MAIN`, exports `WI_ROOT` for the store it finds, and prints
the `wi` command, from the repo's own tree or else the installed plugin's copy. The
librarian's store is `$MAIN/.claude-sandbox/work`, or an existing `.work/` one, which the
snippet finds too. When it prints `no wi found`, `work-items` is not installed, and the
librarian cannot run without it — its whole queue is the store. Stop there: say
"librarian-mode needs work-items, which is not installed: /plugin install
work-items@kmacmcfarlane", and touch nothing else (no opt-in, no store, no dispatch). This
is a repair notice, not a peer hint, so the hint switch never hides it. No store yet, or a
`.work/` one: `first-start.md`. `MAIN` is not this session's cwd: a worktree session — say
so and route every edit through dispatch (SKILL.md § Red flags).

## Step 2 — Read the custody docs

CLAUDE.md's `## Librarian` section: `Scope:`, `Exclude:`, `Checks:`, `Push:` (missing
reads as `main`), `Workflow:`. No section → the opt-in (`opt-in.md`; `status` only reports
it). Then `README.md` — its doctrine, catalog and placement sections when present,
otherwise in full — the rest of `CLAUDE.md` (layout and conventions), and the `dev-cycle`
skill's SKILL.md in full, the cycle every item runs. On re-entry, re-read only the
section, the conventions and dev-cycle's Steps 1–5. When the session lists
`operator-interaction:decisions` or `operator-interaction:plain-names`, load each, every
time: every decision you raise follows the first (`decisions.md`), and every message to
the operator names items by the second. Without `plain-names`, the Report and table
templates carry its rule: `<plain name> (<tag>)`.

## Step 3 — Prime the queue, then read the one item you are working

```bash
$WI prime
$WI show <id> --brief      # for each item marked doing by you
$WI ls --tag hold          # active holds
grep -rh '^decision [0-9]' "$WI_ROOT" | sort -k2 -n | tail -1  # last decision N
```

Take each `doing` item's record up by the `dev-cycle` skill's `references/resume.md`,
whose § LIVE probes the ids its `agent:` lines (and In flight) name, and whose Group B
attaches or salvages. Then migrate any retired decision tag in the store, as
`decide-alone.md` § Retired spellings gives it (no hit, no write). Then, for each item
blocked `watching <repo> <their id>`, the read-only status check of SKILL.md § Intake
step 4 (`forwarding.md`), and for each `awaiting <repo> librarian` or `operator: forward
to <repo> owner down`, its liveness check.

## Step 4 — Inventory the tree

```bash
git -C "$MAIN" status --short
git -C "$MAIN" worktree list
git -C "$MAIN" branch --list 'worktree-*'
```

`git -C "$MAIN" rev-parse -q --verify MERGE_HEAD` succeeds here or before any store
commit: a merge interrupted in the main checkout — a push-rejection merge or a landing
merge, told apart by comparing `MERGE_HEAD` against `origin/main` and the `worktree-*`
branch tips — `merge --abort`, then the matching redo, or a decision when neither matches
(`troubleshooting.md`). A worktree with no live agent (step 3's probes; ListAgents for any
agent no item records) and no `doing` item is an orphan — see `troubleshooting.md`.

## Step 5 — Context-guard

When the session's skill list has no `context-guard:checkpoint`, nothing watches this
session's context: no gate advisory arrives, so `ending-the-session.md` § At 75% never
fires, and there is no checkpoint and no manifest to rehydrate from. Disclose it in the
first expected-output paragraph of each conversation, whatever the argument (`start`,
`status`, `intake`), as one clause: "no context-guard: no checkpoint, no context gate;
handoffs kept current at each idle turn and landing". A Rehydrate after compaction does
not repeat it. The store then carries what the checkpoint would have:

- the in-flight roster is the `agent:` lines dev-cycle already writes at each dispatch
  (the `dev-cycle` skill's `references/record-lines.md`); nothing more is needed;
- every standing hold is a `hold` item;
- after each Idle turn's dispatches, and at each Report or landing, `$WI handoff`
  (`ending-the-session.md`) on each `doing` item whose state changed since the last
  refresh;
- when the operator says they will compact or clear: the forwards sweep
  (`ending-the-session.md` § Forwards), that refresh, then the push
  (`ending-the-session.md`, "Then push what landed"), then the closing Report.
