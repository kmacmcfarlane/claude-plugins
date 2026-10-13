---
name: usage-report
description: Report Claude Code token spend across conversations — per session, per model and per sub-agent dispatch — from the local transcripts, so model routing can be measured; and read one work item's list-price spend per phase by the agent ids on its record. Stub otherwise. The parser, the versioned price table, the item reader and their tests are in place; the report tables, the worked instructions and the catalog row land in the follow-up feature that completes this skill.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "scan | summary [--all] [--since 7d] [--json] | item <item file> [--json]"
---

# Usage report

Not yet a workflow. Everything that exists today lives in the scripts:

```bash
python3 scripts/usage_report.py --help
```

It reads the transcripts under the Claude Code config directory read-only, dedupes
each API response by (`message.id`, `requestId`) across every file it reads, keeping
the line with the most output tokens, joins every sub-agent dispatch to its parent
session and its requested tier, and prices tokens from `scripts/prices.json` — a
versioned list-price table, not a bill. `scan` lists what it found; `summary --json`
emits the totals. The tables and the instructions for using them are the follow-up.

## One item's spend

```bash
python3 scripts/usage_report.py item <item file> [--json] [--per-percent D | --week-used P --week-resets-at T | --no-week]
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
