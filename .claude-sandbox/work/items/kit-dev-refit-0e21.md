---
id: kit-dev-refit-0e21
title: Refit kit-dev after extractions (update-kit, create-skill, marketplace.json)
type: chore
status: done
priority: 3
deps:
  - context-guard-67ff
  - packs-marketplace-bdfd
  - dev-flow-8ca5
  - work-plugin-36f5
  - sandbox-autonomy-870d
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

Closes the epic: rename remaining maintainer tooling to kit-dev (create-skill, update-kit, new-project-from-template), update update-kit's repo-map for the new tree and second marketplace, replace create-skill's flat placement rule with the doctrine decision tree, finalize marketplace.json entries, and remove the dissolved claude-kit plugin.

Phase-6 follow-ups queued by earlier phase reviews (2026-09-02 overnight):
- plugins/dev-flow/skills/implement/SKILL.md:446 references "/claude-kit:update-kit" (namespace-qualified) - repoint to the kit-dev namespace; the standard retirement grep will NOT catch it (greps names, not "claude-kit:" prefixes).
- update-kit/references/repo-map.md: header still frames claude-kit as umbrella; sync target still plugins/claude-kit/skills/; edited skill list omits factor-analysis (11 of 12); claude-templates agent list shows 5 of 7 real files.
- rehydrate.py/_scan_data_dir + install_statusline.py first-sorted-match could pick the wrong dir if the same plugin is installed from two marketplaces (pre-existing pattern; context-guard review nit 3).
- ~/.claude/claude-kit/{context-gate,ledger}/ state dirs KEPT at Phase 1 - revisit here or in the final-naming pass.

## Handoff
- doing: implemented, pending review
- next: fable review, then wi done; epic closes after
- blocked: —
- learned: —

## Notes
- 2026-09-02 claimed by unknown@e7c6135255e0
- 2026-09-02 done: 2e7ea0b; fable review APPROVED; epic end state certified morning-ready
