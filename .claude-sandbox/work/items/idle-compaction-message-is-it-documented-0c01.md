---
id: idle-compaction-message-is-it-documented-0c01
title: "idle compaction message: is it documented, and did the gate see it"
short_display_name: idle compaction message question
type: spike
status: todo
priority: 2
created: 2026-10-12
updated: 2026-10-12
refs:
  - operator, chat 2026-10-12
---

Operator, 2026-10-12: sees 'Compacted while idle, before the prompt cache expired' and asks whether it is a new Claude Code feature. Acceptance: answer from public docs or observation; say which session compacted, at what fill, and whether context-guard's gate (installed version) saw and allowed it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: 2026-10-12 observed in transcripts (Claude Code 2.1.292): the line is a system informational entry written by Claude Code at four compactions — 53cd 10-08 06:41, ba47 10-08 07:12, cbfe 10-08 09:04, cbfe 10-09 13:41 — exactly the four idle auto compactions 22b2 found, each released by context-guard's old checkpoint branch; none since; the installed context-guard is 23b9bc4 (2026-10-09 08:28, before 22b2 landed); Claude Code is now 2.1.293
agent: claude-code-guide ad0d14017355b60fd — public docs and changelog check
