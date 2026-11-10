"""deep-investigation's research-plugin lookup, run (f4ef F3).

`skills/deep-investigation/references/research-peer.md` § Finding the research plugin holds
one fenced bash snippet. It finds the research plugin's root in this order and stops at the
first complete hit: the install record (`research@kmacmcfarlane`, the entry that applies to
the checkout), then the newest cached copy; a miss at both is "no research found". A root is
complete only with the scan floor, the sheet check and both agent bodies. No path under the
working checkout is ever consulted: any repo can name itself `kmacmcfarlane`, so a checkout,
this kit's own included, never supplies the scanner or agent bodies.

This test extracts the snippet and runs it under bash in a temp tree, with a fake config dir
and a fake checkout, one case per rule.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
PEER = PLUGIN / "skills" / "deep-investigation" / "references" / "research-peer.md"
KEY = "research@kmacmcfarlane"
FILES = ("skills/research/scripts/scan-findings.py", "skills/research/scripts/check-sheet.py",
         "agents/research-lane.md", "agents/research-verifier.md")
NONE = "no research found"


def snippet():
    """The one fenced bash block of § Finding the research plugin."""
    body = PEER.read_text(encoding="utf-8")
    sec = re.search(r"^## Finding the research plugin\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not sec:
        return None
    blocks = re.findall(r"^```bash\n(.*?)^```", sec.group(1), re.S | re.M)
    return blocks[0] if len(blocks) == 1 else None


class TestSnippetShape(unittest.TestCase):
    def test_one_block(self):
        self.assertIsNotNone(snippet(), "exactly one bash block in § Finding the research plugin")

    def test_reads_json_isolated(self):
        block = snippet() or ""
        self.assertIn(KEY, block)
        for line in block.splitlines():
            if "python3" in line:
                self.assertIn("python3 -I", line)
        self.assertNotIn("plugins/*/", block)
        self.assertNotIn("$MAIN/plugins", block)
        self.assertNotIn('"$MAIN"/plugins', block)
        self.assertNotIn("marketplace.json", block)


@unittest.skipUnless(shutil.which("bash") and shutil.which("python3"), "bash and python3 needed")
class TestLookupRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cfg = self.tmp / "cfg"
        (self.cfg / "plugins").mkdir(parents=True)
        self.checkout = self.tmp / "work" / "repo"
        self.checkout.mkdir(parents=True)

    # -- fixtures ---------------------------------------------------------------------
    def root(self, path, missing=()):
        for rel in FILES:
            if rel not in missing:
                f = path / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("x\n")
        return path

    def record(self, *entries):
        data = {"version": 2, "plugins": {KEY: list(entries)}}
        (self.cfg / "plugins" / "installed_plugins.json").write_text(json.dumps(data))

    def entry(self, path, scope="user", project=None):
        e = {"scope": scope, "installPath": str(path), "version": "1.0.0"}
        if project is not None:
            e["projectPath"] = str(project)
        return e

    def cache(self, version, age=0, missing=()):
        path = self.root(self.cfg / "plugins" / "cache" / "kmacmcfarlane" / "research" / version,
                         missing)
        t = time.time() - age
        os.utime(path, (t, t))
        return path

    def marketplace(self, name="kmacmcfarlane"):
        d = self.checkout / ".claude-plugin"
        d.mkdir(exist_ok=True)
        (d / "marketplace.json").write_text(json.dumps({"name": name, "plugins": []}))

    def run_lookup(self):
        block = snippet()
        self.assertIsNotNone(block)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp),
               "CLAUDE_CONFIG_DIR": str(self.cfg), "GIT_CEILING_DIRECTORIES": str(self.tmp),
               "LC_ALL": "C"}
        out = subprocess.run(["bash", "-c", block], cwd=str(self.checkout), env=env,
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        lines = out.stdout.strip().splitlines()
        self.assertTrue(lines, "the snippet printed nothing")
        return lines[-1]

    def assertFound(self, path, where):
        self.assertEqual(self.run_lookup(), f"research: {path} ({where})")

    # -- cases ------------------------------------------------------------------------
    def test_user_scope_install(self):
        p = self.root(self.tmp / "inst" / "user")
        self.record(self.entry(p))
        self.assertFound(p, "installed")

    def test_a_deeper_local_entry_beats_user(self):
        user = self.root(self.tmp / "inst" / "user")
        proj = self.root(self.tmp / "inst" / "project")
        local = self.root(self.tmp / "inst" / "local")
        self.record(self.entry(user), self.entry(proj, "project", self.tmp / "work"),
                    self.entry(local, "local", self.checkout))
        self.assertFound(local, "installed")

    def test_another_projects_install_never_answers(self):
        other = self.root(self.tmp / "inst" / "other")
        self.record(self.entry(other, "local", self.tmp / "elsewhere"))
        self.assertEqual(self.run_lookup(), NONE)

    def test_cache_only_takes_the_newest(self):
        self.cache("1.0.0", age=100)
        new = self.cache("1.1.0", age=10)
        self.assertFound(new, "cache, not installed")

    def test_an_incomplete_install_is_passed_over(self):
        p = self.root(self.tmp / "inst" / "user", missing=("agents/research-verifier.md",))
        self.record(self.entry(p))
        c = self.cache("1.0.0")
        self.assertFound(c, "cache, not installed")

    def test_each_missing_file_makes_a_root_incomplete(self):
        for rel in FILES:
            with self.subTest(missing=rel):
                p = self.root(self.tmp / "inst" / rel.replace("/", "_"), missing=(rel,))
                self.record(self.entry(p))
                self.assertEqual(self.run_lookup(), NONE)

    def test_a_kmacmcfarlane_checkout_never_supplies_the_scanner(self):
        self.marketplace("kmacmcfarlane")
        self.root(self.checkout / "plugins" / "research")
        self.assertEqual(self.run_lookup(), NONE)

    def test_the_install_beats_this_marketplaces_checkout(self):
        self.marketplace()
        self.root(self.checkout / "plugins" / "research")
        p = self.root(self.tmp / "inst" / "user")
        self.record(self.entry(p))
        self.assertFound(p, "installed")

    def test_a_planted_plugin_in_a_foreign_checkout_is_never_chosen(self):
        self.root(self.checkout / "plugins" / "x")
        self.root(self.checkout / "plugins" / "research")  # no marketplace.json at all
        self.assertEqual(self.run_lookup(), NONE)

    def test_a_planted_plugin_with_an_install_gives_the_install(self):
        self.marketplace("kmacmcfarlane")
        self.root(self.checkout / "plugins" / "x")
        p = self.root(self.tmp / "inst" / "user")
        self.record(self.entry(p))
        self.assertFound(p, "installed")

    def test_another_marketplaces_research_dir_is_not_chosen(self):
        self.marketplace("someone-else")
        self.root(self.checkout / "plugins" / "research")
        self.assertEqual(self.run_lookup(), NONE)

    def test_nothing_anywhere(self):
        self.assertEqual(self.run_lookup(), NONE)


if __name__ == "__main__":
    unittest.main()
