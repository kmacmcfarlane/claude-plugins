"""The format reference describes the decision counter (03ab F8): the
`counters:` block in § Store tracking, the new § Allocating a decision
number (`wi raise`, `wi counter`, the reseed, gaps valid), and § Operator
questions' One counter naming the record and `wi raise`. Each check is run
again on a copy with its text deleted, and must fail there (the mutant).

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAT = HERE.parent / "references" / "format.md"
SKILL = HERE.parent / "SKILL.md"


def section(text, heading):
    """The body of the `## heading` section, or '' when it is absent."""
    m = re.search(r"^## " + re.escape(heading) + r"[^\n]*\n(.*?)(?=^## |\Z)",
                  text, re.M | re.S)
    return m.group(1) if m else ""


def store_tracking_problems(text):
    body = section(text, "Store tracking")
    out = []
    if not re.search(r"^counters:\n  decision: \d+$", body, re.M):
        out.append("no counters: block example")
    flat = " ".join(body.split())
    if "§ Allocating a decision number" not in flat:
        out.append("no pointer to § Allocating a decision number")
    if "carries the block over unchanged" not in flat:
        out.append("init keeping the block unsaid")
    return out


def allocating_problems(text):
    body = " ".join(section(text, "Allocating a decision number: "
                                  "`wi raise` / `wi counter`").split())
    want = [
        "$WI raise <id> -- '<question line>'",
        "$WI counter",
        "the larger of the counter and the highest N",
        "`archive/*/`",
        "raised: <UTC time, to the second>",
        "`raise` never reads stdin",
        "`wi note --raw`'s refusals",
        "counter: decision reseeded <old> → <new>",
        "a gap is valid, never lowered",
        "re-reads the counter and rescans the items under the lock",
        "conflict markers",
    ]
    return [w for w in want if w not in body]


def one_counter_problems(text):
    body = " ".join(section(text, "Operator questions: "
                                  "`decision N:` / `answer N:`").split())
    want = "the `counters:` block in `store.yaml` that `wi raise` advances"
    return [] if want in body else ["One counter names no record"]


def skill_problems(text):
    out = []
    if "| `$WI raise <id> -- '<question>'` |" not in text:
        out.append("no raise row")
    if "| `$WI counter` |" not in text:
        out.append("no counter row")
    return out


class FormatCounter(unittest.TestCase):

    def setUp(self):
        self.text = FORMAT.read_text(encoding="utf-8")

    def test_store_tracking_has_the_block(self):
        self.assertEqual(store_tracking_problems(self.text), [])

    def test_store_tracking_mutant(self):
        cut = re.sub(r"^counters:\n  decision: \d+\n", "", self.text, flags=re.M)
        self.assertNotEqual(store_tracking_problems(cut), [])

    def test_allocating_section(self):
        self.assertEqual(allocating_problems(self.text), [])

    def test_allocating_mutant(self):
        cut = self.text.replace("## Allocating a decision number", "## Gone", 1)
        self.assertNotEqual(allocating_problems(cut), [])

    def test_one_counter_names_the_record(self):
        self.assertEqual(one_counter_problems(self.text), [])

    def test_one_counter_mutant(self):
        cut = re.sub(r"the `counters:` block in `store.yaml` that\s+`wi raise`",
                     "the counter", self.text)
        self.assertNotEqual(one_counter_problems(cut), [])

    def test_skill_table_rows(self):
        self.assertEqual(skill_problems(SKILL.read_text(encoding="utf-8")), [])

    def test_skill_table_mutant(self):
        text = SKILL.read_text(encoding="utf-8")
        cut = "\n".join(l for l in text.split("\n")
                        if not l.startswith("| `$WI counter` |"))
        self.assertNotEqual(skill_problems(cut), [])


if __name__ == "__main__":
    unittest.main()
