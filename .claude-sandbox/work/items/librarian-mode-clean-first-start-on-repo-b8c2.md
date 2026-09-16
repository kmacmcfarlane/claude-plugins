---
id: librarian-mode-clean-first-start-on-repo-b8c2
title: "librarian-mode: clean first start on repos without plugins/ or a store"
type: feature
status: done
priority: 2
tags: [claude-kit]
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - mcfacehead-com-67 session relaying operator, 2026-09-16; failed first start on the mcfacehead.com docs repo
---

Operator via mcfacehead-com-67 (2026-09-16): /librarian-mode start on a repo with no plugins/ tree and no work-item store stopped Rehydrate with a question; the operator's view is that invoking start IS the call to create the store. Change skills/librarian-mode/SKILL.md (+ agent-brief/review-brief refs only if they hard-code plugins/ paths): (1) Rehydrate step 1 gains a First-start clause — wi glob empty: use the installed plugin's wi.py as the normal case, not a branch-problem fallback; no store at WI_ROOT: run wi init (idempotent) and say so in one line; Troubleshooting's 'stop, creating one is the operator's call' drops for start/intake but STAYS for status (status never creates). (2) Scope becomes repo-relative: custody layer = what the repo's CLAUDE.md declares under a Librarian heading; absent that, plugins/*/skills + plugins/*/hooks + catalog + CLAUDE.md when plugins/ exists, else the documentation tree (README, CLAUDE.md, docs/, servers/) for a codeless repo. 'Never product code' unchanged. Rehydrate step 2's doctrine reading gets the matching conditional. (3) First start prints 'store created, custody layer = <resolved>' so the operator can correct scope before first intake; store creation not committed by start. Acceptance: start on a clean docs repo completes with no AskUserQuestion, creates the store, reports the custody layer; status on the same repo still reports no-store without creating. TOPOLOGY NOTE for operator at landing: this generalizes librarian-mode beyond the claude-plugins shared layer (retro said one librarian, product repos get none; a docs repo fits the anticipated two-tier profile and the operator invoked it there personally) — flag, do not block.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by librarian
- 2026-09-16 done: d0e8d6e merged to local main; review CLEAR round 2

## Review
- Round 1 (3136690): NEEDS_CHANGES — 1 HIGH: a code repo without plugins/ fell into a cascade
  gap (Critical said no layer, Rehydrate proceeded anyway) — undefined start behavior that
  could custody a product repo; 2 MEDIUM: derived scope silently dropped the doctrine
  section; wi init's own dirt (host .gitignore edit, untracked store) deadlocked the first
  Land against the clean-tree rule; 2 LOW (.work/ shadowing; declarations not clipped).
- Round 2 (2511dc5): CLEAR — fourth cascade arm: code + no plugins/ + no ## Librarian
  declaration → start DECLINES with the override hint, creates nothing (per the topology
  decision: product repos get no standing librarian); resolution ordered before init;
  doctrine restored; first-start dirt carve-out in Land + checklist (only the store and
  init's gitignore line); .work/ stores used, never shadowed; declarations clipped by
  never-product-code at resolution. Four acceptance walks pass incl. Go-service decline.
  1 low + 2 nits accepted. SKILL.md at exactly 3000 words — zero headroom; next edit funds
  itself.
- TOPOLOGY NOTE (flagged, not blocking): this generalizes librarian-mode beyond the
  claude-plugins shared layer via per-repo CLAUDE.md ## Librarian declarations. Retro said
  one librarian, product repos none; the decline arm enforces the latter, declarations are
  the deliberate two-tier extension path, and the operator invoked it on mcfacehead.com
  personally. Revert the merge if unwanted.
