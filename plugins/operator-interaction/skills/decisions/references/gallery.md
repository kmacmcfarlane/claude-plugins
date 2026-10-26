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
**Context:** the snapshot is the backup's copy of the database, written to shared storage; the storage lease is the backup's hold on that space, and it lapses at 17:45. You last saw the backup running normally last night · you decide whether it finishes tonight or starts again.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: at 17:45 the lease lapses, the snapshot is lost and the backup starts over (about 3 hours) · reach: tonight's backup, and shared storage the reporting team writes to · ⚠ undo: (b) start the backup again, about 3 hours
- **(a) Resume now**
  *→ the snapshot finishes in about 15 minutes · reach: shared storage, 40% free*
  *pros: the backup completes tonight, with no restart*
  *cons: shared storage stays tight, 40% free, while it finishes*
- (b) Abort the backup
  *→ releases the lease; no backup tonight unless it is started again · reach: tonight's backup only · ⚠ undo: start it again, about 3 hours*
  *pros: the lease and its storage are freed at once*
  *cons: no backup tonight, and a restart costs about 3 hours*
- (z) Decide later — *it waits; at 17:45 the lease lapses and the snapshot is lost*

▸ Background — why now: the storage lease lapses at ~17:45 (90 min from 16:15), and the snapshot is lost with it.

**43 — Remove the deprecated `/v1/export` endpoint?** ⚠ one-way
**What:** whether to delete the old export endpoint `/v1/export`, replaced last quarter by `/v2/export`.
**Context:**
- The API cleanup release is the batch of API changes cut on Thursday; you left it at last quarter's launch of `/v2/export` · you decide whether `/v1` goes in this release
- Two partner integrations still call `/v1/export`
  - their exports fail once it is removed, until they move to `/v2`
- A removed public endpoint cannot quietly come back for the clients that already adapted

▾ Open questions — 1 open: whether the two partners have a switch to `/v2` planned
- whether the two partners have a switch to `/v2` planned

▾ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Basis:** partial — *observed: this week's access log shows 2 partners calling it; inferred: no internal callers (only this repo searched)*
*Evidence:* observed — access log, 2 partner callers this week (link) · inferred — no callers in this repo
- **No internal service calls `/v1/export`.**
  *tripwire:* a call from inside the company shows up in this month's access log
- **Each partner can move to `/v2` within the 90 days.**
  *tripwire:* a partner says its next release is more than 90 days away

**Impact:** later: the cleanup release goes out without this change · reach: the two partners and their users · ⚠ undo: (a) a hotfix restores the endpoint, not the partners' outage

| Impact | Effect | Reach | Undo | Cost |
|---|---|---|---|---|
| (a) Remove it now | the two partners' exports fail from Thursday until they switch | the two partners, and their users | ⚠ a hotfix release restores it; the partners see an outage either way | about an hour |
| **(b) Keep it, with a deprecation header and a sunset date** | nothing breaks; every response announces removal in 90 days | nobody now; the old code stays 90 more days | — | about an hour |
| (c) Investigate first | reads this month's access logs for other callers; could change the answer if both partners have already switched | — | — | about 15 minutes |
| (z) Wait | the endpoint stays as it is, and the cleanup release goes out without this change | the API cleanup release | — | nothing now |

**(a) Remove it now**
*plan in brief:* the `/v1/export` route and its handler are deleted in Thursday's API cleanup release. From then on a call to it gets not found, so the two partners' exports fail until each moves to `/v2/export`.

| Pros | Cons |
|---|---|
| The old endpoint's code and tests go this week | The two partners' exports fail from Thursday until they switch |
| Nothing old is left to maintain or patch | A hotfix brings it back, but not the outage the partners already had |

**(b) Keep it, with a deprecation header and a sunset date**
*plan in brief:* every `/v1/export` response gains a deprecation header naming a sunset date 90 days out, and the release notes say the same. The endpoint is removed after that date, once the partners have had their 90 days.

| Pros | Cons |
|---|---|
| Nothing breaks on Thursday | The old code stays 90 more days |
| Each partner gets a dated warning in every response | The removal comes back as a second change after the sunset date |

**(c) Investigate first**
*plan in brief:* I read this month's access logs for every caller of `/v1/export`, about 15 minutes, and bring 43 back with what they show. Both partners having switched already would change the answer.

| Pros | Cons |
|---|---|
| Settles whether anyone but the two partners still calls it | The answer waits about 15 minutes |

**(z) Wait**
*plan in brief:* nothing changes now: the endpoint stays, and the cleanup release goes out without this change.

| Pros | Cons |
|---|---|
| | This change waits for the next cleanup release |

▾ Background — why now: the API cleanup release is cut on Thursday; this change goes out in it, or waits for the next one.
**Why now:** the API cleanup release is cut on Thursday; this change goes out in it, or waits for the next one.
**Why ask:** removing it breaks two partners and cannot be quietly undone; that call is not mine to take alone.

*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*

**45 — Units on the storage dashboard: MiB or MB?** · *your preference — no recommendation*
**What:** show sizes in binary units (MiB, 1,048,576 bytes) or decimal units (MB, 1,000,000 bytes).
**Context:** the operating system's tools count in binary units and the storage provider bills in decimal ones, so the same disk reads about 5% apart in the two. You left it at the dashboard mock-up, which had placeholder units · you decide which units it shows.
▸ Assumptions — basis: **strong**
**Impact:** later: the dashboard keeps its placeholder units · reach: the dashboard's readers
- (a) MiB
  *→ sizes match what the operating system's tools report*
  *pros: sizes agree with what the operating system's tools show*
  *cons: the dashboard and the bill differ by about 5%*
- (b) MB
  *→ sizes match the storage provider's bill*
  *pros: sizes agree with the storage provider's bill*
  *cons: sizes read about 5% above the operating system's tools*
- (z) Decide later — *it waits; the dashboard keeps its placeholder units until you choose (one config line)*

▸ Background — why now: the new dashboard needs one unit before it ships.

*Gallery note — layout and order: the cards and the block come first, each opening on its decision line (the title and What), then its Context, then its impact (a line on a card; on the block, the line and then a table), the compact list and the hint last, so the list is what is on screen when the agent stops. Why this order: 41 breaks before you are back; the API cleanup group comes next because it holds a ⚠, with 44 kept beside 43; then 42, which blocks the docs build, before 45, which blocks nothing. 44 and 42 stay list lines: you are warm on both, both are two-way and narrow on a strong basis, 44's options converge and 42 is a template you have seen. 41, 43 and 45 are cold, so each is at least a card; 43 is a block because this is its first showing. Each card and the block carries its Context — the terms it uses, then where you left it — and would carry it for a warm reader too; the block's runs to bullets, its first the card-size Context and the rest what a reader coming back may have lost. The list lines carry none. In each card and the block the options keep their letter order and only the recommended one is bold: 43's (b) stays second, and 45, with no recommendation, bolds none. No Impact line carries an effect: each starts at what waiting costs, and on a card each option carries its own effect, reach and cost on the italic line under it, a facet that does not apply left out; on the block the table's rows carry them. 43's block shows what is still open, whether the partners plan to switch, as an open ▾ Open questions fold above its Impact; 41 and 45 have nothing open, so they have no fold. Every card and the block then carry their ▸ Assumptions line just above the Impact: the basis word, and how many assumptions the recommendation rests on, each with its tripwire; 45, with no recommendation, names none, so its line is the basis alone; the block shows the fold open, its Basis line, its evidence and each assumption with its tripwire. No card ends on a Rec line: the bold option is the recommendation, and what is not known is never an assumption. Undo shows only where it bites: 41's (b), whose restart costs about 3 hours, and 43's (a), which no hotfix fully takes back, each marked ⚠ on its option and on the Impact line; 45's options, each one config line from the other, carry none, and on the block 43's reversible rows read `—`. On each card, why now and why ask sit in a closed ▸ Background fold, the first under the options, its summary the first sentence of why now, so the card reads the choices first; the block shows the fold open (▾), its two lines under its table and its options' views. Under 43's table, each option's view in letter order, (z) too: its title, its *plan in brief:* line, then its `Pros | Cons` table, the points in full; the facets stay in the table's row above, so the view does not repeat them, and (z), with no upside, leaves its Pros cell empty. Every list line carries an effect and what waiting costs, the line-only ones too: the recommended option's after its label, and 45's each option's, since it has no recommendation; no list line carries an option's reach, undo or cost; only 43 has a ⚠ slot, and no line has a stakes word.*

- **41 Resume the paused nightly backup?** — rec **(a) resume** → *the snapshot finishes in about 15 minutes* · *later: the snapshot is lost at 17:45 and the backup starts over* · basis **strong** · *25 min old, storage lease lapses ~17:45 (90 min from 16:15)*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** → *nothing breaks; every response announces removal in 90 days* · *later: misses Thursday's API cleanup release* · ⚠ one-way · basis **partial** · *6 h old*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** → *the notice matches the three before it* · *later: no notice published until you choose* · basis **strong** · *why ask: partners read it, and (b) warns them more plainly* · *50 min old* *(line only)*
- **42 Clear the docs build cache?** — rec **(a) clear it** → *the docs build runs again* · *later: the docs build stays blocked* · *template: cache reset* · basis **strong** · *why ask: clearing it drops the other branch's cached build too* · *10 min old* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* → *(a) sizes match the OS tools; (b) sizes match the bill* · *later: placeholder units stay* · basis **strong** · *3 h old*

*Reply with a letter (`41: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

---

## 2. A warm, low-stakes card

*Situation: one decision, the operator watching live. The options diverge, so it is a card, not a line.*

**46 — Retry the failed preview deploy?**
**What:** the preview deploy of the search-page change failed while pulling its base image.
**Context:** the preview is a test copy of the site with the search-page change in it; the base image is the ready-made system it is built on, pulled from a registry. You asked for the preview this morning · you decide whether to retry it or show yesterday's build.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: no preview for this afternoon's design review · reach: the preview site only
- **(a) Retry now**
  *→ the preview shows the change in about 4 minutes if it succeeds; if it fails, no preview yet · cost: about 4 minutes*
  *pros: the design review sees the change itself*
  *cons: if the registry is still slow, 4 minutes go and there is no preview*
- (b) Deploy yesterday's build instead
  *→ the preview shows the old page, without the search-page change*
  *pros: a preview is certain within minutes*
  *cons: the design review sees the old page, not the change*
- (z) Decide later — *it waits; no preview until someone deploys*

▸ Background — why now: the design review is this afternoon, and it needs a preview.

*Gallery note — pros and cons: under each option's impact line sit its `*pros:*` and `*cons:*` lines, labelled as its facets are, one line each: what the option gains, and what it costs or risks. The recommended (a) gives its con too, since a recommendation with no downside is not weighed; (b)'s con is its own cost, not "(a) is better". (z) stays one line and carries neither, here and on the answer page. On the answer page the same two lines are each option's **Pros** and **Cons** rows, laid out as its Effect and Reach.*

---

## 3. One-way but narrow (no ⚠)

**47 — Delete last month's unused staging snapshot `stg-0814`?**
**What:** delete the staging database snapshot from August 14, which nothing restores from.
**Context:** staging is the test copy of the live system; `stg-0814` is a full copy of its database taken on August 14 for a migration test that has finished. Raised when the staging storage alert turned it up · you decide whether it goes.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: storage keeps filling, about 2% a day · reach: staging only; nothing restores from it · ⚠ undo: (a) none — a deleted snapshot cannot be recovered
- **(a) Delete it**
  *→ frees 120 GB of staging storage · reach: staging only · ⚠ undo: none, it cannot be recovered*
  *pros: frees 120 GB, so staging stops nearing its quota*
  *cons: the snapshot is gone for good, should anyone need it*
- (b) Keep it
  *→ storage stays at 85%; a later snapshot may fail when it fills*
  *pros: the snapshot stays, should the migration test need running again*
  *cons: storage keeps filling, and a later snapshot may fail*
- (z) Decide later — *it waits; storage keeps filling by about 2% a day*

▸ Background — why now: staging storage is at 85% of its quota and fills about 2% a day.

*No ⚠ label on the decision: (a)'s `⚠ undo:` and the Impact line's say it is one-way, and the narrow reach says why the decision is not ⚠ one-way. The marker is on the option, never the decision. (b), which deleting later undoes, carries no undo at all: an option shown without one is reversible at little cost.*

---

## 4. The read-back — only for a one-way option

*Situation: decision 43 from example 1. The operator replies "43: a, remove it". Option (a)'s
Undo cell carries ⚠ and says the partners see an outage either way: it cannot be taken back.*

*Read as: 43 → (a) remove `/v1/export` on Thursday. That can't be undone for the two partners who break — confirm and I'll go ahead, or change it.*

*The operator replies "go".*

*Confirmed. Removing it in the Thursday release; I'll say when it is out.*

*Situation: instead the operator replies "43: b, keep it with a sunset date". Option (b) can be
undone at any time, so it is echoed and acted on — no confirmation round.*

*Read as: 43 → (b) keep `/v1/export`, with a deprecation header and a 90-day sunset date. Going ahead — the header can be dropped at any time.*

---

## 5. An ask for another round (a template)

*Situation: the retry-policy change has spent its budget — the dollar amount set for its
build when the build began, inside which review rounds run without asking — and the last
review left one medium finding open. Reaching the budget is the cap the operator set — a
caller may let it pass while quota is plentiful, and here it is not — so the next round is
asked for. The budget cap is a template: its options are fixed — (a) raise the budget, its
new total filled in each time — so they ride by reference once the operator has seen it.
Its justification never does, because what is left, what has been spent and what a round
costs change every time. The first time in a session, a card:*

**48 — Raise the retry-policy change's budget for another round?** · *template: budget cap*
**What:** the change has spent $21 of its $20 budget over four reviews; the last review left one finding open, so it cannot land as it is.
**Context:** the retry-policy change sets how often a failed job is tried again; its budget is the spend its build may use before rounds stop and come back to you. You left it when you asked for the change · you decide whether it gets more.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the change stays unmerged · reach: every job the scheduler retries · cost: (a) up to $9 more, about two rounds
- **(a) Raise to $30, about two rounds here**
  *→ the counter is saved with the job, so a failing job stops after five tries even across a restart · cost: about $4 a round, up to $9 more*
  *pros: the restart bug is fixed before the change ships*
  *cons: up to $9 more, and the change lands a round later*
- (b) Ship as is
  *→ it lands now; after a restart the counter starts from zero, so a job that fails on every run is retried forever · reach: every job that fails on every run*
  *pros: it lands now, with no more spend*
  *cons: a job that fails on every run is retried forever after a restart*
- (c) Park it
  *→ the retry policy stays as it is until someone takes the change up*
  *pros: no spend and no risk now*
  *cons: the retry policy keeps its flaws until someone takes it up*
- (z) Decide later — *it waits, unmerged; nothing lands*

**If left:** *one medium finding: after a restart the retry counter starts again from zero, so a job that fails on every run is retried forever instead of stopping after five tries. The review names the cause but not the fix: the count has to be saved with the job.*
**A round costs:** *spent $21 of $20, about 4% of a week's quota; the weekly quota is 62% used, not below the reserve. The next round costs about $4 and 20 minutes; open findings ran 5 → 2 → 1 over the last three reviews. One more answer from you if that round does not clear it.*
▸ Background — why now: the change is blocked until you answer.

*Later in the session the operator is warm and has seen the template, so a new ask on it,
low-stakes on a strong basis, may stay a line — the options by reference, the justification
still on it:*

- **49 Raise the search-index change's budget for another round?** — rec **(a) raise to $16, about two rounds** → *a deleted page leaves search results at once, if the fix clears* · *later: the change stays unmerged* · *template: budget cap* · basis **strong** · *if left: a deleted page stays in search results until the nightly rebuild · a round: spent $12 of $12, ~$2, ~10 min and ~0.5% of a week's quota a round, weekly 58% used, open findings 3 → 1, one more answer from you* · *10 min old* · **(a) raise the budget** · (b) ship as is · (c) park it · (z) decide later — *it waits, unmerged*

*Not this: "Raise the budget? — rec (a) raise it" with nothing about what is left, what has
been spent or what the round costs. The operator cannot weigh an impact they are not shown.*

---

## 6. A preference

See decision 45 in example 1: the preference list line (label in the rec slot, each option's
effect in the effect slot, wait and basis kept), then a card with its Context, its Impact
line (no effect), options, their impacts, the label, and no recommendation.

---

## 7. Outside my authority

**78 — Allow a run the reviewer waived to ship to users?** · *no recommendation — outside my authority*
**What:** a report run passed with one check waived; shipping it puts the waived output in front of users.
**Context:** a waived check is one a reviewer let through without it passing; here it covers the report's regional totals, the waived section. Raised when the release checklist turned it up · you decide whether that section reaches users on Friday.
▸ Open questions — 1 open: how users use the waived section of the report
▸ Assumptions — basis: **partial**
**Impact:** later: the release slips past Friday if undecided by Thursday noon · reach: every user of the report · ⚠ undo: (a) a follow-up release removes the section, after users have seen it
- (a) Ship it
  *→ users see the report on Friday, with the waived section as is · reach: every user of the report · ⚠ undo: a follow-up release, after users have seen it*
  *pros: users get the report on Friday, as planned*
  *cons: users read the waived section unchecked; a fix reaches them only after*
- (b) Hold it
  *→ the report reaches users once the check passes, about a day later · cost: about a day's work*
  *pros: users get only a checked report*
  *cons: the report reaches users about a day late*
- (c) Ship without the waived section
  *→ users get a shorter report · reach: every user of the report · cost: about an hour's work*
  *pros: users get it on Friday, with nothing unchecked in it*
  *cons: users miss the waived section, and it costs about an hour*
- (z) Decide later — *it waits; the release slips past Friday if undecided by Thursday noon*

▸ Background — why now: the release is Friday, and it slips if this is undecided by Thursday noon.

---

## 8. A time-critical alert

**Alert: the staging certificate expires in 10 minutes.** Staging goes dark for everyone when it does. *Options follow as soon as I have them.*

*Not a decision yet, so no Impact line; the fact it states is the impact. The decision that follows carries one.*

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
**Context:** the product-listing query is the database query behind the listing page; a cache would keep its answers and serve repeat reads, and an index is the database's lookup table that can make the query itself fast. You left it at which caching library to adopt (79) · you decide whether to cache at all.
▸ Open questions — 1 open: the listing's write load, which sets how often a cache goes stale
▸ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Impact:** later: the listing page stays slow · reach: the listing page and its readers
- **(a) Fix the query first**
  *→ an index lets the database find the listed products without reading every row; the page may load fast with no cache · cost: about half a day*
  *pros: the page may be fast with no cache to keep fresh*
  *cons: about half a day before anything is faster*
- (b) Add the cache now
  *→ repeat reads are fast this week; the first read of each listing, and every read after a change, still takes about 2 seconds*
  *pros: repeat reads are fast this week*
  *cons: the slow query stays, and first reads still take about 2 seconds*
- (z) Decide later — *it waits; reads stay slow*

▸ Background — why now: the listing page loads in about 2 seconds, and the performance review is next week.

*Not this: numbering it 79b, which reads as option (b) of 79. A new decision takes the next
plain number; a follow-up that hangs on 81 says so in words ("only if 81 is (a)").*

---

## 11. `tell me`

*Situation: decision 46 from example 2, shown just above. The operator replies "46: tell me
what timed out". Only what the fact changes is sent; the card is one scroll up.*

*Read as: 46 → tell me (what timed out).*

**46 — Added:** pulling the base image from the container registry timed out after 5 minutes; the registry's status page showed degraded service then and shows normal now.
*Recommendation (a) unchanged · impact unchanged · basis unchanged, strong: the registry reports normal service again.*

*Then the operator asks for an option's view: "46: tell me (b)". Its plan in brief, its pros and cons in full, then its facet line, in that order; the card does not change, so there is no **Added:** line.*

*Read as: 46 → tell me (b), its view.*

**46 (b) — Deploy yesterday's build instead**
*plan in brief:* I deploy yesterday's preview build again, the one without the search-page change; it needs no new pull from the registry. The preview is up within minutes, showing the old search page.

| Pros | Cons |
|---|---|
| A preview is certain within minutes | The design review sees the old page, not the change |
| No wait on the slow registry | The search-page change still needs its own preview later |

*→ the preview shows the old page, without the search-page change*

---

## 12. `expand`

*Situation: example 1's message was shown and the operator has replied since, so 41, 43 and 45
were seen. They reply "expand 44". The next message renders 44 at its new level (a card), then
the list: 41, 43 and 45 are unchanged, so they are not rendered again and their lines say so.
43 keeps its ⚠ label; `expand` brings its block back. 42 is still a line.*

**Decisions** — *5 · one ⚠ one-way*

**44 — Deprecation notice: "deprecated" or "scheduled for removal"?**
**What:** the wording of the notice in the `/v1/export` response header and in the release notes.
**Context:** the notice is the warning partners read before an endpoint goes; the three before it, on older endpoints, all said "deprecated". You left it at the wording we talked over an hour ago · you decide which word this one uses.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: no notice is published until you choose · reach: the two partners still on `/v1`, through the header and the release notes
- **(a) "deprecated"**
  *→ the notice matches the three before it*
  *pros: the notice reads like the three before it*
  *cons: it says less plainly that the endpoint will go*
- (b) "scheduled for removal"
  *→ says more plainly that it will go; the only notice worded this way*
  *pros: partners read plainly that the endpoint will go*
  *cons: the only notice worded unlike the rest*
- (z) Decide later — *it waits; no notice is published until you choose*

▸ Background — why now: the notice goes out with the API cleanup release on Thursday.

- **41 Resume the paused nightly backup?** — rec **(a) resume** → *the snapshot finishes in about 15 minutes* · *later: the snapshot is lost at 17:45 and the backup starts over* · basis **strong** · *35 min old, storage lease lapses ~17:45 (80 min from 16:25)* *(shown before)*
- **43 Remove the deprecated `/v1/export` endpoint?** — rec **(b) keep it, with a sunset date** → *nothing breaks; every response announces removal in 90 days* · *later: misses Thursday's API cleanup release* · ⚠ one-way · basis **partial** · *6 h old* *(shown before)*
- **44 Deprecation notice: "deprecated" or "scheduled for removal"?** — rec **(a) "deprecated"** → *the notice matches the three before it* · *later: no notice published until you choose* · basis **strong** · *1 h old*
- **42 Clear the docs build cache?** — rec **(a) clear it** → *the docs build runs again* · *later: the docs build stays blocked* · *template: cache reset* · basis **strong** · *why ask: clearing it drops the other branch's cached build too* · *20 min old* *(line only)*
- **45 Units on the storage dashboard: MiB or MB?** — *your preference, no rec* → *(a) sizes match the OS tools; (b) sizes match the bill* · *later: placeholder units stay* · basis **strong** · *3 h old* *(shown before)*

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
*Recommendation unchanged: (b) keep it with a sunset date — one partner would still break. Impact changed: (a) now breaks one partner, not two.*
*…followed by the block, as in example 1, with the new fact in its Assumptions fold.*

---

## 14. `later`, with and without a when

*Situation: the operator replies "46: later, after the standup".*

*Read as: 46 → later (after the standup, about 10:30). The preview waits until then.*

*At 10:30:*

**46 — back, as you asked ("after the standup"):** retry the failed preview deploy?
*While it waited (1 h): the registry is healthy again, and the design review moved to 14:00. Options and recommendation unchanged; impact changed: waiting now costs the 14:00 review its preview.*
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

- **54 Drop the `legacy_score` column from the shared analytics table?** — rec **(b) keep it, stop writing to it** → *both dashboards keep working; the column goes stale* · *later: the schema cleanup stays blocked* · ⚠ one-way · basis **partial** · *2 h old*
- **55 Theme for the internal status page: light or dark?** — *your preference, no rec* → *(a) light, as today; (b) dark, like the other tools* · *later: it stays light* · basis **strong** · *2 h old*

*…and the hint, last.*

---

## 18. FYI after acting

- **Done: fixed a broken link in the contributing guide, on my task branch** — *two-way, nobody else uses the branch · inside the task you gave me · undo: one revert*

*Not a decision: no number, no options, no hint. Never used for anything one-way or relied on by others. A single line needs no heading; several go under* **Done alone** *(example 24).*

---

## 19. A status-quo default

**56 — Open the pull request now, or wait for the benchmark run?**
**What:** the retry-policy change is ready; its benchmark run finishes in about 25 minutes.
**Context:** the retry-policy change sets how often a failed job is tried again; the benchmark run times it against the current code. You asked for it today and have not seen it since · you decide whether the reviewers start now or after the benchmark.
▸ Open questions — 1 open: whether the benchmark shows a slowdown in retrying jobs
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the branch stays unopened; nothing is lost · reach: every job the scheduler retries
- (a) Open it now
  *→ a slowdown the benchmark would show could be approved before the result arrives · reach: every job the scheduler retries*
  *pros: review starts about 25 minutes sooner*
  *cons: a slowdown could be approved before the benchmark shows it*
- **(b) Wait for the benchmark**
  *→ the change merges only with its speed known · cost: about 25 minutes*
  *pros: the change is reviewed with its speed known*
  *cons: the pull request opens about 25 minutes later*
- (z) Decide later — *it waits*

**If unanswered:** *I leave the branch as it is, unopened, and carry on with the next task. Nothing is lost.*
▸ Background — why now: nothing forces it; the benchmark finishes in about 25 minutes.

---

## 20. Re-showing decisions after a context reset

*Situation: three decisions were raised yesterday; since then the context was reset, so the
operator is cold and every decision is shown as a card or a block. 62 was deferred "until the
load test finishes", and it has finished. 63's recommendation rested on a CDN outage that has
since ended. Nothing changed for 61. None has a deadline and none is ⚠, so they go by waiting
cost: 62 blocks the worker rollout, 63 blocks the docs site build, 61 blocks nothing. 62 is
wide and the reader is cold, so it is a block (with no read-back: it is not ⚠). The store kept
each card with its raised-at time, so each is rendered from the stored card, plus what changed
while it waited — not composed again. Each stored card holds the Context written when it
was raised, so under *while it waited* each card runs its What, that Context and its Impact
line, and 62's block its What, its Context as bullets (the stored card-size Context first),
its open question as an open ▾ Open questions fold, its Impact line and its table; *while it
waited* says whether the impact changed.*

**Decisions** — *3 open · shown again after a context reset*

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new message broker?
*While it waited (1 day): the load test finished — the new broker held three times peak load with no lost messages. Options and recommendation unchanged; impact unchanged.*
**What:** switch every worker service from the old job queue to the new message broker.
**Context:**
- The new broker has carried the email worker alone for two weeks as a trial; you left it at that trial · you decide whether every worker moves now or one goes first
- The switch is a config change in each service
- The old queue keeps running for a week as a fallback
  - after that week it is shut down

▾ Open questions — 1 open: whether the two workers not read rely on the old queue's ordering
- whether the two workers not read rely on the old queue's ordering

▾ Assumptions — basis: **partial** · 1 assumption with its tripwire
**Basis:** partial — *observed: the load test report; inferred: no worker relies on the old queue's ordering*
*Evidence:* observed — load test, three times peak, no lost messages (link) · inferred — ordering not relied on (read 4 of the 6 workers' code)
- **No worker relies on the old queue delivering jobs in order.**
  *tripwire:* a worker's tests fail on jobs that arrive out of order on the new broker

**Impact:** later: the worker rollout stays paused · reach: every worker service and its on-call · ⚠ undo: (a) switch each config back within the week; after that the old queue is gone

| Impact | Effect | Reach | Undo | Cost |
|---|---|---|---|---|
| **(a) Move all workers now** | every worker reads from the new broker today | every worker service, and whoever is on call for them | ⚠ switch each service's config back within the week; after that the old queue is gone | about an hour of config changes |
| (b) Move one service first | the email worker moves today; the rest follow in two days if it stays quiet | the email worker only, for now | — | two more days before the rollout finishes |
| (z) Wait | the rollout stays paused and the old queue keeps running | the worker rollout | — | the old queue's upkeep |

**(a) Move all workers now**
*plan in brief:* each worker service's config switches to the new message broker today, about an hour of changes. The old queue runs a week more as a fallback, then is shut down.

| Pros | Cons |
|---|---|
| The rollout finishes today | Every worker moves at once, so a problem reaches them all |
| The old queue is still there for a week to fall back to | After the week, switching back means bringing the old queue up again |

**(b) Move one service first**
*plan in brief:* the email worker moves to the new broker today; the other services follow in two days if it stays quiet. The old queue keeps running until the last one moves.

| Pros | Cons |
|---|---|
| A problem shows on one service before it reaches the rest | The rollout takes two more days |
| | The old queue runs, and needs upkeep, two days longer |

**(z) Wait**
*plan in brief:* nothing moves: the rollout stays paused and the old queue keeps running.

| Pros | Cons |
|---|---|
| | The worker rollout stays paused |

▾ Background — why now: the worker rollout waits on it.
**Why now:** the worker rollout waits on it.
**Why ask:** every worker service moves at once; how fast the rollout goes is yours to set.

**63 — Vendor the web font or fetch it from the CDN?**
*While it waited (1 day): the CDN outage that prompted vendoring ended, and the provider published its fix. Recommendation changed from (a) vendor to (b) fetch, because the outage is over; impact unchanged: each option does what it did.*
**What:** ship the docs site's web font inside the repo (vendor), or load it from the font CDN (fetch).
**Context:** the font CDN is the font provider's download service, which each page fetches from; vendoring keeps a 400 KB copy of the font in the repo instead. You left it when the CDN outage blanked the docs site's font · you decide where the font comes from in future.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the docs site build stays on hold · reach: the docs site's readers
- (a) Vendor it
  *→ adds 400 KB to the repo; the font still loads if the CDN goes down again*
  *pros: the font loads even when the CDN is down*
  *cons: 400 KB more in the repo, and font updates by hand*
- **(b) Fetch it**
  *→ no growth in the repo; when the CDN is down, pages fall back to a system font · reach: the docs site's readers, whenever the CDN is down*
  *pros: the repo stays small, and the CDN keeps the font current*
  *cons: pages show a system font whenever the CDN is down*
- (z) Decide later — *it waits; the build stays on hold*

▸ Background — why now: the docs site build is on hold until the font's source is settled.

**61 — Turn on strict type checking across the repo?**
*While it waited (1 day): nothing changed; impact unchanged.*
**What:** enable the type checker's strict mode for every package.
**Context:** strict mode is the type checker's setting that refuses loosely typed code; the 31 warnings are what it flags today, all in the two packages the review named. You left it at the review that flagged loose types in two packages · you decide whether the whole repo goes strict, not just those two.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: loosely typed code keeps growing · reach: everyone writing code in the repo
- **(a) Turn it on**
  *→ 31 warnings fixed, strict checks from now on · reach: everyone writing code here · cost: about an hour of my time*
  *pros: type errors are caught before they merge*
  *cons: about an hour now, and stricter checks on every change after*
- (b) Leave it off
  *→ no work now; the loosely typed code keeps growing*
  *pros: no work and no new checks now*
  *cons: the loosely typed code keeps growing, and so does the later fix*
- (z) Decide later — *it waits; the setting stays off*

▸ Background — why now: each week on the loose setting adds more loosely typed code to fix.

- **62 Move the job queue to the new message broker?** — rec **(a) move all workers** → *every worker reads from the new broker today* · *later: the worker rollout stays paused* · basis **partial** · *1 day old*
- **63 Vendor the web font or fetch it from the CDN?** — rec **(b) fetch it** → *no growth in the repo; the font depends on the CDN* · *later: the docs site build stays on hold* · basis **strong** · *1 day old* · *recommendation changed*
- **61 Turn on strict type checking across the repo?** — rec **(a) turn it on** → *31 warnings fixed, strict checks from now on* · *later: loosely typed code keeps growing* · basis **strong** · *1 day old*

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

- **71 Rename the internal metrics prefix?** — rec **(a) keep it** → *dashboards and alerts keep their metric names* · *later: nothing waits on it* · basis **strong** · *2 days old* *(expand for the card)*

---

## 23. Related decisions, each whole

*Situation: four decisions on the same command-line tool, 92 to 95, were shown as cards an
hour ago and the operator has replied since, so each is now a line ending (shown before).
They are one group and stay together in the list, but each keeps its own line and its own
recommendation.*

- **92 Rename the `sync` command to `pull`?** — rec **(a) rename it, keep `sync` as an alias** → *`pull` works; old scripts keep working* · *later: nothing waits on it* · basis **strong** · *1 h old* *(shown before)*
- **93 Drop the `--legacy` flag?** — rec **(b) keep it one more release** → *scripts using `--legacy` keep working a release longer* · *later: nothing waits on it* · basis **partial** · *1 h old* *(shown before)*
- **94 Default log level: `info` or `warn`?** — *your preference, no rec* → *(a) more output by default; (b) quieter by default* · *later: it stays `info`* · basis **strong** · *1 h old* *(shown before)*
- **95 Move the config file under `~/.config`?** — rec **(a) move it, and read the old path too** → *new installs use `~/.config`; old ones still load* · *later: nothing waits on it* · basis **strong** · *1 h old* *(shown before)*

*Not this: one entry for the four — "92–95 CLI cleanup: four small calls, see the cards
above" — which leaves no recommendation, and no impact, where the operator reads the list, so
they cannot answer from it.*

---

## 24. Decided alone, shown after — and a class on every ask

*Situation: the caller names classes of decision and keeps a store. Its rules let the agent
decide changes to words and splits of scope alone; a trade-off is asked. Since its last
report the agent renamed a heading and left one part of the work for a filed follow-up, and it
has one question.
Each thing decided alone was recorded in the store when the agent acted; the report renders
those records. The decisions block stays last.*

**Done alone** — *2 since my last report · say so in your own words to undo or reopen any*
- **Done: renamed the "Setup" heading to "Install" in the command-line guide, to match the other four guides** — *words · two-way (one edit), nothing links to the heading · inside the task you gave me · undo: one edit*
- **Done: left the Windows install steps to a follow-up item, "Windows install steps"** — *scope · two-way (pull it back in any time), nobody waits on it · the class "scope", which your rules let me decide · undo: say "pull it back in"*

**85 — Ship the install script as one file or as a package?**
**What:** how users get the new install script: one file they download and run, or a package from the package manager.
**Context:** the install script sets the command-line tool up on a user's machine; the package manager is the system's own installer, which keeps what it installs up to date. It came from the guide's install section, which waits on it · you decide how users get the script.
▸ Open questions — 1 open: how many users lack the package manager
▸ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Impact:** later: the install section says "coming soon" · reach: everyone installing the command-line tool
- **(a) One file**
  *→ users download and run it; each new version is downloaded again by hand*
  *pros: nothing to publish, and no package manager needed*
  *cons: users fetch each new version by hand*
- (b) A package
  *→ users install it with the package manager, and updates come with it · reach: users who have the package manager · cost: about a day to publish*
  *pros: users get updates with their other packages*
  *cons: about a day to publish, and only for users with the package manager*
- (z) Decide later — *it waits; the install section says "coming soon"*

▸ Background — why now: the command-line guide's install section waits on it.

*What the caller's store holds, one physical line each — a record line for each thing decided alone, and the ask's card line, indented under its headline, that carries its class. The exact lines are the caller's format; these are this invented caller's:*

```
decided: 2026-10-02T14:05Z words — renamed the "Setup" heading to "Install" in the command-line guide, to match the other four guides; safe alone: one edit undoes it and nothing links to the heading · authority: task · reopen: one edit to the heading
decided: 2026-10-02T14:12Z scope — left the Windows install steps to the follow-up item "Windows install steps"; safe alone: it can be pulled back in any time and nobody waits on it · authority: class scope · reopen: say "pull it back in"
decision 85: Ship the install script as one file or as a package? — options: (a) one file [recommended] | (b) a package | (z) decide later
  raised: 2026-10-02T14:20Z
  what: how users get the new install script: one file, or a package from the package manager
  why now: the command-line guide's install section waits on it
  why ask: trade-off — one file never updates itself, a package needs the package manager; which users would rather have is not a fact the agent has
  context: the install script sets the command-line tool up on a user's machine; the package manager is the system's own installer, which keeps what it installs up to date. It came from the guide's install section, which waits on it · you decide how users get the script — then: none
  impact: → (a) users download one file, each update by hand; (b) a package that updates itself, about a day to publish · later: the install section says "coming soon" · reach: everyone installing the command-line tool
  (a) one file — users download and run it; each new version is downloaded again by hand
  (b) a package — users install it with the package manager, and updates come with it — reach: users who have the package manager — cost: about a day to publish
  (z) decide later — it waits; the install section says "coming soon"
```

*The `context:` and `impact:` lines are stored with the card when the decision is raised, one
physical line each, so every view of 85 reads them from there — the card its Context and its
Impact line — and each option's line holds its own effect, reach and cost, which the card
shows under the option, and its `⚠ undo:` when it is one-way or costly (neither of 85's is);
a caller's row of open items reads the recommended option's effect from its option line. The
store keeps *why now* and *why ask* as two lines; the card shows them in its ▸ Background
fold, whose summary, *why now:* and that line's first sentence, is composed when the card is
shown, never stored. This caller's `impact:` line still opens on an effect, `→ …`; the card does
not show it, and its **Impact:** line starts at `later:` (`references/legacy-cards.md`). The `context:`
line's text before ` — then: ` is the card's Context; after it, what a block would add
(`none`: 85 was raised as a card).*

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

---

## 26. Tag size, in a caller's tightest views

*Situation: a caller with a store lists its open items in a table, one row each, and names the
open decisions on one line of its report. Neither has room for a list line, so each decision
shows its number and the recommended option's effect alone, read from its stored option line:
on the report line after an arrow, its letter first; in a row that shows the recommendation,
after it. With no recommendation, each option's in a few words. The decisions block
that closes the message still carries every list line, card and block.*

| item | why |
|---|---|
| preview deploy (ab12) | decision 46: Retry the failed preview deploy? — rec (a) → preview up in about 4 minutes |
| staging storage (cd34) | decision 47: Delete last month's unused staging snapshot? — rec (a) → frees 120 GB of staging storage |
| storage dashboard (ef56) | decision 45: Units on the storage dashboard: MiB or MB? — your preference → (a) OS-tool units; (b) bill units |

`decisions needed: 46 (→ (a) preview up in about 4 minutes), 47 (→ (a) 120 GB freed for good), 45 (→ (a) OS-tool units; (b) bill units)`

*Not this: a row that reads "decision 47: Delete the snapshot? — rec (a)" with nothing after
it. Whether (a) frees space or breaks a restore is what the operator weighs, and the row is
the one place they may look.*

---

## 27. An option the operator carries out

*Situation: a fix to the staging site's sign-in is merged. The automated tests sign in with a
test account, which skips the real sign-in path, so one check needs a real account in the
operator's own browser — something only they can do. Whatever (a) asks of them is on the
card, in its **To act on (a):** part.*

**86 — Run the staging sign-in check from your own browser?**
**What:** a one-off check that the fixed sign-in works with a real account on the staging site. It needs the signed-in session in your everyday browser, which I cannot reach.
**Context:** the staging site is the test copy of the live site; the sign-in check is a script that reuses your browser's signed-in session and opens three pages behind sign-in. It came from the merged sign-in fix, which waits on it · you decide whether to run it or release on the automated tests.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the sign-in fix stays unreleased · reach: (a) the staging site only; (b) everyone who signs in, if the fix is wrong
- **(a) Run it now**
  *→ the fix goes out today if it passes · reach: the staging site only · cost: about 5 minutes of your time*
  *pros: a real sign-in proves the fix before it ships*
  *cons: about 5 minutes of your time*
- (b) Release on the automated tests alone
  *→ the fix goes out unchecked for a real account; if it is wrong, real users cannot sign in until a revert release · reach: everyone who signs in, if the fix is wrong*
  *pros: the fix ships without waiting on you*
  *cons: if it is wrong, real users cannot sign in until a revert*
- (z) Decide later — *it waits; the fix stays unreleased*

**To act on (a):**
1. Sign in at `https://staging.example.com/login` in the browser you use every day.
2. In a terminal on the same machine, run `/opt/checks/staging-sign-in/run.sh --browser-profile default`. It reads that browser's session and opens each page behind sign-in.
3. When it asks which pages to try, paste:

   ```
   account billing settings
   ```

4. Tell me the last line it prints: `3 of 3 pages signed in`, or which pages failed.

▸ Background — why now: the sign-in fix stays unreleased until the check runs.

*Not this: "(a) run it — from the check folder, paste the prompt, tell me; I'll give you the
steps". The folder is never located, the prompt is never shown and the steps are deferred:
the operator has to ask where the files are before they can start.*

---

## 28. A card that summarises a plan

*Situation: a cleanup plan the operator has not read sorts its work into levels. The card
says what each option removes, in words; the plan's label trails as a tag at most, for when
the operator opens the plan.*

**87 — How far should the docs cleanup reach this week?**
**What:** how much of the docs cleanup to do now: only the broken links and the unused images, or also the pages that still cite the retired setup guide.
**Context:** the cleanup plan sorts its work into two levels; the second covers 12 pages that three other teams own. It came from the failing link checker · you decide how far this week's cleanup reaches.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the link checker keeps failing the docs build · reach: the docs site and its readers
- **(a) Remove the broken links and the unused images** (level 1 in the cleanup plan)
  *→ the docs build passes again · reach: 40 pages, no wording changed*
  *pros: the docs build passes this week, with no wording changed*
  *cons: the 12 pages still send readers to steps that no longer work*
- (b) Also rewrite the pages that cite the retired guide (level 2 in the plan)
  *→ those 12 pages point readers at the current guide instead of steps that no longer work · reach: three teams' pages · cost: about a day*
  *pros: readers of those 12 pages get steps that work*
  *cons: about a day more, and three teams' pages change*
- (z) Decide later — *it waits; the docs build keeps failing on the broken links*

▸ Background — why now: the link checker fails the docs build until the cleanup lands.

*Not this: What: "L2, the cleanup scope", with options "(a) level 1 only" and "(b) level 1
plus wording". The operator never read the plan those labels come from, and neither option
says what happens if it is chosen.*

---

## 29. A review's findings, as a group

*Situation: today's code review of the upload-service change left three findings for the
operator to rule on before the merge: F3 (oversize upload), F7 (retry storm) and F9 (stale
temp files). Each needs its own answer, so the bundle is a group: one whole card per finding
under one heading that carries what they share. The set is findings-style, so it is put in
chat, not on an answer page. Each title opens on the finding's label with its short name,
since the operator answers by the review's labels; the number stays the handle.*

**Decisions** — *3*

**Group: upload-service review findings** — *3 decisions, all from today's review, all before the merge*
**Shared context:** the review is today's code review of the upload-service change you asked for; it labels each finding with a number, and these three are the ones it left for you, the rest being fixed.

**51 — F3 (oversize upload) · Check an upload's size before reading it?**
**What:** whether the upload handler checks the size a client declares before it reads the upload, in `upload/handler.go`.
**Context:** the declared size is the length a client sends ahead of the upload; the handler ignores it, reads the whole file into memory and only then compares it with the 50 MB limit. Raised when the review turned it up · you decide whether the check moves first.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the merge waits on this finding · reach: the upload service and every client that uploads
- **(a) Check the declared size first**
  *→ a 2 GB upload is refused at once; before, one such upload filled the server's memory and stalled every other upload on it · cost: about an hour*
  *pros: one oversize upload can no longer stall the server*
  *cons: about an hour more before the change merges*
- (b) Leave it for a follow-up
  *→ the change merges reading first and checking after; an oversize upload still stalls the server until the follow-up lands*
  *pros: the change merges now*
  *cons: an oversize upload still stalls the server until the follow-up lands*
- (z) Decide later — *it waits; the merge waits on this finding*

▸ Background — why now: the merge waits on this finding.

**52 — F7 (retry storm) · Add a backoff to failed disk writes?**
**What:** whether a failed write to disk waits before it is tried again, in the upload service's storage writer.
**Context:** a backoff is a wait that grows after each failed try; today the writer tries again at once, with no wait. Raised when the review turned it up · you decide whether the backoff goes in before the merge.
▸ Open questions — 1 open: how long a busy disk stays busy
▸ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Impact:** later: the merge waits on this finding · reach: the upload service and the disks it writes to
- **(a) Add a backoff, doubling to 30 seconds**
  *→ each retry waits twice as long as the last; before, a disk that failed every write drew hundreds of writes a second until it was taken out · cost: about two hours*
  *pros: a failing disk draws a few writes a minute, not hundreds a second*
  *cons: an upload may wait up to 30 seconds between tries*
- (b) Cap the retries at five, no wait
  *→ the storm stops after five tries in a few milliseconds, and the upload fails · reach: clients whose upload meets a briefly busy disk*
  *pros: the storm stops within milliseconds*
  *cons: an upload fails on a disk that was only briefly busy*
- (z) Decide later — *it waits; the merge waits on this finding*

▸ Background — why now: the merge waits on this finding, and a failing disk still draws a retry storm until then.

**53 — F9 (stale temp files) · Remove an aborted upload's temp file?**
**What:** whether the upload service deletes the temporary file an aborted upload leaves on disk.
**Context:** each upload is written to a temporary file first and moved into place when it completes; an aborted upload's file is never moved or deleted. Raised when the review turned it up · you decide whether the cleanup goes in before the merge.
▸ Assumptions — basis: **strong** · 1 assumption with its tripwire
**Impact:** later: the temp directory keeps growing, about 40 GB a week, until the disk fills · reach: the upload servers' disks
- **(a) Delete it when the upload aborts**
  *→ the temp directory holds only uploads in progress · cost: about an hour*
  *pros: no temp file outlives its upload*
  *cons: a crash during the abort can still leave a file behind*
- (b) A nightly sweep of files older than a day
  *→ the directory still grows through each day, by at most a day's aborted uploads · cost: about an hour*
  *pros: one sweep catches every leftover, crashes included*
  *cons: aborted files pile up for up to a day*
- (z) Decide later — *it waits; the temp directory keeps growing until the disk fills*

▸ Background — why now: the merge waits on this finding, and the temp directory grows about 40 GB a week.

- **51 F3 (oversize upload) · Check an upload's size before reading it?** — rec **(a) check the declared size first** → *an oversize upload is refused before any of it is read* · *later: the merge waits* · basis **strong** · *10 min old*
- **52 F7 (retry storm) · Add a backoff to failed disk writes?** — rec **(a) add a backoff** → *a failing disk gets a few writes a second* · *later: the merge waits* · basis **partial** · *10 min old*
- **53 F9 (stale temp files) · Remove an aborted upload's temp file?** — rec **(a) delete it on abort** → *an aborted upload's file is deleted at once* · *later: the merge waits* · basis **strong** · *10 min old*

*Reply with a letter (`51: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

*Each card is whole — its own What, Context, Assumptions fold line, Impact, options and Background fold line — so each finding gets its own impact and its own answer, and `ok 51-53` still takes all three recommendations. The heading adds what the three share and replaces nothing on them. Each effect says how the failure happens and what changes after the fix, not just its name: F3's says a 2 GB upload fills the server's memory first.*

*Not this: one card, "Fix the upload-service housekeeping before the merge?", with options "(a) fix all", "(b) fix some" and "(z) later". It names a category, not the three findings, gives no impact for any one of them, and has no way to answer F3 differently from F7: the operator cannot decide it without asking what the findings are. Nor one card with a pick per finding (`51: F3 a, F7 b`): its picks would be lettered sub-decisions under one number.*

---

## 30. A reply by label

*Situation: the group in example 29 is on screen. The operator answers by the review's labels:
"F7: b, and go with the rec on F3".*

*Read as: 52 — F7 (retry storm) → (b) cap the retries at five, no wait.*
*Read as: 51 — F3 (oversize upload) → (a) check the declared size first.*

Going ahead on both; 53 — F9 (stale temp files) is still open.

*A reply by label is never an exact* `N: letter`*, so each is echoed with the number, the label and its short name, and is read as the decision whose title carries that label. Not this: "Read as: 52 → (b)", which leaves the operator to check that 52 is the finding they meant; nor reading "F7" as decision 7.*

---

## 31. Impact on the system, by its mechanism

*Situation: a dependency audit of the client package — the library partner apps import to
call our API — found that its public functions take and return types from a date library its
maintainers have archived. The decision is about what partner apps meet, so that is what the
Impact names, with the mechanism spelled out and the term glossed.*

**88 — Stop exposing the archived date library from the client package?**
**What:** whether the client package's public functions switch from the archived date library's types to the standard library's, in the next major release.
**Context:** an archived library is one whose maintainers have stopped releasing it, security fixes included; the client package is what partner apps import to call our API. Raised when the dependency audit turned it up · you decide whether the client's public types change in the next major release.
▸ Open questions — 1 open: how many partner apps also use the date library directly
▸ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Impact:** later: the next major release keeps the archived types · reach: every partner app that imports the client, and its build
- **(a) Switch to the standard types in the next major release**
  *→ an app no longer installs the archived library to call the client; before, it had to, at the exact version the client pins, and could install no other · reach: every partner app, one change each at upgrade · cost: about a day*
  *pros: apps stop depending on a library that gets no security fixes*
  *cons: every partner app makes one change when it upgrades*
- (b) Keep the archived types
  *→ every app keeps installing the archived library at the client's pinned version; a security fix for it never comes, and an app that needs another version of it cannot build · reach: every partner app*
  *pros: no partner app changes anything now*
  *cons: the archived library never gets a security fix, and version clashes stay*
- (z) Decide later — *it waits; the next major release keeps the archived types*

▸ Background — why now: the next major release is being planned, and only a major release allows this change.

*Not this: option effects of "→ the audit finding closes" for (a) and "→ the finding stays open for the next review" for (b), which say what happens to the audit, not to the apps. Nor an option line of "exposes an archived library in its public API" alone: it names the problem and not how an importing app breaks (it must install the library, at our version only, and never gets its fixes), or what is different after the switch. Nor a Context that leaves "archived" unglossed for a reader who has not met the term.*
