---
id: claude-kit-description-diverged-between-23bd
title: claude-kit description diverged between plugin.json and marketplace.json
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - reviewer report, item readme-catalog-missing-the-chat-plugin-a13d
---

Spotted by the a13d reviewer 2026-09-16: plugins/claude-kit/.claude-plugin/plugin.json ends '...and librarian mode for the shared agent layer' while .claude-plugin/marketplace.json's claude-kit description stops at 'upstream kit sync'. Acceptance: one wording, in both files, matching README's claude-kit line; doctrine 'one plugin, one aim' — no description gains an 'and' that joins two aims.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
Scope decided by the librarian: plugins/claude-kit/.claude-plugin/plugin.json and .claude-plugin/marketplace.json only. README.md is read-only here (item b85e edits it in parallel): pick the wording that agrees with README's existing claude-kit description line, or if neither json matches it, align both jsons to the README.
dispatch: implementer opus — rule 2 (marketplace.json / doctrine)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit 4da223e (plugin.json already had the wording; only marketplace.json changed); reviewer opus round 1 dispatched 2026-09-16 16:53:00
- 2026-09-16 done: aeb070b
- review CLEAR, no findings; landed merge aeb070b 2026-09-16 16:54:33. Reviewer note: README's claude-kit line ('Claude Code development tooling — reusable across projects.') is a different, shorter sentence; not aligned, by design — the README table is the inventory.
