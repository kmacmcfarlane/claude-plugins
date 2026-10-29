"""The stop rule inside the research family: one bullet, three bodies.

The research family's three agent bodies (`research-lane`, `research-lane-deep`,
`research-verifier`) carry the Prohibitions bullet on stopping a process or a background
task ("Never send a signal ..."), because each prompt must stand alone. Within the family,
`research-lane.md` is the home: the other two carry it word for word (whitespace and list
marker aside), it names the parts the rule needs (the recorded-PID route, the task-id route
through the harness's background-task stop, and no process found by name, pattern or
listing), and no other family file carries a copy.

The rule's home across the marketplace is dev-cycle's agent-brief.md; dev-flow's
tests/test_research_parity.py holds this family's home to it while both are present. This
file travels with the family.

Standard library only. Run from the plugin dir:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
AGENTS = PLUGIN / "agents"
HOME = AGENTS / "research-lane.md"
COPIES = [AGENTS / "research-lane-deep.md", AGENTS / "research-verifier.md"]
FAMILY_SKILLS = ("research", "research-deep", "research-refine", "research-prune",
                 "chain-of-verification")
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


def family_files():
    """Every *.md the family ships: its agents and its skills."""
    out = sorted(AGENTS.glob("research-*.md"))
    for name in FAMILY_SKILLS:
        out += sorted((PLUGIN / "skills" / name).rglob("*.md"))
    return out


class ResearchStopRule(unittest.TestCase):
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

    def test_copies_match_home(self):
        home = stop_rule(HOME)
        for path in COPIES:
            with self.subTest(path=path.name):
                self.assertEqual(stop_rule(path), home)

    def test_no_unlisted_copy(self):
        listed = {HOME.resolve(), *(p.resolve() for p in COPIES)}
        bullet = re.compile(r"^(\s*)(- |\d+\. )" + re.escape(START), re.M)
        files = family_files()
        self.assertGreaterEqual(len(files), 8)  # guards the walk: 3 agents, 5 SKILL.md
        for path in files:
            if bullet.search(path.read_text(encoding="utf-8")):
                with self.subTest(path=str(path.relative_to(PLUGIN))):
                    self.assertIn(path.resolve(), listed)


if __name__ == "__main__":
    unittest.main()
