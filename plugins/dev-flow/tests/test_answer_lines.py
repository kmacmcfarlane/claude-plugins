"""The librarian's answer lines hold final answers only (answer 344 (a), 13bd).

`wi` reads any `answer N:` line as answered, so what the librarian writes on one decides
whether `wi needs-input` still lists a decision. A follow-up (`later`, `hold`, `dig into`,
`tell me`, `expand`) is never stored as an answer line: it is a `wake N:` line, or nothing
(L1), whether it came in chat or from an answer page or tick-box doc's read-back. This file
pins that rule in `references/decisions.md` § What the store records, **Answered**.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
DECISIONS = PLUGIN / "skills" / "librarian-mode" / "references" / "decisions.md"


def flat(text):
    return " ".join(text.split())


def bullet(text, opener):
    """The flattened top-level bullet of § What the store records that opens with `opener`."""
    lines = text.splitlines()
    start = next(i for i, x in enumerate(lines) if x.startswith("- " + opener))
    end = next(i for i in range(start + 1, len(lines))
               if lines[i].startswith("- ") or lines[i].startswith("#"))
    return flat("\n".join(lines[start:end]))


class FollowUps(unittest.TestCase):

    def setUp(self):
        self.text = DECISIONS.read_text()

    def test_the_rule_bullet(self):
        rule = bullet(self.text, "**A follow-up is never an answer line.**")
        self.assertIn("An `answer N:` line holds a final answer only", rule)
        self.assertIn("A follow-up from an answer page or a tick-box doc is recorded by the "
                      "same rule: the read-back hands it over as `kind: follow-up`, and it "
                      "becomes a `wake N:` line, never an answer line.", rule)

    def test_later_hold_and_dig_into_write_a_wake_line(self):
        self.assertIn("`wake N: <time | event | next Report>`. There is no `answer N:`",
                      bullet(self.text, "**`later [when]`:**"))
        self.assertIn("`wake N: <what it waits on>`, and no `answer N:`",
                      bullet(self.text, "**`hold`:**"))
        self.assertIn("`wake N: when the dig into returns (<what>)`, no `answer N:`",
                      bullet(self.text, "**`dig into [what]`:**"))

    def test_tell_me_and_expand_write_no_answer(self):
        self.assertIn("Neither writes an `answer N:` line", bullet(self.text, "**`tell me`:**"))

    def test_a_follow_up_stored_as_an_answer_is_moved(self):
        self.assertIn("` verbatim N (moved <UTC time>, from its answer line): <the original "
                      "line>`", flat(self.text))


if __name__ == "__main__":
    unittest.main()
