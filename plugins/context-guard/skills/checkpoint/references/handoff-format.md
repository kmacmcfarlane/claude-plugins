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
- The hook labels the manifest FRESH (fresh), AGED (>24h or any commit drift), STALE (>7 days
  or >30 commits — goal lines must be re-confirmed with the operator), LANDED (`mode: land*` —
  header-only, the work is done).
- **Current repo state outranks the manifest.** git log and the work-item store are the
  durable record; the manifest is only the reasoning. The injected precedence line says so:
  repo state beats the manifest; the manifest and ledger beat any machine summary.
- **`items:`** (optional) lists the work-item ids the author expects open or in flight —
  Step 4b fills it with the `wi` ids of open or doing items the manifest mentions. When a
  store is found (`WI_ROOT`, else `.claude-sandbox/work`, else `.work`), the hook names each
  id now done, dropped or missing as `DEAD CLAIM <id> (<status>)`, in every tier. No store:
  silent.
- **Stale Next is withheld, not warned.** When the recorded `head` is not an ancestor of
  HEAD, or HEAD is ≥1 commit past it, the hook replaces the `## Next` body with one line:
  `Next withheld: head moved <N> commits since this manifest (<recorded>..<current>); run wi
  prime and git log.` Other sections stay. Commits touching only `.claude-sandbox/work` (store
  chores) do not count toward N. No time-based expiry — the head check covers it.
- Injection tiers: `compact` → full + ledger tail; `resume`/`fork` → full only when the file
  or repo changed since last injection, else one header line; `startup`/`clear` → header only.
- Updating: every checkpoint rewrites it wholesale (it is a current view, like an INDEX, not a
  log — history lives in git).
