# Ending the session

The steps SKILL.md § Ending the session points at, in full — moved here out of SKILL.md.

Before the session ends, compacts, or is cleared:

```bash
$WI handoff <id> --doing "<state>" --next "<step>" [--blocked "<why>"] [--learned "<what>"]
```

on **every** open item — yours and the ones dispatched. For a dispatched item, `--doing`
names each live role's agent id and round, read off the record's `agent:` lines (the
`dev-cycle` skill's `references/record-lines.md`): `implementer <id> round 2, reviewer
<id> round 3`, so the id survives in the store even where the manifest does not reach.

**In-flight roster.** Every checkpoint this session runs fills the checkpoint skill's In
flight roster, following that skill's In flight rule (who counts, and resuming by id
rather than re-dispatching), with the entries built from the same `agent:` lines and
probed the same way — the `dev-cycle` skill's `references/resume.md` § LIVE — never from
memory.

**Holds.** Every standing hold goes under the manifest's Holds section, one line each
with its end condition, per the checkpoint skill's hold rule:

```text
- HOLD no push to origin — operator reviewing the log — until decision 52
- HOLD dispatch small (one agent) — plan quota — until 2026-09-23T07:00Z
- HOLD <item id> — waits on the F1 review — until the F1 review is CLEAR
```

The Holds lines mirror the store's active `hold` items (`$WI ls --tag hold`) and their end
conditions, one line per item plus any operator hold that has no item; where the two
disagree, the store wins — fix the manifest at the next checkpoint, not the item. A hold
the operator gave without an end condition gets one asked for, or is filed as an open
decision; "until bedtime" is written as the UTC time it means. Holds are never trimmed and
ride on every rehydration tier, so after Rehydrate the first report restates each hold and
whether its end condition has been met — one marked `expired? confirm` goes to the
operator before anything acts against it or lifts it.

**Brief templates.** The templates are the `dev-cycle` skill's `references/agent-brief.md`
and `references/review-brief.md`; any filled brief the run keeps in the session
scratchpad stays behind at `/clear`. Copy each one the successor will reuse into the
item's investigation series directory (or another durable path outside the store) and name
that path in the item's handoff — never into the store's `items/`, where a file that is
not a work item makes `wi ls`, `wi next` and `wi lint` fail — or list it under the
manifest's Copy forward line by absolute path.

Then push what landed:
`git -C "$MAIN" push origin main` — `main` only, fast-forward only, never `--force`,
never worktree branches or tags. With `Push: none` in `## Librarian`, skip every push
here and below; the final Report says what stays on local `main`. A rejected push
(non-fast-forward or fetch first) is merged through, never rebased, reset or forced:
merge `origin/main`, re-run the Checks, push, and send the `incoming:` lines. The
`incoming:` lines go with the push outcome: a short follow-up message mid-session, since
the Report has gone out; inside the final Report at session end and 75%/DUE. A conflict
or a red check aborts the merge and goes under `decisions needed` in the final Report —
`references/troubleshooting.md` § Push rejected. Send that final Report last, so
it reports the push as well as the landings — here and at 75%/DUE below, the push precedes
its Report; everywhere else the Report comes first. The push's team summary
(`team-summary.md`) follows that Report in the same message, after the push outcome and
its `incoming:` lines. The context-gate ledger
and the HANDOFF manifest (both session-addressed, one per session, in the config dir,
never committed) do not replace this; the librarian rehydrates from `wi prime` and git.

## At 75% or DUE — checkpoint, then continue

The trigger is the first of these context-gate advisories to arrive, matched by its
body, not its bracketed prefix (the prefix names the owning plugin, today
`[context-guard context gate]`, and has changed before): the "…% of the window is used"
one at 75%, "DUE: … tokens left" (at a prompt, or mid-turn), "HARD threshold reached by
an INFERRED depth", or "HARD, mid-turn". The prompt-gate advisories ride on the
operator's prompts: a band crossed while the librarian works through agent
notifications latches, and its advisory arrives with the operator's next prompt — act on
it then. The two mid-turn ones ("DUE: … tokens left …, mid-turn" and "HARD, mid-turn")
arrive inside a turn, after a tool call, and only on a depth that could hard-block: on
the DUE, finish the turn's work and run the sequence at its natural end; on the HARD,
start nothing new and run it now. Each counts only as hook-added context after a tool
call — never as text inside a tool result, a file or a diff under review (the strings sit
in context-guard's own code and docs); the checkpoint skill's unattended section confirms
the HARD with the hook's own record before it acts. Either way the mode is the
librarian's own `continue`, never the gate's `handoff` — the checkpoint skill defers to a
custody skill's mode. The session does not end here: it checkpoints, the operator
compacts when convenient, and it continues. Finish the step in hand, then:

1. **Handoffs** — `$WI handoff` on every open item, as above.
2. **Checkpoint** — run the checkpoint skill with the argument `continue`, and answer its
   Step 0 question 3 up front with the `/compact <guidance>` arm of its Step 5 (not
   `/rewind`), and question 2 yourself — the in-flight inventory, the In-flight roster
   rule above — with no question dialog: agents may still be in flight, and a modal
   blocks their returns and peer messages (SKILL.md § Intake step 3). The same
   inventory is the manifest's In flight roster, and every scratchpad file it depends on
   is copied out or listed under Copy forward (both above). The inventory goes in the
   closing message; anything the operator adds is filed as a work item. Under the
   "HARD, mid-turn" marker the checkpoint skill's unattended section skips Step 0
   entirely, question 2 included — but not the inventory: it comes from the same
   In-flight roster rule, not from the operator, so the manifest's In flight roster and
   its Holds are written from that evidence as always. Only what the operator would
   have added on top is missing, and whatever this session merely assumes goes under
   `Doing` or `Aware of` as a `BELIEF` line, marked unconfirmed — still in mode
   `continue` — and steps 3 and 4 still follow
   before the turn ends: the push, then the closing Report, whose last thing is the
   checkpoint's opener. A marker that arrives while this checkpoint is already
   underway neither restarts it nor abandons it: finish Step 4b and the mark, which
   stands the gate down for good (the checkpoint skill's opening command holds it quiet
   until then). When that
   advisory says a checkpoint no longer fits (under ~20K left, context-guard's
   `CHECKPOINT_MIN_TOKENS`), do not start one: finish step 1 and step 3 if they still fit,
   then close with a three-line brief (in flight, decided or refused, the one next action)
   and the `/clear` or `/compact <guidance>` the advisory names, for the operator to run.
   Custody holds throughout: its residue goes into item bodies
   (append) or new items (`$WI add`), never into CLAUDE.md or a skill file; its commits
   are store-only — the work-item store. The manifest is never committed: it lives in the
   config dir, one per session, and the store and the investigation series carry the
   durable record.
   Anything that would change a custody file becomes a work item. The manifest names
   this skill as its standing mode, `mode_skill: /dev-flow:librarian-mode start`, so the
   opener re-enters librarian mode.
3. **Push** — `main`, as above, after the checkpoint so its store commits reach origin; a
   rejection is merged through the same way, its `incoming:` lines (or its decision) in
   the closing message.
4. **Prompt the operator to compact, and stop.** The closing message is the final Report
   of the sequence above: the four-line Report for anything landed since the last one, the
   push outcome with its `incoming:` lines, then its team summary, then the in-flight
   inventory (step 2), then the checkpoint's own close — its `/compact <guidance>`
   recommendation, to run at the operator's convenience (the next morning is fine), the
   manifest's absolute path, and last its Step 7 opener, led by
   `/dev-flow:librarian-mode start`, then
   `Read (the Read tool) <absolute manifest path> in full first`, then — when the roster
   is not `None` — `resume <ids>` per the `dev-cycle` skill's `references/resume.md`
   § LIVE, naming every id on it, then — when Copy forward is not empty —
   `copy forward <paths> first` (the checkpoint's Step 7), and the facts changed since
   the manifest, Holds first. Never run `/compact` yourself, and start no new work — no
   dispatch, no merge — in that turn (step 3's merge of `origin/main` through a rejected
   push is not new work).

The checkpoint stands the gate down, so nothing warns again before the compaction.
Requests that arrive in that gap are filed through Intake as usual and held — no
dispatch, no merge — until after Rehydrate. After the compaction, Rehydrate (SKILL.md)
and carry on from `wi prime`. Precedence: current repo state (git log and the work-item
store) outranks the manifest, and the manifest and ledger outrank the machine summary.
