"""Pros and Cons inline, labelled, on both surfaces (the operator's feedback on decision 302).

"pros and cons with separate sub-headings just like "Effect" and "Reach" to make them easy to
read". Each option but (z) shows its main upside and downside in one line each, always visible:

- the answer page (`decision-page` skill, `assets/index.html`, run under node): the option's
  `pro` and `con` as two rows under it, after its one line, each a facet label (`.lbl`, the
  class More's Effect and Reach carry) in its own column, then the text, with no colon; a none
  one has no row; *if chosen:* before a non-recommended option's line (no more *not recommended
  because:*). `check()` refuses a `pro` or `con` that is not one line of text, and a `pros` or
  `cons` that is not a list of text, holds more than five points or a point that is not text,
  or is empty on an option but (z). The runner's `tradeoffs` lint (`shape:`) fires on an option
  but (z) with no shown pro or con, a recommended option with no con, and a card with two or
  more real options and none; the rows count in the card in all;
- chat (the `decisions` skill): under each option's impact line on a card, two italic lines,
  `*pros: …*` then `*cons: …*`; (z) stays one line. Checked against the card template in
  `references/rendering.md` and every card in `references/gallery.md`.

Each check is proved by a mutation: break it, see it fail.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

from test_chat_context import GALLERY, RENDERING, SKILL_MD, fenced, views
from test_context import RUNNER, runner
from test_depth import HARNESS, card, run_page
from test_impact import NODE, PAGE, example, page_free_script
from test_option_impact import DECIDE_LATER, FACET_LINE, OPTION

# every line break check() refuses in a pro, a con or a point
BREAKS = ["\n", "\r", "\u0085", "\u2028", "\u2029", "\v", "\f"]
PROS = re.compile(r"^  \*pros: \S.*\*$")
CONS = re.compile(r"^  \*cons: \S.*\*$")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def opt_html(html, n, k):
    """Option k's block in card n's html: from its <div class="opt"> to the next option or the
    follow-ups."""
    at = html.index('id="d%d-%s" value="%s"' % (n, k, k))
    start = html.rindex('<div class="opt', 0, at)
    ends = [i for i in (html.find('<div class="opt', at), html.find('<div class="follow">', at)) if i >= 0]
    return html[start:min(ends)]


def row_problems(o_html, pro, con):
    """The option's Pros and Cons rows: after its one line, before its steps and More detail,
    each a facet label then the text, with no colon. pro/con None: no row expected."""
    out = []
    want = [(lab, t) for lab, t in (("Pros", pro), ("Cons", con)) if t is not None]
    if not want:
        if 'class="otr"' in o_html:
            out.append("rows with nothing to show")
        return out
    if 'class="otr"' not in o_html:
        return ["no Pros and Cons rows"]
    rows = o_html[o_html.index('<div class="otr">'):]
    rows = rows[:rows.index("</div>")]
    got = re.findall(r'<p><span class="lbl">([^<]*)</span><span>(.*?)</span></p>', rows)
    if [g[0] for g in got] != [lab for lab, _ in want]:
        out.append("rows %r, want %r" % ([g[0] for g in got], [lab for lab, _ in want]))
    for (lab, t), g in zip(want, got):
        if "[[" not in t and g[1] != esc(t):
            out.append("%s row reads %r" % (lab, g[1]))
    if 'class="oi"' in o_html and o_html.index('class="oi"') > o_html.index('class="otr"'):
        out.append("the rows come before the option's line")
    if o_html.index('</label>') > o_html.index('class="otr"'):
        out.append("the rows sit inside the option's label, where a click picks the option")
    for after in ('class="act"', 'class="odet"'):
        if after in o_html and o_html.index(after) < o_html.index('class="otr"'):
            out.append("the rows come after " + after)
    return out


def layout_problems(html, c):
    """The rows and More's facets share one layout: one CSS rule gives both the label column grid, and
    each renders as a paragraph of that rule's class holding the label, then the text in its own span."""
    out = []
    if not re.search(r"\.otr p,\.odet \.f\{display:grid;grid-template-columns:4\.2rem minmax\(0,1fr\)", html):
        out.append("no one rule lays out both the rows and More's facets")
    for k in ("Effect", "Reach", "Cost"):
        if '<p class="f"><span class="lbl">%s</span><span>' % k not in c["more"]["b"]:
            out.append("More's %s is not in the facet layout" % k)
    if '<p class="f"><span class="lbl owu">⚠ Undo</span><span>' not in c["more"]["b"]:
        out.append("More's Undo is not in the facet layout")
    for k in ("Pros", "Cons"):
        if '<div class="otr"><p><span class="lbl">' not in c["html"] or '<p><span class="lbl">%s</span><span>' % k not in c["html"]:
            out.append("the %s row is not in the facet layout" % k)
    return out


def page_with(script_text, d):
    """Card html rendered by a (mutated) page-free script."""
    out = subprocess.run([NODE, "-e", script_text + HARNESS], input=json.dumps([d]), capture_output=True,
                         text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)["out"][0]


def runner_with(js, d):
    """The runner, mutated, beside a copy of the template."""
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "scripts").mkdir()
        (root / "assets").mkdir()
        shutil.copy(PAGE, root / "assets" / "index.html")
        script = root / "scripts" / "check_cards.js"
        script.write_text(js)
        return runner(d, script=script)


def opt(d, n, k):
    c = next(x for x in d["cards"] if x["n"] == n)
    return next(o for o in c["options"] if o["k"] == k)


@unittest.skipUnless(NODE, "node is not installed")
class PageRows(unittest.TestCase):

    def test_every_option_shows_its_pros_and_cons_rows_after_its_line(self):
        d = example()
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        seen = 0
        for c in d["cards"]:
            html = card(res, c["n"])["html"]
            for o in c["options"]:
                self.assertEqual(row_problems(opt_html(html, c["n"], o["k"]), o.get("pro"), o.get("con")), [],
                                 (c["n"], o["k"]))
                seen += 1
        self.assertEqual(seen, 9)

    def test_the_rows_look_like_effect_and_reach(self):
        # one layout, shared: the rows and More's facets are each a label in a column of its own, then the text
        res = run_page(example())
        self.assertEqual(layout_problems(PAGE.read_text(), card(res, 42)), [])
        self.assertNotRegex(card(res, 41)["html"], r"Pros:|Cons:")

    def test_mutants_a_split_layout_is_caught(self):
        html = PAGE.read_text()
        css = html.replace(".otr p,.odet .f{display:grid;", ".otr p{display:grid;", 1)
        self.assertNotEqual(css, html)
        self.assertTrue(layout_problems(css, card(run_page(example()), 42)))
        src = page_free_script()
        block = src.replace("""const f=(l,v)=>isTxt(v)&&shown(v)?'<p class="f">""", """const f=(l,v)=>isTxt(v)&&shown(v)?'<p>""", 1)
        self.assertNotEqual(block, src)
        self.assertTrue(layout_problems(html, card(page_with(block, example()), 42)))

    def test_decide_later_draws_no_rows_even_when_given(self):
        d = example()
        for c in d["cards"]:
            c["options"][-1]["pro"] = "nothing to set up"
            c["options"][-1]["con"] = "the wait goes on"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        for c in d["cards"]:
            self.assertNotIn('class="otr"', opt_html(card(res, c["n"])["html"], c["n"], "z"), c["n"])
        # the example's (z) gives none
        self.assertFalse(any("pro" in c["options"][-1] or "con" in c["options"][-1] for c in example()["cards"]))
        # mutant: (z) drawn like any option
        src = page_free_script()
        m = src.replace("""const proCon=o=>isObj(o)&&o.k!=="z"?""", "const proCon=o=>isObj(o)?", 1)
        self.assertNotEqual(m, src)
        self.assertIn('class="otr"', opt_html(card(page_with(m, d), 41)["html"], 41, "z"))

    def test_a_none_pro_or_con_has_no_row(self):
        d = example()
        o = opt(d, 41, "a")
        o["pro"] = "none"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertEqual(row_problems(opt_html(card(res, 41)["html"], 41, "a"), None, o["con"]), [])
        o["con"] = "n/a"
        res = run_page(d)
        self.assertEqual(row_problems(opt_html(card(res, 41)["html"], 41, "a"), None, None), [])
        del o["pro"], o["con"]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertNotIn('class="otr"', opt_html(card(res, 41)["html"], 41, "a"))

    def test_the_rows_are_escaped(self):
        d = example()
        opt(d, 43, "a")["pro"] = "<img src=x onerror=alert(1)> stays"
        opt(d, 43, "a")["con"] = "</span><script>alert(1)</script>"
        h = opt_html(card(run_page(d), 43)["html"], 43, "a")
        self.assertNotIn("<img", h)
        self.assertNotIn("<script>", h)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt; stays", h)

    def test_marks_in_a_row_render(self):
        # a row is card text: a slug and a backtick span render as everywhere else
        d = example()
        opt(d, 43, "a")["con"] = "[[42]] waits, and `theme.css` keeps its blue"
        h = opt_html(card(run_page(d), 43)["html"], 43, "a")
        rows = h[h.index('<div class="otr">'):]
        self.assertIn('class="slug in"', rows)
        self.assertIn("<code>theme.css</code>", rows)
        src = page_free_script()
        m = src.replace("'</span><span>'+fmt(v)+'</span></p>'", "'</span><span>'+esc(v)+'</span></p>'", 1)
        self.assertNotEqual(m, src)
        h = opt_html(card(page_with(m, d), 43)["html"], 43, "a")
        rows = h[h.index('<div class="otr">'):]
        self.assertNotIn('class="slug in"', rows)
        self.assertNotIn("<code>", rows)

    def test_mutants_rows_dropped_or_unlabelled_are_caught(self):
        src = page_free_script()
        dropped = src.replace("+proConRows(o)+actList(c,k)", "+actList(c,k)", 1)
        inside = src.replace("'</span>':'')+'</label>'", "'</span>':'')+proConRows(o)+'</label>'", 1)
        self.assertNotEqual(inside, src)
        d = example()
        o = opt(d, 41, "a")
        self.assertTrue(row_problems(opt_html(card(page_with(inside, d), 41)["html"], 41, "a"), o["pro"], o["con"]))
        unlabelled = src.replace("'<p><span class=\"lbl\">'+l+'</span><span>'", "'<p><span>'+l+':</span><span>'", 1)
        for m in (dropped, unlabelled):
            self.assertNotEqual(m, src)
            d = example()
            html = card(page_with(m, d), 41)["html"]
            o = opt(d, 41, "b")
            self.assertTrue(row_problems(opt_html(html, 41, "b"), o["pro"], o["con"]))

    def test_a_non_recommended_option_reads_if_chosen(self):
        res = run_page(example())
        # card 41 recommends (b): (a)'s line follows "if chosen:", (b)'s "because:", (z)'s "if left:"
        html = card(res, 41)["html"]
        self.assertIn('<em>if chosen:</em> the cache failures stay', opt_html(html, 41, "a"))
        self.assertIn('<em>because:</em>', opt_html(html, 41, "b"))
        self.assertIn('<em>if left:</em>', opt_html(html, 41, "z"))
        self.assertIn('<em>if chosen:</em>', opt_html(card(res, 42)["html"], 42, "b"))
        self.assertNotIn("not recommended because", PAGE.read_text())
        # mutant: the old label
        src = page_free_script()
        old = src.replace('(isRec?"because:":"if chosen:")', '(isRec?"because:":(c.rec?"not recommended because:":"if chosen:"))', 1)
        self.assertNotEqual(old, src)
        self.assertNotIn('<em>if chosen:</em>', opt_html(card(page_with(old, example()), 41)["html"], 41, "a"))


@unittest.skipUnless(NODE, "node is not installed")
class PageCheck(unittest.TestCase):

    def refused(self, k, field, value, needle):
        d = example()
        opt(d, 41, k)[field] = value
        bad = run_page(d)["bad"]
        self.assertTrue(any(needle in b for b in bad), (field, value, bad))

    def test_refusals(self):
        six = ["one", "two", "three", "four", "five", "six"]
        self.refused("b", "pros", six, "card 41: (b) pros has 6 points: give at most 5")
        self.refused("z", "cons", six, "card 41: (z) cons has 6 points")
        self.refused("b", "pros", ["x", 3], "(b) pros point 2 is not text")
        self.refused("b", "cons", ["x", " "], "(b) cons point 2 is not text")
        self.refused("b", "pros", "one upside", "(b) pros must be a list of 1 to 5 points as text")
        self.refused("b", "pros", [], "(b) pros is empty")
        self.refused("b", "pro", "one\ntwo", "(b) pro must be one line")
        self.refused("a", "con", "one\r\ntwo", "(a) con must be one line")
        self.refused("a", "pro", 5, "(a) pro must be text")
        for br in BREAKS:
            self.refused("a", "pro", "one" + br + "two", "(a) pro must be one line")
            self.refused("b", "cons", ["fine", "one" + br + "two"], "(b) cons point 2 has a line break")

    def test_mutant_narrow_line_break_is_caught(self):
        src = page_free_script()
        m = src.replace("const LINE_BREAK=/[\\r\\n\\u0085\\u2028\\u2029\\v\\f]/;", "const LINE_BREAK=/[\\r\\n]/;", 1)
        self.assertNotEqual(m, src)
        d = example()
        opt(d, 41, "a")["pro"] = "one\u2028two"
        self.assertEqual(page_with(m, d)["bad"], [])
        d = example()
        opt(d, 41, "b")["pros"] = ["one\u0085two"]
        self.assertEqual(page_with(m, d)["bad"], [])

    def test_what_is_allowed(self):
        d = example()
        opt(d, 41, "b")["pros"] = ["one", "two", "three", "four", "five"]
        opt(d, 41, "z")["pros"] = []
        opt(d, 41, "z")["cons"] = []
        self.assertEqual(run_page(d)["bad"], [])

    def test_mutant_no_cap_is_caught(self):
        src = page_free_script()
        m = src.replace("else if(v.length>PROS_MAX)", "else if(false)", 1)
        self.assertNotEqual(m, src)
        d = example()
        opt(d, 41, "b")["pros"] = ["one", "two", "three", "four", "five", "six"]
        self.assertEqual(page_with(m, d)["bad"], [])


@unittest.skipUnless(NODE, "node is not installed")
class TradeoffsLint(unittest.TestCase):

    def test_the_example_is_clean_and_carries_its_trade_offs(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        for c in example()["cards"]:
            for o in c["options"]:
                at = (c["n"], o["k"])
                if o["k"] == "z":
                    self.assertFalse("pro" in o or "con" in o, at)
                else:
                    self.assertTrue(o.get("pro", "").strip() and o.get("con", "").strip(), at)
                lo = 0 if o["k"] == "z" else 1
                for k in ("pros", "cons"):
                    v = o.get(k, [])
                    self.assertTrue(lo <= len(v) <= 5 and all(isinstance(x, str) and x.strip() for x in v), at)

    def test_an_option_missing_a_row(self):
        d = example()
        del opt(d, 41, "a")["pro"]
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "lint: card 41: shape: (a) has no pro: give it a one-line pro (its inline Pros row), "
                              "or leave it knowingly on an upgraded older card\n")
        d = example()
        del opt(d, 43, "b")["pro"], opt(d, 43, "b")["con"]
        self.assertIn("lint: card 43: shape: (b) has no pro and no con", runner(d)[1])

    def test_a_recommended_option_with_no_con(self):
        d = example()
        del opt(d, 41, "b")["con"]
        out = runner(d)[1]
        self.assertIn("lint: card 41: shape: the recommended option (b) has no con", out)
        self.assertNotIn("shape: (b) has no con", out)
        self.assertEqual(len(out.splitlines()), 1, out)

    def test_a_card_with_none(self):
        d = example()
        for k in ("a", "b"):
            for f in ("pro", "con", "pros", "cons"):
                opt(d, 43, k).pop(f, None)
        out = runner(d)[1]
        self.assertEqual(out, "lint: card 43: shape: none of the card's 2 options but (z) carries its pros and cons: "
                              "give each a one-line pro and con (pro, con: the inline Pros and Cons rows), or leave "
                              "it knowingly on an upgraded older card\n")

    def test_decide_later_is_never_linted(self):
        # the example's (z) gives no pro or con; one given, past the cap, is not shown, so not linted
        d = example()
        d["cards"][0]["options"][-1]["pro"] = " ".join(["word"] * 40)
        self.assertEqual(runner(d)[:2], (0, ""))

    def test_a_pro_or_con_past_the_cap(self):
        d = example()
        opt(d, 41, "a")["con"] = " ".join(["word"] * 25)
        self.assertEqual(runner(d)[:2], (0, ""))
        opt(d, 41, "a")["con"] = " ".join(["word"] * 26)
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "lint: card 41: shape: (a)'s con is 26 words: keep its Cons row to one line, about 25 "
                              "words; the points in full go in cons\n")
        js = RUNNER.read_text()
        off = js.replace("if (n > PROCON_CAP)", "if (false)", 1)
        self.assertNotEqual(off, js)
        self.assertEqual(runner_with(off, d)[:2], (0, ""))

    def test_it_reads_what_the_page_shows(self):
        d = example()
        opt(d, 42, "a")["pro"] = "None."
        self.assertIn("lint: card 42: shape: (a) has no pro", runner(d)[1])
        # mutant: the raw field read again, so a none pro clears the lint
        js = RUNNER.read_text()
        raw = js.replace("page.proCon(o).map(r => r[0])", "[o.pro ? \"Pros\" : \"\", o.con ? \"Cons\" : \"\"]", 1)
        self.assertNotEqual(raw, js)
        self.assertNotIn("(a) has no pro", runner_with(raw, d)[1])

    def test_mutant_lint_removed_is_caught(self):
        js = RUNNER.read_text()
        removed = js.replace("  tradeoffs(c, say);\n", "", 1)
        self.assertNotEqual(removed, js)
        d = example()
        del opt(d, 41, "a")["pro"]
        self.assertEqual(runner_with(removed, d)[:2], (0, ""))

    def test_the_cold_read_covers_the_rows(self):
        d = example()
        opt(d, 43, "a")["con"] = "the 17 widgets break for Frobnicator users"
        out = runner(d)[1]
        self.assertIn('lint: card 43: "17" (pros and cons) counts things its context does not name', out)
        # the rows stay out of the flat part, so the card in all moves only by their words
        js = RUNNER.read_text()
        off = js.replace('  terms(opts(c).flatMap(o => page.proCon(o).map(r => r[1])), " (pros and cons)");\n', "", 1)
        self.assertNotEqual(off, js)
        self.assertNotIn("17", runner_with(off, d)[1])
        self.assertNotIn("o.pro", js[js.index("function flat("):js.index("function flat(") + 400])

    def test_an_id_in_a_row_is_linted(self):
        d = example()
        opt(d, 43, "a")["con"] = "the brand check stays open as KAPPA-3570"
        self.assertIn("lint: card 43: KAPPA-3570 looks like an id ((a))", runner(d)[1])

    def test_the_rows_count_in_the_card_in_all(self):
        d = example()
        opt(d, 43, "a")["pro"] = " ".join(["word"] * 1400)
        out = runner(d)[1]
        self.assertIn("lint: card 43: depth: the card is", out)
        js = RUNNER.read_text()
        uncounted = js.replace(" + optWords + pc;", " + optWords;", 1)
        self.assertNotEqual(uncounted, js)
        self.assertNotIn("depth: the card is", runner_with(uncounted, d)[1])


def chat_problems(body):
    """Each option but (z) on a card: its impact line, then `*pros: …*`, then `*cons: …*`; (z)
    carries neither. Returns (problems, options checked)."""
    out, seen = [], 0
    for k, line in enumerate(body):
        if DECIDE_LATER.match(line):
            nxt = body[k + 1] if k + 1 < len(body) else ""
            if PROS.match(nxt) or CONS.match(nxt):
                out.append("(z) carries a pros or cons line")
            continue
        m = OPTION.match(line)
        if not m:
            continue
        seen += 1
        rest = body[k + 1:k + 4] + ["", "", ""]
        if not FACET_LINE.match(rest[0]):
            out.append("(%s) has no impact line" % m.group(2))
        if not PROS.match(rest[1]):
            out.append("(%s): no *pros: …* line under its impact line: %r" % (m.group(2), rest[1]))
        if not CONS.match(rest[2]):
            out.append("(%s): no *cons: …* line after its pros: %r" % (m.group(2), rest[2]))
    return out, seen


class ChatLines(unittest.TestCase):

    def test_the_card_template(self):
        body = fenced(RENDERING.read_text(), "**N — Title as a question?**\n**What:**")
        probs, seen = chat_problems(body)
        self.assertEqual(probs, [])
        self.assertGreaterEqual(seen, 2)

    def gallery_problems(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "gallery.md"
            p.write_text(text)
            out, seen = [], 0
            for at, kind, body in views(p):
                if kind != "card":
                    continue
                probs, n = chat_problems(body)
                out += ["line %d: %s" % (at, x) for x in probs]
                seen += n
        return out, seen

    def test_every_gallery_card_option(self):
        probs, seen = self.gallery_problems(GALLERY.read_text())
        self.assertEqual(probs, [])
        self.assertGreaterEqual(seen, 38)

    def test_mutants_dropped_or_unlabelled_lines_are_caught(self):
        text = GALLERY.read_text()
        line = "  *cons: no backup tonight, and a restart costs about 3 hours*\n"
        self.assertIn(line, text)
        for m in (text.replace(line, "", 1),
                  text.replace(line, line.replace("*cons: ", "*"), 1),
                  text.replace(line, line.replace("*cons: ", "*Cons: "), 1),
                  text.replace("  *pros: the backup completes tonight, with no restart*\n", "", 1)):
            self.assertNotEqual(m, text)
            self.assertTrue(self.gallery_problems(m)[0])

    def test_the_rule_is_written(self):
        r = RENDERING.read_text()
        self.assertIn("`*pros: …*` then `*cons: …*`", r)
        self.assertIn("decision 302", r)
        self.assertIn("`*pros: …*` and `*cons: …*` lines", SKILL_MD.read_text())


if __name__ == "__main__":
    unittest.main()
