# Team summary

The four-line Report is the audit trail, for the operator. The team summary is for the
people the operator passes the news on to: teammates who did not watch the run and will
read it in Slack, Teams, an email or on a phone. Pointed at from SKILL.md § Report.

## When

- **After each push**, one summary covering everything that push carried, not one per
  item. Normally: the Report, the push, then the summary. At session end and at 75%/DUE
  the push comes before the final Report (`ending-the-session.md`); the summary follows
  that Report in the same closing message.
- **`Push: none`, or no `origin` remote**: one summary per landing batch, right after its
  Report, and its first line says the changes are local only (not pushed).
- **No summary** for a rejected push (nothing reached origin; the rejection goes under
  `decisions needed`), or for a push that carries no landed change, only work-item store
  or checkpoint commits.

## Shape

Plain text, in this order:

1. **A lead line**: the repo and what happened, such as `claude-plugins updates, pushed to
   main:`. With `Push: none`, say `local only, not pushed`.
2. **One bullet per change, about one line each.** Say what changed for the people and
   agents who use the repo: what they can do now, what behaves differently, what was
   fixed. Leave out how the change was made or reviewed: no tiers, models, review rounds,
   fix rounds or verdicts, and no item ids unless a teammate needs one to look something
   up. Several items that make one visible change share a bullet. Internal-only work
   (tests, refactors, store bookkeeping) goes into one last bullet or is left out.
3. **A do-line**: what a human reader must now DO, or `Nothing to do.` That covers a rule
   people now follow, or a command to run. In a plugin marketplace, a change under
   `plugins/` reaches a user only after `/plugin marketplace update <marketplace name>`
   (the `name` in `.claude-plugin/marketplace.json`) and then `/reload-plugins`.
4. **The commit range, last**: `Commits: <old>..<new>`, short shas. `old` is origin's
   `main` before the push and `new` is `main` after it. Read both after the push: a
   successful push updates the tracking ref and logs it, so the entry before that one is
   the old tip:

   ```bash
   OLD=$(git -C "$MAIN" rev-parse --short 'origin/main@{1}')
   NEW=$(git -C "$MAIN" rev-parse --short main)
   git -C "$MAIN" log --oneline "$OLD..$NEW"   # must list exactly this push's commits
   ```

   When the reflog is unavailable (`core.logAllRefUpdates` off, or a fetch updated the
   ref since), or that log does not show this push's commits, read the range from the
   push's own output (the `<old>..<new>  main -> main` line), and from then on note
   `git -C "$MAIN" rev-parse --short origin/main` before each push (SKILL.md § Report).
   With `Push: none` or no `origin`, `old` is `main` before the batch's first merge (that
   merge's first parent), and the line says `(local main)`.

Rules that keep it pasteable:

- **Never a table.** Tables paste badly into chat, email and phones. Also leave out
  headings, nested bullets and bold.
- Put it in its own fenced `text` block, separate from the Report, so the operator can
  copy it exactly as written. The fence only marks what to copy; it is not part of the
  message.
- Backticks only around a command a reader must type, where Slack and Teams, the main
  targets, show it as code. Everywhere else write names plainly: in email or SMS the
  backticks appear as literal characters.
- Keep it short. If a bullet needs a second line, it is describing how the change was
  made, not what changed.
- Paths are fine. Secret values never appear, just as in the Report.

## Example

A push that landed three items and changed plugin files:

```text
claude-plugins updates, pushed to main:
- The librarian now reads plan quota before it dispatches, and slows down near a limit instead of stalling.
- Checkpoints stamp their own time fields, so a resumed session no longer reads a fresh handoff as stale.
- The agent panel shows how much context each sub-agent has left.
What you need to do: run `/plugin marketplace update kmacmcfarlane`, then `/reload-plugins`.
Commits: eda3422..71345aa
```

A docs tree with `Push: none`:

```text
handbook updates, local only, not pushed:
- The onboarding page now covers laptop setup on Fedora.
Nothing to do.
Commits: 1a2b3c4..5d6e7f8 (local main)
```
