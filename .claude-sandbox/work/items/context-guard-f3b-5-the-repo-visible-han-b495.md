---
id: context-guard-f3b-5-the-repo-visible-han-b495
title: "context-guard F3b-5: the repo-visible handoff channel, documented as nothing in the repo (answer 65 a)"
type: feature
status: done
priority: 2
deps:
  - context-guard-f3b-3-the-owner-sid-legacy-c3e1
parent: context-guard-8cc2-f3b-where-handoff-md-a49b
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - a49b; answer 65
---

Plan of record .claude-sandbox/investigations/8cc2-turn-gate-port 04 Open Question 1 / F3b-5 row; operator answer 65 (a): nothing in the repo, the manifest lives in the config dir and its absolute path is printed. Files: skills/checkpoint/references/operator-playbook.md alone. Route sonnet impl, opus review (docs only).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-f3b-5-the-repo-visible-han-b495 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-f3b-5-the-repo-visible-han-b495
dispatch: implementer sonnet — docs only under answer 65 (a); plan routes sonnet impl, opus review
agent: implementer aefc6634251c2dd06 round 1
return: implementer DONE 6303e63
changed: plugins/context-guard/skills/checkpoint/references/operator-playbook.md
dispatch: reviewer opus — rule 4 floor (impl sonnet)
agent: reviewer a9f57490722831112 round 1
verdict: NEEDS_CHANGES round 1 at 6303e63
findings:
- [high] operator-playbook.md:140-145 — handoff_path.py --path <sid> run from a Claude Code session prints the CALLER's path (CLAUDE_CODE_SESSION_ID wins, verified). Pass: say the id counts only outside a session, or give `env -u CLAUDE_CODE_SESSION_ID … --path <sid>`; point at handoff-format.md "Where it lives".
- [medium] :132-134 — rationale conflates answer 47's .claude-sandbox reason with the repo-root reason (overwriting between sessions, decision 65 option c). Pass: keep the two reasons apart.
- [medium] :136-137 — no pointer to the legacy repo HANDOFF.md as read-only transitional; "that overwrite can't happen" contradicts :179-187. Pass: one clause pointing at "An old-layout HANDOFF.md".
- [low] :143 restates handoff-format.md:47-48 — replace with the pointer; [low] :141-142 vs :199-202 — "on the same host and config dir".
dispatch: implementer sonnet — fix round 1 (resume)
agent: implementer aefc6634251c2dd06 round 2
return: implementer DONE b7fa1d4
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a9f57490722831112 round 2
verdict: CLEAR round 2 at b7fa1d4
lows carried to 93a2: the env -u form is not covered by the allow rule (say it prompts); drop internal decision ids from shipped prose.
landed: de0484c
- 2026-09-22 done: de0484c
