"""Pins for references/store-safety.md and SKILL.md § Protecting the store.

Two halves:
- the git behaviours the guidance rests on, re-run against the installed git
  in throwaway repos (first observed 2026-10-15 with git 2.39.5); a git that
  behaves differently fails here, not in a real store;
- doc checks: each rule is carried by the docs, in one home, and every
  `git clean` example is safe or sits under a "never" lead-in.

Every git call runs in a temp dir made by this test (prefix b2dff1-), with
GIT_CEILING_DIRECTORIES at that dir, HOME there, no system config and a temp
global config, so no real repo or store is ever touched.
"""
import fcntl
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
SAFETY_MD = SKILL_DIR / "references" / "store-safety.md"
FORMAT_MD = SKILL_DIR / "references" / "format.md"

HAVE_GIT = shutil.which("git") is not None
HAVE_BASH = shutil.which("bash") is not None
HAVE_FLOCK = shutil.which("flock") is not None
HAVE_TAR = shutil.which("tar") is not None


def _section(text, heading):
    """The body of a `## heading` section, up to the next `## `."""
    m = re.search(r"^## " + re.escape(heading) + r"\s*$(.*?)(?=^## |\Z)",
                  text, re.M | re.S)
    return m.group(1) if m else None


def _bash_fences(text):
    return re.findall(r"```bash\n(.*?)```", text, re.S)


class GitBox(unittest.TestCase):
    """A hermetic temp dir and a git that cannot leave it."""

    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="b2dff1-")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        gcfg = self.tmp / "b2dff1-gitconfig"
        gcfg.write_text("[init]\n\tdefaultBranch = main\n"
                        "[advice]\n\tdetachedHead = false\n")
        self.gcfg = gcfg
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "WORK_ITEMS_", "WI_")) and k != "EMAIL"}
        env.update(HOME=str(self.tmp), XDG_CONFIG_HOME=str(self.tmp / "xdg"),
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(gcfg),
                   GIT_CEILING_DIRECTORIES=str(self.tmp), LC_ALL="C")
        self.env = env

    def _inside(self, cwd):
        cwd = Path(os.path.realpath(cwd))
        self.assertTrue(cwd == self.tmp or self.tmp in cwd.parents,
                        f"refusing to run git outside the test dir: {cwd}")
        return cwd

    def git(self, cwd, *args, check=True):
        r = subprocess.run(["git", *args], cwd=self._inside(cwd), env=self.env,
                           capture_output=True, text=True, timeout=60)
        if check:
            self.assertEqual(r.returncode, 0,
                             f"git {' '.join(args)}: {r.stdout}{r.stderr}")
        return r

    def bash(self, cwd, script, extra_env=None, **kw):
        env = dict(self.env, **(extra_env or {}))
        return subprocess.run(["bash", "-c", script], cwd=self._inside(cwd),
                              env=env, capture_output=True, text=True,
                              timeout=60, **kw)

    def identify(self, repo):
        self.git(repo, "config", "user.name", "Tester")
        self.git(repo, "config", "user.email", "tester@example.invalid")

    def host(self, shape, ignored=True, name="host"):
        """A host repo with a store at .work-items/: shape 'plain' or 'own'.

        It also holds an ignored build/ (for -X pathspec cases) and a tracked
        sub/ directory."""
        h = self.tmp / name
        h.mkdir()
        self.git(h, "init", "-q")
        self.identify(h)
        (h / "README.md").write_text("host\n")
        (h / "sub").mkdir()
        (h / "sub" / "keep.txt").write_text("k\n")
        lines = ["/build/", "*.log"] + (["/.work-items/"] if ignored else [])
        (h / ".gitignore").write_text("\n".join(lines) + "\n")
        self.git(h, "add", "-A")
        self.git(h, "commit", "-q", "-m", "host")
        (h / "build").mkdir()
        (h / "build" / "out.o").write_text("o\n")
        s = h / ".work-items"
        (s / "items").mkdir(parents=True)
        (s / "items" / "a.md").write_text("item a\n")
        (s / ".lock").write_text("")
        if shape == "own":
            self.git(s, "init", "-q")
            self.identify(s)
            (s / ".gitignore").write_text(".lock\n*.tmp*\n")
            self.git(s, "add", "-A")
            self.git(s, "commit", "-q", "-m", "store")
        return h

    def kept(self, host):
        return (host / ".work-items" / "items" / "a.md").exists()


@unittest.skipUnless(HAVE_GIT, "git not installed")
class TestClean(GitBox):
    # (args, store ignored, plain kept, own-repo kept)
    MATRIX = [
        (["-fdx"], True, False, True),
        (["-fdX"], True, False, True),
        (["-fx"], True, True, True),
        (["-ffdx"], True, False, False),
        (["-ffdX"], True, False, False),
        (["-f", "-f", "-d", "-x"], True, False, False),
        (["-fd"], True, True, True),
        (["-fd"], False, False, True),
        (["-fdx", "-e", "/.work-items/"], True, True, True),
        (["-ffdx", "-e", "/.work-items/"], True, True, True),
        (["-fdx", "--", ".", ":!.work-items"], True, True, True),
        (["-fdX", "-e", "/.work-items/"], True, False, True),
        (["-fdX", "--", ".", ":!.work-items"], True, False, True),
        (["-ffdX", "-e", "/.work-items/"], True, False, False),
        (["-fdX", "--", "build/"], True, True, True),
    ]

    def test_clean_matrix(self):
        n = 0
        for args, ignored, plain_kept, own_kept in self.MATRIX:
            for shape, want in (("plain", plain_kept), ("own", own_kept)):
                n += 1
                with self.subTest(args=args, ignored=ignored, shape=shape):
                    h = self.host(shape, ignored=ignored, name=f"h{n}")
                    self.git(h, "clean", *args)
                    self.assertEqual(self.kept(h), want)

    def test_X_with_positive_pathspec_cleans_only_that_dir(self):
        h = self.host("plain")
        self.git(h, "clean", "-fdX", "--", "build/")
        self.assertFalse((h / "build").exists())
        self.assertTrue(self.kept(h))

    def test_doubled_force_deletes_what_the_preview_skipped(self):
        # A linked worktree under an ignored dir: the one-f preview says it
        # would skip it, and a second -f deletes it (and an own-repo store).
        h = self.host("own")
        with open(h / ".gitignore", "a") as f:
            f.write("/wt/\n")
        self.git(h, "worktree", "add", "-q", "wt/x")
        preview = self.git(h, "clean", "-n", "-fdx").stdout
        self.assertIn("Would skip repository wt/x", preview)
        self.git(h, "clean", "-fdx", "-e", "/.work-items/")
        self.assertTrue((h / "wt" / "x" / "README.md").exists())
        self.git(h, "clean", "-f", "-fdx", "-e", "/.work-items/")
        self.assertFalse((h / "wt" / "x").exists())
        self.assertTrue(self.kept(h))
        self.git(h, "clean", "-f", "-fdx")
        self.assertFalse(self.kept(h))

    def test_no_pathspec_works_from_cwd_down(self):
        h = self.host("plain")
        (h / "sub" / "x.log").write_text("l\n")
        self.git(h / "sub", "clean", "-fdx")
        self.assertFalse((h / "sub" / "x.log").exists())
        self.assertTrue(self.kept(h))
        self.assertTrue((h / "build" / "out.o").exists())

    def test_tracked_store_loses_new_items_lock_and_tmp(self):
        h = self.tmp / "tracked"
        h.mkdir()
        self.git(h, "init", "-q")
        self.identify(h)
        s = h / ".work-items"
        (s / "items").mkdir(parents=True)
        (s / "items" / "a.md").write_text("a\n")
        (s / ".gitignore").write_text(".lock\n*.tmp*\n")
        self.git(h, "add", "-A")
        self.git(h, "commit", "-q", "-m", "tracked store")
        (s / ".lock").write_text("")
        (s / "items" / "y.md.tmp1").write_text("t\n")
        (s / "items" / "new.md").write_text("new\n")

        out = self.git(h, "clean", "-n", "-f").stdout
        self.assertIn(".work-items/items/new.md", out)
        out = self.git(h, "clean", "-n", "-fx").stdout
        self.assertIn(".work-items/.lock", out)
        self.assertIn(".work-items/items/y.md.tmp1", out)
        for args in (["-n", "-f"], ["-n", "-fx"], ["-n", "-fdx"]):
            with self.subTest(args=args):
                out = self.git(h, "clean", *args, "-e", "/.work-items/").stdout
                self.assertNotIn(".work-items", out)
        # Under -X, -e turns the exclusion into an ignore rule: the new item
        # becomes ignored, so -X lists it.
        out = self.git(h, "clean", "-n", "-fdX").stdout
        self.assertEqual(out.split(), ["Would", "remove", ".work-items/.lock",
                                       "Would", "remove", ".work-items/items/y.md.tmp1"])
        out = self.git(h, "clean", "-n", "-fdX", "-e", "/.work-items/").stdout
        self.assertIn(".work-items/items/new.md", out)
        self.git(h, "clean", "-f")
        self.assertFalse((s / "items" / "new.md").exists())

    def test_git_inside_plain_store_acts_on_host(self):
        h = self.host("plain")
        s = h / ".work-items"
        top = self.git(s, "rev-parse", "--show-toplevel").stdout.strip()
        self.assertEqual(Path(top), h)
        self.git(s, "clean", "-fdx", ".")
        self.assertFalse(self.kept(h))

    def test_destructive_git_inside_own_store(self):
        h = self.host("own")
        s = h / ".work-items"
        (s / "items" / "a.md").write_text("edited\n")
        self.git(s, "reset", "-q", "--hard")
        self.assertEqual((s / "items" / "a.md").read_text(), "item a\n")
        (s / "items" / "b.md").write_text("new\n")
        self.git(s, "clean", "-fd")
        self.assertFalse((s / "items" / "b.md").exists())

    def test_host_reset_and_checkout_keep_store(self):
        for shape in ("plain", "own"):
            with self.subTest(shape=shape):
                h = self.host(shape, name=f"h-{shape}")
                self.git(h, "branch", "other")
                self.git(h, "reset", "-q", "--hard")
                self.git(h, "checkout", "-q", "-f", "other")
                self.assertTrue(self.kept(h))


@unittest.skipUnless(HAVE_GIT, "git not installed")
class TestStashAndAdd(GitBox):
    def test_stash_all_moves_plain_store_and_pop_restores(self):
        h = self.host("plain")
        self.git(h, "stash", "--all")
        self.assertFalse(self.kept(h))
        self.assertIn("stash@{0}", self.git(h, "stash", "list").stdout)
        self.git(h, "stash", "pop")
        self.assertTrue(self.kept(h))

    def test_stash_all_keeps_own_repo_store(self):
        h = self.host("own")
        (h / "README.md").write_text("changed\n")
        self.git(h, "stash", "--all")
        self.assertTrue(self.kept(h))

    def test_stash_u(self):
        for shape, ignored, want in (("plain", True, True), ("own", True, True),
                                     ("plain", False, False), ("own", False, True)):
            with self.subTest(shape=shape, ignored=ignored):
                h = self.host(shape, ignored=ignored, name=f"h-{shape}-{ignored}")
                (h / "README.md").write_text("changed\n")
                self.git(h, "stash", "-u")
                self.assertEqual(self.kept(h), want)

    def test_add_force_stages_plain_store(self):
        h = self.host("plain")
        self.git(h, "add", "-f", ".work-items")
        staged = self.git(h, "diff", "--cached", "--name-only").stdout
        self.assertIn(".work-items/items/a.md", staged)

    def test_add_force_own_repo_store_makes_gitlink(self):
        h = self.host("own")
        self.git(h, "add", "-f", ".work-items")
        entry = self.git(h, "ls-files", "-s", ".work-items").stdout
        head = self.git(h / ".work-items", "rev-parse", "HEAD").stdout.strip()
        self.assertTrue(entry.startswith("160000 " + head), entry)

    def test_dropped_stash_recovery(self):
        # The § Recovering commands: fsck finds the dropped stash, the one
        # with three parents; its ^3 holds the store; apply <sha> restores it.
        h = self.host("plain")
        self.git(h, "stash", "--all")
        sha = self.git(h, "rev-parse", "stash@{0}").stdout.strip()
        self.git(h, "stash", "drop", "-q")
        self.assertFalse(self.kept(h))
        out = self.git(h, "fsck", "--unreachable").stdout
        commits = [ln.split()[-1] for ln in out.splitlines() if "commit" in ln]
        three = [c for c in commits
                 if len(self.git(h, "rev-list", "--parents", "-n1", c).stdout.split()) == 4]
        self.assertEqual(three, [sha])
        stat = self.git(h, "show", "--stat", "--format=", sha + "^3").stdout
        self.assertIn(".work-items/items/a.md", stat)
        self.git(h, "stash", "apply", sha)
        self.assertTrue(self.kept(h))

    def test_add_own_repo_store_makes_gitlink(self):
        h = self.host("own", ignored=False)
        self.git(h, "add", ".work-items")
        entry = self.git(h, "ls-files", "-s", ".work-items").stdout
        head = self.git(h / ".work-items", "rev-parse", "HEAD").stdout.strip()
        self.assertTrue(entry.startswith("160000 " + head), entry)


@unittest.skipUnless(HAVE_GIT and HAVE_BASH, "git or bash not installed")
class TestCommitRecipe(GitBox):
    def _snippet(self):
        sec = _section(SAFETY_MD.read_text(), "Safe forms")
        fences = [f for f in _bash_fences(sec) if "GIT_AUTHOR_IDENT" in f]
        self.assertEqual(len(fences), 1)
        return fences[0].replace('"<what>"', '"recipe"')

    def _store(self):
        s = self.tmp / "store"
        (s / "items").mkdir(parents=True)
        self.git(s, "init", "-q")
        (s / ".gitignore").write_text(".lock\n*.tmp*\n")
        (s / ".lock").write_text("")
        (s / "items" / "a.md").write_text("a\n")
        return s

    def _no_identity(self):
        # useConfigOnly stops git guessing an address from the host name, so
        # "no identity" holds on any machine.
        with open(self.gcfg, "a") as f:
            f.write("[user]\n\tuseConfigOnly = true\n")

    def test_var_fails_exactly_when_commit_would(self):
        s = self._store()
        self._no_identity()
        self.assertNotEqual(self.git(s, "var", "GIT_AUTHOR_IDENT", check=False).returncode, 0)
        self.git(s, "add", "-A")
        r = self.git(s, "commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Author identity unknown", r.stderr)
        self.identify(s)
        self.assertEqual(self.git(s, "var", "GIT_AUTHOR_IDENT", check=False).returncode, 0)
        self.git(s, "commit", "-q", "-m", "x")

    @unittest.skipUnless(HAVE_FLOCK, "flock not installed")
    def test_recipe_uses_fallback_only_without_identity(self):
        snippet = self._snippet()
        s = self._store()
        self._no_identity()
        r = self.bash(s, snippet, {"S": str(s)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git(s, "log", "-1", "--format=%an <%ae>").stdout.strip(),
                         "wi <wi@localhost>")
        tracked = self.git(s, "ls-files").stdout.split()
        self.assertNotIn(".lock", tracked)

        self.identify(s)
        (s / "items" / "b.md").write_text("b\n")
        r = self.bash(s, snippet, {"S": str(s)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git(s, "log", "-1", "--format=%an").stdout.strip(), "Tester")

    @unittest.skipUnless(HAVE_FLOCK, "flock not installed")
    def test_recipe_waits_for_the_store_lock(self):
        snippet = self._snippet()
        s = self._store()
        self.identify(s)
        fd = os.open(s / ".lock", os.O_RDWR)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX)
        p = subprocess.Popen(["bash", "-c", snippet], cwd=self._inside(s),
                             env=dict(self.env, S=str(s)),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            time.sleep(0.7)
            self.assertIsNone(p.poll(), "the recipe ran while the lock was held")
            self.assertNotEqual(self.git(s, "rev-parse", "-q", "--verify", "HEAD",
                                         check=False).returncode, 0)
            fcntl.flock(fd, fcntl.LOCK_UN)
            _, err = p.communicate(timeout=30)
        finally:
            if p.poll() is None:
                p.kill()
                p.communicate()
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(self.git(s, "log", "-1", "--format=%s").stdout.strip(), "recipe")


@unittest.skipUnless(HAVE_GIT and HAVE_BASH, "git or bash not installed")
class TestBackup(GitBox):
    def _b_line(self):
        sec = _section(SAFETY_MD.read_text(), "Backing up")
        fences = [f for f in _bash_fences(sec) if f.lstrip().startswith("B=")]
        self.assertEqual(len(fences), 1)
        return fences[0].strip()

    def test_bundle_survives_clean_and_restores(self):
        h = self.host("own")
        s = h / ".work-items"
        (s / "items" / "b.md").write_text("b\n")
        self.git(s, "add", "-A")
        self.git(s, "commit", "-q", "-m", "second")
        (s / "items" / "uncommitted.md").write_text("u\n")
        script = (self._b_line() + '\n'
                  'git -C "$S" bundle create "$B/store.bundle" --all\n'
                  'printf %s "$B"')
        r = self.bash(h, script, {"S": str(s)})
        self.assertEqual(r.returncode, 0, r.stderr)
        b = Path(r.stdout)
        self.assertEqual(b, h / ".git" / "work-items-backup")

        self.git(h, "clean", "-ffdx")
        self.assertFalse(s.exists())
        self.assertTrue((b / "store.bundle").is_file())

        self.git(h, "clone", "-q", str(b / "store.bundle"), ".work-items")
        self.git(s, "remote", "remove", "origin")
        self.assertTrue(self.kept(h))
        self.assertTrue((s / "items" / "b.md").exists())
        # A bundle holds only commits: hence "commit first" in § Backing up.
        self.assertFalse((s / "items" / "uncommitted.md").exists())
        self.assertEqual(self.git(s, "rev-list", "--count", "HEAD").stdout.strip(), "2")
        self.assertEqual(self.git(s, "remote").stdout.strip(), "")

    @unittest.skipUnless(HAVE_TAR, "tar not installed")
    def test_tarball_survives_clean_and_restores(self):
        h = self.host("plain")
        s = h / ".work-items"
        script = (self._b_line() + '\n'
                  'tar -C "$(dirname "$S")" -czf "$B/store.tgz" "$(basename "$S")"\n'
                  'printf %s "$B"')
        r = self.bash(h, script, {"S": str(s)})
        self.assertEqual(r.returncode, 0, r.stderr)
        b = Path(r.stdout)
        self.git(h, "clean", "-fdx")
        self.assertFalse(self.kept(h))
        restore = re.search(r'`(tar -C "\$\(dirname "\$S"\)" -xzf "\$B/)<date>(\.tgz")`',
                            _section(SAFETY_MD.read_text(), "Backing up"))
        self.assertIsNotNone(restore, "the plain restore line")
        r = self.bash(h, restore.group(1) + "store" + restore.group(2),
                      {"S": str(s), "B": str(b)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.kept(h))


class TestDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text()
        cls.safety = SAFETY_MD.read_text() if SAFETY_MD.exists() else ""
        cls.fmt = FORMAT_MD.read_text()
        cls.rules = _section(cls.skill, "Protecting the store") or ""

    def test_format_own_path_lists_name_cards(self):
        """3b51 W1: every list of the store's own paths in format.md names
        `cards`: what a store with no .git may hold at its top, where a
        git dir may not lie, § Pathspecs, and the shapes a write commits."""
        text = " ".join(self.fmt.split())
        for needle in (
                "anything but `items`, `archive`, `cards`, `README.md`, "
                "`store.yaml`, `.gitignore`, `.lock`",
                "(`items`, `archive`, `cards`, `README.md`, `store.yaml`, "
                "`.gitignore`: a git dir there",
                "The store's own paths are `items`, `archive`, `cards`, "
                "`README.md`, `store.yaml` and `.gitignore`.",
                "a card record three levels under `cards/` "
                "(`cards/<id>/<N>/<name>.json`"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)
        # no list of the own paths left without it
        self.assertNotIn("`items`, `archive`, `README.md`", text)

    def test_skill_has_the_section_and_points_at_the_reference(self):
        self.assertTrue(self.rules, "SKILL.md lacks § Protecting the store")
        self.assertIn("references/store-safety.md", self.rules)
        self.assertTrue(SAFETY_MD.is_file())
        # SKILL.md stays under the 5000-token line; ~4 bytes a token.
        self.assertLess(len(self.skill.encode()), 5000 * 4)
        self.assertLess(len(self.rules.strip().splitlines()), 40)

    def test_skill_carries_each_rule(self):
        for needle in ("git clean -n -fdx -e /.work-items/",
                       "Never a doubled `-f` (or `--force` twice) near a store: a doubled force "
                       "deletes linked worktrees and nested repos even when the store is excluded",
                       "Never `-x` near a store without excluding it",
                       "then run it without `-n`: `git clean -fdx -e /.work-items/` (one `-f` only)",
                       "`-X` is never safe while the clean reaches a store "
                       "(from the cwd down, or through its pathspec)",
                       "then run `git clean -fdX -- build/ dist/`",
                       "loses new items to any clean without `-X`: add `-e /<store>/` "
                       "(under `-X`, name the directories as above)",
                       "deleted by `git clean -fd` and moved by `git stash -u`",
                       "`git clean -fdX -- build/ dist/`",
                       "never `--all`/`-a`",
                       "`rm -r`: never on the store",
                       "always `git -C <store> …`",
                       "except a commit under its lock",
                       "`git add -f` it",
                       "gitlink, mode 160000",
                       "`WORK_ITEMS_ROOT`",
                       "Never `$WI init` there",
                       "`references/format.md` § Secret rule",
                       "git 2.39.5"):
            with self.subTest(needle=needle):
                self.assertIn(needle, " ".join(self.rules.split()))

    def test_reference_carries_the_safe_patterns(self):
        for heading in ("Why the store needs care", "Safe forms", "Worktrees and clones",
                        "Concurrency and `index.lock`", "Commit failures",
                        "Secrets in the store's history", "Backing up", "Recovering"):
            with self.subTest(heading=heading):
                self.assertIsNotNone(_section(self.safety, heading))
        never = [h for h in re.findall(r"^## (.*)$", self.safety, re.M) if "never" in h]
        self.assertEqual(len(never), 1, "one danger section, headed with 'never'")
        for needle in ('mkdir -p "$B"',
                       "--path-format=absolute --git-common-dir)/work-items-backup",
                       'bundle create "$B/',
                       "remote remove origin",
                       'flock -w 10 "$S/.lock"',
                       "if git -C \"$S\" var GIT_AUTHOR_IDENT",
                       "git clean -n -fdX -- build/ dist/",
                       "git clean -n -fdx -e /.work-items/",
                       "git stash apply stash@{n}",
                       "git stash apply <sha>",
                       "git show --stat <sha>^3",
                       "commit first under the lock (§ Safe forms)",
                       "The committed items and",
                       "2026-10-15 with git 2.39.5",
                       "`-e /<store>/` keeps both, except under `-X`, where it deletes the new items",
                       "tests/test_store_safety.py",
                       "(one `-f` only: a doubled force, `-ff` or `--force` twice, deletes linked "
                       "worktrees and nested repos that the one-`-f` preview skipped, even when "
                       "the store is excluded)"):
            with self.subTest(needle=needle):
                self.assertIn(needle, " ".join(self.safety.split()))

    def test_identity_fallback_only_when_git_var_fails(self):
        # The fallback identity appears once, in the else branch of the git var check.
        self.assertEqual(self.safety.count("-c user.name=wi"), 1)
        self.assertRegex(self.safety,
                         r'if git -C "\$S" var GIT_AUTHOR_IDENT [^\n]*; then id=\(\); '
                         r'else id=\(-c user\.name=wi -c user\.email=wi@localhost\); fi')
        self.assertNotIn("-c user.name=", self.rules)

    def test_doubled_force_has_no_exclusion_escape(self):
        # The rule bans a doubled force outright; the old "without excluding
        # it" escape must not come back.
        flat = " ".join(self.rules.split())
        self.assertNotRegex(flat, r"doubled `-f`[^.]*without excluding it")

    def test_clean_bullet_is_split_by_rule(self):
        bullet = re.search(r"^- `git clean`:\n((?:  - .*\n(?:    .*\n)*)+)", self.rules, re.M)
        self.assertIsNotNone(bullet, "the git clean bullet has sub-bullets")
        subs = re.findall(r"^  - (.*)", bullet.group(1), re.M)
        for start in ("Never a doubled `-f`", "Never `-x`", "`-X` is never safe",
                      "A tracked store", "A plain store that is not ignored"):
            with self.subTest(start=start):
                self.assertEqual(sum(s.startswith(start) for s in subs), 1)

    def test_one_home_per_rule(self):
        # The reference cites the rules, it does not restate them.
        self.assertIn("SKILL.md` § Protecting the store", self.safety)
        self.assertNotIn("## Protecting the store", self.safety)
        for line in ("Never `$WI init` there to make the error go away",
                     "Path and key, never value"):
            self.assertNotIn(line, self.safety)

    def test_format_moving_a_store_says_back_up_first(self):
        sec = _section(self.fmt, "Moving a store")
        self.assertIsNotNone(sec)
        self.assertRegex(sec, r"Before any of them, back up the store\s+"
                              r"\(`references/store-safety\.md` § Backing up\)")
        self.assertIsNotNone(_section(self.safety, "Backing up"))

    def test_every_clean_example_is_safe_or_under_never(self):
        for name, text in (("SKILL.md", self.skill), ("store-safety.md", self.safety)):
            with self.subTest(file=name):
                self.assertGreater(len(_clean_examples(text)), 3)
                self.assertEqual(_unsafe_examples(text), [])

    def test_example_lint_catches_unsafe_forms(self):
        bad = ["Run `git clean -fdx`.",
               "Run `git clean -ffd`.",
               "Run `git clean -f -fdx -e /.work-items/`.",
               "Run `git clean --force -fdx -e /.work-items/`.",
               "Run `git clean -fdx -e /build/`.",
               "Run `git clean -fdx -- . ':!build'`.",
               "Run `git clean -fdX -e /.work-items/`.",
               "Run `git clean -fdX -- . ':!.work-items'`.",
               "Run `git clean -fdX -- ./`.",
               "Run `git clean -fdX -- :/`.",
               "Run `git clean -fdX -- ../`.",
               "Run `git clean -fdX -- '*.o'`.",
               "Run `git clean -fdX`.",
               "Never mind that. Run `git clean -fdx`.",
               "It is never slow: `git clean -fdx`.",
               "Run it\n  `git clean\n  -fdx`.",
               "```bash\ngit clean -fdx\n```"]
        for text in bad:
            with self.subTest(text=text):
                self.assertTrue(_unsafe_examples(text))
        good = ["Never run `git clean -fdx`.",
                "Run `git clean -fdx -e /.work-items/`.",
                "Run `git clean -fdx -e /.claude-sandbox/work/`.",
                "Run `git clean -fdx -- . ':!.work-items'`.",
                "Run `git clean -fdX -- build/`.",
                "## What destroys it (never run these)\n\n| `git clean -fdX` | deleted |"]
        for text in good:
            with self.subTest(text=text):
                self.assertEqual(_unsafe_examples(text), [])

    def test_example_lint_catches_mutations_of_the_skill(self):
        for old, new in (("`git clean -fdX -- build/ dist/`", "`git clean -fdX -e /.work-items/`"),
                         ("`git clean -n -fdx -e /.work-items/`", "`git clean -n -fdx`"),
                         ("`git clean -fdx -e /.work-items/`", "`git clean -f -fdx -e /.work-items/`")):
            with self.subTest(old=old):
                self.assertIn(old, self.rules)
                self.assertTrue(_unsafe_examples(self.skill.replace(old, new, 1)))


_EXCL = (":!", ":^", ":(exclude)")
_STORES = {".work-items", ".claude-sandbox/work", ".work"}


def _clean_examples(text):
    """(example, exempt) for every `git clean …` in a code span (which may
    wrap) or a fence. Exempt when its heading says never, or when "never"
    falls in its own clause: the text since the last `:`, `—`, `|` or
    sentence-ending `.` before it, code spans left out."""
    out = []
    heading = ""
    block = []

    def flush():
        para = "\n".join(block)
        for m in re.finditer(r"`([^`]+)`", para):
            span = " ".join(m.group(1).split())
            if not span.startswith("git clean"):
                continue
            before = re.sub(r"`[^`]*`", "C", para[:m.start()])
            clause = re.split(r":|—|\||\.(?:\s|$)", before)[-1]
            out.append((span, "never" in heading.lower() or "never" in clause.lower()))
        block.clear()

    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            for m in re.finditer(r"git clean[^\n#]*", line):
                out.append((m.group(0).strip(), "never" in heading.lower()))
            continue
        if line.startswith("#"):
            flush()
            heading = line
            continue
        if not line.strip() or re.match(r"\s*(- |\| |\d+\. )", line):
            flush()
        block.append(line)
    flush()
    return out


def _norm(p):
    p = p.strip("'\"")
    for magic in _EXCL:
        if p.startswith(magic):
            p = p[len(magic):]
    return p.strip("/")


def _parse_clean(ex):
    """(forces, has -x, has -X, exclusion patterns, positive pathspecs)."""
    try:
        argv = shlex.split(ex)[2:]
    except ValueError:
        argv = ex.split()[2:]
    forces, x, X, excl, paths = 0, False, False, [], []
    i, opts = 0, True
    while i < len(argv):
        a = argv[i]
        if opts and a == "--":
            opts = False
        elif opts and a == "--force":
            forces += 1
        elif opts and a.startswith("--exclude="):
            excl.append(a.split("=", 1)[1])
        elif opts and a.startswith("-") and not a.startswith("--") and len(a) > 1:
            for j, c in enumerate(a[1:], 1):
                if c == "e":
                    rest = a[j + 1:]
                    if not rest and i + 1 < len(argv):
                        i += 1
                        rest = argv[i]
                    excl.append(rest)
                    break
                forces += c == "f"
                x = x or c == "x"
                X = X or c == "X"
        elif not a.startswith("-") or not opts:
            (excl if a.startswith(_EXCL) else paths).append(a)
        i += 1
    return forces, x, X, excl, paths


def _unsafe_examples(text):
    """Examples not exempt that: force twice; use -x without excluding a
    store path; or use -X without a positive pathspec that leaves the store
    out, or with any exclusion (none protects under -X)."""
    bad = []
    for ex, exempt in _clean_examples(text):
        if exempt:
            continue
        forces, x, X, excl, paths = _parse_clean(ex)
        store_excl = any(_norm(e) in _STORES for e in excl)
        wide = [p for p in paths
                if _norm(p) in ("", ".") or _norm(p).startswith("..") or p.startswith(":/")
                or _norm(p) in _STORES
                or any(c in p for c in "*?[")]
        if forces >= 2:
            bad.append(ex)
        elif X:
            if not paths or wide or excl:
                bad.append(ex)
        elif x and not store_excl:
            bad.append(ex)
    return bad


if __name__ == "__main__":
    unittest.main()
