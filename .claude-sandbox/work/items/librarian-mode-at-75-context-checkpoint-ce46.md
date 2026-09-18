---
id: librarian-mode-at-75-context-checkpoint-ce46
title: "librarian-mode: at 75% context, checkpoint (continue) and prompt the operator to compact"
type: feature
status: doing
priority: 1
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T07:45Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - operator message 2026-09-18
---

Operator 2026-09-18: standard operating procedure for a librarian session whose context reaches 75% used: (1) put every open item's handoff in order (existing Ending-the-session rule), (2) push main per the push rule, (3) run the checkpoint skill with goal = continue, (4) end the turn prompting the operator to run /compact (at their convenience, e.g. the next morning) rather than compacting itself or starting new work; the checkpoint makes the compaction safe and the rehydration hook re-injects the manifest. The 75% trigger reads the status-line gauge / the context-gate advisory band (the gate already emits a 75% advisory). Acceptance: the rule is stated where a librarian will see it at the trigger (the 75% advisory arrives mid-session, so SKILL.md must carry at least a one-line trigger with a pointer to the procedure in references/ending-the-session.md); SKILL.md stays <= 19,000 chars (currently 18,969: pay with a duplication-only trim or put the procedure in the reference); Critical/Route/Red flags byte-identical. Land on main (the plugin-factoring branch carries it at merge via rename detection).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (the librarian's own procedure / doctrine)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009
