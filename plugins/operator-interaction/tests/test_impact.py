"""Every view of a decision shows its impact.

Two halves:

- the decision page (`decision-page` skill): its template's data check and impact
  renderers, loaded from `assets/index.html` and run under node against
  `assets/cards.example.json` and broken copies of it;
- the decisions skill's worked examples: every list line carries its effect and its
  wait, and every card or block opens on its impact.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
PAGE = PLUGIN / "skills" / "decision-page" / "assets" / "index.html"
EXAMPLE = PLUGIN / "skills" / "decision-page" / "assets" / "cards.example.json"
DECISIONS = PLUGIN / "skills" / "decisions"
END_MARK = "/* ---- end of the page-free part"

NODE = shutil.which("node")


def setUpModule():
    # the page tests need node; without it they skip, and say so where the Check's
    # output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's impact tests "
              "(DecisionPageImpact) are skipped, so the page's check and renderers "
              "went untested", file=sys.stderr)

HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
const bad = check(d);
let views = [];
if (!bad.length) {
  CARDS = d.cards; REFS = d.refs || {};
  byN = new Map(CARDS.map(c => [String(c.n), c]));
  views = CARDS.map(c => ({n: c.n, tag: tagEffect(c), line: impactLine(c), table: impactTable(c)}));
}
process.stdout.write(JSON.stringify({bad, views}));
"""


def page_free_script():
    """The template's script up to the end-of-page-free-part marker: the helpers, the
    impact renderers and the data check, none of which touch the page."""
    html = PAGE.read_text()
    start = html.index("<script>") + len("<script>")
    end = html.index(END_MARK)
    return html[start:end]


def run_page(data):
    out = subprocess.run([NODE, "-e", page_free_script() + HARNESS],
                         input=json.dumps(data), capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def example():
    return json.loads(EXAMPLE.read_text())


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageImpact(unittest.TestCase):

    def test_example_passes_the_page_check(self):
        self.assertEqual(run_page(example())["bad"], [])

    def test_every_example_card_has_four_facets_and_a_short_effect(self):
        for c in example()["cards"]:
            imp = c["impact"]
            for k in ("effect", "wait", "reach", "undo"):
                self.assertTrue(isinstance(imp.get(k), str) and imp[k].strip(),
                                f"card {c['n']}: impact.{k}")
            # tag size: under about 10 words
            self.assertLessEqual(len(imp["effect"].split()), 12, f"card {c['n']}")
            self.assertNotIn("stakes", c, f"card {c['n']}: stakes is replaced by impact")
            # a decision with a one-way option names that option's undo, not only the rec's
            if c.get("warn"):
                self.assertIn("(b) none", imp["undo"], f"card {c['n']}")

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    def test_a_card_without_impact_is_refused(self):
        d = example()
        del d["cards"][0]["impact"]
        self.assert_refused(d, "card 41: impact needs")

    def test_each_facet_is_required_and_non_empty(self):
        for k in ("effect", "wait", "reach", "undo"):
            d = example()
            del d["cards"][1]["impact"][k]
            self.assert_refused(d, "card 42: impact needs")
            d = example()
            d["cards"][2]["impact"][k] = "  "
            self.assert_refused(d, "card 43: impact needs")

    def test_cost_is_optional_but_text(self):
        d = example()
        d["cards"][0]["impact"]["cost"] = "about 4 minutes of CI per merge"
        self.assertEqual(run_page(d)["bad"], [])
        d["cards"][0]["impact"]["cost"] = 4
        self.assert_refused(d, "card 41: impact needs")

    def test_blocks_rows_are_option_letters_with_text(self):
        d = example()
        d["cards"][0]["blocks"]["z"] = {"happens": "x", "undo": "y", "who": "z"}
        self.assert_refused(d, "card 41: blocks are keyed")
        d = example()
        del d["cards"][0]["blocks"]["a"]["who"]
        self.assert_refused(d, "card 41: blocks are keyed")
        d = example()
        d["cards"][1]["blocks"]["a"]["cost"] = ["twelve lines"]
        self.assert_refused(d, "card 42:")

    def test_a_warn_card_still_needs_every_row(self):
        d = example()
        del d["cards"][1]["blocks"]["b"]
        self.assert_refused(d, "a ⚠ one-way card needs blocks")

    def test_a_card_without_blocks_still_renders_its_table(self):
        d = example()
        self.assertNotIn("blocks", d["cards"][2])
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        table = res["views"][2]["table"]
        # (a), (b), then the Wait row; the option's impact text stands in as its effect
        self.assertEqual(table.count("<tr"), 1 + 3)
        self.assertIn("The site matches the logo", table)
        self.assertIn("—", table)

    def test_impact_line_order_and_tag_size(self):
        res = run_page(example())
        for v, c in zip(res["views"], example()["cards"]):
            line = v["line"]
            pos = [line.index(t) for t in ("→", "later:", "reach:", "undo:")]
            self.assertEqual(pos, sorted(pos), line)
            self.assertIn("→", v["tag"])
            self.assertNotIn("later:", v["tag"])
            # the tag shows the effect only; slugs render as plain text there
            self.assertIn(c["impact"]["effect"].split("[[")[0].strip()[:10], v["tag"])

    def test_impact_table_columns_rows_and_rec(self):
        res = run_page(example())
        table = res["views"][1]["table"]  # the ⚠ card
        heads = re.findall(r'<th scope="col">([^<]+)</th>', table)
        self.assertEqual(heads, ["Impact", "Effect", "Reach", "Undo", "Cost"])
        rows = re.findall(r"<tr[^>]*>", table)
        self.assertEqual(len(rows), 1 + 2 + 1)  # header, (a), (b), Wait
        self.assertIn('<tr class="isrec"><th scope="row">(a) ', table)
        self.assertIn("(z) Wait", table)
        self.assertIn("The first CI publish waits for this answer.".lower()[:20],
                      table.lower())
        self.assertIn("Twelve lines of redirect config to keep.", table)

    def test_impact_text_is_escaped(self):
        d = example()
        d["cards"][0]["impact"]["effect"] = '<img src=x onerror="alert(1)">'
        d["cards"][0]["impact"]["reach"] = "<script>x</script>"
        d["cards"][0]["blocks"]["b"]["cost"] = "<b>bold</b>"
        v = run_page(d)["views"][0]
        for html in (v["tag"], v["line"], v["table"]):
            self.assertNotIn("<img", html)
            self.assertNotIn("<script>", html)
        self.assertIn("&lt;img", v["tag"])
        self.assertIn("&lt;b&gt;bold", v["table"])

    def test_the_page_renders_impact_in_every_view(self):
        html = PAGE.read_text()
        hud = html[html.index("function renderHud"):html.index("function line(")]
        self.assertIn("tagEffect(c)", hud)
        cards = html[html.index("function renderCards"):html.index("function placeholderFor")]
        self.assertIn("impactLine(c)", cards)
        self.assertIn("tagEffect(c)", cards)
        full = html[html.index("function optionsInFull"):html.index("function renderCards")]
        self.assertIn("impactTable(c)", full)
        pop = html[html.index("function fillPop"):html.index("function place(")]
        self.assertIn("tagEffect(c)", pop)


LIST_LINE = re.compile(r"^- \*\*\d+ .+\?\*\* — ")
CARD_HEAD = re.compile(r"^\*\*\d+ — [^*]+\?\*\*")


class GalleryShowsImpact(unittest.TestCase):
    """The worked examples are what a rendering is checked against: each shows impact at
    its size."""

    def files(self):
        return [DECISIONS / "references" / "gallery.md",
                DECISIONS / "references" / "rendering.md"]

    def test_every_list_line_has_effect_and_wait(self):
        seen = 0
        for f in self.files():
            for n, line in enumerate(f.read_text().splitlines(), 1):
                if LIST_LINE.match(line):
                    seen += 1
                    self.assertIn(" → ", line, f"{f.name}:{n}")
                    self.assertIn("*later: ", line, f"{f.name}:{n}")
                    self.assertNotRegex(line, r"reversible, (narrow|wide)|one-way, narrow",
                                        f"{f.name}:{n}: a stakes word on a line")
        self.assertGreater(seen, 20)

    def test_every_card_and_block_opens_on_its_impact(self):
        seen = 0
        for f in self.files():
            lines = f.read_text().splitlines()
            for i, line in enumerate(lines):
                if not CARD_HEAD.match(line):
                    continue
                seen += 1
                j = i + 1
                while j < len(lines) and (not lines[j].strip()
                                          or lines[j].startswith("*While it waited")):
                    j += 1
                self.assertTrue(lines[j].startswith("**Impact:**")
                                or lines[j].startswith("| Impact |"),
                                f"{f.name}:{i + 1}: {line[:60]} is followed by {lines[j][:40]!r}")
        self.assertGreaterEqual(seen, 10)


if __name__ == "__main__":
    unittest.main()
