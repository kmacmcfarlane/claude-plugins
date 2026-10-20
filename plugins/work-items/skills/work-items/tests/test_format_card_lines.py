"""The format's card-lines paragraph marks the stored `impact:` line's undo.

Answer 260 (a) (2026-10-20): undo is shown only on an option that is one-way or costly to
undo, marked `⚠ undo:`. The librarian's stored card keeps that marker (feature C1 of the
decision-card feedback plan), and this format describes the same `impact:` line as text
`wi` does not parse: its undo is optional and marked, and an older plain `undo:` reads as
written.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

FORMAT = Path(__file__).resolve().parent.parent / "references" / "format.md"
# an undo written without its marker
BARE_UNDO = re.compile(r"(?<!⚠ )\bundo: ")


class CardLinesUndo(unittest.TestCase):

    def setUp(self):
        text = " ".join(FORMAT.read_text().split())
        start = text.index("**Card lines.**")
        self.para = text[start:text.index("`wi prime`", start)]

    def test_the_impact_form_marks_its_optional_undo(self):
        self.assertIn("reach: <reach> [· ⚠ undo: <undo>]", self.para)
        self.assertIsNone(BARE_UNDO.search(self.para.replace("a plain `undo:`", "")),
                          self.para)

    def test_undo_only_where_an_option_is_one_way_or_costly(self):
        self.assertIn("only when some option is one-way or costly to undo", self.para)
        self.assertIn("may carry a plain `undo:`, read as written", self.para)


if __name__ == "__main__":
    unittest.main()
