---
id: librarian-mode-75-sop-follow-up-wording-d72e
title: "librarian-mode 75% SOP: follow-up wording from review"
type: chore
status: doing
priority: 3
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:32Z
created: 2026-09-18
updated: 2026-09-19
refs:
  - reviewer report, item librarian-mode-at-75-context-checkpoint-ce46
---

From the ce46 re-review 2026-09-18 (all low/nit): (10) ending-the-session.md names the advisories by the '[claude-kit context gate]' prefix — after the plugin-factoring merge the gate prints '[context-guard context gate]'; match by the advisory bodies only; (11) 'store-only — the work-item store and the manifest': .claude-sandbox/HANDOFF.md is neither tracked nor ignored and handoff-format.md says trackInHost governs it — commit the manifest only when trackInHost tracks it; (12) drop 'reads the status-line gauge' (the model cannot see it; the advisory latches and arrives on the next prompt) or say read the gate state file; (13) 'the one time the push precedes its Report' is now false (75% does too). Lands on the factored layout after the merge.

## Handoff
- doing: bundled in worktree d72e
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — bundled chores in worktree d72e; >3 files (rule 2)

impl (bundle): DONE 7ace960 (all five; none pre-fixed). Open: agent-brief Commit verbs omit "fixed" (main history uses it).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (bad-subject correction "carried in the merge message" but Land merge has no -m slot); lows 2 (agent-brief declines any severity vs fix-loop low/nit), 3 (SKILL.md push-before-Report at 75% missing), 4 (wrap), 6 (verb list lacks fixed: -> filed separately); nit 5 (ls stderr).
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 51a6789 (1-5 fixed; declined 6 = filed a638).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): NEEDS_CHANGES — medium 1 (push clause omits DUE; DUE fires at 65% on 200K windows; budget allows it), 2 (always-low subject rule has no carve-out for a leaked secret); low 3 (merge -m body needs a blank line), nit 4.
dispatch: implementer opus fix round 2 — resume (mediums only; no fable escalation under f696)

fix round 2 (opus): DONE 32880e2 (1-3; declined nit 4 = budget).
dispatch: reviewer opus review round 3 — resume

review round 3 (opus): NEEDS_CHANGES — 1-3 FIXED, 4 declined OK; new medium 5 (re-review template has no merge-base slot after a secret rebuild), 6 (secret decision must name location/key, never value); lows 7 (rebuild base unnamed in agent-brief), 8 (SKILL review step 4 vs rotation decision), nit 9 (rebase prohibition).
dispatch: implementer opus fix round 3 (last before cap 4) — resume; mediums only -> no fable escalation

fix round 3 (opus): DONE c88ab03 (5-9 fixed, SKILL.md unchanged).
dispatch: reviewer opus review round 4 (final) — resume

review round 4 (opus, final): NEEDS_CHANGES — 5-9 FIXED; new medium 10: review-checklist.md:20-22 § 1 "no amend, rebase or squash of a reviewed commit" contradicts the sanctioned secret rebuild (reset --soft + recommit) -> Land check would fail after a rebuild; low 11: "never quote" covers findings only, not verbatim TESTS output of git log subjects. CAP HIT (4).
decision 35: d72e cap: (a) one extra round for the one-clause § 1 exception, re-review, land; (b) land now, fold finding 10 into b2ad (same secret-rebuild area).

OPERATOR 2026-09-19: decision 35 a — one extra review round for finding 10 (one clause), then land.

dispatch: implementer opus fix round 4 (extra, decision 35) — resume

fix round 4 (extra, opus): DONE 3a0db89 (10 + 11).
dispatch: reviewer opus review round 5 (extra, final) — resume
