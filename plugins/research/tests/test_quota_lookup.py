"""The quota-sense lookup in the research skill's routing, run (f4ef F3).

`skills/research/references/intensity-and-routing.md` § Finding the quota sense holds one
fenced bash snippet that finds dev-flow's `librarian-mode` quota script for § Below the
quota reserve. It stops at the first hit: dev-flow's install record
(`dev-flow@kmacmcfarlane`, the entry that applies to the checkout), then the newest cached
copy. A miss reads as not below. No path under the working checkout is ever consulted: any
repo can name itself `kmacmcfarlane`, so a checkout, this kit's own included, never supplies
the script.

This test extracts the snippet and runs it under bash in a temp tree, with a fake config dir
and a fake checkout, one case per rule. It travels with the research plugin.

Standard library only. Run from the plugin dir:

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
ROUTING = PLUGIN / "skills" / "research" / "references" / "intensity-and-routing.md"
KEY = "dev-flow@kmacmcfarlane"
REL = "skills/librarian-mode/scripts/quota_budget.py"
NONE = "no quota sense found"


def snippet():
    """The one fenced bash block of ### Finding the quota sense."""
    body = ROUTING.read_text(encoding="utf-8")
    sec = re.search(r"^### Finding the quota sense\n(.*?)(?=^##+ |\Z)", body, re.S | re.M)
    if not sec:
        return None
    blocks = re.findall(r"^```bash\n(.*?)^```", sec.group(1), re.S | re.M)
    return blocks[0] if len(blocks) == 1 else None


class TestSnippetShape(unittest.TestCase):
    def test_one_block(self):
        self.assertIsNotNone(snippet(), "exactly one bash block in § Finding the quota sense")

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

    def test_the_reserve_section_points_at_it(self):
        body = ROUTING.read_text(encoding="utf-8")
        sec = re.search(r"^## Below the quota reserve\n(.*?)(?=^## |\Z)", body, re.S | re.M)
        self.assertIsNotNone(sec)
        flat = " ".join(sec.group(1).split())
        self.assertIn("found by the snippet below", flat)
        self.assertIn("No script, or no signal, reads as not below.", flat)


@unittest.skipUnless(shutil.which("bash") and shutil.which("python3"), "bash and python3 needed")
class TestLookupRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cfg = self.tmp / "cfg"
        (self.cfg / "plugins").mkdir(parents=True)
        self.checkout = self.tmp / "work" / "repo"
        self.checkout.mkdir(parents=True)

    def root(self, path):
        f = path / REL
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

    def cache(self, version, age=0):
        path = self.root(self.cfg / "plugins" / "cache" / "kmacmcfarlane" / "dev-flow" / version)
        t = time.time() - age
        os.utime(path / REL, (t, t))
        return path

    def marketplace(self, name="kmacmcfarlane"):
        d = self.checkout / ".claude-plugin"
        d.mkdir(exist_ok=True)
        (d / "marketplace.json").write_text(json.dumps({"name": name, "plugins": []}))

    def run_lookup(self, extra=""):
        block = snippet()
        block = block + extra if block else None
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

    def assertFound(self, root):
        self.assertEqual(self.run_lookup(), f"quota sense: {root / REL}")

    def test_user_scope_install(self):
        p = self.root(self.tmp / "inst" / "user")
        self.record(self.entry(p))
        self.assertFound(p)

    def test_a_deeper_local_entry_beats_user(self):
        user = self.root(self.tmp / "inst" / "user")
        local = self.root(self.tmp / "inst" / "local")
        self.record(self.entry(user), self.entry(local, "local", self.checkout))
        self.assertFound(local)

    def test_another_projects_install_never_answers(self):
        other = self.root(self.tmp / "inst" / "other")
        self.record(self.entry(other, "local", self.tmp / "elsewhere"))
        self.assertEqual(self.run_lookup(), NONE)

    def test_cache_only_takes_the_newest(self):
        self.cache("1.0.0", age=100)
        new = self.cache("1.1.0", age=10)
        self.assertFound(new)

    def test_a_kmacmcfarlane_checkout_never_supplies_the_script(self):
        # A planted script that writes a sentinel: the lookup must not find it, and the
        # guarded call after it must not run it.
        self.marketplace("kmacmcfarlane")
        sentinel = self.tmp / "sentinel"
        f = self.checkout / "plugins" / "dev-flow" / REL
        f.parent.mkdir(parents=True)
        f.write_text("open(%r, 'w').write('ran')\n" % str(sentinel))
        tail = '\ntest "$QB" != no-quota-sense && python3 "$QB" --read-only\ntrue\n'
        out = self.run_lookup(extra=tail)
        self.assertIn(NONE, out)
        self.assertFalse(sentinel.exists(), "the planted script ran")

    def test_the_install_beats_this_marketplaces_checkout(self):
        self.marketplace()
        self.root(self.checkout / "plugins" / "dev-flow")
        p = self.root(self.tmp / "inst" / "user")
        self.record(self.entry(p))
        self.assertFound(p)

    def test_a_planted_plugin_in_a_foreign_checkout_is_never_chosen(self):
        self.root(self.checkout / "plugins" / "x")
        self.root(self.checkout / "plugins" / "dev-flow")  # no marketplace.json at all
        self.assertEqual(self.run_lookup(), NONE)

    def test_another_marketplaces_dev_flow_dir_is_not_chosen(self):
        self.marketplace("someone-else")
        self.root(self.checkout / "plugins" / "dev-flow")
        self.assertEqual(self.run_lookup(), NONE)

    def test_nothing_anywhere(self):
        self.assertEqual(self.run_lookup(), NONE)


if __name__ == "__main__":
    unittest.main()
