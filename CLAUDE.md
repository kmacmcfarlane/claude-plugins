# claude-plugins

Claude Code plugin marketplace. **The doctrine — the seven principles every plugin is
measured against, plus naming practices and the catalog — lives in [README.md](README.md).**
Read it before adding or moving anything. This file carries only the mechanics: where files
go.

Do not restate the principles here; restated rules drift.

## Repository Layout

```
plugins/
  chat/                # Skills for LLM chat sessions in web UIs
    skills/
      product-research/
  context-guard/       # Surviving the context window (hook-owning)
    hooks/             # Gate, ledger, rehydrate, gauge.json publish (+ deprecated statusline copy) + hooks.json + unit tests
    skills/
      {checkpoint,usage-report}/
      checkpoint/scripts/  # context_forensics.py (where a session's context went, from its transcript)
      usage-report/scripts/  # usage_report.py + prices.json (token-spend accounting)
  create-repo/         # Start a new repo for a thread of work, with a session launched on it
    skills/
      create-repo/     # references/launch-command.md
  dev-flow/            # Plan before you code; research into findings or a knowledge base; the librarian that takes custody of a repo
    agents/            # scribe, scout, implementer, implementer-critical, implementer-deep, planner, planner-deep, reviewer, reviewer-light, cross-checker, cross-checker-deep (the dev cycle's role workers); research-lane, research-lane-deep, research-verifier (the research family's workers)
    skills/
      {investigate,implement,dev-cycle,deep-investigation,research,research-deep,research-refine,research-prune,chain-of-verification,librarian-mode}/
      research/scripts/  # tool-preflight.sh (Step 5.1 tool check) + unit tests
      librarian-mode/scripts/  # quota_budget.py (the librarian's quota sense) + unit tests
    tests/             # test_agents.py: every agent file's model and effort pin, and its frontmatter shape
  kit-dev/             # Maintaining this kit itself
    skills/
      {create-skill,update-kit,new-project-from-template,factor-analysis}/
  operator-interaction/ # The agent-operator interface, starting with how decisions are raised and shown
    skills/
      decisions/       # references/{worksheet,rendering,replies,evidence-basis,rationale,gallery}.md
      plain-names/     # plain names for what agents mention, the id a trailing tag
      decision-page/   # a set of decisions as an answer page: assets/{index.html,cards.example.json}, references/{cards-schema,fallback}.md
  ralph/               # Unattended agent loops over a backlog
    skills/
      {backlog-yaml,backlog-entry,backlog-grooming}/
  sandbox/             # Isolated execution: claude-sandbox + the checkout/worktree convention (hook-owning)
    hooks/             # Checkout guard + hooks.json + unit tests
    skills/
      sandbox/
  statusline/          # Always-on status line footer, a statusline-hub display hook (hook-owning; hard-depends on statusline-hub)
    settings.json      # plugin settings default: subagentStatusLine (agent-panel rows)
    hooks/             # statusline (renderer), subagent_statusline (agent-panel renderer), sensor, session_start (registers the hub hook, prune) + hooks.json + unit tests
    skills/
      install-statusline/  # coworker install, hands the slot to install-statusline-hub; references/sensor-contract.md
  statusline-hub/      # The status-line slot, shared: owner-mode dispatcher + embed-mode tee + consent-only wrap mode (hook-owning; owns the statusLine entry)
    hooks/             # hub (render), registry (hooks.d, segments/), tee, owner, session_start (install, takeover, heal, refusal notice), housekeeping (prune) + hooks.json + unit tests
    skills/
      statusline-hub/  # embed recipes (ccstatusline, Starship, shell wrapper), references/hook-contract.md
      install-statusline-hub/  # installer script (install, remove, replace, wrap, unwrap, --status)
      install-statusline-hub/scripts/  # install_hub.py, the installer
  work-items/          # Repo-durable work items + the work-source provider interface
    skills/
      work-items/      # wi CLI (incl. `wi estate`, the cross-repo sweep), references/{format,provider-interface}.md, tests/
      work-items/scripts/  # wi.py, the wi CLI
      work-review/     # the on-demand cross-repo review, written from `wi estate`
```

Every plugin carries `.claude-plugin/plugin.json`; a skill directory holds `SKILL.md` plus
optional `references/`, `scripts/`, `assets/`.

## Conventions

- **Skill location**: `plugins/<plugin>/skills/<name>/SKILL.md` (never `.claude/skills/`).
- **Agent location**: `plugins/<plugin>/agents/<name>.md` — auto-loaded by the plugin system.
  Agent `.md` files define role, tools, model and effort. Task-specific context is injected via
  the Agent prompt, not baked into the definition. One role per file and one effort per file: a
  role that needs a second effort gets a second file, and the per-call `model` moves a file
  across models. `dev-flow` ships fourteen:
  - eleven role workers for the dev cycle — `scribe`, `scout`, `implementer`,
    `implementer-critical`, `implementer-deep`, `planner`, `planner-deep`, `reviewer`,
    `reviewer-light`, `cross-checker`, `cross-checker-deep` — whose frontmatter is `name`,
    `description`, `model` and `effort` only (`tools` left out: every tool);
  - `research-lane`, `research-lane-deep` (the same lane at a second effort) and
    `research-verifier`, the workers of the `research` skill family, routed by the
    `research` skill's `references/intensity-and-routing.md` § Profiles.

  Bodies come in three classes: minimal (the role only; the prompt is the brief) on ten of the
  eleven; a short read-only evidence contract on `scout`; and the research trio's full contract
  (file shape, evidence and security rules), in the body so every lane loads it by
  construction. `plugins/dev-flow/tests/test_agents.py` keeps every file's model and effort
  pin in step with its table. (The three agents that served the deprecated plan-execution
  skill were retired at Phase 3.)
- **Hook location**: `plugins/<plugin>/hooks/<name>.py` — registered in that plugin's
  `plugins/<plugin>/hooks/hooks.json`, which lists each hook under its event (`PreToolUse`,
  `UserPromptSubmit`, `SessionStart`, `Stop`, …) with a `matcher` and a `command` that names
  the script through the plugin root, `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py"` —
  never a relative path, since the command runs with no guaranteed working directory. Tests
  live in `plugins/<plugin>/hooks/tests/` and run with `python3 -m unittest discover -s tests -q`
  from the hooks dir. Hooks, status lines and `settings.json` writes belong only in the
  plugin whose stated aim is that behavior; each such plugin carries its own `hooks.json`
  with only its hooks.
- **Plugin-level tests**: tests not tied to hooks live in `plugins/<plugin>/tests/`, run with
  `python3 -m unittest discover -s tests -q` from the plugin dir.
- **Plugin registry**: `.claude-plugin/marketplace.json` — update when adding or removing a
  plugin (not when adding skills to an existing plugin). Its `name` field, `kmacmcfarlane`,
  is **frozen**: it suffixes every plugin-data directory.
- **Skill reference paths**: bare relative paths (no `./`, no `${CLAUDE_SKILL_DIR}`).
- **Cross-skill references**: a skill may point into a sibling skill of the *same* plugin by
  its backticked name right before a bare path — "the `investigate` skill's
  `references/investigation-format.md`".
  Never `../`, never a path into another plugin (there, README principle 4 applies).
- **Catalog upkeep**: any change to the shape of the marketplace updates the README catalog
  in the same commit.

## Placement rules

Where a new or moved thing goes. The full decision tree is in
[README.md § Where does a new thing go?](README.md); the short form:

1. Alters harness behavior (hooks, status line, `settings.json` writes)? → only a plugin
   whose stated aim *is* that behavior (`plugins/context-guard/` for the context system,
   `plugins/statusline/` for the status line's footer and the agent-panel rows
   (`subagentStatusLine`), `plugins/statusline-hub/` for the status-line slot and its
   settings entry, `plugins/sandbox/` for the checkout/worktree guard).
   Never attach it to a knowledge skill.
2. Pure stack/tool knowledge? → the expertise family, in its own marketplace (`expertise`,
   repo `claude-expertise`) — not this repo.
3. For web-UI chat sessions rather than a coding harness? → the `chat` family (home under
   review).
4. Otherwise, a harness capability: find its aim in the table below and use the **current
   home** column.
5. No aim fits? → new aim, new plugin. Write its catalog row first.

### Aim → home

Plugin names are **provisional** pending operator review. Every row below has landed: the
current home is the real home, and is where files go.

| Aim | Current home | Target home (planned) |
|---|---|---|
| Survive the finite context window (gate, checkpoint, rehydration, token-spend report) | `plugins/context-guard/` | `plugins/context-guard/` — **landed** (Phase 1) |
| Always-on status line (context left, plan usage, model, session name) | `plugins/statusline/` | `plugins/statusline/` — **landed** (3c48) |
| The status-line slot, shared (the owner-mode dispatcher and its hook registry; the embed-mode tee) | `plugins/statusline-hub/` | `plugins/statusline-hub/` — **landed** (F1, bfe2; owner mode F2, b28f) |
| Plan-before-code development flow, research that lands as sourced findings or a curated knowledge base, and a standing librarian that takes custody of a repo's work | `plugins/dev-flow/` | `plugins/dev-flow/` — **landed** (Phase 3) |
| Repo-durable work items / work-source interface | `plugins/work-items/` | `plugins/work-items/` — **landed** (Phase 4) |
| Isolated execution (containers; the checkout/worktree convention and its guard) | `plugins/sandbox/` | `plugins/sandbox/` — **landed** (Phase 5) |
| Unattended agent loops over a backlog ("ralph") | `plugins/ralph/` | `plugins/ralph/` — **landed** (Phase 5) |
| Start a new repo for a thread of work, with an agent session launched on it | `plugins/create-repo/` | `plugins/create-repo/` — **landed** (2c77) |
| The agent–operator interface: what agents need from the operator, in a form they can act on where it appears (first: how decisions are raised and shown; then plain names for what they mention) | `plugins/operator-interaction/` | `plugins/operator-interaction/` — **landed** (9f98) |
| Maintaining this kit itself | `plugins/kit-dev/` | `plugins/kit-dev/` — **landed** (Phase 6) |
| Stack expertise ("make Claude good at X") | the `expertise` marketplace (repo `claude-expertise`) — not this repo | moved to the expertise marketplace (local scaffold, remote pending) — **landed** (Phase 2) |
| Web-UI chat-session skills | `plugins/chat/` | family home under review |

Retired at Phase 3: the deprecated plan-execution skill under the then-`claude-kit` plugin's
`skills/`, and its `agents/`, which existed only to serve it. Retired at Phase 6: the
`claude-kit` plugin itself. All are recoverable from git history on this branch. (The separate
umbrella **repo** `kmacmcfarlane/claude-kit` is unaffected and keeps its name.)

## Librarian
Scope: whole repo (except .claude-sandbox/ and .claude/)
Checks:
- (cd plugins/context-guard/hooks && python3 -m unittest discover -s tests -q)
- (cd plugins/statusline/hooks && python3 -m unittest discover -s tests -q)
- (cd plugins/sandbox/hooks && python3 -m unittest discover -s tests -q)
- (cd plugins/work-items/skills/work-items && python3 -m unittest discover -s tests -q)
- (cd plugins/context-guard/skills/usage-report && python3 -m unittest discover -s tests -q)
- (cd plugins/statusline-hub/hooks && python3 -m unittest discover -s tests -q)
- (cd plugins/dev-flow/skills/librarian-mode/scripts && python3 -m unittest discover -s tests -q)
- (cd plugins/dev-flow/skills/research/scripts && python3 -m unittest discover -s tests -q)
- (cd plugins/dev-flow && python3 -m unittest discover -s tests -q)
Push: main
