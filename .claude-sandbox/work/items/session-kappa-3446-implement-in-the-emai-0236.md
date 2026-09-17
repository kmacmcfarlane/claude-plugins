---
id: session-kappa-3446-implement-in-the-emai-0236
title: session 'kappa-3446 implement' in the email agent keeps dying — suspected plugin-refactor hook
type: bug
status: done
priority: 1
created: 2026-09-17
updated: 2026-09-17
closed: 2026-09-17
refs:
  - operator message 2026-09-17
---

Operator 2026-09-17: their session named 'kappa-3446 implement' in the email agent (sussex communications/email repo) keeps dying; suspects changes from the plugin refactor (marketplace switched today to branch plugin-factoring 996b5ea: context-guard, sandbox incl. PreToolUse checkout guard, work-items, kit-dev, dev-flow, ralph, chat; claude-kit uninstalled) and a hook firing. Diagnose read-only: find the session, the failure mode, the hook responsible, and the fix. Product code is out of scope — only our hooks/skills.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: diagnostician opus — read-only log and transcript forensics

## Diagnosis (2026-09-17; findings copied to .claude-sandbox/investigations/email-session-deaths-findings.md)
- Not our plugins. The email sandbox container is OOM-killed (host docker events: 16:30:11 oom, 16:30:18 die exit=137)
  whenever `make test-unit` runs `ginkgo -r --race` across all packages in parallel; .claude-sandbox/config.yaml
  there sets memoryLimit 16g, swap off, 24-CPU host. Every attributable death lines up with a test-unit run.
- That config dir never switched marketplaces: it still runs claude-kit only (auto-updated to main 287b448), no
  double hooks; 237 hook runs all exit 0; no gate blocks, no deferred compaction (context 54%).
- Operator workaround: cap parallelism (e.g. GOFLAGS=-p=4 ginkgo -r --race --compilers=4 …) or raise memoryLimit
  (~24g; host 32 GiB with other sandboxes ≈5 GiB — capping is safer).

## Notes
- 2026-09-17 done: not a plugin defect: container OOM from parallel race-enabled test build
