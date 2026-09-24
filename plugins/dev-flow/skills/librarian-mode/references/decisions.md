# Putting decisions to the operator

Loaded from SKILL.md § Intake step 3, § The cycle (Decision channel) and § Report. This
file binds the librarian to the `operator-interaction` plugin's `decisions` skill, a soft
dependency (README principle 4). It says only what the librarian supplies to that skill and
what the store records. How a decision is written, ordered and answered is the skill's, and
is not restated here.

## When it applies

The skill is available when the session's skill listing carries `operator-interaction:decisions`
(the `operator-interaction` plugin is installed). Then:

- **Load it at Rehydrate** (SKILL.md § Rehydrate step 2) with the Skill tool, and again after
  every `/clear` or compaction. It is knowledge only: it asks nothing and writes nothing.
- **Every decision the librarian raises follows it:**
  - an Intake ask (step 3);
  - anything dev-cycle raises through the decision channel;
  - a Groom row that needs the operator (`idle-turn.md`);
  - every decision a Report carries.

  It covers the content floor, the list line / card / block, the order, the layout, the hint,
  reading replies with an echo, the read-back on a one-way choice, and "decide later" with a
  wake.
- **Never through AskUserQuestion.** That is the librarian's own rule (SKILL.md § Intake
  step 3), and the skill agrees. The opt-in dialog is the one exception (`opt-in.md`).

Without the skill, nothing here applies. `decisions needed:` stays the numbered list SKILL.md
§ Report describes (one decision per number, its options and their impact, recommendation
first), and replies are recorded as `answer N:`.

## What the librarian supplies to the skill

| The skill asks for | The librarian's binding |
|---|---|
| the caller's numbering | the store counter: `decision N:` continues from the highest N (SKILL.md § Rehydrate step 3); a number is never reused |
| the default wake ("the next time I finish a piece of work and report") | **the next Report**; a `later` with no time or event wakes there |
| the operator's expected return | what the operator said ("back tomorrow morning"), in the item or the transcript; when they said nothing, the return is unknown and every stated deadline goes first |
| who is reading, and how warm | after Rehydrate the operator is **cold** on every decision raised before the reset; the first Report after it re-shows them per the skill, with what changed since each was raised. Between resets: a decision shown in a Report written after the operator's last turn has **not been seen** — background returns can write several Reports while the operator is away — so the next Report shows it at its level again, not *(shown before)*. Your own transcript tells you: has the operator taken a turn since that Report? |
| related decisions (groups) | the same parent item, or the same plugin or files |

## What the store records

The store stays the source of truth, and it keeps the **card**, so a re-show after a reset
renders what the operator read instead of composing it again.

- **Raised:** a headline line, then the card as indented lines under it:

  ```
  decision N: <question, one line> — options: (a) … [recommended] | (b) … | (z) decide later
    raised: <UTC time, e.g. 2026-09-24T14:05Z>
    what: <what is decided, ids glossed>
    why now: <why now; blocks: …>
    (a) <option> — <its impact> [— undo: <how, or cannot>]
    (b) <option> — <its impact>
    (z) decide later — <what waiting costs; the deadline, if any>
    rec: (a) · basis <word> — <reason>
    unknown: <what isn't known, or none>
  ```

  The headline is as the `dev-cycle` skill's `references/record-lines.md` gives the
  `decision:` line, so `wi needs-input` and the counter grep (`^decision [0-9]`) read it
  unchanged; the indented lines match neither `^decision` nor `^answer`. When the decision is
  ⚠ one-way, write `⚠ one-way` after the question, and every option line carries its
  `undo:`. A block's *context you may have lost* goes on a `context:` line after `why now:`.
  A preference or an outside-authority decision writes its label on the `rec:` line.
- **Revised:** when the options or the recommendation really change, write `decision N:`
  again with the new card and a `revised: <time> — <why>` line under it; the last one wins.
- **Re-show:** render the last stored card, adding only *while it waited*.
- **Answered:** `answer N: <the reply> (read as: <the echo's reading>)`. The reading is
  recorded because a natural-language reply can be misread, and the echo is what the
  operator saw.
- **A one-way choice** (the chosen option's `undo:` says it cannot be undone): repeat the
  choice back first. Record `answer N:` only when the operator confirms. Nothing acts before
  that. A reversible choice on a ⚠ decision is echoed and recorded at once.
- **`later [when]`:** `wake N: <time | event | next Report>`. There is no `answer N:`, so the
  decision stays open and `wi needs-input` keeps listing it. Deferred again, it gets another
  `wake N:`; the last one wins (`grep -n '^wake N:'`, last hit). At the wake, re-show it
  with what changed.
- **`tell me`:** an `Added:` fact that changes an option's impact or the rec is a revision
  (above); otherwise nothing new in the store. **`expand`:** nothing new; the same number is
  shown a level higher next round.
- **`dig into [what]`:** a bounded investigation, dispatched like any other (a `dispatch:`
  line, routing and the quota sense apply); its result comes back on the same number.
- **`you decide`:** `answer N: you decide — chose (x), because …`. On ⚠, only a reversible
  option; when the only good answer is the one-way option, it is re-asked, as the skill
  says.
- **`drop`:** `answer N: drop — withdrawn`.
- **A reframe:** `answer N: reframed as decision M`, and M is raised to the floor like any
  new decision.
- **A batch (`ok N-M`):** one `answer` line per accepted number. The skipped ones stay open
  and are re-asked, as the skill says.

## The Report

The four lines per landed change stay exactly as SKILL.md § Report gives them. With the
skill, the decisions come **last in the turn**, where the operator's eye is when you stop:

1. Each change's `decisions needed:` names that change's decision numbers, or `none`.
2. Then the push outcome, any `incoming:` lines, and the team summary, as SKILL.md § Report
   gives them.
3. Then **one decisions block**, the last thing written, laid out as the skill says: the
   decisions shown in full first, in list order, then the compact list of every open decision
   (a deferred one also shows its wake), then the hint when it carries two or more.
4. Shown in full, at the level the skill gives them:
   - those raised since the last Report;
   - those whose wake has come;
   - those shown in a Report the operator has not had a turn since (not yet seen);
   - after Rehydrate, every open one (the cold re-show, paged as the skill says);
   - a ⚠ one-way decision on its first showing and whenever the operator is cold on it;
   - any the operator raised with `expand`, which stays raised.

   Every other open decision is a list line only, ending *(shown before)*. A deferred one
   stays a list line with its wake until the wake comes.

A decision raised between Reports (an Intake ask, a blocked item) is put to the operator in
the message that raises it, per the skill — last in that message. It is carried in every
later Report per items 3 and 4 until it is answered.
