"""dev-flow's copies of the work-item store lookup (item 5f46, F3).

wi finds its store at `.work-items/`, then at the old `.claude-sandbox/work/`, then at the
old `.work/`, and reads `WORK_ITEMS_ROOT` before the deprecated `WI_ROOT`. dev-flow keeps two
copies of that lookup: the `dev-cycle` skill's `references/bindings.md` § Store (the
canonical one every other dev-flow skill names) and the research family's own,
`research/references/intensity-and-routing.md` § Resolving the store (kept separate by the
operator's 2026-10-02 ruling, so the two are not required to match byte for byte). The
skills are prose, so the rules are held by what their files say:

- each copy names the three locations in that order, in its prose and in its loop;
- each copy's loop exports both names;
- across every `*.md` under `plugins/dev-flow/`, any line that assigns `WORK_ITEMS_ROOT=` or
  `WI_ROOT=` (an `export`, a command prefix, a brief's `Store:` line) assigns both, so an
  installed wi older than these copies still finds the store;
- the librarian's first start creates `.work-items/` with both names set as a prefix.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = PLUGIN / "skills"
COPIES = {
    "bindings.md § Store": (SKILLS / "dev-cycle" / "references" / "bindings.md", "## Store"),
    "intensity-and-routing.md § Resolving the store": (
        SKILLS / "research" / "references" / "intensity-and-routing.md",
        "### Resolving the store"),
}
FIRST_START = SKILLS / "librarian-mode" / "references" / "first-start.md"

# The three locations as the loop names them, and as the prose names them, in order.
LOOP_LOCATIONS = ['"$MAIN/.work-items"', '"$MAIN/.claude-sandbox/work"', '"$MAIN/.work"']
PROSE_LOCATIONS = ["`.work-items/`", "`.claude-sandbox/work/`", "`.work/`"]
NEW, OLD = "WORK_ITEMS_ROOT", "WI_ROOT"
ASSIGN = re.compile(r"(?<![A-Za-z0-9_])(WORK_ITEMS_ROOT|WI_ROOT)=")


def section(path, heading):
    """The text from `heading` to the next heading of the same or a higher level."""
    lines = path.read_text(encoding="utf-8").split("\n")
    level = len(heading) - len(heading.lstrip("#"))
    start = lines.index(heading)
    out, fenced = [], False
    for line in lines[start + 1:]:
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"#{1,%d} " % level, line):
            break
        out.append(line)
    return "\n".join(out)


def names_in_order(text, names):
    """True when every name occurs in text and their first occurrences are in order."""
    at = [text.find(n) for n in names]
    return all(i >= 0 for i in at) and at == sorted(at)


def assigns_both(line):
    """None when the line assigns neither name or both; else the names it is missing."""
    found = set(ASSIGN.findall(line))
    if not found:
        return None
    missing = {NEW, OLD} - found
    return missing or None


def loop_lines(text):
    return [l for l in text.split("\n") if l.startswith("for d in ")]


class CopiesTest(unittest.TestCase):
    def test_each_copy_has_one_loop(self):
        for name, (path, heading) in COPIES.items():
            with self.subTest(copy=name):
                self.assertEqual(len(loop_lines(section(path, heading))), 1)

    def test_loop_names_the_three_locations_in_order(self):
        for name, (path, heading) in COPIES.items():
            with self.subTest(copy=name):
                (loop,) = loop_lines(section(path, heading))
                found = re.findall(r'"\$MAIN/[^"]*"', loop.split(";")[0])
                self.assertEqual(found, LOOP_LOCATIONS)

    def test_prose_names_the_three_locations_in_order(self):
        for name, (path, heading) in COPIES.items():
            with self.subTest(copy=name):
                prose = section(path, heading).split("```")[0]
                self.assertTrue(names_in_order(prose, PROSE_LOCATIONS),
                                f"{name}: prose must name {PROSE_LOCATIONS} in order")

    def test_loop_exports_both_names(self):
        for name, (path, heading) in COPIES.items():
            with self.subTest(copy=name):
                (loop,) = loop_lines(section(path, heading))
                self.assertIn(f'export {NEW}="$d" {OLD}="$d"', loop)


class AssignmentsTest(unittest.TestCase):
    def test_every_assignment_sets_both_names(self):
        bad = []
        for path in sorted(PLUGIN.rglob("*.md")):
            for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
                missing = assigns_both(line)
                if missing:
                    bad.append(f"{path.relative_to(PLUGIN)}:{n}: missing "
                               f"{', '.join(sorted(missing))}: {line.strip()}")
        self.assertEqual(bad, [], "\n" + "\n".join(bad))

    def test_some_assignments_are_seen(self):
        # Guards the scan itself: the two loops and the two briefs' Store: lines at least.
        hits = [line for path in PLUGIN.rglob("*.md")
                for line in path.read_text(encoding="utf-8").split("\n")
                if ASSIGN.search(line)]
        self.assertGreaterEqual(len(hits), 4)

    def test_first_start_sets_both_as_a_prefix(self):
        text = FIRST_START.read_text(encoding="utf-8")
        self.assertIn(f'{NEW}="$MAIN/.work-items" {OLD}="$MAIN/.work-items" $WI init',
                      text)


class CheckerTest(unittest.TestCase):
    """Each check catches what it is for."""

    def test_one_name_alone_is_flagged(self):
        self.assertEqual(assigns_both('export WI_ROOT="$d"'), {NEW})
        self.assertEqual(assigns_both('Store: export WORK_ITEMS_ROOT=<abs>'), {OLD})
        self.assertEqual(assigns_both('WI_ROOT="$MAIN/.work-items" $WI init'), {NEW})

    def test_both_names_or_none_pass(self):
        self.assertIsNone(assigns_both('export WORK_ITEMS_ROOT="$d" WI_ROOT="$d"'))
        self.assertIsNone(assigns_both('exports `WORK_ITEMS_ROOT` and `WI_ROOT`'))
        self.assertIsNone(assigns_both('test -n "$WORK_ITEMS_ROOT"'))

    def test_old_order_is_caught(self):
        old = 'for d in "$MAIN/.claude-sandbox/work" "$MAIN/.work" "$MAIN/.work-items"; do'
        self.assertNotEqual(re.findall(r'"\$MAIN/[^"]*"', old), LOOP_LOCATIONS)
        self.assertFalse(names_in_order("`.claude-sandbox/work/`, `.work/`, `.work-items/`",
                                        PROSE_LOCATIONS))
        self.assertFalse(names_in_order("`.claude-sandbox/work/`, then `.work/`",
                                        PROSE_LOCATIONS))


if __name__ == "__main__":
    unittest.main()
