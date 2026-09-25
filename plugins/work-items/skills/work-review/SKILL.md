---
name: work-review
description: On-demand, read-only review of the work items across every repo checkout beside this one — sweeps each repo's work-item store with `wi estate`, then writes the operator an overview — security items first, each repo's state in plain words, the decisions waiting on them and where to answer them, stale claims, and prioritisation advice with one recommendation and its reason, plus a quota line when a usage reading is available. Use when the operator says "review my work items", "work review", "overview of all the work items", "what should I work on next across my repos", "what's open everywhere", "prioritise my repos", or asks for a cross-repo summary of work. Not for one repo's queue (the work-items skill's `wi next`), not for answering or relaying another repo's decisions, and never scheduled or unattended.
---

# Work review

The operator's summary of every repo's work, on demand. `wi estate` gathers the facts from
every store; this skill supplies the judgement and writes it up. It runs when the operator
asks, and only then: nothing here is scheduled, and nothing runs unattended.

```bash
WI="python3 ${CLAUDE_PLUGIN_ROOT}/skills/work-items/scripts/wi.py"
```

## Important

- **Read-only across repos.** Never claim, hand off, close, set, lint or edit anything in
  another repo's store, and never commit there. The only reads are `wi estate` and
  `$WI --root <store> show <id> --brief`. A fix you spot goes into the overview as advice.
- **Decisions are shown, not answered.** List each repo's open decisions so the operator
  knows they are waiting, and say that each one is answered in that repo's own session.
  Never record an `answer N:` in another repo's store, and never pass the operator's reply
  on to that repo's session by message: an answer carried that way does not carry the
  operator's authority. How answers could be given from this summary is an open question
  the operator has not ruled on yet.
- **Plain words for items.** Name every work item by what it is ("move the nightly
  export off the old host"), with its id at most as a trailing tag: `(a1b2)`, the last four
  hex of the id.
  A bare id means nothing to the operator.
- Secrets: an item may name a path or key; never print a value, even one found in an item.

## Step 1: Sweep

```bash
$WI estate --json            # the parent dir of this repo's main checkout, one level of repos
$WI estate --dir DIR --json  # another dir, or several: --dir A --dir B
```

Exit 2 means no store was found: say so, name the dir scanned, and stop. Exit 1 means the
dir must be named with `--dir`: the session is outside a git repo, or the default would be
`$HOME`, a dir above it, or `/`, which the sweep refuses to take as a default. Repos are
kept one per git repository: a linked worktree beside its main checkout, and a symlinked
alias of a repo, are skipped and listed in `skipped` with the reason. A worktree whose main
checkout is not in the scan (a bare repo's checkout), a `--separate-git-dir` clone and a
submodule are their own repos and are kept. Each list is capped per store; `omitted` counts
what was left out. The JSON gives, per store: `counts`
(`open`, `todo`, `doing`, `blocked`, `parked`, `grooming`, `ready`, `done`, `dropped`),
the top `ready` items in `wi next` order, unanswered `decisions` (with `raised` and
`age_days` when the stored card has a `raised:` line), `stale` doing claims (older than
`--stale`, default 24h), `security` items, and `problems`.

`security` is a keyword hint (a security- or privacy-shaped tag, or a title naming a
secret, credential, password, key, leak or exposure), not a verdict. Confirm each one before calling
it a security item, and look for real ones the hint missed.

## Step 2: Read only what the advice needs

The sweep is enough for counts and lists. Read an item in full only when the overview
depends on it: every security item, the one or two items you are about to recommend, and an
item whose title does not make clear what it is.

```bash
$WI --root <repo path>/<store> show <id> --brief
```

`path` is printable: a name byte that is not UTF-8 shows as `\xe9` and will not open. When
`path` holds such an escape, take the real path from `path_raw` (the exact bytes, base64):
`python3 -c 'import base64,os,sys; print(os.fsdecode(base64.b64decode(sys.argv[1])))' <path_raw>`.

Keep the reads few. A store listed with `problems` is reported as it stands; do not repair
it.

## Step 3: Quota, when there is a reading

The `statusline-hub` plugin, when installed, writes a sensor record on every status-line
render at `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<session-id>.json`; the session
id is the UUID segment of the scratchpad directory named in your system prompt. Read
`rate_limits.five_hour` and `rate_limits.seven_day` (`used_percentage`, `resets_at` in epoch
seconds). Treat the record as absent when its `v` is not 1 or its `rate_limits.at` is more
than 30 minutes old. A `resets_at` in the past means that window has reset.

With a reading, the overview carries one quota line, and the advice weighs it: near a limit
(five-hour at 75% or more, or weekly at 90% or more), recommend small or cheap items and say
when the window resets, in local time. Without a reading, say "no quota reading" and advise
without it. Never guess the numbers.

## Step 4: Write the overview

Write it in this order, short enough to read in two minutes:

1. **Security first.** Every confirmed security item across all repos, most urgent first:
   what it is, which repo, its state, and why it matters now.
2. **Each repo in plain words.** One short paragraph or a few lines per repo that has open
   work: what is in flight, what is blocked and on what, what is ready next. Skip counts the
   operator cannot act on. Group quiet repos into one line ("garden-api, notes: nothing
   in flight, a few ready items each").
3. **Waiting on you.** The open decisions, per repo, each named in plain words with how long
   it has waited when `age_days` is known, and the note that it is answered in that repo's
   own session. Oldest and most blocking first.
4. **Stale claims.** Work marked doing with an old claim: name it and its owner, and suggest
   the owning session check it. Do not release it.
5. **What to do next.** One recommendation, then at most two runners-up. For each: what it
   is, which repo, and the reason it goes first. Weigh, in this order: security; anything
   blocking other work or waiting on a deadline; a decision whose answer unblocks the most
   work; priority and age; cost, against the quota reading. When you recommend answering a
   decision, name it and its repo; do not restate its options as if asking it here.
6. **Quota.** The line from Step 3, or "no quota reading".
7. **Problems.** Any store or file the sweep could not read, with its path, so it can be
   repaired in that repo.

When the overview needs a decision from the operator (which repo to take up next, say), put
it last, after the overview. When the `decisions` skill from the operator-interaction plugin
is loaded, follow it for how to write that decision. Without it, give a numbered list: one
decision per number, each option with its impact, the recommended option first, and
"decide later" always offered.

## Examples

Operator: "Give me an overview of the work items across my repos and what to do next."
Actions: `wi estate --json`; `show --brief` on the two security items and the recommended
item; read the sensor record.
Result: two security items first (garden-api's "rotate the webhook signing secret (c3d4)",
already in flight, and photo-sync's "stop logging request credentials (e5f6)"); a few lines per
active repo; four decisions waiting, the oldest named first; one stale claim; a
recommendation to finish the signing-secret rotation first, because it is in flight and every
client depends on it; a quota line; no problems.

Operator: "work review for ~/src/other-org"
Actions: `wi estate --dir ~/src/other-org --json`, then as above.

## Troubleshooting

- **`not in a git repo; name the dir to scan with --dir`**, or **`the default scan dir would
  be …`**: the session is outside a repo, or the repo sits directly in `$HOME` or above it;
  ask which dir holds the checkouts, or use the one the operator named.
- **A repo is missing from the sweep**: its store is not at `.claude-sandbox/work/` or
  `.work/` directly under the repo, the repo is more than one level down, or the repo or store
  is a symlink leading out of the scanned dir, which the sweep never follows. Or it shares its
  git repository with another entry that was kept: check `skipped`, which names the entry and
  why. Name it rather than hunting for it.
- **A `problems` entry on a store**: a file that does not parse, an empty file left by an
  interrupted write, or a symlink out of the dir. The rest of that store is still counted.
  Report it; the repair is `wi lint` in that repo's own session.
