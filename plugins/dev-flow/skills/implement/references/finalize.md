# Finalize — the record and the docs

Loaded from `implement` Step 10, after the terminal action (10a) and the work-item update
(10a½). The SKILL.md keeps each sub-step's rules in summary; this file holds them in full.
Under an orchestrator only 10d runs (see `references/run-modes.md`).

## 10b — Write the outcome

Write `NN_implementation.md` at the next free serial, per the outcome outline in the
`investigate` skill's `references/investigation-format.md`. Its `Supersedes` block names each
plan statement the build overturned, or `Nothing — the plan held`.

Capture: decisions locked at the gates, deviations from the plan (including files that turned
out to be no-ops), the verification outcome **with its tier**, any new analysis the run
produced, the branches delivered, and follow-ups spun out.

Skip this file only when the run produced nothing worth recording — the plan held exactly and
there were no gate decisions. **Say so in the report when you skip it.**

## 10c — Rewrite the index

Regenerate `INDEX.md` wholesale:

- Set each implemented row's Status to `implemented <YYYY-MM-DD>` and fill its Branches column.
  Rows that needed no code get `no code`; rows a later serial invalidated get `superseded by NN`.
- Add the TOC row for the outcome file.
- Refresh the reconciled sections — Deployment & Rollout Notes especially, since deploy reality
  is now known. Update the provenance line to the SHAs actually delivered against.
- **Revisit every deferred question — this is where answers are most likely to exist.**
  Building the change answers questions that reading the plan could not. For each: did the
  implementation settle it? Has anything changed externally? Close what you can, recording the
  evidence in the outcome file, and drop it from the index's Open Questions. Bring the still-open
  ones back to the user once, briefly, with the same defer option. A question deferred twice
  with no movement belongs on its own investigation — offer to spin it out.

  Open Questions must end up listing **only** what is genuinely still unresolved.

## 10d — Documentation follow-ups

Derive the documentation the change requires and apply it — this replaces the release/change-
management step it was adapted from, and it is part of the work, not an afterthought:

- **Any config or code sample you write into docs must be valid in its target format** — a
  snippet is only correct if it parses or runs where it is meant to be pasted. A fenced block
  labelled for readability (`jsonc`, `console`) is not evidence: strict JSON rejects comments
  and trailing commas, and the reader finds out, not you. Parse it, or pin it with a test
  where the project can.
- `CHANGELOG.md` — an entry, if the project keeps one, in its existing style
- `README.md` — when behaviour, flags, config, or setup changed
- `docs/*` — when the change contradicts something written there
- Inline docs — package docs, help text, comments that the change made wrong

Present what you propose to update and what you are skipping, with reasons, then apply. A doc
the change made **wrong** is a defect; do not leave it for later.

