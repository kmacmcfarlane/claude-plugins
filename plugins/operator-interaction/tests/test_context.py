"""Every page card carries a Context that introduces what the rest of it names.

Three parts:

- the decision page (`decision-page` skill): its required `context` field, the refusal of a
  TLDR bullet that carries the recommendation, `contextBlock` (which renders Context, and an
  older card's `what` after it) and the render order (TLDR, then Context, then Impact), loaded
  from `assets/index.html` and run under node against `assets/cards.example.json` and broken
  copies of it; a decision reference and its tooltip, and the reference rule (an open decision
  a card names goes on the page as a card; every `[[N]]` is a card or a ref);
- the pre-publish runner, `scripts/check_cards.js`: its exits and one-line errors, its lint
  for ids anywhere the page shows text, and its lints for counts and named things a card's
  context does not introduce;
- the `rev` rule, in identical words in the four places it is written.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import html as html_lib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, PAGE, END_MARK, example, page_free_script

SKILL = PAGE.parent.parent
RUNNER = SKILL / "scripts" / "check_cards.js"
SCHEMA = SKILL / "references" / "cards-schema.md"
SKILL_MD = SKILL / "SKILL.md"

REV_RULE = (
    "Any change to a card gets a new `rev`, Context included: an **Added:** line after "
    "`tell me`, more detail after `expand`, a `dig into` finding, a corrected fact, a re-ask. "
    "Only a format-only upgrade keeps it: an older card moved to `decision-card/5` by the "
    "`decision-page` skill's `scripts/upgrade_cards.js`, its fields moved and none added. A fact "
    "drawn from anywhere outside the card is new information: a new `rev`.")
RECORD = SKILL.parent / "decisions" / "references" / "card-record.md"


def setUpModule():
    # the page and runner tests need node; without it they skip, and say so where the
    # Check's output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's context tests "
              "(DecisionPageContext, DecisionPageRunner) are skipped, so the page's context "
              "and TLDR checks, contextBlock and the pre-publish runner went untested",
              file=sys.stderr)


# a list of data files in, each one's check() result and its cards' Context blocks, rendered
# Why now and rendered card out
HARNESS = r"""
const ds = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = ds.map(d => {
  const bad = check(d);
  let blocks = [];
  if (!bad.length) {
    CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
    byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
    answers = d._answers || {};
    blocks = CARDS.map(c => ({n: c.n, open: contextBlock(c), tip: tipHtml(String(c.n)),
                              why: fmtD(c.why), what: fmt(c.what || ""), card: cardHtml(c)}));
    blocks.refTips = Object.fromEntries(Object.keys(REFS).map(k => [k, tipHtml(k)]));
    blocks.slugs = {on: slug("41"), ref: slug("38")};
  }
  return {bad, blocks, refTips: blocks.refTips || {}, slugs: blocks.slugs || {}};
});
process.stdout.write(JSON.stringify(out));
"""


def run_pages(datasets, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + HARNESS],
                         input=json.dumps(datasets), capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def run_page(data, script=None):
    return run_pages([data], script)[0]


def with_tldr(bullet):
    d = example()
    d["cards"][0]["tldr"] = ["The docs build runs on a laptop today", bullet]
    return d


# Refused by the page: forms that cannot be anything but the recommendation
REFUSED = [
    "Rec: move it to CI", "**Rec:** x", "1. Rec: b", "- Rec — b", "Rec. (b)", "Rec",
    "rec (b)", "Use rec (b)",
    "Recommended: (b)", "Recommendation — publish from CI",
    "I'd recommend CI", "I’d recommend CI", "We would recommend b", "We’d recommend b",
    "I recommend b", "Recommend (b)", "→ Recommended (b)", "Rec - b",
    "My recommendation: b", "Our recommendation is b",
    "(b) is recommended", "→ (b), recommended", "Start the three now (recommended)",
]
# Known refusals of third-party wording (R2): excluding them needs a lookbehind, which would
# stop the whole page script in an older browser. The fix is to reword the bullet.
KNOWN_REFUSALS = ["Recommendation: the audit's, not mine", "the audit's rec (b)"]
# Passed by the page
PASSED = [
    "Recap: two options", "Records stay", "Reconsider later", "Recent failures",
    "Recompute nightly", "Precedent: kept",
    "The review recommended four changes", "Recommended by the review: four changes",
    "Recommendations from the audit apply",
    "Start the three now", "Move it to CI, or keep it local", "Best: (b)",
    "(b) recommended by the audit", "Option (a) is recommended by the vendor",
    "Recommended (b) by the audit", "Recommended-by-default flags change",
    "Recommendations: four, from the review", "Recommended reading: the audit",
    "Rec room", "Rec’d: b",
]
# Accepted misses (R2): the page passes them; the runner's broad TLDR lint reports them
LINTED_MISSES = ["Rec -b", "Rec-(b)", "Rec’d: b", "Recommend moving to CI",
                 "Recommending CI", "Suggest moving to CI", "We suggest b"]
# Well-known terms the id lint reports and the page never refuses
WELL_KNOWN = ["UTF-8", "SHA-256", "ISO-8601", "GPT-4", "S3", "EC2", "K8s"]


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageContext(unittest.TestCase):

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    def test_the_example_opens_every_card_on_its_context_and_passes(self):
        d = example()
        for c in d["cards"]:
            self.assertTrue(c["context"].strip(), c["n"])
            self.assertNotIn("what", c, c["n"])
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_missing_blank_or_non_text_context_is_refused(self):
        cases = []
        for v in (None, "", "  ", 3, ["x"]):
            d = example()
            if v is None:
                del d["cards"][0]["context"]
            else:
                d["cards"][0]["context"] = v
            cases.append(d)
        for res in run_pages(cases):
            self.assertTrue(any(b.startswith("card 41: context missing") for b in res["bad"]),
                            res["bad"])

    def test_what_is_optional(self):
        d = example()
        for c in d["cards"]:
            c.pop("what", None)
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_cue_only_context_with_a_what_passes(self):
        d = example()
        d["cards"][0]["context"] = "You last saw the build fail twice ([[38]]) · now you pick."
        d["cards"][0]["what"] = "Where the docs site is built from."
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_tldr_bullet_carrying_the_recommendation_is_refused(self):
        bullets = REFUSED + KNOWN_REFUSALS
        for b, res in zip(bullets, run_pages([with_tldr(b) for b in bullets])):
            self.assertIn("card 41: tldr bullet 2 carries the recommendation: the options mark "
                          "it; say what is decided instead", res["bad"], b)

    def test_tldr_wording_that_is_not_the_recommendation_passes(self):
        bullets = PASSED + LINTED_MISSES
        for b, res in zip(bullets, run_pages([with_tldr(b) for b in bullets])):
            self.assertEqual(res["bad"], [], b)

    def test_well_known_terms_never_refuse_the_page(self):
        d = example()
        d["cards"][0]["tldr"] = ["Text is " + " and ".join(WELL_KNOWN)]
        self.assertEqual(run_page(d)["bad"], [])

    def test_two_offending_bullets_give_one_message_naming_the_first(self):
        d = example()
        d["cards"][0]["tldr"] = ["Rec: b", "I recommend b"]
        bad = [b for b in run_page(d)["bad"] if "tldr" in b]
        self.assertEqual(bad, ["card 41: tldr bullet 1 carries the recommendation: the options "
                               "mark it; say what is decided instead"])

    def test_a_tldr_that_is_not_a_list_of_text_gets_the_shape_message_only(self):
        cases = []
        for v in ("x", 3, {}, [1]):
            d = example()
            d["cards"][0]["tldr"] = v
            cases.append(d)
        for res in run_pages(cases):
            tl = [b for b in res["bad"] if "tldr" in b]
            self.assertEqual(tl, ["card 41: tldr must be a list of text"])

    def test_context_block_renders_context_then_an_older_what(self):
        d = example()
        d["cards"][0]["context"] = "the cue ([[38]])"
        d["cards"][0]["what"] = "the old what"
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        b41 = res["blocks"][0]["open"]
        self.assertEqual(b41.count("<p>"), 2)
        self.assertLess(b41.index("the cue"), b41.index("the old what"))
        # without what, one paragraph
        self.assertEqual(res["blocks"][1]["open"].count("<p>"), 1)
        self.assertIn('<span class="lbl">Context</span>', res["blocks"][1]["open"])

    def test_context_block_escapes_and_marks_up(self):
        d = example()
        d["cards"][0]["context"] = '<img src=x onerror="alert(1)" > the `main` branch ([[38]])'
        d["cards"][0]["what"] = "<script >x</script >"
        blk = run_page(d)["blocks"][0]
        h = blk["open"]
        self.assertNotIn("<img", h)
        self.assertNotIn("<script", h)
        self.assertIn("&lt;img", h)
        self.assertIn("<code>main</code>", h)
        self.assertIn('class="slug"', h)
        self.assertIn('data-ref="38"', h)
        # a reference is never a popup trigger; one not on the page shows its tooltip only
        self.assertNotIn("aria-haspopup", h)
        self.assertNotIn('data-goto="38"', h)

    def test_the_open_card_opens_on_the_tldr_then_context_then_impact(self):
        d = example()
        d["cards"][1]["what"] = "Where the old links lead after the move."
        for blk in run_page(d)["blocks"]:
            card = blk["card"]
            self.assertLess(card.index('class="tldr"'), card.index('class="ctx"'), blk["n"])
            self.assertLess(card.index('class="ctx"'), card.index('class="impline"'), blk["n"])
            # Context's summary rendition, once; its levels repeat the labelled wrapper only
            self.assertEqual(card.count(blk["open"]), 1, blk["n"])
            # under decision 197 (a) the Background fold holds Why now and Why ask only
            bg = card[card.index('<summary>Background <span class="fsum">why now: '):]
            bg = bg[:bg.index("</details>")]
            self.assertIn(blk["why"], bg, blk["n"])
            if blk["n"] == 42:
                self.assertNotIn(blk["what"], bg)
                self.assertIn(blk["what"], blk["open"])
        # the on-page popup is gone (answer 335's feedback): a reference's tooltip shows no
        # Context block and no Impact, only its peek (ReferenceTooltip)
        html = PAGE.read_text()
        self.assertNotIn("function fillPop", html)
        tip = html[html.index("function tipHtml("):html.index("/* ---- end of the page-free part")]
        self.assertNotIn("contextBlock(", tip)
        self.assertNotIn("rowEffect(", tip)
        self.assertNotIn("impactLine(", tip)

    def test_the_page_free_part_holds_no_lookbehind(self):
        # a lookbehind is a syntax error in an older browser, and stops the whole script
        self.assertNotIn("(?<", page_free_script())


TIP_ONE_LINE = "+(shown(one)?'<span class=\"tip-l\"> — '+fmtPlain(one)+'</span>':'')"


def tip_text(h):
    return html_lib.unescape(re.sub(r"<[^>]+>", "", h))


def tip_problems(tip, card, answer="none yet"):
    """What a card's tooltip lacks: its Context, each option as (x) title — one line in letter
    order, the recommended one bold and marked, and the answer."""
    out = []
    text = tip_text(tip)
    if "Context" not in text or tip_text(card["context"].split("[[")[0])[:40] not in text:
        out.append("no Context")
    at = -1
    for o in card["options"]:
        # its one line, else its effect
        want = "(%s) %s — %s" % (o["k"], o["title"], (o.get("line") or o["effect"]).split("[[")[0])
        i = text.find(want)
        if i < 0 or i < at:
            out.append("option (%s) is not shown as (x) title — one line, in order" % o["k"])
        at = max(at, i)
    if card["rec"] and not re.search(r'<li class="isrec"><span class="ol">\(%s\)</span>[^<]*'
                                     r'(<span class="tip-l">.*?</span>)?<span class="pill rec">recommended'
                                     % card["rec"], tip):
        out.append("the recommended option is not marked")
    if "your answer: " + answer not in text:
        out.append("the answer is not shown")
    return out


def TIP_FNS():
    """The page's showTip and hideTip, as written."""
    html = PAGE.read_text()
    return html[html.index("function showTip("):html.index("const hoverable=")]


DESCRIBE_HARNESS = r"""
const mk = ref => ({dataset: {ref}, attrs: {}, setAttribute(k, v) { this.attrs[k] = [v, tip.innerHTML]; },
  removeAttribute(k) { delete this.attrs[k]; }});
const tip = {hidden: true, innerHTML: "", style: {}, classList: {add() {}, remove() {}}};
const place = () => {}, tipHtml = k => "tip " + k;
let tipFor = null, tipPinned = false;
const a = mk("41"), b = mk("38"), log = [];
showTip(a); log.push({a: a.attrs["aria-describedby"] || null});
showTip(b); log.push({a: a.attrs["aria-describedby"] || null, b: b.attrs["aria-describedby"] || null});
hideTip(); log.push({b: b.attrs["aria-describedby"] || null, hidden: tip.hidden});
process.stdout.write(JSON.stringify(log));
"""


def describe_problems(fns):
    out = subprocess.run([NODE, "-e", fns + DESCRIBE_HARNESS], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        return ["node failed: " + out.stderr[:200]]
    a1, a2, a3 = json.loads(out.stdout)
    probs = []
    # each set while the tooltip already holds its reference's text
    if a1["a"] != ["tip", "tip 41"] or a2["b"] != ["tip", "tip 38"]:
        probs.append("aria-describedby is not set once the tooltip is shown and filled")
    if a2["a"] is not None or a3["b"] is not None or not a3["hidden"]:
        probs.append("aria-describedby stays on a reference whose tooltip is gone")
    return probs


# the page-bound tooltip and click code, run under node on stand-ins for the page: the slice from the tooltip
# to the end of the click listener, with every listener it adds caught
SHELL_HARNESS = r"""
const handlers = {};
const document = {addEventListener: (t, f) => { handlers[t] = f; }, activeElement: null,
  documentElement: {clientWidth: 800, style: {}}, querySelectorAll: () => [], getElementById: () => null};
const classes = new Set();
const tipEl = {hidden: true, innerHTML: "", style: {}, offsetWidth: 100, offsetHeight: 50,
  classList: {add: c => classes.add(c), remove: (...cs) => cs.forEach(c => classes.delete(c)), contains: c => classes.has(c)}};
const $ = s => s === "#tip" ? tipEl : null;
const matchMedia = () => ({matches: true}), innerHeight = 800, scrollX = 0, scrollY = 0;
const getSelection = () => "";
const calls = [];
const choose = (...a) => calls.push("choose"), write = (...a) => calls.push("write");
const stepSection = () => {}, toggleOption = () => {}, setAll = () => {}, tipHtml = k => "tip " + k;
let byN = new Map([["41", {rec: "b"}]]), readonly = false, answers = {}, timers = {};
const el = (sels, dataset) => ({dataset: dataset || {}, attrs: {},
  closest(s) { return sels.includes(s) ? this : null; }, setAttribute(k, v) { this.attrs[k] = v; },
  removeAttribute(k) { delete this.attrs[k]; }, getBoundingClientRect: () => ({left: 0, top: 0, bottom: 10})});
/* each event a second after the last, unless dt says otherwise (a double tap) */
let now = 0;
const ev = (target, dt) => { now += dt == null ? 1000 : dt;
  const e = {target, pd: false, sp: false, timeStamp: now}; e.preventDefault = () => { e.pd = true; };
  e.stopPropagation = () => { e.sp = true; }; return e; };
""" + "%s" + r"""
const ref = el([".slug", "[data-ref]", "button"], {ref: "38"}), ref2 = el([".slug", "[data-ref]", "button"], {ref: "39"});
const plain = el([]), tipBody = el(["#tip"]), quick = el(["[data-quick]", "button"], {quick: "rec", n: "41"});
const log = {};
handlers.click(ev(ref)); log.pinned = tipPinned; log.pinnedClass = classes.has("pinned");
handlers.mouseover(ev(plain)); log.afterLeave = {shown: !tipEl.hidden, pinned: tipPinned};
showTip(ref2); log.afterMove = {pinned: tipPinned, pinnedClass: classes.has("pinned")};
handlers.click(ev(ref)); hideTip();
log.afterHide = {pinned: tipPinned, shown: !tipEl.hidden, classes: [...classes]};
/* a tap where the tooltip covers a control: the tooltip takes it when the page's CSS gives the tooltip, with
   the classes it has now, pointer-events auto; a radio under the tap gets its change event */
const radio = el(["input"]); radio.radio = {type: "radio", name: "d41", value: "b"};
const takes = () => !tipEl.hidden && (TIP_BASE || TIP_CLASSES.some(c => classes.has(c)));
const tapOver = (under, dt) => { const t = takes() ? tipBody : under, e = ev(t, dt), n = calls.length;
  handlers.click(e); if (t === under && under.radio && !e.pd) handlers.change({target: under.radio});
  return {calls: calls.slice(n), pd: e.pd, sp: e.sp, shown: !tipEl.hidden}; };
handlers.click(ev(ref));
log.tap = tapOver(quick);
/* a tooltip shown by focus, unpinned: over a quick answer, then over a radio */
document.activeElement = ref; handlers.focusin(ev(ref)); log.focusQuick = tapOver(quick);
handlers.focusin(ev(ref)); log.focusRadio = tapOver(radio);
/* pin, close with a second tap (focus stays), the pointer off and back, then a tap on the tooltip */
handlers.click(ev(ref)); handlers.click(ev(ref)); handlers.mouseover(ev(plain)); handlers.mouseover(ev(ref));
log.hoverBack = tapOver(quick);
/* the pointer moving from a reference into its tooltip keeps it open */
document.activeElement = null; handlers.mouseover(ev(ref2)); handlers.mouseover(ev(tipBody));
log.insideTip = {shown: !tipEl.hidden};
/* a double tap on a tooltip shown by focus: the first closes it, the second lands where it was */
document.activeElement = ref; handlers.focusin(ev(ref));
log.dblRadio = [tapOver(radio), tapOver(radio, 100)];
handlers.focusin(ev(ref));
log.dblQuick = [tapOver(quick), tapOver(quick, 100)];
/* focus moving to a control that is not a reference hides a shown tooltip */
document.activeElement = null; handlers.mouseover(ev(ref2)); handlers.focusin(ev(plain));
log.focusOther = {shown: !tipEl.hidden};
/* the pointer leaving keeps a tooltip shown by focus open while its reference has focus */
document.activeElement = ref; handlers.focusin(ev(ref)); handlers.mouseover(ev(plain));
log.focusLeave = {shown: !tipEl.hidden};
process.stdout.write(JSON.stringify(log));
"""


def shell_log(html):
    from test_sticky import rules, decls
    r = rules(html)
    auto = lambda sel: decls(r.get(sel, "")).get("pointer-events") == "auto"
    classes = [sel[len(".tip."):] for sel in r if re.fullmatch(r"\.tip\.[a-z-]+", sel) and auto(sel)]
    code = html[html.index('const tip=$("#tip")'):html.index('addEventListener("resize"')]
    script = (SHELL_HARNESS % code).replace("TIP_BASE", "true" if auto(".tip") else "false").replace(
        "TIP_CLASSES", json.dumps(classes))
    out = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def pinned_problems(log):
    out = []
    if not (log["pinned"] and log["pinnedClass"]):
        out.append("a tap does not pin the tooltip")
    if not (log["afterLeave"]["shown"] and log["afterLeave"]["pinned"]):
        out.append("the pointer leaving hides a pinned tooltip")
    if log["afterMove"]["pinned"] or log["afterMove"]["pinnedClass"]:
        out.append("showing another reference keeps the tooltip pinned")
    if log["afterHide"]["pinned"] or log["afterHide"]["shown"] or log["afterHide"]["classes"]:
        out.append("hiding leaves the tooltip pinned")
    for k in ("tap", "focusQuick", "focusRadio", "hoverBack"):
        tap = log[k]
        if tap["calls"]:
            out.append("a tap on the shown tooltip answered a decision (%s): %s" % (k, tap["calls"]))
        elif not (tap["pd"] and tap["sp"]) or tap["shown"]:
            out.append("a tap on the shown tooltip does not close it and stop there (%s)" % k)
    if not log["insideTip"]["shown"]:
        out.append("the pointer inside the tooltip hides it")
    for k in ("dblRadio", "dblQuick"):
        if log[k][0]["calls"] or log[k][1]["calls"]:
            out.append("a double tap on the tooltip answered a decision (%s): %s"
                       % (k, log[k][0]["calls"] + log[k][1]["calls"]))
    if log["focusOther"]["shown"]:
        out.append("focus moving to another control keeps the tooltip shown")
    if not log["focusLeave"]["shown"]:
        out.append("the pointer leaving hides a tooltip whose reference has focus")
    return out


def pin_problems(html):
    click = html[html.index('document.addEventListener("click"'):html.index('addEventListener("resize"')]
    out = []
    if "else if(tipFor===s&&tipPinned)hideTip();else{showTip(s);pinTip()}" not in click:
        out.append("a tap on a reference not on the page shows nothing")
    if "if(tipPinned)hideTip();" not in click:
        out.append("a pinned tooltip is not closed by a tap elsewhere")
    keys = html[html.index('document.addEventListener("keydown"'):]
    if 'e.key==="Escape"&&tipFor)hideTip()' not in keys:
        out.append("Escape does not close the tooltip")
    return out


def slug_problems(on, ref):
    out = []
    if not (on.startswith("<button") and 'data-goto="41"' in on):
        out.append("an on-page reference is not a link to its card")
    if not ref.startswith("<button") or "data-goto" in ref:
        out.append("a refs reference is not a tooltip-only reference")
    if "aria-describedby" in on + ref:
        out.append("a reference is described by a tooltip that is not shown")
    if "aria-haspopup" in on + ref:
        out.append("a reference opens a popup")
    return out


@unittest.skipUnless(NODE, "node is not installed")
class ReferenceTooltip(unittest.TestCase):
    """Every reference reads N · short name: on the page it opens its card; hovering or focusing it
    shows a tooltip (answer 335's feedback, 7434 M8)."""

    def test_the_references(self):
        s = run_page(example())["slugs"]
        self.assertEqual(slug_problems(s["on"], s["ref"]), [])
        self.assertIn(">41 · Docs build home</button>", s["on"])
        self.assertIn(">38 · build cache reset</button>", s["ref"])
        # mutants: an on-page reference without its link; a refs one as a link
        self.assertIn("an on-page reference is not a link to its card",
                      slug_problems(s["on"].replace(' data-goto="41"', ""), s["ref"]))
        self.assertIn("a refs reference is not a tooltip-only reference",
                      slug_problems(s["on"], s["ref"].replace("<button", '<button data-goto="38"')))
        self.assertIn("a reference is described by a tooltip that is not shown",
                      slug_problems(s["on"].replace("<button", '<button aria-describedby="tip"'), s["ref"]))

    def test_the_tooltip_describes_its_reference_only_while_shown(self):
        # showTip and hideTip, run under node on stand-ins for the tooltip and two references
        self.assertEqual(describe_problems(TIP_FNS()), [])
        # mutants: the attribute left on after hiding; set before the tooltip is filled
        fns = TIP_FNS()
        self.assertTrue(describe_problems(fns.replace('if(tipFor)tipFor.removeAttribute("aria-describedby");', "")))
        moved = fns.replace(';el.setAttribute("aria-describedby","tip");', ";").replace(
            "tipFor=el;tip.innerHTML", 'el.setAttribute("aria-describedby","tip");tipFor=el;tip.innerHTML')
        self.assertNotEqual(moved, fns)
        self.assertTrue(describe_problems(moved))

    def test_a_shown_tooltip_takes_the_tap_and_answers_nothing(self):
        html = PAGE.read_text()
        self.assertEqual(pinned_problems(shell_log(html)), [])
        mutants = {
            "pointer-events back to none": (".tip.shown{pointer-events:auto;", ".tip.shown{pointer-events:none;",
                                             "a tap on the shown tooltip answered a decision"),
            "the old pinned-only pointer rule": (".tip.shown{pointer-events:auto;cursor:pointer}",
                                                  ".tip.pinned{pointer-events:auto}",
                                                  "a tap on the shown tooltip answered a decision (focusQuick)"),
            "the tooltip guard dropped": ('if(e.target.closest("#tip")){e.preventDefault();e.stopPropagation();hideTip();tipClosedAt=e.timeStamp;return}', "",
                                          "a tap on the shown tooltip does not close it and stop there"),
            "the double-tap swallow dropped": ('if(e.timeStamp-tipClosedAt<500){e.preventDefault();e.stopPropagation();return}', "",
                                               "a double tap on the tooltip answered a decision"),
            "focus elsewhere keeps the tooltip": ('if(s)showTip(s);else if(tipFor)hideTip()', "if(s)showTip(s)",
                                                  "focus moving to another control keeps the tooltip shown"),
            "leaving hides a focused reference's tooltip": ("&&tipFor!==document.activeElement)hideTip()", ")hideTip()",
                                                            "the pointer leaving hides a tooltip whose reference has focus"),
            "mouseover hides inside the tooltip": ('!e.target.closest("#tip")&&tipFor', "tipFor",
                                                   "the pointer inside the tooltip hides it"),
            "hideTip keeps the pin": ("tipFor=null;tipPinned=false;", "tipFor=null;", "hiding leaves the tooltip pinned"),
            "leaving hides a pinned one": ("tipFor&&!tipPinned&&tipFor!==", "tipFor&&tipFor!==",
                                           "the pointer leaving hides a pinned tooltip"),
            "moving keeps the pin": ('tipFor.removeAttribute("aria-describedby");tipPinned=false;tip.classList.remove("pinned")}',
                                     'tipFor.removeAttribute("aria-describedby")}',
                                     "showing another reference keeps the tooltip pinned"),
        }
        for name, (old, new, want) in mutants.items():
            with self.subTest(mutant=name):
                self.assertEqual(html.count(old), 1, name)
                probs = pinned_problems(shell_log(html.replace(old, new)))
                self.assertTrue(any(p.startswith(want) for p in probs), (name, probs))

    def test_a_tap_on_a_reference_not_on_the_page_pins_its_tooltip(self):
        # a touch screen has no hover and does not focus a tapped button: the click shows it
        self.assertEqual(pin_problems(PAGE.read_text()), [])
        mutant = PAGE.read_text().replace("else{showTip(s);pinTip()}", "")
        self.assertIn("a tap on a reference not on the page shows nothing", pin_problems(mutant))

    def test_a_cards_tooltip(self):
        d = example()
        res = run_page(d)
        for blk, c in zip(res["blocks"], d["cards"]):
            self.assertEqual(tip_problems(blk["tip"], c), [], c["n"])
        # an answer given shows in it, with the operator's words
        d["_answers"] = {"41": {"choice": "b", "words": "ship it"}}
        tip = run_page(d)["blocks"][0]["tip"]
        self.assertEqual(tip_problems(tip, d["cards"][0], "(b) · rec — “ship it”"), [])
        # an option with no one line shows its effect
        d = example()
        del d["cards"][0]["options"][0]["line"]
        tip = run_page(d)["blocks"][0]["tip"]
        self.assertEqual(tip_problems(tip, d["cards"][0]), [])
        self.assertIn("Nothing changes; the maintainer publishes by hand.", tip_text(tip))

    def test_mutant_title_alone(self):
        script = page_free_script()
        self.assertIn(TIP_ONE_LINE, script)
        d = example()
        tip = run_page(d, script.replace(TIP_ONE_LINE, ""))["blocks"][0]["tip"]
        self.assertTrue(any("is not shown as (x) title — one line" in p for p in tip_problems(tip, d["cards"][0])))

    def test_a_refs_tooltip(self):
        tip = tip_text(run_page(example())["refTips"]["38"])
        self.assertIn("Asked", tip)
        self.assertIn("Clear the docs build cache?", tip)
        self.assertIn("Answera — clear it", tip)
        self.assertIn("Answered earlier this month · not on this page", tip)

    def test_the_tooltip_is_escaped(self):
        d = example()
        d["cards"][0]["context"] = '<script>x</script> the cache ([[38]])'
        d["cards"][0]["options"][0]["title"] = '<img src=x onerror="alert(1)">'
        d["refs"]["38"]["q"] = "<script>y</script>"
        res = run_page(d)
        for h in (res["blocks"][0]["tip"], res["refTips"]["38"]):
            self.assertNotIn("<script", h)
            self.assertNotIn("<img", h)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", res["blocks"][0]["tip"])
        # slugs in it are text, never a nested control
        self.assertNotIn("<button", res["blocks"][0]["tip"])


@unittest.skipUnless(NODE, "node is not installed")
class ReferenceRule(unittest.TestCase):
    """An open decision a card names goes on the page as a card; a ref is never a card; every [[N]]
    is a card or a ref; an excerpt is not scanned (answer 335's feedback, 7434 M8.1)."""

    def bad(self, d):
        return run_page(d)["bad"]

    def test_the_example_passes(self):
        self.assertEqual(self.bad(example()), [])

    def test_each_refusal(self):
        open_ = "refs 38: decision 38 is still open; put its card on the page instead of a ref"
        d = example(); d["refs"]["38"]["when"] = "open"
        self.assertIn(open_, self.bad(d))
        d = example(); d["refs"]["38"]["a"] = "not yet answered"
        self.assertIn(open_, self.bad(d))
        d = example(); d["refs"]["41"] = dict(d["refs"]["38"])
        self.assertIn("refs 41: decision 41 is a card on the page; drop it from refs", self.bad(d))
        stray = lambda bad, at: any(b.startswith(at + ": [[999]] is neither a card on the page nor a ref")
                                    for b in bad)
        d = example(); d["cards"][0]["context"] += " See [[999]]."
        self.assertTrue(stray(self.bad(d), "card 41: context"))
        d = example(); d["cards"][0]["detail"]["why"][1][0]["b"].append("As [[999]] said.")
        self.assertTrue(stray(self.bad(d), "card 41: detail"))
        d = example(); d["page"]["lede"] = "Read [[999]] first."
        self.assertTrue(stray(self.bad(d), "page.lede"))
        d = example(); d["layers"][1][2] = "After [[999]]."
        self.assertTrue(stray(self.bad(d), "layer details note"))
        d = example(); d["layers"][1].append("Shared since [[999]].")
        self.assertTrue(stray(self.bad(d), "layer details shared"))

    def test_an_excerpt_holding_a_slug_passes(self):
        d = example()
        d["cards"][0]["x_excerpt"] = {"text": "see [[999]]", "lang": "text"}
        self.assertEqual([b for b in self.bad(d) if "999" in b], [])
        # mutant: the same text outside an excerpt is refused
        d["cards"][0]["x_excerpt"] = {"text": "see [[999]]", "lang": "text", "other": 1}
        self.assertTrue([b for b in self.bad(d) if "999" in b])


def runner(data=None, *, path=None, cwd=None, script=RUNNER):
    """Run the runner on data written to a temp cards.json, or on a path as given."""
    with tempfile.TemporaryDirectory() as tmp:
        if path is None:
            path = pathlib.Path(tmp) / "cards.json"
            path.write_text(data if isinstance(data, str) else json.dumps(data))
        out = subprocess.run([NODE, str(script), str(path)], capture_output=True, text=True,
                             timeout=60, cwd=cwd or SKILL)
    return out.returncode, out.stdout, out.stderr


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageRunner(unittest.TestCase):

    def assert_one_line(self, out, start):
        lines = out.splitlines()
        self.assertEqual(len(lines), 1, out)
        self.assertTrue(lines[0].startswith(start), out)
        self.assertNotIn("    at ", out)

    def assert_lint(self, d, needle):
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        self.assertTrue(all(x.startswith(("lint: card ", "lint: page: ")) for x in out.splitlines()),
                        out)
        self.assertIn(needle, out)
        return out

    def assert_clean(self, d):
        code, out, err = runner(d)
        self.assertEqual((code, out), (0, ""), err)

    def test_the_example_is_clean(self):
        # end-to-end pin for the example's contexts: no refusal and no lint on any card
        self.assert_clean(example())

    def test_a_missing_context_exits_1_with_the_refusal(self):
        d = example()
        del d["cards"][0]["context"]
        code, out, _ = runner(d)
        self.assertEqual(code, 1)
        self.assertIn("card 41: context missing", out)

    def test_a_missing_file_is_one_line(self):
        code, out, _ = runner(path="/nonexistent/cards.json")
        self.assertEqual(code, 1)
        self.assert_one_line(out, "check_cards: cannot read /nonexistent/cards.json")

    def test_invalid_json_is_one_line(self):
        code, out, _ = runner("{")
        self.assertEqual(code, 1)
        self.assert_one_line(out, "check_cards: not valid JSON")

    def test_an_unreadable_template_or_a_missing_marker_is_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "scripts").mkdir()
            script = root / "scripts" / "check_cards.js"
            shutil.copy(RUNNER, script)
            # no assets/index.html beside it
            code, out, _ = runner(example(), script=script)
            self.assertEqual(code, 1)
            self.assert_one_line(out, "check_cards: cannot read the template")
            # a template with its end-of-page-free-part marker gone
            (root / "assets").mkdir()
            (root / "assets" / "index.html").write_text(PAGE.read_text().replace(END_MARK, "/* x"))
            code, out, _ = runner(example(), script=script)
            self.assertEqual(code, 1)
            self.assert_one_line(out, "check_cards: the template has no page-free part")

    def test_a_file_failing_the_check_gets_refusals_and_no_lints(self):
        # layers kept, so check() reaches the card checks: card 41 has a blank context (a
        # refusal) and KAPPA-3570 in its TLDR, which the id lint would report on a clean file
        d = example()
        d["cards"][0]["context"] = " "
        d["cards"][0]["tldr"].append("Fixes KAPPA-3570")
        code, out, _ = runner(d)
        self.assertEqual(code, 1)
        self.assertIn("card 41: context missing", out)
        self.assertNotIn("lint:", out)

    def test_the_id_lint_covers_every_flat_field_whatever_context_says(self):
        setters = {
            "t": lambda c: c.__setitem__("t", "Docs build KAPPA-3570"),
            "tldr": lambda c: c["tldr"].append("KAPPA-3570 asks for it"),
            "title": lambda c: c["options"][0].__setitem__("title", "Keep KAPPA-3570"),
            "one line": lambda c: c["options"][0].__setitem__("line", "per KAPPA-3570"),
            "open": lambda c: c["open"].append("whether KAPPA-3570 matters"),
        }
        for k in ("wait", "reach", "undo", "cost"):
            setters["impact." + k] = (lambda k: lambda c: c["impact"].__setitem__(k, "per KAPPA-3570"))(k)
        for k in ("effect", "reach", "cost"):
            setters["option " + k] = (lambda k: lambda c: c["options"][0].__setitem__(k, "per KAPPA-3570"))(k)
        for k in ("ifleft", "roundcosts", "ifunanswered", "reason", "norec", "dep"):
            setters[k] = (lambda k: lambda c: c.__setitem__(k, "per KAPPA-3570"))(k)
        for name, put in setters.items():
            with self.subTest(field=name):
                d = example()
                put(d["cards"][0])
                self.assert_lint(d, "lint: card 41: KAPPA-3570 looks like an id")
                # a gloss in Context no longer clears an id: the page names things instead
                d["cards"][0]["context"] = d["cards"][0]["context"][:-1] + "; KAPPA-3570 is its ticket."
                self.assert_lint(d, "lint: card 41: KAPPA-3570 looks like an id")

    def test_ids_in_the_folds_levels_act_lede_layers_and_refs_are_linted(self):
        last_b = lambda lv: lv[-1]["b"]
        for put, needle in (
                (lambda d: d["cards"][0]["options"][0].__setitem__("text", "see KAPPA-3570"), "lint: card 41: "),
                (lambda d: d["cards"][0].__setitem__("evidence", "see KAPPA-3570"), "lint: card 41: "),
                (lambda d: last_b(d["cards"][0]["detail"]["why"][1]).append("See KAPPA-3570."),
                 "lint: card 41: "),
                (lambda d: last_b(d["cards"][0]["options"][1]["detail"][1]).append("See KAPPA-3570."),
                 "lint: card 41: "),
                (lambda d: d["cards"][0]["options"][0].__setitem__("reach", "per KAPPA-3570"),
                 "lint: card 41: "),
                (lambda d: d["cards"][0]["options"][1]["act"].append("Close KAPPA-3570."), "lint: card 41: "),
                (lambda d: d["page"].__setitem__("lede", "From KAPPA-3570."), "lint: page: "),
                (lambda d: d["layers"][0].__setitem__(2, "From KAPPA-3570."), "lint: page: "),
                (lambda d: d["refs"]["38"].__setitem__("q", "Clear KAPPA-3570?"), "lint: page: ")):
            with self.subTest(needle=needle):
                d = example()
                put(d)
                self.assert_lint(d, needle + "KAPPA-3570 looks like an id")
        # in backticks it is something the operator types: clean
        d = example()
        d["cards"][0]["options"][1]["act"].append("Run `close KAPPA-3570` in the tracker.")
        self.assert_clean(d)

    def test_counts_and_named_things_in_the_folds_act_lede_and_layers_are_not_linted(self):
        last_b = lambda lv: lv[-1]["b"]
        t = "The three reviewers, in content mode."
        for put in (lambda d: d["cards"][0].__setitem__("evidence", "Observed: " + t),
                    lambda d: last_b(d["cards"][0]["detail"]["why"][1]).append(t),
                    lambda d: d["cards"][0]["options"][0].__setitem__("reach", t),
                    lambda d: d["cards"][0]["options"][1]["act"].append("Ask " + t),
                    lambda d: d["page"].__setitem__("lede", t),
                    lambda d: d["layers"][0].__setitem__(2, t)):
            d = example()
            put(d)
            self.assert_clean(d)

    def test_slugs_and_hex_colours_are_not_ids(self):
        d = example()
        d["cards"][2]["options"][0]["line"] = "keeps #2d56c8, as [[38]] left it"
        self.assert_clean(d)

    def test_well_known_terms_are_linted_never_refused(self):
        for t in WELL_KNOWN:
            with self.subTest(term=t):
                d = example()
                d["cards"][0]["tldr"].append("Uses " + t)
                self.assert_lint(d, "lint: card 41: " + t + " looks like an id")

    def test_a_count_its_context_does_not_name_is_linted(self):
        d = with_tldr("Start the three now")
        self.assert_lint(d, '"three" counts things its context does not name: say what the '
                            "three things are, or list them")
        # spliced in as a clause: Context's summary stays two sentences
        d["cards"][0]["context"] = (d["cards"][0]["context"][:-1]
                                    + "; the three are the build, the cache and the publish step.")
        self.assert_clean(d)

    def test_numbers_that_are_not_counts_are_not_linted(self):
        d = example()
        d["cards"][1]["options"][0]["line"] = "12 redirects keep old links working"  # twelve, in context
        d["cards"][0]["tldr"] = [
            "Takes about 4 minutes, from 2026-10-08, reaching 50% of readers in 2 weeks",
            "v1.2.3 ships at 14:05, a two-way door"]
        self.assert_clean(d)

    def test_an_ids_digits_are_not_a_count(self):
        d = with_tldr("Fixes KAPPA-3570")
        out = self.assert_lint(d, "KAPPA-3570 looks like an id")
        self.assertEqual(len(out.splitlines()), 1, out)

    def test_a_named_thing_its_context_does_not_gloss_is_linted(self):
        d = example()
        d["cards"][0]["options"][0]["title"] = "Turn on content mode"
        self.assert_lint(d, '"content mode" is not glossed in its context: give it a one-line '
                            "gloss in context")
        d["cards"][0]["context"] = d["cards"][0]["context"][:-1] + "; content mode serves pages as text."
        self.assert_clean(d)

    def test_a_named_thing_drops_its_determiner(self):
        d = with_tldr("The plan stays")
        out = self.assert_lint(d, '"plan" is not glossed')
        self.assertNotIn('"the plan"', out)

    def test_the_broad_tldr_lint_reports_what_the_page_lets_through(self):
        for b in LINTED_MISSES:
            with self.subTest(bullet=b):
                self.assert_lint(with_tldr(b), "lint: card 41: tldr bullet 2 may carry the "
                                               "recommendation")

    def test_the_broad_tldr_lint_leaves_ordinary_rec_words_alone(self):
        for b in ("Recent failures", "Records stay"):
            with self.subTest(bullet=b):
                self.assert_clean(with_tldr(b))

    def test_a_leftover_what_is_linted(self):
        d = example()
        d["cards"][0]["what"] = "Where the documentation site is built and published from."
        self.assert_lint(d, "lint: card 41: what present: move it into context (after the "
                            "terms, before the cue) and delete it")


class RevRule(unittest.TestCase):
    """The `rev` rule decides which answers keep counting: it reads the same wherever it is
    written, so no copy drifts."""

    def test_the_rev_rule_is_in_identical_words_in_all_four_places(self):
        # the v5 upgrade keeps rev, so page answers keep counting
        flat = lambda p: re.sub(r"\s+", " ", p.read_text())
        self.assertEqual(flat(RECORD).count(REV_RULE), 1, "card-record.md: the rev row")
        self.assertEqual(flat(SCHEMA).count(REV_RULE), 1, "cards-schema.md: § Republishing older data")
        self.assertEqual(flat(SKILL_MD).count(REV_RULE), 2, "SKILL.md: step 2's rev bullet and "
                         "step 3's republish paragraph")
        # the retired migration wording is gone from all four
        for p in (RECORD, SCHEMA, SKILL_MD):
            self.assertNotIn("Only the one-time format migration keeps it", flat(p), p.name)


if __name__ == "__main__":
    unittest.main()
