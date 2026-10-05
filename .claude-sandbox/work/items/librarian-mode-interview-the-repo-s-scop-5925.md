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
- doing: —
- next: —
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
