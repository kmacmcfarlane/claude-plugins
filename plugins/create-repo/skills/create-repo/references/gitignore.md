# The new repo's .gitignore

Who writes which lines in a repo this skill makes, and how this skill picks its own.

## Ownership

Each line belongs to whoever creates the file it ignores. There is no shared block that
every new repo gets.

| Lines for | Owner | How they get there |
|---|---|---|
| `.claude-sandbox/` and the files inside it | claude-sandbox | its `init` (Step 5) or `init-ralph` (the template path) writes them |
| what a template ships | the template | they arrive with the template's own `.gitignore` |
| what this skill creates | this skill | this step |
| files no tool creates: Claude Code's personal files, editor and OS clutter | this skill, by judgment | this step |

This skill creates only `README.md` (and `.gitignore` itself), and nothing it creates
needs ignoring today. If a later version of this skill creates a file that should stay out
of git, its line is written here.

**Never rewrite another owner's lines.** Do not remove, reorder, reword or comment out a
line that claude-sandbox or the template wrote, even one that looks wrong or that your own
judgment would not add. Append only. If one of their lines clashes with your judgment (a
`!` negation that re-includes a file you would ignore, say), leave it, add nothing that
fights it, and name it in the report.

## Your judgment lines

Pick the lines for files no tool owns from what the repo is for: its purpose, the template
when there is one, and what the operator has said in this conversation. These are the
usual candidates:

- **Claude Code's personal files**, which are per user and never shared:
  `.claude/settings.local.json` (the local settings file,
  https://code.claude.com/docs/en/settings) and `CLAUDE.local.md` (personal project
  memory, https://code.claude.com/docs/en/memory).
- **OS clutter**: `.DS_Store`, `Thumbs.db`.
- **Editor clutter** that is never shared: `*.swp`, `*~`.

Leave out what a repo often tracks on purpose, such as `.vscode/` or `.idea/` (shared
editor settings) and `.claude/` as a whole (`.claude/settings.json` and project skills are
meant to be committed). Add no stack lines (`node_modules/`, `__pycache__/`, build output):
the repo has no stack yet, and the first session or the template adds them.

## When to ask

Decide and report. Ask the operator first only when the doubt is critical, which means
one of:

- **A file that could hold a secret or credential**: an `.env`, a key, a token file, a
  local config with passwords. Leaning towards ignoring it is safe and needs no question;
  ask when something says it should be tracked instead, such as a template that ships one
  with content in it or a purpose that names it as shared config.
- **A file the operator may want tracked**: a line that would hide something the template
  ships, or that the purpose suggests is shared.

Anything else, decide and name it in the report.

The question follows the `decisions` skill from the operator-interaction plugin when this
session lists `operator-interaction:decisions`. Otherwise it is a plain question in one
message: the file, why it is in doubt, and your recommendation. Ask once, before the
commit that would carry the line.

## Writing the lines

1. Read `$REPO/.gitignore` if it exists. Drop any of your lines that it already holds,
   matched as whole lines.
2. Append the rest at the end of the file under one comment line,
   `# create-repo: personal and editor files`, with a blank line before it when the file
   is not empty. Write with the Edit or Write tool; your lines are fixed patterns, never
   the purpose.
3. Nothing left to add: leave the file untouched and do not create one.

The commit that follows stages `.gitignore` by name with the rest of the step's files.
