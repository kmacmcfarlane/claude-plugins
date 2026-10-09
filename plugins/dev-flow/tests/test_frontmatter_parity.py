"""The review checklist's frontmatter key list matches kit-dev's house rule (spike 72ef DF-13).

dev-cycle's review checklist (section 2) copies the allowed frontmatter keys into its lint,
so a review still runs without kit-dev. The house rule lives in kit-dev's frontmatter
reference; this test checks the copy against it, and the counts the checklist states,
whenever both files sit in the repo. In an isolated copy of dev-flow, with no kit-dev
beside it, the comparison skips; the checklist's own counts are checked either way.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
CHECKLIST = PLUGIN / "skills" / "dev-cycle" / "references" / "review-checklist.md"
# kit-dev's reference, as a sibling plugin of this one in the source repo.
HOUSE = (PLUGIN.parent / "kit-dev" / "skills" / "create-skill" / "references"
         / "frontmatter-reference.md")


def checklist_keys():
    """The `-e <key>` names of the checklist's allowed-keys grep, in order."""
    lines = CHECKLIST.read_text("utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if "allowed keys" in ln and ln.lstrip().startswith("#"))
    keys = []
    for ln in lines[start + 1:]:
        keys += re.findall(r"-e ([A-Za-z_-]+)", ln)
        if "key not allowed" in ln:
            break
    return keys


def stated_counts():
    """(total, required, other) as the checklist's comment above the grep states them."""
    text = CHECKLIST.read_text("utf-8")
    m = re.search(r"# the (\d+) allowed keys: (\d+) required \+ (\d+) optional", text)
    return tuple(int(g) for g in m.groups()) if m else None


def house_keys():
    """(required, allowed) backticked keys from the reference's House rule bullets."""
    text = HOUSE.read_text("utf-8")
    section = re.search(r"^## House rule.*?(?=^## )", text, re.S | re.M).group(0)
    bullets = {}
    for m in re.finditer(r"^- \*\*(\w+)\*\*:(.*?)(?=^- \*\*|^\S|\Z)", section, re.S | re.M):
        bullets[m.group(1)] = re.findall(r"`([A-Za-z_-]+)`", m.group(2))
    return bullets["Required"], bullets["Allowed"]


class ChecklistCounts(unittest.TestCase):
    def test_the_stated_counts_match_the_grep(self):
        keys = checklist_keys()
        counts = stated_counts()
        self.assertIsNotNone(counts, "the checklist's allowed-keys comment is gone")
        total, required, other = counts
        self.assertEqual(total, required + other)
        self.assertEqual(len(keys), total, f"the grep lists {len(keys)} keys: {keys}")
        self.assertEqual(len(set(keys)), len(keys), "a key is listed twice")
        self.assertEqual(keys[:2], ["name", "description"])
        prose = re.sub(r"\s+", " ", CHECKLIST.read_text("utf-8"))
        self.assertIn(f"{total} keys, the {required} required plus the {other} other", prose)


@unittest.skipUnless(HOUSE.is_file(), "kit-dev is not beside dev-flow: nothing to compare")
class Parity(unittest.TestCase):
    def test_the_copy_matches_the_house_rule(self):
        required, allowed = house_keys()
        keys = checklist_keys()
        self.assertEqual(required, ["name", "description"])
        self.assertEqual(sorted(keys), sorted(required + allowed),
                         "review-checklist.md section 2 and kit-dev's frontmatter "
                         "reference disagree; update the copy and its counts")


if __name__ == "__main__":
    unittest.main()
