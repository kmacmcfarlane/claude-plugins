"""The format's decision lines: one table of every kind, and the rules on them.

Answer 344 (a) (2026-10-23), the decision-line grammar fixes (13bd): the format reference
gains § Decision line kinds, one row per line a decision writes, each naming its form, its
column, its writer, the `wi.py` pattern that reads it (if any) and its state. This file pins
that table: every kind named elsewhere in the format has a row, and a *landed* row that names
a pattern names one `wi.py` holds, which the row's form, filled in, matches. A *planned* row
names a pattern its plan will add, so it is not looked up until the row is switched.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import importlib.util
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAT = HERE.parent / "references" / "format.md"
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_format_lines", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

HEADING = "## Decision line kinds"

# every line kind the format and its callers write, by a token its row's form holds; a new
# kind gets a row and an entry here
KINDS = [
    "decision N:", "raised:", "revised:", "card:", "delegation:", "terms:", "act:",
    "grant:", "what:", "answer N:", "verbatim N", "given:", "wake N:", "closed N:",
    "withdrawn N:", "shown N:", "seen N:", "decided:", "open question:", "group g-",
    "depends N:", "writer-run:", "delegation dl-",
]

# the values a form's placeholders are filled with
FILL = {
    "N": "7", "UTC": "2026-10-23T10:00:00Z", "rev": "2026-10-23T10:00:00Z",
    "id": "an-item-1234", "file": "2026-10-23T10-00-00Z.card5.json", "k": "5",
}


def flat(text):
    return " ".join(text.split())


def section(text):
    start = text.index(HEADING)
    end = text.index("\n## ", start + len(HEADING))
    return text[start:end]


def rows(sec):
    """[{kind, form, column, writer, parses, state}] from the section's table."""
    out = []
    for line in sec.splitlines():
        if not line.startswith("| ") or line.startswith("| Kind ") or set(line) <= set("|- "):
            continue
        cells = [c.strip().replace("\\|", "|")
                 for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        out.append(dict(zip(("kind", "form", "column", "writer", "parses", "state"), cells)))
    return out


def fill(form, column):
    """The row's first form, filled with sample values: optional parts dropped, the first
    alternative taken, each placeholder its FILL value (else `x`), an indented kind indented."""
    code = re.search(r"`([^`]+)`", form).group(1)
    code = re.sub(r"\[[^\[\]]*\]", "", code)
    code = re.sub(r"<([^<>|]+?) \|[^<>]*>", r"<\1>", code)
    code = re.sub(r"<([^<>]+)>", lambda m: FILL.get(m.group(1), "x"), code)
    code = re.sub(r"(?<=: )N\b|\bN(?=[:/ ])", FILL["N"], code)
    code = code.replace("…", "x")
    return ("  " + code) if column.startswith("indented") else code


class DecisionLineKinds(unittest.TestCase):

    def setUp(self):
        self.text = FORMAT.read_text()
        self.sec = section(self.text)
        self.rows = rows(self.sec)

    def test_the_section_holds_one_table(self):
        self.assertGreaterEqual(len(self.rows), 15)
        for row in self.rows:
            self.assertEqual(len(row), 6, row)
            self.assertRegex(row["state"], r"^(landed|planned|legacy)\b", row["kind"])

    def test_every_kind_has_a_row(self):
        forms = " ".join(row["form"] for row in self.rows)
        for token in KINDS:
            self.assertIn(token, forms, f"no row names {token!r}")

    def test_every_n_keyed_line_named_in_the_format_has_a_row(self):
        # a `<word> N:` line named in any other section of the format is a kind
        rest = self.text.replace(self.sec, "")
        named = set(re.findall(r"`([a-z]+) (?:N|[0-9]+):", rest))
        kinds = {re.match(r"`?([a-z]+)", row["form"]).group(1) for row in self.rows}
        self.assertTrue(named)
        self.assertFalse(named - kinds, f"kinds with no row: {sorted(named - kinds)}")

    def test_a_landed_row_names_a_pattern_wi_holds_and_its_form_matches(self):
        checked = set()
        for row in self.rows:
            if not row["state"].startswith("landed"):
                continue
            for name in re.findall(r"\b[A-Z]+_RE\b", row["parses"]):
                pattern = getattr(wi, name, None)
                self.assertIsInstance(pattern, re.Pattern, f"{name} is not in wi.py")
                sample = fill(row["form"], row["column"])
                match = pattern.fullmatch if name == "CARD_RE" else pattern.match
                self.assertIsNotNone(match(sample), f"{name} does not read {sample!r}")
                checked.add(name)
        self.assertTrue({"DECISION_RE", "ANSWER_RE", "RAISED_RE", "CARD_RE", "SHOWN_RE",
                         "SEEN_RE"} <= checked, checked)

    def test_the_notes_under_the_table(self):
        sec = flat(self.sec)
        self.assertIn("the commit that builds it switches the row to *landed*", sec)
        self.assertIn("Event lines are never versioned", sec)
        self.assertIn("**`card:` in two places.**", sec)


class FollowUpsAreNeverAnswers(unittest.TestCase):
    """L1: `wi` reads any `answer N:` line as answered, so a follow-up written as one hides
    an open decision; the format says so, and how a line stored that way is rewritten."""

    def setUp(self):
        text = flat(FORMAT.read_text())
        start = text.index("## Operator questions")
        self.ops = text[start:text.index("## Allocating a decision number", start)]
        self.table = {row["kind"]: row for row in rows(section(FORMAT.read_text()))}

    def test_the_operator_questions_rule(self):
        self.assertIn("**A follow-up is never an answer line.** An `answer N:` line holds a "
                      "final answer only", self.ops)
        self.assertIn("`later`, `hold` and `dig into` write a `wake N:` line", self.ops)
        self.assertIn("`tell me` and `expand` write none", self.ops)
        self.assertIn("`wi` reads any `answer N:` line as answered", self.ops)
        self.assertIn("`verbatim N (moved <UTC>, from its answer line): <the original line>`",
                      self.ops)

    def test_the_table_rows(self):
        self.assertIn("a final answer only, never a follow-up", self.table["answer"]["state"])
        self.assertIn("(moved <UTC>, from its answer line)", self.table["verbatim"]["form"])


class Reframes(unittest.TestCase):
    """L2: a reframe writes its answer line and `closed N: superseded by M` together; a
    `withdrawn N:` line is legacy, read as those two lines."""

    def setUp(self):
        text = flat(FORMAT.read_text())
        start = text.index("## Closed: `closed N:`")
        self.closed = text[start:text.index("## Shown and seen", start)]
        self.table = {row["kind"]: row for row in rows(section(FORMAT.read_text()))}

    def test_the_closed_section(self):
        self.assertIn("A reframe closes as `superseded by M` at once, with its answer line: "
                      "`answer N: reframed as decision M …` and `closed N: superseded by M`, "
                      "written together.", self.closed)
        self.assertIn("An older `withdrawn N: reframed as M` line (no grammar of its own) is "
                      "read the same way", self.closed)
        self.assertIn("it is never written again", self.closed)

    def test_withdrawn_is_legacy_in_the_table(self):
        row = self.table["withdrawn"]
        self.assertTrue(row["state"].startswith("legacy: read as `answer N: reframed as "
                                                "decision M` and `closed N: superseded by M`"),
                        row["state"])
        self.assertEqual(row["writer"], "nobody: never written again")


class ShownNamesItsRev(unittest.TestCase):
    """L4: a showing names the card revision shown, one line per card on a page."""

    def setUp(self):
        self.text = FORMAT.read_text()
        start = self.text.index("## Shown and seen")
        self.shown = self.text[start:self.text.index("## Decided alone", start)]

    def test_the_grammar_line_takes_rev(self):
        self.assertIn("\nshown N: <UTC time> <chat | page | doc> [rev <rev>]\n", self.shown)
        self.assertIn("The optional `rev <rev>` after the surface word names the card revision "
                      "shown", flat(self.shown))

    def test_one_line_per_card_on_a_page(self):
        self.assertIn("one line per card, each naming that `rev`, never one note for the page",
                      flat(self.shown))

    def test_the_table_row(self):
        row = {r["kind"]: r for r in rows(section(self.text))}["shown"]
        self.assertIn("[rev <rev>]", row["form"])


if __name__ == "__main__":
    unittest.main()
