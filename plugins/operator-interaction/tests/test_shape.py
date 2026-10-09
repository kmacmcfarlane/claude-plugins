"""Every page card's levels have their shapes, and the page names things instead of tagging them.

Three parts:

- the decision page (`decision-page` skill): the level shapes (a bullet as text or
  `{t, sub}`, a section as `{h, b}`) and their check, the nested and sectioned render, and
  the Impact one facet a line at every level; loaded from `assets/index.html` and run under
  node against `assets/cards.example.json` and copies of it;
- the pre-publish runner's shape lints, `scripts/check_cards.js`: summaries a sentence or
  two, medium terse bullets with a sub-bullet or two, high headed sections, the Impact's
  medium one bullet per facet, and a card Impact effect that reads as the recommendation's;
- the runner's id lint: ids anywhere the page shows text, the page and layer titles and
  `refs` included, with the forms that are not ids left clean.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import sys
import unittest

from test_impact import NODE, example
from test_context import runner
from test_depth import card, run_page, run_pages


def setUpModule():
    # the page and runner tests need node; without it they skip, and say so where the
    # Check's output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's shape tests "
              "(DecisionPageShapes, ShapeRunner, IdRunner) are skipped, so the level shapes, "
              "their render and the shape and id lints went untested", file=sys.stderr)


def c41(d):
    return d["cards"][0]


def c43(d):
    return d["cards"][2]


def words(n, w="word"):
    return " ".join([w] * n)


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageShapes(unittest.TestCase):

    def test_every_detail_key_takes_text_bullets_or_sections(self):
        shapes = ["text",
                  ["a", {"t": "b", "sub": ["c", "d"]}, {"t": "e"}],
                  [{"h": "H", "b": ["a", {"t": "b", "sub": ["c"]}]}]]
        datasets = []
        for k in ("context", "rec", "why", "whyask", "dep", "evidence"):
            for sh in shapes:
                d = example()
                c41(d)["detail"][k] = [sh]
                datasets.append(d)
        for sh in shapes:
            d = example()
            c41(d)["detail"]["o"]["a"] = [sh]
            datasets.append(d)
        for sh in shapes[1:]:
            d = example()
            c41(d)["detail"]["tldr"] = [sh]
            datasets.append(d)
        for v in ("text", {"t": "a", "sub": ["b"]}, ["a", {"t": "b", "sub": ["c"]}]):
            d = example()
            c41(d)["detail"]["impact"] = [{"effect": v, "wait": v, "cost": v}]
            datasets.append(d)
        for res in run_pages(datasets)["out"]:
            self.assertEqual(res["bad"], [])

    def test_an_empty_or_null_sub_is_accepted_and_renders_no_sub_list(self):
        for sub in ([], None):
            d = example()
            c41(d)["detail"]["why"][0] = [{"t": "Two publishes broke", "sub": sub}, "Blocks two cards"]
            res = run_page(d)
            self.assertEqual(res["bad"], [], sub)
            self.assertIn("<li>Two publishes broke</li>", card(res, 41)["parts"]["why"][1])

    def test_one_mention_draws_one_id_line(self):
        d = example()
        c43(d)["why"] = "see commit abc123"
        lines = [x for x in runner(d)[1].splitlines() if "looks like an id" in x]
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("commit abc123 looks like an id", lines[0])

    def test_the_evidence_summary_refuses_sections_and_bullets_with_sub_bullets(self):
        for v in ([{"h": "H", "b": ["a"]}], [{"t": "a", "sub": ["b"]}]):
            d = example()
            c41(d)["evidence"] = v
            res = run_page(d)
            self.assertIn("card 41: evidence must be text or a non-empty list of text", res["bad"])

    def test_a_t_and_h_object_is_refused_in_a_level_and_in_an_impact_facet(self):
        d = example()
        c41(d)["detail"]["context"] = [[{"t": "a", "h": "b", "b": ["c"]}]]
        self.assertTrue(any("card 41: detail.context must be" in b for b in run_page(d)["bad"]))
        d = example()
        c41(d)["detail"]["impact"][0]["wait"] = {"t": "a", "h": "b"}
        self.assertTrue(any("card 41: detail.impact must be" in b for b in run_page(d)["bad"]))

    def test_sub_bullets_nest_and_sections_render_in_order(self):
        res = run_page(example())
        p = card(res, 41)["parts"]
        med = p["ctx"][1]
        self.assertIn("<li>A stale cache broke two publishes this month<ul class=\"lvl sub\">"
                      "<li>a leftover copy of an old build, reused by mistake</li>", med)
        high = p["ctx"][2]
        heads = [high.index('<div class="lvs"><h4 class="lvh">%s</h4><ul class="lvl">' % h)
                 for h in ("Today", "What CI changes", "Why now", "What rides on it")]
        self.assertEqual(heads, sorted(heads))

    def test_a_heading_is_escaped_and_never_links(self):
        d = example()
        c41(d)["detail"]["why"][1][0]["h"] = '<img src=x> https://x.example.com/h [[38]]'
        h = card(run_page(d), 41)["parts"]["why"][2]
        head = h[h.index('<h4 class="lvh">'):h.index("</h4>")]
        self.assertNotIn("<img", head)
        self.assertIn("&lt;img", head)
        self.assertNotIn("<a ", head)
        self.assertIn('data-ref="38"', head)

    def test_the_impact_is_one_facet_a_line_at_every_level(self):
        res = run_page(example())
        imp = card(res, 41)["parts"]["imp"]
        # summary: a paragraph per facet, in the one order
        self.assertEqual(imp[0].count("<p>"), 5)
        pos = [imp[0].index(t) for t in ("<p><b>→</b>", "<p><i>later:</i>", "<p><i>reach:</i>",
                                         "<p><i>undo:</i>", "<p><i>cost:</i>")]
        self.assertEqual(pos, sorted(pos))
        # medium: one bullet per facet, the options in its sub-bullets
        top = imp[1][imp[1].index('<ul class="lvl">') + len('<ul class="lvl">'):]
        self.assertEqual(len([x for x in top.split("<li>") if x.startswith(("<b>", "<i>"))]), 5)
        self.assertIn("<li><b>→</b> sets where the docs build runs, and who can publish"
                      '<ul class="lvl sub"><li>(a) nothing changes', imp[1])
        # high: a section per facet
        self.assertEqual(imp[2].count('<div class="lvs">'), 5)

    def test_older_text_levels_still_render_as_paragraphs(self):
        d = example()
        c41(d)["detail"]["context"] = ["Older medium text.", "Older high text."]
        c41(d)["detail"]["impact"] = [{"effect": "older effect", "wait": "older wait"}]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        p = card(res, 41)["parts"]
        self.assertIn("<p>Older medium text.</p>", p["ctx"][1])
        self.assertIn("<li><b>→</b> older effect</li>", p["imp"][1])


@unittest.skipUnless(NODE, "node is not installed")
class ShapeRunner(unittest.TestCase):

    def lint(self, d, *needles):
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        for n in needles:
            self.assertIn(n, out)
        return out

    def clean(self, d):
        code, out, err = runner(d)
        self.assertEqual((code, out), (0, ""), err)

    def no_shape(self, d):
        code, out, err = runner(d)
        self.assertNotIn("shape:", out, err)

    def test_the_example_is_clean(self):
        self.clean(example())

    def test_contexts_summary_is_two_sentences_and_about_60_words(self):
        d = example()
        c43(d)["context"] = "One. Two. Three."
        self.lint(d, "lint: card 43: shape: Context's summary is 3 sentences")
        d = example()
        c43(d)["context"] = "accent colour, one theme setting: " + words(56)
        self.lint(d, "lint: card 43: shape: Context's summary is 61 words")
        # two sentences, 60 words: clean
        c43(d)["context"] = "accent colour, one theme setting: " + words(54) + ". Second."
        self.no_shape(d)

    def test_the_tldr_is_one_or_two_terse_bullets(self):
        d = example()
        c43(d)["tldr"] = ["Keep the blue", "Or the green", "Or neither"]
        self.lint(d, "lint: card 43: shape: the TLDR has 3 bullets")
        d = example()
        c43(d)["tldr"] = ["Keep the blue", words(15)]
        self.lint(d, "lint: card 43: shape: TLDR bullet 2 is 15 words")
        c43(d)["tldr"] = ["Keep the blue", words(14)]
        self.no_shape(d)

    def test_an_impact_facet_is_about_16_words(self):
        d = example()
        c43(d)["impact"]["reach"] = words(17)
        self.lint(d, "lint: card 43: shape: Impact reach is 17 words")
        c43(d)["impact"]["reach"] = words(16)
        self.no_shape(d)

    def test_medium_is_terse_bullets_with_a_sub_bullet_or_two(self):
        cases = [
            ("Older prose at more detail, written as one paragraph.", "Why now more detail is prose: write it as terse bullets"),
            ([{"h": "H", "b": ["a b c"]}], "Why now more detail is in sections: save sections for full detail"),
            ([words(2)] * 7, "Why now more detail has 7 bullets"),
            ([{"t": "a b", "sub": ["c", "d", "e"]}], "Why now more detail bullet 1 has 3 sub-bullets"),
            ([{"t": "a b", "sub": [words(15)]}], "Why now more detail bullet 1.1 is 15 words"),
            (["One point. Then another."], "Why now more detail bullet 1 is 2 sentences"),
        ]
        for medium, needle in cases:
            with self.subTest(needle=needle):
                d = example()
                c41(d)["detail"]["why"][0] = medium
                self.lint(d, "lint: card 41: shape: " + needle)
        d = example()
        c41(d)["detail"]["why"][0] = [{"t": "a b", "sub": ["c", words(14)]}] + ["x y"] * 5
        self.no_shape(d)

    def test_high_is_headed_sections(self):
        for high in ("Older prose at full detail.", ["a plain", "list of bullets"]):
            d = example()
            c41(d)["detail"]["whyask"][1] = high
            self.lint(d, "lint: card 41: shape: Why ask full detail is not in sections: give full "
                         "detail as headed sections with bullets")
        # the Impact's high is facet objects, shown as sections: never linted for it
        out = runner(example())[1]
        self.assertNotIn("the Impact line full detail", out)

    def test_a_fold_summary_is_linted_only_where_the_part_has_levels(self):
        d = example()
        c43(d)["why"] = "One. Two. Three."
        self.no_shape(d)
        d = example()
        c41(d)["why"] = "One. Two. Three."
        self.lint(d, "lint: card 41: shape: Why now's summary is 3 sentences")

    def test_the_sentence_counter_skips_abbreviations_versions_code_and_links(self):
        d = example()
        c43(d)["context"] = ("The accent colour, e.g. the blue, is one theme setting in v1.2.3 "
                             "of `theme.toml` at https://x.example.com/a.b. Second sentence.")
        self.no_shape(d)

    def test_the_impacts_medium_is_one_bullet_per_facet(self):
        d = example()
        c41(d)["detail"]["impact"][0]["wait"] = ["the laptop build stays", "they wait"]
        self.lint(d, "lint: card 41: shape: the Impact's more detail, wait, is a list: give each "
                     "facet one bullet")
        d = example()
        c41(d)["detail"]["impact"][0]["reach"]["t"] = words(15)
        self.lint(d, "lint: card 41: shape: the Impact's more detail, reach is 15 words")
        d = example()
        c41(d)["detail"]["impact"][0]["undo"]["sub"].append("(c) a third")
        self.lint(d, "lint: card 41: shape: the Impact's more detail, undo, has 3 sub-bullets: "
                     "give a facet one or two; where it differs across more than two options, "
                     "group them")
        # two sub-bullets on a two-option card: clean
        d = example()
        self.assertEqual(len(c41(d)["detail"]["impact"][0]["undo"]["sub"]), 2)
        self.clean(d)

    def test_card_41s_impact_medium_is_at_least_twice_its_summary(self):
        # a pin on the example, not a lint: the step from the summary is visible
        w = lambda x: (sum(w(v) for v in x.values()) if isinstance(x, dict)
                       else sum(w(v) for v in x) if isinstance(x, list) else len(str(x).split()))
        c = c41(example())
        self.assertGreaterEqual(w(c["detail"]["impact"][0]), 2 * w(c["impact"]))
        # and a sub-bullet or two per facet
        for v in c["detail"]["impact"][0].values():
            self.assertLessEqual(len(v.get("sub", [])) if isinstance(v, dict) else 0, 2)

    def test_an_effect_that_reads_as_the_recommendations_is_linted(self):
        d = example()
        c41(d)["impact"]["effect"] = "publishing no longer depends on one laptop"
        self.lint(d, "lint: card 41: impact: the effect reads as the recommended option's")
        d = example()
        c41(d)["detail"]["impact"][0]["effect"] = "publishing no longer depends on one laptop"
        self.lint(d, "lint: card 41: impact: the effect (more detail) reads as the recommended "
                     "option's")
        # one naming the options is the decision's: clean
        d = example()
        c41(d)["impact"]["effect"] = "(a) the laptop publishes; (b) CI publishes"
        self.clean(d)
        # a card with no recommendation is never linted for it
        d = example()
        c43(d)["impact"]["effect"] = "the site matches the logo"
        self.assertNotIn("impact: the effect", runner(d)[1])

    def test_the_tldr_rec_lint_walks_sections_bullets_and_sub_bullets(self):
        d = example()
        c41(d)["detail"]["tldr"][1][0]["b"][1] = "Suggest moving to CI"
        self.lint(d, "lint: card 41: tldr bullet 3 (full detail) may carry the recommendation")
        d = example()
        c41(d)["detail"]["tldr"][0][1]["sub"][0] = "Suggest moving to CI"
        self.lint(d, "lint: card 41: tldr bullet 4 (more detail) may carry the recommendation")
        d = example()
        c41(d)["detail"]["tldr"][0][1]["sub"][0] = "Recent failures"
        self.clean(d)


LINTED = ["History scrub (4151)", "Operator activity records (0999, 3e8e)", "Checkpoint (9652)",
          "see work item 4151", "per commit 8ea8a3c", "as decision 151 said", "per answer 201 (c)",
          "the format (2ff6)", "decision-page-tldr-first-levels-shaped-s-1e00", "item #4151"]
CLEAN = ["each item added", "the item faded", "commit 100 lines", "item 2026",
         "end-to-end-cafe", "since then (2026)", "since (1999)", "as [[151]] said",
         "see https://x.example.com/a1b2c3d4", "the `.cache/1e00` path", "keeps #2d56c8",
         "from 2026-10-09", "answer 2 questions", "card 3 of 5", "a wait (1500 ms)"]


@unittest.skipUnless(NODE, "node is not installed")
class IdRunner(unittest.TestCase):

    def test_ids_are_linted_on_a_card(self):
        for s in LINTED:
            with self.subTest(text=s):
                d = example()
                c43(d)["why"] = s
                code, out, _ = runner(d)
                self.assertEqual(code, 2, out)
                self.assertIn("lint: card 43: ", out)
                self.assertIn("looks like an id (why): name the", out)

    def test_ids_are_linted_in_the_page_and_layer_titles(self):
        for s in LINTED:
            with self.subTest(text=s):
                d = example()
                d["page"]["title"] = s
                d["layers"][1][1] = s
                code, out, _ = runner(d)
                self.assertEqual(code, 2, out)
                self.assertIn("looks like an id (the page title)", out)
                self.assertIn("looks like an id (the title of layer details)", out)
                self.assertTrue(all(x.startswith("lint: page: ") for x in out.splitlines()), out)

    def test_a_decision_by_number_is_told_its_slug(self):
        d = example()
        c43(d)["why"] = "as decision 151 said"
        self.assertIn("decision 151 looks like an id (why): name the decision by its slug [[151]]",
                      runner(d)[1])

    def test_forms_that_are_not_ids_stay_clean(self):
        for s in CLEAN:
            with self.subTest(text=s):
                d = example()
                c43(d)["why"] = s
                code, out, err = runner(d)
                self.assertEqual((code, out), (0, ""), err)

    def test_refs_answers_are_the_operators_own_words(self):
        d = example()
        d["refs"]["38"]["a"] = "a, as in (4151)"
        out = runner(d)[1]
        self.assertIn("lint: page: refs 38 a holds (4151), which looks like an id: if these are "
                      "the operator's own words, leave them as given; otherwise name the thing", out)
        d = example()
        d["refs"]["38"]["q"] = "Clear the cache (4151)?"
        self.assertIn("lint: page: (4151) looks like an id (refs 38 q)", runner(d)[1])


if __name__ == "__main__":
    unittest.main()
