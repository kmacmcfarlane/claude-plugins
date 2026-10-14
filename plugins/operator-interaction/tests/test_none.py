"""A part with nothing to say is not shown; Options in full is gone (the operator, 2026-10-14).

The operator's words: the Options in full section repeated each option's inline detail, so it
goes; and a sub-section that is empty or none is not displayed (a decision with no
dependencies, an Impact whose cost is none). The decision page (`decision-page` skill) does
both with one helper, `isNone`, loaded from `assets/index.html` and run under node against
copies of `assets/cards.example.json`. The fields whose none is itself a statement (the
required Impact facets, the basis word, the rec line's unknown) stay shown.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import sys
import unittest

from test_impact import NODE, PAGE, example
from test_depth import card, node, run_page


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the decision page's none tests (DecisionPageNone) "
              "are skipped, so hiding empty or none parts went untested", file=sys.stderr)


NONE_HARNESS = r"""
const xs = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(xs.map(isNone)));
"""


def panes(html):
    return re.findall(r'<details class="pane"(?: open)?><summary>([^<]+)</summary>', html)


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageNone(unittest.TestCase):

    def test_is_none_reads_empty_missing_and_none_words(self):
        nones = [None, "", "  ", "none", "None", " NONE. ", "n/a", "N/A.", "Nothing.", "-", "—",
                 [], ["", "none"], {"t": "None."}]
        somes = ["(b) none — lost ranking does not come back", "Nothing to undo.", "no",
                 "none of the above", ["none", "one step"], {"h": "none", "b": ["x"]}, {"t": "x"}]
        got = node(NONE_HARNESS, nones + somes)
        self.assertEqual(got, [True] * len(nones) + [False] * len(somes))

    def test_one_helper_used_everywhere(self):
        html = PAGE.read_text()
        self.assertEqual(html.count("const NONE_WORDS="), 1)
        self.assertEqual(html.count("const isNone="), 1)
        free = html[html.index("<script>"):html.index("/* ---- end of the page-free part")]
        for fn in ("const facetShown=", "function line(", "function parts(", "function optionDetail(",
                   "function cardHtml("):
            body = free[free.index(fn):]
            body = body[:body.index("\n}") if fn.startswith("function") else body.index("\n")]
            self.assertTrue("shown(" in body or "isNone(" in body or "facetShown(" in body, fn)

    def test_options_in_full_is_gone_from_the_template(self):
        html = PAGE.read_text()
        self.assertNotIn("Options in full", html)
        self.assertNotIn("optionsInFull", html)
        self.assertNotIn("impactTable", html)
        self.assertNotIn("<table", html)

    def test_no_dep_no_dependencies_fold(self):
        for dep in (None, "", "none", "None."):
            d = example()
            c = d["cards"][1]
            if dep is None:
                c.pop("dep")
            else:
                c["dep"] = dep
            h = card(run_page(d), 42)["html"]
            self.assertEqual(panes(h), ["Background", "Evidence and unknowns"], dep)
            self.assertNotIn("depends on:", h, dep)
            self.assertNotIn("Depends on", h, dep)
            self.assertNotIn("nothing on this page", h, dep)
        # with levels but no summary, a placeholder holds its place, as the Evidence's does
        d = example()
        d["cards"][1]["dep"] = "none"
        d["cards"][1]["detail"]["dep"] = ["Waits on the CI publish decision.",
                                          [{"h": "Waits on", "b": ["The CI publish decision."]}]]
        h = card(run_page(d), 42)["html"]
        self.assertIn("Dependencies", panes(h))
        self.assertIn("Not summarised: more detail shows what it depends on.", h)

    def test_a_none_cost_is_not_shown_but_a_required_facet_is(self):
        for cost in ("none", "None.", "n/a", " "):
            d = example()
            d["cards"][0]["impact"]["cost"] = cost
            d["cards"][0]["impact"]["undo"] = "none"
            c = card(run_page(d), 41)
            self.assertNotIn("<i>cost:</i>", c["parts"]["imp"][0], cost)
            # undo: none says the decision cannot be undone: a required facet stays
            self.assertIn("<i>undo:</i> none", c["parts"]["imp"][0], cost)
        # the levels too: a none cost facet at medium and high is left out
        d = example()
        for lvl in d["cards"][0]["detail"]["impact"]:
            lvl["cost"] = "none"
        c = card(run_page(d), 41)
        self.assertNotIn("<i>cost:</i>", c["parts"]["imp"][1])
        self.assertNotIn('<h4 class="lvh">Cost</h4>', c["parts"]["imp"][2])

    def test_a_none_blocks_cell_is_not_shown(self):
        d = example()
        row = d["cards"][1]["blocks"]["b"]
        row["cost"] = "None."
        row["who"] = "n/a"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        more = card(res, 42)["more"]["b"]
        self.assertNotIn(">Cost<", more)
        self.assertNotIn(">Reach<", more)
        self.assertIn('<span class="lbl">Effect</span>', more)
        self.assertIn('<span class="lbl">Undo</span>', more)

    def test_a_none_unknown_leaves_the_fold_and_stays_on_the_rec_line(self):
        d = example()
        res = run_page(d)
        c43 = card(res, 43)  # unknown: none in the example
        fold = c43["html"][c43["html"].index("<summary>Evidence and unknowns</summary>"):]
        self.assertNotIn('<span class="lbl">Unknown</span>', fold)
        self.assertIn('<span class="lbl">Basis</span>', fold)
        self.assertIn(" · unknown: none</p>", c43["parts"]["rec"][0])
        # a real unknown shows in both
        c41 = card(res, 41)
        self.assertIn('<span class="lbl">Unknown</span>whether anyone publishes', c41["html"])

    def test_empty_or_none_evidence_is_no_part(self):
        for ev in ("none", "N/A"):
            d = example()
            d["cards"][2]["evidence"] = ev
            h = card(run_page(d), 43)["html"]
            self.assertNotIn('data-sec="ev"', h)
            self.assertNotIn("N/A", h)

    def test_none_flat_lines_and_one_lines_are_not_shown(self):
        d = example()
        c = d["cards"][2]
        c["ifunanswered"] = "None."
        c["ifleft"] = "n/a"
        c["o"][0][4] = "none"
        h = card(run_page(d), 43)["html"]
        self.assertNotIn("If unanswered:", h)
        self.assertNotIn("If left:", h)
        lab = re.search(r'<label class="optl"><input type="radio" name="d43" id="d43-a".*?</label>', h).group(0)
        self.assertNotIn('class="oi"', lab)

    def test_a_one_way_card_opens_each_options_more(self):
        res = run_page(example())
        h = card(res, 42)["html"]
        for k in ("a", "b"):
            self.assertIn('<div class="odet" id="d42-%s-more">' % k, h)
        self.assertIn('<div class="odet" id="d42-z-more" hidden>', h)
        self.assertIn('<div class="odet" id="d41-a-more" hidden>', card(res, 41)["html"])


if __name__ == "__main__":
    unittest.main()
