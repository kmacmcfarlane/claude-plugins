# HANDOFF.md — the rehydration manifest

One per repo, **authored by the checkpoint skill** (never machine-synthesized: intent is a
snapshot only its author can write; the facts around it — age, drift, dirty count — are
computed live by `hooks/rehydrate.py` at injection). Work-addressed (class b1): lives at
`.claude-sandbox/HANDOFF.md` when `.claude-sandbox/` exists (so `trackInHost` governs it),
else `./HANDOFF.md`. Write-side budget **≤6,000 chars**; the hook trims Scrolls → Aware-of and
never the mandatory tiers, under its 9,000-char injection cap.

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
1–2 actions. Work-item IDs (`wi show <id>`) once `.work/` exists.

## Scrolls
TOC, read on demand: `path — one line on what it holds`.
```

## Rules

- **Secrets: path and key, never value.** A manifest lands in git; sops and `kind: Secret`
  gates do not see prose. Name where a secret lives, never what it is.
- The hook labels the manifest FRESH (fresh), AGED (>24h or any commit drift), STALE (>7 days
  or >30 commits — goal lines must be re-confirmed with the operator), LANDED (`mode: land*` —
  header-only, the work is done).
- Injection tiers: `compact` → full + ledger tail; `resume`/`fork` → full only when the file
  or repo changed since last injection, else one header line; `startup`/`clear` → header only.
- Updating: every checkpoint rewrites it wholesale (it is a current view, like an INDEX, not a
  log — history lives in git).
