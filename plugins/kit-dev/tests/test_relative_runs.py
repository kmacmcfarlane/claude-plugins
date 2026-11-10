"""Script runs in skill text never resolve against the working directory (item 185f, F6).

A command such as `python3 scripts/<name>.py` or `node scripts/<name>.js` runs the file
found relative to the Bash tool's working directory, which is normally the checkout, so
a checkout holding a same-named file gets it run. Every such run now names an absolute base:

- a SKILL.md's own command writes `"${CLAUDE_PLUGIN_ROOT}/…"`, which loading the skill fills
  in (https://code.claude.com/docs/en/plugins-reference § Environment variables);
- a reference file is read with a tool, so nothing in it is filled in, and the variable is
  not in the Bash tool's environment. The SKILL.md that owns it states the root once in a
  **Plugin root** line, which its load fills in, and the reference's command takes it in
  a guard: `R="<plugin root>"; case $R in /*) <interp> "$R/…";; *) echo … >&2; false;; esac`.
  A root left unfilled, or filled with a relative path, runs nothing: unguarded, either
  one is a path under the working directory. A command whose placeholder names another
  base (install-statusline-hub's `<plugin root>`, the librarian's record-check directory)
  takes the same guard. The decision-page writer brief carries the root to a writer
  sub-agent, which loads no skill;
- a prose mention of the quota sense points at budget.md § Running it, the guarded command,
  instead of repeating a command.

For every site this suite:

- checks the text: each guarded (or `${CLAUDE_PLUGIN_ROOT}`) command is there as often as
  the site has it; no command runs `scripts/…` or `hooks/…` relatively, runs a placeholder
  path without the guard, or, in a reference, runs a `${CLAUDE_PLUGIN_ROOT}` command (in
  Bash that expands to `/hooks/…`, broken);
- runs every guarded command found in the file under bash from a temp checkout holding
  planted same-named scripts that write a sentinel (at the cwd-relative path, the
  plugin-relative path, `plugins/x/…` and a directory spelled like the placeholder): with
  the placeholder unfilled and filled with `plugins/x` it refuses and runs nothing; filled
  with the root the owning SKILL.md states once its load fills in the variable, the
  install's stub runs; the plant never does. A SKILL.md's `${CLAUDE_PLUGIN_ROOT}` command
  is run from the loaded text the same way;
- runs the mutants: the unguarded placeholder line, unfilled or filled with `plugins/x`,
  runs the plant; each site's old relative line runs the plant (the old
  `${CLAUDE_PLUGIN_ROOT}` reference line never reaches the install); spliced back, each is
  flagged by the text check; a SKILL.md without its root line and a writer brief without
  the root fail their checks.

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
REL_X = "plugins/x"  # a relative root a checkout can plant under

# The SKILL.md that states the root for each plugin's references (any one of them serves).
OWNERS = {
    "context-guard": ["context-guard/skills/checkpoint/SKILL.md"],
    "dev-flow": ["dev-flow/skills/dev-cycle/SKILL.md", "dev-flow/skills/librarian-mode/SKILL.md"],
    "operator-interaction": ["operator-interaction/skills/decision-page/SKILL.md"],
}

QB = "skills/librarian-mode/scripts/quota_budget.py"
CC = "skills/decision-page/scripts/check_cards.js"
UC = "skills/decision-page/scripts/upgrade_cards.js"
SW = "skills/decision-page/scripts/split_writers.js"
CL = "skills/claim-md/scripts/claim_check.py"
IH = "skills/install-statusline-hub/scripts/install_hub.py"
# The librarian's record check: its placeholder, the guard's message, where it points in
# the install, and the old unquoted line with the placeholder filled with a relative dir.
DP_PH = "<decision-page skill dir>"
DP_WHAT = "decision-page skill dir"
DP_REL, DP_UNDER = "scripts/check_cards.js", "skills/decision-page"
DP_OLD = "node plugins/x/scripts/check_cards.js"


def site(path, interp, rel, n, kind="guard", ph=PH, var="R", what="plugin root",
         under="", old=None, owner=True):
    """One site. kind: guard (a placeholder taken in a guard), var (a SKILL.md command on
    ${CLAUDE_PLUGIN_ROOT}). under: where the placeholder points inside the install root.
    old: the pre-fix line, by default `<interp> scripts/<file>` or `<interp> hooks/<file>`."""
    if old is None:
        old = f"{interp} {rel[rel.index('scripts/'):] if 'scripts/' in rel else rel}"
    return dict(path=path, interp=interp, rel=rel, n=n, kind=kind, ph=ph, var=var, what=what,
                under=under, old=old, owner=owner)


SITES = [
    site("context-guard/skills/checkpoint/references/handoff-format.md", "python3",
         "hooks/handoff_path.py", 2),
    site("context-guard/skills/checkpoint/references/handoff-format.md", "python3",
         "hooks/spin_off.py", 1, old='python3 "${CLAUDE_PLUGIN_ROOT}/hooks/spin_off.py"'),
    site("dev-flow/skills/librarian-mode/references/budget.md", "python3", QB, 2),
    site("dev-flow/skills/librarian-mode/references/decisions.md", "node",
         DP_REL, 1, ph=DP_PH, var="D", what=DP_WHAT, under=DP_UNDER, owner=False,
         old=DP_OLD),
    site("operator-interaction/skills/decision-page/references/writers.md", "node", SW, 1),
    site("operator-interaction/skills/decision-page/references/writers.md", "node", CC, 4),
    site("operator-interaction/skills/decision-page/references/writer-digest.md", "node", UC, 1),
    site("operator-interaction/skills/decision-page/references/writer-digest.md", "node", CC, 2),
    site("statusline-hub/skills/install-statusline-hub/SKILL.md", "python3", IH, 1,
         owner=False),
    site("operator-interaction/skills/decision-page/SKILL.md", "node", UC, 1, kind="var"),
    site("operator-interaction/skills/decision-page/SKILL.md", "node", CC, 2, kind="var"),
    site("ownership/skills/claim-md/SKILL.md", "python3", CL, 4, kind="var"),
]
# Prose that names the quota sense points at budget.md § Running it: (file, pointers).
POINTERS = {
    "dev-flow/skills/dev-cycle/references/bindings.md": 2,
    "dev-flow/skills/dev-cycle/references/model-routing.md": 1,
}
POINTER = "`references/budget.md` § Running it"
FIXED = sorted({s["path"] for s in SITES} | set(POINTERS)
               | {f for fs in OWNERS.values() for f in fs})
RELATIVE = re.compile(r"\b(?:python3|node|bash|sh)(?: -I)? +(?:\./)?(?:scripts|hooks)/")
UNGUARDED = re.compile(r"\b(?:python3|node)(?: -I)? +\"?<[^>]+>/")
QUOTA_RUN = re.compile(r"\b(?:python3|node)\b[^`]*quota_budget\.py")
SPAN = re.compile(r"`[^`]*`|^.*$", re.M)


def flat(text):
    return re.sub(r"\s+", " ", text)


def guard_re(s):
    """A guarded command of site s; group 1 is its arguments."""
    v = re.escape("$" + s["var"])
    return re.compile(
        re.escape(f'{s["var"]}="{s["ph"]}"; case ') + v + r" in /\*\) "
        + re.escape(s["interp"]) + ' "' + v + re.escape("/" + s["rel"]) + '"'
        + r"([^;`]*);; \*\) echo " + re.escape(f'"{s["what"]} not absolute: ') + v
        + re.escape('" >&2; false;; esac'))


def var_cmd(s):
    return f'{s["interp"]} "{VAR}/{s["rel"]}"'


def unguarded(s, root=None):
    return f'{s["interp"]} "{s["ph"] if root is None else root}/{s["rel"]}"'


def text_problems(path, text):
    """Every way a fixed file's text can bring back a run from the working directory."""
    out = []
    t = flat(text)
    for m in RELATIVE.finditer(t):
        out.append(f"{path}: relative run {t[m.start():m.start() + 60]!r}")
    for m in UNGUARDED.finditer(t):
        out.append(f"{path}: placeholder run without the guard {t[m.start():m.start() + 60]!r}")
    if "/references/" in path:
        for m in SPAN.finditer(text):
            span = m.group()
            if VAR in span and re.search(r"\b(?:python3|node|bash|sh)\b", span):
                out.append(f"{path}: a reference runs a {VAR} command: {span[:80]!r}")
        if PH in text and "**Plugin root**" not in text and "your brief gives" not in text:
            out.append(f"{path}: uses {PH} but names no source for it")
    for s in SITES:
        if s["path"] != path:
            continue
        got = (len(guard_re(s).findall(t)) if s["kind"] == "guard" else t.count(var_cmd(s)))
        if got < s["n"]:
            out.append(f"{path}: {s['rel']} run {got} times, not {s['n']}")
    if path in POINTERS:
        if QUOTA_RUN.search(t):
            out.append(f"{path}: runs the quota sense instead of pointing at § Running it")
        if t.count(POINTER) < POINTERS[path]:
            out.append(f"{path}: fewer than {POINTERS[path]} pointers to § Running it")
    return out


def owner_problems(text):
    return [] if text.count(BASE_LINE) == 1 else ["the Plugin root line is not there once"]


BRIEF_ROOT = "- the plugin root, the absolute path the `SKILL.md`'s **Plugin root** line gives"


def brief_problems(text):
    t = flat(text)
    brief = t[t.find("## The brief"):t.find("## The merge")]
    return [] if BRIEF_ROOT in brief else ["the writer brief does not carry the plugin root"]


def read(path):
    return (PLUGINS / path).read_text(encoding="utf-8")


WRITERS = "operator-interaction/skills/decision-page/references/writers.md"


@unittest.skipUnless(IN_REPO, "runs only in the source repo")
class TextTest(unittest.TestCase):
    def test_owners_state_the_root(self):
        for files in OWNERS.values():
            for f in files:
                self.assertEqual(owner_problems(read(f)), [], f)

    def test_mutant_owner_without_root_line(self):
        for files in OWNERS.values():
            for f in files:
                self.assertNotEqual(owner_problems(read(f).replace(BASE_LINE, "")), [], f)

    def test_fixed_files_clean(self):
        for f in FIXED:
            self.assertEqual(text_problems(f, read(f)), [], f)

    def test_writer_brief_carries_root(self):
        self.assertEqual(brief_problems(read(WRITERS)), [])

    def test_mutant_brief_without_root(self):
        t = re.sub(r"   - the plugin root,.*?checkout;\n", "", read(WRITERS), flags=re.S)
        self.assertNotEqual(brief_problems(t), [])

    def test_mutants_flagged(self):
        """Each site's old line, and its unguarded placeholder line, spliced back in place of
        one of its commands, is flagged."""
        for s in SITES:
            t = flat(read(s["path"]))
            if s["kind"] == "guard":
                m = guard_re(s).search(t)
                spans = {"old": s["old"] + m.group(1), "unguarded": unguarded(s) + m.group(1)}
                for name, new in spans.items():
                    mutant = t[:m.start()] + new + t[m.end():]
                    with self.subTest(site=s["path"], rel=s["rel"], mutant=name):
                        self.assertNotEqual(text_problems(s["path"], mutant), [])
            else:
                mutant = t.replace(var_cmd(s), s["old"], 1)
                with self.subTest(site=s["path"], rel=s["rel"], mutant="old"):
                    self.assertNotEqual(text_problems(s["path"], mutant), [])

    def test_mutant_pointer_runs_the_script(self):
        old = 'python3 "<plugin root>/skills/librarian-mode/scripts/quota_budget.py" --read-only'
        for path in POINTERS:
            mutant = flat(read(path)).replace(POINTER, old, 1)
            self.assertNotEqual(text_problems(path, mutant), [], path)


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

    def fixture(self, s):
        root = self.tmp / "cache" / "kmacmcfarlane" / s["path"].split("/")[0] / "1.0.0"
        checkout = self.tmp / "work" / "repo"
        ok, sentinel = self.tmp / "OK", self.tmp / "SENTINEL"
        for f in (ok, sentinel):
            f.unlink(missing_ok=True)

        def put(path, mark):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(STUB[s["interp"]].format(p=str(mark)))

        rel = s["rel"]
        put(root / s["under"] / rel, ok)
        short = rel[rel.index("scripts/"):] if "scripts/" in rel else rel
        for p in (checkout / short, checkout / rel, checkout / s["ph"] / rel,
                  checkout / REL_X / rel):
            put(p, sentinel)
        return root, checkout, ok, sentinel

    def filled(self, s, root):
        """What the session puts in the placeholder: the root its owner's load states, or,
        for a placeholder found another way, the install's absolute path."""
        if not s["owner"]:
            return str(root / s["under"]) if s["under"] else str(root)
        owner = OWNERS[s["path"].split("/")[0]][0]
        m = BASE_RE.search(read(owner).replace(VAR, str(root)))
        self.assertIsNotNone(m, owner)
        self.assertTrue(os.path.isabs(m.group(1)), m.group(1))
        return m.group(1)

    def run_cmd(self, cmd, checkout):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
        return subprocess.run(["bash", "-c", cmd], cwd=checkout, env=env,
                              capture_output=True, text=True, timeout=30)

    def runnable(self, cmd, s):
        """The other placeholders in the arguments (`<file>`, `<draft>`) become words."""
        head = f'{s["var"]}="{s["ph"]}"'
        return head + re.sub(r"<[^>]+>", "X", cmd[len(head):])

    def guarded(self, s):
        cmds = [m.group(0) for m in guard_re(s).finditer(flat(read(s["path"])))]
        self.assertGreaterEqual(len(cmds), s["n"], s["path"])
        return cmds

    def each(self, kind):
        return [s for s in SITES if s["kind"] == kind and HAVE[s["interp"]]]

    def test_guard_runs_install_never_plant(self):
        for s in self.each("guard"):
            for cmd in self.guarded(s):
                root, checkout, ok, sentinel = self.fixture(s)
                cmd = self.runnable(cmd, s)
                for fill in (s["ph"], REL_X):
                    with self.subTest(site=s["path"], rel=s["rel"], fill=fill):
                        p = self.run_cmd(cmd.replace(s["ph"], fill, 1), checkout)
                        self.assertNotEqual(p.returncode, 0)
                        self.assertIn("not absolute", p.stderr)
                        self.assertFalse(sentinel.exists(), "a checkout plant ran")
                        self.assertFalse(ok.exists())
                with self.subTest(site=s["path"], rel=s["rel"], fill="root"):
                    self.run_cmd(cmd.replace(s["ph"], self.filled(s, root), 1), checkout)
                    self.assertTrue(ok.exists(), "the install's script did not run")
                    self.assertFalse(sentinel.exists(), "a checkout plant ran")

    def test_mutant_unguarded_runs_plant(self):
        for s in self.each("guard"):
            for fill in (None, REL_X):
                root, checkout, ok, sentinel = self.fixture(s)
                with self.subTest(site=s["path"], rel=s["rel"], fill=fill):
                    self.run_cmd(unguarded(s, fill), checkout)
                    self.assertTrue(sentinel.exists(), "the unguarded line ran no plant")

    def test_var_runs_install_never_plant(self):
        for s in self.each("var"):
            with self.subTest(site=s["path"], rel=s["rel"]):
                root, checkout, ok, sentinel = self.fixture(s)
                cmd = var_cmd(s).replace(VAR, str(root))
                self.assertIn(cmd, flat(read(s["path"])).replace(VAR, str(root)))
                self.run_cmd(cmd, checkout)
                self.assertTrue(ok.exists(), "the install's script did not run")
                self.assertFalse(sentinel.exists(), "a checkout plant ran")

    def test_mutant_old_line(self):
        for s in SITES:
            if not HAVE[s["interp"]]:
                continue
            with self.subTest(site=s["path"], rel=s["rel"]):
                root, checkout, ok, sentinel = self.fixture(s)
                self.run_cmd(s["old"], checkout)
                if VAR in s["old"]:
                    # in Bash the variable is unset: `/hooks/…`, never the install
                    self.assertFalse(ok.exists())
                else:
                    self.assertTrue(sentinel.exists(), "the old line ran no plant")

    def test_unloaded_owner_gives_no_root(self):
        """Read without its load, the root line holds no absolute path."""
        for files in OWNERS.values():
            m = BASE_RE.search(read(files[0]))
            self.assertFalse(os.path.isabs(m.group(1)))


if __name__ == "__main__":
    unittest.main()
