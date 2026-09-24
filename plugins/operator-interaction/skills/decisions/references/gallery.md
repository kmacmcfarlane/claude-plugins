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
- **(a) Resume now** — *the snapshot finishes in about 15 minutes*
- **(b) Abort the backup** — *releases the lease; no backup tonight unless it is started again*
- **(z) Decide later** — *it waits; at 17:45 the lease lapses and the snapshot is lost*

Rec **(a)** · basis **strong** — *checked the storage quota: 40% free, enough to finish* · unknown: none

**43 — Remove the deprecated `/v1/export` endpoint?** ⚠ one-way
**What:** whether to delete the old export endpoint `/v1/export`, replaced last quarter by `/v2/export`.
**Why now:** the API cleanup release is cut on Thursday and waits on this.
**Context you may have lost:** two partner integrations still call `/v1/export`; once it is removed their exports fail until they move to `/v2`, and a removed public endpoint cannot quietly come back for the clients that already adapted.

**(a) Remove it now**
- *What happens:* the two partners' exports fail from Thursday until they switch.
- *Undo:* restoring it takes a hotfix release; the partners see an outage either way.
- *Who is affected:* the two partners, and their users.

**(b) Keep it, with a deprecation header and a sunset date**
- *What happens:* nothing breaks; every response carries a header announcing removal in 90 days.
- *Undo:* the header can be dropped at any time.
- *Who is affected:* nobody now; the old code stays for 90 more days.

**(c) Investigate first** — *about 15 minutes: read this month's access logs for other callers; could change the answer if both partners have already switched*

**(z) Decide later** — *it waits; the endpoint stays as it is, and the cleanup release goes out without this change*

Rec **(b)** · basis **partial** — *observed: this week's access log shows 2 partners calling it; inferred: no internal callers (only this repo searched)*
*Basis:* observed — access log, 2 partner callers this week (link) · inferred — no callers in this repo · unknown — whether the partners have a switch planned
*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*

**45 — Units on the storage dashboard: MiB or MB?** · *your preference — no recommendation*
**What:** show sizes in binary units (MiB, 1,048,576 bytes) or decimal units (MB, 1,000,000 bytes).
**Why now:** the new dashboard needs one; nothing else waits on it.
- **(a) MiB** — *matches what the operating system's tools report*
- **(b) MB** — *matches the storage provider's bill*
- **(z) Decide later** — *it waits; the dashboard keeps its placeholder units until you choose (one config line)*

*No recommendation: no fact settles this.* · basis **strong** — *checked: nothing reads the dashboard's units programmatically* · unknown: none

*Gallery note — layout and order: the cards and the block come first, the compact list and the hint last, so the list is what is on screen when the agent stops. Why this order: 41 breaks before you are back; the API cleanup group comes next because it holds a ⚠, with 44 kept beside 43; then 42, which blocks the docs build, before 45, which blocks nothing. 44 and 42 stay list lines: you are warm on both, both are two-way and narrow on a strong basis, 44's options converge and 42 is a template you have seen. 41, 43 and 45 are cold, so each is at least a card; 43 is a block because this is its first showing.*

- **41 Resume the paused nightly backup?** — rec **(a) resume** · *reversible, narrow* · basis **strong** · *25 min old, storage lease lapses ~17:45 (90 min from 16:15), blocks tonight's backup*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** · ⚠ one-way · basis **partial** · *6 h old, blocks the API cleanup release*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** · *reversible, narrow* · basis **strong** · *50 min old, blocks nothing* *(line only)*
- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *10 min old, blocks the docs build* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *3 h old, blocks nothing*

*Reply with a letter (`41: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

---

## 2. A warm, low-stakes card

*Situation: one decision, the operator watching live. The options diverge, so it is a card, not a line.*

**46 — Retry the failed preview deploy?**
**What:** the preview deploy of the search-page change failed while pulling its base image.
**Why now:** the design review this afternoon needs the preview.
- **(a) Retry now** — *about 4 minutes; the preview is up if it succeeds*
- **(b) Deploy yesterday's build instead** — *the review sees the old page*
- **(z) Decide later** — *it waits; no preview until someone deploys*

Rec **(a)** · basis **strong** — *the deploy log shows a registry timeout, not a build error* · unknown: none

---

## 3. One-way but narrow (no ⚠)

**47 — Delete last month's unused staging snapshot `stg-0814`?** · *one-way, narrow*
**What:** delete the staging database snapshot from August 14, which nothing restores from.
**Why now:** staging storage is at 85% of its quota.
- **(a) Delete it** — *frees 120 GB; the snapshot cannot be recovered afterwards*
- **(b) Keep it** — *storage stays at 85%; a later snapshot may fail when it fills*
- **(z) Decide later** — *it waits; storage keeps filling by about 2% a day*

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

## 5. A template

*Situation: a recurring decision whose options are fixed. The operator has seen this template
before and is warm; the stakes are low and the basis strong, so it may stay a line.*

- **48 Waive the review-round cap for the retry-policy change?** — rec **(a) one more round** · *template: review-round cap* · *reversible, narrow* · basis **strong** · *the reviewer's last finding is a one-line fix* · *(a) one more round · (b) ship as is · (c) park it · (z) decide later — it waits, unreviewed*

*The first time the operator meets this template in a session, it is shown as a full card.*

---

## 6. A preference

See decision 45 in example 1: the preference list line (label in the rec slot, stakes and
basis kept), then a card with options, their impacts, the label, and no recommendation.

---

## 7. Outside my authority

**78 — Allow a run the reviewer waived to ship to users?** · *no recommendation — outside my authority*
**What:** a report run passed with one check waived; shipping it puts the waived output in front of users.
**Why now:** the release is scheduled for Friday.
**Why no recommendation:** whether users may see output a reviewer waived is a product call, not mine.
- **(a) Ship it** — *users see the report on Friday, with the waived section as is*
- **(b) Hold it** — *the release slips until the check passes; about a day's work*
- **(c) Ship without the waived section** — *users get a shorter report; about an hour's work*
- **(z) Decide later** — *it waits; the release slips past Friday if undecided by Thursday noon*

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
- **(a) Fix the query first** — *about half a day; may make caching unnecessary*
- **(b) Add the cache now** — *faster reads this week; the slow query stays*
- **(z) Decide later** — *it waits; reads stay slow*

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
- **(a) "deprecated"** — *matches the three endpoints deprecated before*
- **(b) "scheduled for removal"** — *says more plainly that it will go; the only notice worded this way*
- **(z) Decide later** — *it waits; no notice is published until you choose*

Rec **(a)** · basis **strong** — *read the three earlier notices* · unknown: none

- **41 Resume the paused nightly backup?** — rec **(a) resume** · *reversible, narrow* · basis **strong** · *storage lease lapses ~17:45 (80 min from 16:25), blocks tonight's backup* *(shown before)*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** · ⚠ one-way · basis **partial** · *blocks the API cleanup release* *(shown before)*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** · *reversible, narrow* · basis **strong** · *1 h old, blocks nothing*
- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *blocks the docs build* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* · *reversible, narrow* · basis **strong** · *blocks nothing* *(shown before)*

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

- **Done: fixed a broken link in the contributing guide, on my task branch** — *two-way (one revert), nobody else uses the branch; inside the task you gave me.*

*Not a decision: no number, no options, no hint. Never used for anything one-way or relied on by others.*

---

## 19. A status-quo default

**56 — Open the pull request now, or wait for the benchmark run?**
**What:** the retry-policy change is ready; its benchmark run finishes in about 25 minutes.
**Why now:** you asked for the change today.
- **(a) Open it now** — *reviewers start today; the benchmark result arrives mid-review*
- **(b) Wait for the benchmark** — *about 25 minutes*
- **(z) Decide later** — *it waits*

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
while it waited — not composed again.*

**Decisions** — *3, raised yesterday · shown again after a context reset*

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new message broker?
*While it waited (1 day): the load test finished — the new broker held three times peak load with no lost messages. Options and recommendation unchanged.*
**What:** switch every worker service from the old job queue to the new message broker.
**Why now:** the worker rollout waits on it.
**Context you may have lost:** the switch is a config change in each service; the old queue keeps running for a week as a fallback.

**(a) Move all workers now**
- *What happens:* every worker service reads from the new broker from today.
- *Undo:* switch each service's config back within the week; after that the old queue is gone.
- *Who is affected:* every worker service, and whoever is on call for them.

**(b) Move one service first**
- *What happens:* the email worker moves today; the rest follow in two days if it stays quiet.
- *Undo:* one config change.
- *Who is affected:* the email worker only, for now.

**(z) Decide later** — *it waits; the rollout stays paused and the old queue keeps running*

Rec **(a)** · basis **partial** — *observed: the load test report; inferred: no worker relies on the old queue's ordering*
*Basis:* observed — load test, three times peak, no lost messages (link) · inferred — ordering not relied on (read 4 of the 6 workers' code) · unknown — the 2 workers not read

**63 — Vendor the web font or fetch it from the CDN?**
*While it waited (1 day): the CDN outage that prompted vendoring ended, and the provider published its fix. Recommendation changed from (a) vendor to (b) fetch, because the outage is over.*
**What:** ship the docs site's web font inside the repo (vendor), or load it from the font CDN (fetch).
**Why now:** the docs site build waits on it.
- **(a) Vendor it** — *adds 400 KB to the repo; the font still loads if the CDN goes down again*
- **(b) Fetch it** — *no growth in the repo; the font depends on the CDN*
- **(z) Decide later** — *it waits; the build stays on hold*

Rec **(b)** · basis **strong** — *checked the CDN's status history and loaded the font from it* · unknown: none

**61 — Turn on strict type checking across the repo?**
*While it waited (1 day): nothing changed.*
**What:** enable the type checker's strict mode for every package.
**Why now:** new code is being written against the loose setting, so each week adds more to fix later.
- **(a) Turn it on** — *31 existing warnings to fix, about an hour of my time*
- **(b) Leave it off** — *no work now; the loosely typed code keeps growing*
- **(z) Decide later** — *it waits; the setting stays off*

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
decisions on the release) and the ⚠ one are rendered in full; the other four are lines. The
heading says so.* *(Paging is provisional.)*

**Decisions** — *8 open · 4 shown in full · one ⚠ one-way*

*…the three release cards and the ⚠ block, then the list, where the four held back read:*

- **71 Rename the internal metrics prefix?** — rec **(a) keep it** · *reversible, narrow* · basis **strong** · *2 days old, blocks nothing* *(expand for the card)*
