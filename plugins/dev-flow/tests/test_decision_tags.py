"""The two-word decision tags (answer 134 (a), item bb44).

A raised decision's `why ask:` opens with a reason (why it is the operator's), a decision
alone's `decided:` line carries a kind (what changed), and the old spellings live only in
`decide-alone.md` § Class names, ### Retired spellings, the map every librarian migrates its
store from. The skills are prose, so the rules are held by what their files say:

- § Class names lists exactly the nine reasons plus `unclassed`, and the six kinds;
- § The line's reasons table runs in the fixed order § Class names gives;
- the Retired spellings subsection is the file's last heading (the residue check's exemption
  runs to the next heading), and every new tag it maps to is a current tag;
- outside that subsection, no dev-flow file writes a retired spelling as a tag, names a
  retired tag as a class, or opens a trade-off's text with the retired `<impact>:` shape.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = PLUGIN / "skills"
DECIDE = SKILLS / "librarian-mode" / "references" / "decide-alone.md"

REASONS = ["blocker", "one-way", "trust", "contract", "reach", "spend", "precedent",
           "your-call", "trade-off", "unclassed"]
KINDS = ["words", "design", "place", "scope", "reading", "cap"]
CURRENT = set(REASONS) | set(KINDS)
RETIRED = ["wording", "minor-design", "narrowing", "ruled-rule-case", "table-placement",
           "reply-reading", "forwarding", "wider-scope", "rule-change", "placement",
           "api-name", "relay"]
RETIRED_HEADING = "### Retired spellings"


def text(path):
    return path.read_text(encoding="utf-8")


def section(body, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else None


def first_column(table_text, header, col=1):
    """The backticked tags in column `col` (1-based) of the table whose header row opens `header`."""
    lines = table_text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("| " + header + " |"))
    tags = []
    for ln in lines[start + 2:]:
        if not ln.startswith("|"):
            break
        cell = ln.split("|")[col]
        tags += re.findall(r"`([a-z-]+)`", cell)
    return tags


def outside_retired(body):
    """The file's lines with the Retired spellings subsection blanked (up to the next heading)."""
    out, skip = [], False
    for ln in body.splitlines():
        if ln.startswith(RETIRED_HEADING):
            skip = True
            out.append("")
            continue
        if ln.startswith("#"):
            skip = False
        out.append("" if skip else ln)
    return out


def dev_flow_texts():
    for path in sorted(SKILLS.rglob("*.md")):
        body = text(path)
        lines = outside_retired(body) if path == DECIDE else body.splitlines()
        yield path, lines


class TestClassNames(unittest.TestCase):
    def setUp(self):
        self.names = section(text(DECIDE), "Class names")
        self.assertIsNotNone(self.names, "decide-alone.md has no § Class names")

    def test_the_reasons(self):
        self.assertEqual(first_column(self.names, "Reason"), REASONS)

    def test_the_kinds(self):
        self.assertEqual(first_column(self.names, "Kind"), KINDS)

    def test_the_line_runs_the_reasons_in_order(self):
        line = section(text(DECIDE), "The line")
        self.assertEqual(first_column(line, "#", col=2), REASONS)

    def test_the_line_lists_the_kinds(self):
        line = section(text(DECIDE), "The line")
        self.assertEqual(first_column(line, "Kind"), KINDS)


class TestRetiredSpellings(unittest.TestCase):
    def setUp(self):
        self.body = text(DECIDE)
        self.lines = self.body.splitlines()

    def test_it_is_the_last_heading(self):
        heads = [ln for ln in self.lines if ln.startswith("#")]
        self.assertEqual(heads[-1], RETIRED_HEADING)

    def test_no_fence_line_opens_with_a_hash(self):
        # A `#` line inside the subsection, even in a code block, ends the exemption early.
        i = self.lines.index(RETIRED_HEADING)
        for n, ln in enumerate(self.lines[i + 1:], i + 2):
            self.assertFalse(ln.startswith("#"), f"decide-alone.md:{n}: {ln}")

    def test_every_retired_spelling_is_mapped(self):
        i = self.lines.index(RETIRED_HEADING)
        sub = "\n".join(self.lines[i:])
        for old in RETIRED:
            self.assertRegex(sub, re.compile(r"^\| [^|]*`" + re.escape(old) + r"`", re.M), old)

    def test_every_new_tag_is_current(self):
        i = self.lines.index(RETIRED_HEADING)
        for ln in self.lines[i:]:
            cells = ln.split("|")
            if not ln.startswith("| `") or len(cells) < 4:
                continue
            new = cells[3]
            first = re.search(r"`([a-z-]+)`", new)
            if new.strip().startswith("read by hand") or new.strip().startswith("the reason"):
                continue
            self.assertIsNotNone(first, ln)
            self.assertIn(first.group(1), CURRENT, ln)


class TestNoRetiredResidue(unittest.TestCase):
    def test_no_retired_tag_in_backticks(self):
        pat = re.compile(r"`(" + "|".join(map(re.escape, RETIRED)) + r")`")
        for path, lines in dev_flow_texts():
            for n, ln in enumerate(lines, 1):
                m = pat.search(ln)
                self.assertIsNone(m, f"{path.relative_to(PLUGIN)}:{n}: {m and m.group(0)}")

    def test_every_named_class_is_current(self):
        pat = re.compile(r"class `([a-z-]+)`")
        for path, lines in dev_flow_texts():
            for n, ln in enumerate(lines, 1):
                for tag in pat.findall(ln):
                    self.assertIn(tag, CURRENT, f"{path.relative_to(PLUGIN)}:{n}")

    def test_no_trade_off_opens_with_a_word_and_colon(self):
        pat = re.compile(r"why ask: trade-off — [a-z-]+:")
        for path, lines in dev_flow_texts():
            for n, ln in enumerate(lines, 1):
                self.assertIsNone(pat.search(ln), f"{path.relative_to(PLUGIN)}:{n}")


if __name__ == "__main__":
    unittest.main()
