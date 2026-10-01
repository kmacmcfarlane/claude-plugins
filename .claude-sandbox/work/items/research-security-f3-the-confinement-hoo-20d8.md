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
