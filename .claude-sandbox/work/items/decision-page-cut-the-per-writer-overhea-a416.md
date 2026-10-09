---
id: decision-page-cut-the-per-writer-overhea-a416
title: "decision-page: cut the per-writer overhead of writing a page (shared digest, fewer writers, fewer turns)"
short_display_name: decision page writer overhead
type: chore
status: todo
priority: 2
created: 2026-10-09
updated: 2026-10-09
refs:
  - operator message 2026-10-09
---

Operator 2026-10-09 asked why the 22-card page cost so much. Measured (subagent transcripts, this session): 5 opus writers, 18-29 turns each, peak context 143k-201k, 13.1M cache-read and ~785k fresh input tokens in all (~$7-9 at Opus 5.5 list on the input side; output not reliably recorded in transcripts). Each writer starts at ~44k (system prompt, every tool, CLAUDE.md, skill list) and re-reads the same ~25k of decision-page SKILL.md, schema and example, then the plan series; the card text itself is ~27k tokens across all 22. Acceptance: SKILL.md Step 2 gives the writer a compact digest of the fields and rules (or the caller passes one), a writer handles a whole page or large groups so shared reading is paid once or twice, reads are batched in few turns, and the check-and-fix loop edits rather than rewrites the build file; measured before and after on the same page.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
findings: carried — from 1e00 review 2: rewrap rulings.md:65 and cards-schema.md:248
note: measured 2026-10-09T08:57Z — one writer for 7 cards: 10 turns, ~132k peak context, reads batched, the file written once and edited (open-decisions page); last night's 5 writers for 22 cards: 18-29 turns and 143-201k each, 13.1M cache-read in all. The skill change should make one writer the default.
