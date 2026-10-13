"""Tests for claim_check.py. Every case builds its own fixture estate of git repos in a temp
dir and fixes the clock with --today, so the suite reads no repo file outside this skill and
passes from a copy of the plugin alone.

Run from the skill's scripts/ dir:

    python3 -m unittest discover -s tests -q
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import claim_check as cc  # noqa: E402

TODAY = "2026-10-09"
UP = ".."  # a parent-dir path part, kept out of literal paths
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def standard_text():
    """format.md § 7's standard text, as its lines (the blockquote, markers removed)."""
    lines = (SKILL / "references" / "format.md").read_text("utf-8").splitlines()
    i = lines.index("### The standard text")
    out = []
    for line in lines[i + 1:]:
        if line.startswith(">"):
            out.append(line[1:].strip())
        elif out:
            break
    return "\n".join(out)


STD = standard_text()

DEFAULTS = {
    "sentence": "{name} owns the order lifecycle.",
    "status": "Status: approved by the operator 2026-10-01",
    "reviewed": "Reviewed: 2026-10-01",
    "claim": ("## Claim\n\n{name} owns its records.\n\n| Area | What that covers |\n"
              "|---|---|\n| Order records | the tables |\n"),
    "not_ours": "## Not ours\n\n- pricing policy — operator\n",
    "boundaries": "## Boundaries\n\nnone known\n",
    "changing": "## Changing this claim\n\n" + STD + "\n",
}


def claim(name, extra="", **parts):
    """A complete claim for repo `name`; a part set to None is left out."""
    p = dict(DEFAULTS, title=f"# CLAIM: {name}")
    p.update(parts)
    blocks = [p["title"], p["sentence"]]
    head = [p[k] for k in ("status", "reviewed") if p[k] is not None]
    blocks.append("\n".join(head) if head else None)
    blocks += [p["claim"], p["not_ours"], p["boundaries"], extra or None, p["changing"]]
    return "\n\n".join(s.replace("{name}", name).strip("\n")
                       for s in blocks if s is not None) + "\n"


def git(cwd, *args):
    env = dict(os.environ, **GIT_ENV)
    subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                    "-C", str(cwd), *args], check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Estate:
    def __init__(self, root):
        self.dir = Path(root) / "estate"
        self.dir.mkdir()

    def repo(self, name, files=None, store=None, commit=True, untracked=None):
        d = self.dir / name
        d.mkdir()
        git(d, "init", "-q", "-b", "main")
        for rel, body in (files or {}).items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(body, bytes):
                p.write_bytes(body)
            else:
                p.write_text(body, "utf-8")
        if store:
            (d / store).mkdir(parents=True)
        if commit:
            git(d, "add", "-A")
            git(d, "commit", "-q", "--allow-empty", "-m", "init")
        for rel, body in (untracked or {}).items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, "utf-8")
        return d


def run(*args, today=TODAY):
    out, err = io.StringIO(), io.StringIO()
    argv = list(args) + (["--today", today] if today else [])
    code = cc.main(argv, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def run_json(*args, **kw):
    code, out, err = run(*args, "--json", **kw)
    return code, json.loads(out) if out else None, err


def kinds(doc):
    return sorted((f["flag"], f["kind"], f["repo"]) for f in doc["flags"])


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="claimcheck-")
        self.tmp = Path(self._tmp.name)
        self.e = Estate(self.tmp)
        cc._parse_hook = None

    def tearDown(self):
        cc._parse_hook = None
        self._tmp.cleanup()

    def check(self, repo, *args, **kw):
        return run_json("--repo", str(self.e.dir / repo), *args, **kw)

    def flags_of(self, repo, *args, **kw):
        code, doc, err = self.check(repo, *args, **kw)
        self.assertIn(code, (0, 1), err)
        return kinds(doc)

    def estate(self, *args, **kw):
        code, doc, err = run_json("--estate", "--dir", str(self.e.dir), *args, **kw)
        self.assertIn(code, (0, 1), err)
        return kinds(doc)


# -- shape -----------------------------------------------------------------------------------


class Shape(Base):
    def test_complete_claim_gives_no_flag(self):
        self.e.repo("a", {"CLAIM.md": claim("a")})
        code, doc, _ = self.check("a")
        self.assertEqual(code, 0)
        self.assertEqual(doc["flags"], [])

    def test_each_required_part_missing(self):
        cases = {"status": "status", "reviewed": "reviewed", "claim": "claim",
                 "not_ours": "not-ours", "boundaries": "boundaries", "changing": "changing"}
        for part, kind in cases.items():
            with self.subTest(part=part):
                name = "r" + part.replace("_", "")
                self.e.repo(name, {"CLAIM.md": claim(name, **{part: None})})
                self.assertIn(("SHAPE", kind, name), self.flags_of(name))

    def test_title_missing_or_wrong_name(self):
        self.e.repo("a", {"CLAIM.md": claim("a").replace("# CLAIM: a\n", "")})
        self.assertIn(("SHAPE", "title", "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim("b").replace("# CLAIM: b", "# CLAIM: other")})
        self.assertIn(("SHAPE", "title", "b"), self.flags_of("b"))
        self.e.repo("c", {"CLAIM.md": claim("c").replace("# CLAIM: c", "# CLAIM: `C`")})
        self.assertNotIn(("SHAPE", "title", "c"), self.flags_of("c"))

    def test_malformed_dates(self):
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2026-13-01")})
        self.assertIn(("SHAPE", "reviewed", "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim(
            "b", status="Status: proposed 2026-02-30, pending the operator")})
        self.assertIn(("SHAPE", "status", "b"), self.flags_of("b"))
        self.e.repo("c", {"CLAIM.md": claim("c", status="Status: approved, I think")})
        self.assertIn(("SHAPE", "status", "c"), self.flags_of("c"))

    def test_status_forms_accepted(self):
        for i, s in enumerate(["Status: approved by the operator 2026-10-01 (a0#12)",
                               "Status: approved by the operator 2026-10-01.",
                               "Status: proposed 2026-10-01, pending the operator"]):
            with self.subTest(status=s):
                name = f"a{i}"
                self.e.repo(name, {"CLAIM.md": claim(name, status=s.replace("a0", name))})
                self.assertEqual(self.flags_of(name), [])

    def test_heading_inside_a_fence_does_not_count(self):
        text = claim("a", boundaries=None) + "\n```\n## Boundaries\n\nnone known\n```\n"
        self.e.repo("a", {"CLAIM.md": text})
        self.assertIn(("SHAPE", "boundaries", "a"), self.flags_of("a"))

    def test_extra_headings_and_optional_sections_accepted(self):
        extra = ("## Roles\n\n### Producer\n\nemits.\n\n## Interfaces\n\nx\n\n## Readers\n\n"
                 "y\n\n## In transit\n\n| Thing | From | To | When |\n|---|---|---|---|\n"
                 "| a report | here | there | later |\n\n## Definitions\n\nz\n\n"
                 "## Amendments\n\n- 2026-10-01: first (upkeep, reported)\n\n"
                 "## Something else\n\nfree text\n")
        self.e.repo("a", {"CLAIM.md": claim("a", extra=extra)})
        self.assertEqual(self.flags_of("a"), [])

    def test_changing_text_must_be_the_standard_text(self):
        self.e.repo("a", {"CLAIM.md": claim("a", changing="## Changing this claim\n\nAsk me.\n")})
        self.assertIn(("SHAPE", "changing", "a"), self.flags_of("a"))
        rewrapped = "## Changing this claim\n\n" + " ".join(STD.split()).replace(
            "`## Boundaries`", "## Boundaries") + "\n"
        self.e.repo("b", {"CLAIM.md": claim("b", changing=rewrapped)})
        self.assertEqual(self.flags_of("b"), [])

    def test_template_and_format_carry_the_same_standard_text(self):
        tpl = (SKILL / "assets" / "CLAIM.template.md").read_text("utf-8")
        body = tpl.split("## Changing this claim", 1)[1]
        self.assertEqual(cc.N(body), cc.N(STD))

    def test_not_ours_lines(self):
        self.e.repo("a", {"CLAIM.md": claim("a", not_ours="## Not ours\n\n- no dash here\n")})
        self.assertIn(("SHAPE", "not-ours", "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours="## Not ours\n\nnone known\n")})
        self.assertEqual(self.flags_of("b"), [])
        self.e.repo("c", {"CLAIM.md": claim("c", not_ours="## Not ours\n\n")})
        self.assertIn(("SHAPE", "not-ours", "c"), self.flags_of("c"))
        self.e.repo("d", {"CLAIM.md": claim(
            "d", not_ours="## Not ours\n\nnone known\n- x — operator\n")})
        self.assertIn(("SHAPE", "not-ours", "d"), self.flags_of("d"))
        self.e.repo("f", {"CLAIM.md": claim(
            "f", not_ours="## Not ours\n\n- a thing — external:\n")})
        self.assertIn(("SHAPE", "not-ours", "f"), self.flags_of("f"))

    def test_boundaries_none_known_and_empty(self):
        self.e.repo("a", {"CLAIM.md": claim("a")})  # none known
        self.assertEqual(self.flags_of("a"), [])
        self.e.repo("b", {"CLAIM.md": claim("b", boundaries="## Boundaries\n\n")})
        self.assertIn(("SHAPE", "boundaries", "b"), self.flags_of("b"))
        self.e.repo("x")
        both = ("## Boundaries\n\nnone known\n\n### x\n\nRule: r.\n\n"
                "- an item — Defined here\n")
        self.e.repo("c", {"CLAIM.md": claim("c", boundaries=both)})
        self.assertIn(("SHAPE", "boundaries", "c"), self.flags_of("c"))

    def test_boundary_line_rule_reads_top_level_items_only(self):
        self.e.repo("x")
        ok = ("## Boundaries\n\n### x\n\nRule: x reads.\nSome prose about it.\n\n"
              "- the format — Defined here\n  - Ours: the writer, with a — dash\n"
              "  - Theirs: the reader\n")
        self.e.repo("a", {"CLAIM.md": claim("a", boundaries=ok)})
        self.assertEqual(self.flags_of("a"), [])
        bad = ok + "- a loose item with no pointer\n"
        self.e.repo("b", {"CLAIM.md": claim("b", boundaries=bad)})
        self.assertIn(("SHAPE", "boundaries", "b"), self.flags_of("b"))
        bad2 = ok.replace("— Defined here", "— Defined somewhere")
        self.e.repo("c", {"CLAIM.md": claim("c", boundaries=bad2)})
        self.assertIn(("SHAPE", "boundaries", "c"), self.flags_of("c"))

    def test_subsection_needs_a_rule_and_an_item(self):
        self.e.repo("x")
        self.e.repo("a", {"CLAIM.md": claim(
            "a", boundaries="## Boundaries\n\n### x\n\n- the format — Defined here\n")})
        self.assertIn(("SHAPE", "boundaries", "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim(
            "b", boundaries="## Boundaries\n\n### x\n\nRule: r.\n")})
        self.assertIn(("SHAPE", "boundaries", "b"), self.flags_of("b"))


# -- age -------------------------------------------------------------------------------------


class Age(Base):
    def test_stale_after_180_days(self):
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2026-04-11")})  # 181
        self.assertIn(("STALE", None, "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim("b", reviewed="Reviewed: 2026-04-12")})  # 180
        self.assertEqual(self.flags_of("b"), [])

    def test_pending_after_30_days(self):
        self.e.repo("a", {"CLAIM.md": claim(
            "a", status="Status: proposed 2026-09-08, pending the operator")})  # 31
        self.assertIn(("PENDING", None, "a"), self.flags_of("a"))
        self.e.repo("b", {"CLAIM.md": claim(
            "b", status="Status: proposed 2026-09-09, pending the operator")})  # 30
        self.assertEqual(self.flags_of("b"), [])

    def test_approved_never_pending(self):
        self.e.repo("a", {"CLAIM.md": claim(
            "a", status="Status: approved by the operator 2020-01-01")})
        self.assertNotIn(("PENDING", None, "a"), self.flags_of("a"))


# -- resolve ---------------------------------------------------------------------------------


class Resolve(Base):
    def test_unresolved_owner_neighbour_pointer(self):
        b = ("## Boundaries\n\n### ghost\n\nRule: r.\n\n- the format — Defined here\n")
        self.e.repo("a", {"CLAIM.md": claim(
            "a", not_ours="## Not ours\n\n- reports — nowhere\n", boundaries=b)})
        got = self.flags_of("a")
        self.assertIn(("UNRESOLVED", "owner", "a"), got)
        self.assertIn(("UNRESOLVED", "neighbour", "a"), got)
        self.e.repo("x")
        b2 = ("## Boundaries\n\n### x\n\nRule: r.\n\n"
              "- the format — Defined in ghost CLAIM.md § Boundaries\n"
              "- the api — Defined in ghost2 (no claim yet)\n")
        self.e.repo("c", {"CLAIM.md": claim("c", boundaries=b2)})
        got = self.flags_of("c")
        self.assertEqual([k for k in got if k[0] == "UNRESOLVED"],
                         [("UNRESOLVED", "pointer", "c")] * 2)

    def test_operator_and_external_never_flagged(self):
        self.e.repo("a", {"CLAIM.md": claim("a", not_ours=(
            "## Not ours\n\n- pricing — operator\n- payments — external: a vendor\n"))})
        self.assertEqual(self.flags_of("a"), [])

    def test_owner_matched_under_n(self):
        self.e.repo("metrics")
        self.e.repo("a", {"CLAIM.md": claim(
            "a", not_ours="## Not ours\n\n- reports — `Metrics`\n")})
        self.assertEqual(self.flags_of("a"), [])


# -- pointer ---------------------------------------------------------------------------------


def pointer_claim(name, where, nb="b"):
    return claim(name, boundaries=f"## Boundaries\n\n### {nb}\n\nRule: r.\n\n- the format — {where}\n")


class Pointer(Base):
    def b_with(self, files=None, untracked=None):
        return self.e.repo("b", files or {"CLAIM.md": claim("b", boundaries=(
            "## Boundaries\n\n### a\n\nRule: r.\n\n- the format — Defined here\n"
            "  - Ours: x\n  - Theirs: y\n"))}, untracked=untracked)

    def test_resolving_pointer(self):
        self.b_with()
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b CLAIM.md § Boundaries / a")})
        self.assertEqual(self.flags_of("a"), [])

    def test_heading_matched_under_n(self):
        self.b_with()
        self.e.repo("a", {"CLAIM.md": pointer_claim(
            "a", "Defined in b CLAIM.md § `boundaries`  /  A")})
        self.assertEqual(self.flags_of("a"), [])

    def test_dangling_kinds(self):
        self.b_with(untracked={"LOOSE.md": "## Boundaries\n"})
        cases = {
            "Defined in b MISSING.md § Boundaries": "file",
            "Defined in b LOOSE.md § Boundaries": "file",          # untracked
            "Defined in b CLAIM.md § Nowhere": "heading",
            "Defined in b CLAIM.md § a / Boundaries": "heading",    # wrong nesting
            f"Defined in b {UP}/b/CLAIM.md § Boundaries": "outside",
            "Defined in b /etc/hosts § Boundaries": "outside",
        }
        for i, (where, kind) in enumerate(cases.items()):
            with self.subTest(where=where):
                name = f"a{i}"
                self.e.repo(name, {"CLAIM.md": pointer_claim(name, where)})
                got = self.flags_of(name)
                self.assertIn(("DANGLING", kind, name), got)

    def test_dangling_symlink_out(self):
        outside = self.tmp / "outside.md"
        outside.write_text("## Boundaries\n", "utf-8")
        d = self.b_with()
        os.symlink(outside, d / "LINK.md")
        git(d, "add", "LINK.md")
        git(d, "commit", "-q", "-m", "link")
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b LINK.md § Boundaries")})
        self.assertIn(("DANGLING", "outside", "a"), self.flags_of("a"))

    def test_pathspec_is_literal(self):
        # A pointer to a file literally named *.md: the tracked check matches that name only,
        # never a glob over other tracked files.
        d = self.b_with(untracked={"*.md": "## Boundaries\n"})  # CLAIM.md is tracked
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b *.md § Boundaries")})
        self.assertIn(("DANGLING", "file", "a"), self.flags_of("a"))  # untracked, not globbed
        git(d, "add", "--", ":(literal)*.md")
        git(d, "commit", "-q", "-m", "star")
        self.assertEqual([f for f in self.flags_of("a") if f[0] == "DANGLING"], [])

    def test_pointer_into_a_charter(self):
        self.b_with({"CLAIM.md": claim("b"), "CHARTER.md": "# Charter\n\n## Boundary tests\n"})
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b CHARTER.md § Boundary tests")})
        self.assertEqual([f for f in self.flags_of("a") if f[0] == "DANGLING"], [])

    def test_awaiting(self):
        self.b_with()
        self.e.repo("c")
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b (no claim yet)")})
        self.assertIn(("AWAITING", None, "a"), self.flags_of("a"))
        self.e.repo("d", {"CLAIM.md": pointer_claim("d", "Defined in c (no claim yet)", nb="c")})
        self.assertEqual(self.flags_of("d"), [])


# -- reciprocity and conflict ------------------------------------------------------------------


def here_claim(name, nb, item="the format", **kw):
    return claim(name, boundaries=(f"## Boundaries\n\n### {nb}\n\nRule: r.\n\n"
                                   f"- {item} — Defined here\n  - Ours: x\n"), **kw)


class Pairs(Base):
    def test_one_sided(self):
        self.e.repo("b", {"CLAIM.md": claim("b")})
        self.e.repo("a", {"CLAIM.md": here_claim("a", "b")})
        self.assertIn(("ONE-SIDED", None, "a"), self.flags_of("a"))

    def test_one_sided_needs_a_neighbour_claim(self):
        self.e.repo("b")
        self.e.repo("a", {"CLAIM.md": here_claim("a", "b")})
        self.assertEqual(self.flags_of("a"), [])

    def test_reciprocal_pair_is_clean(self):
        self.e.repo("b", {"CLAIM.md": pointer_claim("b", "Defined in a CLAIM.md § Boundaries / b",
                                                    nb="a")})
        self.e.repo("a", {"CLAIM.md": here_claim("a", "b")})
        self.assertEqual(self.flags_of("a"), [])
        self.assertEqual(self.estate(), [])

    def test_defined_twice_under_n(self):
        self.e.repo("b", {"CLAIM.md": here_claim("b", "a", item="The `Format`")})
        self.e.repo("a", {"CLAIM.md": here_claim("a", "b", item="the format")})
        self.assertIn(("CONFLICT", "defined-twice", "a"), self.flags_of("a"))

    def test_defined_twice_is_pair_scoped(self):
        # a defines "the format" for b; c defines "the format" for a: different pairs.
        self.e.repo("b", {"CLAIM.md": pointer_claim("b", "Defined in a CLAIM.md § Boundaries / b",
                                                    nb="a")})
        self.e.repo("c", {"CLAIM.md": claim("c", boundaries=(
            "## Boundaries\n\n### a\n\nRule: r.\n\n- the format — Defined here\n"))})
        self.e.repo("a", {"CLAIM.md": claim("a", boundaries=(
            "## Boundaries\n\n### b\n\nRule: r.\n\n- the format — Defined here\n\n"
            "### c\n\nRule: r.\n\n- the format — Defined in c CLAIM.md § Boundaries / a\n"))})
        self.assertNotIn("defined-twice", [k for _, k, _ in self.estate()])

    def test_owner_conflict(self):
        self.e.repo("m")
        self.e.repo("n")
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours="## Not ours\n\n- Reports — n\n")})
        self.e.repo("a", {"CLAIM.md": claim("a", not_ours="## Not ours\n\n- `reports` — m\n")})
        self.assertIn(("CONFLICT", "owner", "a"), self.estate())

    def test_claimed_and_not_ours(self):
        self.e.repo("z")
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours="## Not ours\n\n- order records — z\n")})
        self.e.repo("a", {"CLAIM.md": claim("a")})  # claims "Order records"
        got = self.estate()
        self.assertIn(("CONFLICT", "claimed-and-not-ours", "a"), got)
        # owner a itself: no conflict
        shutil.rmtree(self.e.dir / "b")
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours="## Not ours\n\n- order records — a\n")})
        self.assertEqual(self.estate(), [])

    def test_single_mode_loads_named_neighbours(self):
        self.e.repo("m")
        self.e.repo("n")
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours="## Not ours\n\n- reports — n\n")})
        self.e.repo("a", {"CLAIM.md": claim(
            "a", not_ours="## Not ours\n\n- reports — m\n- other — b\n")})
        self.assertIn(("CONFLICT", "owner", "a"), self.flags_of("a"))


# -- in transit ------------------------------------------------------------------------------


def transit(*things):
    rows = "".join(f"| {t} | here | there | later |\n" for t in things)
    return "## In transit\n\n| Thing | From | To | When |\n|---|---|---|---|\n" + rows


class Transit(Base):
    def test_moved(self):
        self.e.repo("b", {"tool.py": "x\n"})
        self.e.repo("a", {"CLAIM.md": claim("a", extra=transit(
            "`b:tool.py`", "`b:gone.py`", "a report (no path)", f"`b:{UP}/a/CLAIM.md`"))})
        got = self.flags_of("a")
        self.assertEqual(sorted(k for k in got if k[0] == "MOVED?"),
                         [("MOVED?", "missing", "a"), ("MOVED?", "outside", "a")])

    def test_this_repo_paths_read_from_its_tree(self):
        self.e.repo("a", {"CLAIM.md": claim("a", extra=transit("`a:scripts/x.py`")),
                          "scripts/x.py": "x\n"})
        self.assertEqual(self.flags_of("a"), [])

    def test_symlink_out(self):
        (self.tmp / "o.py").write_text("x\n", "utf-8")
        d = self.e.repo("b")
        os.symlink(self.tmp / "o.py", d / "l.py")
        self.e.repo("a", {"CLAIM.md": claim("a", extra=transit("`b:l.py`"))})
        self.assertIn(("MOVED?", "outside", "a"), self.flags_of("a"))


# -- MISMATCH --------------------------------------------------------------------------------


def lib(*lines, fence=False):
    body = "## Librarian\nScope: whole repo\nNot owned:\n" + "".join(f"- {l}\n" for l in lines) \
        + "Checks:\n- make test\n"
    if fence:
        body = "```\n" + body + "```\n"
    return "# Project\n\n" + body + "\n## Other\n\ntext\n"


class Mismatch(Base):
    def repo(self, not_ours, claude):
        self.e.repo("m")
        return self.e.repo("a", {"CLAIM.md": claim("a", not_ours=not_ours), "CLAUDE.md": claude})

    def test_three_kinds(self):
        self.repo("## Not ours\n\n- reports — m\n- pricing — operator\n- dash — external: v\n",
                  lib("the cluster — m", "reports — operator", "dash — external: v"))
        code, doc, _ = self.check("a")
        got = sorted((f["flag"], f["kind"], f["owner_form"]) for f in doc["flags"])
        self.assertEqual(got, [("MISMATCH", "claim-only", "operator"),
                               ("MISMATCH", "librarian-only", "repo"),
                               ("MISMATCH", "owner", "repo")])
        owner = [f for f in doc["flags"] if f["kind"] == "owner"][0]
        self.assertTrue(re.fullmatch(r"a:CLAUDE\.md:\d+", owner["other"]))

    def test_names_before_the_dash(self):
        self.repo("## Not ours\n\n- `Reports` — m\n", lib("reports — m"))
        self.assertEqual(self.flags_of("a"), [])

    def test_external_claim_only_is_reported_with_its_form(self):
        self.repo("## Not ours\n\n- payments — external: a vendor\n", lib("other — m"))
        code, doc, _ = self.check("a")
        co = [f for f in doc["flags"] if f["kind"] == "claim-only"]
        self.assertEqual(len(co), 1)
        self.assertEqual(co[0]["owner_form"], "external")

    def test_either_list_absent_gives_no_flag(self):
        self.repo("## Not ours\n\n- reports — m\n", "# Project\n\n## Librarian\nScope: x\n")
        self.assertEqual(self.flags_of("a"), [])
        shutil.rmtree(self.e.dir / "a")
        shutil.rmtree(self.e.dir / "m")
        self.repo("## Not ours\n\n- reports — m\n", "# Project\n\nNo librarian here.\n")
        self.assertEqual(self.flags_of("a"), [])

    def test_none_known_is_not_a_name(self):
        self.repo("## Not ours\n\nnone known\n", lib("reports — m"))
        self.assertEqual(self.flags_of("a"), [("MISMATCH", "librarian-only", "a")])

    def test_librarian_section_in_a_fence_is_ignored(self):
        self.repo("## Not ours\n\n- reports — m\n", lib("other — m", fence=True))
        self.assertEqual(self.flags_of("a"), [])


# -- coverage --------------------------------------------------------------------------------


class Coverage(Base):
    def test_unclaimed(self):
        self.e.repo("s1", store=".work/items")
        self.e.repo("s2", store=".claude-sandbox/work/items")
        self.e.repo("plain")
        self.e.repo("ok", {"CLAIM.md": claim("ok")}, store=".work/items")
        self.assertEqual(self.estate(), [("UNCLAIMED", None, "s1"), ("UNCLAIMED", None, "s2")])

    def test_unclaimed_single_repo(self):
        self.e.repo("plain")
        self.assertEqual(self.flags_of("plain"), [("UNCLAIMED", None, "plain")])


# -- discovery and naming ---------------------------------------------------------------------


@contextlib.contextmanager
def cwd(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


@contextlib.contextmanager
def home(path):
    old = os.environ.get("HOME")
    os.environ["HOME"] = str(path)
    try:
        yield
    finally:
        if old is None:
            del os.environ["HOME"]
        else:
            os.environ["HOME"] = old


class Discovery(Base):
    def test_default_dir_from_main_and_from_a_worktree(self):
        a = self.e.repo("a", {"CLAIM.md": claim("a")})
        git(a, "worktree", "add", "-q", str(a / ".claude" / "worktrees" / "w"), "-b", "w")
        for where in (a, a / ".claude" / "worktrees" / "w"):
            with self.subTest(where=str(where)), cwd(where):
                code, out, err = run("--json")
                doc = json.loads(out)
                self.assertEqual(Path(doc["dir"]), Path(os.path.realpath(self.e.dir)))

    def test_refusal_of_home_and_above(self):
        a = self.e.repo("a", {"CLAIM.md": claim("a")})
        for h in (self.e.dir, a):  # the dir is $HOME; the dir is above $HOME
            with self.subTest(home=str(h)), home(h):
                code, _, err = run("--repo", str(a), "--estate")
                self.assertEqual(code, 2)
                self.assertIn("$HOME", err)
                code, out, _ = run("--repo", str(a), "--json")
                doc = json.loads(out)
                self.assertIsNone(doc["dir"])
                self.assertTrue(any("neighbour checks skipped" in n for n in doc["notes"]))
        self.assertTrue(cc.refused(Path("/")))

    def test_dir_overrides_the_default(self):
        other = self.tmp / "other"
        other.mkdir()
        self.e.repo("a", {"CLAIM.md": claim("a", not_ours="## Not ours\n\n- x — b\n")})
        self.assertIn(("UNRESOLVED", "owner", "a"), self.flags_of("a"))
        git_b = other / "b"
        git_b.mkdir()
        git(git_b, "init", "-q")
        code, doc, _ = self.check("a", "--dir", str(other))
        self.assertNotIn(("UNRESOLVED", "owner", "a"), kinds(doc))

    def test_non_utf8_directory_name_is_escaped(self):
        raw = os.fsdecode(b"r\xff")
        d = self.e.dir / raw
        d.mkdir()
        git(d, "init", "-q")
        (d / ".work" / "items").mkdir(parents=True)
        self.e.repo("a", {"CLAIM.md": claim("a")})
        code, out, err = run("--estate", "--dir", str(self.e.dir))
        self.assertEqual(code, 1, err)
        out.encode("utf-8")  # encodable: no lone surrogate reaches the output
        self.assertIn("UNCLAIMED - r\\xff:CLAIM.md:0 file", out)
        code, doc, _ = run_json("--estate", "--dir", str(self.e.dir))
        self.assertIn("r\\xff", [r["repo"] for r in doc["repos"]])
        self.assertIn(("UNCLAIMED", None, "r\\xff"), kinds(doc))

    def test_git_file_child_and_symlink_out_are_skipped(self):
        a = self.e.repo("a", {"CLAIM.md": claim("a")})
        git(a, "worktree", "add", "-q", str(self.e.dir / "a-wt"), "-b", "wt")
        far = self.tmp / "far"
        far.mkdir()
        git(far, "init", "-q")
        os.symlink(far, self.e.dir / "link")
        code, doc, _ = run_json("--estate", "--dir", str(self.e.dir))
        reasons = sorted(s["reason"] for s in doc["skipped"])
        self.assertEqual(len(reasons), 2)
        self.assertEqual([r["repo"] for r in doc["repos"]], ["a"])

    def test_worktree_naming_and_estate_replacement(self):
        b = self.e.repo("b", {"CLAIM.md": claim("b", boundaries=(
            "## Boundaries\n\n### a\n\nRule: r.\n\n- the format — Defined in a CLAIM.md § "
            "Boundaries / b\n"))})
        a = self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2020-01-01")})
        wt = a / ".claude" / "worktrees" / "draft-dir"
        git(a, "worktree", "add", "-q", str(wt), "-b", "draft")
        (wt / "CLAIM.md").write_text(here_claim("a", "b"), "utf-8")
        git(wt, "commit", "-qam", "draft")
        code, doc, _ = run_json("--repo", str(wt))
        self.assertEqual([r["repo"] for r in doc["repos"]], ["a"])
        self.assertEqual(doc["flags"], [])  # the worktree's claim, not main's stale one
        code, doc, _ = run_json("--repo", str(wt), "--estate")
        self.assertEqual(sorted(r["repo"] for r in doc["repos"]), ["a", "b"])
        self.assertEqual(Path(next(r["path"] for r in doc["repos"] if r["repo"] == "a")), wt)
        self.assertNotIn("CONFLICT", [f["flag"] for f in doc["flags"]])
        self.assertEqual(doc["flags"], [])


# -- --claim ---------------------------------------------------------------------------------


class ClaimArg(Base):
    def test_claim_replaces_the_repos_claim(self):
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2020-01-01")})
        draft = self.tmp / "draft.md"
        draft.write_text(claim("a"), "utf-8")
        self.assertIn(("STALE", None, "a"), self.flags_of("a"))
        code, doc, _ = self.check("a", "--claim", str(draft))
        self.assertEqual(doc["flags"], [])
        self.assertEqual(doc["repos"][0]["claim"], str(draft))
        draft.write_text(claim("a", status=None), "utf-8")
        code, doc, _ = self.check("a", "--claim", str(draft))
        self.assertEqual(doc["flags"][0]["file"], str(draft))
        self.assertEqual(doc["flags"][0]["flag"], "SHAPE")

    def test_claim_missing_file(self):
        self.e.repo("a")
        code, out, err = run("--repo", str(self.e.dir / "a"), "--claim", str(self.tmp / "no.md"))
        self.assertEqual(code, 2)
        self.assertEqual(err.strip(), "claim_check: the --claim file does not exist")

    def test_claim_with_estate_replaces_only_this_repo(self):
        self.e.repo("b", {"CLAIM.md": claim("b", reviewed="Reviewed: 2020-01-01")})
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2020-01-01")})
        draft = self.tmp / "draft.md"
        draft.write_text(claim("a"), "utf-8")
        code, doc, _ = self.check("a", "--estate", "--claim", str(draft))
        self.assertEqual(kinds(doc), [("STALE", None, "b")])

    def test_stand_in_claim_is_exempt_from_tracked(self):
        # b points at a's CLAIM.md heading; a's claim is an untracked draft passed as --claim.
        self.e.repo("b", {"CLAIM.md": claim("b", boundaries=(
            "## Boundaries\n\n### a\n\nRule: r.\n\n- the format — Defined in a CLAIM.md § "
            "Boundaries / b\n"))})
        self.e.repo("a")
        draft = self.tmp / "draft.md"
        draft.write_text(here_claim("a", "b"), "utf-8")
        code, doc, _ = self.check("a", "--estate", "--claim", str(draft))
        self.assertEqual(doc["flags"], [])


# -- limits ----------------------------------------------------------------------------------


class Limits(Base):
    def test_problem_kinds(self):
        big = claim("big") + ("x" * 1024 + "\n") * 300
        self.e.repo("big", {"CLAIM.md": big})
        self.e.repo("bad", {"CLAIM.md": b"# CLAIM: bad\n\xff\xfe\n"})
        d = self.e.repo("dir")
        (d / "CLAIM.md").mkdir()
        (d / "CLAIM.md" / "x").write_text("x", "utf-8")
        out = self.tmp / "out.md"
        out.write_text(claim("sym"), "utf-8")
        s = self.e.repo("sym")
        os.symlink(out, s / "CLAIM.md")
        u = self.e.repo("unr", {"CLAIM.md": claim("unr")})
        os.chmod(u / "CLAIM.md", 0)
        try:
            got = self.estate()
        finally:
            os.chmod(u / "CLAIM.md", 0o644)
        problems = sorted((k, r) for f, k, r in got if f == "PROBLEM")
        expected = [("not-regular", "dir"), ("not-utf8", "bad"), ("symlink-out", "sym"),
                    ("too-large", "big")]
        if os.geteuid() != 0:
            expected.append(("unreadable", "unr"))
        self.assertEqual(problems, sorted(expected))

    def test_fifo_is_not_opened(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("no mkfifo")
        d = self.e.repo("f")
        os.mkfifo(d / "CLAIM.md")
        self.assertEqual(self.flags_of("f"), [("PROBLEM", "not-regular", "f")])


# -- the output contract ----------------------------------------------------------------------


def tree_hash(root):
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(dirnames + filenames):
            p = Path(dirpath) / name
            st = os.lstat(p)
            h.update(str(p.relative_to(root)).encode("utf-8", "surrogateescape"))
            h.update(str(st.st_mode).encode())
            if os.path.islink(p):
                h.update(os.readlink(p).encode("utf-8", "surrogateescape"))
            elif os.path.isfile(p):
                h.update(p.read_bytes())
    return h.hexdigest()


class Contract(Base):
    def test_json_keys_and_types(self):
        self.e.repo("b")
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2020-01-01")})
        code, doc, _ = self.check("a")
        self.assertEqual(code, 1)
        self.assertEqual(set(doc), {"version", "today", "dir", "repos", "flags", "skipped",
                                    "notes"})
        self.assertEqual(doc["version"], 1)
        self.assertEqual(set(doc["repos"][0]), {"repo", "path", "claim", "store"})
        self.assertEqual(set(doc["flags"][0]), {"flag", "kind", "repo", "file", "line",
                                                "section", "other", "owner_form"})
        self.assertTrue(os.path.isabs(doc["repos"][0]["claim"]))
        code, doc, _ = run_json("--estate", "--dir", str(self.e.dir))
        claims = {r["repo"]: r["claim"] for r in doc["repos"]}
        self.assertIs(claims["b"], False)
        self.assertIsInstance(claims["a"], str)

    def test_text_line_shape(self):
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed="Reviewed: 2020-01-01")})
        code, out, _ = run("--repo", str(self.e.dir / "a"))
        self.assertEqual(code, 1)
        first = out.splitlines()[0]
        self.assertRegex(first, r"^STALE - a:CLAIM\.md:\d+ Reviewed$")
        self.assertTrue(out.splitlines()[-1].startswith("notes: "))

    def test_exit_codes(self):
        self.e.repo("a", {"CLAIM.md": claim("a")})
        self.assertEqual(run("--repo", str(self.e.dir / "a"))[0], 0)
        self.assertEqual(run("--repo", str(self.e.dir / "a"), "--bogus")[0], 2)
        self.assertEqual(run("--repo", str(self.e.dir / "a"), today="2026-1-1")[0], 2)
        self.assertEqual(run("--repo", str(self.tmp))[0], 2)  # not a git repo
        cc._parse_hook = lambda text: 1 / 0
        code, out, err = run("--repo", str(self.e.dir / "a"))
        self.assertEqual(code, 3)
        self.assertEqual(err.strip(), cc.INTERNAL)
        self.assertEqual(out, "")

    def test_runs_as_a_script(self):
        self.e.repo("a", {"CLAIM.md": claim("a")})
        r = subprocess.run([sys.executable, str(SCRIPTS / "claim_check.py"), "--repo",
                            str(self.e.dir / "a"), "--today", TODAY], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_read_only(self):
        self.e.repo("b", {"CLAIM.md": here_claim("b", "a")}, store=".work/items")
        self.e.repo("a", {"CLAIM.md": pointer_claim("a", "Defined in b CLAIM.md § Boundaries / a"),
                          "CLAUDE.md": lib("x — b")})
        before = tree_hash(self.e.dir)
        run("--repo", str(self.e.dir / "a"))
        run("--repo", str(self.e.dir / "a"), "--json")
        run("--estate", "--dir", str(self.e.dir))
        self.assertEqual(tree_hash(self.e.dir), before)


# -- no content: the sentinel ------------------------------------------------------------------

S = "SENTINEL"


class Sentinel(Base):
    def assert_clean(self, repo, flag, kind, *extra):
        for mode in ([], ["--json"]):
            code, out, err = run("--repo", str(self.e.dir / repo), *extra, *mode)
            with self.subTest(mode=mode, flag=flag):
                self.assertNotIn(S, out)
                self.assertNotIn(S, err)
                if mode:
                    self.assertIn((flag, kind), [(f["flag"], f["kind"])
                                                 for f in json.loads(out)["flags"]])
                else:
                    self.assertIn(f"{flag} {kind or '-'} ", out)

    def test_free_text_fields(self):
        self.e.repo("r2")
        text = claim("a", sentence=f"a owns {S} things.", reviewed="Reviewed: 2020-01-01",
                     claim=f"## Claim\n\n{S}.\n\n| Area | What |\n|---|---|\n| {S} area | {S} |\n",
                     boundaries=(f"## Boundaries\n\n### r2\n\nRule: {S} rule.\n\n"
                                 f"- {S} item — Defined here\n  - Ours: {S}\n"))
        self.e.repo("a", {"CLAIM.md": text})
        self.assert_clean("a", "STALE", None)

    def test_owner(self):
        self.e.repo("a", {"CLAIM.md": claim("a", not_ours=f"## Not ours\n\n- x — {S}-x\n")})
        self.assert_clean("a", "UNRESOLVED", "owner")

    def test_pointer_file_and_heading(self):
        self.e.repo("r2", {"CLAIM.md": claim("r2")})
        self.e.repo("a", {"CLAIM.md": pointer_claim(
            "a", f"Defined in r2 {S}.md § Boundaries", nb="r2")})
        self.assert_clean("a", "DANGLING", "file")
        self.e.repo("c", {"CLAIM.md": pointer_claim(
            "c", f"Defined in r2 CLAIM.md § {S}", nb="r2")})
        self.assert_clean("c", "DANGLING", "heading")

    def test_in_transit(self):
        self.e.repo("r2")
        self.e.repo("a", {"CLAIM.md": claim("a", extra=transit(f"`r2:{S}`"))})
        self.assert_clean("a", "MOVED?", "missing")

    def test_neighbour(self):
        self.e.repo("a", {"CLAIM.md": claim("a", boundaries=(
            f"## Boundaries\n\n### {S}\n\nRule: r.\n\n- x — Defined here\n"))})
        self.assert_clean("a", "UNRESOLVED", "neighbour")

    def test_reviewed_date(self):
        self.e.repo("a", {"CLAIM.md": claim("a", reviewed=f"Reviewed: 2026-13-01 {S}")})
        self.assert_clean("a", "SHAPE", "reviewed")

    def test_not_ours_name_in_conflict_and_mismatch(self):
        self.e.repo("m")
        self.e.repo("n")
        self.e.repo("b", {"CLAIM.md": claim("b", not_ours=f"## Not ours\n\n- {S} thing — n\n")})
        self.e.repo("a", {"CLAIM.md": claim(
            "a", not_ours=f"## Not ours\n\n- {S} thing — m\n- other — b\n"),
            "CLAUDE.md": lib(f"{S} thing — n", f"{S} only — m")})
        self.assert_clean("a", "CONFLICT", "owner")
        self.assert_clean("a", "MISMATCH", "owner")
        self.assert_clean("a", "MISMATCH", "librarian-only")

    def test_guard(self):
        self.e.repo("a", {"CLAIM.md": claim("a")})

        def boom(text):
            raise ValueError(f"{S} {text}")
        cc._parse_hook = boom
        for mode in ([], ["--json"]):
            code, out, err = run("--repo", str(self.e.dir / "a"), *mode)
            self.assertEqual(code, 3)
            self.assertNotIn(S, out + err)
            self.assertEqual(err.strip(), cc.INTERNAL)


# -- the shipped example (tier 4, in the suite) ------------------------------------------------


class Example(Base):
    def test_example_pair_with_deploy_gives_no_flag(self):
        ex = (SKILL / "references" / "example.md").read_text("utf-8")
        blocks = dict(re.findall(r"## `(\w+)/CLAIM\.md`\n\n```markdown\n(.*?)\n```", ex, re.S))
        self.assertEqual(sorted(blocks), ["metrics", "orders"])
        for name, body in blocks.items():
            body = body.replace("<the standard text, format.md § 7, verbatim>", STD)
            files = {"CLAIM.md": body + "\n"}
            if name == "orders":
                files["scripts/weekly_report.py"] = "x\n"
            self.e.repo(name, files)
        self.e.repo("deploy")
        code, doc, err = run_json("--estate", "--dir", str(self.e.dir), today="2026-10-09")
        self.assertEqual((code, doc["flags"]), (0, []), err)


if __name__ == "__main__":
    unittest.main()
