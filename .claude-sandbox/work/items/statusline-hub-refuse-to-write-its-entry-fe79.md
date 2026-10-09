---
id: statusline-hub-refuse-to-write-its-entry-fe79
title: "statusline-hub: refuse to write its entry into a project's tracked .claude/settings.json"
short_display_name: hub writes tracked project settings
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T09:47Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - statusline-hub-end-the-silent-wait-behin-7dd3 review 1
---

From the 7dd3 review 1 (low 2), 2026-10-08: the dead-copy take path guards only settings.local.json, so a dead copy in a project's tracked .claude/settings.json (the old installer's --project) is replaced with the hub's machine-specific absolute path. Acceptance: decide whether tracked files are refused or said once; a test pins it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (bug)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a428d65ba07fb6f87
return: DONE worktree-agent-a428d65ba07fb6f87 6a74752 (guard extended: a git-tracked non-user settings file is refused with reason tracked on every take-the-slot path; tells the user once; installer untouched; heal's plain restore of its own entry not guarded; tests in temp dirs; 11/11 Checks)
dispatch: reviewer opus high — review round 1 of 6a74752
agent: reviewer a327c87bd6419153b
verdict: review round 1 NEEDS_CHANGES (medium 1: heal's two unguarded restores still write into tracked project files, rewriting a team's committed footer entry; medium 2: the message's 'install in your user settings' fix doesn't work there, shared outranks user — lead with --local; lows: _git_tracks lets writes through on timeout; tests leak GIT_* env into another repo's index; three docs state takeover without the exception; nits)
decided: 2026-10-09T10:07Z design — heal is guarded the same way as takeover on both restores; an explicit --project install is told to rerun --project to restore it there
dispatch: implementer opus medium — fix round 1 (resume a428d65ba07fb6f87)
return: DONE 71c8e7f (heal guarded on both restores; --project records scope and is told to rerun --project; message leads with --local and removing the dead entry; git timeout waits; GIT_* stripped in tests; docs; tracked checked first; 11/11 Checks)
dispatch: reviewer opus high — review round 2 (resume a327c87bd6419153b)
