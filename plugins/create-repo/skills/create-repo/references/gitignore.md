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
| files no tool creates: Claude Code's personal files and worktrees, secret-holding files, editor and OS clutter | this skill, by judgment | this step |

claude-sandbox's `init` also writes `.claude/worktrees/`. When it has, the check in
Writing the lines finds it already ignored and this skill adds nothing for it; in the
plain path (no claude-sandbox) this skill writes it.

This skill creates only `README.md` (and `.gitignore` itself), and nothing it creates
needs ignoring today. If a later version of this skill creates a file that should stay out
of git, its line is written here.

**Never rewrite another owner's lines.** Do not remove, reorder, reword or comment out a
line that claude-sandbox or the template wrote, even one that looks wrong or that your own
judgment would not add. Append only, and never append a line that undoes theirs (Writing
the lines, steps 2 and 3, say how to tell).

## Your judgment lines

Pick the lines for files no tool owns from what the repo is for: its purpose, the template
when there is one, and what the operator has said in this conversation. These are the
usual candidates:

- **Claude Code's personal files**, which are per user and never shared:
  `.claude/settings.local.json` (the local settings file,
  https://code.claude.com/docs/en/settings) and `CLAUDE.local.md` (personal project
  memory, https://code.claude.com/docs/en/memory).
- **Claude Code's worktrees**: `.claude/worktrees/`, which the worktrees docs say to add
  to `.gitignore` (https://code.claude.com/docs/en/worktrees). Without it, a worktree
  created there is staged as an embedded repository by a later `git add -A`.
- **Secret-holding files**, by default: `.env` and `.env.*`, with `!.env.example` after
  them so a shared example stays tracked. Ignoring a file that could hold a secret is the
  safe side; the next section says when to ask instead.
- **OS clutter**: `.DS_Store`, `Thumbs.db`.
- **Editor clutter** that is never shared: `*.swp`, `*~`.

Without a reason in the purpose, the template or the conversation to leave one out, add
every candidate above.

Leave out what a repo often tracks on purpose, such as `.vscode/` or `.idea/` (shared
editor settings) and `.claude/` as a whole (`.claude/settings.json` and project skills are
meant to be committed). Add no stack lines (`node_modules/`, `__pycache__/`, build output):
the repo has no stack yet, and the first session or the template adds them.

## When to ask

Decide and report. Ask the operator first only when the doubt is critical, which means
one of:

- **A file that could hold a secret or credential**: an `.env`, a key, a token file, a
  local config with passwords. Ignoring it is the default and needs no question (the
  `.env` lines above); ask when something says it should be tracked instead, such as a
  template that ships one with content in it or a purpose that names it as shared config.
- **A file the operator may want tracked**: a line that would hide something the template
  ships, or that the purpose suggests is shared.

Anything else, decide and name it in the report.

Put every critical doubt in one message, one numbered decision each, before the commit
that would carry the lines. The message follows the `decisions` skill from the
operator-interaction plugin when this session lists `operator-interaction:decisions`.
Otherwise it is a plain message, each decision giving the file, why it is in doubt, and
your recommendation.

## Writing the lines

1. Read `$REPO/.gitignore` if it exists.
2. Test each candidate against the rules already in place, with one sample path for it
   (`.claude/settings.local.json`, `CLAUDE.local.md`, `.claude/worktrees/w`, `.env`,
   `.env.local`, `.DS_Store`, `Thumbs.db`, `a.swp`, `a~`):
   ```bash
   git -C "$REPO" check-ignore --no-index -v '.claude/settings.local.json'
   ```
   A match prints `file:line:pattern`, a tab, then the path; read the pattern field.
   Count only a match whose file field is `.gitignore`; a match from `.git/info/exclude`
   or a global excludes file is this machine's alone, so keep the candidate.
   - No output (exit 1): nothing covers it; keep the candidate.
   - A pattern not starting with `!`: already ignored, perhaps by a wider line such as
     `.claude/*`; drop the candidate.
   - A pattern starting with `!`: another owner un-ignores it on purpose. Drop the
     candidate, append nothing that would re-ignore that path, and name the line in the
     report.
   `!.env.example` goes in only when `.env.*` does.
3. Check the kept candidates against every `!` line already in `.gitignore`, since one
   sample path can miss a negation for another path the candidate covers, such as
   `!.claude/worktrees/` under `.claude/*`, or `!.env.development` with no `.env.*`
   above it. When a candidate's pattern would match the path a `!` line names (for
   `.env.*`, any `.env.` name; for `.claude/worktrees/`, anything inside it), drop that
   candidate, since appending it after the `!` line would ignore that path again, and
   name the `!` line in the report. A `!.env.example` line does not count here, since
   this skill appends its own `!.env.example` right after `.env.*`.
4. Append the kept candidates at the end of the file under one comment line,
   `# create-repo: Claude Code personal files, secrets, editor and OS files`, with a
   blank line before it when the file is not empty. Write with the Edit or Write tool;
   your lines are fixed patterns, never the purpose.
5. Nothing left to add: leave the file untouched and do not create one.

The commit that follows stages `.gitignore` by name with the rest of the step's files.
