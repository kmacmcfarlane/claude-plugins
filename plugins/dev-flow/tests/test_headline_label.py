"""A decision raised from one labelled item stores its label first in the headline.

Answer 269 (a), widened (2026-10-20): a source label (a review's F7, a plan's OQ3) is written
label first with a plain short name, and a decision raised from one labelled item opens its
title on it. The librarian stores what its views read, so the headline's question carries
the label and its short name first (feature C3 of the decision-card feedback plan), while
the decision number stays the handle that `wi` and the counter read (`^decision [0-9]`).

Since the store keeps card records (feature K3 of the v5 card layout plan), the headline is
`wi`'s, built from the record's `label` and `q`: `decisions.md` names that template and keeps
the example headline, so the counter and `wi` read it unchanged. A headline stored before the
rule, its label in `what:`, is read by the decisions skill's legacy reference.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REFS = PLUGIN / "skills" / "librarian-mode" / "references"
DECISIONS = REFS / "decisions.md"
REPORT = REFS / "report.md"
EXAMPLE = "decision 41: F7 (oversize upload) · Cap the upload size? — options: "
COUNTER = re.compile(r"^decision [0-9]")
TEMPLATE = "decision N: [<label.id> (<label.name>) · ]<q>[ ⚠ one-way] — options: "


def template_problems(text):
    """The headline template is `wi`'s, label first, built from the record."""
    out = []
    tmpl = next((x for x in text.splitlines() if x.strip().startswith("decision N: ")), "")
    if not tmpl.strip().startswith(TEMPLATE):
        out.append("no label-first headline template")
    if "**The headline** is `wi`'s, built from the record's `label` and `q`, never typed" \
            not in " ".join(text.split()):
        out.append("the headline is not named as wi's")
    return out


def flat(path):
    return " ".join(path.read_text().split())


class HeadlineLabel(unittest.TestCase):

    def test_the_headline_template_takes_the_label_first(self):
        self.assertEqual(template_problems(DECISIONS.read_text()), [])
        # mutants: the template typed by the librarian again; the label after the question
        text = DECISIONS.read_text()
        self.assertTrue(template_problems(text.replace(TEMPLATE, "decision N: <q> — options: ")))
        self.assertTrue(template_problems(text.replace("built from the record's `label` and `q`",
                                                       "typed by the librarian")))

    def test_the_example_headline_still_reads_as_a_decision(self):
        text = DECISIONS.read_text()
        line = next((x.strip() for x in text.splitlines() if x.strip().startswith(EXAMPLE)),
                    None)
        self.assertIsNotNone(line, "no example headline with a label first")
        self.assertRegex(line, COUNTER)

    def test_the_label_no_longer_rides_in_what(self):
        text = flat(DECISIONS)
        self.assertNotIn("rides in the card's `what:` line", text)
        self.assertNotIn("the label rides at the end of `what:`", text)
        # the dated clause moved to the decisions skill's legacy reference
        self.assertNotIn("A headline stored before this rule", text)
        self.assertIn("its record carries that label and its short name, `label {id, name}`", text)

    def test_the_counter_names_the_label_first(self):
        text = flat(REPORT)
        start = text.index("## The counter")
        section = text[start:text.index("## ", start + 3)]
        self.assertIn("first in the headline's question, with its short name", section)
        self.assertIn("never a second numbering", section)


if __name__ == "__main__":
    unittest.main()
