"""The What part (F6, answer 290 (a)): what is decided, after Context, and for a set every item.

Three parts:

- the decision page (`decision-page` skill, under node): `whatPart` renders `what` and the set's
  `items` after Context and before the folds above the Impact, never folded, labelled *What · N
  items*, each item's name, where, about and per (its outcome under each option, in letter order),
  every field escaped; `check()` refuses a malformed `what` or `items`;
- the pre-publish runner (`scripts/check_cards.js`, under node): the set refusal (a card that counts
  two or more things where it says what is decided, with no `items` or too few, a lint on a card the
  upgrader carried over with its rev; the
  runner's alone, in page and record mode), the `count` lint's fix pointing to `items` there, the
  `rec-only` lint on an item's `per`, the id lint over the What part, and the What part in the card
  in all;
- the chat card (the `decisions` skill): **What:** after **Context:**, a set's items one bullet
  each under it, the floor's item 1 and the cold read naming the set, and a gallery set card.

Each check is proved by a mutation: a broken template, runner or text fails it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import pathlib
import re
import shutil
import sys
import tempfile
import unittest

from test_impact import NODE, PAGE, DECISIONS, example, page_free_script
from test_context import run_page, runner, RUNNER, SKILL
from test_record import run_record, record_of
from test_chat_context import fenced, views, heads, GALLERY, RENDERING, SKILL_MD, REFS

WORKSHEET = REFS / "worksheet.md"
ITEM_BULLET = re.compile(r"^- (?!\*\*\(|\()[^ ].* — .+$")


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the What part's page and runner tests (WhatPartPage, "
              "WhatPartRunner) are skipped, so its render, its check and the set refusal went untested",
              file=sys.stderr)


def card42(res):
    return next(b for b in res["blocks"] if b["n"] == 42)


def three(card):
    card["items"] = [{"name": "Install guide", "where": "/guides/", "about": "a how-to guide"},
                     {"name": "Search guide", "about": "a how-to guide"},
                     {"name": "Theme settings", "about": "a configuration page"}]
    return card


def mutant_runner(old, new):
    """A copy of the runner, beside a copy of the template, with one string replaced."""
    tmp = tempfile.mkdtemp()
    root = pathlib.Path(tmp)
    (root / "scripts").mkdir()
    shutil.copytree(SKILL / "assets", root / "assets")
    js = RUNNER.read_text()
    assert js.count(old) == 1, old
    (root / "scripts" / "check_cards.js").write_text(js.replace(old, new))
    return root / "scripts" / "check_cards.js"


@unittest.skipUnless(NODE, "node is not installed")
class WhatPartPage(unittest.TestCase):

    def test_the_example_shows_each_cards_what_and_its_sets_items(self):
        res = run_page(example())
        self.assertEqual(res["bad"], [])
        for b in res["blocks"]:
            self.assertTrue(b["whatp"].startswith('<div class="what"><span class="lbl">What'), b["n"])
            self.assertIn(b["what"], b["whatp"], b["n"])
        w = card42(res)["whatp"]
        self.assertIn('<span class="lbl">What · 12 items</span>', w)
        self.assertEqual(w.count("<li>"), 12)
        self.assertIn('<span class="iname">Install the tool</span><span class="iwhere">/guides/</span> — a how-to guide', w)
        # a card with no items: its label is What alone
        self.assertIn('<span class="lbl">What</span>', res["blocks"][0]["whatp"])

    def test_it_sits_after_context_before_the_folds_and_is_never_folded(self):
        for b in run_page(example())["blocks"]:
            card = b["card"]
            at = card.index('<div class="what">')
            self.assertLess(card.index('<div class="ctx">'), at, b["n"])
            self.assertLess(at, card.index('class="gfold afold"'), b["n"])
            self.assertLess(at, card.index('class="impline"'), b["n"])
            # only the card itself is open around it: no fold holds it
            self.assertEqual(card[:at].count("<details") - card[:at].count("</details>"), 1, b["n"])
        # mutant: the part placed inside the Assumptions fold
        html = PAGE.read_text()
        old = "+whatPart(c)+openFold(c)+assumeFold(c,P)"
        self.assertEqual(html.count(old), 1)
        script = page_free_script().replace(old, "+openFold(c)+assumeFold(c,P).replace('<div>','<div>'+whatPart(c))")
        b = run_page(example(), script)["blocks"][1]
        at = b["card"].index('<div class="what">')
        self.assertNotEqual(b["card"][:at].count("<details") - b["card"][:at].count("</details>"), 1)

    def test_per_shows_each_options_outcome_in_letter_order(self):
        d = example()
        c = d["cards"][1]
        c["items"][0]["per"] = {"b": "breaks", "a": "redirects to its new address"}
        c["items"][1]["per"] = {"a": "none"}
        w = card42(run_page(d))["whatp"]
        self.assertIn('<span class="iper"><b>(a)</b>redirects to its new address; <b>(b)</b>breaks</span>', w)
        # a none outcome is not shown, and an item with none shows no per line
        self.assertEqual(w.count('class="iper"'), 1)

    def test_none_is_not_shown(self):
        d = example()
        d["cards"][0]["what"] = "none"
        d["cards"][1]["items"][0]["where"] = "n/a"
        d["cards"][1]["items"][1]["about"] = "-"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertEqual(res["blocks"][0]["whatp"], "")
        self.assertNotIn("n/a", card42(res)["whatp"])
        # no what and no items: no part at all
        d = example()
        del d["cards"][1]["what"], d["cards"][1]["items"]
        self.assertNotIn('<div class="what">', card42(run_page(d))["card"])

    def test_every_field_is_escaped(self):
        bad = ['<script>x</script>', '<img src=x onerror="alert(1)">']
        for v in bad:
            d = example()
            d["cards"][0]["what"] = v
            it = d["cards"][1]["items"][0]
            it.update({"name": v, "where": v, "about": v, "per": {"a": v}})
            res = run_page(d)
            self.assertEqual(res["bad"], [], v)
            for b in res["blocks"]:
                self.assertNotIn("<script", b["card"], v)
                self.assertNotIn("<img", b["card"], v)
        # mutant: an item's about drawn raw
        old = "' — '+fmt(x.about)"
        self.assertEqual(PAGE.read_text().count(old), 1)
        d = example()
        d["cards"][1]["items"][0]["about"] = bad[1]
        b = card42(run_page(d, page_free_script().replace(old, "' — '+x.about")))
        self.assertIn("<img", b["card"])

    def test_check_refuses_a_malformed_what_or_items(self):
        cases = {
            "what must be text": lambda c: c.__setitem__("what", ["x"]),
            "items must be a non-empty list": lambda c: c.__setitem__("items", []),
            "item 1 needs its name": lambda c: c["items"][0].pop("name"),
            "item 2 where must be text": lambda c: c["items"][1].__setitem__("where", 3),
            "item 1 about must be text": lambda c: c["items"][0].__setitem__("about", ["x"]),
            "item 1 per must be an object": lambda c: c["items"][0].__setitem__("per", "a: x"),
            "item 1 per names (d), which is not one of the card's options":
                lambda c: c["items"][0].__setitem__("per", {"d": "x"}),
            "item 1 per (a) must be text": lambda c: c["items"][0].__setitem__("per", {"a": 1}),
        }
        for needle, put in cases.items():
            with self.subTest(needle):
                d = example()
                put(d["cards"][1])
                bad = run_page(d)["bad"]
                self.assertTrue(any(b.startswith("card 42: ") and needle in b for b in bad), bad)
        # a well-formed per passes
        d = example()
        d["cards"][1]["items"][0]["per"] = {"a": "redirects", "b": "breaks", "z": "waits"}
        self.assertEqual(run_page(d)["bad"], [])
        # mutant: the letter check gone, an unknown letter passes
        old = 'if(!os.includes(k))bad.push(at+" per names ("+k+"), which is not one of the card\'s options");\n          else '
        self.assertEqual(page_free_script().count(old), 1)
        d = example()
        d["cards"][1]["items"][0]["per"] = {"d": "x"}
        self.assertEqual(run_page(d, page_free_script().replace(old, ""))["bad"], [])


SET_REFUSAL = "a set not listed in items: it counts "


def refusal_in(out):
    """Whether the runner's output holds the set refusal (a lint line holding the same words is no refusal)."""
    return any(SET_REFUSAL in x and not x.startswith("lint:") for x in out.splitlines())


@unittest.skipUnless(NODE, "node is not installed")
class WhatPartRunner(unittest.TestCase):

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_a_count_where_the_card_says_what_is_decided_needs_its_items(self):
        places = {
            "t": lambda c: c.__setitem__("t", "Move three pages"),
            "first tldr bullet": lambda c: c["tldr"].__setitem__(0, "Move three pages"),
            "option title": lambda c: c["options"][0].__setitem__("title", "Keep three pages"),
            "option line": lambda c: c["options"][0].__setitem__("line", "keeps three pages local"),
        }
        for name, put in places.items():
            with self.subTest(name):
                d = example()
                put(d["cards"][0])
                code, out, _ = runner(d)
                self.assertEqual(code, 1, out)
                self.assertIn("card 41: " + SET_REFUSAL + "3 things where it says what is decided", out)
                self.assertNotIn("lint:", out)
                # listed: no refusal
                three(d["cards"][0])
                code, out, _ = runner(d)
                self.assertNotIn(SET_REFUSAL, out)
                self.assertIn(code, (0, 2), out)

    def test_a_count_in_the_second_tldr_bullet_goes_to_the_count_lint(self):
        d = example()
        d["cards"][0]["tldr"][1] = "Move three pages"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertNotIn(SET_REFUSAL, out)
        self.assertIn('"three" counts things its context does not name: say what the three things are', out)
        # mutant: every bullet read for the refusal
        script = mutant_runner("const out = [c.t, c.tldr[0]];", "const out = [c.t, ...c.tldr];")
        self.assertEqual(runner(d, script=script)[0], 1)

    def test_fewer_items_than_the_largest_count_are_refused(self):
        d = example()
        d["cards"][0]["tldr"][0] = "Move three pages"
        three(d["cards"][0])["items"].pop()
        code, out, _ = runner(d)
        self.assertEqual(code, 1, out)
        self.assertIn("card 41: " + SET_REFUSAL + "3 things where it says what is decided, but items lists 2", out)
        # the largest count rules: "two" and "three", two items, still short
        d["cards"][0]["options"][0]["title"] = "Keep two pages"
        self.assertEqual(runner(d)[0], 1)

    def test_any_other_mismatch_is_a_lint(self):
        # more items than the count, or a list matching none of two counts but not short of the largest
        d = example()
        d["cards"][0]["tldr"][0] = "Move three pages"
        three(d["cards"][0])["items"].append({"name": "Search settings", "about": "a configuration page"})
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 41: shape: " + SET_REFUSAL + "3 things where it says what is decided, but items "
                      "lists 4: make the count and the list agree", out)
        # mutant: the length rule exact again, the longer list refused
        script = mutant_runner("n < Math.max(...small) && !carried(c)", "n !== Math.max(...small) && !carried(c)")
        self.assertEqual(runner(d, script=script)[0], 1)

    def test_a_count_elsewhere_is_never_refused(self):
        # Context, the Impact, (z)'s line, the folds: not where the card says what is decided
        for put in (lambda c: c.__setitem__("context", c["context"] + " The three pages stay."),
                    lambda c: c["impact"].__setitem__("wait", "the three pages wait"),
                    lambda c: c["options"][2].__setitem__("line", "three pages wait"),
                    lambda c: c.__setitem__("evidence", "Observed: three pages.")):
            d = example()
            put(d["cards"][0])
            code, out, _ = runner(d)
            self.assertNotIn(SET_REFUSAL, out)

    def refused(self, line):
        """Whether the line, as card 41's option (a) line, is refused as a set; a line not refused never exits 1."""
        d = example()
        d["cards"][0]["options"][0]["line"] = line
        code, out, _ = runner(d)
        r = refusal_in(out)
        if not r:
            self.assertNotEqual(code, 1, line + ": " + out)
        return r

    def test_a_numbered_label_is_not_a_set(self):
        # a numeral labels one thing only after a label noun (LABEL_HEAD, a closed list), and only when it ends the
        # text, comes before punctuation, a function word, or a verb and its object; after any other word it counts
        for t in ("File 9 proposed work items", "Fix 3 broken links", "Move 12 old pages", "Ship 4 new skills",
                  "Fix 3 bugs", "Fix the 3 failing tests",
                  # fix round 3: a verb before the numeral heads no label
                  "Retire 3 plugins this quarter", "Archive 5 repos this month",
                  "Delete 4 files the build no longer needs", "This deletes 4 files the build no longer needs",
                  "The move retires three plugins the hub no longer loads", "Delete three", "Retire 3 now",
                  "Archive 5 in this round"):
            with self.subTest(t):
                self.assertTrue(self.refused(t))
        for t in ("Clarify principle 3", "as step 2 of the guide says", "runs on Python 3 only", "Clarify principle 3.",
                  "Build tier three", "Option two first"):
            with self.subTest(t):
                self.assertFalse(self.refused(t))
        # mutants: the label rule gone; a noun after the numeral read as a function word
        script = mutant_runner("const LABEL_NUM = /([A-Za-z]+)\\s+$/;", "const LABEL_NUM = /$^/;")
        d = example()
        d["cards"][0]["options"][0]["line"] = "Clarify principle 3"
        self.assertIn(SET_REFUSAL, runner(d, script=script)[1])
        script = mutant_runner('|| (!!nx && FUNC_AFTER.has(nx[1].toLowerCase()))', "|| !!nx")
        d["cards"][0]["options"][0]["line"] = "fix item 3 broken links"
        self.assertTrue(refusal_in(runner(d)[1]))
        self.assertNotIn(SET_REFUSAL, runner(d, script=script)[1])
        # mutant: any word a label head again, so a verb on no list ("Retire") heads a label
        d["cards"][0]["options"][0]["line"] = "Retire 3 now"
        script = mutant_runner(" || !LABEL_HEAD.test(p[1])) return false;", ") return false;")
        self.assertFalse(refusal_in(runner(d, script=script)[1]))

    def test_numbers_that_count_no_set_are_not_refused(self):
        for t in ("retries 3 times", "pages 3-5 move", "move 3-5 of them", "serves HTTP/2 clients",
                  "keeps 2 of the pages", "indents 2 spaces", "cuts it to 600 words", "trims 1350 to 900 words", "moves 3 to 5 pages",
                  "Which of the two hosts stays",
                  # versions, codes, years, dates and label lists (fix round 2, M1)
                  "Drop Python 2 support", "Keep the Python 3 build", "Use Node 22 everywhere", "Plan the 2027 roadmap",
                  "Fix the 404 page", "Serve a 404 for old URLs", "Due by 26 October", "Due by October 26",
                  "principle 3 implies the change", "findings 3, 4 and 7", "Close issues 12, 14"):
            with self.subTest(t):
                self.assertFalse(self.refused(t))
        # a year is no count for the count lint either
        d = example()
        d["cards"][0]["options"][0]["line"] = "Plan the 2027 roadmap"
        self.assertNotIn('"2027"', runner(d)[1])
        script = mutant_runner("const counts = s => [...unId(s).matchAll(COUNT)].filter(m => !(/^[0-9]+$/.test(m[1]) && YEAR.test(m[1])))",
                               "const counts = s => [...unId(s).matchAll(COUNT)]")
        self.assertIn('"2027"', runner(d, script=script)[1])
        # a count of 100 or more is linted, never refused
        d = example()
        d["cards"][0]["options"][0]["line"] = "Fix the 404 page"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 41: shape: " + SET_REFUSAL + "404 things", out)
        # the options themselves, counted where the card has that many real options (card 41 has two)
        for t in ("Choose between the two options", "Pick one of two layouts"):
            with self.subTest(t):
                self.assertFalse(self.refused(t))
        # but a count of another number, or a sentence not about the options, is a set
        self.assertTrue(self.refused("Choose between the three options"))
        self.assertTrue(self.refused("Move two pages"))
        # mutants: no unit rule; no options rule
        d = example()
        d["cards"][0]["options"][0]["line"] = "indents 2 spaces"
        script = mutant_runner('|| new RegExp("^(?:\\\\s*(?:to|and|-|–)\\\\s*[0-9a-z]+)?\\\\s+" + SET_UNIT + "\\\\b", "i").test(after)', "")
        self.assertIn(SET_REFUSAL, runner(d, script=script)[1])
        d["cards"][0]["options"][0]["line"] = "Choose between the two options"
        script = mutant_runner(".filter(x => !(x === nOpts && ABOUT_OPTIONS.test(t)))", "")
        self.assertIn(SET_REFUSAL, runner(d, script=script)[1])
        # mutants: each M1 rule gone, its phrase refused again
        for phrase, old, new in (
                ("Plan the 2027 roadmap", "!(/^[0-9]+$/.test(m[1]) && YEAR.test(m[1])) && ", ""),
                ("Drop Python 2 support", "&& !afterName(t, m) ", ""),
                ("Due by 26 October", "&& !nearMonth(t, m) ", ""),
                ("Close issues 12, 14", "&& !inNumList(t, m) ", ""),
                ("Fix the 404 page", "const SET_BIG = 100;", "const SET_BIG = 1e9;"),
                ("principle 3 implies the change", "\n    || (!!nx && /s$/i.test(nx[1]) && !!nx[2] && OBJ_DET.has(nx[2].toLowerCase()))", "")):
            with self.subTest(mutant=phrase):
                d["cards"][0]["options"][0]["line"] = phrase
                out = runner(d, script=mutant_runner(old, new))[1]
                # a year of 100 or more comes back as the set lint; the rest as the refusal
                self.assertTrue(SET_REFUSAL in out if phrase == "Plan the 2027 roadmap" else refusal_in(out), out)

    def test_a_verb_heads_no_label(self):
        # fix round 2, L2, and fix round 3: a verb is no label noun, so these count
        for t in ("Ship 3 now", "Close 5", "Fix 3 in this round", "Keep three and drop two"):
            with self.subTest(t):
                self.assertTrue(self.refused(t))
        # a numeral after a verb further in still reads as before: a label before a function word
        self.assertFalse(self.refused("as step 2 of the guide says"))
        # on a two-option card, "Pick 2 hosts" names no options, so it counts
        self.assertTrue(self.refused("Pick 2 hosts"))
        self.assertFalse(self.refused("Pick one of two layouts"))
        # mutant: pick back among the options words
        d = example()
        d["cards"][0]["options"][0]["line"] = "Pick 2 hosts"
        script = mutant_runner("|which of|which one|between|one of|either)", "|which of|which one|between|one of|either|pick)")
        self.assertFalse(refusal_in(runner(d, script=script)[1]))

    def test_top_remaining_both_and_all_of_the_count(self):
        # fix round 3: a count after top, remaining, next or final; "both" before a plural noun is two; the
        # "N of the" exception does not hold after all, both or each
        for t in ("Keep the top three", "Retire the remaining three", "Keep the next four", "Ship the final five",
                  "Retire both plugins", "Ship all three of the skills", "Close each three of the tickets"):
            with self.subTest(t):
                self.assertTrue(self.refused(t))
        for t in ("Do both", "Keep both options", "keeps 2 of the pages", "Treat both as out of scope", "Keep both, this time"):
            with self.subTest(t):
                self.assertFalse(self.refused(t))
        # "Keep the top two" on this two-option card names no options: refused, at least a lint
        self.assertTrue(self.refused("Keep the top two"))
        # mutants: both read as nothing; the of-the exception after all again
        d = example()
        d["cards"][0]["options"][0]["line"] = "Retire both plugins"
        script = mutant_runner(".concat([...t.matchAll(BOTH)].filter(m => !/^options$/i.test(m[1]) && !FUNC_AFTER.has(m[1].toLowerCase())).map(() => 2))", "")
        self.assertFalse(refusal_in(runner(d, script=script)[1]))
        d["cards"][0]["options"][0]["line"] = "Treat both as out of scope"
        script = mutant_runner(" && !FUNC_AFTER.has(m[1].toLowerCase())).map(() => 2))", ").map(() => 2))")
        self.assertTrue(refusal_in(runner(d, script=script)[1]))
        d["cards"][0]["options"][0]["line"] = "Retire both plugins"
        script = mutant_runner(".concat([...t.matchAll(BOTH)].filter(m => !/^options$/i.test(m[1]) && !FUNC_AFTER.has(m[1].toLowerCase())).map(() => 2))", "")
        self.assertFalse(refusal_in(runner(d, script=script)[1]))
        d["cards"][0]["options"][0]["line"] = "Ship all three of the skills"
        script = mutant_runner(" && !/\\b(?:all|both|each)\\s+$/i.test(before)", "")
        self.assertFalse(refusal_in(runner(d, script=script)[1]))

    def test_a_count_in_what_without_its_items_is_linted(self):
        # fix round 2, L4: a count lint, never a refusal
        d = example()
        d["cards"][0]["what"] = "Which three steps of the docs build move to CI."
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 41: what counts 3 things its items do not list: list each in items", out)
        three(d["cards"][0])
        self.assertNotIn("what counts", runner(d)[1])
        # a list of another length: the lint names it
        d["cards"][0]["items"].append({"name": "Search settings", "about": "a configuration page"})
        self.assertIn("what counts 3 things its items do not list (items lists 4)", runner(d)[1])
        # card 42's what counts its twelve items: clean
        d = example()
        d["cards"][1]["what"] = "Whether the twelve moved pages answer at their old web addresses."
        self.assertEqual(runner(d)[:2], (0, ""))
        # mutant: the what lint gone
        d = example()
        d["cards"][0]["what"] = "Which three steps of the docs build move to CI."
        script = mutant_runner("for (const x of setCounts(c.what, nOpts)) if (x >= 2 && x !== items.length)",
                               "for (const x of []) if (x)")
        self.assertNotIn("what counts", runner(d, script=script)[1])

    def test_the_page_itself_never_refuses_it(self):
        # the runner's alone, so an older published page still renders
        d = example()
        del d["cards"][1]["items"]
        self.assertEqual(run_page(d)["bad"], [])
        code, out, _ = runner(d)
        self.assertEqual(code, 1, out)
        self.assertIn("card 42: " + SET_REFUSAL + "12 things", out)

    def test_a_record_is_refused_the_same_way(self):
        r = record_of(example()["cards"][1])
        self.assertEqual(run_record(r), (0, ""))
        del r["items"]
        code, out = run_record(r)
        self.assertEqual(code, 1, out)
        self.assertIn("record 42: " + SET_REFUSAL + "12 things", out)

    def test_a_carried_over_card_gets_the_lint_until_it_is_revised(self):
        # the upgrader's marker names the rev it kept: while rev is that rev, the set is a lint (a lazy, seamless
        # upgrade keeps every rev); a writer's revision, a new rev, makes it a refusal again
        d = example()
        c = d["cards"][1]
        del c["items"]
        c["upgraded"] = {"from": "kit", "rev": c["rev"]}
        self.assertEqual(run_page(d)["bad"], [])
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 42: shape: " + SET_REFUSAL + "12 things", out)
        self.assertIn("carried over by the upgrader with its rev, so linted, and refused once revised with a new rev", out)
        r = record_of(c)
        self.assertEqual(run_record(r)[0], 2)
        c["rev"] = "2026-10-27T08:00:00Z"
        code, out, _ = runner(d)
        self.assertEqual(code, 1, out)
        self.assertIn("card 42: " + SET_REFUSAL + "12 things", out)
        # mutant: the marker read without its rev
        c["rev"] = "2026-10-27T08:00:00Z"
        script = mutant_runner("c.upgraded.rev === c.rev", "true")
        self.assertEqual(runner(d, script=script)[0], 2)
        # the page refuses a malformed marker
        for bad in ("kit", {"from": "kit"}, {"from": "kit", "rev": "yesterday"}, {"from": "", "rev": c["rev"]},
                    {"from": "hand", "rev": c["rev"]}, {"from": "Kit", "rev": c["rev"]}):
            with self.subTest(bad=bad):
                c["upgraded"] = bad
                self.assertTrue(any("upgraded must be {from, rev}" in b for b in run_page(d)["bad"]))

    def test_the_set_refusal_mutant(self):
        d = example()
        del d["cards"][1]["items"]
        script = mutant_runner("refuse = !!small.length && n < Math.max(...small) && !carried(c);", "refuse = false;")
        code, out, _ = runner(d, script=script)
        self.assertNotEqual(code, 1, out)

    def test_an_unlisted_count_in_those_places_points_to_items(self):
        d = example()
        d["cards"][0]["tldr"][0] = "Move four pages"
        three(d["cards"][0])["items"].append({"name": "Search settings", "about": "a configuration page"})
        d["cards"][0]["options"][0]["title"] = "Keep three pages"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn('lint: card 41: "three" counts things its context does not name: list the three things in '
                      "items, the What part", out)
        # the items' own number is named by the list: "four" is not linted
        self.assertNotIn('"four"', out)
        # outside those places the fix stays Context's
        d = example()
        d["cards"][0]["impact"]["wait"] = "the five pages wait"
        self.assertIn("say what the five things are, or list them, in context", runner(d)[1])

    def test_a_per_giving_the_recommended_option_alone_is_linted(self):
        d = example()
        d["cards"][1]["items"][0]["per"] = {"a": "redirects to its new address"}
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: card 42: impact: item 1 (Install the tool)'s per gives only the recommended option's "
                      "outcome", out)
        d["cards"][1]["items"][0]["per"]["b"] = "breaks"
        self.assertEqual(runner(d)[:2], (0, ""))
        # a per for another option alone is not the recommendation's
        d["cards"][1]["items"][0]["per"] = {"b": "breaks"}
        self.assertEqual(runner(d)[:2], (0, ""))
        # the recommended option and (z): it says what waiting does too
        d["cards"][1]["items"][0]["per"] = {"a": "redirects", "z": "stays where it is"}
        self.assertEqual(runner(d)[:2], (0, ""))
        script = mutant_runner("if (ks.length === 1 && ks[0] === c.rec)",
                               'if (ks.includes(c.rec) && ks.every(k => k === c.rec || k === "z"))')
        self.assertIn("per gives only the recommended", runner(d, script=script)[1])

    def test_the_id_lint_reads_the_what_part(self):
        for put, at in ((lambda c: c.__setitem__("what", "Whether KAPPA-3570 lands."), "(what)"),
                        (lambda c: c["items"][0].__setitem__("name", "KAPPA-3570 guide"), "(item 1)"),
                        (lambda c: c["items"][1].__setitem__("where", "KAPPA-3570"), "(item 2)"),
                        (lambda c: c["items"][2].__setitem__("about", "per KAPPA-3570"), "(item 3)"),
                        (lambda c: c["items"][0].__setitem__("per", {"a": "per KAPPA-3570", "b": "x"}), "(item 1)")):
            with self.subTest(at):
                d = example()
                put(d["cards"][1])
                code, out, _ = runner(d)
                self.assertEqual(code, 2, out)
                self.assertIn("lint: card 42: KAPPA-3570 looks like an id " + at, out)

    def test_the_what_part_counts_in_the_card_in_all(self):
        d = example()
        for x in d["cards"][1]["items"]:
            x["about"] = " ".join(["word"] * 80)
        code, out, _ = runner(d)
        self.assertIn("lint: card 42: depth: the card is ", out)
        script = mutant_runner("+ words(whatTexts(c)) + bg", "+ bg")
        self.assertNotIn("depth: the card is ", runner(d, script=script)[1])


def item_bullets(body):
    """A view's What item bullets: the bullet lines right under its **What:** line."""
    k = next((i for i, x in enumerate(body) if x.startswith("**What:**")), None)
    out = []
    for x in body[k + 1:] if k is not None else []:
        if not x.startswith("- "):
            break
        out.append(x)
    return out


def what_problems(where, body):
    """A view's What: one **What:** line, after Context (and its bullets) and before any fold above the
    Impact and the Impact; under it, item bullets only, each `- name — about`, none an option."""
    out = []
    ks = [i for i, x in enumerate(body) if x.startswith("**What:**")]
    if len(ks) != 1:
        return [f"{where}: {len(ks)} What lines"]
    k = ks[0]
    ctx = next((i for i, x in enumerate(body) if x.startswith("**Context:**")), None)
    imp = next((i for i, x in enumerate(body) if x.startswith(("**Impact:**", "▸ ", "▾ "))), None)
    if ctx is None or not ctx < k:
        out.append(f"{where}: What is not after Context")
    if imp is not None and not k < imp:
        out.append(f"{where}: What is not before the folds and the Impact")
    for x in item_bullets(body):
        if not ITEM_BULLET.match(x):
            out.append(f"{where}: an item bullet off its form: {x[:50]}")
    return out


class WhatPartChat(unittest.TestCase):

    def test_the_card_and_block_templates_put_what_after_context(self):
        text = RENDERING.read_text()
        card = fenced(text, "**N — Title as a question?**\n**Context:**")
        self.assertEqual(heads(card)[:3], ["Context", "What", "Impact"])
        self.assertEqual(what_problems("rendering.md card", card), [])
        self.assertTrue(item_bullets(card), "the card template shows a set's item bullet")
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:2], ["Context", "What"])
        self.assertEqual(what_problems("rendering.md block", block), [])

    def test_every_gallery_view_puts_what_after_context(self):
        for n, kind, body in views(GALLERY):
            self.assertEqual(what_problems(f"gallery.md:{n}", body), [])
        # mutant: a card in the old order, What before Context
        n, kind, body = next(v for v in views(GALLERY) if v[1] == "card")
        k = next(i for i, x in enumerate(body) if x.startswith("**What:**"))
        old = body[:1] + [body[k]] + [x for i, x in enumerate(body[1:], 1) if i != k]
        self.assertTrue(what_problems("mutant", old))

    def test_the_gallery_lists_a_sets_items_and_shows_the_count_alone_as_not_this(self):
        sets = [(n, body) for n, kind, body in views(GALLERY) if item_bullets(body)]
        self.assertTrue(sets, "no gallery card lists a set's items")
        n, body = sets[0]
        items = item_bullets(body)
        self.assertGreaterEqual(len(items), 3)
        # each option's own outcome where it differs, in letter order
        self.assertTrue(any(re.search(r"\*\(a\) [^*]+; \(b\) [^*]+\*$", x) for x in items), items)
        text = GALLERY.read_text()
        self.assertIn("*Not this: a What of ", text[text.index(body[0]):])
        # mutant: an option where an item bullet belongs
        k = next(i for i, x in enumerate(body) if x.startswith("**What:**"))
        self.assertTrue(what_problems("mutant", body[:k + 1] + ["- (a) Keep it — x"] + body[k + 1:]))

    def test_the_floor_and_the_cold_read_name_the_set(self):
        skill = " ".join(SKILL_MD.read_text().split())
        self.assertIn("for a set, every item it acts on, one bullet each under **What:**", skill)
        cold = " ".join(WORKSHEET.read_text().split())
        self.assertIn("could you name every item it acts on", cold)
        flat = " ".join(RENDERING.read_text().split())
        self.assertIn("**What:** after **Context:**", flat)

    def test_a_set_named_by_its_rule_passes_the_cold_read(self):
        cold = " ".join(WORKSHEET.read_text().split())
        self.assertIn("unless the card names the set by a rule that picks out its members", cold)
        # gallery 87 names its twelve pages by their rule, and says so
        text = GALLERY.read_text()
        s87 = text[text.index("**87 — "):text.index("## 29.")]
        self.assertIn("*The set is named by its rule, \"the pages that cite the retired setup guide\", rather than "
                      "listed", s87)

    def test_the_page_docs_state_the_rule_named_set_the_trust_boundary_and_the_gap(self):
        page = SKILL / "references"
        rule = ("A set named by a rule that picks out its members (*the pages that cite the retired setup guide*) keeps "
                "its count out of the checked places (the title, the first TLDR bullet, the option titles and lines), "
                "or lists its items.")
        for f in (page / "cards-schema.md", page / "writer-digest.md", SKILL / "SKILL.md"):
            self.assertIn(rule, " ".join(f.read_text().split()), f.name)
        # fix round 3: the label rule by its closed noun list, in one clause
        for f in (page / "cards-schema.md", page / "writer-digest.md"):
            self.assertIn("a numeral right after a label noun from a closed list", " ".join(f.read_text().split()), f.name)
        self.assertIn("a numeral after a label noun from a closed list (principle, step, tier, …), never after a verb",
                      " ".join((REFS / "rulings.md").read_text().split()))
        trust = "is the writer's self-check, not a gate, and the marker is the upgrader's alone"
        for f in (page / "writer-digest.md", REFS / "card-record.md"):
            self.assertIn(trust, " ".join(f.read_text().split()), f.name)
        legacy = " ".join((REFS / "legacy-cards.md").read_text().split())
        self.assertIn("data upgraded by an earlier upgrader, before the marker, carries none, so its set check is a "
                      "refusal. Re-upgrade it from its kit or legacy source", legacy)
        # the nits: the checked places named the same way
        for f in (page / "writer-digest.md", SKILL / "SKILL.md"):
            flat = " ".join(f.read_text().split())
            self.assertIn("first TLDR bullet", flat, f.name)
            self.assertIn("but (z)'s", flat, f.name)

    def test_the_rulings_mark_the_reversed_orders(self):
        flat = " ".join((REFS / "rulings.md").read_text().split())
        self.assertIn("Context absorbs What (decision 197 (a), the operator's answer 2026-10-08; reversed on the page "
                      "by answer 290 (a)", flat)
        self.assertIn("(the What line's place before Context reversed by answer 290 (a)", flat)
        self.assertIn("**The What part after Context, listing a set, both surfaces**", flat)


if __name__ == "__main__":
    unittest.main()
