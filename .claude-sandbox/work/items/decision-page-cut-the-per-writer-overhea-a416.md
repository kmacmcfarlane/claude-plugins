---
id: decision-page-cut-the-per-writer-overhea-a416
title: "decision-page: cut the per-writer overhead of writing a page (shared digest, fewer writers, fewer turns)"
short_display_name: decision page writer overhead
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T08:57Z
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
dispatch: implementer opus medium — build, worktree (chore; no plan)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
return: DONE worktree-agent-a5aa638c006bd182a b12ad40 (Step 2 'Write it cheaply'; new references/writer-digest.md with test_digest.py pinning fields, lint keys both ways and follow; carried rewraps; operator-interaction 123; reported 10 Checks, kit-dev's not listed)
dispatch: reviewer opus high — review round 1 of b12ad40
agent: reviewer af1922219a541a7ad
verdict: review round 1 NEEDS_CHANGES (medium 1: Step 2 still points the writer at the schema and example; medium 2: the digest's act row lacks the secret rule and the non-empty rule; medium 3: the same-page before/after measurement is not done; minors 4-10: digest gaps, impact effect rule, rev reason, printed lint prefixes, test reach, path wording, page-size test; nits 11-12)
decided: 2026-10-09T09:14Z scope — finding 3: no extra page is written just to measure; the change lands, and the item stays open until the next page written under it records turns and peak context against the 22-card baseline (same writer setup, a comparable page)
dispatch: implementer opus medium — fix round 1 (resume a5aa638c006bd182a)
return: DONE 8f65102 on merge 366b1fa (Step 2 points at the digest; act secret rule; digest gaps; line-start column; test_digest pins keys, Required cells, thresholds, follow, with mutations; 11/11 Checks, operator-interaction 127; its scan used the shared scratchpad scan.sh, which another agent had overwritten, so the reviewer reruns cc_scan)
dispatch: reviewer opus high — review round 2 (resume af1922219a541a7ad)
