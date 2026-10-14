---
id: foundation-count-reviews-per-gate-and-ke-8d7c
title: "foundation: count reviews per gate, and keep the operator conversation going while a gate's review runs"
short_display_name: per-gate reviews, overlapping talk
type: spike
status: todo
priority: 2
created: 2026-10-14
updated: 2026-10-14
refs:
  - foundation-skill-build-the-green-field-f-cc8a
---

Answer 205 b (2026-10-14) with a design request: count review rounds per gate; and propose the optimal way to continue into the next phase while a gate review is processed, keeping a class of operator discussion going that is likely still valid after the review returns, at the cost of a more complex gate/review structure. Acceptance: a plan series proposing the structure, back to the operator before any build.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/foundation-count-reviews-per-gate-and-ke-8d7c/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan per-gate review counts and overlapping operator talk (answer 205 b)
agent: planner a454d20caa97aeb97 round 1
return: planner DONE .claude-sandbox/investigations/foundation-count-reviews-per-gate-and-ke-8d7c (00_initial.md; F1 per-gate counting, F2 ask ahead; OQ1-OQ7; F1 after fb35)
baseline: 9ccc9dc88f17cae9b9dd6cfed2aad901de2ba5ab1d58782f9b930d15d29caa0c  00_initial.md 30eb9ce57042429e156362008390719881ae7de87cb834376dbee0cf065cf18d  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer a06b4755eb6d8b126 plan round 1
verdict: NEEDS_CHANGES plan round 1 (2 high: an answer touching an earlier phase must be a reopen, not an amendment; ahead answers go out of force at the next verdict under bindings.md's in-force rule; 9 medium: budget line source and fable/raise lines, fb35 overlap understated, OQ6 and the trial pause, librarian channel and decide-alone, reconcile not mechanical, G3 examples break D2, cap approval passes a gate without CLEAR, no minimal B weighed, answer 205 overstated; 9 low; 2 nits)
dispatch: planner opus high — resume, plan fix round 1 (all findings, verbatim report passed)
agent: planner a454d20caa97aeb97 round 2
return: planner DONE .claude-sandbox/investigations/foundation-count-reviews-per-gate-and-ke-8d7c (01_review-round-1.md; all 22 applied, none declined; OQ1-OQ7 revised)
baseline: 9ccc9dc88f17cae9b9dd6cfed2aad901de2ba5ab1d58782f9b930d15d29caa0c  00_initial.md 1ca1a907ad775373ff39dd331641f83d108d31623368e504444c3e092776078f  01_review-round-1.md 6489274214b7bb98e37de5a8833a6b3f65f62a76a6db75369eb3a634798d626d  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer a06b4755eb6d8b126 plan round 2
verdict: NEEDS_CHANGES plan round 2 (all 22 closed; new 1 medium: a reopen during gate N's review drops gate N's open work; 5 low: budget src read by the finish chain and fable rule, no-reading line re-base, resume.md granted-round end, Ids: on reopen serials, ahead question vs Held row double decision, OQ7 names incomplete; 3 nits)
dispatch: planner opus high — resume, plan fix round 2
agent: planner a454d20caa97aeb97 round 3
return: planner DONE .claude-sandbox/investigations/foundation-count-reviews-per-gate-and-ke-8d7c (02_review-round-2.md; reopen pauses gate N then resumes with its open work; no-reading gate keeps the fourth-review fallback; OQ7 names complete)
baseline: 9ccc9dc88f17cae9b9dd6cfed2aad901de2ba5ab1d58782f9b930d15d29caa0c  00_initial.md 1ca1a907ad775373ff39dd331641f83d108d31623368e504444c3e092776078f  01_review-round-1.md b7d9216140bf158a4f2b0c9ffad6d1557dd2ec0d0872662fdb9a71c7bdf1fe19  02_review-round-2.md 7bf5405ec2a3dd36b1e9a271ac7390cf06f5a1c10f2230c26add3a1bc490df7e  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer a06b4755eb6d8b126 plan round 3
verdict: NEEDS_CHANGES plan round 3 (all 9 round-2 closed; new 1 medium: a reopen taken during gate N's review goes out of force at gate N's verdict and resume never sees it; 1 low: the spend-unread fallback needs a clause in the cap list and resume's CAP; 1 nit: fb35 now landed)
dispatch: planner opus high — resume, plan fix round 3 (exact fixes given)
agent: planner a454d20caa97aeb97 round 4
return: planner DONE .claude-sandbox/investigations/foundation-count-reviews-per-gate-and-ke-8d7c (03_review-round-3.md; reopen-in-review survives the verdict and resume GATEs it; spend-unread gate caps at its fourth review)
baseline: 9ccc9dc88f17cae9b9dd6cfed2aad901de2ba5ab1d58782f9b930d15d29caa0c  00_initial.md 1ca1a907ad775373ff39dd331641f83d108d31623368e504444c3e092776078f  01_review-round-1.md b7d9216140bf158a4f2b0c9ffad6d1557dd2ec0d0872662fdb9a71c7bdf1fe19  02_review-round-2.md caf33a12cbc8b4cc8b3bcc8c11ef2caa095034e85fa1b99bca37da3c942a05f9  03_review-round-3.md ffed88b09e1bd6151d6f89b80cdc2b1e110c8380a422d8872e301ee5711d8c8d  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 4 (the cap)
agent: reviewer a06b4755eb6d8b126 plan round 4
verdict: NEEDS_CHANGES plan round 4 (all 3 round-3 closed; 1 medium + 2 low + 1 nit, all exact fixes stated by the reviewer: the orchestrator writes nothing in the series; the Group D check reads only unanswered or in-force reopens; the live path holds gate N's round too; INDEX blast-radius line)
decided: 2026-10-14T08:04Z cap — past the fourth review, only exact-fix leftovers: one finish round, read by the librarian (authority answer 145; no hold caps rounds)
dispatch: planner opus high — resume, plan finish round
agent: planner a454d20caa97aeb97 round 5 (finish)
result: DONE finish at 04_finish-round.md (four exact fixes; read by the librarian)
verdict: CLEAR plan after 3 fix rounds, 1 finish (plan series 00-04)
decision 220: OQ1 — how large is each foundation gate's spend allowance? — options: (a) the full plan default per gate ($28, or $40 for a spike), a budget pin read per gate [recommended] | (b) the literal reading of answer 205: one plan budget split three ways, about $9 per gate | (c) one budget across the run, only the review count per gate | (z) decide later: F1 waits
decision 221: OQ2 — what does a review cap at a foundation gate end in? — options: (a) a finish round for exact fixes, then the gate decision with a cap part; holding findings offered only when none touches a one-way ADR, the claim or an interface's terms; a granted round's leftovers come back to the decision [recommended] | (b) today's plan rule: stop and carry, decided without asking | (c) every gate cap raised as an ask for another round | (z) decide later: F1 waits
decision 222: OQ3 — which design keeps the operator conversation going while a gate's review runs? — options: (a) full ask-ahead: next-phase questions meeting five criteria, answers provisional with what they rest on, re-asked automatically when a fix changes that [recommended] | (b) ask-ahead minimal: early answers kept as Held rows, the next drafter re-checks them, no tracking machinery | (c) no overlap: ship per-gate counting only | (d) a second agent drafts the next phase during the review | (e) the operator approves first and the review follows | (z) decide later: F2 waits
decision 223: OQ4 — does asking ahead also run under an orchestrator (the librarian or dev-cycle)? — options: (a) yes, through the planner's AHEAD field, or under the minimal design from the Held rows [recommended] | (b) standalone sessions only | (z) decide later: ships as (a)
decision 224: OQ5 — does a new gate pass (a revise, or a gate resuming after a reopen) start a fresh review count? — options: (a) yes [recommended] | (b) no, it continues the gate's count | (z) decide later: ships as (a)
decision 225: OQ6 — do foundation runs stay in the xhigh planner trial? — options: (a) exclude them, with the trial's pause rule re-read [recommended] | (b) enrol on the first gate, counted within it | (z) decide later: ships as (a)
decision 226: OQ7 — approve the new record names this adds (they become part of the store format other tools read)? — options: (a) approve: the gate-open: line, the ahead tag, gate-status values 'in review round <n>' and 'paused for <reopen serial>', the cap reason, the AHEAD field, the per-gate budget source, the Ids: line, the bites field, the rests on: card line, and the status words provisional, re-ask, carried, held, amendment, reopen, raised, dropped [recommended] | (b) the same set with the line named gate: | (c) other names, in your words | (z) decide later: ships as (a)
