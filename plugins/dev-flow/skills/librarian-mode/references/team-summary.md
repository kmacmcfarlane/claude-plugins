# Team summary

The four-line Report is the audit trail, for the operator. The team summary is for the
people the operator passes the news on to: teammates who did not watch the run and will
read it in Slack, Teams, an email or on a phone. Pointed at from SKILL.md § Report, and from the `dev-cycle` skill's `references/bindings.md` § Landing.

## When

- **After each push**, one summary covering everything that push carried, not one per
  item. Normally: the Report, the push outcome with its `incoming:` lines (SKILL.md
  § Report), then the summary. At session end and at 75%/DUE the push comes before the
  final Report (`ending-the-session.md`); the summary follows that Report, after the
  push outcome and its `incoming:` lines, in the same closing message.
- **`Push: none`, or no `origin` remote**: one summary per landing batch, right after its
  Report, and its header line says the changes are local only (not pushed).
- **No summary** for a rejected push that stops on a conflict, a red check or a
  decision (nothing reached origin; it goes under `decisions needed`) — a rejection
  merged through and pushed gets its summary, of this session's landings, not the
  incoming commits — or for a push that carries no landed change, only work-item store
  or checkpoint commits.

## Shape

Plain text, in this order:

1. **A two-line header.** The first line, bold, names the plugin or marketplace, what
   kind of update this is, the date, and the commit range in parentheses. `old` is
   `origin/main` before the push and `new` is `origin/main` after it:

   ```bash
   OLD=$(git -C "$MAIN" rev-parse --short 'origin/main@{1}')
   NEW=$(git -C "$MAIN" rev-parse --short origin/main)
   git -C "$MAIN" log --oneline "$OLD..$NEW"   # must list exactly this push's commits
   ```

   When the reflog is unavailable (`core.logAllRefUpdates` off, or a fetch updated the
   ref since), or that log does not show this push's commits, read the range from the
   push's own output (the `<old>..<new>  main -> main` line), and from then on note
   `git -C "$MAIN" rev-parse --short origin/main` right before each push, again after
   any fetch and merge; the value noted before the push that succeeds is `old` (SKILL.md
   § Report).
   The second line, plain text right under the first, is one short sentence naming the
   pickup step, then one confirming review: in a plugin marketplace, "Update your
   plugins to pick it up." — a change under `plugins/` reaches a user only after
   `/plugin marketplace update <marketplace name>` (the `name` in
   `.claude-plugin/marketplace.json`) and then `/reload-plugins`, which is what that
   sentence stands for — followed by "Every change was reviewed before it merged."
   With `Push: none` or no `origin`, `old` is `main` before the batch's first merge (that
   merge's first parent), the header's first line says `local only, not pushed` in place
   of the commit range, and the second line drops the pickup sentence, keeping only the
   review one.

2. **One change area per bold title, on its own line, with exactly one bullet under
   it.** The bullet is one sentence, two at most, stating WHAT changed for the people
   and agents who use the repo — never a commit subject, an item id, a tier, a model, a
   review round, a fix round or a verdict. Several items that make one visible change
   share a title and its bullet; maintenance and plumbing (tests, refactors, dependency
   bumps, store bookkeeping) collapse the same way, under one title such as
   `**Housekeeping**`. Order the areas by what the reader feels: the change most people
   will notice first, invisible plumbing last.

3. **No tables, no sub-bullets, no lists of files or commit shas under an item.** The
   bullet is the whole change area's text — flat, one level, nothing nested under it.

4. **A closing line**: whether anything requires action on existing work — a rule people
   now follow, a migration, a re-run of a setup step, a config written before this that
   now needs an update — or `Nothing on existing work needs action.` This is distinct
   from the header's pickup step, which is about picking up the change itself, not
   fixing or adjusting something older.

Rules that keep it pasteable:

- **Never a table.** Tables paste badly into chat, email and phones. No markdown
  headings.
- Bold appears only on the header's first line and each change area's title — never
  inside a bullet.
- Put it in its own fenced `text` block, separate from the Report, so the operator can
  copy it exactly as written. The fence only marks what to copy; it is not part of the
  message.
- Backticks only around a command a reader must type, where Slack and Teams, the main
  targets, show it as code. Everywhere else write names plainly, including a commit
  range: in email or SMS the backticks appear as literal characters.
- Keep it short. A bullet that needs a third sentence is carrying rationale or
  mechanism — cut it back to WHAT.
- Paths are fine. Secret values never appear, just as in the Report.

## Example

A push that landed two visible changes and a round of maintenance, for a fictitious
`dev-flow` plugin update:

```text
**dev-flow plugin update, 2026-09-23 (marketplace a1b2c3d..e4f5a6b)**
Update your plugins to pick it up. Every change was reviewed before it merged.
**Faster investigate handoffs**
- The investigate skill now hands a finished plan straight to implement, with no extra confirmation step in between.
**Clearer checkpoint prompts**
- A checkpoint now names the exact manifest file it wrote, so you know where to look after a compact.
**Housekeeping**
- Dependency bumps and test cleanup across two plugins.
Nothing on existing work needs action.
```
