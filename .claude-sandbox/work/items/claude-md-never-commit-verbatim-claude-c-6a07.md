---
id: claude-md-never-commit-verbatim-claude-c-6a07
title: "CLAUDE.md: never commit verbatim Claude Code source, prompts or strings"
short_display_name: no verbatim Claude Code source rule
type: chore
status: done
priority: 0
created: 2026-10-06
updated: 2026-10-06
closed: 2026-10-06
refs:
  - operator 2026-10-06
---

Operator 2026-10-06, verbatim: 'we need to be sure to avoid documenting any verbatim code or prompts, because distributing that would be copyright infringement. This needs to be protected with SOLID guidance in CLAUDE.md for the repo, and we should put that into a CLAUDE.md in the leaked source repo we have been referencing in the mcfacehead plugins repo as well.' Acceptance: a CLAUDE.md section in this repo that agents cannot miss: no verbatim code, prompts, strings or minified identifiers from Claude Code's source (the leaked repo, the installed bundle or binary) in any tracked file or commit message; behaviour stated as observed or documented; facts only derivable from internals hinted at, not copied; no unreleased features; a check before commit and push. The other two CLAUDE.md files are outside this librarian's Scope: relayed to the marketplace librarian.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
correction: 2026-10-06 the relay went to the marketplace session, which is the Sussex marketplace librarian (scope plugins/kappa-dev), not mcfacehead-plugins'; it declined and filed nothing; no mcfacehead-plugins session is running (ListAgents: a mcfacehead.com session only), so the mcfacehead-plugins and leaked-checkout CLAUDE.md parts go back to the operator

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: full claude-md-never-commit-verbatim-claude-c-6a07 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/claude-md-never-commit-verbatim-claude-c-6a07
budget: 2026-10-06T07:04Z build $10 — default chore
dispatch: implementer opus medium — build (a CLAUDE.md rule is an opus signal)
agent: implementer a1898c49b84063cca round 1
return: implementer DONE_WITH_CONCERNS dc0199d (40-line ## Claude Code source material section after the opening paragraph; self-check hits only rule prose; added deobfusc and internal flag/event names; identifier-shape grep noisy by design)
changed:
  CLAUDE.md — ## Claude Code source material
dispatch: reviewer opus high — review round 1
agent: reviewer a0544db499ede2489 round 1
verdict: NEEDS_CHANGES round 1 at dc0199d
findings:
  1. [high] CLAUDE.md:37-43 — the grep misses inventory rows: single-letter mangled names, internal event and env-var names (window_rules.py:122-130), quoted internal 429 text in fixtures and in window_rules.py:105-106, unparenthesised mangled constant labels (:56), and version-stamped provenance lines without the listed phrases (lib_context.py:37, 87, 1345-1346; design-rationale.md:117; operator-playbook.md:37-38; subagent_statusline.py:58-60)
  2. [medium] CLAUDE.md:41-42 — pre-push form fails with no upstream and reads empty input as clean; hides merge resolutions. Fix: CLAUDE.md:41-42 — "before a push, run the same grep over `git log -p --cc HEAD --not --remotes` instead"
  3. [medium] CLAUDE.md:44-45 — no procedure for a hit found after a commit exists
  4. [medium] CLAUDE.md:15-17, 24-27 — scoped by source, so prompt or system text seen in context could be committed as "observed"; silent on observed strings the code must match
  5. [medium] CLAUDE.md:31-32 — "unreleased" misses features shipped but switched off; no way to establish release status
  6. [medium] CLAUDE.md:28-30 — the content-free hint has no example or edges
  7. [low] CLAUDE.md:42 — "four phrases", the pattern has five. Fix: CLAUDE.md:42 — "catches the five phrases"
  8. [low] CLAUDE.md:37,41 — the message check assumes git commit -F
  9. [low] CLAUDE.md:17 vs 33 — issue and PR text unchecked
  10. [low] CLAUDE.md:5 — "only the mechanics" no longer true
  note: the section names a leaked source checkout in a public file; pushed store items already hold forbidden material (e347 item line 16; context-guard exact-depth item line 61)
cost: 2026-10-06T07:17Z build $1.76 of $10 after review 1 — must-fix 6 — prices 2
decided: rulings for the fix round, each inside the operator's stated rule (verbatim words, answers 163, 164) — class: reading
  4: verbatim prompt, system-prompt and system-reminder text is forbidden whatever its source, context included; a short machine value the code must match (an error code, a field or env-var name a user sees) is allowed, labelled observed with version; quoted internal message text is not
  5: unreleased = not in the public docs and not observable in normal use on a public release; a feature present but switched off counts as unreleased; when unsure, it is unreleased
  6: a hint may name the topic in plain words only — no location, identifier, value, file or search anchor — and no hint is left about an unreleased feature; one example in the section
  3: a hit found after a commit and before a push: the branch is rebuilt as dev-cycle's secret rule rebuilds it, never a fix commit on top; a hit already pushed goes to the history-scrub path (operator, 4151)
  1: the check covers shapes it can (single-letter called names, unparenthesised short labels next to provenance words, version-stamp provenance lines for a read) and a local untracked deny-list file the agent maintains for exact internal strings, at a path outside every tracked tree; reading the diff stays required; provenance is decided by reading
  public naming: the section says "any copy of Claude Code's source, leaked or installed" without naming a specific checkout
  store: the scrub (e347) and the history scrub (4151) cover pushed store items too
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer a1898c49b84063cca round 2
return: implementer DONE_WITH_CONCERNS 461bbee (1-10 fixed; cc_scan function with shape greps, local deny-list, reading; deny-list starts empty; internal event names caught only by the deny-list and reading)
changed:
  CLAUDE.md — section rewritten to the round-1 rulings; opening sentence amended
dispatch: reviewer opus high — resume (review round 2)
agent: reviewer a0544db499ede2489 round 2
verdict: NEEDS_CHANGES round 2 at 461bbee
findings:
  round 1: 1, 2, 4-10 FIXED; 3 PARTIAL
  1. [high] CLAUDE.md:80-85 — the rebuild boundary is "after a commit, before a push" and omits the cited secret rule's step 1 reach check; the pre-push scan runs on shared main (9 unpushed commits from several items), so a literal reader would flatten main. Fix: CLAUDE.md:80-85 — "Found while it is still only on its own unmerged branch: rebuild that branch the way `plugins/dev-flow/skills/dev-cycle/references/fix-loop.md` § A leaked secret does (its step 1 reach check first, then a soft reset to the merge base and one clean recommit), never a fix commit on top; found once it is merged into another branch (local main included) or pushed: stop and hand it to the operator — scrubbing that history is the operator's path, tracked as work item `history-scrub-purge-claude-code-bundle-d-4151`."
  2. [medium] CLAUDE.md:67, :60 — a missing deny-list (fresh clone, other machine, run outside the repo) is skipped silently. Fix: CLAUDE.md:67 — warn on stderr when missing or empty, and strip blank lines before grep -F -f
  3. [low] CLAUDE.md:67 — a deny-list of only blank lines floods under the harness grep (ugrep)
  4. [low] CLAUDE.md:73 — the pre-push scan reads HEAD, not the ref being pushed
  5. [low] CLAUDE.md:70-71 — MSG unset: the message is silently not scanned
  6. [low] CLAUDE.md:36-39 — the hint's topic is unbounded and can assert an internal-only fact
  7. [nit] CLAUDE.md:83 over the wrap width
cost: 2026-10-06T07:34Z build $4.22 of $10 after review 2 — must-fix 2 — prices 2
decided: low 6 — a hint's topic names a behaviour a user can see (e.g. when a window warning fires), never an internal mechanism, component or feature; low 4 — the pre-push scan names the ref being pushed — class: reading
dispatch: implementer opus medium — resume (fix round 2)
agent: implementer a1898c49b84063cca round 3
return: implementer DONE f593e40 (round-2 1-7 fixed; warnings on missing/blank deny-list, outside a repo, empty MSG; pre-push names the ref; hint topic is user-visible behaviour)
changed:
  CLAUDE.md — round-2 fixes
dispatch: reviewer opus high — resume (review round 3)
agent: reviewer a0544db499ede2489 round 3
verdict: CLEAR round 3 at f593e40
findings:
  round 2: 1-7 FIXED
  1. [low] CLAUDE.md:70 — a CRLF deny-list entry silently misses under GNU grep
  2. [low] CLAUDE.md:84 — no pipefail: a failed git log feeds empty input and the scan looks clean
cost: 2026-10-06T07:43Z build $5.55 of $10 after review 3 — must-fix 0 — prices 2
landed: 86a0227
- 2026-10-06 done: 86a0227
correction: 2026-10-06T16:36Z the rule's "Quoted message text may not, observed or not" came from my ruling 4 in the round-1 fix, an over-reach of the operator's words ("verbatim code or prompts"); a message Claude Code shows the user is observable output, not source; the operator challenged it (on decision 167); raised as decision 175
decision 175: Should the copyright rule allow quoting a message Claude Code shows to users (an error or warning), labelled as observed or documented, while still banning internal strings users never see? — options: (a) yes: user-visible message text may be quoted, labelled with its source and version [recommended] | (b) no: keep banning all quoted message text | (z) decide later
  raised: 2026-10-06T16:36Z
  what: the last sentence of CLAUDE.md § Claude Code source material rule 2 ("Quoted message text may not, observed or not")
  why now: it decides two scrub-plan choices (167, 169); blocks: the scrub build's latch design
  why ask: rule-change — it is your copyright rule, and I wrote that sentence by my own ruling, beyond your words
  context: you asked why quoted message text is banned when it is observable · you decide whether the rule bans it
  impact: → the gate may match the credits error by its user-visible text, cited to the public errors page, and keep today's 200K hard stop after it · later: the scrub build waits on 167 and 169 · reach: everything committed to this repo · undo: an edit to CLAUDE.md
  (a) allow user-visible messages — internal strings never shown to users stay banned; a quoted message carries "observed on <version>" or the doc URL — reach: this repo's committed text — undo: an edit
  (b) keep the ban — the gate recognises the error by machine values only and only warns after it (167 a, 169 c)
  (z) decide later — the scrub build waits
  rec: (a) · basis partial — your rule targets copying source; a message every user sees is behaviour, and the errors page documents it
  unknown: whether the transcript holds the message text in full (it lacks the documented prefix on 2.1.274; the rest is unobserved)
