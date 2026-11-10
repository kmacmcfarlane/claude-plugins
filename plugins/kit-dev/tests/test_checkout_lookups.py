"""Lookups of another plugin's script that never take it from the working checkout, run
(item 185f, F3).

Two plugins carry a copy of the `wi` lookup and have no skill-text suite of their own, so
their run tests live here (kit-dev reads other plugins' files by design):

- W3, context-guard's checkpoint SKILL.md § Reaching `wi`. The checkpoint runs it once per
  repo whose store it writes, from that repo, so a sibling repo it routes a finding to is a
  checkout like any other;
- W4, ralph's backlog-yaml SKILL.md, "Reaching `wi`", run before the two bridge commands.

Each runs one rule: the install record (the entry that applies to the checkout), then the
cache only when the record cannot answer (its read exits non-zero), and a hit only when it
is an absolute path. No path under the working checkout is ever used, so a checkout
disguised as this kit (marketplace name `kmacmcfarlane`, `origin` the kit's URL, a store, a
planted `wi.py`) never supplies the script. Both blocks are byte-equal to dev-flow's
canonical copy (dev-cycle's references/bindings.md § Store) when it sits beside them.

Also run: context-guard's operator-playbook.md lookup of its own `mark_checkpoint.py`, a
listed variant (it ranks the install record from the working directory and falls back to
the data dir's `current-hooks` link). It keeps `P` only when absolute, prints `installPath`
only when absolute, and runs the script only from an absolute path, so a planted
`hooks/mark_checkpoint.py` or `current-hooks/mark_checkpoint.py` under the working
directory never runs.

Each block is extracted and run under bash in a temp tree, with a fake config dir and a fake
checkout. A planted script writes a sentinel file when it runs. Every scenario is also run
against mutants of the block (the pre-fix checkout-first lines spliced back in, the plain
`test -n` guard with a printed `-`, an unconditional cache, no `rc`, no absolute `P`, no
absolute check; for the variant, no isabs print, no absolute `P`, an unguarded run), and
each mutant is shown to fail the scenario that guards against it.

Runs only in the source repo (it reads other plugins); in an isolated copy of kit-dev it
skips. Standard library only. Run from plugins/kit-dev:

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

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
IN_REPO = ((REPO / "README.md").is_file()
           and (REPO / ".claude-plugin" / "marketplace.json").is_file())
TOOLS = all(shutil.which(t) for t in ("bash", "python3", "git"))
KIT_URL = "https://github.com/kmacmcfarlane/claude-plugins.git"
MISS = None

CHECKPOINT = PLUGINS / "context-guard" / "skills" / "checkpoint" / "SKILL.md"
PLAYBOOK = PLUGINS / "context-guard" / "skills" / "checkpoint" / "references" / \
    "operator-playbook.md"
BACKLOG = PLUGINS / "ralph" / "skills" / "backlog-yaml" / "SKILL.md"
CANON = PLUGINS / "dev-flow" / "skills" / "dev-cycle" / "references" / "bindings.md"
DESCRIPTIONS = {"context-guard": PLUGINS / "context-guard" / ".claude-plugin" / "plugin.json",
                "ralph": PLUGINS / "ralph" / ".claude-plugin" / "plugin.json"}

WI = dict(var="WI_PY", key="work-items@kmacmcfarlane", plugin="work-items",
          rel="skills/work-items/scripts/wi.py", miss="no wi found", rank="$MAIN")
LOOKUPS = {"W3": dict(WI, file=CHECKPOINT), "W4": dict(WI, file=BACKLOG)}


def bash_blocks(path):
    return re.findall(r"^```bash\n(.*?)^```", path.read_text(encoding="utf-8"), re.S | re.M)


def wi_block(path):
    """The one fenced bash block of the file that assigns `WI_PY`."""
    hits = [b for b in bash_blocks(path) if re.search(r"^WI_PY=", b, re.M)]
    return hits[0] if len(hits) == 1 else None


def block(name):
    return wi_block(LOOKUPS[name]["file"])


# -- mutants: each returns the block with one guard undone ------------------------------
def _sub(text, old, new):
    if old not in text:
        raise AssertionError(f"mutant target not in block: {old!r}")
    return text.replace(old, new)


def case_line(s):
    return f'{s["var"]}=; case $IP in /*) test -f "$IP/{s["rel"]}" && {s["var"]}=$IP/{s["rel"]};; esac'


def plain_guard(s):
    return f'{s["var"]}=; test -n "$IP" && test -f "$IP/{s["rel"]}" && {s["var"]}=$IP/{s["rel"]}'


def mut_prefix(b, s):
    """The pre-fix lines: the checkout glob first, then `$IP/<rel>` unchecked."""
    old = (f'{s["var"]}=$(ls "{s["rank"]}"/plugins/*/{s["rel"]} 2>/dev/null | head -1)\n'
           f'test -n "${s["var"]}" || {s["var"]}="$IP/{s["rel"]}"')
    return _sub(b, case_line(s), old)


def mut_dash(b, s):
    """A heredoc that prints `-` on failure, read by a plain `test -n` guard."""
    b = _sub(b, "    sys.exit(1)", '    print("-"); sys.exit(1)')
    return _sub(b, case_line(s), plain_guard(s))


def mut_unconditional_cache(b, s):
    return _sub(b, 'test "$rc" -ne 0 && ', "")


def mut_no_rc(b, s):
    return _sub(b, ')"; rc=$?', ')"')


def mut_relative_p(b, s):
    return _sub(b, "; case $P in /*) ;; *) P=/dev/null/plugins;; esac", "")


def mut_no_abs_check(b, s):
    b = _sub(b, 'print(ip if os.path.isabs(ip) else "")', "print(ip)")
    return _sub(b, case_line(s), plain_guard(s))


# -- the fixture ----------------------------------------------------------------------
class Fx:
    """One temp tree: a config dir, a checkout, a sentinel path."""

    def __init__(self, s, plugin=None, rel=None):
        self.s = s
        self.plugin = plugin or s["plugin"]
        self.rel = rel or s["rel"]
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.cfg = self.tmp / "cfg"
        (self.cfg / "plugins").mkdir(parents=True)
        self.checkout = self.tmp / "work" / "repo"
        self.checkout.mkdir(parents=True)
        self.sentinel = self.tmp / "SENTINEL"
        self.config_dir = str(self.cfg)

    def close(self):
        shutil.rmtree(self.tmp, True)

    def write(self, path, planted):
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "import os\n"
        if planted:
            body += f"open({str(self.sentinel)!r}, 'a').write(__file__ + '\\n')\n"
        body += "print('RAN ' + os.path.abspath(__file__))\n"
        path.write_text(body)
        return path

    def install(self, version, age=0):
        root = self.cfg / "plugins" / "cache" / "kmacmcfarlane" / self.plugin / version
        f = self.write(root / self.rel, planted=False)
        t = time.time() - age
        os.utime(f, (t, t))  # ls -t sorts the file glob by the file's own mtime
        return root

    def plant(self, root):
        return self.write(root / self.rel, planted=True)

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

    def git_env(self):
        return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C"}

    def disguise(self, repo=None):
        """Make a checkout look like this kit, with a store and planted files."""
        repo = repo or self.checkout
        repo.mkdir(parents=True, exist_ok=True)
        (repo / ".work-items" / "items").mkdir(parents=True)
        (repo / ".work-items" / "items" / "x.md").write_text("title: x\n")
        (repo / ".claude-plugin").mkdir()
        (repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"name": "kmacmcfarlane", "plugins": []}))
        git = ["git", "-C", str(repo)]
        subprocess.run(git + ["init", "-q"], check=True, env=self.git_env())
        subprocess.run(git + ["remote", "add", "origin", KIT_URL], check=True,
                       env=self.git_env())
        self.plant(repo / "plugins" / self.plugin)
        self.plant(repo / "plugins" / "x")
        self.plant(repo / "-")

    def run_lookup(self, text):
        """Run a `wi` block, then `$WI --help`; the bound path, MISS, or a problem string."""
        text += "\n$WI --help\n" + 'printf "BOUND %s\\n" "$WI_PY"\n'
        env = dict(self.git_env(), CLAUDE_CONFIG_DIR=self.config_dir,
                   GIT_CEILING_DIRECTORIES=str(self.tmp))
        out = subprocess.run(["bash", "-c", text], cwd=str(self.checkout), env=env,
                             capture_output=True, text=True, timeout=60)
        lines = out.stdout.strip().splitlines()
        bound = [ln[6:] for ln in lines if ln == "BOUND" or ln.startswith("BOUND ")]
        if not bound:
            return f"<unparsed: {out.stdout!r} {out.stderr!r}>"
        bound = bound[-1]
        if not bound:
            return MISS if self.s["miss"] in lines else f"<no miss words: {out.stdout!r}>"
        if os.path.isabs(bound):
            ran = [ln[4:] for ln in lines if ln.startswith("RAN ")]
            if ran != [bound]:
                return f"<bound {bound} but ran {ran}>"
        return bound

    def file(self, root):
        return str(root / self.rel)

    def sentinel_written(self):
        return self.sentinel.exists()


# -- scenarios: each returns (expected, actual, sentinel written) -----------------------
def sc_user_install(fx, b):
    root = fx.install("1.0.0")
    fx.record(fx.entry(root))
    return fx.file(root), fx.run_lookup(b), fx.sentinel_written()


def sc_local_beats_user(fx, b):
    user, proj, local = fx.install("u"), fx.install("p"), fx.install("l")
    fx.record(fx.entry(user), fx.entry(proj, "project", fx.tmp / "work"),
              fx.entry(local, "local", fx.checkout))
    return fx.file(local), fx.run_lookup(b), fx.sentinel_written()


def sc_another_projects_cached_install(fx, b):
    other = fx.install("1.0.0")  # a real installPath is a cache copy
    fx.record(fx.entry(other, "local", fx.tmp / "elsewhere"))
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_missing_record_takes_newest_cache(fx, b):
    fx.install("1.0.0", age=100)
    new = fx.install("1.1.0", age=10)
    return fx.file(new), fx.run_lookup(b), fx.sentinel_written()


def sc_key_absent_takes_cache(fx, b):
    c = fx.install("1.0.0")
    fx.record(fx.entry(fx.tmp / "nowhere"), key="something-else@kmacmcfarlane")
    return fx.file(c), fx.run_lookup(b), fx.sentinel_written()


def sc_malformed_record_takes_cache(fx, b):
    c = fx.install("1.0.0")
    fx.record(raw="{not json")
    return fx.file(c), fx.run_lookup(b), fx.sentinel_written()


def sc_disguised_checkout_nothing_installed(fx, b):
    fx.disguise()
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_disguised_checkout_installed(fx, b):
    fx.disguise()
    root = fx.install("1.0.0")
    fx.record(fx.entry(root))
    return fx.file(root), fx.run_lookup(b), fx.sentinel_written()


def sc_sibling_repo(fx, b):
    """The checkpoint routes a finding to a sibling repo and runs the lookup from it: the
    session's own repo has a local install, the sibling none and a planted wi.py."""
    trusted = fx.tmp / "work" / "trusted"
    trusted.mkdir(parents=True)
    fx.record(fx.entry(fx.install("1.0.0"), "local", trusted))
    fx.disguise()  # the sibling, where the lookup runs
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_relative_install_path(fx, b):
    fx.plant(fx.checkout / "plugins" / fx.plugin)
    fx.record(fx.entry("plugins/" + fx.plugin))
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_dash_dir_missing_record(fx, b):
    fx.plant(fx.checkout / "-")
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_relative_config_dir(fx, b):
    rel = fx.checkout / "cfgrel" / "plugins"
    fx.plant(rel / "cache" / "kmacmcfarlane" / fx.plugin / "1.0.0")
    evil = fx.checkout / "evil"
    fx.plant(evil)
    rel.mkdir(parents=True, exist_ok=True)
    (rel / "installed_plugins.json").write_text(
        json.dumps({"plugins": {fx.s["key"]: [fx.entry(evil)]}}))
    fx.config_dir = "cfgrel"
    return MISS, fx.run_lookup(b), fx.sentinel_written()


def sc_nothing_anywhere(fx, b):
    return MISS, fx.run_lookup(b), fx.sentinel_written()


SCENARIOS = [sc_user_install, sc_local_beats_user, sc_another_projects_cached_install,
             sc_missing_record_takes_newest_cache, sc_key_absent_takes_cache,
             sc_malformed_record_takes_cache, sc_disguised_checkout_nothing_installed,
             sc_disguised_checkout_installed, sc_sibling_repo, sc_relative_install_path,
             sc_dash_dir_missing_record, sc_relative_config_dir, sc_nothing_anywhere]


def _under(a, co):
    return isinstance(a, str) and a.startswith(str(co) + "/")


# Each mutant, the scenario it must fail, and how it fails it.
MUTANTS = [
    (mut_prefix, sc_disguised_checkout_nothing_installed, _under),
    (mut_prefix, sc_sibling_repo, _under),
    (mut_dash, sc_dash_dir_missing_record, lambda a, co: isinstance(a, str) and a.startswith("-/")),
    (mut_unconditional_cache, sc_another_projects_cached_install,
     lambda a, co: isinstance(a, str) and "/cfg/plugins/cache/kmacmcfarlane/" in a),
    (mut_unconditional_cache, sc_sibling_repo,
     lambda a, co: isinstance(a, str) and "/cfg/plugins/cache/kmacmcfarlane/" in a),
    (mut_no_rc, sc_missing_record_takes_newest_cache, lambda a, co: a is MISS),
    (mut_relative_p, sc_relative_config_dir, _under),
    (mut_no_abs_check, sc_relative_install_path,
     lambda a, co: isinstance(a, str) and a.startswith("plugins/")),
]
RUN_MUTANTS = (mut_prefix, mut_relative_p, mut_no_abs_check)


def outcome(name, scenario, text):
    """(expected, actual, sentinel written, the checkout) for one scenario on one text."""
    fx = Fx(LOOKUPS[name])
    try:
        return scenario(fx, text) + (fx.checkout,)
    finally:
        fx.close()


@unittest.skipUnless(IN_REPO, "not in the source repo: the other plugins are not here")
class TestBlockShape(unittest.TestCase):
    def test_one_block_each(self):
        for name in LOOKUPS:
            with self.subTest(lookup=name):
                self.assertIsNotNone(block(name), f"{name}: exactly one bash block assigns it")

    def test_no_checkout_glob(self):
        for name in LOOKUPS:
            b = block(name) or ""
            with self.subTest(lookup=name):
                self.assertNotRegex(b, r'"?\$\{?(MAIN|WORKTREE|PWD)\}?"?/plugins')
                self.assertNotIn("plugins/*/", b)
                for line in b.splitlines():
                    if "python3" in line and "installed_plugins.json" in line:
                        self.assertIn("python3 -I", line)

    def test_drop_the_ip_guard_is_caught_by_text(self):
        # Without the `case $IP in /*)` line an empty IP forms `/skills/…`, a root path no
        # test can plant; held by text.
        for name, s in LOOKUPS.items():
            with self.subTest(lookup=name):
                self.assertIn(case_line(s), block(name) or "")


def copy_problems(canon, copies):
    """The names of the copies that are not byte-equal to the canonical block."""
    return [name for name, b in copies.items() if b != canon]


@unittest.skipUnless(IN_REPO and CANON.is_file(), "dev-flow's canonical copy is not here")
class TestByteEqualToTheCanonicalCopy(unittest.TestCase):
    def test_equal(self):
        canon = wi_block(CANON)
        self.assertIsNotNone(canon)
        self.assertEqual(copy_problems(canon, {n: block(n) for n in LOOKUPS}), [])

    def test_one_changed_byte_is_caught(self):
        canon = wi_block(CANON)
        for name in LOOKUPS:
            with self.subTest(lookup=name):
                b = block(name)
                bad = b.replace("head -1", "head -2", 1)
                self.assertNotEqual(bad, b)
                self.assertEqual(copy_problems(canon, {name: bad}), [name])


@unittest.skipUnless(IN_REPO and TOOLS, "the source repo, bash, python3 and git needed")
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


@unittest.skipUnless(IN_REPO and TOOLS, "the source repo, bash, python3 and git needed")
class TestLookupMutants(unittest.TestCase):
    """Each mutant of each block fails the scenario that guards against it."""

    def test_each_mutant_is_caught(self):
        for name, s in LOOKUPS.items():
            for mutant, scenario, bad in MUTANTS:
                with self.subTest(lookup=name, mutant=mutant.__name__,
                                  scenario=scenario.__name__):
                    expected, actual, _, co = outcome(name, scenario, mutant(block(name), s))
                    self.assertNotEqual(actual, expected, f"{mutant.__name__} passed")
                    self.assertTrue(bad(actual, co), f"{mutant.__name__}: {actual!r}")

    def test_a_checkout_script_runs_under_the_run_mutants(self):
        # The sentinel proves the planted script itself ran, not only that it was picked.
        for name, s in LOOKUPS.items():
            for mutant, scenario, _ in MUTANTS:
                if mutant in RUN_MUTANTS:
                    with self.subTest(lookup=name, mutant=mutant.__name__,
                                      scenario=scenario.__name__):
                        self.assertTrue(outcome(name, scenario, mutant(block(name), s))[2])


# -- the mark_checkpoint.py variant -----------------------------------------------------
MC = dict(key="context-guard@kmacmcfarlane", plugin="context-guard",
          rel="hooks/mark_checkpoint.py", miss="no mark_checkpoint.py found")


def mc_block():
    hits = [b for b in bash_blocks(PLAYBOOK) if re.search(r"^MC=", b, re.M)]
    return hits[0] if len(hits) == 1 else None


def mc_run(fx, text):
    """The script that ran (its absolute path), MISS on the miss words, or a problem."""
    text = text.replace("<session_id>", "s")
    env = dict(fx.git_env(), CLAUDE_CONFIG_DIR=fx.config_dir)
    out = subprocess.run(["bash", "-c", text], cwd=str(fx.checkout), env=env,
                         capture_output=True, text=True, timeout=60)
    lines = out.stdout.strip().splitlines()
    ran = [ln[4:] for ln in lines if ln.startswith("RAN ")]
    if len(ran) == 1:
        return ran[0]
    if not ran and lines == [MC["miss"]]:
        return MISS
    return f"<unparsed: {out.stdout!r} {out.stderr!r}>"


def data_dir(fx, name="context-guard-kmacmcfarlane"):
    d = fx.cfg / "plugins" / "data" / name / "current-hooks"
    return fx.write(d / "mark_checkpoint.py", planted=False)


def mc_user_install(fx, b):
    root = fx.install("1.0.0")
    fx.record(fx.entry(root))
    return fx.file(root), mc_run(fx, b), fx.sentinel_written()


def mc_data_dir_fallback(fx, b):
    f = data_dir(fx)
    return str(f), mc_run(fx, b), fx.sentinel_written()


def mc_relative_install_path(fx, b):
    fx.plant(fx.checkout / "plugins" / "context-guard")
    fx.record(fx.entry("plugins/context-guard"))
    f = data_dir(fx)
    return str(f), mc_run(fx, b), fx.sentinel_written()


def mc_nothing_but_a_planted_link(fx, b):
    fx.write(fx.checkout / "current-hooks" / "mark_checkpoint.py", planted=True)
    fx.plant(fx.checkout)  # hooks/mark_checkpoint.py under the working directory
    return MISS, mc_run(fx, b), fx.sentinel_written()


def mc_relative_config_dir(fx, b):
    rel = fx.checkout / "cfgrel" / "plugins"
    evil = fx.checkout / "evil"
    fx.plant(evil)
    rel.mkdir(parents=True)
    (rel / "installed_plugins.json").write_text(
        json.dumps({"plugins": {MC["key"]: [fx.entry(evil)]}}))
    fx.config_dir = "cfgrel"
    return MISS, mc_run(fx, b), fx.sentinel_written()


MC_SCENARIOS = [mc_user_install, mc_data_dir_fallback, mc_relative_install_path,
                mc_nothing_but_a_planted_link, mc_relative_config_dir]


def mc_mut_no_isabs(b):
    return _sub(b, 'print(ip if os.path.isabs(ip) else "")', "print(ip)")


def mc_mut_relative_p(b):
    return _sub(b, "; case $P in /*) ;; *) P=/dev/null/plugins;; esac", "")


def mc_mut_unguarded_run(b):
    return _sub(b, 'case $MC in /*) python3 "$MC" <session_id>;; *) echo "no mark_checkpoint.py found";; esac',
                'python3 "$MC" <session_id>')


def mc_mut_no_isabs_unguarded(b):
    return mc_mut_unguarded_run(mc_mut_no_isabs(b))


# Each mutant, the scenario it fails, and whether a planted script then runs. Without the
# isabs print alone, the relative installPath wins over the data dir and the run guard
# refuses it (the scenario fails, nothing runs); with the run guard gone too, it runs.
MC_MUTANTS = [(mc_mut_no_isabs, mc_relative_install_path, False),
              (mc_mut_no_isabs_unguarded, mc_relative_install_path, True),
              (mc_mut_relative_p, mc_relative_config_dir, True),
              (mc_mut_unguarded_run, mc_nothing_but_a_planted_link, True)]


def mc_outcome(scenario, text):
    fx = Fx(MC, plugin=MC["plugin"], rel=MC["rel"])
    try:
        return scenario(fx, text)
    finally:
        fx.close()


@unittest.skipUnless(IN_REPO and TOOLS, "the source repo, bash, python3 and git needed")
class TestMarkCheckpointVariant(unittest.TestCase):
    def test_one_block(self):
        self.assertIsNotNone(mc_block())

    def test_every_scenario(self):
        for scenario in MC_SCENARIOS:
            with self.subTest(scenario=scenario.__name__):
                expected, actual, sentinel = mc_outcome(scenario, mc_block())
                self.assertEqual(actual, expected)
                self.assertFalse(sentinel, "a working-directory script ran")

    def test_each_mutant_is_caught(self):
        for mutant, scenario, runs in MC_MUTANTS:
            with self.subTest(mutant=mutant.__name__):
                expected, actual, sentinel = mc_outcome(scenario, mutant(mc_block()))
                self.assertNotEqual(actual, expected, f"{mutant.__name__} passed")
                self.assertEqual(sentinel, runs, f"{mutant.__name__}: {actual!r}")


# -- the prose: the installed copy only -------------------------------------------------
OLD_PROSE = ("repo's own tree", "repo's tree", "repo tree")
NEW_PROSE = ("No path under the working checkout is ever used",
             "the cache only when the record cannot answer",
             "Each step guards against a path the checkout could supply",
             "No checkout file adds an install-record entry or a cache copy")


def prose_problems(texts):
    """(file, phrase) for each old phrase left or new phrase missing."""
    out = []
    for name, text in texts.items():
        flat = " ".join(text.split())
        out += [(name, "old: " + p) for p in OLD_PROSE if p in flat]
        if name in ("W3", "W4"):
            out += [(name, "missing: " + p) for p in NEW_PROSE if p not in flat]
    return out


def prose_texts():
    texts = {"W3": CHECKPOINT.read_text(encoding="utf-8"),
             "W4": BACKLOG.read_text(encoding="utf-8")}
    for name, path in DESCRIPTIONS.items():
        texts[name] = json.loads(path.read_text(encoding="utf-8"))["description"]
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
    for p in market["plugins"]:
        if p["name"] in DESCRIPTIONS:
            texts["marketplace " + p["name"]] = p.get("description", "")
    return texts


@unittest.skipUnless(IN_REPO, "not in the source repo: the other plugins are not here")
class TestTheProse(unittest.TestCase):
    def test_installed_copy_only(self):
        self.assertEqual(prose_problems(prose_texts()), [])

    def test_mutant_with_the_old_sentence_fails(self):
        texts = prose_texts()
        texts["W3"] = texts["W3"].replace(
            "taken from the installed copy:",
            "found from the repo's own tree when it carries that plugin, else from the "
            "installed copy:")
        texts["ralph"] += " found in the repo's tree or the installed plugin"
        problems = prose_problems(texts)
        self.assertIn(("W3", "old: repo's own tree"), problems)
        self.assertIn(("ralph", "old: repo's tree"), problems)

    def test_mutant_without_the_rule_fails(self):
        texts = prose_texts()
        texts["W4"] = " ".join(texts["W4"].split()).replace("No path under the working",
                                                             "A path under the working")
        self.assertIn(("W4", "missing: No path under the working checkout is ever used"),
                      prose_problems(texts))


if __name__ == "__main__":
    unittest.main()
