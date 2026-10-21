"""Tests for the wi launcher (scripts/wi) and `wi install-launcher` (8805 F1).

Every case runs sealed: HOME, CLAUDE_CONFIG_DIR and CLAUDE_CODE_PLUGIN_CACHE_DIR
are fresh temp dirs, PATH is /usr/bin:/bin plus what the case adds, and
GIT_CEILING_DIRECTORIES stops git at the temp dir. No case reads or writes the
real home, its ~/.local/bin, or the real plugin install. The cases that touch
HOME's own handling run in-process with Path.home and expanduser patched to
raise, so a fallback to the passwd home fails instead of writing there.
"""
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
LAUNCHER = SCRIPTS / "wi"
WI = SCRIPTS / "wi.py"
PLUGIN = HERE.parent.parent.parent      # plugins/work-items
MARKER = "# wi launcher (work-items plugin)."
KEY = "work-items@kmacmcfarlane"
BASE_PATH = "/usr/bin:/bin"

spec = importlib.util.spec_from_file_location("wi_launcher_under_test", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)


def snapshot(top, skip=()):
    """Every path under top: kind, bytes or link text, and a file's
    mtime_ns. Directories are listed by presence only (adding a file moves
    a directory's mtime). Paths in skip are left out."""
    snap = {}
    top = Path(top)
    if not top.exists():
        return snap
    for dirpath, dirnames, filenames in os.walk(top):
        for name in dirnames + filenames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(top))
            if rel in skip:
                continue
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode):
                snap[rel] = ("link", os.readlink(p))
            elif stat.S_ISDIR(st.st_mode):
                snap[rel] = ("dir",)
            else:
                snap[rel] = ("file", p.read_bytes(), st.st_mtime_ns)
    return snap


def temp_files(top):
    """Any install temp file (.wi-*) left anywhere under top."""
    return [p for p in Path(top).rglob(".wi-*")]


class Sealed(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wi-launcher-"))
        self.addCleanup(self._cleanup)
        self.home = self.tmp / "home"
        self.cfg = self.tmp / "cfg"
        self.cache = self.tmp / "cache"
        for d in (self.home, self.cfg / "plugins", self.cache):
            d.mkdir(parents=True)
        self.work = self.tmp / "work"
        self.work.mkdir()

    def _cleanup(self):
        # a case may leave a read-only directory behind
        for dirpath, dirnames, _ in os.walk(self.tmp):
            for name in dirnames:
                p = os.path.join(dirpath, name)
                if not os.path.islink(p):
                    with contextlib.suppress(OSError):
                        os.chmod(p, 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("WI_", "WORK_ITEMS_", "GIT_",
                                    "CLAUDE_", "PYTHON"))}
        env.update(HOME=str(self.home), CLAUDE_CONFIG_DIR=str(self.cfg),
                   CLAUDE_CODE_PLUGIN_CACHE_DIR=str(self.cache),
                   PATH=BASE_PATH, GIT_CEILING_DIRECTORIES=str(self.tmp))
        env.update(extra)
        return env


class TestLauncher(Sealed):
    """The launcher runs only the wi.py the install record names."""

    def stub(self, where, label):
        """A fake install at where whose wi.py prints label and its argv."""
        py = Path(where) / "skills/work-items/scripts/wi.py"
        py.parent.mkdir(parents=True, exist_ok=True)
        body = ("import json, sys\n"
                f"print({label!r}, json.dumps(sys.argv[1:]))\n"
                "sys.exit(3 if '--exit3' in sys.argv else 0)\n")
        py.write_text(body)
        return Path(where)

    def trap(self, path):
        """A file at path that, run or imported, touches path + '.ran'."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        flag = str(path) + ".ran"
        path.write_text(f"open({flag!r}, 'w').close()\n")
        return Path(flag)

    def record(self, plugins_root, entries):
        Path(plugins_root).mkdir(parents=True, exist_ok=True)
        (Path(plugins_root) / "installed_plugins.json").write_text(
            json.dumps({"version": 2, "plugins": {KEY: entries}}))

    def copy(self):
        """A copy of the launcher in its own temp dir, as a person's is."""
        d = self.tmp / "copybin"
        d.mkdir(exist_ok=True)
        dst = d / "wi"
        shutil.copy2(LAUNCHER, dst)
        return dst

    def launch(self, launcher, args=(), cwd=None, **env):
        return subprocess.run([str(launcher)] + list(args),
                              env=self.env(**env), cwd=str(cwd or self.work),
                              capture_output=True, text=True, timeout=30)

    def test_file_shape(self):
        self.assertTrue(os.access(LAUNCHER, os.X_OK))
        lines = LAUNCHER.read_text().split("\n")
        self.assertEqual(lines[0], "#!/bin/sh")
        self.assertTrue(lines[1].startswith(MARKER))

    def test_user_record_runs_stub_args_whole_exit_passes(self):
        inst = self.stub(self.tmp / "inst", "USER")
        self.record(self.cache, [{"scope": "user", "installPath": str(inst)}])
        r = self.launch(self.copy(), ["a b", "--exit3"])
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertEqual(r.stdout.strip(), 'USER ["a b", "--exit3"]')

    def test_project_entry_holding_cwd_beats_user(self):
        user = self.stub(self.tmp / "u", "USER")
        proj = self.stub(self.tmp / "p", "PROJECT")
        self.record(self.cache, [
            {"scope": "user", "installPath": str(user)},
            {"scope": "project", "installPath": str(proj),
             "projectPath": str(self.work)}])
        r = self.launch(self.copy())
        self.assertEqual(r.stdout.split()[0], "PROJECT", r.stderr)
        # a project entry for another directory never answers
        other = self.tmp / "other"
        other.mkdir()
        r = self.launch(self.copy(), cwd=other)
        self.assertEqual(r.stdout.split()[0], "USER", r.stderr)

    def test_cache_dir_variable_beats_config_dir(self):
        a = self.stub(self.tmp / "a", "CONFIG")
        b = self.stub(self.tmp / "b", "CACHE")
        self.record(self.cfg / "plugins",
                    [{"scope": "user", "installPath": str(a)}])
        self.record(self.cache, [{"scope": "user", "installPath": str(b)}])
        r = self.launch(self.copy())
        self.assertEqual(r.stdout.split()[0], "CACHE", r.stderr)
        env = self.env()
        del env["CLAUDE_CODE_PLUGIN_CACHE_DIR"]
        r = subprocess.run([str(self.copy())], env=env, cwd=str(self.work),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.stdout.split()[0], "CONFIG", r.stderr)

    def test_no_record_exits_127_and_runs_nothing(self):
        flag = self.trap(self.tmp / "inst/skills/work-items/scripts/wi.py")
        r = self.launch(self.copy())
        self.assertEqual(r.returncode, 127)
        self.assertIn("wi: no work-items install found under", r.stderr)
        self.assertFalse(flag.exists())

    def test_relative_install_path_never_resolves_against_cwd(self):
        flag = self.trap(self.work / "rel/skills/work-items/scripts/wi.py")
        self.record(self.cache, [{"scope": "user", "installPath": "rel"}])
        r = self.launch(self.copy())
        self.assertEqual(r.returncode, 127, r.stdout + r.stderr)
        self.assertIn("no work-items install found", r.stderr)
        self.assertFalse(flag.exists(), "a relative installPath ran")

    def test_json_py_in_cwd_or_beside_copy_never_imported(self):
        inst = self.stub(self.tmp / "inst", "USER")
        self.record(self.cache, [{"scope": "user", "installPath": str(inst)}])
        launcher = self.copy()
        in_cwd = self.trap(self.work / "json.py")
        beside = self.trap(launcher.parent / "json.py")
        r = self.launch(launcher)
        self.assertEqual(r.stdout.split()[0], "USER", r.stderr)
        self.assertFalse(in_cwd.exists())
        self.assertFalse(beside.exists())

    def test_no_sibling_step(self):
        inst = self.stub(self.tmp / "inst", "USER")
        self.record(self.cache, [{"scope": "user", "installPath": str(inst)}])
        launcher = self.copy()
        flag = self.trap(launcher.parent / "wi.py")
        r = self.launch(launcher)
        self.assertEqual(r.stdout.split()[0], "USER", r.stderr)
        self.assertFalse(flag.exists(), "the wi.py beside the copy ran")
        # in place in the plugin tree, the real wi.py beside it is not run
        r = self.launch(LAUNCHER, ["--help"])
        self.assertEqual(r.stdout.split()[0], "USER", r.stderr)

    def test_cwd_repo_copy_never_runs(self):
        inst = self.stub(self.tmp / "inst", "USER")
        self.record(self.cache, [{"scope": "user", "installPath": str(inst)}])
        repo = self.work / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True,
                       env=self.env(), capture_output=True)
        flag = self.trap(repo / "plugins/x/skills/work-items/scripts/wi.py")
        r = self.launch(self.copy(), cwd=repo)
        self.assertEqual(r.stdout.split()[0], "USER", r.stderr)
        self.assertFalse(flag.exists(), "the cwd repo's wi.py ran")


class InstallCase(Sealed):
    def setUp(self):
        super().setUp()
        self.bin = self.home / ".local" / "bin"
        self.T = self.bin / "wi"
        self.src = LAUNCHER.read_bytes()

    def install(self, path=BASE_PATH, wi_py=WI, **env):
        return subprocess.run(
            [sys.executable, str(wi_py), "install-launcher"],
            env=self.env(PATH=path, **env), cwd=str(self.work),
            capture_output=True, text=True, timeout=30)

    def assertOnlyTargetChanged(self, before):
        skip = {".local", ".local/bin", ".local/bin/wi"}
        self.assertEqual(snapshot(self.home, skip), before)
        self.assertEqual(temp_files(self.home), [])

    def removal(self):
        return f"remove it with: rm {self.home}/.local/bin/wi"


class TestInstallLauncher(InstallCase):
    def test_refuses_foreign_file(self):
        self.bin.mkdir(parents=True)
        self.T.write_text("#!/bin/sh\necho mine\n")
        before = snapshot(self.home)
        r = self.install()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("refused", r.stderr)
        self.assertNotIn("rm ", r.stdout + r.stderr)
        self.assertEqual(snapshot(self.home), before)
        self.assertEqual(temp_files(self.home), [])

    def test_refuses_symlink_target_even_to_a_marked_file(self):
        self.bin.mkdir(parents=True)
        real = self.tmp / "marked"
        real.write_bytes(b"#!/bin/sh\n" + MARKER.encode() + b" old\n")
        self.T.symlink_to(real)
        before, real_before = snapshot(self.home), real.read_bytes()
        r = self.install()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertTrue(self.T.is_symlink())
        self.assertEqual(snapshot(self.home), before)
        self.assertEqual(real.read_bytes(), real_before)

    def test_idempotent(self):
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        st1 = os.stat(self.T)
        second = self.install()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed", second.stdout)
        st2 = os.stat(self.T)
        self.assertEqual((st1.st_ino, st1.st_mtime_ns),
                         (st2.st_ino, st2.st_mtime_ns))
        self.assertEqual(self.T.read_bytes(), self.src)

    def test_never_touches_rc_files(self):
        rcs = [".bashrc", ".bash_profile", ".profile", ".zshrc", ".zprofile",
               ".config/fish/config.fish"]
        for rc in rcs:
            p = self.home / rc
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# {rc}\n")
        before = snapshot(self.home)
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("is not on your PATH", r.stdout)
        self.assertOnlyTargetChanged(before)

    def test_prints_removal_absent_identical_earlier(self):
        r = self.install()                                   # absent
        self.assertIn(self.removal(), r.stdout.splitlines())
        r = self.install()                                   # identical
        self.assertIn(self.removal(), r.stdout.splitlines())
        self.T.write_bytes(b"#!/bin/sh\n" + MARKER.encode() + b" old\n")
        r = self.install()                                   # earlier
        self.assertIn(self.removal(), r.stdout.splitlines())

    def test_earlier_launcher_replaced(self):
        self.bin.mkdir(parents=True)
        self.T.write_bytes(b"#!/bin/sh\n" + MARKER.encode() + b" old\nexit 9\n")
        os.chmod(self.T, 0o644)
        before = snapshot(self.home, {".local/bin/wi"})
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"updated: {self.T}", r.stdout)
        self.assertEqual(self.T.read_bytes(), self.src)
        self.assertEqual(stat.S_IMODE(os.stat(self.T).st_mode), 0o755)
        self.assertOnlyTargetChanged(
            {k: v for k, v in before.items()
             if k not in (".local", ".local/bin")})

    def test_absent_bin_created(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"installed: {self.T}", r.stdout)
        self.assertTrue(self.bin.is_dir() and not self.bin.is_symlink())
        self.assertEqual(self.T.read_bytes(), self.src)
        self.assertEqual(stat.S_IMODE(os.stat(self.T).st_mode), 0o755)
        self.assertEqual(temp_files(self.home), [])

    def test_identical_but_not_executable_made_executable(self):
        self.bin.mkdir(parents=True)
        self.T.write_bytes(self.src)
        os.chmod(self.T, 0o644)
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("made executable", r.stdout)
        self.assertEqual(stat.S_IMODE(os.stat(self.T).st_mode), 0o755)

    def test_on_path_no_note(self):
        r = self.install(path=f"{self.bin}:{BASE_PATH}")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("not on your PATH", r.stdout)

    def test_other_wi_on_path_named(self):
        other = self.tmp / "otherbin"
        other.mkdir()
        (other / "wi").write_text("#!/bin/sh\n")
        os.chmod(other / "wi", 0o755)
        r = self.install(path=f"{self.bin}:{other}:{BASE_PATH}")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"note: another wi is on your PATH at {other}/wi",
                      r.stdout)
        self.assertNotIn(f"another wi is on your PATH at {self.T}", r.stdout)

    def test_missing_source_launcher_exits_3(self):
        alone = self.tmp / "alone"
        alone.mkdir()
        shutil.copy2(WI, alone / "wi.py")
        r = self.install(wi_py=alone / "wi.py")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("launcher not found beside wi.py", r.stderr)
        (alone / "wi").write_text("#!/bin/sh\n# not the launcher\n")
        r = self.install(wi_py=alone / "wi.py")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertFalse(self.T.exists())


class TestInstallDirectories(InstallCase):
    def test_bin_symlink_to_owned_dir(self):
        real = self.tmp / "elsewhere" / "bin"
        real.mkdir(parents=True)
        os.chmod(real, 0o755)
        (self.home / ".local").mkdir()
        self.bin.symlink_to(real)
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((real / "wi").read_bytes(), self.src)
        self.assertIn(f"installed: {self.T} (in {os.path.realpath(real)})",
                      r.stdout)

    def test_bin_symlink_to_group_writable_dir_refused(self):
        real = self.tmp / "open"
        real.mkdir()
        os.chmod(real, 0o777)
        (self.home / ".local").mkdir()
        self.bin.symlink_to(real)
        r = self.install()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("refused", r.stderr)
        self.assertEqual(list(real.iterdir()), [])

    def test_bin_dangling_symlink_refused(self):
        gone = self.tmp / "gone" / "bin"
        (self.home / ".local").mkdir()
        self.bin.symlink_to(gone)
        r = self.install()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("refused", r.stderr)
        self.assertEqual(os.readlink(self.bin), str(gone))
        self.assertFalse((self.tmp / "gone").exists())

    def test_local_symlink_to_owned_dir_gets_bin(self):
        real = self.tmp / "realocal"
        real.mkdir()
        os.chmod(real, 0o755)
        (self.home / ".local").symlink_to(real)
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((real / "bin").is_dir())
        self.assertEqual((real / "bin" / "wi").read_bytes(), self.src)

    def test_local_regular_file_exits_3(self):
        (self.home / ".local").write_text("not a dir\n")
        r = self.install()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("cannot write", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(temp_files(self.home), [])

    @unittest.skipIf(os.getuid() == 0, "root writes a 555 directory")
    def test_read_only_bin_exits_3(self):
        self.bin.mkdir(parents=True)
        os.chmod(self.bin, 0o555)
        r = self.install()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("cannot write", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        os.chmod(self.bin, 0o755)
        self.assertEqual(temp_files(self.home), [])
        self.assertFalse(self.T.exists())


class InProcess(Sealed):
    """wi.main(["install-launcher"]) in this process, with Path.home and
    expanduser patched to raise and the cwd in a temp dir."""

    def setUp(self):
        super().setUp()
        old = os.getcwd()
        os.chdir(self.work)
        self.addCleanup(os.chdir, old)
        for target in (mock.patch.object(pathlib.Path, "home",
                                          side_effect=AssertionError("home")),
                       mock.patch.object(os.path, "expanduser",
                                         side_effect=AssertionError("expand"))):
            target.start()
            self.addCleanup(target.stop)

    def main(self, env):
        err, out = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                rc = wi.main(["install-launcher"])
        return rc, out.getvalue(), err.getvalue()


class TestInstallHome(InProcess):
    def refused(self, home):
        before_cwd, before_home = snapshot(self.work), snapshot(self.home)
        env = {"PATH": BASE_PATH}
        with mock.patch.dict(os.environ, {}, clear=False):
            if home is None:
                os.environ.pop("HOME", None)
            else:
                env["HOME"] = home
            rc, out, err = self.main(env)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("refused: HOME must be an absolute directory", err)
        self.assertEqual(snapshot(self.work), before_cwd)
        self.assertEqual(snapshot(self.home), before_home)

    def test_home_unset(self):
        self.refused(None)

    def test_home_empty(self):
        self.refused("")

    def test_home_relative(self):
        self.refused("rel")
        self.assertFalse((self.work / "rel").exists())
        # a relative HOME that names a directory under the cwd is refused too
        (self.work / "rel").mkdir()
        self.refused("rel")
        self.assertFalse((self.work / "rel" / ".local").exists())

    def test_home_root(self):
        self.refused("/")
        self.refused("//")

    def test_home_not_a_directory(self):
        f = self.tmp / "file"
        f.write_text("x")
        self.refused(str(f))


class TestInstallRaces(InProcess):
    def setUp(self):
        super().setUp()
        self.T = self.home / ".local" / "bin" / "wi"
        self.foreign = b"#!/bin/sh\necho someone else's\n"
        self.env = {"HOME": str(self.home), "PATH": BASE_PATH}

    def test_create_race_refused(self):
        real_link = os.link

        def racing_link(src, dst, *a, **kw):
            Path(dst).write_bytes(self.foreign)
            return real_link(src, dst, *a, **kw)

        with mock.patch.object(os, "link", racing_link):
            rc, out, err = self.main(self.env)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("refused", err)
        self.assertEqual(self.T.read_bytes(), self.foreign)
        self.assertEqual(temp_files(self.home), [])

    def test_upgrade_race_refused(self):
        self.T.parent.mkdir(parents=True)
        self.T.write_bytes(b"#!/bin/sh\n" + MARKER.encode() + b" old\n")
        real_mkstemp = tempfile.mkstemp

        def racing_mkstemp(*a, **kw):
            res = real_mkstemp(*a, **kw)
            side = self.T.parent / "side"
            side.write_bytes(self.foreign)
            os.rename(side, self.T)
            return res

        with mock.patch.object(tempfile, "mkstemp", racing_mkstemp):
            rc, out, err = self.main(self.env)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("refused", err)
        self.assertEqual(self.T.read_bytes(), self.foreign)
        self.assertEqual(temp_files(self.home), [])


class TestNeverFromAHook(unittest.TestCase):
    def test_no_hooks(self):
        self.assertFalse((PLUGIN / "hooks").exists())
        self.assertEqual(list(PLUGIN.rglob("hooks.json")), [])
        manifest = json.loads(
            (PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        self.assertNotIn("hooks", manifest)


if __name__ == "__main__":
    unittest.main()
