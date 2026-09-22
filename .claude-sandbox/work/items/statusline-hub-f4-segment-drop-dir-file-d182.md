---
id: statusline-hub-f4-segment-drop-dir-file-d182
title: "statusline-hub F4: segment drop dir (file-drop providers)"
type: feature
status: done
priority: 3
deps:
  - statusline-hub-f2-owner-mode-hooks-d-reg-b28f
parent: spike-status-line-multiplexer-dependency-d193
created: 2026-09-21
updated: 2026-09-22
closed: 2026-09-22
---

d193 07 § F4 (03 F1's contract under CFG/statusline-hub/segments/). Optional; producers: context-guard labels, operator-attention identity chip, claude-sandbox chip.

## Handoff
- doing: worktree ready, not yet dispatched (paused for 1222)
- next: dispatch implementer (opus) after 1222's investigation and the model switch back to opus
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
- dispatch: implementer opus — hub code, new producer contract (doctrine: cross-plugin data channel)
- 2026-09-22: worktree fast-forwarded to main 488ffe2+ (0 commits of its own); answer 53 lifts the hold. dispatch: implementer opus — hub code, new producer contract
- impl r0 DONE fc76e6d (opus): segments read in registry.py (4 KiB, 16 providers, 40 cols, sanitised, fg names, expires_at or 24 h / 30 d, hooks.d trust rules, never run), hub.py arrange/fit (COLUMNS drops segments by priority only), housekeeping prune, --status lists, hook-contract § 11; 22 tests fail on main; median render 17.4 → 18.0 ms at 16 providers; line byte-identical with no dir. OQs: producer items (context-guard labels, attention chip, sandbox chip); embed-mode tee prints no segments; staleness/colour defaults are the implementer's.
- librarian: staleness defaults (24 h / 30 d) and the colour list accepted as v1 defaults — no producer exists yet, and the contract doc is where a later change lands; producers and tee --segments filed after landing.
- dispatch: reviewer opus — hub code + cross-plugin contract (rule 4)
- review r1 (opus) at fc76e6d: CLEAR. Byte-identical line without segments (COLUMNS unset/10/200/garbage); hostile files each cost only their own segment; sanitiser strips OSC-8/CSI/C1/bidi; 40 providers ≈0.35 ms. Lows: producer mkstemp temps not matched by the prune's _TMP shape; prune-vs-producer races (inode compare; retry on FileNotFoundError); fit_line ignores the health glyph width; README names-are-API + owner-mode bullets, CLAUDE.md "registry (hooks.d)" and install-statusline-hub --status wording omit segments/; nits: safe_sid wording, scan order. OQ: whether Claude Code sets COLUMNS for the status-line command (unverified).
- Review result: 1 review round, 0 fix rounds; lows filed by the librarian as a follow-up (author's call deferred, none medium+); impl opus, review opus.
- land checks (librarian, worktree fc76e6d): seven suites OK; diff read — 7 files, all in scope.
- 2026-09-22 done: 6966be3
