---
name: update-kit
description: Sync agent workflow files, subagent definitions, and skills from this project back to the upstream claude-templates, claude-plugins (plugin marketplace), claude-expertise (expertise marketplace), and claude-sandbox repos. Use when user says "sync upstream", "update templates", "update kit", "push changes to claude-templates", "propagate skills", or "sync skills". User-invoked only.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, TaskCreate, TaskUpdate
argument-hint: "[files|skills|all]"
---

# Update Kit

Syncs changes from a child project back to upstream repos. Works with any project scaffolded
from the `local-web-app` template.

> **Naming note.** The umbrella repo `claude-kit` keeps its name and its README (Phase 2.5
> below). The *plugin* that used to ship this skill was also called `claude-kit`; it dissolved
> into aim-named plugins, and this skill now ships in `kit-dev`. Wherever this document says
> `claude-kit` it means the umbrella **repo**, never a plugin.

## Critical: Check the repos, not the environment

What matters is whether the sibling repos are reachable — not whether you are in a container.
claude-sandbox commonly mounts the whole work tree, in which case they are. **Probe for them.**

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$PROJECT_ROOT")
for r in claude-templates claude-plugins claude-expertise claude-sandbox claude-kit; do
  test -d "$PARENT/$r" && echo "found  $r" || echo "MISSING $r"
done
```

- **All present** → proceed, whether or not `/.dockerenv` exists.
- **Some present** → proceed with what is reachable; report which repos are missing and which
  parts of the sync are therefore skipped. `claude-expertise` and `claude-kit` are optional —
  without `claude-expertise`, expertise-pack skills have nowhere to land, so report them as
  deferred rather than misfiling them into a claude-plugins plugin.
- **None present** → stop:

  > The sibling repos are not reachable from `<PARENT>`. If you are in a claude-sandbox
  > container, add a mount for the parent directory to `.claude-sandbox/config.yaml` and
  > relaunch; otherwise run this skill from a checkout whose siblings are on disk.

Never edit a repo you could not locate, and never assume a path you did not verify.

---

## Where to edit, and on which branch

**This section is canonical for every skill-doc edit, whoever initiates it** — a direct
`/update-kit` run, or the retrospective step of `investigate` / `implement`. Do all of it
**before** editing a single file.

### Edit the real checkout, never the plugin cache

Skill sources live in a marketplace checkout at `plugins/<plugin>/skills/<skill>/` —
`claude-plugins` for harness plugins, `claude-expertise` for expertise packs. The plugin cache — under `$CLAUDE_CONFIG_DIR/plugins/`,
which is `~/.claude/plugins/` only when `CLAUDE_CONFIG_DIR` is unset — is **ephemeral and
overwritten on plugin update**, so edits there are silently lost and never reach the repo.

The skills you are currently running from are the cache copy. Resolve `$CLAUDE_CONFIG_DIR`
rather than assuming a path, and confirm the file you are about to edit is under the checkout.

### Settle the branch, and ask

Name the branch you would use and confirm it before editing. Settling it afterwards costs a
cherry-pick and a conflict resolution.

- **Work is in flight** (a retro, or an in-flight investigation) → that work's branch, so the
  change is reviewable alongside what taught you it. This holds even for changes that look
  entirely generic.
- **Nothing particular in play** → the default branch, left unpushed unless asked.

### Check the branch is not stale — in both directions

```bash
git -C <repo> fetch origin
git -C <repo> rev-list --count <branch>..origin/<default>   # commits BEHIND
git -C <repo> rev-list --count origin/<default>..<branch>   # commits AHEAD
```

**An empty `origin/<default>..<branch>` means the branch is *behind* — an ancestor of the
default — not up to date.** Editing from a stale base produces a change that reverts other
people's work. If behind, merge the default in before editing.

---

## What earns a place in a skill

**Every addition costs context on every load.** A passage that helps one run while displacing
context on all the others is a net loss even when it is true. The default answer to "should
this go in the skill?" is **no**. Before adding anything, require all three:

1. **It will recur.** A fact about how the system *is* recurs; a narration of what went wrong
   once does not. "The build image has no `jq`" earns its place. "I wrote a grep that matched
   nothing" does not.
2. **It is not discoverable at the moment of need.** If an agent would hit it immediately from
   an error message, a failing lint, or the repo's own README, a pointer beats a copy. Skills
   exist for what is *invisible* until it bites — ordering constraints, silent failure modes,
   cross-repo coupling, decisions with no trace in the code.
3. **It changes what someone would do.** If the reader's actions are identical with and without
   the text, it is commentary. Cut it.

**Weight the bar by how often the skill loads.** A line in a frequently-loaded skill is paid
for constantly and must be a one-line invariant, not an explanation. A rarely-loaded workflow
skill can afford more.

**Push length into `references/`.** A reference file loads only when its subject is at hand, so
that is where procedures, command recipes, and worked detail belong. If an addition to a
SKILL.md body runs past a few lines, move it to a reference and leave a one-line pointer.
Prefer *editing* an existing bullet to be more correct over *appending* a new one.

**Do not state counts.** "13 lambdas", "22 call sites", "read by 10 consumers" — these rot
silently, and a reader who trusts a stale one is worse off than one who counts. Give the shape
and how to derive the number. When correcting a stale count, **remove it rather than refreshing
it** — refreshing just resets the clock.

**Watch duplication specifically**: restating a rule that already appears above in different
words, or copying guidance from another skill instead of pointing at the skill that owns it.

**Removing text is as valuable as adding it.** If a section is now wrong, or never earned its
place, propose the deletion in the same review table with what it costs and why it goes.

---

## Phase 0: Scan & Plan

### Step 0.1: Resolve paths

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$PROJECT_ROOT")
PROJECT_NAME=$(basename "$PROJECT_ROOT")
TEMPLATES="$PARENT/claude-templates/local-web-app"
PLUGINS="$PARENT/claude-plugins/plugins"      # harness plugins (marketplace: kmacmcfarlane)
EXPERTISE="$PARENT/claude-expertise/plugins"  # expertise packs (marketplace: expertise) — probe
KIT="$PARENT/claude-kit"                      # umbrella repo, README sync only — probe
```

There is **no single skills root any more.** A skill's upstream home is a *plugin* under one
of the two marketplaces, so every path is built as `$PLUGINS/<plugin>/skills/<name>/` or
`$EXPERTISE/<plugin>/skills/<name>/`. Never hardcode a plugin name — Step 0.3 discovers it.

Verify sibling repos exist. If any are missing, report which and continue with the reachable
ones (`$EXPERTISE` and `$KIT` are optional; `$PLUGINS` is required for any skill sync).

### Step 0.2: Dynamic template diff (replaces hardcoded file list)

Recursively compare the project against the template, **excluding** known project-specific paths.

**Resolve the agent-docs root on both sides first.** The current template roots them at
`.claude-sandbox/agent/`; older projects and older templates use a top-level `agent/`. Probe
each side (`test -d .claude-sandbox/agent || test -d agent`) and build paths from what you
find — the `agent/` prefixes below and in the syncable-tree list are relative to whichever
root each side actually has. Never map a project path straight onto the template.

Use this exclude list:

```
# Project-specific content — never sync to template
agent/backlog.yaml          # Has project stories
agent/backlog_done.yaml     # Has project completed stories
agent/PRD.md                # Product requirements are project-specific
agent/QA_ALLOWED_ERRORS.md  # Project-specific error allowlist
agent/QUESTIONS.md          # Project-specific clarifications
agent/ideas/                # Contains project-specific ideas (structure syncs, content doesn't)
agent/claude-kit-repo-map.md # This IS the project-specific config
CHANGELOG.md                # Project history
config.yaml                 # Runtime config
docker-compose*.yml         # Project compose files
Makefile                    # Project build targets (root and backend/)
backend/                    # Application code
frontend/                   # Application code
docs/                       # Project architecture docs
.claude-sandbox/ralph/      # Runtime state
.claude/worktrees/          # Worktree state (harness-native worktrees)
.e2e/                       # E2E artifacts
node_modules/               # Dependencies
__pycache__/                # Python cache
```

For each syncable path, classify:

| Marker | Meaning |
|--------|---------|
| `[M]` | Modified — file exists in both, content differs |
| `[A]` | Added — file exists in project but not template |
| `[D]` | Deleted — file exists in template but not project |
| `[T]` | Trim — content upstream is now wrong, duplicated, or never earned its place |
| `[=]` | Identical — no sync needed |

`[T]` is a first-class outcome, not an afterthought. When a scan turns up upstream text that
is stale, duplicated, or fails the three-part bar above, propose the deletion in the same
table as the additions, with what it costs and why it goes.

Run a recursive diff across these syncable directory trees:
- `agent/` (excluding items in the exclude list above)
- `.claude/agents/`
- `.claude/settings.json`
- `.mcp.json`
- `CLAUDE.md`
- `.gitignore`
- `scripts/` (all scripts)

Note: `.claude/skills/` is NOT synced to the template. Skills come from marketplace plugins, not from the template. Only sync skills to the marketplace checkouts (Step 0.3 decides which).

For the `agent/ideas/` directory specifically: sync the **directory structure and stub headers** (the idea category files), but NOT the idea entries themselves. Compare only the first 3 lines of each ideas file.

### Step 0.3: Dynamic skills diff

Scan ALL skills in the project (`.claude/skills/*/SKILL.md`) and compare against both
marketplaces. Do NOT rely on `claude-kit-repo-map.md` for the scan — discover skills
dynamically.

**A skill's upstream home is discovered, never assumed.** Search across every plugin in both
marketplaces:

```bash
for root in "$PLUGINS" "$EXPERTISE"; do
  test -d "$root" || continue
  ls -d "$root"/*/skills/<name> 2>/dev/null
done
```

For each project skill:
- If it is found in exactly one plugin: that is its home; diff all files in the skill
  directory → `[M]`, `[=]`
- If it is found in **more than one** plugin: stop and report — a duplicated skill name across
  plugins is a factoring bug, not something to sync into.
- If it is NOT found anywhere: mark as `[A?]` (candidate for upstream — needs triage and
  routing, below)
- Read the skill's SKILL.md and check for project-specific content (project name, domain
  terms). Classify as "generic" or "project-specific".

For each upstream-only skill (exists in a marketplace but not in the project): mark as `[D?]`
(informational — the project may not use this skill).

#### Routing an `[A?]` skill to a plugin

A new upstream skill has no home yet. Route it **by aim**, using the decision tree in the
claude-plugins checkout's `CLAUDE.md` § Placement rules (the full form is in its
`README.md` § Where does a new thing go?) — read that file, do not reproduce its table from
memory, because it moves as the marketplace changes. The shape of the answer:

- alters harness behavior (hooks, status line, `settings.json` writes) → the plugin whose aim
  *is* that behavior;
- pure stack/tool knowledge ("make Claude good at X") → an expertise pack under `$EXPERTISE`,
  one plugin per stack; if `$EXPERTISE` is not reachable, defer the skill rather than
  misfiling it;
- tooling for maintaining this kit itself → `kit-dev`;
- otherwise → the claude-plugins plugin that owns that aim; if none does, a **new plugin** is
  the answer, which is an operator decision, not a sync step.

Present each `[A?]` with its routed destination as `[A?] <skill> → routed: <plugin>` and get
confirmation before Phase 2 copies anything.

### Step 0.4: Reverse-diff (template → project)

Check for files that exist in the template but NOT in the project. These may be stale template files that the project has since deleted or restructured.

Exclude template boilerplate that projects legitimately don't have (e.g., `cmd/README.md`, `.gitkeep` files, `agent/PROMPT_DEBUG.md`).

Flag each as:
- `[D-template]` — exists in template only; may need deletion if the project intentionally removed it

### Step 0.5: Content-level diff triage

For each `[M]` file, perform a quick diff analysis:

1. Count lines added/removed/changed
2. Check whether the **project version** contains project-specific terms (the project name, domain-specific words from PRD.md). Extract the project name from `agent/backlog.yaml`'s `project` field, and scan the first 20 lines of PRD.md for domain terms.
3. Classify the diff:
   - **Generic improvement**: Changes are purely generic (workflow, practices, patterns). → Sync directly.
   - **Project-specific addition**: Changes reference project-specific features, components, or domain terms. → Skip or genericize.
   - **Mixed**: Some changes are generic, some are project-specific. → Needs manual review.

Present the classification with each `[M]` file in the summary.

### Step 0.6: Present scan results and build plan

Present the full scan results to the user, organized by repo:

```
## claude-templates

### Template files
[M] agent/AGENT_FLOW.md (generic improvement — 45 lines added, 12 removed)
[M] agent/TEST_PRACTICES.md (mixed — 15 generic additions, 3 project-specific)
[A] agent/BUG_REPORTING.md (new file, 76 lines)
[D-template] agent/IDEAS.md (exists in template only — project uses ideas/ directory instead)
[=] agent/PROMPT_AUTO.md
...

## claude-plugins (plugins/<plugin>/skills/)

### Skills
[M] kit-dev/update-kit/SKILL.md (generic improvement — 2 lines changed)
[M] work-items/work-items/references/format.md (generic improvement — 4 lines changed)
[A?] gate-tuner → routed: context-guard (project-only, appears generic — recommend upstream)
[A?] comfyui-api → routed: expertise marketplace (project-specific — skip)
[=] ralph/backlog-yaml/
...

## claude-expertise (plugins/<plugin>/skills/)

### Skills
[=] goa/goa/
[D?] musubi-tuner/musubi-tuner/ (upstream only — project does not use it)
...
```

Then use **TaskCreate** to build a checklist. Create one task per file or logical group:

- Group `[=]` files into a single "skip" note (no task needed)
- Each `[M]` classified as "generic improvement" → task: "Sync <file> to template"
- Each `[M]` classified as "mixed" → task: "Review and genericize <file>"
- Each `[A]` → task: "Add <file> to template"
- Each `[D-template]` → task: "Remove <file> from template (confirm with user)"
- Each `[A?]` generic skill → task: "Sync <skill> to <routed plugin> in <marketplace repo>"
- Group "project-specific" skips into a single informational task

Present the task list to the user and ask for confirmation before proceeding:

> **Proposed sync plan: N tasks**
>
> Ready to proceed? You can adjust tasks before I start.

---

## Phase 1: Sync Template Files

For each task involving template file sync:

### Step 1.1: Copy or genericize

- **Generic improvements** (`[M]` classified generic, or `[A]`): Copy the project file to the template location. Then run the genericization check (Step 1.2).
- **Mixed files** (`[M]` classified mixed): Read both versions. Write the template version incorporating the generic improvements while stripping project-specific content. Replace:
  - The project name (from `backlog.yaml` `project` field) with `myproject` or remove entirely
  - Domain-specific examples with generic equivalents
  - Project-specific file paths, config schemas, or component names with generic placeholders
- **Deleted files** (`[D-template]`): Confirm with user, then `rm` from template.

### Step 1.2: Post-sync genericization verification

After writing each file to the template, run a verification scan:

```bash
# Extract project name from backlog.yaml
PROJECT_NAME=$(python3 -c "
from ruamel.yaml import YAML
data = YAML().load(open('agent/backlog.yaml'))
print(data.get('project', ''))
")

# Also extract domain terms from PRD.md (first 20 lines, nouns)
# These are terms like product names, specific technologies, data formats

# Scan the template file for project-specific content
grep -in "$PROJECT_NAME" "$TEMPLATE_FILE"
# Also grep for domain terms extracted above
```

If any hits are found, fix them before marking the task complete. Common replacements:
- Project name → `myproject` or remove
- Specific UI component examples → generic equivalents
- Domain-specific data formats → `<data format>` placeholder
- Specific endpoint paths → generic API examples

### Step 1.3: Mark task complete

After each file is synced and verified, update the task status to `completed`.

---

## Phase 2: Sync Skills

### Step 2.1: Process each skill task

For `[A?]` skills classified as generic:
1. Copy the entire skill directory to the home Step 0.3 routed it to —
   `$PLUGINS/<plugin>/skills/<name>/` or `$EXPERTISE/<plugin>/skills/<name>/`
2. If the routed plugin does not exist yet, **stop and ask** — creating a plugin is an
   operator decision (new aim → new plugin), and it needs a `.claude-plugin/plugin.json`, a
   `marketplace.json` entry and a catalog row, none of which this skill invents
3. Run genericization verification on each file in the skill
4. Update the marketplace README catalog in the same commit if the change alters the shape of
   the marketplace (a new plugin, or a skill list a table states)

For `[M]` skills:
1. Overwrite each changed file in the upstream skill directory (the home discovered in
   Step 0.3, in whichever marketplace it was found)
2. Run genericization verification

For `[A?]` skills classified as project-specific:
1. Skip — note in the summary that these were not synced

### Step 2.2: Update repo map

If any new skills were synced upstream, update `agent/claude-kit-repo-map.md` to add them to the sync list. This keeps the repo map accurate for future runs.

---

## Phase 2.5: Update claude-kit README

The `claude-kit` repo (formerly `kmac-claude-kit`) contains the umbrella README that documents the entire toolkit — components, agent pipeline, tooling, workflow, and skills reference. This README must stay current as the toolkit evolves.

The repo keeps the name `claude-kit`. The plugin that once carried that name is gone (see the
naming note at the top) — so when updating this README, describe the toolkit as a marketplace
of aim-named plugins, and never write `claude-kit` as if it were still an installable plugin.

### Step 2.5.1: Check for README drift

If the `$KIT` repo exists, read `$KIT/README.md` and compare against the current state of:
- **Components table**: Does it accurately describe each repo's purpose?
- **Tree diagram**: Does it reflect the current project structure (agent docs, scripts, skills, MCP servers)?
- **Agent pipeline**: Does it describe the current story lifecycle and subagent roles?
- **Tooling section**: Are all scripts (backlog.py, worktree.py, merge_helper.py) documented?
- **Skills reference table**: Does it list all skills currently in the two marketplaces, under the plugins that own them?
- **Workflow section**: Does it cover parallel execution, UAT grooming, upstream sync?

### Step 2.5.2: Update if needed

If any section is outdated or missing:
1. Create a task: "Update claude-kit README"
2. Read the current README, then rewrite the outdated sections based on the current state of the template, skills, and workflow docs you've already read during this sync
3. Do NOT include project-specific content — the README describes the toolkit generically
4. Commit with message format: `docs: update README — <brief summary of what changed>`

### Step 2.5.3: Skip conditions

Skip this phase if:
- `$KIT` repo does not exist at the expected path
- No template or skills changes were made in this sync run (README is likely still current)

---

## Phase 3: Report & Verify

### Step 3.1: Final cross-repo genericization sweep

Run a single comprehensive grep across the **entire template directory** for the project name and domain terms:

```bash
grep -ri "$PROJECT_NAME" "$TEMPLATES/" --include="*.md" --include="*.json" --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml"
```

If any hits remain, fix them. This is the safety net — catches anything the per-file checks missed.

### Step 3.2: Summary report

Show a concise summary organized by repo:

```
## Sync Summary

### claude-templates
- Modified: N files
- Added: N files
- Removed: N files
- Skipped (project-specific): N files

### claude-plugins
- Modified: N skills (listed as <plugin>/<skill>)
- Added: N skills (with the plugin each was routed to)
- Skipped (project-specific): N skills

### claude-expertise
- Modified / Added: N skills (listed as <plugin>/<skill>)
- Deferred (marketplace not reachable): N skills

### claude-kit (umbrella repo)
- README.md updated (if applicable)

### Project
- Updated: agent/claude-kit-repo-map.md (if new skills added)

Remember to commit and push in:
  - /path/to/claude-templates
  - /path/to/claude-plugins
  - /path/to/claude-expertise (if expertise packs changed)
  - /path/to/claude-kit (if the umbrella README changed)
  - /path/to/project (if repo map changed)

After pushing claude-plugins, projects subscribed to the marketplace can install or update the affected skills with the `/plugins` slash command in Claude Code (it pulls the latest from the marketplace).
```

### Step 3.3: All tasks completed

Verify all tasks are marked `completed`. If any remain, report them.

---

## What NOT to Sync (reference)

Project-specific content that must never go upstream:
- `agent/backlog.yaml`, `agent/backlog_done.yaml` (story content)
- `agent/PRD.md` (product requirements)
- `agent/QA_ALLOWED_ERRORS.md` (project-specific error allowlist)
- `agent/QUESTIONS.md` (project-specific clarifications)
- `agent/ideas/` content (idea entries — the directory structure and stub headers DO sync)
- `agent/claude-kit-repo-map.md` (this IS the project-specific config)
- `CHANGELOG.md` (project history)
- `CLAUDE.md` data persistence section (project-specific), tooling ecosystem links
- `config.yaml`, `docker-compose*.yml`, `Makefile` (project-specific build/deploy)
- Application code: `backend/`, `frontend/`, `docs/`

**Note on CLAUDE.md**: This file is partially syncable. The structure, safety rules, architecture boundaries, and quick command patterns are generic. But sections like "Data persistence" (specific database schema references) and project-specific Makefile targets are not. Treat CLAUDE.md as a "mixed" file that always needs manual review.

## Troubleshooting

### "Repo not found" error
The sibling repos must be checked out alongside this project:
```
parent-directory/
  your-project/        (this project)
  claude-templates/    (template repo)
  claude-plugins/      (harness-plugin marketplace — source of truth for skills)
  claude-expertise/    (expertise-pack marketplace, optional — stack knowledge packs)
  claude-kit/          (umbrella repo, optional — for README sync)
  claude-sandbox/      (sandbox repo, optional)
```

### Merge conflicts
This skill does a one-way overwrite (project → upstream). If the upstream has changes not present in this project, those will be lost. Check `git diff` in the upstream repo before syncing if you suspect divergence.
