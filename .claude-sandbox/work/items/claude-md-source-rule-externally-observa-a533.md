---
id: claude-md-source-rule-externally-observa-a533
title: "CLAUDE.md source rule: externally observable text may be quoted, labelled (answer 175 a)"
short_display_name: allow quoting observable text
type: chore
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T19:03Z
created: 2026-10-06
updated: 2026-10-06
refs:
  - operator 2026-10-06, answer 175
---

Operator 2026-10-06, answer 175: '175a - externally observable is how I would phrase it, not just literally displayed to users'. Acceptance: CLAUDE.md § Claude Code source material rule 2's 'Quoted message text may not, observed or not' is replaced: text or values that are externally observable (shown to users, written to transcripts, passed to hooks, in status-line payloads or API responses) may be quoted, labelled with how and on which version it was observed, or the public doc URL; rule 1's internal-strings ban covers only strings the source holds that are not externally observable; prompts and system-prompt/system-reminder text stay banned whatever their source (operator's words: 'verbatim code or prompts'); cc_scan unchanged.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: full claude-md-source-rule-externally-observa-a533 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/claude-md-source-rule-externally-observa-a533
budget: 2026-10-06T19:03Z build $10 — default chore
dispatch: implementer opus medium — build (a CLAUDE.md rule)
agent: implementer a8bb4d53a834c426f round 1
return: implementer DONE 9863a42 (rules 1-2 amended; prompts stay banned; cc_scan unchanged)
changed:
  CLAUDE.md — § Claude Code source material rules 1 and 2
dispatch: reviewer opus high — review round 1
agent: reviewer a4f2e54720aae421d round 1
verdict: NEEDS_CHANGES round 1 at 9863a42
findings:
  1. [medium] CLAUDE.md:33-40 vs :19-25 — rule 2's permission names only prompts as an exception, so observable verbatim code, minified identifiers or recipes (a stack trace a user sees) and unreleased features (rule 4) read as allowed. Fix: CLAUDE.md:39-40 — "Prompts, verbatim code, minified or internal identifiers and extraction recipes stay banned (rule 1), and an unreleased feature is not described (rule 4), even where one shows up in one of those places, such as a stack trace a user sees."
  2. [low] CLAUDE.md:34-37 — inspecting the running program (debugger, heap dump, injected script) could pass as observing. Fix: CLAUDE.md:35 — add "Inspecting the running program's code or memory (a debugger, a heap dump, an injected script) is reading the source, not observing it."
  3. [low] CLAUDE.md:101 — rule 5's "verbatim material" removal would hit permitted quotes. Fix: "verbatim material" → "verbatim material rule 1 bans"
  4. [low] CLAUDE.md:42-48 — a quote next to a hint hands the reader a search anchor; optional: "the hint does not quote the text, even where rule 2 lets it be quoted elsewhere"
  5. [nit] "prompt" undefined (tool descriptions, built-in agent and command instructions, expanded slash-command prompts)
  note: under the operator's wording, internal flag and event names observable outside the source (files Claude Code writes, debug logs) are now allowed — wider than the 175 card's "user-visible messages"
cost: 2026-10-06T19:16Z build $1.49 of $10 after review 1 — must-fix 1 — prices 2
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer a8bb4d53a834c426f round 2
return: implementer DONE b49229b (1-5 fixed with the given words)
changed:
  CLAUDE.md — rules 1, 2, 3, 5 per review round 1
dispatch: reviewer opus high — resume (review round 2)
agent: reviewer a4f2e54720aae421d round 2
verdict: CLEAR round 2 at b49229b
findings:
  round 1: 1-5 FIXED
  1. [low] CLAUDE.md:37-39 — "That covers message and error text" now follows the inspection sentence and reads as referring to it. Fix: CLAUDE.md:38 — "That covers message and error text" → "Externally observable text covers message and error text"
  2. [nit] CLAUDE.md:28-29 — "built-in" limits only agent and command instructions; optional words: "Claude Code's own tool descriptions, built-in agent and command instructions, and the text a built-in slash command expands to count as prompts."
decided: one short round for low 1 and nit 2 before landing — a rule whose sentence points at the wrong antecedent gets misread; both are exact words; inside the $10 budget — class: cap
dispatch: implementer opus medium — resume (fix round 2, exact words)
agent: implementer a8bb4d53a834c426f round 3
return: implementer DONE 26eb770 (two exact wording fixes; paragraphs rewrapped)
changed:
  CLAUDE.md — rule 1 prompt gloss, rule 2 coverage sentence
dispatch: reviewer opus high — resume (review round 3)
agent: reviewer a4f2e54720aae421d round 3
