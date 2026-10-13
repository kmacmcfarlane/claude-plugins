---
id: research-scan-floor-bypass-and-false-hol-4c3d
title: "research scan floor: bypass and false-hold follow-ups from review round 8"
short_display_name: scan floor bypass follow-ups
type: bug
status: todo
priority: 2
deps:
  - research-security-f1-the-scan-floor-819f
created: 2026-10-02
updated: 2026-10-02
refs:
  - answer 144
---

Filed per answer 144 (further bypass forms after round 8 are follow-ups, not landing blockers). From 819f's round-8 review: (3) the plain-word '> within 300 chars' heuristic false-holds prose with a later > (e.g. 'Use the <instructions element; values > 3 are rare.', 'Set a<developer budget => fine.', 'In 2023, <assistant turns averaged 40 tokens (n > 200).'); possible fix: require the > after a [\w:-] run or a quote; (4) the spaced opener's <-in-value bypass ('< system-reminder a="<"> y', '< system a="<"> y'); (5) a markup name followed by punctuation ('x <system-reminder. y') and '<human: hi>' are not held. Acceptance: each form held or false hold cleared, with tests, linear under the property test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
