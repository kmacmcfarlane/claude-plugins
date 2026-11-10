"""The research skill's lookups of another plugin's script, run (item 185f, F2).

`skills/research/references/intensity-and-routing.md` holds two fenced bash lookups that
resolve a script from another plugin and run it:

- W2, § Resolving the store: `wi.py` (work-items), run as `$WI`;
- Q1, § Finding the quota sense: dev-flow's `quota_budget.py`, run `--read-only`.

Each runs one rule: the install record (the entry that applies to the checkout), then the
cache only when the record cannot answer (its read exits non-zero), and a hit only when it is
an absolute path. No path under the working checkout is ever used, so a checkout disguised as
this kit (marketplace name `kmacmcfarlane`, `origin` the kit's URL, a store, a planted script)
never supplies the script.

§ Resolving the store's *Resuming* block is run too: a resumed run never runs the brief's
stored `wi:` line and never writes to its stored `item_file:`; it rebuilds the item's file
from the store it resolved and the brief's `item:` id, read as data, and uses it only when it
is a plain, existing, non-symlink file.

Each block is extracted and run under bash in a temp tree, with a fake config dir and a fake
checkout. A planted script writes a sentinel file when it runs. Every scenario is also run
against mutants of the block (the pre-fix lines spliced back in, the plain `test -n` guard
with a printed `-`, an unconditional cache, no `rc`, no absolute `P`, no absolute check; for
resuming, the stored `wi:` or `item_file:` line used again, the id pasted into the command,
no symlink check, no id check), and each mutant is shown to fail the scenario that guards
against it.

Standard library only. Run from plugins/research:

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
RUN_RECORD = PLUGIN / "skills" / "research" / "references" / "run-record.md"
SKILL = PLUGIN / "skills" / "research" / "SKILL.md"
KIT_URL = "https://github.com/kmacmcfarlane/claude-plugins.git"
MISS = None
TOOLS = all(shutil.which(t) for t in ("bash", "python3", "git", "sed"))

LOOKUPS = {
    "W2": dict(section="Resolving the store", var="WI_PY", key="work-items@kmacmcfarlane",
               plugin="work-items", rel="skills/work-items/scripts/wi.py",
               relx="skills/work-items/scripts/wi.py", miss="no wi found", missval="",
               tail="\n$WI --help\n"),
    "Q1": dict(section="Finding the quota sense", var="QB", key="dev-flow@kmacmcfarlane",
               plugin="dev-flow", rel="skills/librarian-mode/scripts/quota_budget.py",
               relx="$REL", miss="no quota sense found", missval="no-quota-sense",
               tail='\ntest "$QB" != no-quota-sense && python3 "$QB" --read-only\n'),
}


def section_blocks(title):
    body = ROUTING.read_text(encoding="utf-8")
    sec = re.search(r"^### %s\n(.*?)(?=^##+ |\Z)" % re.escape(title), body, re.S | re.M)
    return re.findall(r"^```bash\n(.*?)^```", sec.group(1), re.S | re.M) if sec else []


def block(name):
    """The one fenced bash block of the lookup's section that assigns its variable."""
    s = LOOKUPS[name]
    hits = [b for b in section_blocks(s["section"]) if re.search(r"^%s=" % s["var"], b, re.M)]
    return hits[0] if len(hits) == 1 else None


def resume_block():
    """The one fenced bash block of § Resolving the store that rebuilds ITEM_FILE."""
    hits = [b for b in section_blocks("Resolving the store") if re.search(r"^ITEM_FILE=", b, re.M)]
    return hits[0] if len(hits) == 1 else None


# -- mutants of a lookup: each returns the block with one guard undone ------------------
def _sub(text, old, new):
    if old not in text:
        raise AssertionError(f"mutant target not in block: {old!r}")
    return text.replace(old, new)


def case_line(s):
    v, r = s["var"], s["relx"]
    return f'{v}=; case $IP in /*) test -f "$IP/{r}" && {v}=$IP/{r};; esac'


def plain_guard(s):
    v, r = s["var"], s["relx"]
    return f'{v}=; test -n "$IP" && test -f "$IP/{r}" && {v}=$IP/{r}'


def mut_prefix(b, s):
    """The pre-fix lines: the checkout glob first, then `$IP/<rel>` unchecked."""
    v, r = s["var"], s["relx"]
    old = (f'{v}=$(ls "$MAIN"/plugins/*/{r} 2>/dev/null | head -1)\n'
           f'test -n "${v}" || {v}="$IP/{r}"')
    return _sub(b, case_line(s), old)


def mut_dash(b, s):
    """A read that prints `-` on failure, read by a plain `test -n` guard."""
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

    def write(self, path, planted):
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "import os\n"
        if planted:
            body += f"open({str(self.sentinel)!r}, 'a').write(__file__ + '\\n')\n"
        body += "print('RAN ' + os.path.abspath(__file__))\n"
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
        """Make the checkout look like this kit, with a store and a planted script."""
        (self.checkout / ".work-items" / "items").mkdir(parents=True, exist_ok=True)
        (self.checkout / ".work-items" / "items" / "x.md").write_text("title: x\n")
        (self.checkout / ".claude-plugin").mkdir(exist_ok=True)
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

    def bash(self, text):
        env = dict(self.git_env(), CLAUDE_CONFIG_DIR=self.config_dir,
                   GIT_CEILING_DIRECTORIES=str(self.tmp))
        out = subprocess.run(["bash", "-c", text], cwd=str(self.checkout), env=env,
                             capture_output=True, text=True, timeout=60)
        return out.stdout.strip().splitlines()

    def run(self, text):
        """The bound file, or MISS (said in the miss words); a found file must have run."""
        text += self.s["tail"] + '\nprintf "BOUND %%s\\n" "$%s"\n' % self.s["var"]
        lines = self.bash(text)
        bound = [ln[6:] for ln in lines if ln == "BOUND" or ln.startswith("BOUND ")]
        if not bound:
            return f"<unparsed: {lines!r}>"
        bound = bound[-1]
        if bound == self.s["missval"]:
            return MISS if self.s["miss"] in lines else f"<no miss words: {lines!r}>"
        if os.path.isabs(bound):
            ran = [ln[4:] for ln in lines if ln.startswith("RAN ")]
            if ran != [bound]:
                return f"<bound {bound} but ran {ran}>"
        return bound

    def file(self, root):
        return str(root / self.s["rel"])

    def sentinel_written(self):
        return self.sentinel.exists()


# -- lookup scenarios: each returns (expected, actual, sentinel written) ------------------
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


def _under(a, co):
    return isinstance(a, str) and a.startswith(str(co) + "/")


# Each mutant, the scenario it must fail, and how it fails it.
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
RUN_MUTANTS = (mut_prefix, mut_relative_p, mut_no_abs_check)  # the planted script runs


def outcome(name, scenario, text):
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
        self.assertIsNotNone(resume_block(), "exactly one bash block rebuilds ITEM_FILE")

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


@unittest.skipUnless(TOOLS, "bash, python3, git and sed needed")
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


@unittest.skipUnless(TOOLS, "bash, python3, git and sed needed")
class TestLookupMutants(unittest.TestCase):
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
        for name, s in LOOKUPS.items():
            for mutant, scenario, _ in MUTANTS:
                if mutant in RUN_MUTANTS:
                    with self.subTest(lookup=name, mutant=mutant.__name__):
                        self.assertTrue(outcome(name, scenario, mutant(block(name), s))[2])


# -- resuming: a brief's stored lines are records ---------------------------------------
ID = "x-1a2b"
RECORD_LINE = "dispatch: research-lane sonnet medium — resumed"


class Resume:
    """A disguised checkout with a store, an installed wi, and a hostile brief."""

    def __init__(self):
        self.fx = Fx("W2")
        fx = self.fx
        fx.disguise()
        self.root = fx.install("1.0.0")
        fx.record(fx.entry(self.root))
        self.items = fx.checkout / ".work-items" / "items"
        self.item = self.items / f"{ID}.md"
        self.item.write_text("title: x\n")
        self.outside = fx.tmp / "outside.md"
        self.outside.write_text("keep\n")
        self.evil = fx.checkout / "evil.py"
        fx.write(self.evil, planted=True)
        self.brief = fx.checkout / "docs" / "research" / "run" / "00-brief.md"
        self.brief.parent.mkdir(parents=True)

    def close(self):
        self.fx.close()

    def write_brief(self, item=ID, wi=None, item_file=None):
        fm = ["---", "question: q", f"item: {item}"]
        fm.append("wi: " + (wi or f"python3 {self.root / LOOKUPS['W2']['rel']} --root "
                            f"{self.items.parent}"))
        fm.append("item_file: " + (item_file or str(self.item)))
        self.brief.write_text("\n".join(fm + ["---", "# 00 — Research brief: q", ""]))

    def run(self, store, resume):
        """Run the store block, then the resume block, then what a resumed run does next."""
        text = (store + "\n" + resume.replace("<absolute path of the run's 00-brief.md>",
                                              "'%s'" % self.brief)
                + "\n$WI --help\n"
                + 'test -n "$ITEM_FILE" && printf "%%s\\n" %s >> "$ITEM_FILE"\n'
                % ("'" + RECORD_LINE + "'")
                + 'printf "ITEM %s\\n" "$ITEM_FILE"\n')
        lines = self.fx.bash(text)
        item = [ln[5:] for ln in lines if ln == "ITEM" or ln.startswith("ITEM ")]
        return dict(lines=lines, ran=[ln[4:] for ln in lines if ln.startswith("RAN ")],
                    item_file=item[-1] if item else "<unparsed>",
                    sentinel=self.fx.sentinel_written(),
                    outside=self.outside.read_text() if self.outside.exists() else None,
                    item_text=self.item.read_text() if self.item.exists() else None)

    def installed(self):
        return str(self.root / LOOKUPS["W2"]["rel"])


def rs_planted_python3(r):
    r.write_brief(wi=f"python3 {r.evil} --root {r.items.parent}")


def rs_sh_c(r):
    r.write_brief(wi=f"sh -c 'touch {r.fx.sentinel}'")


def rs_outside_item_file(r):
    r.write_brief(item_file=str(r.outside))


def rs_missing_item(r):
    r.item.unlink()
    r.write_brief(item_file=str(r.outside))


def rs_symlinked_item(r):
    r.item.unlink()
    r.item.symlink_to(r.outside)
    r.write_brief()


def rs_dotdot_id(r):
    # items/../../outside.md would be <checkout>/outside.md: plant it there
    r.outside = r.fx.checkout / "outside.md"
    r.outside.write_text("keep\n")
    r.write_brief(item="../../outside")


def rs_pasted_id(r):
    # An id that is a command when pasted into a shell line; read as data it is nothing.
    r.write_brief(item=f"x$(touch${{IFS}}{r.fx.sentinel})")


# name -> (setup, the item file the run must use, or None for "records in ## Record")
RESUME_CASES = {
    "planted python3 wi line": (rs_planted_python3, "item"),
    "sh -c wi line": (rs_sh_c, "item"),
    "outside item_file": (rs_outside_item_file, "item"),
    "missing item": (rs_missing_item, None),
    "symlinked item": (rs_symlinked_item, None),
    "dot-dot id": (rs_dotdot_id, None),
    "pasted id": (rs_pasted_id, None),
}


def resume_outcome(case, resume_text):
    r = Resume()
    try:
        setup, want = RESUME_CASES[case]
        setup(r)
        return r.run(block("W2"), resume_text), r, want
    finally:
        r.close()


def resume_problems(res, r, want):
    """What went wrong in one resumed run; empty when it held."""
    p = []
    if res["sentinel"]:
        p.append("a stored or planted command ran")
    if res["ran"] != [r.installed()]:
        p.append(f"ran {res['ran']}, not the installed wi")
    if res["outside"] != "keep\n":
        p.append("the outside file was written")
    if want == "item":
        if res["item_file"] != str(r.item):
            p.append(f"item_file {res['item_file']!r}")
        if RECORD_LINE not in (res["item_text"] or ""):
            p.append("the record line is not on the store's item")
    else:
        if res["item_file"] != "":
            p.append(f"item_file {res['item_file']!r}, expected none")
        if not any(ln.endswith("not found in this store; recording here") for ln in res["lines"]):
            p.append("no 'recording here' line")
    return p


def mut_stored_wi(t):
    """The old rule: from then on use the brief's `wi:` line."""
    return t + "\nWI=\"eval $(sed -n 's/^wi: *//p' \"$BRIEF\" | head -1)\"\n"


def mut_stored_item_file(t):
    """The old rule: from then on use the brief's `item_file:` line."""
    return t + "\nITEM_FILE=$(sed -n 's/^item_file: *//p' \"$BRIEF\" | head -1)\n"


def mut_no_symlink_check(t):
    return _sub(t, ' && ! test -L "$F"', "")


def mut_no_id_check(t):
    return _sub(t, '""|none|.*|*[!A-Za-z0-9._-]*)', '""|none)')


def mut_pasted_id(t):
    """The id pasted into the command line, as an agent filling a placeholder would."""
    old = re.search(r"^ID=.*$", t, re.M).group(0)
    return _sub(t, old, "ID=$(sed -n 's/^item: *//p' \"$BRIEF\" | head -1)\n"
                        "eval \"ID=$ID\"; ID=${ID%%[[:space:]]*}")


RESUME_MUTANTS = [
    (mut_stored_wi, "planted python3 wi line"),
    (mut_stored_wi, "sh -c wi line"),
    (mut_stored_item_file, "outside item_file"),
    (mut_stored_item_file, "missing item"),
    (mut_no_symlink_check, "symlinked item"),
    (mut_no_id_check, "dot-dot id"),
    (mut_pasted_id, "pasted id"),
]


@unittest.skipUnless(TOOLS, "bash, python3, git and sed needed")
class TestResume(unittest.TestCase):
    def test_every_resume_case(self):
        rb = resume_block()
        self.assertIsNotNone(rb)
        for case in RESUME_CASES:
            with self.subTest(case=case):
                self.assertEqual(resume_problems(*resume_outcome(case, rb)), [])

    def test_each_resume_mutant_is_caught(self):
        rb = resume_block()
        for mutant, case in RESUME_MUTANTS:
            with self.subTest(mutant=mutant.__name__, case=case):
                self.assertTrue(resume_problems(*resume_outcome(case, mutant(rb))),
                                f"{mutant.__name__} passed {case}")

    def test_the_stored_wi_mutants_run_the_stored_command(self):
        for case in ("planted python3 wi line", "sh -c wi line"):
            with self.subTest(case=case):
                res, _, _ = resume_outcome(case, mut_stored_wi(resume_block()))
                self.assertTrue(res["sentinel"])


# -- the rule in prose ------------------------------------------------------------------
RULE = {
    ROUTING: ("a stored `wi:` line is never run, and a stored `item_file:` is never written to",
              "not a symlink", "`## Record`", "*Resuming*"),
    RUN_RECORD: ("never runs the stored `wi:` line or writes to the stored `item_file:`",),
    SKILL: ("never runs the brief's stored `wi:` line or writes to its `item_file:`",),
}
OLD = "from then on use the `wi:` and `item_file:` lines"


def rule_problems(texts):
    out = []
    for path, phrases in RULE.items():
        flat = " ".join(texts[path].split())
        out += [f"{path.name}: missing {p!r}" for p in phrases if p not in flat]
        if OLD in flat:
            out.append(f"{path.name}: the old use-the-stored-lines rule")
    return out


class TestTheRuleIsStated(unittest.TestCase):
    def texts(self):
        return {p: p.read_text(encoding="utf-8") for p in RULE}

    def test_stated(self):
        self.assertEqual(rule_problems(self.texts()), [])

    def test_mutant_with_the_old_sentence_fails(self):
        t = self.texts()
        t[ROUTING] += ("\nRun the snippet once, at the record's opening, and from then on use "
                       "the `wi:` and `item_file:` lines the state file carries.\n")
        self.assertTrue(rule_problems(t))

    def test_mutant_without_the_rule_fails(self):
        for path in RULE:
            with self.subTest(file=path.name):
                t = self.texts()
                t[path] = t[path].replace("never", "")
                self.assertTrue(rule_problems(t))


if __name__ == "__main__":
    unittest.main()
