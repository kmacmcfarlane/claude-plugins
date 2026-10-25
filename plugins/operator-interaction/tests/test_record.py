"""The page reads decision-page/5, each card a decision-card/5 record (answers 341 (a), 343 (a)).

The template's `check()` (loaded from `skills/decision-page/assets/index.html`, run under node)
refuses what a record needs to render, one fixture and one refusal each: the stamps (absent,
older or newer), a positive whole `n`, a UTC `rev`, `q`, options as objects in letter order, an
option flagged one-way with no undo, `act` on (z), `open` not a list, an older field left on a
stamped card. An `impact.effect` an older writer left is ignored, never shown. The runner's
`--record` mode checks one record file: clean on an example card made a record, refusing a
broken one and the page-only `L` and `dep`.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, example
from test_depth import card, run_page
from test_context import RUNNER, SKILL


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the card record tests (RecordCheck, RecordRunner) are "
              "skipped, so the page's decision-page/5 check and the runner's --record mode went untested",
              file=sys.stderr)


def bad(d):
    return run_page(d)["bad"]


def refused(test, d, needle):
    b = bad(d)
    test.assertTrue(any(needle in x for x in b), (needle, b))


@unittest.skipUnless(NODE, "node is not installed")
class RecordCheck(unittest.TestCase):

    def test_the_example_is_stamped_and_passes(self):
        d = example()
        self.assertEqual(d["format"], "decision-page/5")
        for c in d["cards"]:
            self.assertEqual(c["format"], "decision-card/5", c["n"])
            self.assertTrue(c["q"].strip(), c["n"])
        self.assertEqual(bad(d), [])

    def test_the_envelope_stamp(self):
        d = example()
        del d["format"]
        self.assertEqual(bad(d), ["cards.json is in an older format: upgrade it (scripts/upgrade_cards.js) and republish"])
        d["format"] = "decision-page/4"
        self.assertEqual(bad(d), ["cards.json is in an older format: upgrade it (scripts/upgrade_cards.js) and republish"])
        d["format"] = "decision-page/6"
        self.assertEqual(bad(d), ["this page template is older than its data (decision-page/6): update the plugins"])
        d["format"] = "cards/5"
        self.assertEqual(bad(d), ["format must be decision-page/5"])

    def test_a_cards_stamp(self):
        d = example()
        del d["cards"][0]["format"]
        refused(self, d, "card 41: in an older format (no decision-card/5 stamp): upgrade it")
        d = example()
        d["cards"][0]["format"] = "decision-card/6"
        refused(self, d, "card 41: in a newer format (decision-card/6) than this page template reads: "
                         "leave it off the page and hand it over")

    def test_n_is_a_positive_whole_number(self):
        for n in (0, -3, True, 41.5, "41"):
            with self.subTest(n=n):
                d = example()
                d["cards"][0]["n"] = n
                refused(self, d, "n must be a whole number of 1 or more")

    def test_rev_and_raised_are_utc_times(self):
        for rev in ("v1", "2026-01-12", "2026-01-12 09:30:00Z"):
            d = example()
            d["cards"][0]["rev"] = rev
            refused(self, d, "card 41: rev must be a UTC time")
        # the minute form is read
        d = example()
        d["cards"][0]["rev"] = "2026-01-12T09:30Z"
        self.assertEqual(bad(d), [])
        d["cards"][0]["raised"] = "yesterday"
        refused(self, d, "card 41: raised must be a UTC time")

    def test_q_is_required_and_one_line(self):
        d = example()
        del d["cards"][0]["q"]
        refused(self, d, "card 41: q missing")
        d = example()
        d["cards"][0]["q"] = "Where?\nAnd why?"
        refused(self, d, "card 41: q must be one line")

    def test_options_are_objects_in_letter_order(self):
        d = example()
        o = d["cards"][0]["options"]
        o[0], o[1] = o[1], o[0]
        refused(self, d, "card 41: options must be in letter order, each letter once")
        d = example()
        d["cards"][0]["options"][0] = ["a", "full", "impact", "title", "one line"]
        refused(self, d, "card 41: each option is an object with k (one letter a-z) and its title")
        d = example()
        d["cards"][0]["options"].pop()
        refused(self, d, "card 41: the last option must be (z) decide later")

    def test_oneway_without_undo_and_act_on_z(self):
        d = example()
        del d["cards"][1]["options"][1]["undo"]
        refused(self, d, "card 42: (b) is flagged one-way (oneway: true) but has no undo")
        d = example()
        d["cards"][0]["options"][2]["act"] = ["Wait."]
        refused(self, d, "card 41: (z) has act")

    def test_open_is_a_list_of_text(self):
        for v in ("a question", [3], {"q": "x"}):
            d = example()
            d["cards"][0]["open"] = v
            refused(self, d, "card 41: open must be a list of text")

    def test_an_older_field_on_a_stamped_card_is_refused(self):
        for k, v in (("o", []), ("blocks", {}), ("warn", True), ("unknown", "x"), ("act", {}), ("stakes", "x")):
            with self.subTest(field=k):
                d = example()
                d["cards"][0][k] = v
                refused(self, d, "card 41: %s is an older field" % k)

    def test_why_whyask_and_reason_are_not_refused(self):
        # owed by a new card, linted by the runner; an upgraded older card may lack them
        d = example()
        for k in ("why", "whyask", "reason"):
            del d["cards"][2][k]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertNotIn("<summary>Background", card(res, 43)["html"])

    def test_an_impact_effect_is_ignored_not_shown(self):
        d = example()
        d["cards"][0]["impact"]["effect"] = "an older card-level effect"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertNotIn("an older card-level effect", card(res, 41)["html"])
        # mutant: a template that still shows it
        from test_impact import page_free_script
        from test_depth import node, HARNESS
        script = page_free_script().replace('const IMP_FACETS=[["wait"', 'const IMP_FACETS=[["effect","→","Effect"],["wait"')
        out = subprocess.run([NODE, "-e", script + HARNESS], input=json.dumps([d]), capture_output=True,
                             text=True, timeout=60)
        self.assertIn("an older card-level effect", out.stdout)

    def test_open_questions_fold(self):
        res = run_page(example())
        h = card(res, 42)["html"]
        fold = h[h.index('<details class="gfold ofold">'):]
        fold = fold[:fold.index("</details>")]
        self.assertIn('<span class="gsum">2 open: how many external sites link to the old URLs</span>', fold)
        self.assertEqual(fold.count("<li>"), 2)
        # closed, after Context and before the Impact
        self.assertLess(h.index('data-sec="ctx"'), h.index('<details class="gfold ofold">'))
        self.assertLess(h.index('<details class="gfold ofold">'), h.index('data-sec="imp"'))
        self.assertNotIn('<details class="gfold ofold" open', h)
        # its summary cuts the first question at about 12 words; the text is escaped
        d = example()
        d["cards"][0]["open"] = [" ".join("w%d" % i for i in range(20)), "<img src=x onerror=1>"]
        h = card(run_page(d), 41)["html"]
        self.assertIn("2 open: " + " ".join("w%d" % i for i in range(12)) + " …</span>", h)
        self.assertNotIn("<img", h)


def record_of(c):
    r = copy.deepcopy(c)
    r.pop("L", None)
    r.pop("dep", None)
    if isinstance(r.get("detail"), dict):
        r["detail"].pop("dep", None)
    return r


def run_record(rec):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "record.json"
        p.write_text(json.dumps(rec))
        out = subprocess.run([NODE, str(RUNNER), "--record", str(p)], capture_output=True, text=True,
                             timeout=60, cwd=SKILL)
    return out.returncode, out.stdout


@unittest.skipUnless(NODE, "node is not installed")
class RecordRunner(unittest.TestCase):

    def test_an_example_card_as_a_record_is_clean(self):
        for c in example()["cards"]:
            self.assertEqual(run_record(record_of(c)), (0, ""), c["n"])

    def test_a_broken_record_is_refused(self):
        r = record_of(example()["cards"][0])
        del r["options"][1]["effect"]
        code, out = run_record(r)
        self.assertEqual(code, 1, out)
        self.assertIn("record 41: (b) needs its effect", out)

    def test_page_only_fields_are_refused_in_a_record(self):
        r = record_of(example()["cards"][1])
        r["L"] = "details"
        r["dep"] = "[[41]] (b)"
        code, out = run_record(r)
        self.assertEqual(code, 1, out)
        self.assertIn("record 42: L is page-only", out)
        self.assertIn("record 42: dep is page-only", out)

    def test_a_record_lints_under_its_own_name(self):
        r = record_of(example()["cards"][2])
        del r["whyask"]
        code, out = run_record(r)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: record 43: depth: whyask missing", out)

    def test_usage(self):
        out = subprocess.run([NODE, str(RUNNER), "--record"], capture_output=True, text=True, timeout=60, cwd=SKILL)
        self.assertEqual(out.returncode, 1)
        self.assertIn("check_cards: usage:", out.stdout)


if __name__ == "__main__":
    unittest.main()
