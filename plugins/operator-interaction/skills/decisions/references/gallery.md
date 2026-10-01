# Gallery

Worked examples of every case in this skill. **Every example here is illustrative**: invented,
generic, about no real project, and the numbers are arbitrary. Each shows a situation, then
what the agent writes. Use them to check a rendering against the rules, not as text to copy.

---

## 1. Several decisions in one message

*Situation: five open decisions. The operator comes back tomorrow morning. Fifty minutes ago
they discussed the deprecation notice wording and the docs cache (warm on both); they have not
seen the others. The nightly backup is paused and holds a storage lease that lapses at 17:45
today.*

**Decisions** — *5 · one ⚠ one-way*

**41 — Resume the paused nightly backup?**
**What:** the nightly backup of the reporting database paused halfway through its snapshot and holds a storage lease.
**Why now:** the lease lapses at ~17:45 today (90 min from 16:15); after that the half-written snapshot is discarded and the backup starts over (about 3 hours).
**Why ask:** aborting is a real choice too: the snapshot fills shared storage the reporting team also writes to, and whether tonight's backup outranks their jobs is yours to weigh.
- **(a) Resume now** — *the snapshot finishes in about 15 minutes*
- (b) Abort the backup — *releases the lease; no backup tonight unless it is started again*
- (z) Decide later — *it waits; at 17:45 the lease lapses and the snapshot is lost*

Rec **(a)** · basis **strong** — *checked the storage quota: 40% free, enough to finish* · unknown: none

**43 — Remove the deprecated `/v1/export` endpoint?** ⚠ one-way
**What:** whether to delete the old export endpoint `/v1/export`, replaced last quarter by `/v2/export`.
**Why now:** the API cleanup release is cut on Thursday; this change goes out in it, or waits for the next one.
**Why ask:** removing it breaks two partners and cannot be quietly undone; that call is not mine to take alone.
**Context you may have lost:** two partner integrations still call `/v1/export`; once it is removed their exports fail until they move to `/v2`, and a removed public endpoint cannot quietly come back for the clients that already adapted.

(a) Remove it now
- *What happens:* the two partners' exports fail from Thursday until they switch.
- *Undo:* restoring it takes a hotfix release; the partners see an outage either way.
- *Who is affected:* the two partners, and their users.

**(b) Keep it, with a deprecation header and a sunset date**
- *What happens:* nothing breaks; every response carries a header announcing removal in 90 days.
- *Undo:* the header can be dropped at any time.
- *Who is affected:* nobody now; the old code stays for 90 more days.

(c) Investigate first — *about 15 minutes: read this month's access logs for other callers; could change the answer if both partners have already switched*

(z) Decide later — *it waits; the endpoint stays as it is, and the cleanup release goes out without this change*

Rec **(b)** · basis **partial** — *observed: this week's access log shows 2 partners calling it; inferred: no internal callers (only this repo searched)*
*Basis:* observed — access log, 2 partner callers this week (link) · inferred — no callers in this repo · unknown — whether the partners have a switch planned
*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*

**45 — Units on the storage dashboard: MiB or MB?** · *your preference — no recommendation*
**What:** show sizes in binary units (MiB, 1,048,576 bytes) or decimal units (MB, 1,000,000 bytes).
**Why now:** the new dashboard needs one; nothing else waits on it.
**Why ask:** no fact settles it; which readers the units should suit is yours to say.
- (a) MiB — *matches what the operating system's tools report*
- (b) MB — *matches the storage provider's bill*
- (z) Decide later — *it waits; the dashboard keeps its placeholder units until you choose (one config line)*

*No recommendation: no fact settles this.* · basis **strong** — *checked: nothing reads the dashboard's units programmatically* · unknown: none

*Gallery note — layout and order: the cards and the block come first, the compact list and the hint last, so the list is what is on screen when the agent stops. Why this order: 41 breaks before you are back; the API cleanup group comes next because it holds a ⚠, with 44 kept beside 43; then 42, which blocks the docs build, before 45, which blocks nothing. 44 and 42 stay list lines: you are warm on both, both are two-way and narrow on a strong basis, 44's options converge and 42 is a template you have seen. 41, 43 and 45 are cold, so each is at least a card; 43 is a block because this is its first showing. In each card and the block the options keep their letter order and only the recommended one is bold: 43's (b) stays second, and 45, with no recommendation, bolds none.*

- **41 Resume the paused nightly backup?** — rec **(a) resume** · *reversible, narrow* · basis **strong** · *25 min old, storage lease lapses ~17:45 (90 min from 16:15), blocks tonight's backup*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** · ⚠ one-way · basis **partial** · *6 h old, misses Thursday's API cleanup release if undecided*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** · *reversible, narrow* · basis **strong** · *why ask: partners read it, and (b) warns them more plainly* · *50 min old, blocks nothing* *(line only)*
- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *why ask: clearing it drops the other branch's cached build too* · *10 min old, blocks the docs build* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *3 h old, blocks nothing*

*Reply with a letter (`41: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

---

## 2. A warm, low-stakes card

*Situation: one decision, the operator watching live. The options diverge, so it is a card, not a line.*

**46 — Retry the failed preview deploy?**
**What:** the preview deploy of the search-page change failed while pulling its base image.
**Why now:** the design review this afternoon needs the preview.
**Why ask:** if the retry fails too, the review starts with no preview at all; you may prefer yesterday's build as the sure thing.
- **(a) Retry now** — *about 4 minutes; the preview is up if it succeeds*
- (b) Deploy yesterday's build instead — *the review sees the old page*
- (z) Decide later — *it waits; no preview until someone deploys*

Rec **(a)** · basis **strong** — *the deploy log shows a registry timeout, not a build error* · unknown: none

---

## 3. One-way but narrow (no ⚠)

**47 — Delete last month's unused staging snapshot `stg-0814`?** · *one-way, narrow*
**What:** delete the staging database snapshot from August 14, which nothing restores from.
**Why now:** staging storage is at 85% of its quota.
**Why ask:** the snapshot cannot be recovered once it is deleted.
- **(a) Delete it** — *frees 120 GB; the snapshot cannot be recovered afterwards*
- (b) Keep it — *storage stays at 85%; a later snapshot may fail when it fills*
- (z) Decide later — *it waits; storage keeps filling by about 2% a day*

Rec **(a)** · basis **strong** — *listed the restore jobs: none reference it* · unknown: none

---

## 4. The read-back — only for a one-way option

*Situation: decision 43 from example 1. The operator replies "43: a, remove it". Option (a)'s
Undo line says the partners see an outage either way: it cannot be taken back.*

*Read as: 43 → (a) remove `/v1/export` on Thursday. That can't be undone for the two partners who break — confirm and I'll go ahead, or change it.*

*The operator replies "go".*

*Confirmed. Removing it in the Thursday release; I'll say when it is out.*

*Situation: instead the operator replies "43: b, keep it with a sunset date". Option (b) can be
undone at any time, so it is echoed and acted on — no confirmation round.*

*Read as: 43 → (b) keep `/v1/export`, with a deprecation header and a 90-day sunset date. Going ahead — the header can be dropped at any time.*

---

## 5. An ask for another round (a template)

*Situation: the retry-policy change has had its four review rounds — the cap — and the last
review left one medium finding open. The review-round cap is a template: its options are
fixed, so they ride by reference once the operator has seen it. Its justification never
does, because what is left and what a round costs change every time. The first time in a
session, a card:*

**48 — One more review round for the retry-policy change?** · *template: review-round cap*
**What:** the change has used its four review rounds; the last review left one finding open, so it cannot land as it is.
**Why now:** the change is blocked until you answer; nothing else waits on it.
**Why ask:** another round spends quota and your attention past the cap you set: the finding under *If left* is what it buys.
**If left:** *one medium finding: after a restart the retry counter starts again from zero, so a job that fails on every run is retried forever instead of stopping after five tries.*
**A round costs:** *about 20 minutes and roughly 3% of the 5-hour quota; one more answer from you if that round does not clear it.*
- **(a) One more round** — *the fix goes back to the implementer, then a fresh review; it lands in about 20 minutes if it clears*
- (b) Ship as is — *it lands now, with the endless retry in it*
- (c) Park it — *the change waits, unmerged, until someone takes it up*
- (z) Decide later — *it waits, unmerged; nothing lands*

Rec **(a)** · basis **strong** — *the finding names the line and a one-line fix; an endless retry costs more than one round* · unknown: none

*Later in the session the operator is warm and has seen the template, so a new ask on it,
low-stakes on a strong basis, may stay a line — the options by reference, the justification
still on it:*

- **49 One more review round for the search-index change?** — rec **(a) one more round** · *template: review-round cap* · *reversible, narrow* · basis **strong** · *if left: a deleted page stays in search results until the nightly rebuild · a round: ~10 min, ~1% of quota, one more answer from you* · *10 min old, blocks the search-index change* · **(a) one more round** · (b) ship as is · (c) park it · (z) decide later — *it waits, unmerged*

*Not this: "Waive the cap? — rec (a) one more round" with nothing about what is left or what
the round costs. The operator cannot weigh an impact they are not shown.*

---

## 6. A preference

See decision 45 in example 1: the preference list line (label in the rec slot, stakes and
basis kept), then a card with options, their impacts, the label, and no recommendation.

---

## 7. Outside my authority

**78 — Allow a run the reviewer waived to ship to users?** · *no recommendation — outside my authority*
**What:** a report run passed with one check waived; shipping it puts the waived output in front of users.
**Why now:** the release is scheduled for Friday.
**Why ask:** shipping it puts output a reviewer waived in front of users, and nothing I can check says whether that is acceptable.
**Why no recommendation:** whether users may see output a reviewer waived is a product call, not mine.
- (a) Ship it — *users see the report on Friday, with the waived section as is*
- (b) Hold it — *the release slips until the check passes; about a day's work*
- (c) Ship without the waived section — *users get a shorter report; about an hour's work*
- (z) Decide later — *it waits; the release slips past Friday if undecided by Thursday noon*

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
**What:** whether to put a cache in front of the product-listing query, or first make the query itself fast.
**Why now:** the listing page takes about 2 seconds to load, and the performance review is next week.
**Why ask:** it turns what you asked for — a cache — into a query fix; changing the scope of your request is yours to say.
- **(a) Fix the query first** — *about half a day; may make caching unnecessary*
- (b) Add the cache now — *faster reads this week; the slow query stays*
- (z) Decide later — *it waits; reads stay slow*

Rec **(a)** · basis **partial** — *observed: the query takes 1.8 s in the profile; inferred: an index would fix it* · unknown: write load

---

## 11. `tell me`

*Situation: decision 46 from example 2, shown just above. The operator replies "46: tell me
what timed out". Only what the fact changes is sent; the card is one scroll up.*

*Read as: 46 → tell me (what timed out).*

**46 — Added:** pulling the base image from the container registry timed out after 5 minutes; the registry's status page showed degraded service then and shows normal now.
Rec **(a)**, unchanged · basis **strong** — *the registry reports normal service again*

---

## 12. `expand`

*Situation: example 1's message was shown and the operator has replied since, so 41, 43 and 45
were seen. They reply "expand 44". The next message renders 44 at its new level (a card), then
the list: 41, 43 and 45 are unchanged, so they are not rendered again and their lines say so.
43 keeps its ⚠ label; `expand` brings its block back. 42 is still a line.*

**Decisions** — *5 · one ⚠ one-way*

**44 — Deprecation notice: "deprecated" or "scheduled for removal"?**
**What:** the wording of the notice in the `/v1/export` response header and in the release notes.
**Why now:** it goes out with the API cleanup release.
**Why ask:** partners read the notice, and (b) warns them more plainly than the three notices before it.
- **(a) "deprecated"** — *matches the three endpoints deprecated before*
- (b) "scheduled for removal" — *says more plainly that it will go; the only notice worded this way*
- (z) Decide later — *it waits; no notice is published until you choose*

Rec **(a)** · basis **strong** — *read the three earlier notices* · unknown: none

- **41 Resume the paused nightly backup?** — rec **(a) resume** · *reversible, narrow* · basis **strong** · *35 min old, storage lease lapses ~17:45 (80 min from 16:25), blocks tonight's backup* *(shown before)*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** · ⚠ one-way · basis **partial** · *6 h old, misses Thursday's API cleanup release if undecided* *(shown before)*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing*
- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *why ask: clearing it drops the other branch's cached build too* · *20 min old, blocks the docs build* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *3 h old, blocks nothing* *(shown before)*

*Reply with a letter (`44: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

*On a block, `expand` gets: already at full detail — `tell me [what]` for something specific?*

---

## 13. `dig into` and its return

*Situation: the operator picks the priced option on decision 43: "43: c". Picking it is a dig
into: it is echoed, with no read-back, because it acts on nothing.*

*Read as: 43 → dig into (other callers in this month's access logs). About 15 minutes; 43 comes back to you with what I find.*

*Fifteen minutes later:*

**43 — back from the investigation:** remove the deprecated `/v1/export` endpoint? ⚠ one-way
**Found:** one of the two partners switched to `/v2` last week; the other still calls `/v1` every day. No other callers.
*Recommendation unchanged: (b) keep it with a sunset date — one partner would still break.*
*…followed by the block, as in example 1, with the new fact in its basis line.*

---

## 14. `later`, with and without a when

*Situation: the operator replies "46: later, after the standup".*

*Read as: 46 → later (after the standup, about 10:30). The preview waits until then.*

*At 10:30:*

**46 — back, as you asked ("after the standup"):** retry the failed preview deploy?
*While it waited (1 h): the registry is healthy again, and the design review moved to 14:00. Options and recommendation unchanged.*
*…followed by the card.*

*Situation: on decision 41 (the storage lease lapsing at ~17:45), the operator replies "later". No time given; the agent is partway through a migration it expects to finish in about two hours.*

*Read as: 41 → later. I'll bring it back when I next finish a piece of work and report — about two hours, after the migration — or tell me a time. Note: that is likely after the storage lease lapses at ~17:45 (90 min from 16:15); if the backup is still paused then, the half-written snapshot is lost and the backup starts over (about 3 hours). Keep that, or pick a time before 17:45?*

---

## 15. `you decide`, and on ⚠

*Situation: the operator replies "44: you decide".*

*Read as: 44 → you decide. I'll take (a) "deprecated", to match the earlier notices; noted in my next update.*

*Situation: the operator replies "43: you decide". The recommendation, (b), can be undone; so
the agent may take it, and says it will never take (a) on its own.*

*Read as: 43 → you decide. I'll take (b), keep it with a sunset date — it can be undone at any time. Removing the endpoint, (a), can't be, so I won't do that without your own choice.*

*Had the recommendation been the one-way option, the reply would be: 43's best answer is (a), which can't be undone — it needs your own choice. Which do you want?*

---

## 16. `drop`

*Situation: the operator replies "80: drop" on a decision about a report layout that a later request made moot.*

*Read as: 80 → drop. Retired; it won't come back.*

---

## 17. A batch with exclusions

*Situation: decisions 51–55 were shown as a list: 51 regenerate the API reference docs, 52
bump a test-only library's patch version, 53 rename a private helper function (all two-way and
narrow, each with a recommendation), 54 drop the `legacy_score` column from the shared
analytics table that two dashboards read (⚠ one-way), 55 light or dark theme for the internal
status page (a preference). The operator replies "ok 51-55".*

*Accepted 51, 52, 53. Skipped: 54 (⚠ one-way, needs your own answer), 55 (your preference, no recommendation).*

**Decisions** — *2 · one ⚠ one-way*

*…54 as a block (the operator has not seen it as one) and 55 as a card, then the list:*

- **54 Drop the `legacy_score` column from the shared analytics table?** — rec **(b) keep it, stop writing to it** · ⚠ one-way · basis **partial** · *2 h old, blocks the schema cleanup*
- **55 Theme for the internal status page: light or dark?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *2 h old, blocks nothing*

*…and the hint, last.*

---

## 18. FYI after acting

- **Done: fixed a broken link in the contributing guide, on my task branch** — *two-way, nobody else uses the branch · inside the task you gave me · undo: one revert*

*Not a decision: no number, no options, no hint. Never used for anything one-way or relied on by others. A single line needs no heading; several go under* **Done alone** *(example 24).*

---

## 19. A status-quo default

**56 — Open the pull request now, or wait for the benchmark run?**
**What:** the retry-policy change is ready; its benchmark run finishes in about 25 minutes.
**Why now:** you asked for the change today.
**Why ask:** opening it now starts the reviewers' time before the benchmark is known, against your wish to have it today.
- (a) Open it now — *reviewers start today; the benchmark result arrives mid-review*
- **(b) Wait for the benchmark** — *about 25 minutes*
- (z) Decide later — *it waits*

**If unanswered:** *I leave the branch as it is, unopened, and carry on with the next task. Nothing is lost.*
Rec **(b)** · basis **strong** — *the benchmark is running now* · unknown: whether it shows a regression

---

## 20. Re-showing decisions after a context reset

*Situation: three decisions were raised yesterday; since then the context was reset, so the
operator is cold and every decision is shown as a card or a block. 62 was deferred "until the
load test finishes", and it has finished. 63's recommendation rested on a CDN outage that has
since ended. Nothing changed for 61. None has a deadline and none is ⚠, so they go by waiting
cost: 62 blocks the worker rollout, 63 blocks the docs site build, 61 blocks nothing. 62 is
wide and the reader is cold, so it is a block (with no read-back: it is not ⚠). The store kept
each card with its raised-at time, so each is rendered from the stored card, plus what changed
while it waited — not composed again. Each stored card holds the context cue written when it
was raised, so under *while it waited* the cards carry **Context:**, and 62's block opens its
*Context you may have lost* with the same cue.*

**Decisions** — *3 open · shown again after a context reset*

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new message broker?
*While it waited (1 day): the load test finished — the new broker held three times peak load with no lost messages. Options and recommendation unchanged.*
**What:** switch every worker service from the old job queue to the new message broker.
**Why now:** the worker rollout waits on it.
**Why ask:** every worker service moves at once; how fast the rollout goes is yours to set.
**Context you may have lost:** you left it at the broker trial on the email worker · you decide whether every worker moves now or one goes first. The switch is a config change in each service; the old queue keeps running for a week as a fallback.

**(a) Move all workers now**
- *What happens:* every worker service reads from the new broker from today.
- *Undo:* switch each service's config back within the week; after that the old queue is gone.
- *Who is affected:* every worker service, and whoever is on call for them.

(b) Move one service first
- *What happens:* the email worker moves today; the rest follow in two days if it stays quiet.
- *Undo:* one config change.
- *Who is affected:* the email worker only, for now.

(z) Decide later — *it waits; the rollout stays paused and the old queue keeps running*

Rec **(a)** · basis **partial** — *observed: the load test report; inferred: no worker relies on the old queue's ordering*
*Basis:* observed — load test, three times peak, no lost messages (link) · inferred — ordering not relied on (read 4 of the 6 workers' code) · unknown — the 2 workers not read

**63 — Vendor the web font or fetch it from the CDN?**
*While it waited (1 day): the CDN outage that prompted vendoring ended, and the provider published its fix. Recommendation changed from (a) vendor to (b) fetch, because the outage is over.*
**What:** ship the docs site's web font inside the repo (vendor), or load it from the font CDN (fetch).
**Why now:** the docs site build waits on it.
**Why ask:** 400 KB in the repo against a font that fails when the CDN does: a trade-off with no fact to settle it for you.
**Context:** you left it when the CDN outage blanked the docs site's font · you decide where the font comes from in future.
- (a) Vendor it — *adds 400 KB to the repo; the font still loads if the CDN goes down again*
- **(b) Fetch it** — *no growth in the repo; the font depends on the CDN*
- (z) Decide later — *it waits; the build stays on hold*

Rec **(b)** · basis **strong** — *checked the CDN's status history and loaded the font from it* · unknown: none

**61 — Turn on strict type checking across the repo?**
*While it waited (1 day): nothing changed.*
**What:** enable the type checker's strict mode for every package.
**Why now:** new code is being written against the loose setting, so each week adds more to fix later.
**Why ask:** it changes how everyone writes new code in the repo, not just this task.
**Context:** you left it at the review that flagged loose types in two packages · you decide whether the whole repo goes strict, not just those two.
- **(a) Turn it on** — *31 existing warnings to fix, about an hour of my time*
- (b) Leave it off — *no work now; the loosely typed code keeps growing*
- (z) Decide later — *it waits; the setting stays off*

Rec **(a)** · basis **strong** — *ran strict mode locally: 31 warnings, all in two packages* · unknown: none

- **62 Move the job queue to the new message broker?** — rec **(a) move all workers** · *reversible, wide — every worker service* · basis **partial** · *1 day old, blocks the worker rollout*
- **63 Vendor the web font or fetch it from the CDN?** — rec **(b) fetch it** · *reversible, narrow* · basis **strong** · *1 day old, blocks the docs site build* · *recommendation changed*
- **61 Turn on strict type checking across the repo?** — rec **(a) turn it on** · *reversible, narrow* · basis **strong** · *1 day old, blocks nothing*

*Reply with a letter (`62: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

---

## 21. Printed while you were away

*Situation: at 12:10 the agent raised decision 66 as a card in a status report. The operator
was at lunch. Background work finished at 12:40 and 13:05, and the agent wrote two more
reports. The operator has not taken a turn since 12:10, so 66 has not been seen: in the 13:05
report it is still a card, not a line ending (shown before).*

*When the operator replies at 13:30 about something else, 66 counts as seen from then; the next
report shows it as a line ending (shown before), unless something about it changed.*

---

## 22. Paging a cold re-show

*Situation: after a context reset, eight decisions are open; one is ⚠. The first group (three
decisions on the release) already makes three, so it and the ⚠ one are rendered in full; the
other four are lines. The heading says so.* *(Paging is provisional.)*

**Decisions** — *8 open · shown again after a context reset · 4 shown in full · one ⚠ one-way*

*…the three release cards and the ⚠ block, then the list, where the four held back read:*

- **71 Rename the internal metrics prefix?** — rec **(a) keep it** · *reversible, narrow* · basis **strong** · *2 days old, blocks nothing* *(expand for the card)*

---

## 23. Related decisions, each whole

*Situation: four decisions on the same command-line tool, 92 to 95, were shown as cards an
hour ago and the operator has replied since, so each is now a line ending (shown before).
They are one group and stay together in the list, but each keeps its own line and its own
recommendation.*

- **92 Rename the `sync` command to `pull`?** — rec **(a) rename it, keep `sync` as an alias** · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing* *(shown before)*
- **93 Drop the `--legacy` flag?** — rec **(b) keep it one more release** · *reversible, narrow* · basis **partial** · *1 h old, blocks nothing* *(shown before)*
- **94 Default log level: `info` or `warn`?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing* *(shown before)*
- **95 Move the config file under `~/.config`?** — rec **(a) move it, and read the old path too** · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing* *(shown before)*

*Not this: one entry for the four — "92–95 CLI cleanup: four small calls, see the cards
above" — which leaves no recommendation where the operator reads the list, so they cannot
answer from it.*

---

## 24. Decided alone, shown after — and a class on every ask

*Situation: the caller names classes of decision and keeps a store. Its rules let the agent
decide wording and narrowing alone; a trade-off is asked. Since its last report the agent
renamed a heading and left one part of the work for a filed follow-up, and it has one question.
Each thing decided alone was recorded in the store when the agent acted; the report renders
those records. The decisions block stays last.*

**Done alone** — *2 since my last report · say so in your own words to undo or reopen any*
- **Done: renamed the "Setup" heading to "Install" in the command-line guide, to match the other four guides** — *wording · two-way (one edit), nothing links to the heading · inside the task you gave me · undo: one edit*
- **Done: left the Windows install steps to a follow-up item, "Windows install steps"** — *narrowing · two-way (pull it back in any time), nobody waits on it · the class "narrowing", which your rules let me decide · undo: say "pull it back in"*

**85 — Ship the install script as one file or as a package?**
**What:** how users get the new install script: one file they download and run, or a package from the package manager.
**Why now:** the command-line guide's install section waits on it.
**Why ask:** *trade-off* — one file is quicker to get but never updates itself; a package updates but needs the package manager. Which your users would rather have is not a fact I have.
- **(a) One file** — *users download and run it; each new version is downloaded again by hand*
- (b) A package — *users install it with the package manager, and updates come with it; about a day to publish*
- (z) Decide later — *it waits; the install section says "coming soon"*

Rec **(a)** · basis **partial** — *observed: the other four tools ship one file; inferred: users are used to that* · unknown: how many users lack the package manager

*What the caller's store holds, one physical line each — a record line for each thing decided alone, and the ask's card line, indented under its headline, that carries its class. The exact lines are the caller's format; these are this invented caller's:*

```
decided: 2026-10-02T14:05Z wording — renamed the "Setup" heading to "Install" in the command-line guide, to match the other four guides; safe alone: one edit undoes it and nothing links to the heading · authority: task · reopen: one edit to the heading
decided: 2026-10-02T14:12Z narrowing — left the Windows install steps to the follow-up item "Windows install steps"; safe alone: it can be pulled back in any time and nobody waits on it · authority: class narrowing · reopen: say "pull it back in"
decision 85: Ship the install script as one file or as a package? — options: (a) one file [recommended] | (b) a package | (z) decide later
  raised: 2026-10-02T14:20Z
  what: how users get the new install script: one file, or a package from the package manager
  why now: the command-line guide's install section waits on it
  why ask: trade-off — one file never updates itself, a package needs the package manager; which users would rather have is not a fact the agent has
```

*The operator replies "put Setup back, and 85: a".*

*Read as: undo the "Install" rename.* The heading reads "Setup" again. 85 (a): the install section will point at the one file.

*"85: a" is an exact letter, so it gets no* Read as *line; the words beside it get theirs.*

*Had they replied "I'd rather decide the Windows split myself", it would be read as a reopen: a new numbered decision, naming the* Done *line it reopens, with its own card and* why ask.

*Not this: a report that says nothing of the rename and the split because neither was asked. What was decided alone is shown, once, where the operator already reads.*

---

## 25. A message with several replies

*Situation: decisions 61–63 were shown as a list: 61 the retry limit for the upload job, 62
keep the old export format or drop it, 63 which week to upgrade the database. The operator
answers all three in one message, with two questions mixed in: "61: b. 62 —
keep it, but why does it need its own test suite? 63 the week of the 14th is fine. And why is
the nightly build so slow lately?"*

*Read as: 62 → (a) keep the old export format.*
*Read as: 63 → (b) the upgrade in the week of the 14th.*
*Read as: a question of its own — why the nightly build got slow.*

**62, your question:** the old format has its own test suite because its dates are parsed by
separate code that the main suite never runs. Folding the two together is about an hour; I
filed it as a follow-up rather than doing it now.

**The nightly build, your question:** I don't know yet. It went from about 20 to about 35
minutes in the last week, starting the day the new integration tests landed; that is the
likely cause, not a confirmed one. Finding out is about an hour; I filed it as the item "slow
nightly build" and will bring back what I find.

Going ahead: the upload job retries three times, then alerts (61 (b)); the old export stays;
the upgrade is booked for the week of the 14th.

*61: b is an exact letter, so it gets no echo line. Not this: filing either follow-up with no
words — neither why the suite exists nor what is known about the slow build — or calling the
build question "a new request" and answering it with an item. The operator asked; an action is
not an answer. Nor one echo for 62 that leaves 63 and the build question without theirs.*
