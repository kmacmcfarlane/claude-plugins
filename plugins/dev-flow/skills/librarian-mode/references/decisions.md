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

  It covers the content floor, the list line / card / block, the order, the hint, reading
  replies with an echo, the ⚠ read-back, and "decide later" with a wake.
- **Never through AskUserQuestion.** That is the librarian's own rule (SKILL.md § Intake
  step 3), and the skill agrees. The opt-in dialog is the one exception (`opt-in.md`).

Without the skill, nothing here applies. `decisions needed:` stays the numbered list SKILL.md
§ Report describes (one decision per number, its options and their impact, recommendation
first), and replies are recorded as `answer N:`.

## What the librarian supplies to the skill

| The skill asks for | The librarian's binding |
|---|---|
| the caller's numbering | the store counter: `decision N:` continues from the highest N (SKILL.md § Rehydrate step 3); a number is never reused |
| the caller's next check-in (the default wake) | **the next Report**; a `later` with no time or event wakes there |
| the operator's expected return ("likely back") | what the operator said ("back tomorrow morning"), in the item or the transcript; otherwise the skill's fallback |
| who is reading, and how warm | after Rehydrate the operator is **cold** on every decision raised before the reset; the first Report after it re-shows them per the skill, with what changed since each was raised |
| related decisions (groups) | the same parent item, or the same plugin or files |

## What the store records

The store stays the source of truth. The card is how a decision is shown; the decision
keeps one line in the item.

- **Raised:** `decision N: <question, one line> — options: (a) … [recommended] | (b) … | (z) decide later`,
  recommendation first, as the `dev-cycle` skill's `references/record-lines.md` gives the
  `decision:` line.
  One line, as today, so `wi needs-input` and a later session can still read it. When the
  item is ⚠ one-way, write `⚠ one-way` after the question.
- **Answered:** `answer N: <the reply> (read as: <the echo's reading>)`. The reading is
  recorded because a natural-language reply can be misread, and the echo is what the
  operator saw.
- **⚠ one-way:** repeat the choice back first. Record `answer N:` only when the operator
  confirms. Nothing acts before that.
- **`later [when]`:** `wake N: <time | event | next Report>`. There is no `answer N:`, so the
  decision stays open and `wi needs-input` keeps listing it. Deferred again, it gets another
  `wake N:`; the last one wins (`grep -n '^wake N:'`, last hit). At the wake, re-show it
  with what changed.
- **`tell me` / `expand`:** nothing new in the store. Re-show the same number next round.
- **`dig into [what]`:** a bounded investigation, dispatched like any other (a `dispatch:`
  line, routing and the quota sense apply); its result comes back on the same number.
- **`you decide`:** `answer N: you decide — chose (x), because …`. Refused on ⚠, as the skill
  says.
- **`drop`:** `answer N: drop — withdrawn`.
- **A reframe:** `answer N: reframed as decision M`, and M is raised to the floor like any
  new decision.
- **A batch (`ok N-M`):** one `answer` line per accepted number. The skipped ones stay open
  and are re-asked, as the skill says.

## The Report

The four lines per landed change stay exactly as SKILL.md § Report gives them. With the
skill:

1. Each change's `decisions needed:` names that change's decision numbers, or `none`.
2. After the last four-line block comes **one decisions block**. It carries every open
   decision, each as a list line in the skill's order. A deferred one also shows its wake.
3. Below the list, some decisions are shown in full, at the level the skill gives them, in
   list order:
   - those raised since the last Report;
   - those whose wake has come;
   - after Rehydrate, every open one (the cold re-show);
   - every ⚠ one-way decision, always, as a block;
   - any the operator raised with `expand`, which stays raised.

   Every other open decision stays a list line. A deferred one stays a list line with its
   wake until the wake comes.
4. The hint closes the decisions block when it carries two or more decisions. It closes
   the block, not the message.
5. Then the push outcome, any `incoming:` lines, and the team summary, as today.

A decision raised between Reports (an Intake ask, a blocked item) is put to the operator in
the message that raises it, per the skill. It is carried in every later Report per items 2
and 3 until it is answered.
