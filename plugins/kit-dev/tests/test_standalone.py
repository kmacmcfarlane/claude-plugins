"""Each plugin's tests pass with no other plugin present (README principle 2).

For every plugin under plugins/, the plugin directory alone is copied into a fresh
temporary tree (as <tmp>/plugins/<name>/, so a test that reaches for a sibling plugin or the
repo's README finds nothing there) and every test suite inside it is run with
`python3 -m unittest discover -s tests -q` from the suite's parent directory, the same
command CLAUDE.md § Librarian Checks runs in the repo. A suite that needs a sibling plugin
or a repo file must skip without it, never fail.

Runs only in the source repo (it needs plugins/ and .claude-plugin/marketplace.json two
levels above this plugin); in an isolated copy, kit-dev's own run of it, it skips.
STANDALONE_JOBS (default 3) bounds how many suites run at once.

Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
IN_REPO = (REPO / ".claude-plugin" / "marketplace.json").is_file() and (REPO / "plugins").is_dir()
TIMEOUT_S = 900
JOBS = max(1, int(os.environ.get("STANDALONE_JOBS", "3") or 3))
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def plugins():
    """Every plugin directory under plugins/: the ones carrying .claude-plugin/plugin.json."""
    return sorted(p for p in (REPO / "plugins").iterdir()
                  if (p / ".claude-plugin" / "plugin.json").is_file())


def suites(plugin):
    """Each `tests` directory in the plugin holding a test_*.py, relative to the plugin."""
    found = []
    for d in sorted(plugin.rglob("tests")):
        rel = d.relative_to(plugin)
        if not d.is_dir() or "__pycache__" in rel.parts or "tests" in rel.parts[:-1]:
            continue
        if any(d.glob("test_*.py")):
            found.append(rel)
    return found


def run_alone(plugin, suite, tmp):
    """Copy the plugin alone into tmp and run one suite there; (returncode, output)."""
    root = Path(tmp) / plugin.name / "plugins" / plugin.name
    if not root.exists():
        shutil.copytree(plugin, root, ignore=IGNORE, symlinks=True)
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONSTARTUP")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
                           cwd=root / suite.parent, env=env, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired as e:
        return -1, f"timed out after {TIMEOUT_S}s\n{e.output or ''}"
    return r.returncode, r.stdout


@unittest.skipUnless(IN_REPO, "not in the source repo: no sibling plugins to isolate from")
class EachPluginAlone(unittest.TestCase):
    def test_every_plugin_has_found_suites(self):
        # A plugin that ships hooks or scripts with tests must be found here; guard the finder.
        names = {p.name for p in plugins() if suites(p)}
        for expected in ("context-guard", "statusline", "statusline-hub", "sandbox",
                         "work-items", "dev-flow", "operator-interaction", "kit-dev"):
            self.assertIn(expected, names)

    def test_each_suite_passes_with_no_other_plugin_present(self):
        jobs = [(p, s) for p in plugins() for s in suites(p)]
        with tempfile.TemporaryDirectory(prefix="standalone-") as tmp:
            # Copy first, serially, so parallel suites of one plugin share one copy.
            for p in {p for p, _ in jobs}:
                shutil.copytree(p, Path(tmp) / p.name / "plugins" / p.name,
                                ignore=IGNORE, symlinks=True)
            with ThreadPoolExecutor(max_workers=JOBS) as pool:
                results = list(pool.map(lambda j: (j, run_alone(j[0], j[1], tmp)), jobs))
        for (plugin, suite), (code, out) in results:
            with self.subTest(plugin=plugin.name, suite=str(suite)):
                tail = "\n".join(out.strip().splitlines()[-40:])
                self.assertEqual(code, 0, f"{plugin.name}/{suite} failed alone:\n{tail}")


if __name__ == "__main__":
    unittest.main()
