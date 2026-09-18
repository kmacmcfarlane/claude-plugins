---
id: context-guard-epoch-end-tokens-source-co-8588
title: "context-guard: epoch_end_tokens source comment, CLAUDE_PLUGIN_ROOT claim, data-dir pick, sweep stamp fallback"
type: chore
status: todo
priority: 4
created: 2026-09-18
updated: 2026-09-18
---

From the 3685+fe33 round-2 review (2026-09-18), low/nit: (1) lib_context.py:324 comment says top-level tokens has no writer — context_warn.py:41 writes it every prompt; pick the fresher of exact.tokens/tokens by timestamp and fix the comment; (2) install-statusline SKILL.md:69-74 says Claude Code sets CLAUDE_PLUGIN_ROOT in Bash calls — likely it is substituted in the skill text instead; verify and word accordingly; (3) ls -td | head -1 data-dir pick is a heuristic — prefer installed_plugins.json installPath like work-items does; (4) a planted .swept symlink disables the once-a-day limit — fall back to a second stamp name or accept. Lands after 3c48 moves install-statusline (re-home (2)/(3) there).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
