"""The stop rule: one home, copies held to it.

dev-cycle's agent-brief.md carries the Prohibitions bullet on stopping a process or a
background task ("Never send a signal ..."), and says so in its paragraph "The stop rule's
home". The review brief and the three research agents' bodies carry the same bullet word
for word, because each prompt must stand alone. This test holds every copy to the home
(whitespace and list marker aside), and holds the home to the parts the rule needs: the
recorded-PID route, the task-id route through the harness's background-task stop, and no
process found by name, pattern or listing.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REFS = PLUGIN / "skills" / "dev-cycle" / "references"
HOME = REFS / "agent-brief.md"
COPIES = [
    REFS / "review-brief.md",
    PLUGIN / "agents" / "research-lane.md",
    PLUGIN / "agents" / "research-lane-deep.md",
    PLUGIN / "agents" / "research-verifier.md",
]
START = "Never send a signal"


def stop_rule(path):
    """The list item that starts with START, its continuation lines joined, whitespace
    collapsed. Fails when there is not exactly one."""
    lines = path.read_text(encoding="utf-8").splitlines()
    found = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(- |\d+\. )" + re.escape(START), line)
        if not m:
            continue
        indent = len(m.group(1)) + len(m.group(2))
        item = [line[indent:]]
        for nxt in lines[i + 1:]:
            if not nxt.strip() or not nxt.startswith(" " * indent):
                break  # a blank line or the next item ends this one
            item.append(nxt.strip())
        found.append(" ".join(" ".join(item).split()))
    if len(found) != 1:
        raise AssertionError(f"{path.name}: {len(found)} stop-rule bullets, want 1")
    return found[0]


class StopRule(unittest.TestCase):
    def test_home_names_both_routes(self):
        rule = stop_rule(HOME)
        self.assertIn("never stop a background task, agent or teammate you did not start", rule)
        self.assertIn("the PID you recorded (`$!` after a background start)", rule)
        self.assertIn("`run_in_background`, its task id", rule)
        self.assertIn("`TaskStop`", rule)
        self.assertIn("https://code.claude.com/docs/en/tools-reference", rule)
        self.assertIn("Never by name or pattern", rule)
        self.assertIn("(`ps`, `pgrep`, `/tasks`, or a list in an error)", rule)
        self.assertIn("inside a container or not", rule)

    def test_home_paragraph_names_every_copy(self):
        text = HOME.read_text(encoding="utf-8")
        self.assertIn("**The stop rule's home.**", text)
        for name in ("review-brief.md", "`research-lane`", "`research-lane-deep`",
                     "`research-verifier`", "tests/test_stop_rule.py"):
            self.assertIn(name, text)

    def test_no_unlisted_copy(self):
        listed = {HOME.resolve(), *(p.resolve() for p in COPIES)}
        bullet = re.compile(r"^(\s*)(- |\d+\. )" + re.escape(START), re.M)
        for path in PLUGIN.rglob("*.md"):
            if bullet.search(path.read_text(encoding="utf-8")):
                with self.subTest(path=str(path.relative_to(PLUGIN))):
                    self.assertIn(path.resolve(), listed)

    def test_copies_match_home(self):
        home = stop_rule(HOME)
        for path in COPIES:
            with self.subTest(path=path.name):
                self.assertEqual(stop_rule(path), home)

    def test_review_brief_points_home(self):
        text = REFS.joinpath("review-brief.md").read_text(encoding="utf-8")
        self.assertIn("\"The stop rule's home\"", " ".join(text.split()))


if __name__ == "__main__":
    unittest.main()
