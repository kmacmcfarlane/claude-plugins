"""The decision page's writer digest stays in step with the schema and the runner.

`skills/decision-page/references/writer-digest.md` is what a page's writer reads in place of
`references/cards-schema.md` and the example. It must carry:

- every key of the schema's Top level, A page card and An excerpt tables, and of the card
  record's A card and An option tables (the `decisions` skill's `references/card-record.md`;
  but `what`, older data only), each with its own Required cell;
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
RECORD = SKILL.parent / "decisions" / "references" / "card-record.md"
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
    "words in an option's effect, at or under which mech fires": r"\bMECH_MIN = (\d+)",
    "words in the Background fold's summary": r"\bBGSUM_CAP = (\d+)",
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
        cls.record = RECORD.read_text(encoding="utf-8")
        cls.js = RUNNER.read_text(encoding="utf-8")
        cls.example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_top_level_fields(self):
        self.assertEqual(required_problems(self.schema, self.digest, "Top level"), [])
        self.assertTrue({"format", "page", "layers", "follow", "cards", "refs"}
                        <= set(keyed(section(self.schema, "Top level"), 2)))

    def test_page_card_fields(self):
        # a page card is a card record plus L and dep, the page-only fields
        self.assertEqual(required_problems(self.schema, self.digest, "A page card"), [])
        self.assertEqual(set(keyed(section(self.schema, "A page card"), 2)), {"L", "dep"})

    def test_card_fields(self):
        # the card and option tables are the record's (card-record.md), Required cells and all
        self.assertEqual(required_problems(self.record, self.digest, "A card"), [])
        self.assertGreaterEqual(len(keyed(section(self.record, "A card"), 2)), 26)
        self.assertEqual(required_problems(self.record, self.digest, "An option"), [])
        self.assertGreaterEqual(len(keyed(section(self.record, "An option"), 2)), 15)

    def test_the_v5_fields_are_listed(self):
        card = keyed(section(self.digest, "A card"), 1)
        self.assertEqual(card.get("format"), "to render")
        self.assertEqual(card.get("open"), "optional")
        self.assertEqual(card.get("label"), "optional")
        # the Assumptions fold's field (A1): optional, linted on a card with a recommendation
        self.assertEqual(card.get("assume"), "optional; a card with a recommendation and none is linted")
        gone = self.digest.replace("| `assume` | optional;", "| assume | optional;")
        self.assertIn("A card: `assume` missing", required_problems(self.record, gone, "A card"))
        self.assertNotIn("o", card)
        self.assertNotIn("blocks", card)
        self.assertNotIn("warn", card)
        self.assertNotIn("unknown", card)
        self.assertEqual(keyed(section(self.digest, "An option"), 1).get("effect"), "to render, but on (z)")
        # the flag has the decisions skill's ⚠ undo: scope, one-way or costly, in both
        self.assertIn("`true` on each option one-way or costly to undo", self.digest)
        self.assertIn("`true` on an option one-way or costly to undo", self.record)
        for text in (self.digest, self.record):
            self.assertNotIn("costly but reversible", text)
        gone = self.digest.replace("| `label` | optional |", "| label | optional |")
        self.assertIn("A card: `label` missing", required_problems(self.record, gone, "A card"))
        # the option's inline Pros and Cons (F4), owed by a new card but on (z), and the points in full
        option = keyed(section(self.digest, "An option"), 1)
        for k in ("pro", "con"):
            self.assertEqual(option.get(k), "of a new card, but on (z)")
        for k in ("pros", "cons"):
            self.assertEqual(option.get(k), "optional")
        gone = self.digest.replace("| `con` | of a new card, but on (z) |", "| con | of a new card, but on (z) |")
        self.assertIn("An option: `con` missing", required_problems(self.record, gone, "An option"))
        req = self.digest.replace("| `pro` | of a new card, but on (z) |", "| `pro` | optional |")
        self.assertTrue(required_problems(self.record, req, "An option"))
        # the page's label before a non-recommended option's line is if chosen: in both
        for text in (self.digest, self.record):
            self.assertNotIn("not recommended because:", text)

    def test_card_field_mutations(self):
        gone = self.digest.replace("| `basis` | to render |", "| basis | to render |")
        self.assertIn("A card: `basis` missing",
                      required_problems(self.record, gone, "A card"))
        req = self.digest.replace("| `norec` | to render when `rec` is null |", "| `norec` | optional |")
        self.assertNotEqual(req, self.digest)
        self.assertTrue(required_problems(self.record, req, "A card"))
        opt = self.digest.replace("| `effect` | to render, but on (z) |", "| `effect` | optional |")
        self.assertNotEqual(opt, self.digest)
        self.assertTrue(required_problems(self.record, opt, "An option"))
        top = self.digest.replace("| `refs` | no |", "| `refs` | yes |")
        self.assertTrue(required_problems(self.schema, top, "Top level"))
        page = self.digest.replace("| `L` | yes |", "| L | yes |")
        self.assertIn("A page card: `L` missing", required_problems(self.schema, page, "A page card"))
    def test_excerpt_fields(self):
        self.assertEqual(required_problems(self.schema, self.digest, "An excerpt"), [])
        self.assertEqual(set(keyed(section(self.schema, "An excerpt"), 2)), {"text", "lang", "src"})

    def test_excerpt_field_mutations(self):
        gone = self.digest.replace("| `src` | no |", "| src | no |")
        self.assertIn("An excerpt: `src` missing",
                      required_problems(self.schema, gone, "An excerpt"))
        req = self.digest.replace("| `text` | yes |", "| `text` | no |")
        self.assertTrue(required_problems(self.schema, req, "An excerpt"))

    def test_lints(self):
        emitted = runner_lints(self.js)
        self.assertTrue({"shape", "id", "grow", "rec-only", "page", "refs"} <= set(emitted))
        self.assertEqual(emitted["shape"], {"shape:"})
        self.assertEqual(emitted["rec-only"], {"impact:"})
        # rule 259 on the page (7434 S1): the system lint prints under the Impact's start
        self.assertEqual(emitted["process"], {"impact:"})
        # rule 268 on the page (7434 S2): the mechanism lint too
        self.assertEqual(emitted["mech"], {"impact:"})
        # rule 263 on the page (7434 S4): the bundle lint is page-wide
        self.assertEqual(emitted["group"], {"page:"})
        self.assertEqual(emitted["id"], {""})
        self.assertEqual(lint_problems(self.js, self.digest), [])

    def test_lint_mutations(self):
        new_key = self.js.replace('say("bg", "depth:', 'say("bgx", "depth:', 1)
        self.assertIn("lint `bgx` missing", lint_problems(new_key, self.digest))
        start = self.digest.replace("| `ev` | `depth:` |", "| `ev` | — |")
        self.assertTrue(lint_problems(self.js, start))
        stale = self.digest.replace("| `key` |", "| `keys` |")
        self.assertIn("lint `keys` not emitted", lint_problems(self.js, stale))
        # the one-way lint key (answer 260 (a), the page's row flag): its row, and its start
        self.assertEqual(runner_lints(self.js)["oneway"], {"oneway:"})
        gone = self.digest.replace("| `oneway` | `oneway:` |", "| oneway | `oneway:` |")
        self.assertIn("lint `oneway` missing", lint_problems(self.js, gone))
        moved = self.digest.replace("| `oneway` | `oneway:` |", "| `oneway` | `depth:` |")
        self.assertTrue(lint_problems(self.js, moved))
        # the Background fold's summary lint (answer 338): its row, and its start
        self.assertEqual(runner_lints(self.js)["bgsum"], {"shape:"})
        gone = self.digest.replace("| `bgsum` | `shape:` |", "| bgsum | `shape:` |")
        self.assertIn("lint `bgsum` missing", lint_problems(self.js, gone))
        moved = self.digest.replace("| `bgsum` | `shape:` |", "| `bgsum` | `depth:` |")
        self.assertTrue(lint_problems(self.js, moved))
        # the Assumptions fold's lint (A1): its row, and its start
        self.assertEqual(runner_lints(self.js)["assume"], {"depth:"})
        gone = self.digest.replace("| `assume` | `depth:` |", "| assume | `depth:` |")
        self.assertIn("lint `assume` missing", lint_problems(self.js, gone))
        moved = self.digest.replace("| `assume` | `depth:` |", "| `assume` | `shape:` |")
        self.assertTrue(lint_problems(self.js, moved))
        # the trade-offs lint (F4): its row, and its start
        self.assertEqual(runner_lints(self.js)["tradeoffs"], {"shape:"})
        gone = self.digest.replace("| `tradeoffs` | `shape:` |", "| tradeoffs | `shape:` |")
        self.assertIn("lint `tradeoffs` missing", lint_problems(self.js, gone))
        moved = self.digest.replace("| `tradeoffs` | `shape:` |", "| `tradeoffs` | `depth:` |")
        self.assertTrue(lint_problems(self.js, moved))

    def test_thresholds(self):
        self.assertEqual(threshold_problems(self.js, self.digest), [])

    def test_threshold_mutations(self):
        for old, new in [("TERSE = 14", "TERSE = 15"), ("MEDIUM_CAP = 6", "MEDIUM_CAP = 7"),
                         ("cw > 60", "cw > 61"), ("all > 1350", "all > 1400"),
                         ("cs > 2", "cs > 3"), ("c.tldr.length > 2", "c.tldr.length > 3"),
                         ("MECH_MIN = 4", "MECH_MIN = 5"), ("BGSUM_CAP = 25", "BGSUM_CAP = 26")]:
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
