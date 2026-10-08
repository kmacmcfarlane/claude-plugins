# When the page cannot be used

Two steps down, taken in order. Say which one you took, and why, in the message that hands
the decisions over: *The answer page needs the db capability, which this session doesn't
have, so the decisions are in a doc with tick boxes instead.*

## 1. A doc with tick boxes

When page artifacts or the `db` capability are unavailable but a docs tool is (a Claude Docs
connector, or another document tool the session lists), put the decisions in one doc.
Follow that tool's own instructions for creating and filling it (load its skill or guide
first); this file sets only the layout.

- One heading per group, in list order; under it, one section per decision, headed with its
  number, short name and effect at tag size: `41 · Docs build home → publishing no longer
  depends on one laptop`.
- In each section, the card's essentials as text: the **Impact:** line first
  (`→ effect · later: wait · reach: … · undo: …`, ⚠ one-way before it when it is), then the
  TLDR bullets, **Context:** when there is one, **What:**, **Why now:**, **Why ask:** (class
  first), and the rec line `Rec (b) · basis strong — reason · unknown: …`. A card with
  `blocks` also gets the Impact table: a row per option, then the Wait row; Effect, Reach,
  Undo, Cost.
- Then a tick box per option, in letter order, the recommended one in bold, each with its
  impact: `☐ **(b) Publish from CI** — removes the one-machine dependency`.
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
