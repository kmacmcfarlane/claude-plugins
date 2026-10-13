---
id: librarian-mode-say-so-without-context-gu-64c7
title: "librarian-mode: say so without context-guard; its work-items stop"
short_display_name: librarian degrade without context-guard
type: bug
status: done
priority: 3
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F4 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F4 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
note: from 4bd4 OQ2 (2026-10-09T08:34Z): this item also carries its peer hint step (KD-2 for factor-analysis / DF-9 for librarian-mode), per .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/ INDEX.md
dispatch: implementer opus medium — build, worktree (bug; acceptance from the 72ef series; doctrine and kit-dev lint on main)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a08fd24241b7e085f
return: DONE worktree-agent-a08fd24241b7e085f 7c97d18 (Rehydrate step 5 without context-guard: one clause, handoffs every idle turn; stops cleanly without wi; edges declared in plugin.json, marketplace.json, README; 11/11 Checks; peer-hint step left for 4bd4)
dispatch: reviewer opus high — review round 1
agent: reviewer abd2cf9b58581e2ca
verdict: review round 1 NEEDS_CHANGES (medium 1: idle-turn handoff refresh misses the in-flight roster and 'every open item' is 136 writes — roster's home is the agent: lines; refresh only changed doing items, after dispatch and at each Report or landing; lows: disclose once per conversation whatever the argument, drop 'after /clear' from no-repeat; DF-9 deferral unrecorded; rule stated in four places; nits)
decided: 2026-10-09T08:59Z scope — DF-9 (librarian-mode's peer hint) stays with 4bd4's stage 2: its pointer target, the dev-cycle skill's references/bindings.md § Peer hint, is planned there and not on main; recorded on 4bd4 with its text
dispatch: implementer opus medium — fix round 1 (resume a08fd24241b7e085f)
return: DONE 2554393 (roster = agent: lines; refresh only changed doing items, after dispatch and at each Report or landing; disclosure first paragraph of each conversation; one home in step 5 with pointers; nits; message corrects DF-9's ownership)
dispatch: reviewer opus high — review round 2 (resume abd2cf9b58581e2ca)
verdict: review round 2 CLEAR (nits: an announced compact or clear runs step 5's narrow refresh while ending-the-session.md says every open item — harmless, the broader one wins; intake's first paragraph reads correctly)
landed: 8e5c7d7 (merge of 7c97d18, 2554393); Checks 11/11 OK
- 2026-10-09 done
