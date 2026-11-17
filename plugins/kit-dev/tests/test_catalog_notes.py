"""Degrade notes the catalog must keep (README principle 4).

A plugin description names its dependencies only (CLAUDE.md § Conventions, Plugin
descriptions); how a plugin degrades without a peer is written in its README catalog
"Depends on" cell. This test pins the notes a plugin's own behaviour rests on, so trimming a
cell cannot drop them silently. Each entry in NOTES is (source plugin, target, phrases): the
target's entry in the source's cell, from its backticked name to the close of the
parenthesis that follows it, must hold every phrase.

The pins are proved by a mutant: the same check over a cell with a phrase removed fails.
Runs only in the source repo (it reads README.md); in an isolated copy of kit-dev the scan
skips, the mutants still run. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
README = REPO / "README.md"
IN_REPO = README.is_file() and (REPO / ".claude-plugin" / "marketplace.json").is_file()

NOTES = [
    # dev-flow's librarian runs the card-record checker when node is present, and stores
    # the record after wi's own checks without it.
    ("dev-flow", "operator-interaction", ("decision-page", "checker", "without the checker")),
    # research puts its asks to the operator per operator-interaction's guidance, and as a
    # plain lettered list without it.
    ("research", "operator-interaction", ("the research skills", "`decisions` skill",
                                          "plain lettered list")),
]


def catalog_cells(text):
    """Plugin name -> its catalog "Depends on" cell."""
    cells = {}
    for line in text.splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) == 4:
            m = re.fullmatch(r"`([a-z0-9-]+)`", cols[1])
            if m:
                cells[m.group(1)] = cols[3]
    return cells


def entry(cell, target):
    """The target's entry in a cell: `target` at depth 0 through its parenthesis; '' if none."""
    depth = 0
    i = 0
    head = f"`{target}`"
    while i < len(cell):
        ch = cell[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and cell.startswith(head, i):
            j = cell.find("(", i + len(head))
            if j < 0:
                return cell[i:]
            d = 0
            for k in range(j, len(cell)):
                if cell[k] == "(":
                    d += 1
                elif cell[k] == ")":
                    d -= 1
                    if d == 0:
                        return cell[i:k + 1]
            return cell[i:]
        i += 1
    return ""


def missing(cells, source, target, phrases):
    """Problems for one pin: an absent cell or entry, or each phrase the entry lacks."""
    if source not in cells:
        return [f"{source}: no catalog row"]
    e = entry(cells[source], target)
    if not e:
        return [f"{source}: no `{target}` entry in its Depends on cell"]
    return [f"{source} -> {target}: note lacks {p!r}" for p in phrases if p not in e]


ROW = ("| …x | `src` | **current** | `peer` (soft; uses its decision-page checker, and "
       "without the checker stores it anyway), `other` (soft; unrelated) |")


class Mutants(unittest.TestCase):
    def test_good_row_passes(self):
        cells = catalog_cells(ROW)
        self.assertEqual(missing(cells, "src", "peer",
                                 ("decision-page", "checker", "without the checker")), [])

    def test_dropped_phrase_fails(self):
        cells = catalog_cells(ROW.replace(", and without the checker stores it anyway", ""))
        self.assertTrue(missing(cells, "src", "peer", ("without the checker",)))

    def test_phrase_in_another_entry_fails(self):
        # The phrase must sit in the target's own entry, not a neighbour's.
        cells = catalog_cells(ROW)
        self.assertTrue(missing(cells, "src", "other", ("checker",)))

    def test_absent_entry_and_row_fail(self):
        cells = catalog_cells(ROW)
        self.assertTrue(missing(cells, "src", "gone", ("x",)))
        self.assertTrue(missing(cells, "nobody", "peer", ("x",)))


@unittest.skipUnless(IN_REPO, "needs the source repo (README.md)")
class RealCatalog(unittest.TestCase):
    def test_pinned_notes(self):
        cells = catalog_cells(README.read_text("utf-8"))
        problems = [p for src, tgt, phrases in NOTES for p in missing(cells, src, tgt, phrases)]
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
