---
id: context-guard-epoch-end-tokens-source-co-8588
title: "context-guard: epoch_end_tokens source comment, CLAUDE_PLUGIN_ROOT claim, data-dir pick, sweep stamp fallback"
type: chore
status: doing
priority: 4
owner: unknown@360f41058e92
claimed: 2026-09-21T18:18Z
created: 2026-09-18
updated: 2026-09-21
---

From the 3685+fe33 round-2 review (2026-09-18), low/nit: (1) lib_context.py:324 comment says top-level tokens has no writer — context_warn.py:41 writes it every prompt; pick the fresher of exact.tokens/tokens by timestamp and fix the comment; (2) install-statusline SKILL.md:69-74 says Claude Code sets CLAUDE_PLUGIN_ROOT in Bash calls — likely it is substituted in the skill text instead; verify and word accordingly; (3) ls -td | head -1 data-dir pick is a heuristic — prefer installed_plugins.json installPath like work-items does; (4) a planted .swept symlink disables the once-a-day limit — fall back to a second stamp name or accept. Lands after 3c48 moves install-statusline (re-home (2)/(3) there).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic across two plugins (context-guard, statusline)

## Implementer result
- round 1 DONE_WITH_CONCERNS 13c5348 (opus): (1) epoch_end_tokens picks the fresher of exact/top-level (ledger only; nothing that can block changed); (2) CLAUDE_PLUGIN_ROOT claim moved to the checkpoint playbook, reworded per docs; (3) HARD STOP hatch prints the running hook's own mark_checkpoint.py path; playbook snippet reads installPath; statusline owner.data_dir prefers CLAUDE_PLUGIN_DATA → install record → cache path → scan; (4) fallback sweep stamp .swept-2, skip if both planted. 18 new tests.
- dispatch: reviewer opus — rule 4
