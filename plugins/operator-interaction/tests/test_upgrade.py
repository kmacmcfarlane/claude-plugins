"""The upgrader moves older page data to decision-page/5, format only, every rev kept.

`skills/decision-page/scripts/upgrade_cards.js`, run under node on two fixtures with invented
text: `tests/fixtures/cards.legacy.json` (the shipped example before v5, kept verbatim) and
`tests/fixtures/cards.kit.json` (three cards in the shape of the answer page's working kit, one
of them in its v4 layout). Each upgrades to a file the page's check passes and the runner runs
on with no refusal, once the legacy set card is given its items (the set refusal, F6); the legacy map (effect from the blocks row, else the option's impact;
`warn` to `oneway`; `unknown` to `open`, none dropped); the kit's name trap (its `pros` the one
line, `prosT` the rows) with its mutant; every rev kept byte for byte; all or nothing (a card
it cannot map stops the run, nothing written); `--only`, `--records`; a v5 file passed through.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE
from test_depth import run_page
from test_context import runner, SKILL
from test_record import run_record

# an older card never held assumptions: the upgrade invents none, so a recommended card is linted for
# them, which a writer leaves knowingly on an upgraded card (the Assumptions fold, A1)
ASSUME_LINT = "depth: no assumptions: "
# nor pros and cons (F4): the upgrade invents none, so the tradeoffs lint fires on an upgraded
# legacy card, left knowingly the same way
TRADEOFFS_LINTS = ("options but (z) carries its pros and cons", ") has no pro", ") has no con")
# nor a plan in brief (F5): an upgraded card's view shows its text instead, so the plan lint is left knowingly too
PLAN_LINTS = ("options carries its plan in brief", ") has no plan: ")


# nor a set's items (F6): an older card about a set counts its items without listing them, which the runner
# refuses (the set refusal: the What part lists every item), so a writer gives the upgraded card its items before a
# republish. The legacy fixture's card 42 moves twelve pages
SET_REFUSAL = ": a set not listed in items: it counts 12 things where it says what is decided"
ITEMS_42 = [{"name": "Guide %d" % i, "where": "/guides/", "about": "a how-to guide"} for i in range(1, 11)] + [
    {"name": "Site settings", "where": "/config/", "about": "a configuration page"},
    {"name": "Theme settings", "where": "/config/", "about": "a configuration page"}]


def with_items(card):
    """The writer's step after an upgrade: card 42's twelve moved pages, listed in items."""
    if card.get("n") == 42:
        card["items"] = copy.deepcopy(ITEMS_42)
    return card


def unassumed(code, out):
    """The runner's (code, output) less the lints an upgraded older card may carry knowingly: assume,
    tradeoffs and plan, since the upgrade invents no field."""
    rest = [x for x in out.splitlines()
            if ASSUME_LINT not in x and not any(t in x for t in TRADEOFFS_LINTS + PLAN_LINTS)]
    return (0 if code == 2 and not rest else code), "".join(x + "\n" for x in rest)

UPGRADER = SKILL / "scripts" / "upgrade_cards.js"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
LEGACY = FIXTURES / "cards.legacy.json"
KIT = FIXTURES / "cards.kit.json"
QMAP = {"41": "Where should the docs site be built and published from?",
        "42": "What happens to the old URLs of the twelve moved pages?",
        "43": "Which accent colour should the docs site use?",
        "51": "Should the nightly backup also keep an offsite copy?",
        "52": "Should old nightly backups be pruned after thirty days?",
        "53": "When should the backup report be sent?"}


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the upgrader tests (Upgrade) are skipped, so moving older "
              "page data to decision-page/5 went untested", file=sys.stderr)


def load(p):
    return json.loads(pathlib.Path(p).read_text())


def upgrade(data, qmap=QMAP, args=(), script=UPGRADER):
    """Run the upgrader on data; (exit code, stdout, the output file's data or None, the records dir's files)."""
    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp)
        (t / "in.json").write_text(data if isinstance(data, str) else json.dumps(data))
        cmd = [NODE, str(script), str(t / "in.json"), str(t / "out.json")]
        if qmap is not None:
            (t / "q.json").write_text(json.dumps(qmap))
            cmd += ["--questions", str(t / "q.json")]
        extra = []
        for a in args:
            if isinstance(a, list):  # a --only set, written to a file
                (t / "only.txt").write_text("\n".join(str(n) for n in a) + "\n")
                extra.append(str(t / "only.txt"))
            elif a == "RECORDS":
                extra.append(str(t / "recs"))
            else:
                extra.append(a)
        out = subprocess.run(cmd + extra, capture_output=True, text=True, timeout=60)
        res = load(t / "out.json") if (t / "out.json").exists() else None
        recs = {p.name: load(p) for p in sorted((t / "recs").glob("*.json"))} if (t / "recs").exists() else {}
        raw = (t / "out.json").read_text() if (t / "out.json").exists() else None
    return out.returncode, out.stdout, res, recs, raw


def opt(card, k):
    return next(o for o in card["options"] if o["k"] == k)


def by_n(d):
    return {c["n"]: c for c in d["cards"]}


# the name trap, as a check on an upgraded option: the one-line pro and con are text, the table's pros
# and cons lists
def name_trap_problems(o):
    out = []
    for k in ("pro", "con"):
        if k in o and not isinstance(o[k], str):
            out.append("(%s) %s is not one line" % (o["k"], k))
    for k in ("pros", "cons"):
        if k in o and not isinstance(o[k], list):
            out.append("(%s) %s is not the table's rows" % (o["k"], k))
    return out


REV_KEPT = '{ note.rev = "rev kept"; return rev; }'
REV_NORMALISED = '{ note.rev = "rev kept"; return rev.replace(/T([0-9][0-9]:[0-9][0-9])Z$/, "T$1:00Z"); }'
PROTO_SAFE = "const y = Object.create(null);\n      for (const k of Object.keys(x)) y[k] = x[k];"
TRAP = ('if ("pros" in o) x.pro = o.pros;\n    if ("cons" in o) x.con = o.cons;\n'
        '    if ("prosT" in o) x.pros = o.prosT;\n    if ("consT" in o) x.cons = o.consT;')
TRAP_STRAIGHT = ('if ("pros" in o) x.pros = o.pros;\n    if ("cons" in o) x.cons = o.cons;\n'
                 '    if ("prosT" in o) x.prosT = o.prosT;\n    if ("consT" in o) x.consT = o.consT;')


@unittest.skipUnless(NODE, "node is not installed")
class Upgrade(unittest.TestCase):

    def test_the_legacy_fixture_upgrades_to_a_page_that_passes(self):
        code, out, d, _, _ = upgrade(load(LEGACY))
        self.assertEqual(code, 0, out)
        self.assertEqual(d["format"], "decision-page/5")
        self.assertEqual(run_page(d)["bad"], [])
        # the set card is refused until its items are listed, and it alone (F6)
        code, rout, _ = runner(d)
        self.assertEqual((code, [x.split(":")[0] for x in rout.splitlines()]), (1, ["card 42"]), rout)
        self.assertIn("card 42" + SET_REFUSAL, rout)
        for c in d["cards"]:
            with_items(c)
        self.assertEqual(run_page(d)["bad"], [])
        self.assertEqual(unassumed(*runner(d)[:2]), (0, ""))
        # the legacy cards with a recommendation are the ones linted for it
        self.assertEqual(sorted(x.split(":")[1].strip() for x in runner(d)[1].splitlines() if ASSUME_LINT in x),
                         ["card 41", "card 42"])
        # and every legacy card, holding no pros and cons, is linted for them (F4)
        self.assertEqual(sorted(x.split(":")[1].strip() for x in runner(d)[1].splitlines()
                                if "options but (z) carries its pros and cons" in x),
                         ["card 41", "card 42", "card 43"])
        # every rev kept, every card reported
        old = {c["n"]: c["rev"] for c in load(LEGACY)["cards"]}
        self.assertEqual({c["n"]: c["rev"] for c in d["cards"]}, old)
        for n in old:
            self.assertIn("card %d: legacy, rev kept" % n, out)

    def test_the_legacy_map(self):
        src = by_n(load(LEGACY))
        d = by_n(upgrade(load(LEGACY))[2])
        # effect from the blocks row's happens, reach from who; o[1] the text, o[3] the title, o[4] the line
        b = opt(d[41], "b")
        self.assertEqual(b["effect"], src[41]["blocks"]["b"]["happens"])
        self.assertEqual(b["reach"], src[41]["blocks"]["b"]["who"])
        self.assertEqual((b["text"], b["title"], b["line"]), tuple(src[41]["o"][1][i] for i in (1, 3, 4)))
        self.assertEqual(b["act"], src[41]["act"]["b"])
        self.assertEqual(b["detail"], src[41]["detail"]["o"]["b"])
        # (z)'s impact is its effect, what waiting does
        self.assertEqual(opt(d[41], "z")["effect"], src[41]["o"][2][2])
        # warn -> oneway; the flagged row's undo and flag move into its option
        self.assertTrue(d[42]["oneway"])
        self.assertNotIn("warn", d[42])
        self.assertTrue(opt(d[42], "b")["oneway"])
        self.assertEqual(opt(d[42], "b")["undo"], src[42]["blocks"]["b"]["undo"])
        # unknown -> open; "none" leaves no open
        self.assertEqual(d[41]["open"], [src[41]["unknown"]])
        self.assertNotIn("open", d[43])
        # no card-level effect, at any level; no positional options or blocks left
        for c in d.values():
            self.assertNotIn("effect", c["impact"])
            for lv in c.get("detail", {}).get("impact", []):
                self.assertNotIn("effect", lv)
            for k in ("o", "blocks", "act", "warn", "unknown"):
                self.assertNotIn(k, c)
            self.assertNotIn("o", c.get("detail", {}))
            self.assertEqual(c["q"], QMAP[str(c["n"])])

    def test_an_option_with_no_row_takes_its_impact_as_its_effect(self):
        src = load(LEGACY)
        del src["cards"][2]["blocks"]
        d = by_n(upgrade(src)[2])
        self.assertEqual(opt(d[43], "b")["effect"], src["cards"][2]["o"][1][2])
        self.assertNotIn("reach", opt(d[43], "b"))

    def test_a_minute_rev_survives_byte_for_byte_and_a_bad_one_is_renewed(self):
        # an answer counts only when its rev equals its card's exactly: the upgrade never rewrites one
        src = load(LEGACY)
        src["cards"][0]["rev"] = "2026-01-12T09:30Z"
        src["cards"][1]["rev"] = "version two"
        code, out, d, _, _ = upgrade(src)
        self.assertEqual(code, 0, out)
        self.assertEqual(run_page(d)["bad"], [])
        d = by_n(d)
        self.assertEqual(d[41]["rev"], "2026-01-12T09:30Z")
        self.assertIn("card 41: legacy, rev kept", out)
        self.assertRegex(d[42]["rev"], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
        self.assertIn('card 42: legacy, new rev (was "version two")', out)
        # mutant: an upgrader that normalises the minute form to seconds
        js = UPGRADER.read_text()
        self.assertEqual(js.count(REV_KEPT), 1)
        with tempfile.TemporaryDirectory() as tmp:
            m = pathlib.Path(tmp) / "upgrade_cards.js"
            m.write_text(js.replace(REV_KEPT, REV_NORMALISED))
            mutant = by_n(upgrade(src, script=m)[2])
        self.assertNotEqual(mutant[41]["rev"], src["cards"][0]["rev"])

    def test_the_kit_fixture_upgrades_to_a_page_that_passes(self):
        code, out, d, _, _ = upgrade(load(KIT))
        self.assertEqual(code, 0, out)
        self.assertEqual(run_page(d)["bad"], [])
        rcode, rout, _ = runner(d)
        # no refusal; the only lints are the assume lint on a recommended card the kit gave no assumptions, and the cold read of the kit's own
        # pro and con rows and of its plans and tables (the option's view), and the kit's per that names the
        # recommended option alone, which an upgrade carries over as written and cannot complete without inventing,
        # and the plan lint on a (z) the kit gave no plan. Its what is the What part now (F6): no lint
        self.assertIn(rcode, (0, 2), rout)
        self.assertNotIn("what present", rout)
        self.assertTrue(all(ASSUME_LINT in x or "(pros and cons)" in x or "per gives only the recommended" in x
                            or "(an option's view)" in x or any(t in x for t in PLAN_LINTS)
                            for x in rout.splitlines()), rout)
        # the kit's plans come over as the option's plan in brief, and its view opens on them
        self.assertTrue(all(o.get("plan") for c in d["cards"] for o in c["options"] if o["k"] != "z"))
        h = run_page(d)["cards"][0]["more"]["a"]
        self.assertTrue(h.startswith('<div class="oplan"><span class="lbl">Plan in brief</span>'), h[:80])
        self.assertIn("card 51: kit, rev kept", out)
        self.assertIn("card 52: kit (v4), rev kept;", out)
        self.assertEqual(by_n(d)[52]["rev"], "2026-02-03T08:15Z")
        # an evidence attachment's id is dropped, and said
        self.assertIn('evidence attachment id "health" dropped', out)

    def test_the_kit_map(self):
        src = by_n(load(KIT))
        d = by_n(upgrade(load(KIT))[2])
        c = d[51]
        # the name trap: the kit's pros/cons are the one line, prosT/consT the table's rows
        a = opt(c, "a")
        self.assertEqual(a["title"], src[51]["options"][0]["text"])
        self.assertEqual(a["pro"], src[51]["options"][0]["pros"])
        self.assertEqual(a["con"], src[51]["options"][0]["cons"])
        self.assertEqual(a["pros"], src[51]["options"][0]["prosT"])
        self.assertEqual(a["cons"], src[51]["options"][0]["consT"])
        for o in c["options"]:
            self.assertEqual(name_trap_problems(o), [], o["k"])
        self.assertEqual(opt(c, "b")["act"], src[51]["act"]["b"])
        # assumptions paired with their tripwires; background into why and whyask
        self.assertEqual(c["assume"], [{"rests": r, "tw": t} for r, t in
                                       zip(src[51]["assume"]["assumptions"], src[51]["assume"]["tripwires"])])
        self.assertEqual((c["basis"], c["reason"]), (src[51]["assume"]["basis"], src[51]["assume"]["reason"]))
        self.assertEqual((c["why"], c["whyask"]), (src[51]["background"]["why"], src[51]["background"]["whyask"]))
        # evidence attachments into one flat list; the example's mode into form
        self.assertEqual(c["evidence"], ["Health report — Observed: the disk logs rising read errors.",
                                         "Observed: it is four years old."])
        self.assertEqual([x["kind"] for x in c["attached"]], ["example"])
        self.assertEqual(c["attached"][0]["form"], "invented to illustrate")
        self.assertNotIn("mode", c["attached"][0])
        self.assertEqual(d[52]["evidence"], ["Free space — The disk's free space drops about one percent a night."])
        # scope, finding, rejected
        self.assertEqual(c["scope"], {"level": "shapes", "says": "the backup job's target list"})
        self.assertEqual(c["finding"]["mechanism"], src[51]["finding"]["what"])
        self.assertEqual(c["finding"]["excerpt"], src[51]["finding"]["code"])
        self.assertEqual(c["rejected"], [{"t": "A second local disk", "why": ["It burns with the first."]}])
        # likelihood: observed kept; another word kept at the head of seen
        self.assertEqual(d[53]["likelihood"], {"kind": "observed", "seen": src[53]["likelihood"]["text"]})
        self.assertEqual(d[52]["likelihood"]["kind"], "evidence")
        self.assertTrue(d[52]["likelihood"]["seen"].startswith("(estimated) "))
        # what: {intro, items} into what and items; the dependency line as text with its slug
        self.assertEqual(d[52]["what"], "The backups the pruning would delete.")
        self.assertEqual(d[52]["items"][0], {"name": "the nightly backups", "about": "one per night",
                                             "per": {"a": "older than thirty days deleted"}})
        self.assertEqual(d[52]["items"][1], {"name": "the weekly snapshots"})
        self.assertEqual(d[52]["dep"], "only if [[51]] is (a) or (b)")
        # the v4 layout's assume.unknown is open; no effect on any Impact
        self.assertEqual(d[52]["open"], ["whether any old backup is needed for an audit"])
        self.assertEqual(d[51]["open"], src[51]["open"])
        for x in d.values():
            self.assertNotIn("effect", x["impact"])
            self.assertNotIn("background", x)

    def test_the_name_trap_mutant(self):
        # mapped straight across, the one-line texts land where the table's rows belong
        js = UPGRADER.read_text()
        self.assertEqual(js.count(TRAP), 1)
        with tempfile.TemporaryDirectory() as tmp:
            m = pathlib.Path(tmp) / "upgrade_cards.js"
            m.write_text(js.replace(TRAP, TRAP_STRAIGHT))
            d = by_n(upgrade(load(KIT), script=m)[2])
        self.assertIn("(a) pros is not the table's rows", name_trap_problems(opt(d[51], "a")))

    def test_all_or_nothing(self):
        cases = [
            ("unequal assumptions", lambda d: d["cards"][0]["assume"]["tripwires"].pop(),
             "card 51: assume has 2 assumptions and 1 tripwires"),
            ("unknown scope", lambda d: d["cards"][0]["scope"].__setitem__("k", "nice to have"),
             'card 51: scope level "nice to have" is not one the record has'),
            ("unknown field", lambda d: d["cards"][1].__setitem__("mood", "calm"),
             "card 52: field mood is not one the kit's schema names"),
            ("writer marker", lambda d: d["cards"][2]["options"][0].__setitem__("plan", "@@WRITE | was: x"),
             "card 53: a writer marker (@@WRITE) is still in it"),
            ("newer stamp", lambda d: d["cards"][2].__setitem__("format", "decision-card/6"),
             "card 53: in a newer format (decision-card/6): never downgraded"),
        ]
        for name, put, want in cases:
            with self.subTest(case=name):
                d = load(KIT)
                put(d)
                code, out, res, _, _ = upgrade(d)
                self.assertEqual(code, 1, out)
                self.assertIn(want, out)
                self.assertIn("nothing written", out)
                self.assertIsNone(res)
        # no question for a card
        q = dict(QMAP)
        del q["53"]
        code, out, res, _, _ = upgrade(load(KIT), qmap=q)
        self.assertEqual(code, 1, out)
        self.assertIn("card 53: no q: give its question in --questions", out)
        self.assertIsNone(res)

    def test_only_upgrades_the_set(self):
        d = load(KIT)
        d["cards"][2]["mood"] = "calm"  # outside the set: never checked
        code, out, res, _, _ = upgrade(d, args=("--only", [51, 52]))
        self.assertEqual(code, 0, out)
        self.assertEqual([c["n"] for c in res["cards"]], [51, 52])
        # a number in the set that is not in the file is a problem
        code, out, res, _, _ = upgrade(load(KIT), args=("--only", [51, 99]))
        self.assertEqual(code, 1, out)
        self.assertIn("card 99: in the set, not in", out)

    def test_records(self):
        code, out, res, recs, _ = upgrade(load(LEGACY), args=("--records", "RECORDS"))
        self.assertEqual(code, 0, out)
        self.assertEqual(sorted(recs), ["41.json", "42.json", "43.json"])
        for name, r in recs.items():
            self.assertNotIn("L", r, name)
            self.assertNotIn("dep", r, name)
            self.assertEqual(r["format"], "decision-card/5")
            if name == "42.json":
                self.assertEqual(run_record(r)[0], 1, name)
                self.assertIn("record 42" + SET_REFUSAL, run_record(r)[1])
            self.assertEqual(unassumed(*run_record(with_items(r))), (0, ""), name)
        self.assertEqual(by_n(res)[42]["dep"], "[[41]] (b)")

    def test_a_v5_file_passes_through(self):
        _, _, _, _, raw = upgrade(load(LEGACY))
        code, out, res, _, raw2 = upgrade(raw)
        self.assertEqual(code, 0, out)
        self.assertIn("already decision-page/5", out)
        self.assertEqual(raw2, raw)

    def test_a_bad_or_duplicate_n_is_refused_and_nothing_is_written_anywhere(self):
        # n names the record file: "../../escaped" must never reach a path, and a duplicate never overwrite one
        d = load(KIT)
        d["cards"][0]["n"] = "../../escaped"
        d["cards"][2]["n"] = 52
        with tempfile.TemporaryDirectory() as tmp:
            t = pathlib.Path(tmp)
            work = t / "a" / "b"
            work.mkdir(parents=True)
            (work / "in.json").write_text(json.dumps(d))
            (work / "q.json").write_text(json.dumps(QMAP))
            out = subprocess.run([NODE, str(UPGRADER), str(work / "in.json"), str(work / "out.json"),
                                  "--questions", str(work / "q.json"), "--records", str(work / "recs")],
                                 capture_output=True, text=True, timeout=60)
            files = sorted(str(p.relative_to(t)) for p in t.rglob("*") if p.is_file())
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn('card "../../escaped": n must be a whole number of 1 or more', out.stdout)
        self.assertIn("card 52: number used twice", out.stdout)
        self.assertIn("nothing written", out.stdout)
        self.assertEqual(files, ["a/b/in.json", "a/b/q.json"])
        for n in (0, -1, 2.5, True):
            d = load(KIT)
            d["cards"][0]["n"] = n
            code, out, res, _, _ = upgrade(d)
            self.assertEqual(code, 1, (n, out))
            self.assertIsNone(res)

    def test_a_bad_option_letter_is_a_listed_problem(self):
        for k in ("a)(", "", "ab", "A"):
            with self.subTest(letter=k):
                d = load(LEGACY)
                d["cards"][0]["o"][0][0] = k
                d["cards"][0]["blocks"].pop("a")
                code, out, res, _, _ = upgrade(d)
                self.assertEqual(code, 1, out)
                self.assertIn("card 41: an option letter %s is not one letter a-z" % json.dumps(k), out)
                self.assertIsNone(res)
        d = load(KIT)
        d["cards"][0]["options"][0]["k"] = "a("
        code, out, _, _, _ = upgrade(d)
        self.assertEqual(code, 1, out)
        self.assertIn('card 51: an option letter "a(" is not one letter a-z', out)

    def test_a_v5_file_honours_only_and_records(self):
        _, _, _, _, raw = upgrade(load(LEGACY))
        code, out, res, recs, raw2 = upgrade(raw, args=("--only", [41, 43], "--records", "RECORDS"))
        self.assertEqual(code, 0, out)
        self.assertEqual([c["n"] for c in res["cards"]], [41, 43])
        self.assertEqual(res["format"], "decision-page/5")
        self.assertEqual(sorted(recs), ["41.json", "43.json"])
        for r in recs.values():
            self.assertNotIn("L", r)
        self.assertEqual(by_n(res)[41], by_n(json.loads(raw))[41])
        # --records alone: OUT stays byte for byte, every record written
        code, out, _, recs, raw3 = upgrade(raw, args=("--records", "RECORDS"))
        self.assertEqual(code, 0, out)
        self.assertEqual(raw3, raw)
        self.assertEqual(sorted(recs), ["41.json", "42.json", "43.json"])
        # an unstamped card in a stamped file is refused
        bad = json.loads(raw)
        del bad["cards"][1]["format"]
        code, out, res, _, _ = upgrade(bad)
        self.assertEqual(code, 1, out)
        self.assertIn("card 42: not stamped decision-card/5 in a decision-page/5 file", out)

    def test_a_likelihood_with_no_basis(self):
        d = load(KIT)
        del d["cards"][2]["likelihood"]["basis"]
        res = by_n(upgrade(d)[2])
        self.assertEqual(res[53]["likelihood"], {"kind": "evidence", "seen": d["cards"][2]["likelihood"]["text"]})
        self.assertNotIn("undefined", json.dumps(res[53]))

    def test_a_link_to_a_dropped_evidence_id_is_refused(self):
        d = load(KIT)
        d["cards"][0]["context"] += " See [[att:health|the health report]]."
        code, out, res, _, _ = upgrade(d)
        self.assertEqual(code, 1, out)
        self.assertIn('card 51: a link names evidence attachment "health"', out)

    def test_the_evidence_link_refusal_matches_the_id_exactly(self):
        # ids health and healthcheck: a link to healthcheck never refuses the dropped health
        for link, refused in (("[[att:healthcheck|the check]]", False), ("[[att:health|the report]]", True),
                              ("[[att:health]]", True), ("[[att:healthy|x]]", False)):
            with self.subTest(link=link):
                d = load(KIT)
                d["cards"][0]["context"] += " See " + link + "."
                code, out, _, _, _ = upgrade(d)
                self.assertEqual(code, 1 if refused else 0, out)
                self.assertEqual('a link names evidence attachment "health"' in out, refused, out)

    def test_a_kit_option_with_no_text_is_a_listed_problem(self):
        for v in (None, "", "  "):
            with self.subTest(text=v):
                d = load(KIT)
                if v is None:
                    del d["cards"][0]["options"][1]["text"]
                else:
                    d["cards"][0]["options"][1]["text"] = v
                code, out, res, _, _ = upgrade(d)
                self.assertEqual(code, 1, out)
                self.assertIn("card 51: (b) has no text", out)
                self.assertIsNone(res)

    def test_an_attachment_key_named_proto_stays_a_plain_key(self):
        raw = KIT.read_text().replace('"mode": "invented to illustrate"',
                                      '"mode": "invented to illustrate", "__proto__": {"polluted": true}')
        self.assertNotEqual(raw, KIT.read_text())
        code, out, res, _, _ = upgrade(raw)
        self.assertEqual(code, 0, out)
        att = by_n(res)[51]["attached"][0]
        self.assertEqual(att.get("__proto__"), {"polluted": True})
        self.assertNotIn("polluted", att)
        # mutant: an Object.assign copy turns the key into a prototype, and it is lost
        js = UPGRADER.read_text()
        self.assertEqual(js.count(PROTO_SAFE), 1)
        with tempfile.TemporaryDirectory() as tmp:
            m = pathlib.Path(tmp) / "upgrade_cards.js"
            m.write_text(js.replace(PROTO_SAFE, "const y = Object.assign({}, x);"))
            att = by_n(upgrade(raw, script=m)[2])[51]["attached"][0]
        self.assertNotIn("__proto__", att)

    def test_writes_make_out_dir_and_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = pathlib.Path(tmp)
            (t / "in.json").write_text(KIT.read_text())
            (t / "q.json").write_text(json.dumps(QMAP))
            base = [NODE, str(UPGRADER), str(t / "in.json")]
            # OUT in a directory that does not exist yet
            out = subprocess.run(base + [str(t / "new" / "deeper" / "out.json"), "--questions", str(t / "q.json")],
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(out.returncode, 0, out.stdout)
            self.assertEqual(load(t / "new" / "deeper" / "out.json")["format"], "decision-page/5")
            # a record file that exists is named before it is replaced; a directory at DIR/52.json fails the write
            recs = t / "recs"
            (recs / "52.json").mkdir(parents=True)
            (recs / "51.json").write_text("old")
            out = subprocess.run(base + [str(t / "out.json"), "--questions", str(t / "q.json"), "--records", str(recs)],
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(out.returncode, 2, out.stdout)
            self.assertIn("note: %s exists and will be replaced" % (recs / "51.json"), out.stdout)
            self.assertIn("upgrade_cards: cannot write %s:" % (recs / "52.json"), out.stdout)
            self.assertNotIn("    at ", out.stdout + out.stderr)
            # OUT was written whole, first; no temp file is left behind
            self.assertEqual(load(t / "out.json")["format"], "decision-page/5")
            self.assertEqual([p.name for p in t.rglob(".*tmp-*")], [])
            self.assertTrue((recs / "52.json").is_dir())

    def test_a_file_it_cannot_place_is_refused(self):
        code, out, res, _, _ = upgrade({"cards": [{"n": 1, "t": "x"}]})
        self.assertEqual(code, 1, out)
        self.assertIn("a shape the upgrader cannot place", out)
        code, out, _, _, _ = upgrade("{")
        self.assertEqual(code, 2, out)


if __name__ == "__main__":
    unittest.main()
