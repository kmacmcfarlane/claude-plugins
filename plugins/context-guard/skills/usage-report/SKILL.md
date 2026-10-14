---
name: usage-report
description: Report Claude Code token spend across conversations from the local transcripts — totals, then tables by served model, by requested dispatch tier (with the main sessions' own turns as `main`), by UTC day, by session and by sub-agent dispatch — in tokens by class, Opus-equivalent tokens and a list-price dollar estimate, so model routing can be measured; and read one work item's list-price spend per phase by the agent ids on its record. Use when the user says "usage report", "token spend", "what did this cost", "how much went to sub-agents", "is the routing paying off", "spend by model", or asks how one work item's budget was spent. Read-only and offline; dollars are an estimate, not a bill.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "report [--all] [--since 7d] [--flat] [--top N] [--json] | item <item file> [--json]"
---

# Usage report

Account for where tokens went: which models served them, which dispatch tiers asked for
them, on which days, in which sessions and in which sub-agent dispatches. The script reads
the transcripts under the Claude Code config directory and nothing else; it never writes,
never calls the network, and is never wired into a hook or the status line (it re-reads
whole transcripts).

## Run it

Run from the project whose spend you want: the scope is the project directory matching
the working directory (a worktree with no transcripts of its own resolves to its project;
one with its own sessions is its own scope, and `--all` covers both).

```bash
UR="${CLAUDE_PLUGIN_ROOT}/skills/usage-report/scripts/usage_report.py"
python3 -I "$UR" report                 # this project, all time
python3 -I "$UR" report --since 7d      # the last seven days (or an ISO date)
python3 -I "$UR" report --all           # every project
python3 -I "$UR" report --flat          # nested dispatches as their own rows
python3 -I "$UR" report --top 0         # every session and dispatch row
python3 -I "$UR" report --json          # the same data, whole, for an artifact or a script
```

Pass the user's arguments through. `summary` prints the totals alone, `scan` lists the
files read, and `--help` lists every flag. Warnings go to stderr: an unknown model, or a
price table with entries marked uncertain.

## Read the tables

Every table has the same columns: `input`, `output`, `cache wr` (cache creation), `cache rd`
(cache read), `opus-eq`, `$ est` and `share` (the row's part of the total estimated
dollars). Token counts are short (`1.2k`, `5.6M`).

- **The header** names the scope, the window, whether dispatches are rolled up, the price
  table's version and date, and the counts: sessions and dispatch rows with spend, API
  responses, compactions, and duplicate lines dropped.
- **Opus-equivalent tokens** weight each token class by its price on the model that served
  it over its price on the normalization base (Opus): the tokens Opus would have used for the
  same dollars. It is the unit for judging routing, because it holds when the dollars are
  not what is billed.
- **By model (served)** is what actually answered, from each response's own model. A row
  marked `*` includes model ids priced through an alias in `scripts/prices.json` (a legacy
  id priced as its current same-family entry); the note under the table names each one and
  its share. A row named `unknown:<id>` is a model the table does not know, priced at the
  default model so the total is not short, and warned about; add the model to the table.
- **By requested tier** is what each dispatch asked for (`sonnet`, `opus`, `fable`, or
  `inherit` when it named none), plus `main`, the main sessions' own turns. It sums to the
  totals. Set beside By model, it shows routing at work: tokens asked for at one tier and
  served by another, and how much of the spend the main session keeps.
- **By day (UTC)** buckets each response by its UTC date.
- **Sessions** and **Dispatches** are sorted by estimated dollars, `--top` rows each
  (default 10). A dispatch row rolls its nested dispatches into it by default (`+N` after the
  type); `--flat` gives each its own row. `served` lists the models that answered it.

Records are counted once per API response, keyed by (`message.id`, `requestId`) across
every file read, keeping the line with the most output tokens, so a response repeated in
another file also counts once. As observed in local transcripts (Claude Code 2.1.285 and
2.1.292, counted with a script over one session's file; 2.1.292 sub-agent transcripts),
about half the responses are written as two or more lines for the same response (in a
main transcript the usage block repeats; in a sub-agent transcript an earlier line carries
a partial `output_tokens`), so a sum over every line over-counts. A response with zero
tokens in every class is skipped.

## Dollars are an estimate

`$ est` is list price from `scripts/prices.json`, a versioned table with its source URL and
retrieval date. It is not a bill: on a subscription plan the dollar figure is not what is
charged, and the docs say so for `/usage` too (https://code.claude.com/docs/en/costs). Fast
mode and the batch discount are not modelled. Use the dollars, and the Opus-equivalent
figure, to compare one slice against another, not as an invoice.

## Reconcile before you publish a number

Two local counters can disagree, so check this report against Claude Code's own `/usage`
view before a figure leaves the conversation. `/usage` shows the current session's tokens
by model and a locally computed cost (https://code.claude.com/docs/en/costs).

1. Run `/usage` in the session to reconcile and note its per-model token counts.
2. From that same session, print its row from the report (`$CLAUDE_CODE_SESSION_ID` is
   the current session's id in the Bash tool, https://code.claude.com/docs/en/env-vars):

   ```bash
   python3 -I "$UR" report --json | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps([r for r in d["sessions"] if r["session_id"] == sys.argv[1]], indent=2))' "$CLAUDE_CODE_SESSION_ID"
   ```

   The row has `main` (the main conversation's own turns), `totals` (with its dispatches)
   and `by_model` (the totals split by served model).
3. Compare model by model, against `main` and against `totals`. A match within a few
   percent on either is a pass; say which one matched. A wider gap means the number is not
   ready to publish: report both figures and the gap instead of either one.

## One item's spend

```bash
python3 -I "$UR" item <item file> [--json] [--per-percent D | --week-used P --week-resets-at T | --no-week]
```

Reads the item's `agent:` lines, joins every agent id on them to its transcript, and
prints the list-price spend per phase (`plan`, `build`), the cumulative spend after
each review, the share of the week, and the flags. The rules are in
`scripts/item_spend.py`'s docstring; in short:

- every agent id on any `agent:` line counts, whatever the line's shape; every
  transcript segment counts (`unrecorded` when an id has more rounds than lines,
  `lost` when fewer); nested agents count, placed by their own start times;
- phases split by time against timestamped `budget: <UTC> <phase> $<total> — <source>`
  lines; with none, they are inferred and flagged;
- Claude models only; zero-token `<synthetic>` records are skipped; a Claude model the
  price table does not know makes its phase **unread**, never priced as another;
- an agent whose transcript is gone reads through the phase's last
  `cost: <UTC> <phase> $<spent> of $<budget> …` line plus the segments after it, or is
  unread;
- the share of the week is spend over this window's measured local rate (local Claude
  spend since the window opened, over the weekly `used_percentage` from the status-line
  sensor record or `--week-used`); below 10% used, or with no reading, dollars stand alone.

`--json` gives the same reading as data, with `reading: read | unread` per phase and
for the item.
