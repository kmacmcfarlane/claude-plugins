"""dev-cycle's lookups of another plugin's file, run (item 185f, F1).

`skills/dev-cycle/references/bindings.md` holds three fenced bash lookups that resolve a
file from another plugin:

- W1, § Store: `wi.py` (work-items), run as `$WI`;
- U1, § Spend budget, the reader: `usage_report.py` (context-guard), run on the record;
- C1, § Authoring rules: kit-dev's `create-skill/SKILL.md`, handed to builders and
  reviewers as the kit's authoring rules.

Each runs one rule: the install record (the entry that applies to the checkout), then the
cache only when the record cannot answer (its read exits non-zero), and a hit only when it is
an absolute path. No path under the working checkout is ever used, so a checkout disguised as
this kit (marketplace name `kmacmcfarlane`, `origin` the kit's URL, a store, a planted script)
never supplies the file.

This test extracts each block and runs it under bash in a temp tree, with a fake config dir
and a fake checkout, one scenario per rule. A planted script writes a sentinel file when it
runs. Every scenario is also run against mutants of the block (the pre-fix checkout-first
lines spliced back in, the plain `test -n` guard with a printed `-`, an unconditional cache,
no `rc`, no absolute `P`, no absolute check at all), and each mutant is shown to fail the
scenario that guards against it.

It also holds deep-investigation's rule that the strategy doc's stored `wi:` and
`item_file:` lines are records, never run or written to.

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
BINDINGS = PLUGIN / "skills" / "dev-cycle" / "references" / "bindings.md"
DEEP = PLUGIN / "skills" / "deep-investigation"
KIT_URL = "https://github.com/kmacmcfarlane/claude-plugins.git"
MISS = None

LOOKUPS = {
    "W1": dict(var="WI_PY", key="work-items@kmacmcfarlane", plugin="work-items",
               rel="skills/work-items/scripts/wi.py", miss="no wi found", rank="$MAIN",
               executed=True),
    "U1": dict(var="UR_PY", key="context-guard@kmacmcfarlane", plugin="context-guard",
               rel="skills/usage-report/scripts/usage_report.py", miss="no reader found",
               rank="$MAIN", executed=True),
    "C1": dict(var="CS", key="kit-dev@kmacmcfarlane", plugin="kit-dev",
               rel="skills/create-skill/SKILL.md", miss="no create-skill found",
               rank="$WORKTREE", executed=False),
}


def block(name):
    """The one fenced bash block of bindings.md that assigns the lookup's variable."""
    var = LOOKUPS[name]["var"]
    blocks = re.findall(r"^```bash\n(.*?)^```", BINDINGS.read_text(encoding="utf-8"),
                        re.S | re.M)
    hits = [b for b in blocks if re.search(r"^%s=" % var, b, re.M)]
    return hits[0] if len(hits) == 1 else None


# -- mutants: each returns the block with one guard undone ------------------------------
def _sub(text, old, new):
    if old not in text:
        raise AssertionError(f"mutant target not in block: {old!r}")
    return text.replace(old, new)


def case_line(s):
    return f'{s["var"]}=; case $IP in /*) test -f "$IP/{s["rel"]}" && {s["var"]}=$IP/{s["rel"]};; esac'


def mut_prefix(b, s):
    """The pre-fix lines: the checkout glob first, then `$IP/<rel>` unchecked."""
    old = (f'{s["var"]}=$(ls "{s["rank"]}"/plugins/*/{s["rel"]} 2>/dev/null | head -1)\n'
           f'test -n "${s["var"]}" || {s["var"]}="$IP/{s["rel"]}"')
    return _sub(b, case_line(s), old)


def mut_dash(b, s):
    """A heredoc that prints `-` on failure, read by a plain `test -n` guard."""
    b = _sub(b, "    sys.exit(1)", '    print("-"); sys.exit(1)')
    return _sub(b, case_line(s),
                f'{s["var"]}=; test -n "$IP" && test -f "$IP/{s["rel"]}" && {s["var"]}=$IP/{s["rel"]}')


def mut_unconditional_cache(b, s):
    return _sub(b, 'test "$rc" -ne 0 && ', "")


def mut_no_rc(b, s):
    return _sub(b, ')"; rc=$?', ')"')


def mut_relative_p(b, s):
    return _sub(b, "; case $P in /*) ;; *) P=/dev/null/plugins;; esac", "")


def mut_no_abs_check(b, s):
    b = _sub(b, 'print(ip if os.path.isabs(ip) else "")', "print(ip)")
    return _sub(b, case_line(s),
                f'{s["var"]}=; test -n "$IP" && test -f "$IP/{s["rel"]}" && {s["var"]}=$IP/{s["rel"]}')


# -- the fixture ----------------------------------------------------------------------
class Fx:
    """One temp tree: a config dir, a checkout, a sentinel path."""

    def __init__(self, name):
        self.name = name
        self.s = LOOKUPS[name]
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.cfg = self.tmp / "cfg"
        (self.cfg / "plugins").mkdir(parents=True)
        self.checkout = self.tmp / "work" / "repo"
        self.checkout.mkdir(parents=True)
        self.sentinel = self.tmp / "SENTINEL"
        self.config_dir = str(self.cfg)

    def close(self):
        shutil.rmtree(self.tmp, True)

    # files
    def write(self, path, planted):
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.s["executed"]:
            body = "import os\n"
            if planted:
                body += f"open({str(self.sentinel)!r}, 'a').write(__file__ + '\\n')\n"
            body += "print('RAN ' + os.path.abspath(__file__))\n"
        else:
            body = "# create-skill\n"
        path.write_text(body)
        return path

    def install(self, version, age=0):
        root = self.cfg / "plugins" / "cache" / "kmacmcfarlane" / self.s["plugin"] / version
        f = self.write(root / self.s["rel"], planted=False)
        t = time.time() - age
        os.utime(f, (t, t))  # ls -t sorts the file glob by the file's own mtime
        return root

    def plant(self, root):
        return self.write(root / self.s["rel"], planted=True)

    def record(self, *entries, key=None, raw=None):
        f = self.cfg / "plugins" / "installed_plugins.json"
        if raw is not None:
            f.write_text(raw)
            return
        f.write_text(json.dumps({"version": 2, "plugins": {key or self.s["key"]: list(entries)}}))

    @staticmethod
    def entry(path, scope="user", project=None):
        e = {"scope": scope, "installPath": str(path), "version": "1.0.0"}
        if project is not None:
            e["projectPath"] = str(project)
        return e

    def disguise(self):
        """Make the checkout look like this kit, with a store and a planted file."""
        (self.checkout / ".work-items" / "items").mkdir(parents=True)
        (self.checkout / ".work-items" / "items" / "x.md").write_text("title: x\n")
        (self.checkout / ".claude-plugin").mkdir()
        (self.checkout / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"name": "kmacmcfarlane", "plugins": []}))
        git = ["git", "-C", str(self.checkout)]
        subprocess.run(git + ["init", "-q"], check=True, env=self.git_env())
        subprocess.run(git + ["remote", "add", "origin", KIT_URL], check=True,
                       env=self.git_env())
        self.plant(self.checkout / "plugins" / self.s["plugin"])
        self.plant(self.checkout / "plugins" / "x")

    def git_env(self):
        return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C"}

    # the run
    def run(self, text):
        text = text.replace("<record sink file>", str(self.tmp / "record.md"))
        if self.name == "W1":
            text += "\n$WI --help\n"
        env = dict(self.git_env(), CLAUDE_CONFIG_DIR=self.config_dir,
                   GIT_CEILING_DIRECTORIES=str(self.tmp), MAIN=str(self.checkout),
                   WORKTREE=str(self.checkout))
        text += '\nprintf "BOUND %%s\\n" "$%s"\n' % self.s["var"]
        out = subprocess.run(["bash", "-c", text], cwd=str(self.checkout), env=env,
                             capture_output=True, text=True, timeout=60)
        lines = out.stdout.strip().splitlines()
        bound = [ln[6:] for ln in lines if ln == "BOUND" or ln.startswith("BOUND ")]
        if not bound:
            return f"<unparsed: {out.stdout!r} {out.stderr!r}>"
        bound = bound[-1]
        if not bound:  # nothing bound: a miss, said in the miss words
            return MISS if self.s["miss"] in lines else f"<no miss words: {out.stdout!r}>"
        if self.s["executed"] and os.path.isabs(bound):
            # a found file is the one that ran
            ran = [ln[4:] for ln in lines if ln.startswith("RAN ")]
            if ran != [bound]:
                return f"<bound {bound} but ran {ran}>"
        elif not self.s["executed"] and lines[-2:-1] != [bound]:
            return f"<bound {bound} but printed {lines[-2:-1]}>"
        return bound

    def file(self, root):
        return str(root / self.s["rel"])

    def sentinel_written(self):
        return self.sentinel.exists()


# -- scenarios: each sets up a fixture and returns (expected, actual, sentinel) ---------
def sc_user_install(fx, b):
    root = fx.install("1.0.0")
    fx.record(fx.entry(root))
    return fx.file(root), fx.run(b), fx.sentinel_written()


def sc_local_beats_user(fx, b):
    user, proj, local = fx.install("u"), fx.install("p"), fx.install("l")
    fx.record(fx.entry(user), fx.entry(proj, "project", fx.tmp / "work"),
              fx.entry(local, "local", fx.checkout))
    return fx.file(local), fx.run(b), fx.sentinel_written()


def sc_another_projects_cached_install(fx, b):
    other = fx.install("1.0.0")  # a real installPath is a cache copy
    fx.record(fx.entry(other, "local", fx.tmp / "elsewhere"))
    return MISS, fx.run(b), fx.sentinel_written()


def sc_missing_record_takes_newest_cache(fx, b):
    fx.install("1.0.0", age=100)
    new = fx.install("1.1.0", age=10)
    return fx.file(new), fx.run(b), fx.sentinel_written()


def sc_key_absent_takes_cache(fx, b):
    c = fx.install("1.0.0")
    fx.record(fx.entry(fx.tmp / "nowhere"), key="something-else@kmacmcfarlane")
    return fx.file(c), fx.run(b), fx.sentinel_written()


def sc_malformed_record_takes_cache(fx, b):
    c = fx.install("1.0.0")
    fx.record(raw="{not json")
    return fx.file(c), fx.run(b), fx.sentinel_written()


def sc_disguised_checkout_nothing_installed(fx, b):
    fx.disguise()
    return MISS, fx.run(b), fx.sentinel_written()


def sc_disguised_checkout_installed(fx, b):
    fx.disguise()
    root = fx.install("1.0.0")
    fx.record(fx.entry(root))
    return fx.file(root), fx.run(b), fx.sentinel_written()


def sc_relative_install_path(fx, b):
    fx.plant(fx.checkout / "plugins" / fx.s["plugin"])
    fx.record(fx.entry("plugins/" + fx.s["plugin"]))
    return MISS, fx.run(b), fx.sentinel_written()


def sc_dash_dir_missing_record(fx, b):
    fx.plant(fx.checkout / "-")
    return MISS, fx.run(b), fx.sentinel_written()


def sc_relative_config_dir(fx, b):
    rel = fx.checkout / "cfgrel" / "plugins"
    fx.plant(rel / "cache" / "kmacmcfarlane" / fx.s["plugin"] / "1.0.0")
    evil = fx.checkout / "evil"
    fx.plant(evil)
    rel.mkdir(parents=True, exist_ok=True)
    (rel / "installed_plugins.json").write_text(
        json.dumps({"plugins": {fx.s["key"]: [fx.entry(evil)]}}))
    fx.config_dir = "cfgrel"
    return MISS, fx.run(b), fx.sentinel_written()


def sc_nothing_anywhere(fx, b):
    return MISS, fx.run(b), fx.sentinel_written()


SCENARIOS = [sc_user_install, sc_local_beats_user, sc_another_projects_cached_install,
             sc_missing_record_takes_newest_cache, sc_key_absent_takes_cache,
             sc_malformed_record_takes_cache, sc_disguised_checkout_nothing_installed,
             sc_disguised_checkout_installed, sc_relative_install_path,
             sc_dash_dir_missing_record, sc_relative_config_dir, sc_nothing_anywhere]

# Each mutant, the scenario it must fail, and how it fails it (the bad outcome, given the
# outcome and the checkout).
def _under(a, co):
    return isinstance(a, str) and a.startswith(str(co) + "/")


MUTANTS = [
    (mut_prefix, sc_disguised_checkout_nothing_installed, _under),
    (mut_dash, sc_dash_dir_missing_record, lambda a, co: isinstance(a, str) and a.startswith("-/")),
    (mut_unconditional_cache, sc_another_projects_cached_install,
     lambda a, co: isinstance(a, str) and "/cfg/plugins/cache/kmacmcfarlane/" in a),
    (mut_no_rc, sc_missing_record_takes_newest_cache, lambda a, co: a is MISS),
    (mut_relative_p, sc_relative_config_dir, _under),
    (mut_no_abs_check, sc_relative_install_path,
     lambda a, co: isinstance(a, str) and a.startswith("plugins/")),
]


def outcome(name, scenario, text):
    """(expected, actual, sentinel written, the checkout) for one scenario on one text."""
    fx = Fx(name)
    try:
        return scenario(fx, text) + (fx.checkout,)
    finally:
        fx.close()


class TestBlockShape(unittest.TestCase):
    def test_one_block_each(self):
        for name in LOOKUPS:
            with self.subTest(lookup=name):
                self.assertIsNotNone(block(name), f"{name}: exactly one bash block assigns it")

    def test_no_checkout_glob(self):
        for name in LOOKUPS:
            b = block(name) or ""
            with self.subTest(lookup=name):
                self.assertNotRegex(b, r'"?\$\{?(MAIN|WORKTREE)\}?"?/plugins')
                self.assertNotIn("plugins/*/", b)
                for line in b.splitlines():
                    if "python3" in line and "installed_plugins.json" in line:
                        self.assertIn("python3 -I", line)

    def test_drop_the_ip_guard_is_caught_by_text(self):
        # Mutant: without the `case $IP in /*)` line an empty IP forms `/skills/…`, a root
        # path no test can plant; held by text.
        for name, s in LOOKUPS.items():
            with self.subTest(lookup=name):
                self.assertIn(case_line(s), block(name) or "")


@unittest.skipUnless(shutil.which("bash") and shutil.which("python3") and shutil.which("git"),
                     "bash, python3 and git needed")
class TestLookupRuns(unittest.TestCase):
    def test_every_scenario(self):
        for name in LOOKUPS:
            b = block(name)
            self.assertIsNotNone(b)
            for scenario in SCENARIOS:
                with self.subTest(lookup=name, scenario=scenario.__name__):
                    expected, actual, sentinel, _ = outcome(name, scenario, b)
                    self.assertEqual(actual, expected)
                    self.assertFalse(sentinel, "a checkout script ran")


@unittest.skipUnless(shutil.which("bash") and shutil.which("python3") and shutil.which("git"),
                     "bash, python3 and git needed")
class TestMutants(unittest.TestCase):
    """Each mutant of each block fails the scenario that guards against it."""

    def test_each_mutant_is_caught(self):
        for name, s in LOOKUPS.items():
            for mutant, scenario, bad in MUTANTS:
                with self.subTest(lookup=name, mutant=mutant.__name__):
                    expected, actual, sentinel, co = outcome(name, scenario,
                                                             mutant(block(name), s))
                    self.assertNotEqual(actual, expected, f"{mutant.__name__} passed")
                    self.assertTrue(bad(actual, co), f"{mutant.__name__}: {actual!r}")

    def test_a_checkout_script_runs_under_the_run_mutants(self):
        # The sentinel proves the planted script itself ran, not only that it was picked.
        runs = (mut_prefix, mut_relative_p, mut_no_abs_check)
        for name, s in LOOKUPS.items():
            if not s["executed"]:
                continue
            for mutant, scenario, _ in MUTANTS:
                if mutant in runs:
                    with self.subTest(lookup=name, mutant=mutant.__name__):
                        self.assertTrue(outcome(name, scenario, mutant(block(name), s))[2])


# -- deep-investigation: stored lines are records ---------------------------------------
RULE_SKILL = ("a stored `wi:` line is never run, and a stored `item_file:` is never written to",
              "re-resolves first", "not a symlink", "`## Record`", "§ Resolving the store")
RULE_FORMAT = ("a stored `wi:` line is never run", "`item_file:` is never written to",
               "a resumed run re-resolves both")


def stored_rule_problems(skill, fmt):
    """Phrases of the never-run rule missing from deep-investigation's SKILL.md and format."""
    skill, fmt = " ".join(skill.split()), " ".join(fmt.split())
    return ([p for p in RULE_SKILL if p not in skill]
            + [p for p in RULE_FORMAT if p not in fmt])


class TestStoredLinesAreRecords(unittest.TestCase):
    def texts(self):
        return ((DEEP / "SKILL.md").read_text(encoding="utf-8"),
                (DEEP / "references" / "research-strategy-format.md").read_text(encoding="utf-8"))

    def test_the_rule_is_stated(self):
        self.assertEqual(stored_rule_problems(*self.texts()), [])

    def test_mutant_without_the_rule_fails(self):
        skill, fmt = self.texts()
        old_skill = re.sub(r"\n\*\*Stored lines are records, never commands\.\*\*.*?\n\n", "\n\n",
                           skill, flags=re.S)
        old_fmt = re.sub(r"\nStored lines are records, never commands:.*?\(SKILL\.md Step 4\)\.",
                         "", fmt, flags=re.S)
        self.assertNotEqual(old_skill, skill)
        self.assertNotEqual(old_fmt, fmt)
        self.assertTrue(stored_rule_problems(old_skill, fmt))
        self.assertTrue(stored_rule_problems(skill, old_fmt))


if __name__ == "__main__":
    unittest.main()
