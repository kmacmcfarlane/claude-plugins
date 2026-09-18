---
id: detect-a-gitignored-or-untracked-work-it-8efe
title: detect a gitignored or untracked work-item store; one shared ignore-shape helper
type: spike
status: doing
priority: 2
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:24Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer Paseo stop-gap (agents repo); operator-attention e5516d2
---

Peer 'Paseo stop-gap' (agents repo), 2026-09-18, retrospective on the 7f00 class. Ask: judge whether it's worth (1) wi lint and the wi prime header warning when the store root is git check-ignore'd or has zero tracked files while holding items; (2) test_wi.py covering private, sidecar and already-ignored shapes, including the 'store exists but ignored' state; (3) one shared shape-classification helper instead of per-tool re-implementations, plus a 'who may write a host .gitignore' rule in agents decision 0002. Siblings: 7772 (wi add recurrence), 37d3 (config.yaml un-ignore), claude-sandbox a7bf. Acceptance: a recommendation per point, then features filed. Held until plugin-factoring merges.

## Handoff
- doing: in review/fix loop in worktree (see item body)
- next: review -> land
- blocked: —
- learned: —

## Librarian decision (2026-09-18)
- Point 1: build it. `wi prime` header and `wi lint` warn when the resolved store root is inside a git repo and either `git check-ignore -q <store>/items` succeeds, or the store holds items but `git ls-files <store>` lists none. The warning names the cause class and the remedies (remove the whole-dir ignore, trackInHost: true, or the claude-sandbox launcher fix 18a7). Skip silently outside git, or when git is unavailable. Sidecar stores (the store sits in its own nested repo) are fine: check against the repo that contains the store.
- Point 2: done by 7772 (a sweep over all 17 subcommands with a coverage guard). Add tests for the new warning only.
- Point 3: the shared shape helper and the "who may write a host .gitignore" rule live in the agents repo (decision 0002) and the claude-sandbox launcher (18a7, which follows CS-LAY-018). Not this repo's to change. Recommendation relayed to the peer: the launcher's refusal (18a7) is the single writer that matters. wi's classifier stays local.
dispatch: implementer opus — executable logic (wi.py)

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

impl: DONE_WITH_CONCERNS 65344d7 (check-ignore on items + a would-be item path; ls-files only at >=10 items; lint exits 3; prime header-trim fix)
dispatch: reviewer opus — rule 4

- 2026-09-18: 18a7 landed (claude-sandbox 490d8ca). If this item takes a fix round, reword the remedy "update the claude-sandbox launcher (its item 18a7)" to "a claude-sandbox launcher at 490d8ca or later warns about this".
