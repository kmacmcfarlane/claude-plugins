# Gallery

Worked examples of every case in this skill. **Every example here is illustrative**: invented,
generic, about no real project, and the numbers are arbitrary. Each shows a situation, then
what the agent writes. Use them to check a rendering against the rules, not as text to copy.

---

## 1. Several decisions in one message

*Situation: five open decisions. The operator comes back tomorrow morning. They discussed the
changelog wording and the flaky tests an hour ago (warm); they have not seen the others. A
paused migration step holds a database lock that expires at 15:30 today.*

**Decisions** — *5 · one ⚠ one-way*

- **71 Resume the paused migration step?** — rec **(a) resume** · *reversible, narrow* · basis **strong** · *20 min old, lock expires 15:30, blocks the rest of the migration*
- **73 Rename the published package?** — rec **(b) keep the name, add an alias** · ⚠ one-way · basis **partial** · *5 h old, blocks the release notes*
- **74 Changelog: "fixes" or "resolves"?** — rec **(a) "fixes"** · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing* *(line only)*
- **72 Re-run the flaky test suite?** — rec **(a) re-run** · *reversible, narrow* · basis **strong** · *40 min old, blocks merging a reviewed change* *(line only)*
- **75 Date format for log output?** — *your preference, no rec* · *reversible, narrow* · *2 h old, blocks nothing*

**71 — Resume the paused migration step?**
**What:** step 4 of the customer-table migration is paused and holds a database lock.
**Why now:** the lock expires at 15:30 today; after that the step fails and must be re-run from the start (about 2 hours).
- **(a) Resume now** — *the step finishes in about 10 minutes; the tested rollback still works afterwards*
- **(b) Roll back the step** — *releases the lock; the migration waits for a fresh run*
- **(z) Decide later** — *at 15:30 the lock expires and the step fails; a full re-run costs about 2 hours*

Rec **(a)** · basis **strong** — *I ran the dry-run for this step and it passed* · unknown: none

**73 — Rename the published package?** ⚠ one-way
**What:** whether to rename the package `fastcsv` to `csvkit-fast`, which three other teams import.
**Why now:** the release notes wait on the name.
**Context you may have lost:** a published name cannot be taken back cleanly once others have moved to the new one; three teams import it today.

**(a) Rename now**
- *What happens:* the three teams' builds break until each updates its imports.
- *Undo:* renaming back leaves anyone who already moved broken a second time.
- *Who is affected:* the three importing teams.

**(b) Keep the name, add an alias**
- *What happens:* nothing breaks; the new name works alongside the old.
- *Undo:* the alias can be removed later, after notice.
- *Who is affected:* nobody now; two names to maintain.

**(c) Investigate first** — *about 20 minutes: check whether any importer pins the old name; could make (a) safe if none do*

**(z) Decide later** — *the release notes keep waiting; no deadline*

Rec **(b)** · basis **partial** — *observed: the package index lists 3 dependents; inferred: no internal callers (only this repo searched)*
*Basis:* observed — package index, 3 dependents (link) · inferred — no callers in this repo · unknown — whether the teams pin versions
*I'll repeat your choice back and act only once you confirm.*

**75 — Date format for log output?** · *your preference — no recommendation*
**What:** ISO 8601 (`2026-09-23T14:05:00Z`) or RFC 2822 (`Wed, 23 Sep 2026 14:05:00 +0000`).
**Why now:** the new logger needs one; nothing else waits on it.
- **(a) ISO 8601** — *sorts as text; the common choice for machine-read logs*
- **(b) RFC 2822** — *easier to read by eye; matches mail headers*
- **(z) Decide later** — *the logger ships with ISO 8601 until you choose; one config line changes it*

*No recommendation: no fact settles this.* · basis **strong** — *checked: nothing in the project reads either format* · unknown: none

*Reply with a letter (`71: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

*Gallery note — why this order: 71 breaks before you are back; the packaging group comes next because it holds a ⚠, with 74 kept beside 73; then 72, which blocks a merge, before 75, which blocks nothing.*

---

## 2. A warm, low-stakes card

*Situation: one decision, the operator watching live.*

**72 — Re-run the flaky test suite?**
**What:** the integration suite failed once on a network timeout unrelated to the change.
**Why now:** merging the reviewed change waits on a green run.
- **(a) Re-run** — *about 6 minutes; the merge goes ahead if it passes*
- **(z) Decide later** — *the merge waits*

Rec **(a)** · basis **strong** — *the failure log shows a connection timeout* · unknown: none

---

## 3. One-way but narrow (no ⚠)

**76 — Delete the scratch branch `try-parser-v2`?** · *one-way, narrow*
**What:** delete a branch only I used, whose useful commit is already merged.
**Why now:** tidying before the next task.
- **(a) Delete it** — *cannot be restored after the reflog expires; nothing else references it*
- **(b) Keep it** — *one more stale branch in the list*
- **(z) Decide later** — *nothing waits on it*

Rec **(a)** · basis **strong** — *the one commit that mattered is on main* · unknown: none

---

## 4. The read-back on a ⚠ answer

*Situation: decision 73 from example 1. The operator replies "73: b, keep and alias".*

*Read as: 73 → (b) keep the name `fastcsv` and add the alias `csvkit-fast`. This one is one-way — confirm and I'll go ahead, or change it.*

*The operator replies "yes".*

*Confirmed. Adding the alias now; I'll report when it is published.*

---

## 5. A template

*Situation: a recurring decision whose options are fixed; the operator has seen it before.*

- **77 Waive the review-round cap for the date-parser change?** — *template: review-round cap* · rec **(a) one more round** · basis **strong** · *reviewer's last finding is a one-line fix* · *(a) one more round · (b) ship as is · (c) park*

*The first time the operator meets this template in a session, it is shown as a full card.*

---

## 6. A preference

See decision 75 in example 1: options with their impacts, a label, and no recommendation.

---

## 7. Outside my authority

**78 — Allow a run the reviewer waived to ship to users?** · *no recommendation — outside my authority*
**What:** a report run passed with one check waived; shipping it puts the waived output in front of users.
**Why now:** the release is scheduled for Friday.
**Why no recommendation:** whether users may see output a reviewer waived is a product call, not mine.
- **(a) Ship it** — *users see the report on Friday, with the waived section as is*
- **(b) Hold it** — *the release slips until the check passes; about a day's work*
- **(c) Ship without the waived section** — *users get a shorter report; about an hour's work*
- **(z) Decide later** — *the release slips past Friday if undecided by Thursday noon*

*No recommendation: see why above.* · basis **partial** — *observed: the waived check's output; inferred: the fix estimate* · unknown: how users use that section

---

## 8. A time-critical alert

**Alert: the staging certificate expires in 10 minutes.** Staging goes dark for everyone when it does. *Options follow as soon as I have them.*

---

## 9. An open question

**Open questions** *(not decisions yet — each needs your framing)*
- What should the release criteria for the beta be? *I can't offer options until I know whether speed or stability comes first.*

---

## 10. A reply in words, and a reframe

*Situation: decision 79 asked which caching library to adopt. The operator replies "79 — the second one, but only for reads".*

*Read as: 79 → (b) the second library, used for reads only. Going ahead.*

*Situation: instead the operator replies "do we even need caching? the slow path is the database query".*

*Read as: a reframe of 79 — the question is whether to cache at all. New decision 81 replaces 79:*

**81 — Cache at all, or fix the slow query first?**
- **(a) Fix the query first** — *about half a day; may make caching unnecessary*
- **(b) Add the cache now** — *faster reads this week; the slow query stays*
- **(z) Decide later** — *reads stay slow*

Rec **(a)** · basis **partial** — *observed: the query takes 1.8 s in the profile; inferred: an index would fix it* · unknown: write load

---

## 11. `tell me`

*Situation: the operator replies "72: tell me which tests failed".*

*Read as: 72 → tell me (which tests failed).*

**72 — Re-run the flaky test suite?**
**Added:** two tests failed, both in the network client, both on the same connection timeout.
- **(a) Re-run** — *about 6 minutes; the merge goes ahead if it passes*
- **(z) Decide later** — *the merge waits*

Rec **(a)**, unchanged · basis **strong** — *the failure log shows the timeout* · unknown: none

---

## 12. `expand`

*Situation: example 1's list was shown; the operator replies "expand 74". In the next message
74 moves from a line to a card, keeps its number and place, and the rest stay as they were:*

- **74 Changelog: "fixes" or "resolves"?** — rec **(a) "fixes"** · *reversible, narrow* · basis **strong** · *2 h old*
- *…the other four lines as before…*

**74 — Changelog: "fixes" or "resolves"?**
**What:** the wording of one changelog entry for the parser fix.
**Why now:** the release notes collect entries today.
- **(a) "fixes"** — *matches the other 14 entries this release*
- **(b) "resolves"** — *reads more formally; this entry would stand out*
- **(z) Decide later** — *the entry ships with "fixes"*

Rec **(a)** · basis **strong** — *read the other entries in the changelog* · unknown: none

*On a block, `expand` gets: already at full detail — `tell me [what]` for something specific?*

---

## 13. `dig into` and its return

*Situation: the operator picks the priced option on decision 73: "73: c".*

*Read as: 73 → dig into (whether any importer pins the old name). About 20 minutes; 73 comes back to you with what I find.*

*Twenty minutes later:*

**73 — back from the investigation:** rename the published package? ⚠ one-way
**Found:** two of the three teams pin the package by version, not by name; the third imports it by name and would break.
*Recommendation unchanged: (b) keep the name, add an alias — one team still breaks on a rename.*
*…followed by the block, as in example 1, with the new fact in its basis line.*

---

## 14. `later`, with and without a when

*Situation: the operator replies "72: later, after lunch".*

*Read as: 72 → later (after lunch, about 13:30). The merge waits until then.*

*At 13:30:*

**72 — back, as you asked ("after lunch"):** re-run the flaky test suite?
*While it waited (2 h): a second change is now also waiting on a green run. Options and recommendation unchanged.*
*…followed by the card.*

*Situation: on decision 71 (the lock expiring at 15:30), the operator replies "later". No time, no regular check-in, return unknown.*

*Read as: 71 → later. When? Unless you say, I'll bring it back the next time you start a turn after at least one other exchange. Note: the lock expires at 15:30; if the step is still paused then, it fails and needs a full two-hour re-run. Keep that, or pick a time before 15:30?*

---

## 15. `you decide`, and its refusal on ⚠

*Situation: the operator replies "74: you decide".*

*Read as: 74 → you decide. I'll take (a) "fixes", to match the other entries; noted in my next update.*

*Situation: the operator replies "73: you decide".*

*73 is one-way — it needs your own choice. I recommend (b) keep the name and add an alias, because one importing team would break on a rename. Which do you want?*

---

## 16. `drop`

*Situation: the operator replies "80: drop" on a decision about a report layout that a later request made moot.*

*Read as: 80 → drop. Retired; it won't come back.*

---

## 17. A batch with exclusions

*Situation: decisions 85–89 were shown: 85 re-run a flaky suite, 86 bump a dev-only dependency's patch version, 87 tidy an internal README paragraph (all reversible, each with a recommendation), 88 force-push to rewrite a shared branch two people build on (⚠ one-way), 89 tabs or spaces in a new config (a preference). The operator replies "ok 85-89".*

*Accepted 85, 86, 87. Skipped: 88 (⚠ one-way, needs your own answer), 89 (your preference, no recommendation).*

*…followed by 88 as a block and 89 as a card, and the hint.*

---

## 18. Report after acting

- **Done: fixed a spelling slip ("recieve") in the setup guide, on my task branch** — *two-way (one revert), nobody else uses the branch; inside the task you gave me.*

*Not a decision: no number, no options, no hint. Never used for anything one-way or relied on by others.*

---

## 19. A status-quo default

**90 — Open the pull request now, or wait for the flaky suite?**
**What:** the change is ready; the flaky suite has not had a green run yet.
**Why now:** you asked for the change today.
- **(a) Open it now** — *reviewers start today; they may see one red check*
- **(b) Wait for a green run** — *about 20 minutes*
- **(z) Decide later** — *the branch stays as it is*

**If unanswered:** *I leave the branch as it is, unopened, and carry on with the next task. Nothing is lost.*
Rec **(b)** · basis **strong** — *the suite is running now* · unknown: whether it goes green

---

## 20. Re-showing decisions after a context reset

*Situation: three decisions were raised yesterday; since then the context was reset and the operator is cold. 92 was deferred "until the CI fix lands", and it has landed. 93's recommendation rested on an upstream bug that has since been fixed.*

**Decisions** — *3, raised yesterday · you are coming back after a context reset*

- **92 Upgrade the runtime dependency?** — rec **(a) upgrade** · *reversible, wide* · basis **partial** · *1 day old, touches every service's build*
- **93 Pin or float the parsing library?** — rec **(b) float** · *reversible, narrow* · basis **strong** · *1 day old* · *recommendation changed*
- **91 Adopt the new lint rule across the repo?** — rec **(a) adopt** · *reversible, narrow* · basis **strong** · *1 day old, unchanged* *(line only)*

**92 — back, as you asked ("until the CI fix lands"):** upgrade the runtime dependency?
*While it waited (1 day): the CI fix landed. Options and recommendation unchanged.*
**What:** move every service from runtime 3.11 to 3.12.
**Context you may have lost:** it touches every service's build; the CI fix removed the failure that held it back.
- **(a) Upgrade now** — *every service rebuilds; a failure in one is reverted per service*
- **(b) Upgrade one service first** — *a day slower; limits a surprise to one service*
- **(z) Decide later** — *the old runtime's security support ends next month*

Rec **(a)** · basis **partial** — *observed: the full CI run passes on 3.12; inferred: no runtime-specific code outside tests* · unknown: production-only behaviour

**93 — Pin or float the parsing library?**
*While it waited (1 day): upstream released 2.4.1, which fixes the bug the pin was guarding against. Recommendation changed from (a) pin to (b) float, because the bug is fixed.*
- **(a) Pin to 2.3.9** — *stays on a version without the fix*
- **(b) Float at 2.4.x** — *picks up the fix and later patches*
- **(z) Decide later** — *stays pinned*

Rec **(b)** · basis **strong** — *read the 2.4.1 release notes and ran the tests against it* · unknown: none

*Reply with a letter (`92: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*
