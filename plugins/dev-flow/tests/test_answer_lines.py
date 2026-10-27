"""The librarian's answer lines hold final answers only (answer 344 (a), 13bd).

`wi` reads any `answer N:` line as answered, so what the librarian writes on one decides
whether `wi needs-input` still lists a decision. A follow-up (`later`, `hold`, `dig into`,
`tell me`, `expand`) is never stored as an answer line: it is a `wake N:` line, or nothing
(L1), whether it came in chat or from an answer page or tick-box doc's read-back. A reframe
writes its answer line and `closed N: superseded by M` together (L2). An answer page's
publish writes one `shown` line per card, with its `rev`, counted (L4). This file pins those
rules in `references/decisions.md` § What the store records, **Answered**.

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
                      "same rule: the read-back hands it over as `kind: follow-up` (as it does "
                      "`you decide` and `drop`, which are final answers and keep their answer "
                      "lines), and it is recorded as the bullets below give: a `wake N:` line "
                      "for `later` and `dig into`, nothing for `tell me` and `expand`; never an "
                      "answer line.", rule)
        self.assertIn("`later` (the `(z)` option too, by its letter or its words)", rule)

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
        text = flat(self.text)
        self.assertIn("` verbatim N (moved <UTC time>, from its answer line): <the original "
                      "line>`", text)
        self.assertIn("**A `later`, `hold` or `dig into` stored as an answer line** before the "
                      "follow-up rule (below), on a decision with no later final answer, is "
                      "rewritten", text)
        self.assertIn("one followed by a final answer is left as written", text)

    def test_a_chat_showing_names_its_rev(self):
        self.assertIn("with `rev <rev>` from its last `card:` line when it has one",
                      bullet(self.text, "**Shown:**"))


class Reframes(unittest.TestCase):
    """L2: a reframe writes an answer line and a closed line together; `withdrawn N:` is
    never written again, and one already stored is read as those two lines."""

    def test_the_reframe_bullet_holds_both_lines(self):
        reframe = bullet(DECISIONS.read_text(), "**A reframe:**")
        self.assertIn('`answer N: reframed as decision M — "<the reply>"`', reframe)
        self.assertIn("`closed N: superseded by M`", reframe)
        self.assertIn("A `withdrawn N:` line is never written", reframe)
        self.assertIn("is read as those two lines", reframe)


class PageShowings(unittest.TestCase):
    """L4: one `shown` line per card an answer page hands over, with its `rev`, counted."""

    def test_the_shown_bullet(self):
        shown = bullet(DECISIONS.read_text(), "**Shown:**")
        self.assertIn("append one `shown N: <time> page rev <rev>` line per card the "
                      "`decision-page` skill hands over", shown)
        self.assertIn("never one note for the page", shown)
        self.assertIn("count the lines against the hand-over's count (*N cards handed over*) "
                      "and write any missing one before the Report", shown)
        self.assertIn("a kept card writes no line", shown)


if __name__ == "__main__":
    unittest.main()
