# Planned Improvements

## Adopt SendMessage for reject-retry loops

**Status**: Blocked — requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (experimental, not stable as of v2.1.146).

**What it enables**: On reject, resume the SAME implementer via `SendMessage(to: agentId)` instead of spawning fresh. The resumed agent retains full conversation history (all prior tool calls, results, reasoning), which means:
- No need to re-read the plan file
- No need to re-read shared context
- No need to re-include prior IMPLEMENTER_REPORTs and REVIEW_VERDICTs in the prompt
- Faster iteration, less token waste

**Current workaround**: Spawn a fresh implementer with all prior context stuffed into the prompt. Works but is token-heavy and loses the agent's working memory.

**When to adopt**: Once `SendMessage` is available without the experimental flag (watch [anthropics/claude-code#35240](https://github.com/anthropics/claude-code/issues/35240) and the [agent teams docs](https://code.claude.com/docs/en/agent-teams)).

**Migration**: In SKILL.md step 3c, change the REJECTED handler from "spawn fresh with full context" to:
```
SendMessage(to: [implementer agent id], message: "Your changes were rejected. Attempt [N]/3.
[REVIEW_VERDICT block]
Fix the issues. Re-run tests. End with IMPLEMENTER_REPORT.")
```

## Worktree reliability

**Status**: Monitoring — `isolation: "worktree"` has known bugs around branch reuse ([#51596](https://github.com/anthropics/claude-code/issues/51596)) and silent failures ([#39886](https://github.com/anthropics/claude-code/issues/39886)).

**Mitigation**: The orchestrator should verify worktree creation succeeded (check that the returned branch/path exist) before treating the task as running. If worktree creation fails silently, fall back to running the task without isolation and warn the user.

**When to revisit**: These issues are actively being worked on. Check the issue tracker periodically.
