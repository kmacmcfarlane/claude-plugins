# HANDOFF.md — the rehydration manifest

One per session, **authored by the checkpoint skill** (never machine-synthesized: intent
is a snapshot only its author can write; the facts around it — age, drift, dirty count
— are computed live by `hooks/rehydrate.py` at injection). Session-addressed: it lives in
the Claude config dir at `${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<sid>/HANDOFF.md`
(`python3 hooks/handoff_path.py --path "$CLAUDE_CODE_SESSION_ID"` prints it; `<sid>` is
the session id made path-safe), never in a repo — so no session overwrites another's,
and it is never committed. The path cannot be guessed, so every checkpoint prints it. What
must outlast the config dir goes where Step 3 routes it: the work item's handoff block
(`wi handoff`), the investigation series, the commit. Write-side budget **≤6,000 chars**;
the hook trims Scrolls → Next → Aware-of (keeping CORRECTION/REFUSED) and never the
mandatory tiers, under its 9,000-char injection cap.

**The old layout** — `.claude-sandbox/HANDOFF.md`, else `HANDOFF.md` at the repo root, one
per repo — is never written again. The hook still reads such a file, live and read-only,
for a session that has no manifest of its own (by the ownership rule below), and says once
per session where that session's own manifest lives. Nothing rewrites or deletes it: the
operator removes it when they choose.

## Format

```markdown
---
handoff: 1
repo: <name>
session: <stamped>   # machine fields: the mark step stamps these five, never type them
written: <stamped>
head: <stamped>
branch: <stamped>
top: <stamped>
mode: continue | handoff
by: checkpoint
mode_skill: /<plugin>:<mode> start   # optional: the standing mode to re-enter
next_skill: /<plugin>:<skill> <args>  # optional: the one-shot skill to run next
items:            # optional: wi ids you expect still open or in flight
  - <work-item-id>
---
## Doing
2–3 lines, present tense: what is in flight and where it stands.

## Goal
mode: <continue|handoff> — operator: "<their last stated goal, verbatim>"

## Holds
One line per standing hold, ≤8; `None` when there are none.
- HOLD <what is held> — <why> — until <end condition: decision N | an event | a UTC time>

## In flight
One line per agent this session dispatched that is not finished; `None` when drained.
- <role> — <work item> — agent <id> — round <n> — waiting on <what>

## Read in full
≤5 paths, one per line with WHY each cannot be skipped. This is raw rehydration:
the next session reads these before doing anything else.
One path per line, first on the line (backticked or bare; absolute, or relative to the
root of the repo the manifest records in `top:`). When the hook injects the manifest in full into its own session, it records
these paths; a Read with no offset or limit (the Read tool) marks each one read, and
the next prompt's context names any still unread, once — `cat`, `grep` or a partial Read
does not count. It never blocks and costs no turn.

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

- **Secrets: path and key, never value.** Every session that can read the config dir can
  read a manifest, and its lines get copied into commits and work items; sops and
  `kind: Secret` gates do not see prose. Name where a secret lives, never what it is.
- **In flight is a roster, not a summary.** Every agent this session dispatched that is
  not finished gets a line — implementer and reviewer alike, since a reviewer's rounds of
  context are the costliest thing to lose — whether it is still running or has returned
  and will be resumed (a reviewer awaiting a fix round, an implementer awaiting its
  findings). `None` only when no such agent is left. `round` is the review or fix round the
  agent is on (`1` for a first pass); `waiting on` is what the agent or its next step waits
  for (its own return, a review, a fix round, an operator decision). Background agents
  survive `/clear` in the same Claude Code process and resume by id (verified): the
  successor resumes each one with `SendMessage` to its id and **does not re-dispatch it
  fresh** — a fresh agent re-derives every round the old one holds. Their output files
  stay under the predecessor's session dir (`…/<old session>/tasks/`); `/clear` does not
  move them. After a fresh process (the session exited and relaunched) resuming is
  unverified: try `SendMessage` first, and re-dispatch from the roster's round only if it
  fails. When In flight is not `None`, the checkpoint's Step 7 opener names the ids to
  resume, so the rule reaches the successor before it acts. In flight and Copy forward are
  never trimmed: the hook's trim protects them by name, with Doing, Goal, Holds and Read in
  full (the trim rule below).
- **A hold is a line with an end condition.** Every standing restriction the operator set —
  "no push until decision 52", "dispatch small until the quota resets", "pause the loop
  until 07:00" — goes under **Holds**, not Aware of, one line each: what is held, why, and
  the END CONDITION that lifts it — a decision number (`until decision 52`), an event
  (`until the F1 review is CLEAR`), or a time. Write a time as a UTC stamp (`until
  2026-09-23T07:00Z`; a bare date ends with that UTC day), never "bedtime" or "tonight":
  the hook can only check a time it can read, and a "pause until bedtime" hold once ran 37
  hours. Each line starts with `HOLD` (after its `- `; any case, bold allowed): the hook
  reads only those lines, so prose not led by HOLD is never injected. A hold with no end
  condition is an open question — ask the operator for one. Holds ride on every tier of a
  manifest this session owns: the full tiers inject the section untrimmed; the header-only
  tiers (`startup`, `clear`, an unchanged `resume`) append its lines after the header line
  in compact form (at most 8 lines, 800 chars, control characters stripped, the rest
  counted). A hold whose end clause — the text after its last `until` (or `until:`), else
  after its last ` — ` — leads with a time already past is marked `[expired? confirm: its
  end time has passed]`, never dropped: the successor asks the operator before acting
  against it or lifting it. A decision or an event is never marked, even one that mentions
  a date later in the clause (`until decision 52 (filed 2026-09-20)`): it holds until
  confirmed. The foreign header carries no holds — another session's holds are not this
  session's. Lift a hold by deleting its line at the next checkpoint.
- **Nothing a successor needs lives only in a session scratchpad.** The scratchpad is
  session-scoped: `/clear` gives the successor a new, empty one while `tasks/` stays
  behind, so a path into the old scratchpad works only by accident. Before writing the
  manifest, copy every such file — a stage file, a brief template, a working note — to the
  owning investigation series (or another durable path outside the work-item store) and
  name the copy; or, when it cannot move now, list it under **Copy forward** by absolute
  path. Never copy it into the store's `items/` directory: a file there that is not a work
  item makes `wi ls`, `wi next` and `wi lint` fail. Never point Read in full or Scrolls
  into a scratchpad.
- **Stage boundary in a skill chain:** the published stage file is the authoritative record —
  **Read in full** points at it, and the manifest carries only what the files do not hold
  (deploy state, test fixtures/accounts, cross-ticket blocks, model/agent rules,
  CORRECTION/REFUSED lines).
- The hook labels the manifest FRESH (fresh), AGED (>24h, any commit drift, or a recorded
  `head` that no longer describes HEAD by ancestry), STALE (>7 days or >30 commits of drift,
  counting both sides — commits ahead plus commits behind, so a HEAD 50 behind is STALE — goal
  lines must be re-confirmed with the operator), LANDED (`mode: land*` — header-only, the work
  is done; the checkpoint skill no longer writes it, and the hook still reads it on a
  manifest an older version wrote). Drift never counts commits that touch only `.claude-sandbox/work` (store chores),
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
  it whenever a standing mode is active, in either mode; omit it otherwise. Its presence tells
  the next session to re-enter that mode first: the checkpoint's Step 7 opener leads with it,
  and the hook names it on the header line in every tier except LANDED. Any skill's command
  may go here; the format knows none by name. Accepted shape, whole value (quotes around
  it allowed): `/name` or `/plugin:name` — a letter or digit first, then letters, digits,
  `_`, `.`, `-` — followed by at most four arguments of letters, digits and `_ . : = / -`,
  single spaces between, ≤200 chars in all. Anything else (backticks, prose, punctuation,
  control characters) is dropped silently: the header speaks in the hook's voice, and a
  manifest is text any session can write. On a STALE manifest the header names the
  mode for the operator to confirm instead of telling the session to re-enter it.
- **`next_skill:`** (optional) names the one-shot skill the next session should run — the
  checkpoint's `then <next-skill>` argument — as the slash command the operator would type,
  arguments included (e.g. `/dev-flow:implement 8cc2-turn-gate-port`). Written only when
  that argument names one; omitted otherwise. `mode_skill:` still leads: the standing mode
  is re-entered first, then the next skill runs. Same accepted shape as `mode_skill:`, and
  anything else is dropped silently. The hook names it on the header line of every tier of
  a manifest this session owns, after the standing mode, except LANDED — for confirmation
  on a STALE manifest — and never on the foreign header. The Step 7 opener carries it.
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
- Injection tiers: `compact` → full + ledger digest; `resume`/`fork` → full only when the file
  or repo changed since last injection, else one header line; a **linked `/clear`** → full
  (the compact tier, with its trim) + the **predecessor's** ledger digest, labelled
  `[context-guard ledger — predecessor <sid>, by /clear: …]`; `startup` and any other
  `clear` → header only. A `/clear` is linked when the successor's SessionStart finds the
  record the predecessor's SessionEnd(clear) left in the same Claude Code process (at most
  two minutes old), and it takes the full tier only when that link pinned exactly the
  version on disk now — the predecessor's own per-session manifest, found by the linked
  session id. No link, a pin of none, or a version rewritten since gets nothing from that
  file (the successor has no manifest of its own yet); a `landed` manifest an older version
  wrote gets its header, as its `/clear` is a fresh start.
  The whole injection stays under the 9,000-char budget: the body is trimmed to leave room
  for the digest. The successor's own new ledger starts `# ledger <sid> (successor of
  <predecessor sid>)`, a line the digest keeps, so the link survives its later compactions.
  Every header-only tier of an owned manifest carries the Holds lines as well; every full
  tier, the linked `/clear` included, injects the Holds section with its expiry marks.
- **Trim order**, when the full body is over its budget: the frontmatter `items:` list, then
  Scrolls, then Next (the hook's own `Next withheld` line kept), then the Aware-of lines other
  than CORRECTION and REFUSED, then any other section not listed here, last first (Scrolls,
  Next and Aware of keep what their own step kept). Headings match by name, ignoring a
  trailing `:` or `(…)` (`## Holds:` is Holds). Doing,
  Goal, Holds, In flight, Read in full and Copy forward are **never trimmed**; only a body
  whose protected sections alone exceed the budget is cut at its end. A trimmed section keeps
  its heading and reads `(trimmed — read the manifest file)`.
- **The ledger digest** (2,500 chars, never exceeded) keeps reasoning ahead of pointers.
  The *room* is the budget less a share held back for the closing line. `R`/`C` lines
  from every epoch come first (newest first, up to half the room), then `D`/`X`/`U`/`Q`
  ranked together newest first, then the remaining `R`/`C`, then the machine-written `P`
  pointers in what is left. A line too long for half the room is cut with a ` [cut]`
  marker, not dropped. Kept lines print in file order under their epoch headers. When
  anything is left out or cut, a last line counts it and names the ledger file. A budget
  too small for even that line gives an empty digest. The ledger file is never rewritten.
- **Machine fields are stamped, never typed.** `written:` (UTC now, `%Y-%m-%dT%H:%M:%SZ`),
  `head:` (`git rev-parse --short HEAD` of the manifest's repo), `branch:`, `top:` (that
  repo's toplevel, else the working directory — the manifest records the repo it is about,
  because it need not live inside it) and `session:` (the author's own id,
  `$CLAUDE_CODE_SESSION_ID`, which follows `/clear`) are written by `mark_checkpoint.py` at
  the end of Step 4b: write each as `<stamped>`. What it stamps is the author's **own**
  per-session manifest, `${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<sid>/HANDOFF.md`
  (`python3 hooks/handoff_path.py --path` prints it), when that file exists — and, only
  while it does not, an old-layout repo manifest. It rewrites those frontmatter lines only (adding any that
  are missing before the closing `---`), leaves every other byte as written, and replaces
  the file atomically. It stamps only a manifest written in the last 30 minutes. A
  per-session manifest is the author's **by its path**, so a `session:` copied from the
  manifest it replaced is simply corrected there, and an id passed that differs from
  `$CLAUDE_CODE_SESSION_ID` names no path and so grants nothing. An old-layout repo
  manifest is one file every session in a checkout shares, so there it also stamps only a `session:`
  that is a placeholder or the author, or names the session whose manifest the author
  replaced — its `/clear` predecessor or fork parent,
  or the author of a `handoff` it read in full — when the file is no longer the version
  that link pinned or that Read adopted (it was rewritten, the id copied). So a copied id
  is corrected, while an untouched predecessor's or parent's manifest and a concurrent
  peer's are never claimed; those get a `not stamped` warning. A manifest already stamped
  and not rewritten since is left as it is, so a repeated mark does not re-date it. It
  warns when the manifest's `session:` is still not the author's id. Hand-typed stamps
  were wrong in
  13 of 15 sampled writes (some hours in the future, read as FRESH), and since `session:`
  is the ownership key below, a copied id makes the new manifest foreign to its author and
  re-injects it in full into the predecessor.
- **Age** is read from `written:` as UTC (`Z`, an explicit offset, or no zone). A missing,
  unreadable (`2026-08-31 21:00 CDT`, a placeholder) or future stamp — more than 10 minutes
  ahead — is not trusted: the file's mtime ages the manifest instead, and the label names
  why, `(no stamp)`, `(stamp unreadable)` or `(stamp in the future)` (joined to any head
  reason with `; `). A future stamp is never FRESH: at least AGED. An mtime also more than
  10 minutes ahead dates nothing: the reason adds `, file time in the future`, and the
  label is at least AGED. An offset beyond ±14:59 is unreadable.
- **Whose memory it is.** Those tiers apply only to a manifest this session owns. A
  session's **own** per-session manifest is always its own — by its path, whatever its
  `session:` says. Another session's is reached only through a link or a Read, and only
  while it is still the version promised; with none of these, the hook shows it nothing.
  Ownership of
  those — and of an old-layout repo manifest — names a *version*: the `session:` field plus
  the hash of the file's raw text, so a rewrite is a new version. A version is this
  session's when:
  - it has no `session:` (a hand-written repo manifest is everyone's);
  - this session wrote it (`session:` is its id), any version;
  - a link pinned exactly that version: a `/clear` successor is linked to the session that
    ran `/clear` (same Claude Code process), a fork to its parent, and both inherit the
    linking session's own links, up to 8 deep. A link pins the version on disk only if it
    was the linking session's own at that moment — a manifest a third session overwrote is
    never passed on;
  - this session **read exactly that version in full** and its `mode:` is `handoff`.

  A link or Read of another session's per-session manifest that no longer matches is
  skipped: the author moved on, and this session keeps its own file or none. An old-layout
  repo manifest that is not this session's — another session's, or a later rewrite by a
  parent, a resumed predecessor or an adopted author — gets one header line on every source, naming the path
  and the author session, with no body, no precedence line and no standing mode: "If the
  operator's opener names this manifest, read it in full; otherwise it is another session's
  and not your memory." The derived check lines still follow it — dead claims, unparseable
  `items:`, and the Next-withheld line — since they describe the file, not anyone's memory.
  The ledger digest and `/compact` guidance still inject on `compact`.
- **Reading adopts; `cat` looks.** A whole-file Read (no offset, no limit) of a `mode:
  handoff` manifest adopts that version: it is re-injected into this session after a
  compaction. To look without adopting, use `cat` (a Bash read) or a Read with an offset or
  limit. A `continue` or `landed` manifest is never adopted by reading it; a subagent's Read
  adopts nothing.
- Updating: every checkpoint rewrites it wholesale (it is a current view, like an INDEX, not a
  log). It has no history: what must outlast it goes to git and the work-item store (Step 3).
