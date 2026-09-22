---
id: statusline-hub-segments-d182-review-lows-5cde
title: "statusline-hub segments: d182 review lows"
type: chore
status: done
priority: 3
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - d182 review r1
---

From d182 review r1 (CLEAR) 2026-09-22: producer temp files (mkstemp dot-files) not matched by prune's _TMP shape → never pruned, block rmdir; prune-vs-producer races (inode compare before unlink; § 11 tells producers to retry on FileNotFoundError); fit_line ignores the health glyph's width; README names-are-API + owner-mode bullets, CLAUDE.md layout 'registry (hooks.d)' and install-statusline-hub --status wording should mention segments/; nits: § 11 safe_sid wording ('a safe token'), scan_segments checks the dir before hub_problem(); verify Claude Code sets COLUMNS for the status-line command.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full statusline-hub-segments-d182-review-lows-5cde /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-hub-segments-d182-review-lows-5cde
dispatch: implementer opus — executable logic (statusline-hub hooks) + README/CLAUDE.md layout
agent: implementer ad7d3f4f757fdc85e round 1
return: implementer DONE cd313ea
changed: statusline-hub hooks/{housekeeping,hub}.py, hooks/tests/test_segments.py, skills/statusline-hub/references/hook-contract.md, skills/install-statusline-hub/{SKILL.md,scripts/install_hub.py}, README.md, CLAUDE.md
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a56df1deb2fecdbcd round 1
verdict: CLEAR round 1 at cd313ea
landed: ba0f218
- 2026-09-22 done: ba0f218
