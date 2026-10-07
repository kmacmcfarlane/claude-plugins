---
id: research-security-f3-the-confinement-hoo-20d8
title: "research security F3: the confinement hook, with a filtered shell for local lanes"
short_display_name: confinement hook
type: feature
status: todo
priority: 2
deps:
  - research-security-bounded-live-probes-fo-ec4f
  - research-security-f2-deep-investigation-1ffd
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/caef-research-security/05_second-opinion-closing.md
  - caef answers 101, 108
---

caef serial 05 F3 (A3.1-A3.10) under answer 101 a: the web lane's shell runs only the two PDF commands; a separate local lane without web tools gets a shell behind an always-on command filter, bounded by the OS user and saying so. Transcript rules move to the conversation lane (108 a, next item).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

Acceptance added by answer 135 (carried from the security-probes plan, ec4f, finding M1, serial 09:24-32, 87): the filter admits running tools/** only while the run has no tools.reviewed/; once tools.reviewed/ exists it denies writes to tools/**; a post-freeze fixture proves a mining lane cannot write then run an unreviewed script. The build's opus review checks it.
note: 2026-10-06T02:46Z F3 is next (F1 66cc7ff, F2 3626e8b landed); per serial 08 § PB-1 its build waits on the operator-attended PB-1; kit written to the librarian's scratchpad pb1/ (pb1.settings.json log-only hooks, pb1-hook.py, paste.txt), smoke-tested
decision 160: Will you run the one attended check the confinement hook's build waits on (about 5 minutes in a throwaway session)? — options: (a) yes, now or when you choose; I give you the three steps [recommended] | (b) skip it; build without the two checks it gates | (z) decide later
  raised: 2026-10-06T02:46Z
  what: PB-1, the pre-build check in the research-security plan (serial 08): you launch one throwaway interactive haiku session with a logging-only hook, paste one prompt that has two research agents fetch a public test page, then exit; I read the log. It confirms two harness facts the confinement hook relies on: sub-agent hook calls carry the main session's id (gates A3.11), and web tools reach research agents without a tool-search step (gates A3.12)
  why now: F1 and F2 have landed; F3 is next in the plan's build order; blocks: the confinement hook build (F3), and after it the URL policy (F4)
  why ask: your-call — it needs an interactive session only you can run (the plan's ruling: operator-attended)
  context: you approved the research-security plan's cards (101-108) and its probe sessions · you run or skip the last pre-build probe
  stakes: reversible, narrow — a throwaway directory, one public test URL, no file written, no repo as cwd
  (a) run it — from the kit directory: claude --model haiku --settings <kit>/pb1.settings.json, paste the prompt, exit, tell me; I check the pass conditions and dispatch F3; a fail re-plans A3.11 or builds A3.12 without the tool-search drop, as the plan says
  (b) skip it — F3 builds A3.11 and A3.12 on untested assumptions; a wrong one means a hook that misattributes sub-agent calls or drops a needed step
  (z) decide later — F3 and F4 wait; the rest of the queue moves
  rec: (a) · basis strong — the plan rules F3 waits for it; it is one short session
  unknown: none
decision 161: What should the new plugin that holds the research confinement hook be called? — options: (a) research-guard [recommended] | (b) another name (say it) | (z) decide later
  raised: 2026-10-06T02:46Z
  what: the name of the new hook-owning plugin F3 creates (the plan chose a new plugin over extending sandbox, name provisional, e.g. research-guard, serial 05 Q1)
  why now: the build creates the plugin directory, catalog row and data directory under this name; blocks: the confinement hook build
  why ask: api-name — a plugin name is API (it names the plugin's data directory and every install), and plugin names are yours
  context: the plan left the name provisional for you · you name the plugin
  stakes: reversible, narrow before release — a rename later moves the plugin's data directory and every install
  (a) research-guard — says what it does (guards research agents) and pairs with context-guard
  (b) another name — the build uses yours
  (z) decide later — the build waits
  rec: (a) · basis partial — it follows the existing guard naming and the plan's own placeholder
  unknown: none
note: 2026-10-06 operator on decision 160, verbatim: "160 - decision skill feedback: you gave me a decision I can't act on. You haven't specified the location of paste.txt. That blocks me from doing the test now and makes me ask you where the file is in another turn. This is inefficient." (read as: not an answer — the card lacked paste.txt's absolute path and its text; the steps are re-shown complete; filed decisions-skill feedback)
decision 160: Will you run the one attended check the confinement hook's build waits on (about 5 minutes in a throwaway session)? — options: (a) yes, now or when you choose; I give you the three steps [recommended] | (b) skip it; build without the two checks it gates | (z) decide later
  raised: 2026-10-06T02:46Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: PB-1, the pre-build check in the research-security plan (serial 08): you launch one throwaway interactive haiku session with a logging-only hook, paste one prompt that has two research agents fetch a public test page, then exit; I read the log. It confirms two harness facts the confinement hook relies on: sub-agent hook calls carry the main session's id (gates A3.11), and web tools reach research agents without a tool-search step (gates A3.12)
  why now: F1 and F2 have landed; F3 is next in the plan's build order; blocks: the confinement hook build (F3), and after it the URL policy (F4)
  why ask: your-call — it needs an interactive session only you can run (the plan's ruling: operator-attended)
  context: you approved the research-security plan's cards (101-108) and its probe sessions · you run or skip the last pre-build probe
  impact: → two harness behaviours are confirmed and the confinement hook build starts · later: the confinement hook and the URL policy wait · reach: one throwaway session you run; no repo touched · undo: —
  stakes: reversible, narrow — a throwaway directory, one public test URL, no file written, no repo as cwd
  (a) run it — from the kit directory: claude --model haiku --settings <kit>/pb1.settings.json, paste the prompt, exit, tell me; I check the pass conditions and dispatch F3; a fail re-plans A3.11 or builds A3.12 without the tool-search drop, as the plan says
  (b) skip it — F3 builds A3.11 and A3.12 on untested assumptions; a wrong one means a hook that misattributes sub-agent calls or drops a needed step
  (z) decide later — F3 and F4 wait; the rest of the queue moves
  rec: (a) · basis strong — the plan rules F3 waits for it; it is one short session
  unknown: none
decision 161: What should the new plugin that holds the research confinement hook be called? — options: (a) research-guard [recommended] | (b) another name (say it) | (z) decide later
  raised: 2026-10-06T02:46Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: the name of the new hook-owning plugin F3 creates (the plan chose a new plugin over extending sandbox, name provisional, e.g. research-guard, serial 05 Q1)
  why now: the build creates the plugin directory, catalog row and data directory under this name; blocks: the confinement hook build
  why ask: api-name — a plugin name is API (it names the plugin's data directory and every install), and plugin names are yours
  context: the plan left the name provisional for you · you name the plugin
  impact: → the new plugin, its catalog row and its data folder are named research-guard · later: the confinement hook build waits · reach: every install of the plugin · undo: a rename later moves its data folder
  stakes: reversible, narrow before release — a rename later moves the plugin's data directory and every install
  (a) research-guard — says what it does (guards research agents) and pairs with context-guard
  (b) another name — the build uses yours
  (z) decide later — the build waits
  rec: (a) · basis partial — it follows the existing guard naming and the plan's own placeholder
  unknown: none
answer 160: later (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:44:46.475Z; read as: later, default wake — the next Report)
answer 161: a (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:45:01.873Z; read as: (a) the plugin is named research-guard)
