# HANDOFF.md — the rehydration manifest

One per repo, **authored by the checkpoint skill** (never machine-synthesized: intent
is a snapshot only its author can write; the facts around it — age, drift, dirty count
— are computed live by `hooks/rehydrate.py` at injection). Work-addressed (class b1):
lives at `.claude-sandbox/HANDOFF.md` when `.claude-sandbox/` exists (so `trackInHost`
governs it), else `HANDOFF.md` at the repo root. Write-side budget **≤6,000 chars**;
the hook trims Scrolls → Aware-of and never the mandatory tiers (nor In flight or Copy
forward), under its 9,000-char injection cap.

## Format

```markdown
---
handoff: 1
repo: <name>
session: <session-id>   # $CLAUDE_CODE_SESSION_ID: this session, never the replaced manifest's
written: 2026-08-30T21:40:00Z
head: <short-sha>
branch: <branch>
mode: land | continue | handoff | landed
by: checkpoint
mode_skill: /<plugin>:<mode> start   # optional: the standing mode to re-enter
items:            # optional: wi ids you expect still open or in flight
  - <work-item-id>
---
## Doing
2–3 lines, present tense: what is in flight and where it stands.

## Goal
mode: <land|continue|handoff> — operator: "<their last stated goal, verbatim>"

## In flight
One line per live or resumable agent this session dispatched; `None` when drained.
- <role> — <work item> — agent <id> — round <n> — waiting on <what>

## Read in full
≤5 paths, one per line with WHY each cannot be skipped. This is raw rehydration:
the next session reads these before doing anything else.

## Copy forward
Files a successor needs that still sit only in a session scratchpad; omit when none.
- <absolute path> — <what it is, where to copy it>

## Aware of
Tagged one-liners. A CORRECTION outranks the claim it corrects; REFUSED stays refused.
- CORRECTION <what was wrong, what is right>
- REFUSED <capability/action the operator declined>
- DEFERRED <decision parked, and its owner>
- DECIDED <choice + one-clause why>
- OPEN <question, owner, blocks-or-not>
- BELIEF <unverified assumption, labelled>
- HARNESS <friction to route to the plugin repo>

## Next
1–2 actions. Work-item IDs (`wi show <id>`) once a store exists — the store, not
this section, is the durable record of what is next.

## Scrolls
TOC, read on demand: `path — one line on what it holds`.
```

## Rules

- **Secrets: path and key, never value.** A manifest lands in git; sops and `kind: Secret`
  gates do not see prose. Name where a secret lives, never what it is.
- **In flight is a roster, not a summary.** Every agent this session dispatched that is
  running or resumable gets a line — implementer and reviewer alike, since a reviewer's
  rounds of context are the costliest thing to lose. `round` is the review or fix round the
  agent is on (`1` for a first pass); `waiting on` is what the agent or its next step waits
  for (its own return, a review, a fix round, an operator decision). Background agents
  survive `/clear` in the same Claude Code process and resume by id (verified): the
  successor resumes each one with `SendMessage` to its id and **does not re-dispatch it
  fresh** — a fresh agent re-derives every round the old one holds. Their output files
  stay under the predecessor's session dir (`…/<old session>/tasks/`); `/clear` does not
  move them. A fresh process (the session exited and relaunched) cannot resume them; there
  the roster tells the successor what to re-dispatch and from which round. The hook never
  trims this section.
- **Nothing a successor needs lives only in a session scratchpad.** The scratchpad is
  session-scoped: `/clear` gives the successor a new, empty one while `tasks/` stays
  behind, so a path into the old scratchpad works only by accident. Before writing the
  manifest, copy every such file — a stage file, a brief template, a working note — to the
  work item or its investigation series and name the copy; or, when it cannot move now,
  list it under **Copy forward** by absolute path. Never point Read in full or Scrolls
  into a scratchpad.
- **Stage boundary in a skill chain:** the published stage file is the authoritative record —
  **Read in full** points at it, and the manifest carries only what the files do not hold
  (deploy state, test fixtures/accounts, cross-ticket blocks, model/agent rules,
  CORRECTION/REFUSED lines).
- The hook labels the manifest FRESH (fresh), AGED (>24h, any commit drift, or a recorded
  `head` that no longer describes HEAD by ancestry), STALE (>7 days or >30 commits of drift,
  counting both sides — commits ahead plus commits behind, so a HEAD 50 behind is STALE — goal
  lines must be re-confirmed with the operator), LANDED (`mode: land*` — header-only, the work
  is done). Drift never counts commits that touch only `.claude-sandbox/work` (store chores),
  so a HEAD rewound over (or diverged by) store-only commits is no code drift: it reads FRESH
  with Next shown, not "not an ancestor"; and when the only commits HEAD lacks are store-only
  while HEAD gained code, it reads as plain forward movement (`AGED`, "N commits since"). The
  label and the Next withhold read the same ancestry check, so a withheld Next is never FRESH:
  a recorded head missing locally reads `AGED (recorded head not found locally)`, one that is
  not an ancestor of HEAD (HEAD rewound behind it, or diverged) reads
  `AGED (recorded head is not an ancestor)` — `STALE (<reason>)` when age or drift already
  make it STALE. When the recorded head cannot be checked at all, the checks degrade to the
  plain manifest (Next shown) and the label carries the reason, so an unverified manifest
  never reads as plain FRESH: `(git unavailable)` when git itself does not run (not
  installed, failing, or hung past its 5s timeout), `(head unverified)` when git runs but
  there is no HEAD to check against (the manifest sits outside a repo, or the repo has no
  commits) — e.g. `FRESH (head unverified)`, or `AGED`/`STALE` on age. The one-line
  `systemMessage` shown to the operator carries the same label and reason
  (`Rehydrated from AGED (recorded head is not an ancestor) manifest (...)`).
- **Current repo state outranks the manifest.** git log and the work-item store are the
  durable record; the manifest is only the reasoning. The injected precedence line says so:
  repo state beats the manifest; the manifest and ledger beat any machine summary.
- **`items:`** (optional) lists the work-item ids the author expects open or in flight —
  Step 4b fills it with the `wi` ids of open or doing items the manifest mentions. When a
  store is found (`WI_ROOT`, else `.claude-sandbox/work`, else `.work`), the hook names each
  id now done, dropped or missing as `DEAD CLAIM <id> (<status>)`, in every tier. Ids resolve
  as `wi` does (id, alias, unique prefix); `# comments` are ignored; only the first 50 are read;
  entries that are not id-shaped are skipped and counted on one line
  (`items: <N> unparseable entr(y|ies) skipped`) under its own heading, "Manifest `items:`
  entries not checked against the store" — not under the dead-claims heading, since the store
  contradicts nothing there. No store: silent. When the hook trims for budget it collapses
  only the frontmatter `items:` list (LF or CRLF line endings); an `items:` line in the body
  is left alone.
- **`mode_skill:`** (optional) names the standing mode the session was running — a skill
  that holds the session in a role until told otherwise (a librarian, a watcher), not a
  one-shot skill it merely used — as the slash command the operator would type to enter it,
  arguments included (e.g. `/dev-flow:librarian-mode start`). One command, not a list. Set
  it in every mode but *landed*; omit it when no standing mode is active. Its presence tells
  the next session to re-enter that mode first: the checkpoint's Step 7 opener leads with it,
  and the hook names it on the header line in every tier except LANDED. Any skill's command
  may go here; the format knows none by name. Accepted shape, whole value (quotes around
  it allowed): `/name` or `/plugin:name` — a letter or digit first, then letters, digits,
  `_`, `.`, `-` — followed by at most four arguments of letters, digits and `_ . : = / -`,
  single spaces between, ≤200 chars in all. Anything else (backticks, prose, punctuation,
  control characters) is dropped silently: the header speaks in the hook's voice, and a
  committed manifest is text anyone can write. On a STALE manifest the header names the
  mode for the operator to confirm instead of telling the session to re-enter it.
- **Stale Next is withheld, not warned.** When the recorded `head` is not an ancestor of
  HEAD, or HEAD is ≥1 commit past it, the hook replaces the `## Next` body with one line.
  Its variants:
  - ahead, N ≥ 2: `Next withheld: head moved <N> commits since this manifest
    (<recorded>..<current>); run wi prime and git log.`
  - ahead, one commit: `... head moved 1 commit since this manifest (<recorded>..<current>); ...`
  - not an ancestor (HEAD rewound behind the recorded head, or diverged from it): N is the
    commits on HEAD's side and M those on the recorded head's side, from one
    `git rev-list --left-right --count <recorded>...HEAD`, so a pure rewind reads
    `0 commits ahead, M behind` (M ≥ 1: with M = 0 the recorded code is still under HEAD, so
    it reads as the plain ahead variant above, or FRESH with Next shown when N = 0 too):
    `... head moved <N> commit(s) ahead, <M> behind since this manifest (<recorded>..<current>,
    recorded head is not an ancestor); ...`
  - not found locally (N is unknowable): `... head moved ? commits since this manifest
    (<recorded>..<current>, recorded head not found locally); ...`

  Other sections stay. Commits touching only `.claude-sandbox/work` (store chores) do not
  count toward N or M. No time-based expiry — the head check covers it.
- A LANDED manifest skips both checks (no dead claims, Next not withheld): the work is done.
  Either check degrades to the plain manifest if git or the store fails.
- Injection tiers: `compact` → full + ledger tail; `resume`/`fork` → full only when the file
  or repo changed since last injection, else one header line; `startup`/`clear` → header only.
- **`session:` is the author's own id**, read from `$CLAUDE_CODE_SESSION_ID` when the
  manifest is written (Claude Code sets it for every Bash call, and it follows `/clear`).
  Never copy it from the manifest being replaced: after `/clear` or a handoff that id is the
  predecessor's, and since the field is the ownership key below, the new manifest would be
  foreign to its author and re-injected in full into the predecessor. `mark_checkpoint.py`
  warns when the manifest's `session:` is not the id it is given.
- **Whose memory it is.** Those tiers apply only to a manifest this session owns. Ownership
  names a *version* — the `session:` field plus the hash of the file's raw text — so a
  rewrite is a new version. A version is this session's when:
  - it has no `session:` (a hand-written manifest is everyone's);
  - this session wrote it (`session:` is its id), any version;
  - a link pinned exactly that version: a `/clear` successor is linked to the session that
    ran `/clear` (same Claude Code process), a fork to its parent, and both inherit the
    linking session's own links, up to 8 deep. A link pins the version on disk only if it
    was the linking session's own at that moment — a manifest a third session overwrote is
    never passed on;
  - this session **read exactly that version in full** and its `mode:` is `handoff`.

  Anything else — another session's manifest, or a later rewrite by a parent, a resumed
  predecessor or an adopted author — gets one header line on every source, naming the path
  and the author session, with no body, no precedence line and no standing mode: "If the
  operator's opener names this manifest, read it in full; otherwise it is another session's
  and not your memory." The derived check lines still follow it — dead claims, unparseable
  `items:`, and the Next-withheld line — since they describe the file, not anyone's memory.
  The ledger tail and `/compact` guidance still inject on `compact`.
- **Reading adopts; `cat` looks.** A whole-file Read (no offset, no limit) of a `mode:
  handoff` manifest adopts that version: it is re-injected into this session after a
  compaction. To look without adopting, use `cat` (a Bash read) or a Read with an offset or
  limit. A `continue` or `landed` manifest is never adopted by reading it; a subagent's Read
  adopts nothing.
- Updating: every checkpoint rewrites it wholesale (it is a current view, like an INDEX, not a
  log — history lives in git).
