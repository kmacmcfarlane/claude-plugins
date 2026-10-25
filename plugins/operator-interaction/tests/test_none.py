"""A part with nothing to say is not shown; Options in full is gone (the operator, 2026-10-14).

The operator's words: the Options in full section repeated each option's inline detail, so it
goes; and a sub-section that is empty or none is not displayed (a decision with no
dependencies, an Impact whose cost is none). The decision page (`decision-page` skill) does
both with one helper, `isNone`, loaded from `assets/index.html` and run under node against
copies of `assets/cards.example.json`. The fields whose none is itself a statement (the
required Impact facets, an option's undo, the basis word) stay shown. An empty or none `open`
list has no Open questions fold.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import sys
import unittest

from test_impact import NODE, PAGE, example
from test_depth import card, node, run_page
from test_context import runner


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the decision page's none tests (DecisionPageNone) "
              "are skipped, so hiding empty or none parts went untested", file=sys.stderr)


NONE_HARNESS = r"""
const xs = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(xs.map(isNone)));
"""


def panes(html):
    return re.findall(r'<details class="pane"(?: open)?><summary>([^<]+?)(?: <span class="fsum">.*?</span>)?</summary>', html)


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageNone(unittest.TestCase):

    def test_is_none_reads_empty_missing_and_none_words(self):
        nones = [None, "", "  ", "none", "None", " NONE. ", "n/a", "N/A.", "-", "—",
                 [], ["", "none"], {"t": "None."}]
        somes = ["(b) none — lost ranking does not come back", "Nothing to undo.", "no", "Nothing.",
                 "none of the above", ["none", "one step"], {"h": "none", "b": ["x"]}, {"t": "x"}]
        got = node(NONE_HARNESS, nones + somes)
        self.assertEqual(got, [True] * len(nones) + [False] * len(somes))

    def test_one_helper_used_everywhere(self):
        html = PAGE.read_text()
        self.assertEqual(html.count("const NONE_WORDS="), 1)
        self.assertEqual(html.count("const isNone="), 1)
        free = html[html.index("<script>"):html.index("/* ---- end of the page-free part")]
        for fn in ("const facetShown=", "function line(", "function parts(", "function optionDetail(",
                   "function cardHtml(", "const openFold=", "const assumeOf=", "const assumeFold="):
            body = free[free.index(fn):]
            body = body[:body.index("\n}") if fn.startswith("function") else body.index("};\n")]
            self.assertTrue(any(x in body for x in ("shown(", "(shown)", "isNone(", "facetShown(")), fn)

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
            self.assertEqual(panes(h), ["Background"], dep)
            self.assertNotIn("depends on:", h, dep)
            self.assertNotIn("Depends on", h, dep)
            self.assertNotIn("nothing on this page", h, dep)
        # with levels but no summary, a placeholder holds its place, as the evidence's does
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

    def test_a_none_option_facet_is_not_shown(self):
        d = example()
        o = d["cards"][2]["options"][1]
        o["cost"] = "None."
        o["reach"] = "n/a"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        more = card(res, 43)["more"]["b"]
        self.assertNotIn(">Cost<", more)
        self.assertNotIn(">Reach<", more)
        self.assertIn('<span class="lbl">Effect</span>', more)

    def test_a_none_undo_always_shows(self):
        # on a one-way card an option's Undo decides the read-back: none there says it cannot be undone
        for undo in ("None.", "none", "—"):
            d = example()
            d["cards"][1]["options"][0]["undo"] = undo
            more = card(run_page(d), 42)["more"]["a"]
            self.assertIn('<span class="lbl">Undo</span>' + undo, more, undo)

    def test_a_one_way_more_shows_its_facets_first(self):
        res = run_page(example())
        more = card(res, 42)["more"]["b"]
        pos = [more.index(f) for f in ('<span class="lbl">Effect</span>', '<span class="lbl">Reach</span>',
                                       '<span class="lbl owu">⚠ Undo</span>', '<span class="lbl">Cost</span>')]
        self.assertEqual(pos, sorted(pos))
        self.assertLess(pos[-1], more.index('class="sec"'))
        # any other card: the text first, then the facets
        more = card(res, 41)["more"]["a"]
        self.assertLess(more.index('class="sec"'), more.index('<span class="lbl">Effect</span>'))

    def test_a_one_way_cards_option_with_a_blank_reach_or_effect_is_refused(self):
        for f, want in (("effect", "card 42: (b) needs its effect"), ("reach", "card 42: (b) needs its reach")):
            d = example()
            d["cards"][1]["options"][1][f] = "  "
            self.assertIn(want, " | ".join(run_page(d)["bad"]), f)
        # the undo is required only on an option flagged one-way
        for undo in ("  ", None):
            d = example()
            if undo is None:
                del d["cards"][1]["options"][1]["undo"]
            else:
                d["cards"][1]["options"][1]["undo"] = undo
            self.assertEqual(run_page(d)["bad"], ["card 42: (b) is flagged one-way (oneway: true) but has no "
                                                  "undo: say how it is reversed and at what cost, or that it "
                                                  "cannot be and why"], undo)
        # a blank reach on any other card is not refused (it is just not shown)
        d = example()
        d["cards"][0]["options"][1]["reach"] = ""
        self.assertEqual(run_page(d)["bad"], [])

    def test_no_open_questions_no_fold(self):
        for v in (None, [], ["none"], ["", "n/a"]):
            d = example()
            if v is None:
                d["cards"][0].pop("open")
            else:
                d["cards"][0]["open"] = v
            h = card(run_page(d), 41)["html"]
            self.assertNotIn("Open questions", h, v)
        # card 43 has none: no fold
        self.assertNotIn("Open questions", card(run_page(example()), 43)["html"])

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
        c["options"][0]["line"] = "none"
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


def unflagged_warn_page():
    """A ⚠ card with undos on its options and none flagged one-way: the shape an upgraded older ⚠ card takes."""
    d = example()
    c = d["cards"][1]
    c["impact"]["undo"] = "(a) remove the redirect lines; (b) none — lost search ranking does not come back"
    c["options"][0]["undo"] = "Remove the redirect lines; nothing else changes."
    del c["options"][1]["oneway"]
    return d


@unittest.skipUnless(NODE, "node is not installed")
class OneWayOptions(unittest.TestCase):
    """Undo is optional on an option; an option flagged `oneway: true` needs its undo; a ⚠ card with no option
    flagged (an upgraded older ⚠ card) still shows (answer 260 (a), the page's one-way flag)."""

    def test_an_unflagged_warn_card_passes_the_page_check(self):
        res = run_page(unflagged_warn_page())
        self.assertEqual(res["bad"], [])
        # its undos show as written, with the plain label: nothing marks them one-way
        more = card(res, 42)["more"]
        for k in ("a", "b"):
            self.assertIn('<span class="lbl">Undo</span>', more[k], k)
            self.assertNotIn("⚠ Undo", more[k], k)
        self.assertIn("<p><i>undo:</i> (a) remove", card(res, 42)["parts"]["imp"][0])

    def test_an_unflagged_warn_card_lints_and_is_not_refused(self):
        code, out, _ = runner(unflagged_warn_page())
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 42: oneway: a ⚠ one-way card has no option flagged one-way: "
                      "set oneway: true, with its undo, on each option one-way or costly to undo", out)
        # the example, flagged, is clean
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_a_flagged_option_needs_the_impacts_undo(self):
        d = example()
        del d["cards"][1]["impact"]["undo"]
        self.assertEqual(run_page(d)["bad"], [])
        out = runner(d)[1]
        self.assertIn("lint: card 42: oneway: (b) is flagged one-way but the Impact carries no undo", out)
        # a narrow decision with an option costly to undo: no ⚠ label, that option flagged, the same rules
        d = example()
        d["cards"][2]["options"][1]["oneway"] = True
        self.assertEqual(run_page(d)["bad"], ["card 43: (b) is flagged one-way (oneway: true) but has no "
                                              "undo: say how it is reversed and at what cost, or that it "
                                              "cannot be and why"])
        d["cards"][2]["options"][1]["undo"] = "Retake every guide screenshot, about an hour."
        self.assertEqual(run_page(d)["bad"], [])
        self.assertIn("lint: card 43: oneway: (b) is flagged one-way but the Impact carries no undo",
                      runner(d)[1])

    def test_the_flag_is_true_or_false(self):
        d = example()
        d["cards"][1]["options"][1]["oneway"] = "yes"
        self.assertIn("card 42: (b) oneway must be true or false", run_page(d)["bad"])
        d["cards"][1]["options"][1]["oneway"] = False
        self.assertEqual(run_page(d)["bad"], [])
        d = example()
        d["cards"][1]["oneway"] = "yes"
        self.assertIn("card 42: oneway must be true or false", run_page(d)["bad"])

    def test_an_option_without_undo_shows_none_and_a_flagged_one_is_marked(self):
        res = run_page(example())
        more = card(res, 42)["more"]
        self.assertNotIn("Undo", more["a"])
        self.assertIn('<span class="lbl owu">⚠ Undo</span>Cannot be fully undone', more["b"])
        self.assertNotIn("undo", card(res, 43)["parts"]["imp"][0])
        # the marker is styled from the theme's warn token
        self.assertIn(".impline i.owu,.lbl.owu{color:var(--warn)", PAGE.read_text())


if __name__ == "__main__":
    unittest.main()
