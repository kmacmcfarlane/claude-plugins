---
id: librarian-mode-interview-the-repo-s-scop-5925
title: "librarian-mode: interview the repo's scope of responsibility into ## Librarian, and ask repos that lack it"
short_display_name: interview librarian scope
type: feature
status: doing
priority: 1
parent: agent-scope-protocol-declared-scope-the-51df
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-05T17:36Z
created: 2026-10-04
updated: 2026-10-05
refs:
  - answer 152
---

Operator 2026-10-04, answer 152 (verbatim on 1222): the short-term step of the agent scope protocol is a simple librarian-mode change — interview scope for the ## Librarian CLAUDE.md section, and ask to fill it for repos that don't have it filled yet. Today the opt-in (references/opt-in.md) asks Scope (paths), Checks and Push. Plan must settle: which scope-of-responsibility fields the interview adds (e.g. systems the librarian owns or acts on, what it needs to observe, credentials it needs — named by path and key, never value — what it does not own and who does), how the section records them (CLAUDE.md lines the librarian reads at Rehydrate), how a librarian whose section lacks them asks at start (a numbered decision, since a modal is allowed only before anything is in flight), and how a librarian advertises its scope to peers and escalates an overlap to the operator. Keep it a small skill change; the long-term protocol is the parent spike with the agents librarian.

## Handoff
- doing: plan CLEAR (5925 series 00-02)
- next: on 153-155: dispatch the build from main with the answers; carried 21, 22
- blocked: —
- learned: —
note: agents' reading (2026-10-04, on 51df): the ## Librarian section stays the single authority for scope; credentials stay with the operator per session via claude-sandbox launch config — the interview should name needed credentials by path and key only, and point grants at the sandbox launch config

## Notes
- 2026-10-05 claimed by Kyle-McFarlane@401123cbad11
target: plan librarian-mode-interview-the-repo-s-scop-5925 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/5925-librarian-scope-interview
dispatch: planner opus high — plan (answer 152 a, short term)
agent: planner a84db3183c674645f round 1
return: planner PLAN_READY .claude-sandbox/investigations/5925-librarian-scope-interview/ (INDEX, 00); four operator questions (line names, binding, how to ask, access check)
baseline: 6a05713a226d 00_initial.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer a675af042d3aeeff7 round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings:
  claims about existing text check out; all eleven sibling sections hold only Scope/Checks/Push; no script parses ## Librarian
  1. [high] 00:155-159 — the interview chore is todo and ready, so the Idle turn would dispatch it and an implementer edit CLAUDE.md mid-decision; hold it out of Work (claimed doing with an unanswered decision, or blocked), never dispatched, closed by the transcription
  2. [high] 00:379-391; INDEX:64-71 — OQ2 (rule-change) and OQ4 (trust) marked non-blocking, build writes (a); raised classes; mark blocking or ship the conservative option
  3. [medium] 00:191-237 — grown past "simple": binding, Ground, access check, other-agent detection, Rehydrate re-detection; factor feature 1 (lines, interview, write, Rehydrate/status display, overlap detection while drafting) and defer the rest to 51df
  4-11. [medium] Ground is a shared path contract (separate brief line or defer); Red flags SKILL.md:351 and 3460's edit of it; the bypass looser than opt-in (echo the exact block, re-echo on change, MERGE_HEAD precondition, raise widening Critical 3 as a rule-change); drafting can push private details (only what tracked files publish; name grant elements without asserting the file; cascade); the access check's injection and tilde issues; sibling reads too broad (only sections with Scope:, untrusted data, no Rehydrate sweep); "system" undefined; card draft vs decisions.md one-line context and stored-field rendering
  12-14. [low] heavy analysis turn (scout or next Report; order vs the session-name gate); worktree session case; departure from answer 152's read-as stated in OQ3
  15. [nit] no counts in INDEX
librarian ruling on 3: narrowing — feature 1 only in this item (the four lines, the interview, the guarded write, the Rehydrate/status display, overlap detection while drafting); binding, Ground, the access check and other-agent detection go to the parent 51df; this keeps it the simple change the operator asked for, and OQ2/OQ4 leave this item with them
dispatch: planner opus high — resume (plan fix round 1)
agent: planner a84db3183c674645f round 2
return: planner PLAN_READY — serial 01_narrowed-feature-1.md (findings 1-15; OQ2/OQ4 moved to 51df)
baseline: 6a05713a226d 00_initial.md ccb2832e0162 01_narrowed-feature-1.md 
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer a675af042d3aeeff7 round 2
verdict: NEEDS_CHANGES round 2 (plan)
findings:
  prior 1-15 closed or deferred to 51df; serial 01's wi claims verified against wi.py
  16. [medium] 01:350, INDEX:82 — OQ3 (trade-off, raised) marked non-blocking; mark it blocking like OQ1 and OQ6
  17. [medium] 01:198, 201-209 — an overlap answer after the interview card is answered changes the block without an echo; raise the interview card only after every overlap decision is answered, or revise and re-ask it
  18. [low] 01:145-148 — a drop re-asks every start; a grep-able decline line, or say drop = ask again and point at Systems: none
  19. [low] 01:360-365 — OQ6 (b) contradicts "never dispatched"; one sentence on what changes under (b)
  20. [nit] 01:145 — the blocked item shows only as its decision row in Groom
dispatch: planner opus high — resume (plan fix round 2)
agent: planner a84db3183c674645f round 3
return: planner PLAN_READY — serial 02_card-order-and-drop.md (16-20)
baseline: 6a05713a226d 00_initial.md ccb2832e0162 01_narrowed-feature-1.md 6f14d3b9562b 02_card-order-and-drop.md 
dispatch: reviewer opus high — resume (plan review round 3)
agent: reviewer a675af042d3aeeff7 round 3
verdict: CLEAR round 3 (plan)
findings:
  16-20 closed
  21. [low] 02:83-84,133-135; 01:364 — OQ6 (b) is not a trivial-documentation chore: CLAUDE.md is never self-reviewed (decide-alone.md:140-141, model-routing.md:330-331); state (b)'s cost as one implementer plus one reviewer dispatch per repo
  22. [nit] INDEX.md:31-32 — Status column values outside the format's vocabulary
findings: carried — 21 [low], 22 [nit] above, verbatim; into this item's build (21 is reflected in decision 155's card)
decision 153: What should the four new scope lines in a repo's ## Librarian section be called? — options: (a) Systems:, Observes:, Access:, Not owned: [recommended] | (b) Systems:, Observe:, Credentials:, Neighbours: | (c) one free-text Responsibility: block, nothing parsed | (z) decide later
  raised: 2026-10-05T17:53Z
  what: the stored names of the scope interview's lines (was OQ1 of the scope-interview plan, 5925): what the librarian owns or acts on; what it only reads; the credentials it needs, by path or key with where the grant lives, never a value; what it does not own and who does
  why now: the plan cleared review in 3 rounds; blocks: the build's wording
  why ask: api-name — names written into every opted-in repo's CLAUDE.md are yours
  context: you asked for a simple librarian-mode change that interviews each repo's scope into its ## Librarian section (answer 152) · you name the lines — then: none
  stakes: reversible, wide — every opted-in repo's CLAUDE.md
  (a) Systems: / Observes: / Access: / Not owned: — Not owned: gives forwarding (3460) a target; Access: lines read "<path or $KEY> — grant: <launch-config element>" — undo: a rename edits each repo's section — who: every librarian
  (b) Systems: / Observe: / Credentials: / Neighbours: — "Credentials" is blunter; "Neighbours" names the other owner rather than the thing
  (c) one free-text Responsibility: block — nothing parsed, so no later binding or overlap check can read it
  (z) decide later — the build waits
  rec: (a) · basis partial — each name says what the line holds; the reviewer found no clash with existing section lines
  unknown: none
decision 154: How should a repo be asked for its scope lines? — options: (a) always one numbered decision on a drafted block, after the opt-in [recommended] | (b) a fresh opt-in asks for the lines inside its own dialog; existing repos get a numbered decision | (c) the dialog whenever nothing is running, a numbered decision otherwise | (z) decide later
  raised: 2026-10-05T17:53Z
  what: how the interview reaches you (was OQ3 of the scope-interview plan)
  why now: blocks the build
  why ask: trade-off — and (a) departs from my reading of your answer 152 ("the opt-in interviews the repo's scope")
  context: you asked to interview scope for the ## Librarian section and to ask repos that lack it · you decide whether that happens inside the opt-in dialog or as a card after it — then: a helper drafts the lines from the repo's tracked files (never .claude-sandbox/env) and reads sibling repos' sections for overlaps; overlaps are asked first, then one card shows the final block
  stakes: reversible, narrow — how you are asked
  (a) a numbered card on a drafted block — you correct a proposed block instead of composing it in a dialog; works the same for new and existing repos; never blocks the session — undo: an edit — who: every librarian
  (b) inside a fresh opt-in's dialog; a card for existing repos — closest to your words for new repos, but a dialog cannot show a drafted block well
  (c) the dialog when nothing is running — a dialog can block a session against peer messages
  (z) decide later — the build waits
  rec: (a) · basis partial — a drafted block needs reading and correcting, which your feedback says fits a card, not a dialog
  unknown: none
decision 155: May the librarian write the scope block you confirm straight into CLAUDE.md, as it does your opt-in answer? — options: (a) yes: extend the transcription exception to the exact block you confirmed [recommended] | (b) no new exception: the confirmed block runs the cycle as its own change, with a reviewer | (z) decide later
  raised: 2026-10-05T17:53Z
  what: whether a librarian edits its own CLAUDE.md section from your confirmed answer (was OQ6 of the scope-interview plan)
  why now: blocks the build (it sets the librarian's Critical rule's wording)
  why ask: rule-change — "you do not edit custody files" has two exceptions today; this adds a third
  context: today a librarian may write only your opt-in answer into ## Librarian itself · you decide whether your confirmed scope block gets the same treatment — then: the write is guarded: only the exact block shown back as your answer, in the main checkout, on main, CLAUDE.md clean, no merge in progress, a commit touching only CLAUDE.md
  stakes: reversible, narrow — each repo's ## Librarian section
  (a) extend the exception — the block lands as soon as you confirm it; nothing else in CLAUDE.md can change this way — undo: revert the commit — who: every librarian
  (b) through the cycle — one implementer and one reviewer dispatch per repo (CLAUDE.md is never self-reviewed), roughly $3-5 each, to insert a block you already approved word for word
  (z) decide later — the build waits
  rec: (a) · basis partial — the block is your exact words and the guard is tighter than the opt-in's; a review would check a transcription
  unknown: none
answer 153: 153a (2026-10-06T01:37Z, chat; read as: (a) Systems:, Observes:, Access:, Not owned:)
answer 154: 154a (2026-10-06T01:37Z, chat; read as: (a) always one numbered decision on a drafted block, after the opt-in)
answer 155: 155a (2026-10-06T01:37Z, chat; read as: (a) extend the transcription exception to the exact confirmed block, guarded)
target: full librarian-mode-interview-the-repo-s-scop-5925 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-interview-the-repo-s-scop-5925
budget: 2026-10-06T01:44Z build $22 — default other build
dispatch: implementer opus medium — build (plan CLEAR r3, series 00-02; answers 153 a, 154 a, 155 a; carried 21, 22)
agent: implementer a43502b67a4ba3d10 round 1
