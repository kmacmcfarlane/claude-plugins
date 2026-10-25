"""The librarian's stored `impact:` line gives the Effect across all the options.

Answer 206 (a), widened (2026-10-14): the decisions skill's chat cards define Effect as the
decision's impact across all its options, favouring none, as its answer page does, and show
each option's own effect, reach, undo and cost under it. The librarian stores what those
views read, so its definition follows, and lines stored before stay readable as written.

Answer 260 (a) (2026-10-20): undo is shown only on an option that is one-way or costly to
undo, marked `⚠ undo:`, and the Impact line carries it only when some option is. The store
keeps the marker (feature C1 of the decision-card feedback plan): the `impact:` and option
templates mark their undo and carry it only as an optional facet, no rule still asks for an
undo on every option of a ⚠ decision, the read-back keys on the marker, and older stored
plain undos read as written. (The `work-items` format's card-lines paragraph, which
describes the same `impact:` line, is checked in that plugin's own suite.)

The operator's v5 ruling (2026-10-22) and answer 340 (a) (2026-10-23): no card shows a
card-level effect, so where a closed view shows one effect, the Report's tag size and the
Groom row, it is the recommended option's own, its letter first, read from its option line:
`46 (→ (a) preview up in about 4 minutes)`. (The stored `impact:` line itself is the store's,
re-pointed when the store keeps card records.)

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
# an undo written without its marker
BARE_UNDO = re.compile(r"(?<!⚠ )\bundo: ")


def flat(path):
    return " ".join(path.read_text().split())


def template(text, start):
    return next(x for x in text.splitlines() if x.strip().startswith(start))


class ImpactLine(unittest.TestCase):

    def test_the_stored_effect_covers_the_options(self):
        text = DECISIONS.read_text()
        self.assertNotIn("Effect (the recommended option's;", text)
        self.assertIn("across all its options, favouring none", text)
        tmpl = next(x for x in text.splitlines() if x.strip().startswith("impact: → "))
        self.assertIn("(a) …; (b) …", tmpl)

    def test_older_lines_are_read_as_written(self):
        text = DECISIONS.read_text()
        self.assertIn("it is read as written, never rewritten at render time", text)

    def test_each_option_line_holds_its_own_impact(self):
        text = DECISIONS.read_text()
        self.assertIn("each option line holds that option's own", " ".join(text.split()))

    def test_tag_size_examples_show_the_recommended_effect(self):
        for f in (REPORT, CYCLE, DECISIONS):
            self.assertEqual(tag_size_problems(f.name, f.read_text()), [])
        # mutants: the old example, across the options; the letter dropped
        old = "`46 (→ (a) preview up in about 4 minutes; (b) yesterday's page)`"
        self.assertTrue(tag_size_problems("mutant", old))
        self.assertTrue(tag_size_problems("mutant", "`46 (→ preview up in about 4 minutes)`"))

    def test_a_row_showing_the_recommendation_carries_its_own_effect(self):
        flat = " ".join(IDLE.read_text().split())
        self.assertIn("read from the last card stored for N", flat)
        self.assertIn("the recommended option's own effect from its option line", flat)
        self.assertIn("its letter first", flat)
        self.assertIn("`→ (x) <effect>`", flat)
        self.assertIn("never from the `impact:` line", flat)


TAG_EXAMPLE = "46 (→ (a) preview up in about 4 minutes)"


def tag_size_problems(where, text):
    """The tag-size example shows the recommended option's effect, its letter first, and no
    other option's after it."""
    flat = " ".join(text.split())
    out = []
    if TAG_EXAMPLE not in flat:
        out.append(f"{where}: no tag-size example with the recommended option's effect")
    if re.search(r"46 \(→ \(a\) preview up in about 4 minutes; \(b\) ", flat):
        out.append(f"{where}: the tag size gives every option's effect")
    if re.search(r"46 \(→ preview up", flat):
        out.append(f"{where}: the tag size drops the letter")
    return out


# rules 259 and 268 in the store (decision-page parity, S6): the two clauses, each with a mutant
SYSTEM_CLAUSE = "Effect and Reach are about the thing the work builds, never the process, which is Wait"
MECH_TEMPLATE = "(a) <option> — <its effect, by its mechanism>"


def store_clause_problems(text):
    out = []
    if SYSTEM_CLAUSE not in " ".join(text.split()):
        out.append("no system clause (259)")
    if MECH_TEMPLATE not in text or "by its mechanism, how it happens" not in " ".join(text.split()):
        out.append("no mechanism clause (268)")
    return out


class StoredRules(unittest.TestCase):

    def test_both_clauses(self):
        self.assertEqual(store_clause_problems(DECISIONS.read_text()), [])

    def test_mutations(self):
        text = DECISIONS.read_text()
        self.assertIn("no system clause (259)",
                      store_clause_problems(text.replace("never the process, which is Wait", "")))
        self.assertIn("no mechanism clause (268)",
                      store_clause_problems(text.replace("<its effect, by its mechanism>", "<its effect>")))


class UndoMarker(unittest.TestCase):

    def test_the_impact_template_marks_its_optional_undo(self):
        tmpl = template(DECISIONS.read_text(), "impact: → ")
        self.assertIn("[· ⚠ undo: ", tmpl)
        self.assertIsNone(BARE_UNDO.search(tmpl), tmpl)

    def test_the_option_template_marks_its_optional_undo(self):
        tmpl = template(DECISIONS.read_text(), "(a) <option> — ")
        self.assertIn("[— ⚠ undo: ", tmpl)
        self.assertIsNone(BARE_UNDO.search(tmpl), tmpl)

    def test_undo_is_stored_only_where_it_bites(self):
        text = flat(DECISIONS)
        self.assertIn("An option line with no undo is reversible at little cost", text)
        # the rules answer 260 reversed are gone
        self.assertNotIn("every option line carries its `reach:` and `undo:`", text)
        self.assertNotIn("on a ⚠ decision every option line carries its undo", text)
        self.assertNotIn("a block's missing `undo:`", text)
        # the backfill trigger honours an older card's plain undo read as the marker
        self.assertIn("a ⚠ one-way decision with no option marked `⚠ undo:` (on a card stored "
                      "before the marker, a plain `undo:` that reads as the marker counts)", text)

    def test_the_read_back_keys_on_the_marker(self):
        text = flat(DECISIONS)
        self.assertIn("**A one-way choice on a ⚠ decision** (the chosen option's line carries "
                      "`⚠ undo:`", text)

    def test_older_plain_undos_read_as_written(self):
        text = flat(DECISIONS)
        self.assertIn("may carry a plain `undo:` on every option and on its `impact:` line", text)
        self.assertIn("is read as the marker", text)


if __name__ == "__main__":
    unittest.main()
