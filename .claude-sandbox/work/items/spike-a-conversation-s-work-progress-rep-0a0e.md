---
id: spike-a-conversation-s-work-progress-rep-0a0e
title: "spike: a conversation's work-progress report (done, in flight, not done and why) — options by data cost"
short_display_name: conversation progress report
type: spike
status: todo
priority: 2
created: 2026-10-16
updated: 2026-10-16
refs:
  - operator message 2026-10-16
---

Operator 2026-10-16, verbatim: "We should have a concept of a conversation's reporting on work progress. I'm interested in a table of what was done, what's in-flight, and what wasn't done and why. What does that look like I'd like a work-item to present that in a useful way (options with data already available vs analysis that's easy vs time/resource consuming analysis)." Acceptance: a series showing what the report looks like (mock tables), with options tiered by cost (data already available / easy analysis / costly analysis), each naming its sources, its home plugin, and a recommendation.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: planner opus high — spike plan: progress report options by data cost
agent: planner a1e112ecae0cf2d30 plan round 1
return: planner DONE (00_initial.md; mock tables from this session; T1 store/git/ledger <1s but measurably wrong; T2 script joins record lines, scope by session agent ids, reasons + owners, spend; T3 transcript reads $2-6/session; home: new dev-flow skill progress-report; OQ1-OQ8; found store drift: 3769 6d12 fb35 aa4e 7e8f merged and pushed but open; 8/25 landed: lines; 215 answered not acted)
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer a03d55da9a00e63ad plan round 1
verdict: NEEDS_CHANGES plan round 1 (3 high: ledger join misattributes swept store commits (28e1 via 5f753608); adopted ledger carries parent history so scope (a) silently becomes --chain; claude-analytics' approved CLAIM owns spend reports and transcript reads and retires usage_report/item_spend; mediums: T2 parses transcript records, merge grammar and done-without-merge class, footnote tags not plain names, T3 cost ungrounded and needs chunking, T3 safety (mechanical drop of injected text; filing T3 findings goes public); lows 9-13)
decided: closing the five drifted items (05fbbb85) was librarian bookkeeping — merged, pushed and CLEAR, only the status write missed; class: record upkeep, authority: the land step; reported to the operator 2026-10-16 as done alone. OQ5 narrows to the land-step fix.
dispatch: planner opus high — resume, plan fix round 1
agent: planner a1e112ecae0cf2d30 round 2
return: planner DONE (01_review-round-1.md; all 13 applied; home now a split with claude-analytics; OQ1-OQ9, OQ1/OQ3'/OQ9 block)
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer a03d55da9a00e63ad plan round 2
verdict: NEEDS_CHANGES plan round 2 (1-13 fixed; new mediums: OQ9 (a) says claude-analytics reads sub-agent files but F1 reads them; OQ9 lacks a strict-split option, (z) cost understated, OQ3'/OQ7/OQ9 precedence; tags not unique (05bb, 81ae); Done table lost 'what landed'; lows: three untagged cells, scope rule wording, dropped/parked/grooming unmapped)
dispatch: planner opus high — resume, plan fix round 2
agent: planner a1e112ecae0cf2d30 round 3
return: planner DONE (02_review-round-2.md; 14-20 applied; scope now 38 items (4 filed, not started); OQ9 (d) strict split loses 10/38; shared-tag guard)
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer a03d55da9a00e63ad plan round 3
verdict: NEEDS_CHANGES plan round 3 (14-20 fixed; recount 38 and 10-of-38 reproduce; 21 medium: out-of-scope merges never a row, header counts them (exact text given); 22-24 exact wording)
decided: finish round of exact leftovers 21-24 (texts given by the reviewer) — authority answer 145
dispatch: planner opus high — resume, finish round
agent: planner a1e112ecae0cf2d30 finish round
review: self — finish round 03: exactly 21-24 as given; header count rule stated once; supersedes named
verdict: CLEAR plan (round 3 + finish)
note: OQ3 (home) and OQ7 (spend column) follow decision 252's answer, not raised separately
decision 252: 0a0e OQ9 — the line with claude-analytics for the progress report — options: (a) split with interim readers: dev-flow builds the done/in-flight/why table from its own records; spend through usage-report and the sub-agent file-name read are disclosed interim readers, named to claude-analytics [recommended] | (b) the whole report is claude-analytics' workflow report; dev-flow ships nothing now | (c) amend claude-analytics' claim so dev-flow owns all of it | (d) strict split: the table now; spend and the agent-id join only once claude-analytics serves them | (z) decide later
  raised: 2026-10-16T02:08Z
  what: where the report's parts live, against claude-analytics' approved CLAIM.md (spend reports, transcript and sub-agent reads)
  why now: the spike plan cleared review; the build needs these
  why ask: scope — crosses an ownership boundary you approved on 2026-10-08; (c) changes that claim
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) full report now, two interim reads replaced later; (b) nothing here until claude-analytics builds it; (c) a claim change by message to claude-analytics; (d) on this session loses 10 of 38 items (6 landed show only as a header count) · later: blocks the build; home (OQ3) and spend column (OQ7) follow this answer · reach: dev-flow, claude-analytics · undo: interim readers are removable
  (a) as recommended
  (b) all claude-analytics
  (c) amend the claim
  (d) strict split — measured loss 10 of 38 here
  (z) decide later — ships as (d) with the same loss
  rec: (a) · basis strong — measured on this session (38 items, 10 lost under (d))
  unknown: whether claude-analytics agrees to the interim readers (a message to it)
decision 253: 0a0e OQ1 — which tier to build first — options: (a) tier 1 and tier 2 together: store, git and record lines, worked out by a script, no model [recommended] | (b) tier 1 only: the store and git as they are | (c) all three, including transcript reading | (z) decide later
  raised: 2026-10-16T02:08Z
  what: build scope
  why now: the spike plan cleared review; the build needs these
  why ask: your preference — cost versus accuracy
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) right states, reasons and owners, ~2 s plus ~1.8 s per item for spend, no model; (b) <1 s but wrong (drifted items show open, a concurrent session's item creeps in); (c) adds asks never filed and partial completion at $1.6-4 per session · later: blocks the build · reach: dev-flow · undo: add tiers later
  (a) as recommended
  (b) tier 1 only — measurably wrong
  (c) all three — reads transcripts, needs 257
  (z) decide later — nothing built
  rec: (a) · basis strong — measured on this session
  unknown: none
decision 254: 0a0e OQ2 — what counts as 'this conversation' — options: (a) this session id with its compactions; --epoch and --chain flags; the header notes a /clear predecessor [recommended] | (b) since the last compaction | (c) the whole handoff chain | (z) decide later
  raised: 2026-10-16T02:08Z
  what: the report's default scope
  why now: the spike plan cleared review; the build needs these
  why ask: your preference
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) matches how a session is experienced; (b) shorter, loses earlier work; (c) spans sessions back weeks · later: none, default (a) · reach: the report · undo: a flag
  (a) as recommended
  (b) last compaction
  (c) handoff chain
  (z) decide later — builds as (a)
  rec: (a) · basis partial — /clear splits one conversation into two scopes, said in the header
  unknown: none
decision 255: 0a0e OQ4 — when the report shows without being asked — options: (a) on demand, plus once in the librarian's closing message [recommended] | (b) also after each push | (c) on demand only | (z) decide later
  raised: 2026-10-16T02:08Z
  what: when it appears
  why now: the spike plan cleared review; the build needs these
  why ask: your preference — attention
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) one end-of-session view; (b) a table after every push; (c) only when asked · later: none, default (a) · reach: librarian sessions · undo: one line
  (a) as recommended
  (b) after each push too
  (c) on demand only
  (z) decide later — builds as (a)
  rec: (a) · basis partial — preference
  unknown: none
decision 256: 0a0e OQ5 — stop items staying open after they land — options: (a) file an item so the land step writes landed: and closes the item, or names what is left [recommended] | (b) rely on the report's drift check | (z) decide later
  raised: 2026-10-16T02:08Z
  what: a fix for the drift found (five merged items left open; 8 of 25 landed: lines)
  why now: the spike plan cleared review; the build needs these
  why ask: scope — changes the librarian's land step
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) the store stays true by construction; (b) drift recurs and the report flags it · later: none · reach: librarian-mode land step · undo: two-way
  (a) as recommended
  (b) report only
  (z) decide later
  rec: (a) · basis strong — measured drift on this session
  unknown: none
decision 257: 0a0e OQ6 — may the costly tier read conversation text — options: (a) yes, only when asked on that run, paraphrase only, wherever 252 puts it [recommended] | (b) never | (c) automatically at session end | (z) decide later
  raised: 2026-10-16T02:08Z
  what: transcript reading for asks never filed and partial completion
  why now: the spike plan cleared review; the build needs these
  why ask: reach — transcripts hold your words; findings filed from it would be pushed to a public repo
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) on request only; anything filed goes through the secret rule, the source-material scan and your yes; (b) no costly tier; (c) every session, unasked · later: blocks only the costly tier · reach: your transcripts · undo: two-way
  (a) as recommended
  (b) never
  (c) automatic
  (z) decide later — the costly tier waits
  rec: (a) · basis strong — chunked readers, harness-injected text dropped by a parser
  unknown: the real per-session cost (estimate $1.6-4)
decision 258: 0a0e OQ8 — a counts line in the checkpoint manifest — options: (a) later, as a context-guard item | (b) no | (z) decide later [recommended]
  raised: 2026-10-16T02:08Z
  what: whether checkpoints record done/in-flight/not-done counts
  why now: the spike plan cleared review; the build needs these
  why ask: your preference
  context: spike 0a0e plan CLEAR (00-03, .claude-sandbox/investigations/spike-a-conversation-s-work-progress-rep-0a0e/) — then: none
  impact: → (a) a later item; (b) none · later: nothing waits · reach: context-guard · undo: two-way
  (a) later item
  (b) no
  (z) decide later [recommended] — nothing needs it yet
  rec: (z) · basis partial — no consumer yet
  unknown: none
