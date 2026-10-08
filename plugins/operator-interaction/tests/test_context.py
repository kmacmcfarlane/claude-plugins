"""Every page card opens on a Context that introduces what the rest of it names.

Three parts:

- the decision page (`decision-page` skill): its required `context` field, the refusal of a
  TLDR bullet that carries the recommendation, `contextBlock` (which renders Context, and an
  older card's `what` after it) and the render order, loaded from `assets/index.html` and run
  under node against `assets/cards.example.json` and broken copies of it;
- the pre-publish runner, `scripts/check_cards.js`: its exits and one-line errors, and its
  lints for ids, counts and named things a card's context does not introduce;
- the `rev` rule, in identical words in the four places it is written.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, PAGE, END_MARK, example, page_free_script

SKILL = PAGE.parent.parent
RUNNER = SKILL / "scripts" / "check_cards.js"
SCHEMA = SKILL / "references" / "cards-schema.md"
SKILL_MD = SKILL / "SKILL.md"

REV_RULE = (
    "Any change to a card gets a new `rev`, Context included: an **Added:** line after "
    "`tell me`, more detail after `expand`, a `dig into` finding, a corrected fact, a re-ask. "
    "Only the one-time format migration keeps it: a card written before Context existed, whose "
    "own `what` and resume cue move into `context`, and whose terms are glossed from its own "
    "folds alone. A gloss drawn from anywhere outside the card is new information: a new `rev`.")


def setUpModule():
    # the page and runner tests need node; without it they skip, and say so where the
    # Check's output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's context tests "
              "(DecisionPageContext, DecisionPageRunner) are skipped, so the page's context "
              "and TLDR checks, contextBlock and the pre-publish runner went untested",
              file=sys.stderr)


# a list of data files in, each one's check() result and its cards' Context blocks out
HARNESS = r"""
const ds = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = ds.map(d => {
  const bad = check(d);
  let blocks = [];
  if (!bad.length) {
    CARDS = d.cards; REFS = d.refs || {};
    byN = new Map(CARDS.map(c => [String(c.n), c]));
    blocks = CARDS.map(c => ({n: c.n, open: contextBlock(c), pop: contextBlock(c, true)}));
  }
  return {bad, blocks};
});
process.stdout.write(JSON.stringify(out));
"""


def run_pages(datasets):
    out = subprocess.run([NODE, "-e", page_free_script() + HARNESS],
                         input=json.dumps(datasets), capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def run_page(data):
    return run_pages([data])[0]


def with_tldr(bullet):
    d = example()
    d["cards"][0]["tldr"] = ["The docs build runs on a laptop today", bullet]
    return d


# Refused by the page: forms that cannot be anything but the recommendation
REFUSED = [
    "Rec: move it to CI", "**Rec:** x", "1. Rec: b", "- Rec — b", "Rec. (b)", "Rec",
    "rec (b)", "Use rec (b)",
    "Recommended: (b)", "Recommendation — publish from CI",
    "I'd recommend CI", "I’d recommend CI", "We would recommend b", "We’d recommend b",
    "I recommend b", "Recommend (b)", "→ Recommended (b)", "Rec - b",
    "My recommendation: b", "Our recommendation is b",
    "(b) is recommended", "→ (b), recommended", "Start the three now (recommended)",
]
# Known refusals of third-party wording (R2): excluding them needs a lookbehind, which would
# stop the whole page script in an older browser. The fix is to reword the bullet.
KNOWN_REFUSALS = ["Recommendation: the audit's, not mine", "the audit's rec (b)"]
# Passed by the page
PASSED = [
    "Recap: two options", "Records stay", "Reconsider later", "Recent failures",
    "Recompute nightly", "Precedent: kept",
    "The review recommended four changes", "Recommended by the review: four changes",
    "Recommendations from the audit apply",
    "Start the three now", "Move it to CI, or keep it local", "Best: (b)",
    "(b) recommended by the audit", "Option (a) is recommended by the vendor",
    "Recommended (b) by the audit", "Recommended-by-default flags change",
    "Recommendations: four, from the review", "Recommended reading: the audit",
    "Rec room", "Rec’d: b",
]
# Accepted misses (R2): the page passes them; the runner's broad TLDR lint reports them
LINTED_MISSES = ["Rec -b", "Rec-(b)", "Rec’d: b", "Recommend moving to CI",
                 "Recommending CI", "Suggest moving to CI", "We suggest b"]
# Well-known terms the id lint reports and the page never refuses
WELL_KNOWN = ["UTF-8", "SHA-256", "ISO-8601", "GPT-4", "S3", "EC2", "K8s"]


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageContext(unittest.TestCase):

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    def test_the_example_opens_every_card_on_its_context_and_passes(self):
        d = example()
        for c in d["cards"]:
            self.assertTrue(c["context"].strip(), c["n"])
            self.assertNotIn("what", c, c["n"])
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_missing_blank_or_non_text_context_is_refused(self):
        cases = []
        for v in (None, "", "  ", 3, ["x"]):
            d = example()
            if v is None:
                del d["cards"][0]["context"]
            else:
                d["cards"][0]["context"] = v
            cases.append(d)
        for res in run_pages(cases):
            self.assertTrue(any(b.startswith("card 41: context missing") for b in res["bad"]),
                            res["bad"])

    def test_what_is_optional(self):
        d = example()
        for c in d["cards"]:
            c.pop("what", None)
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_cue_only_context_with_a_what_passes(self):
        d = example()
        d["cards"][0]["context"] = "You last saw the build fail twice ([[38]]) · now you pick."
        d["cards"][0]["what"] = "Where the docs site is built from."
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_tldr_bullet_carrying_the_recommendation_is_refused(self):
        bullets = REFUSED + KNOWN_REFUSALS
        for b, res in zip(bullets, run_pages([with_tldr(b) for b in bullets])):
            self.assertIn("card 41: tldr bullet 2 carries the recommendation: the options mark "
                          "it; say what is decided instead", res["bad"], b)

    def test_tldr_wording_that_is_not_the_recommendation_passes(self):
        bullets = PASSED + LINTED_MISSES
        for b, res in zip(bullets, run_pages([with_tldr(b) for b in bullets])):
            self.assertEqual(res["bad"], [], b)

    def test_well_known_terms_never_refuse_the_page(self):
        d = example()
        d["cards"][0]["tldr"] = ["Text is " + " and ".join(WELL_KNOWN)]
        self.assertEqual(run_page(d)["bad"], [])

    def test_two_offending_bullets_give_one_message_naming_the_first(self):
        d = example()
        d["cards"][0]["tldr"] = ["Rec: b", "I recommend b"]
        bad = [b for b in run_page(d)["bad"] if "tldr" in b]
        self.assertEqual(bad, ["card 41: tldr bullet 1 carries the recommendation: the options "
                               "mark it; say what is decided instead"])

    def test_a_tldr_that_is_not_a_list_of_text_gets_the_shape_message_only(self):
        cases = []
        for v in ("x", 3, {}, [1]):
            d = example()
            d["cards"][0]["tldr"] = v
            cases.append(d)
        for res in run_pages(cases):
            tl = [b for b in res["bad"] if "tldr" in b]
            self.assertEqual(tl, ["card 41: tldr must be a list of text"])

    def test_context_block_renders_context_then_an_older_what(self):
        d = example()
        d["cards"][0]["context"] = "the cue ([[38]])"
        d["cards"][0]["what"] = "the old what"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        b41 = res["blocks"][0]["open"]
        self.assertEqual(b41.count("<p>"), 2)
        self.assertLess(b41.index("the cue"), b41.index("the old what"))
        # without what, one paragraph
        self.assertEqual(res["blocks"][1]["open"].count("<p>"), 1)
        self.assertIn('<span class="lbl">Context</span>', res["blocks"][1]["open"])

    def test_context_block_escapes_and_marks_up(self):
        d = example()
        d["cards"][0]["context"] = '<img src=x onerror="alert(1)" > the `main` branch ([[38]])'
        d["cards"][0]["what"] = "<script >x</script >"
        blk = run_page(d)["blocks"][0]
        for h in (blk["open"], blk["pop"]):
            self.assertNotIn("<img", h)
            self.assertNotIn("<script", h)
            self.assertIn("&lt;img", h)
            self.assertIn("<code>main</code>", h)
        self.assertIn('class="slug"', blk["open"])
        self.assertIn('data-ref="38"', blk["open"])
        # the popup renders slugs as text, never a nested button
        self.assertIn('<span class="slug-t">38', blk["pop"])
        self.assertNotIn("<button", blk["pop"])

    def test_the_open_card_and_the_popup_open_on_context(self):
        html = PAGE.read_text()
        cards = html[html.index("function renderCards"):html.index("function placeholderFor")]
        self.assertLess(cards.index("contextBlock(c)"), cards.index("impactLine(c)"))
        self.assertLess(cards.index("impactLine(c)"), cards.index('class="tldr"'))
        # under decision 197 (a) the Background fold holds Why now and Why ask only
        bg = cards[cards.index("<summary>Background</summary>"):cards.index("Options in full")]
        self.assertNotIn("c.what", bg)
        self.assertNotIn("c.context", cards.replace("contextBlock(c)", ""))
        pop = html[html.index("function fillPop"):html.index("function place(")]
        self.assertLess(pop.index("contextBlock(c,true)"), pop.index('class="tldr"'))

    def test_the_page_free_part_holds_no_lookbehind(self):
        # a lookbehind is a syntax error in an older browser, and stops the whole script
        self.assertNotIn("(?<", page_free_script())


def runner(data=None, *, path=None, cwd=None, script=RUNNER):
    """Run the runner on data written to a temp cards.json, or on a path as given."""
    with tempfile.TemporaryDirectory() as tmp:
        if path is None:
            path = pathlib.Path(tmp) / "cards.json"
            path.write_text(data if isinstance(data, str) else json.dumps(data))
        out = subprocess.run([NODE, str(script), str(path)], capture_output=True, text=True,
                             timeout=60, cwd=cwd or SKILL)
    return out.returncode, out.stdout, out.stderr


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageRunner(unittest.TestCase):

    def assert_one_line(self, out, start):
        lines = out.splitlines()
        self.assertEqual(len(lines), 1, out)
        self.assertTrue(lines[0].startswith(start), out)
        self.assertNotIn("    at ", out)

    def assert_lint(self, d, needle):
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        self.assertTrue(all(x.startswith("lint: card ") for x in out.splitlines()), out)
        self.assertIn(needle, out)
        return out

    def assert_clean(self, d):
        code, out, err = runner(d)
        self.assertEqual((code, out), (0, ""), err)

    def test_the_example_is_clean(self):
        # end-to-end pin for the example's contexts: no refusal and no lint on any card
        self.assert_clean(example())

    def test_a_missing_context_exits_1_with_the_refusal(self):
        d = example()
        del d["cards"][0]["context"]
        code, out, _ = runner(d)
        self.assertEqual(code, 1)
        self.assertIn("card 41: context missing", out)

    def test_a_missing_file_is_one_line(self):
        code, out, _ = runner(path="/nonexistent/cards.json")
        self.assertEqual(code, 1)
        self.assert_one_line(out, "check_cards: cannot read /nonexistent/cards.json")

    def test_invalid_json_is_one_line(self):
        code, out, _ = runner("{")
        self.assertEqual(code, 1)
        self.assert_one_line(out, "check_cards: not valid JSON")

    def test_an_unreadable_template_or_a_missing_marker_is_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "scripts").mkdir()
            script = root / "scripts" / "check_cards.js"
            shutil.copy(RUNNER, script)
            # no assets/index.html beside it
            code, out, _ = runner(example(), script=script)
            self.assertEqual(code, 1)
            self.assert_one_line(out, "check_cards: cannot read the template")
            # a template with its end-of-page-free-part marker gone
            (root / "assets").mkdir()
            (root / "assets" / "index.html").write_text(PAGE.read_text().replace(END_MARK, "/* x"))
            code, out, _ = runner(example(), script=script)
            self.assertEqual(code, 1)
            self.assert_one_line(out, "check_cards: the template has no page-free part")

    def test_a_file_failing_the_check_gets_refusals_and_no_lints(self):
        # layers kept, so check() reaches the card checks: card 41 has a blank context (a
        # refusal) and KAPPA-3570 in its TLDR, which the id lint would report on a clean file
        d = example()
        d["cards"][0]["context"] = " "
        d["cards"][0]["tldr"].append("Fixes KAPPA-3570")
        code, out, _ = runner(d)
        self.assertEqual(code, 1)
        self.assertIn("card 41: context missing", out)
        self.assertNotIn("lint:", out)

    def test_the_id_lint_covers_every_flat_field(self):
        setters = {
            "t": lambda c: c.__setitem__("t", "Docs build KAPPA-3570"),
            "tldr": lambda c: c["tldr"].append("KAPPA-3570 asks for it"),
            "title": lambda c: c["o"][0].__setitem__(3, "Keep KAPPA-3570"),
            "one line": lambda c: c["o"][0].__setitem__(4, "per KAPPA-3570"),
        }
        for k in ("effect", "wait", "reach", "undo", "cost"):
            setters["impact." + k] = (lambda k: lambda c: c["impact"].__setitem__(k, "per KAPPA-3570"))(k)
        for k in ("ifleft", "roundcosts", "ifunanswered", "reason", "unknown", "norec", "dep"):
            setters[k] = (lambda k: lambda c: c.__setitem__(k, "per KAPPA-3570"))(k)
        for name, put in setters.items():
            with self.subTest(field=name):
                d = example()
                put(d["cards"][0])
                self.assert_lint(d, "lint: card 41: KAPPA-3570 is not introduced in its context")
                d["cards"][0]["context"] += " KAPPA-3570 is the docs team's ticket for the move."
                self.assert_clean(d)

    def test_the_folds_act_lede_and_layer_notes_are_not_linted(self):
        for put in (lambda d: d["cards"][0]["o"][0].__setitem__(1, "see KAPPA-3570"),
                    lambda d: d["cards"][0].__setitem__("evidence", "see KAPPA-3570"),
                    lambda d: d["cards"][0]["act"]["b"].append("Close KAPPA-3570."),
                    lambda d: d["page"].__setitem__("lede", "From KAPPA-3570."),
                    lambda d: d["layers"][0].__setitem__(2, "From KAPPA-3570.")):
            d = example()
            put(d)
            self.assert_clean(d)

    def test_slugs_and_hex_colours_are_not_ids(self):
        d = example()
        d["cards"][2]["o"][0][4] = "keeps #2d56c8, as [[38]] left it"
        self.assert_clean(d)

    def test_well_known_terms_are_linted_never_refused(self):
        for t in WELL_KNOWN:
            with self.subTest(term=t):
                d = example()
                d["cards"][0]["tldr"].append("Uses " + t)
                self.assert_lint(d, "lint: card 41: " + t + " is not introduced")

    def test_a_count_its_context_does_not_name_is_linted(self):
        d = with_tldr("Start the three now")
        self.assert_lint(d, '"three" counts things its context does not name: say what the '
                            "three things are, or list them")
        d["cards"][0]["context"] += " The three are the build, the cache and the publish step."
        self.assert_clean(d)

    def test_numbers_that_are_not_counts_are_not_linted(self):
        d = example()
        d["cards"][1]["o"][0][4] = "12 redirects keep old links working"  # twelve, in context
        d["cards"][0]["tldr"] = ["Takes about 4 minutes, from 2026-10-08",
                                 "v1.2.3 ships at 14:05, a two-way door",
                                 "Reaches 50% of readers in 2 weeks"]
        self.assert_clean(d)

    def test_an_ids_digits_are_not_a_count(self):
        d = with_tldr("Fixes KAPPA-3570")
        out = self.assert_lint(d, "KAPPA-3570 is not introduced")
        self.assertEqual(len(out.splitlines()), 1, out)

    def test_a_named_thing_its_context_does_not_gloss_is_linted(self):
        d = example()
        d["cards"][0]["o"][0][3] = "Turn on content mode"
        self.assert_lint(d, '"content mode" is not glossed in its context: give it a one-line '
                            "gloss in context")
        d["cards"][0]["context"] += " Content mode is the host's setting that serves pages as text."
        self.assert_clean(d)

    def test_a_named_thing_drops_its_determiner(self):
        d = with_tldr("The plan stays")
        out = self.assert_lint(d, '"plan" is not glossed')
        self.assertNotIn('"the plan"', out)

    def test_the_broad_tldr_lint_reports_what_the_page_lets_through(self):
        for b in LINTED_MISSES:
            with self.subTest(bullet=b):
                self.assert_lint(with_tldr(b), "lint: card 41: tldr bullet 2 may carry the "
                                               "recommendation")

    def test_the_broad_tldr_lint_leaves_ordinary_rec_words_alone(self):
        for b in ("Recent failures", "Records stay"):
            with self.subTest(bullet=b):
                self.assert_clean(with_tldr(b))

    def test_a_leftover_what_is_linted(self):
        d = example()
        d["cards"][0]["what"] = "Where the documentation site is built and published from."
        self.assert_lint(d, "lint: card 41: what present: move it into context (after the "
                            "terms, before the cue) and delete it")


class RevRule(unittest.TestCase):
    """The `rev` rule decides which answers keep counting: it reads the same wherever it is
    written, so no copy drifts."""

    def test_the_rev_rule_is_in_identical_words_in_all_four_places(self):
        flat = lambda p: re.sub(r"\s+", " ", p.read_text())
        self.assertEqual(flat(SCHEMA).count(REV_RULE), 2, "cards-schema.md: the rev row and "
                         "§ Republishing older data")
        self.assertEqual(flat(SKILL_MD).count(REV_RULE), 2, "SKILL.md: step 2's rev bullet and "
                         "step 3's republish paragraph")


if __name__ == "__main__":
    unittest.main()
