---
id: statusline-hub-f5-wrap-mode-run-a-foreig-7e71
title: "statusline-hub F5: wrap mode (run a foreign status line inside the hub, with consent)"
type: feature
status: doing
priority: 2
deps:
  - statusline-hub-f2-owner-mode-hooks-d-reg-b28f
parent: spike-status-line-multiplexer-dependency-d193
owner: unknown@360f41058e92
claimed: 2026-09-21T23:45Z
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F5 / 03 F2. Operator decision 40 (b): ASK once on first run when a foreign statusLine exists, so the user knows they were wrapped. Unwrap restores the original entry exactly.

## Handoff
- doing: implementer dispatched (opus, agent af08fa66aa946f79c)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — settings ownership (wrap/unwrap a foreign statusLine) + executable logic; fable signal: fable unavailable, fallback

## Implementer result
- round 1 DONE_WITH_CONCERNS 627b1fd (opus): wrap.json record (manifest trust rules, survives data-dir deletion); write_settings expect_entry/raw (byte-exact unwrap); detached runner (5 s kill, last-good cache); first run asks once, never wraps; stale write-backs re-wrapped (consented) / after unwrap undone; installer --wrap/--unwrap/--unwrap --replace; 24 tests (fail 23 on main). Deviations: record in wrap.json not owner.json; slow commands shown next render; output unsanitised (user's own renderer), 16 KiB cap. Open: CLAUDE.md installer line; assumed /bin/sh -c; uninstall while wrapped leaves the user's line blank until reinstall.
- dispatch: reviewer opus — rule 4; fable signal (settings ownership, runs a user command): fable unavailable, fallback

## Review round 1 — NEEDS_CHANGES (opus) at 627b1fd
- /bin/sh -c verified against 2.1.278 (shell:true, session cwd, payload on stdin, env + CLAUDE_PROJECT_DIR/COLUMNS/LINES); consent otherwise holds; trust rules hold; byte-exact unwrap holds; runner holds.
- [high] wrap not scoped: wrap.json is config-wide, so a project/local-scope --wrap runs that project's command in EVERY session (reproduced: project A's `sh ./sl.sh` ran B's sl.sh); first-run offer suggests --project --wrap for a repo-committed command; owner.json repointed to A's file. Fix: run only when the wrapped file applies to this session, or user-scope-only --wrap; test.
- [medium] lost-marker adoption silently re-runs a wrap the user undid → adopt as wrapping only when running is already true; else unwrapped + restore; test.
- [medium] uninstall while wrapped blanks the user's line, entry only in wrap.json → at least say "--unwrap before uninstalling" in the success message + SKILL; better a documented recovery.
- lows: colour bleed (RESET between inner output and segments); CLAUDE_CODE_SHELL_PREFIX ignored; CLAUDE.md layout lines.
- dispatch: implementer opus — fix round 1 (same agent resumed; fable-signal fallback)
