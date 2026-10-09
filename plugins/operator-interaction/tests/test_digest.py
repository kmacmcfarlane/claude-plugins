"""The decision page's writer digest stays in step with the schema and the runner.

`skills/decision-page/references/writer-digest.md` is what a page's writer reads in place of
`references/cards-schema.md` and the example. It must carry:

- every key of the schema's Top level and A card tables (but `what`, older data only), each
  with the schema's own Required cell;
- every lint key the pre-publish runner, `scripts/check_cards.js`, emits, and none it does
  not, each with the start its printed line has (`shape:`, `impact:`, `depth:`, `page:` or
  none);
- the runner's thresholds, at the runner's values;
- the `follow` list exactly as the example holds it.

Each check is a function returning its problems; each is run on the real files (no problems)
and on a mutated copy (a problem), so a check that cannot fail does not pass for one.

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

# the card keys the digest leaves out on purpose
SKIPPED = {"what"}
# the page-wide lints print under "lint: page:", whatever their key
PAGE_WIDE_START = "page:"
# a digest threshold row -> the runner's value, found by this pattern in check_cards.js
THRESHOLDS = {
    "words in a summary or medium bullet": r"\bTERSE = (\d+)",
    "sub-bullets on one bullet": r"\bSUB_CAP = (\d+)",
    "bullets in a medium level": r"\bMEDIUM_CAP = (\d+)",
    "sentences in Context's summary": r"\bcs > (\d+)",
    "words in Context's summary": r"\bcw > (\d+)",
    "bullets in the TLDR": r"\bc\.tldr\.length > (\d+)",
    "words in a summary Impact facet": r"words\(c\.impact\[k\]\) > (\d+)",
    "words in the card in all": r"\ball > (\d+)",
}


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
        # the first cells hold no pipe; a later one may (a code span), so split three times
        rows.append([c.strip() for c in line.strip().strip("|").split("|", 3)])
    return rows[1:]


def keyed(body, col):
    """{key: the cell in column col}, for each row whose first cell is one backticked key."""
    out = {}
    for cells in table_rows(body):
        m = re.fullmatch(r"`([A-Za-z-]+)`", cells[0])
        if m:
            out[m.group(1)] = cells[col] if col < len(cells) else None
    return out


def required_problems(schema, digest, heading):
    """A schema key the digest lacks, or whose Required cell differs."""
    want = {k: v for k, v in keyed(section(schema, heading), 2).items() if k not in SKIPPED}
    have = keyed(section(digest, heading), 1)
    out = []
    for k, req in want.items():
        if k not in have:
            out.append("%s: `%s` missing" % (heading, k))
        elif have[k] != req:
            out.append("%s: `%s` Required is %r, the schema's %r" % (heading, k, have[k], req))
    return out


def runner_lints(js):
    """{lint key: the set of starts its lines print}. A card lint's key is the first word of
    say("<key> …"); its start is the second argument's leading "word:", or "" for none."""
    out = {}
    for m in re.finditer(r'\bsay\("([a-z-]+)[^"]*"(?:\s*\+[^,]*)?,\s*("([a-z-]+): )?', js):
        out.setdefault(m.group(1), set()).add(m.group(3) + ":" if m.group(3) else "")
    for k in set(re.findall(r'"lint: ([a-z]+): ', js)) - {"card"}:
        out.setdefault(k, set()).add(PAGE_WIDE_START)
    # the page-wide lints' own keys print under the page's start too
    page_say = re.search(r"function pageIds\(.*?\n}\n", js, re.S)
    for k in re.findall(r'\bsay\("([a-z-]+)', page_say.group(0) if page_say else ""):
        out[k] = {PAGE_WIDE_START}
    return out


def lint_problems(js, digest):
    """A runner key the digest lacks or that the runner no longer emits, or a wrong start."""
    emitted = runner_lints(js)
    listed = keyed(section(digest, "The checks"), 1)
    out = ["lint `%s` missing" % k for k in sorted(set(emitted) - set(listed))]
    out += ["lint `%s` not emitted" % k for k in sorted(set(listed) - set(emitted))]
    for k in sorted(set(emitted) & set(listed)):
        starts = emitted[k]
        if len(starts) != 1:
            out.append("lint `%s` prints under several starts: %s" % (k, sorted(starts)))
            continue
        want = next(iter(starts))
        got = listed[k].strip("`")
        if (got if got != "—" else "") != want:
            out.append("lint `%s` starts %r, the digest says %r" % (k, want, listed[k]))
    return out


def threshold_problems(js, digest):
    """A threshold the digest gives at another value than the runner, or not at all."""
    rows = {c[0]: c[1] for c in table_rows(section(digest, "The runner's thresholds"))}
    out = []
    for name, pattern in THRESHOLDS.items():
        m = re.search(pattern, js)
        if not m:
            out.append("the runner has no %r (%s)" % (name, pattern))
        elif rows.get(name) != m.group(1):
            out.append("%r is %s in the runner, %r in the digest"
                       % (name, m.group(1), rows.get(name)))
    return out


def follow_problems(digest, example):
    m = re.search(r"```json\n(.*?)```", section(digest, "Top level"), re.S)
    if not m:
        return ["the digest carries no follow block"]
    return [] if json.loads(m.group(1)) == example["follow"] else ["follow differs"]


class WriterDigest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.digest = DIGEST.read_text(encoding="utf-8")
        cls.schema = SCHEMA.read_text(encoding="utf-8")
        cls.js = RUNNER.read_text(encoding="utf-8")
        cls.example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_top_level_fields(self):
        self.assertEqual(required_problems(self.schema, self.digest, "Top level"), [])
        self.assertTrue({"page", "layers", "follow", "cards", "refs"}
                        <= set(keyed(section(self.schema, "Top level"), 2)))

    def test_card_fields(self):
        self.assertEqual(required_problems(self.schema, self.digest, "A card"), [])
        self.assertGreaterEqual(len(keyed(section(self.schema, "A card"), 2)), 26)

    def test_card_field_mutations(self):
        gone = self.digest.replace("| `basis` | yes |", "| basis | yes |")
        self.assertIn("A card: `basis` missing",
                      required_problems(self.schema, gone, "A card"))
        req = self.digest.replace("| `norec` | when `rec` is null |", "| `norec` | no |")
        self.assertTrue(required_problems(self.schema, req, "A card"))
        top = self.digest.replace("| `refs` | no |", "| `refs` | yes |")
        self.assertTrue(required_problems(self.schema, top, "Top level"))

    def test_lints(self):
        emitted = runner_lints(self.js)
        self.assertTrue({"shape", "id", "grow", "rec-only", "page", "refs"} <= set(emitted))
        self.assertEqual(emitted["shape"], {"shape:"})
        self.assertEqual(emitted["rec-only"], {"impact:"})
        self.assertEqual(emitted["id"], {""})
        self.assertEqual(lint_problems(self.js, self.digest), [])

    def test_lint_mutations(self):
        new_key = self.js.replace('say("bg", "depth:', 'say("bgx", "depth:', 1)
        self.assertIn("lint `bgx` missing", lint_problems(new_key, self.digest))
        start = self.digest.replace("| `ev` | `depth:` |", "| `ev` | — |")
        self.assertTrue(lint_problems(self.js, start))
        stale = self.digest.replace("| `key` |", "| `keys` |")
        self.assertIn("lint `keys` not emitted", lint_problems(self.js, stale))

    def test_thresholds(self):
        self.assertEqual(threshold_problems(self.js, self.digest), [])

    def test_threshold_mutations(self):
        for old, new in [("TERSE = 14", "TERSE = 15"), ("MEDIUM_CAP = 6", "MEDIUM_CAP = 7"),
                         ("cw > 60", "cw > 61"), ("all > 1350", "all > 1400"),
                         ("cs > 2", "cs > 3"), ("c.tldr.length > 2", "c.tldr.length > 3")]:
            with self.subTest(old=old):
                self.assertIn(old, self.js)
                self.assertTrue(threshold_problems(self.js.replace(old, new), self.digest))
        facet = self.digest.replace("| words in a summary Impact facet | 16 |",
                                    "| words in a summary Impact facet | 20 |")
        self.assertTrue(threshold_problems(self.js, facet))
        for row in ("| sentences in Context's summary | 2 |", "| bullets in the TLDR | 2 |"):
            with self.subTest(row=row):
                self.assertIn(row, self.digest)
                cut = self.digest.replace(row, row.replace("| 2 |", "| 3 |"))
                self.assertTrue(threshold_problems(self.js, cut))

    def test_follow(self):
        self.assertEqual(follow_problems(self.digest, self.example), [])
        self.assertTrue(follow_problems(self.digest.replace('"Anything I should weigh?"',
                                                            '"Anything?"'), self.example))


if __name__ == "__main__":
    unittest.main()
