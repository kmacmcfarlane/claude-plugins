"""The checkpoint skill commits the work-item store through `wi commit`
(item d1e9, F2; b2df's F-R5): under wi's lock, into the repo that holds the
store, `nothing to commit` for a store that repo ignores. A hand commit and
the `check-ignore` test that guarded it survive only in the fallback for a
`wi` older than the verb, which takes the store's lock too.

context-guard keeps its own sentence (it may not point into dev-flow), so the
rule is held here by what SKILL.md says. Standard library only; run from
plugins/context-guard/hooks:

    python3 -m unittest discover -s tests -q
"""
import os
import re
import unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(os.path.dirname(HOOKS), "skills", "checkpoint",
                     "SKILL.md")
FALLBACK_START = "A `wi` without `commit`"
FALLBACK_END = "Respect each repo's rules"


def flat(text):
    """Every run of whitespace one space, so a wrapped phrase is found."""
    return re.sub(r"\s+", " ", text)


def fallback_span(text):
    start = text.find(FALLBACK_START)
    if start < 0:
        return None
    end = text.find(FALLBACK_END, start)
    return start, (end if end >= 0 else len(text))


def outside(text, needle, span):
    """Offsets of needle in text that are not inside span."""
    out, i = [], text.find(needle)
    while i >= 0:
        if span is None or not span[0] <= i < span[1]:
            out.append(i)
        i = text.find(needle, i + 1)
    return out


class CheckpointStoreCommitTest(unittest.TestCase):
    def setUp(self):
        with open(SKILL, encoding="utf-8") as fh:
            self.text = flat(fh.read())
        self.span = fallback_span(self.text)

    def test_names_wi_commit(self):
        self.assertIn('Commit the store with `wi commit -m "<message>"`',
                      self.text)
        self.assertIn("Never commit the store with `git` directly.",
                      self.text)
        # Step 4a-half commits as 4a says
        self.assertIn('commit the store as 4a says (`wi commit -m', self.text)

    def test_check_ignore_only_in_the_fallback(self):
        self.assertIsNotNone(self.span)
        self.assertEqual(outside(self.text, "check-ignore", self.span), [])
        self.assertEqual(outside(self.text, 'git -C "$WORK_ITEMS_ROOT" commit',
                                 self.span), [])

    def test_fallback_takes_the_lock(self):
        fallback = self.text[slice(*self.span)]
        self.assertIn('flock -w 10 "$WORK_ITEMS_ROOT/.lock"', fallback)
        self.assertIn("check-ignore", fallback)

    def test_old_rule_is_gone(self):
        self.assertNotIn("The store's commit goes to the repo that holds it",
                         self.text)

    def test_checker_catches_a_check_ignore_outside(self):
        text = flat("skip it (`git -C x check-ignore -q x`). "
                    f"{FALLBACK_START} … check-ignore … {FALLBACK_END}")
        self.assertEqual(len(outside(text, "check-ignore",
                                     fallback_span(text))), 1)


if __name__ == "__main__":
    unittest.main()
