---
id: checkpoint-continue-carries-a-standing-s-81ae
title: checkpoint continue carries a standing session mode (opener re-invokes librarian-mode)
type: feature
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T22:44Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - "peer: claude-sandbox librarian (uds 246.sock)"
---

Peer claude-sandbox librarian 2026-09-21, relaying its operator: /context-guard:checkpoint continue in a librarian-mode session produced a Step 7 opener that never re-invoked /dev-flow:librarian-mode start, so 'continue' did not visibly mean staying in librarian mode. Asks: (1) handoff-format records the active standing mode/skill (e.g. frontmatter mode_skill: /dev-flow:librarian-mode, or a Standing mode line in Doing); (2) checkpoint Step 7 opener re-invokes that skill first; (3) librarian-mode references/ending-the-session.md tells the librarian to name itself as the opener's skill. Acceptance: all three, context-guard stays free of any hard knowledge of dev-flow (the key is generic: any skill), soft pointer only.

## Handoff
- doing: implementer dispatched (opus, agent aa86565569c32d63c)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —
- peer's own item: claude-sandbox store relay-checkpoint-continue-should-carry-a-1a58
- dispatch: implementer opus — two plugins (context-guard, dev-flow) + manifest format doctrine

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Implementer result
- round 1 DONE d6bb9b3 (opus): handoff-format mode_skill: (optional, generic); SKILL 4b fills, Step 7 leads with it; rehydrate.py names it in the header on every tier except LANDED (only /-prefixed, one line, ≤200 chars) + tests (fail 3 without); ending-the-session sets it to /dev-flow:librarian-mode start.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at d6bb9b3
- acceptance 1-4 met; no-key output byte-identical to main on every tier.
- [medium] rehydrate.py:302-310,563-566 mode_skill filter lets injected prose/backtick breakout/control chars into the header as a hook-voiced order (repo-committed HANDOFF.md reaches a fresh session) → strict shape regex, drop otherwise; soften/skip on STALE; tests.
- lows: SKILL.md template vs prose + precedence with `then <next-skill>`; ending-the-session sentence splice; rewrap nits; docstring token count; commit aspect (carried in merge message).
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE 2da22ab (opus): strict ASCII fullmatch regex + 200 cap, STALE asks to confirm, tests (fail 6 without); lows a-d fixed; commit aspect declined (merge message).
- dispatch: reviewer opus — review r2 (same reviewer resumed)
