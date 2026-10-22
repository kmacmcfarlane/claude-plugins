"""The answer page keeps parity with the chat card (the 2026-10-21 *Both surfaces* ruling).

A decision-format change lands on the chat card (the `decisions` skill) and on the answer page
(the `decision-page` skill), and on the librarian's stored card where it applies. These checks
read the rulings, the page's text and, under node, the page and its pre-publish runner:

- *Both surfaces*: the ruling, its date and its alternative not taken, in both skills;
- the page forms of the card rules that landed chat-only at first, each with its ruling.

Each check is a function returning its problems, run on the real files (no problems) and on a
mutated copy (a problem), so a check that cannot fail does not pass for one.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
PAGE_SKILL = PLUGIN / "skills" / "decision-page"
RULINGS = PLUGIN / "skills" / "decisions" / "references" / "rulings.md"
PAGE_SKILL_MD = PAGE_SKILL / "SKILL.md"


def flat(text):
    return re.sub(r"\s+", " ", text)


def bullet(text, name):
    """The rulings bullet opening `- **name**`, joined onto one line; "" when there is none."""
    m = re.search(r"^- \*\*" + re.escape(name) + r"\*\*.*?(?=^- |^## |\Z)", text, re.S | re.M)
    return flat(m.group(0)) if m else ""


BOTH_CORE = ("planned together; a surface left out names its obvious reason, and one that is "
             "unclear goes to the operator. Not taken: a rule scoped to the surface whose "
             "feedback raised it")


def both_surfaces_problems(text):
    b = bullet(text, "Both surfaces")
    if not b:
        return ["no Both surfaces bullet"]
    out = []
    if "(2026-10-21" not in b:
        out.append("Both surfaces: no date")
    if BOTH_CORE not in b:
        out.append("Both surfaces: the rule or its Not taken differs")
    return out


class BothSurfaces(unittest.TestCase):
    def setUp(self):
        self.rulings = RULINGS.read_text()
        self.page = PAGE_SKILL_MD.read_text()

    def test_in_both_skills(self):
        self.assertEqual(both_surfaces_problems(self.rulings), [])
        self.assertEqual(both_surfaces_problems(self.page), [])

    def test_the_page_skill_has_a_rulings_section_pointing_at_the_decisions_rulings(self):
        m = re.search(r"^## Rulings\n(.*?)(?=^## )", self.page, re.S | re.M)
        self.assertTrue(m)
        self.assertIn("the `decisions` skill's `references/rulings.md`", flat(m.group(1)))

    def test_mutations(self):
        for text in (self.rulings, self.page):
            self.assertEqual(both_surfaces_problems(text.replace("**Both surfaces**", "**Both**")),
                             ["no Both surfaces bullet"])
            self.assertIn("Both surfaces: no date",
                          both_surfaces_problems(text.replace("**Both surfaces** (2026-10-21",
                                                              "**Both surfaces** (")))
            self.assertIn("Not taken: a rule scoped", text)
            cut = text.replace("Not taken: a rule scoped", "Not taken: nothing scoped")
            self.assertIn("Both surfaces: the rule or its Not taken differs",
                          both_surfaces_problems(cut))


if __name__ == "__main__":
    unittest.main()
