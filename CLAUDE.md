# claude-plugins

Claude Code plugin marketplace. **The doctrine — the seven principles every plugin is
measured against, plus naming practices and the catalog — lives in [README.md](README.md).**
Read it before adding or moving anything. This file carries only the mechanics: where files
go, and what may never be committed.

Do not restate the principles here; restated rules drift.

## Claude Code source material

This repo is public. Read this before you write, commit, push or post anything that touches
Claude Code's behaviour.

1. **Never commit Claude Code's source.** From any copy of Claude Code's source, leaked or
   installed (the bundle or binary included), none of the following goes into any tracked
   file, test fixture, commit message, work-item text pushed with the repo, or issue or PR
   text:
   - verbatim code, or internal strings: message or error text, and flag and event names,
     that the source holds and that are not externally observable. Text that is externally
     observable is not internal; rule 2 says what that is and how to label it;
   - minified or internal identifiers (short mangled function names, internal variable and
     constant names), including as a label in a comment that maps our code to theirs;
   - extraction recipes, such as a grep of the bundle, a byte offset, or an anchor to
     search for.

   Verbatim prompt, system-prompt and system-reminder text is forbidden whatever its
   source, observable or not, the text in your own context included: seeing it in your own
   context is not external observation. Claude Code's own tool descriptions, built-in agent
   and command instructions, and the text a built-in slash command expands to count as
   prompts.
2. **State behaviour as observed or documented.** Observed: say how it was observed (a
   status-line payload, a transcript, a hook's environment, a test run) and on which Claude
   Code version. Documented: give the public URL. Never write "read from the binary", or
   any other internals, as a source. Text and values that are externally observable may be
   quoted or written. Externally observable means observable from outside Claude Code's
   source: shown to users, written to transcripts, passed to hooks in their input or
   environment, in status-line payloads, in API responses, or on a public doc page.
   Inspecting the running program's code or memory (a debugger, a heap dump, an injected
   script) is reading the source, not observing it. Externally observable text covers
   message and error text as well as short machine values the code must match (an error
   code, a field or env-var name). Each is labelled with how and on which Claude Code
   version it was observed, or with the public doc URL. Prompts, verbatim code, minified or
   internal identifiers and extraction recipes stay banned (rule 1), and an unreleased
   feature is not described (rule 4), even where one shows up in one of those places, such
   as a stack trace a user sees.
3. **A fact only the internals show is not written down.** In its place you may leave a
   hint that it can be derived from Claude Code's internals, so agents know to consult the
   source themselves. The hint's topic is a behaviour a user can see, such as when a
   warning fires, never an internal mechanism, component or feature, and it is named in
   plain words only: no location, identifier, value, file or search anchor, and the hint
   does not quote the text, even where rule 2 lets it be quoted elsewhere. For example,
   "when this warning fires can be derived from Claude Code's internals" is a hint; naming
   the function that decides it, or its threshold, is not. No hint is left about an
   unreleased feature.
4. **Never describe an unreleased feature.** Unreleased means not in the public docs and
   not observable in normal use on a public release. A feature that is present but switched
   off is unreleased. When unsure, treat it as unreleased.
5. **Check before every commit, every push, and every issue or PR text you post.** The
   check has three parts, and the grep only surfaces candidates: whether a line is observed
   or internal is decided by reading it.
   - **Shape greps.** `cc_scan` below prints every line holding one of the five phrases
     `bundle`, `binary`, `cli.js`, `minified`, `deobfusc`; a name of one to four
     characters called like a function; a short mixed-case or dollar-bearing token (the
     shape minified names take), the commonest of those only next to a provenance word; a
     version number, since a version paired with a claim about behaviour is to be read,
     not auto-removed; or a `CLAUDE_CODE_` env-var name, to confirm it is user-visible.
   - **The deny-list.** `$(git rev-parse --git-common-dir)/info/claude-code-denylist` is a
     local file, never committed or pushed: one exact internal string or name per line.
     When you meet one, add it there. `cc_scan` greps for every entry, and says so on
     stderr when the file is missing, holds no entries, or cannot be found (outside a
     repo): a scan without it is not clean.
   - **Reading.** Read the whole diff, the message and the post text yourself. It stays
     required whatever the greps print.

   ```bash
   cc_scan() {  # bash; text on stdin; prints candidate lines to read, nothing when clean
     local t gd deny=; t=$(cat)
     if gd=$(git rev-parse --git-common-dir 2>/dev/null); then
       deny="$gd/info/claude-code-denylist"
     else
       echo "cc_scan: not in a git repo; deny-list not consulted" >&2
     fi
     {
       printf '%s\n' "$t" | grep -niE 'bundle|binary|cli\.js|minified|deobfusc'
       printf '%s\n' "$t" | grep -nE '(^|[^A-Za-z0-9_.])[A-Za-z_][A-Za-z0-9$_]{0,3}\(|[0-9]+\.[0-9]+\.[0-9]+|CLAUDE_CODE_[A-Z0-9_]+'
       printf '%s\n' "$t" | grep -nE '(^|[^A-Za-z0-9_$])([A-Za-z]+\$[A-Za-z0-9]*|[A-Za-z0-9]?[a-z][A-Z][A-Za-z0-9]?|[A-Za-z][0-9][A-Za-z][A-Za-z0-9]?)([^A-Za-z0-9_$]|$)'
       printf '%s\n' "$t" | grep -nE '(^|[^A-Za-z0-9_$])([A-Z]{2}[a-z][A-Za-z0-9]?|[A-Z][a-z][A-Z][A-Za-z0-9]?)([^A-Za-z0-9_$]|$)' \
         | grep -iE '\b(via|per|cop(y|ies|ied)|mirrors?|match(es)?|source|internal|chunk|derived|read from)\b'
       if [ -n "$deny" ] && grep -q '[^[:space:]]' "$deny" 2>/dev/null; then
         printf '%s\n' "$t" | grep -nF -f <(grep -v '^[[:space:]]*$' "$deny")
       elif [ -n "$deny" ]; then
         echo "cc_scan: deny-list missing or empty: $deny" >&2
       fi
     } | sort -t: -k1,1n -u
   }
   # before a commit: the staged lines and the message text
   # (MSG=$(cat <-F file>), or MSG set to the -m string)
   [ -n "$MSG" ] || echo "cc_scan: MSG is empty; the commit message was not scanned" >&2
   { git diff --cached -U0 | grep '^+'; printf '%s\n' "$MSG"; } | cc_scan
   # before a push: every commit of the ref you push (<ref>, e.g. main) not yet on any
   # remote, merge resolutions included
   git log -p --cc <ref> --not --remotes | cc_scan
   # before posting an issue or PR: the text itself
   cc_scan < body.md
   ```

   Every hit that is verbatim material rule 1 bans, an internal identifier, a recipe, an
   internal source or an unreleased feature is removed before the commit, never after. A
   hit in prose that only names the rule, as this section does, may stay. Found while it is
   still only on its own unmerged branch: rebuild that branch the way
   `plugins/dev-flow/skills/dev-cycle/references/fix-loop.md` § A leaked secret does (its
   step 1 reach check first, then a soft reset to the merge base and one clean recommit),
   never a fix commit on top. Found once it is merged into another branch (local main
   included) or pushed: stop and hand it to the operator. Scrubbing that history is the
   operator's path, tracked as work item `history-scrub-purge-claude-code-bundle-d-4151`.
6. **Why:** distributing verbatim code or prompts is copyright infringement; observed
   behaviour is fact, and fact is ours to write down.

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
      usage-report/scripts/  # usage_report.py + item_spend.py (an item's spend by agent id) + prices.json (token-spend accounting)
  create-repo/         # Start a new repo for a thread of work, with a session launched on it
    skills/
      create-repo/     # references/{launch-command,gitignore}.md
  dev-flow/            # Plan before you code; research into findings or a knowledge base; the librarian that takes custody of a repo
    agents/            # scribe, scout, implementer, implementer-critical, implementer-deep, planner, planner-deep, reviewer, reviewer-light, cross-checker, cross-checker-deep (the dev cycle's role workers); research-lane, research-lane-deep, research-verifier (the research family's workers)
    skills/
      {investigate,implement,dev-cycle,foundation,deep-investigation,research,research-deep,research-refine,research-prune,chain-of-verification,librarian-mode}/
      research/scripts/  # tool-preflight.sh (Step 5.1 tool check), scan-findings.py (the scan floor under the verifier) + unit tests
      librarian-mode/scripts/  # quota_budget.py (the librarian's quota sense) + unit tests
    tests/             # test_agents.py: every agent file's model and effort pin, and its frontmatter shape; test_deep_investigation.py: deep-investigation's research-family security parity; test_research_asks.py: the research family's asks as text, the owner section, its pointers, the ledger kinds and the manifest edge; test_decision_tags.py: the librarian's two-word decision tags, their order, the retired spellings and no residue of them
  kit-dev/             # Maintaining this kit itself
    skills/
      {create-skill,update-kit,new-project-from-template,factor-analysis}/
  operator-interaction/ # The agent-operator interface, starting with how decisions are raised and shown
    skills/
      decisions/       # references/{worksheet,rendering,replies,evidence-basis,rationale,rulings,gallery}.md
      plain-names/     # plain names for what agents mention, the id a trailing tag
      decision-page/   # a set of decisions as an answer page: assets/{index.html,cards.example.json}, references/{cards-schema,fallback}.md, scripts/check_cards.js (the pre-publish check; node optional)
    tests/             # test_impact.py: the decision page's impact check and renderers (under node), and the decisions gallery's impact at every size; test_act.py: the page's act field and its check (under node), and the gallery's To act on parts, placeholders and labels; test_context.py: the page's context field, its TLDR check and render order, and the pre-publish runner (under node); test_depth.py: the page's detail levels, the More button's option detail, links and the runner's depth lints (under node)
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
- **README footer**: a `README.md` inside a skill folder is allowed, for humans, and ends
  with the line `*User-facing documentation, not agent instructions.*` (the dev-cycle
  review checklist lints this).
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
- (cd plugins/operator-interaction && python3 -m unittest discover -s tests -q)
Push: main
