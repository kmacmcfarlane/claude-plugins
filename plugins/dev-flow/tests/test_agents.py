"""Pin test for dev-flow's agent files.

Every file in plugins/dev-flow/agents/ must be a row of EXPECTED and carry exactly that
row's model and effort pin. The per-model and per-effort rules hold on the table and on
disk. The frontmatter must parse the way the harness needs it to: a plugin agent whose
YAML does not parse still loads, with every field ignored (so no pin), and the error goes
only to the debug log. Every agent is named in CLAUDE.md, README.md and both manifests,
and the dev-flow description is identical in the two manifests. Every role file is a row
of dev-cycle's model-routing.md § Profiles, which its description points at, and the row
carries the file's own pin. Every research worker is a row of the research skill's
intensity-and-routing.md § Profiles with its pin; the two lane files share one body and one
tool set; and scout keeps the tools chain-of-verification's checks need while that skill
dispatches it.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REPO = PLUGIN.parent.parent
AGENTS = PLUGIN / "agents"
ROUTING = PLUGIN / "skills" / "dev-cycle" / "references" / "model-routing.md"
RESEARCH_ROUTING = PLUGIN / "skills" / "research" / "references" / "intensity-and-routing.md"
COVE = PLUGIN / "skills" / "chain-of-verification" / "SKILL.md"

# The keys a role file carries, and nothing else. `tools` stays out (every tool) until the
# tool-limits change edits this table.
ROLE_KEYS = frozenset({"name", "description", "model", "effort"})

# Frontmatter fields a plugin agent honours (the plugins components docs). A contract-body
# file may carry any of these; a role file carries ROLE_KEYS only.
SUPPORTED_KEYS = frozenset({
    "name", "description", "model", "effort", "maxTurns", "tools", "disallowedTools",
    "skills", "memory", "background", "omitClaudeMd", "isolation", "color", "experimental",
})

MODELS = frozenset({"sonnet", "opus", "haiku", "fable", "inherit"})
EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})

DISPATCHER = "Dispatched by dev-flow's dev-cycle and librarian-mode"
NOT_DIRECT = "not for direct use."

# name: (model, effort, keys, kind)
#   keys: ROLE_KEYS for a role file; None for a research contract-body file, whose keys are
#         checked against SUPPORTED_KEYS.
#   kind: "role" (always shipped, dormant or not) or "research" (the research family's
#         workers).
EXPECTED = {
    "scribe": ("sonnet", "low", ROLE_KEYS, "role"),
    "scout": ("sonnet", "medium", ROLE_KEYS, "role"),
    "implementer": ("sonnet", "medium", ROLE_KEYS, "role"),
    "implementer-critical": ("opus", "high", ROLE_KEYS, "role"),
    "implementer-deep": ("opus", "xhigh", ROLE_KEYS, "role"),
    "planner": ("opus", "high", ROLE_KEYS, "role"),
    "planner-deep": ("opus", "xhigh", ROLE_KEYS, "role"),
    "reviewer": ("opus", "high", ROLE_KEYS, "role"),
    "cross-checker": ("fable", "high", ROLE_KEYS, "role"),
    "cross-checker-deep": ("fable", "xhigh", ROLE_KEYS, "role"),
    "research-lane": ("sonnet", "medium", None, "research"),
    "research-lane-deep": ("opus", "high", None, "research"),
    "research-verifier": ("sonnet", "low", None, "research"),
    # The operator's reviewer-effort answer (126 b) added it: opus medium for fact and docs
    # changes in the home-network and product-docs repos.
    "reviewer-light": ("opus", "medium", ROLE_KEYS, "role"),
}

# (rule, predicate on (model, effort), the only agents that may satisfy it)
RULES = [
    ("effort low", lambda m, e: e == "low", {"scribe", "research-verifier"}),
    ("effort medium", lambda m, e: e == "medium",
     {"implementer", "scout", "research-lane", "reviewer-light"}),
    ("opus at effort high", lambda m, e: m == "opus" and e == "high",
     {"implementer-critical", "planner", "reviewer", "research-lane-deep"}),
    ("effort xhigh", lambda m, e: e == "xhigh",
     {"implementer-deep", "planner-deep", "cross-checker-deep"}),
    ("effort max", lambda m, e: e == "max", set()),
    ("model fable", lambda m, e: m == "fable", {"cross-checker", "cross-checker-deep"}),
    ("model haiku", lambda m, e: m == "haiku", set()),
]


# ---------------------------------------------------------------------------------------
# A strict reader for the one frontmatter shape the agent files use: the block between the
# first two `---` lines, one top-level `key: value` per line, no duplicate keys, each value a
# valid single-line YAML scalar. It refuses what a YAML loader would refuse, and what it
# would load as something other than the written text.

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
    """A name as a token, never a substring: `planner` does not match in `planner-deep`."""
    return re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(name), text) is not None


def agent_files():
    return {p.stem: p for p in sorted(AGENTS.glob("*.md"))}


def pins():
    """{stem: (model, effort)} for every agent file on disk that parses."""
    out = {}
    for stem, path in agent_files().items():
        try:
            fields, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except FrontmatterError:
            continue  # test_frontmatter_parses reports it
        out[stem] = (fields.get("model", (None,))[0], fields.get("effort", (None,))[0])
    return out


# ---------------------------------------------------------------------------------------

class TestFrontmatterReader(unittest.TestCase):
    """The reader must refuse what the harness would skip, or it passes a broken file."""

    GOOD = '---\nname: a\ndescription: "One. Two; not for direct use."\nmodel: opus\neffort: high\n---\n\nBody.\n'

    def bad(self, text, fragment):
        with self.assertRaises(FrontmatterError) as cm:
            parse_frontmatter(text)
        self.assertIn(fragment, str(cm.exception))

    def test_good_block_parses(self):
        fields, body = parse_frontmatter(self.GOOD)
        self.assertEqual(set(fields), {"name", "description", "model", "effort"})
        self.assertEqual(fields["description"], ("One. Two; not for direct use.", "double"))
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
        self.bad(self.GOOD.replace('use."', "use."), "not closed")

    def test_refuses_colon_space_in_plain_value(self):
        self.bad(self.GOOD.replace('"One. Two; not for direct use."', "Role: one"), "': '")

    def test_refuses_comment_in_plain_value(self):
        self.bad(self.GOOD.replace("model: opus", "model: opus #pin"), "comment")

    def test_refuses_flow_sequence(self):
        self.bad(self.GOOD.replace("model: opus", "model: [opus]"), "indicator")

    def test_refuses_nested_line(self):
        self.bad(self.GOOD.replace("model: opus\n", "model: opus\n  extra: 1\n"), "top-level")

    def test_refuses_non_string_name(self):
        self.bad(self.GOOD.replace("name: a", "name: yes"), "string")

    def test_token_match_is_not_a_substring_match(self):
        self.assertFalse(named("planner", "`planner-deep` and cross-checker-deep"))
        self.assertFalse(named("cross-checker", "cross-checker-deep"))
        self.assertFalse(named("implementer", "implementer-critical"))
        self.assertTrue(named("planner", "`planner`, planner-deep"))


class TestTable(unittest.TestCase):
    def test_rules_hold_on_the_table(self):
        for rule, pred, only in RULES:
            with self.subTest(rule=rule):
                hit = {n for n, (m, e, _, _) in EXPECTED.items() if pred(m, e)}
                self.assertEqual(hit, only)

    def test_table_values_are_allowed(self):
        for name, (model, effort, _, _) in EXPECTED.items():
            with self.subTest(agent=name):
                self.assertIn(model, MODELS)
                self.assertIn(effort, EFFORTS)


class TestAgentFiles(unittest.TestCase):
    def setUp(self):
        self.files = agent_files()

    def fields(self, stem):
        return parse_frontmatter(self.files[stem].read_text(encoding="utf-8"))[0]

    def test_every_shipped_row_exists_on_disk(self):
        # Dormant files (dispatched only on a pin or a stage that may not arise) included.
        self.assertEqual(len(EXPECTED), 14)
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
                self.assertEqual(self.fields(stem)["name"][0], stem)

    def test_pins_match_the_table(self):
        for stem in self.files.keys() & EXPECTED.keys():
            model, effort, _, _ = EXPECTED[stem]
            with self.subTest(agent=stem):
                fields = self.fields(stem)
                self.assertEqual(fields.get("model"), (model, "plain"))
                self.assertEqual(fields.get("effort"), (effort, "plain"))

    def test_rules_hold_on_disk(self):
        on_disk = pins()
        for rule, pred, only in RULES:
            with self.subTest(rule=rule):
                hit = {n for n, (m, e) in on_disk.items() if pred(m, e)}
                self.assertLessEqual(hit, only)

    def test_keys(self):
        for stem in self.files.keys() & EXPECTED.keys():
            expected = EXPECTED[stem][2]
            with self.subTest(agent=stem):
                keys = set(self.fields(stem))
                if expected is None:
                    self.assertLessEqual(ROLE_KEYS, keys)
                    self.assertLessEqual(keys, SUPPORTED_KEYS)
                else:
                    self.assertEqual(keys, expected)

    def test_role_descriptions_are_dispatchable(self):
        roles = [s for s in self.files if s in EXPECTED and EXPECTED[s][2] is ROLE_KEYS]
        self.assertGreaterEqual(len(roles), 10)
        for stem in roles:
            model, effort, _, _ = EXPECTED[stem]
            with self.subTest(agent=stem):
                desc, quoting = self.fields(stem)["description"]
                self.assertEqual(quoting, "double")
                sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", desc)
                self.assertEqual(len(sentences), 2, sentences)
                role, dispatch = sentences
                self.assertIn("§ Profiles", role)
                for word in (model, effort):
                    self.assertRegex(role, re.compile(r"\b%s\b" % word, re.IGNORECASE))
                self.assertTrue(dispatch.startswith(DISPATCHER), dispatch)
                self.assertTrue(dispatch.endswith(NOT_DIRECT), dispatch)


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


class TestProfiles(unittest.TestCase):
    """Each role description routes by model-routing.md § Profiles: the pointer resolves, and
    the table there keeps each file's pin."""

    @classmethod
    def setUpClass(cls):
        cls.rows = profile_rows(ROUTING.read_text(encoding="utf-8"))

    def test_section_exists(self):
        self.assertIsNotNone(self.rows, f"{ROUTING.name} has no ## Profiles section")

    def test_every_role_file_is_a_row_with_its_pin(self):
        roles = sorted(s for s in agent_files() if s in EXPECTED and EXPECTED[s][2] is ROLE_KEYS)
        self.assertGreaterEqual(len(roles), 10)
        for stem in roles:
            model, effort, _, _ = EXPECTED[stem]
            with self.subTest(agent=stem):
                self.assertIn(stem, self.rows or {})
                self.assertRegex(self.rows[stem], r"^%s / %s\b" % (model, effort))

    def test_every_row_is_an_agent_file(self):
        self.assertEqual(set(self.rows or {}) - set(agent_files()), set())

    def test_reader_takes_rows_of_the_section_only(self):
        text = ("## Profiles\n\n| Agent | Pin | When |\n|---|---|---|\n"
                "| `planner` | opus / high | x |\n\n## Next\n\n| `scout` | sonnet / low | y |\n")
        self.assertEqual(profile_rows(text), {"planner": "opus / high"})
        self.assertIsNone(profile_rows("## Other\n"))


class TestResearchProfiles(unittest.TestCase):
    """The research skill's routing keeps its own § Profiles: every research worker is a row
    with its file's pin, and every row is an agent file with its pin (scout included)."""

    @classmethod
    def setUpClass(cls):
        cls.rows = profile_rows(RESEARCH_ROUTING.read_text(encoding="utf-8"))

    def test_section_exists(self):
        self.assertIsNotNone(self.rows, f"{RESEARCH_ROUTING.name} has no ## Profiles section")

    def test_every_research_file_is_a_row_with_its_pin(self):
        research = sorted(s for s in agent_files() if s in EXPECTED and EXPECTED[s][3] == "research")
        self.assertGreaterEqual(len(research), 3)
        for stem in research:
            model, effort, _, _ = EXPECTED[stem]
            with self.subTest(agent=stem):
                self.assertIn(stem, self.rows or {})
                self.assertRegex(self.rows[stem], r"^%s / %s\b" % (model, effort))

    def test_every_row_is_an_agent_file_with_its_pin(self):
        rows = self.rows or {}
        self.assertEqual(set(rows) - set(agent_files()), set())
        for stem, cell in rows.items():
            model, effort, _, _ = EXPECTED[stem]
            with self.subTest(agent=stem):
                self.assertRegex(cell, r"^%s / %s\b" % (model, effort))

    def test_no_general_purpose_row(self):
        m = re.search(r"^## Profiles\n(.*?)(?=^## |\Z)",
                      RESEARCH_ROUTING.read_text(encoding="utf-8"), re.S | re.M)
        self.assertIsNotNone(m)
        self.assertNotIn("general-purpose", m.group(1))


class TestLaneVariants(unittest.TestCase):
    """research-lane-deep is research-lane at another effort: the contract body and the tool
    set are byte-identical, so every lane loads the same contract by construction."""

    def test_body_and_tools_match(self):
        files = agent_files()
        base_fields, base_body = parse_frontmatter(files["research-lane"].read_text(encoding="utf-8"))
        deep_fields, deep_body = parse_frontmatter(
            files["research-lane-deep"].read_text(encoding="utf-8"))
        self.assertEqual(deep_body, base_body)
        self.assertEqual(deep_fields["tools"], base_fields["tools"])


class TestScoutServesCove(unittest.TestCase):
    """While chain-of-verification dispatches scout, scout keeps the tools its codebase and
    web checks use: no tools key (every tool), or one that includes them all."""

    NEEDED = {"WebSearch", "WebFetch", "Read", "Glob", "Grep"}

    def test_scout_keeps_coves_tools(self):
        if "dev-flow:scout" not in COVE.read_text(encoding="utf-8"):
            self.skipTest("chain-of-verification does not dispatch scout")
        fields, _ = parse_frontmatter(agent_files()["scout"].read_text(encoding="utf-8"))
        if "tools" not in fields:
            return
        tools = {t.strip() for t in fields["tools"][0].split(",")}
        self.assertLessEqual(self.NEEDED, tools)


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

    def test_every_agent_is_named_in_each_doc(self):
        stems = set(agent_files())
        self.assertTrue(stems)
        for stem in sorted(stems):
            with self.subTest(agent=stem):
                self.assertTrue(f"`{stem}`" in self.claude_md, "CLAUDE.md")
                self.assertTrue(f"`{stem}`" in self.readme, "README.md")
                self.assertTrue(named(stem, self.plugin_desc), "plugin.json description")
                self.assertTrue(named(stem, self.market_desc), "marketplace.json description")


if __name__ == "__main__":
    unittest.main()
