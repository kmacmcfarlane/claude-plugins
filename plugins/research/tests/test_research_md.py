"""The repo's RESEARCH.md: its template, its owner section, and the skills' pointers (f4ef F4).

A repo describes its research corpus for any agent in a RESEARCH.md at the top of the
checkout, found through one plain markdown-link line in CLAUDE.md. One owner section,
`storage-and-knowledge-base.md` § RESEARCH.md, holds every rule; the skills point to it. The
skills are prose, so the rules are held by what their files say:

- the template has the frontmatter keys and the sections, in the order the owner section's
  shape table gives;
- the owner section exists once and carries its load-bearing rules (the four content
  sources, never fetched text, the exact pointer line, CLAUDE.md never written by a skill);
- no `@` import of RESEARCH.md anywhere in the plugin;
- rule 3 reads KB.md, then RESEARCH.md's `kb:`, then the legacy CLAUDE.md key;
- research, research-refine and research-prune point to the section, and the charter round
  carries its question;
- the plugin's manifest names RESEARCH.md, and in the source repo the marketplace entry and
  the README catalog row do too.

Standard library only. Run from the plugin dir:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = PLUGIN / "skills"
STORAGE = SKILLS / "research" / "references" / "storage-and-knowledge-base.md"
TEMPLATE = SKILLS / "research" / "assets" / "RESEARCH.template.md"
REPO = PLUGIN.parent.parent
HEADING = "RESEARCH.md"
POINTER = "§ " + HEADING
POINTER_LINE = ("Research: [RESEARCH.md](RESEARCH.md) — where this repo's research lands and its "
                "shape; read it before researching or citing research here.")
SECTIONS = ("## Where research lands", "## Shape", "## Before you research", "## Optional")
KEYS = ("kind", "updated", "kb", "runs")
FIXED_SUMMARY = "Research for <repo name>: where it lands and how it is laid out."


def text(path):
    return path.read_text(encoding="utf-8")


def flat(s):
    """Whitespace runs folded to one space, so a rule wrapped across lines still matches."""
    return re.sub(r"\s+", " ", s)


def section(body, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading outside a fence."""
    out, inside, fence = [], False, False
    for line in body.splitlines():
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            if inside:
                break
            inside = line == "## " + heading
            continue
        if inside:
            out.append(line)
    return "\n".join(out) if inside or out else None


def frontmatter_keys(body):
    m = re.match(r"---\n(.*?)\n---\n", body, re.S)
    if not m:
        return None
    return [ln.split(":", 1)[0] for ln in m.group(1).splitlines() if ln and not ln.startswith(" ")]


class TestTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = text(TEMPLATE)

    def test_frontmatter_keys_in_order(self):
        self.assertEqual(frontmatter_keys(self.body), list(KEYS))
        self.assertIn("\nkind: research-corpus\n", self.body)

    def test_h1_then_summary(self):
        after = self.body.split("\n---\n", 1)[1].lstrip("\n").splitlines()
        self.assertTrue(after[0].startswith("# Research — "), after[0])
        nxt = [ln for ln in after[1:] if ln.strip()][0]
        self.assertTrue(nxt.startswith("> "), nxt)

    def test_sections_in_order(self):
        heads = [ln for ln in self.body.splitlines() if ln.startswith("## ")]
        self.assertEqual(heads, list(SECTIONS))

    def test_fixed_summary_matches_the_owner_section(self):
        self.assertIn(FIXED_SUMMARY, self.body)
        self.assertIn(FIXED_SUMMARY, flat(section(text(STORAGE), HEADING)))

    def test_shape_table_follows_the_template(self):
        """The owner section's shape table names each key and section in the template's order."""
        sec = section(text(STORAGE), HEADING)
        rows = [ln for ln in sec.splitlines() if ln.startswith("| `")]
        names = [re.match(r"\| `([^`]+)`", r).group(1) for r in rows]
        wanted = ["kind: research-corpus", "updated:", "kb:", "runs:"] + list(SECTIONS)
        got = [n for n in names if n in wanted]
        self.assertEqual(got, wanted)
        self.assertIn("# Research — <repo name>", names)


class TestOwnerSection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = text(STORAGE)
        sec = section(cls.body, HEADING)
        if not sec:
            raise AssertionError(f"no '## {HEADING}' in {STORAGE.name}")
        cls.raw = sec
        cls.sec = flat(sec)

    def test_heading_exactly_once(self):
        self.assertEqual(len(re.findall(r"^## RESEARCH\.md$", self.body, re.M)), 1)

    def test_pointer_line_exact(self):
        fenced = re.findall(r"```markdown\n(.*?)\n\s*```", self.raw, re.S)
        self.assertEqual([f.strip() for f in fenced], [POINTER_LINE])

    def test_four_content_sources(self):
        for needle in ("four sources only", "paths", "purpose sentence", "fixed text",
                       "text the operator wrote or approved",
                       "Never from fetched pages or lane output"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.sec)

    def test_claude_md_never_written(self):
        self.assertIn("`CLAUDE.md` is never written by a skill.", self.sec)
        self.assertIn("never an `@` import", self.sec)

    def test_template_named(self):
        self.assertIn("`assets/RESEARCH.template.md`", self.sec)

    def test_without_it(self):
        self.assertIn("A repo without it", self.sec)

    def test_unattended_writes_nothing(self):
        self.assertIn("Unattended: nothing is written.", self.sec)


class TestNoImport(unittest.TestCase):
    def test_no_at_import_in_the_plugin(self):
        at = "@" + "RESEARCH.md"
        hits = [p for p in PLUGIN.rglob("*") if p.is_file() and "tests" not in p.parts
                and p.suffix in (".md", ".json", ".py", ".sh") and at in text(p)]
        self.assertEqual(hits, [])


class TestRuleThree(unittest.TestCase):
    def test_order_kb_md_then_kb_key_then_legacy(self):
        row = [ln for ln in text(STORAGE).splitlines() if ln.startswith("| 3 |")]
        self.assertEqual(len(row), 1)
        cell = row[0]
        pos = [cell.find(n) for n in ("containing `KB.md`", "`RESEARCH.md`'s `kb:`",
                                      "a `research:` key")]
        self.assertNotIn(-1, pos, cell)
        self.assertEqual(pos, sorted(pos), cell)
        self.assertIn("legacy", cell[pos[1]:])


class TestPointers(unittest.TestCase):
    def test_each_skill_points_to_the_section(self):
        for name in ("research", "research-refine", "research-prune"):
            with self.subTest(skill=name):
                self.assertIn(POINTER, text(SKILLS / name / "SKILL.md"))

    def test_research_steps(self):
        body = text(SKILLS / "research" / "SKILL.md")
        for step in ("## Step 2", "## Step 4", "## Step 10", "## Step 11"):
            with self.subTest(step=step):
                sec = body.split(step, 1)[1].split("\n## ", 1)[0]
                self.assertIn("RESEARCH.md", sec)
        step11 = flat(body.split("## Step 11", 1)[1].split("\n## ", 1)[0])
        self.assertIn("hands over the pointer line", step11)
        self.assertIn("never writes `CLAUDE.md` itself", step11)

    def test_refine_step_one(self):
        body = text(SKILLS / "research-refine" / "SKILL.md")
        sec = body.split("### Step 1", 1)[1].split("\n### ", 1)[0]
        self.assertIn(POINTER, flat(sec))

    def test_prune_rows(self):
        body = text(SKILLS / "research-prune" / "SKILL.md")
        for kind in ("add", "drop", "fix"):
            with self.subTest(kind=kind):
                self.assertIn(f"| research-md: {kind} |", body)
        self.assertIn("never the summary or `## Before you research`", flat(body))

    def test_charter_round_asks_it(self):
        sec = section(text(STORAGE), "The knowledge base")
        self.assertIsNotNone(sec)
        self.assertRegex(sec, r"\n7\. \*\*RESEARCH\.md\*\*")

    def test_landed_names_it(self):
        body = text(SKILLS / "research" / "references" / "run-record.md")
        landed = [ln for ln in body.splitlines() if ln.startswith("LANDED:")]
        self.assertEqual(len(landed), 1)
        self.assertIn(POINTER, landed[0])


class TestDocs(unittest.TestCase):
    def test_manifest_names_it(self):
        desc = json.loads(text(PLUGIN / ".claude-plugin" / "plugin.json"))["description"]
        self.assertIn("RESEARCH.md", desc)

    @unittest.skipUnless((REPO / ".claude-plugin" / "marketplace.json").is_file()
                         and (REPO / "README.md").is_file(), "not in the source repo")
    def test_marketplace_and_catalog_name_it(self):
        entries = [p for p in json.loads(text(REPO / ".claude-plugin" / "marketplace.json"))["plugins"]
                   if p["name"] == PLUGIN.name]
        self.assertEqual(len(entries), 1)
        self.assertIn("RESEARCH.md", entries[0]["description"])
        cell = f"| `{PLUGIN.name}` | **current** |"
        rows = [ln for ln in text(REPO / "README.md").splitlines()
                if ln.startswith("| ") and cell in ln]
        self.assertEqual(len(rows), 1)
        self.assertIn("RESEARCH.md", rows[0].split(cell)[0])


if __name__ == "__main__":
    unittest.main()
