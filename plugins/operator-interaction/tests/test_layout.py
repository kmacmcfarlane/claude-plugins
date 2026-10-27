"""The page card in v5 order (d84f F11): every part of an open card, in one fixed order.

The decision page (`decision-page` skill) renders each card with `cardHtml`, loaded from
`assets/index.html` and run under node. Its body runs:

1. the TLDR (03ab's dependency line will follow it, once 03ab F3 lands);
2. Context, What, Finding, Scope, Likelihood;
3. the upper folds: Open questions, then Assumptions;
4. the Impact;
5. the round lines: If left, A round costs, If unanswered;
6. the fieldset: each option with its line, its Pros and Cons rows and **More**; then the
   follow-ups; then the words box;
7. *Clear answer*;
8. the bottom folds: Background, Attached, Dependencies (until 03ab F3 removes it), Rejected
   alternatives.

A part with nothing to say is left out; whatever is shown keeps this order. One Dependencies fold
is allowed, between Attached and Rejected alternatives, until 03ab F3 lands. A ⚠ one-way card
keeps the same order.

Each check is proved by a mutation of the template: Context after What, Assumptions after the
Impact, Background after Attached.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, example, page_free_script
from test_depth import HARNESS


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the decision page's layout tests (CardLayout) are "
              "skipped, so the v5 card order went untested", file=sys.stderr)


# the parts of an open card in the v5 order, each with the marker that opens it in cardHtml's body
# 03ab F3: drop Dependencies here and invert the allowance test
ORDER = [
    ("TLDR", '<span class="lbl">TLDR</span>'),
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
    ("Dependencies", None),
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
    for n in BOTTOM + ["Dependencies"]:
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
            self.assertEqual(names[:2], ["TLDR", "Context"], c["n"])

    def test_a_one_way_card_keeps_the_same_order(self):
        d = full()
        c = next(x for x in d["cards"] if x["n"] == 41)
        c["oneway"] = True
        h = render(d)[41]
        self.assertEqual(problems(h), [])
        self.assertEqual([n for n, _ in layout(h)], NAMES)

    def test_one_dependencies_fold_is_allowed_between_attached_and_rejected_until_03ab_f3(self):
        h = render(full())[41]
        names = [n for n, _ in layout(h)]
        self.assertEqual(names[-3:], ["Attached", "Dependencies", "Rejected alternatives"])
        # mutants: the fold after Rejected alternatives; a second one
        dep = re.search(r'<details class="pane"><summary>Dependencies</summary>.*?</details>', h).group(0)
        rej = re.search(r'<details class="pane"><summary>Rejected alternatives.*?</ul></div></details>', h).group(0)
        moved = h.replace(dep, "").replace(rej, rej + dep)
        self.assertTrue(any("out of order" in p for p in problems(moved)), problems(moved))
        twice = h.replace(dep, dep + dep)
        self.assertIn("more than one Dependencies", problems(twice))

    def test_the_upper_folds_come_before_the_impact_and_the_bottom_folds_after_the_fieldset(self):
        h = render(full())[41]
        pos = dict(layout(h))
        self.assertLess(pos["Open questions"], pos["Assumptions"])
        self.assertLess(pos["Assumptions"], pos["Impact"])
        end = body(h).index("</fieldset>")
        self.assertLess(end, pos["Clear answer"])
        for n in BOTTOM + ["Dependencies"]:
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


if __name__ == "__main__":
    unittest.main()
