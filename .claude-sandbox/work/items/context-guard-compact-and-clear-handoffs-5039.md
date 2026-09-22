---
id: context-guard-compact-and-clear-handoffs-5039
title: "context-guard: /compact and /clear handoffs lose state — investigate failure modes and fix"
type: spike
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T15:44Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: 'some stuff broke in the /compact handoff' — investigate now while the librarian session still holds the context; consider other likely handoff failure modes the strategy does not address; research compacted conversation logs for how past handoffs went. P1: every compaction slows progress. Acceptance: a findings series (observed failures with evidence, failure-mode catalogue, gaps in the current checkpoint/rehydrate/HANDOFF strategy incl. the 8cc2 F3a/F3b plan and answer 47) and factored fix items.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## First-hand observations (librarian session a1a4c97c, successor by /clear of 0c7eafc7, 2026-09-22)
Written while the context is live; evidence paths are under ~/.claude/projects/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/.
- O1 predecessor 0c7eafc7 (29 MB transcript) compacted manually 3× at ~800K/931K/841K tokens (09-18 15:00, 09-19 05:46, 09-21 22:33), then /clear → a1a4c97c. Every compaction was operator-driven, late (80–93% of a 1M window).
- O2 HANDOFF.md `written: 2026-09-22T06:00:00Z` is a hand-typed round stamp; the F1 worktree it calls "dispatched just before this handoff" was created 08:20:41Z. The manifest's time is not trustworthy — hook-stamp it.
- O3 the manifest said F1's agent "may not survive" /clear. It did: background-agent notifications from before /clear arrive in the successor, and task output files stay under the predecessor's session dir (…/0c7eafc7…/tasks/). The handoff carried the agent id for F1 only; the 426a reviewer's id (4 rounds of context) was not carried, so the successor dispatched a fresh reviewer, which re-derived the item and found two new mediums (a fifth round). Agent ids per in-flight role belong in the manifest/item.
- O4 the successor gets a fresh scratchpad; working files the brief templates depended on (common-brief.md, common-review.md) lived in the predecessor's scratchpad. The handoff named the old path — it worked only because the scratchpad persists on the host. Stage state a successor needs must not live in a session-scoped dir, or the manifest must list it for copy.
- O5 "Read in full" lines were not honoured: the successor did NOT read the predecessor's ledger (…/claude-kit/ledger/0c7eafc7…md, checkpoint #5) nor 1222/00_initial.md in full — it grepped. Nothing enforces or checks the read list; a successor under time pressure skims.
- O6 the operator typed a long `start` argument carrying handoff facts ("F1 may have lost its agent… keep dispatch small until decision 53; no push until decision 52"). What the operator had to restate is exactly what the rehydration failed to surface up front (constraints/holds).
- O7 /clear changes the session id; the ledger is per session, so the successor started an empty ledger — the predecessor's decisions live only in its ledger file + the manifest's "Aware of". No lineage link from new ledger to old (F3a adds lineage for the manifest only).
- O8 the repo HANDOFF.md at .claude-sandbox/ is shared by every session in the checkout (14 peer sessions were live); answer 47(c) moves to per-session manifests. Until F3a/F3b land, any session's rehydrate may inject this librarian's manifest (and vice versa).
- O9 the manifest's "Next" was stale on arrival in small ways (F1 described as possibly dead; d182/220b "ready but not dispatched" — correct), but open decisions were listed well; decision numbering continued correctly from the store.
- O10 operator standards carried as "DECIDED" lines (two-line recap) were honoured — the Aware-of section works for rules; it fails for things the successor must DO first (O5, O6).
dispatch: investigator opus — spike through dev-flow investigate (orchestrated, read-only); series .claude-sandbox/investigations/5039-handoff-failures/; transcripts are private operator data: read locally, quote minimally, no values of secrets

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

## Investigation result (opus, 2026-09-22) — series .claude-sandbox/investigations/5039-handoff-failures/ (00_findings.md, INDEX.md)
16 compaction boundaries across 8 transcripts, the /clear, and one cross-session manifest resume. Top modes: (1) /clear successor gets a ~230-char header while the predecessor promised full injection [strong]; (2) hand-typed machine fields — 13/15 manifest writes across 7 sessions carry invented times (some 11–12 h future → labelled FRESH), placeholder heads [strong]; (3) holds buried in Aware-of, trimmed second, absent from header-only injection; a "pause until bedtime" hold ran 37 h [strong]; (4) /clear splits session dirs (scratchpad moves, tasks/ stays), new ledger starts at epoch 1 unlinked [strong]; (5) "Read in full" not honoured (cat/grep) [strong]; (6) per-role agent ids not carried [moderate]; (7) compaction ledger tail is mostly commit pointers (13/17 lines) [moderate]; (8) foreign manifest injected on resume — fixed by F3a [moderate]; (9) operator hand-carries opener and /compact text, TUI hard-wraps break it [strong]; (10) stale depth warning right after compaction, cause unconfirmed [moderate]. Verified: $CLAUDE_CODE_SESSION_ID follows /clear; background agents survive /clear and resume by id. Summary drift is a code-level prediction only (summaries skimmed).
Factored (librarian): H1–H7 below as children; F3b's serial 04 takes: a next_skill: field, a one-line opener naming the Read tool, printing the full path + continuation commands (answer 47), H5's predecessor lookup by lineage id.
decisions (librarian, one line each): OQ1 build H5 now against the current repo manifest (P1; F3b re-points it); OQ2 a `## Holds` section, never trimmed; OQ4 unread "Read in full" paths reminded as a line in the next prompt's context (no extra turn); OQ5 both — mark step rewrites machine fields, the hook falls back to file mtime; OQ6 the opener names the Read tool (cat does not adopt, by design).
decision 60: what a linked /clear successor is given (item H5) — (a) the full manifest plus a digest of the predecessor's ledger (reasoning lines first) [recommended: /clear in handoff mode is a continuation of the same work; F3a already links it, and header-only is what broke today]; (b) the header plus the ledger digest, full manifest only after a Read; (c) header only (today).
answer 60: (a) a linked /clear successor gets the full manifest plus a digest of the predecessor's ledger (reasoning first) (operator 2026-09-22)
