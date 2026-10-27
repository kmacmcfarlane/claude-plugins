# Card writers

How a page's cards are shared among writers, what every writer is briefed with, and how their
records come back together as one `cards.json`. A page of `WRITER_CAP` cards or fewer has one
writer, and the caller may write it itself; the rest of this file is for a page over that.

## The split

**Layers first.** The caller has already chosen each card's layer `L` and its `dep`:

- **The layer** is the card's stored group where the caller keeps one (a librarian's group
  lines): the layer's key is the group id, its title the group's plain name, never the id, its
  note what its members share, and its `shared` the group's shared context. With no store,
  related decisions form the layers as the `decisions` skill groups them, each keyed by its
  name case-folded, with whitespace collapsed and spaces turned to hyphens (`Page parity  with
  chat` → `page-parity-with-chat`); names that compare equal share one layer.
- **Cards in no group** go in one last layer: key `other`, title *Other decisions*, note *not
  grouped with another decision; each stands alone*. It is the page's alone: chat shows a lone
  decision with no heading.
- **The dependency** is the card's stored dependency where the caller keeps one, written in
  the dependency line's sentence form with slugs (`references/cards-schema.md` § A page card,
  *The dependency line*). A decision a card depends on that is not on the page goes in `refs`
  when it is answered; an open one is added to the page as a card, so it lands with its
  dependents.
- Inside every layer, cards are in the `decisions` skill's order: each after every card in its
  layer that its `dep` names.

**The skeleton.** The caller writes the page in outline, in page order: `layers`, each card's
`n`, `L` and `dep`, and the `refs` keys (`{"layers": [[key, title, note], …], "cards": [{"n",
"L", "dep"}, …], "refs": {"38": {}}}`; anything else is ignored). Then it splits it:

```bash
node scripts/split_writers.js [--cap N] skeleton.json
```

run from this skill's base directory. It prints `{"cap", "writers": [{"cards": [n…],
"layers": [key…], "over_cap": bool}], "notes": […]}`, each writer's cards in page order, and
exits 1 on a skeleton it cannot read (a card with no `n` or `L`, an `L` not in `layers`, a
repeated `n`, the `other` layer not last). The rule it applies, short enough to apply by hand
where there is no node:

1. Cards that share a layer are linked. A card is linked to each `[[M]]` in its `dep` that is
   a card on the page. The linked sets, closed transitively, are the **units**. A `[[M]]` in
   `refs` is neither linked nor reported; any other is a note: "card N depends on [[M]], which
   is neither a card on this page nor a ref: add it as a card".
2. Total cards at or under the cap give one writer.
3. A unit over the cap is split into **atoms**, the sets linked by `dep` alone, closed
   transitively. Atoms are packed in page order (by their first card's layer, then position)
   into pieces at or under the cap. An atom over the cap stays whole on a writer of its own,
   marked over cap. A depends chain is never cut; only same-layer links are.
4. Units, and the pieces of split units, are packed in page order. Each writer takes the next
   whole one while the total stays at or under the cap, so several small groups share a
   writer, and a group is never split across writers except over the cap.

**The cap.** `WRITER_CAP = 15` cards per writer, at or under. It is an estimate from one
observation, not a measurement: 22 cards came to about 27k tokens of card text, and fifteen
leaves a writer room for its cards' sources beside the shared reading (step 2 of `SKILL.md`,
the digest, the `decisions` floor). It counts cards, not tokens: pass a lower `--cap` when the
sources are heavy. It is tuned from the writers' runs: the caller records each writer's cards,
tokens and first-check lints.

## The brief

Whenever there are two or more writers, every writer gets the same digest and the same
finished example card, so the cards read as one page.

1. **The example card first.** The caller writes, or writer 1 writes as its first step, the
   first card in page order, at every level its decision scales to, as a `decision-card/5`
   record (the `decisions` skill's `references/card-record.md`). It is checked with
   `node scripts/check_cards.js --record <file>` until it has no refusal and every lint is
   fixed or left knowingly, before the other writers start. That card, from the current set,
   is the example.
2. **Every writer's brief**, in this order:
   - the writer digest (`references/writer-digest.md`, pasted or by path);
   - the example card's JSON, labelled "match its voice, density and level shapes; do not copy
     its facts";
   - the `decisions` skill's floor, by pointer;
   - the page's whole `layers` list and every card's `n` and `t`, so slugs, layer keys and
     short names agree across writers;
   - the id → plain-name map;
   - its own card numbers, their approved text and their source paths.
3. Writer 1 keeps the example card, unchanged unless the merged check names it.

With one writer there is no example stage, and the brief is the digest alone.

## The merge

- **A writer returns records**: one `decision-card/5` record per card it was given, each
  checked with `node scripts/check_cards.js --record <file>` before it is handed back. A writer
  never writes `L`, `dep` or `refs`: they are the caller's, from the skeleton.
- **The caller stores them**, each with its store's write path (a new decision raised, a
  revision as a new revision); a caller with no store keeps the checked files.
- **The caller builds `cards.json` from the records it has stored**, not from the writers'
  files: the envelope (`format`, `page`, `layers`, `follow`), then each card in page order, its
  stored record plus its `L` and `dep`, then the page's `refs`. So the page shows exactly what
  the store holds, and a record the store refused never reaches it.
- **One check over the whole file**: `node scripts/check_cards.js cards.json`, once. Each line
  goes back to the writer of the card it names, whose fix is a new revision stored the same
  way, or the caller fixes it itself; a `page:` line is the caller's.
