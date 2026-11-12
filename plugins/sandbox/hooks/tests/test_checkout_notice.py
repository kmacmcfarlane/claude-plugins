"""checkout_notice tests (item 7f9c, F2): the hook is run as a subprocess with a
SessionStart or SubagentStart JSON payload on stdin against real temp git
repos, the way Claude Code runs it.

Each check is a method that takes a hooks directory and returns its problems,
so the same check runs against the shipped hooks and against a mutant: a copy
of the hooks directory with one edit to checkout_notice.py or
checkout_guard.py. TestNotice asserts every check is clean on the shipped
hooks; TestNoticeMutants asserts each mutant in MUTANTS makes its check fail.

Mutants: the worktree test ignored; the override ignored; a notice on a git
error; hookEventName hard-coded to SessionStart; a relative path in the text;
no path cap; the cap measured before escaping; no escaping; escaping only
below U+0020; the backtick not escaped; the rules-file clause in its old
wording; "is not checked" dropped; the rules-file clause dropped; the
boundary sentence dropped; the convention stated as fact; the allow-all test
ignored; the allow clause always on; `{}` printed when silent; a timestamp in
the text; a `<system-reminder>` tag in the text; the fixed text padded over
its cap; the status sentence dropped; the guard's path relative; the command
unquoted; a guard's path that needs escaping kept; no cap on the guard's
path; that cap measured on the raw path.
"""
import json, os, shlex, shutil, subprocess, sys, tempfile, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS = ("SessionStart", "SubagentStart")
SCRUB = ("SANDBOX_ALLOW_CHECKOUT_EDITS", "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS",
         "GIT_DIR")

FIXED_CAP = 1200
PATH_CAP = 256
TOTAL_CAP = 1712
FALLBACK_TOP = "this repository's main checkout"
ALLOW_CLAUSE = " except paths .claude/allow-checkout-edits allows"
RULES_CLAUSE = (
    "except the rules file .claude/allow-checkout-edits, which is the "
    "operator's to change: Edit and Write on it are denied from every working "
    "directory, and a Bash write to it is not checked but breaks the same "
    "rule")
BOUNDARY = ("The guard catches accidental edits through the edit tools; it is "
            "not a security boundary.")
CONVENTION = ("The sandbox convention is that changes to tracked files are "
              "made from a linked worktree")
BASH = "The guard does not check Bash writes"
STATUS = (" python3 %s --status prints whether the guard is on for the "
          "current directory.")
OLD_RULES_WORDING = "which agents may not change by any tool"

# Characters escape_path must escape, and their escaped forms.
ESCAPES = {
    "\n": "\\x0a", "\t": "\\x09", "\x00": "\\x00", "\x01": "\\x01",
    "\x7f": "\\x7f", "\x85": "\\x85", "\x9b": "\\x9b", "\xad": "\\xad",
    "\u2028": "\\u2028", "\u2029": "\\u2029", "\u200e": "\\u200e",
    "\u200f": "\\u200f", "\u202a": "\\u202a", "\u202e": "\\u202e",
    "\u2066": "\\u2066", "\u2069": "\\u2069", "\ufeff": "\\ufeff",
    "\U000e0001": "\\U000e0001", "`": "\\x60", "\\": "\\\\",
}
# The ones a directory name can hold and git prints on one line (a NUL cannot
# be in a name, and a line break makes both the guard and the notice read the
# cwd as not-git, which test_line_break_in_top_is_silent pins).
PATH_SPECIALS = "\t\x01\x7f\x9b\u200e\u200f\u202a\u202e\u2066\u2069\ufeff`\\"


def git(cwd, *args):
    subprocess.run(("git", "-C", cwd, "-c", "user.name=t",
                    "-c", "user.email=t@t") + args,
                   check=True, capture_output=True)


def make_repo(path, files=("README.md", "src.py", "bin/tool", "issues/x.md")):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q")
    for rel in files:
        p = os.path.join(path, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("x\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "init")
    return os.path.realpath(path)


def scrubbed(env):
    e = dict(os.environ)
    for k in SCRUB:
        e.pop(k, None)
    e.update(env or {})
    return e


def run_hook(hooks, name, stdin, env=None):
    p = subprocess.run([sys.executable, os.path.join(hooks, name)],
                       input=stdin, capture_output=True, text=True,
                       env=scrubbed(env), timeout=30)
    return p.returncode, p.stdout


def run_notice(hooks, cwd, event="SessionStart", env=None):
    payload = {"session_id": "s", "hook_event_name": event, "cwd": cwd}
    if event == "SubagentStart":
        payload.update({"agent_id": "a1", "agent_type": "general-purpose"})
    if event == "SessionStart":
        payload["source"] = "startup"
    return run_hook(hooks, "checkout_notice.py", json.dumps(payload), env)


def context(stdout):
    """The additionalContext of one JSON object, or None."""
    try:
        return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return None


def module_eval(hooks, expr, arg=None):
    """Evaluate `expr` with checkout_notice imported as n and checkout_guard
    as cg, both from `hooks`, in a fresh interpreter; `arg` is bound."""
    code = ("import json, sys; sys.path.insert(0, sys.argv[1]); "
            "import checkout_notice as n, checkout_guard as cg; "
            "arg = json.loads(sys.argv[2]); "
            "print(json.dumps(%s))" % expr)
    p = subprocess.run([sys.executable, "-I", "-c", code, hooks,
                        json.dumps(arg)], capture_output=True, text=True,
                       timeout=30)
    if p.returncode != 0:
        raise AssertionError(p.stderr)
    return json.loads(p.stdout)


def path_of_len(base, n, special=""):
    """A directory path of exactly n characters under base, its last
    component holding `special`; created."""
    head = os.path.join(base, "p")
    need = n - len(head) - 1  # the rest, after one more separator
    if need < len(special) + 1:
        raise AssertionError("base too long for %d" % n)
    parts = []
    while need > 0:
        take = min(need, 200)
        if need - take == 1:  # never leave a lone separator with no name
            take -= 1
        parts.append(take)
        need -= take + 1
    names = ["d" * k for k in parts]
    names[-1] = special + names[-1][len(special):]
    path = os.path.join(head, *names)
    assert len(path) == n, (len(path), n)
    return path


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = os.path.realpath(self.tmp.name)
        self.repo = make_repo(os.path.join(self.base, "repo"))
        self.wt = os.path.join(self.base, "wt")
        git(self.repo, "worktree", "add", "-q", self.wt, "-b", "wt-branch")
        self.plain = os.path.join(self.base, "plain")
        os.makedirs(self.plain)
        with open(os.path.join(self.plain, "f"), "w") as f:
            f.write("x\n")
        self.marker = os.path.join(self.repo, ".claude",
                                   "allow-checkout-edits")

    def tearDown(self):
        self.tmp.cleanup()

    def rules(self, text):
        if os.path.exists(self.marker):
            os.remove(self.marker)
        if text is not None:
            os.makedirs(os.path.dirname(self.marker), exist_ok=True)
            with open(self.marker, "w") as f:
                f.write(text)

    def silent_cases(self):
        """(label, cwd, env, rules text or None, raw stdin or None)."""
        cases = [
            ("worktree", self.wt, {}, None, None),
            ("non-git", self.plain, {}, None, None),
            ("git absent", self.repo,
             {"PATH": os.path.join(self.base, "nobin")}, None, None),
            ("git broken", self.repo,
             {"GIT_DIR": os.path.join(self.base, "no.git")}, None, None),
            ("garbage stdin", self.repo, {}, None, "not json"),
            ("empty stdin", self.repo, {}, None, ""),
            ("stdin a list", self.repo, {}, None, "[]"),
            ("other event", self.repo, {}, None,
             json.dumps({"hook_event_name": "Stop", "cwd": self.repo})),
            ("allow **", self.repo, {}, "allow **\n", None),
            ("allow *", self.repo, {}, "allow *\n", None),
            ("allow /**", self.repo, {}, "allow /**\n", None),
            ("allow **/**", self.repo, {}, "deny bin/**\nallow **/**\n", None),
        ]
        for name in SCRUB[:2]:
            cases.append(("override " + name, self.repo, {name: "1"}, None,
                          None))
        return cases

    # --- the checks: each returns a list of problems ------------------------

    def check_on(self, hooks):
        out = []
        self.rules(None)
        for event in EVENTS:
            for cwd in (self.repo, os.path.join(self.repo, "issues")):
                rc, stdout = run_notice(hooks, cwd, event)
                label = (event, cwd)
                try:
                    obj = json.loads(stdout)
                except Exception:
                    out.append((label, "not one JSON object", stdout))
                    continue
                hso = obj.get("hookSpecificOutput", {})
                text = hso.get("additionalContext", "")
                if rc != 0:
                    out.append((label, "exit", rc))
                if list(obj) != ["hookSpecificOutput"]:
                    out.append((label, "keys", list(obj)))
                if hso.get("hookEventName") != event:
                    out.append((label, "event", hso.get("hookEventName")))
                if not text.startswith("sandbox checkout guard: `%s` is a "
                                       "main git checkout" % self.repo):
                    out.append((label, "top not named absolute", text[:120]))
                if "<system-reminder>" in text or "</" in text:
                    out.append((label, "tag in text"))
                if len(text) > TOTAL_CAP:
                    out.append((label, "over the total cap", len(text)))
                if stdout.count("\n") != 1 or not stdout.endswith("\n"):
                    out.append((label, "not one line"))
        return out

    def check_silent(self, hooks):
        out = []
        for label, cwd, env, rules, raw in self.silent_cases():
            self.rules(rules)
            for event in EVENTS:
                if raw is None:
                    rc, stdout = run_notice(hooks, cwd, event, env)
                else:
                    rc, stdout = run_hook(hooks, "checkout_notice.py", raw,
                                          env)
                if (rc, stdout) != (0, ""):
                    out.append((label, event, rc, stdout[:80]))
        self.rules(None)
        return out

    def check_clauses(self, hooks):
        out = []
        self.rules(None)
        text = context(run_notice(hooks, self.repo)[1]) or ""
        for want in (RULES_CLAUSE, BOUNDARY, CONVENTION, BASH):
            if want not in text:
                out.append(("missing", want))
        if OLD_RULES_WORDING in text:
            out.append(("old wording", OLD_RULES_WORDING))
        return out

    def check_allow_clause(self, hooks):
        out = []
        for rules, want in (("allow **\ndeny bin/**\n", True),
                            ("allow issues/**\n", True),
                            ("deny bin/**\n", False),
                            ("allow [\n", False),
                            ("", False),
                            (None, False)):
            self.rules(rules)
            text = context(run_notice(hooks, self.repo)[1])
            if text is None:
                out.append((rules, "no notice"))
            elif (ALLOW_CLAUSE + ". " in text) != want:
                out.append((rules, "allow clause", not want))
        self.rules(None)
        return out

    def check_determinism(self, hooks):
        self.rules("allow issues/**\n")
        runs = [run_notice(hooks, self.repo, "SubagentStart")[1]
                for _ in range(2)]
        self.rules(None)
        return [] if runs[0] == runs[1] and runs[0] else [("differs", runs)]

    def check_fixed_budget(self, hooks):
        out = []
        # Every optional clause in, both paths empty (the guard's path
        # quoted: '').
        n = module_eval(hooks, "len(n.notice_text('', True, ''))")
        if n > FIXED_CAP:
            out.append(("fixed text", n))
        return out

    def check_path_cap(self, hooks):
        """Paths at the cap kept, one over replaced, escaped length counted."""
        out = []
        for n, special, kept in ((PATH_CAP, "", True),
                                 (PATH_CAP + 1, "", False),
                                 (PATH_CAP, "\t", False)):
            top = make_repo(path_of_len(self.base, n, special))
            if top != path_of_len(self.base, n, special):
                out.append(("realpath moved", top))
            text = context(run_notice(hooks, top)[1])
            if text is None:
                out.append((n, repr(special), "no notice"))
                continue
            if len(text) > TOTAL_CAP:
                out.append((n, "over the total cap", len(text)))
            shown = "`%s`" % top.replace("\t", "\\x09")
            if kept and shown not in text:
                out.append((n, repr(special), "path not kept"))
            if not kept and (FALLBACK_TOP not in text or
                             top.split(os.sep)[-1][-20:] in text):
                out.append((n, repr(special), "path not replaced"))
            shutil.rmtree(os.path.join(self.base, "p"))
        return out

    def check_escape_fn(self, hooks):
        out = []
        got = module_eval(hooks, "[cg.escape_path(c) for c in arg]",
                          list(ESCAPES))
        for (ch, want), g in zip(ESCAPES.items(), got):
            if g != want:
                out.append(("escape_path", repr(ch), g, want))
        if module_eval(hooks, "cg.escape_path(arg)", "a/b c.d-é") \
                != "a/b c.d-é":
            out.append(("plain text changed",))
        return out

    def check_escaped_path(self, hooks):
        out = []
        top = os.path.join(self.base, "x" + PATH_SPECIALS + "y")
        if os.path.exists(top):
            shutil.rmtree(top)
        top = make_repo(top)
        text = context(run_notice(hooks, top)[1])
        shutil.rmtree(top)
        if text is None:
            return [("no notice for the special path",)]
        want = "x" + "".join(ESCAPES[c] for c in PATH_SPECIALS) + "y"
        if "`%s/%s`" % (self.base, want) not in text:
            out.append(("escaped path not shown", text[:300]))
        for c in PATH_SPECIALS:
            if c not in "`\\" and c in text:
                out.append(("raw character in text", repr(c)))
        if text.count("`") != 2:
            out.append(("backticks", text.count("`")))
        return out

    def check_status_sentence(self, hooks):
        """The notice ends with the guard's status command, its path the real
        absolute one beside the hook, quoted; and the command runs."""
        out = []
        self.rules(None)
        script = os.path.realpath(os.path.join(hooks, "checkout_guard.py"))
        want = STATUS % shlex.quote(script)
        for event in EVENTS:
            text = context(run_notice(hooks, self.repo, event)[1]) or ""
            if not text.endswith(want):
                out.append((event, "status sentence", text[-160:]))
                continue
            argv = shlex.split(text[len(text) - len(want):].split(
                " prints whether")[0])
            if not os.path.isabs(argv[1]):
                out.append((event, "path not absolute", argv[1]))
            p = subprocess.run([sys.executable] + argv[1:], cwd=self.repo,
                               capture_output=True, text=True,
                               env=scrubbed({}), timeout=30)
            if (p.returncode, p.stdout) != (
                    0, "on main-checkout %s\n" % self.repo):
                out.append((event, "command", p.returncode, p.stdout,
                            p.stderr[-200:]))
        return out

    def check_status_cap(self, hooks):
        """The guard's path, shell-quoted, capped at PATH_CAP; a path that
        needs escaping, or is over the cap quoted, leaves the sentence out."""
        out = []
        cases = (
            ("/" + "d" * (PATH_CAP - 1), True),
            ("/" + "d" * PATH_CAP, False),
            ("/a b/it's/checkout_guard.py", True),  # quoted, runs as printed
            ("/a b" + "d" * (PATH_CAP - 5), False),  # 255 raw, 257 quoted
            ("/a`b/checkout_guard.py", False),  # the backtick needs escaping
            ("/" + "d" * 10 + "\t", False),
            ("/a b/" + PATH_SPECIALS + "/checkout_guard.py", False),
        )
        texts = module_eval(hooks, "[n.notice_text('/r', False, s) "
                            "for s in arg]", [c[0] for c in cases])
        for (script, kept), text in zip(cases, texts):
            label = (len(script), script[-12:])
            if kept and not text.endswith(STATUS % shlex.quote(script)):
                out.append((label, "sentence not kept", text[-120:]))
            if not kept and ("--status" in text or
                             not text.endswith("are the operator's to set.")):
                out.append((label, "sentence not left out", text[-120:]))
            if len(text) > TOTAL_CAP:
                out.append((label, "over the total cap", len(text)))
            for c in PATH_SPECIALS + "\t":
                if c not in "`\\" and c in text:
                    out.append((label, "raw character", repr(c)))
        return out

    def parity_mismatches(self, hooks):
        """Over cwd states x rules files: a notice iff the guard denies an
        Edit on at least one of the cwd's tracked files."""
        out = []
        cwds = (("main", self.repo, {}), ("worktree", self.wt, {}),
                ("non-git", self.plain, {}),
                ("git broken", self.repo,
                 {"GIT_DIR": os.path.join(self.base, "no.git")}),
                ("override", self.repo, {"SANDBOX_ALLOW_CHECKOUT_EDITS": "1"}))
        rule_sets = (("none", None), ("partial", "allow issues/**\n"),
                     ("allow-all", "allow **\n"), ("broken", "allow [\n"))
        for cname, cwd, env in cwds:
            p = subprocess.run(("git", "-C", cwd, "ls-files", "-z"),
                               capture_output=True, env=scrubbed({}))
            files = [os.path.join(cwd, os.fsdecode(f))
                     for f in p.stdout.split(b"\0") if f] \
                if p.returncode == 0 else []
            for rname, rules in rule_sets:
                self.rules(rules)
                noticed = context(run_notice(hooks, cwd, "SubagentStart",
                                             env)[1]) is not None
                denied = False
                for f in files:
                    _, so = run_hook(hooks, "checkout_guard.py", json.dumps(
                        {"tool_name": "Edit", "cwd": cwd,
                         "tool_input": {"file_path": f}}), env)
                    if "deny" in so:
                        denied = True
                        break
                if noticed != denied:
                    out.append((cname, rname, "notice", noticed,
                                "guard denies", denied))
        self.rules(None)
        return out


class TestNotice(Fixture):
    def test_on_in_a_main_checkout(self):
        self.assertEqual(self.check_on(HOOKS), [])

    def test_silent_cases_print_nothing(self):
        self.assertEqual(self.check_silent(HOOKS), [])

    def test_clauses(self):
        self.assertEqual(self.check_clauses(HOOKS), [])

    def test_allow_clause(self):
        self.assertEqual(self.check_allow_clause(HOOKS), [])

    def test_deterministic(self):
        self.assertEqual(self.check_determinism(HOOKS), [])

    def test_fixed_budget(self):
        self.assertEqual(self.check_fixed_budget(HOOKS), [])

    def test_path_cap(self):
        self.assertEqual(self.check_path_cap(HOOKS), [])

    def test_escape_function(self):
        self.assertEqual(self.check_escape_fn(HOOKS), [])

    def test_escaped_path_in_text(self):
        self.assertEqual(self.check_escaped_path(HOOKS), [])

    def test_parity_with_the_guard(self):
        self.assertEqual(self.parity_mismatches(HOOKS), [])

    def test_line_break_in_top_is_silent(self):
        # git prints such a top on two lines; the guard and the notice both
        # read the cwd as not-git, so they agree: no notice, no deny.
        top = make_repo(os.path.join(self.base, "a\nb"))
        self.assertEqual(run_notice(HOOKS, top), (0, ""))
        _, so = run_hook(HOOKS, "checkout_guard.py", json.dumps(
            {"tool_name": "Edit", "cwd": top,
             "tool_input": {"file_path": os.path.join(top, "README.md")}}))
        self.assertNotIn("deny", so)

    def test_registered_for_both_events(self):
        with open(os.path.join(HOOKS, "hooks.json")) as f:
            hooks = json.load(f)["hooks"]
        cmd = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/checkout_notice.py"'
        for event in EVENTS:
            entries = hooks[event]
            self.assertEqual(len(entries), 1, event)
            self.assertNotIn("matcher", entries[0], event)  # every source/type
            (h,) = entries[0]["hooks"]
            self.assertEqual((h["type"], h["command"]), ("command", cmd))
            self.assertNotIn("async", h)

    def test_shipped_text(self):
        # The text as it ships, in this repo's shape, for the record.
        text = module_eval(HOOKS, "n.notice_text(arg, False, '/g/cg.py')",
                           "/r")
        self.assertTrue(text.startswith("sandbox checkout guard: `/r` is a "
                                        "main git checkout"))
        self.assertTrue(text.endswith("are the operator's to set." +
                                      STATUS % "/g/cg.py"))

    def test_status_sentence(self):
        self.assertEqual(self.check_status_sentence(HOOKS), [])

    def test_status_cap(self):
        self.assertEqual(self.check_status_cap(HOOKS), [])


# (name, file, old, new, the check that must catch it)
MUTANTS = (
    ("worktree test ignored", "checkout_notice.py",
     "    if not state.on:\n        return None\n",
     "    if not state.on and state.why != \"linked-worktree\":\n"
     "        return None\n    state = state._replace(top=state.top or cwd)\n",
     "check_silent"),
    ("override ignored", "checkout_notice.py",
     "state = cg.checkout_state(cwd, env)",
     "state = cg.checkout_state(cwd, {})",
     "check_silent"),
    ("notice on a git error", "checkout_notice.py",
     "    if not state.on:\n        return None\n",
     "    if not state.on and state.why != \"not-git\":\n"
     "        return None\n    state = state._replace(top=state.top or cwd)\n",
     "check_silent"),
    ("worktree test ignored (parity)", "checkout_notice.py",
     "    if not state.on:\n        return None\n",
     "    if not state.on and state.why != \"linked-worktree\":\n"
     "        return None\n    state = state._replace(top=state.top or cwd)\n",
     "parity_mismatches"),
    ("event hard-coded", "checkout_notice.py",
     '"hookEventName": event,', '"hookEventName": "SessionStart",',
     "check_on"),
    ("relative path", "checkout_notice.py",
     "esc = cg.escape_path(top)",
     "esc = cg.escape_path(os.path.relpath(top))",
     "check_on"),
    ("no path cap", "checkout_notice.py",
     "if len(esc) <= PATH_CAP", "if True", "check_path_cap"),
    ("cap measured before escaping", "checkout_notice.py",
     "if len(esc) <= PATH_CAP", "if len(top) <= PATH_CAP", "check_path_cap"),
    ("no escaping", "checkout_notice.py",
     "esc = cg.escape_path(top)", "esc = top", "check_escaped_path"),
    ("escaping only below U+0020", "checkout_guard.py",
     "elif unicodedata.category(ch) in ESCAPED_CATEGORIES:",
     "elif o < 0x20:", "check_escaped_path"),
    ("escaping only below U+0020 (function)", "checkout_guard.py",
     "elif unicodedata.category(ch) in ESCAPED_CATEGORIES:",
     "elif o < 0x20:", "check_escape_fn"),
    ("backtick not escaped", "checkout_guard.py",
     'elif ch == "`":', "elif False:", "check_escaped_path"),
    ("old rules-file wording", "checkout_notice.py",
     "\".claude/allow-checkout-edits, which is the operator's to change: Edit \"",
     "\".claude/allow-checkout-edits, which agents may not change by any "
     "tool: Edit \"", "check_clauses"),
    ("'is not checked' dropped", "checkout_notice.py",
     '"write to it is not checked but breaks the same rule.',
     '"write to it breaks the same rule.', "check_clauses"),
    ("rules-file clause dropped", "checkout_notice.py",
     '".claude-sandbox/ are exempt, except the rules file "',
     '".claude-sandbox/ are exempt. The rules file "', "check_clauses"),
    ("boundary sentence dropped", "checkout_notice.py",
     '"edits through the edit tools; it is not a security boundary. The "',
     '"edits through the edit tools. The "', "check_clauses"),
    ("convention stated as fact", "checkout_notice.py",
     '"sandbox convention is that changes to tracked files are made from a "',
     '"repo\'s changes to tracked files are made from a "', "check_clauses"),
    ("allow-all ignored", "checkout_notice.py",
     "    if allow_all:\n        return None\n",
     "    if False:\n        return None\n", "check_silent"),
    ("allow clause always on", "checkout_notice.py",
     'ALLOW_CLAUSE if has_allow else ""', "ALLOW_CLAUSE",
     "check_allow_clause"),
    ("{} printed when silent", "checkout_notice.py",
     "    if out is not None:\n        sys.stdout.write(out + \"\\n\")\n",
     "    sys.stdout.write((out or \"{}\") + \"\\n\")\n", "check_silent"),
    ("timestamp in the text", "checkout_notice.py",
     '"additionalContext": notice_text(state.top, has_allow),',
     '"additionalContext": notice_text(state.top, has_allow) + '
     'repr(__import__("time").time()),', "check_determinism"),
    ("tag in the text", "checkout_notice.py",
     '"overrides (SANDBOX_ALLOW_CHECKOUT_EDITS=1, rules in "',
     '"overrides <system-reminder>(SANDBOX_ALLOW_CHECKOUT_EDITS=1, rules in "',
     "check_on"),
    ("fixed text over its cap", "checkout_notice.py",
     '"overrides (SANDBOX_ALLOW_CHECKOUT_EDITS=1, rules in "',
     '"overrides " + "x" * 200 + "(SANDBOX_ALLOW_CHECKOUT_EDITS=1, rules in "',
     "check_fixed_budget"),
    ("status sentence dropped", "checkout_notice.py",
     "                       status=status)", '                       status="")',
     "check_status_sentence"),
    ("guard's path relative", "checkout_notice.py",
     "return os.path.realpath(cg.__file__)",
     "return os.path.relpath(os.path.realpath(cg.__file__))",
     "check_status_sentence"),
    ("command unquoted", "checkout_notice.py",
     "cmd = shlex.quote(script)", "cmd = script", "check_status_cap"),
    ("guard's path needing escaping kept", "checkout_notice.py",
     "ok = cg.escape_path(script) == script and len(cmd) <= PATH_CAP",
     "ok = len(cmd) <= PATH_CAP", "check_status_cap"),
    ("no cap on the guard's path", "checkout_notice.py",
     "ok = cg.escape_path(script) == script and len(cmd) <= PATH_CAP",
     "ok = cg.escape_path(script) == script", "check_status_cap"),
    ("guard's path cap measured raw", "checkout_notice.py",
     "and len(cmd) <= PATH_CAP", "and len(script) <= PATH_CAP",
     "check_status_cap"),
)


class TestNoticeMutants(Fixture):
    def mutant_dir(self, name, old, new):
        d = tempfile.mkdtemp(dir=self.base, prefix="mut")
        for f in ("checkout_guard.py", "checkout_notice.py"):
            shutil.copy(os.path.join(HOOKS, f), d)
        p = os.path.join(d, name)
        with open(p) as f:
            src = f.read()
        if src.count(old) != 1:
            raise AssertionError("mutant target not found once: %r" % old)
        with open(p, "w") as f:
            f.write(src.replace(old, new))
        return d

    def test_each_mutant_is_caught(self):
        for label, name, old, new, check in MUTANTS:
            with self.subTest(mutant=label):
                d = self.mutant_dir(name, old, new)
                self.assertNotEqual(getattr(self, check)(d), [], label)
                shutil.rmtree(d)

    def test_unmutated_copy_passes(self):
        d = tempfile.mkdtemp(dir=self.base, prefix="copy")
        for f in ("checkout_guard.py", "checkout_notice.py"):
            shutil.copy(os.path.join(HOOKS, f), d)
        checks = sorted({m[4] for m in MUTANTS})
        for check in checks:
            self.assertEqual(getattr(self, check)(d), [], check)


if __name__ == "__main__":
    unittest.main()
