"""checkout_guard.py --status tests (item 7f9c, F3): the status mode is run as
a subprocess against real temp git repos, the way a skill runs it.

Each check takes a hooks directory and returns its problems, so it runs
against the shipped hooks and against a mutant copy (one edit to
checkout_guard.py or checkout_notice.py). TestStatus asserts every check is
clean on the shipped hooks; TestStatusMutants asserts each mutant in MUTANTS
makes its check fail.

Parity: `--path` gives the hook's verdict for the same input, and judge_path's
code; the session line says `on` exactly when the notice speaks, except when
the rules allow every file (the notice is silent, the session line still
`on`: it reports the working directory, not the rules).

Mutants: status reads stdin; `--path` lets the rules file's denials through;
`off` printed as `on`; the off word dropped; `<top>` unescaped; a relative
--cwd taken as given; an error escaping on a deleted working directory; the
working directory read for an absolute --cwd; a relative --path resolved
against the process's directory; a duplicate option accepted; a code renamed
in the code only; a code renamed in SKILL.md only; the rules sentence dropped
from SKILL.md; the notice speaking with the override set.
"""
import contextlib, json, os, re, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

import test_checkout_notice as tn

HOOKS = tn.HOOKS
sys.path.insert(0, HOOKS)
import checkout_guard as cg  # noqa: E402
SKILL = os.path.join(os.path.dirname(HOOKS), "skills", "sandbox", "SKILL.md")
SKILL_CMD = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/checkout_guard.py" --status'
CODES_LEAD = "The codes, frozen:"
RULES_SENTENCE = (
    "The session line reports the working directory's state, not the rules "
    "file: a main checkout whose rules allow every file still prints "
    "`on main-checkout`. `--path` gives the verdict for one file, rules "
    "included.")
OFF_WORDS = ("override", "not-git", "linked-worktree")
RULE_SETS = (("none", None), ("partial", "allow issues/**\n"),
             ("broken", "allow [\n"), ("allow-all", "allow **\n"))
FILES = ("issues/x.md", "bin/tool", "new.txt", ".claude/allow-checkout-edits",
         ".claude/settings.json", "../outside.txt", "")
REL_FILES = ("bin/tool",)  # handed over relative: resolved against --cwd


def run_status(hooks, args, cwd=None, env=None):
    p = subprocess.run(
        [sys.executable, os.path.join(hooks, "checkout_guard.py")] + args,
        cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        env=tn.scrubbed(env), timeout=30)
    return p.returncode, p.stdout, p.stderr


def hook_verdict(hooks, cwd, path, env):
    payload = {"tool_name": "Edit", "cwd": cwd, "tool_input": {}}
    if path:
        payload["tool_input"]["file_path"] = path
    _, so = tn.run_hook(hooks, "checkout_guard.py", json.dumps(payload), env)
    return "denied" if '"deny"' in so else "allowed"


@contextlib.contextmanager
def proc_env(env):
    with mock.patch.dict(os.environ):
        for k in tn.SCRUB:
            os.environ.pop(k, None)
        os.environ.update(env)
        yield


def skill_codes(text):
    """The backticked words of SKILL.md's frozen code sentence."""
    m = re.search(re.escape(CODES_LEAD) + r"(.*?)\.(\s|$)", text, re.S)
    return re.findall(r"`([^`]+)`", m.group(1)) if m else None


class Fixture(tn.Fixture):
    def cwds(self):
        """(label, cwd, env, the session line wanted)."""
        on = "on main-checkout " + self.repo
        return (
            ("main", self.repo, {}, on),
            ("main subdir", os.path.join(self.repo, "issues"), {}, on),
            ("worktree", self.wt, {}, "off linked-worktree"),
            ("non-git", self.plain, {}, "off not-git"),
            ("git absent", self.repo,
             {"PATH": os.path.join(self.base, "nobin")}, "off not-git"),
            ("git broken", self.repo,
             {"GIT_DIR": os.path.join(self.base, "no.git")}, "off not-git"),
            ("override", self.repo, {"SANDBOX_ALLOW_CHECKOUT_EDITS": "1"},
             "off override"),
            ("override alias", self.repo,
             {"CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "1"}, "off override"),
            ("override not 1", self.repo,
             {"SANDBOX_ALLOW_CHECKOUT_EDITS": "true"}, on),
        )

    # --- the checks: each returns a list of problems ------------------------

    def check_session_lines(self, hooks):
        out = []
        self.rules(None)
        for label, cwd, env, want in self.cwds():
            for how, args, pcwd in (
                    ("--cwd", ["--status", "--cwd", cwd], None),
                    ("--cwd=", ["--status", "--cwd=" + cwd], None),
                    ("process cwd", ["--status"], cwd),
                    ("relative --cwd", ["--cwd", os.path.relpath(cwd, self.base),
                                        "--status"], self.base)):
                got = run_status(hooks, args, pcwd, env)
                if got != (0, want + "\n", ""):
                    out.append((label, how, got, want))
        return out

    def check_escaped_top(self, hooks):
        top = tn.make_repo(os.path.join(self.base, "x" + tn.PATH_SPECIALS + "y"))
        rc, so, _ = run_status(hooks, ["--status", "--cwd", top])
        shutil.rmtree(top)
        want = "x" + "".join(tn.ESCAPES[c] for c in tn.PATH_SPECIALS) + "y"
        if (rc, so) != (0, "on main-checkout %s/%s\n" % (self.base, want)):
            return [("escaped top", rc, so)]
        return []

    def check_deleted_cwd(self, hooks):
        """A deleted working directory: still exit 0 and one line; an absolute
        --cwd is still answered."""
        out = []
        gone = os.path.join(self.base, "gone")
        script = os.path.join(hooks, "checkout_guard.py")
        for args, want in (([], "off not-git\n"),
                           (["--cwd", "rel"], "off not-git\n"),
                           (["--path", "x"], "off not-git\n"),
                           (["--cwd", self.repo],
                            "on main-checkout %s\n" % self.repo)):
            os.makedirs(gone)
            p = subprocess.run(
                ["sh", "-c", 'cd "$1" && rmdir "$1" && shift && exec "$@"',
                 "sh", gone, sys.executable, script, "--status"] + args,
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                env=tn.scrubbed({}), timeout=30)
            if (p.returncode, p.stdout) != (0, want):
                out.append((args, p.returncode, p.stdout, p.stderr[-200:]))
            if os.path.isdir(gone):
                os.rmdir(gone)
        return out

    def check_bad_args(self, hooks):
        out = []
        for args in (["--stat"], ["--status", "--path"], ["--status", "x"],
                     ["--status", "--status"], ["--cwd", self.repo],
                     ["--status=1"], ["--status", "--cwd", "a", "--cwd", "b"],
                     ["--status", "--path=a", "--path", "b"], ["-h"]):
            rc, so, se = run_status(hooks, args, self.repo)
            if rc != 2 or so or not se.startswith("usage: checkout_guard.py "
                                                  "--status"):
                out.append((args, rc, so, se[:80]))
        return out

    def check_no_stdin(self, hooks):
        """Run with stdin a pipe that never closes: status must not wait."""
        p = subprocess.Popen(
            [sys.executable, os.path.join(hooks, "checkout_guard.py"),
             "--status", "--cwd", self.repo], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=tn.scrubbed({}))
        try:
            p.wait(timeout=10)
            so = p.stdout.read().decode()
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            return [("waited on stdin",)]
        finally:
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
        return [] if so == "on main-checkout %s\n" % self.repo else [("out", so)]

    def path_parity(self, hooks, cwds=None, rule_sets=RULE_SETS):
        """Over cwd states x rules files x files: `--path`'s verdict is the
        hook's, and its code is judge_path's."""
        out = []
        for label, cwd, env, _ in cwds or self.cwds():
            for rname, rules in rule_sets:
                self.rules(rules)
                for rel in FILES + tuple("rel:" + f for f in REL_FILES):
                    path = (rel[4:] if rel.startswith("rel:") else
                            os.path.join(cwd, rel) if rel else "")
                    rc, so, _ = run_status(
                        hooks, ["--status", "--cwd", cwd, "--path=" + path],
                        env=env)
                    hook = hook_verdict(hooks, cwd, path, env)
                    with proc_env(env):
                        allowed, code, _ = cg.judge_path(cwd, path)
                    want = "%s %s\n" % ("allowed" if allowed else "denied",
                                        code)
                    if (rc, so) != (0, want) or so.split(" ")[0] != hook:
                        out.append((label, rname, rel, so, want, hook))
        self.rules(None)
        return out

    def on_iff_notice(self, hooks):
        """The session line says `on` exactly when the notice speaks, rules
        allowing every file aside; when both speak they name one top."""
        out = []
        for label, cwd, env, _ in self.cwds():
            for rname, rules in RULE_SETS:
                self.rules(rules)
                _, so, _ = run_status(hooks, ["--status", "--cwd", cwd],
                                      env=env)
                for event in tn.EVENTS:
                    text = tn.context(tn.run_notice(hooks, cwd, event,
                                                    env)[1])
                    on = so.startswith("on ")
                    want = on and rname != "allow-all"
                    if (text is not None) != want:
                        out.append((label, rname, event, so, text is not None))
                    elif text is not None and not text.startswith(
                            "sandbox checkout guard: `%s` " % so[17:-1]):
                        out.append((label, rname, event, "top differs"))
        self.rules(None)
        return out

    def check_skill_words(self, hooks, skill_text=None):
        """SKILL.md's frozen code list equals CODES, it names the off words
        and the guarded command, and holds the rules sentence."""
        if skill_text is None:
            with open(SKILL) as f:
                skill_text = f.read()
        out = []
        codes = tn.module_eval(hooks, "list(cg.CODES)")
        words = skill_codes(skill_text)
        if words != codes:
            out.append(("codes", words, codes))
        if "```bash\n%s\n```" % SKILL_CMD not in skill_text:
            out.append(("command",))
        for w in OFF_WORDS:
            if "`off %s`" % w not in skill_text:
                out.append(("off word", w))
        if RULES_SENTENCE not in skill_text:
            out.append(("rules sentence",))
        return out


class TestStatus(Fixture):
    def test_session_lines(self):
        self.assertEqual(self.check_session_lines(HOOKS), [])

    def test_escaped_top(self):
        self.assertEqual(self.check_escaped_top(HOOKS), [])

    def test_bad_args(self):
        self.assertEqual(self.check_bad_args(HOOKS), [])

    def test_deleted_cwd(self):
        self.assertEqual(self.check_deleted_cwd(HOOKS), [])

    def test_never_reads_stdin(self):
        self.assertEqual(self.check_no_stdin(HOOKS), [])

    def test_path_parity_with_the_hook(self):
        self.assertEqual(self.path_parity(HOOKS), [])

    def test_on_exactly_when_the_notice_speaks(self):
        self.assertEqual(self.on_iff_notice(HOOKS), [])

    def test_skill_words(self):
        self.assertEqual(self.check_skill_words(HOOKS), [])

    def test_hook_mode_unchanged_without_arguments(self):
        # No arguments: the hook, which reads stdin (garbage fails open).
        rc, so = tn.run_hook(HOOKS, "checkout_guard.py", "not json")
        self.assertEqual((rc, so), (0, "{}\n"))


# (label, file, old, new, check): `check` is a method name; a file of None
# mutates SKILL.md's text, handed to the check, instead of a hooks file.
MUTANTS = (
    ("status reads stdin", "checkout_guard.py",
     "    opts = parse_status_args(argv)\n",
     "    sys.stdin.read()\n    opts = parse_status_args(argv)\n",
     "check_no_stdin"),
    ("--path lets the rules file's denials through", "checkout_guard.py",
     "        allowed, code, _ = judge_path(cwd, path, env)\n",
     "        allowed, code, _ = judge_path(cwd, path, env)\n"
     "        allowed = allowed or code in (\"rules\", \"broken\")\n",
     "path_parity"),
    ("off printed as on", "checkout_guard.py",
     'return "off " + state.why', 'return "on " + state.why',
     "check_session_lines"),
    ("off printed as on (notice parity)", "checkout_guard.py",
     'return "off " + state.why', 'return "on " + state.why',
     "on_iff_notice"),
    ("off word dropped", "checkout_guard.py",
     'return "off " + state.why', 'return "off"', "check_session_lines"),
    ("top unescaped", "checkout_guard.py",
     'return "on main-checkout " + escape_path(state.top)',
     'return "on main-checkout " + state.top', "check_escaped_top"),
    ("relative --cwd taken as given", "checkout_guard.py",
     'cwd = os.path.join(os.getcwd(), cwd or "")',
     'cwd = os.path.join("/", cwd or "")', "check_session_lines"),
    ("an error escapes status_main", "checkout_guard.py",
     '    except Exception:\n        line = "off not-git"',
     '    except ZeroDivisionError:\n        line = "off not-git"',
     "check_deleted_cwd"),
    ("getcwd read even for an absolute --cwd", "checkout_guard.py",
     "        if not cwd or not os.path.isabs(cwd):\n",
     "        if os.getcwd() and (not cwd or not os.path.isabs(cwd)):\n",
     "check_deleted_cwd"),
    ("--path relative to the process cwd", "checkout_guard.py",
     '        line = status_line(cwd, opts.get("path"))',
     '        line = status_line(cwd, opts.get("path") and os.path.abspath('
     'opts["path"]))', "path_parity"),
    ("duplicate option accepted", "checkout_guard.py",
     "        if name in seen:\n            return None\n", "",
     "check_bad_args"),
    ("code renamed in the code only", "checkout_guard.py",
     '"outside", "exempt", "untracked", "rules", "broken")',
     '"outside", "exempt", "not-tracked", "rules", "broken")',
     "check_skill_words"),
    ("code renamed in SKILL.md only", None, "`untracked`", "`not-tracked`",
     "check_skill_words"),
    ("rules sentence dropped from SKILL.md", None, RULES_SENTENCE, "",
     "check_skill_words"),
    ("notice speaks with the override set", "checkout_notice.py",
     "state = cg.checkout_state(cwd, env)",
     "state = cg.checkout_state(cwd, {})", "on_iff_notice"),
)


class TestStatusMutants(Fixture):
    def hooks_copy(self):
        d = tempfile.mkdtemp(dir=self.base, prefix="mut")
        for f in ("checkout_guard.py", "checkout_notice.py"):
            shutil.copy(os.path.join(HOOKS, f), d)
        return d

    def test_each_mutant_is_caught(self):
        with open(SKILL) as f:
            skill = f.read()
        for label, name, old, new, check in MUTANTS:
            with self.subTest(mutant=label):
                d = self.hooks_copy()
                kw = {}
                if name is None:
                    self.assertEqual(skill.count(old), 1, label)
                    kw["skill_text"] = skill.replace(old, new)
                else:
                    p = os.path.join(d, name)
                    with open(p) as f:
                        src = f.read()
                    self.assertEqual(src.count(old), 1, label)
                    with open(p, "w") as f:
                        f.write(src.replace(old, new))
                if check == "path_parity":  # one cwd keeps it quick
                    kw["cwds"] = self.cwds()[:1]
                self.assertNotEqual(getattr(self, check)(d, **kw), [], label)
                shutil.rmtree(d)

    def test_unmutated_copy_passes(self):
        d = self.hooks_copy()
        for check in sorted({m[4] for m in MUTANTS}):
            self.assertEqual(getattr(self, check)(d), [], check)


if __name__ == "__main__":
    unittest.main()
