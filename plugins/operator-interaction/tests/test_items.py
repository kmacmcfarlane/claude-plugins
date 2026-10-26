"""The What part (F6, answer 290 (a)): what is decided, after Context, and for a set every item.

Three parts:

- the decision page (`decision-page` skill, under node): `whatPart` renders `what` and the set's
  `items` after Context and before the folds above the Impact, never folded, labelled *What · N
  items*, each item's name, where, about and per (its outcome under each option, in letter order),
  every field escaped; `check()` refuses a malformed `what` or `items`;
- the pre-publish runner (`scripts/check_cards.js`, under node): the set refusal (a card that counts
  two or more things where it says what is decided, with no `items` list of that length; the
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


@unittest.skipUnless(NODE, "node is not installed")
class WhatPartRunner(unittest.TestCase):

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_a_count_where_the_card_says_what_is_decided_needs_its_items(self):
        places = {
            "t": lambda c: c.__setitem__("t", "Move three pages"),
            "tldr": lambda c: c["tldr"].append("Move three pages"),
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

    def test_items_of_another_length_are_refused_and_named(self):
        d = example()
        d["cards"][0]["tldr"].append("Move three pages")
        three(d["cards"][0])["items"].pop()
        code, out, _ = runner(d)
        self.assertEqual(code, 1, out)
        self.assertIn("card 41: " + SET_REFUSAL + "3 things where it says what is decided, but items lists 2", out)

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

    def test_a_numbered_label_is_not_a_set(self):
        # "principle 3", "step 2": a numeral after a word labels one thing; "Fix 3 bugs" counts three
        for t, refused in (("Clarify principle 3", False), ("as step 2 did", False),
                           ("Fix 3 bugs", True), ("Fix the 3 failing tests", True)):
            with self.subTest(t):
                d = example()
                d["cards"][0]["options"][0]["line"] = t
                out = runner(d)[1]
                self.assertEqual(SET_REFUSAL in out, refused, out)
        # mutant: the label rule gone, "principle 3" is refused as a set
        d = example()
        d["cards"][0]["options"][0]["line"] = "Clarify principle 3"
        script = mutant_runner("const LABEL_NUM = /([A-Za-z]+)\\s+$/;", "const LABEL_NUM = /$^/;")
        self.assertIn(SET_REFUSAL, runner(d, script=script)[1])

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

    def test_the_set_refusal_mutant(self):
        d = example()
        del d["cards"][1]["items"]
        script = mutant_runner("if (seen.size && !seen.has(n)) {", "if (false) {")
        code, out, _ = runner(d, script=script)
        self.assertNotEqual(code, 1, out)
        self.assertNotIn(SET_REFUSAL, out)

    def test_an_unlisted_count_in_those_places_points_to_items(self):
        d = example()
        d["cards"][0]["tldr"].append("Move three pages")
        three(d["cards"][0])
        d["cards"][0]["options"][0]["title"] = "Keep five pages"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn('lint: card 41: "five" counts things its context does not name: list the five things in '
                      "items, the What part", out)
        # the items' own number is named by the list: "three" is not linted
        self.assertNotIn('"three"', out)
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


if __name__ == "__main__":
    unittest.main()
