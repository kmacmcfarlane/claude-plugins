"""Tests for check-sheet.py, the score-sheet check the orchestrator runs after the verifier.

The acceptance is work item 2e75 (the verifier's procedure faults, from the e184 record):
header counts come from the table, not from what the verifier typed; a verdict other than
UNREACHABLE or NOT_FOUND for a source the verifier did not open is a defect and is tallied
as unreachable; a run's own files are never a source, so a verdict resting on one is a
defect and is tallied as not_found; and a sheet missing a section says so. Every run also
asserts that stdout carries positions, rule names and counts only, never the sheet's text.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "check-sheet.py"
MARK = "zqx-sheet-text"  # in every cell, so a leak of sheet text shows on stdout

ROWS_OK = [
    ("1", "w1.md", "https://example.invalid/a", "WebFetch", "SUPPORTED"),
    ("2", "w1.md", "https://example.invalid/b", "WebFetch", "PARTIAL"),
    ("3", "w2.md", "https://example.invalid/c", "WebFetch", "CONTRADICTED"),
    ("4", "w2.md", "https://example.invalid/d", "WebFetch", "NOT_FOUND"),
    ("5", "w2.md", "https://example.invalid/e", "—", "UNREACHABLE"),
]


def header(counts):
    lines = ["---", "run: demo", "date: 2026-10-13"]
    lines += [f"{k}: {v}" for k, v in counts.items()]
    lines += ["gate: PASS", "---"]
    return lines


def sheet(rows, counts=None, drop=(), cols=("#", "File", "Claim (short)", "Source",
                                            "Opened", "Verdict", "Note")):
    if counts is None:
        counts = {"sampled": len(rows)}
        for v in ("supported", "partial", "contradicted", "not_found", "unreachable"):
            counts[v] = sum(1 for r in rows if r[4].lower() == v)
    out = header(counts) + ["# Verification — demo", ""]
    for s in ("Security check", "Sampled claims", "Axis scores", "Gate",
              "Suggested follow-ups"):
        if s in drop:
            continue
        out.append(f"## {s}")
        if s == "Sampled claims":
            out.append("| " + " | ".join(cols) + " |")
            out.append("|" + "---|" * len(cols))
            for num, f, src, opened, verdict in rows:
                vals = {"#": num, "File": f, "Claim (short)": f"claim {MARK}",
                        "Source": src, "Opened": opened, "Verdict": verdict,
                        "Note": f"data: {MARK}"}
                out.append("| " + " | ".join(vals[c] for c in cols) + " |")
        else:
            out.append(f"none found {MARK}")
        out.append("")
    return "\n".join(out) + "\n"


class CheckSheet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="2e75-")
        self.dir = Path(self.tmp.name)
        (self.dir / "findings").mkdir()
        (self.dir / "findings" / "w1.md").write_text("x\n")
        (self.dir / "01-synthesis.md").write_text("x\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, text, *extra, cwd=None):
        p = self.dir / "verification.md"
        p.write_text(text, encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), *extra],
                           capture_output=True, text=True, cwd=cwd or self.dir.parent)
        self.assertNotIn(MARK, r.stdout + r.stderr)
        return r

    def tally(self, r):
        line = next(l for l in r.stdout.splitlines() if l.startswith("TALLY: "))
        return dict((k, int(v)) for k, v in
                    (part.rsplit(" ", 1) for part in line[7:].split(", ")))

    def rules(self, r):
        return [l.split(": ", 1)[1] for l in r.stdout.splitlines()
                if l.startswith("verification.md:")]

    def test_clean_sheet(self):
        r = self.run_check(sheet(ROWS_OK))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.tally(r), {"sampled": 5, "supported": 1, "partial": 1,
                                         "contradicted": 1, "not_found": 1,
                                         "unreachable": 1, "demoted": 0})
        self.assertIn("CHECK: 0 defects", r.stdout)

    def test_header_that_disagrees_with_its_table(self):
        # the 7113 r2 shape: the header's supported count is two short of the table's
        counts = {"sampled": 5, "supported": 0, "partial": 1, "contradicted": 1,
                  "not_found": 1, "unreachable": 2}
        r = self.run_check(sheet(ROWS_OK, counts))
        self.assertEqual(r.returncode, 1)
        self.assertEqual(sorted(self.rules(r)),
                         ["header-mismatch supported", "header-mismatch unreachable"])
        self.assertEqual(self.tally(r)["supported"], 1)  # from the table, not the header

    def test_header_field_missing(self):
        counts = {"sampled": 5, "supported": 1, "partial": 1, "contradicted": 1,
                  "not_found": 1}
        r = self.run_check(sheet(ROWS_OK, counts))
        self.assertEqual(self.rules(r), ["header-missing unreachable"])

    def test_verdict_for_an_unopened_source(self):
        rows = ROWS_OK + [("6", "w2.md", "https://example.invalid/f", "—", "SUPPORTED"),
                          ("7", "w2.md", "https://example.invalid/g", "", "PARTIAL"),
                          ("8", "w2.md", "https://example.invalid/h", "no", "NOT_FOUND")]
        r = self.run_check(sheet(rows))
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.rules(r), ["unopened-verdict", "unopened-verdict"])
        t = self.tally(r)
        self.assertEqual((t["supported"], t["partial"], t["unreachable"], t["not_found"],
                          t["demoted"]), (1, 1, 3, 2, 2))

    def test_own_run_file_as_source(self):
        series = self.dir.parent / (self.dir.name + "-series")
        series.mkdir()
        try:
            rows = ROWS_OK + [
                ("6", "w1.md", "`findings/w1.md:12`", "Read", "SUPPORTED"),
                ("7", "w1.md", "01-synthesis.md", "Read", "PARTIAL"),
                ("8", "w1.md", f"[s]({series}/00_initial.md)", "Read", "SUPPORTED"),
                ("9", "w1.md", "findings/w1.md", "—", "NOT_FOUND"),
            ]
            r = self.run_check(sheet(rows), "--own", str(series))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertEqual(self.rules(r), ["own-run-source"] * 3)
            t = self.tally(r)
            self.assertEqual((t["not_found"], t["demoted"], t["sampled"]), (5, 3, 9))
        finally:
            series.rmdir()

    def test_prose_and_outside_paths_are_not_own_files(self):
        rows = ROWS_OK + [
            ("6", "w1.md", "TCP/IP spec, arXiv:2607.08700, e.g. p. 5", "WebFetch",
             "SUPPORTED"),
            ("7", "w1.md", "/usr/share/doc/README.md", "Read", "SUPPORTED"),
            ("8", "w1.md", "https://example.invalid/findings/w1.md", "WebFetch",
             "SUPPORTED"),
        ]
        r = self.run_check(sheet(rows))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_missing_sections_and_columns(self):
        r = self.run_check(sheet(ROWS_OK, drop=("Suggested follow-ups",)))
        self.assertEqual(self.rules(r), ["missing-section suggested-follow-ups"])
        r = self.run_check(sheet([x[:3] + ("", x[4]) for x in ROWS_OK],
                                 cols=("#", "File", "Claim (short)", "Source", "Verdict",
                                       "Note")))
        self.assertIn("missing-column opened", self.rules(r))

    def test_bad_verdict(self):
        rows = ROWS_OK + [("6", "w1.md", "https://example.invalid/z", "WebFetch",
                           "LIKELY")]
        r = self.run_check(sheet(rows))
        self.assertIn("bad-verdict", self.rules(r))

    def test_usage_errors(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT),
                            str(self.dir / "absent.md")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("TALLY", r.stdout)
        r = self.run_check("---\nsampled: 0\n---\n# nothing\n")
        self.assertEqual(r.returncode, 2)
        r = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
