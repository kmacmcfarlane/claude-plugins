"""The answer page's card writers: split by group and dependency, one brief, the merge (03ab F4, F5).

A page over `WRITER_CAP` cards goes to several writers. `scripts/split_writers.js` splits its
skeleton: cards that share a layer, and a card and each on-page card its `dep` names, are one
unit, closed transitively; a unit over the cap is cut only between same-layer cards, never along
a depends chain; units and pieces are packed in page order at or under the cap. Each splitter
test runs the real script and a copy of it with one string replaced, which the test must catch
(under node; skipped with a warning without it). `references/writers.md` states the rule, the
cap's basis as an estimate, the *Other decisions* layer, the brief every writer gets (the
digest and one finished example record from the current set, checked first) and the merge
from the stored records. The runner's id lint learns the stored group id's shape. The text
checks each run on the real file and on a copy with the phrase deleted.

Page-only: chat has one writer, and a lone chat decision has no heading.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, example
from test_context import RUNNER, SKILL, runner
from test_items import mutant_runner

SPLIT = SKILL / "scripts" / "split_writers.js"
WRITERS = SKILL / "references" / "writers.md"
DIGEST = SKILL / "references" / "writer-digest.md"
SCHEMA = SKILL / "references" / "cards-schema.md"
SKILL_MD = SKILL / "SKILL.md"

FIND = "while (parent.get(x) !== x) x = parent.get(x); return x;"


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the writer split tests (Split) and the group id lint "
              "(GroupIdLint) are skipped, so split_writers.js and the runner's group id went untested",
              file=sys.stderr)


def mutant(old, new):
    """A copy of the splitter with one string replaced, in its own temp directory."""
    js = SPLIT.read_text()
    assert js.count(old) == 1, old
    path = pathlib.Path(tempfile.mkdtemp()) / "split_writers.js"
    path.write_text(js.replace(old, new))
    return path


def split(d, cap=None, script=SPLIT):
    """(exit code, parsed output or None, stdout) for the skeleton d."""
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "skeleton.json"
        p.write_text(d if isinstance(d, str) else json.dumps(d))
        args = [NODE, str(script)] + (["--cap", str(cap)] if cap is not None else []) + [str(p)]
        out = subprocess.run(args, capture_output=True, text=True, timeout=60)
    try:
        parsed = json.loads(out.stdout) if out.returncode == 0 else None
    except ValueError:
        parsed = None
    return out.returncode, parsed, out.stdout + out.stderr


def skeleton(layers, deps=None, refs=None):
    """layers: [(key, [n…]), …] in page order; deps: {n: dep text}."""
    d = {"layers": [[k, k.title()] for k, _ in layers],
         "cards": [{"n": n, "L": k} for k, ns in layers for n in ns]}
    for c in d["cards"]:
        if deps and c["n"] in deps:
            c["dep"] = deps[c["n"]]
    if refs is not None:
        d["refs"] = refs
    return d


def writers_of(out):
    return [w["cards"] for w in out["writers"]]


def holder(out, n):
    return next(i for i, w in enumerate(out["writers"]) if n in w["cards"])


@unittest.skipUnless(NODE, "node is not installed")
class Split(unittest.TestCase):

    def run_ok(self, d, cap=None, script=SPLIT):
        code, out, text = split(d, cap, script)
        self.assertEqual(code, 0, text)
        return out

    def test_the_example_gives_one_writer(self):
        d = example()
        out = self.run_ok(d)
        self.assertEqual(out["cap"], 15)
        self.assertEqual(out["writers"], [{"cards": [41, 42, 43], "layers": ["direction", "details"],
                                           "over_cap": False}])
        self.assertEqual(out["notes"], [])
        # mutant: a cap of 1, which splits it
        out = self.run_ok(d, script=mutant("const WRITER_CAP = 15;", "const WRITER_CAP = 1;"))
        self.assertNotEqual(out["writers"], [{"cards": [41, 42, 43], "layers": ["direction", "details"],
                                              "over_cap": False}])

    def test_two_layers_of_ten_give_one_writer_each(self):
        d = skeleton([("a", list(range(1, 11))), ("b", list(range(11, 21)))])
        out = self.run_ok(d)
        self.assertEqual(writers_of(out), [list(range(1, 11)), list(range(11, 21))])
        self.assertEqual([w["layers"] for w in out["writers"]], [["a"], ["b"]])
        # mutant: the same-layer link removed, which packs fifteen cards and cuts layer b
        out = self.run_ok(d, script=mutant("else union(unit, first.get(c.L), c.n);", "else {}"))
        self.assertNotEqual(writers_of(out), [list(range(1, 11)), list(range(11, 21))])

    def test_a_dep_across_layers_merges_them(self):
        # a (5) b (8) c (5): unlinked, a and b share a writer; card 14 in c depends on card 1 in a
        d = skeleton([("a", [1, 2, 3, 4, 5]), ("b", list(range(6, 14))), ("c", list(range(14, 19)))],
                     {14: "only if [[1]] is (a)"})
        out = self.run_ok(d)
        self.assertEqual(holder(out, 1), holder(out, 14))
        self.assertEqual(writers_of(out), [[1, 2, 3, 4, 5, 14, 15, 16, 17, 18], list(range(6, 14))])
        # mutant: the dep link removed
        out = self.run_ok(d, script=mutant("if (pos.has(m)) links.push([c.n, m]);", "if (pos.has(m)) {}"))
        self.assertNotEqual(holder(out, 1), holder(out, 14))

    def abc(self):
        # A = 1 (L1), B = 7 (L2), C = 18 (L3); 1 depends on 7, 7 on 18; one unit of 18 at cap 15
        return skeleton([("l1", list(range(1, 7))), ("l2", list(range(7, 13))), ("l3", list(range(13, 19)))],
                        {1: "only if [[7]] is (a)", 7: "only if [[18]] is (b)"})

    def test_a_chain_across_three_layers_is_closed_transitively(self):
        out = self.run_ok(self.abc(), cap=15)
        self.assertEqual(holder(out, 1), holder(out, 7))
        self.assertEqual(holder(out, 7), holder(out, 18))
        self.assertTrue(all(len(w) <= 15 for w in writers_of(out)))
        # mutant: find without path following (direct links only)
        out = self.run_ok(self.abc(), cap=15, script=mutant(FIND, "return parent.get(x);"))
        self.assertFalse(holder(out, 1) == holder(out, 7) == holder(out, 18), writers_of(out))

    def test_a_layer_over_the_cap_is_cut_but_never_its_chain(self):
        # one layer of 20; 15 depends on 14, 16 on 15, 17 on 16
        d = skeleton([("big", list(range(1, 21)))],
                     {15: "only if [[14]] is (a)", 16: "after [[15]] is answered, whatever its answer",
                      17: "only if [[16]] is (b)"})
        out = self.run_ok(d, cap=15)
        self.assertTrue(all(len(w) <= 15 for w in writers_of(out)))
        self.assertEqual(len({holder(out, n) for n in (14, 15, 16, 17)}), 1)
        self.assertEqual(writers_of(out), [list(range(1, 14)), list(range(14, 21))])
        # mutant: atoms built without dep links, which cuts the chain
        out = self.run_ok(d, cap=15, script=mutant(
            "for (const [a, b] of links) if (inU.has(a) && inU.has(b)) union(atom, a, b);", ""))
        self.assertGreater(len({holder(out, n) for n in (14, 15, 16, 17)}), 1)

    def test_a_chain_over_the_cap_is_one_writer_marked(self):
        deps = {n: "only if [[%d]] is (a)" % (n - 1) for n in range(2, 18)}
        d = skeleton([("chain", list(range(1, 18))), ("rest", [18, 19])], deps)
        out = self.run_ok(d, cap=15)
        self.assertEqual(out["writers"][0], {"cards": list(range(1, 18)), "layers": ["chain"], "over_cap": True})
        self.assertEqual(out["writers"][1:], [{"cards": [18, 19], "layers": ["rest"], "over_cap": False}])
        self.assertIn("over the cap of 15: one writer, marked over cap", " ".join(out["notes"]))
        # mutant: the cap enforced on an atom, which cuts the chain
        out = self.run_ok(d, cap=15, script=mutant(
            "if (it.cards.length > cap) { out.push({cards: it.cards.slice(), over_cap: true}); cur = null; continue; }",
            "if (it.cards.length > cap) { for (let i = 0; i < it.cards.length; i += cap) "
            "out.push({cards: it.cards.slice(i, i + cap), over_cap: false}); cur = null; continue; }"))
        self.assertGreater(len({holder(out, n) for n in range(1, 18)}), 1)

    def test_an_open_target_not_on_the_page_is_reported(self):
        d = skeleton([("a", [1, 2])], {2: "only if [[219]] is (a)"})
        out = self.run_ok(d)
        self.assertEqual(out["notes"], ["card 2 depends on [[219]], which is neither a card on this page "
                                        "nor a ref: add it as a card"])
        self.assertEqual(writers_of(out), [[1, 2]])
        # mutant: the target dropped silently
        out = self.run_ok(d, script=mutant("else if (!refs.has(String(m)))", "else if (false)"))
        self.assertEqual(out["notes"], [])

    def test_a_dep_on_a_ref_is_clean_and_its_unit_unchanged(self):
        d = skeleton([("a", [1, 2]), ("b", [3])], {2: "only if [[38]] is (a)"}, refs={"38": {}})
        out = self.run_ok(d)
        self.assertEqual(out["notes"], [])
        self.assertEqual(writers_of(out), [[1, 2, 3]])
        # mutant: refs dropped from the skeleton, which reports the dependency
        del d["refs"]
        self.assertEqual(len(self.run_ok(d)["notes"]), 1)

    def test_a_malformed_skeleton_exits_1(self):
        for put, needle in ((lambda d: d["cards"][0].pop("n"), "needs n"),
                            (lambda d: d["cards"][0].pop("L"), "needs L"),
                            (lambda d: d["cards"][0].__setitem__("L", "nowhere"), "is not a layers key"),
                            (lambda d: d["cards"][1].__setitem__("n", 1), "n repeated")):
            with self.subTest(needle=needle):
                d = skeleton([("a", [1, 2])])
                put(d)
                code, out, text = split(d)
                self.assertEqual(code, 1, text)
                self.assertIn(needle, text)
                self.assertTrue(text.startswith("split_writers: "), text)
        code, _, text = split("{not json")
        self.assertEqual(code, 1, text)
        code, _, text = split(skeleton([("a", [1])]), cap=0)
        self.assertEqual(code, 1, text)
        # mutant: the layers-key check removed, which reads an unknown L
        d = skeleton([("a", [1, 2])])
        d["cards"][0]["L"] = "nowhere"
        js = mutant('if (!keys.includes(c.L)) fail(', 'if (false) fail(')
        self.assertNotEqual(split(d, script=js)[0], 1)

    def test_other_decisions_is_the_last_layer(self):
        d = skeleton([("g-1022-a3f", [1, 2]), ("other", [3])])
        d["layers"][1] = ["other", "Other decisions", "not grouped with another decision; each stands alone"]
        self.assertEqual(split(d)[0], 0)
        # mutant: other placed first, which is refused
        d["layers"].reverse()
        code, _, text = split(d)
        self.assertEqual(code, 1, text)
        self.assertIn("layer other (Other decisions) must be the last layer", text)
        # mutant of the script: the check removed
        js = mutant("if (at >= 0 && at !== keys.length - 1) fail(", "if (false) fail(")
        self.assertEqual(split(d, script=js)[0], 0)

    def test_the_cap_matches_writers_md(self):
        self.assertEqual(cap_problems(SPLIT.read_text(), WRITERS.read_text()), [])
        js = SPLIT.read_text().replace("const WRITER_CAP = 15;", "const WRITER_CAP = 16;")
        self.assertNotEqual(cap_problems(js, WRITERS.read_text()), [])


def cap_problems(js, md):
    a = re.search(r"const WRITER_CAP = (\d+);", js)
    b = re.search(r"`WRITER_CAP = (\d+)` cards per writer", md)
    if not a or not b:
        return ["the cap is not stated in both"]
    return [] if a.group(1) == b.group(1) else [f"script {a.group(1)}, writers.md {b.group(1)}"]


def flat(text):
    return " ".join(text.split())


def section(text, heading):
    start = text.find("\n## " + heading + "\n")
    if start < 0:
        return ""
    end = text.find("\n## ", start + 1)
    return flat(text[start:end if end > 0 else len(text)])


SPLIT_PHRASES = (
    "the layer's key is the group id, its title the group's plain name, never the id",
    "each keyed by its name case-folded, with whitespace collapsed and spaces turned to hyphens",
    "**Cards in no group** go in one last layer: key `other`, title *Other decisions*",
    "It is the page's alone: chat shows a lone decision with no heading.",
    "A decision a card depends on that is not on the page goes in `refs` when it is answered; "
    "an open one is added to the page as a card",
    "node scripts/split_writers.js [--cap N] skeleton.json",
    "A depends chain is never cut; only same-layer links are.",
    "Each writer takes the next whole one while the total stays at or under the cap",
    "It is an estimate from one observation, not a measurement: 22 cards came to about 27k "
    "tokens of card text",
    "the caller records each writer's cards, tokens and first-check lints",
)
BRIEF_PHRASES = (
    "the same digest and the same finished example card",
    "as a `decision-card/5` record",
    "`node scripts/check_cards.js --record <file>`",
    "before the other writers start",
    "That card, from the current set, is the example.",
    "the writer digest (`references/writer-digest.md`, pasted or by path)",
    "\"match its voice, density and level shapes; do not copy its facts\"",
    "the page's whole `layers` list and every card's `n` and `t`",
    "Writer 1 keeps the example card, unchanged unless the merged check names it.",
    "With one writer there is no example stage, and the brief is the digest alone.",
)
MERGE_PHRASES = (
    "**A writer returns records**",
    "checked with `node scripts/check_cards.js --record <file>` before it is handed back",
    "A writer never writes `L`, `dep` or `refs`",
    "**The caller builds `cards.json` from the records it has stored**, not from the writers' files",
    "its stored record plus its `L` and `dep`, then the page's `refs`",
    "**One check over the whole file**",
)


def writers_problems(text):
    out = []
    for heading, phrases in (("The split", SPLIT_PHRASES), ("The brief", BRIEF_PHRASES),
                             ("The merge", MERGE_PHRASES)):
        body = section(text, heading)
        out += [f"§ {heading} lacks {p!r}" for p in phrases if p not in body]
    # store-agnostic: no work item and no other plugin's script
    if "item_spend" in text:
        out.append("writers.md names item_spend")
    if re.search(r"\b[a-z0-9]+(?:-[a-z0-9]+){2,}-[0-9a-f]{4}\b|\b03ab\b", text):
        out.append("writers.md names a work item")
    return out


def pointer_problems(skill, digest, schema):
    out = []
    step = skill[skill.find("## Step 2"):skill.find("## Step 3")]
    if "`references/writers.md`" not in step:
        out.append("SKILL.md step 2 does not point at references/writers.md")
    for name, text in (("digest", digest), ("schema", schema)):
        rows = [x for x in text.splitlines() if x.startswith("| `L` |")]
        if len(rows) != 1 or "stored group" not in rows[0] or "`other`" not in rows[0] \
                or "*Other decisions*" not in rows[0]:
            out.append(f"the {name}'s L row names no stored group or Other decisions")
    rows = [x for x in digest.splitlines() if x.startswith("| `dep` |")]
    if len(rows) != 1 or "from the caller's stored dependency" not in rows[0]:
        out.append("the digest's dep row names no stored dependency")
    return out


class WritersText(unittest.TestCase):

    def test_writers_md(self):
        self.assertEqual(writers_problems(WRITERS.read_text()), [])

    def test_each_phrase_is_load_bearing(self):
        text = WRITERS.read_text()
        for p in SPLIT_PHRASES + BRIEF_PHRASES + MERGE_PHRASES:
            pattern = r"\s+".join(re.escape(w) for w in p.split())
            cut, n = re.subn(pattern, "gone", text)
            self.assertGreaterEqual(n, 1, p)
            self.assertNotEqual(writers_problems(cut), [], p)

    def test_no_work_item_and_no_item_spend(self):
        text = WRITERS.read_text()
        # the other plugin's script name is built, so this test holds no reference to it
        for insert in ("Tokens come from the " + "item" + "_spend script.",
                       "Recorded on decisions-structured-depends-and-group-l-03ab.",
                       "Recorded on 03ab."):
            with self.subTest(insert=insert):
                self.assertNotEqual(writers_problems(text + "\n" + insert + "\n"), [])

    def test_the_pointers(self):
        skill, digest, schema = SKILL_MD.read_text(), DIGEST.read_text(), SCHEMA.read_text()
        self.assertEqual(pointer_problems(skill, digest, schema), [])
        # mutants: each pointer deleted
        step = skill[skill.find("## Step 2"):skill.find("## Step 3")]
        self.assertNotEqual(pointer_problems(skill.replace(step, step.replace("`references/writers.md`", "it")),
                                             digest, schema), [])
        for old in ("stored group", "*Other decisions*"):
            self.assertNotEqual(pointer_problems(skill, digest.replace(old, "x"), schema), [], old)
            self.assertNotEqual(pointer_problems(skill, digest, schema.replace(old, "x")), [], old)
        self.assertNotEqual(pointer_problems(skill, digest.replace("from the caller's stored dependency", "x"),
                                             schema), [])


@unittest.skipUnless(NODE, "node is not installed")
class GroupIdLint(unittest.TestCase):
    """A stored group id is store-internal: in a layer title or a card's text it is an id."""

    def lines(self, d, script=RUNNER):
        code, out, err = runner(d, script=script)
        self.assertNotEqual(code, 1, out + err)
        return [x for x in out.splitlines() if "g-1022-a3f" in x]

    def test_a_group_id_on_the_page_lints(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        d = example()
        d["layers"][0][1] = "decision cards (g-1022-a3f)"
        page = self.lines(d)
        self.assertTrue(page and all(x.startswith("lint: page: ") for x in page), page)
        d = example()
        d["cards"][0]["context"] = d["cards"][0]["context"][:-1] + ", in group g-1022-a3f."
        card = self.lines(d)
        self.assertTrue(card and card[0].startswith("lint: card 41: g-1022-a3f looks like an id"), card)
        # mutant: the group id alternative removed from ID_TOKEN
        js = mutant_runner("|\\bg-[0-9]{4}-[0-9a-f]{3}\\b/g;", "/g;")
        d = example()
        d["layers"][0][1] = "decision cards (g-1022-a3f)"
        self.assertEqual(self.lines(d, js), [])

    def test_a_group_id_as_a_layer_key_is_clean(self):
        d = example()
        old = d["layers"][0][0]
        d["layers"][0][0] = "g-1022-a3f"
        for c in d["cards"]:
            if c["L"] == old:
                c["L"] = "g-1022-a3f"
        self.assertEqual(runner(d)[:2], (0, ""))


if __name__ == "__main__":
    unittest.main()
