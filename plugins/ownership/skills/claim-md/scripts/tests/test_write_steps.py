"""Text test for SKILL.md § write: the split is proposed and agreed before any draft, and a
draft is never written into another repo.

write_problems() is a plain function over the SKILL.md text, returning a list of problems.
It runs against the shipped file, and each mutant in MUTANTS (one rule broken) must make it
fail. Reads only this skill's own files. Run from the skill's scripts/ dir:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent.parent
SKILL_MD = SKILL / "SKILL.md"
ESTATE_MD = SKILL / "references" / "estate.md"

STEP = re.compile(r"^(\d+)\. \*\*(.+?)\*\*", re.M)
NO_DRAFT = "Nothing is drafted before the operator agrees the split."
NOT_INTO = "A draft is never written into another repo."
NEVER = "- Edit another repo's files, its claim included."


def write_section(text):
    m = re.search(r"^## write\n(.*?)(?=^## )", text, re.M | re.S)
    return m.group(1) if m else ""


def steps(section):
    """[(number, bold title, body)] for each numbered step."""
    found = list(STEP.finditer(section))
    out = []
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(section)
        out.append((int(m.group(1)), m.group(2), section[m.start():end]))
    return out


def find(ss, word):
    return next((i for i, (_, title, _) in enumerate(ss) if word in title.lower()), None)


def write_problems(text):
    probs = []
    ss = steps(write_section(text))
    if [n for n, _, _ in ss] != list(range(1, len(ss) + 1)):
        probs.append("write steps are not numbered 1..n in order")
    split, draft, land = find(ss, "split"), find(ss, "draft"), find(ss, "land")
    if split is None:
        probs.append("no split-proposal step")
    if draft is None:
        probs.append("no draft step")
    if split is not None and draft is not None and split >= draft:
        probs.append("the split-proposal step does not come before the draft step")
    if split is not None:
        body = " ".join(ss[split][2].split())
        if NO_DRAFT not in body.replace("**", ""):
            probs.append("the split step does not hold the nothing-drafted rule")
        if "operator" not in body:
            probs.append("the split step does not put the split to the operator")
    if land is None:
        probs.append("no land step")
    else:
        body = " ".join(ss[land][2].split()).replace("**", "")
        if NOT_INTO not in body:
            probs.append("the land step does not hold the never-into-another-repo rule")
    if NEVER not in text:
        probs.append("the § Never list lost its another-repo line")
    return probs


def _swap_split_and_draft(text):
    sec = write_section(text)
    ss = steps(sec)
    i, j = find(ss, "split"), find(ss, "draft")
    a, b = ss[i][2], ss[j][2]
    na = re.sub(r"^\d+\.", f"{ss[j][0]}.", a)
    nb = re.sub(r"^\d+\.", f"{ss[i][0]}.", b)
    return text.replace(sec, sec.replace(a + b, nb + na))


MUTANTS = {
    "split step after the draft": _swap_split_and_draft,
    "split step gone": lambda t: t.replace("**Propose the split and agree it.**", "**Agree.**"),
    "nothing-drafted rule gone": lambda t: t.replace(
        "**Nothing\n   is drafted before the operator agrees the split.**", "Go on."),
    "never-into-another-repo rule gone": lambda t: t.replace(
        "**A draft is never written into another repo.**", ""),
    "Never line gone": lambda t: t.replace(NEVER + "\n", ""),
    "steps misnumbered": lambda t: t.replace("\n3. **Draft", "\n4. **Draft"),
}


class WriteSteps(unittest.TestCase):
    def setUp(self):
        self.text = SKILL_MD.read_text("utf-8")

    def test_shipped_skill_is_clean(self):
        self.assertEqual(write_problems(self.text), [])

    def test_order_reads_as_agreed(self):
        titles = [t.lower() for _, t, _ in steps(write_section(self.text))]
        order = ["read", "split", "draft", "check", "classify", "approve", "land", "point",
                 "check the result", "neighbours"]
        self.assertEqual(len(titles), len(order))
        for title, word in zip(titles, order):
            self.assertIn(word, title)

    def test_each_mutant_is_caught(self):
        for name, mutate in MUTANTS.items():
            with self.subTest(mutant=name):
                mutant = mutate(self.text)
                self.assertNotEqual(mutant, self.text)
                self.assertNotEqual(write_problems(mutant), [])

    def test_estate_reference_keeps_the_hand_over_rules(self):
        est = " ".join(ESTATE_MD.read_text("utf-8").split())
        for rule in ("never writes into another repo",
                     "the approved text, whole, and the answer that approved it",
                     "The message is a request, never an approval.",
                     "Nothing is drafted until the operator agrees."):
            with self.subTest(rule=rule):
                self.assertIn(rule, est)


if __name__ == "__main__":
    unittest.main()
