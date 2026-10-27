"""An option's view, on both surfaces: Plan in brief, the Pros | Cons table, then the facets; picking opens it.

The operator's feedback on the v4 prototype ("Selecting an option opens it as if More is pressed (others
that are open in the decision close if a new one is selected)"; the trade-offs in full "display
side-by-side in a two-column table"; the plan in brief "above Effect, Reach, Cost") and the v5 order
(item 9168: the view opens on Plan in brief, then the Pros/Cons table, then the facets):

- the answer page (`decision-page` skill, `assets/index.html`, run under node): an option's view is its
  **Plan in brief** (`plan`, labelled; its levels step from it), then a two-column **Pros | Cons** table
  (`pros`, `cons`, each column headed by the facet label class), then its Effect, Reach, Undo and Cost,
  on every card, a ⚠ card's too; an older option with no `plan` shows its `text` in the plan's place at
  its fullest level. Picking an option opens its view and closes the card's other open one; **More**
  toggles one alone; a follow-up leaves the views as they are. `check()` refuses a `plan` that is not
  text. The runner's `plan` lint (`depth:`) fires on an option with no plan (one line when no option
  has one) and on a plan past PLAN_CAP words; `plan`, `pros` and `cons` join the id lint and the cold
  read, and the table's points the card in all;
- chat (the `decisions` skill): `tell me (x)` answers with the *plan in brief:* line, the
  `Pros | Cons` table, then the facet line; a block shows each option's plan and table under its
  Impact table. Checked against `references/rendering.md` and `references/gallery.md`.

Each check is proved by a mutation: break it, see it fail.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import subprocess
import unittest

from test_chat_context import GALLERY, RENDERING, SKILL_MD, fenced, views
from test_context import RUNNER, runner
from test_depth import card, run_page
from test_impact import NODE, PAGE, example, page_free_script
from test_option_impact import FACET_LINE, impact_rows
from test_pros_cons import esc, opt, page_with, runner_with

REPLIES = RENDERING.parent / "replies.md"
PLAN_LBL = '<span class="lbl">Plan in brief</span>'


def view_problems(h, o):
    """An option's view html in the v5 order: Plan in brief (labelled), then the Pros | Cons table, then
    the facets. Returns the problems, empty when clean."""
    out = []
    marks = []
    if o.get("plan"):
        if not h.startswith('<div class="oplan">' + PLAN_LBL):
            out.append("the view does not open on its Plan in brief")
        marks.append(("plan", h.find(PLAN_LBL)))
    sides = [s for s in ("pros", "cons") if o.get(s)]
    if sides:
        if '<div class="opc">' not in h:
            return out + ["no Pros | Cons table"]
        t = h[h.index('<div class="opc">'):]
        heads = re.findall(r'<div class="opc[pc]"><span class="lbl">(Pros|Cons)</span><ul>', t)
        if heads != [s.capitalize() for s in sides]:
            out.append("the table's heads are %r" % heads)
        for s in sides:
            col = re.search(r'<div class="opc%s"><span class="lbl">%s</span><ul>(.*?)</ul></div>'
                            % (s[0], s.capitalize()), t)
            items = re.findall(r"<li>(.*?)</li>", col.group(1)) if col else []
            if len(items) != len(o[s]):
                out.append("%s shows %d points of %d" % (s, len(items), len(o[s])))
            for got, want in zip(items, o[s]):
                if "[[" not in want and "`" not in want and got != esc(want):
                    out.append("%s point reads %r" % (s, got))
        marks.append(("table", h.index('<div class="opc">')))
    if '<p class="f">' in h:
        marks.append(("facets", h.index('<p class="f">')))
    if [p for _, p in marks] != sorted(p for _, p in marks):
        out.append("the order is %r, not plan, table, facets" % [m for m, _ in sorted(marks, key=lambda x: x[1])])
    return out


@unittest.skipUnless(NODE, "node is not installed")
class PageView(unittest.TestCase):

    def test_every_view_runs_plan_table_facets(self):
        d = example()
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        seen = 0
        for c in d["cards"]:
            more = card(res, c["n"])["more"]
            for o in c["options"]:
                self.assertTrue(o.get("plan"), (c["n"], o["k"]))
                self.assertEqual(view_problems(more[o["k"]], o), [], (c["n"], o["k"]))
                seen += 1
        self.assertEqual(seen, 9)

    def test_mutant_facets_before_the_table_is_caught(self):
        src = page_free_script()
        m = src.replace("return plan+prosConTable(o)+facets;", "return plan+facets+prosConTable(o);", 1)
        self.assertNotEqual(m, src)
        d = example()
        o = opt(d, 41, "b")
        self.assertIn("the order is", " ".join(view_problems(page_with(m, d)["cards"][0]["more"]["b"], o)))
        # and the plan after the table
        m = src.replace("return plan+prosConTable(o)+facets;", "return prosConTable(o)+plan+facets;", 1)
        self.assertTrue(view_problems(page_with(m, d)["cards"][0]["more"]["b"], o))

    def test_the_table_is_two_columns_headed_by_the_facet_label(self):
        html = PAGE.read_text()
        self.assertRegex(html, r"\.opc\{display:grid;grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\)")
        self.assertIn(".opc>.opcp{grid-column:1}", html)
        self.assertIn(".opc>.opcc{grid-column:2}", html)
        # not a <table>: the page's no-table checks stand
        from test_impact import before_attached
        self.assertNotIn("<table", before_attached(card(run_page(example()), 41)["html"]))
        # a side with none is not drawn, and a lone side keeps its own column: 42's (z) gives cons alone
        z = card(run_page(example()), 42)["more"]["z"]
        self.assertIn('<div class="opc"><div class="opcc"><span class="lbl">Cons</span>', z)
        self.assertNotIn('class="opcp"', z)
        # none points are left out; with none on either side there is no table
        d = example()
        opt(d, 43, "a")["pros"] = ["none", "Readers see the site they know"]
        h = card(run_page(d), 43)["more"]["a"]
        self.assertEqual(h.count("<li>"), 1 + len(opt(d, 43, "a")["cons"]))
        for s in ("pros", "cons"):
            opt(d, 43, "a").pop(s)
        self.assertNotIn('class="opc"', card(run_page(d), 43)["more"]["a"])
        # mutant: the heads lose the label class
        src = page_free_script()
        m = src.replace("""'"><span class="lbl">'+l+'</span><ul>'""", """'"><b>'+l+'</b><ul>'""", 1)
        self.assertNotEqual(m, src)
        o = opt(example(), 41, "b")
        self.assertIn("the table's heads are []", view_problems(page_with(m, example())["cards"][0]["more"]["b"], o))

    def test_five_points_a_side_all_shown_six_refused(self):
        d = example()
        five = ["one", "two", "three", "four", "five"]
        opt(d, 41, "b")["pros"] = five
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        self.assertEqual(view_problems(card(res, 41)["more"]["b"], opt(d, 41, "b")), [])
        opt(d, 41, "b")["cons"] = five + ["six"]
        self.assertIn("card 41: (b) cons has 6 points: give at most 5, the weightiest", run_page(d)["bad"])

    def test_the_plan_and_points_are_escaped_and_carry_the_marks(self):
        d = example()
        o = opt(d, 43, "b")
        o["plan"] = "<img src=x onerror=alert(1)> then [[42]] and `theme.css` change."
        o["cons"] = ["</li><script>alert(1)</script>", "[[41]] waits, `a.css` too"]
        h = card(run_page(d), 43)["more"]["b"]
        self.assertNotIn("<img", h)
        self.assertNotIn("<script>", h)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", h)
        plan = h[:h.index('<div class="opc">')]
        table = h[h.index('<div class="opc">'):h.index('<p class="f">')]
        for part in (plan, table):
            self.assertIn('class="slug in"', part)
            self.assertIn("<code>", part)
        # mutant: the plan and the points escaped only, never formatted
        src = page_free_script()
        m = src.replace("'<li>'+fmtD(p)+'</li>'", "'<li>'+esc(p)+'</li>'", 1).replace(
            "P[\"opt-\"+o.k]=pl?[rend(pl,fmtD)]", "P[\"opt-\"+o.k]=pl?[rend(pl,esc)]", 1)
        self.assertEqual(m.count("esc(p)"), 1)
        h = page_with(m, d)["cards"][2]["more"]["b"]
        self.assertNotIn('class="slug in"', h[:h.index('<p class="f">')])

    def test_check_refuses_a_plan_that_is_not_text(self):
        d = example()
        opt(d, 41, "a")["plan"] = ["a list"]
        self.assertIn("card 41: (a) plan must be text", run_page(d)["bad"])
        src = page_free_script()
        m = src.replace('["line","text","plan","effect"', '["line","text","effect"', 1)
        self.assertNotEqual(m, src)
        self.assertEqual(page_with(m, d)["bad"], [])

    def test_every_view_starts_closed_and_the_lede_says_how_it_opens(self):
        res = run_page(example())
        self.assertNotIn('class="btn omore on"', "".join(c["html"] for c in res["cards"]))
        flat = " ".join(PAGE.read_text().split())
        self.assertIn("picking an option opens its view (and closes the card's other one)", flat)
        self.assertIn("its plan in brief, its <b>Pros</b> and <b>Cons</b> side by side, then its own effect", flat)


# a stand-in for the page: the More buttons and views of one card, as cardHtml draws them
PICK_HARNESS = r"""
const els = {};
const mk = (k, open) => { const v = {hidden: !open}; els["d41-" + k + "-more"] = v;
  const attrs = {"aria-expanded": String(open), "aria-controls": "d41-" + k + "-more"}, cls = new Set(open ? ["on"] : []);
  return {dataset: {omore: k, n: "41"}, getAttribute: a => attrs[a], setAttribute: (a, x) => { attrs[a] = x; },
    classList: {toggle: (c, on) => on ? cls.add(c) : cls.delete(c)}, cls, attrs, view: v}; };
const bs = [mk("a", true), mk("b", false), mk("z", false)];
const root = {getElementById: id => els[id] || null,
  querySelectorAll: s => s === '[data-omore][data-n="41"]' ? bs : []};
const state = () => Object.fromEntries(bs.map(b => [b.dataset.omore,
  {shown: !b.view.hidden, expanded: b.attrs["aria-expanded"], on: b.cls.has("on")}]));
const log = {};
pickView(root, "41", "b"); log.pickB = state();
pickView(root, "41", "b"); log.pickBagain = state();
moreView(root, "41", "a"); log.moreA = state();
moreView(root, "41", "a"); log.moreAagain = state();
pickView(root, "41", "z"); log.pickZ = state();
log.pure = {pick: pickOpen({a: true, b: false}, "b"), more: moreOpen({a: true, b: false}, "b"),
  again: pickOpen({a: false, b: true}, "b")};
process.stdout.write(JSON.stringify(log));
"""


def picking(script):
    out = subprocess.run([NODE, "-e", script + PICK_HARNESS], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def open_views(st):
    return sorted(k for k, v in st.items() if v["shown"])


def pick_problems(log):
    out = []
    if open_views(log["pickB"]) != ["b"]:
        out.append("picking (b) leaves %r open, not (b) alone" % open_views(log["pickB"]))
    if open_views(log["pickBagain"]) != ["b"]:
        out.append("picking (b) again leaves %r open, not (b)" % open_views(log["pickBagain"]))
    if log["pure"]["again"] != {"a": False, "b": True}:
        out.append("pickOpen on an open (b) gives %r" % log["pure"]["again"])
    if open_views(log["moreA"]) != ["a", "b"]:
        out.append("More on (a) leaves %r open: it toggles (a) alone" % open_views(log["moreA"]))
    if open_views(log["moreAagain"]) != ["b"]:
        out.append("More on (a) again leaves %r open" % open_views(log["moreAagain"]))
    if open_views(log["pickZ"]) != ["z"]:
        out.append("picking (z) leaves %r open" % open_views(log["pickZ"]))
    for st in log.values():
        if "shown" not in next(iter(st.values()), {}):
            continue
        for k, v in st.items():
            if v["expanded"] != str(v["shown"]).lower() or v["on"] != v["shown"]:
                out.append("(%s)'s More does not say whether its view shows" % k)
    return out


@unittest.skipUnless(NODE, "node is not installed")
class Picking(unittest.TestCase):

    def test_picking_opens_one_and_closes_the_other_more_toggles_one(self):
        log = picking(page_free_script())
        self.assertEqual(pick_problems(log), [])
        self.assertEqual(log["pure"], {"pick": {"a": False, "b": True}, "more": {"a": True, "b": True},
                                       "again": {"a": False, "b": True}})

    def test_mutants_no_close_and_more_closing_others_are_caught(self):
        src = page_free_script()
        for old, new in (("const pickOpen=(open,k)=>{const o={};for(const x in open)o[x]=x===k;return o};",
                          "const pickOpen=(open,k)=>Object.assign({},open,{[k]:true});"),
                         ("function moreView(root,n,k){", "function moreView(root,n,k){return pickView(root,n,k);"),
                         ("o[x]=x===k;return o};", "o[x]=x===k?!open[x]:false;return o};"),
                         ("el.hidden=!on;b.setAttribute(\"aria-expanded\",String(on));",
                          "el.hidden=!on;")):
            with self.subTest(new=new):
                m = src.replace(old, new, 1)
                self.assertNotEqual(m, src)
                self.assertTrue(pick_problems(picking(m)))

    def test_the_change_listener_picks_an_option_never_a_follow_up(self):
        html = PAGE.read_text()
        code = html[html.index('document.addEventListener("change"'):html.index('document.addEventListener("input"')]
        harness = r"""
const handlers = {}, picks = [];
const document = {addEventListener: (t, f) => { handlers[t] = f; }};
const choose = () => {}, $ = () => ({focus: () => {}});
const pickView = (root, n, k) => picks.push([n, k]);
const FOLLOW_KEYS = new Set(["later", "tell me", "expand", "dig into", "you decide", "drop"]);
""" + code + r"""
for (const v of ["b", "later", "z", "drop"]) handlers.change({target: {type: "radio", name: "d41", value: v}});
process.stdout.write(JSON.stringify(picks));
"""

        def run(c):
            out = subprocess.run([NODE, "-e", c], capture_output=True, text=True, timeout=60)
            self.assertEqual(out.returncode, 0, out.stderr)
            return json.loads(out.stdout)

        self.assertEqual(run(harness), [["41", "b"], ["41", "z"]])
        cut = harness.replace("if(!FOLLOW_KEYS.has(t.value))pickView(", "pickView(", 1)
        self.assertNotEqual(cut, harness)
        self.assertNotEqual(run(cut), [["41", "b"], ["41", "z"]])
        gone = harness.replace("if(!FOLLOW_KEYS.has(t.value))pickView(document,t.name.slice(1),t.value);", "", 1)
        self.assertNotEqual(gone, harness)
        self.assertEqual(run(gone), [])


@unittest.skipUnless(NODE, "node is not installed")
class PlanLint(unittest.TestCase):

    def test_the_example_is_clean_and_every_option_has_its_plan(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        for c in example()["cards"]:
            for o in c["options"]:
                self.assertTrue(o.get("plan", "").strip(), (c["n"], o["k"]))
                self.assertNotIn("text", o, (c["n"], o["k"]))

    def test_an_option_with_no_plan(self):
        d = example()
        del opt(d, 41, "a")["plan"]
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "lint: card 41: depth: (a) has no plan: give it a Plan in brief (plan: 2–4 sentences, "
                              "what choosing it sets in motion), the first part of its view; or leave it knowingly on "
                              "an upgraded older card, whose view shows its text instead\n")
        # (z) too
        d = example()
        del opt(d, 43, "z")["plan"]
        self.assertIn("lint: card 43: depth: (z) has no plan", runner(d)[1])

    def test_a_card_with_none_gets_one_line(self):
        d = example()
        for o in d["cards"][2]["options"]:
            o["text"] = o.pop("plan")
        out = runner(d)[1]
        self.assertEqual(out, "lint: card 43: depth: none of the card's 3 options carries its plan in brief: give each, "
                              "(z) too, a plan (2–4 sentences, what choosing it sets in motion), the first part of its "
                              "view; or leave it knowingly on an upgraded older card, whose view shows its text instead\n")

    def test_it_reads_what_the_page_shows(self):
        d = example()
        opt(d, 42, "a")["plan"] = "None."
        self.assertIn("lint: card 42: depth: (a) has no plan", runner(d)[1])
        js = RUNNER.read_text()
        raw = js.replace("miss = os.filter(o => !page.planOf(o))", "miss = os.filter(o => !o.plan)", 1)
        self.assertNotEqual(raw, js)
        self.assertNotIn("(a) has no plan", runner_with(raw, d)[1])

    def test_a_plan_past_the_cap(self):
        d = example()
        opt(d, 43, "a")["plan"] = " ".join(["word"] * 100) + "."
        self.assertEqual(runner(d)[:2], (0, ""))
        opt(d, 43, "a")["plan"] = " ".join(["word"] * 101) + "."
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "lint: card 43: depth: (a)'s plan is 101 words: keep its Plan in brief to 2–4 sentences, "
                              "about 100 words at most; its fuller renditions go in its levels (detail)\n")
        js = RUNNER.read_text()
        off = js.replace("if (n > PLAN_CAP)", "if (false)", 1)
        self.assertNotEqual(off, js)
        self.assertEqual(runner_with(off, d)[:2], (0, ""))

    def test_mutant_lint_removed_is_caught(self):
        js = RUNNER.read_text()
        removed = js.replace("  plan(c, say);\n", "", 1)
        self.assertNotEqual(removed, js)
        d = example()
        del opt(d, 41, "a")["plan"]
        self.assertEqual(runner_with(removed, d)[:2], (0, ""))

    def test_ids_in_the_view_are_linted(self):
        for field, value in (("plan", "The brand check closes as KAPPA-3570 on Thursday."),
                             ("pros", ["The brand check closes as KAPPA-3570"]),
                             ("cons", ["KAPPA-3570 stays open"])):
            with self.subTest(field=field):
                d = example()
                opt(d, 43, "a")[field] = value
                self.assertIn("lint: card 43: KAPPA-3570 looks like an id ((a))", runner(d)[1])
                js = RUNNER.read_text()
                m = js.replace('"cost", "pro", "con", "pros", "cons"]) put(', '"cost", "pro", "con"]) put(', 1).replace(
                    '"text", "plan", "effect"', '"text", "effect"', 1)
                self.assertNotEqual(m, js)
                self.assertNotIn("KAPPA-3570", runner_with(m, d)[1])

    def test_the_cold_read_covers_the_view(self):
        for field, value in (("plan", "The 17 widgets are rebuilt for Frobnicator users."),
                             ("cons", ["The 17 widgets break"])):
            with self.subTest(field=field):
                d = example()
                opt(d, 43, "a")[field] = value
                self.assertIn('lint: card 43: "17" (an option\'s view) counts things its context does not name',
                              runner(d)[1])
                js = RUNNER.read_text()
                off = js.replace('  terms(opts(c).flatMap(viewTexts), " (an option\'s view)", namedView);\n', "", 1)
                self.assertNotEqual(off, js)
                self.assertNotIn("17", runner_with(off, d)[1])

    def test_the_tables_points_count_in_the_card_in_all(self):
        d = example()
        opt(d, 43, "a")["pros"] = [" ".join(["word"] * 300)] * 5
        out = runner(d)[1]
        self.assertIn("lint: card 43: depth: the card is", out)
        js = RUNNER.read_text()
        m = js.replace(" + words(page.prosCons(o).map(r => r[1])), 0);", ", 0);", 1)
        self.assertNotEqual(m, js)
        self.assertNotIn("depth: the card is", runner_with(m, d)[1])


# ---- fix round 1: the click path, re-picking, the cold read over the view, the plan's line and the phone layout

# the page's click listener and More's toggleOption, as the template holds them, beside stand-ins that record what
# reaches the views
CLICK_HARNESS = r"""
const handlers = {}, calls = [];
const document = {addEventListener: (t, f) => { handlers[t] = f; }, querySelectorAll: () => []};
const moreView = (root, n, k) => calls.push(["more", root === document, n, k]);
const pickView = (root, n, k) => calls.push(["pick", root === document, n, k]);
const stepSection = () => calls.push(["step"]), setAll = () => {}, goCard = () => {}, choose = () => {};
const hideTip = () => {}, showTip = () => {}, pinTip = () => {}, getSelection = () => "", $ = () => null;
let tipClosedAt = -Infinity, tipPinned = false, tipFor = null, readonly = false, answers = {}, byN = new Map();
const syncCard = () => {}, syncAll = () => {}, write = () => {};
const FOLLOW_KEYS = new Set(["later", "tell me", "expand", "dig into", "you decide", "drop"]);
%s
const el = (sels, props) => Object.assign({closest(s) { return sels.includes(s) ? this : null; }, dataset: {}}, props || {});
const click = t => { const n = calls.length; handlers.click({target: t, timeStamp: 1e6, preventDefault() {}, stopPropagation() {}});
  return calls.slice(n); };
const log = {
  more: click(el(["[data-omore]", "button"], {dataset: {omore: "b", n: "41"}})),
  repick: click(el(["input"], {type: "radio", name: "d41", value: "b", checked: true})),
  unchecked: click(el(["input"], {type: "radio", name: "d41", value: "b", checked: false})),
  followUp: click(el(["input"], {type: "radio", name: "d41", value: "later", checked: true})),
};
process.stdout.write(JSON.stringify(log));
"""


def click_log(html):
    code = html[html.index("function toggleOption("):html.index("function placeholderFor(")]
    code += html[html.index('document.addEventListener("click"'):html.index('addEventListener("resize"')]
    out = subprocess.run([NODE, "-e", CLICK_HARNESS % code], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def click_problems(log):
    out = []
    if log["more"] != [["more", True, "41", "b"]]:
        out.append("a click on More reaches %r, not moreView(document, 41, b) alone" % log["more"])
    if log["repick"] != [["pick", True, "41", "b"]]:
        out.append("a click on the picked option reaches %r, not pickView(document, 41, b)" % log["repick"])
    if log["unchecked"]:
        out.append("a click that picks nothing reaches %r" % log["unchecked"])
    if log["followUp"]:
        out.append("a click on a follow-up reaches %r" % log["followUp"])
    return out


@unittest.skipUnless(NODE, "node is not installed")
class FixRound(unittest.TestCase):

    def test_more_and_a_re_pick_reach_the_views_through_the_click_listener(self):
        self.assertEqual(click_problems(click_log(PAGE.read_text())), [])

    def test_mutants_on_the_click_path_are_caught(self):
        html = PAGE.read_text()
        for old, new in (("function toggleOption(b){moreView(document,b.dataset.n,b.dataset.omore)}",
                          "function toggleOption(b){pickView(document,b.dataset.n,b.dataset.omore)}"),
                         ("else if(om)toggleOption(om);", "else if(om);"),
                         ("if(pk&&pk.type===\"radio\"&&pk.checked&&", "if(false&&pk&&pk.type===\"radio\"&&pk.checked&&"),
                         ("&&!FOLLOW_KEYS.has(pk.value))pickView(", ")pickView(")):
            with self.subTest(new=new):
                m = html.replace(old, new, 1)
                self.assertNotEqual(m, html)
                self.assertTrue(click_problems(click_log(m)))

    def test_a_saved_pick_stays_closed_and_the_docs_say_so(self):
        # the page opens views only on a click or a change; a reload renders every view closed
        self.assertNotIn("pickView", PAGE.read_text()[PAGE.read_text().index("function syncCard("):
                                                      PAGE.read_text().index("function syncAll(")])
        schema = " ".join((PAGE.parent.parent / "references" / "cards-schema.md").read_text().split())
        self.assertIn("A click on an option already picked opens its view too", schema)
        self.assertIn("A pick saved earlier and shown again on a reload leaves its view closed", schema)
        rulings = " ".join((RENDERING.parent / "rulings.md").read_text().split())
        self.assertIn("a click on an option already picked opening its view too, a pick saved earlier staying closed on a reload", rulings)

    def test_the_cold_read_over_the_view_skips_verb_phrases(self):
        d = example()
        opt(d, 43, "b")["plan"] = ("We need to plan and review the change; it reaches review without plan, "
                                   "from the template, then plan for review.")
        self.assertEqual(runner(d)[:2], (0, ""))
        # a real named thing, unglossed, still fires
        opt(d, 43, "b")["cons"] = ["The content mode of the guides changes"]
        out = runner(d)[1]
        self.assertEqual(out, 'lint: card 43: "content mode" (an option\'s view) is not glossed in its context: give it a '
                              "one-line gloss in context, what it is and where it comes from\n")
        # mutant: the view read as the flat part is
        js = RUNNER.read_text()
        m = js.replace('" (an option\'s view)", namedView);', '" (an option\'s view)");', 1)
        self.assertNotEqual(m, js)
        d = example()
        opt(d, 43, "b")["plan"] = "We need to plan and review the change; it reaches review without plan, from the template."
        self.assertIn("is not glossed", runner_with(m, d)[1])

    def test_qualified_names_with_ed_or_ing_still_fire(self):
        for field, value in (("plan", "The staging phase and a managed setting change."),
                             ("cons", ["The staging phase and a managed setting change"])):
            with self.subTest(field=field):
                d = example()
                opt(d, 43, "b")[field] = value
                out = runner(d)[1]
                for t in ("staging phase", "managed setting"):
                    self.assertIn('"%s" (an option\'s view) is not glossed' % t, out)
                js = RUNNER.read_text()
                m = js.replace("const VERB_FORM = /(?:es)$/;", "const VERB_FORM = /(?:es|ed|ing)$/;", 1)
                self.assertNotEqual(m, js)
                self.assertNotIn("is not glossed", runner_with(m, d)[1])

    def test_a_possessive_is_no_qualifier(self):
        for apos in ("'", "’"):
            d = example()
            opt(d, 43, "b")["plan"] = "The maintainer" + apos + "s plan stays."
            self.assertEqual(runner(d)[:2], (0, ""), apos)
        js = RUNNER.read_text()
        m = js.replace("return possessive || DET.has(w)", "return DET.has(w)", 1)
        self.assertNotEqual(m, js)
        self.assertIn('"s plan" (an option\'s view) is not glossed', runner_with(m, d)[1])

    def test_an_option_with_both_plan_and_text(self):
        d = example()
        opt(d, 41, "a")["text"] = "Keep building on a laptop."
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertEqual(out, "lint: card 41: depth: (a) has both plan and text; text is not shown: its view opens on the "
                              "plan, so put what text says in the plan or its levels (detail), and drop text\n")
        js = RUNNER.read_text()
        m = js.replace('if (page.planOf(o) && typeof o.text === "string" && o.text.trim())', "if (false)", 1)
        self.assertNotEqual(m, js)
        self.assertEqual(runner_with(m, d)[:2], (0, ""))

    def test_check_refuses_a_line_break_in_a_plan(self):
        from test_pros_cons import BREAKS
        for br in BREAKS:
            d = example()
            opt(d, 41, "b")["plan"] = "One sentence." + br + "Another."
            self.assertIn("card 41: (b) plan must be one line: its Plan in brief, 2-4 sentences, with no line break",
                          run_page(d)["bad"], repr(br))
        src = page_free_script()
        m = src.replace("if(isStr(o.plan)&&LINE_BREAK.test(o.plan))", "if(false)", 1)
        self.assertNotEqual(m, src)
        self.assertEqual(page_with(m, d)["bad"], [])

    def test_the_columns_stack_at_phone_width(self):
        html = PAGE.read_text()

        def stacked(h):
            phone = re.findall(r"@media \(max-width:640px\)\{(.*?)\n\}", h, re.S)
            return any(re.search(r"\n  \.opc\{grid-template-columns:minmax\(0,1fr\)\}", p)
                       and ".opc>.opcp,.opc>.opcc{grid-column:1}" in p for p in phone)

        self.assertTrue(stacked(html))
        m = html.replace("  .opc>.opcp,.opc>.opcc{grid-column:1}\n", "", 1)
        self.assertNotEqual(m, html)
        self.assertFalse(stacked(m))
        # Pros then Cons: the source order the stacked grid keeps
        z = card(run_page(example()), 41)["more"]["b"]
        self.assertLess(z.index('class="opcp"'), z.index('class="opcc"'))


# ---- chat: tell me (x) and the block

PLAN_LINE = re.compile(r"^\*plan in brief:\* \S")
PROS_CONS_HEAD = "| Pros | Cons |"


def chat_view_problems(lines, facet=True):
    """One option's view in chat: the *plan in brief:* line, then its `| Pros | Cons |` table (when it has
    points), then (in a tell me (x) answer) its facet line, in that order."""
    out = []
    plan = [i for i, x in enumerate(lines) if PLAN_LINE.match(x)]
    table = [i for i, x in enumerate(lines) if x == PROS_CONS_HEAD]
    fac = [i for i, x in enumerate(lines) if x.startswith("*→ ")]
    if len(plan) != 1:
        return ["%d *plan in brief:* lines" % len(plan)]
    if len(table) > 1:
        out.append("two tables")
    if table and lines[table[0] + 1] != "|---|---|":
        out.append("the table has no rule under its head")
    rows = []
    for x in lines[table[0] + 2:] if table else []:
        if not x.startswith("|"):
            break
        rows.append(x)
        if x.count("|") != 3:
            out.append("a row is not two cells: %r" % x)
    if table and not 1 <= len(rows) <= 5:
        out.append("%d rows: one to five" % len(rows))
    if facet:
        if len(fac) != 1 or not FACET_LINE.match("  " + lines[fac[0]]):
            return out + ["no facet line"]
    order = [("plan", plan[0])] + ([("table", table[0])] if table else []) + ([("facets", fac[0])] if facet else [])
    if [p for _, p in order] != sorted(p for _, p in order):
        out.append("the order is %r, not plan, table, facets" % [n for n, _ in sorted(order, key=lambda x: x[1])])
    return out


def tell_me_answers(text):
    """Each `tell me (x)` answer in a text: its lines, from its `**N (x) — title**` head to the next
    blank-line-separated part that is not its own (a rule, a heading, an italic note)."""
    lines = text.splitlines()
    out = []
    for i, x in enumerate(lines):
        if re.match(r"^\*\*(N|\d+) \(([a-z])\) — [^*]+\*\*$", x):
            j = i + 1
            while j < len(lines) and not (lines[j] in ("---", "```") or lines[j].startswith(("#", "*Gallery note"))):
                j += 1
            out.append((i + 1, lines[i:j]))
    return out


def block_view_problems(body):
    """A block's options' views: under its Impact table, one per row of that table, in its letter order,
    each its bold title, its *plan in brief:* line, then its Pros | Cons table; all before any To act on,
    If left and Background part. Returns (problems, views seen)."""
    out = []
    rows = impact_rows(body)
    letters = [re.match(r"^\| (?:\*\*)?\(([a-z])\)", r).group(1) for r in rows]
    end = max(i for i, x in enumerate(body) if x in rows)
    heads = [(i, re.match(r"^\*\*\(([a-z])\) [^*]+\*\*$", x).group(1)) for i, x in enumerate(body)
             if re.match(r"^\*\*\(([a-z])\) [^*]+\*\*$", x)]
    if [k for _, k in heads] != letters:
        out.append("views %r for the table's rows %r" % ([k for _, k in heads], letters))
    stops = [i for i, x in enumerate(body) if x.startswith(("▾ Background", "**To act on (", "**If left:**"))]
    for n, (i, k) in enumerate(heads):
        if i < end:
            out.append("(%s)'s view sits above the Impact table" % k)
        j = heads[n + 1][0] if n + 1 < len(heads) else min([s for s in stops if s > i] or [len(body)])
        if any(i < s < j for s in stops):
            out.append("(%s)'s view runs past a later part" % k)
        if not PLAN_LINE.match(body[i + 1] if i + 1 < len(body) else ""):
            out.append("(%s): no *plan in brief:* line under its title" % k)
        out += ["(%s): %s" % (k, p) for p in chat_view_problems(body[i:j], facet=False)]
    return out, len(heads)


class ChatView(unittest.TestCase):

    def test_the_rendering_template(self):
        text = RENDERING.read_text()
        t = fenced(text, "**N (x) — Option title**")
        self.assertEqual(chat_view_problems(t), [])
        self.assertIn("## An option's view", text)
        flat = " ".join(text.split())
        self.assertIn("**The order is fixed**: the *plan in brief:* line first, then the table, then the option's facet line", flat)

    def test_the_block_template_shows_each_options_view_under_its_table(self):
        block = fenced(RENDERING.read_text(), "**N — Title as a question?** ⚠ one-way")
        probs, n = block_view_problems(block)
        # the template shows (a) and (b) in full and says each option after does the same
        self.assertEqual([p for p in probs if not p.startswith("views ")], [])
        self.assertGreaterEqual(n, 2)

    def test_every_tell_me_answer_in_the_gallery(self):
        found = tell_me_answers(GALLERY.read_text())
        self.assertGreaterEqual(len(found), 1)
        for at, lines in found:
            self.assertEqual(chat_view_problems(lines), [], "gallery.md:%d" % at)

    def test_mutant_facets_before_the_table_is_caught(self):
        text = GALLERY.read_text()
        at, lines = tell_me_answers(text)[0]
        fac = next(x for x in lines if x.startswith("*→ "))
        moved = [x for x in lines if x != fac]
        moved.insert(moved.index(PROS_CONS_HEAD) - 1, fac)
        self.assertIn("the order is", " ".join(chat_view_problems(moved)))
        # and the plan after the table
        p = next(x for x in lines if PLAN_LINE.match(x))
        late = [x for x in lines if x != p]
        late.insert(late.index(fac), p)
        self.assertTrue(chat_view_problems(late))
        # a table with no rule, or over five rows
        self.assertTrue(chat_view_problems([x for x in lines if x != "|---|---|"]))
        i = lines.index(PROS_CONS_HEAD) + 2
        self.assertTrue(chat_view_problems(lines[:i] + [lines[i]] * 6 + lines[i + 2:]))

    def test_every_gallery_block_shows_each_options_view(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind != "block":
                continue
            probs, k = block_view_problems(body)
            self.assertEqual(probs, [], "gallery.md:%d" % n)
            self.assertGreaterEqual(k, 3, "gallery.md:%d" % n)
            seen += 1
        self.assertGreaterEqual(seen, 2)

    def test_mutants_a_block_view_dropped_or_moved_are_caught(self):
        n, _, body = next(v for v in views(GALLERY) if v[1] == "block")
        i = body.index("**(b) Keep it, with a deprecation header and a sunset date**")
        j = body.index("**(c) Investigate first**")
        dropped = body[:i] + body[j:]
        self.assertTrue(block_view_problems(dropped)[0])
        t = next(k for k, x in enumerate(body) if x.startswith("| Impact |"))
        above = body[:t] + body[i:j] + body[t:i] + body[j:]
        self.assertTrue(block_view_problems(above)[0])
        no_plan = [x for x in body if not x.startswith("*plan in brief:* every `/v1/export`")]
        self.assertTrue(block_view_problems(no_plan)[0])
        bg = next(k for k, x in enumerate(body) if x.startswith("▾ Background"))
        late = body[:i] + body[j:bg] + body[i:j] + body[bg:]
        self.assertTrue(block_view_problems(late)[0])

    def test_the_rule_is_written(self):
        self.assertIn("`tell me (x)` answers with that option's view", SKILL_MD.read_text())
        self.assertIn("then each option's *plan in brief:* and its `Pros | Cons` table", SKILL_MD.read_text())
        self.assertIn("`tell me (x)`, an option's letter, asks for that option's view", REPLIES.read_text())


if __name__ == "__main__":
    unittest.main()
