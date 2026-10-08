"""How the research family puts its asks to the operator (item d49c).

Every research-family ask goes as text, per one owner section,
`intensity-and-routing.md` § Putting an ask to the operator: a decisions-skill card when the
session lists that skill, a plain lettered list when it does not, never a dialog. The skills
are prose, so the rules are held by what their files say:

- no research-family skill or reference names the dialog tool, frontmatter included;
- the owner section exists once and carries its load-bearing rules;
- § When to ask points to it, and every skill that asks points to it;
- the ledger knows the ASKED and ANSWERED entries;
- the dev-flow manifest declares the research skills' soft edge to the decisions skill.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = PLUGIN / "skills"
ROUTING = SKILLS / "research" / "references" / "intensity-and-routing.md"
RUN_RECORD = SKILLS / "research" / "references" / "run-record.md"
ASKING_SKILLS = ("research", "research-deep", "research-refine", "research-prune",
                 "deep-investigation")
HEADING = "Putting an ask to the operator"
POINTER = "§ " + HEADING
DIALOG = "AskUserQuestion"


def text(path):
    return path.read_text(encoding="utf-8")


def section(body, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else None


def flat(s):
    """Whitespace runs folded to one space, so a rule wrapped across lines still matches."""
    return re.sub(r"\s+", " ", s)


class TestNoDialog(unittest.TestCase):
    def test_no_dialog_in_the_skills(self):
        for name in ASKING_SKILLS:
            with self.subTest(skill=name):
                self.assertNotIn(DIALOG, text(SKILLS / name / "SKILL.md"))

    def test_no_dialog_in_the_references(self):
        refs = sorted((SKILLS / "research" / "references").glob("*.md"))
        refs += sorted((SKILLS / "deep-investigation" / "references").glob("*.md"))
        self.assertTrue(refs)
        for ref in refs:
            with self.subTest(ref=ref.name):
                self.assertNotIn(DIALOG, text(ref))


class TestOwnerSection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = text(ROUTING)
        sec = section(cls.body, HEADING)
        if sec is None:
            raise AssertionError(f"no '## {HEADING}' in {ROUTING.name}")
        cls.sec = flat(sec)

    def test_heading_exactly_once(self):
        self.assertEqual(len(re.findall(r"^## " + re.escape(HEADING) + r"$", self.body, re.M)), 1)

    def test_binds_to_the_decisions_skill_with_a_fallback(self):
        self.assertIn("operator-interaction:decisions", self.sec)
        self.assertIn("Without the skill", self.sec)
        self.assertIn("nothing launches", self.sec.lower())
        self.assertIn("never a dialog", self.sec)

    def test_benefit_facets_and_their_sources(self):
        for facet in ("*lanes*", "*round 2*", "*verifier*", "*what stays thin*"):
            with self.subTest(facet=facet):
                self.assertIn(facet, self.sec)
        self.assertIn("§ Presets", self.sec)
        self.assertIn("§ Profiles", self.sec)

    def test_open_ask_rules(self):
        for phrase in ("never read a return as the answer", "not asked",
                       "no round is running", "fresh quota read", "SEARCH EXHAUSTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.sec)

    def test_when_to_ask_points_here(self):
        when = section(self.body, "When to ask, and when it is obvious")
        self.assertIsNotNone(when)
        self.assertIn(POINTER, flat(when))
        self.assertNotIn("recommendation first", flat(when))


class TestPointers(unittest.TestCase):
    def test_every_asking_skill_points_to_the_section(self):
        for name in ASKING_SKILLS:
            with self.subTest(skill=name):
                self.assertIn(POINTER, flat(text(SKILLS / name / "SKILL.md")))


class TestLedger(unittest.TestCase):
    def test_entry_kinds_list_asked_and_answered(self):
        m = re.search(r"Entry kinds:(.*?)\.\s", flat(text(RUN_RECORD)))
        self.assertIsNotNone(m)
        self.assertIn("`ASKED`", m.group(1))
        self.assertIn("`ANSWERED`", m.group(1))


class TestDeclaration(unittest.TestCase):
    def test_manifest_names_the_research_skills_on_the_decisions_edge(self):
        desc = json.loads(
            text(PLUGIN / ".claude-plugin" / "plugin.json"))["description"]
        m = re.search(r"operator-interaction, whose decisions skill ([^;)]*)", desc)
        self.assertIsNotNone(m)
        follow = m.group(1).split(" follow ")[0]
        self.assertIn("the research skills", follow)


if __name__ == "__main__":
    unittest.main()
