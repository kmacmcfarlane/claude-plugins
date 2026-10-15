---
id: forward-the-operator-s-store-location-th-a0eb
title: Forward the operator's store-location thoughts to the claude-sandbox session
short_display_name: store thoughts to claude-sandbox
type: chore
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - operator message 2026-10-15
---

Operator 2026-10-15: forward to claude-sandbox (which plans to migrate stores everywhere) the operator's 214 words (a git-ignored root store as the default everywhere, simpler without claude-sandbox; CLAUDE.md standalone rule) and the landed wi init rule (sidecar -> track; else trackInHost via CLAUDE_SANDBOX_TRACK_IN_HOST; else layout; outside claude-sandbox ask). Note: plan-03 moves stores into the .claude-sandbox sidecar, the opposite direction; 227 (folder name, this repo's move) is unanswered.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
sent: 2026-10-15T02:00Z to claude-sandbox (peer a9c783): the operator's 214 words verbatim, the landed wi init rule, decision 227 open, decision 180's words; asked how they fit plan-03 and what it needs from wi
reply: 2026-10-15T02:00Z claude-sandbox: matches the operator's words there ('./.work or ./.agents/work … they should operate separately'); its store step is paused for every repo after the pilot until its decision 115; hooper already on ./.work; needs nothing else from wi; would follow 227's name, .work by default; a nested .git store would need wi to treat it as tracked
sent: 2026-10-15T02:15Z to claude-sandbox: answer 227 verbatim, the WORK_ITEMS_ prefix, deprecated fallbacks, build filed (5f46)
reply: 2026-10-15T02:51Z to claude-sandbox on its plan 04's five points: (1) observed on main d39e0e7c: init --no-track on a moved store records ignored, keeps items; (2) planned F2 lookup and two-store warning; (3) correction: --no-track writes /<store>/ to the root .gitignore; (4) push held until F1-F4 land; (5) wi --help names WORK_ITEMS_ROOT (F1)
