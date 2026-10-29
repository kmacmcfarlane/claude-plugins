"""Pin test for the research family's agent files.

The research family's three workers (`research-lane`, `research-lane-deep`,
`research-verifier`) each carry their full contract in the body, so their frontmatter may hold
any field a plugin agent honours, and must carry exactly its row's model and effort pin. The
frontmatter must parse the way the harness needs it to: a plugin agent whose YAML does not
parse still loads, with every field ignored (so no pin), and the error goes only to the debug
log. Every worker is a row of the research skill's intensity-and-routing.md § Profiles with its
pin, and every row there is a worker (or dev-cycle's shared `scout`, at its declared pin);
the two lane files share one body and one tool set. Every worker is named in CLAUDE.md,
README.md and both manifests of the plugin that ships it, and that plugin's description is
identical in the two manifests.

This file travels with the research family; dev-flow's `tests/test_agents.py` holds the role
workers, and dev-flow's `tests/test_research_parity.py` holds `scout`'s row to dev-flow's
`agents/scout.md`. The frontmatter reader is a copy of test_agents.py's: test helpers are not
shared across plugins.

Standard library only. Run from the plugin dir:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REPO = PLUGIN.parent.parent
AGENTS = PLUGIN / "agents"
ROUTING = PLUGIN / "skills" / "research" / "references" / "intensity-and-routing.md"

# Frontmatter fields a plugin agent honours (the plugins components docs). A worker carries
# at least name, description, model and effort, and nothing outside this set.
REQUIRED_KEYS = frozenset({"name", "description", "model", "effort"})
SUPPORTED_KEYS = frozenset({
    "name", "description", "model", "effort", "maxTurns", "tools", "disallowedTools",
    "skills", "memory", "background", "omitClaudeMd", "isolation", "color", "experimental",
})

MODELS = frozenset({"sonnet", "opus", "haiku", "fable", "inherit"})
EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})

# name: (model, effort)
EXPECTED = {
    "research-lane": ("sonnet", "medium"),
    "research-lane-deep": ("opus", "high"),
    "research-verifier": ("sonnet", "low"),
}

# dev-cycle's `scout` is shared: chain-of-verification dispatches it, so § Profiles carries
# its row too, at this pin (dev-flow's test_research_parity.py holds it to scout's file).
SHARED = {"scout": ("sonnet", "medium")}

# (rule, predicate on (model, effort), the only workers that may satisfy it). dev-flow's
# test_agents.py holds the same rules for the role workers; the two sets are disjoint.
RULES = [
    ("effort low", lambda m, e: e == "low", {"research-verifier"}),
    ("effort medium", lambda m, e: e == "medium", {"research-lane"}),
    ("opus at effort high", lambda m, e: m == "opus" and e == "high", {"research-lane-deep"}),
    ("effort xhigh", lambda m, e: e == "xhigh", set()),
    ("effort max", lambda m, e: e == "max", set()),
    ("model fable", lambda m, e: m == "fable", set()),
    ("model haiku", lambda m, e: m == "haiku", set()),
]


# ---------------------------------------------------------------------------------------
# A strict reader for the one frontmatter shape the agent files use (a copy of
# test_agents.py's): the block between the first two `---` lines, one top-level `key: value`
# per line, no duplicate keys, each value a valid single-line YAML scalar.

class FrontmatterError(ValueError):
    pass


KEY_LINE = re.compile(r"([A-Za-z][A-Za-z0-9]*): (.*)")
DQ_ESCAPES = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v",
              "f": "\f", "r": "\r", "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\",
              "N": "\x85", "_": "\xa0", "L": "\u2028", "P": "\u2029"}
PLAIN_BAD_START = set("[]{},#&*!|>'\"%@`")
NON_STRING = re.compile(r"(true|false|yes|no|on|off|null|~|[-+]?[0-9][0-9_.eE+-]*)",
                        re.IGNORECASE)


def _double_quoted(raw, key):
    if len(raw) < 2 or not raw.endswith('"'):
        raise FrontmatterError(f"{key}: double-quoted value is not closed at line end")
    body, out, i = raw[1:-1], [], 0
    while i < len(body):
        c = body[i]
        if c == '"':
            raise FrontmatterError(f"{key}: unescaped \" inside a double-quoted value")
        if c == "\\":
            if i + 1 >= len(body):
                raise FrontmatterError(f"{key}: dangling backslash")
            n = body[i + 1]
            if n in "xuU":
                width = {"x": 2, "u": 4, "U": 8}[n]
                digits = body[i + 2:i + 2 + width]
                if not re.fullmatch(r"[0-9A-Fa-f]{%d}" % width, digits):
                    raise FrontmatterError(f"{key}: bad \\{n} escape")
                out.append(chr(int(digits, 16)))
                i += 2 + width
                continue
            if n not in DQ_ESCAPES:
                raise FrontmatterError(f"{key}: unknown escape \\{n}")
            out.append(DQ_ESCAPES[n])
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _single_quoted(raw, key):
    if not re.fullmatch(r"'(?:[^']|'')*'", raw):
        raise FrontmatterError(f"{key}: single-quoted value is not closed, or has a lone '")
    return raw[1:-1].replace("''", "'")


def _plain(raw, key):
    if raw[0] in PLAIN_BAD_START or raw[:2] in ("- ", "? ", ": ") or raw in ("-", "?", ":"):
        raise FrontmatterError(f"{key}: unquoted value starts with a YAML indicator: {raw[:10]!r}")
    if ": " in raw or raw.endswith(":"):
        raise FrontmatterError(f"{key}: unquoted value contains ': ' (quote it)")
    if " #" in raw:
        raise FrontmatterError(f"{key}: unquoted value contains ' #', which starts a comment")
    return raw


def parse_frontmatter(text):
    """Return ({key: (value, quoting)}, body). quoting is 'double', 'single' or 'plain'."""
    if not text.startswith("---\n"):
        raise FrontmatterError("file does not start with a --- line")
    lines = text[4:].split("\n")
    try:
        end = lines.index("---")
    except ValueError:
        raise FrontmatterError("frontmatter is not closed by a second --- line") from None
    fields = {}
    for n, line in enumerate(lines[:end], 2):
        if "\t" in line:
            raise FrontmatterError(f"line {n}: tab character")
        m = KEY_LINE.fullmatch(line)
        if not m:
            raise FrontmatterError(f"line {n}: not a single top-level 'key: value' line: {line!r}")
        key, raw = m.group(1), m.group(2).strip(" ")
        if key in fields:
            raise FrontmatterError(f"line {n}: duplicate key {key!r}")
        if not raw:
            raise FrontmatterError(f"line {n}: {key} has no value")
        if raw[0] == '"':
            fields[key] = (_double_quoted(raw, key), "double")
        elif raw[0] == "'":
            fields[key] = (_single_quoted(raw, key), "single")
        else:
            value = _plain(raw, key)
            if key in ("name", "description") and NON_STRING.fullmatch(value):
                raise FrontmatterError(f"{key}: unquoted {value!r} does not load as a string")
            fields[key] = (value, "plain")
    return fields, "\n".join(lines[end + 1:])


def named(name, text):
    """A name as a token, never a substring: `research-lane` does not match in
    `research-lane-deep`."""
    return re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(name), text) is not None


def worker_files():
    """{stem: path} for the research workers on disk (the role workers beside them in
    dev-flow, while the family ships there, are test_agents.py's)."""
    return {p.stem: p for p in sorted(AGENTS.glob("research-*.md"))}


def fields_of(stem):
    return parse_frontmatter(worker_files()[stem].read_text(encoding="utf-8"))[0]


def profile_rows(text):
    """{agent: pin cell} for each `| `agent` | pin | ... |` row of the ## Profiles section,
    or None when the section is missing."""
    m = re.search(r"^## Profiles\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return None
    rows = {}
    for line in m.group(1).splitlines():
        row = re.match(r"\|\s*`([\w-]+)`\s*\|([^|]*)\|", line)
        if row:
            rows[row.group(1)] = row.group(2).strip()
    return rows


# ---------------------------------------------------------------------------------------

class TestFrontmatterReader(unittest.TestCase):
    """The reader must refuse what the harness would skip, or it passes a broken file."""

    GOOD = '---\nname: a\ndescription: "One. Two."\nmodel: opus\neffort: high\n---\n\nBody.\n'

    def bad(self, text, fragment):
        with self.assertRaises(FrontmatterError) as cm:
            parse_frontmatter(text)
        self.assertIn(fragment, str(cm.exception))

    def test_good_block_parses(self):
        fields, body = parse_frontmatter(self.GOOD)
        self.assertEqual(set(fields), {"name", "description", "model", "effort"})
        self.assertEqual(fields["description"], ("One. Two.", "double"))
        self.assertEqual(body.strip(), "Body.")

    def test_refuses_duplicate_key(self):
        self.bad(self.GOOD.replace("effort: high\n", "effort: high\neffort: low\n"), "duplicate")

    def test_refuses_unclosed_block(self):
        self.bad(self.GOOD.replace("\n---\n\nBody", "\n\nBody"), "not closed")

    def test_refuses_missing_opening(self):
        self.bad(self.GOOD[4:], "does not start")

    def test_refuses_inner_quote(self):
        self.bad(self.GOOD.replace('"One.', '"One "x".'), 'unescaped "')

    def test_refuses_unclosed_quote(self):
        self.bad(self.GOOD.replace('Two."', "Two."), "not closed")

    def test_refuses_colon_space_in_plain_value(self):
        self.bad(self.GOOD.replace('"One. Two."', "Role: one"), "': '")

    def test_refuses_comment_in_plain_value(self):
        self.bad(self.GOOD.replace("model: opus", "model: opus #pin"), "comment")

    def test_refuses_flow_sequence(self):
        self.bad(self.GOOD.replace("model: opus", "model: [opus]"), "indicator")

    def test_refuses_nested_line(self):
        self.bad(self.GOOD.replace("model: opus\n", "model: opus\n  extra: 1\n"), "top-level")

    def test_refuses_non_string_name(self):
        self.bad(self.GOOD.replace("name: a", "name: yes"), "string")

    def test_token_match_is_not_a_substring_match(self):
        self.assertFalse(named("research-lane", "`research-lane-deep` only"))
        self.assertTrue(named("research-lane", "`research-lane`, research-lane-deep"))


class TestTable(unittest.TestCase):
    def test_rules_hold_on_the_table(self):
        for rule, pred, only in RULES:
            with self.subTest(rule=rule):
                hit = {n for n, (m, e) in EXPECTED.items() if pred(m, e)}
                self.assertEqual(hit, only)

    def test_table_values_are_allowed(self):
        for name, (model, effort) in {**EXPECTED, **SHARED}.items():
            with self.subTest(agent=name):
                self.assertIn(model, MODELS)
                self.assertIn(effort, EFFORTS)


class TestWorkerFiles(unittest.TestCase):
    def setUp(self):
        self.files = worker_files()

    def test_every_row_exists_on_disk(self):
        self.assertEqual(len(EXPECTED), 3)
        self.assertEqual(set(EXPECTED) - set(self.files), set())

    def test_every_file_on_disk_is_in_the_table(self):
        self.assertEqual(set(self.files) - set(EXPECTED), set())

    def test_frontmatter_parses(self):
        for stem, path in self.files.items():
            with self.subTest(agent=stem):
                try:
                    parse_frontmatter(path.read_text(encoding="utf-8"))
                except FrontmatterError as e:
                    self.fail(f"{path.name}: {e}")

    def test_name_is_the_file_stem(self):
        for stem in self.files:
            with self.subTest(agent=stem):
                self.assertEqual(fields_of(stem)["name"][0], stem)

    def test_pins_match_the_table(self):
        for stem in self.files.keys() & EXPECTED.keys():
            model, effort = EXPECTED[stem]
            with self.subTest(agent=stem):
                fields = fields_of(stem)
                self.assertEqual(fields.get("model"), (model, "plain"))
                self.assertEqual(fields.get("effort"), (effort, "plain"))

    def test_rules_hold_on_disk(self):
        for rule, pred, only in RULES:
            with self.subTest(rule=rule):
                hit = set()
                for stem in self.files:
                    try:
                        f = fields_of(stem)
                    except FrontmatterError:
                        continue  # test_frontmatter_parses reports it
                    if pred(f.get("model", (None,))[0], f.get("effort", (None,))[0]):
                        hit.add(stem)
                self.assertLessEqual(hit, only)

    def test_keys(self):
        for stem in self.files.keys() & EXPECTED.keys():
            with self.subTest(agent=stem):
                keys = set(fields_of(stem))
                self.assertLessEqual(REQUIRED_KEYS, keys)
                self.assertLessEqual(keys, SUPPORTED_KEYS)


class TestResearchProfiles(unittest.TestCase):
    """The research skill's routing keeps its own § Profiles: every research worker is a row
    with its file's pin, and every row is a worker with its pin, or the shared scout at its
    declared pin."""

    @classmethod
    def setUpClass(cls):
        cls.rows = profile_rows(ROUTING.read_text(encoding="utf-8"))

    def test_section_exists(self):
        self.assertIsNotNone(self.rows, f"{ROUTING.name} has no ## Profiles section")

    def test_every_research_file_is_a_row_with_its_pin(self):
        research = sorted(s for s in worker_files() if s in EXPECTED)
        self.assertGreaterEqual(len(research), 3)
        for stem in research:
            model, effort = EXPECTED[stem]
            with self.subTest(agent=stem):
                self.assertIn(stem, self.rows or {})
                self.assertRegex(self.rows[stem], r"^%s / %s\b" % (model, effort))

    def test_every_row_is_an_agent_with_its_pin(self):
        rows = self.rows or {}
        self.assertEqual(set(rows) - set(worker_files()) - set(SHARED), set())
        for stem, cell in rows.items():
            model, effort = {**EXPECTED, **SHARED}[stem]
            with self.subTest(agent=stem):
                self.assertRegex(cell, r"^%s / %s\b" % (model, effort))

    def test_no_general_purpose_row(self):
        m = re.search(r"^## Profiles\n(.*?)(?=^## |\Z)",
                      ROUTING.read_text(encoding="utf-8"), re.S | re.M)
        self.assertIsNotNone(m)
        self.assertNotIn("general-purpose", m.group(1))

    def test_reader_takes_rows_of_the_section_only(self):
        text = ("## Profiles\n\n| Agent | Pin | When |\n|---|---|---|\n"
                "| `research-lane` | sonnet / medium | x |\n\n## Next\n\n"
                "| `scout` | sonnet / low | y |\n")
        self.assertEqual(profile_rows(text), {"research-lane": "sonnet / medium"})
        self.assertIsNone(profile_rows("## Other\n"))


class TestLaneVariants(unittest.TestCase):
    """research-lane-deep is research-lane at another effort: the contract body and the tool
    set are byte-identical, so every lane loads the same contract by construction."""

    def test_body_and_tools_match(self):
        files = worker_files()
        base_fields, base_body = parse_frontmatter(files["research-lane"].read_text(encoding="utf-8"))
        deep_fields, deep_body = parse_frontmatter(
            files["research-lane-deep"].read_text(encoding="utf-8"))
        self.assertEqual(deep_body, base_body)
        self.assertEqual(deep_fields["tools"], base_fields["tools"])


# The repo's own docs and marketplace sit two levels up only in the source repo; a copy of
# this plugin alone has none (kit-dev's standalone check runs it that way).
IN_REPO = all((REPO / f).is_file() for f in (".claude-plugin/marketplace.json", "CLAUDE.md",
                                            "README.md"))


@unittest.skipUnless(IN_REPO, "not in the source repo: no marketplace.json, CLAUDE.md or README.md")
class TestDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin_desc = json.loads(
            (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["description"]
        market = json.loads(
            (REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        entries = [p for p in market["plugins"] if p["name"] == PLUGIN.name]
        if len(entries) != 1:
            raise AssertionError(f"marketplace.json has {len(entries)} {PLUGIN.name} entries")
        cls.market_desc = entries[0]["description"]
        cls.claude_md = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        cls.readme = (REPO / "README.md").read_text(encoding="utf-8")

    def test_manifest_descriptions_are_identical(self):
        self.assertEqual(self.plugin_desc, self.market_desc)

    def test_every_worker_is_named_in_each_doc(self):
        stems = set(worker_files())
        self.assertTrue(stems)
        for stem in sorted(stems):
            with self.subTest(agent=stem):
                self.assertTrue(f"`{stem}`" in self.claude_md, "CLAUDE.md")
                self.assertTrue(f"`{stem}`" in self.readme, "README.md")
                self.assertTrue(named(stem, self.plugin_desc), "plugin.json description")
                self.assertTrue(named(stem, self.market_desc), "marketplace.json description")


if __name__ == "__main__":
    unittest.main()
