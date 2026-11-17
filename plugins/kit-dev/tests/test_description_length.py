"""Plugin descriptions stay short (CLAUDE.md § Conventions, Plugin descriptions).

The plugin menu shows a plugin's whole description, and a long one overflows it (observed by
the operator on 2026-11-17, when one description ran to 3610 characters). For every
plugins/*/.claude-plugin/plugin.json and every .claude-plugin/marketplace.json entry:

- the summary, the text before the first " (", is at most SUMMARY_MAX characters;
- the whole description is at most TOTAL_MAX characters;
- the plugin.json description and the marketplace.json entry's are identical;
- the dependency clause holds names only: each entry, its kind head stripped, is a bare
  name (KIND_HEAD, NAME_ENTRY, MULTIWORD), never how-it-degrades prose, and the clause
  closes the description (CLAUSE_TAIL).

Each check is a plain function returning a list of problems, and each is proved by a mutant:
a deliberately bad description fed to it must fail. The mutants run anywhere; the scan of
the real files runs only in the source repo (it reads every plugin and marketplace.json) and
skips in an isolated copy of kit-dev. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
IN_REPO = MARKETPLACE.is_file() and (REPO / "plugins").is_dir()

# The rule asks for about 100; the cap leaves room for a summary a little over that (the
# longest today is 117), so the test fails a drift, not a carefully written sentence.
SUMMARY_MAX = 120

# The longest description today is dev-flow's, 414 characters: a summary, eleven agent
# names (which test_agents.py requires in it), nine soft dependency names and one
# external. 420 leaves room for a few characters of rewording but not another name, so
# the next growth past that is a prompt to trim, not a silent overflow; every other
# description sits under 270.
TOTAL_MAX = 420

# The dependency clause opens at the first parenthesis whose text starts with one of these
# words, in any case, exactly as test_declared_edges.py finds it.
CLAUSE_OPEN = re.compile(r"\((?=\s*(?:soft|requires|external|optional|hard)\b)", re.I)

# Names only, held by shape rather than by a list of banned phrases: the clause is split
# on ';', each entry loses its kind head, and what is left must be a bare one-word name
# (letters, digits, '.', '-': `node`, `claude-sandbox`) or a name in MULTIWORD. Anything
# else, a comma clause, two words such as "plan file" or a sentence such as "without it
# nothing is filed", is how-it-degrades prose, which belongs in the README catalog cell and
# the skill text. A kind such as optional goes in the head (`external, optional:`), never
# after the name. The clause ends the description: only its ')' and an optional '.'
# follow it, so no prose can trail in a second parenthesis.
KIND_HEAD = re.compile(
    r"^(?:soft:|requires\b|agents:|external(?:,\s*(?:soft|required|optional))?:)\s*")
NAME_ENTRY = re.compile(r"^[A-Za-z0-9.\-]+$")
# Real names of more than one word, each added by hand.
MULTIWORD = {"claude.ai Artifacts"}
CLAUSE_TAIL = re.compile(r"^\)\.?$")


def summary(desc):
    """The summary sentence: the text before the first ' ('."""
    return desc.split(" (", 1)[0]


def dependency_clause(desc):
    """(the clause's text inside its parentheses, the text from its ')' to the end);
    ('', '') when it has none, and the tail '' when it never closes."""
    m = CLAUSE_OPEN.search(desc)
    if not m:
        return "", ""
    body = desc[m.end():]
    end = body.find(")")
    return (body[:end], body[end:]) if end >= 0 else (body, "")


def check_summary(desc):
    n = len(summary(desc))
    return [f"summary is {n} chars, over {SUMMARY_MAX}"] if n > SUMMARY_MAX else []


def check_total(desc):
    n = len(desc)
    return [f"description is {n} chars, over {TOTAL_MAX}"] if n > TOTAL_MAX else []


def check_identical(plugin_desc, market_desc):
    if plugin_desc != market_desc:
        return ["plugin.json and marketplace.json descriptions differ"]
    return []


def check_names_only(desc):
    clause, tail = dependency_clause(desc)
    if not clause:
        return []
    problems = []
    if not CLAUSE_TAIL.match(tail):
        problems.append(f"text after the dependency clause: {tail!r}")
    for raw in clause.split(";"):
        name = KIND_HEAD.sub("", raw.strip()).strip()
        if not (NAME_ENTRY.match(name) or name in MULTIWORD):
            problems.append(f"dependency entry is not a bare name: {raw.strip()!r}")
    return problems


def check_one(desc):
    return check_summary(desc) + check_total(desc) + check_names_only(desc)


GOOD = ("Do one thing well for the operator (agents: a, b) "
        "(external: some-repo; soft: work-items; dev-flow).")


class Mutants(unittest.TestCase):
    """Each check fails on a deliberately bad description."""

    def test_good_passes(self):
        self.assertEqual(check_one(GOOD), [])
        self.assertEqual(check_identical(GOOD, GOOD), [])

    def test_long_summary_fails(self):
        bad = "x" * (SUMMARY_MAX + 1) + " (soft: work-items)."
        self.assertTrue(check_summary(bad))
        self.assertEqual(check_summary("x" * SUMMARY_MAX + " (soft: a)."), [])

    def test_long_total_fails(self):
        bad = "Short summary (soft: " + "; ".join(["work-items"] * 60) + ")."
        self.assertGreater(len(bad), TOTAL_MAX)
        self.assertEqual(check_summary(bad), [])
        self.assertTrue(check_total(bad))

    def test_drifted_copy_fails(self):
        self.assertTrue(check_identical(GOOD, GOOD.replace("well", "badly")))
        self.assertTrue(check_identical(GOOD, GOOD + " "))

    def test_degrade_prose_fails(self):
        for bad in (
            "Summary (soft: work-items, whose wi files the items).",
            "Summary (soft: dev-flow, without which the plan is a file).",
            "Summary (requires hub; soft: dev-flow; without it nothing is filed).",
            "Summary (external: some-repo, Without It the launch is plain).",
            "Summary (Soft dependencies: work-items, whose wi files items).",
            "Summary (soft: work-items, to file items when installed).",
            "S (soft: a; b) (without it nothing is filed).",
            "Summary (soft: dev-flow; plan file).",
            "Summary (external: claude-kit, optional).",
            "Summary (soft: a; b",
        ):
            with self.subTest(bad=bad):
                self.assertTrue(check_names_only(bad))

    def test_degrade_words_outside_clause_pass(self):
        # Only the dependency clause is held to names, not the summary.
        self.assertEqual(check_names_only("Run tools whose output matters (soft: a)."), [])

    def test_external_kinds_pass(self):
        # An external entry's kind is a word, not prose: these forms stay allowed.
        for ok in ("Summary (external, required: claude-sandbox; soft: sandbox).",
                   "Summary (external, soft: claude-sandbox; soft: sandbox; dev-flow).",
                   "Summary (soft: a; b; external, soft: claude-analytics).",
                   "Summary (external: claude-templates; external, optional: claude-kit; "
                   "soft: a).",
                   "Summary (external, soft: claude.ai Artifacts; node).",
                   "Summary (requires statusline-hub; soft: context-guard)."):
            with self.subTest(ok=ok):
                self.assertEqual(check_one(ok), [])


@unittest.skipUnless(IN_REPO, "needs the source repo (marketplace.json and plugins/)")
class RealDescriptions(unittest.TestCase):
    """Every plugin.json and marketplace.json description passes every check."""

    def setUp(self):
        self.plugins = {}
        for f in sorted((REPO / "plugins").glob("*/.claude-plugin/plugin.json")):
            self.plugins[f.parent.parent.name] = json.loads(f.read_text())["description"]
        self.market = {p["name"]: p.get("description", "")
                       for p in json.loads(MARKETPLACE.read_text())["plugins"]}

    def test_found_plugins(self):
        self.assertTrue(self.plugins)
        self.assertTrue(self.market)

    def test_plugin_json(self):
        problems = [f"plugins/{name}/.claude-plugin/plugin.json: {p}"
                    for name, desc in self.plugins.items() for p in check_one(desc)]
        self.assertEqual(problems, [])

    def test_marketplace_json(self):
        problems = [f"marketplace.json {name}: {p}"
                    for name, desc in self.market.items() for p in check_one(desc)]
        self.assertEqual(problems, [])

    def test_identical(self):
        problems = []
        for name in sorted(set(self.plugins) | set(self.market)):
            if name not in self.plugins or name not in self.market:
                problems.append(f"{name}: in only one of plugin.json and marketplace.json")
                continue
            problems += [f"{name}: {p}"
                         for p in check_identical(self.plugins[name], self.market[name])]
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
