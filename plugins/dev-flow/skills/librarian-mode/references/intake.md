# Intake

The detail behind SKILL.md § Intake's steps, which run in that order for every request.
Steps 3 to 5 live in SKILL.md, `forwarding.md` and `walkthroughs.md`.

## Step 1 — File it

The short display name is what you will call the item to the operator: 3–6 words, no id or
tag, no leading article, never the word "until" (a HOLD line reads it as syntax), **40
characters or fewer**. An exit 1 naming `short_display_name` means it is over 40
characters and nothing was written: shorten it and re-run. Any other exit 1 is the call's
own error (a title over 120 characters, a dep or parent that does not resolve, a line
break): fix that. An exit 2 naming `--short-display-name` means an older `wi`: file
without the flag, and write the name from the title at each mention. Only the item's
owner sets or changes the name later (`$WI set <id> short_display_name "<name>"`); a
mention never writes it.

## Step 2 — Peer requests: a forward

**A forward** (first line `forwarded from <repo> <id>`) is filed with that line in
`--ref`, and answered only after step 4's Scope check: `accepted <your id> for <repo>
<id>`, or `declined for <repo> <id>: <why>` (`forwarding.md`). When you close an accepted
one, tell the forwarder's session, when live: `landed <your id> for <repo> <id>`, or
`dropped <your id> for <repo> <id>: <why>` (when it is not, its read of your store finds
the close where the stores sit side by side; otherwise send it when that session is next
live).
