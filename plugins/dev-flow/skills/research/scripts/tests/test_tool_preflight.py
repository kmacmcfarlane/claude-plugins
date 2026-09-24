"""Tests for tool-preflight.sh (the research skill's Step 5.1 tool check).

A port of agent-research's research-tooling harness (series 02 § Test matrix: 29
assertions plus a negative control), made hermetic: every case runs against a
fixture "host" tree in a temp dir, a fake mountinfo, stub docker, uname, sha256sum
and timeout binaries, and a PATH holding only the utilities the script needs, so
no case depends on this machine's layout, its kernel, its Docker or coreutils, or
whether poppler is installed. The three
cases the source ran against its live container (D1, R1, R2) use fixtures here.

Each case runs under dash and bash when both exist (else under sh), and the two
shells' full outputs must match. Extra cases cover the round-3 review lows the
port fixed: a removed matched Dockerfile, nearer= only for a nearer chain
position, and the physical $PWD fallback.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "tool-preflight.sh"

SHELLS = [s for s in ("dash", "bash") if shutil.which(s)] or ["sh"]
UTILS = ("dirname", "basename", "git", "grep", "sed", "tr", "cut", "head", "cat")
# Stubbed rather than linked, so no case depends on the host's coreutils or kernel:
# uname prints Linux (the macOS case puts its own uname first on PATH), sha256sum
# is Python's hashlib, and timeout just runs its command.
SHA256SUM = """import hashlib, sys
print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest() + "  -")
"""

F = {}  # fixture paths, filled by setUpModule


def tag(ctx):
    """The launcher's child tag, implemented independently of the script."""
    df = ctx + "/.claude-sandbox/Dockerfile"
    s = re.sub(r"[^a-z0-9._-]", "-", os.path.basename(ctx).lower())
    h = hashlib.sha256((df + "\0" + ctx).encode()).hexdigest()[:6]
    return "claude-sandbox-df-%s-%s" % (s, h)


def _exe(path, body):
    path.write_text("#!/bin/sh\n" + body + "\n")
    path.chmod(0o755)


def setUpModule():
    tmp = tempfile.TemporaryDirectory()
    F["_tmp"] = tmp
    w = Path(os.path.realpath(tmp.name))
    F["W"] = str(w)

    bin_ = w / "bin"
    bin_.mkdir()
    for u in UTILS:
        p = shutil.which(u)
        if p:
            (bin_ / u).symlink_to(p)
    _exe(bin_ / "uname", "echo Linux")
    _exe(bin_ / "timeout", 'shift; exec "$@"')
    (bin_ / "sha256sum").write_text("#!%s\n%s" % (sys.executable, SHA256SUM))
    (bin_ / "sha256sum").chmod(0o755)
    F["BIN"] = str(bin_)

    b = w / "fs"                                  # stands in for the host filesystem
    t = b / "home/rt/work"                        # tree level with a Dockerfile
    p1, p2 = t / "proj1", t / "proj2"             # P1 has its own Dockerfile, P2 has none
    c = b / "home/rt/cfg"                         # tree for config-override cases
    e = b / "home/rt/empty/proj"                  # a project with no Dockerfile anywhere
    sp = t / "with space/proj"                    # a project path with whitespace
    for d in (t / ".claude-sandbox", p1 / ".claude-sandbox", p2, c / ".claude-sandbox",
              c / "p3/.claude-sandbox", c / "p4", c / "p5/.claude-sandbox",
              c / "p6/.claude-sandbox", e, sp):
        d.mkdir(parents=True)
    for d in (t, p1, c):
        (d / ".claude-sandbox/Dockerfile").write_text("FROM claude-sandbox\n")
    (c / ".claude-sandbox/config.yaml").write_text("baseOnly: true\n")
    (c / "p3/.claude-sandbox/config.yaml").write_text("baseOnly: false\n")
    (c / "p5/.claude-sandbox/config.yaml").write_text(
        "baseOnly: false\ndockerfileDir: /opt/elsewhere  # override\n")
    (c / "p6/.claude-sandbox/config.yaml").write_text('baseOnly: false\ndockerfile: ""\n')
    (w / "link1").symlink_to(p1)                  # a logical path to P1
    F.update(T=str(t), P1=str(p1), P2=str(p2), C=str(c), E=str(e), LINK1=str(w / "link1"),
             SPACE=str(sp))

    # linked worktree: main checkout with a Dockerfile, worktree as a sibling
    lw = w / "lw"
    (lw / "main/.claude-sandbox").mkdir(parents=True)
    (lw / "main/.claude-sandbox/Dockerfile").write_text("FROM claude-sandbox\n")
    genv = dict(os.environ, GIT_CEILING_DIRECTORIES=str(w))
    for cmd in (["git", "init", "-q"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                 "--allow-empty", "-m", "i"],
                ["git", "worktree", "add", "-q", str(lw / "wt")]):
        subprocess.run(cmd, cwd=lw / "main", env=genv, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    F.update(MAIN=str(lw / "main"), WT=str(lw / "wt"))

    stubs = w / "stub"

    def stub(name, body):
        d = stubs / name
        d.mkdir(parents=True)
        _exe(d / "docker", body)
        return str(d)

    F["NODOCKER"] = stub("nodocker", "exit 1")
    F["DBASE"] = stub("base", "echo claude-sandbox:run")
    F["DOTHER"] = stub("other", "echo claude-sandbox-df-elsewhere-abc123:run")
    F["DTREE"] = stub("tree", "echo %s:run" % tag(str(t)))
    F["DMAIN"] = stub("main", "echo %s:run" % tag(str(lw / "main")))
    F["DP2"] = stub("p2", "echo %s:run" % tag(str(p2)))
    F["DE"] = stub("e", "echo %s:run" % tag(str(e)))
    F["DP1"] = stub("p1", "echo %s:run" % tag(str(p1)))
    (stubs / "all").mkdir()
    for tool in ("pdftotext", "pdfinfo", "pdftoppm"):
        _exe(stubs / "all" / tool, "")
    F["ALL"] = str(stubs / "all")
    (stubs / "darwin").mkdir()
    _exe(stubs / "darwin/uname", "echo Darwin")
    F["DARWIN"] = str(stubs / "darwin")
    F["EMPTY"] = str(stubs / "empty")             # a PATH entry with no docker at all
    os.mkdir(F["EMPTY"])

    # fake mountinfo: "id parent dev root mountpoint opts - fstype source superopts"
    def mi(name, *pairs):
        f = w / ("mi-" + name)
        lines = ["1 0 0:1 / / rw - overlay overlay rw"]
        for root, mp in zip(pairs[::2], pairs[1::2]):
            lines.append("40 1 0:40 %s %s rw,relatime - btrfs /dev/x rw" % (root, mp))
        f.write_text("\n".join(lines) + "\n")
        return str(f)

    F["MI_SAMEFS"] = mi("samefs", str(p1), str(p1))            # project on the root fs
    F["MI_SEPHOME"] = mi("sephome", "/rt/work/proj1", str(p1))  # separate /home fs
    F["MI_ATHOME"] = mi("athome", "/@home/rt/work/proj1", str(p1))  # btrfs @home
    F["MI_DIFFPATH"] = mi("diffpath", "/srv/x/home/rt/work", str(t),
                          "/rt/work/proj2", str(p2))           # host /srv/x/... on the tree path
    F["MI_PARENT"] = mi("parent", "/home/rt/work", str(t),
                        "/home/rt/work/proj2", str(p2))        # parent-dir mount covers the tree
    F["MI_PROJONLY"] = mi("projonly", "/rt/work/proj2", str(p2))  # only the project mounted
    F["MI_CFG"] = mi("cfg", str(c), str(c))                    # config tree at its path
    F["MI_LW"] = mi("lw", str(lw), str(lw))                    # the worktree fixture mounted
    F["MI_E"] = mi("e", "/rt/empty/proj", str(e))              # the empty project only

    for fam, text in (("debian", "ID=debian"), ("ubuntu", "ID=ubuntu\nID_LIKE=debian"),
                      ("fedora", "ID=fedora"), ("arch", "ID=arch"), ("other", "ID=plan9")):
        (w / ("os-" + fam)).write_text(text + "\n")
        F["OS_" + fam.upper()] = str(w / ("os-" + fam))


def tearDownModule():
    F["_tmp"].cleanup()


def run(shell, path=(), sandbox=True, script=SCRIPT, cwd=None, **env):
    """Run the preflight; `path` dirs go before the utilities bin."""
    e = {
        "PATH": ":".join(list(path) + [F["BIN"]]),
        "HOME": F["W"],
        "LC_ALL": "C",
        "GIT_CEILING_DIRECTORIES": F["W"],
        "RESEARCH_PREFLIGHT_SANDBOX_MARKER": "/nonexistent",
    }
    if sandbox:
        e["CLAUDE_SANDBOX_VERSION"] = "test"
    e.update(env)
    r = subprocess.run([shutil.which(shell), str(script)], env=e, cwd=cwd or F["W"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       timeout=60)
    return r.returncode, r.stdout


def cases():
    """(label, expected line or ~substring, run kwargs). 29 assertions, as in 02."""
    T, P1, P2, C, L = F["T"], F["P1"], F["P2"], F["C"], F["MAIN"]
    DF = "/.claude-sandbox/Dockerfile"
    nd = [F["NODOCKER"]]
    out = [
        # --- no Docker: fake mountinfo ---------------------------------------------
        ("M1 same-fs /home, project Dockerfile", "CHILD nearest-visible " + P1 + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P1, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_SAMEFS"])),
        ("M2 separate /home fs (root /rt/...)", "CHILD nearest-visible " + P1 + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P1, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_SEPHOME"])),
        ("M3 btrfs @home (root /@home/...)", "CHILD nearest-visible " + P1 + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P1, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_ATHOME"])),
        ("M4 different-path mount on tree (known false positive)", "CHILD nearest-visible " + T + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P2, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_DIFFPATH"])),
        ("M5 parent-dir mount covers tree", "CHILD nearest-visible " + T + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P2, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
        ("M6 only the project mounted", "CHILD unseen " + T,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P2, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        ("M6 FIX cites the cascade report",
         "~last level marked 'Dockerfile (nearest wins)' under 'Sandbox config cascade'",
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P2, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        ("M7 local baseOnly:false beats upstream true", "CHILD nearest-visible " + C + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=C + "/p3", RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_CFG"])),
        ("M8 upstream baseOnly:true", "CHILD override baseOnly " + C + "/.claude-sandbox/config.yaml",
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=C + "/p4", RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_CFG"])),
        ("M9 dockerfileDir override",
         "CHILD override dockerfileDir " + C + "/p5/.claude-sandbox/config.yaml",
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=C + "/p5", RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_CFG"])),
        ('M10 dockerfile: "" is no override', "CHILD nearest-visible " + C + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=C + "/p6", RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_CFG"])),
        # --- Docker path: tag matched against every chain level --------------------
        ("D1 tree mounted, hash-confirmed (source: live container)", "CHILD confirmed " + T + DF,
         dict(path=[F["DTREE"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
        ("D2 tree unseen but hash-confirmed", "CHILD confirmed " + T + DF,
         dict(path=[F["DTREE"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        ("D3 project Dockerfile added after launch",
         "CHILD confirmed " + T + DF + " nearer=" + P1 + DF,
         dict(path=[F["DTREE"]], CLAUDE_SANDBOX_PROJECT_DIR=P1,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_SEPHOME"])),
        ("D3 FIX names the nearer file", "~the next launch builds from " + P1 + DF,
         dict(path=[F["DTREE"]], CLAUDE_SANDBOX_PROJECT_DIR=P1,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_SEPHOME"])),
        ("D4 base image", "CHILD base-image -",
         dict(path=[F["DBASE"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        ("D5 child tag no level accounts for",
         "CHILD built-from-unseen claude-sandbox-df-elsewhere-abc123",
         dict(path=[F["DOTHER"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        ("D5 FIX cites cascade report and rebuild line",
         "~'Building ... child image from ...' on a rebuild",
         dict(path=[F["DOTHER"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PROJONLY"])),
        # --- linked worktree ----------------------------------------------------------
        ("L1 linked worktree, no Docker", "CHILD nearest-visible " + L + DF,
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=F["WT"], RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_LW"])),
        ("L2 linked worktree, hash-confirmed", "CHILD confirmed " + L + DF,
         dict(path=[F["DMAIN"]], CLAUDE_SANDBOX_PROJECT_DIR=F["WT"],
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_LW"])),
        # --- tools --------------------------------------------------------------------
        ("R1 no docker binary at all (source: live container)", "CHILD nearest-visible " + T + DF,
         dict(path=[F["EMPTY"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
        ("R2 all tools present", "TOOLS env=sandbox ok=pdftotext,pdfinfo,pdftoppm missing=none",
         dict(path=[F["ALL"]] + nd, CLAUDE_SANDBOX_PROJECT_DIR=P2,
              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
        ("R3 extra tool", "MISSING sqlite3",
         dict(path=nd, CLAUDE_SANDBOX_PROJECT_DIR=P2, RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"],
              RESEARCH_PREFLIGHT_EXTRA="sqlite3")),
    ]
    # --- hosts (env hooks) --------------------------------------------------------------
    for fam, want in (
            ("DEBIAN", "FIX sudo apt-get install -y poppler-utils sqlite3"),
            ("UBUNTU", "FIX sudo apt-get install -y poppler-utils sqlite3"),
            ("FEDORA", "FIX sudo dnf install -y poppler-utils sqlite"),
            ("ARCH", "FIX sudo pacman -S --needed poppler sqlite"),
            ("OTHER", "FIX install the packages that provide: pdftotext,pdfinfo,pdftoppm,sqlite3 "
                      "(Debian names: poppler-utils sqlite3)")):
        out.append(("H host " + fam.lower(), want,
                    dict(sandbox=False, RESEARCH_PREFLIGHT_OS_RELEASE=F["OS_" + fam],
                         RESEARCH_PREFLIGHT_EXTRA="sqlite3")))
    out.append(("H host macOS (stub uname)", "FIX brew install poppler sqlite",
                dict(sandbox=False, path=[F["DARWIN"]], RESEARCH_PREFLIGHT_EXTRA="sqlite3")))
    return out


def matches(out, want):
    lines = out.splitlines()
    if want.startswith("~"):
        return want[1:] in out
    return want in lines


class Matrix(unittest.TestCase):
    """02 § Test matrix: 29 assertions, each under every shell."""

    def test_count(self):
        self.assertEqual(len(cases()), 29)

    def test_matrix(self):
        for shell in SHELLS:
            for label, want, kw in cases():
                with self.subTest(shell=shell, case=label):
                    rc, out = run(shell, **kw)
                    self.assertEqual(rc, 0, out)
                    self.assertTrue(matches(out, want), "want %r\n%s" % (want, out))

    def test_shells_agree(self):
        if len(SHELLS) < 2:
            self.skipTest("only one of dash/bash is installed")
        for label, _, kw in cases():
            with self.subTest(case=label):
                self.assertEqual(run(SHELLS[0], **kw)[1], run(SHELLS[1], **kw)[1])

    def test_never_prescribes_a_project_dockerfile(self):
        """Every 'create' in any output is the 'Do not create' warning."""
        for label, _, kw in cases() + LowFixes.cases():
            with self.subTest(case=label):
                out = run(SHELLS[0], **kw)[1]
                for m in re.finditer(r"\bcreate\b", out, re.I):
                    self.assertEqual(out[max(0, m.start() - 7):m.start()], "Do not ", out)

    def test_syntax(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                r = subprocess.run([shutil.which(shell), "-n", str(SCRIPT)],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                self.assertEqual(r.returncode, 0, r.stdout)


class LowFixes(unittest.TestCase):
    """The round-3 review lows (17, 18) the port fixed; 02's script fails each."""

    @staticmethod
    def cases():
        T, P2, E = F["T"], F["P2"], F["E"]
        DF = "/.claude-sandbox/Dockerfile"
        return [
            # 17a: the image was built from P2's file, since removed; the tree file is
            # farther, so it is the next one, never "nearer".
            ("17a matched file removed, next is farther",
             "CHILD confirmed " + P2 + DF + " removed next=" + T + DF,
             dict(path=[F["DP2"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
            ("17a FIX names the next file", "~it builds from " + T + DF,
             dict(path=[F["DP2"]], CLAUDE_SANDBOX_PROJECT_DIR=P2,
                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
            # 17b: removed, and no Dockerfile left on any mounted level.
            ("17b matched file removed, none left", "CHILD confirmed " + E + DF + " removed",
             dict(path=[F["DE"]], CLAUDE_SANDBOX_PROJECT_DIR=E,
                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_E"])),
            ("17b FIX says do not create", "~Do not create a project-level",
             dict(path=[F["DE"]], CLAUDE_SANDBOX_PROJECT_DIR=E,
                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_E"])),
            # 17c: matched at the project, present; the tree file is farther: no nearer=.
            ("17c nearest is the matched file", "CHILD confirmed " + F["P1"] + DF,
             dict(path=[F["DP1"]], CLAUDE_SANDBOX_PROJECT_DIR=F["P1"],
                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])),
        ]

    def test_low_17(self):
        for shell in SHELLS:
            for label, want, kw in self.cases():
                with self.subTest(shell=shell, case=label):
                    rc, out = run(shell, **kw)
                    self.assertEqual(rc, 0, out)
                    self.assertTrue(matches(out, want), "want %r\n%s" % (want, out))

    def test_low_18_physical_pwd(self):
        """With CLAUDE_SANDBOX_PROJECT_DIR unset, a symlinked cwd resolves physically."""
        for shell in SHELLS:
            with self.subTest(shell=shell):
                rc, out = run(shell, path=[F["NODOCKER"]], cwd=F["LINK1"], PWD=F["LINK1"],
                              RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_SEPHOME"])
                self.assertIn("CHILD nearest-visible " + F["P1"] + "/.claude-sandbox/Dockerfile",
                              out.splitlines(), out)


class Guards(unittest.TestCase):
    """Fix-round guards: whitespace in the chain, an unreadable mountinfo."""

    def test_whitespace_path_is_unknown(self):
        for shell in SHELLS:
            for docker in (F["NODOCKER"], F["DTREE"]):
                with self.subTest(shell=shell, docker=docker):
                    rc, out = run(shell, path=[docker], CLAUDE_SANDBOX_PROJECT_DIR=F["SPACE"],
                                  RESEARCH_PREFLIGHT_MOUNTINFO=F["MI_PARENT"])
                    self.assertEqual(rc, 0, out)
                    self.assertIn("CHILD unknown (path contains whitespace)", out.splitlines(), out)
                    self.assertIn("Do not create a project-level", out)

    def test_unreadable_mountinfo_counts_all_levels_visible(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                rc, out = run(shell, path=[F["NODOCKER"]], CLAUDE_SANDBOX_PROJECT_DIR=F["P2"],
                              RESEARCH_PREFLIGHT_MOUNTINFO=F["W"] + "/no-such-mountinfo")
                self.assertEqual(rc, 0, out)
                self.assertIn("CHILD nearest-visible " + F["T"] + "/.claude-sandbox/Dockerfile",
                              out.splitlines(), out)


class NegativeControl(unittest.TestCase):
    """The fixtures catch the faults 02's review found: each mutant reintroduces one
    fault from 01's script and must fail the case that guards it (02 § Negative control)."""

    MUTANTS = [
        # finding 12: 01's visibility rule, "mountinfo root ends with the mount point"
        ("root-suffix visibility",
         '    [ "$mp" = / ] && continue\n',
         '    [ "$mp" = / ] && continue\n    case "$_d" in *"$mp") ;; *) continue ;; esac\n',
         "M2 separate /home fs (root /rt/...)", "CHILD unseen "),
        # finding 13: 01 compared the tag against the nearest visible Dockerfile only
        ("tag checked against the nearest file only",
         "      for lvl in $levels; do   # every chain level",
         "      for lvl in ${near%/.claude-sandbox/Dockerfile}; do   # every chain level",
         "D2 tree unseen but hash-confirmed", "CHILD built-from-unseen "),
        # finding 16: 01 counted any baseOnly key, false included, as an override
        ("baseOnly: false read as an override",
         'case "${1:-}" in true|True|TRUE)',
         'case "${1:-}" in ?*)',
         "M7 local baseOnly:false beats upstream true", "CHILD override baseOnly "),
    ]

    def test_mutants_fail(self):
        src = SCRIPT.read_text()
        by_label = {c[0]: c for c in cases()}
        for name, old, new, label, bad in self.MUTANTS:
            with self.subTest(mutant=name):
                self.assertIn(old, src, "mutation target drifted: update the control")
                mutant = Path(F["W"]) / "mutant.sh"
                mutant.write_text(src.replace(old, new, 1))
                _, want, kw = by_label[label]
                out = run(SHELLS[0], script=mutant, **kw)[1]
                self.assertFalse(matches(out, want), "mutant passed %s:\n%s" % (label, out))
                self.assertIn(bad, out)


if __name__ == "__main__":
    unittest.main()
