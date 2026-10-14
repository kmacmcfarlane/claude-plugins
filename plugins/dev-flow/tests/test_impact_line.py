"""The librarian's stored `impact:` line gives the Effect across all the options.

Answer 206 (a), widened (2026-10-14): the decisions skill's chat cards define Effect as the
decision's impact across all its options, favouring none, as its answer page does, and show
each option's own effect, reach, undo and cost under it. The librarian stores what those
views read, so its definition follows, and lines stored before stay readable as written.

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

    def test_tag_size_examples_cover_the_options(self):
        for f in (REPORT, CYCLE, DECISIONS):
            flat = " ".join(f.read_text().split())
            self.assertNotRegex(flat, r"46 \(→ preview up", f.name)
            self.assertRegex(flat, r"46 \(→ \(a\) preview up in about 4 minutes; \(b\) ", f.name)

    def test_a_row_showing_the_recommendation_carries_its_own_effect(self):
        flat = " ".join(IDLE.read_text().split())
        self.assertIn("read from the last card stored for N", flat)
        self.assertIn("the recommended option's own effect from its option line", flat)


if __name__ == "__main__":
    unittest.main()
