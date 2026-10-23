"""The page writes one answer document per decision, of exactly {n, choice, kind, words, rec, rev, at}.

The answers collection is the contract the read-back counts on (`skills/decision-page/references/
cards-schema.md` § The answers collection): `rev` decides which answers count, and a format-only
upgrade keeps it. The page's `write` function, as written in `assets/index.html`, is run under node
against a stand-in for the store: an option, a follow-up, words only and a cleared answer.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import subprocess
import sys
import unittest

from test_impact import NODE, PAGE


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the answer document tests (AnswerDocument) are skipped, "
              "so the page's answer writes went untested", file=sys.stderr)


FIELDS = {"n", "choice", "kind", "words", "rec", "rev", "at"}

HARNESS = r"""
const docs = {}, log = [];
let readonly = false, answers = {};
const inflight = {}, dirty = {}, setSave = () => {};
const FOLLOW_KEYS = new Set(["later", "tell me", "expand", "dig into", "you decide", "drop"]);
const byN = new Map([["41", {n: 41, rec: "b", rev: "2026-01-12T09:30:00Z"}], ["43", {n: 43, rec: null, rev: "2026-01-12T09:30:00Z"}]]);
const col = {doc: id => ({set: async v => { docs[id] = v; log.push(["set", id]); }, delete: async () => { delete docs[id]; log.push(["delete", id]); }})};
const db = {};
""" + "%s" + r"""
(async () => {
  const out = {};
  answers = {"41": {choice: "b", words: ""}}; await write("41"); out.option = docs["41"];
  answers = {"41": {choice: "tell me", words: "the fork question"}}; await write("41"); out.follow = docs["41"];
  answers = {"43": {choice: null, words: "either is fine"}}; await write("43"); out.words = docs["43"];
  answers = {"43": {}}; await write("43"); out.cleared = "43" in docs;
  process.stdout.write(JSON.stringify(out));
})();
"""


def write_fn(html):
    return html[html.index("async function write(n){"):html.index("function choose(")]


def run(html):
    out = subprocess.run([NODE, "-e", HARNESS % write_fn(html)], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def doc_problems(res):
    out = []
    for k in ("option", "follow", "words"):
        if set(res[k]) != FIELDS:
            out.append("the %s answer's fields are %s, not exactly %s" % (k, sorted(res[k]), sorted(FIELDS)))
    return out


FRESH_HARNESS = r"""
let answers = {}, raw = {};
const timers = {}, inflight = {};
let synced = 0; const syncAll = () => { synced++; };
const byN = new Map([["41", {n: 41, rev: "2026-01-12T09:30Z"}], ["42", {n: 42, rev: "2026-01-12T09:30:00Z"}]]);
""" + "%s" + r"""
raw = {"41": {choice: "b", words: "", rev: "2026-01-12T09:30Z", at: "x"},
       "42": {choice: "a", words: "", rev: "2026-01-11T08:00:00Z", at: "y"},
       "99": {choice: "a", words: "", rev: "2026-01-12T09:30Z", at: "z"}};
applyRaw();
process.stdout.write(JSON.stringify(answers));
"""
FRESH = "const fresh=(c,v)=>!!v&&v.rev===c.rev;"


def apply_raw(html):
    code = html[html.index("const fresh="):html.index("function renderMap(")]
    out = subprocess.run([NODE, "-e", FRESH_HARNESS % code], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


@unittest.skipUnless(NODE, "node is not installed")
class AnswersCount(unittest.TestCase):
    """An answer counts only when its rev equals its card's exactly (`fresh`): one given to another rev reads as open."""

    def test_only_an_exact_rev_counts(self):
        html = PAGE.read_text()
        self.assertEqual(html.count(FRESH), 1)
        got = apply_raw(html)
        # 41's minute-form rev matches byte for byte; 42's answer was given to an older rev; 99 is not on the page
        self.assertEqual(sorted(got), ["41"])
        self.assertEqual(got["41"]["choice"], "b")
        # mutant: a fresh that ignores rev counts the stale answer
        mutant = apply_raw(html.replace(FRESH, "const fresh=(c,v)=>!!v;"))
        self.assertIn("42", mutant)


@unittest.skipUnless(NODE, "node is not installed")
class AnswerDocument(unittest.TestCase):

    def setUp(self):
        self.html = PAGE.read_text()

    def test_exactly_its_fields(self):
        res = run(self.html)
        self.assertEqual(doc_problems(res), [])
        o, f, w = res["option"], res["follow"], res["words"]
        self.assertEqual((o["n"], o["choice"], o["kind"], o["words"], o["rec"], o["rev"]),
                         (41, "b", "option", "", "b", "2026-01-12T09:30:00Z"))
        self.assertEqual((f["choice"], f["kind"], f["words"]), ("tell me", "follow-up", "the fork question"))
        self.assertEqual((w["choice"], w["kind"], w["words"], w["rec"]), (None, None, "either is fine", None))
        self.assertRegex(o["at"], r"^\d{4}-\d{2}-\d{2}T")
        # a cleared answer deletes its document
        self.assertFalse(res["cleared"])

    def test_mutants(self):
        # a field added, or one dropped, is caught
        added = self.html.replace("rev:byN.get(String(n)).rev,", "rev:byN.get(String(n)).rev,format:\"x\",", 1)
        self.assertNotEqual(added, self.html)
        self.assertTrue(doc_problems(run(added)))
        dropped = self.html.replace("rec:byN.get(String(n)).rec||null,", "", 1)
        self.assertNotEqual(dropped, self.html)
        self.assertTrue(doc_problems(run(dropped)))


if __name__ == "__main__":
    unittest.main()
