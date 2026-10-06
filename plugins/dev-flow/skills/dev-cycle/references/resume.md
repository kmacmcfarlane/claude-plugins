# Resume

How a run takes an interrupted cycle up again, from its record alone: one state, one next
action. SKILL.md § Step 0.4 runs it on every invocation, on the record and the repository
as Step 0 found them — before this run writes a line or adds a worktree, so nothing this
run does reads as an interrupted one. A record with nothing in it is S0 and the run simply
starts. A caller resuming several targets runs it once per target, in whatever order its
own queue says. `full`, `plan` and `review` read the same facts and the same table; the
mode changes only what a fact is computed from.

It reads the lines `record-lines.md` fixes, git, and the agents. It writes one line of its own,
`spent:` (§ The GATE); every other line is written by the step that owns it, never by a
resume.

**Reduce first, then read one table.** Every cross-cutting test — freshness, the cap,
retries, the brief variant, the decision gate — is a fact computed once in § The
reduction. **No row recomputes a fact, and the GATE is evaluated once, for the selected
row's question** — `review` mode's S11 reads the dispatch permission's pair only to
choose that question (§ The state table, the dispatch permission).

## Phase lines and riders

Four line kinds are **phase lines**: `dispatch:`, `return:`, `verdict:` and `landed:`.
They move the run, and only a phase line can be its last state. Every other line —
`target:`, `checks:`, `intent:`, `agent:`, `review:`, `baseline:`, `findings:`, `changed:`,
`decision:`, `answer:`, `spent:`, `subject-fix:`, `conflict:`, `blocked:`, `trial:`,
`cross-check:`, `cross-check-rulings:`, `budget:`, `cost:` — is a
**rider**: it never displaces a phase line, and it is read only where a fact below names
it.

A **helper line** is a rider too, although it is a `dispatch:`: one whose role is `scribe`
or `scout`, which a caller writes for its own helper or read-only question, or a
cross-check on an accepted offer (`record-lines.md`), and the
`agent:` line under it (`record-lines.md`). A `dispatch:` whose role is `research-lane`,
`research-verifier` or `synthesis` is a helper line too: a research skill's run recording
onto the item (the `research` skill's `references/intensity-and-routing.md` § Recording),
with its `agent:` lines. A helper line never counts as a phase line, so a scribe
rendering a decision's card leaves that decision after the last phase line, and the GATE
still reads it as pending. One rider check runs at every resume, outside the states: a
cross-check helper line — signal `— cross-check (…)` or `— cross-check stand-in (…)`,
never an older record's `— second opinion (…)` — with no `cross-check:` line after it is
probed as LIVE probes an id. Still running: left to finish. Finished with a report:
collected, and its return recorded as when it returns (`model-routing.md` § Fable
cross-checks). Gone: its `cross-check: … dropped` line is written and the drop is named
in the resume summary and the Report's `open questions:`, so the operator can accept it
again.

A line that is missing reads as **not recorded**, and every default escalates: a
`BLOCKED` with no reason reads as `permission` (`record-lines.md`), an unreadable freshness test
as `STALE`, an untagged dispatch permission as not found. None of them lands, and none
dispatches twice. A record written before a shape existed is therefore legal input.

## The reduction

The mode and the workspace are the recorded `target:` line's, never this invocation's
words. `<workspace>` below is that line's third field.

0. **SINK** — `reachable` | `unreachable`, from the Record sink binding (`bindings.md`
   § The ten). An item body is reachable. A scratchpad run record that does not exist in
   this session is `unreachable`: it may never have been written, or it belonged to a
   session that has ended. When SINK is `unreachable`, every fact read from lines is
   **absent** — not false — and only group P is read.
1. **LANDED** — yes when a `landed:` line is anywhere in the record; no otherwise.
2. **PHASE** — `NONE` (no lines) | `RIDERS` (lines, but no phase line) | `DISPATCH` |
   `RETURN` | `VERDICT` | `LANDED`: the kind of the last phase line. The six values are
   exhaustive and disjoint over any record.
3. **fresh(v)** — true when the verdict line `v` still judges the tree as it stands:
   - `full`, `review`: `v`'s `at <sha>` equals `git -C <workspace> rev-parse HEAD`.
   - `plan`: the `baseline:` recorded immediately before `v` equals a fresh
     `sha256sum <series>/[0-9][0-9]_*.md`; `v`'s own `at <series path>` names the series,
     not its state.
   - **false whenever it cannot be evaluated**: the workspace is gone, `rev-parse` fails,
     the series path is gone, or no `baseline:` precedes a plan verdict. A stale verdict
     never lands and opens a fresh review, whose reviewer blocks on a missing workspace,
     so the failure escalates.
   - never asked of a `verdict: BLOCKED`, which judged nothing.

   **FRESH** = fresh(the last verdict), `CURRENT` | `STALE`, when PHASE is `VERDICT`.
4. **ROUNDS** and **CAP** — CAP is **the one cap test.**
   - **ROUNDS** — count, in the current phase — the lines after the record's last
     `target:` line, or the whole record when it has none — the `verdict:` lines whose
     verdict is `CLEAR`, `NEEDS_CHANGES` or `SHOW_STOPPER` (never `BLOCKED`), minus one
     when the most recent `CLEAR` satisfies fresh(). A plan's verdicts never count in its
     build. An answered waiver never changes the count.
   - **CAP** — `UNDER` | `AT_CAP`: `AT_CAP` when ROUNDS ≥ 4, or when the phase's spend,
     read now as `bindings.md` § Spend budget's check reads it (read-only: resume writes
     no `cost:` or `budget:` line), is at or over the amount in force — unless a fresh
     weekly reading taken now is below 50% used (`bindings.md` § Spend budget, While the
     quota is plentiful), which a stale verdict's rows read too; `UNDER` otherwise, a
     phase with no reading included. `AT_CAP` sends the row to SKILL.md § Step 4.3, which
     decides what it ends in — a stop, a round it opens unasked, or a raise; it is
     never by itself a raise. CAP answers one question — *may another review round be
     opened without Step 4.3?* — so only a row whose action opens one reads it.
5. **RETRIES** — the `BLOCKED` phase lines of one kind recorded since the last line of
   that kind that was not `BLOCKED`: `return:` lines for group C, `verdict:` lines for
   S12. Two retries are allowed, so a third `BLOCKED` stops (`fix-loop.md` § The
   verdicts).
6. **VARIANT** — the reviewer's brief, decided here and nowhere else. The first row that
   holds wins; "the last verdict" means the last one that is not `BLOCKED`.

   | condition | brief (`review-brief.md`) |
   |---|---|
   | a `conflict:` line after the last `verdict:` | the merge-conflict case of § Re-review variant (`fix-loop.md` § A merge conflict) |
   | mode `plan` | § Plan-review variant |
   | mode `review`, no verdict yet | § Review-mode variant |
   | mode `full`, no verdict yet | the full brief |
   | `full` or `review`, the last verdict `CLEAR` | the full brief — the new commits are work no finding describes |
   | `full` or `review`, the last verdict `NEEDS_CHANGES` or `SHOW_STOPPER` | § Re-review variant, the recorded `findings:` pasted for verification |

   In `review` mode every row is taken on top of § Review-mode variant: its worktree,
   branch check, claims and intent replacements always apply, since the workspace is on
   `<branch>`, never on `worktree-<name>`.

   The secret-rebuild case is not a row: it is selected by the critical finding inside the
   `findings:` block a fix round hands forward (`fix-loop.md` § A leaked secret).
7. **GATE(q)** — `ANSWERED` | `PENDING` | `NONE`, for the one question `q` the selected
   row names, and evaluated only then:

   | arm | the pair read | its value |
   |---|---|---|
   | **state-scoped** — every question but one | the last `decision:` or `answer:` recorded after the last phase line, skipping the tagged decisions' own lines — each `dispatch-permission` or `fable-offer` `decision:`, its `answer:` (a caller's `answer N:` by its number) and `spent:`. Only the run-scoped arm reads the dispatch permission; nothing here reads a fable offer, which never gates a run | an `answer:` → `ANSWERED`; a `decision:` with no `answer:` after it → `PENDING`; neither → `NONE` |
   | **run-scoped** — `q` is `review` mode's dispatch permission | the last `decision: dispatch-permission` anywhere in the record | its `answer:` recorded → `ANSWERED`; none → `PENDING`; no such line, or a `spent:` line recorded after it → `NONE` |

   Under a caller the tagged line is its `decision N:` carrying the same tag, and its
   untagged `answer N:` pairs by the number (`record-lines.md`, `answer:`). The run-scoped
   arm matches a literal tag, so no other "yes" — a cap waiver, a `NEEDS_CONTEXT` answer —
   is ever read as permission to touch the author's branch; an untagged pair from an older
   record is not found, and the question is asked again.
8. **LIVE** — `one` | `none` | `many`, computed when PHASE is `DISPATCH`. The
   **generation** is every `agent:` id recorded since the last phase line that is not a
   `dispatch:`, a helper line's `agent:` never included — a re-dispatch appends a new
   pair, so a resume of a resume probes every id it made. No `agent:` line in it → `none`: the Agent call never returned an id. Otherwise
   probe each id: `ListAgents` first; an id it does not list gets a SendMessage asking for
   its status, because a fresh process may not list an agent that is alive. Running, or
   answering, counts as alive; so does a finished one whose report carries a `STATUS`
   (a reviewer's: a verdict), since it holds a report to collect. A finished one whose
   report carries none — an error, a 429 that cut it off — counts as gone, and so
   does an unlisted id whose SendMessage fails. The same id repeated under a `— resume`
   dispatch is probed once.
9. **REMNANT** — `present` | `absent`, computed when SINK is `unreachable`. **An artefact
   is a remnant only when the run the record belonged to created it and the target was
   never handed it** — one rule, not a list to widen case by case. The artefacts a cycle
   creates are a `worktree-<slug>` branch and its worktree (`full`, SKILL.md § Step 3.1),
   a `.claude/worktrees/review-<slug>` worktree (`review`, `bindings.md` § Review target
   case 3), an agent whose task names the target, a series directory under the Series home
   (`plan`), and a merge pending in the main checkout (`git -C "$MAIN" rev-parse -q
   --verify MERGE_HEAD` succeeds). Anything the target was handed is input, not a remnant:
   a series given as a slug or plan path, and a worktree already on `<branch>` — a
   `review-<slug>` one an earlier run added included — which § Review target's case 2
   reuses as it stands, so in `review` mode only a live agent or a pending merge is ever a
   remnant. `present` when any remnant exists; `absent` otherwise.
10. **MERGED** — yes | no, computed when SINK is `reachable`, LANDED is no, the mode is
    `full` or `review`, and the last phase line is a `verdict: CLEAR`; no otherwise. Yes
    when a merge on the base has that verdict's `at <sha>` as its merged
    parent — the landing merge, made and never recorded, because the run died between
    SKILL.md § Step 5.3's merge and its `landed:` line:

    ```bash
    git -C "$MAIN" log --merges --format='%H %P' <sha>..<base> \
      | awk -v s="$(git -C "$MAIN" rev-parse --verify -q <sha>^{commit})" 's != "" && $3 == s {print $1}'
    ```

    `<base>` is the Base binding. A printed sha is yes, and it is the merge sha; no
    output, or a `<sha>` git cannot resolve, is no. It reads git alone, so it holds when
    the workspace and its branch are already gone — where fresh() alone would read
    `STALE` and re-review, and re-land, work that has landed.

**CHANNEL** is not computed: it is the Decision channel binding's durability, `durable` or
`ephemeral` (`bindings.md` § The ten).

## The state table

Group P is read first; the rest is selected by PHASE, then by the axes each group lists.
Each group's axes are exhaustive over their own values, so no record matches two rows and
none matches nothing.

**Group P — preconditions**

| SINK | REMNANT | LANDED | MERGED | State | The single next action |
|---|---|---|---|---|---|
| `reachable` | — | yes | — | **S2** landed | § The landing tail, with the `landed:` line's merge sha. Terminal — never re-dispatched, re-landed or rebuilt. |
| `reachable` | — | no | yes | **S2b** merged, not recorded | Land's merge was made; its `landed:` line was not. First the tail's `MERGE_HEAD` step (§ The landing tail). Then write SKILL.md § Step 5.3's `landed: <merge sha>`, with the sha MERGED printed, and run the rest of § The landing tail. Never a second merge, a review or a dispatch. |
| `unreachable` | `present` | absent | — | **S0b** not resumable | Report and stop: the run is not resumable from this session; name the remnant and leave it to the orphan-worktree rule (`troubleshooting.md` § Landing). When the remnant is a pending merge, the report says "a merge is pending in the main checkout (one this run may not have made)" and leaves it to that section's "A merge left uncommitted in the main checkout" instead. No GATE — it would read and write the sink that is unreachable. Dispatch nothing. |
| `unreachable` | `absent` | absent | — | **S0** | Nothing outlived the sink: go on as a new run. |
| `reachable` | — | no | no | — | Read PHASE: groups A–D. |

**Group A — PHASE `NONE` or `RIDERS`**

| PHASE | State | The single next action |
|---|---|---|
| `NONE` | **S0** nothing recorded | Nothing to resume: go on to the mode's next step after Step 0. |
| `RIDERS` | **S1** bindings only | GATE, the question being any decision the riders carry (the only live case: one raised before the first dispatch). `PENDING` → § The GATE. `ANSWERED` or `NONE` → as S0, with the recorded bindings and answers; nothing the record answers is asked again. |

**Group B — PHASE `DISPATCH`.** CAP is never read here: a dispatch an answer at a cap
opened is a dispatch, and its verdict meets the cap again — except a plan round the
operator granted, which ends on the path the grant named (`bindings.md` § Decisions, What
a cap ends in).

| LIVE | State | The single next action |
|---|---|---|
| `one` | **S3a** attach | Never dispatch beside it. Still running: leave it to finish. Finished with a report never recorded: collect the report and hand it to the step that writes its phase line — SKILL.md § Step 1 (planner), § Step 3.5 (implementer) or § Step 4.5 (reviewer). |
| `none` | **S3b** salvage | In a record written before cross-checks became riders, a `cross-checker` or `cross-checker-deep` dispatch is a cross-check — a `dispatch: cross-checker` line, whatever its effort. A record written before the role agents shows a second opinion as a `reviewer fable` dispatch in a run with no `model: fable` pin. Either is a cross-check, never salvaged: it is dropped, whatever its signal says, named under the Report's `open questions:` so the operator can accept it again, and the state is the one the last verdict before it gives (`model-routing.md` § Fable cross-checks). Any other: GATE first on a decision recorded after the dispatch — a fable pin's ask, or an effort pin's, when the call failed (`model-routing.md` § Fallback): `PENDING` → § The GATE. `ANSWERED` → § Salvage, then re-dispatch as the answer says. `NONE` → § Salvage, then re-dispatch at the same role, agent file, tier and round — the file the dead dispatch's role and effort name; under `inherit`, the one its signal names as not loaded; on a line written before the effort field (effort unrecorded), the file `model-routing.md` § Profiles routes that role and tier to now, the item's pins and any trial arm applied — a reviewer briefed by VARIANT; a producer at a fix round re-dispatched as `fix-loop.md` § A NEEDS_CHANGES round says for a gone agent (an implementer), or as `agent-brief.md` § Plan variant says (a planner). |
| `many` | **S13** two live agents | Stop. Dispatch nothing and stop no agent. GATE, the question naming every live id: which one to keep is always a human's decision, never the cycle's. |

**Group C — PHASE `RETURN`.** The producer is the `implementer`, or the `planner` in
`plan` mode; the role is a field of the line, never a selector.

| STATUS | reason | RETRIES | State | The single next action |
|---|---|---|---|---|
| `DONE`, `DONE_WITH_CONCERNS` | — | — | **S4** reviewable | SKILL.md § Step 4: dispatch a reviewer with VARIANT, or review it yourself when Step 2 rule 5's waiver holds for the diff as it stands. |
| `NEEDS_CONTEXT` | — | — | **S5** needs context | GATE, the agent's question. `ANSWERED` → re-dispatch the same producer with the answer, at least opus. Never a review. |
| `BLOCKED` | `setup` | < 3 | **S6a** retryable | Fix the setup the return names and re-dispatch the same producer. Not a round. |
| `BLOCKED` | `setup` | ≥ 3 | **S6b** retries spent | `$WI block` when there is an item, then GATE, the blocked change. |
| `BLOCKED` | `permission`, or none recorded | — | **S6c** permission | `$WI block` when there is an item, then GATE, the permission. Never re-dispatched. |

**Group D — PHASE `VERDICT`**, over verdict × FRESH × CAP; `—` marks an axis the row
does not read, because its action opens no round. Before S9 or S11 acts on a `CURRENT`
verdict: a decided-alone record of the cap (librarian-mode: a `decided:` line of class
`cap`), a budget waiver's `decided:` line of class `spend` (authority `answer 176`,
standalone too: `bindings.md` § Spend budget, The Done-alone line) or a `findings:
carried` block recorded after the last verdict means Step 4.3 already ran: take its action
— for the waiver, the round it opens — and write nothing new.

| verdict | FRESH | CAP | State | The single next action |
|---|---|---|---|---|
| `BLOCKED` | — | — | **S12** | RETRIES < 3 and reason `setup` → re-dispatch the reviewer with the setup fixed and VARIANT; not a round. Otherwise `$WI block` when there is an item, then GATE, the blocked review. |
| `CLEAR` | `CURRENT` | — | **S7** | `full`, `review`: SKILL.md § Step 5 (Land). `plan`: Step 1's after-`CLEAR` tail, its blocking open questions being the GATE's question, then Step 6. A fable offer is raised there too, never gated on (`model-routing.md` § Fable cross-checks). |
| `CLEAR` | `STALE` | `UNDER` | **S8** | `spent:` first (§ The GATE); then Step 4 with VARIANT. |
| `CLEAR` | `STALE` | `AT_CAP` | **S11** | `spent:` first; then GATE, the cap, naming the staleness. |
| `NEEDS_CHANGES` | `CURRENT` | `UNDER` | **S9** | Open a fix round (its spend check first, `bindings.md` § Spend budget, which writes a `cost:` line a dead run left unwritten, `must-fix ?`): resume the producer its `agent:` line names, or dispatch one, with the verdict's own `findings:` block verbatim — never a `findings: cross-check` rider, which goes to the next review brief (`fix-loop.md` § A NEEDS_CHANGES round). In `review` mode, GATE on the dispatch permission first (below). |
| `NEEDS_CHANGES` | `CURRENT` | `AT_CAP` | **S11** | GATE, the cap. |
| `NEEDS_CHANGES` | `STALE` | `UNDER` | **S10** | `spent:` first. The findings are spent with the verdict — the tree they judged is gone. Step 4 with VARIANT, the findings pasted for verification only. |
| `NEEDS_CHANGES` | `STALE` | `AT_CAP` | **S11** | `spent:` first; then GATE, the cap, naming the staleness. |
| `SHOW_STOPPER` | `CURRENT` | — | **S11** | GATE, the show-stopper; never re-dispatched on the verdict alone. `review` mode: the question may be the dispatch permission instead (below). |
| `SHOW_STOPPER` | `STALE` | `UNDER` | **S10** | As the `NEEDS_CHANGES` row above. |
| `SHOW_STOPPER` | `STALE` | `AT_CAP` | **S11** | `spent:` first; then GATE, the cap, naming the staleness. |

S11, `ANSWERED`: act exactly as SKILL.md § Step 4.4 would have — a waiver opens the round
it grants (a budget increase writes its `budget:` line first); a park or a block stops.
S11 at the cap on a `CURRENT` verdict, `NONE`: apply SKILL.md § Step 4.3 first — a stop
and carry (a granted plan path's end included), a finish round, or a round it opens
unasked past the fourth review is taken, not raised, unless the verdict is a
`SHOW_STOPPER` or a finding changes the scope or reverses a recorded decision; only its
raise goes to § The GATE.

**The dispatch permission in `review` mode.** There, S9's question is the dispatch
permission (SKILL.md § Usage), and so is the question of S11's current `SHOW_STOPPER` row
unless a yes to it is already in force from before this verdict: the ask stands in for
Step 4.4's only before any fix loop, and after one a show-stopper escalates as in `full`.
Answered no → report the findings to the branch's author, `$WI handoff <id>` noting it (no
item: nothing further), and stop. Answered yes → open the fix round, as S9 does in `full`.

## The landing tail

S2 and S2b share it: what SKILL.md § Step 5 does after its `landed:` line, run on whatever
a dead run left undone. In order:

1. **`MERGE_HEAD`.** `git -C "$MAIN" rev-parse -q --verify MERGE_HEAD` succeeds → report
   "landed `<merge sha>`; a merge is pending in the main checkout" and stop: follow
   `troubleshooting.md` § Landing, "A merge left uncommitted in the main checkout".
2. **Anything left?** S2 with an item only: the item is `done` → the tail already ran:
   report "already landed `<merge sha>`" and stop. With no item, and in S2b, go on: a
   store-less record has no mark of a finished tail — nothing left to remove proves
   nothing in `review` mode, whose Step 5.4 may have nothing to remove from the start —
   and steps 3–5 are safe to repeat.
3. **Checks on the base as it stands**: the Checks binding and `review-checklist.md` § 6
   from `$MAIN`, with `BASE=<merge sha>^1`, the base before this merge. A red one is
   this merge's only when `git -C "$MAIN" log --oneline <merge sha>..<base>` is empty;
   otherwise the report names those later commits beside the red check, since any of
   them may have caused it. Either way it follows `troubleshooting.md` § Landing, "A
   check is red on the base after the merge", and rules out the push below; it never
   re-enters the fix loop.
4. **Push.** Already on `origin/<base>` (`git -C "$MAIN" merge-base --is-ancestor <merge
   sha> origin/<base>` succeeds) → nothing to do. Under a librarian, never: the push is
   the librarian's, after its Report (`bindings.md` § What a librarian binds). Standalone,
   only when a recorded `answer:` picked `Merge and push` and step 3 was green: SKILL.md
   § Step 5.3's push. A push the dead run's invocation asked for in words was never
   recorded, so it is not made either. Every push not made is named in the report:
   "landed `<merge sha>`, not pushed" and why.
5. **Clean up and close**: SKILL.md § Step 5 steps 4 and 5 on whatever still exists — a
   worktree already removed or a branch already deleted is skipped, a dirty worktree is
   reported and asked about, never removed.

## The GATE

Wherever a row says GATE, and nowhere else, a pending decision is handled — by this
table, which applies `bindings.md` § Decisions and adds nothing to it:

| GATE | CHANNEL | Action |
|---|---|---|
| `NONE` | any | Raise the row's question as § Decisions raises any decision: a self-contained `decision:` line first. A resume is heavy analysis, so end the turn with the resume summary and ask at the start of the next. |
| `PENDING` | `ephemeral` | § Decisions' ephemeral arm: end the turn with the resume summary; the next turn opens by asking the recorded `decision:` verbatim. No second `decision:` line. |
| `PENDING` | `durable` | § Decisions' durable arm: hand back and stop. The caller resumes the target once the answer lands. |
| `ANSWERED` | any | Act on it exactly as the step that raised it would have. Never raise it again. |

**The `spent:` line.** A stale verdict spends the dispatch permission recorded under it:
the author's new commits are new information, so the question is asked afresh under the
next verdict, with the next findings. The rows that act on a `STALE` verdict — S8, S10
and S11's stale rows — write, before they act, one line

```
spent: dispatch-permission
```

for each permission pair not already followed by one, **answered or not**. Only a
`review` record ever carries one. It is recorded rather than derived: every test that
tries to derive it from git either spends the permission on the run's own fix round or
revives a spent "no" once a fresh review lands at the author's new sha — and all of them
have no value once the workspace is gone, while a recorded line survives.

## Salvage

Before S3b re-dispatches, nothing the dead run left is discarded:

- **implementer** — `git -C <workspace> log <T>..HEAD` and `git -C <workspace> status
  --short`, where `<T>` is the last counted verdict's `<sha>`, or the Base binding when
  there is none. Both go into the brief, and the re-dispatch builds on top of the
  worktree as it stands (the same move as `model-routing.md` § Fallback's mid-run 429).
- **planner** — the serials under the series path that the last `baseline:` does not
  list (every serial, before any review) go into the brief; the planner builds on them.
- **reviewer** — nothing: a reviewer writes nothing.

The re-dispatch writes a fresh `dispatch:` and `agent:` pair (SKILL.md § Step 2 rule 7);
the old id stays in the generation, so a later resume probes both.

## The resume summary

Step 0's expected output names the state, the facts that selected it, and the action
taken — e.g. `resumed at S10: verdict NEEDS_CHANGES round 2 at 1a2b3c is STALE (HEAD
4d5e6f), CAP UNDER; findings spent, re-review dispatched`. S0 says there was nothing
to resume; S0b says what is not resumable and why; S2b names the merge sha it found.
