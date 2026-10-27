"""Attached (F3; answers 264 (a), 291 (a) and 286 (b), each with the operator's words), on both surfaces.

Five parts:

- the decision page (`decision-page` skill, under node): `attachedFold` renders the record's
  `attached` as the second of the bottom folds, after Background and before Dependencies and
  Rejected alternatives, closed, its summary the count and the titles; each attachment its own
  entry, closed, its title, a kind pill and its source line, its body in its kind's shape (a code
  block through `codeBlock`, prose, a link, a table, a numbered list, a status list, a tree),
  every text escaped. A `[[att:id|label]]` link in any text is a dotted button that `openAtt`
  follows; one to an id the card does not hold is its label as plain text. `check()` refuses a
  malformed attachment, which also runs in the runner's `--record` mode;
- the pre-publish runner (`scripts/check_cards.js`, under node): it refuses a link to an id the
  card does not attach, a link not in the `[[att:id|label]]` form, and a secret in an
  attachment or the Finding's excerpt (named by where it is and its key, never its value); the
  skill's grep step runs the runner's own patterns; the id lint reads every shown text but an
  excerpt-shaped body, the cold read the titles; attachments never count in the card in all;
  the `attached` lint sizes them;
- the upgrader (`scripts/upgrade_cards.js`, under node): the kit's attachments map as they
  stand, an example's `mode` read as its `form`; a kind the record has not, or an `attached` not
  a list, is refused, all or nothing; a null `attached` is none;
- the chat card (the `decisions` skill): the `▸ Attached — N: <titles>` line after
  ▸ Background and before ▸ Rejected alternatives, closed on a card, open in a block and in
  gallery § 37, each attachment a bold head line over its body, a blank line before each head
  after the first and before a table;
- the kind list, one list in the page, the upgrader, the schema, the digest and the chat rules.

Each check is proved by a mutation: a broken template, runner, upgrader or text fails it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, example, page_free_script
from test_context import runner, RECORD, SKILL
from test_record import run_record, record_of
from test_items import mutant_runner
from test_upgrade import upgrade, load, KIT, UPGRADER
from test_chat_context import fenced, views, GALLERY, RENDERING, SKILL_MD, REFS, FOLD
from test_finding import one, mutant_page, HOSTILE
from test_digest import section, table_rows, required_problems as field_problems

DIGEST = SKILL / "references" / "writer-digest.md"
SCHEMA = SKILL / "references" / "cards-schema.md"
PAGE_SKILL = SKILL / "SKILL.md"
RUNNER_JS = SKILL / "scripts" / "check_cards.js"

KINDS = ["excerpt", "summary", "link", "example", "preview", "table", "matrix", "steps", "checks", "depmap"]


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the Attached page, runner and upgrader tests (AttachPage, "
              "AttachRunner, AttachUpgrade) are skipped, so its render, its checks, its refusals and its "
              "upgrade went untested", file=sys.stderr)


def card(d, n):
    return next(c for c in d["cards"] if c["n"] == n)


def fold(html):
    """A card's Attached fold as rendered: "" when there is none."""
    m = re.search(r'<details class="pane"><summary>Attached.*?</div></details>(?=<details class="pane">|</div></div></details>)',
                  html, re.S)
    return m.group(0) if m else ""


def panes(html):
    return re.findall(r'<details class="pane"(?: open)?><summary>(Background|Attached|Dependencies|Rejected alternatives)', html)


# one attachment of each kind, as a writer writes it
SAMPLES = {
    "excerpt": {"id": "x", "kind": "excerpt", "title": "The handler", "src": "upload/handler.go:40-45",
                "body": {"lang": "go", "text": "body, err := io.ReadAll(r.Body)\nif len(body) > max {"}},
    "summary": {"kind": "summary", "title": "The disk graph", "body": ["The temp directory grew 40 GB in a week."],
                "pointer": "the metrics board's upload panel"},
    "link": {"kind": "link", "title": "Provider status", "url": "https://status.example.com/history",
             "body": "two outages in twelve months", "src": "cited in the outage review"},
    "example": {"kind": "example", "title": "A restore", "form": "narrative",
                "body": ["A restore from the bucket takes about an hour."]},
    "preview": {"kind": "preview", "title": "The new row", "src": "invented to illustrate",
                "body": {"text": "41  Docs build home  rec (b)  -> (b) every merge publishes"}},
    "table": {"kind": "table", "title": "Homes", "body": {"cols": ["Home", "Clean"], "rows": [["laptop", "no"], ["CI", "yes"]]}},
    "matrix": {"kind": "matrix", "title": "Who it reaches", "body": {"cols": ["Who", "How"], "rows": [["writers", "publish on merge"]]}},
    "steps": {"kind": "steps", "title": "Roll back", "body": [{"t": "revert the merge"}, {"t": "publish again", "d": "from CI"}]},
    "checks": {"kind": "checks", "title": "Trial build", "body": [{"s": "pass", "t": "builds"}, {"s": "fail", "t": "links", "d": "two dead"},
                                                              {"s": "pending", "t": "publish"}]},
    "depmap": {"kind": "depmap", "title": "What waits", "body": [{"n": 41, "name": "docs build home", "self": True,
                                                                  "kids": [{"n": 42, "name": "docs address", "rel": "waits on", "note": "only on (b)"}]}]},
}
# what each kind's body is drawn as
SHAPES = {
    "excerpt": ['<figure class="xc"', '<span class="pill cls">go</span>', "io.ReadAll(r.Body)"],
    "summary": ["<p>The temp directory grew 40 GB in a week.</p>", '<p class="aptr"><span class="lbl inl">Full text:</span>'],
    "link": ['<a href="https://status.example.com/history" target="_blank" rel="noopener">', "<p>two outages in twelve months</p>"],
    "example": ['<span class="asrc">invented to illustrate</span>', "<p>A restore from the bucket takes about an hour.</p>"],
    "preview": ['<figure class="xc"', '<span class="asrc">invented to illustrate</span>'],
    "table": ['<div class="atbl" tabindex="0"><table><thead><tr><th scope="col">Home</th><th scope="col">Clean</th></tr>',
              "<tr><td>CI</td><td>yes</td></tr>"],
    "matrix": ['<th scope="col">Who</th>', "<td>publish on merge</td>"],
    "steps": ['<ol class="asteps"><li><span class="stt">revert the merge</span></li>', '<span class="std">from CI</span>'],
    "checks": ['<p class="atally">1 pass · 1 fail · 1 pending</p>', '<span class="st st-fail">fail</span>'],
    "depmap": ['<ul class="adep">', 'class="slug in self" data-ref="41" data-goto="41">41 · docs build home</button>',
               '<span class="drel">waits on</span> ', "<ul><li>", '<span class="dnote"> — only on (b)</span>'],
}
PILLS = {"excerpt": "excerpt", "summary": "summary", "link": "link", "example": "worked example", "preview": "preview",
         "table": "comparison", "matrix": "who&#39;s affected", "steps": "steps", "checks": "check results",
         "depmap": "dependency map"}


def with_att(*atts, n=41):
    d = example()
    card(d, n)["attached"] = [copy.deepcopy(a) for a in atts]
    # the example's evidence links its own log, which this list replaces
    card(d, 41)["evidence"] = "Build logs for both failed publishes show the same stale cache directory."
    return d


@unittest.skipUnless(NODE, "node is not installed")
class AttachPage(unittest.TestCase):

    def test_the_example_shows_card_41s_fold(self):
        res = one(example())
        self.assertEqual(res["bad"], [])
        f = fold(res["cards"]["41"]["card"])
        self.assertTrue(f.startswith('<details class="pane"><summary>Attached <span class="fsum">3: The second failed build · '
                                     'Where the build could run · A trial CI build on a branch</span></summary>'), f[:300])
        self.assertEqual(f.count('<details class="att"'), 3)
        self.assertIn('<details class="att" id="att-41-log"><summary><span class="at">The second failed build</span>'
                      '<span class="pill akind">excerpt</span><span class="asrc">', f)
        self.assertEqual(fold(res["cards"]["42"]["card"]), "")
        self.assertEqual(fold(res["cards"]["43"]["card"]), "")
        # mutant: the fold left out of the card
        res = one(example(), mutant_page("    +attachedFold(c)\n", ""))
        self.assertEqual(fold(res["cards"]["41"]["card"]), "")

    def test_it_is_the_second_bottom_fold_and_closed(self):
        def problems(script=None):
            out = []
            d = with_att(SAMPLES["table"], n=42)
            for n in (41, 42):
                h = one(d if n == 42 else example(), script)["cards"][str(n)]["card"]
                ps = panes(h)
                want = ["Background", "Attached"] + (["Dependencies"] if n == 42 else []) + (["Rejected alternatives"] if n == 41 else [])
                if ps != want:
                    out.append("%d: %s" % (n, ps))
                if '<details class="pane" open><summary>Attached' in h or '<details class="att" open' in h:
                    out.append("%d: open" % n)
            return out
        self.assertEqual(problems(), [])
        # mutants: after Rejected alternatives; the fold open; an entry open
        moved = mutant_page("    +attachedFold(c)\n", "").replace("    +rejectedFold(c)\n", "    +rejectedFold(c)+attachedFold(c)\n", 1)
        self.assertTrue(problems(moved))
        self.assertTrue(problems(mutant_page("return '<details class=\"pane\"><summary>Attached'",
                                             "return '<details class=\"pane\" open><summary>Attached'")))
        self.assertTrue(problems(mutant_page("return '<details class=\"att\"'+", "return '<details class=\"att\" open'+")))

    def test_the_summary_counts_and_names_each_title(self):
        d = with_att(SAMPLES["table"], dict(SAMPLES["steps"], title="Undo [[42]]'s `move`"))
        f = fold(one(d)["cards"]["41"]["card"])
        self.assertIn('<span class="fsum">2: Homes · Undo 42&#39;s <code>move</code></span></summary>', f)
        self.assertNotIn("<button", f[:f.index("</summary>")])
        # mutant: the count dropped
        f = fold(one(d, mutant_page("'+as.length+': '+as.map", "'+as.map"))["cards"]["41"]["card"])
        self.assertNotIn(">2: ", f)

    def test_each_kind_has_its_shape_and_pill(self):
        for k in KINDS:
            with self.subTest(k):
                res = one(with_att(SAMPLES[k]))
                self.assertEqual(res["bad"], [], k)
                f = fold(res["cards"]["41"]["card"])
                self.assertIn('<span class="pill akind">' + PILLS[k] + '</span>', f, k)
                for m in SHAPES[k]:
                    self.assertIn(m, f, (k, m))
        # mutants: the table drawn as a list; steps unnumbered; the tally gone
        self.assertNotIn("<table>", fold(one(with_att(SAMPLES["table"]), mutant_page(
            "return '<div class=\"atbl\" tabindex=\"0\"><table>", "return '<div class=\"atbl\" tabindex=\"0\"><ul>"))["cards"]["41"]["card"]))
        self.assertNotIn('<ol class="asteps">', fold(one(with_att(SAMPLES["steps"]), mutant_page(
            "return '<ol class=\"asteps\">'", "return '<ul class=\"asteps\">'"))["cards"]["41"]["card"]))
        self.assertNotIn("atally", fold(one(with_att(SAMPLES["checks"]), mutant_page(
            "return '<p class=\"atally\">'+CHECK_STATES.map(st=>xs.filter(x=>x.s===st).length+' '+st).join(\" · \")+'</p><ul",
            "return '<ul"))["cards"]["41"]["card"]))

    def test_an_excerpt_body_is_data_never_parsed(self):
        a = dict(SAMPLES["excerpt"], body={"text": "see [[42]] and `x` and [[att:x|me]]\n<script>alert(1)</script>"})
        f = fold(one(with_att(a))["cards"]["41"]["card"])
        body = f[f.index('<pre class="xpre"'):]
        self.assertIn("see [[42]] and `x` and [[att:x|me]]", body)
        self.assertIn("&lt;script&gt;", body)
        self.assertNotIn("<button", body)

    def test_every_text_is_escaped(self):
        def places(v):
            return {
                "title": dict(SAMPLES["table"], title=v),
                "src": dict(SAMPLES["table"], src=v),
                "pointer": dict(SAMPLES["summary"], pointer=v),
                "summary": dict(SAMPLES["summary"], body=[v]),
                "link note": dict(SAMPLES["link"], body=v),
                "narrative": dict(SAMPLES["example"], body=[v]),
                "heading": {"kind": "table", "title": "t", "body": {"cols": [v], "rows": [["x"]]}},
                "cell": {"kind": "matrix", "title": "t", "body": {"cols": ["a"], "rows": [[v]]}},
                "step": {"kind": "steps", "title": "t", "body": [{"t": v, "d": v}]},
                "check": {"kind": "checks", "title": "t", "body": [{"s": "fail", "t": v, "d": v}]},
                "node": {"kind": "depmap", "title": "t", "body": [{"n": 99, "name": v, "rel": v, "note": v}]},
            }

        def problems(script=None):
            out = []
            for v in HOSTILE:
                for where, a in places(v).items():
                    h = one(with_att(a), script)["cards"]["41"]["card"]
                    f = fold(h)
                    if not f:
                        out.append("%s %r: no fold" % (where, v))
                    elif "<script" in f or "<img" in f:
                        out.append("%s %r renders raw" % (where, v))
            return out
        self.assertEqual(problems(), [])
        # mutants: a cell, a step, a check, a node's name and the title each drawn raw
        for old, new in (("r.map(x=>'<td>'+fmt(x)+'</td>')", "r.map(x=>'<td>'+x+'</td>')"),
                         ("'<li><span class=\"stt\">'+fmt(x.t)+'</span>'+(isTxt(x.d)&&shown(x.d)?'<span class=\"std\">'+fmtD(x.d)+'</span>':'')+'</li>').join(\"\")+'</ol>'",
                          "'<li><span class=\"stt\">'+x.t+'</span></li>').join(\"\")+'</ol>'"),
                         ("<span><span class=\"stt\">'+fmt(x.t)+'</span>", "<span><span class=\"stt\">'+x.t+'</span>"),
                         ("(isTxt(x.name)?' · '+fmtPlain(x.name):'')", "(isTxt(x.name)?' · '+x.name:'')"),
                         ("<span class=\"at\">'+fmtPlain(a.title)+'</span>'", "<span class=\"at\">'+a.title+'</span>'"),
                         ("'<span class=\"pill akind\">'+esc(ATT_KINDS[a.kind])", "'<span class=\"pill akind\">'+a.title")):
            with self.subTest(old[:40]):
                self.assertTrue(problems(mutant_page(old, new)))

    def test_none_is_not_shown(self):
        for v in ([], [dict(SAMPLES["table"], title="none")]):
            res = one(with_att(*v))
            self.assertEqual(res["bad"], [], v)
            self.assertNotIn("<summary>Attached", res["cards"]["41"]["card"], v)
        # mutant: the none test gone from the titles
        h = one(with_att(dict(SAMPLES["table"], title="none")),
                mutant_page("isTxt(a.title)&&shown(a.title)):[]", "isTxt(a.title)):[]"))["cards"]["41"]["card"]
        self.assertIn("<summary>Attached", h)

    def test_a_link_never_shows_its_markup_where_it_cannot_link(self):
        d = example()
        c = card(d, 41)
        c["t"] = "Docs build ([[att:log|the log]])"
        c["options"][0]["title"] = "Keep [[att:log|the log]]"
        c["rejected"][0]["t"] = "Office machine ([[att:log|the log]])"
        c["why"] = "Two broken publishes ([[att:log|the log]]) this month. Blocks [[42]]."
        h = one(d)["cards"]["41"]["card"]
        self.assertNotIn("[[att:", h)
        self.assertIn("<h3>Docs build (the log)", h)
        self.assertIn("Keep the log", h)
        self.assertIn("1: Office machine (the log)", h)
        self.assertIn("why now: Two broken publishes (the log) this month.", h)
        for old, new in (('esc(c.t.replace(ATT_LINK,"$2"))', "esc(c.t)"),
                         ('esc(o.title.replace(ATT_LINK,"$2"))+(isRec', "esc(o.title)+(isRec"),
                         ('r.t.trim().replace(ATT_LINK,"$2")', "r.t.trim()"),
                         ('c.why.trim().replace(ATT_LINK,"$2")', "c.why.trim()")):
            with self.subTest(old):
                self.assertIn("[[att:", one(d, mutant_page(old, new))["cards"]["41"]["card"])

    def test_a_slug_and_a_tooltip_never_show_link_markup(self):
        harness = r"""
const d=JSON.parse(require("fs").readFileSync(0,"utf8"));
CARDS=d.cards;REFS=d.refs||{};FOLLOW=d.follow;byN=new Map(CARDS.map(c=>[String(c.n),c]));FOLLOW_KEYS=new Set(FOLLOW.map(f=>f[0]));answers={};
process.stdout.write(JSON.stringify({slug:slug("41"),tip:tipHtml("41")}));
"""
        d = example()
        card(d, 41)["t"] = "Docs build ([[att:log|the log]])"
        card(d, 41)["options"][0]["title"] = "Keep [[att:log|the log]]"

        def run(script):
            out = subprocess.run([shutil.which("node"), "-e", script + harness], input=json.dumps(d),
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(out.returncode, 0, out.stderr[:300])
            return json.loads(out.stdout)
        r = run(page_free_script())
        self.assertIn("41 · Docs build (the log)", r["slug"])
        self.assertIn("Keep the log", r["tip"])
        self.assertNotIn("[[att:", r["slug"] + r["tip"])
        # mutants: nameOf and the tooltip's option title raw again
        self.assertIn("[[att:", run(mutant_page('if(c)return c.t.replace(ATT_LINK,"$2");', "if(c)return c.t;"))["slug"])
        self.assertIn("[[att:", run(mutant_page(""")</span> '+esc(o.title.replace(ATT_LINK,"$2"))""", """)</span> '+esc(o.title)"""))["tip"])

    def test_a_source_line_falls_back_to_the_excerpts_own(self):
        a = {k: v for k, v in SAMPLES["excerpt"].items() if k != "src"}
        a["body"] = dict(a["body"], src="upload/handler.go:40-45 at 3f2a9c1")
        h = fold(one(with_att(a))["cards"]["41"]["card"])
        self.assertIn('<span class="asrc">upload/handler.go:40-45 at 3f2a9c1</span>', h)
        self.assertNotIn("has no source line", runner(with_att(a))[1])
        # mutants: the page's fallback and the runner's each gone
        h = fold(one(with_att(a), mutant_page(':xcOk(a.body)&&isTxt(a.body.src)&&shown(a.body.src)?a.body.src:""', ':""'))["cards"]["41"]["card"])
        self.assertNotIn('class="asrc"', h)
        js = mutant_runner(" && !(isExcerptObj(b) && shownSrc(b.src))", "")
        self.assertIn("has no source line", runner(with_att(a), script=js)[1])

    def test_a_dependency_map_is_at_most_eight_deep(self):
        def deep(n):
            node = {"n": 41, "name": "leaf"}
            for i in range(n - 1):
                node = {"n": 41, "name": "level", "kids": [node]}
            return dict(SAMPLES["depmap"], body=[node])
        self.assertEqual(one(with_att(deep(8)))["bad"], [])
        bad = one(with_att(deep(9)))["bad"]
        self.assertTrue(any("is deeper than 8 levels" in b for b in bad), bad)
        self.assertEqual(one(with_att(deep(9)), mutant_page("if(lv>DEP_DEPTH){", "if(false){"))["bad"], [])

    def test_a_link_opens_its_attachment(self):
        h = one(example())["cards"]["41"]["card"]
        self.assertIn('(<button type="button" class="attref" data-att="log" data-n="41">the second failed build</button>)', h)
        self.assertIn('id="att-41-log"', h)
        # an id the card does not hold, and the same link off a card, are the label as plain text
        d = example()
        card(d, 41)["evidence"] = "see [[att:nope|the log]]"
        self.assertIn("see the log", one(d)["cards"]["41"]["card"])
        # mutant: the button never drawn
        h = one(example(), mutant_page("CUR&&attIds(CUR).has(id)?", "false?"))["cards"]["41"]["card"]
        self.assertNotIn('class="attref"', h)
        # openAtt, on a stand-in page: the card, the Attached fold and the entry open
        harness = r"""
const mk=id=>({id,open:false,closest(s){return s==="details.pane"?pane:null}});
const pane={open:false},card=mk("card-41"),att=mk("att-41-log");
const root={getElementById:id=>({"card-41":card,"att-41-log":att})[id]||null};
const got=openAtt(root,"41","log"),none=openAtt(root,"41","nope");
process.stdout.write(JSON.stringify({got:!!got,none,card:card.open,pane:pane.open,att:att.open}));
"""

        def run(script):
            out = subprocess.run([NODE, "-e", script + harness], capture_output=True, text=True, timeout=60)
            self.assertEqual(out.returncode, 0, out.stderr[:300])
            return json.loads(out.stdout)
        self.assertEqual(run(page_free_script()), {"got": True, "none": None, "card": True, "pane": True, "att": True})
        # mutant: the fold left closed
        self.assertFalse(run(mutant_page("if(f)f.open=true;", ""))["pane"])

    CASES = {
        "attached must be a list of attachments": [lambda c: c.__setitem__("attached", {"kind": "table"})],
        "attached 1 must be an object": [lambda c: c["attached"].__setitem__(0, "a log")],
        "attached 1 kind must be one of excerpt, summary, link, example, preview, table, matrix, steps, checks, depmap": [
            lambda c: c["attached"][0].__setitem__("kind", "image"),
            lambda c: c["attached"][0].__setitem__("kind", "constructor")],
        "evidence is the card's own evidence": [lambda c: c["attached"][0].__setitem__("kind", "evidence")],
        "attached 1 (excerpt) url is not a field a excerpt attachment has": [lambda c: c["attached"][0].__setitem__("url", "https://x.example")],
        "attached 1 (excerpt) id must be lower-case letters": [lambda c: c["attached"][0].__setitem__("id", "Log 1")],
        "attached 2 (table) id log is used twice": [lambda c: c["attached"][1].__setitem__("id", "log")],
        "attached 1 (excerpt) needs its title, one line of text": [
            lambda c: c["attached"][0].pop("title"), lambda c: c["attached"][0].__setitem__("title", "a\nb")],
        "attached 1 (excerpt) src must be one line of text": [lambda c: c["attached"][0].__setitem__("src", "a\u2028b")],
        "attached 1 (excerpt) body: an excerpt needs text": [lambda c: c["attached"][0].__setitem__("body", {"text": " "})],
        "attached 2 (table) body must be {cols, rows}": [
            lambda c: c["attached"][1].__setitem__("body", [["a"]]),
            lambda c: c["attached"][1]["body"].__setitem__("cols", []),
            lambda c: c["attached"][1]["body"].__setitem__("extra", 1)],
        "attached 2 (table) body rows must be a non-empty list": [lambda c: c["attached"][1]["body"].__setitem__("rows", [])],
        "attached 2 (table) body row 2 must be a list of 4 cells": [
            lambda c: c["attached"][1]["body"]["rows"][1].pop(),
            lambda c: c["attached"][1]["body"]["rows"][1].__setitem__(0, "a\nb")],
        "attached 3 (checks) body check 3 must be {s, t, d}": [
            lambda c: c["attached"][2]["body"][2].__setitem__("s", "skipped"),
            lambda c: c["attached"][2]["body"][2].__setitem__("why", "x")],
        "attached 3 (checks) body must be a non-empty list of check results": [lambda c: c["attached"][2].__setitem__("body", [])],
    }
    KIND_CASES = {
        "(preview) needs its source line": dict(SAMPLES["preview"], src=None),
        "(example) form must be mock (a code block) or narrative (prose)": {k: v for k, v in SAMPLES["example"].items() if k != "form"},
        "(example) body (a mock): an excerpt must be": dict(SAMPLES["example"], form="mock"),
        "(example) body (a narrative) must be text": dict(SAMPLES["example"], body=[]),
        "(summary) pointer must be one line of text": dict(SAMPLES["summary"], pointer="a\nb"),
        "(link) url must be one https:// address": dict(SAMPLES["link"], url="javascript:alert(1)"),
        "(steps) body step 2 must be {t, d}": dict(SAMPLES["steps"], body=[{"t": "a"}, {"d": "b"}]),
        "(steps) body step 1 d must be text": dict(SAMPLES["steps"], body=[{"t": "a", "d": 3}]),
        "(depmap) body node 1.1 must be {n, name, rel, note, kids}": dict(SAMPLES["depmap"], body=[{"n": 41, "name": "x", "kids": [{"n": "a", "name": "y"}]}]),
        "(depmap) body node 1 kids must be a non-empty list": dict(SAMPLES["depmap"], body=[{"n": 41, "name": "x", "kids": []}]),
    }

    def test_check_refuses_a_malformed_attachment(self):
        for needle, puts in self.CASES.items():
            for i, put in enumerate(puts):
                with self.subTest(needle=needle, i=i):
                    d = example()
                    put(card(d, 41))
                    bad = one(d)["bad"]
                    self.assertTrue(any(b.startswith("card 41: ") and needle in b for b in bad), (needle, bad))
        for needle, a in self.KIND_CASES.items():
            with self.subTest(needle=needle):
                a = {k: v for k, v in a.items() if v is not None}
                bad = one(with_att(a))["bad"]
                self.assertTrue(any(b.startswith("card 41: attached 1 ") and needle in b for b in bad), (needle, bad))
        # mutants: the list test, the kind test, the field test, the id test and the duplicate test each gone
        d = example()
        card(d, 41)["attached"] = {"kind": "table"}
        # with the list test gone the check stops on the object instead of refusing it
        with self.assertRaisesRegex(AssertionError, "node failed"):
            one(d, mutant_page('if(!Array.isArray(c.attached))bad.push(', 'if(false)bad.push('))
        d = example()
        card(d, 41)["attached"][0]["kind"] = "image"
        # the kind test gone, an unknown kind passes the check (and the fold leaves it out)
        self.assertEqual(one(d, mutant_page("if(!isAttKind(a.kind))return [", "if(false)return ["))["bad"], [])
        d = example()
        card(d, 41)["attached"][0]["url"] = "https://x.example"
        self.assertEqual(one(d, mutant_page("if(!keys.includes(x))out.push(", "if(false)out.push("))["bad"], [])
        d = example()
        card(d, 41)["attached"][1]["id"] = "log"
        self.assertEqual(one(d, mutant_page("if(ids.has(a.id))bad.push(", "if(false)bad.push("))["bad"], [])
        a = dict(SAMPLES["link"], url="javascript:alert(1)")
        self.assertEqual(one(with_att(a), mutant_page('if(!(typeof a.url==="string"&&ATT_URL.test(a.url)))out.push(',
                                                      'if(false)out.push('))["bad"], [])

    def test_the_digest_carries_the_attachment_fields(self):
        schema, digest = SCHEMA.read_text(), DIGEST.read_text()

        def required_problems(a, b, h):
            # the field table only: the kind table's rows, in the same section, have their own check
            return [x for x in field_problems(a, b, h) if not any("`%s`" % k in x for k in KINDS)]
        self.assertEqual(required_problems(schema, digest, "An attachment"), [])
        # mutants: a field dropped from the digest; a Required cell changed
        gone = re.sub(r"^\| `pointer` \|.*\n", "", digest, count=1, flags=re.M)
        self.assertIn("An attachment: `pointer` missing", required_problems(schema, gone, "An attachment"))
        req = digest.replace("| `title` | yes |", "| `title` | no |", 1)
        self.assertTrue(required_problems(schema, req, "An attachment"))

    def test_the_kind_list_is_one_list(self):
        html = (SKILL / "assets" / "index.html").read_text()
        m = re.search(r"const ATT_KINDS=\{(.*?)\};", html, re.S)
        page = re.findall(r"(\w+):\"", m.group(1))
        self.assertEqual(page, KINDS)
        up = re.search(r"const ATT_KINDS = \[(.*?)\];", UPGRADER.read_text()).group(1)
        self.assertEqual(re.findall(r'"(\w+)"', up), KINDS)
        self.assertEqual(kind_problems(DIGEST.read_text(), "writer-digest.md"), [])
        self.assertEqual(kind_problems(SCHEMA.read_text(), "cards-schema.md"), [])
        rows = re.findall(r"^\| `([a-z]+)`(?:, `([a-z]+)`)?(?:, an `example` in `mock` form)? \|", RENDERING.read_text(), re.M)
        chat = {k for r in rows for k in r if k} | {"example"}
        self.assertEqual(chat, set(KINDS))
        # mutant: a kind dropped from the digest's table
        cut = re.sub(r"^\| `depmap` \|.*\n", "", DIGEST.read_text(), flags=re.M)
        self.assertTrue(kind_problems(cut, "mutant"))


def kind_problems(text, where):
    """The `## An attachment` section's kind table against the page's list."""
    body = section(text, "An attachment")
    kinds = [c[0].strip("`") for c in table_rows(body) if re.fullmatch(r"`[a-z]+`", c[0]) and c[0].strip("`") in KINDS + ["evidence"]]
    kinds = [k for k in kinds if k not in ("id", "kind", "title", "src", "body", "url", "pointer", "form")]
    return [] if kinds == KINDS else ["%s: the kinds are %s" % (where, kinds)]


def fake(prefix, n, alphabet="A"):
    """A made-up token of the right shape, built at run time so no file holds one."""
    return prefix + alphabet * n


SECRETS = {
    "a private key block": "-----BEGIN RSA PRIVATE KEY-----",
    "a GitHub token": "token " + fake("ghp_", 36),
    "a Slack token": fake("xoxb-", 24, "1"),
    "an AWS access key": "key " + fake("AKIA", 16, "Q"),
    "an API key": "use " + fake("sk-", 30, "b"),
    "an assignment of a secret, key db_password": "db_password = \"" + "x7" * 10 + "\"",
}


@unittest.skipUnless(NODE, "node is not installed")
class AttachRunner(unittest.TestCase):

    def test_the_example_is_clean_and_so_is_its_record(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        self.assertEqual(run_record(record_of(card(example(), 41))), (0, ""))

    def test_a_link_to_an_id_the_card_does_not_hold_is_refused(self):
        for text, needle in (("see [[att:nope|the log]]", "card 41: context links attachment nope, which the card does not attach"),
                             ("see [[att:log]]", "card 41: context has a link to an attachment not written [[att:id|label]]"),
                             ("see [[att:Log|x]]", "card 41: context has a link to an attachment not written")):
            with self.subTest(text):
                d = example()
                card(d, 41)["context"] += " " + text
                code, out = runner(d)[:2]
                self.assertEqual(code, 1, out)
                self.assertIn(needle, out)
        # in a record too; an excerpt's text is data, never read
        rec = record_of(card(example(), 41))
        rec["attached"][1]["body"]["rows"][0][0] = "[[att:nope|x]]"
        code, out = run_record(rec)
        self.assertEqual(code, 1, out)
        self.assertIn("record 41: attached[1].body.rows[0][0] links attachment nope", out)
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] += "\n[[att:nope|x]]"
        self.assertEqual(runner(d)[0], 0)
        # mutant: the refusal gone
        d = example()
        card(d, 41)["context"] += " see [[att:nope|the log]]"
        js = mutant_runner("else if (!ids.has(f[1])) out.push(", "else if (false) out.push(")
        self.assertNotEqual(runner(d, script=js)[0], 1)

    def test_a_secret_is_refused_by_where_and_key_never_its_value(self):
        for name, line in SECRETS.items():
            with self.subTest(name):
                d = example()
                card(d, 41)["attached"][0]["body"]["text"] += "\n" + line
                code, out = runner(d)[:2]
                self.assertEqual(code, 1, out)
                self.assertIn("card 41: attached 1.body.text line 5 looks like it holds a secret (" + name + ")", out)
                value = line.split()[-1].strip('"')
                if name != "a private key block":
                    self.assertNotIn(value, out)
        # in a table cell, in a record, and in the Finding's excerpt
        rec = record_of(card(example(), 41))
        rec["attached"][1]["body"]["rows"][0][1] = "api_key: " + "Z9" * 12
        code, out = run_record(rec)
        self.assertEqual(code, 1, out)
        self.assertIn("record 41: attached 2.body.rows[0][1] line 1 looks like it holds a secret (an assignment of a secret, key api_key)", out)
        d = example()
        card(d, 43)["finding"]["excerpt"]["text"] += "\npassword: " + "q1" * 9
        code, out = runner(d)[:2]
        self.assertEqual(code, 1, out)
        self.assertIn("card 43: finding.excerpt.text line", out)
        # not a secret: a short value, a prose mention
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] += "\ntoken = abc\nthe token is kept in the CI secrets"
        self.assertEqual(runner(d)[0], 0)
        # mutant: the secret check gone
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] += "\n" + SECRETS["a GitHub token"]
        js = mutant_runner("const attRefusals = (c, w) => [...attLinkProblems(c, w), ...secretProblems(c, w)];",
                           "const attRefusals = (c, w) => [...attLinkProblems(c, w)];")
        self.assertNotEqual(runner(d, script=js)[0], 1)

    def test_the_grep_step_runs_the_runners_patterns(self):
        self.assertEqual(grep_problems(PAGE_SKILL.read_text(), RUNNER_JS.read_text()), [])
        grep = shutil.which("grep")
        if not grep:
            self.skipTest("no grep")
        args = grep_args(PAGE_SKILL.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "cards.json"
            p.write_text(json.dumps(example(), indent=1))
            self.assertEqual(subprocess.run([grep, *args, str(p)], capture_output=True, text=True).returncode, 1)
            for name, line in SECRETS.items():
                d = example()
                card(d, 41)["attached"][0]["body"]["text"] += "\n" + line
                p.write_text(json.dumps(d, indent=1))
                out = subprocess.run([grep, *args, str(p)], capture_output=True, text=True)
                self.assertEqual(out.returncode, 0, name)
        # a token after a JSON escape: at a line's start (after \\n), after a tab, after a curly quote (\\u201c), and
        # the runner the same on the real text
        tok = fake("ghp_", 36, "C")
        for name, text in (("line start", "first line\n" + tok), ("tab", "x\t" + tok), ("curly quote", "\u201c" + tok + "\u201d"),
                           ("key", "x\n" + fake("AKIA", 16, "R")), ("api key", "x\t" + fake("sk-", 24, "d"))):
            with self.subTest(name):
                d = example()
                card(d, 41)["attached"][0]["body"]["text"] = text
                with tempfile.TemporaryDirectory() as tmp:
                    p = pathlib.Path(tmp) / "cards.json"
                    p.write_text(json.dumps(d, indent=1))
                    self.assertEqual(subprocess.run([grep, *args, str(p)], capture_output=True, text=True).returncode, 0, name)
                self.assertEqual(runner(d)[0], 1, name)
        # mutant: the JSON-escape boundary gone from the grep: a token after \\n is missed
        cut = PAGE_SKILL.read_text().replace("|\\\\[nrtbf]|\\\\u[0-9A-Fa-f]{4})(ghp", ")(ghp", 1)
        self.assertNotEqual(cut, PAGE_SKILL.read_text())
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] = "first line\n" + tok
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "cards.json"
            p.write_text(json.dumps(d, indent=1))
            self.assertEqual(subprocess.run([grep, *grep_args(cut), str(p)], capture_output=True, text=True).returncode, 1)
        # mutants: a pattern dropped from the skill's grep; one dropped from the runner; one changed in the grep
        cut = PAGE_SKILL.read_text().replace("    -e 'glpat-[A-Za-z0-9_-]{20,}' \\\n", "", 1)
        self.assertIn("the runner's pattern glpat-[A-Za-z0-9_-]{20,} is not in the grep step", grep_problems(cut, RUNNER_JS.read_text()))
        js = RUNNER_JS.read_text().replace('  ["a GitLab token", "glpat-[A-Za-z0-9_-]{20,}"],\n', "", 1)
        self.assertIn("the grep step's pattern glpat-[A-Za-z0-9_-]{20,} is not the runner's", grep_problems(PAGE_SKILL.read_text(), js))
        changed = PAGE_SKILL.read_text().replace("-e 'xox[abprs]-", "-e 'xox[ab]-", 1)
        self.assertEqual(len(grep_problems(changed, RUNNER_JS.read_text())), 2)
        # the step prints line numbers only
        self.assertIn("    cards.json | cut -d: -f1\n", PAGE_SKILL.read_text())

    def test_the_key_is_echoed_only_when_it_cannot_be_the_value(self):
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] = "Zx9Qw8Er7Ty6Ui5Op4Lk-secret: whatever-goes-here-long"
        code, out = runner(d)[:2]
        self.assertEqual(code, 1, out)
        self.assertIn("(an assignment of a secret, its key holds secret)", out)
        for part in ("Zx9Q", "Op4Lk", "whatever"):
            self.assertNotIn(part, out)
        # a plain key still prints
        card(d, 41)["attached"][0]["body"]["text"] = "db_password = " + "x7" * 10
        self.assertIn("key db_password)", runner(d)[1])
        # mutant: every key echoed
        card(d, 41)["attached"][0]["body"]["text"] = "Zx9Qw8Er7Ty6Ui5Op4Lk-secret: whatever-goes-here-long"
        js = mutant_runner("&& !/[A-Za-z0-9]{8,}/.test(k.replace(m[1], \"-\")) ? k : null;", "? k : null;")
        self.assertIn("Zx9Qw8Er7Ty6Ui5Op4Lk", runner(d, script=js)[1])

    def test_a_fallen_back_key_names_its_keyword_and_leaves_the_name_to_fill(self):
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] = "DATABASE_PASSWORD = " + "x7" * 10
        code, out = runner(d)[:2]
        self.assertEqual(code, 1, out)
        self.assertIn("(an assignment of a secret, its key holds PASSWORD)", out)
        self.assertIn("[redacted: key <name> in <where it is kept>]", out)
        self.assertNotIn("DATABASE", out)
        # mutant: the fallback names nothing
        js = mutant_runner('asg ? ", its key holds " + m[1] : ""', '""')
        self.assertNotIn("its key holds", runner(d, script=js)[1])

    def test_a_long_key_or_wide_spacing_still_hits_on_both_sides(self):
        grep = shutil.which("grep")
        args = grep_args(PAGE_SKILL.read_text())
        for text in ("password_for_the_service_running_in_production_east = Zx9Qw8Er7Ty6Ui5Op4Lk",
                     "password" + " " * 50 + "= Zx9Qw8Er7Ty6Ui5Op4Lk"):
            with self.subTest(text[:30]):
                d = example()
                card(d, 41)["attached"][0]["body"]["text"] = text
                self.assertEqual(runner(d)[0], 1)
                if grep:
                    with tempfile.TemporaryDirectory() as tmp:
                        f = pathlib.Path(tmp) / "cards.json"
                        f.write_text(json.dumps(d, indent=1))
                        self.assertEqual(subprocess.run([grep, *args, str(f)], capture_output=True, text=True).returncode, 0)
        # mutant: the suffix back at 40, in the runner: the long key passes
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] = "password_for_the_service_running_in_production_east = Zx9Qw8Er7Ty6Ui5Op4Lk"
        js = mutant_runner("access[_-]?key)[A-Za-z0-9_-]{0,80}", "access[_-]?key)[A-Za-z0-9_-]{0,40}")
        self.assertNotEqual(runner(d, script=js)[0], 1)
        # the documented misses, in all three places
        net = "The patterns are a net, not a proof"
        self.assertIn(net, " ".join(PAGE_SKILL.read_text().split()))
        self.assertIn(net, " ".join(SCHEMA.read_text().split()))
        self.assertIn(net, " ".join(RUNNER_JS.read_text().split()))

    def test_a_long_line_does_not_make_the_assignment_backtrack(self):
        import time
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] = '"token"' * 2400
        t = time.monotonic()
        runner(d)
        self.assertLess(time.monotonic() - t, 3.0)
        node = shutil.which("node")
        pat = [p for p in runner_patterns(RUNNER_JS.read_text()) if "password" in p][0]
        bench = "const r=new RegExp(%s,'i'),s='\"token\"'.repeat(2400),t=Date.now();r.test(s);process.stdout.write(String(Date.now()-t))"
        ms = int(subprocess.run([node, "-e", bench % json.dumps(pat)], capture_output=True, text=True, timeout=60).stdout)
        self.assertLess(ms, 500)
        # the bounds are there: no unbounded star in the assignment
        self.assertNotIn("*", pat)

    def test_the_id_lint_reads_the_shown_texts_never_an_excerpt(self):
        for where, put in (("title", lambda a: a[1].__setitem__("title", "Homes per OQ3")),
                           ("src", lambda a: a[1].__setitem__("src", "from OQ3")),
                           ("cell", lambda a: a[1]["body"]["rows"][0].__setitem__(0, "OQ3")),
                           ("check", lambda a: a[2]["body"][0].__setitem__("t", "OQ3 builds"))):
            with self.subTest(where):
                d = example()
                put(card(d, 41)["attached"])
                self.assertIn("lint: card 41: OQ3 looks like an id (attached)", runner(d)[1])
                js = mutant_runner('  put("attached", attachedTexts(c));\n', "")
                self.assertNotIn("OQ3 looks like an id", runner(d, script=js)[1])
        d = example()
        card(d, 41)["attached"][0]["body"]["text"] += "\nOQ3 7c41e0d"
        self.assertNotIn("looks like an id", runner(d)[1])

    def test_the_cold_read_reads_the_titles(self):
        d = example()
        card(d, 41)["attached"][1]["title"] = "The seven build homes"
        self.assertIn('lint: card 41: "seven" (attached) counts things its context does not name', runner(d)[1])
        js = mutant_runner('  terms(page.attachedOf(c).map(a => a.title), " (attached)");\n', "")
        self.assertNotIn("(attached)", runner(d, script=js)[1])
        # a count in a body is not read
        d = example()
        card(d, 41)["attached"][2]["body"][0]["t"] = "the seven pages build"
        self.assertNotIn("(attached)", runner(d)[1])

    def test_they_never_count_in_the_card_in_all(self):
        d = with_att(dict(SAMPLES["summary"], body=" ".join(["word"] * 1400)))
        self.assertNotIn("depth: the card is", runner(d)[1])
        js = mutant_runner("+ words(rejectedTexts(c)) ", "+ words(rejectedTexts(c)) + words(attachedTexts(c)) ")
        self.assertIn("depth: the card is", runner(d, script=js)[1])

    def test_the_attached_lint_asks_for_a_source(self):
        d = with_att(SAMPLES["table"], SAMPLES["example"])
        out = runner(d)[1]
        self.assertIn("lint: card 41: depth: attachment 1 (Homes) has no source line", out)
        self.assertNotIn("attachment 2 (A restore) has no source line", out)
        self.assertNotIn("has no source line", runner(example())[1])
        js = mutant_runner('if (a.kind !== "example" && !shownSrc(a.src)', 'if (false && !shownSrc(a.src)')
        self.assertNotIn("has no source line", runner(d, script=js)[1])

    def test_a_page_with_excerpts_names_its_repos(self):
        self.assertNotIn("lede", runner(example())[1])
        d = example()
        d["page"]["lede"] = "Three invented decisions about a documentation site."
        out = runner(d)[1]
        self.assertIn("lint: page: lede names no repo, though the page shows excerpts", out)
        # a Finding's excerpt alone counts too; a page with none needs no repo
        card(d, 41).pop("attached")
        card(d, 41)["evidence"] = "Build logs."
        self.assertIn("lede names no repo", runner(d)[1])
        card(d, 43)["finding"].pop("excerpt")
        self.assertNotIn("lede names no repo", runner(d)[1])
        # mutant: the lint gone
        d = example()
        d["page"]["lede"] = "Three invented decisions about a documentation site."
        js = mutant_runner("  if (xc && !(typeof pg.lede", "  if (false && !(typeof pg.lede")
        self.assertNotIn("lede names no repo", runner(d, script=js)[1])

    def test_the_attached_lint_sizes_them(self):
        d = with_att(*[dict(SAMPLES["table"], title="Table %d" % i) for i in range(7)])
        self.assertIn("lint: card 41: depth: the card carries 7 attachments", runner(d)[1])
        d = with_att(dict(SAMPLES["excerpt"], body={"text": "\n".join("line %d" % i for i in range(81))}))
        self.assertIn("lint: card 41: depth: attachment 1 (The handler) is 81 lines", runner(d)[1])
        d = with_att(dict(SAMPLES["excerpt"], body={"text": "x" * 4097}))
        self.assertIn("4097 bytes", runner(d)[1])
        js = mutant_runner("  attachedSize(c, say);\n", "")
        self.assertNotIn("depth: attachment 1", runner(d, script=js)[1])


GREP_E = re.compile(r"-e '([^']*)'")


def grep_args(skill):
    block = skill[skill.index("  grep -nEi "):]
    block = block[:block.index("cards.json")]
    return ["-nEi"] + [x for p in GREP_E.findall(block) for x in ("-e", p)]


def runner_patterns(js):
    """The runner's SECRET_PATTERNS, each JavaScript string literal decoded to the pattern it holds."""
    block = js[js.index("const SECRET_PATTERNS = ["):]
    return [json.loads('"' + x + '"') for x in re.findall(r'\["[^"]+", "((?:[^"\\]|\\.)*)"\]', block[:block.index("];")])]


def grep_problems(skill, js):
    """The skill's grep step against the runner's SECRET_PATTERNS, both ways: each of the runner's in the grep, each of
    the grep's in the runner, in the same order."""
    want, have = runner_patterns(js), grep_args(skill)[2::2]
    out = ["the runner's pattern %s is not in the grep step" % p for p in want if p not in have]
    out += ["the grep step's pattern %s is not the runner's" % p for p in have if p not in want]
    if not want:
        out.append("the runner has no patterns")
    elif not out and have != want:
        out.append("the grep step's patterns are not in the runner's order")
    return out


@unittest.skipUnless(NODE, "node is not installed")
class AttachUpgrade(unittest.TestCase):

    def kit(self):
        return load(KIT)

    def test_the_kit_attachments_map_as_they_stand(self):
        kit = self.kit()
        k51 = card(kit, 51)
        k51["attached"].append(copy.deepcopy(SAMPLES["table"]))
        k51["attached"].append({"kind": "example", "title": "A mock", "mode": "mock", "body": {"text": "x"}})
        k51["attached"].append({"kind": "example", "title": "Mock in words", "mode": "mock", "body": ["the page would read: X", "then Y"]})
        k51["attached"].append({"kind": "depmap", "title": "Waits", "body": [{"n": "52", "name": "thing", "kids": [{"n": " 53 ", "name": "other"}]}]})
        code, out, d = upgrade(kit)[:3]
        self.assertEqual(code, 0, out)
        atts = card(d, 51)["attached"]
        self.assertEqual([a["kind"] for a in atts], ["example", "table", "example", "example", "depmap"])
        self.assertEqual(atts[0]["form"], "narrative")
        self.assertEqual(atts[1], SAMPLES["table"])
        self.assertEqual(atts[2]["form"], "mock")
        # a mode the body does not match: the body decides
        self.assertEqual(atts[3]["form"], "narrative")
        self.assertIn('example "Mock in words" read as form narrative (its body is prose; its mode "mock" dropped)', out)
        # a numeric-string node number is the number
        self.assertEqual(atts[4]["body"], [{"n": 52, "name": "thing", "kids": [{"n": 53, "name": "other"}]}])
        self.assertIn('example "A restore" read as form narrative', out)
        # the upgraded file passes the page's check and the runner
        code, out = runner(d)[:2]
        self.assertNotEqual(code, 1, out)

    def test_a_kind_or_a_shape_it_cannot_map_is_refused(self):
        for put, needle in ((lambda c: c["attached"].append({"kind": "image", "title": "x"}), 'an attachment\'s kind "image" is not one the record has'),
                            (lambda c: c.__setitem__("attached", {"kind": "table"}), "attached is not a list of attachments"),
                            (lambda c: c["attached"].append({"kind": "depmap", "title": "W", "body": [{"n": "x41", "name": "a"}]}),
                             'a depmap node\'s n "x41" is not a decision number'),
                            (lambda c: c["attached"].append({"kind": "depmap", "title": "W", "body": [{"n": 41, "name": "a", "kids": [{"n": 0, "name": "b"}]}]}),
                             "a depmap node's n 0 is not a decision number")):
            with self.subTest(needle):
                kit = self.kit()
                put(card(kit, 51))
                code, out, d = upgrade(kit)[:3]
                self.assertEqual(code, 1, out)
                self.assertIn("card 51: " + needle, out)
                self.assertIsNone(d)
        # a null attached is none, never refused
        kit = self.kit()
        card(kit, 51)["attached"] = None
        code, out, d = upgrade(kit)[:3]
        self.assertEqual(code, 0, out)
        self.assertNotIn("attached", card(d, 51))
        # mutants: the body test gone from the example's form; the numeric-string read gone
        src = UPGRADER.read_text()
        for old, new in (('y.form = xc ? "mock" : "narrative";', 'y.form = m === "mock" ? "mock" : "narrative";'),
                         ('if (isStr(o.n) && /^[1-9][0-9]*$/.test(o.n.trim()))', "if (false)")):
            with self.subTest(old), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(src.count(old), 1)
                js = pathlib.Path(tmp) / "upgrade_cards.js"
                js.write_text(src.replace(old, new))
                kit = self.kit()
                card(kit, 51)["attached"] = [{"kind": "example", "title": "M", "mode": "mock", "body": ["a"]},
                                             {"kind": "depmap", "title": "W", "body": [{"n": "52", "name": "x"}]}]
                code, out, d = upgrade(kit, script=js)[:3]
                self.assertTrue(code == 1 or runner(d)[0] == 1, out)
        # mutant: the kind refusal gone, an unknown kind passes the upgrader
        src = UPGRADER.read_text()
        old = "} else if (!ATT_KINDS.includes(x.kind)) {"
        self.assertEqual(src.count(old), 1)
        with tempfile.TemporaryDirectory() as tmp:
            js = pathlib.Path(tmp) / "upgrade_cards.js"
            js.write_text(src.replace(old, "} else if (false) {"))
            kit = self.kit()
            card(kit, 51)["attached"].append({"kind": "image", "title": "x"})
            self.assertEqual(upgrade(kit, script=js)[0], 0)


@unittest.skipUnless(NODE, "node is not installed")
class AttachKitRegression(unittest.TestCase):
    """The reviewer's kit cases (a mock example whose body is prose, a depmap node numbered as a string) upgrade to
    attachments the page's check() passes."""

    def test_the_upgraded_kit_cases_pass_the_page(self):
        kit = load(KIT)
        card(kit, 51)["attached"] += [{"id": "ex", "kind": "example", "title": "A mock", "mode": "mock", "body": ["the page would read: X", "then Y"]},
                                      {"id": "dm", "kind": "depmap", "title": "Waits", "body": [{"n": "41", "name": "thing"}]}]
        code, out, d = upgrade(kit)[:3]
        self.assertEqual(code, 0, out)
        code, out = runner(d)[:2]
        self.assertNotEqual(code, 1, out)


# the gallery's cards with an Attached line
ATTACHED_CARDS = {52, 53, 86}
ATT_NAME = "Attached"
HEAD = re.compile(r"^\*\*([^*].*?)\*\* · \*([^*]+)\*( — .+)?$")


def att_problems(where, body, block=False):
    """A view's Attached fold against the rules: one at most; after ▸ Background, before any
    ▸ Rejected alternatives; its summary `N: title · title`, N the titles' count; closed on a card,
    open in a block, where each attachment is a bold head line in the summary's order, a blank
    line before each head after the first, and a table only after a blank line."""
    at = [i for i, x in enumerate(body) if (m := FOLD.match(x)) and m.group(2) == ATT_NAME]
    if not at:
        return []
    out = []
    if len(at) > 1:
        out.append(where + ": more than one Attached line")
    k = at[0]
    m = FOLD.match(body[k])
    if m.group(1) != ("▾" if block else "▸"):
        out.append(where + ": the fold is " + ("closed in a block" if block else "open on a card"))
    folds = [(i, f.group(2)) for i, x in enumerate(body) if (f := FOLD.match(x))]
    bg = [i for i, n in folds if n == "Background"]
    rej = [i for i, n in folds if n == "Rejected alternatives"]
    if not bg or bg[0] > k:
        out.append(where + ": the Attached line is not after Background")
    if rej and rej[0] < k:
        out.append(where + ": the Attached line is after Rejected alternatives")
    if any(n not in ("Rejected alternatives",) for i, n in folds if i > k):
        out.append(where + ": a fold other than Rejected alternatives after Attached")
    s = re.match(r"^(\d+): (\S.*)$", m.group(3).replace(" *(only where the decision rests on material)*", ""))
    if not s:
        return out + [where + ": the summary is not 'N: title · title'"]
    titles = s.group(2).split(" · ")
    if int(s.group(1)) != len(titles):
        out.append(where + ": the summary counts %s and names %d" % (s.group(1), len(titles)))
    if block:
        end = next((i for i in range(k + 1, len(body)) if FOLD.match(body[i]) or body[i].startswith("*If you pick ")), len(body))
        part = body[k + 1:end]
        heads, fence = [], None
        for j, x in enumerate(part):
            if fence:
                if x.startswith(fence):
                    fence = None
                continue
            f = re.match(r"^(`{3,}|~{3,})", x)
            if f:
                fence = f.group(1)
                continue
            h = HEAD.match(x)
            if h:
                if heads and (j == 0 or part[j - 1].strip()):
                    out.append(where + ": no blank line before the head of %s" % h.group(1))
                heads.append(h.group(1))
            elif x.startswith("|") and j and not part[j - 1].startswith("|") and part[j - 1].strip():
                out.append(where + ": a table with no blank line before it")
        if heads != titles:
            out.append(where + ": the open fold's heads %s are not the summary's %s" % (heads, titles))
    return out


class AttachChat(unittest.TestCase):

    def test_the_templates_carry_the_fold(self):
        text = RENDERING.read_text()
        card_t = fenced(text, "**N — Title as a question?**\n- the TLDR")
        self.assertTrue(any(x.startswith("▸ Attached — 2: ") for x in card_t))
        self.assertEqual(att_problems("rendering.md card", card_t), [])
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertTrue(any(x.startswith("▾ Attached — 1: ") for x in block))
        self.assertEqual(att_problems("rendering.md block", block, block=True), [])
        lines = text.splitlines()
        k = lines.index("▾ Attached — 2: Last night's write log · The write tests on the change")
        self.assertEqual(lines[k - 1], "````")
        ex = lines[k - 1:lines.index("````", k)]
        self.assertEqual(att_problems("rendering.md § Folds", ["▸ Background — why now: x"] + ex, block=True), [])
        flat = " ".join(text.split())
        self.assertIn("**▸ Attached** — the material the decision rests on", flat)
        self.assertIn("`tell me attached` answers with it open", flat)
        self.assertIn("reads *label (attached)* in chat", flat)

    def test_every_gallery_fold_is_well_formed(self):
        seen = set()
        for n, kind, body in views(GALLERY):
            if any((m := FOLD.match(x)) and m.group(2) == ATT_NAME for x in body):
                seen.add(int(re.match(r"^\*\*(\d+)", body[0]).group(1)))
            self.assertEqual(att_problems(f"gallery.md:{n}", body, kind == "block"), [])
        self.assertEqual(seen, ATTACHED_CARDS)
        text = GALLERY.read_text()
        sec = text[text.index("## 37. Attached, opened"):]
        lines = sec.splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("▾ Attached — "))
        end = next(i for i in range(k, len(lines)) if lines[i].startswith("*Each attachment"))
        body = ["▸ Background — why now: x"] + lines[k:end]
        self.assertEqual(att_problems("gallery.md § 37", body, block=True), [])
        self.assertIn("*Read as: 52 → tell me (attached).*", sec)
        # mutants: the blank line before a head dropped; the blank line before the table dropped
        j = body.index(next(x for x in body if x.startswith("**The write tests")))
        self.assertIn("gallery.md § 37: no blank line before the head of The write tests on the change",
                      att_problems("gallery.md § 37", body[:j - 1] + body[j:], block=True))
        t = next(i for i, x in enumerate(body) if x.startswith("| Who |"))
        self.assertIn("gallery.md § 37: a table with no blank line before it",
                      att_problems("gallery.md § 37", body[:t - 1] + body[t:], block=True))

    def test_the_fold_checks_fail_on_broken_cards(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**52 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("▸ Attached — "))
        bg = next(i for i, x in enumerate(body) if x.startswith("▸ Background — "))
        mutants = {
            "above Background": body[:bg] + [body[k]] + body[bg:k] + body[k + 1:],
            "after Rejected": body[:k] + ["▸ Rejected alternatives — 1: x"] + [body[k]] + body[k + 1:],
            "a miscount": body[:k] + [body[k].replace("— 3: ", "— 2: ")] + body[k + 1:],
            "no summary": body[:k] + ["▸ Attached — Last night's write log"] + body[k + 1:],
            "open on a card": body[:k] + ["▾" + body[k][1:]] + body[k + 1:],
            "twice": body[:k + 1] + [body[k]] + body[k + 1:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(att_problems("mutant", b), name)

    def test_the_skills_the_record_the_worksheet_and_the_ruling_say_it(self):
        skill = " ".join(SKILL_MD.read_text().split())
        self.assertIn("the ▸ Attached fold line (their count and titles)", skill)
        self.assertIn("then any Attached fold open, each attachment's bold head line over its body", skill)
        page_skill = " ".join(PAGE_SKILL.read_text().split())
        self.assertIn("set `attached`: each `{id, kind, title, src, body}`", page_skill)
        self.assertIn("**The secret grep.**", page_skill)
        record = RECORD.read_text()
        self.assertRegex(record, r"\n\| `attached` \| list of attachments \| optional \| \*\*Attached\*\*")
        self.assertIn("three marks render", record)
        self.assertIn("| Attached | the material the decision rests on", (REFS / "worksheet.md").read_text())
        self.assertIn("- **Attached, a fold of its own, both surfaces** (2026-10-20, answer 264 (a)",
                      (REFS / "rulings.md").read_text())
        self.assertIn("| any other attachment | `attached`, as it stands", (REFS / "legacy-cards.md").read_text())
        self.assertIn("**Attached**: each attachment's title on a bold line",
                      " ".join((SKILL / "references" / "fallback.md").read_text().split()))

    def test_no_invisible_separator_in_the_sources(self):
        for p in [*(SKILL.parent.glob("*/SKILL.md")), *(SKILL.parent.glob("*/references/*.md")),
                  *(SKILL.glob("assets/*")), *(SKILL.glob("scripts/*.js")), pathlib.Path(__file__)]:
            t = p.read_text()
            for ch in ("\u2028", "\u2029", "\u200b", "\ufeff"):
                self.assertNotIn(ch, t, "%s holds U+%04X" % (p.name, ord(ch)))


if __name__ == "__main__":
    unittest.main()
