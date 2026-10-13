---
id: doctrine-degrade-disclose-hint-once-amen-bdff
title: "doctrine: degrade, disclose, hint once - amend README principle 4 and the bridge wording"
short_display_name: degrade disclose hint once doctrine
type: chore
status: done
priority: 2
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F1 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F1 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order). Waits on decision 190 (adopt the pattern).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (chore; acceptance from the 72ef series; answers 190 a / 192 a)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a0ec08ea6adf9f9a7
return: DONE worktree-agent-a0ec08ea6adf9f9a7 1c9b52d (principle 4 degrade/disclose/hint once; three bridge sentences + provider-interface fixed to match wi export/import; CLAUDE.md Peer hints convention incl. 191 a switch; added 'disclosure is never switched off'; 10/10 Checks)
dispatch: reviewer opus high — review round 1 of 1c9b52d
agent: reviewer aa6047d54d942a58c
verdict: review round 1 NEEDS_CHANGES (medium 1: Claude Code behaviour in the Peer hints convention unlabelled — cite plugins-reference and hooks docs; lows 2-5: stdout reach too broad, ralph catalog cell, disclosure vs switch wording, bridge-as-pattern clause; nits 6-9)
dispatch: implementer opus medium — fix round 1 (resume a0ec08ea6adf9f9a7)
return: DONE e172b53 (fix round 1: four citations verified by fetch and cited, settings-env reach left for 4bd4 to observe; stdout reach narrowed incl. PostModelSwitch; ralph cell; disclosure vs hint; bridge clause; nits)
dispatch: reviewer opus high — review round 2 (resume aa6047d54d942a58c)
verdict: review round 2 NEEDS_CHANGES (all nine round-1 findings fixed, citations checked against the raw pages; new low 1: an async hook's systemMessage reaches Claude, not the user — add 'only from a synchronous hook'; nit: e172b53's message misstates additionalContext's reach)
decided: 2026-10-09T07:42Z cap — finish round: the one-clause fix, amended into e172b53 with its message corrected (unmerged branch, last commit); authority answer 145
dispatch: implementer opus medium — finish round (resume a0ec08ea6adf9f9a7)
return: DONE bf286f1 (amend of e172b53: synchronous-hook clause, cited and checked; message corrected)
review: self
verdict: finish round CLEAR — diff read: the one clause and its reflow
landed: 728f156 (merge of 1c9b52d, bf286f1); Checks 10/10 OK
- 2026-10-09 done
