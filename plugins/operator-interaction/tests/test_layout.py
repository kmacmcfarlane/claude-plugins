"""The page card in v5 order (d84f F11): every part of an open card, in one fixed order.

The decision page (`decision-page` skill) renders each card with `cardHtml`, loaded from
`assets/index.html` and run under node. Its body runs:

1. the TLDR, then, on a card that depends on another, its dependency line (03ab F3);
2. Context, What, Finding, Scope, Likelihood;
3. the upper folds: Open questions, then Assumptions;
4. the Impact;
5. the round lines: If left, A round costs, If unanswered;
6. the fieldset: each option with its line, its Pros and Cons rows and **More**; then the
   follow-ups; then the words box;
7. *Clear answer*;
8. the bottom folds: Background, Attached, Rejected alternatives.

A part with nothing to say is left out; whatever is shown keeps this order. There is no
Dependencies fold: 03ab F3 removed it, and the dependency line after the TLDR replaces it
(`DependencyLine` below: its place, its link to an on-page card, its ref slug, its escaping, and
the runner's key lint on an older `detail.dep`). A ⚠ one-way card keeps the same order.

Each check is proved by a mutation of the template: Context after What, Assumptions after the
Impact, Background after Attached, the Dependencies fold restored, the dependency line after
Context, the line drawn on a none `dep`, an on-page target drawn as a slug, the line unescaped.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, PAGE, example, page_free_script
from test_depth import HARNESS


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the decision page's layout tests (CardLayout) are "
              "skipped, so the v5 card order went untested", file=sys.stderr)


# the parts of an open card in the v5 order, each with the marker that opens it in cardHtml's body
# 03ab F3 dropped the Dependencies fold: the dependency line follows the TLDR, and a fold of that name
# is an unknown fold
ORDER = [
    ("TLDR", '<span class="lbl">TLDR</span>'),
    ("Depends", '<p class="depl">'),
    ("Context", '<div class="ctx">'),
    ("What", '<div class="what">'),
    ("Finding", '<div class="fnd">'),
    ("Scope", '<div class="scp">'),
    ("Likelihood", '<div class="lkh">'),
    ("Open questions", '<details class="gfold ofold">'),
    ("Assumptions", '<details class="gfold afold">'),
    ("Impact", '<div class="impline">'),
    ("If left", '<strong>If left:</strong>'),
    ("A round costs", '<strong>A round costs:</strong>'),
    ("If unanswered", '<strong>If unanswered:</strong>'),
    ("Options", '<div class="opts">'),
    ("Follow-ups", '<div class="follow">'),
    ("Words", '-words" data-n='),
    ("Clear answer", 'data-clear='),
    ("Background", None),
    ("Attached", None),
    ("Rejected alternatives", None),
]
NAMES = [n for n, _ in ORDER]
UPPER = ["Open questions", "Assumptions"]
BOTTOM = ["Background", "Attached", "Rejected alternatives"]
PANE = re.compile(r'<details class="pane"(?: open)?><summary>([^<]+?)(?: <span class="fsum">.*?</span>)?</summary>')


def body(html):
    return html[html.index('<div class="body">'):]


def balanced_div(s, i):
    """The end of the <div ...> that opens at i, past its matching </div>."""
    depth, j = 0, i
    while True:
        a, b = s.find("<div", j), s.find("</div>", j)
        if a != -1 and a < b:
            depth, j = depth + 1, a + 4
        else:
            depth, j = depth - 1, b + 6
            if depth == 0:
                return j


def shown(html):
    """The body as first drawn: each part's hidden detail levels taken out, so a part's marker counts once."""
    b, tag = body(html), '<div class="lv" hidden>'
    while tag in b:
        i = b.index(tag)
        b = b[:i] + b[balanced_div(b, i):]
    return b


# the Impact marker repeats once per line, so it is not counted
REPEATS = {"Impact"}


def counts(html):
    """Each part's marker, counted in the body as first drawn."""
    b = shown(html)
    return {name: b.count(marker) for name, marker in ORDER if marker is not None}


def options(html):
    """Each option's <div class="opt...">...</div> span in the body."""
    b, out = body(html), []
    for m in re.finditer(r'<div class="opt[ "]', b):
        out.append(b[m.start():balanced_div(b, m.start())])
    return out


def layout(html):
    """The parts a card shows, as (name, position) in document order."""
    b = body(html)
    got = []
    for name, marker in ORDER:
        if marker is not None and marker in b:
            got.append((name, b.index(marker)))
    for m in PANE.finditer(b):
        got.append((m.group(1), m.start()))
    return sorted(got, key=lambda p: p[1])


def problems(html):
    """Every way a card's body departs from the v5 order; empty when it keeps it."""
    b, got = body(html), layout(html)
    names = [n for n, _ in got]
    out = []
    for n in names:
        if n not in NAMES:
            out.append("unknown fold: " + n)
    for n in set(names):
        if names.count(n) > 1:
            out.append("more than one " + n)
    for n, k in counts(html).items():
        if k > 1 and n not in REPEATS:
            out.append("more than one " + n)
    known = [n for n in names if n in NAMES]
    if known != sorted(known, key=NAMES.index):
        out.append("out of order: " + " < ".join(known))
    pos = dict(got)
    # the upper folds before the Impact, the bottom folds after the fieldset
    if "Impact" in pos:
        for n in UPPER:
            if n in pos and pos[n] > pos["Impact"]:
                out.append(n + " after the Impact")
    end = b.index("</fieldset>") if "</fieldset>" in b else -1
    for n in BOTTOM:
        if n in pos and pos[n] < end:
            out.append(n + " inside or before the fieldset")
    # each option's line, its Pros and Cons rows and More sit in the fieldset, before the follow-ups
    start, follow = b.find("<fieldset>"), b.find('<div class="follow">')
    for marker in ('<div class="opt', '<div class="otr">', 'class="btn omore'):
        for m in re.finditer(re.escape(marker), b):
            if not start < m.start() < follow:
                out.append(marker + " outside the options")
    return out


def has_rows(o):
    """An option the page draws Pros and Cons rows for: one but (z) with its one-line pro or con."""
    return o["k"] != "z" and any(isinstance(o.get(f), str) and o[f].strip() for f in ("pro", "con"))


def option_problems(html, card):
    """Each option with pros or cons (its pro or con line, never (z)): exactly one Pros and Cons row block and one More, More first."""
    out = []
    spans = options(html)
    for o, span in zip(card["options"], spans):
        if not has_rows(o):
            continue
        rows, more = span.count('<div class="otr">'), span.count('class="btn omore')
        if rows != 1:
            out.append("(%s): %d Pros and Cons rows" % (o["k"], rows))
        if more != 1:
            out.append("(%s): %d More buttons" % (o["k"], more))
        if rows == 1 and more == 1 and span.index('class="btn omore') > span.index('<div class="otr">'):
            out.append("(%s): More after the rows" % o["k"])
    if len(spans) != len(card["options"]):
        out.append("%d option spans for %d options" % (len(spans), len(card["options"])))
    return out


def render(d, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + HARNESS], input=json.dumps([d]),
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    res = json.loads(out.stdout)["out"][0]
    if res["bad"]:
        raise AssertionError(res["bad"])
    return {c["n"]: c["html"] for c in res["cards"]}


def mutant(old, new):
    script = page_free_script()
    assert script.count(old) == 1, old
    return script.replace(old, new)


def full():
    """The example with card 41 carrying every part: the Finding of 43, the Likelihood, Best response?
    and dependencies of 42, and every round line."""
    d = copy.deepcopy(example())
    cs = {c["n"]: c for c in d["cards"]}
    c = cs[41]
    c["finding"] = copy.deepcopy(cs[43]["finding"])
    for k in ("likelihood", "best", "dep"):
        c[k] = copy.deepcopy(cs[42][k])
    c["ifleft"], c["roundcosts"] = "the laptop build stays", "a day of the maintainer's time"
    return d


MORE_ROWS = ("+(det?'<button type=\"button\" class=\"btn omore'", "+proConRows(o)+actList(c,k)")
CTX_WHAT = 'secHtml(c,"ctx","Context",P.ctx)+whatPart(c)'
ASSUME_IMP = 'assumeFold(c,P)+secHtml(c,"imp","Impact",P.imp)'
BG_ATT = ("    +(bg?'<details class=\"pane\"><summary>Background'+bgSum(c)+'</summary><div>'+bg+'</div></details>':'')\n"
          "    +attachedFold(c)\n")


@unittest.skipUnless(NODE, "node is not installed")
class CardLayout(unittest.TestCase):

    def test_every_part_is_present_in_order(self):
        h = render(full())[41]
        self.assertEqual(problems(h), [])
        want = [n for n in NAMES]
        self.assertEqual([n for n, _ in layout(h)], want)

    def test_every_example_card_keeps_the_order_with_its_folds_where_present(self):
        d = example()
        for c in d["cards"]:
            h = render(d)[c["n"]]
            self.assertEqual(problems(h), [], c["n"])
            names = [n for n, _ in layout(h)]
            upper = [n for n in names if n in UPPER]
            bottom = [n for n in names if n in BOTTOM]
            self.assertEqual(upper, [n for n in UPPER if n in upper], c["n"])
            self.assertEqual(bottom, [n for n in BOTTOM if n in bottom], c["n"])
            self.assertEqual(upper, (["Open questions"] if c.get("open") else []) + ["Assumptions"], c["n"])
            self.assertEqual(names[:2], ["TLDR", "Depends" if c.get("dep") else "Context"], c["n"])

    def test_a_one_way_card_keeps_the_same_order(self):
        d = full()
        c = next(x for x in d["cards"] if x["n"] == 41)
        c["oneway"] = True
        h = render(d)[41]
        self.assertEqual(problems(h), [])
        self.assertEqual([n for n, _ in layout(h)], NAMES)

    def test_no_dependencies_fold_is_allowed(self):
        # 03ab F3: the Dependencies fold is gone; one in a card is an unknown fold
        for d in (full(), example()):
            for n, h in render(d).items():
                self.assertNotIn("<summary>Dependencies", h, n)
                self.assertEqual(problems(h), [], n)
        h = render(full())[41]
        names = [n for n, _ in layout(h)]
        self.assertEqual(names[-3:], ["Background", "Attached", "Rejected alternatives"])
        self.assertEqual(names[:3], ["TLDR", "Depends", "Context"])
        # mutant: the fold restored in the template, between Attached and Rejected alternatives
        fold = ("    +attachedFold(c)\n",
                "    +attachedFold(c)+(shown(c.dep)?'<details class=\"pane\"><summary>Dependencies</summary><div>'"
                "+fmt(c.dep)+'</div></details>':'')\n")
        h = render(full(), mutant(*fold))[41]
        self.assertIn("unknown fold: Dependencies", problems(h))

    def test_the_upper_folds_come_before_the_impact_and_the_bottom_folds_after_the_fieldset(self):
        h = render(full())[41]
        pos = dict(layout(h))
        self.assertLess(pos["Open questions"], pos["Assumptions"])
        self.assertLess(pos["Assumptions"], pos["Impact"])
        end = body(h).index("</fieldset>")
        self.assertLess(end, pos["Clear answer"])
        for n in BOTTOM:
            self.assertGreater(pos[n], pos["Clear answer"], n)

    def test_each_option_with_pros_or_cons_has_one_rows_block_and_one_more_before_it(self):
        for d in (full(), example()):
            hs = render(d)
            for c in d["cards"]:
                self.assertEqual(option_problems(hs[c["n"]], c), [], c["n"])
        self.assertTrue(any(has_rows(o) for o in full()["cards"][0]["options"]))

    def test_mutant_pro_con_rows_dropped_is_caught(self):
        d = full()
        h = render(d, mutant("+proConRows(o)+actList(c,k)", "+actList(c,k)"))[41]
        c = next(x for x in d["cards"] if x["n"] == 41)
        self.assertTrue(any("0 Pros and Cons rows" in p for p in option_problems(h, c)), option_problems(h, c))

    def test_mutant_more_and_the_rows_swapped_is_caught(self):
        script = page_free_script()
        i = script.index(MORE_ROWS[0])
        j = script.index(MORE_ROWS[1], i)
        more = script[i:j].rstrip()
        swapped = script[:i] + "+proConRows(o)\n      " + more + "+actList(c,k)" + script[j + len(MORE_ROWS[1]):]
        d = full()
        h = render(d, swapped)[41]
        c = next(x for x in d["cards"] if x["n"] == 41)
        self.assertIn("(a): More after the rows", option_problems(h, c))

    def test_each_part_marker_counts_once_but_the_impact(self):
        for d in (full(), example()):
            for n, h in render(d).items():
                k = counts(h)
                self.assertTrue(all(v <= 1 for p, v in k.items() if p not in REPEATS), (n, k))

    def test_mutant_a_second_context_after_what_is_caught(self):
        h = render(full(), mutant(CTX_WHAT, CTX_WHAT + '+secHtml(c,"ctx","Context",P.ctx)'))[41]
        self.assertIn("more than one Context", problems(h))

    def test_mutant_context_after_what_is_caught(self):
        h = render(full(), mutant(CTX_WHAT, 'whatPart(c)+secHtml(c,"ctx","Context",P.ctx)'))[41]
        self.assertTrue(any("out of order" in p for p in problems(h)), problems(h))

    def test_mutant_assumptions_after_the_impact_is_caught(self):
        h = render(full(), mutant(ASSUME_IMP, 'secHtml(c,"imp","Impact",P.imp)+assumeFold(c,P)'))[41]
        self.assertIn("Assumptions after the Impact", problems(h))

    def test_mutant_background_after_attached_is_caught(self):
        a, b = BG_ATT.split("\n")[:2]
        h = render(full(), mutant(BG_ATT, b + "\n" + a + "\n"))[41]
        self.assertTrue(any("out of order" in p for p in problems(h)), problems(h))

    def test_mutant_a_bottom_fold_inside_the_fieldset_is_caught(self):
        h = render(full(), mutant("+'<fieldset><legend>", "+rejectedFold(c)+'<fieldset><legend>"))[41]
        self.assertTrue(problems(h), h)


TIP_HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
const c = byN.get("42");
process.stdout.write(JSON.stringify({line: depLine(c), tip38: tipHtml("38"), tip41: tipHtml("41")}));
"""
DEP_TLDR = 'secHtml(c,"tldr","TLDR",P.tldr)+depLine(c)+secHtml(c,"ctx","Context",P.ctx)'


def dep_line(html):
    """The card's dependency line, its markup, or None."""
    m = re.search(r'<p class="depl">.*?</p>', body(html))
    return m.group(0) if m else None


def text_of(markup):
    return re.sub(r"<[^>]+>", "", markup).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


@unittest.skipUnless(NODE, "node is not installed")
class DependencyLine(unittest.TestCase):
    """The dependency line (03ab F3): second on the card, after the TLDR, before Context; static;
    an on-page target a link that opens its card, with its tooltip; a ref keeps its slug."""

    def test_the_example_card_42_reads_its_line_after_the_tldr(self):
        h = render(example())[42]
        line = dep_line(h)
        self.assertEqual(text_of(line), "depends: only if 41 (Docs build home) is (b)")
        self.assertIn('<button type="button" class="declink" data-ref="41" data-goto="41">41 (Docs build home)</button>', line)
        b = body(h)
        self.assertLess(b.index('<span class="lbl">TLDR</span>'), b.index('<p class="depl">'))
        self.assertLess(b.index('<p class="depl">'), b.index('<div class="ctx">'))
        # static: no level button for it, and no part of its own in parts()
        self.assertNotIn('data-sec="dep"', h)
        # mutant: the older [[41]] (b) form renders as written, so the sentence is the writer's
        d = example()
        d["cards"][1]["dep"] = "[[41]] (b)"
        self.assertEqual(text_of(dep_line(render(d)[42])), "depends: 41 (Docs build home) (b)")

    def test_mutant_the_line_after_context_is_caught(self):
        h = render(example(), mutant(DEP_TLDR, 'secHtml(c,"tldr","TLDR",P.tldr)+secHtml(c,"ctx","Context",P.ctx)+depLine(c)'))[42]
        self.assertTrue(any("out of order" in p for p in problems(h)), problems(h))

    def test_no_dep_or_a_none_dep_draws_no_line(self):
        for dep in (None, "", "none", "None.", " "):
            d = example()
            c = d["cards"][1]
            if dep is None:
                c.pop("dep")
            else:
                c["dep"] = dep
            h = render(d)[42]
            self.assertIsNone(dep_line(h), dep)
            self.assertNotIn("depends:", h, dep)
        # mutant: the line drawn whatever dep says
        d = example()
        d["cards"][1]["dep"] = "none"
        h = render(d, mutant("const depLine=c=>isTxt(c.dep)&&shown(c.dep)", "const depLine=c=>isTxt(c.dep)"))[42]
        self.assertIsNotNone(dep_line(h))

    def test_an_on_page_target_is_a_link_and_a_ref_keeps_its_slug(self):
        d = example()
        d["cards"][1]["dep"] = "only if [[41]] is (a) or (c), and after [[38]] is answered, whatever its answer"
        line = dep_line(render(d)[42])
        self.assertEqual(text_of(line), "depends: only if 41 (Docs build home) is (a) or (c), and after "
                                         "38 · build cache reset is answered, whatever its answer")
        # the on-page target: the line's own N (name) form, a link that opens its card, its tooltip trigger
        self.assertIn('class="declink" data-ref="41" data-goto="41">41 (Docs build home)</button>', line)
        # the ref: its slug, with the ref tooltip and no card to open
        self.assertIn('<button type="button" class="slug" data-ref="38">38 · build cache reset</button>', line)
        self.assertNotIn('data-goto="38"', line)
        # the click handler opens a declink's card as it does an on-page slug's
        self.assertIn('const s=e.target.closest(".slug")||e.target.closest(".declink");', PAGE.read_text())
        # mutant: the on-page target drawn as a slug
        h = render(d, mutant("return byN.has(k)?", "return false?"))[42]
        self.assertNotIn('class="declink"', dep_line(h))

    def test_the_line_is_escaped(self):
        d = example()
        d["cards"][1]["dep"] = 'only if [[41]] is (b) <script>alert(1)</script> & "x"'
        d["cards"][0]["t"] = "Docs <b>build</b> home"
        line = dep_line(render(d)[42])
        self.assertNotIn("<script>", line)
        self.assertNotIn("<b>", line)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;x&quot;", line)
        self.assertIn("41 (Docs &lt;b&gt;build&lt;/b&gt; home)", line)
        # mutants: the text unescaped; the name unescaped
        h = render(d, mutant("+code(esc(c.dep))", "+code(c.dep)"))[42]
        self.assertIn("<script>", dep_line(h) or h)
        h = render(d, mutant("' ('+esc(nm)+')'", "' ('+nm+')'"))[42]
        self.assertIn("<b>build</b>", dep_line(h))

    def test_dep_must_be_one_line_of_text(self):
        for bad in (["[[41]] (b)"], {"n": 41, "letters": ["b"]}, "only if [[41]]\nis (b)"):
            d = example()
            d["cards"][1]["dep"] = bad
            out = subprocess.run([NODE, "-e", page_free_script() + HARNESS], input=json.dumps([d]),
                                 capture_output=True, text=True, timeout=60)
            res = json.loads(out.stdout)["out"][0]
            self.assertTrue(any("card 42: dep must be one line of text" in b for b in res["bad"]), (bad, res["bad"]))
        # mutant: the refusal dropped
        script = mutant("if(c.dep!=null&&!(isStr(c.dep)&&!LINE_BREAK.test(c.dep)))", "if(false)")
        d = example()
        d["cards"][1]["dep"] = ["[[41]] (b)"]
        out = subprocess.run([NODE, "-e", script + HARNESS], input=json.dumps([d]), capture_output=True, text=True, timeout=60)
        self.assertFalse(any("dep must be" in b for b in json.loads(out.stdout)["out"][0]["bad"]))

    def test_each_target_carries_its_tooltip(self):
        d = example()
        d["cards"][1]["dep"] = "only if [[41]] is (b), and after [[38]] is answered, whatever its answer"

        def run(script=None):
            out = subprocess.run([NODE, "-e", (script or page_free_script()) + TIP_HARNESS], input=json.dumps(d),
                                 capture_output=True, text=True, timeout=60)
            if out.returncode != 0:
                raise AssertionError("node failed: " + out.stderr)
            return json.loads(out.stdout)

        def problems(r):
            out = []
            refs = re.findall(r'data-ref="(\d+)"', r["line"])
            if refs != ["41", "38"]:
                out.append("the targets' tooltip triggers: %s" % refs)
            if 'class="declink"' not in r["line"]:
                out.append("the on-page target is no link")
            tip = r["tip38"]
            if '<span class="lbl">Asked</span>Clear the docs build cache?' not in tip or '<span class="lbl">Answer</span>a — clear it' not in tip:
                out.append("the off-page target's tooltip lacks Asked and Answer")
            if '<span class="lbl">Context</span>' not in r["tip41"]:
                out.append("the on-page target's tooltip lacks its card's Context")
            return out

        self.assertEqual(problems(run()), [])
        # mutant: data-ref stripped from depRef, so the on-page target shows no tooltip
        script = mutant('''class="declink" data-ref="'+esc(k)+'" data-goto=''', '''class="declink" data-goto=''')
        self.assertIn("the targets' tooltip triggers: ['38']", problems(run(script)))

    def test_an_older_detail_dep_lints_key_once_and_nothing_else(self):
        from test_context import RUNNER, runner
        from test_pros_cons import runner_with
        d = example()
        d["cards"][1]["detail"]["dep"] = ["Waits on the CI publish decision.",
                                          [{"h": "Waits on", "b": ["The CI publish decision."]}]]
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        lines = [x for x in out.splitlines() if "dep" in x]
        self.assertEqual(len(lines), 1, out)
        self.assertTrue(lines[0].startswith("lint: card 42: depth: detail.dep is not a part the page shows"), lines)
        self.assertNotIn("Depends on", out)
        # mutant: dep left in the runner's parts, which prints no key line and lints its levels instead
        js = RUNNER.read_text().replace('why: "Why now", whyask: "Why ask", evidence: "the Evidence"};',
                                        'why: "Why now", whyask: "Why ask", dep: "Depends on", evidence: "the Evidence"};')
        code, out, _ = runner_with(js, d)
        self.assertFalse(any("detail.dep is not a part" in x for x in out.splitlines()), out)


if __name__ == "__main__":
    unittest.main()
