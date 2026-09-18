# HANDOFF.md — the rehydration manifest

One per repo, **authored by the checkpoint skill** (never machine-synthesized: intent
is a snapshot only its author can write; the facts around it — age, drift, dirty count
— are computed live by `hooks/rehydrate.py` at injection). Work-addressed (class b1):
lives at `.claude-sandbox/HANDOFF.md` when `.claude-sandbox/` exists (so `trackInHost`
governs it), else `HANDOFF.md` at the repo root. Write-side budget **≤6,000 chars**;
the hook trims Scrolls → Aware-of and never the mandatory tiers, under its 9,000-char
injection cap.

## Format

```markdown
---
handoff: 1
repo: <name>
session: <session-id>
written: 2026-08-30T21:40:00Z
head: <short-sha>
branch: <branch>
mode: land | continue | handoff | landed
by: checkpoint
items:            # optional: wi ids you expect still open or in flight
  - <work-item-id>
---
## Doing
2–3 lines, present tense: what is in flight and where it stands.

## Goal
mode: <land|continue|handoff> — operator: "<their last stated goal, verbatim>"

## Read in full
≤5 paths, one per line with WHY each cannot be skipped. This is raw rehydration:
the next session reads these before doing anything else.

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
  with Next shown, not "not an ancestor". The
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
- **Stale Next is withheld, not warned.** When the recorded `head` is not an ancestor of
  HEAD, or HEAD is ≥1 commit past it, the hook replaces the `## Next` body with one line.
  Its variants:
  - ahead, N ≥ 2: `Next withheld: head moved <N> commits since this manifest
    (<recorded>..<current>); run wi prime and git log.`
  - ahead, one commit: `... head moved 1 commit since this manifest (<recorded>..<current>); ...`
  - not an ancestor (HEAD rewound behind the recorded head, or diverged from it): N is the
    commits on HEAD's side and M those on the recorded head's side, from one
    `git rev-list --left-right --count <recorded>...HEAD`, so a pure rewind reads
    `0 commits ahead, M behind` (M ≥ 1: a rewind with no code commits on either side is
    FRESH and Next is shown):
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
- Updating: every checkpoint rewrites it wholesale (it is a current view, like an INDEX, not a
  log — history lives in git).
