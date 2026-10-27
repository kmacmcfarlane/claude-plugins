"""The group and depends lines read and linted by `wi` (03ab F2).

format.md § Groups and dependencies defines the lines; `wi` parses them
read-only into the JSON views (`needs-input --json`, `estate --json`): each
decision record gains `group` ({"id", "name", "shares", "context"}, resolved
store-wide, or null with no member line) and `depends` (the last line's
targets, [] after `none`, null with no line). `wi lint` reports malformed,
orphan, unknown id, no members, duplicate id, dangling, self and cycle, each
naming the file and line, and never follows a link for these reads.

Each check here was proved against a mutant of wi.py: the mutant named in
the test's docstring makes it fail. Temporary stores only; git runs with a
temp HOME and global config, and never sees a repo around the temp dir.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"
FORMAT = HERE.parent / "references" / "format.md"

spec = importlib.util.spec_from_file_location("wi_links", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

GIT = shutil.which("git")
ITEM = """---
id: {iid}
title: {iid}
type: task
status: {status}
priority: 2
created: 2026-08-01
updated: 2026-08-01
---

Description of {iid}.

## Notes
{notes}
"""
GID = "g-1022-a3f"
GID2 = "g-1023-b04"


class LinkCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="wi-links-")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = self.tmp / "home"
        home.mkdir()
        (home / "gitconfig").write_text("")
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "WI_", "WORK_ITEMS_"))}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home),
                   GIT_CONFIG_GLOBAL=str(home / "gitconfig"),
                   GIT_CONFIG_NOSYSTEM="1",
                   GIT_CEILING_DIRECTORIES=str(self.tmp),
                   WORK_ITEMS_OWNER="tester@local")
        self.env = env
        self.base = self.tmp / "base"
        self.root = self.base / ".work-items"
        (self.root / "items").mkdir(parents=True)
        (self.root / "store.yaml").write_text(
            "# wi store settings; format: the work-items skill's "
            "references/format.md\ntracking: tracked\n")

    # -- helpers ---------------------------------------------------------

    def wi(self, *args):
        env = dict(self.env, WORK_ITEMS_ROOT=str(self.root))
        return subprocess.run([sys.executable, str(WI), *args], env=env,
                              capture_output=True, text=True, cwd=self.tmp)

    def item(self, iid, *lines, where="items", status="todo"):
        path = self.root / where / f"{iid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ITEM.format(iid=iid, status=status,
                                    notes="\n".join(lines)))
        return path

    def needs(self):
        """{(id, N): decision record} from needs-input --json."""
        r = self.wi("needs-input", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return {(rec["id"], d["n"]): d for rec in json.loads(r.stdout)
                for d in rec["decisions"]}

    def lint(self):
        """lint's problem lines that this feature reports (the store's own
        custody lines are not this file's business)."""
        r = self.wi("lint")
        self.assertIn(r.returncode, (0, 3), r.stdout + r.stderr)
        return [ln for ln in r.stdout.splitlines()
                if not ln.startswith(("lint clean",))
                and ("group" in ln or "depends" in ln or "decision" in ln
                     or "symbolic link" in ln)]

    def where(self, path, text):
        """`<path>:<line>` of the first line equal to `text`."""
        lines = path.read_text().split("\n")
        return f"{path}:{lines.index(text) + 1}"


# ── JSON ────────────────────────────────────────────────────────────────────


class TestJson(LinkCase):

    def test_no_lines_gives_null(self):
        """Mutant: link_fields returning {} for a missing member ({"id":
        None, …}) instead of null."""
        self.item("a-item-1111", "decision 4: open?")
        d = self.needs()[("a-item-1111", 4)]
        self.assertIsNone(d["group"])
        self.assertIsNone(d["depends"])

    def test_member_resolves_its_entity(self):
        """Mutant: the entity lookup dropped (name always null)."""
        self.item("a-item-1111", "decision 4: open?",
                  f"group {GID}: decision cards  ", f"group 4: {GID}")
        self.assertEqual(self.needs()[("a-item-1111", 4)]["group"],
                         {"id": GID, "name": "decision cards",
                          "shares": None, "context": None})

    def test_bundle_carries_shares_and_context(self):
        """Mutant: shares and context not carried into the record."""
        self.item("a-item-1111", "decision 4: open?",
                  f"group {GID}: upload findings · shares: all from today's "
                  "review · context: the review read the upload path",
                  f"group 4: {GID}")
        g = self.needs()[("a-item-1111", 4)]["group"]
        self.assertEqual((g["shares"], g["context"]),
                         ("all from today's review",
                          "the review read the upload path"))

    def test_rename_last_entity_line_wins(self):
        """The operator's drift fixed: a rename is one appended entity
        line, members unchanged, every member reads the new name. Mutant:
        the first entity line kept."""
        self.item("a-item-1111", "decision 4: open?", "decision 5: open?",
                  f"group {GID}: old name", f"group 4: {GID}",
                  f"group 5: {GID}", f"group {GID}: new name")
        d = self.needs()
        self.assertEqual({d[("a-item-1111", n)]["group"]["name"]
                          for n in (4, 5)}, {"new name"})
        self.assertEqual(self.lint(), [])

    def test_regroup_last_member_line_wins(self):
        """Mutant: the first member line per N kept."""
        self.item("a-item-1111", "decision 4: open?", f"group {GID}: one",
                  f"group {GID2}: two", f"group 4: {GID}", f"group 4: {GID2}")
        self.assertEqual(self.needs()[("a-item-1111", 4)]["group"]["id"],
                         GID2)

    def test_entity_in_an_archived_item_resolves(self):
        """Mutant: needs-input looks the id up in items/ only."""
        self.item("old-item-2222", f"group {GID}: archived group",
                  where="archive/2026", status="done")
        self.item("a-item-1111", "decision 4: open?", f"group 4: {GID}")
        self.assertEqual(self.needs()[("a-item-1111", 4)]["group"]["name"],
                         "archived group")

    def test_unknown_id_has_null_values(self):
        """Mutant: an unknown id given null for the whole key."""
        self.item("a-item-1111", "decision 4: open?", f"group 4: {GID}")
        self.assertEqual(self.needs()[("a-item-1111", 4)]["group"],
                         {"id": GID, "name": None, "shares": None,
                          "context": None})

    def test_fenced_and_indented_lines_are_not_read(self):
        """Mutant: _link_scan's fence rule removed."""
        self.item("a-item-1111", "decision 4: open?",
                  f"group {GID}: name", "```", f"group 4: {GID}",
                  "depends 4: 3", "```", f"  group 4: {GID}", "  depends 4: 3")
        d = self.needs()[("a-item-1111", 4)]
        self.assertIsNone(d["group"])
        self.assertIsNone(d["depends"])

    def test_depends_targets_split(self):
        """Mutant: the target's repo or letter dropped."""
        self.item("a-item-1111", "decision 4: open?",
                  "depends 4: 3 (a), 3 (c), agents#12, 2 — why")
        self.assertEqual(self.needs()[("a-item-1111", 4)]["depends"], [
            {"n": 3, "repo": None, "letter": "a"},
            {"n": 3, "repo": None, "letter": "c"},
            {"n": 12, "repo": "agents", "letter": None},
            {"n": 2, "repo": None, "letter": None}])

    def test_last_depends_line_is_the_whole_set_and_none_empties_it(self):
        """Mutant: the first depends line per N kept."""
        self.item("a-item-1111", "decision 4: open?", "decision 5: open?",
                  "depends 4: 3", "depends 4: none — settled",
                  "depends 5: 3", "depends 5: 2")
        d = self.needs()
        self.assertEqual(d[("a-item-1111", 4)]["depends"], [])
        self.assertEqual(d[("a-item-1111", 5)]["depends"],
                         [{"n": 2, "repo": None, "letter": None}])

    def test_text_and_plain_unchanged_by_the_lines(self):
        """Text and --plain output are byte-identical with and without the
        lines."""
        self.item("a-item-1111", "decision 4: open?")
        before = (self.wi("needs-input").stdout,
                  self.wi("needs-input", "--plain").stdout)
        self.item("a-item-1111", "decision 4: open?", f"group {GID}: x",
                  f"group 4: {GID}", "depends 4: none")
        self.assertEqual((self.wi("needs-input").stdout,
                          self.wi("needs-input", "--plain").stdout), before)

    def test_a_linked_archive_file_is_not_read(self):
        """A store-wide read follows no link: an entity line only in a
        symlinked archive file does not resolve. Mutant: _no_link always
        True."""
        outside = self.tmp / "outside.md"
        outside.write_text(ITEM.format(iid="old-item-2222", status="done",
                                       notes=f"group {GID}: linked"))
        (self.root / "archive" / "2026").mkdir(parents=True)
        (self.root / "archive" / "2026" / "old-item-2222.md").symlink_to(
            outside)
        self.item("a-item-1111", "decision 4: open?", f"group 4: {GID}")
        self.assertIsNone(self.needs()[("a-item-1111", 4)]["group"]["name"])

    def test_a_linked_archive_dir_is_not_read(self):
        """Mutant: _no_link checks only the file, not its directories."""
        real = self.tmp / "elsewhere"
        real.mkdir()
        (real / "old-item-2222.md").write_text(ITEM.format(
            iid="old-item-2222", status="done", notes=f"group {GID}: linked"))
        (self.root / "archive").mkdir()
        (self.root / "archive" / "2026").symlink_to(real)
        self.item("a-item-1111", "decision 4: open?", f"group 4: {GID}")
        self.assertIsNone(self.needs()[("a-item-1111", 4)]["group"]["name"])

    def test_estate_carries_the_same_fields(self):
        """Mutant: estate's decision records without link_fields."""
        scan = self.tmp
        self.item("old-item-2222", f"group {GID}: archived group",
                  where="archive/2026", status="done")
        self.item("a-item-1111", "decision 4: open?", f"group 4: {GID}",
                  "depends 4: agents#3 (b)")
        r = self.wi("estate", "--dir", str(scan), "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        repos = json.loads(r.stdout)["repos"]
        repo = [x for x in repos if x["repo"] == "base"]
        self.assertEqual(len(repo), 1, repos)
        repo = repo[0]
        d = repo["decisions"][0]
        self.assertEqual(d["group"], {"id": GID, "name": "archived group",
                                      "shares": None, "context": None})
        self.assertEqual(d["depends"],
                         [{"n": 3, "repo": "agents", "letter": "b"}])

    def test_wi_patterns_are_the_formats(self):
        """wi.py holds the section's own patterns, `T` expanded. Mutant:
        `[a-y]` widened to `[a-z]` in DEPENDS_RE."""
        text = FORMAT.read_text()
        start = text.index("## Groups and dependencies")
        sec = text[start:text.index("\n## ", start + 3)]
        t = re.search(r"`T` standing for one\s+target, `([^`]+)`", sec)
        pats = dict(re.findall(r"^- (group entity|group member|depends|each "
                               r"target): `([^`]+)`$", sec, re.M))
        self.assertEqual(pats["group entity"], wi.GROUP_ENTITY_RE.pattern)
        self.assertEqual(pats["group member"], wi.GROUP_MEMBER_RE.pattern)
        self.assertEqual(pats["depends"].replace("T", t.group(1)),
                         wi.DEPENDS_RE.pattern)
        self.assertEqual(pats["each target"], wi.TARGET_RE.pattern)

    def test_format_says_a_superseded_line_counts_and_how_to_clear_it(self):
        """L1: `closed N:` stays unparsed, and the cycle bullet says what
        that means. Mutant: either sentence deleted from format.md."""
        flat = " ".join(FORMAT.read_text().split())
        self.assertIn("a superseded decision's own leftover `depends N:` line "
                      "still counts", flat)
        self.assertIn("appending `depends N: none` to it clears the finding",
                      flat)


# ── lint ────────────────────────────────────────────────────────────────────


class TestLint(LinkCase):

    def test_a_clean_store(self):
        self.item("a-item-1111", "decision 4: open?", "decision 5: open?",
                  f"group {GID}: x · shares: y · context: z",
                  f"group 4: {GID}", f"group 5: {GID}",
                  "depends 5: 4 (a), agents#9 — why", "depends 4: none")
        r = self.wi("lint")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_malformed(self):
        """Each candidate that matches no pattern, with its path and line;
        `groups 4:` and a fenced line are no candidates. Mutant: the
        malformed branch of _link_scan removed."""
        bad = ["group 4: decision cards", "group g-1022-A3F: x",
               "group g-1022-a3f:  x", "depends 4: 3 (z)",
               "depends 4: 3 —  ", "group 4:"]
        p = self.item("a-item-1111", "decision 4: open?", "decision 3: x?",
                      *bad, "groups 4: x", "```", "depends 4: 3 (z) ",
                      "```")
        got = self.lint()
        for line in bad:
            kind = line.split()[0]
            self.assertIn(f"{self.where(p, line)}: malformed {kind} line, "
                          "not read", "\n".join(got))
        self.assertEqual(len(got), len(bad), got)

    def test_orphan(self):
        """Mutant: the orphan check removed."""
        p = self.item("a-item-1111", "decision 4: open?",
                      f"group {GID}: x", f"group 4: {GID}", f"group 9: {GID}",
                      "depends 9: 4")
        self.item("b-item-2222", "decision 9: open?")
        got = self.lint()
        self.assertEqual(got, [
            f"{self.where(p, f'group 9: {GID}')}: orphan group line: this "
            "item holds no `decision 9:` line; move it to the item that does",
            f"{self.where(p, 'depends 9: 4')}: orphan depends line: this "
            "item holds no `decision 9:` line; move it to the item that "
            "does"])

    def test_unknown_id(self):
        """The last member line only: one regrouped onto a known id is
        clean. Mutant: the unknown-id check removed."""
        p = self.item("a-item-1111", "decision 4: open?", "decision 5: x?",
                      f"group {GID}: x", f"group 4: {GID2}",
                      f"group 5: {GID2}", f"group 5: {GID}")
        self.assertEqual(self.lint(), [
            f"{self.where(p, f'group 4: {GID2}')}: decision 4: unknown "
            f"group id {GID2}, with no entity line in items/ or archive/"])

    def test_no_members(self):
        """An id no member line ever named fires; one whose only member was
        regrouped later is clean. Mutant: only last member lines count as
        naming an id."""
        p = self.item("a-item-1111", "decision 4: open?",
                      f"group {GID}: first", f"group {GID2}: second",
                      "group g-1024-ccc: never named",
                      f"group 4: {GID}", f"group 4: {GID2}")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'group g-1024-ccc: never named')}: group "
            "g-1024-ccc has no members: no member line (`group N: "
            "g-1024-ccc`) names it anywhere in the store"])

    def test_duplicate_id(self):
        """Two items fire, at the later one, naming the first; one id
        twice in one item is a revision. Mutant: every repeat counted, so
        the one-item case fires."""
        self.item("a-item-1111", "decision 4: open?", f"group {GID}: x",
                  f"group {GID}: x renamed", f"group 4: {GID}")
        p = self.item("b-item-2222", "decision 5: open?", f"group {GID}: y",
                      f"group 5: {GID}")
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertTrue(got[0].startswith(
            f"{self.where(p, f'group {GID}: y')}: duplicate group id {GID}: "
            f"its entity line is also in {self.root / 'items' / 'a-item-1111.md'}"),
            got)
        self.assertIn("deletes it and re-creates its group under a new id",
                      got[0])

    def test_duplicate_with_an_archived_copy_flags_the_live_one(self):
        """L4: the archived copy is kept, the items/ line flagged. Mutant:
        the first copy in lookup order (items/) kept."""
        old = self.item("old-item-3333", f"group {GID}: old",
                        where="archive/2026", status="done")
        p = self.item("a-item-1111", "decision 4: open?", f"group {GID}: x",
                      f"group 4: {GID}")
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertTrue(got[0].startswith(
            f"{self.where(p, f'group {GID}: x')}: duplicate group id {GID}: "
            f"its entity line is also in {old}"), got)

    def test_duplicate_fixed_is_clean(self):
        """After the later line is deleted and its group re-created under
        a new id with new member lines, the store is clean."""
        self.item("a-item-1111", "decision 4: open?", f"group {GID}: x",
                  f"group 4: {GID}")
        self.item("b-item-2222", "decision 5: open?", f"group {GID2}: y",
                  f"group 5: {GID2}")
        self.assertEqual(self.lint(), [])

    def test_dangling(self):
        """A bare target and an archived decision; another repo's target
        is syntax only. Mutant: the dangling check removed."""
        self.item("old-item-3333", "decision 2: old?", "answer 2: a",
                  where="archive/2026", status="done")
        p = self.item("a-item-1111", "decision 4: open?",
                      "depends 4: 2, 99 (b), agents#98")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 4: 2, 99 (b), agents#98')}: decision "
            "4: dangling target 99, with no `decision 99:` line in items/ "
            "or archive/"])

    def test_only_the_last_depends_line_is_held(self):
        """An appended line clears a dangling target. Mutant: every
        depends line held, not the last per N."""
        self.item("a-item-1111", "decision 4: open?", "depends 4: 99",
                  "depends 4: none — the reframe settled it")
        self.assertEqual(self.lint(), [])

    def test_self(self):
        """Mutant: the self check removed (the edge then left to the cycle
        check, which skips it)."""
        p = self.item("a-item-1111", "decision 4: open?", "depends 4: 4")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 4: 4')}: decision 4 depends on "
            "itself (4)"])

    def test_cycles(self):
        """A 2-cycle and a 3-cycle fire, each once; a chain does not, nor
        the chain into a cycle, which is named from its lowest N; two
        cycles sharing nodes are one finding. Mutants: the cycle walk
        removed; a component's members not sorted (named from where the
        walk entered it); every component reported, singletons included."""
        p = self.item("a-item-1111", *[f"decision {n}: x?" for n in range(1, 17)],
                      "depends 1: 2", "depends 2: 1",
                      "depends 3: 4", "depends 4: 5", "depends 5: 3",
                      "depends 6: 7", "depends 7: 8",
                      "depends 10: 12", "depends 12: 11", "depends 11: 12",
                      "depends 13: 14, 15", "depends 14: 13", "depends 15: 13")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 1: 2')}: depends cycle among 1, 2 "
            "(2 decisions)",
            f"{self.where(p, 'depends 3: 4')}: depends cycle among 3, 4, 5 "
            "(3 decisions)",
            f"{self.where(p, 'depends 11: 12')}: depends cycle among 11, 12 "
            "(2 decisions)",
            f"{self.where(p, 'depends 13: 14, 15')}: depends cycle among 13, "
            "14, 15 (3 decisions)"])

    def test_dense_graph_is_one_bounded_line(self):
        """300 decisions each depending on all the others: one line, ten
        members listed, quickly. Mutant: the member list not capped."""
        ns = range(1, 301)
        lines = [f"decision {n}: x?" for n in ns] + [
            f"depends {n}: " + ", ".join(str(m) for m in ns if m != n)
            for n in ns]
        p = self.item("a-item-1111", *lines)
        t0 = time.monotonic()
        got = self.lint()
        self.assertLess(time.monotonic() - t0, 10)
        first = "depends 1: " + ", ".join(str(m) for m in range(2, 301))
        self.assertEqual(got, [
            f"{self.where(p, first)}: depends cycle among 1, 2, 3, 4, 5, 6, "
            "7, 8, 9, 10 … and 290 more (300 decisions)"])

    def test_dense_graph_fast_in_process(self):
        """The component walk alone on the 300-node complete graph, and a
        10,000-long ring (no recursion limit)."""
        t0 = time.monotonic()
        comps = wi._components({n: [m for m in range(300) if m != n]
                                for n in range(300)})
        ring = wi._components({n: [(n + 1) % 10000] for n in range(10000)})
        self.assertLess(time.monotonic() - t0, 3)
        self.assertEqual([len(c) for c in comps], [300])
        self.assertEqual([len(c) for c in ring], [10000])

    def test_same_m_alternatives_count_once(self):
        """Dangling and self once per M; a 2-cycle whose back edge names
        two letters of one M is one finding. Mutant: the per-line seen_m
        set removed."""
        p = self.item("a-item-1111", "decision 7: x?", "decision 8: x?",
                      "decision 1: x?", "decision 2: x?",
                      "depends 7: 9 (a), 9 (b)", "depends 8: 8 (a), 8 (b)",
                      "depends 1: 2", "depends 2: 1 (a), 1 (b)")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 7: 9 (a), 9 (b)')}: decision 7: "
            "dangling target 9, with no `decision 9:` line in items/ or "
            "archive/",
            f"{self.where(p, 'depends 8: 8 (a), 8 (b)')}: decision 8 depends "
            "on itself (8)",
            f"{self.where(p, 'depends 1: 2')}: depends cycle among 1, 2 "
            "(2 decisions)"])

    def test_a_linked_archive_item_is_skipped_silently(self):
        """L3: a linked file under archive/ is neither read nor reported.
        Mutant: the items/-only condition dropped."""
        outside = self.tmp / "outside.md"
        outside.write_text(ITEM.format(iid="b-item-2222", status="done",
                                       notes="depends 9: 4"))
        (self.root / "archive" / "2026").mkdir(parents=True)
        (self.root / "archive" / "2026" / "b-item-2222.md").symlink_to(outside)
        self.assertEqual(self.lint(), [])

    def test_a_linked_item_is_reported_and_not_read(self):
        """Mutant: _no_link always True (the link read, its orphan line
        reported instead)."""
        outside = self.tmp / "outside.md"
        outside.write_text(ITEM.format(iid="b-item-2222", status="todo",
                                       notes="depends 9: 4"))
        link = self.root / "items" / "b-item-2222.md"
        link.symlink_to(outside)
        got = self.lint()
        self.assertEqual(got, [f"{link}: reached through a symbolic link; its "
                               "group and depends lines are not read, and "
                               "it counts for none of them store-wide"])

    @unittest.skipUnless(GIT, "git not on PATH")
    def test_this_repo_by_its_origin_name(self):
        """`<this repo>#N` is local: self and dangling fire on it, from the
        origin remote's last path part; another repo's does not. Mutant:
        repo-qualified targets never read as this repo's."""
        subprocess.run(["git", "init", "-q", str(self.base)], env=self.env,
                       check=True)
        subprocess.run(["git", "-C", str(self.base), "remote", "add",
                        "origin", "git@example.com:someone/myrepo.git"],
                       env=self.env, check=True)
        p = self.item("a-item-1111", "decision 4: open?",
                      "depends 4: myrepo#4, myrepo#97, base#96, agents#95")
        line = self.where(p, "depends 4: myrepo#4, myrepo#97, base#96, "
                             "agents#95")
        self.assertEqual(self.lint(), [
            f"{line}: decision 4 depends on itself (myrepo#4)",
            f"{line}: decision 4: dangling target myrepo#97, with no "
            "`decision 97:` line in items/ or archive/"])

    @unittest.skipUnless(GIT, "git not on PATH")
    def test_this_repo_from_a_linked_worktree_is_the_main_checkout(self):
        """L2: a store in a linked worktree with no origin names the main
        checkout: `base#4` is self, `wtree#4` another repo's. Mutant: the
        --git-common-dir call dropped (the worktree's own name used)."""
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(g + ["init", "-q", str(self.base)], env=self.env,
                       check=True)
        (self.base / "f").write_text("x\n")
        subprocess.run(g + ["-C", str(self.base), "add", "f"], env=self.env,
                       check=True)
        subprocess.run(g + ["-C", str(self.base), "commit", "-qm", "c"],
                       env=self.env, check=True)
        wt = self.tmp / "wtree"
        subprocess.run(g + ["-C", str(self.base), "worktree", "add", "-q",
                            str(wt)], env=self.env, check=True,
                       capture_output=True)
        self.root = wt / ".work-items"
        (self.root / "items").mkdir(parents=True)
        (self.root / "store.yaml").write_text("tracking: ignored\n")
        p = self.item("a-item-1111", "decision 4: open?",
                      "depends 4: base#4, wtree#4")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 4: base#4, wtree#4')}: decision 4 "
            "depends on itself (base#4)"])

    @unittest.skipUnless(GIT, "git not on PATH")
    def test_this_repo_without_origin_is_its_checkout_dir(self):
        """Mutant: the main checkout's name fallback removed."""
        subprocess.run(["git", "init", "-q", str(self.base)], env=self.env,
                       check=True)
        p = self.item("a-item-1111", "decision 4: open?", "depends 4: base#4")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 4: base#4')}: decision 4 depends on "
            "itself (base#4)"])

    def test_this_repo_outside_git_is_the_store_parent(self):
        """Outside git, the store's parent directory names this repo."""
        p = self.item("a-item-1111", "decision 4: open?", "depends 4: base#4")
        self.assertEqual(self.lint(), [
            f"{self.where(p, 'depends 4: base#4')}: decision 4 depends on "
            "itself (base#4)"])


if __name__ == "__main__":
    unittest.main()
