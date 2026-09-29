---
name: plain-names
description: "Name the things you mention to the operator (work items, tickets, branches, investigation series, commits) in plain words, with an id at most as a trailing tag, so they know what you mean without looking it up. Use whenever you write text the operator reads: a report or summary line, a decision echo, a table row, a relay or peer message meant for them, a hand-off note they will read. Not for agent-to-agent text (briefs, store and record lines, commit trailers, CLI arguments), which keeps full ids, except stored text the operator is shown as written, such as a stored decision card."
---

# Plain names

A bare id (`c4e1`, `7c41e0d`) is a black box to the operator. They read your text with their
attention, not with a lookup, so name what you mention the way they would say it, and let the
id trail as a tag at most.

*Examples in this skill are illustrative: invented, not about any real project.*

## When

Any text the operator reads: a report or summary line, a decision and its echo, a table row, a
relay or a peer message meant for them, a hand-off note they will read. That includes stored
text the operator is shown as written, such as a stored decision card.

**Exempt, full ids kept:**

- agent-only text: briefs, store and record lines, commit trailers, CLI arguments;
- anything a parser reads;
- decision numbers (`72: a`), the operator's answer handle;
- agent ids the operator copies to message or resume an agent;
- bookkeeping commit subjects (a tracker's own store commits), which stay terse.

## The rule

Name the thing (a work item, ticket, branch, investigation series or commit) by a **plain
name**: what it is, in about 3–6 words, the way the operator would say it. Then, at most, its
**short tag** in parentheses: *the flaky upload test (7c2a)*.

### The name

- **A stored short display name is the name**, where the tracker keeps one. Use its words
  verbatim, and add an article when the sentence needs one: stored `flaky upload test`,
  written *the flaky upload test (7c2a)*. The stored form carries no article.
- **Otherwise write one from the title and body, at each mention:**
  - drop a component prefix unless it disambiguates;
  - prefer the operator's own words for the thing;
  - put no id or tag inside it;
  - coin no new code word (no "W4", no "F2c") unless the operator already uses it.
- **Mentioning a thing never writes its name into the tracker.** A stored name is set by
  whoever files the thing, or later by its owner.
- **Keep one name per thing** for as long as the operator sees it: a session, or a run of
  reports.
- **No syntax words.** A name never contains a word its surrounding line uses as syntax. In a
  line whose end condition is read after "until", the name holds no "until".

### The tag

- The tag is the id's short form, and it trails the name, never replacing it. For an id that
  ends in four hex (`export-retry-fix-a1b2`), it is those four: `(a1b2)`.
- It is a recognition cue for someone who has seen the thing before, not a unique reference:
  one id's slug can begin with another id's four hex.
- Handed a bare tag, search the tracker by id suffix and also by id prefix, archived items
  included. One match is the item; more than one, ask which.
- Name a commit by what it did. Its short sha trails only when the operator may need it.

### Repeats and tables

- The first mention in a message carries the name and the tag. Later mentions in the same
  message use the name alone.
- A table cell holds `name (tag)`.

## Examples

An echo of a decision reply:

*Read as: 3 → (a) the search-index rebuild (c4e1) stays parked until the quota resets.*

Not: *Read as: 3 → (a) c4e1 stays parked until then.*

A report line about a change:

```
changed: the export retry fix (a1b2) — failed exports retry twice before alerting; 2 files
```

A table:

| item | next |
|---|---|
| export retry fix (a1b2) | review |
| docs cache cleanup (e5f6) | after the export retry fix |

A relay:

*From the billing session: the invoice-rounding bug (9f3c) is fixed on their side, so the
export retry fix can land.*

## When it goes wrong

- **A bare tag matches more than one item:** ask which, naming each candidate by its plain
  name and its own tag.
- **A stored name no longer fits the thing:** use it as stored all the same, and tell whoever
  owns the thing so they can change it. A mention never rewrites it.

## Rulings

The operator has ruled on these, except the two marked as not theirs. Each keeps the
alternative not taken, in case practice argues for it.

- **Handle** (2026-09-29) — a plain name, then the id's short tag trailing. Not taken: the
  name only; the title verbatim with the tag; the full id.
- **Home** (2026-09-29) — this generic skill, which the skills that write to the operator
  point at. Not taken: the decisions skill only; the tracker's own format reference; both.
- **Stored name** (2026-09-29) — a tracker's stored short display name is used verbatim, with
  an article added in prose; without one, a name is written from the title. Not taken: always
  writing it fresh; the tracker deriving it mechanically.
- **Report lines** (2026-09-29) — a report's line about a change leads with
  `<plain name> (<tag>)`. Not taken: the full id; the name with the full id.
- **Mentions store nothing** (2026-09-29; not the operator's ruling: the kit maintainer's
  call, made in plan review) — a name written at a mention is not stored; a stored name is
  set at filing, or later by the thing's owner. Not taken: storing the written name with the
  next write to the thing.
- **Bookkeeping commit subjects** (2026-09-29; delegated: the operator said "you decide") —
  these stay terse. Not taken: plain names there too.
