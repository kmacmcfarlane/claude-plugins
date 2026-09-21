---
name: usage-report
description: Report Claude Code token spend across conversations — per session, per model and per sub-agent dispatch — from the local transcripts, so model routing can be measured. Stub. The parser, the versioned price table and its tests are in place; the report tables, the worked instructions and the catalog row land in the follow-up feature that completes this skill.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "scan | summary [--all] [--since 7d] [--json]"
---

# Usage report

Not yet a workflow. Everything that exists today lives in the script:

```bash
python3 scripts/usage_report.py --help
```

It reads the transcripts under the Claude Code config directory read-only, dedupes
each API response by (`message.id`, `requestId`) across every file it reads, keeping
the line with the most output tokens, joins every sub-agent dispatch to its parent
session and its requested tier, and prices tokens from `scripts/prices.json` — a
versioned list-price table, not a bill. `scan` lists what it found; `summary --json`
emits the totals. The tables and the instructions for using them are the follow-up.
