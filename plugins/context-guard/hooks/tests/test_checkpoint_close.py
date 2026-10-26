#!/usr/bin/env python3
"""c90d: every checkpoint's close, in both modes and on the lean and
unattended paths, carries one fenced, single-line `/compact <guidance>` to
paste unedited, its guidance naming the manifest path, the open item, every
hold and every REFUSED line; the opener stays its own line; the echo's window
part points at the `/compact` line. Held here by what SKILL.md and the
operator playbook say. Standard library only; run from the hooks dir:
python3 -m unittest discover -s tests -q
"""
import os
import re
import unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(os.path.dirname(HOOKS), "skills", "checkpoint")


def _read(*parts):
    with open(os.path.join(SKILL_DIR, *parts), encoding="utf-8") as fh:
        return fh.read()


def _fenced(text):
    """The bodies of every ```text fence, inner fences of a ```` block
    included."""
    return re.findall(r"^```text\n(.*?)^```$", text, re.M | re.S)


def _flat(text):
    return " ".join(text.split())


class TestCloseCompactLine(unittest.TestCase):

    def setUp(self):
        self.skill = _read("SKILL.md")
        self.step7 = self.skill.split("## Step 7", 1)[1].split("\n## Rules", 1)[0]
        body = self.skill.split("## Step 0", 1)[1]
        self.step0 = body.split("\n## Step 1", 1)[0]
        self.step5 = self.skill.split("## Step 5", 1)[1].split("\n## Step 6", 1)[0]
        self.unattended = self.skill.split(
            "## Invoked by the mid-turn gate", 1)[1].split("\n## Step 0", 1)[0]
        self.lean = self.skill.split("**Lean path:**", 1)[1].split("\n\n", 1)[0]

    def test_compact_line_in_both_modes(self):
        flat = _flat(self.step7)
        self.assertIn("**The `/compact` line**, in both modes", flat)
        self.assertIn("as **one line**, fenced, with **no leading whitespace**", flat)
        # the handoff-only item carries /clear alone, not the /compact line
        handoff_only = flat.split("**For a handoff only**", 1)[1].split("3. ", 1)[0]
        self.assertNotIn("/compact", handoff_only)

    def test_guidance_names_path_item_holds_refusals(self):
        flat = _flat(self.step7)
        self.assertIn("names the manifest's absolute path, the open item, and every "
                      "hold and every REFUSED line", flat)
        lines = [b.strip("\n") for b in _fenced(self.step7)]
        compact = [b for b in lines if b.startswith("/compact ")]
        self.assertEqual(len(compact), 1, "one /compact template in Step 7")
        tpl = compact[0]
        self.assertNotIn("\n", tpl)
        for part in ("<absolute manifest path>", "<item id>", "HOLD", "REFUSED"):
            self.assertIn(part, tpl, part)

    def test_opener_is_its_own_line_after_the_compact_line(self):
        fences = [b.strip("\n") for b in _fenced(self.step7)]
        starts = [b.split(" ", 1)[0] for b in fences]
        self.assertIn("/compact", starts)
        opener = [i for i, b in enumerate(fences) if "Read (the Read tool)" in b]
        self.assertEqual(len(opener), 1)
        self.assertLess(starts.index("/compact"), opener[0])
        self.assertNotIn("/compact", fences[opener[0]].split(" — ", 1)[0])
        self.assertIn("its own line apart from the `/compact` line", _flat(self.step7))

    def test_echo_points_at_the_line(self):
        self.assertNotIn("as recommended above", self.skill)
        self.assertIn("window: the /compact line below", self.step0)

    def test_question_3_feeds_the_line_in_both_modes(self):
        flat = _flat(self.step0)
        self.assertIn("every REFUSED line and every hold; Step 7 prints it, in both "
                      "modes, as the close's `/compact` line", flat)

    def test_step5_defers_to_the_printed_line(self):
        self.assertIn("Step 7 prints that `/compact` as a line to paste", _flat(self.step5))

    def test_lean_and_unattended_paths_print_it(self):
        self.assertIn("the `/compact` line", self.lean)
        flat = _flat(self.unattended)
        self.assertIn("its `/compact` line included", flat)
        self.assertIn("the close's `/compact` line is printed for them to run then",
                      flat)


class TestPlaybookCloseExamples(unittest.TestCase):

    def setUp(self):
        self.pb = _read("references", "operator-playbook.md")
        self.where = self.pb.split("## Where the manifest lives", 1)[1]

    def test_both_modes_show_a_pasteable_compact_line(self):
        for label in ("A continue's close, for example",
                      "A handoff's close, for example"):
            self.assertIn(label, self.where, label)
            block = self.where.split(label, 1)[1].split("\n````\n", 1)[0]
            fences = [b.strip("\n") for b in _fenced(block + "\n")]
            compact = [b for b in fences if b.startswith("/compact ")]
            self.assertEqual(len(compact), 1, label)
            self.assertNotIn("\n", compact[0])
            self.assertIn("HANDOFF.md", compact[0])
            self.assertIn("HOLD", compact[0])
            self.assertTrue(any("Read (the Read tool)" in b and not b.startswith("/compact")
                                for b in fences), label)

    def test_not_handoff_only(self):
        self.assertNotIn("a handoff also prints `/clear`,\n`/compact", self.pb)
        self.assertIn("in both modes, a fenced\none-line `/compact <guidance>`", self.pb)


if __name__ == "__main__":
    unittest.main()
