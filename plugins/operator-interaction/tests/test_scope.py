"""The Scope line against the requirements (F8, answer 266 (b)), on both surfaces.

Three parts:

- the decision page (`decision-page` skill, under node): `scopePart` renders the record's
  `scope`, `{level, says}`, after the What part and any Finding and before the folds above the
  Impact, never folded: its level as a small boxed word (*required*, *shapes the work*, *outside
  the criteria*), then `says` through `fmt`. `check()` refuses a malformed scope, which also runs
  in the runner's `--record` mode;
- the pre-publish runner (`scripts/check_cards.js`, under node): the id lint and the cold read
  read the Scope's `says`, and it counts in the card in all;
- the chat card (the `decisions` skill): the **Scope:** line after **What:** and any
  **Finding:** in the card and block templates, its form `**Scope:** *level* — says`, on every
  gallery card that carries one.

Each check is proved by a mutation: a broken template, runner or text fails it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import sys
import unittest

from test_impact import NODE, example, finding_end
from test_context import runner, RECORD
from test_record import run_record, record_of
from test_items import mutant_runner
from test_chat_context import fenced, views, heads, GALLERY, RENDERING, SKILL_MD
from test_finding import one, mutant_page, HOSTILE


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the Scope's page and runner tests (ScopePage, ScopeRunner) "
              "are skipped, so its render, its check and its lints went untested", file=sys.stderr)


def c41(d):
    return next(c for c in d["cards"] if c["n"] == 41)


def scp(res, n):
    """The Scope part of card n, as the open card shows it: "" when there is none."""
    card = res["cards"][str(n)]["card"]
    m = re.search(r'<div class="scp">.*?</div>', card)
    return m.group(0) if m else ""


@unittest.skipUnless(NODE, "node is not installed")
class ScopePage(unittest.TestCase):

    def test_the_example_shows_card_41s_scope(self):
        res = one(example())
        self.assertEqual(res["bad"], [])
        self.assertEqual(scp(res, 41), '<div class="scp"><span class="lbl">Scope</span><p><span class="lvw sc-required">'
                         'required</span>any contributor can publish a docs change without waiting on one person, as the '
                         'docs brief asks</p></div>')
        self.assertEqual(scp(res, 42), "")
        self.assertEqual(scp(res, 43), "")
        # mutant: the part left out of the card
        res = one(example(), mutant_page("+findingPart(c)+scopePart(c)+", "+findingPart(c)+"))
        self.assertEqual(scp(res, 41), "")

    def test_each_level_shows_its_word(self):
        for level, word in (("required", "required"), ("shapes", "shapes the work"), ("outside", "outside the criteria")):
            with self.subTest(level):
                d = example()
                c41(d)["scope"] = {"level": level, "says": "the settings layout"}
                h = scp(one(d), 41)
                self.assertIn('<span class="lvw sc-%s">%s</span>the settings layout' % (level, word), h)
        # outside with no says, or a none one: its word alone
        for says in (None, "none"):
            d = example()
            c41(d)["scope"] = {"level": "outside"} if says is None else {"level": "outside", "says": says}
            res = one(d)
            self.assertEqual(res["bad"], [])
            self.assertEqual(scp(res, 41), '<div class="scp"><span class="lbl">Scope</span><p><span class="lvw '
                             'sc-outside">outside the criteria</span></p></div>')
        # mutant: the word table reads one level as another
        d = example()
        c41(d)["scope"] = {"level": "shapes", "says": "x"}
        h = scp(one(d, mutant_page('shapes:"shapes the work"', 'shapes:"required"')), 41)
        self.assertNotIn("shapes the work", h)

    def test_it_sits_after_what_and_the_finding_before_the_folds_and_is_never_folded(self):
        def problems(script=None, finding=False):
            d = example()
            if finding:
                c41(d)["finding"] = {"mechanism": "the laptop's cache served a stale build twice this month"}
            card = one(d, script)["cards"]["41"]["card"]
            if '<div class="scp">' not in card:
                return ["no scope"]
            at = card.index('<div class="scp">')
            out = []
            if not card.index('<div class="what">') < at:
                out.append("before What")
            if finding and not card.index('<div class="fnd">') < at:
                out.append("before the Finding")
            if not at < card.index('class="gfold afold"') or not at < card.index('class="impline"'):
                out.append("after the folds or the Impact")
            if card[:at].count("<details") - card[:at].count("</details>") != 1:
                out.append("inside a fold")
            return out
        self.assertEqual(problems(), [])
        self.assertEqual(problems(finding=True), [])
        # mutants: before What; before the Finding; inside the Assumptions fold
        self.assertTrue(problems(mutant_page("+whatPart(c)+findingPart(c)+scopePart(c)+",
                                             "+scopePart(c)+whatPart(c)+findingPart(c)+")))
        self.assertTrue(problems(mutant_page("+findingPart(c)+scopePart(c)+", "+scopePart(c)+findingPart(c)+"),
                                 finding=True))
        self.assertTrue(problems(mutant_page(
            "+scopePart(c)+openFold(c)+assumeFold(c,P)",
            "+openFold(c)+assumeFold(c,P).replace('<div>','<div>'+scopePart(c))")))

    def test_says_is_escaped(self):
        def problems(script=None):
            out = []
            for v in HOSTILE:
                d = example()
                c41(d)["scope"]["says"] = v
                h = scp(one(d, script), 41)
                if "<script" in h or "<img" in h:
                    out.append("%r renders raw" % v)
            return out
        self.assertEqual(problems(), [])
        # a slug in says is a mark, as in every text field
        d = example()
        c41(d)["scope"]["says"] = "as [[42]] asks"
        self.assertIn("slug", scp(one(d), 41))
        # mutant: says drawn raw
        self.assertTrue(problems(mutant_page("+(isTxt(s.says)&&shown(s.says)?fmt(s.says):'')",
                                             "+(isTxt(s.says)&&shown(s.says)?s.says:'')")))

    CASES = {
        "scope must be {level, says}, its level one of required, shapes or outside": [
            lambda c: c.__setitem__("scope", "required"),
            lambda c: c["scope"].__setitem__("level", "nice to have"),
            lambda c: c["scope"].__setitem__("level", "__proto__"),
            lambda c: c["scope"].__setitem__("level", "constructor"),
            lambda c: c["scope"].pop("level"),
        ],
        "scope says must be one line of text": [
            lambda c: c["scope"].__setitem__("says", "a\nb"),
            lambda c: c["scope"].__setitem__("says", 3),
        ],
        "scope says is missing: a required scope says the criterion": [
            lambda c: c["scope"].pop("says"),
            lambda c: c["scope"].__setitem__("says", "  "),
        ],
        "scope says is missing: a shapes scope says what in the work it shapes": [
            lambda c: c.__setitem__("scope", {"level": "shapes"}),
        ],
    }

    def test_check_refuses_a_malformed_scope(self):
        for needle, puts in self.CASES.items():
            for i, put in enumerate(puts):
                with self.subTest(needle=needle, i=i):
                    d = example()
                    put(c41(d))
                    bad = one(d)["bad"]
                    self.assertTrue(any(b.startswith("card 41: ") and needle in b for b in bad), bad)
        # outside needs no says
        d = example()
        c41(d)["scope"] = {"level": "outside"}
        self.assertEqual(one(d)["bad"], [])
        # mutants: the level test, the line test and the says test each gone
        d = example()
        c41(d)["scope"]["level"] = "nice to have"
        self.assertEqual(one(d, mutant_page("if(!isObj(s)||!isScopeLevel(s.level))", "if(!isObj(s))"))["bad"], [])
        d = example()
        c41(d)["scope"]["says"] = "a\nb"
        self.assertEqual(one(d, mutant_page("&&!(isStr(s.says)&&!LINE_BREAK.test(s.says))", "&&!isStr(s.says)"))["bad"], [])
        d = example()
        del c41(d)["scope"]["says"]
        self.assertEqual(one(d, mutant_page('else if(s.level!=="outside"&&!isTxt(s.says))', "else if(false)"))["bad"], [])


@unittest.skipUnless(NODE, "node is not installed")
class ScopeRunner(unittest.TestCase):

    def test_the_example_is_clean_and_so_is_its_record(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        self.assertEqual(run_record(record_of(c41(example()))), (0, ""))

    def test_a_record_with_a_malformed_scope_is_refused(self):
        rec = record_of(c41(example()))
        rec["scope"]["level"] = "nice to have"
        code, out = run_record(rec)
        self.assertEqual(code, 1, out)
        self.assertIn("record 41: scope must be {level, says}", out)

    def test_the_id_lint_reads_says(self):
        d = example()
        c41(d)["scope"]["says"] = "the brief's criterion OQ3"
        self.assertIn("lint: card 41: OQ3 looks like an id (scope)", runner(d)[1])
        js = mutant_runner('  put("scope", scopeTexts(c));\n', "")
        self.assertNotIn("OQ3 looks like an id", runner(d, script=js)[1])

    def test_the_cold_read_reads_says(self):
        d = example()
        c41(d)["scope"]["says"] = "the brief's seven criteria all hold"
        self.assertIn('lint: card 41: "seven" (the scope) counts things its context does not name', runner(d)[1])
        js = mutant_runner('terms(scopeTexts(c), " (the scope)");', "")
        self.assertNotIn("(the scope)", runner(d, script=js)[1])

    def test_says_counts_in_the_card_in_all(self):
        d = example()
        c41(d)["scope"]["says"] = " ".join(["word"] * 1400)
        self.assertIn("lint: card 41: depth: the card is", runner(d)[1])
        js = mutant_runner("+ words(scopeTexts(c)) ", "")
        self.assertNotIn("depth: the card is", runner(d, script=js)[1])


# the gallery's cards with a Scope line
SCOPE_CARDS = {98}
SCOPE_LINE = re.compile(r"^\*\*Scope:\*\* \*(required|shapes the work|outside the criteria)\*(?: — (\S.*))?$")


def scope_problems(where, body):
    """A view's Scope line against the rules: one at most; its form, a level word in italics and,
    on required and shapes, the text after it; after What and any Finding (with nothing else
    between), before the folds and the Impact."""
    at = [i for i, x in enumerate(body) if x.startswith("**Scope:**")]
    if not at:
        return []
    out = []
    if len(at) > 1:
        out.append(where + ": more than one Scope line")
    k = at[0]
    m = SCOPE_LINE.match(body[k])
    if not m:
        out.append(where + ": the Scope line is not `**Scope:** *level* — text`")
    elif m.group(1) != "outside the criteria" and not m.group(2):
        out.append(where + ": a %s Scope says nothing after its level" % m.group(1))
    w = next((i for i, x in enumerate(body) if x.startswith("**What:**")), None)
    if w is None or w > k:
        out.append(where + ": the Scope line is not after What")
    else:
        j = w + 1
        while j < k:
            if body[j].startswith("**Finding:**"):
                j = finding_end(body, j)
            elif body[j].startswith("- "):
                j += 1
            else:
                break
        if j != k:
            out.append(where + ": something but What's items and the Finding stands between What and the Scope")
    later = [i for i, x in enumerate(body) if x.startswith(("▸ ", "▾ ", "**Impact:**"))]
    if not later or min(later) < k:
        out.append(where + ": the Scope line is not before the folds and the Impact")
    return out


class ScopeChat(unittest.TestCase):

    def test_the_templates_put_the_scope_after_the_finding(self):
        text = RENDERING.read_text()
        card = fenced(text, "**N — Title as a question?**\n**Context:**")
        self.assertEqual(heads(card)[:5], ["Context", "What", "Finding", "Scope", "Impact"])
        k = next(i for i, x in enumerate(card) if x.startswith("**Scope:**"))
        self.assertTrue(card[k].startswith("**Scope:** *required* — "), card[k])
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:4], ["Context", "What", "Finding", "Scope"])
        flat = " ".join(text.split())
        self.assertIn("- **Scope:** wherever the work states requirements", flat)
        self.assertIn("answer 266 (b)", flat)
        for word in ("*required*", "*shapes the work*", "*outside the criteria*"):
            self.assertIn(word, flat)

    def test_every_gallery_scope_line_is_well_formed_and_placed(self):
        seen = set()
        for n, kind, body in views(GALLERY):
            if any(x.startswith("**Scope:**") for x in body):
                seen.add(int(re.match(r"^\*\*(\d+)", body[0]).group(1)))
            self.assertEqual(scope_problems(f"gallery.md:{n}", body), [])
        self.assertEqual(seen, SCOPE_CARDS)

    def test_the_scope_checks_fail_on_broken_cards(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**98 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("**Scope:**"))
        w = next(i for i, x in enumerate(body) if x.startswith("**What:**"))
        imp = next(i for i, x in enumerate(body) if x.startswith("**Impact:**"))
        mutants = {
            "before What": body[:w] + [body[k]] + body[w:k] + body[k + 1:],
            "after the Impact": body[:k] + body[k + 1:imp + 1] + [body[k]] + body[imp + 1:],
            "an unknown level": body[:k] + [body[k].replace("*required*", "*nice to have*")] + body[k + 1:],
            "no criterion": body[:k] + ["**Scope:** *required*"] + body[k + 1:],
            "no italics": body[:k] + [body[k].replace("*required*", "required")] + body[k + 1:],
            "twice": body[:k + 1] + [body[k]] + body[k + 1:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(scope_problems("mutant", b), name)
        # outside with no text passes
        self.assertEqual(scope_problems("outside", body[:k] + ["**Scope:** *outside the criteria*"] + body[k + 1:]), [])

    def test_the_floor_the_worksheet_the_record_and_the_ruling_say_it(self):
        skill = " ".join(SKILL_MD.read_text().split())
        self.assertIn("11. **Its scope**, wherever the work states requirements", skill)
        self.assertIn("**Scope:** (*required* and the criterion, *shapes the work* and what, or *outside the criteria*)", skill)
        refs = SKILL_MD.parent / "references"
        self.assertIn("| Requirements | the work's stated requirements", (refs / "worksheet.md").read_text())
        record = RECORD.read_text()
        self.assertRegex(record, r"\n\| `scope` \| `\{level, says\}` \| optional \| \*\*Scope:\*\*")
        # no longer among the fields an upgraded card may carry unshown
        upgraded = record.split("## Fields an upgraded card may already carry")[1].split("\n## ")[0]
        self.assertNotIn("`scope` (`{level, says}`)", upgraded)
        rulings = (refs / "rulings.md").read_text()
        self.assertIn("- **A Scope line against the requirements, both surfaces** (2026-10-20, answer 266 (b)", rulings)


if __name__ == "__main__":
    unittest.main()
