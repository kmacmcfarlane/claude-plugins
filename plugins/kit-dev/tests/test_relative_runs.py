"""Script runs in skill text never resolve against the working directory (item 185f, F6).

A command such as `python3 scripts/<name>.py` or `node scripts/<name>.js` runs the file
found relative to the Bash tool's working directory, which is normally the checkout, so
a checkout holding a same-named file gets it run. Every such run now names an absolute base:

- a SKILL.md's own command writes `"${CLAUDE_PLUGIN_ROOT}/…"`, which loading the skill fills
  in (https://code.claude.com/docs/en/plugins-reference § Environment variables);
- a reference file is read with a tool, so nothing in it is filled in, and the variable is
  not in the Bash tool's environment. Its commands write `"<plugin root>/…"`, and the
  SKILL.md that owns it states the root once in a **Plugin root** line, which its load
  fills in. The decision-page writer brief carries that root to a writer sub-agent, which
  loads no skill.

For every fixed site this suite:

- checks the text: the new absolute-base command is there, and no command in the fixed
  files runs `scripts/…` or `hooks/…` relatively, and no reference runs a
  `${CLAUDE_PLUGIN_ROOT}` command (which in Bash expands to `/hooks/…`, broken);
- runs it: the owning SKILL.md is "loaded" (the variable replaced by a temp install root),
  the root read from its **Plugin root** line (or the command taken from the loaded
  SKILL.md itself), and the command run under bash from a temp checkout holding a planted
  same-named script that writes a sentinel. The install's stub runs; the plant never does.
- runs the mutant: the site's old line, run the same way, runs the plant (or, for the old
  `${CLAUDE_PLUGIN_ROOT}` reference line, never reaches the install), and the text check
  flags the old line spliced back into the file.

Runs only in the source repo (it reads other plugins); in an isolated copy of kit-dev it
skips. Standard library only; the node sites skip without node. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
IN_REPO = ((REPO / "README.md").is_file()
           and (REPO / ".claude-plugin" / "marketplace.json").is_file())
HAVE = {t: bool(shutil.which(t)) for t in ("bash", "python3", "node")}

BASE_LINE = "**Plugin root:** `${CLAUDE_PLUGIN_ROOT}`"
BASE_RE = re.compile(r"\*\*Plugin root:\*\* `([^`]+)`")
PH = "<plugin root>"
VAR = "${CLAUDE_PLUGIN_ROOT}"

# The SKILL.md that states the root for each plugin's references (any one of them serves).
OWNERS = {
    "context-guard": ["context-guard/skills/checkpoint/SKILL.md"],
    "dev-flow": ["dev-flow/skills/dev-cycle/SKILL.md", "dev-flow/skills/librarian-mode/SKILL.md"],
    "operator-interaction": ["operator-interaction/skills/decision-page/SKILL.md"],
}

# (file under plugins/, interpreter, script path inside the plugin, occurrences, old line);
# OLD stands for the site's pre-fix relative line, `<interp> scripts/<file>` or
# `<interp> hooks/<file>`, built by old_cmd.
OLD = None
QB = "skills/librarian-mode/scripts/quota_budget.py"
CC = "skills/decision-page/scripts/check_cards.js"
UC = "skills/decision-page/scripts/upgrade_cards.js"
SW = "skills/decision-page/scripts/split_writers.js"
CL = "skills/claim-md/scripts/claim_check.py"
SITES = [
    ("context-guard/skills/checkpoint/references/handoff-format.md", "python3",
     "hooks/handoff_path.py", 2, OLD),
    ("context-guard/skills/checkpoint/references/handoff-format.md", "python3",
     "hooks/spin_off.py", 1, 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/spin_off.py"'),
    ("dev-flow/skills/dev-cycle/references/bindings.md", "python3", QB, 2, OLD),
    ("dev-flow/skills/dev-cycle/references/model-routing.md", "python3", QB, 1, OLD),
    ("dev-flow/skills/librarian-mode/references/budget.md", "python3", QB, 2, OLD),
    ("operator-interaction/skills/decision-page/references/writers.md", "node", SW, 1, OLD),
    ("operator-interaction/skills/decision-page/references/writers.md", "node", CC, 4, OLD),
    ("operator-interaction/skills/decision-page/references/writer-digest.md", "node", UC, 1, OLD),
    ("operator-interaction/skills/decision-page/references/writer-digest.md", "node", CC, 2, OLD),
    ("operator-interaction/skills/decision-page/SKILL.md", "node", UC, 1, OLD),
    ("ownership/skills/claim-md/SKILL.md", "python3", CL, 4, OLD),
]


def old_cmd(site):
    """The pre-fix line: the interpreter and the script's path below the skill dir."""
    if site[4] is not OLD:
        return site[4]
    rel = site[2]
    return f"{site[1]} {rel[rel.index('scripts/'):] if 'scripts/' in rel else rel}"


FIXED = sorted({s[0] for s in SITES} | {f for fs in OWNERS.values() for f in fs})
RELATIVE = re.compile(r"\b(?:python3|node|bash|sh)(?: -I)? +(?:\./)?(?:scripts|hooks)/")
SPAN = re.compile(r"`[^`]*`|^.*$", re.M)


def flat(text):
    return re.sub(r"\s+", " ", text)


def new_cmd(site):
    path, interp, rel = site[0], site[1], site[2]
    base = PH if "/references/" in path else VAR
    return f'{interp} "{base}/{rel}"'


def text_problems(path, text):
    """Every way a fixed file's text can bring back a run from the working directory."""
    out = []
    t = flat(text)
    for m in RELATIVE.finditer(t):
        out.append(f"{path}: relative run {t[m.start():m.start() + 60]!r}")
    if "/references/" in path:
        for m in SPAN.finditer(text):
            span = m.group()
            if VAR in span and re.search(r"\b(?:python3|node|bash|sh)\b", span):
                out.append(f"{path}: a reference runs a {VAR} command: {span[:80]!r}")
        if PH in text and "**Plugin root**" not in text and "your brief gives" not in text:
            out.append(f"{path}: uses {PH} but names no source for it")
    for site in SITES:
        if site[0] == path and t.count(new_cmd(site)) < site[3]:
            out.append(f"{path}: {new_cmd(site)!r} fewer than {site[3]} times")
    return out


def read(path):
    return (PLUGINS / path).read_text(encoding="utf-8")


@unittest.skipUnless(IN_REPO, "runs only in the source repo")
class TextTest(unittest.TestCase):
    def test_owners_state_the_root(self):
        for files in OWNERS.values():
            for f in files:
                self.assertEqual(read(f).count(BASE_LINE), 1, f)

    def test_fixed_files_clean(self):
        for f in FIXED:
            self.assertEqual(text_problems(f, read(f)), [], f)

    def test_writer_brief_carries_root(self):
        t = flat(read("operator-interaction/skills/decision-page/references/writers.md"))
        brief = t[t.find("## The brief"):t.find("## The merge")]
        self.assertIn("- the plugin root, the absolute path the `SKILL.md`'s **Plugin root** "
                      "line gives", brief)

    def test_mutants_flagged(self):
        """Each site's old line, spliced back in place of the new one, is flagged."""
        for site in SITES:
            text = read(site[0])
            old = flat(text).replace(new_cmd(site), old_cmd(site), 1)
            with self.subTest(site=site[0], rel=site[2]):
                self.assertNotEqual(text_problems(site[0], old), [])

    def test_mutant_brief_without_root(self):
        t = read("operator-interaction/skills/decision-page/references/writers.md")
        t = re.sub(r"   - the plugin root,.*?checkout;\n", "", t, flags=re.S)
        self.assertNotIn("- the plugin root, the absolute path", flat(t))


STUB = {
    "python3": "import sys\nopen({p!r}, 'a').write(__file__ + '\\n')\n",
    "node": "require('fs').appendFileSync({p!r}, __filename + '\\n');\n",
}


@unittest.skipUnless(IN_REPO and HAVE["bash"], "runs only in the source repo, with bash")
class RunTest(unittest.TestCase):
    """The site's command runs the install's script; a checkout plant never runs."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def fixture(self, site):
        interp, rel = site[1], site[2]
        root = self.tmp / "cache" / "kmacmcfarlane" / site[0].split("/")[0] / "1.0.0"
        checkout = self.tmp / "work" / "repo"
        ok, sentinel = self.tmp / "OK", self.tmp / "SENTINEL"
        for f in (ok, sentinel):
            f.unlink(missing_ok=True)

        def put(path, mark):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(STUB[interp].format(p=str(mark)))

        put(root / rel, ok)
        # plants: the cwd-relative path the old line names, the plugin-relative path, and
        # a directory spelled like the placeholder
        short = rel[rel.index("scripts/"):] if "scripts/" in rel else rel
        for p in (checkout / short, checkout / rel, checkout / PH / rel):
            put(p, sentinel)
        return root, checkout, ok, sentinel

    def loaded_root(self, site, root):
        """The root the owning SKILL.md states once its load fills in the variable."""
        owner = OWNERS[site[0].split("/")[0]][0]
        loaded = read(owner).replace(VAR, str(root))
        m = BASE_RE.search(loaded)
        self.assertIsNotNone(m, owner)
        self.assertTrue(os.path.isabs(m.group(1)), m.group(1))
        return m.group(1)

    def command(self, site, root):
        """The site's command as the session sees it: the loaded text, the root put in."""
        cmd = new_cmd(site)
        if "/references/" in site[0]:
            text = flat(read(site[0])).replace(PH, self.loaded_root(site, root))
            cmd = cmd.replace(PH, self.loaded_root(site, root))
        else:
            text = flat(read(site[0])).replace(VAR, str(root))
            cmd = cmd.replace(VAR, str(root))
        self.assertIn(cmd, text)
        return cmd

    def run_cmd(self, cmd, checkout):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
        return subprocess.run(["bash", "-c", cmd], cwd=checkout, env=env,
                              capture_output=True, text=True, timeout=30)

    def each(self):
        for site in SITES:
            if not HAVE[site[1]]:
                continue
            yield site

    def test_new_line_runs_install_never_plant(self):
        for site in self.each():
            with self.subTest(site=site[0], rel=site[2]):
                root, checkout, ok, sentinel = self.fixture(site)
                self.run_cmd(self.command(site, root), checkout)
                self.assertTrue(ok.exists(), "the install's script did not run")
                self.assertFalse(sentinel.exists(), "a checkout plant ran")

    def test_old_line_is_the_mutant(self):
        for site in self.each():
            with self.subTest(site=site[0], rel=site[2]):
                root, checkout, ok, sentinel = self.fixture(site)
                self.run_cmd(old_cmd(site), checkout)
                if VAR in old_cmd(site):
                    # in Bash the variable is unset: `/hooks/…`, never the install
                    self.assertFalse(ok.exists())
                else:
                    self.assertTrue(sentinel.exists(), "the old relative line ran no plant")

    def test_unloaded_owner_gives_no_root(self):
        """Read without its load, the base line holds no absolute path."""
        for files in OWNERS.values():
            m = BASE_RE.search(read(files[0]))
            self.assertFalse(os.path.isabs(m.group(1)))

    def test_mutant_owner_without_base_line(self):
        """With the base line gone, a loaded owner states no root to run from."""
        for files in OWNERS.values():
            for f in files:
                loaded = read(f).replace(BASE_LINE, "").replace(VAR, str(self.tmp))
                self.assertIsNone(BASE_RE.search(loaded), f)


if __name__ == "__main__":
    unittest.main()
