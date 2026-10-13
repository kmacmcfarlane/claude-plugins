# The Report

The detail behind SKILL.md § Report, whose four-line template, plain names and
numbered-decision rule stay there.

## Spikes and self-review

A spike reports its series path on `changed:`, as dev-cycle's `plan` mode does. A
self-reviewed change writes `review self` in place of the reviewer's tier, as dev-cycle's
Step 6 does.

## The verified line

The tiers are the final ones, written as the `dev-cycle` skill's
`references/model-routing.md` § Recording gives them (a bumped round, a fable
cross-check). Each check is one of the `Checks:` commands, named by the directory it runs
in, relative to the repo root (`plugins/dev-flow` for `(cd plugins/dev-flow && …)`, `.`
for one with no `cd`); when two commands share a directory, add the command's
distinguishing word after it (`. lint pass`). Then its outcome: `pass`, or `fail — <what
failed>`. Every `Checks:` command is named, in its order there; for a `Checks:` of those
two commands: `plugins/dev-flow pass, plugins/kit-dev pass`.

## The counter

It is **one counter**: every question put to the operator takes its number from it — an
Intake ask, a dev-cycle decision, a Groom row, a series' or a gate's own questions, whose
labels (OQ3, R1, G5) survive as a tag on the decision, never a second numbering. The two
exceptions are the opt-in dialog (`opt-in.md`) and the session-name gate
(`session-name.md`). Another repo's decision is written `<repo>#N`, never a bare N. The
counter lives in the store: raising a decision appends one line to its item's body — one
physical line, never wrapped, since `wi` reads the headline only to the line's end — in
the form of the `dev-cycle` skill's `references/record-lines.md` `decision:` line,
numbered:

```
decision N: <question> — options: (a) … [recommended] | (b) … | (z) decide later
```

The reply is `answer N: <reply>`; on re-entry continue from the highest N (`rehydrate.md`
§ Step 3), else 1.

## With the decisions skill

With the `operator-interaction:decisions` skill loaded, the four lines stay, and each
`decisions needed:` names its decision numbers, each with its effect at that skill's tag
size, read from the stored card's `impact:` line: `46 (→ preview up in about 4 minutes)`.
One decisions block, written per that skill, is the **last thing in the turn** — after the
push outcome, its `incoming:` lines and the team summary below. The stored card, the store
lines per reply, the default wake (the next Report) and the re-show after Rehydrate are in
`decisions.md`.

## Done alone

What was decided alone since the last Report goes in a **Done alone** group of `Done:`
lines after the four lines per landed change — extra lines, beyond the four
(`decide-alone.md` § The Report).

## Batching

Batch several landings in one message, four lines each; anything blocked or declined since
the last report goes under `decisions needed` of the next — except a forward still
awaiting acceptance, watched, or held for a down owner (SKILL.md § Intake step 4), which is
its `Done:` line and the forwards line until it lands back. Do not wait for the operator's
review to take the next request.

## The push

Then, unless `Push: none`, push: `git -C "$MAIN" push origin main` — fast-forward only.
Its outcome is one line, in one of two forms:

```
pushed: main → origin/main, fast-forward <old>..<new>
not pushed: <why, one clause>[ — decision N]
```

`<old>..<new>` is the short-sha range git's push output prints for `main`. `not pushed:`
covers any push not made, such as a rejection that stopped on a conflict, a red check or
a decision (its number trailing); a push skipped while a push-rejection decision is open;
no `origin` remote (said once, `troubleshooting.md`); and `not pushed: nothing to push —
main fast-forwarded to origin/main` when `main` was strictly behind (`troubleshooting.md`
§ Push rejected step 1). A rejection merged through adds one `incoming: <sha> <subject> —
<author>` line per incoming commit under the outcome line — extra lines, beyond the four
per landed change. The `incoming:` lines go with the push outcome: a short
follow-up message mid-session, since the Report has gone out; inside the final Report at
session end and 75%/DUE (`troubleshooting.md` § Push rejected).

## The team summary

After each push (with `Push: none`, each batch), one team summary for people who did not
watch the run, a bold title and one bullet per change area, never a table or sub-bullets,
after the push outcome and its `incoming:` lines: `team-summary.md` (once
`origin/main@{1}` has failed, note `origin/main` before pushing; no `origin` remote: local
only, no pickup step).
