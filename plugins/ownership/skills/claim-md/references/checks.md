# The claim check

Two kinds of check: the mechanical one, `scripts/claim_check.py`, and the reading checks, the
session's own judgement. Both run **on demand**: when check mode runs, or in a sweep across
the repos. Nothing runs continuously. The line forms the script parses are `format.md` § 10.

## Running the script

`scripts/claim_check.py` is under this skill's base directory. Run it with `python3`:

```
claim_check.py [--repo DIR] [--claim PATH] [--estate] [--dir DIR] [--today YYYY-MM-DD] [--json]
```

- `--repo` is the repo to check, by default the working directory's. A linked worktree
  checks its own files: a claim being written in a worktree is the one checked.
- **The repo's name** is always its main checkout's directory name, found through the
  common git dir, also from a linked worktree. That name is used in the output, in matching
  a neighbour's `### <repo>` heading, and for "this repo".
- `--claim PATH` checks the file at `PATH` as the repo's CLAIM.md: a draft, before it is
  written. The repo's identity, siblings and CLAUDE.md still come from `--repo`. A pointer
  into this repo's CLAIM.md reads the draft, which need not be tracked.
- **The sibling dir** is the parent of the main checkout. `--dir` names another. A default
  dir that is `$HOME`, an ancestor of it, or `/` is refused: with `--estate` that is exit 2;
  for one repo the neighbour checks are skipped and a note says so.
- A **sibling** is a direct child of the sibling dir holding a `.git` directory. A child whose
  `.git` is a file (a linked worktree or a submodule) is listed as skipped, and so is a child
  that resolves outside the dir. A sibling "has a store" when `.work/items/` or
  `.claude-sandbox/work/items/` exists in it.
- **Without `--estate`** the script checks this repo's claim and CLAUDE.md, and compares its
  claim with the claims of the siblings it names. **With `--estate`** it checks every
  sibling. With `--estate`, the files of `--repo` replace its main checkout's entry, so a
  worktree's draft and main's copy are never both loaded.
- `--today` fixes the clock, for tests.
- **Read only.** The script never writes and never opens the network. It runs git with fixed
  arguments, drops git's stderr, reads git's stdout only for the paths `rev-parse` prints
  (the top level and the common git dir), and judges `ls-files` (is a pointed-to file
  tracked?, with literal pathspecs, so a name is never a glob) by its exit code alone.

The thresholds are two named constants in the script: `STALE_DAYS = 180` and
`PENDING_DAYS = 30`.

## The flags

| Flag | Kind | Raised when | Prior art |
|---|---|---|---|
| `SHAPE` | `title`, `status`, `reviewed`, `claim`, `not-ours`, `boundaries`, `changing` | a required part is missing, a date is malformed or not a real date, a line is not in its form (`format.md` § 10), or `## Changing this claim` is not the standard text | GitHub reports CODEOWNERS syntax errors |
| `STALE` | — | `Reviewed:` is more than 180 days before today | RFC 9116 `Expires`; RFC 2350's date of last update |
| `PENDING` | — | `Status: proposed` is more than 30 days before today. An approved claim never | — |
| `UNRESOLVED` | `owner`, `neighbour`, `pointer` | a repo-form owner, a `### <neighbour>`, or a pointer's repo that is not a sibling. `operator` and `external:` are never flagged | GitHub skips owners without access; Gerrit ignores non-resolvable owners and validates on demand |
| `DANGLING` | `file`, `heading`, `outside` | a `Defined in <repo> <file> § <heading>` whose file is missing or untracked, whose file lacks the heading (under `N`), or whose path is absolute, holds `..`, or resolves through a symlink out of the repo | Chromium `file://` includes must resolve |
| `AWAITING` | — | `Defined in <repo> (no claim yet)` where `<repo>` now has a CLAIM.md | — |
| `ONE-SIDED` | — | a `Defined here` item for a neighbour whose CLAIM.md has no `### <this repo>` | Backstage `providesApis` / `consumesApis` |
| `CONFLICT` | `defined-twice`, `owner`, `claimed-and-not-ours` | the same item `Defined here` in A's `### B` and in B's `### A`; one thing under `## Not ours` in two claims with different owners; an area A claims that B lists under `## Not ours` with an owner other than A | RACI's single Accountable |
| `MOVED?` | `missing`, `outside` | an In transit `<repo>:<path>` that no longer exists in that repo, or that is absolute, holds `..`, or resolves out of the repo | — |
| `MISMATCH` | `librarian-only`, `claim-only`, `owner` | the repo has a CLAIM.md **and** its CLAUDE.md has a `## Librarian` `Not owned:` list: a name in only one of the two lists, or in both with different owners. With either list absent there is no comparison | — |
| `UNCLAIMED` | — | with `--estate`, a sibling with a store and no CLAIM.md; for one repo, the checked repo with no CLAIM.md | — |
| `PROBLEM` | `unreadable`, `too-large`, `not-utf8`, `not-regular`, `symlink-out` | a CLAIM.md, a CLAUDE.md or a pointed-to file that cannot be read safely: over 256 KiB, not UTF-8, not a regular file, or a symlink out of its repo. It is not parsed | — |

`MISMATCH` keys on the lines in the files, never on which plugins are installed.

## The output contract

**Text**, one line per flag:

```
<FLAG> <kind|-> <repo>:<file>:<line> <section>[ other: <repo>:<file>:<line>][ owner_form: <form>]
```

then `skipped: <path> (<reason>)` lines and `notes: <note>` lines; the last note counts the
repos checked, the claims read and the flags.

**`--json`:**

```
{"version": 1, "today": "YYYY-MM-DD", "dir": "<path>" | null,
 "repos": [{"repo", "path", "claim", "store"}],
 "flags": [{"flag", "kind", "repo", "file", "line", "section", "other", "owner_form"}],
 "skipped": [{"path", "reason"}], "notes": ["..."]}
```

- `repos[].claim` is `false`, or the absolute path of the claim file read: the repo's
  CLAIM.md, or the `--claim` argument.
- `kind` is `null` for a flag with no kind. `other` is `null` or a location.
- `owner_form` is set on every `MISMATCH` (`repo`, `operator` or `external`: the owner form
  of the line flagged) and `null` elsewhere. It is a fixed word, never the owner's text, so
  a claim-only line with an external owner can be routed (below).

**Never a line's content.** The output holds only fixed words, locations and paths found on
disk, and command-line arguments:

- `file` is `CLAIM.md`, `CLAUDE.md`, or the `--claim` path. A flag about a file named by a
  pointer is given at the pointer's own location.
- `line` is a line number; `0` means the part is missing, or the flag is about the whole
  file.
- `section` is one of `title`, `Status`, `Reviewed`, `Claim`, `Not ours`, `Boundaries`,
  `In transit`, `Changing this claim`, `Librarian Not owned`, `file`, or
  `Boundaries / <repo>`, where `<repo>` is printed only when the subsection's name equals a
  sibling's directory name, in the listing's spelling; any other subsection is
  `Boundaries subsection`.
- `other:` is only ever the location of the other line, in CONFLICT, ONE-SIDED and MISMATCH.
- Path bytes that are not UTF-8 are escaped.

**Exit codes:** 0, the run finished with no flag; 1, it finished with flags; 2, a usage error
or a refusal (a fixed message on stderr); 3, an internal error. On an internal error stderr
holds only `claim_check: internal error; details are not printed`, never the exception.

## The reading checks

After the script, read the claim against the repo, as the session's own judgement:

- the areas under `## Claim` still match what the repo's tree and README say it does;
- `## Not ours` still covers what is next door;
- two claims that overlap in meaning, not only in text.

## Where each finding goes

"This repo" is the repo the check ran for: its own claim or CLAUDE.md. A flag found in
another repo's files is **reported only**, never filed there. The operator decides whether it
is relayed to that repo's session as a request. Substance and upkeep are `format.md` § 7.

| Flag (kind) | In this repo | Substance or upkeep |
|---|---|---|
| `SHAPE` title, reviewed, changing | restore the line or the standard text | upkeep: the approved form is restored, and the meaning is unchanged |
| `SHAPE` status | restore it from the recorded approval; with no record, write `proposed` | upkeep when the approval is recorded; otherwise substance: the claim goes to the operator for approval |
| `SHAPE` claim, not-ours, boundaries (a part missing, or a malformed line) | write or repair the part | substance when content is added or changed; upkeep when only the line form is repaired and the meaning stays |
| `STALE` | review the claim (the reading checks) | upkeep (a Reviewed bump) when nothing changed; substance for any change found |
| `PENDING` | show the pending approval to the operator again | substance (the decision already open) |
| `UNRESOLVED` owner, neighbour, pointer | correct the name | upkeep for a typo or a renamed repo; substance when the owner or neighbour no longer exists |
| `DANGLING` file, heading, outside | fix the pointer | upkeep when it follows a landed neighbour change (a moved file or heading); substance when the defining text is gone, so the item needs a defining side: to the operator |
| `AWAITING` | point at the neighbour's new claim | upkeep |
| `ONE-SIDED` | nothing in this claim; the neighbour lacks a pointer | reported for the neighbour |
| `CONFLICT` defined-twice, owner, claimed-and-not-ours | — | substance: a decision to the operator |
| `MOVED?` missing, outside | close the row, or correct the path | upkeep when the move landed or the path was renamed; otherwise to the operator |
| `MISMATCH` librarian-only | add the line to `## Not ours` | substance: to the operator |
| `MISMATCH` claim-only, `owner_form` repo or operator | copy the line into the librarian's `Not owned:` | upkeep, reported |
| `MISMATCH` claim-only, `owner_form` external | — | reported only, never copied: the librarian list's owner is a repo name or `operator`, and has no external form |
| `MISMATCH` owner | — | substance: to the operator |
| `UNCLAIMED` (this repo) | offer write mode | substance (a new claim) |
| `UNCLAIMED` (estate) | — | reported: the estate's progress |
| `PROBLEM` unreadable, too-large, not-utf8, not-regular, symlink-out | fix the file by hand | upkeep when the content is kept; substance when the content changes |
| reading-check gaps and overlaps | — | substance: a decision to the operator |

A fix in this repo is filed as a work item when the work-item tool and a store are present
(SKILL.md § Peers); otherwise it is listed in the result.

**The event signal.** An ownership question that recurs, or a work item routed to the wrong
repo, means a claim is missing a line: file a claim-update item in this repo, or report it
for the repo that owns the thing.
