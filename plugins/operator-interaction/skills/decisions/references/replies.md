# Replies

How to read the operator's answer to a decision, and what to do with it. Replies come in
natural language; the words in the hint are shortcuts that make intent unambiguous, never a
requirement. Examples are **illustrative**.

## Reading a reply

1. Find the decision it answers: the number, or the one decision in play. A reply that names
   no number while several are open: ask which, in one line.
2. Classify it as one of the reply types below. Words other than the shortcuts count — "look
   into who imports it first" is `dig into`; "remind me tomorrow" is `later`; "skip it" is
   `drop`; "your call" is `you decide`.
3. **Echo** every reply that is not an exact `N: letter`, in one italic line before you act:
   *Read as: 43 → dig into (other callers in the access logs).* The echo is how a misreading is caught
   in one turn instead of after the damage.
4. Act — except on a ⚠ one-way choice (the read-back below).

When a reply mixes a letter and words (`43: b, keep it with a sunset date`), the letter
decides; the words are checked against the option and a mismatch is asked about, not guessed.

## Reply types

**Choose — `N: letter`, or a choice in words.** Act on it. For a ⚠ one-way decision, first
repeat the choice back and act only once the operator confirms:

*Read as: 43 → (b) keep the endpoint, with a deprecation header and a sunset date. This
decision is one-way — confirm and I'll go ahead, or change it.*

A confirmation in any words counts ("yes", "go", "confirmed"). The read-back applies only to
replies that choose an option that acts on the world; `later`, `tell me`, `expand`, `dig into`
and `drop` on a ⚠ decision are echoed normally. So is picking a priced *investigate first*
option (`43: c`): it is a `dig into`, it acts on nothing, and it gets an echo, not a
read-back.

**`later [when]` — decide later.** Nothing happens except that the decision waits. Set its
wake:

- a time — "tomorrow morning", "after 14:00";
- an event — "when the load test finishes", "after the release";
- none given — your next check-in, if you have a rhythm (a status report); otherwise ask, and
  state the default: *Read as: 3 → later. When? Unless you say, I'll bring it back the next
  time you start a turn after at least one other exchange.* *(provisional — pending the
  operator's ruling)*

**A deadline changes `later`.** When the decision has a deadline and the wake is not known to
fall before it — a later time, an event with no time, or the default — the echo warns and
restates what happens at the deadline:

*Read as: 41 → later (after the standup). Note: the storage lease lapses at 17:45; if the
backup is still paused then, the half-written snapshot is lost and the backup starts over
(about 3 hours). Keep that, or pick a time before 17:45?*

When the wake fires, re-show the decision with what changed while it waited
(`references/rendering.md` § Re-show with what changed). A deferral nobody wakes becomes a
default by omission; every deferral has a wake.

**`tell me [what]` — more context.** Re-show the **same decision, same number**, with the fact
added in a **Added:** line. Options and recommendation stay as they were, unless the new fact
changes the recommendation — then say so and why. Near-zero cost when you already know the
fact; if finding it needs real work, say so and offer `dig into` instead.

**`expand` — more detail.** Show the decision one level higher in your next message (line →
card → block). It keeps its number and place, and stays raised on later re-shows. On a block:
*already at full detail — `tell me [what]` for something specific?*

**`dig into [what]` — investigate first**, typed or picked as a priced option on the card.
Echo it, with no read-back. A bounded investigation: state its cost up front
(time, and model or spend where it matters), run it, and bring back the **same number** with
a **Found:** line. The decision is re-shown with what the investigation changed. Offer it
yourself as a priced option on the card when the missing fact could change the choice and
costs less to find than a wrong choice would.

**`you decide` — hand it back.** You decide, record your reason, and say what you chose in
your next update: *Read as: 44 → you decide. I'll take (a) "deprecated", because it matches
the earlier notices; noted in my next update.* **Refused on ⚠ one-way:** *43 is one-way — it
needs your own choice. I recommend (b), because …. Which do you want?*

**`drop` — retire it.** *Read as: 80 → drop. Retired; it won't come back.* If something still
depends on it, say what happens now.

**Reframe — the reply changes the question.** When the operator answers a different question
than the one asked ("the real question is whether we need caching at all"), withdraw the old
decision and raise the new one under a new number that points back: *Read as: a reframe of 79
— new decision 81 replaces it.* Then show 81 at its level.

**Batch — `ok N-M`, or `N-M: rec`.** Accept the recommendation for each decision in the range,
except:

- ⚠ one-way decisions — they need the operator's own choice;
- decisions with no recommendation (preference, outside my authority) — there is nothing to
  accept.

Echo what was accepted and why the rest were skipped, then re-ask the skipped ones:

*Accepted 51, 52, 53. Skipped: 54 (⚠ one-way, needs your own answer), 55 (your preference,
no recommendation).*

Never write "answer alone" in the echo; say why each was skipped.

## Defaults

- **No timed default on an action.** An unanswered decision never turns into an action because
  time passed. *(provisional — pending the operator's ruling)*
- **A status-quo default** may be stated on the card, because it changes nothing: *If
  unanswered: I leave the branch as it is and carry on with other work.* It says what stays as
  it is; it never says an option of the agent's choosing takes effect.
- Why: silence cannot tell agreement from "didn't see it" or "didn't care". Every practice
  that treats silence as consent limits itself to matters already low-stakes, and the harm
  comes when someone relies on the outcome before the operator reviews it
  (`references/rationale.md`).
