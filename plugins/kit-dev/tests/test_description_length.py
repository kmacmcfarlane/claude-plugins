"""Plugin descriptions stay short (CLAUDE.md § Conventions, Plugin descriptions).

The plugin menu shows a plugin's whole description, and a long one overflows it (observed by
the operator on 2026-11-17, when one description ran to 3610 characters). For every
plugins/*/.claude-plugin/plugin.json and every .claude-plugin/marketplace.json entry:

- the summary, the text before the first " (", is at most SUMMARY_MAX characters;
- the whole description is at most TOTAL_MAX characters;
- the plugin.json description and the marketplace.json entry's are identical;
- the dependency clause holds names only, no how-it-degrades prose (DEGRADE_PROSE).

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

# The rule asks for about 100. The longest summary today is statusline-hub's, 155
# characters, because it names all three of its core functions (the dispatcher and hook
# registry, and the sensor record other plugins read); every other summary is at most 117.
# 160 holds that one with a little room and fails the next drift past it.
SUMMARY_MAX = 160

# The longest description today is dev-flow's, 414 characters: a summary, eleven agent
# names (which test_agents.py requires in it), nine soft dependency names and one
# external. 420 leaves room for a few characters of rewording but not another name, so
# the next growth past that is a prompt to trim, not a silent overflow; every other
# description sits under 270.
TOTAL_MAX = 420

# How-it-degrades prose belongs in the README catalog cell and the skill text, never in
# the description's dependency clause.
DEGRADE_PROSE = ("whose ", "without which", "without it")

# The dependency clause opens at the first parenthesis starting with one of these words,
# as test_declared_edges.py reads it.
CLAUSE_OPEN = re.compile(r" \((?:soft|requires|external|optional|hard)\b")


def summary(desc):
    """The summary sentence: the text before the first ' ('."""
    return desc.split(" (", 1)[0]


def dependency_clause(desc):
    """The dependency clause, from its opening parenthesis to the end; '' when none."""
    m = CLAUSE_OPEN.search(desc)
    return desc[m.start():] if m else ""


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


def check_no_degrade_prose(desc):
    clause = dependency_clause(desc).lower()
    return [f"dependency clause holds degrade prose {p!r}" for p in DEGRADE_PROSE if p in clause]


def check_one(desc):
    return check_summary(desc) + check_total(desc) + check_no_degrade_prose(desc)


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
        ):
            with self.subTest(bad=bad):
                self.assertTrue(check_no_degrade_prose(bad))

    def test_degrade_words_outside_clause_pass(self):
        # The words only count inside the dependency clause, not in the summary.
        self.assertEqual(check_no_degrade_prose("Run tools whose output matters (soft: a)."), [])

    def test_external_kinds_pass(self):
        # An external entry's kind is a word, not prose: these forms stay allowed.
        for ok in ("Summary (external, required: claude-sandbox; soft: sandbox).",
                   "Summary (external, soft: claude-sandbox; soft: sandbox; dev-flow).",
                   "Summary (soft: a; b; external, soft: claude-analytics).",
                   "Summary (external: claude-templates; claude-kit, optional; soft: a)."):
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
