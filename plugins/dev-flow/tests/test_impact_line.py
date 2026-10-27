"""The librarian's stored card keeps each option's own impact, and the closed views read it.

Answer 206 (a), widened (2026-10-14): the decisions skill's chat cards define the Impact across
all the options, favouring none, as its answer page does, and show each option's own effect,
reach, undo and cost under it. The librarian stores what those views read.

Answer 260 (a) (2026-10-20): undo is shown only on an option that is one-way or costly to
undo, and the Impact carries it only when some option is. The store keeps the marker: no rule
still asks for an undo on every option of a ⚠ decision, and the read-back keys on the marker.

The operator's v5 ruling (2026-10-22) and answer 340 (a) (2026-10-23): no card shows a
card-level effect, so where a closed view shows one effect, the Report's tag size and the
Groom row, it is the recommended option's own: at tag size its letter first,
`46 (→ (a) preview up in about 4 minutes)`; on the Groom row, which already shows `rec (x)`,
after that letter, not repeated: `— rec (b) → <effect>`.

The store keeps card records (answers 341 (a)–343 (a), feature K3 of the v5 card layout plan):
a decision is raised with `$WI raise … --record` from the card the decisions skill's
card-record reference defines, so `decisions.md` holds no stored `impact:` or option-line
template of its own; the rules above stand on the record's `impact`, `effect`, `undo` and
`oneway`, and older stored lines are read by the decisions skill's legacy reference. The Groom
row reads the effect from the record (`$WI show <id> --card N --json`), a legacy card's from
its option line. (The `work-items` format's card-lines paragraph is checked in that plugin's
own suite.)

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LIB = PLUGIN / "skills" / "librarian-mode"
DECISIONS = LIB / "references" / "decisions.md"
IDLE = LIB / "references" / "idle-turn.md"
REPORT = LIB / "references" / "report.md"
CYCLE = PLUGIN / "skills" / "dev-cycle" / "SKILL.md"
LEGACY_POINTER = "legacy cards are read by the decisions skill's legacy reference"


def flat(path):
    return " ".join(path.read_text().split())


def record_problems(text):
    """decisions.md raises a card record with `$WI raise … --record`, names the card-record
    reference, and stores no `impact:` or option-line template of its own."""
    out = []
    if "$WI raise <id> --record" not in text:
        out.append("no `$WI raise <id> --record`")
    if "`references/card-record.md`" not in text:
        out.append("no card-record reference")
    if any(x.strip().startswith("impact: → ") for x in text.splitlines()):
        out.append("an `impact: → ` template is stored")
    if any(x.strip().startswith("(a) <option> — ") for x in text.splitlines()):
        out.append("an option-line template is stored")
    return out


class ImpactLine(unittest.TestCase):

    def test_the_store_raises_records(self):
        text = DECISIONS.read_text()
        self.assertEqual(record_problems(text), [])
        # mutants: the stored templates restored; the raise without --record; no reference
        self.assertIn("an `impact: → ` template is stored",
                      record_problems(text + "\n    impact: → <effect> · later: <wait>\n"))
        self.assertIn("an option-line template is stored",
                      record_problems(text + "\n    (a) <option> — <its effect>\n"))
        self.assertIn("no `$WI raise <id> --record`",
                      record_problems(text.replace("$WI raise <id> --record", "$WI raise <id> --")))
        self.assertIn("no card-record reference",
                      record_problems(text.replace("`references/card-record.md`", "the record")))

    def test_the_impact_covers_the_options(self):
        text = flat(DECISIONS)
        self.assertIn("**The Impact** (`impact`), across all its options, favouring none", text)
        self.assertIn("There is no card-level effect: each option carries its own", text)

    def test_older_lines_are_read_as_written(self):
        text = flat(DECISIONS)
        self.assertIn(LEGACY_POINTER, text)
        # the dated clauses left for the legacy reference
        for gone in ("An `impact:` line stored before Effect covered the options",
                     "it is read as written, never rewritten at render time",
                     "may carry `who:` in place of `reach:`",
                     "which a card stored before it keeps as written"):
            self.assertNotIn(gone, text)

    def test_each_option_holds_its_own_impact(self):
        self.assertIn("**Each option holds its own impact**: its `effect`, then `reach`, `undo` "
                      "and `cost` where they apply", flat(DECISIONS))

    def test_tag_size_examples_show_the_recommended_effect(self):
        for f in (REPORT, CYCLE, DECISIONS):
            self.assertEqual(tag_size_problems(f.name, f.read_text()), [])
        # mutants: the old example, across the options; the letter dropped
        old = "`46 (→ (a) preview up in about 4 minutes; (b) yesterday's page)`"
        self.assertTrue(tag_size_problems("mutant", old))
        self.assertTrue(tag_size_problems("mutant", "`46 (→ preview up in about 4 minutes)`"))

    def test_the_report_reads_the_record(self):
        for f in (REPORT, DECISIONS):
            self.assertIn("**Reading a card**; a legacy card's option line", flat(f), f.name)

    def test_a_row_showing_the_recommendation_carries_its_own_effect(self):
        flat_text = flat(IDLE)
        self.assertEqual(groom_problems(flat_text), [])
        # mutant: the row repeats the letter after its rec (x)
        mutant = flat_text.replace("`— rec (b) → <effect>`", "`— rec (b) → (b) <effect>`")
        self.assertNotEqual(mutant, flat_text)
        self.assertIn("the Groom row repeats the recommended letter", groom_problems(mutant))
        # mutant: the row reads the stored lines, not the record
        mutant = flat_text.replace("`$WI show <id> --card N --json`", "the stored lines")
        self.assertNotEqual(mutant, flat_text)
        self.assertIn("missing: `$WI show <id> --card N --json`", groom_problems(mutant))
        # mutant: a Groom row upgrades the card
        mutant = flat_text.replace("so it never upgrades or backfills the card",
                                   "so it upgrades the card first")
        self.assertNotEqual(mutant, flat_text)
        self.assertTrue(groom_problems(mutant))


TAG_EXAMPLE = "46 (→ (a) preview up in about 4 minutes)"


def tag_size_problems(where, text):
    """The tag-size example shows the recommended option's effect, its letter first, and no
    other option's after it."""
    flat_text = " ".join(text.split())
    out = []
    if TAG_EXAMPLE not in flat_text:
        out.append(f"{where}: no tag-size example with the recommended option's effect")
    if re.search(r"46 \(→ \(a\) preview up in about 4 minutes; \(b\) ", flat_text):
        out.append(f"{where}: the tag size gives every option's effect")
    if re.search(r"46 \(→ preview up", flat_text):
        out.append(f"{where}: the tag size drops the letter")
    return out


GROOM = ("read from the last card stored for N",
         "`$WI show <id> --card N --json`",
         "the recommended option's own effect from the record's option",
         "the arrow follows that letter and the letter is not repeated",
         "`— rec (b) → <effect>`",
         "A legacy card (no `card:` line) gives the recommended option's effect from its option "
         "line", "never from the `impact:` line",
         "a Groom row is no touch, so it never upgrades or backfills the card")


def groom_problems(text):
    """The Groom row's effect: the recommended option's own, from the card record, after the
    row's `rec (x)` with the letter not repeated; a legacy card's from its option line, never
    from its `impact:` line; and the row never upgrades the card."""
    flat_text = " ".join(text.split())
    out = ["missing: " + phrase for phrase in GROOM if phrase not in flat_text]
    if re.search(r"rec \(([a-y])\) → \(\1\)", flat_text) or "`→ (x) <effect>`" in flat_text:
        out.append("the Groom row repeats the recommended letter")
    return out


# rules 259 and 268 in the store (decision-page parity, S6): the two clauses, each with a mutant
SYSTEM_CLAUSE = "Effect and Reach are about the thing the work builds, never the process, which is Wait"
MECH_CLAUSE = "each option's `effect` gives it by its mechanism, how it happens"


def store_clause_problems(text):
    flat_text = " ".join(text.split())
    out = []
    if SYSTEM_CLAUSE not in flat_text:
        out.append("no system clause (259)")
    if MECH_CLAUSE not in flat_text:
        out.append("no mechanism clause (268)")
    return out


class StoredRules(unittest.TestCase):

    def test_both_clauses(self):
        self.assertEqual(store_clause_problems(DECISIONS.read_text()), [])

    def test_mutations(self):
        text = flat(DECISIONS)
        self.assertIn("no system clause (259)",
                      store_clause_problems(text.replace("never the process, which is Wait", "")))
        self.assertIn("no mechanism clause (268)",
                      store_clause_problems(text.replace("by its mechanism, how it happens", "plainly")))


UNDO_RULES = [
    "**Undo is stored only where it bites** (answer 260 (a))",
    "carries `oneway: true` and its `undo`",
    "never one without the other, since the marker decides the read-back",
    "An option with no `undo` is reversible at little cost",
    "The marker marks the option, never the decision",
    "`undo` only when some option is one-way or costly to undo",
    "**A one-way choice on a ⚠ decision** (the chosen option carries `oneway: true` and its "
    "`undo` in the record",
]

REVERSED = ("every option line carries its `reach:` and `undo:`",
            "on a ⚠ decision every option line carries its undo",
            "a block's missing `undo:`")


def undo_problems(text):
    flat_text = " ".join(text.split())
    out = ["missing: " + p for p in UNDO_RULES if p not in flat_text]
    out += ["reversed rule kept: " + r for r in REVERSED if r in flat_text]
    return out


class UndoMarker(unittest.TestCase):
    """Undo only where it bites, and the read-back keyed on the marker, as rules on the
    record's `undo` and `oneway`; older plain undos are the legacy reference's."""

    def test_the_record_marks_its_optional_undo(self):
        self.assertEqual(undo_problems(DECISIONS.read_text()), [])

    def test_undo_mutants(self):
        flat_text = flat(DECISIONS)
        for phrase in UNDO_RULES:
            cut = flat_text.replace(phrase, "gone")
            self.assertNotEqual(cut, flat_text, phrase)
            self.assertTrue(undo_problems(cut), phrase)
        # a rule answer 260 reversed, restored
        self.assertTrue(undo_problems(flat_text + " on a ⚠ decision every option line carries its undo"))

    def test_older_plain_undos_read_as_written(self):
        text = flat(DECISIONS)
        self.assertNotIn("may carry a plain `undo:` on every option and on its `impact:` line", text)
        self.assertIn(LEGACY_POINTER, text)
        self.assertIn("on a legacy card, what the legacy reference reads as the marker", text)


if __name__ == "__main__":
    unittest.main()
