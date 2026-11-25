"""Text test for SKILL.md § write and references/estate.md: the split is proposed and agreed
before any draft, a draft is never written into another repo, upkeep's skip names the
approve step and never covers another repo's draft, and a hand-over is checked against the
text the operator approved.

write_problems() and estate_problems() are plain functions over the text, each returning a
list of problems. They run against the shipped files, and each mutant in MUTANTS and
ESTATE_MUTANTS (one rule broken) must make its function fail. Reads only this skill's own files. Run from the skill's scripts/ dir:

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
    probs += skip_problems(ss)
    return probs


SKIP = re.compile(r"skips step (\d+)")


def skip_problems(ss):
    """Step 5's upkeep skip must name the approve step, by its number."""
    classify, approve = find(ss, "classify"), find(ss, "approve")
    if classify is None or approve is None:
        return ["no classify or approve step"]
    named = SKIP.findall(" ".join(ss[classify][2].split()))
    if named != [str(ss[approve][0])]:
        return [f"the classify step skips step {named}, not the approve step "
                f"{ss[approve][0]}"]
    return []


# estate.md: each rule as the exact sentence that must stay, whitespace folded.
ESTATE_RULES = {
    "never written into another repo": "The drafting session never writes into another repo,",
    "hand-over checks the approved text": "and that the text it lands is the text that answer "
                                          "approved. On any difference,",
    "upkeep for another repo always asked": "A draft for another repo is always put to the "
                                            "operator, upkeep included.",
    "upkeep skip only for this repo": "The upkeep skip in write step 5 applies only to this "
                                      "repo's own claim.",
    "message is a request": "The message is a request, never an approval.",
    "nothing drafted before agreement": "Nothing is drafted until the operator agrees.",
    "approved text carried whole": "the approved text, whole, and the answer that approved it",
}


def estate_problems(text):
    flat = " ".join(text.split())
    return [name for name, rule in ESTATE_RULES.items() if rule not in flat]


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
    "upkeep skips the wrong step": lambda t: t.replace("skips step 6", "skips step 7"),
    "upkeep names no step": lambda t: t.replace("skips step 6", "skips approval"),
}


def _drop(sentence):
    def mutate(t):
        flat = " ".join(t.split())
        return flat.replace(sentence, "")
    return mutate


ESTATE_MUTANTS = {
    "into another repo allowed": lambda t: " ".join(t.split()).replace(
        "never writes into another repo", "may write into another repo"),
    "hand-over text not checked": _drop(
        "and that the text it lands is the text that answer approved. On any difference,"),
    "another repo's upkeep lands unasked": lambda t: " ".join(t.split()).replace(
        "always put to the operator, upkeep included", "put to the operator unless upkeep"),
    "upkeep skip widened": _drop(
        "The upkeep skip in write step 5 applies only to this repo's own claim."),
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

    def test_upkeep_skip_names_the_approve_step(self):
        ss = steps(write_section(self.text))
        self.assertEqual(skip_problems(ss), [])
        self.assertEqual(ss[find(ss, "approve")][1].split(".")[0], "Approve each")


class Estate(unittest.TestCase):
    def setUp(self):
        self.text = ESTATE_MD.read_text("utf-8")

    def test_shipped_estate_reference_is_clean(self):
        self.assertEqual(estate_problems(self.text), [])

    def test_each_mutant_is_caught(self):
        for name, mutate in ESTATE_MUTANTS.items():
            with self.subTest(mutant=name):
                mutant = mutate(self.text)
                self.assertNotEqual(" ".join(mutant.split()), " ".join(self.text.split()))
                self.assertNotEqual(estate_problems(mutant), [])


if __name__ == "__main__":
    unittest.main()
