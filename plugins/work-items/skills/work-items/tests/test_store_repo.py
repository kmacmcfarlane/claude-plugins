"""Tests for a work-item store that is its own git repo (d1e9 F1): telling
the store's .git apart (own, unrecorded, dedicated, missing, broken, old),
the hardened store git runner, custody through it, and the store-repo rows
of `prime` and `lint`; `wi commit` (F2), one test group per row of its
table in format.md § Committing the store; and `wi init` creating or
adopting the store's repo (F3, TestInit).

Every git call here runs in a temp dir: HOME is a temp dir, the global
config is a temp file (GIT_CONFIG_GLOBAL), GIT_CONFIG_NOSYSTEM=1, and
GIT_CEILING_DIRECTORIES is the temp dir, so neither the machine's config
nor a repo around the temp dir is ever read. Marker scripts prove that no
hook, fsmonitor or clean filter runs: each test that relies on one first
shows the marker firing under plain git, then that it stays silent under
the runner, `wi prime` and `wi lint`.
"""
import contextlib
import fcntl
import importlib.util
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_store_repo", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

GIT = shutil.which("git")


def git_version():
    if not GIT:
        return (0,)
    out = subprocess.run(["git", "--version"], capture_output=True,
                         text=True).stdout
    m = re.search(r"(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0,)


ITEM = """---
id: {iid}
title: {iid}
type: task
status: todo
priority: 2
created: 2026-08-01
updated: 2026-08-01
---

Description of {iid}.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
"""


@unittest.skipUnless(GIT, "git not available")
class StoreRepoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="d1e9f1-")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = self.tmp / "home"
        home.mkdir()
        self.gitconfig = home / "gitconfig"
        self.gitconfig.write_text("")
        self.marks = self.tmp / "marks"
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "WI_", "WORK_ITEMS_"))}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home),
                   GIT_CONFIG_GLOBAL=str(self.gitconfig),
                   GIT_CONFIG_NOSYSTEM="1",
                   GIT_CEILING_DIRECTORIES=str(self.tmp),
                   WORK_ITEMS_OWNER="tester@local")
        env.pop("EMAIL", None)
        self.env = env
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- helpers ---------------------------------------------------------

    def git(self, cwd, *args, check=True, env=None):
        full = dict(self.env, **(env or {}))
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(args),
            cwd=cwd, env=full, capture_output=True, text=True, check=check)

    def wi(self, args, root, env=None):
        full = dict(self.env, WORK_ITEMS_ROOT=str(root))
        full.update(env or {})
        return subprocess.run([sys.executable, str(WI)] + args, env=full,
                              capture_output=True, text=True)

    def marker(self, name, passthrough=False):
        """An executable script that appends its name to the marks file;
        a filter's copy also passes its stdin through."""
        path = self.tmp / "bin" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"#!/bin/sh\necho {name} >> '{self.marks}'\n"
                        + ("cat\n" if passthrough else ""))
        path.chmod(0o755)
        return path

    def marked(self):
        return self.marks.read_text().split() if self.marks.exists() else []

    def clear_marks(self):
        if self.marks.exists():
            self.marks.unlink()

    def store_files(self, store, own=True, items=("one-aaaa",)):
        (store / "items").mkdir(parents=True, exist_ok=True)
        (store / "README.md").write_text("# Work items\n")
        (store / ".gitignore").write_text(".lock\n*.tmp*\n")
        (store / "store.yaml").write_text(
            "tracking: tracked\n" + ("repo: own\n" if own else ""))
        for iid in items:
            (store / "items" / f"{iid}.md").write_text(ITEM.format(iid=iid))

    def make_host(self, name="host", ignore=True):
        host = self.tmp / name
        host.mkdir()
        self.git(host, "init", "-q")
        if ignore:
            (host / ".gitignore").write_text("/.work-items/\n")
        (host / "src.txt").write_text("host file\n")
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "host")
        return host

    def make_own(self, host=True, own=True, commit=True):
        """A store at <host>/.work-items with its own repo, committed."""
        base = self.make_host() if host else self.tmp / "nohost"
        base.mkdir(exist_ok=True)
        store = base / ".work-items"
        self.store_files(store, own=own)
        self.git(store, "init", "-q", "--template=")
        if commit:
            self.git(store, "add", "-A")
            self.git(store, "commit", "-q", "-m", "init")
        return store

    def state(self, store):
        return wi.store_repo_state(store)


class TestDetection(StoreRepoCase):
    """d1e9 D1: what a store's .git is."""

    def test_plain_store_makes_no_git_call(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        with mock.patch.object(wi.subprocess, "run") as run:
            rs = self.state(store)
        self.assertEqual(rs.state, "plain")
        run.assert_not_called()

    def test_dir_git_own(self):
        store = self.make_own()
        rs = self.state(store)
        self.assertEqual(rs.state, "own", rs.reason)
        self.assertEqual(rs.git_dir, str(store / ".git"))
        self.assertEqual(rs.host, self.tmp / "host")

    def test_own_outside_any_repo(self):
        rs = self.state(self.make_own(host=False))
        self.assertEqual(rs.state, "own", rs.reason)
        self.assertIsNone(rs.host)

    def test_unrecorded_needs_a_host(self):
        self.assertEqual(self.state(self.make_own(own=False)).state,
                         "unrecorded")

    def test_dedicated_top_of_repo_store(self):
        self.assertEqual(
            self.state(self.make_own(host=False, own=False)).state,
            "dedicated")

    def test_missing(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=True)
        self.assertEqual(self.state(store).state, "missing")

    def test_git_file_inside_store_is_valid(self):
        self.make_host()
        store = self.tmp / "host" / ".work-items"
        self.store_files(store)
        self.git(self.tmp, "init", "-q", "--template=",
                 f"--separate-git-dir={store / 'gitdata'}", str(store))
        self.assertTrue((store / ".git").is_file())
        self.assertEqual(self.state(store).state, "own")

    def test_git_file_to_host_worktree_points_outside(self):
        host = self.make_host()
        wt = self.tmp / "wt"
        self.git(host, "worktree", "add", "-q", "--detach", str(wt))
        store = host / ".work-items"
        self.store_files(store)
        shutil.copy(wt / ".git", store / ".git")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(".git points outside the store", rs.reason)
        self.assertIn(str(host / ".git"), rs.reason)

    def test_absorbed_submodule_git_file_points_outside(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        (host / ".git" / "modules").mkdir()
        self.git(self.tmp, "init", "-q", "--template=",
                 f"--separate-git-dir={host / '.git' / 'modules' / 'store'}",
                 str(store))
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(".git points outside the store", rs.reason)

    def test_bare_git_is_broken(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        self.git(self.tmp, "init", "-q", "--bare", str(store / ".git"))
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("bare", rs.reason)

    def test_empty_git_is_broken_and_never_reaches_the_host(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        (store / ".git").mkdir()
        head = (host / ".git" / "HEAD").read_bytes()
        index = (host / ".git" / "index").read_bytes()
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("not a usable repository", rs.reason)
        r = wi._store_git(store, "add", "-A", "--", "items")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((host / ".git" / "HEAD").read_bytes(), head)
        self.assertEqual((host / ".git" / "index").read_bytes(), index)

    def test_symlink_git_inside_is_valid(self):
        store = self.make_own()
        (store / ".git").rename(store / "gitreal")
        (store / ".git").symlink_to("gitreal")
        self.assertEqual(self.state(store).state, "own")

    def test_symlink_git_outside_is_broken(self):
        host = self.make_host()
        other = self.tmp / "other"
        other.mkdir()
        self.git(other, "init", "-q")
        store = host / ".work-items"
        self.store_files(store)
        (store / ".git").symlink_to(other / ".git")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("points outside", rs.reason)

    def test_old_location_git(self):
        self.make_host()
        store = self.tmp / "host" / ".work"
        self.store_files(store)
        self.git(store, "init", "-q", "--template=")
        self.assertEqual(self.state(store).state, "old")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("holds a git repo at an old location", r.stdout)
        self.assertIn("Moving a store", r.stdout)


class TestAttributes(StoreRepoCase):
    """d1e9 D1'': an attribute file makes an own or own-unrecorded store
    broken; wi runs no filter it names."""

    def filtered_store(self, own=True):
        store = self.make_own(own=own)
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        return store

    def assert_broken_and_silent(self, store, path):
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(f"{path} selects git attributes", rs.reason)
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertIn("selects git attributes", r.stdout)
        self.assertEqual(self.wi(["lint"], store).returncode, 3)
        self.assertEqual(self.marked(), [])

    def test_info_attributes(self):
        store = self.filtered_store()
        info = store / ".git" / "info"
        info.mkdir()
        (info / "attributes").write_text("* filter=mark\n")
        # control: plain git runs that filter
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        (store / "items" / "x.md").unlink()
        self.clear_marks()
        self.assert_broken_and_silent(store, ".git/info/attributes")

    def test_root_gitattributes(self):
        store = self.filtered_store()
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.assert_broken_and_silent(store, ".gitattributes")

    def test_deeper_gitattributes(self):
        store = self.filtered_store()
        (store / "items" / "sub").mkdir()
        (store / "items" / "sub" / ".gitattributes").write_text(
            "* filter=mark\n")
        self.assert_broken_and_silent(store, "items/sub/.gitattributes")

    def test_index_only_gitattributes(self):
        store = self.make_own()
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.git(store, "add", ".gitattributes")
        (store / ".gitattributes").unlink()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        self.assert_broken_and_silent(store, ".gitattributes")

    def test_unrecorded_store_with_attributes_is_broken(self):
        store = self.filtered_store(own=False)
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.assertEqual(self.state(store).state, "broken")

    def test_dedicated_store_keeps_its_attributes(self):
        store = self.make_own(host=False, own=False)
        (store / ".gitattributes").write_text("*.md text\n")
        self.assertEqual(self.state(store).state, "dedicated")
        r = self.wi(["lint"], store)
        self.assertNotIn("attributes", r.stdout + r.stderr)

    def test_global_attributes_file_runs_no_filter(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        attrs = self.tmp / "home" / "attributes"
        attrs.write_text("* filter=mark\n")
        self.git(self.tmp, "config", "--global", "core.attributesFile",
                 str(attrs))
        self.git(self.tmp, "config", "--global", "filter.mark.clean",
                 str(filt))
        (store / "items" / "x.md").write_text("x\n")
        # control: plain git reads the global attributes file
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        self.assertEqual(self.state(store).state, "own")
        r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    @unittest.skipIf(git_version() < (2, 41),
                     "git below 2.41 does not read GIT_ATTR_SOURCE")
    def test_attr_source_env_is_scrubbed(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        attrs = self.tmp / "attrs"
        attrs.mkdir()
        (attrs / ".gitattributes").write_text("* filter=mark\n")
        blob = subprocess.run(
            ["git", "hash-object", "-w", str(attrs / ".gitattributes")],
            cwd=store, env=self.env, capture_output=True, text=True,
            check=True).stdout.strip()
        tree = subprocess.run(
            ["git", "mktree"], cwd=store, env=self.env, capture_output=True,
            text=True, check=True,
            input=f"100644 blob {blob}\t.gitattributes\n").stdout.strip()
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md", env={"GIT_ATTR_SOURCE": tree})
        self.assertIn("clean", self.marked())      # control
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        with mock.patch.dict(os.environ, {"GIT_ATTR_SOURCE": tree}):
            r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marked(), [])

    @unittest.skipIf(git_version() < (2, 43),
                     "git below 2.43 does not read attr.tree")
    def test_attr_tree_in_store_config_is_pinned_empty(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        attrs = self.tmp / "attrs"
        attrs.mkdir()
        (attrs / ".gitattributes").write_text("* filter=mark\n")
        blob = subprocess.run(
            ["git", "hash-object", "-w", str(attrs / ".gitattributes")],
            cwd=store, env=self.env, capture_output=True, text=True,
            check=True).stdout.strip()
        tree = subprocess.run(
            ["git", "mktree"], cwd=store, env=self.env, capture_output=True,
            text=True, check=True,
            input=f"100644 blob {blob}\t.gitattributes\n").stdout.strip()
        self.git(store, "config", "attr.tree", tree)
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())      # control
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marked(), [])


class TestRunner(StoreRepoCase):
    """d1e9 D2: the hardened store runner."""

    def commit_via_runner(self, store, msg="runner"):
        (store / "items" / "two-bbbb.md").write_text(ITEM.format(iid="two-bbbb"))
        r = wi._store_git(store, "add", "-A", "--", "items")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = wi._store_git(store, "-c", "user.name=t", "-c", "user.email=t@t",
                          "commit", "-q", "-m", msg, "--", "items")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_no_hook_or_fsmonitor_runs(self):
        store = self.make_own()
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        for name in ("pre-commit", "post-commit", "commit-msg"):
            shutil.copy(self.marker(f"global-{name}"), hooks / name)
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        # control: plain git runs the global hooks
        (store / "items" / "c.md").write_text("c\n")
        self.git(store, "add", "items/c.md")
        self.git(store, "commit", "-q", "-m", "control")
        self.assertIn("global-pre-commit", self.marked())
        self.clear_marks()
        (store / ".git" / "hooks").mkdir(exist_ok=True)
        shutil.copy(self.marker("store-pre-commit"),
                    store / ".git" / "hooks" / "pre-commit")
        shutil.copy(self.marker("root-pre-commit"), store / "pre-commit")
        self.git(store, "config", "core.fsmonitor",
                 str(self.marker("fsmonitor")))
        self.commit_via_runner(store)
        wi._store_git(store, "status", "--porcelain")
        self.assertEqual(self.marked(), [])
        (store / "pre-commit").unlink()
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    def test_fsmonitor_control_and_prime_lint(self):
        store = self.make_own()
        self.git(store, "config", "core.fsmonitor",
                 str(self.marker("fsmonitor")))
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        self.git(store, "status", "--porcelain")
        self.assertIn("fsmonitor", self.marked())   # control
        self.clear_marks()
        (store / ".gitignore").write_text(".lock\n*.tmp*\nitems/\n")
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    def test_gpg_sign_with_missing_gpg_still_commits(self):
        store = self.make_own()
        self.git(self.tmp, "config", "--global", "commit.gpgSign", "true")
        self.git(self.tmp, "config", "--global", "gpg.program",
                 str(self.tmp / "no-such-gpg"))
        (store / "items" / "c.md").write_text("c\n")
        self.git(store, "add", "items/c.md")
        r = self.git(store, "commit", "-q", "-m", "control", check=False)
        self.assertNotEqual(r.returncode, 0)          # control
        self.commit_via_runner(store)

    def test_host_hook_env_acts_on_the_store(self):
        store = self.make_own()
        host = self.tmp / "host"
        host_index = (host / ".git" / "index").read_bytes()
        with mock.patch.dict(os.environ, {
                "GIT_DIR": str(host / ".git"),
                "GIT_WORK_TREE": str(host),
                "GIT_INDEX_FILE": str(host / ".git" / "index")}):
            r = wi._store_git(store, "rev-parse", "--show-toplevel")
            self.assertEqual(r.stdout.strip(), str(store))
            self.commit_via_runner(store)
        log = self.git(store, "log", "--format=%s").stdout.split()
        self.assertEqual(log[0], "runner")
        self.assertEqual((host / ".git" / "index").read_bytes(), host_index)

    def test_env_and_argv(self):
        store = self.make_own()
        seen = {}

        def fake(argv, **kw):
            seen.setdefault("calls", []).append((argv, kw["env"], kw["cwd"]))
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        with mock.patch.dict(os.environ, {"GIT_LITERAL_PATHSPECS": "1",
                                          "GIT_ATTR_SOURCE": "HEAD",
                                          "GIT_OBJECT_DIRECTORY": "/x",
                                          "GIT_ICASE_PATHSPECS": "1",
                                          "GIT_GLOB_PATHSPECS": "1",
                                          "GIT_NOGLOB_PATHSPECS": "1"}), \
                mock.patch.object(wi.subprocess, "run", fake):
            wi._store_git(store, "status")
            wi._store_git(store, "check-ignore", "-q", "items")
        (argv, env, cwd), (argv2, env2, _) = seen["calls"]
        self.assertEqual(cwd, str(store))
        for pin in ("core.hooksPath=/dev/null", "core.fsmonitor=false",
                    "commit.gpgSign=false", "gc.auto=0",
                    "maintenance.auto=false", "core.attributesFile=/dev/null",
                    f"attr.tree={wi.EMPTY_TREE}"):
            self.assertIn(pin, argv)
        self.assertEqual(argv[-1], "status")
        self.assertEqual(env["GIT_CEILING_DIRECTORIES"], str(store.parent))
        self.assertEqual(env["GIT_ATTR_NOSYSTEM"], "1")
        self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["LC_ALL"], "C")
        self.assertEqual(env["GIT_LITERAL_PATHSPECS"], "1")
        self.assertNotIn("GIT_ATTR_SOURCE", env)
        self.assertNotIn("GIT_OBJECT_DIRECTORY", env)
        for name in ("GIT_ICASE_PATHSPECS", "GIT_GLOB_PATHSPECS",
                     "GIT_NOGLOB_PATHSPECS"):
            self.assertNotIn(name, env)
            self.assertNotIn(name, env2)
        self.assertNotIn("GIT_LITERAL_PATHSPECS", env2)
        self.assertEqual(argv2[-3:], ["check-ignore", "-q", "items"])


class TestNestedRepo(StoreRepoCase):
    """Review round 1: git status recurses into a gitlink, where the nested
    repo's own config and attributes are not pinned."""

    def nested(self):
        store = self.make_own()
        sub = store / "items" / "sub"
        sub.mkdir()
        self.git(sub, "init", "-q", "--template=")
        (sub / "f.txt").write_text("one\n")
        self.git(sub, "add", "f.txt")
        self.git(sub, "commit", "-q", "-m", "sub")
        self.git(store, "add", "items/sub")
        self.git(store, "commit", "-q", "-m", "gitlink")
        (sub / ".git" / "info").mkdir()
        (sub / ".git" / "info" / "attributes").write_text("* filter=mark\n")
        self.git(sub, "config", "filter.mark.clean",
                 str(self.marker("clean", passthrough=True)))
        (sub / "f.txt").write_text("two\n")
        return store, sub

    def test_nested_repo_filter_never_runs(self):
        store, _ = self.nested()
        self.git(store, "status", "--porcelain")
        self.assertIn("clean", self.marked())      # control
        self.clear_marks()
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/sub/.git is a nested git repo or gitlink",
                      rs.reason)
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertIn("nested git repo or gitlink", r.stdout)
        # the status call itself never recurses, whatever the state says
        wi._uncommitted(store)
        self.assertEqual(self.marked(), [])

    def test_index_only_gitlink_is_broken(self):
        store, sub = self.nested()
        shutil.rmtree(sub)
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/sub is a nested git repo or gitlink", rs.reason)

    def test_git_file_below_root_is_broken(self):
        store = self.make_own()
        (store / "items" / ".git").write_text("gitdir: /nowhere\n")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/.git is a nested git repo", rs.reason)

    def test_gitattributes_name_is_case_blind(self):
        store = self.make_own()
        (store / "items" / ".GitAttributes").write_text("* filter=mark\n")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/.GitAttributes selects git attributes",
                      rs.reason)


class TestLazyFetch(StoreRepoCase):
    """F2 review round 1: a promisor remote fetches a missing object lazily,
    running the uploadpack (or ssh command) the store's config names."""

    def promisor_store(self, key="remote.origin.promisor", value="true"):
        store = self.make_own()
        tree = self.git(store, "rev-parse", "HEAD^{tree}").stdout.strip()
        (store / ".git" / "objects" / tree[:2] / tree[2:]).unlink()
        self.git(store, "config", "remote.origin.url",
                 str(self.tmp / "nowhere"))
        self.git(store, "config", "remote.origin.uploadpack",
                 str(self.marker("uploadpack")))
        if key.startswith("extensions."):
            self.git(store, "config", "core.repositoryformatversion", "1")
        self.git(store, "config", key, value)
        # control: plain git fetches the missing tree, running the script
        self.git(store, "status", "--porcelain", check=False)
        self.assertIn("uploadpack", self.marked())
        self.clear_marks()
        return store

    def test_runner_never_fetches_lazily(self):
        store = self.promisor_store()
        wi._store_git(store, "status", "--porcelain")
        wi._store_git(store, "cat-file", "-p", "HEAD^{tree}")
        self.assertEqual(self.marked(), [])

    def test_promisor_remote_is_broken(self):
        store = self.promisor_store()
        self.assertIn("sets remote.origin.promisor", self.state(store).reason)
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("a lazy fetch from a promisor remote can run commands",
                      r.stdout)
        r = self.wi(["commit", "-m", "x"], store)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("sets remote.origin.promisor", r.stderr)
        self.wi(["prime"], store)
        self.assertEqual(self.marked(), [])

    def test_partial_clone_extension_is_broken(self):
        store = self.promisor_store("extensions.partialClone", "origin")
        self.assertIn("sets extensions.partialclone",
                      self.state(store).reason)
        r = self.wi(["commit", "-m", "x"], store)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.marked(), [])


class TestEdges(StoreRepoCase):
    """Review round 1: a ceiling that would split, a read-only store."""

    def test_pathsep_in_parent_reads_as_unknown(self):
        base = self.tmp / "a:b"
        base.mkdir()
        store = base / ".work-items"
        self.store_files(store)
        self.git(store, "init", "-q", "--template=")
        self.assertIsNone(wi._store_git(store, "status"))
        self.assertEqual(self.state(store).state, "unknown")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    @unittest.skipIf(os.geteuid() == 0, "root ignores file modes")
    def test_read_only_store_lint_skips_uncommitted(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        store.chmod(0o555)
        self.addCleanup(store.chmod, 0o755)
        r = self.wi(["lint"], store)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("uncommitted check skipped", r.stderr)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestCustody(StoreRepoCase):
    """d1e9 D6': custody's reads run through the runner in an own store."""

    def test_items_rule_in_own_store_gitignore_is_named(self):
        store = self.make_own()
        (store / ".gitignore").write_text(".lock\n*.tmp*\nitems/\n")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn(".gitignore:3 'items/'", r.stdout)
        self.assertNotIn("--no-track", r.stdout)
        r = self.wi(["prime"], store)
        self.assertIn(".gitignore:3 'items/'", r.stdout)

    def test_custody_goes_through_the_runner(self):
        store = self.make_own()
        calls = []
        real = wi._store_git

        def spy(*a, **kw):
            calls.append(a[1:3])
            return real(*a, **kw)

        with mock.patch.object(wi, "_store_git", spy):
            wi.custody_warning(store)
        self.assertIn(("check-ignore", "-v"), calls)


class TestChecks(StoreRepoCase):
    """d1e9 D6: the store-repo rows of lint and prime."""

    def lint(self, store, code=0):
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r

    def test_clean_own_store(self):
        store = self.make_own()
        r = self.lint(store)
        self.assertIn("lint clean: 1 items", r.stdout)
        self.assertEqual(r.stderr, "")
        r = self.wi(["prime"], store)
        self.assertNotIn("WARNING", r.stdout)
        self.assertNotIn("note", r.stdout)

    def test_missing(self):
        store = self.tmp / "host" / ".work-items"
        self.make_host()
        self.store_files(store)
        r = self.lint(store, 3)
        self.assertIn("records `repo: own` in store.yaml but has no .git",
                      r.stdout)
        self.assertIn("`wi init --no-track` to start new history", r.stdout)
        self.assertIn("has no .git", self.wi(["prime"], store).stdout)

    def test_broken(self):
        store = self.tmp / "host" / ".work-items"
        self.make_host()
        self.store_files(store)
        (store / ".git").mkdir()
        r = self.lint(store, 3)
        self.assertIn("not a usable store repo", r.stdout)
        self.assertIn("never `rm -rf`", r.stdout)

    def test_uncommitted_is_a_notice(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        r = self.lint(store, 0)
        self.assertIn("1 uncommitted path(s)", r.stderr)
        self.assertIn("`wi commit`", r.stderr)
        self.assertIn("uncommitted", self.wi(["prime"], store).stdout)

    def test_uncommitted_skipped_under_a_held_lock(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        with open(store / ".lock", "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            start = time.monotonic()
            r = self.lint(store, 0)
            self.assertLess(time.monotonic() - start, 8)
        self.assertIn("uncommitted check skipped", r.stderr)
        self.assertNotIn("uncommitted path", r.stderr)

    def test_stale_index_lock(self):
        store = self.make_own()
        lock = store / ".git" / "index.lock"
        lock.write_text("")
        old = time.time() - 3600
        os.utime(lock, (old, old))
        r = self.lint(store, 3)
        self.assertIn(f"{lock} is 1h00m old", r.stdout)
        self.assertIn("remove it only when no git process runs", r.stdout)
        self.assertIn("index.lock", self.wi(["prime"], store).stdout)

    def test_fresh_index_lock_is_not_reported(self):
        store = self.make_own()
        (store / ".git" / "index.lock").write_text("")
        r = self.lint(store, 0)
        self.assertNotIn("index.lock", r.stdout)

    def test_host_does_not_ignore(self):
        store = self.make_own()
        (self.tmp / "host" / ".gitignore").write_text("")
        r = self.lint(store, 3)
        self.assertIn("does not ignore store", r.stdout)
        self.assertIn("`wi init --no-track`", r.stdout)
        # prime reads no host
        self.assertNotIn("does not ignore", self.wi(["prime"], store).stdout)

    def test_host_tracks_the_store(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        self.git(host, "add", "-f", ".work-items/README.md")
        self.git(host, "commit", "-q", "-m", "tracked")
        self.git(store, "init", "-q", "--template=")
        self.git(store, "add", "-A")
        self.git(store, "commit", "-q", "-m", "init")
        # the host's ls-files runs with fsmonitor off: a marker fsmonitor in
        # the host's config fires under plain git (control), never in lint
        self.git(host, "config", "core.fsmonitor",
                 str(self.marker("host-fsmonitor")))
        self.git(host, "ls-files", "-s", "--", ".work-items")
        self.assertIn("host-fsmonitor", self.marked())
        self.clear_marks()
        r = self.lint(store, 3)
        self.assertIn("tracks 1 path(s) under .work-items", r.stdout)
        self.assertIn("rm -r -q --cached -- .work-items", r.stdout)
        self.assertEqual(self.marked(), [])

    def test_remote_names_only(self):
        store = self.make_own()
        self.git(store, "remote", "add", "origin",
                 "https://user:secret@example.invalid/x.git")
        r = self.lint(store, 0)
        self.assertIn("has a remote (origin)", r.stderr)
        self.assertIn("meant to be local", r.stderr)
        self.assertNotIn("secret", r.stdout + r.stderr)
        self.assertNotIn("secret", self.wi(["prime"], store).stdout)

    def test_repo_value_other_than_own(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: tracked\nrepo: shared\n")
        r = self.lint(store, 3)
        self.assertIn("repo must be own (got 'shared')", r.stdout)

    def test_more_than_one_repo_line(self):
        store = self.make_own()
        (store / "store.yaml").write_text(
            "tracking: tracked\nrepo: own\nrepo: own\n")
        self.git(store, "commit", "-q", "-am", "yaml")
        r = self.lint(store, 3)
        self.assertIn("more than one repo: line", r.stdout)

    def test_prime_shows_one_store_repo_line(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        lock = store / ".git" / "index.lock"
        lock.write_text("")
        old = time.time() - 3600
        os.utime(lock, (old, old))
        out = self.wi(["prime"], store).stdout
        self.assertIn("uncommitted", out)        # first in table order
        self.assertNotIn("index.lock", out)

    def test_plain_store_unchanged(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        r = self.lint(store, 0)
        self.assertEqual(r.stderr, "")


class TestPathspec(StoreRepoCase):
    """d1e9 D4' and D4'': only existing paths, matched exactly."""

    def test_listing_match(self):
        self.assertEqual(wi._kept_by_listing(["archive"],
                                             ["archive/2026/x.md"]),
                         ["archive"])
        self.assertEqual(wi._kept_by_listing(["items/x.md"],
                                             ["items/x.md.tmp1"]), [])
        self.assertEqual(wi._kept_by_listing(["items/x.md"], ["items/x.md"]),
                         ["items/x.md"])

    def test_existing_paths(self):
        store = self.make_own()
        (store / "archive" / "2026").mkdir(parents=True)
        (store / "archive" / "2026" / "x.md").write_text("x\n")
        self.git(store, "add", "archive")
        self.git(store, "commit", "-q", "-m", "archive")
        shutil.rmtree(store / "archive")
        self.assertEqual(
            wi.existing_paths(store, wi.OWN_PATHS),
            ["items", "archive", "README.md", "store.yaml", ".gitignore"])
        self.git(store, "rm", "-r", "-q", "--cached", "archive")
        self.assertNotIn("archive", wi.existing_paths(store, wi.OWN_PATHS))


class TestCommit(StoreRepoCase):
    """d1e9 D5, D5' (F2): `wi commit`, one row of its table per test group."""

    MSG = "chore: work-item store - landed"

    def commit(self, store, *args, code=0, env=None):
        r = self.wi(["commit", *args], store, env=env)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r

    def run_main(self, store, *args):
        """wi in this process (for patches); (exit, stdout, stderr)."""
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = wi.main(["--root", str(store), "commit", *args])
        return code, out.getvalue(), err.getvalue()

    def subjects(self, repo):
        return self.git(repo, "log", "--format=%s").stdout.splitlines()

    def files_in_head(self, repo):
        return self.git(repo, "show", "--name-only", "--no-renames",
                        "--format=", "HEAD").stdout.split()

    def edit(self, store, iid="one-aaaa", extra="edit\n"):
        (store / "items" / f"{iid}.md").write_text(
            ITEM.format(iid=iid) + extra)

    def lock_free(self, store):
        with open(store / ".lock", "a") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return False
            fcntl.flock(fh, fcntl.LOCK_UN)
            return True

    # -- own -------------------------------------------------------------

    def test_own_hand_edit_committed_with_no_archive(self):
        store = self.make_own()
        self.assertFalse((store / "archive").exists())
        self.edit(store)
        r = self.commit(store, "-m", self.MSG)
        sha = self.git(store, "rev-parse", "--short", "HEAD").stdout.strip()
        self.assertEqual(r.stdout, f"committed {sha}\n")
        self.assertEqual(self.subjects(store)[0], self.MSG)
        self.assertEqual(self.files_in_head(store), ["items/one-aaaa.md"])
        self.assertEqual(self.git(store, "status", "--porcelain").stdout, "")
        self.assertEqual(self.wi(["lint"], store).stderr, "")

    def test_own_default_message(self):
        store = self.make_own()
        self.edit(store)
        self.commit(store)
        self.assertEqual(self.subjects(store)[0], wi.COMMIT_DEFAULT_MESSAGE)

    def test_own_nothing_to_commit(self):
        store = self.make_own()
        before = self.subjects(store)
        r = self.commit(store, "-m", self.MSG)
        self.assertEqual(r.stdout, "nothing to commit\n")
        self.assertEqual(self.subjects(store), before)

    def test_own_new_removed_and_archived_paths(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").unlink()
        (store / "items" / "new-cccc.md").write_text(
            ITEM.format(iid="new-cccc"))
        (store / "archive" / "2026").mkdir(parents=True)
        (store / "archive" / "2026" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa"))
        self.commit(store, "-m", self.MSG)
        self.assertEqual(sorted(self.files_in_head(store)),
                         ["archive/2026/one-aaaa.md", "items/new-cccc.md",
                          "items/one-aaaa.md"])
        self.assertEqual(self.git(store, "status", "--porcelain").stdout, "")

    def test_own_hand_staged_file_stays_staged_and_out(self):
        store = self.make_own()
        (store / "scratch.txt").write_text("staged by hand\n")
        self.git(store, "add", "scratch.txt")
        self.edit(store)
        self.commit(store, "-m", self.MSG)
        self.assertEqual(self.files_in_head(store), ["items/one-aaaa.md"])
        self.assertEqual(self.git(store, "diff", "--cached",
                                  "--name-only").stdout.split(),
                         ["scratch.txt"])

    def test_own_waits_for_the_lock_then_exits_4(self):
        store = self.make_own()
        self.edit(store)
        before = self.subjects(store)
        with open(store / ".lock", "a") as fh, \
                mock.patch.object(wi.Lock.__init__, "__defaults__", (0.3,)):
            fcntl.flock(fh, fcntl.LOCK_EX)
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 4, out + err)
        self.assertIn("lock timeout", err)
        self.assertEqual(self.subjects(store), before)
        self.assertIn("items/one-aaaa.md",
                      self.git(store, "status", "--porcelain").stdout)

    def test_own_runs_no_hook_fsmonitor_or_signing(self):
        store = self.make_own()
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        for name in ("pre-commit", "commit-msg", "post-commit"):
            shutil.copy(self.marker(f"global-{name}"), hooks / name)
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        self.git(store, "commit", "-q", "--allow-empty", "-m", "control")
        self.assertIn("global-pre-commit", self.marked())   # control
        self.clear_marks()
        (store / ".git" / "hooks").mkdir(exist_ok=True)
        shutil.copy(self.marker("store-pre-commit"),
                    store / ".git" / "hooks" / "pre-commit")
        self.git(store, "config", "core.fsmonitor",
                 str(self.marker("fsmonitor")))
        self.git(self.tmp, "config", "--global", "commit.gpgSign", "true")
        self.git(self.tmp, "config", "--global", "gpg.program",
                 str(self.tmp / "no-such-gpg"))
        self.edit(store)
        self.commit(store, "-m", self.MSG)
        self.assertEqual(self.subjects(store)[0], self.MSG)
        self.assertEqual(self.marked(), [])

    def test_own_host_hook_env_does_not_reach_the_host(self):
        store = self.make_own()
        host = self.tmp / "host"
        head = self.git(host, "rev-parse", "HEAD").stdout
        index = (host / ".git" / "index").read_bytes()
        self.edit(store)
        self.commit(store, "-m", self.MSG, env={
            "GIT_DIR": str(host / ".git"), "GIT_WORK_TREE": str(host),
            "GIT_INDEX_FILE": str(host / ".git" / "index")})
        self.assertEqual(self.subjects(store)[0], self.MSG)
        self.assertEqual(self.git(host, "rev-parse", "HEAD").stdout, head)
        self.assertEqual((host / ".git" / "index").read_bytes(), index)

    def test_own_identity_fallback(self):
        store = self.make_own()
        r = subprocess.run(["git", "var", "GIT_AUTHOR_IDENT"], cwd=store,
                           env=self.env, capture_output=True)
        if r.returncode == 0:
            self.skipTest("git finds an identity on this machine")
        self.edit(store)
        self.commit(store, "-m", self.MSG)
        self.assertEqual(self.git(store, "log", "-1",
                                  "--format=%an <%ae>|%cn <%ce>").stdout,
                         "wi <wi@localhost>|wi <wi@localhost>\n")
        # nothing is written to any config
        self.assertNotIn("user", (store / ".git" / "config").read_text())
        self.assertEqual(self.gitconfig.read_text(), "")

    def test_own_identity_from_env_wins(self):
        store = self.make_own()
        self.edit(store)
        self.commit(store, "-m", self.MSG, env={
            "GIT_AUTHOR_NAME": "Ann", "GIT_AUTHOR_EMAIL": "ann@example.invalid",
            "GIT_COMMITTER_NAME": "Cy",
            "GIT_COMMITTER_EMAIL": "cy@example.invalid"})
        self.assertEqual(self.git(store, "log", "-1",
                                  "--format=%an|%cn").stdout, "Ann|Cy\n")

    def test_own_index_lock_conflict_retries_then_fails(self):
        store = self.make_own()
        lock = store / ".git" / "index.lock"
        lock.write_text("")
        self.edit(store)
        before = self.subjects(store)
        start = time.monotonic()
        r = self.commit(store, "-m", self.MSG, code=3)
        self.assertGreaterEqual(time.monotonic() - start,
                                wi.INDEX_LOCK_RETRIES * wi.INDEX_LOCK_WAIT)
        self.assertIn("not committed", r.stderr)
        self.assertIn("index.lock", r.stderr)
        self.assertTrue(lock.exists())        # never deleted
        self.assertEqual(self.subjects(store), before)
        self.assertTrue(self.lock_free(store))

    def test_own_retry_counts(self):
        store = self.make_own()
        self.edit(store)
        calls = []
        busy = subprocess.CompletedProcess(
            [], 128, "", "fatal: Unable to create '/x/.git/index.lock': "
            "File exists.")

        def fake(root, *args, **kw):
            if "add" in args:
                calls.append(args)
                return busy
            return real(root, *args, **kw)

        real = wi._store_git
        with mock.patch.object(wi, "_store_git", fake), \
                mock.patch.object(wi, "INDEX_LOCK_WAIT", 0.0):
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 3)
        self.assertEqual(len(calls), 1 + wi.INDEX_LOCK_RETRIES)

    def test_own_shared_deadline(self):
        store = self.make_own()
        self.edit(store)
        with mock.patch.object(wi, "COMMIT_DEADLINE", 0.0):
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 3, out + err)
        self.assertIn("not committed: timed out", err)
        self.assertTrue(self.lock_free(store))

    def test_own_killed_call_names_index_lock(self):
        store = self.make_own()
        self.edit(store)
        real = wi._store_git
        seen = {}

        def fake(root, *args, **kw):
            seen.setdefault("timeouts", []).append(kw.get("timeout"))
            return None if "commit" in args else real(root, *args, **kw)

        with mock.patch.object(wi, "_store_git", fake):
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 3, out + err)
        self.assertIn(f"if {store / '.git' / 'index.lock'} is left, remove "
                      "it only when no git process runs", err)
        # every commit step is bounded by what is left of the 5 s deadline
        steps = seen["timeouts"][-4:]
        self.assertTrue(all(0 < t <= wi.COMMIT_DEADLINE for t in steps),
                        steps)

    def test_own_gc_runs_after_the_lock_is_released(self):
        store = self.make_own()
        real = wi._store_git
        gc = []

        def spy(root, *args, **kw):
            if "gc" in args:
                gc.append((args, self.lock_free(store)))
            return real(root, *args, **kw)

        with mock.patch.object(wi, "_store_git", spy):
            code, out, _ = self.run_main(store, "-m", self.MSG)
            self.assertEqual(out, "nothing to commit\n")
            self.assertEqual(gc, [])          # no commit, no gc
            self.edit(store)
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 0, out + err)
        ((args, free),) = gc
        self.assertTrue(free)
        self.assertIn(f"gc.auto={wi.GC_AUTO}", args)
        self.assertIn("gc.autoDetach=false", args)
        self.assertEqual(args[-2:], ("--auto", "-q"))

    def test_own_commit_goes_only_through_the_runner(self):
        store = self.make_own()
        self.edit(store)
        plain = []
        real = wi._git

        def spy(cwd, *args, **kw):
            plain.append((str(cwd), args))
            return real(cwd, *args, **kw)

        with mock.patch.object(wi, "_git", spy):
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 0, out + err)
        # plain git only asks for the host around the store, from its parent
        self.assertTrue(all(os.path.realpath(cwd) != str(store)
                            and "commit" not in args and "add" not in args
                            for cwd, args in plain), plain)

    # -- own repos wi did not set up, or cannot trust ---------------------

    def test_unrecorded_is_refused(self):
        store = self.make_own(own=False)
        self.edit(store)
        before = self.subjects(store)
        r = self.commit(store, "-m", self.MSG, code=1)
        self.assertIn("is its own git repo, not set up by wi: "
                      "`wi init --no-track` adopts it", r.stderr)
        self.assertEqual(self.subjects(store), before)

    def test_missing_is_refused(self):
        self.make_host()
        store = self.tmp / "host" / ".work-items"
        self.store_files(store)
        r = self.commit(store, code=1)
        self.assertIn("records `repo: own` in store.yaml but has no .git",
                      r.stderr)

    def test_broken_is_refused_and_never_reaches_the_host(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        (store / ".git").mkdir()
        head = self.git(host, "rev-parse", "HEAD").stdout
        r = self.commit(store, code=1)
        self.assertIn("not a usable store repo", r.stderr)
        self.assertEqual(self.git(host, "rev-parse", "HEAD").stdout, head)
        self.assertEqual(self.git(host, "status", "--porcelain").stdout, "")

    def test_attribute_file_is_refused(self):
        store = self.make_own()
        (store / "items" / ".gitattributes").write_text("*.md filter=x\n")
        r = self.commit(store, code=1)
        self.assertIn("selects git attributes", r.stderr)

    def test_old_location_git_is_refused(self):
        host = self.make_host()
        store = host / ".work"
        self.store_files(store, own=False)
        self.git(store, "init", "-q", "--template=")
        r = self.commit(store, code=1)
        self.assertIn("old location", r.stderr)

    def test_git_not_answering_is_exit_3(self):
        base = self.tmp / "a:b"
        base.mkdir()
        store = base / ".work-items"
        self.store_files(store)
        self.git(store, "init", "-q", "--template=")
        r = self.commit(store, code=3)
        self.assertIn("git did not answer", r.stderr)

    # -- tracked by the repo that holds it --------------------------------

    def test_host_tracked_store(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "store")
        hook = host / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        shutil.copy(self.marker("host-pre-commit"), hook)
        (host / "src.txt").write_text("staged host change\n")
        self.git(host, "add", "src.txt")
        self.edit(store)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        r = self.commit(store, "-m", self.MSG, env=env)
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(self.subjects(host)[0], self.MSG)
        self.assertEqual(self.files_in_head(host),
                         [".work-items/items/one-aaaa.md"])
        self.assertEqual(self.git(host, "diff", "--cached",
                                  "--name-only").stdout.split(), ["src.txt"])
        self.assertIn("host-pre-commit", self.marked())   # its rules run
        self.assertFalse((store / ".git").exists())

    def test_host_tracked_hook_refusal_is_exit_3(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "store")
        hook = host / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("#!/bin/sh\necho refused by policy >&2\nexit 1\n")
        hook.chmod(0o755)
        self.edit(store)
        before = self.subjects(host)
        r = self.commit(store, "-m", self.MSG, code=3, env={
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
        self.assertIn("not committed: refused by policy", r.stderr)
        self.assertEqual(self.subjects(host), before)
        self.assertTrue(self.lock_free(store))

    def test_sidecar_store(self):
        host = self.make_host(ignore=False)
        (host / ".gitignore").write_text("/.claude-sandbox/\n")
        sidecar = host / ".claude-sandbox"
        store = sidecar / "work"
        self.store_files(store, own=False)
        self.git(sidecar, "init", "-q")
        self.git(sidecar, "add", "-A")
        self.git(sidecar, "commit", "-q", "-m", "sidecar")
        host_before = self.subjects(host)
        self.edit(store)
        r = self.commit(store, "-m", self.MSG, env={
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(self.subjects(sidecar)[0], self.MSG)
        self.assertEqual(self.files_in_head(sidecar),
                         ["work/items/one-aaaa.md"])
        self.assertEqual(self.subjects(host), host_before)

    def test_dedicated_store_commits_by_its_own_rules(self):
        store = self.make_own(host=False, own=False)
        hook = store / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        shutil.copy(self.marker("dedicated-pre-commit"), hook)
        self.edit(store)
        self.commit(store, "-m", self.MSG, env={
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
        self.assertEqual(self.subjects(store)[0], self.MSG)
        self.assertIn("dedicated-pre-commit", self.marked())

    # -- ignored, outside git ----------------------------------------------

    def test_ignored_store(self):
        host = self.make_host()                 # ignores /.work-items/
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: tracked\n")
        before = self.subjects(host)
        r = self.commit(store, "-m", self.MSG)
        self.assertEqual(r.stdout, f"nothing to commit: {store} is "
                         f"git-ignored by {host}\n")
        self.assertEqual(self.subjects(host), before)
        self.assertFalse((store / ".git").exists())

    def test_recorded_ignored_store(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: ignored\n")
        before = self.subjects(host)
        r = self.commit(store)
        self.assertIn("is recorded git-ignored", r.stdout)
        self.assertEqual(self.subjects(host), before)

    def test_outside_git(self):
        store = self.tmp / "loose" / ".work-items"
        self.store_files(store, own=False)
        r = self.commit(store)
        self.assertEqual(r.stdout,
                         f"nothing to commit: {store} is in no git repo\n")

    def test_git_missing(self):
        empty = self.tmp / "nobin"
        empty.mkdir()
        # a store with history of its own: its changes stay uncommitted
        store = self.make_own()
        self.edit(store)
        r = self.commit(store, code=3, env={"PATH": str(empty)})
        self.assertIn(f"store {store} not committed: git not found",
                      r.stderr)
        # recorded own, its .git gone: the same
        shutil.rmtree(store / ".git")
        self.commit(store, code=3, env={"PATH": str(empty)})
        # any other store: nothing to commit
        plain = self.tmp / "loose" / ".work-items"
        self.store_files(plain, own=False)
        r = self.commit(plain, env={"PATH": str(empty)})
        self.assertIn("is in no git repo (git not found)", r.stdout)

    # -- review round 1 ------------------------------------------------------

    def test_empty_items_in_own_store_commits(self):
        # every item archived: items/ is an empty directory
        store = self.make_own()
        (store / "archive" / "2026").mkdir(parents=True)
        (store / "items" / "one-aaaa.md").rename(
            store / "archive" / "2026" / "one-aaaa.md")
        r = self.commit(store, "-m", self.MSG)
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(self.git(store, "show", "--name-status",
                                  "--format=", "HEAD").stdout.split()[0][0],
                         "R")
        self.assertEqual(self.commit(store).stdout, "nothing to commit\n")

    def test_own_store_with_no_commit_yet_and_empty_items(self):
        store = self.tmp / "host" / ".work-items"
        self.make_host()
        self.store_files(store, items=())
        self.git(store, "init", "-q", "--template=")
        r = self.commit(store, "-m", self.MSG)
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(sorted(self.files_in_head(store)),
                         [".gitignore", "README.md", "store.yaml"])

    def test_host_tracked_store_with_empty_items(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False, items=())
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "store")
        (store / "README.md").write_text("# Work items\nedited\n")
        r = self.commit(store, "-m", self.MSG, env=self.IDENT)
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(self.files_in_head(host), [".work-items/README.md"])

    def test_existing_paths_drops_empty_and_ignored_only(self):
        store = self.make_own()
        (store / "archive").mkdir()                       # empty
        (store / "items" / "one-aaaa.md").unlink()        # a removal
        self.assertEqual(wi.existing_paths(store, wi.OWN_PATHS),
                         ["items", "README.md", "store.yaml", ".gitignore"])
        self.git(store, "add", "-A")
        self.git(store, "commit", "-q", "-m", "gone")
        (store / "items" / "x.md.tmp1").write_text("tmp\n")   # ignored
        self.assertNotIn("items", wi.existing_paths(store, wi.OWN_PATHS))

    def test_unanswered_host_lookup_is_unknown_and_refused(self):
        # an unrecorded own repo is never taken for a dedicated one, whose
        # commit runs plain git (its hooks), when git did not answer
        store = self.make_own(own=False)
        hook = store / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        shutil.copy(self.marker("store-pre-commit"), hook)
        self.edit(store)
        before = self.subjects(store)
        real = wi._git

        def slow(cwd, *args, **kw):
            if args[:2] == ("rev-parse", "--show-toplevel"):
                return None
            return real(cwd, *args, **kw)

        with mock.patch.object(wi, "_git", slow):
            self.assertEqual(self.state(store).state, "unknown")
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 3, out + err)
        self.assertIn("git did not answer", err)
        self.assertEqual(self.subjects(store), before)
        self.assertEqual(self.marked(), [])

    def test_host_lookup_failing_otherwise_is_unknown(self):
        store = self.make_own(own=False)
        real = wi._git

        def broken(cwd, *args, **kw):
            if args[:2] == ("rev-parse", "--show-toplevel"):
                return subprocess.CompletedProcess(
                    args, 128, "", "fatal: unsafe repository\n")
            return real(cwd, *args, **kw)

        with mock.patch.object(wi, "_git", broken):
            self.assertEqual(self.state(store).state, "unknown")
        # outside any repo, git says so: no host, a dedicated store
        self.assertEqual(
            self.state(self.make_own(host=False, own=False)).state,
            "dedicated")

    IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def test_tracked_commit_ignores_the_callers_git_steering(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "store")
        self.edit(store)
        elsewhere = self.tmp / "elsewhere-objects"
        elsewhere.mkdir()
        env = dict(self.IDENT, GIT_LITERAL_PATHSPECS="1",
                   GIT_OBJECT_DIRECTORY=str(elsewhere),
                   GIT_COMMON_DIR=str(self.tmp / "no-such-common"))
        r = self.commit(store, "-m", self.MSG, env=env)
        self.assertTrue(r.stdout.startswith("committed "), r.stdout)
        self.assertEqual(self.subjects(host)[0], self.MSG)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.git(host, "cat-file", "-e", "HEAD^{tree}")
        # an ignored store is still read as ignored under that env
        ignored = self.make_host(name="ign") / ".work-items"
        self.store_files(ignored, own=False)
        r = self.commit(ignored, env={"GIT_LITERAL_PATHSPECS": "1"})
        self.assertIn("is git-ignored by", r.stdout)

    def test_tracked_timeout_names_the_repos_index_lock(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "store")
        self.edit(store)
        real = wi._git

        def killed(cwd, *args, **kw):
            return None if "commit" in args else real(cwd, *args, **kw)

        with mock.patch.object(wi, "_git", killed):
            code, out, err = self.run_main(store, "-m", self.MSG)
        self.assertEqual(code, 3, out + err)
        self.assertIn(f"timed out; if {host / '.git' / 'index.lock'} is "
                      f"left, remove it only when no git process runs in "
                      f"{host}", err)

    # -- the message ---------------------------------------------------------

    def test_secret_message_is_refused(self):
        store = self.make_own()
        self.edit(store)
        before = self.subjects(store)
        value = "Zq8vN3kLm2Pw7Rt5Xy9B"
        r = self.commit(store, "-m", f"chore: store - token={value}", code=1)
        self.assertIn("the message: likely secret value", r.stderr)
        self.assertIn("nothing committed", r.stderr)
        self.assertNotIn(value, r.stdout + r.stderr)
        self.assertEqual(self.subjects(store), before)

    def test_empty_message_is_refused(self):
        store = self.make_own()
        self.edit(store)
        r = self.commit(store, "-m", "  ", code=1)
        self.assertIn("the message is empty", r.stderr)


class InitCase(StoreRepoCase):
    """Helpers for the `wi init` tests (d1e9 F3)."""


    def init(self, store, *flags, code=0, env=None):
        r = self.wi(["init", *flags], store, env=env)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r

    def run_init(self, store, *flags):
        """wi init in this process (for patches); (exit, stdout, stderr)."""
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = wi.main(["--root", str(store), "init", *flags])
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def subjects(self, repo):
        return self.git(repo, "log", "--format=%s").stdout.splitlines()

    def files_in_head(self, repo):
        return sorted(self.git(repo, "ls-tree", "-r", "--name-only",
                               "HEAD").stdout.split())

    def snapshot(self, *dirs):
        """Every path under dirs with its bytes (a symlink's target), to
        prove that nothing was written."""
        snap = {}
        for d in dirs:
            for dirpath, dirnames, files in os.walk(d):
                for name in dirnames + files:
                    p = Path(dirpath) / name
                    snap[str(p)] = (os.readlink(p) if p.is_symlink() else
                                    p.read_bytes() if p.is_file() else None)
        return snap

    def assert_own_store(self, store, subject, files):
        self.assertEqual(wi.read_tracking(store), "tracked")
        self.assertTrue(wi.read_repo_own(store))
        self.assertEqual(self.state(store).state, "own")
        self.assertEqual(self.subjects(store)[0], subject)
        self.assertEqual(self.files_in_head(store), sorted(files))
        self.assertEqual(self.git(store, "status", "--porcelain").stdout, "")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stderr, "")

    NEW_FILES = [".gitignore", "README.md", "store.yaml"]

    def assert_refused(self, store, *flags, says, host=None):
        host = host or store.parent
        watched = [host] + ([store] if store.exists() else [])
        before = self.snapshot(*watched)
        r = self.init(store, *flags or ("--no-track",), code=1)
        self.assertIn(says, r.stderr)
        self.assertIn("nothing written", r.stderr)
        self.assertEqual(self.snapshot(*watched), before)
        return r


class TestInit(InitCase):
    """d1e9 D3 (F3): `wi init`'s git-ignored choice gives the store its own
    repo, new or adopted; the refusals before anything is written; the
    own-unrecorded and no-history notices it answers."""

    # -- a new store -----------------------------------------------------

    def test_new_store_gets_its_own_repo(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        r = self.init(store, "--no-track")
        self.assertEqual((host / ".gitignore").read_text(), "/.work-items/\n")
        self.assertIn(f"own repo: created {store / '.git'}", r.stdout)
        self.assertIn("committed ", r.stdout)
        # an empty template: no sample hooks, no description, no info/
        self.assertEqual(sorted(os.listdir(store / ".git")),
                         ["COMMIT_EDITMSG", "HEAD", "config", "index", "logs",
                          "objects", "refs"])
        self.assertEqual((store / ".git" / "HEAD").read_text(),
                         "ref: refs/heads/main\n")
        cfg = self.git(store, "config", "--local", "--list").stdout
        self.assertIn("core.hookspath=/dev/null", cfg)
        self.assertIn("core.fsmonitor=false", cfg)
        self.assertEqual((store / "store.yaml").read_text().splitlines()[1:],
                         ["tracking: tracked", "repo: own"])
        # one commit, with no archive/ and an empty items/
        self.assertEqual(self.subjects(store), ["wi init: store created"])
        self.assert_own_store(store, "wi init: store created", self.NEW_FILES)
        # the host does not see the store
        self.assertEqual(self.git(host, "status", "--porcelain").stdout,
                         "?? .gitignore\n")

    def test_host_line_is_written_before_git_init(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        seen = []
        real = wi._store_git

        def spy(root, *args, **kw):
            if args[:1] == ("init",):
                gi = host / ".gitignore"
                seen.append((gi.read_text() if gi.exists() else None,
                             os.path.lexists(store / ".git")))
            return real(root, *args, **kw)
        with mock.patch.object(wi, "_store_git", spy):
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(seen, [("/.work-items/\n", False)])

    def test_no_terminal_default_and_menu_choice_2(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        r = self.init(store)                     # subprocess: no terminal
        self.assertIn("WARNING no terminal", r.stderr)
        self.assertIn("with its own local repo", r.stderr)
        self.assert_own_store(store, "wi init: store created", self.NEW_FILES)
        host2 = self.make_host("host2", ignore=False)
        store2 = host2 / ".work-items"
        import io
        out = io.StringIO()
        with mock.patch.object(wi, "_interactive", return_value=True), \
                mock.patch.object(sys, "stdin", io.StringIO("2\n")), \
                contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = wi.main(["--root", str(store2), "init"])
        self.assertEqual(code, 0)
        self.assertIn("the repo ignores the store, which keeps its own local "
                      "history [default]", out.getvalue())
        self.assert_own_store(store2, "wi init: store created",
                              self.NEW_FILES)

    def test_new_store_outside_any_repo(self):
        store = self.tmp / "loose" / ".work-items"
        r = self.init(store, "--no-track")
        self.assertIn("not in a git repo: no .gitignore written", r.stdout)
        self.assertFalse((self.tmp / "loose" / ".gitignore").exists())
        self.assert_own_store(store, "wi init: store created", self.NEW_FILES)
        self.assertIsNone(self.state(store).host)
        # a rerun is idempotent: nothing new to commit
        r = self.init(store, "--no-track")
        self.assertIn("nothing to commit", r.stdout)
        self.assertEqual(len(self.subjects(store)), 1)

    def test_rerun_on_an_own_store_commits_what_is_outstanding(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.init(store, "--no-track")
        (store / "items" / "one-aaaa.md").write_text(ITEM.format(iid="one-aaaa"))
        self.init(store, "--no-track")
        self.assertEqual(self.subjects(store)[0], "wi init: adopted 1 item")
        self.assertEqual((host / ".gitignore").read_text(), "/.work-items/\n")

    def test_first_commit_falls_back_to_wi_identity(self):
        r = subprocess.run(["git", "var", "GIT_AUTHOR_IDENT"], cwd=self.tmp,
                           env=self.env, capture_output=True)
        if r.returncode == 0:
            self.skipTest("git finds an identity on this machine")
        store = self.make_host(ignore=False) / ".work-items"
        self.init(store, "--no-track")
        self.assertEqual(self.git(store, "log", "-1",
                                  "--format=%an <%ae>").stdout,
                         "wi <wi@localhost>\n")
        self.assertNotIn("user", (store / ".git" / "config").read_text())

    # -- adopting --------------------------------------------------------

    def test_adopt_a_plain_ignored_store_with_items(self):
        host = self.make_host()                  # ignores /.work-items/
        store = host / ".work-items"
        self.store_files(store, own=False, items=("one-aaaa", "two-bbbb"))
        (store / "store.yaml").write_text("tracking: ignored\n")
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("has no history of its own", r.stdout + r.stderr)
            self.assertIn("`wi init --no-track` gives it its own local repo",
                          r.stdout + r.stderr)
        r = self.init(store, "--no-track")
        self.assertIn("no line added", r.stdout)
        self.assertEqual((host / ".gitignore").read_text(), "/.work-items/\n")
        self.assert_own_store(store, "wi init: adopted 2 items",
                              self.NEW_FILES + ["items/one-aaaa.md",
                                                "items/two-bbbb.md"])
        self.assertNotIn("no history", self.wi(["prime"], store).stdout)

    def test_adopt_a_hand_made_repo_keeps_its_history(self):
        store = self.make_own(own=False)         # committed, unrecorded
        self.git(store, "branch", "-m", "trunk")
        first = self.git(store, "rev-parse", "HEAD").stdout.strip()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        # before: the unrecorded notice, and wi commit refuses it
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertIn("is its own git repo, not set up by wi", r.stdout
                          + r.stderr)
            self.assertIn("`wi init --no-track` adopts it, history kept",
                          r.stdout + r.stderr)
        self.assertEqual(self.wi(["lint"], store).returncode, 0)
        r = self.init(store)                     # no flag: a note only
        self.assertIn("`wi init --no-track` adopts it", r.stderr)
        self.assertFalse(wi.read_repo_own(store))
        gi = (self.tmp / "host" / ".gitignore").read_bytes()
        r = self.init(store, "--no-track")
        self.assertIn(f"own repo: adopted {store / '.git'} (its history "
                      "kept)", r.stdout)
        # the host's line is found from the host, not from the store's repo
        self.assertIn("already ignored by git (.gitignore:1 "
                      "'/.work-items/'): no line added", r.stdout)
        self.assertEqual((self.tmp / "host" / ".gitignore").read_bytes(), gi)
        self.assertEqual(self.git(store, "rev-parse", "HEAD^").stdout.strip(),
                         first)
        self.assertEqual(self.git(store, "symbolic-ref", "HEAD").stdout,
                         "refs/heads/trunk\n")
        self.assertEqual(self.subjects(store),
                         ["wi init: adopted 1 item", "init"])
        self.assertEqual(self.git(store, "show", "--name-only", "--format=",
                                  "HEAD").stdout.split(),
                         ["items/one-aaaa.md", "store.yaml"])
        cfg = self.git(store, "config", "--local", "--list").stdout
        self.assertIn("core.hookspath=/dev/null", cfg)
        self.assertIn("core.fsmonitor=false", cfg)
        self.assertEqual(self.wi(["lint"], store).stderr, "")

    def test_adopt_a_repo_with_a_remote_and_lint_names_it(self):
        store = self.make_own(own=False)
        self.git(store, "remote", "add", "origin",
                 "https://user:secret@example.invalid/store.git")
        self.init(store, "--no-track")
        self.assertTrue(wi.read_repo_own(store))
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("has a remote (origin)", r.stderr)
        self.assertNotIn("secret", r.stdout + r.stderr)

    def test_the_fixes_that_name_init_no_track_work(self):
        # F1's lint rows name `wi init --no-track` as their fix
        cases = {
            # own, missing: start new history
            "missing": lambda s, h: shutil.rmtree(s / ".git"),
            # the host does not ignore the store: init adds the line
            "host line": lambda s, h: (h / ".gitignore").write_text(""),
            # repo: other than own: init rewrites it
            "repo value": lambda s, h: (s / "store.yaml").write_text(
                "tracking: tracked\nrepo: mine\n"),
            # more than one repo: line
            "two repo lines": lambda s, h: (s / "store.yaml").write_text(
                "tracking: tracked\nrepo: own\nrepo: own\n"),
        }
        for i, (name, breakit) in enumerate(cases.items()):
            with self.subTest(name):
                host = self.make_host(f"host{i}")
                store = host / ".work-items"
                self.init(store, "--no-track")
                breakit(store, host)
                r = self.wi(["lint"], store)
                self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
                self.assertIn("wi init --no-track", r.stdout)
                self.init(store, "--no-track")
                r = self.wi(["lint"], store)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(r.stderr, "")
                self.assertEqual((store / "store.yaml").read_text()
                                 .splitlines()[1:],
                                 ["tracking: tracked", "repo: own"])

    # -- refusals: nothing written ---------------------------------------

    def test_refuses_a_broken_git(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / ".git").mkdir()
        self.assert_refused(store, says="not a usable store repo: .git is "
                            "not a usable repository")

    def test_refuses_a_git_pointing_outside(self):
        host = self.make_host()
        wt = self.tmp / "wt"
        self.git(host, "worktree", "add", "-q", "--detach", str(wt))
        store = host / ".work-items"
        self.store_files(store, own=False)
        shutil.copy(wt / ".git", store / ".git")
        self.assert_refused(store, says=".git points outside the store")

    def test_refuses_a_repo_holding_other_files(self):
        store = self.make_own(own=False)
        (store / "src").mkdir()
        (store / "src" / "main.c").write_text("int main;\n")
        self.git(store, "add", "src/main.c")
        self.git(store, "commit", "-q", "-m", "code")
        self.assert_refused(store, says="is a git repo holding other files "
                            "(src/main.c): refusing to adopt it")

    def test_refuses_when_the_host_tracks_the_store(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(host, "add", ".work-items")
        self.git(host, "commit", "-q", "-m", "tracked store")
        n = len(self.git(host, "ls-files", ".work-items").stdout.split())
        self.assert_refused(store, says=f"tracks {n} path(s) under "
                            ".work-items: untrack them first")

    def test_refuses_attribute_files_and_nested_repos(self):
        cases = {
            "root .gitattributes": lambda s: (s / ".gitattributes")
            .write_text("*.md filter=mark\n"),
            "deep .gitattributes": lambda s: (
                (s / "items" / "sub").mkdir(),
                (s / "items" / "sub" / ".gitattributes").write_text("x\n")),
            "nested repo": lambda s: (s / "items" / "inner" / ".git").mkdir(
                parents=True),
        }
        for i, (name, plant) in enumerate(cases.items()):
            with self.subTest(name):
                host = self.make_host(f"attr{i}")
                store = host / ".work-items"
                self.store_files(store, own=False)
                plant(store)
                self.assert_refused(store, says="refusing to give it its "
                                    "own repo")
        # an adopted repo: <git-dir>/info/attributes, a promisor remote
        store = self.make_own(own=False)
        (store / ".git" / "info").mkdir()
        (store / ".git" / "info" / "attributes").write_text("* filter=x\n")
        self.assert_refused(store, says="selects git attributes")
        (store / ".git" / "info" / "attributes").unlink()
        self.git(store, "config", "remote.origin.promisor", "true")
        self.assert_refused(store, says="a lazy fetch from a promisor remote")

    def test_refuses_a_store_that_is_a_bare_git_dir(self):
        host = self.make_host()
        store = host / ".work-items"
        self.git(self.tmp, "init", "-q", "--bare", str(store))
        self.assert_refused(store, says="is a git directory, not a store")

    def test_refuses_when_git_cannot_say_whether_a_host_is_around(self):
        host = self.make_host()
        store = host / ".work-items"
        with mock.patch.object(wi, "_host_repo",
                               return_value=wi.HOST_UNKNOWN):
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 1, out + err)
        self.assertIn("git did not say whether a repo is around", err)
        self.assertFalse(store.exists())

    def test_track_on_an_own_store_is_refused(self):
        store = self.make_own()
        before = (store / "store.yaml").read_text()
        r = self.init(store, "--track", code=1)
        self.assertIn("is its own git repo; the host cannot track it (that "
                      "commits a gitlink, mode 160000): use `wi init "
                      "--no-track`", r.stderr)
        self.assertEqual((store / "store.yaml").read_text(), before)
        # a dedicated store, the top of its own repo with none around it,
        # keeps `--track` and its repo-root refusal for `--no-track`
        loose = self.make_own(host=False, own=False)
        self.init(loose, "--track")
        r = self.init(loose, "--no-track", code=1)
        self.assertIn("store is the repo root: no .gitignore written",
                      r.stderr)
        self.assertFalse(wi.read_repo_own(loose))

    # -- the edges ---------------------------------------------------------

    def test_new_old_location_store_needs_the_flag(self):
        # no store is made at an old location without the flag, so init
        # never makes one the next init refuses; with it, --no-track makes
        # today's plain ignored store, never a repo
        host = self.make_host(ignore=False)
        store = host / ".work"
        for flags in (("--no-track",), ("--track",), ()):
            r = self.init(store, *flags, code=1)
            self.assertIn(f"{store}: an old store location", r.stderr)
            self.assertIn("--allow-old-location", r.stderr)
            self.assertFalse(store.exists())
            self.assertFalse((host / ".gitignore").exists())
        r = self.init(store, "--no-track", "--allow-old-location")
        self.assertIn("is at an old location, so it gets no repo of its own",
                      r.stderr)
        self.assertEqual(wi.read_tracking(store), "ignored")
        self.assertFalse(os.path.lexists(store / ".git"))
        self.assertEqual((host / ".gitignore").read_text(), "/.work/\n")
        r = self.wi(["lint"], store)
        self.assertNotIn("no history", r.stdout + r.stderr)

    def test_git_not_on_path_makes_a_plain_ignored_store(self):
        empty = self.tmp / "nobin"
        empty.mkdir()
        store = self.tmp / "loose" / ".work-items"
        r = self.init(store, "--no-track", env={"PATH": str(empty)})
        self.assertIn(f"wi: WARNING git not found: {store} has no history "
                      "of its own; run `wi init --no-track` again where git "
                      "is available", r.stderr)
        self.assertEqual(wi.read_tracking(store), "ignored")
        self.assertFalse(os.path.lexists(store / ".git"))
        # without git there is no notice either
        r = self.wi(["lint"], store, env={"PATH": str(empty)})
        self.assertNotIn("no history", r.stdout + r.stderr)

    def test_init_takes_the_store_lock(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: ignored\n")
        with open(store / ".lock", "a") as fh, \
                mock.patch.object(wi.Lock.__init__, "__defaults__", (0.3,)):
            fcntl.flock(fh, fcntl.LOCK_EX)
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 4, out + err)
        self.assertIn("lock timeout", err)
        self.assertFalse(os.path.lexists(store / ".git"))
        self.assertEqual(wi.read_tracking(store), "ignored")

    def test_a_failed_first_commit_keeps_the_store_and_warns(self):
        store = self.make_host() / ".work-items"
        with mock.patch.object(wi, "_commit_own_paths",
                               side_effect=wi.CommitFailed("boom")):
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 0, out + err)
        self.assertIn("wi: WARNING store not committed: boom (the change is "
                      "saved; `wi commit` commits it)", err)
        self.assertTrue(wi.read_repo_own(store))
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("uncommitted path(s)", r.stderr)

    def test_a_failed_git_init_records_nothing(self):
        store = self.make_host() / ".work-items"
        real = wi._store_git

        def failing(root, *args, **kw):
            if args[:1] == ("init",):
                return subprocess.CompletedProcess(args, 128, "",
                                                   "fatal: no room\n")
            return real(root, *args, **kw)
        with mock.patch.object(wi, "_store_git", failing):
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 1, out + err)
        self.assertIn("own repo not set up: fatal: no room; tracking not "
                      "recorded", err)
        self.assertIn("own repo not set up; tracking not recorded", out)
        self.assertFalse((store / "store.yaml").exists())

    # -- what git may never do here -----------------------------------------

    def test_no_template_hook_is_installed_or_run(self):
        store = self.make_host(ignore=False) / ".work-items"
        tpl = self.tmp / "tpl"
        (tpl / "hooks").mkdir(parents=True)
        for name in ("pre-commit", "post-commit"):
            shutil.copy(self.marker(f"tpl-{name}"), tpl / "hooks" / name)
        self.git(self.tmp, "config", "--global", "init.templateDir",
                 str(tpl))
        control = self.tmp / "control"
        self.git(self.tmp, "init", "-q", str(control))
        self.assertTrue((control / ".git" / "hooks" / "pre-commit").exists())
        self.init(store, "--no-track", env={"GIT_TEMPLATE_DIR": str(tpl)})
        self.assertFalse((store / ".git" / "hooks").exists())
        self.assertEqual(self.marked(), [])
        self.assertEqual(self.subjects(store), ["wi init: store created"])

    def test_global_hooks_and_signing_do_not_run_at_init(self):
        host = self.make_host(ignore=False)
        store = host / ".work-items"
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        for name in ("pre-commit", "commit-msg", "post-commit"):
            shutil.copy(self.marker(f"global-{name}"), hooks / name)
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        self.git(self.tmp, "config", "--global", "commit.gpgSign", "true")
        self.git(self.tmp, "config", "--global", "gpg.program",
                 str(self.tmp / "no-such-gpg"))
        r = self.git(host, "commit", "-q", "--allow-empty", "-m", "control",
                     check=False)
        self.assertNotEqual(r.returncode, 0)                # control: gpg
        self.assertIn("global-pre-commit", self.marked())   # control: hook
        self.clear_marks()
        self.init(store, "--no-track")
        self.assertEqual(self.subjects(store), ["wi init: store created"])
        self.assertEqual(self.marked(), [])

    def test_callers_git_steering_never_redirects_init(self):
        # a host hook's env: GIT_DIR and friends name the host's repo, and
        # literal pathspecs would make the host's check-ignore fail
        host = self.make_host(ignore=False)
        (host / ".gitignore").write_text(".work-*/\n")
        self.git(host, "add", ".gitignore")
        self.git(host, "commit", "-q", "-m", "glob")
        head = self.git(host, "rev-parse", "HEAD").stdout
        index = (host / ".git" / "index").read_bytes()
        store = host / ".work-items"
        r = self.init(store, "--no-track", env={
            "GIT_DIR": str(host / ".git"), "GIT_WORK_TREE": str(host),
            "GIT_INDEX_FILE": str(host / ".git" / "index"),
            "GIT_COMMON_DIR": str(host / ".git"),
            "GIT_OBJECT_DIRECTORY": str(host / ".git" / "objects"),
            "GIT_LITERAL_PATHSPECS": "1"})
        self.assertIn("already ignored by git (.gitignore:1 '.work-*/')",
                      r.stdout)
        self.assertEqual((host / ".gitignore").read_text(), ".work-*/\n")
        self.assertEqual(self.git(host, "rev-parse", "HEAD").stdout, head)
        self.assertEqual((host / ".git" / "index").read_bytes(), index)
        self.assert_own_store(store, "wi init: store created", self.NEW_FILES)
        # the env is put back after init, in this process too
        with mock.patch.dict(os.environ, {"GIT_DIR": "/nowhere"}):
            store2 = self.make_host("host2", ignore=False) / ".work-items"
            code, out, err = self.run_init(store2, "--no-track")
            self.assertEqual(code, 0, out + err)
            self.assertEqual(os.environ["GIT_DIR"], "/nowhere")


class TestInitReview(InitCase):
    """d1e9 F3 review round 1: what may pass for the host's ignore line,
    where a store's git dir may sit, what a directory may hold before
    `git init`, includes in an adopted repo's config, and a store that
    changes while init waits for its lock."""

    def test_store_gitignore_rule_is_not_the_hosts_line(self):
        for i, rule in enumerate(("items/\n", "*\n")):
            with self.subTest(rule=rule):
                host = self.make_host(f"own-gi{i}", ignore=False)
                store = host / ".work-items"
                (store / "items").mkdir(parents=True)
                (store / ".gitignore").write_text(rule)
                r = self.init(store, "--no-track")
                self.assertIn("added /.work-items/", r.stdout)
                self.assertEqual((host / ".gitignore").read_text(),
                                 "/.work-items/\n")
                self.git(host, "add", "-A")
                self.assertNotIn(".work-items", self.git(
                    host, "ls-files", "-s").stdout)

    def test_lint_does_not_take_a_store_rule_for_the_hosts_line(self):
        store = self.make_own()
        host = self.tmp / "host"
        (host / ".gitignore").write_text("")
        (store / ".gitignore").write_text(".lock\n*.tmp*\nitems/\n")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn(f"the repo at {host} does not ignore store", r.stdout)

    def test_plain_store_ensure_ignored_finds_the_repo_from_the_store(self):
        # the default path (an old location, no git for a repo): the repo
        # is found from the store, and a store rule does not count either
        host = self.make_host(ignore=False)
        store = host / ".work"
        (store / "items").mkdir(parents=True)
        (store / ".gitignore").write_text("items/\n")
        ok, msg = wi.ensure_ignored(store)
        self.assertTrue(ok, msg)
        self.assertEqual(msg, f"added /.work/ to {host / '.gitignore'}")
        ok, msg = wi.ensure_ignored(store)
        self.assertIn("already ignored by git (.gitignore:1 '/.work/')", msg)

    def test_git_dir_among_the_stores_own_paths_is_broken(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store, own=False)
        self.git(self.tmp, "init", "-q", "--template=",
                 f"--separate-git-dir={store / 'items' / 'gd'}", str(store))
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(".git points into the store's own path items", rs.reason)
        self.assert_refused(store, says="points into the store's own path "
                            "items")

    def test_refuses_a_directory_holding_other_things(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / "notes.txt").write_text("not a store file\n")
        self.assert_refused(store, says="holds notes.txt, which is not a "
                            "store file: refusing to give it its own repo")
        # the lock and a write's tmp file are a store's own
        (store / "notes.txt").unlink()
        (store / ".lock").write_text("")
        (store / "store.yaml.tmpab12").write_text("")
        self.init(store, "--no-track")
        self.assertTrue(wi.read_repo_own(store))

    def test_refuses_an_adopted_repo_whose_config_includes_a_file(self):
        for key in ("include.path", "includeIf.gitdir:/elsewhere/.path"):
            with self.subTest(key=key):
                store = self.make_own(own=False)
                self.git(store, "config", key, str(self.tmp / "inc"))
                self.assert_refused(store, says="git config includes another "
                                    "file")
                shutil.rmtree(self.tmp / "host")

    def test_worktree_config_setting_hooks_refuses_adoption(self):
        # extensions.worktreeConfig: config.worktree is read after the local
        # config, so a hooksPath there, or an include there naming one, wins
        # over the /dev/null init writes, for a hand-run git
        hooks = self.tmp / "evil-hooks"
        hooks.mkdir()
        shutil.copy(self.marker("pre-commit"), hooks / "pre-commit")
        inc = self.tmp / "inc"
        inc.write_text(f"[core]\n\thooksPath = {hooks}\n")
        cases = {"hooksPath": ("core.hooksPath", str(hooks)),
                 "include": ("include.path", str(inc)),
                 "fsmonitor": ("core.fsmonitor", str(self.marker("fsmon")))}
        for name, (key, value) in cases.items():
            with self.subTest(name):
                store = self.make_own(own=False)
                self.git(store, "config", "extensions.worktreeConfig", "true")
                self.git(store, "config", "--worktree", key, value)
                code, out, err = self.run_init(store, "--no-track")
                self.assertEqual(code, 1, out + err)
                want = key if key != "include.path" else "core.hooksPath"
                self.assertIn(f"own repo not set up: {want} resolves to", err)
                self.assertFalse(wi.read_repo_own(store))
                shutil.rmtree(self.tmp / "host")
        self.assertEqual(self.marked(), [])

    def test_callers_command_scope_config_does_not_fail_the_read_back(self):
        # the caller's env sets core.hooksPath at command scope; the pinned
        # calls override it, and the read-back ignores it, so init succeeds
        hooks = self.tmp / "env-hooks"
        hooks.mkdir()
        shutil.copy(self.marker("pre-commit"), hooks / "pre-commit")
        envs = {"count": {"GIT_CONFIG_COUNT": "1",
                          "GIT_CONFIG_KEY_0": "core.hooksPath",
                          "GIT_CONFIG_VALUE_0": str(hooks)},
                "parameters": {"GIT_CONFIG_PARAMETERS":
                               f"'core.hookspath'='{hooks}'"}}
        for i, (name, env) in enumerate(envs.items()):
            with self.subTest(name):
                store = self.make_host(f"cmd{i}", ignore=False) / ".work-items"
                r = self.init(store, "--no-track", env=env)
                self.assertIn("committed ", r.stdout)
                self.assertTrue(wi.read_repo_own(store))
        self.assertEqual(self.marked(), [])

    def test_other_files_in_head_but_not_the_index_are_refused(self):
        store = self.make_own(own=False)
        (store / "src").mkdir()
        (store / "src" / "main.c").write_text("int main;\n")
        self.git(store, "add", "src/main.c")
        self.git(store, "commit", "-q", "-m", "code")
        self.git(store, "rm", "-q", "--cached", "src/main.c")
        self.assertNotIn("src/main.c",
                         self.git(store, "ls-files").stdout)
        self.assert_refused(store, says="holding other files (src/main.c)")

    def test_a_git_that_appears_while_init_waits_is_checked_again(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: ignored\n")
        wt = self.tmp / "wt"
        self.git(host, "worktree", "add", "-q", "--detach", str(wt))
        real_enter = wi.Lock.__enter__

        def enter(lock):
            # another process plants a .git into another repo meanwhile
            if not os.path.lexists(store / ".git"):
                shutil.copy(wt / ".git", store / ".git")
            return real_enter(lock)
        with mock.patch.object(wi.Lock, "__enter__", enter):
            code, out, err = self.run_init(store, "--no-track")
        self.assertEqual(code, 1, out + err)
        # refused by the check, before any `git init` runs in it
        self.assertIn("has a .git that is not a usable store repo: .git "
                      "points outside the store", err)
        self.assertNotIn("own repo not set up", err)
        self.assertEqual(wi.read_tracking(store), "ignored")
        self.assertFalse(wi.read_repo_own(store))

    def test_adopting_a_repo_with_no_items_says_adopted(self):
        store = self.make_own(own=False)
        for p in (store / "items").iterdir():
            p.unlink()
        self.git(store, "add", "-A")
        self.git(store, "commit", "-q", "-m", "empty")
        self.init(store, "--no-track")
        self.assertEqual(self.subjects(store)[0], "wi init: adopted 0 items")


class TestOldLocationRefusal(InitCase):
    """The operator's ruling on d1e9 F3: `wi init` makes or keeps no store
    at an old location (`.work/`, `.claude-sandbox/work/`), and makes none
    beside an old location holding items/ (beside its repo's top), unless
    --allow-old-location is passed."""

    FLAG = "--allow-old-location"

    def old_store(self, host, rel=".work", sidecar=False):
        store = host / rel
        if sidecar:
            (host / ".claude-sandbox").mkdir(exist_ok=True)
            self.git(host / ".claude-sandbox", "init", "-q")
        self.store_files(store, own=False)
        return store

    def test_root_at_an_old_location_is_refused(self):
        host = self.make_host()
        cases = ((".work", False), (".claude-sandbox/work", False),
                 (".claude-sandbox/work", True))
        for i, (rel, sidecar) in enumerate(cases):
            for flags in (("--track",), ("--no-track",), ()):
                with self.subTest(rel=rel, sidecar=sidecar, flags=flags):
                    base = host / f"c{i}"
                    base.mkdir(exist_ok=True)
                    store = (base / rel if base.joinpath(rel, "items")
                             .is_dir() else self.old_store(base, rel,
                                                           sidecar))
                    before = self.snapshot(base)
                    r = self.init(store, *flags, code=1)
                    self.assertEqual(self.snapshot(base), before)
                    if sidecar and flags == ("--no-track",):
                        # 3c06's refusal comes first, its message kept
                        self.assertIn("a git-ignored store there lands in no "
                                      "repo; nothing written", r.stderr)
                        continue
                    self.assertIn(f"{store}: an old store location "
                                  "(.claude-sandbox/work, .work); init makes "
                                  "no store at one, keeps none there, and "
                                  "makes none beside one holding items/: use "
                                  ".work-items/, moving the old store first "
                                  "if there is one (the work-items skill's "
                                  "references/format.md § Moving a store)",
                                  r.stderr)
                    self.assertIn("nothing written", r.stderr)
                    self.assertIn(self.FLAG, r.stderr)
                    self.assertNotIn("deprecated", r.stderr)
                    self.assertNotIn("note:", r.stderr)

    def test_an_old_store_beside_a_new_one_is_refused(self):
        host = self.make_host()
        old = self.old_store(host, ".claude-sandbox/work")
        store = host / ".work-items"
        r = self.init(store, "--no-track", code=1)
        self.assertIn(f"{old}: an old store location", r.stderr)
        self.assertFalse(store.exists())
        # with the override, the new store is made as ever
        self.init(store, "--no-track", self.FLAG)
        self.assertTrue(wi.read_repo_own(store))
        # beside the repo's top, for a store below it too
        deeper = host / "sub" / ".work-items"
        r = self.init(deeper, "--no-track", code=1)
        self.assertIn(f"{old}: an old store location", r.stderr)

    def test_the_export_sentence_only_when_wi_resolved_the_root(self):
        host = self.make_host()
        store = self.old_store(host)
        r = self.init(store, "--track", code=1)       # WORK_ITEMS_ROOT
        self.assertIn("change any WORK_ITEMS_ROOT export that names the old "
                      "path", r.stderr)
        r = subprocess.run([sys.executable, str(WI), "--root", str(store),
                            "init", "--track"], env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("WORK_ITEMS_ROOT", r.stderr)

    def test_a_store_counts_by_items_only(self):
        # claude-sandbox's A9: the store already moved away, the sidecar's
        # .gitignore still naming /work/, an empty .work/ left behind
        host = self.make_host()
        (host / ".claude-sandbox").mkdir()
        self.git(host / ".claude-sandbox", "init", "-q")
        (host / ".claude-sandbox" / ".gitignore").write_text("/work/\n")
        (host / ".claude-sandbox" / "work").mkdir()
        (host / ".work").mkdir()
        (host / ".work" / "notes").write_text("x\n")
        store = host / ".work-items"
        self.init(store, "--no-track")
        self.assertTrue(wi.read_repo_own(store))
        # and the override, with nothing old to override, is refused
        r = self.init(store, "--no-track", self.FLAG, code=1)
        self.assertIn(f"{self.FLAG} overrides only a root at an old location",
                      r.stderr)

    def test_the_override_at_an_old_location(self):
        host = self.make_host(ignore=False)
        store = self.old_store(host)
        (store / "store.yaml").unlink()
        r = self.init(store, "--no-track", self.FLAG)
        self.assertIn("deprecated: store", r.stderr)
        self.assertIn("gets no repo of its own", r.stderr)
        self.assertEqual(wi.read_tracking(store), "ignored")
        self.assertFalse(os.path.lexists(store / ".git"))
        # never recorded: the next init needs it again
        self.assertNotIn("allow", (store / "store.yaml").read_text())
        self.init(store, "--track", code=1)
        self.init(store, "--track", self.FLAG)
        self.assertEqual(wi.read_tracking(store), "tracked")
        self.init(store, self.FLAG)                   # the existing-store path
        r = self.wi(["prime"], store)
        self.assertIn("deprecated: store", r.stdout)
        r = self.wi(["lint"], store)
        self.assertIn("deprecated: store", r.stderr)


class TestGitPins(StoreRepoCase):
    """Pins of the git behaviour d1e9 rests on; a git change shows here."""

    def test_check_ignore_exits_1_inside_store_repo(self):
        store = self.make_own()
        r = self.git(store, "check-ignore", "-q", str(store), check=False)
        self.assertEqual(r.returncode, 1)
        r = self.git(self.tmp / "host", "check-ignore", "-q", ".work-items",
                     check=False)
        self.assertEqual(r.returncode, 0)

    def test_check_ignore_refuses_literal_pathspecs(self):
        store = self.make_own()
        r = self.git(store, "check-ignore", "-q", "items", check=False,
                     env={"GIT_LITERAL_PATHSPECS": "1"})
        self.assertEqual(r.returncode, 128)

    def test_empty_git_falls_through_without_a_ceiling(self):
        host = self.make_host()
        store = host / ".work-items"
        (store / ".git").mkdir(parents=True)
        r = self.git(store, "rev-parse", "--show-toplevel", check=False)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), str(host))
        r = self.git(store, "rev-parse", "--show-toplevel", check=False,
                     env={"GIT_CEILING_DIRECTORIES": str(host)})
        self.assertEqual(r.returncode, 128)

    def test_empty_hooks_path_runs_no_hook(self):
        store = self.make_own()
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        shutil.copy(self.marker("pre-commit"), hooks / "pre-commit")
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        shutil.copy(self.marker("root-pre-commit"), store / "pre-commit")
        self.git(store, "add", "pre-commit")
        self.git(store, "-c", "core.hooksPath=", "commit", "-q", "-m", "x")
        self.assertEqual(self.marked(), [])

    def test_commit_with_nothing_staged_exits_1(self):
        store = self.make_own()
        r = self.git(store, "commit", "-q", "-m", "x", check=False)
        self.assertEqual(r.returncode, 1)

    def test_pathspec_matching_nothing_fails(self):
        # why only existing paths go into a pathspec: add exits 128, commit 1
        store = self.make_own()
        r = self.git(store, "add", "-A", "--", "archive", check=False)
        self.assertEqual(r.returncode, 128)
        r = self.git(store, "commit", "-q", "-m", "x", "--", "archive",
                     check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("did not match", r.stderr)


if __name__ == "__main__":
    unittest.main()
