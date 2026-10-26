"""What the decision page hands its caller (answer 344 (a), 13bd).

The read-back hands each new answer over with its kind; a follow-up is handed over as one and
is never an answer, so a caller that keeps a store writes it as a wake line, not an answer line
(L1). A publish hands over one showing per new card, with its `rev`, and their count (L4).
Pinned in `skills/decision-page/SKILL.md` Steps 3 and 6.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
PAGE_SKILL = PLUGIN / "skills" / "decision-page"
SKILL = PAGE_SKILL / "SKILL.md"


def flat(text):
    return " ".join(text.split())


def step(text, heading, upto):
    start = text.index(heading)
    return text[start:text.index(upto, start)]


class FollowUpHandOver(unittest.TestCase):

    def setUp(self):
        self.step6 = step(flat(SKILL.read_text()), "## Step 6:", "## Troubleshooting")

    def test_a_follow_up_is_handed_over_as_one_and_is_not_an_answer(self):
        self.assertIn("A follow-up (`later`, `tell me`, `expand`, `dig into`) is handed over as "
                      "one, `kind: follow-up`, and is not an answer: a caller that keeps a store "
                      "records it by its own follow-up rule (a wake line), never as an answer "
                      "line", self.step6)

    def test_you_decide_and_drop_stay_final_answers(self):
        self.assertIn("`you decide` and `drop` carry the same kind and are final answers",
                      self.step6)


class ShownHandOver(unittest.TestCase):
    """L4: a publish hands over one showing per new card, with its `rev`, and their count."""

    def test_step_3_hands_over_each_rev_and_the_count(self):
        step3 = step(flat(SKILL.read_text()), "## Step 3:", "## Step 4:")
        self.assertIn("hand the caller the card's number, its `rev`, the publish time (UTC, your "
                      "clock) and the surface word *page*, one per card, then their count: *N "
                      "cards handed over*", step3)
        self.assertIn("A republish that keeps a card's `rev` hands over nothing for it", step3)


if __name__ == "__main__":
    unittest.main()
