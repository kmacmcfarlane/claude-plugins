# Team summary

The four-line Report is the audit trail, for the operator. The team summary is for the
people the operator passes the news on to: teammates who did not watch the run and will
read it in Slack, Teams, an email or on a phone. Pointed at from SKILL.md § Report.

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

1. **A header line**: where it landed and the action needed to pick it up, in one line.
   Name the repo, the push outcome, the commit range, and the pickup step (or say none is
   needed). In a plugin marketplace, a change under `plugins/` reaches a user only after
   `/plugin marketplace update <marketplace name>` (the `name` in
   `.claude-plugin/marketplace.json`) and then `/reload-plugins`. `old` is `origin/main`
   before the push and `new` is `main` after it:

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
   merge's first parent), the header says `local only, not pushed`, and it carries no
   pickup step.

2. **One bullet per landed change**, a bold short title, then a colon and a short
   statement of WHAT changed for the people and agents who use the repo — never a commit
   subject or an item id. Leave out how the change was made or reviewed: no tiers,
   models, review rounds, fix rounds or verdicts. Several items that make one visible
   change share a bullet. Order the bullets by what the reader feels: the change most
   people will notice first, invisible plumbing last.

3. **One sub-bullet under each of those, two at most.** WHAT ONLY: an observable effect —
   what a user or agent can now do, or notices behaving differently — never why it was
   needed, how it works internally, its mechanism, its rationale, or the evidence behind
   it. At most two short fragments per line, semicolon-separated, not full sentences, and
   each fragment observable on its own — if it names a check, a stamp, a counter or
   anything else the code does, it is HOW, not WHAT.

4. **Maintenance and plumbing collapsed into ONE bullet**, marked `(maintenance)` —
   tests, refactors, dependency bumps, store bookkeeping. No sub-bullet needed; if one is
   useful, the same WHAT-only, two-fragment rule applies.

5. **A closing line**: whether anything requires action on existing work — a rule people
   now follow, a migration, a re-run of a setup step, a config written before this that
   now needs an update — or `Nothing on existing work needs action.` This is distinct
   from the header's pickup step, which is about picking up the change itself, not
   fixing or adjusting something older.

Rules that keep it pasteable:

- **Never a table.** Tables paste badly into chat, email and phones. No headings.
- Bold appears only on a bullet's title. Nesting goes one level deep — the WHAT-only
  sub-bullet — and no deeper.
- Put it in its own fenced `text` block, separate from the Report, so the operator can
  copy it exactly as written. The fence only marks what to copy; it is not part of the
  message.
- Backticks only around a command a reader must type, where Slack and Teams, the main
  targets, show it as code. Everywhere else write names plainly, including a commit
  range: in email or SMS the backticks appear as literal characters.
- Keep it short. A sub-bullet that needs a third fragment is carrying rationale or
  mechanism — cut it back to WHAT.
- Paths are fine. Secret values never appear, just as in the Report.

## Example

A push that landed three visible changes and a round of maintenance:

```text
claude-plugins updates, pushed to main (eda3422..71345aa) — run `/plugin marketplace update kmacmcfarlane`, then `/reload-plugins`.
- **Plan-usage pacing**: the librarian slows down near a plan limit instead of stalling.
  - A wave with plenty of quota left runs full speed; a wave running low moves slower instead of stopping.
- **Stable checkpoints**: a resumed session no longer treats a fresh handoff as stale.
  - Resuming right after a checkpoint picks up right where it left off; no stale-handoff false alarm.
- **Agent panel context**: each sub-agent's status line now shows how much context it has left.
  - Shows per agent in the agent panel; updates as the agent works.
- **Housekeeping** (maintenance): dependency bumps and test cleanup across three plugins.
Nothing on existing work needs action.
```
