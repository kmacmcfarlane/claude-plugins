"""Card records (3b51 W2): `wi raise --record` writes one immutable JSON file
per revision at cards/<id>/<N>/<rev>.card<k>.json before the item's lines,
its `card:` line last; the headline is built from the record; `--revise N`
restates an open decision (refused once any `answer N:` line exists,
store-wide); `--lines` adds machine lines, also alone under the current card;
`--raised`, `--why` and `--check`; strict JSON, a size cap, headline-field
refusals, two secret scans, a symlink-safe level walk, and adoption of a
byte-identical orphan.

Each check here was proved against a mutant of wi.py (the mutant named in
the test's docstring makes it fail). Temporary stores only; git runs with a
temp HOME and global config, and never sees a repo around the temp dir.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import copy
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_cards", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

GIT = shutil.which("git")
IID = "probe-item-1111"
OTHER = "other-item-2222"
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

## Notes
{notes}
"""
UTC_SECOND = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"
REV = "2026-10-23T10:00:00Z"
REV2 = "2026-10-23T11:00:00Z"
SECRET = "DB_PASS=hunter2hunter2hunterXYZ"   # test_wi's assignment fake
KEYISH = "Zq8vK2mW9xR4tY7uP3sL6nB1"           # an invented key-shaped value


def record(**over):
    rec = {
        "format": "decision-card/5", "rev": REV, "t": "probe upload",
        "q": "Ship the probe upload?",
        "label": {"id": "F7", "name": "probe upload"}, "oneway": True,
        "tldr": ["whether the probe ships"], "context": "The probe is a test.",
        "options": [{"k": "a", "title": "Ship it", "effect": "it ships"},
                    {"k": "b", "title": "Hold it", "effect": "it waits"},
                    {"k": "z", "title": "decide later"}],
        "rec": "b", "basis": "partial",
    }
    rec.update(over)
    return rec


class CardCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="wi-w2-")))
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
        self.root = self.tmp / "base" / ".work-items"
        (self.root / "items").mkdir(parents=True)
        (self.root / "store.yaml").write_text(
            "# wi store settings; format: the work-items skill's "
            "references/format.md\ntracking: tracked\n")
        self.item(IID)
        self.recfile = self.tmp / "rec.json"

    # -- helpers ---------------------------------------------------------

    def wi(self, *args, input=None, root=None, **kw):
        env = dict(self.env, WORK_ITEMS_ROOT=str(root or self.root))
        return subprocess.run([sys.executable, str(WI), *args], env=env,
                              capture_output=True, text=True, input=input,
                              **kw)

    def ok(self, *args, **kw):
        r = self.wi(*args, **kw)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def refused(self, code, *args, why=None, **kw):
        """Exit `code`, nothing written (snapshot unchanged), stdout empty."""
        before = self.snapshot()
        r = self.wi(*args, **kw)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        self.assertEqual(r.stdout, "")
        if why:
            self.assertIn(why, r.stderr)
        self.assertEqual(self.snapshot(), before)
        return r

    def item(self, iid, notes="- 2026-08-01 started", where="items"):
        path = self.root / where / f"{iid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ITEM.format(iid=iid, notes=notes))
        return path

    def item_text(self, iid=IID):
        return (self.root / "items" / f"{iid}.md").read_text()

    def write_rec(self, rec, path=None):
        path = path or self.recfile
        path.write_text(json.dumps(rec, ensure_ascii=False))
        return str(path)

    def raise_rec(self, rec=None, *extra):
        return self.ok("raise", IID, "--record",
                       self.write_rec(rec or record()), *extra)

    def snapshot(self):
        """Bytes of every file under the store but the lock, and the set of
        directories."""
        out = {}
        for dirpath, dirs, files in os.walk(self.root):
            out[dirpath] = None
            for f in files:
                if f == ".lock":
                    continue
                p = os.path.join(dirpath, f)
                out[p] = Path(p).read_bytes()
        return out

    def card_files(self):
        return sorted(str(p.relative_to(self.root))
                      for p in (self.root / "cards").rglob("*") if p.is_file()) \
            if (self.root / "cards").exists() else []

    def loaded(self, iid=IID):
        return wi.load_item_anywhere(self.root, iid)


class TestRaiseRecord(CardCase):

    def test_new_carded_raise(self):
        """Prints N; the file holds the record with n = N, as json.dumps
        writes it; the item gains the headline, `raised:` and `card:` in
        that order, and card_lines names the file."""
        r = self.raise_rec()
        self.assertEqual(r.stdout, "1\n")
        rel = f"cards/{IID}/1/2026-10-23T10-00-00Z.card5.json"
        self.assertEqual(self.card_files(), [rel])
        data = (self.root / rel).read_bytes()
        expect = record()
        expect["n"] = 1
        self.assertEqual(data, (json.dumps(expect, ensure_ascii=False,
                                           indent=2) + "\n").encode())
        text = self.item_text()
        self.assertRegex(text, re.escape(
            "\ndecision 1: F7 (probe upload) · Ship the probe upload? "
            "⚠ one-way — options: (a) Ship it | (b) Hold it [recommended] "
            "| (z) decide later\n  raised: ") + UTC_SECOND + re.escape(
            f"\n  card: {rel} rev {REV} · decision-card/5 — the card is this "
            "record; read it with the decisions skill's card-record "
            "reference; never backfill this card from lines\n"))
        self.assertEqual(wi.card_lines(self.loaded()),
                         {1: [(rel, REV, "decision-card/5")]})
        self.assertIn("decision: 1", (self.root / "store.yaml").read_text())

    def test_callers_n_is_overwritten(self):
        """Mutant: n kept from the caller (999 in the file)."""
        self.raise_rec(record(n=999))
        f = next((self.root / "cards").rglob("*.json"))
        self.assertEqual(json.loads(f.read_text())["n"], 1)

    def test_headline_with_no_recommendation(self):
        """rec null: ` — <norec>` after the last option, no `[recommended]`,
        and no ⚠ one-way without oneway. Mutant: norec dropped."""
        rec = record(rec=None, norec="your preference — no recommendation")
        del rec["label"], rec["oneway"]
        self.raise_rec(rec)
        self.assertIn("\ndecision 1: Ship the probe upload? — options: (a) "
                      "Ship it | (b) Hold it | (z) decide later — your "
                      "preference — no recommendation\n", self.item_text())

    def test_rec_may_be_z(self):
        """Mutant: the old (z) exclusion."""
        self.raise_rec(record(rec="z"))
        self.assertRegex(self.item_text(),
                         r"\(z\) decide later \[recommended\]\n  raised:")

    def test_check_writes_nothing(self):
        """--check on a valid record: exit 0, the store byte-identical (no
        cards/ made); on a record with ` | ` in q: exit 1. Mutant: --check
        writing."""
        before = self.snapshot()
        r = self.ok("raise", IID, "--record", self.write_rec(record()),
                    "--check")
        self.assertIn("would raise decision 1", r.stdout)
        self.assertEqual(self.snapshot(), before)
        self.refused(1, "raise", IID, "--record",
                     self.write_rec(record(q="a | b")), "--check", why="' | '")

    def test_second_writer_of_one_rev_refused(self):
        """A revision with the same rev and format: exit 3, the first file
        unchanged, no second card: line. Mutant: create=True dropped (and
        the named-file check removed: the file replaced)."""
        self.raise_rec()
        f = next((self.root / "cards").rglob("*.json"))
        first = f.read_bytes()
        rec = record(n=1, q="Ship it now?")
        self.refused(3, "raise", IID, "--revise", "1", "--why", "re-ask",
                     "--record", self.write_rec(rec), why="immutable")
        self.assertEqual(f.read_bytes(), first)
        self.assertEqual(self.item_text().count("  card: "), 1)

    def test_rev_patterns(self):
        """Minute form refused with the fix; a trailing newline refused
        (fullmatch, not match with $); a non-ASCII digit refused. Mutants:
        the write pattern with optional seconds; re.match with $; \\d."""
        self.refused(1, "raise", IID, "--record",
                     self.write_rec(record(rev="2026-10-23T10:00Z")),
                     why="write it to the second")
        self.refused(1, "raise", IID, "--record",
                     self.write_rec(record(rev=REV + "\n")), why="rev:")
        self.refused(1, "raise", IID, "--record",
                     self.write_rec(record(rev="2026-10-23T1\u0662:00:00Z")),
                     why="rev:")

    def test_format_pattern(self):
        for fmt in ("decision-card/0", "decision-card/5\n", "card/5", 5):
            with self.subTest(fmt=fmt):
                self.refused(1, "raise", IID, "--record",
                             self.write_rec(record(format=fmt)),
                             why="format:")

    def test_shape_refusals(self):
        bad_opts = [
            ("options", []),
            ("options", [{"k": "b", "title": "x"}, {"k": "a", "title": "y"}]),
            ("options", [{"k": "a", "title": "x"}, {"k": "a", "title": "y"}]),
            ("options", [{"k": "A", "title": "x"}]),
            ("options", [{"k": "a"}]),
            ("rec", "q"),
            ("rec", None),          # null without norec
            ("label", {"id": "F 7", "name": "x"}),
            ("label", "F7"),
            ("oneway", "yes"),
            ("q", ""),
        ]
        for key, val in bad_opts:
            with self.subTest(key=key, val=val):
                self.refused(1, "raise", IID, "--record",
                             self.write_rec(record(**{key: val})),
                             why="nothing written")

    def test_lines_after_card(self):
        """A delegation: line lands after card:."""
        lines = self.tmp / "lines"
        lines.write_text("  delegation: dl-1023-abc\n  terms: until done\n")
        self.raise_rec(None, "--lines", str(lines))
        self.assertRegex(self.item_text(), r"\n  card: [^\n]*\n  delegation: "
                                           r"dl-1023-abc\n  terms: until done\n")

    def test_machine_line_keys(self):
        """impact: (card content) and raised: (wi's own) refused; a
        column-0 line refused. Mutant: the key list removed."""
        for text, why in (("  impact: → x\n", "goes in the record"),
                          ("  raised: 2026-10-23T10:00:00Z\n", "wi's own"),
                          ("grant: g-1\n", "indented"),
                          (f"  act: {SECRET}\n", "likely secret")):
            with self.subTest(text=text):
                p = self.tmp / "lines"
                p.write_text(text)
                self.refused(1, "raise", IID, "--record",
                             self.write_rec(record()), "--lines", str(p),
                             why=why)

    def test_empty_grant_refused(self):
        """Mutant: the empty-grant check removed."""
        for text in ("  grant:\n", "  grant:   \n"):
            with self.subTest(text=text):
                p = self.tmp / "lines"
                p.write_text(text)
                self.refused(1, "raise", IID, "--record",
                             self.write_rec(record()), "--lines", str(p),
                             why="grant's id")

    def test_misspelled_options_never_reach_the_store(self):
        """Each exits 2 with the store byte-identical; `-- --q` is the
        question `--q`. Mutant: the one-leftover check (`len(left) > 1`) removed
        (`--chek -- q` raises q)."""
        for args in (["--chek"], [f"--recrod={self.recfile}"],
                     ["--chek", "--"], ["--chek", "--", "q"]):
            with self.subTest(args=args):
                self.refused(2, "raise", IID, *args)
        self.ok("raise", IID, "--", "--q")
        self.assertIn("\ndecision 1: --q\n", self.item_text())

    def test_record_and_lines_cannot_both_read_stdin(self):
        self.refused(1, "raise", IID, "--record", "-", "--lines", "-",
                     input="{}", why="stdin")

    def test_record_from_stdin(self):
        r = self.ok("raise", IID, "--record", "-",
                    input=json.dumps(record()))
        self.assertEqual(r.stdout, "1\n")
        self.assertEqual(len(self.card_files()), 1)

    def test_stdin_never_read_for_a_file_record(self):
        """stdin an open, never-closed pipe, --record <file>: returns at
        once. Mutant: stdin read whenever it is not a terminal."""
        env = dict(self.env, WORK_ITEMS_ROOT=str(self.root))
        proc = subprocess.Popen(
            [sys.executable, str(WI), "raise", IID, "--record",
             self.write_rec(record())], env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            code = proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            self.fail("raise blocked on an open stdin")
        finally:
            proc.stdin.close()
        out = proc.stdout.read().decode()
        proc.stdout.close()
        proc.stderr.close()
        self.assertEqual((code, out), (0, "1\n"))

    def test_question_and_record_exclusive(self):
        self.refused(1, "raise", IID, "--record", self.write_rec(record()),
                     "--", "q?", why="exclusive")

    def test_card_line_reads_back_and_raised_reads_past_it(self):
        """decision_raised still reads a raised: line after a card: line."""
        self.item(IID, notes=(
            f"decision 4: q?\n  card: cards/{IID}/4/2026-10-23T10-00-00Z."
            f"card5.json rev {REV} · decision-card/5\n  raised: {REV}"))
        it = self.loaded()
        self.assertEqual(wi.decision_raised(it), {4: REV})
        self.assertEqual(list(wi.card_lines(it)), [4])

    def test_card_lines_fence_and_block_rules(self):
        """A card: line inside a fence is ignored; one under another N's
        block counts for that N. Mutant: the fence rule removed."""
        line = (f"  card: cards/{IID}/5/2026-10-23T10-00-00Z.card5.json rev "
                f"{REV} · decision-card/5")
        self.item(IID, notes=(f"decision 5: q?\n```\ndecision 9: x\n{line}\n"
                              f"```\ndecision 6: r?\n{line}"))
        self.assertEqual(list(wi.card_lines(self.loaded())), [6])

    def test_needs_input_unchanged_but_for_the_new_n(self):
        """needs-input --plain and --json, estate --json: the same before
        and after a carded raise, apart from the new decision."""
        self.ok("raise", IID, "--", "first?")
        before = [self.ok("needs-input", "--plain").stdout,
                  json.loads(self.ok("needs-input", "--json").stdout)]
        est = json.loads(self.ok("estate", "--dir", str(self.tmp),
                                 "--json").stdout)
        self.raise_rec()
        plain = self.ok("needs-input", "--plain").stdout
        self.assertEqual([ln for ln in plain.splitlines()
                          if "\t2\t" not in ln], before[0].splitlines())
        data = json.loads(self.ok("needs-input", "--json").stdout)
        decs = data[0]["decisions"]
        self.assertEqual([d for d in decs if d["n"] != 2],
                         before[1][0]["decisions"])
        self.assertEqual(decs[-1]["text"], wi.unanswered_decisions(
            self.loaded())[-1][1])
        est2 = json.loads(self.ok("estate", "--dir", str(self.tmp),
                                  "--json").stdout)
        self.assertEqual(sorted(est2), sorted(est))


class TestStrict(CardCase):

    def raw(self, text, why):
        self.recfile.write_text(text)
        return self.refused(1, "raise", IID, "--record", str(self.recfile),
                            why=why)

    def test_size_cap(self):
        """A 300 KB record refused. Mutant: the cap removed."""
        self.raw(json.dumps(record(context="x" * 300_000)), "over 256 KB")

    def test_constants_refused(self):
        """NaN, Infinity, -Infinity, an overflowing number. Mutants: the
        parse_constant hook removed; the parse_float hook removed."""
        base = json.dumps(record())[:-1]
        for tail in ('"x": NaN}', '"x": Infinity}', '"x": -Infinity}',
                     '"x": 1e400}'):
            with self.subTest(tail=tail):
                self.raw(base + ", " + tail, "not JSON" if "e400" not in tail
                         else "too large")

    def test_duplicate_key_refused_at_depth(self):
        """Mutant: object_pairs_hook removed."""
        base = json.dumps(record())[:-1]
        self.raw(base + ', "deep": {"a": 1, "a": 2}}', "duplicate key")
        self.raw(base + ', "rev": "' + REV + '"}', "duplicate key")

    def test_deep_nesting_refused(self):
        """Mutant: the RecursionError catch removed (a traceback)."""
        r = self.raw("[" * 200_000 + "]" * 200_000, "nothing written")
        self.assertNotIn("Traceback", r.stderr)
        base = json.dumps(record())[:-1]
        r = self.raw(base + ', "x": ' + "[" * 100_000 + "]" * 100_000 + "}",
                     "nothing written")
        self.assertNotIn("Traceback", r.stderr)

    def test_not_an_object_or_not_json(self):
        self.raw("[1, 2]", "not a JSON object")
        self.raw("{nope", "not valid JSON")
        self.recfile.write_bytes(b'{"q": "\xff"}')
        self.refused(1, "raise", IID, "--record", str(self.recfile),
                     why="not UTF-8")

    def test_lone_surrogate_refused(self):
        """A lone surrogate fails the encoding before any write."""
        base = json.dumps(record())[:-1]
        self.raw(base + ', "context2": "a\\ud800b"}', "surrogate")

    def test_headline_field_classes(self):
        """One row per class; mutants: each class's check removed."""
        rows = [
            ({"q": "a\u2028b"}, "line break"),
            ({"options": [{"k": "a", "title": "x\ty"}]}, "control"),
            ({"q": "a\u202eb"}, "format character"),
            ({"options": [{"k": "a", "title": "x | y"}], "rec": "a"}, "' | '"),
            ({"q": "pick one [Recommended]"}, "[recommended]"),
            ({"q": "pick — options: (a) x"}, "options"),
            ({"options": [{"k": "a", "title": "go (b) now"}], "rec": "a"},
             "option marker"),
            ({"label": {"id": "F7", "name": "x\u2066y"}}, "format character"),
            ({"rec": None, "norec": "no | rec"}, "' | '"),
        ]
        for over, why in rows:
            with self.subTest(over=over):
                self.refused(1, "raise", IID, "--record",
                             self.write_rec(record(**over)), why=why)

    def test_written_bytes_capped(self):
        """A record under 256 KB whose indented bytes run past it (indent
        grows with depth) is refused before any write. Mutant: the cap on
        the encoded bytes removed (the file is written)."""
        deep = [0] * 90_000
        for _ in range(55):
            deep = [deep]
        text = json.dumps(record(x=deep), separators=(",", ":"))
        self.assertLess(len(text.encode()), wi.RECORD_CAP)
        self.raw(text, "as written over 256 KB")

    def test_depth_limit(self):
        """65 levels refused, 64 written. Mutant: the depth check removed."""
        def nested(levels):   # the record is level 1, "x" adds the rest
            v = 0
            for _ in range(levels - 1):
                v = [v]
            return v
        self.raw(json.dumps(record(x=nested(65))), "nested more than 64")
        self.raise_rec(record(x=nested(64)))

    def test_underflow_refused(self):
        """A non-zero literal that reads as 0. Mutant: the underflow check
        removed. A literal 0.0e-400 stays a zero."""
        base = json.dumps(record())[:-1]
        self.raw(base + ', "x": 1e-400}', "too small")
        self.recfile.write_text(base + ', "x": 0.0e-400}')
        self.ok("raise", IID, "--record", str(self.recfile))

    def test_forged_tokens_from_format_characters(self):
        """Zero-width spaces between a token's parts, a word joiner, a soft
        hyphen, a BOM and a tag character are each refused. Mutant: the Cf
        check removed (the forged title is written)."""
        zw = "\u200b"
        forged = f"[recom{zw}mended] {zw}| ({zw}c)"
        for title in (forged, "a\u2060b", "a\u00adb", "\ufeffab",
                      "ab\U000e0041"):
            with self.subTest(title=title):
                rec = record(options=[{"k": "a", "title": title},
                                      {"k": "z", "title": "later"}], rec="z")
                self.refused(1, "raise", IID, "--record", self.write_rec(rec),
                             why="format character")

    def test_headline_nits(self):
        """⚠ one-way inside q; the label's delimiters in label.name; ` — `
        in a title with no recommendation; q starting with whitespace.
        Mutants: each check removed."""
        norec = record(rec=None, norec="your preference — no recommendation",
                       options=[{"k": "a", "title": "go — now"},
                                {"k": "z", "title": "later"}])
        rows = [
            (record(q="ship it ⚠ one-way"), "⚠ one-way"),
            (record(label={"id": "F7", "name": "probe (x"}), "delimiters"),
            (record(label={"id": "F7", "name": "probe · x"}), "delimiters"),
            (norec, "norec label"),
            (record(q=" ship it?"), "starts with whitespace"),
        ]
        for rec, why in rows:
            with self.subTest(why=why):
                self.refused(1, "raise", IID, "--record", self.write_rec(rec),
                             why=why)
        # with a recommendation, ` — ` in a title is fine
        self.raise_rec(record(options=[{"k": "a", "title": "go — now"},
                                       {"k": "z", "title": "later"}], rec="a"))

    def test_question_may_hold_an_option_marker(self):
        """Mutant: the marker check applied to q."""
        self.raise_rec(record(q="Pick (b) or not?"))
        self.assertIn("Pick (b) or not?", self.item_text())


class TestSecrets(CardCase):

    def test_secret_deep_in_a_plan(self):
        """A one-line secret in an option's plan: `record line <k>`, the
        value not on stderr. Mutant: the scan run over the headline only."""
        rec = record()
        rec["options"][0]["plan"] = SECRET
        r = self.refused(1, "raise", IID, "--record", self.write_rec(rec),
                         why="record line")
        self.assertNotIn("hunter2", r.stderr)

    def test_multiline_secrets_by_json_path(self):
        """Laid over two lines inside one value: caught by the decoded scan,
        named by JSON path and line. Mutant: the decoded scan removed."""
        cases = [
            (("options", 0, "plan"), f"api_key: |\n  {KEYISH}",
             "options[0].plan line 2"),
            (("finding", "excerpt", "text"),
             f"export API_TOKEN=\\\n  {KEYISH}", "finding.excerpt.text line 2"),
            (("context",), f"Authorization:\n  Bearer {KEYISH}x",
             "context line 2"),
        ]
        for keys, val, why in cases:
            with self.subTest(why=why):
                rec = record()
                if keys[0] == "finding":
                    rec["finding"] = {"excerpt": {"text": val}}
                elif keys[0] == "options":
                    rec["options"][0]["plan"] = val
                else:
                    rec["context"] = val
                r = self.refused(1, "raise", IID, "--record",
                                 self.write_rec(rec), why=why)
                self.assertNotIn(KEYISH, r.stderr)

    def test_list_strings_scanned_with_their_key(self):
        """A secret listed under its key reads as `<key>: <value>`. Mutant:
        list strings scanned without their parent key."""
        for key, val in (("api_key", KEYISH), ("DB_PASSWORD",
                                                "hunter2hunter2hunterXYZ")):
            with self.subTest(key=key):
                rec = record()
                rec["extra"] = {key: [val]}
                r = self.refused(1, "raise", IID, "--record",
                                 self.write_rec(rec),
                                 why=f"extra.{key}[0] line 1")
                self.assertNotIn(val, r.stderr)

    def test_long_key_named_by_position(self):
        """A key past 32 characters is named by its place. Mutant: the
        32-character bound raised to 64."""
        key = "k" * 40
        rec = record()
        rec[key] = f"api_key: |\n  {KEYISH}"
        r = self.refused(1, "raise", IID, "--record", self.write_rec(rec),
                         why="<key ")
        self.assertNotIn(key, r.stderr)

    def test_prose_token_is_clean(self):
        self.raise_rec(record(context="the token count is fine here"))


class TestLevelWalk(CardCase):

    def outside(self):
        out = self.tmp / "outside"
        out.mkdir()
        return out

    def test_symlinked_item_level(self):
        """cards/<id> a link out of the store: exit 3, the outside dir
        empty. Mutant: the lstat check removed (the file lands outside)."""
        out = self.outside()
        (self.root / "cards").mkdir()
        os.symlink(out, self.root / "cards" / IID)
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="symbolic link")
        self.assertEqual(list(out.iterdir()), [])

    def test_symlinked_n_level(self):
        out = self.outside()
        (self.root / "cards" / IID).mkdir(parents=True)
        os.symlink(out, self.root / "cards" / IID / "1")
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="symbolic link")
        self.assertEqual(list(out.iterdir()), [])

    def test_symlinked_cards(self):
        """Mutant: the walk started below cards."""
        out = self.outside()
        os.symlink(out, self.root / "cards")
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="symbolic link")
        self.assertEqual(list(out.iterdir()), [])

    def test_missing_levels_made(self):
        self.raise_rec()
        self.assertTrue((self.root / "cards" / IID / "1").is_dir())


class TestOrphans(CardCase):

    def built_bytes(self, n=1):
        rec = record()
        rec["n"] = n
        return (json.dumps(rec, ensure_ascii=False, indent=2) + "\n").encode()

    def place(self, data, n=1):
        d = self.root / "cards" / IID / str(n)
        d.mkdir(parents=True)
        f = d / "2026-10-23T10-00-00Z.card5.json"
        f.write_bytes(data)
        return f

    def test_identical_orphan_adopted(self):
        """One card: line, the file untouched. Mutant: adoption without the
        byte comparison is covered by the next test."""
        f = self.place(self.built_bytes())
        st = f.stat()
        self.raise_rec()
        self.assertEqual(self.item_text().count("  card: "), 1)
        self.assertEqual((f.stat().st_ino, f.stat().st_mtime_ns),
                         (st.st_ino, st.st_mtime_ns))

    def test_differing_orphan_refused(self):
        """Mutant: adoption without the byte comparison."""
        self.place(b"{}\n")
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="named by no card: line and differs")

    def test_named_identical_file_refused(self):
        """A file a card: line names is immutable even with equal bytes.
        Mutant: adoption without the store-wide name check."""
        # the other item's decision 1 makes the raise's N 2
        f = self.place(self.built_bytes(2), n=2)
        self.item(OTHER, notes=(
            f"decision 1: q?\n  card: {f.relative_to(self.root)} rev {REV} "
            "· decision-card/5"), where="archive/2026")
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="immutable")

    def test_symlink_with_equal_bytes_refused(self):
        """Mutant: adoption by open and compare, no lstat."""
        target = self.tmp / "same.json"
        target.write_bytes(self.built_bytes())
        d = self.root / "cards" / IID / "1"
        d.mkdir(parents=True)
        os.symlink(target, d / "2026-10-23T10-00-00Z.card5.json")
        # the lstat names it; O_NOFOLLOW behind it would refuse it too
        self.refused(3, "raise", IID, "--record", self.write_rec(record()),
                     why="is a symbolic link; a card record")


class TestRevise(CardCase):

    def setUp(self):
        super().setUp()
        self.raise_rec()   # decision 1, carded

    def rev(self, *extra, rec=None):
        rec = rec or record(n=1, rev=REV2, q="Ship it today?")
        return ("raise", IID, "--revise", "1", "--why", "re-asked",
                "--record", self.write_rec(rec), *extra)

    def test_revision_appends_revised_and_card(self):
        self.ok(*self.rev())
        text = self.item_text()
        self.assertRegex(text, r"\ndecision 1: F7 \(probe upload\) · Ship it "
                         r"today\? [^\n]*\n  revised: " + UTC_SECOND +
                         r" — re-asked\n  card: cards/" + IID +
                         r"/1/2026-10-23T11-00-00Z\.card5\.json rev ")
        self.assertEqual(len(wi.card_lines(self.loaded())[1]), 2)
        self.assertEqual(wi.unanswered_decisions(self.loaded())[0][1][:20],
                         "F7 (probe upload) · ")
        self.assertIn("decision: 1", (self.root / "store.yaml").read_text())

    def test_n_must_match(self):
        """Mutant: the check removed."""
        self.refused(1, *self.rev(rec=record(n=2, rev=REV2)), why="n:")

    def test_answered_on_another_item(self):
        """Mutant: the scan limited to the same item."""
        self.item(OTHER, notes="answer 1: b", where="archive/2026")
        self.refused(1, *self.rev(), why=f"on {OTHER}")

    def test_answered_line_in_fence_not_counted(self):
        self.item(OTHER, notes="```\nanswer 1: b\n```")
        self.ok(*self.rev())

    def test_wake_only_is_open(self):
        self.item(OTHER, notes="wake 1: 2026-11-01")
        self.ok(*self.rev())

    def test_no_such_decision_on_item(self):
        self.refused(1, "raise", IID, "--revise", "7", "--why", "x",
                     "--record", self.write_rec(record(n=7, rev=REV2)),
                     why="decision 7 is not on")

    def test_headline_only_revision_refused_with_a_card(self):
        """Mutant: the check removed."""
        self.refused(1, "raise", IID, "--revise", "1", "--why", "x", "--",
                     "a new headline?", why="has a card record")

    def test_headline_only_revision_without_a_card(self):
        n = self.ok("raise", IID, "--", "plain?").stdout.strip()
        self.ok("raise", IID, "--revise", n, "--why", "reworded", "--",
                "plainer?")
        self.assertRegex(self.item_text(), r"\ndecision 2: plainer\?\n  "
                         r"revised: " + UTC_SECOND + r" — reworded\n")

    def test_why_rules(self):
        """--why required with --revise, refused without; a line break, a
        fence opener and a secret shape refused. Mutant: --why unchecked."""
        self.refused(1, "raise", IID, "--revise", "1", "--record",
                     self.write_rec(record(n=1, rev=REV2)), why="--why")
        self.refused(1, "raise", IID, "--why", "x", "--", "q?", why="--why")
        for bad, why in (("a\nb", "one line"), ("```", "code fence"),
                         (SECRET, "likely secret")):
            with self.subTest(bad=bad):
                r = self.refused(1, "raise", IID, "--revise", "1", "--why",
                                 bad, "--record",
                                 self.write_rec(record(n=1, rev=REV2)),
                                 why=why)
                self.assertNotIn("hunter2", r.stderr)

    def test_raised_rules(self):
        """--raised refused when N has a raised: line; written when it has
        none; the write pattern only."""
        self.refused(1, *self.rev("--raised", REV), why="already has")
        self.item(OTHER, notes="decision 5: old?")
        self.refused(1, "raise", OTHER, "--revise", "5", "--why", "v5",
                     "--raised", "2026-10-01T09:00Z", "--record",
                     self.write_rec(record(n=5)), why="--raised must")
        self.ok("raise", OTHER, "--revise", "5", "--why", "v5", "--raised",
                "2026-10-01T09:00:00Z", "--record",
                self.write_rec(record(n=5)))
        self.assertEqual(wi.decision_raised(self.loaded(OTHER)),
                         {5: "2026-10-01T09:00:00Z"})
        self.refused(1, "raise", IID, "--raised", REV, "--", "q?",
                     why="--raised goes with --revise")

    def test_bad_revise_number(self):
        for n in ("0", "x", "\u0661", "1\n"):
            with self.subTest(n=n):
                self.refused(1, "raise", IID, "--revise", n, "--why", "x",
                             "--", "q?", why="decision number")


class TestLinesOnly(CardCase):

    def setUp(self):
        super().setUp()
        self.raise_rec()
        # a later column-0 line after the card block
        it = self.loaded()
        it.append_note("- 2026-10-24 later note")
        wi.save_item(self.root, it)
        self.lines = self.tmp / "lines"
        self.lines.write_text("  grant: g-x\n")

    def test_inserted_after_the_card_block(self):
        """No new file; the record unchanged; card_lines names the same
        file; the lines sit before the later column-0 line. Mutant: the
        lines appended at the end of ## Notes."""
        f = next((self.root / "cards").rglob("*.json"))
        data = f.read_bytes()
        cards = wi.card_lines(self.loaded())
        self.ok("raise", IID, "--revise", "1", "--why", "grant listed",
                "--lines", str(self.lines))
        self.assertEqual(self.card_files(), [str(f.relative_to(self.root))])
        self.assertEqual(f.read_bytes(), data)
        self.assertEqual(wi.card_lines(self.loaded()), cards)
        self.assertRegex(self.item_text(), r"\n  card: [^\n]*\n  revised: "
                         + UTC_SECOND + r" — grant listed \(machine lines "
                         r"added; record unchanged\)\n  grant: g-x\n- "
                         r"2026-10-24 later note\n")

    def test_refused_once_answered(self):
        """Mutant: the answer check skipped for the lines-only form."""
        self.item(OTHER, notes="answer 1: a")
        self.refused(1, "raise", IID, "--revise", "1", "--why", "g",
                     "--lines", str(self.lines), why="is answered")

    def test_refused_without_a_card(self):
        self.ok("raise", IID, "--", "plain?")
        self.refused(1, "raise", IID, "--revise", "2", "--why", "g",
                     "--lines", str(self.lines), why="no card record")

    def test_impact_refused(self):
        self.lines.write_text("  impact: → x\n")
        self.refused(1, "raise", IID, "--revise", "1", "--why", "g",
                     "--lines", str(self.lines), why="goes in the record")

    def test_lines_without_record_or_revise_refused(self):
        self.refused(1, "raise", IID, "--lines", str(self.lines), "--", "q?",
                     why="--lines goes with")


@unittest.skipUnless(GIT, "git not available")
class TestOwnRepo(CardCase):

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "own" / ".work-items"
        r = self.wi("init", "--no-track", root=self.root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.item(IID)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "item")

    def git(self, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=self.root, env=self.env, capture_output=True, text=True,
            check=True)

    def test_one_commit_holds_file_item_and_counter(self):
        r = self.raise_rec()
        self.assertNotIn("not committed", r.stderr)
        self.assertEqual(self.git("log", "-1", "--format=%s").stdout.strip(),
                         f"wi raise: {IID}")
        files = self.git("show", "--name-only", "--format=", "HEAD").stdout
        self.assertEqual(sorted(files.split()), sorted([
            f"cards/{IID}/1/2026-10-23T10-00-00Z.card5.json",
            f"items/{IID}.md", "store.yaml"]))
        self.assertEqual(self.git("status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main()
