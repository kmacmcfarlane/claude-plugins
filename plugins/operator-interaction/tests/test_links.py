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

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest

from test_chat_context import (GALLERY, RENDERING, SKILL_MD, TLDR_OPENER, fenced, lazy_problems,
                               order_problems, parts, views)
from test_impact import DECISIONS

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
        text = GALLERY.read_text().replace("**Group: upload-service review findings**",
                                           "**Group: upload-service review findings (g-1022-a3f)**", 1)
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


if __name__ == "__main__":
    unittest.main()
