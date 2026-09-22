# Ending the session

The steps SKILL.md § Ending the session points at, in full — moved here out of SKILL.md.

Before the session ends, compacts, or is cleared:

```bash
$WI handoff <id> --doing "<state>" --next "<step>" [--blocked "<why>"] [--learned "<what>"]
```

on **every** open item — yours and the ones dispatched. For a dispatched item, `--doing`
names each live role's agent id and round (`implementer <id> round 2, reviewer <id> round
3`), so the id survives in the store even where the manifest does not reach.

**In-flight roster.** Every checkpoint this session runs fills the checkpoint skill's In
flight roster, following that skill's In flight rule (who counts, and resuming by id
rather than re-dispatching), with the entries built from the `dispatch:` lines on the
`doing` items and ListAgents, never from memory.

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
here and below; the final Report says what stays on local `main`. A rejected
non-fast-forward push is not fixed by pulling, fetching, rebasing or merging: stop, and
carry it under `decisions needed` in the final Report. Send that final Report last, so
it reports the push as well as the landings — here and at 75%/DUE below, the push precedes
its Report; everywhere else the Report comes first. The context-gate ledger
(session-addressed, one per session) and HANDOFF (work-addressed, class b1, one per
repo) do not replace this; the librarian rehydrates from `wi prime` and git.

## At 75% or DUE — checkpoint, then continue

The trigger is the first of these context-gate advisories to arrive, matched by its
body, not its bracketed prefix (the prefix names the owning plugin, today
`[context-guard context gate]`, and has changed before): the "…% of the window is used"
one at 75%, "DUE: … tokens left", or "HARD threshold reached by an INFERRED depth". They
ride on the operator's prompts: a band crossed while the librarian works through agent
notifications latches, and its advisory arrives with the operator's next prompt — act on
it then. The session does not end
here: it checkpoints, the operator compacts when convenient, and it continues. Finish
the step in hand, then:

1. **Handoffs** — `$WI handoff` on every open item, as above.
2. **Checkpoint** — run the checkpoint skill with the argument `continue`, and answer its
   Step 0 question 3 up front with the `/compact <guidance>` arm of its Step 5 (not
   `/rewind`), and question 2 yourself — the in-flight inventory, from the `doing` items,
   their `dispatch:` lines and ListAgents — with no question dialog: agents may still be
   in flight, and a modal blocks their returns and peer messages (SKILL.md § Intake
   step 3). The same inventory is the manifest's In flight roster, and every scratchpad
   file it depends on is copied out or listed under Copy forward (both above). The
   inventory goes in the closing message; anything the operator adds is
   filed as a work item. Custody holds throughout: its residue goes into item bodies
   (append) or new items (`$WI add`), never into CLAUDE.md or a skill file; its commits
   are store-only — the work-item store, and the manifest only when the repo tracks it
   (`trackInHost` governs `.claude-sandbox/HANDOFF.md`; an untracked manifest stays out
   of the commit).
   Anything that would change a custody file becomes a work item. The manifest names
   this skill as its standing mode, `mode_skill: /dev-flow:librarian-mode start`, so the
   opener re-enters librarian mode.
3. **Push** — `main`, as above, after the checkpoint so its store commits reach origin; a
   rejection stops the same way and goes under `decisions needed` in the closing message.
4. **Prompt the operator to compact, and stop.** The closing message is the final Report
   of the sequence above: the four-line Report for anything landed since the last one,
   the push outcome, then the checkpoint's own close — its `/compact <guidance>`
   recommendation, to run at the operator's convenience (the next morning is fine), and
   last its Step 7 opener, led by `/dev-flow:librarian-mode start`, then `read
   <manifest path> in full first`, then — when the roster is not `None` — `resume <ids>
   with SendMessage; do not re-dispatch` naming every id on it, then — when Copy forward is
   not empty — `copy forward <paths> first` (the checkpoint's Step 7), and the facts
   changed since the manifest, Holds first. Never run
   `/compact` yourself, and start no new work — no dispatch, no merge — in that turn.

The checkpoint stands the gate down, so nothing warns again before the compaction.
Requests that arrive in that gap are filed through Intake as usual and held — no
dispatch, no merge — until after Rehydrate. After the compaction, Rehydrate (SKILL.md)
and carry on from `wi prime`. Precedence: current repo state (git log and the work-item
store) outranks the manifest, and the manifest and ledger outrank the machine summary.
