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
import shlex
import subprocess
import tempfile
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
        self.assertIn("Item-level log lines a decision may cause (`dispatch:`, `agent:`, "
                      "`result:`) carry no N and are not decision lines.", sec)


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
        self.assertIn("`later` (the `(z)` option too, by its letter or its words), `hold` and "
                      "`dig into` write a `wake N:` line", self.ops)
        self.assertIn("`tell me` and `expand` write none", self.ops)
        self.assertIn("`wi` reads any `answer N:` line as answered", self.ops)
        self.assertIn("`verbatim N (moved <UTC>, from its answer line): <the original line>`",
                      self.ops)
        self.assertIn("A `later`, `hold` or `dig into` stored as an answer line before this "
                      "rule, on a decision with no later final answer, is rewritten", self.ops)
        self.assertIn("one followed by a final answer is left as written", self.ops)

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


# ── 03ab F1: the group and depends lines ──────────────────────────────────────────────────

GROUPS = "## Groups and dependencies: `group` / `depends`"


def groups_section(text):
    """The § Groups and dependencies body, or '' when the heading is gone."""
    if GROUPS not in text:
        return ""
    start = text.index(GROUPS)
    return text[start:text.index("\n## ", start + len(GROUPS))]


def patterns(sec):
    """{name: compiled} from the section's own `- <name>: `<regex>`` bullets, `T` expanded."""
    t = re.search(r"`T` standing for one\s+target, `([^`]+)`", sec)
    out = {}
    for name, rx in re.findall(r"^- (group entity|group member|depends|each target): `([^`]+)`$",
                               sec, re.M):
        if name == "depends" and t:
            rx = rx.replace("T", "(?:" + t.group(1) + ")")
        out[name] = re.compile(rx)
    return out


ACCEPT = {
    "group member": ["group 290: g-1022-a3f"],
    "group entity": [
        "group g-1022-a3f: decision cards",
        "group g-1022-a3f: upload review findings · shares: all from today's review · "
        "context: the review read the upload path",
    ],
    "depends": [
        "depends 42: 41 (b)", "depends 42: 41 (a), 41 (c), 47", "depends 42: none",
        "depends 42: none — the reframe settled it", "depends 42: 41 (b), agents#12 — both",
    ],
}
REJECT = {
    "group member": ["group 290: GRP12", "group 290: decision cards", "group 290: g-1022-A3F"],
    "group entity": [
        "group g-22-a3f: x", "group g-1022-A3F: x", "group g-1022-a3f0: x",
        "group g-1022-a3f:  x", "group g-1022-a3f: x · shares: y", "group GRP12: x",
        "  group g-1022-a3f: x",
    ],
    "depends": [
        "depends 42: 41 (z)", "depends 42: 41b", "depends 42: 41 —  ", "  depends 42: 41",
        "depends 42:",
    ],
}


def grammar_problems(text):
    sec = groups_section(text)
    pats = patterns(sec)
    out = []
    for name in ("group entity", "group member", "depends", "each target"):
        if name not in pats:
            out.append(f"no {name} pattern")
    for name, lines in ACCEPT.items():
        for line in lines:
            if name in pats and not pats[name].match(line):
                out.append(f"{name} rejects {line!r}")
    for name, lines in REJECT.items():
        for line in lines:
            if name in pats and pats[name].match(line):
                out.append(f"{name} accepts {line!r}")
    if "group entity" in pats:
        m = pats["group entity"].match(ACCEPT["group entity"][1])
        if m and m.groups()[1:] != ("upload review findings", "all from today's review",
                                    "the review read the upload path"):
            out.append(f"the bundle form splits as {m.groups()!r}")
    if "group member" in pats and "group entity" in pats:
        if pats["group member"].match(ACCEPT["group entity"][0]) \
                or pats["group entity"].match(ACCEPT["group member"][0]):
            out.append("an entity line and a member line read as each other")
    if "each target" in pats:
        got = pats["each target"].findall("41 (a), 41 (c), agents#47")
        if got != [("", "41", "a"), ("", "41", "c"), ("agents", "47", "")]:
            out.append(f"the targets split as {got!r}")
    return out


def rules_problems(text):
    sec = flat(groups_section(text))
    want = [
        "The last entity line per id wins, so a rename is one appended entity line",
        "the last member line per N wins, so a regroup is one appended member line",
        "A reader looks an id up across the whole store, `items/` and then `archive/*/`",
        "A member line holding a name instead of an id is malformed",
        "reads its item's default group: the item's `short_display_name`, else its title",
        "Group ids are not numbers and take nothing from the decision counter",
        "there is no group counter and no lock",
        "Before writing it, check that it is not taken",
        "The session that finds one deletes the entity line it wrote, the one deletion these "
        "lines allow",
        "re-creates its group under a new id, with new member lines",
        "Repeats of one id within one item are renames (last wins), never a duplicate",
        "it is never shown to the operator, on any surface",
        "Targets on the same M are alternatives (any listed letter); targets on different Ms "
        "all apply",
        "so `(z)` is not written",
        "The last line per N is the whole set, and `none` empties it",
        "resolves to M, following the chain; the resolved edge keeps no letter",
        "`wi` does not parse them yet",
        "never through `raise --lines`",
        "never a dispatched agent",
        "never inserted between a `decision N:` headline and its card",
    ]
    return [w for w in want if w not in sec]


def fenced_after(sec, opener):
    """The first ```bash block whose first line starts with `opener`."""
    for block in re.findall(r"```bash\n(.*?)```", sec, re.S):
        if block.startswith(opener):
            return block
    return None


def make_id(text, t="2026-10-22T09:15:02Z", item="decisions-structured-depends-and-group-l-03ab",
            name="decision cards"):
    """Run the section's id line with a fixed time and inputs; its stdout, or None."""
    block = fenced_after(groups_section(text), "t=$(date")
    if block is None:
        return None
    block = block.replace("t=$(date -u +%Y-%m-%dT%H:%M:%SZ)", "t=" + t, 1)
    block = block.replace("<item id>", item).replace("<plain name>", name)
    run = subprocess.run(["bash", "-c", block], capture_output=True, text=True, timeout=30)
    return run.stdout.strip()


def taken(text, store, gid):
    """Run the section's not-taken check against `store` for `gid`: True when it says taken."""
    block = fenced_after(groups_section(text), "grep -rqE")
    if block is None:
        return None
    block = block.replace("<root>", shlex.quote(str(store))).replace("<id>", gid)
    run = subprocess.run(["bash", "-c", "unset -f grep find; " + block], capture_output=True,
                         text=True, timeout=30)
    return run.stdout.strip() == "taken"


ROWS = {
    "group": "`group g-<MMDD>-<hhh>: <plain name>[ · shares: <what its members share> · "
             "context: <shared context>]`",
    "group member": "`group N: g-<MMDD>-<hhh>`",
    "depends": "`depends N: <M[ (x)] | <repo>#M[ (x)] | none>[, …][ — <why>]`",
    "writer run": "`writer-run: <UTC> <page short name> w<k>/<K> — cards <n> · tokens "
                  "<input>/<output> · lints <n> [<keys>]`",
}


def table_problems(text):
    table = {r["kind"]: r for r in rows(section(text))}
    out = []
    for kind, form in ROWS.items():
        row = table.get(kind)
        if row is None:
            out.append(f"no {kind} row")
            continue
        if row["form"] != form:
            out.append(f"{kind} form {row['form']!r}")
        if not row["state"].startswith("landed"):
            out.append(f"{kind} is {row['state']!r}")
        if row["column"].split(",")[0] != "0":
            out.append(f"{kind} column {row['column']!r}")
    for kind in ("group", "group member", "depends"):
        if kind in table and "never a dispatched agent" not in table[kind]["writer"]:
            out.append(f"{kind} names no writer rule")
    return out


class GroupsAndDependencies(unittest.TestCase):
    """03ab F1: § Groups and dependencies gives the group entity and member lines, the
    `g-<MMDD>-<hhh>` id (made from a short time plus a hash, checked not taken, no counter),
    and `depends N:`; § Decision line kinds lists each kind as landed. Each check runs on the
    real format and on a mutant copy, which it must catch."""

    def setUp(self):
        self.text = FORMAT.read_text()

    def test_the_grammar(self):
        self.assertEqual(grammar_problems(self.text), [])

    def test_the_grammar_mutants(self):
        sec = groups_section(self.text)
        for old, new in [("[0-9a-f]{3})$", "[0-9a-zA-Z]{3})$"),  # member hex widened
                         (r"\([a-y]\))?`", r"\([a-z]\))?`"),     # (z) let through
                         ("[^·\\s][^·]*?)(?: · shares", ".+?)(?: · shares"),  # name takes ·
                         ("- depends: `", "- depend: `")]:       # the pattern lost
            self.assertIn(old, sec)
            cut = self.text.replace(sec, sec.replace(old, new))
            self.assertNotEqual(grammar_problems(cut), [], old)

    def test_the_rules(self):
        self.assertEqual(rules_problems(self.text), [])

    def test_the_rules_mutants(self):
        sec = groups_section(self.text)
        for phrase in ["Group ids are not numbers", "the one deletion these lines allow",
                       "Targets on the same M are alternatives", "`archive/*/`",
                       "never through `raise --lines`"]:
            self.assertIn(phrase, flat(sec))
            cut = self.text.replace(sec, flat(sec).replace(phrase, "gone"))
            self.assertNotEqual(rules_problems(cut), [], phrase)

    def test_the_id_line(self):
        self.assertEqual(make_id(self.text), "g-1022-d6f")
        self.assertRegex(make_id(self.text, t="2026-01-05T23:59:59Z", item="x", name="y"),
                         r"^g-0105-[0-9a-f]{3}$")

    def test_the_id_line_mutant(self):
        cut = self.text.replace("| cut -c1-3)", "| cut -c1-4)")
        self.assertNotEqual(cut, self.text)
        self.assertNotRegex(make_id(cut), r"^g-\d{4}-[0-9a-f]{3}$")

    def test_the_not_taken_check(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "items").mkdir()
            (root / "archive" / "2026").mkdir(parents=True)
            (root / "items" / "a.md").write_text("group g-1022-b00: one\n")
            (root / "archive" / "2026" / "b.md").write_text("group g-1022-a3f: two\n")
            self.assertTrue(taken(self.text, root, "g-1022-a3f"))
            self.assertTrue(taken(self.text, root, "g-1022-b00"))
            self.assertFalse(taken(self.text, root, "g-1022-c11"))
            # mutant: the archive left out of the check
            cut = self.text.replace("<root>/items <root>/archive", "<root>/items")
            self.assertNotEqual(cut, self.text)
            self.assertFalse(taken(cut, root, "g-1022-a3f"))

    def test_the_table_rows(self):
        self.assertEqual(table_problems(self.text), [])

    def test_the_table_rows_mutants(self):
        sec = section(self.text)
        for old, new in [("| landed; last line per N is the whole set |",
                          "| planned (the depends-and-groups plan) |"),
                         ("| group member |", "| member |"),
                         ("w<k>/<K> — cards", "w<k> — cards")]:
            self.assertIn(old, sec)
            cut = self.text.replace(sec, sec.replace(old, new))
            self.assertNotEqual(table_problems(cut), [], old)


if __name__ == "__main__":
    unittest.main()
