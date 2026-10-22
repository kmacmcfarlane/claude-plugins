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
import sys
import unittest
from pathlib import Path

from test_impact import NODE, PAGE, example
from test_context import runner

PLUGIN = Path(__file__).resolve().parent.parent
PAGE_SKILL = PLUGIN / "skills" / "decision-page"
RULINGS = PLUGIN / "skills" / "decisions" / "references" / "rulings.md"
PAGE_SKILL_MD = PAGE_SKILL / "SKILL.md"
SCHEMA = PAGE_SKILL / "references" / "cards-schema.md"
DIGEST = PAGE_SKILL / "references" / "writer-digest.md"
FALLBACK = PAGE_SKILL / "references" / "fallback.md"


def setUpModule():
    # the runner tests need node; without it they skip, and say so where the Check's output
    # shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's parity tests (SystemLint and "
              "the other runner and render checks) are skipped, so the page forms of the card "
              "rules went untested", file=sys.stderr)


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


# ---- S1 (system impact on the page), rule 259

def static_lede(html):
    m = re.search(r'<p class="lede">(For each decision.*?)</p>', html, re.S)
    return m.group(1) if m else ""


SYSTEM_LEDE = "An Impact describes the system the work builds, never the review or the process"


def system_text_problems(html, fallback, schema, rulings):
    out = []
    lede = static_lede(html)
    if SYSTEM_LEDE not in lede or "changes in the system the work builds" not in lede:
        out.append("the lede does not say the Impact describes the system")
    if "describing the system the work builds, never the review or the process" not in flat(fallback):
        out.append("the doc fallback does not say it")
    if "An Impact describes the system the work builds, never the review or the process" not in flat(schema):
        out.append("the schema does not say it")
    b = bullet(rulings, "Impact names the system")
    if "On the answer page (2026-10-22, *Both surfaces*" not in b or "`process` lint" not in b:
        out.append("rule 259 does not name its page form")
    return out


class SystemText(unittest.TestCase):
    def setUp(self):
        self.args = [PAGE.read_text(), FALLBACK.read_text(), SCHEMA.read_text(), RULINGS.read_text()]

    def test_the_page_says_it(self):
        self.assertEqual(system_text_problems(*self.args), [])

    def test_mutations(self):
        html, fb, sc, ru = self.args
        self.assertEqual(system_text_problems(html.replace(SYSTEM_LEDE, "An Impact"), fb, sc, ru),
                         ["the lede does not say the Impact describes the system"])
        self.assertTrue(system_text_problems(html, fb.replace("describing the system", "on"), sc, ru))
        self.assertTrue(system_text_problems(html, fb, sc.replace("An Impact describes the system", "It"), ru))
        self.assertTrue(system_text_problems(html, fb, sc, ru.replace("`process` lint", "lint")))


PROCESS_FIRES = [
    # (where on card 41, a setter, the line's place)
    ("effect", lambda c: c["impact"].__setitem__("effect", "review comments wait"), "the effect"),
    ("reach", lambda c: c["impact"].__setitem__("reach", "another round of review"), "the reach"),
    ("happens", lambda c: c["blocks"]["b"].__setitem__("happens", "the change waits on review"), "(b)'s effect"),
    ("who", lambda c: c["blocks"]["a"].__setitem__("who", "a blocked session"), "(a)'s reach"),
    ("option", lambda c: c["o"][1].__setitem__(2, "the session is blocked"), "(b)'s impact"),
    ("medium", lambda c: c["detail"]["impact"][0]["effect"].__setitem__("t", "costs your time each run"),
     "the effect (more detail)"),
    ("high", lambda c: c["detail"]["impact"][1].__setitem__("reach", ["your attention each week"]),
     "the reach (full detail)"),
]
PROCESS_CLEAN = ["the code review checklist gains a step", "a comment in the hook explains the guard",
                 "a round-trip per request", "the reviewer agent reads the new rule"]


@unittest.skipUnless(NODE, "node is not installed")
class SystemLint(unittest.TestCase):
    """The runner's `process` lint: process phrases in an Effect or Reach, never bare words."""

    def process_lines(self, d):
        return [x for x in runner(d)[1].splitlines() if "names the process" in x]

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_each_phrase_fires_where_effect_and_reach_are_read(self):
        for name, put, where in PROCESS_FIRES:
            with self.subTest(field=name):
                d = example()
                put(d["cards"][0])
                code, out, _ = runner(d)
                self.assertEqual(code, 2, out)
                self.assertIn("lint: card 41: impact: " + where + " names the process", out)

    def test_wait_z_and_a_round_ask_are_never_read(self):
        d = example()
        d["cards"][0]["impact"]["wait"] = "review comments wait for you"
        d["cards"][0]["o"][-1][2] = "another round of review waits"
        self.assertEqual(self.process_lines(d), [])
        d = example()
        d["cards"][0]["impact"]["effect"] = "review comments wait"
        d["cards"][0]["ifleft"] = "the leftover findings stay open"
        self.assertEqual(self.process_lines(d), [])

    def test_system_effects_that_share_a_word_stay_clean(self):
        for s in PROCESS_CLEAN:
            with self.subTest(text=s):
                d = example()
                d["cards"][0]["impact"]["effect"] = s
                d["cards"][0]["impact"]["reach"] = s
                self.assertEqual(self.process_lines(d), [])


# ---- S2 (mechanism on the page), rule 268

def mechanism_text_problems(digest, schema, skill, rulings):
    out = []
    if "the options, each with its consequence by its mechanism: how it happens, who meets it and when, and the before and after" not in flat(digest):
        out.append("the digest's floor does not ask for the mechanism")
    if "Could you say how it happens, not only that it does?" not in flat(digest):
        out.append("the digest's cold read does not ask it")
    if "`happens` the effect by its mechanism" not in flat(schema):
        out.append("the schema's blocks row does not say it")
    if "each effect by its mechanism" not in flat(skill):
        out.append("SKILL.md does not say it")
    b = bullet(rulings, "Explain the mechanism")
    if "On the answer page (2026-10-22, *Both surfaces*" not in b or "`mech` lint" not in b:
        out.append("rule 268 does not name its page form")
    return out


class MechanismText(unittest.TestCase):
    def setUp(self):
        self.args = [DIGEST.read_text(), SCHEMA.read_text(), PAGE_SKILL_MD.read_text(), RULINGS.read_text()]

    def test_the_page_says_it(self):
        self.assertEqual(mechanism_text_problems(*self.args), [])

    def test_mutations(self):
        for i, (old, new) in enumerate([("by its mechanism: how", "by its: how"),
                                        ("`happens` the effect by its mechanism", "`happens` the effect"),
                                        ("each effect by its mechanism", "each effect"),
                                        ("`mech` lint", "lint")]):
            with self.subTest(old=old):
                args = list(self.args)
                j = [0, 1, 2, 3][i]
                self.assertIn(old, args[j])
                args[j] = args[j].replace(old, new)
                self.assertTrue(mechanism_text_problems(*args))


@unittest.skipUnless(NODE, "node is not installed")
class MechanismLint(unittest.TestCase):
    """The runner's `mech` lint: an option's effect of a bare label, four words or fewer."""

    def mech_lines(self, d):
        return [x for x in runner(d)[1].splitlines() if "say its mechanism" in x]

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_a_bare_label_fires(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "importers break"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn('lint: card 41: impact: (a)\'s effect is 2 words ("importers break"): say its '
                      "mechanism", out)

    def test_a_no_change_statement_and_z_stay_clean(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "Nothing changes."
        d["cards"][0]["o"][-1][2] = "it waits"
        self.assertEqual(self.mech_lines(d), [])

    def test_an_option_with_no_row_is_read_from_its_impact(self):
        d = example()
        del d["cards"][2]["blocks"]
        d["cards"][2]["o"][1][2] = "screenshots break"
        self.assertEqual(self.mech_lines(d), ["lint: card 43: impact: (b)'s effect is 2 words "
                                              '("screenshots break"): say its mechanism, how it '
                                              "happens, who meets it and when, and the before and "
                                              "after; or leave it knowingly"])

    def test_the_threshold_is_four_words(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "the importers break downstream"
        self.assertEqual(len(self.mech_lines(d)), 1)
        d["cards"][0]["blocks"]["a"]["happens"] = "the importers break downstream today"
        self.assertEqual(self.mech_lines(d), [])


if __name__ == "__main__":
    unittest.main()
