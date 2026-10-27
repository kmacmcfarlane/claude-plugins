"""The Likelihood and Best response? on a risk decision (F9, answers 267 (a), widened, and 339 (a)),
on both surfaces.

Three parts:

- the decision page (`decision-page` skill, under node): `likelihoodPart` renders the record's
  `likelihood`, `{kind, seen}`, and `best` after the Scope and before the folds above the Impact,
  never folded: the kind as a small boxed word (*observed*, *evidence*), then `seen`, then
  **Best response?** and `best` on a line of its own, each through `fmt`. `check()` refuses a
  malformed likelihood and a `best` with no likelihood, which also runs in the runner's
  `--record` mode;
- the pre-publish runner (`scripts/check_cards.js`, under node): the id lint reads `seen` and
  `best`; the cold read reads `best` whole and `seen` for named things (an observed count in it is
  its fact, not a set Context names); both count in the card in all;
- the chat card (the `decisions` skill): the **Likelihood:** line and its **Best response?:**
  line after **Scope:** in the card and block templates, their form, and on every gallery risk
  card a line that names its event and gives a fact with its source, or the evidence and what
  would settle it: never a bare *no data*, an estimate, or a percentage with no source.

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
        print("WARNING: node is not installed: the Likelihood's page and runner tests (LikelihoodPage, "
              "LikelihoodRunner) are skipped, so its render, its check and its lints went untested", file=sys.stderr)


def c42(d):
    return next(c for c in d["cards"] if c["n"] == 42)


def lkh(res, n):
    """The Likelihood part of card n, as the open card shows it: "" when there is none."""
    card = res["cards"][str(n)]["card"]
    m = re.search(r'<div class="lkh">.*?</div>', card)
    return m.group(0) if m else ""


SEEN = ("readers followed old links to the moved pages about 300 times last month, mostly from other sites and "
        "bookmarks (the site's access log)")
BEST = "yes — only a redirect keeps those links working; a hint on the not-found page still loses the reader for a click"


@unittest.skipUnless(NODE, "node is not installed")
class LikelihoodPage(unittest.TestCase):

    def test_the_example_shows_card_42s_likelihood_and_best_response(self):
        res = one(example())
        self.assertEqual(res["bad"], [])
        self.assertEqual(lkh(res, 42), '<div class="lkh"><span class="lbl">Likelihood</span><p><span class="lvw lk-observed">'
                         'observed</span>' + SEEN.replace("'", "&#39;") + '</p><span class="lbl">Best response?</span><p>'
                         + BEST + '</p></div>')
        self.assertEqual(lkh(res, 41), "")
        self.assertEqual(lkh(res, 43), "")
        # mutants: the part left out of the card; Best response? left out of the part
        res = one(example(), mutant_page("+scopePart(c)+likelihoodPart(c)+", "+scopePart(c)+"))
        self.assertEqual(lkh(res, 42), "")
        res = one(example(), mutant_page("+(b?'<span class=\"lbl\">Best response?</span><p>'+fmt(b)+'</p>':'')", ""))
        self.assertNotIn("Best response?", lkh(res, 42))

    def test_each_kind_shows_its_word_and_none_is_not_shown(self):
        for kind in ("observed", "evidence"):
            with self.subTest(kind):
                d = example()
                c42(d)["likelihood"]["kind"] = kind
                self.assertIn('<span class="lvw lk-%s">%s</span>' % (kind, kind), lkh(one(d), 42))
        # a none best: no Best response? line; a none seen: no part at all
        d = example()
        c42(d)["best"] = "n/a"
        h = lkh(one(d), 42)
        self.assertTrue(h)
        self.assertNotIn("Best response?", h)
        d = example()
        c42(d)["likelihood"]["seen"] = "none"
        self.assertEqual(lkh(one(d), 42), "")
        # mutant: a none seen shown
        script = mutant_page("&&isTxt(c.likelihood.seen)&&shown(c.likelihood.seen)?c.likelihood:null",
                             "&&isTxt(c.likelihood.seen)?c.likelihood:null")
        self.assertNotEqual(lkh(one(d, script), 42), "")

    def test_it_sits_after_the_scope_before_the_folds_and_is_never_folded(self):
        def problems(script=None):
            d = example()
            c42(d)["scope"] = {"level": "outside"}
            card = one(d, script)["cards"]["42"]["card"]
            if '<div class="lkh">' not in card:
                return ["no likelihood"]
            at = card.index('<div class="lkh">')
            out = []
            if not card.index('<div class="what">') < at or not card.index('<div class="scp">') < at:
                out.append("before What or the Scope")
            if not at < card.index('class="gfold afold"') or not at < card.index('class="impline"'):
                out.append("after the folds or the Impact")
            if card[:at].count("<details") - card[:at].count("</details>") != 1:
                out.append("inside a fold")
            return out
        self.assertEqual(problems(), [])
        # mutants: before the Scope; inside the Assumptions fold
        self.assertTrue(problems(mutant_page("+scopePart(c)+likelihoodPart(c)+", "+likelihoodPart(c)+scopePart(c)+")))
        self.assertTrue(problems(mutant_page(
            "+likelihoodPart(c)+openFold(c)+assumeFold(c,P)",
            "+openFold(c)+assumeFold(c,P).replace('<div>','<div>'+likelihoodPart(c))")))

    def test_seen_and_best_are_escaped(self):
        def problems(script=None):
            out = []
            for v in HOSTILE:
                d = example()
                c42(d)["likelihood"]["seen"] = v
                c42(d)["best"] = v
                h = lkh(one(d, script), 42)
                if "<script" in h or "<img" in h:
                    out.append("%r renders raw" % v)
            return out
        self.assertEqual(problems(), [])
        # mutants: seen drawn raw; best drawn raw
        self.assertTrue(problems(mutant_page("+'</span>'+fmt(l.seen)+'</p>'", "+'</span>'+l.seen+'</p>'")))
        self.assertTrue(problems(mutant_page("Best response?</span><p>'+fmt(b)+'</p>'", "Best response?</span><p>'+b+'</p>'")))

    CASES = {
        "likelihood must be {kind, seen}, its kind observed or evidence": [
            lambda c: c.__setitem__("likelihood", "observed"),
            lambda c: c["likelihood"].__setitem__("kind", "estimated"),
            lambda c: c["likelihood"].pop("kind"),
        ],
        "likelihood needs its seen": [
            lambda c: c["likelihood"].pop("seen"),
            lambda c: c["likelihood"].__setitem__("seen", " "),
            lambda c: c["likelihood"].__setitem__("seen", 3),
        ],
        "likelihood seen must be one line of text": [
            lambda c: c["likelihood"].__setitem__("seen", "a\nb"),
        ],
        "best must be one line of text": [
            lambda c: c.__setitem__("best", "a\u2028b"),
            lambda c: c.__setitem__("best", ["yes"]),
        ],
        "best needs likelihood": [
            lambda c: c.pop("likelihood"),
        ],
    }

    def test_check_refuses_a_malformed_likelihood_or_best(self):
        for needle, puts in self.CASES.items():
            for i, put in enumerate(puts):
                with self.subTest(needle=needle, i=i):
                    d = example()
                    put(c42(d))
                    bad = one(d)["bad"]
                    self.assertTrue(any(b.startswith("card 42: ") and needle in b for b in bad), bad)
        # a likelihood with no best passes
        d = example()
        del c42(d)["best"]
        self.assertEqual(one(d)["bad"], [])
        # mutants: each test gone
        cases = [
            (lambda c: c["likelihood"].__setitem__("kind", "estimated"),
             "if(!isObj(l)||!LIKELIHOOD_KINDS.includes(l.kind))", "if(!isObj(l))"),
            (lambda c: c["likelihood"].pop("seen"),
             "else if(!isTxt(l.seen))bad.push", "else if(false)bad.push"),
            (lambda c: c["likelihood"].__setitem__("seen", "a\nb"),
             "else if(LINE_BREAK.test(l.seen))", "else if(false)"),
            (lambda c: c.__setitem__("best", "a\nb"),
             "if(!(isStr(c.best)&&!LINE_BREAK.test(c.best)))", "if(!isStr(c.best))"),
            (lambda c: c.pop("likelihood"),
             "else if(c.likelihood==null)", "else if(false)"),
        ]
        for put, old, new in cases:
            with self.subTest(old):
                d = example()
                put(c42(d))
                self.assertEqual(one(d, mutant_page(old, new))["bad"], [])


@unittest.skipUnless(NODE, "node is not installed")
class LikelihoodRunner(unittest.TestCase):

    def test_the_example_is_clean_and_so_is_its_record(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        self.assertEqual(run_record(record_of(c42(example()))), (0, ""))

    def test_a_record_with_best_and_no_likelihood_is_refused(self):
        rec = record_of(c42(example()))
        del rec["likelihood"]
        code, out = run_record(rec)
        self.assertEqual(code, 1, out)
        self.assertIn("record 42: best needs likelihood", out)

    def test_the_id_lint_reads_seen_and_best(self):
        for put in (lambda c: c["likelihood"].__setitem__("seen", "the outage OQ3 came back twice"),
                    lambda c: c.__setitem__("best", "no: OQ3 covers it")):
            d = example()
            put(c42(d))
            self.assertIn("lint: card 42: OQ3 looks like an id (likelihood)", runner(d)[1])
            js = mutant_runner('  put("likelihood", likelihoodTexts(c));\n', "")
            self.assertNotIn("OQ3 looks like an id", runner(d, script=js)[1])

    def test_the_cold_read_reads_best_whole_and_seen_for_named_things(self):
        # best: a count Context does not name
        d = example()
        c42(d)["best"] = "no: seven other pages break the same way"
        self.assertIn('lint: card 42: "seven" (the likelihood) counts things its context does not name', runner(d)[1])
        js = mutant_runner('if (b) terms([b], " (the likelihood)");', "")
        self.assertNotIn("(the likelihood)", runner(d, script=js)[1])
        # seen: a named thing Context does not gloss
        d = example()
        c42(d)["likelihood"]["seen"] = "readers hit old links 300 times last month in the preview mode (the access log)"
        out = runner(d)[1]
        self.assertIn('lint: card 42: "preview mode" (the likelihood) is not glossed in its context', out)
        # seen's observed count is its fact: no count lint on it
        self.assertNotIn('"300"', out)
        js = mutant_runner('if (l) terms([l.seen], " (the likelihood)", named, undefined, false);',
                           'if (l) terms([l.seen], " (the likelihood)", named, undefined, true);')
        self.assertIn('"300" (the likelihood) counts things', runner(d, script=js)[1])
        js = mutant_runner('if (l) terms([l.seen], " (the likelihood)", named, undefined, false);', "")
        self.assertNotIn("preview mode", runner(d, script=js)[1])

    def lk_lints(self, likelihood, script=None):
        d = example()
        c42(d)["likelihood"] = likelihood
        return [x for x in runner(d, **({"script": script} if script else {}))[1].splitlines()
                if x.startswith("lint: card 42: impact: ") and ("likelihood" in x or "best" in x)]

    def test_the_likelihood_lint_fires_on_an_estimate_a_percentage_and_no_source(self):
        out = self.lk_lints({"kind": "observed", "seen": "a 40% chance the old links break again, I am fairly confident"})
        text = "\n".join(out)
        self.assertIn('the likelihood holds an estimate ("chance")', text)
        self.assertIn('the likelihood gives a share ("%") with no source in brackets beside it', text)
        self.assertIn("an observed likelihood ends on no source in brackets", text)
        self.assertEqual(len(out), 3, out)

    def test_the_likelihood_lint_fires_on_no_data(self):
        out = self.lk_lints({"kind": "evidence", "seen": "no data"})
        self.assertEqual(len(out), 1, out)
        self.assertIn('the likelihood says only "no data"', out[0])
        self.assertIn("a bare no data is never the line", out[0])

    def test_the_likelihood_lint_fires_on_percent_in_words_and_a_carried_basis_word(self):
        out = "\n".join(self.lk_lints({"kind": "evidence", "seen": "(estimated) the disk fills in about three months; "
                                                                     "a week of usage graphs would show it"}))
        self.assertIn('opens on a carried-over basis word ("(estimated)")', out)
        out = "\n".join(self.lk_lints({"kind": "observed", "seen": "readers hit old links (access log) on two percent of visits"}))
        self.assertIn('gives a share ("percent")', out)
        # a percentage with its source after it, an observed fact ending on its source, and an evidence line: clean
        for lk in ({"kind": "observed", "seen": "old links were 2 percent of last month's visits (the site's access log)"},
                   {"kind": "evidence", "seen": "no log covers the old links; a week of the access log would show it"}):
            self.assertEqual(self.lk_lints(lk), [], lk)

    def test_the_finish_round_probes(self):
        def lints(kind, seen):
            return self.lk_lints({"kind": kind, "seen": seen})

        def has(kind, seen, needle):
            out = "\n".join(lints(kind, seen))
            self.assertIn(needle, out, seen)
        # 1. estimate words
        for seen in ("a high probability the disk fills; a week of usage graphs would show it",
                     "the disk almost certainly fills; a week of usage graphs would show it",
                     "I'd guess the disk fills; a week of usage graphs would show it",
                     "maybe the disk fills; a week of usage graphs would show it"):
            has("evidence", seen, "the likelihood holds an estimate")
        # 2. a basis word only on evidence, never (observed); a bracketed name is no basis word
        has("evidence", "(estimated) the disk fills; a week of usage graphs would show it", "carried-over basis word")
        for kind in ("observed", "evidence"):
            self.assertFalse([x for x in lints(kind, "(CI) fails on every PR touching docs, 14 of 14 (CI history)")
                              if "basis word" in x], kind)
        self.assertFalse([x for x in lints("observed", "(estimated) the disk fills in three months (usage graphs)")
                          if "basis word" in x])
        # 3. an estimate word in quoted text is the source's, not the writer's
        self.assertEqual(lints("observed", 'the log shows "connection likely reset" on every retry (ops log)'), [])
        # 4. a share inside a bracket that holds a word is sourced
        self.assertEqual(lints("observed", "failed on 3 of 40 deploys (CI history, 7.5%)"), [])
        has("observed", "a 40% chance the old links break again, I am fairly confident", "gives a share")
        # 5. no-data phrasings
        for seen in ("no data available", "no data yet", "none known"):
            has("evidence", seen, "a bare no data is never the line")
        # 6. a ratio in words, unsourced only
        has("evidence", "nine in ten uploads fail; a week of logs would show it", 'gives a share ("nine in ten")')
        self.assertEqual(lints("observed", "nine in ten uploads fail (CI history)"), [])

    def test_the_finish_round_mutants(self):
        cases = [
            # the new estimate words gone
            ({"kind": "evidence", "seen": "maybe the disk fills; a week of graphs would show it"},
             "|maybe|perhaps|almost certain(ly)?|guess(ed)?|presumabl[ey])", ")", False),
            # quoted text read again
            ({"kind": "observed", "seen": 'the log shows "connection likely reset" on every retry (ops log)'},
             "const e = unquoted(s).match(LK_ESTIMATE);", "const e = s.match(LK_ESTIMATE);", True),
            # the basis word on any kind
            ({"kind": "observed", "seen": "(estimated) the disk fills in three months (usage graphs)"},
             'if (l.kind === "evidence" && LK_CARRIED.test(s))', "if (LK_CARRIED.test(s))", True),
            # a share inside a worded bracket no longer sourced
            ({"kind": "observed", "seen": "failed on 3 of 40 deploys (CI history, 7.5%)"},
             "if (/[A-Za-z]{2,}/.test(inner.replace(m[0], \" \"))) continue;", "", True),
            # the ratio in words gone
            ({"kind": "evidence", "seen": "nine in ten uploads fail; a week of logs would show it"},
             "|\\b\\w+ in (?:ten|a hundred|\\d+)\\b/gi", "/gi", False),
            # the new no-data phrasings gone
            ({"kind": "evidence", "seen": "none known"},
             "|unknown|not known|none known|tbd)", "|unknown|not known)", False),
        ]
        for lk, old, new, lints_under_mutant in cases:
            with self.subTest(old):
                before, after = self.lk_lints(lk), self.lk_lints(lk, mutant_runner(old, new))
                if lints_under_mutant:
                    self.assertEqual(before, [], lk)
                    self.assertTrue(after, lk)
                else:
                    self.assertTrue(before, lk)
                    self.assertEqual(after, [], lk)

    def test_each_likelihood_lint_is_proved_by_a_mutant(self):
        cases = [
            ({"kind": "evidence", "seen": "no data"}, "if (LK_NO_DATA.test(s))", "if (false)"),
            ({"kind": "evidence", "seen": "outages are likely; a week of logs would show it"},
             "if (e) say(", "if (false) say("),
            ({"kind": "evidence", "seen": "down 2% of the time; a week of logs would show it"},
             "if (p) say(", "if (false) say("),
            ({"kind": "evidence", "seen": "(estimated) the disk fills; a week of graphs would show it"},
             'if (l.kind === "evidence" && LK_CARRIED.test(s))', "if (false)"),
            ({"kind": "observed", "seen": "readers hit the old links about 300 times last month"},
             'if (l.kind === "observed" && !LK_SOURCE_END.test(s))', "if (false)"),
            ({"kind": "evidence", "seen": "outages are likely; a week of logs would show it"},
             "  likelihoodLint(c, say);\n", ""),
        ]
        for lk, old, new in cases:
            with self.subTest(old):
                self.assertTrue(self.lk_lints(lk), lk)
                self.assertEqual(self.lk_lints(lk, mutant_runner(old, new)), [], lk)

    def test_a_new_card_with_no_best_is_linted_but_not_one_carried_over(self):
        d = example()
        del c42(d)["best"]
        out = runner(d)[1]
        self.assertIn("lint: card 42: impact: the likelihood has no best", out)
        # a none best is not shown, so it counts as missing
        d = example()
        c42(d)["best"] = "n/a"
        self.assertIn("the likelihood has no best", runner(d)[1])
        # carried over by the upgrader with its rev: no lint; revised with a new rev: the lint again
        d = example()
        del c42(d)["best"]
        c42(d)["upgraded"] = {"from": "kit", "rev": c42(d)["rev"]}
        self.assertNotIn("has no best", runner(d)[1])
        c42(d)["upgraded"]["rev"] = "2026-01-01T00:00:00Z"
        self.assertIn("has no best", runner(d)[1])
        # mutants: the best lint gone; the carried-over skip gone
        d = example()
        del c42(d)["best"]
        self.assertNotIn("has no best", runner(d, script=mutant_runner("if (!page.bestOf(c) && !carried(c))", "if (false)"))[1])
        c42(d)["upgraded"] = {"from": "kit", "rev": c42(d)["rev"]}
        self.assertIn("has no best", runner(d, script=mutant_runner("if (!page.bestOf(c) && !carried(c))",
                                                                   "if (!page.bestOf(c))"))[1])

    def test_the_digest_and_the_record_say_best_is_owed_by_a_new_card(self):
        for path in (RECORD, RECORD.parent.parent.parent / "decision-page" / "references" / "writer-digest.md"):
            self.assertIn("of a new card (lint); needs `likelihood`", path.read_text(), path)

    def test_seen_and_best_count_in_the_card_in_all(self):
        for put in (lambda c: c["likelihood"].__setitem__("seen", " ".join(["word"] * 1400)),
                    lambda c: c.__setitem__("best", " ".join(["word"] * 1400))):
            d = example()
            put(c42(d))
            self.assertIn("lint: card 42: depth: the card is", runner(d)[1])
            js = mutant_runner("+ words(likelihoodTexts(c)) ", "")
            self.assertNotIn("depth: the card is", runner(d, script=js)[1])


# the gallery's risk cards, with a Likelihood line
LIKELIHOOD_CARDS = {99}
LIKELIHOOD_LINE = re.compile(r"^\*\*Likelihood:\*\* \*\((observed|evidence)\)\* (\S.*)$")
BEST_LINE = re.compile(r"^\*\*Best response\?:\*\* (\S.*)$")
NO_DATA = re.compile(r"^\W*(no data|unknown|not known|none)\W*$", re.I)
# the runner's own patterns (check_cards.js, LK_ESTIMATE and LK_PERCENT): an estimate word; a percentage ("%" or
# "percent") with no bracketed source after it
ESTIMATE = re.compile(r"\b(likely|unlikely|probab(ly|le|ility|ilities)|chances?|odds|maybe|perhaps|almost certain(ly)?|guess(ed)?|presumabl[ey])\b", re.I)
PERCENT = re.compile(r"(%|\bper\s?cent\b)(?![\s\S]*\()", re.I)
# Best response?'s one form: its yes or no, then a dash (`no — …`), as rendering.md's example has it
BEST_YES_NO = re.compile(r"^(yes|no|partly)\b", re.I)
BEST_FORM = re.compile(r"^(yes|no|partly) — \S", re.I)
NUMBER = re.compile(r"\b(\d+|once|twice|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|never)\b", re.I)


def likelihood_problems(where, body):
    """A view's Likelihood and Best response? against the rules: at most one Likelihood line, its
    form `**Likelihood:** *(kind)* text`; observed: a fact with its source in brackets; evidence: the
    evidence and what would settle it; never a bare no data, an estimate, or a percentage with no
    source; a Best response? line right under it, and none without it; after What, any Finding and
    any Scope, before the folds and the Impact."""
    at = [i for i, x in enumerate(body) if x.startswith("**Likelihood:**")]
    bests = [i for i, x in enumerate(body) if x.startswith("**Best response?:**")]
    if not at:
        return [where + ": a Best response? with no Likelihood"] if bests else []
    out = []
    if len(at) > 1:
        out.append(where + ": more than one Likelihood line")
    k = at[0]
    m = LIKELIHOOD_LINE.match(body[k])
    if not m:
        out.append(where + ": the Likelihood line is not `**Likelihood:** *(kind)* text`")
    else:
        kind, text = m.groups()
        if NO_DATA.match(text):
            out.append(where + ": a bare no data")
        if ESTIMATE.search(text):
            out.append(where + ": an estimate, not a fact")
        if PERCENT.search(text):
            out.append(where + ": a percentage with no source")
        if kind == "observed" and not (NUMBER.search(text) and re.search(r"\([^)]+\)\s*$", text)):
            out.append(where + ": an observed Likelihood with no fact and its source in brackets")
        if kind == "evidence" and " would " not in " " + text + " ":
            out.append(where + ": an evidence Likelihood that does not say what would settle it")
        if len(text.split()) < 8:
            out.append(where + ": a Likelihood too short to name its event and its fact")
    if bests != [k + 1] or not BEST_LINE.match(body[k + 1]):
        out.append(where + ": no Best response? line right under the Likelihood")
    else:
        b = BEST_LINE.match(body[k + 1]).group(1)
        if BEST_YES_NO.match(b) and not BEST_FORM.match(b):
            out.append(where + ": Best response? opens on its yes or no with no dash after it: `no — …`")
    w = next((i for i, x in enumerate(body) if x.startswith("**What:**")), None)
    if w is None or w > k:
        out.append(where + ": the Likelihood is not after What")
    else:
        j = w + 1
        while j < k:
            if body[j].startswith("**Finding:**"):
                j = finding_end(body, j)
            elif body[j].startswith(("- ", "**Scope:**")):
                j += 1
            else:
                break
        if j != k:
            out.append(where + ": something but What's items, the Finding and the Scope stands before the Likelihood")
    later = [i for i, x in enumerate(body) if x.startswith(("▸ ", "▾ ", "**Impact:**"))]
    if not later or min(later) < k:
        out.append(where + ": the Likelihood is not before the folds and the Impact")
    return out


def ruling_problems(rulings):
    """The 267 ruling's entry keeps the operator's words apart from the designs: the percentage rule and the order of
    other facts sit in its designs clause, labelled a reading of answer 267's words."""
    entry = " ".join(rulings.split("- **Likelihood, widened, and Best response?")[1].split("\n- **")[0].split())
    if "Designs made in planning and build, not the operator's:" not in entry:
        return ["no designs clause"]
    words, designs = entry.split("Designs made in planning and build, not the operator's:", 1)
    out = []
    if "a reading of answer 267's words" not in designs:
        out.append("the order of facts is not labelled a reading of answer 267's words")
    for part in ("a percentage only as an observed share", "when it last happened, an observed share"):
        if part in words:
            out.append("%r stands among the operator's words" % part)
        if part not in designs:
            out.append("%r is not in the designs clause" % part)
    return out


class LikelihoodChat(unittest.TestCase):

    def test_the_templates_put_the_likelihood_after_the_scope(self):
        text = RENDERING.read_text()
        card = fenced(text, "**N — Title as a question?**\n**Context:**")
        self.assertEqual(heads(card)[:6], ["Context", "What", "Finding", "Scope", "Likelihood", "Impact"])
        k = next(i for i, x in enumerate(card) if x.startswith("**Likelihood:**"))
        self.assertTrue(card[k].startswith("**Likelihood:** *(observed)* the event it counts"), card[k])
        self.assertTrue(card[k + 1].startswith("**Best response?:** whether acting here"), card[k + 1])
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:5], ["Context", "What", "Finding", "Scope", "Likelihood"])
        flat = " ".join(text.split())
        self.assertIn("- **Likelihood:** on a **risk decision**", flat)
        self.assertIn("- **Best response?:** the Likelihood part's second line", flat)
        self.assertIn("answer 339 (a)", flat)

    def test_every_gallery_risk_card_carries_a_sound_likelihood(self):
        seen = set()
        for n, kind, body in views(GALLERY):
            if any(x.startswith("**Likelihood:**") for x in body):
                seen.add(int(re.match(r"^\*\*(\d+)", body[0]).group(1)))
            self.assertEqual(likelihood_problems(f"gallery.md:{n}", body), [])
        self.assertEqual(seen, LIKELIHOOD_CARDS)

    def test_the_gallery_risk_card_names_its_event(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**99 — "))
        line = next(x for x in body if x.startswith("**Likelihood:**"))
        # the event it counts, in plain words, before the fact
        self.assertRegex(line, r"\*\(observed\)\* the payment provider went down twice in the last twelve months")

    def test_the_likelihood_checks_fail_on_broken_cards(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**99 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("**Likelihood:**"))
        w = next(i for i, x in enumerate(body) if x.startswith("**What:**"))
        imp = next(i for i, x in enumerate(body) if x.startswith("**Impact:**"))
        swap = lambda s: body[:k] + [s] + body[k + 1:]
        mutants = {
            "no data": swap("**Likelihood:** *(evidence)* no data"),
            "an estimate": swap("**Likelihood:** *(observed)* outages at the payment provider are unlikely, twice a year (a guess)"),
            "a percentage with no source": swap("**Likelihood:** *(observed)* the payment provider is down 2% of the time, at most"),
            "a percentage with its bracket before it": swap("**Likelihood:** *(observed)* the provider (its status page) is down 2% of the time, at most"),
            "a percent in words with no source": swap("**Likelihood:** *(observed)* the payment provider (twice) is down two percent of the time"),
            "Best response? with no dash": body[:k + 1] + [body[k + 1].replace("no — ", "no: ")] + body[k + 2:],
            "observed with no source": swap("**Likelihood:** *(observed)* the payment provider went down twice in the last twelve months"),
            "evidence with nothing to settle it": swap("**Likelihood:** *(evidence)* no outage log covers the provider before this year at all"),
            "an unknown kind": swap(body[k].replace("*(observed)*", "*(estimated)*")),
            "no Best response?": body[:k + 1] + body[k + 2:],
            "Best response? alone": body[:k] + body[k + 1:],
            "before What": body[:w] + body[k:k + 2] + body[w:k] + body[k + 2:],
            "after the Impact": body[:k] + body[k + 2:imp + 1] + body[k:k + 2] + body[imp + 1:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(likelihood_problems("mutant", b), name)
        # the evidence form, with what would settle it, passes
        ok = swap("**Likelihood:** *(evidence)* no outage log covers the provider before this year; its status page would show the last two years")
        self.assertEqual(likelihood_problems("evidence", ok), [])
        # a percentage with its source in brackets after it passes
        ok = swap("**Likelihood:** *(observed)* the payment provider was down for 0.02% of last year's minutes (its status page)")
        self.assertEqual(likelihood_problems("percent", ok), [])

    def test_rendering_and_the_gallery_write_best_response_one_way(self):
        flat = " ".join(RENDERING.read_text().split())
        self.assertIn("(**Best response?:** no — a queued retry covers both outages;", flat)
        for line in GALLERY.read_text().splitlines():
            m = BEST_LINE.match(line)
            if m and BEST_YES_NO.match(m.group(1)):
                self.assertRegex(m.group(1), BEST_FORM, line)

    def test_the_floor_the_worksheet_the_evidence_rule_the_record_and_the_ruling_say_it(self):
        skill = " ".join(SKILL_MD.read_text().split())
        self.assertIn("12. **Its likelihood**, on a risk decision", skill)
        refs = SKILL_MD.parent / "references"
        ws = " ".join((refs / "worksheet.md").read_text().split())
        self.assertIn("| Risk | whether the options trade against a failure", ws)
        self.assertIn("does its **Likelihood:** name what it is the likelihood of", ws)
        eb = " ".join((refs / "evidence-basis.md").read_text().split())
        self.assertIn("A bare *no data* is never the line", eb)
        self.assertNotIn("never as a number", eb)
        record = RECORD.read_text()
        self.assertRegex(record, r"\n\| `likelihood` \| `\{kind, seen\}` \| optional \| \*\*Likelihood:\*\*")
        self.assertRegex(record, r"\n\| `best` \| text, one line \| of a new card \(lint\); needs `likelihood` \|")
        upgraded = record.split("## Fields an upgraded card may already carry")[1].split("\n## ")[0]
        self.assertNotIn("`likelihood` (`{kind, seen}`)", upgraded)
        rulings = (refs / "rulings.md").read_text()
        self.assertIn("- **Likelihood, widened, and Best response?, both surfaces** (2026-10-20, answer 267 (a)", rulings)
        self.assertEqual(ruling_problems(rulings), [])
        # mutant: the percentage rule back among the operator's words, before the designs clause
        entry = rulings.split("- **Likelihood, widened, and Best response?")[1]
        moved = entry.replace("and a percentage only as an observed share with its source and window; ", "")
        moved = moved.replace("A bare *no data* is never the line;",
                              "A bare *no data* is never the line; a percentage only as an observed share with its source and window;")
        self.assertTrue(ruling_problems("- **Likelihood, widened, and Best response?" + moved))


if __name__ == "__main__":
    unittest.main()
