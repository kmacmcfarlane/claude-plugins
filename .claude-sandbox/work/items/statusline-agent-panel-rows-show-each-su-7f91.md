---
id: statusline-agent-panel-rows-show-each-su-7f91
title: "statusline agent-panel rows: show each sub-agent's model and effort beside its context fill"
short_display_name: sub-agent rows show model and effort
type: feature
status: done
priority: 1
created: 2026-10-07
updated: 2026-10-08
closed: 2026-10-08
---

Operator 2026-10-07, verbatim: 'I'd like the status-line entries on sub-agents to show the model and effort too in addition to the context fill'. Acceptance: plugins/statusline/hooks/subagent_statusline.py renders each sub-agent row's model and effort alongside its context fill, from what the subagentStatusLine payload documents or what is observable (CLAUDE.md § Claude Code source material: observed with method and version, or the docs URL); where a field is absent, the row says nothing rather than guessing; tests.

## Handoff
- doing: fix round 1 (agent stopped mid-edit)
- next: check the worktree for uncommitted edits; resume a4bd4861771a0bec2 with SendMessage or re-dispatch fix round 1; then review round 2 (reviewer aa336218277396d92)
- blocked: —
- learned: —

## Notes
- 2026-10-07 claimed by Kyle-McFarlane@2d49f8460283
target: full statusline-agent-panel-rows-show-each-su-7f91 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-agent-panel-rows-show-each-su-7f91
budget: 2026-10-07T20:36Z build $22 — default other build
dispatch: implementer opus medium — build (status-line hook code)
agent: implementer a4bd4861771a0bec2 round 1
return: implementer DONE 56eedcb (model and effort from the documented subagent payload fields; tag dropped whole before the name; 7 tests; README and install-statusline SKILL.md row format updated)
changed:
  plugins/statusline/hooks/subagent_statusline.py and its test — model/effort tag
  README.md, plugins/statusline/skills/install-statusline/SKILL.md — row format
dispatch: reviewer opus high — review round 1
agent: reviewer aa336218277396d92 round 1
verdict: NEEDS_CHANGES round 1 at 56eedcb
findings:
  1. [medium] subagent_statusline.py:647-650 — when the tag doesn't fit, its room goes back to the description, so from 26 to 36 columns the description shows and the model/effort does not (non-monotonic); docs say the description is cut first; test :435-436 asserts the inverted case
  2. [medium] install-statusline/SKILL.md:135-139 outside Files in scope — accepted into scope (it states the row format)
  3. [low] commit subject feat: is not a house verb. subject-fix: 56eedcb added: statusline sub-agent rows - show each agent's model and effort beside its context fill
  4. [low] SKILL.md:148 — version note omits model 2.1.205 and effort 2.1.214
  5-6. [nit] numeric effort unbounded; SKILL.md:139 wrap
decided: finding 1 — drop the description whenever a non-empty tag does not fit, so model and effort outlast the description as the docs say and the operator asked; finding 2 accepted into scope — class: design
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer a4bd4861771a0bec2 round 2
stopped: 2026-10-07T20:58Z implementer a4bd4861771a0bec2 round 2 stopped by the librarian before tmux restart (operator: 'spin down open tasks'); worktree state as found; resume with SendMessage, else re-dispatch fix round 1 from the record
resume: 2026-10-08 SendMessage resumed implementer a4bd4861771a0bec2 (fix round 1) after the tmux restart
return: DONE 34a2802 fix round 1 (all six findings; effort over 6 chars drops only the effort, model kept)
changed: plugins/statusline/hooks/subagent_statusline.py, tests/test_subagent_statusline.py, skills/install-statusline/SKILL.md (round 1 fixes)
dispatch: reviewer opus high — review round 2 (resume aa336218277396d92)
verdict: review 2 CLEAR at 34a2802 (must-fix 0); lows 7 (long tag suppresses description) and 8 (version claim lacks its doc URL in the file, with Fix:)
decided: words — fix round 2 for finding 8's exact Fix: (CLAUDE.md source-material rule 2 wants the doc URL in the file; review 2 is below the cap, so no cap rule applies); finding 7 filed as a follow-up, not this change
subject-fix: 56eedcb added: statusline sub-agent rows - show each agent's model and effort beside its context fill
dispatch: implementer opus medium — fix round 2, finding 8 only (resume a4bd4861771a0bec2)
return: DONE 2962c2a fix round 2 (finding 8 Fix applied; paragraph rewrapped; nested parenthesis)
dispatch: reviewer opus high — review round 3 (resume aa336218277396d92)
verdict: review 3 CLEAR at 2962c2a (must-fix 0; nit 9 nested parenthesis declined: reads correctly)
landed: d27ce61 (merge --no-ff into main; Checks 10/10 OK; push scan clean)
- 2026-10-08 done
