"""Every view of a decision shows its impact.

Two halves:

- the decision page (`decision-page` skill): its template's data check and impact
  renderers, loaded from `assets/index.html` and run under node against
  `assets/cards.example.json` and broken copies of it;
- the decisions skill's worked examples: every list line carries its effect and its
  wait, and every card or block shows its impact right after its Context.

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
# what the page's isNone treats as saying nothing (trimmed, any case): the operator's rule of 2026-10-14
NONE = {"", "none", "none.", "n/a", "n/a.", "-", "–", "—"}


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
  CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
  byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
  views = CARDS.map(c => ({n: c.n, tag: tagEffect(c), line: impactLine(c), row: rowHtml(c),
                           more: Object.fromEntries(c.o.map(o => [o[0], optionDetail(c, o[0])])),
                           card: cardHtml(c)}));
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


def run_page(data, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + HARNESS],
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

    def test_every_example_card_has_three_facets_undo_where_one_way_and_a_short_effect(self):
        for c in example()["cards"]:
            imp = c["impact"]
            for k in ("effect", "wait", "reach"):
                self.assertTrue(isinstance(imp.get(k), str) and imp[k].strip(),
                                f"card {c['n']}: impact.{k}")
            # undo only where an option is one-way or costly (answer 260 (a)): the flagged rows
            flagged = [k for k, r in c.get("blocks", {}).items() if r.get("oneway")]
            self.assertEqual("undo" in imp, bool(flagged), f"card {c['n']}")
            for k in flagged:
                self.assertIn("(%s)" % k, imp["undo"], f"card {c['n']}")
            for k, r in c.get("blocks", {}).items():
                self.assertEqual("undo" in r, bool(r.get("oneway")), (c["n"], k))
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

    def test_undo_is_optional_but_text(self):
        d = example()
        del d["cards"][1]["impact"]["undo"]
        self.assertEqual(run_page(d)["bad"], [])
        d = example()
        d["cards"][0]["impact"]["undo"] = "(b) switch the pipeline off"
        self.assertEqual(run_page(d)["bad"], [])
        d["cards"][0]["impact"]["undo"] = ["(b) switch the pipeline off"]
        self.assert_refused(d, "card 41: impact needs effect, wait and reach as text (undo and cost optional, as text)")

    def test_each_facet_is_required_and_non_empty(self):
        for k in ("effect", "wait", "reach"):
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

    def test_a_card_without_blocks_still_shows_each_options_effect(self):
        d = example()
        del d["cards"][2]["blocks"]  # older data: blocks is required on a ⚠ card only
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        more = res["views"][2]["more"]
        # the option's impact text stands in as its effect; the facets it lacks are left out
        self.assertIn('<span class="lbl">Effect</span>The site matches the logo', more["b"])
        for k in ("a", "b"):
            self.assertNotIn(">Reach<", more[k])
            self.assertNotIn("—", more[k])

    def test_impact_line_order_and_tag_size(self):
        res = run_page(example())
        for v, c in zip(res["views"], example()["cards"]):
            line = v["line"]
            pos = [line.index(t) for t in ("→", "later:", "reach:", "undo:") if t != "undo:" or "undo" in c["impact"]]
            self.assertEqual(pos, sorted(pos), line)
            # one facet a line: a paragraph per facet given, no separator between them
            given = sum(1 for k in ("effect", "wait", "reach", "undo", "cost") if c["impact"].get(k))
            self.assertEqual(line.count("<p>"), given, line)
            self.assertNotIn(" · <i>", line)
            self.assertIn("→", v["tag"])
            self.assertNotIn("later:", v["tag"])
            # the tag shows the effect only; slugs render as plain text there
            self.assertIn(c["impact"]["effect"].split("[[")[0].strip()[:10], v["tag"])

    def test_each_options_more_carries_what_the_impact_table_did(self):
        # Options in full went (the operator, 2026-10-14): each row of its Impact table is in
        # its option's More, Effect, Reach, Undo, Cost in that order; the Wait row is the card's
        # Impact line (later:) and (z)'s More
        d = example()
        res = run_page(d)
        for v, c in zip(res["views"], d["cards"]):
            for k, row in c["blocks"].items():
                more = v["more"][k]
                # an Effect, Reach or Cost cell that is none is left out; Undo always shows
                cells = [(f, x) for f, x in (("Effect", "happens"), ("Reach", "who"), ("Undo", "undo"),
                                             ("Cost", "cost")) if x in row and (x == "undo" or row[x].strip().lower() not in NONE)]
                # a row flagged one-way marks its Undo
                lbl = lambda f: ('<span class="lbl owu">⚠ Undo</span>' if f == "Undo" and row.get("oneway")
                                 else '<span class="lbl">%s</span>' % f)
                pos = [more.index(lbl(f)) for f, _ in cells]
                if c.get("warn"):  # the one-way card's row comes before the option's text
                    self.assertLess(pos[-1], more.index('class="sec"'), (c["n"], k))
                self.assertEqual(pos, sorted(pos), (c["n"], k))
                for _, x in cells:
                    self.assertIn(row[x][:20], more, (c["n"], k, x))
            self.assertIn("<i>later:</i>", v["line"])
            self.assertIn('<span class="lbl">Wait</span>', v["more"]["z"])
            self.assertNotIn("Options in full", v["card"])
            self.assertNotIn("<table", v["card"])
        warn = res["views"][1]
        self.assertIn("The first CI publish waits for this answer.", warn["more"]["z"])
        self.assertIn("Twelve lines of redirect config to keep.", warn["more"]["a"])

    def test_impact_text_is_escaped(self):
        d = example()
        d["cards"][0]["impact"]["effect"] = '<img src=x onerror="alert(1)">'
        d["cards"][0]["impact"]["reach"] = "<script>x</script>"
        d["cards"][0]["blocks"]["b"]["cost"] = "<b>bold</b>"
        v = run_page(d)["views"][0]
        for html in (v["tag"], v["line"], v["more"]["b"]):
            self.assertNotIn("<img", html)
            self.assertNotIn("<script>", html)
        self.assertIn("&lt;img", v["tag"])
        self.assertIn("&lt;b&gt;bold", v["more"]["b"])

    def test_the_row_shows_the_rec_pill_and_the_effect_across_the_options(self):
        # the closed card's row (its summary) keeps the Effect across the options at tag size,
        # beside the rec pill (*Impact across the options on an answer page*; decision 335 open)
        for v in run_page(example())["views"]:
            self.assertEqual(row_problems(v), [], v["n"])
        # mutant: the row's effect read from the recommended option's blocks row
        mutant = page_free_script().replace(ROW_EFFECT, ROW_EFFECT_REC)
        self.assertNotEqual(mutant, page_free_script())
        v41 = run_page(example(), mutant)["views"][0]
        self.assertIn("the row does not show the Effect across the options", row_problems(v41))

    def test_the_page_renders_impact_in_every_view(self):
        # the open card, rendered: its Impact line, the effect on its row (its summary), and
        # each option's own effect in its More
        for v in run_page(example())["views"]:
            card = v["card"]
            self.assertIn('class="impline"', card, v["n"])
            self.assertIn(v["line"], card, v["n"])
            summary = card[:card.index("</summary>")]
            self.assertIn('class="eff"', summary, v["n"])
            for k, more in v["more"].items():
                self.assertIn(more, card, (v["n"], k))
                if k != "z":
                    self.assertIn('<span class="lbl">Effect</span>', more, (v["n"], k))


ROW_EFFECT = "const rowEffect=c=>tagEffect(c);"
ROW_EFFECT_REC = ("const rowEffect=c=>'<span class=\"eff\"><b>→</b>'"
                  "+esc(((c.blocks||{})[c.rec]||{}).happens||\"\")+'</span>';")


def row_problems(v):
    """A row without the rec pill (or its no-recommendation label) and the Effect at tag size."""
    out = []
    if v["tag"] not in v["row"]:
        out.append("the row does not show the Effect across the options")
    if 'class="pill rec"' not in v["row"] and 'class="pill none"' not in v["row"]:
        out.append("the row has no rec pill")
    return out


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

    def test_every_card_and_block_shows_its_impact_right_after_its_context(self):
        # the answer page's order: the decision line (title, What), Context, then the
        # impact; a Context section is a line, or a heading over bullets (a block)
        seen = 0
        for f in self.files():
            lines = f.read_text().splitlines()
            for i, line in enumerate(lines):
                if not CARD_HEAD.match(line):
                    continue
                seen += 1
                j = i + 1
                in_context = False
                while j < len(lines):
                    x = lines[j]
                    if x.startswith("**Context:**"):
                        in_context = True
                    elif in_context and x.startswith(("- ", "  - ")):
                        pass  # a block's Context bullets
                    elif x.strip() and not x.startswith(("*While it waited", "**What:**")):
                        break
                    else:
                        in_context = in_context and bool(x.strip())
                    j += 1
                self.assertTrue(lines[j].startswith("**Impact:**")
                                or lines[j].startswith("| Impact |"),
                                f"{f.name}:{i + 1}: {line[:60]} is followed by {lines[j][:40]!r}")
        self.assertGreaterEqual(seen, 10)


if __name__ == "__main__":
    unittest.main()
