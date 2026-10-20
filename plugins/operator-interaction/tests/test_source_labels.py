"""The plain-names skill's Source labels rule, its ruling, and tracker ids still name first.

A source label (F1, OQ3, R2-1, A4a) is written label first with its short name in
parentheses; later mentions take the label alone. Tracker ids keep the Handle ruling: the
plain name first, the short tag trailing. Checked against the plain-names SKILL.md and, read
only, the decisions skill's gallery. Each check is proved by a mutation.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import pathlib
import re
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
PLAIN = PLUGIN / "skills" / "plain-names" / "SKILL.md"
GALLERY = PLUGIN / "skills" / "decisions" / "references" / "gallery.md"

# a tracker id's short tag: four hex with at least one digit, e.g. (a1b2)
TAG = r"(?=[0-9a-f]{0,3}[0-9])[0-9a-f]{4}"
NAME_THEN_TAG = re.compile(rf"[A-Za-z][A-Za-z' -]*[a-z] \({TAG}\)")
# a bare tag leading its name: "a1b2 (export retry fix)" or "(a1b2) export retry"
TAG_THEN_NAME = re.compile(rf"(?:(?:^|[\s|*]){TAG} \([a-z]|(?:^|\| |: )\({TAG}\) [a-z])")
# a source label with its short name: "F1 (memory pressure on startup)"
LABEL_WITH_NAME = re.compile(r"\b[A-Z]{1,3}\d+(?:-\d+|[a-z])? \([a-z][a-z ]+[a-z]\)")


def section(text, heading):
    """The body of the `## heading` section, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise AssertionError(f"no section {heading!r}")
    return m.group(1)


def source_ruling(text):
    """The Rulings bullet for Source labels, joined onto one line."""
    rulings = section(text, "Rulings")
    m = re.search(r"^- \*\*Source labels\*\*.*?(?=^- |\Z)", rulings, re.S | re.M)
    if not m:
        raise AssertionError("no Source labels ruling")
    return " ".join(m.group(0).split())


def rule_problems(text):
    """What the Source labels rule lacks; empty when it is whole."""
    body = " ".join(section(text, "Source labels").split())
    need = {
        "the label-first form": LABEL_WITH_NAME.search(body),
        "any shape": "any shape" in body,
        "tracker ids name first": "Tracker ids are not source labels" in body
        and "name first" in body,
        "taken from the source": "Take it from the source" in body,
        "written where none": "Write one" in body,
        "plain words, not a slug": "plain words" in body and "not a slug" in body,
        "repeats by label alone": "take the label alone" in body,
        "the repeat rule's difference": "other way from tracker ids" in body,
    }
    return [k for k, ok in need.items() if not ok]


def ruling_problems(text):
    r = source_ruling(text)
    need = {
        "dated": "(2026-10-20" in r,
        "the operator's words": "expand Fn style labels" in r,
        "tracker ids keep Handle": "keep **Handle**" in r,
        "designs marked": "designs made in planning" in r,
        "slug not taken": re.search(r"Not taken: the slug form", r),
    }
    return [k for k, ok in need.items() if not ok]


def tracker_problems(text):
    """Lines where a tracker tag leads its name; empty when every tag trails."""
    return [ln for ln in text.splitlines() if TAG_THEN_NAME.search(ln)]


class SourceLabelsRule(unittest.TestCase):
    def setUp(self):
        self.text = PLAIN.read_text()

    def test_rule_is_whole(self):
        self.assertEqual(rule_problems(self.text), [])

    def test_rule_mutation(self):
        broken = self.text.replace("take the label alone", "take the name alone")
        self.assertIn("repeats by label alone", rule_problems(broken))
        broken = LABEL_WITH_NAME.sub("F1", self.text)
        self.assertIn("the label-first form", rule_problems(broken))

    def test_description_widened(self):
        desc = re.search(r"^description: (.*)$", self.text, re.M).group(1)
        self.assertIn("source label", desc)

    def test_example_and_not_this(self):
        examples = section(self.text, "Examples")
        self.assertIn("*As per F2 (stale cache after deploy), make a note", examples)
        self.assertIn("Not: *As per F2, make a note", examples)

    def test_ruling(self):
        self.assertEqual(ruling_problems(self.text), [])

    def test_ruling_mutation(self):
        broken = self.text.replace("Not taken: the slug form", "Not taken: nothing")
        self.assertIn("slug not taken", ruling_problems(broken))
        broken = self.text.replace("- **Source labels** (2026-10-20", "- **Labels** (2026-10-20")
        with self.assertRaises(AssertionError):
            source_ruling(broken)


class TrackerIdsNameFirst(unittest.TestCase):
    """A tracker id is still written name first, its tag trailing (the Handle ruling)."""

    def check(self, path):
        text = path.read_text()
        self.assertTrue(NAME_THEN_TAG.search(text), f"{path.name}: no `name (tag)` at all")
        self.assertEqual(tracker_problems(text), [], path.name)

    def test_plain_names(self):
        self.check(PLAIN)

    def test_gallery(self):
        self.check(GALLERY)

    def test_mutation(self):
        self.assertEqual(tracker_problems("| preview deploy (ab12) | next |"), [])
        self.assertTrue(tracker_problems("| ab12 (preview deploy) | next |"))
        self.assertTrue(tracker_problems("the fix: (a1b2) export retry fix"))
        # a source label leads by design and is not a tracker tag
        self.assertEqual(tracker_problems("as per F1 (memory pressure on startup)"), [])


if __name__ == "__main__":
    unittest.main()
