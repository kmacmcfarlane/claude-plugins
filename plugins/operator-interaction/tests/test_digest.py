"""The decision page's writer digest stays in step with the schema and the runner.

`skills/decision-page/references/writer-digest.md` is what a page's writer reads in place of
`references/cards-schema.md` and the example. It must name:

- every field the schema marks required (or required under a condition), at the top level
  and on a card;
- every lint key the pre-publish runner, `scripts/check_cards.js`, emits;
- the `follow` list exactly as the example holds it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "decision-page"
DIGEST = SKILL / "references" / "writer-digest.md"
SCHEMA = SKILL / "references" / "cards-schema.md"
RUNNER = SKILL / "scripts" / "check_cards.js"
EXAMPLE = SKILL / "assets" / "cards.example.json"


def section(text, heading):
    """The body of a `## heading` section, up to the next `## `."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise AssertionError("no section ## " + heading)
    return m.group(1)


def table_rows(body):
    """Each table row's cells, header and rule rows dropped."""
    rows = []
    for line in body.splitlines():
        if not line.startswith("|") or re.match(r"^\|[-| ]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows[1:] if rows else rows


def required_keys(schema_text, heading):
    """The keys whose Required cell is yes, or names a condition (when …, required when …)."""
    out = set()
    for cells in table_rows(section(schema_text, heading)):
        if len(cells) < 3:
            continue
        req = cells[2].lower()
        if req.startswith("yes") or req.startswith("when") or "required" in req:
            out.update(re.findall(r"`([A-Za-z]+)`", cells[0]))
    return out


def digest_keys(digest_text, heading):
    """The backticked keys in the first column of a digest table."""
    out = set()
    for cells in table_rows(section(digest_text, heading)):
        out.update(re.findall(r"`([A-Za-z-]+)`", cells[0]))
    return out


def runner_lint_keys(js):
    """The first word of every key a card's lints are said under (say("<key> …"), and each
    page-wide lint's own prefix ("lint: page: …"); a card's prefix is its number, not a key."""
    page_wide = set(re.findall(r'"lint: ([a-z]+): ', js)) - {"card"}
    return set(re.findall(r'\bsay\("([a-z-]+)', js)) | page_wide


class WriterDigest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.digest = DIGEST.read_text(encoding="utf-8")
        cls.schema = SCHEMA.read_text(encoding="utf-8")
        cls.js = RUNNER.read_text(encoding="utf-8")

    def test_names_every_required_top_level_field(self):
        need = required_keys(self.schema, "Top level")
        self.assertTrue({"layers", "follow", "cards"} <= need, need)
        missing = need - digest_keys(self.digest, "Top level")
        self.assertFalse(missing, "the digest's Top level table lacks: %s" % sorted(missing))

    def test_names_every_required_card_field(self):
        need = required_keys(self.schema, "A card")
        self.assertTrue({"n", "rev", "context", "impact", "tldr", "o", "norec", "blocks", "act"} <= need, need)
        missing = need - digest_keys(self.digest, "A card")
        self.assertFalse(missing, "the digest's A card table lacks: %s" % sorted(missing))

    def test_names_every_lint_the_runner_emits(self):
        emitted = runner_lint_keys(self.js)
        self.assertTrue({"shape", "id", "grow", "rec-only", "page"} <= emitted, emitted)
        listed = digest_keys(self.digest, "The checks")
        missing = emitted - listed
        self.assertFalse(missing, "the digest's lint table lacks the runner's: %s" % sorted(missing))
        stale = listed - emitted
        self.assertFalse(stale, "the digest's lint table names keys the runner no longer emits: %s" % sorted(stale))

    def test_follow_matches_the_example(self):
        m = re.search(r"```json\n(.*?)```", section(self.digest, "Top level"), re.S)
        self.assertIsNotNone(m, "the digest carries no follow block")
        follow = json.loads(EXAMPLE.read_text(encoding="utf-8"))["follow"]
        self.assertEqual(json.loads(m.group(1)), follow)


if __name__ == "__main__":
    unittest.main()
