"""Stored groups and dependencies on the chat surface (03ab F3), each check proved by a mutation.

The decisions skill reads the group and the dependency its caller stores (a librarian's group
lines and `depends N:` lines). A stored group is the group, by its plain name; its id is never
shown. A decision that waits on another's answer carries one dependency line, second on its
card and block, after the TLDR (answer 336 (a)) and before Context, the title line left bare
(the v4 layout, answer 313):

    *depends: only if 41 (name) is (a) or (c), and after 47 (name) is answered, whatever its answer*

Checked here: the line's form (`DEP_LINE`) on the template's example and the gallery's
dependent card, its place, the number it names being a card in the same gallery section, a
blank line keeping it out of the TLDR bullet above it; the SKILL.md clauses; no group id in
the chat references; the plain-names sentence; no Dependencies fold left in the skills' text;
the rulings bullet. The page's line is `test_layout.py`'s `DependencyLine`.

The dependency-tree order (03ab F7, answer 307 (a)): inside a group, each decision after what
it depends on, then the precedence. Checked here: the SKILL.md rule, the rendering § Order note
and its open-target sentence, the rulings bullet, the gallery's worked order (example 38), and
the runner's `deporder` lint on the example and on fixtures, each proved by a mutation.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest

from test_chat_context import (GALLERY, RENDERING, SKILL_MD, TLDR_OPENER, fenced, lazy_problems,
                               order_problems, parts, views)
from test_impact import DECISIONS, NODE, example
from test_context import runner
from test_items import mutant_runner

PLUGIN = DECISIONS.parent.parent
RULINGS = DECISIONS / "references" / "rulings.md"
PLAIN_NAMES = PLUGIN / "skills" / "plain-names" / "SKILL.md"
PAGE_SKILL = PLUGIN / "skills" / "decision-page"

# one target group: only if M (name) is (x), its letters alternatives; or after M (name) is answered
_ONE = (r"(only if \d+ \(.+?\) is \([a-y]\)((,? or|,) \([a-y]\))*"
        r"|after \d+ \(.+?\) is answered, whatever its answer)")
DEP_LINE = re.compile(r"^\*depends: " + _ONE + r"(, and " + _ONE + r")*\*$")
DEP_NUMS = re.compile(r"(?:only if|after) (\d+) \(")
GROUP_ID = re.compile(r"\bg-\d{4}-[0-9a-f]{3}\b|\bGRP\d+\b")


def dep_lines(lines):
    return [x for x in lines if x.startswith("*depends:")]


def template_example(text=None):
    card = fenced(text if text is not None else RENDERING.read_text(), TLDR_OPENER)
    got = dep_lines(card)
    return got[0] if len(got) == 1 else None


def sections(text):
    """The gallery's sections: (heading, lines)."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = (line, [])
            out.append(cur)
        elif cur:
            cur[1].append(line)
    return out


def gallery_problems(text):
    """Every dependent card and block in the gallery: its line in form, second (after the TLDR),
    and every number it names a card in the same section. Empty when clean; at least one
    dependent card must exist."""
    out, seen = [], 0
    for head, lines in sections(text):
        cards = {m.group(1) for x in lines for m in [re.match(r"^\*\*(\d+) — ", x)] if m}
        for i, x in enumerate(lines):
            if not x.startswith("*depends:"):
                continue
            seen += 1
            if not DEP_LINE.match(x):
                out.append(f"{head}: a dependency line off its form: {x[:60]!r}")
            for n in DEP_NUMS.findall(x):
                if n not in cards:
                    out.append(f"{head}: the dependency line names {n}, no card in its section")
    for n, kind, body in views_of(text):
        ps = parts(body)
        if "depends" in ps:
            i = ps.index("depends")
            if ps[i - 1] != "TLDR" or any(p not in ("title", "TLDR") for p in ps[:i]):
                out.append(f"view at line {n}: the dependency line is not second, after the TLDR: {ps}")
            out.extend(order_problems(f"view at line {n}", body))
            out.extend(lazy_problems(f"view at line {n}", body))
    if not seen:
        out.append("no dependent card in the gallery")
    return out


def views_of(text):
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "g.md"
        p.write_text(text)
        return views(p)


def flat(path):
    return " ".join(path.read_text().split())


def missing(text, clauses):
    """The clauses a file's text lacks, read with its whitespace collapsed; empty when it holds them all."""
    f = " ".join(text.split())
    return [c for c in clauses if c not in f]


SKILL_CLAUSES = (
    "says so on its dependency line, second on its card, read from the caller's stored dependency",
    "its dependency line, `*depends: only if 41 (name) is (a) or (c), and after 47 (name) is answered, whatever its answer*`",
    "A group the caller stores is the group, and related decisions are the rule only where it stores none",
    "its id never shown")
RENDERING_CLAUSES = (
    "**A group the caller stores is the group**", "`{id, name, shares, context}`",
    "A stored group with `shares` and `context` is a bundle and takes the heading; one without them is kept together under no heading",
    "The group's id is store-internal and never shown",
    "the groups are the ones the caller stores where it stores them",
    "`<repo>'s M (name)` where the caller knows its name, else `<repo>'s decision M`",
    "a bold head, a fold line or the dependency line that follows it")
PLAIN_CLAUSES = ("Its id (`g-1022-a3f`) is store-internal and never shown to the operator",)
RULING_CLAUSES = (
    "answer 313", "answer 336 (a)", "never shown on either surface", "second on the card, after the TLDR",
    "the Dependencies fold is gone",
    "Not taken: groups worked out at render time from the item and dependencies in prose only")


def ruling_bullet(text):
    start = text.find("- **Groups and dependencies, stored; writers by group** (2026-10-21")
    if start < 0:
        return ""
    end = text.find("\n- **", start + 1)
    return text[start:end if end > 0 else len(text)]


class DependencyLineForm(unittest.TestCase):

    FIXTURES = [
        "*depends: only if 41 (vendor the font) is (a)*",
        "*depends: only if 41 (vendor the font) is (a) or (c)*",
        "*depends: only if 41 (vendor the font) is (a), (b), or (c), and after 47 (the font licence) is answered, whatever its answer*",
    ]

    def test_the_regex_takes_the_three_letter_forms_and_refuses_and(self):
        for f in self.FIXTURES:
            self.assertTrue(DEP_LINE.match(f), f)
        self.assertFalse(DEP_LINE.match("*depends: only if 41 (vendor the font) is (a) and (c)*"))
        # mutant: the letters narrowed back to ( or (x))*, which refuses the three-letter fixture
        narrow = re.compile(DEP_LINE.pattern.replace(r"((,? or|,) \([a-y]\))*", r"( or \([a-y]\))*"))
        self.assertFalse(narrow.match(self.FIXTURES[2]))

    def test_the_card_template_shows_the_line_second_and_the_openers_stay(self):
        text = RENDERING.read_text()
        line = template_example(text)
        self.assertIsNotNone(line)
        self.assertTrue(DEP_LINE.match(line), line)
        self.assertIn(" or (c)", line)
        # mutants: or replaced by and (the form fails); the line moved onto the title line (the opener's
        # fenced block is no longer found)
        self.assertFalse(DEP_LINE.match(line.replace(" or (c)", " and (c)")))
        moved = text.replace("**N — Title as a question?**\n- the TLDR",
                             "**N — Title as a question?** — " + line + "\n- the TLDR", 1)
        with self.assertRaises(AssertionError):
            fenced(moved, TLDR_OPENER)

    def test_the_rendering_bullet_names_its_source_and_its_forms(self):
        f = flat(RENDERING)
        for s in ("**Dependency line:**", "read from the caller's stored dependency", "`depends N:`",
                  "{n, repo, letter}", "*is (a) or (c)*", "*after M (name) is answered, whatever its answer*",
                  "joined by *, and*", "the title line stays bare", "never *depends: none*"):
            self.assertIn(s, f, s)

    def test_a_blank_line_keeps_the_line_out_of_the_tldr(self):
        body = ["**82 — Q?**", "- a TLDR bullet", "*depends: only if 81 (x) is (a)*", "**Context:** c · d"]
        self.assertTrue(lazy_problems("x", body))
        self.assertEqual(lazy_problems("x", body[:2] + [""] + body[2:]), [])


class GalleryDependentCard(unittest.TestCase):

    def test_the_gallery_has_a_dependent_card_in_form(self):
        self.assertEqual(gallery_problems(GALLERY.read_text()), [])

    def test_mutant_the_number_not_in_the_section_is_caught(self):
        text = GALLERY.read_text().replace("*depends: only if 81 (", "*depends: only if 99 (", 1)
        self.assertTrue(any("names 99" in p for p in gallery_problems(text)), gallery_problems(text))

    def test_mutant_the_line_under_context_is_caught(self):
        text = GALLERY.read_text()
        line = next(x for x in text.splitlines() if x.startswith("*depends:"))
        ctx = text[text.index(line) + len(line) + 1:].split("\n", 1)[0]
        moved = text.replace(line + "\n" + ctx, ctx + "\n" + line, 1)
        self.assertTrue(gallery_problems(moved), "moved under Context")

    def test_mutant_the_line_above_the_tldr_is_caught(self):
        text = GALLERY.read_text()
        line = next(x for x in text.splitlines() if x.startswith("*depends:"))
        lines = text.splitlines()
        i = lines.index(line)
        t = max(j for j in range(i) if re.match(r"^\*\*\d+ — ", lines[j]))
        moved = lines[:t + 1] + [line] + [x for x in lines[t + 1:i]] + lines[i + 1:]
        self.assertTrue(gallery_problems("\n".join(moved)), "moved above the TLDR")

    def test_mutant_or_for_and_is_caught(self):
        text = GALLERY.read_text().replace("is (a)*\n**Context:** the sort column", "is (a) and (b)*\n**Context:** the sort column", 1)
        self.assertNotEqual(text, GALLERY.read_text())
        self.assertTrue(any("off its form" in p for p in gallery_problems(text)))


class StoredGroupsAndText(unittest.TestCase):

    def test_skill_md_names_the_line_and_the_stored_group(self):
        text = SKILL_MD.read_text()
        self.assertEqual(missing(text, SKILL_CLAUSES), [])
        # mutants: each clause's opening words reworded in the file's text, and the check re-run
        for c in SKILL_CLAUSES:
            mutated = " ".join(text.split()).replace(c, "X" + c[1:])
            self.assertEqual(missing(mutated, SKILL_CLAUSES), [c], c)

    def test_rendering_reads_the_stored_group(self):
        text = RENDERING.read_text()
        self.assertEqual(missing(text, RENDERING_CLAUSES), [])
        for c in RENDERING_CLAUSES:
            mutated = " ".join(text.split()).replace(c, "X" + c[1:])
            self.assertIn(c, missing(mutated, RENDERING_CLAUSES), c)

    def test_no_group_id_in_the_chat_references(self):
        def found(text):
            out, fence = [], False
            for line in text.splitlines():
                if line.startswith("```"):
                    fence = not fence
                    continue
                if not fence and GROUP_ID.search(line):
                    out.append(line)
            return out
        for p in (GALLERY, RENDERING, SKILL_MD):
            self.assertEqual(found(p.read_text()), [], p.name)
        # mutant: a group id on a group heading
        text = GALLERY.read_text().replace("**Group: upload-service review findings · 51–53**",
                                           "**Group: upload-service review findings · 51–53 (g-1022-a3f)**", 1)
        self.assertTrue(found(text))

    def test_plain_names_says_a_group_id_is_never_shown(self):
        text = PLAIN_NAMES.read_text()
        self.assertEqual(missing(text, PLAIN_CLAUSES), [])
        # mutant: the sentence's bullet deleted from the file's text
        start = text.index("- **A group of decisions has no tag.**")
        end = text.index("\n- **", start + 1)
        self.assertEqual(missing(text[:start] + text[end + 1:], PLAIN_CLAUSES), list(PLAIN_CLAUSES))

    def test_no_dependencies_fold_left_in_the_skills(self):
        for p in sorted((PLUGIN / "skills").rglob("*.md")) + [PAGE_SKILL / "assets" / "index.html"]:
            if p.name == "rulings.md":
                continue  # the record of what was ruled keeps the old shape's words
            self.assertNotIn("Dependencies fold", flat(p), p)
            self.assertNotIn("Dependencies where there are any", flat(p), p)

    def test_the_rulings_bullet_carries_its_date_and_not_taken(self):
        text = RULINGS.read_text()
        self.assertEqual(missing(ruling_bullet(text), RULING_CLAUSES), [])
        # mutants, in the file's text: its Not taken cut; its date changed (the bullet is then not found)
        cut = text.replace("  Not taken: groups worked out at render time", "  Kept: groups worked out at render time", 1)
        self.assertNotEqual(cut, text)
        self.assertIn(RULING_CLAUSES[-1], missing(ruling_bullet(cut), RULING_CLAUSES))
        undated = text.replace("writers by group** (2026-10-21", "writers by group** (", 1)
        self.assertEqual(missing(ruling_bullet(undated), RULING_CLAUSES), list(RULING_CLAUSES))


# ---- the dependency-tree order (03ab F7) ----

CYCLE = ("the members of a dependency cycle are ordered among themselves by the precedence alone; "
         "their other dependencies still hold")
ORDER_SKILL = ("**Inside a group, dependents come after what they depend on:** each decision goes after every "
               "decision it depends on in the same group, and among those free to go, the same precedence holds.",
               "The members of a dependency cycle (a work-item store's lint flags one) are ordered among themselves "
               "by the precedence alone; their other dependencies still hold.")
ORDER_RENDERING = ("inside a group, each decision goes after every decision it depends on in the same group",
                   "so a deadline or ⚠ dependent still waits for its target", CYCLE,
                   "A set shows every open decision its cards name or depend on, each as its own card or line, "
                   "placed by the dependency order above",
                   "The hover tooltip and the click that opens a named card are the answer page's alone")
ORDER_RULING = ("answer 307 (a)", "sorting by the dep tree makes the most sense to me", "both surfaces",
                "`deporder`", CYCLE, "Not taken: one precedence inside a group whatever the dependencies")
CHAT_SET_RULING = ("A set in chat shows every open decision its cards name or depend on; the hover tooltip and "
                   "the jump to a card are page-only, since chat has no hover or click",)


def section_text(path, heading):
    text = path.read_text()
    start = text.index(heading)
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


def order_ruling(text):
    start = text.find("- **Dependents after what they depend on, both surfaces** (2026-10-22")
    if start < 0:
        return ""
    end = text.find("\n- **", start + 1)
    return text[start:end if end > 0 else len(text)]


def gallery_order_problems(text):
    """Gallery example 38: every "X depends on Y" its prose states has Y's list line before X's.
    Empty when clean; the section must state at least one dependency and list both ends."""
    start = text.find("## 38. Dependents after what they depend on")
    if start < 0:
        return ["no example 38"]
    end = text.find("\n## ", start + 1)
    body = text[start:end if end > 0 else len(text)]
    at = {}
    for line in body.splitlines():
        m = re.match(r"^- \*\*(\d+) ", line)
        if m:
            at.setdefault(m.group(1), len(at))
    pairs = set(re.findall(r"\b(\d+) depends on (\d+)\b", body))
    if not pairs:
        return ["example 38 states no dependency"]
    out = []
    for x, y in sorted(pairs):
        if x not in at or y not in at:
            out.append(f"{x} or {y} has no list line")
        elif at[y] > at[x]:
            out.append(f"{x} is listed before {y}, which it depends on")
    return out


class DependencyOrderText(unittest.TestCase):

    def test_skill_md_states_the_order_inside_a_group(self):
        text = SKILL_MD.read_text()
        self.assertEqual(missing(section_text(SKILL_MD, "## Order"), ORDER_SKILL), [])
        # mutant: the paragraph deleted from the file's text
        start = text.index("**Inside a group, dependents come after")
        end = text.index("\n\n", start)
        self.assertEqual(missing(text[:start] + text[end:], ORDER_SKILL), list(ORDER_SKILL))

    def test_rendering_order_states_the_rule_and_the_open_targets(self):
        body = section_text(RENDERING, "## Order")
        self.assertEqual(missing(body, ORDER_RENDERING), [])
        # mutant: the open-target sentence deleted
        cut = body.replace("A set shows every open decision its cards name or depend on", "", 1)
        self.assertNotEqual(cut, body)
        self.assertEqual(missing(cut, ORDER_RENDERING), [ORDER_RENDERING[-2]])

    def test_the_rulings_bullet_and_the_chat_set_clause(self):
        text = RULINGS.read_text()
        self.assertEqual(missing(order_ruling(text), ORDER_RULING), [])
        self.assertEqual(missing(ruling_bullet(text), CHAT_SET_RULING), [])
        # mutants: the bullet deleted (its heading gone); the chat-set clause cut from its bullet
        gone = text.replace("- **Dependents after what they depend on, both surfaces**", "- **Something else**", 1)
        self.assertEqual(missing(order_ruling(gone), ORDER_RULING), list(ORDER_RULING))
        cut = text.replace("A set in chat shows every open decision", "A set shows", 1)
        self.assertNotEqual(cut, text)
        self.assertEqual(missing(ruling_bullet(cut), CHAT_SET_RULING), list(CHAT_SET_RULING))

    def test_the_gallery_works_an_order_through(self):
        text = GALLERY.read_text()
        self.assertEqual(gallery_order_problems(text), [])
        # mutant: the dependent ⚠ line moved above its target, the order the precedence alone gives
        lines = text.splitlines()
        a = next(i for i, x in enumerate(lines) if x.startswith("- **111 "))
        b = next(i for i, x in enumerate(lines) if x.startswith("- **113 "))
        lines[a], lines[b] = lines[b], lines[a]
        self.assertIn("113 is listed before 111, which it depends on", gallery_order_problems("\n".join(lines)))


def deporder_lines(d, script=None):
    code, out, err = runner(d, script=script) if script else runner(d)
    if code == 1:
        raise AssertionError("refused: " + out + err)
    return [x for x in out.splitlines() if "which comes after it in its group" in x]


def moved(d, n, before):
    """The cards with card n moved to just before card `before`."""
    cs = d["cards"]
    c = next(x for x in cs if x["n"] == n)
    cs.remove(c)
    cs.insert(next(i for i, x in enumerate(cs) if x["n"] == before), c)
    return d


@unittest.skipUnless(NODE, "node is not installed")
class DepOrderLint(unittest.TestCase):

    LINE = "lint: card 43: depends on [[42]], which comes after it in its group; move it after"

    def same_layer(self):
        d = example()
        d["cards"][2]["dep"] = "only if [[42]] is (a)"
        self.assertEqual([c["n"] for c in d["cards"]], [41, 42, 43])
        self.assertEqual(d["cards"][1]["L"], d["cards"][2]["L"])
        return d

    def test_the_example_is_clean(self):
        self.assertEqual(deporder_lines(example()), [])

    def test_a_dependent_before_its_target_in_one_layer_fires(self):
        self.assertEqual(deporder_lines(self.same_layer()), [])
        self.assertEqual(deporder_lines(moved(self.same_layer(), 43, 42)), [self.LINE])
        # mutant: the position test always true, which fires on the right order too
        js = mutant_runner("&& at.get(m) > i &&", "&& true &&")
        self.assertEqual(deporder_lines(self.same_layer(), js), [self.LINE])

    def test_the_same_order_across_two_layers_is_clean(self):
        d = moved(example(), 42, 41)  # 42 depends on 41, which is in another layer
        self.assertEqual(deporder_lines(d), [])
        # mutant: the layer test dropped
        js = mutant_runner("return t.L === c.L && ", "return ")
        self.assertEqual(deporder_lines(moved(example(), 42, 41), js),
                         ["lint: card 42: depends on [[41]], which comes after it in its group; move it after"])

    def test_a_dep_on_a_ref_is_clean(self):
        d = example()
        d["cards"][1]["dep"] = "only if [[38]] is (a)"
        self.assertEqual(deporder_lines(d), [])
        # mutant: a ref read as a later card in the same layer
        js = mutant_runner("const t = d.cards[at.get(m)];\n      return t.L === c.L && at.get(m) > i",
                           "const t = d.cards[at.get(m)] || c;\n      return t.L === c.L && (at.has(m) ? at.get(m) : 1e9) > i")
        js2 = js.read_text().replace("depsOf(c).filter(m => at.has(m))", "depsOf(c)")
        js.write_text(js2)
        self.assertEqual(deporder_lines(d, js),
                         ["lint: card 42: depends on [[38]], which comes after it in its group; move it after"])

    def test_a_cycle_closed_through_the_other_layer_is_clean(self):
        d = example()
        d["cards"][0]["dep"] = "only if [[42]] is (a)"
        d["cards"][1]["dep"] = "only if [[43]] is (a)"
        d["cards"][2]["dep"] = "only if [[41]] is (a)"
        self.assertEqual(deporder_lines(d), [])
        # mutant: only a direct back edge read as a cycle, which misses the cycle through 41 and fires on 42
        js = mutant_runner(" && !reaches(m, me)", " && !(edges.get(m) || []).includes(me)")
        self.assertEqual(deporder_lines(d, js),
                         ["lint: card 42: depends on [[43]], which comes after it in its group; move it after"])

    def test_a_two_card_cycle_in_one_layer_is_clean(self):
        d = example()
        d["cards"][1]["dep"] = "only if [[43]] is (a)"
        d["cards"][2]["dep"] = "only if [[42]] is (b)"
        self.assertEqual(deporder_lines(d), [])
        # mutant: the cycle skip removed, which fires on 42
        js = mutant_runner(" && !reaches(m, me)", "")
        self.assertEqual(deporder_lines(d, js),
                         ["lint: card 42: depends on [[43]], which comes after it in its group; move it after"])


if __name__ == "__main__":
    unittest.main()
