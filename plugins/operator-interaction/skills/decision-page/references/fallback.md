# When the page cannot be used

Two steps down, taken in order. Say which one you took, and why, in the message that hands
the decisions over: *The answer page needs the db capability, which this session doesn't
have, so the decisions are in a doc with tick boxes instead.*

## 1. A doc with tick boxes

When page artifacts or the `db` capability are unavailable but a docs tool is (a Claude Docs
connector, or another document tool the session lists), put the decisions in one doc.
Follow that tool's own instructions for creating and filling it (load its skill or guide
first); this file sets only the layout.

- One heading per group, in list order, with a short table of contents, as the page's map
  gives one: its decisions by number and short name; a bundle's (a layer with `shared`) reads
  `<title> — N decisions, <note>`, then a **Shared context:** line with its shared context; under it, one section per decision, headed with its
  number, short name and the recommended option's effect, its letter first, as the page's row
  shows it: `41 · Docs build home → (b) every merge to main builds and publishes the site from
  CI`; with no recommendation, each option's in a few words, `→ (a) …; (b) …`; a card with a
  `label` puts the label and its short name after its own, `43 · Theme colour · D3 (site
  colour off the logo) → …`.
- In each section, the card's essentials as text: the TLDR bullets first, then **Context:**
  (the terms the card uses, then where the operator left it), then ⚠ one-way when it is and
  **Impact:**, across all the options, describing the system the work builds, never the review or
  the process (what waiting holds up is its `later:` line), one facet a line (`later: …`, `reach: …`,
  `⚠ undo: …` only when an option is one-way or costly, `cost: …` where given, each on its own
  line; there is no card-level effect). There is no Rec line: the recommended option is the
  bold one.
  Each card also gets its options' table: a row per option, then the Wait row; Effect, Reach,
  Undo, Cost, each option's own, then Pros and Cons, its one-line `pro` and `con` (as the
  page's rows under each option).
- A doc cannot toggle a level, so each part shows one rendition. **Context** is at its top
  level, its high in `detail` when it has one: that high holds the facts a cold reader has
  lost (the `decisions` skill's `references/card-record.md` § Levels), and a doc reader has no
  click to reach it. The Impact line and the TLDR are at their summary. After the Impact and
  the options' table, a **More detail** sub-heading carries the fold parts at their top level,
  in the card's v5 order: the **Open questions** as a list (the fold above the Impact), then
  **Assumptions** (the fold under it): a **Basis:** line with the basis word and `reason`, the
  Evidence with its paths and links, then each assumption in bold with its *tripwire:* under
  it; then each option's view, in the page's order: its **Plan in brief** (its `plan`, or an older
  option's `text`), its **Pros | Cons** table (`pros` and `cons`, two columns), then its Effect,
  Reach, Undo and Cost; then **Background**, the first fold
  after the options, a bold line with **Why now:** and **Why ask:** (class first) under it (a
  doc cannot fold, so the fold's content sits there, where the page keeps it closed), then
  Depends on. That is the card-in-all measure of
  `references/cards-schema.md` § Size, with Context at its high. A level in sections shows
  each heading as a bold line, its bullets under it.
- No ids: items, commits and series by their short names or titles, as on the page
  (`references/cards-schema.md` § No ids on the page).
- Then a tick box per option, in letter order, the recommended one in bold, each with its own
  `effect`: `☐ **(b) Publish from CI** — every merge to main builds and publishes the site
  from CI`.
- When an option has `act`, after the option tick boxes: **To act on (x):** with its numbered
  steps, as the option gives them, per option that has them.
- Then a tick box per follow-up, with its placeholder: `☐ later [when]`, `☐ tell me [what]`,
  `☐ expand`, `☐ dig into [what]`, `☐ you decide`, `☐ drop`.
- Then a line for the operator's words: `Your words:` with space to write.
- A slug becomes plain text with its short name: `[41 · Docs build home]`.

The doc cannot make the boxes exclusive. Tell the operator: *tick one box per decision; write
in Your words to add anything.* When reading it back:

- one box ticked: that is the choice; the words line is its words;
- **two or more boxes ticked, or a tick the words contradict: ask back in chat**, never pick
  one (the `decisions` skill's `references/replies.md`, a letter the words contradict);
- no box and words written: a words-only answer;
- nothing: unanswered.

When a decision changes after the doc is shared (an **Added:** line, a re-ask), rewrite its
section with every box unticked and say so in chat: ticks on the old text answered the old
card. Keep what you last handed over for each decision (its ticks and words), and hand over
only the decisions whose ticks or words differ from it; the rest are unchanged, not open.

For a caller that records shown and seen, hand over each decision's number, the time (UTC,
your clock) and the word *doc*: as shown, when the doc is shared and when a section is
rewritten unticked; as seen, with each decision a read-back hands over, and with no other.

Read the doc back with the same tool, then echo and hand over as SKILL.md's read-back step
says. The doc is the record of what was ticked: quote it, do not paraphrase it.

## 2. The plain decisions block

With no docs tool either, put the decisions to the operator in chat as the `decisions` skill
lays out several decisions in one message: cards in list order, then the list, then the hint.
Their replies are read as that skill's replies reference says.
